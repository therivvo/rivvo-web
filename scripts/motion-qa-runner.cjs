#!/usr/bin/env node
/**
 * motion-qa-runner.cjs — Game Motion QA runner (Playwright).
 *
 * Serves as the PROBE + FRAMES layers of the game-motion-qa skill:
 *   1. Opens the game URL, starts a race (skipCountdown if available)
 *   2. Samples kart telemetry every ~2s via window.__sk3d.raceManager.karts
 *   3. Captures frame sequence f0 (pre-race) + f1..fN (mid-race, MOVING)
 *   4. Verifies motion invariants against the track path (optional --paths)
 *   5. Writes <out>/telemetry.jsonl + <out>/motion-report.md
 *
 * Usage:
 *   node scripts/motion-qa-runner.cjs <url> [--out DIR] [--track N]
 *       [--paths MODULE] [--frames N] [--no-skip-countdown] [--sample-ms MS]
 *
 *   url       game URL, e.g. http://localhost:3457/?test
 *   --out     output dir (default ./qa-out)
 *   --track   track id for path selection (default 1)
 *   --paths   ESM module exporting TRACK_PATH/CITY_PATH (e.g.
 *             ./src/track/TrackBuilder.js) — enables heading/lateral checks
 *   --frames  number of mid-race frames (default 3)
 *   --sample-ms  real-time ms between telemetry samples (default 2000)
 *
 * Expects global playwright at NODE_PATH (see headless-screenshot-capture).
 */
const path = require('path');
const fs = require('fs');
const { pathToFileURL } = require('url');

const args = process.argv.slice(2);
function arg(name, def) {
  const i = args.indexOf(name);
  return i >= 0 ? args[i + 1] : def;
}
const URL = args[0];
const OUT = path.resolve(arg('--out', './qa-out'));
const TRACK = parseInt(arg('--track', '1'), 10);
const PATHS_MOD = arg('--paths', null);
const FRAMES = parseInt(arg('--frames', '3'), 10);
const SKIP_CD = !args.includes('--no-skip-countdown');
const SAMPLE_MS = parseInt(arg('--sample-ms', '2000'), 10);
const HOLD_KEY = arg('--hold-key', null);
const SPEED_GATE = parseFloat(arg('--speed-gate', '0')); // min m/s of any kart before f1 (0=off)
const CAM_BEHIND = args.includes('--cam-behind'); // force chase cam before frames

if (!URL) {
  console.error('usage: node motion-qa-runner.cjs <url> [--out DIR] [--track N] [--paths MOD] [--frames N]');
  process.exit(1);
}

fs.mkdirSync(OUT, { recursive: true });

// ---- track path module (optional, enables heading/lateral invariants) ----
let trackPaths = null;
if (PATHS_MOD) {
  const mod = awaitImport(PATHS_MOD);
}

async function awaitImport(modPath) {
  const resolved = path.resolve(modPath);
  try {
    const mod = await import(pathToFileURL(resolved).href);
    const key = TRACK === 2 ? 'CITY_PATH' : 'TRACK_PATH';
    trackPaths = {
      path: mod[key] || (TRACK === 2 ? mod.CITY_PATH : mod.TRACK_PATH),
      roadWidth: typeof mod.getRoadWidthAt === 'function' ? mod.getRoadWidthAt() : null,
    };
    if (trackPaths.path) {
      const THREE = await import('three');
      const pts = trackPaths.path.map((v) => v.clone ? v : new THREE.Vector3(v.x, v.y, v.z));
      trackPaths.curve = new THREE.CatmullRomCurve3(pts, true, 'catmullrom', 0.5);
      trackPaths.length = trackPaths.curve.getLength();
    }
  } catch (e) {
    console.warn('WARN: --paths import failed:', e.message);
  }
}

function tangentAt(progress01) {
  if (!trackPaths || !trackPaths.curve) return null;
  const t = Math.min(Math.max(progress01, 0.001), 0.999);
  return trackPaths.curve.getTangentAt(t);
}

function pointAt(progress01) {
  if (!trackPaths || !trackPaths.curve) return null;
  const t = Math.min(Math.max(progress01, 0.001), 0.999);
  return trackPaths.curve.getPointAt(t);
}

// ---- invariant checks (see game-motion-qa skill) ----
function checkInvariants(samples) {
  const results = [];
  const push = (name, ok, detail) => results.push({ name, ok, detail });

  let headingBad = 0, headingTotal = 0, latBad = 0, latTotal = 0;
  let speedBad = 0, progressBad = 0, finiteBad = 0, lapBad = 0;
  let stuck = {}, stuckT = {};
  const halfW = (trackPaths && trackPaths.roadWidth ? trackPaths.roadWidth : 18) / 2;
  const maxSpeed = 60; // configurable per game; here: kart ~34m/s + boosts

  for (let i = 0; i < samples.length; i++) {
    const s = samples[i];
    for (const k of s.karts) {
      const id = k.id;
      // finite
      if (![k.x, k.y, k.z, k.heading, k.speed].every(Number.isFinite)) {
        finiteBad++; continue;
      }
      // speed window
      if (Math.abs(k.speed) > maxSpeed * 1.3) speedBad++;
      // progress monotonic (only while moving and not spinning)
      if (i > 0 && Math.abs(k.speed) > 5) {
        const prev = samples[i - 1].karts.find((p) => p.id === id);
        // lap wrap (progress 0.995 -> 0.000 when lap increments) is NORMAL —
        // never flag a regression across a lap boundary
        if (prev && k.lap === prev.lap && k.progress < prev.progress - 0.05) progressBad++;
      }
      // lap
      if (i > 0) {
        const prev = samples[i - 1].karts.find((p) => p.id === id);
        if (prev && k.lap - prev.lap > 1) lapBad++;
      }
      // heading vs tangent (needs path)
      if (trackPaths && Math.abs(k.speed) > 5 && !k.spin) {
        const tan = tangentAt(k.progress);
        if (tan) {
          headingTotal++;
          const hx = Math.sin(k.heading), hz = Math.cos(k.heading);
          const dot = hx * tan.x + hz * tan.z;
          if (dot < 0.5) headingBad++;
        }
      }
      // lateral offset (needs path)
      if (trackPaths && !k.spin) {
        const tan = tangentAt(k.progress);
        const pt = pointAt(k.progress);
        if (tan && pt) {
          latTotal++;
          const ox = k.x - pt.x, oz = k.z - pt.z;
          const lateral = Math.abs(ox * tan.z - oz * tan.x);
          if (lateral > halfW + 6) latBad++; // +6m soft margin for runoff
        }
      }
      // stuck
      if (k.finished || k.spin) { stuckT[id] = 0; continue; }
      if (Math.abs(k.speed) < 1) {
        stuckT[id] = (stuckT[id] || 0) + s.t - (samples[i - 1]?.t || s.t) + (samples[i - 1]?.t || s.t) - (samples[i - 1]?.t || s.t);
        // simpler: count sample gaps
        if (i > 0) stuckT[id] = (stuckT[id] || 0) + (s.t - samples[i - 1].t);
        if (stuckT[id] >= 2.5) { stuck[id] = { t: s.t.toFixed(1), x: k.x.toFixed(1), z: k.z.toFixed(1) }; }
      } else {
        stuckT[id] = 0;
      }
    }
  }

  push('finite-position', finiteBad === 0, finiteBad ? `${finiteBad} samples non-finite` : 'all finite');
  push('speed-window', speedBad === 0, speedBad ? `${speedBad} over max*1.3` : 'ok');
  push('progress-monotonic', progressBad === 0, progressBad ? `${progressBad} regressions >0.05` : 'ok');
  push('lap-delta', lapBad === 0, lapBad ? `${lapBad} lap jumps >1` : 'ok');
  push('heading-vs-tangent', headingBad === 0, trackPaths ? `${headingBad}/${headingTotal} wrong-way samples` : 'skipped (no --paths)');
  push('lateral-offset', latBad === 0, trackPaths ? `${latBad}/${latTotal} off-road samples` : 'skipped (no --paths)');
  const stuckList = Object.entries(stuck);
  push('stuck', stuckList.length === 0, stuckList.length ? stuckList.map(([id, v]) => `kart${id}@${v.t}s (${v.x},${v.z})`).join('; ') : 'no stuck');
  return results;
}

// ---- main ----
(async () => {
  const log = (...a) => { console.log(...a); try { fs.appendFileSync(path.join(OUT, 'runner.log'), a.join(' ') + '\n'); } catch {} };
  const { chromium } = require(process.env.NODE_PATH
    ? path.join(process.env.NODE_PATH, 'playwright')
    : 'playwright');
  const browser = await chromium.launch({
    args: ['--no-sandbox', '--disable-dev-shm-usage', '--enable-unsafe-swiftshader',
      '--use-gl=angle', '--use-angle=swiftshader'],
  });
  const page = await browser.newPage({ viewport: { width: 1280, height: 800 } });
  const samples = [];
  const startedAt = Date.now();

  try {
    await page.route('**fonts.googleapis.com/**', (r) => r.abort());
    await page.route('**fonts.gstatic.com/**', (r) => r.abort());

    log(`URL: ${URL}`);
    log('goto...');
    await page.goto(URL, { waitUntil: 'domcontentloaded', timeout: 45000 });
    log('goto ok');

    // wait for QA hook
    let ready = false;
    for (let i = 0; i < 40; i++) {
      ready = await page.evaluate(() => !!(
        window.__sk3d && window.__sk3d.raceManager && window.__sk3d.raceManager.karts
      )).catch(() => false);
      if (ready) break;
      await new Promise((r) => setTimeout(r, 500));
    }
    if (!ready) throw new Error('window.__sk3d.raceManager not available');
    log('QA hook ready');

    // f0 — pre-race (grid/countdown)
    // SwiftShader: the first render can take 20-60s real; capturing before it
    // yields an empty canvas (frames critic: "no kart, void"). Wait for the
    // renderer to have drawn at least one frame.
    try {
      for (let i = 0; i < 60; i++) {
        const drawn = await page.evaluate(() => {
          const r = window.__sk3d && window.__sk3d.renderer;
          return r && r.info && r.info.render ? r.info.render.frame : 0;
        }).catch(() => 0);
        if (drawn > 0) break;
        await new Promise(r => setTimeout(r, 1500));
      }
    } catch {}
    const f0 = path.join(OUT, 'f0.png');
    log('f0 screenshot...');
    await forceCam();
    await page.screenshot({ path: f0, timeout: 60000 });
    log('f0 (pre-race):', f0);

    // start race
    const hasSkip = await page.evaluate(() => typeof window.__sk3d.skipCountdown === 'function').catch(() => false);
    if (SKIP_CD && hasSkip) {
      await page.evaluate(() => window.__sk3d.skipCountdown());
      log('skipCountdown: yes');
    } else {
      log('skipCountdown: no (waiting real countdown)');
    }

    // hold a key (e.g. ArrowUp) so the PLAYER kart also moves in headless —
    // otherwise only AI karts are motion subjects
    if (HOLD_KEY) {
      await page.keyboard.down(HOLD_KEY);
      log(`holding key: ${HOLD_KEY}`);
    }

    // Resilient screenshot: SwiftShader WebGL renders ~1-2fps and a
    // mid-race canvas capture can take 60-180s (see headless-screenshot-capture).
    // A failed frame is logged, never fatal — telemetry must survive.
    // Force a chase cam right before every shot (--cam-behind): in
    // SwiftShader the camera lerp is dt-based and takes MINUTES real-time to
    // catch the player (frames come out as blank sky / menu-showcase void).
    // Function declarations so the f0 block above can call them (hoisting).
    async function forceCam() {
      if (!CAM_BEHIND) return;
      try {
        await page.evaluate(() => {
          const cam = window.__sk3d.camera;
          const pk = window.__sk3d.playerKart ? window.__sk3d.playerKart() : null;
          if (cam && pk) {
            const st = pk.state;
            const q = pk.group.quaternion;
            const fx = 2 * (q.x * q.z + q.w * q.y);
            const fy = 2 * (q.y * q.z - q.w * q.x);
            const fz = 1 - 2 * (q.x * q.x + q.y * q.y);
            cam.position.set(st.position.x - fx * 8, st.position.y + 3.2, st.position.z - fz * 8);
            cam.lookAt(st.position.x + fx * 4, st.position.y + 1.2, st.position.z + fz * 4);
            cam.fov = 68;
            cam.updateProjectionMatrix();
          }
        }).catch(() => {});
      } catch {}
    }
    // Resilient screenshot: SwiftShader WebGL renders ~1-2fps and a
    // mid-race canvas capture can take 60-180s (see headless-screenshot-capture).
    // A failed frame is logged, never fatal — telemetry must survive.
    async function capture(name, atSec) {
      await forceCam();
      const f = path.join(OUT, name);
      try {
        log(`${name} screenshot (t=${atSec}s)...`);
        await page.screenshot({ path: f, timeout: 180000 });
        log(`${name}:`, f);
        return true;
      } catch (e) {
        log(`WARN: ${name} screenshot failed: ${e.message}`);
        return false;
      }
    };

    // f1 — early race, ONLY once a kart is actually MOVING (speed gate).
    // In SwiftShader the game clock advances ~0.05-0.1s per real second, so
    // wall-time waits capture the launch phase (speed ~2 m/s) and the critic
    // reads "not moving" — gate on real speed instead.
    if (SPEED_GATE > 0) {
      let gated = false;
      for (let i = 0; i < 150 && !gated; i++) {
        const maxSpeed = await page.evaluate(() => Math.max(0, ...(window.__sk3d.raceManager.karts || []).map((k) => Math.abs(k.state.speed)))).catch(() => 0);
        if (maxSpeed >= SPEED_GATE) { log(`speed gate ok: ${maxSpeed.toFixed(1)} m/s`); gated = true; }
        else await new Promise((r) => setTimeout(r, 2000));
      }
      if (!gated) log('WARN: speed gate not reached in 300s — capturing anyway');
    } else {
      await new Promise((r) => setTimeout(r, 4000));
    }
    await capture('f1.png', 'speed-gated');

    // sample + frames
    let frameIdx = 2;
    const t0 = Date.now();
    while (Date.now() - t0 < 26000) {
      const elapsed = (Date.now() - t0) / 1000;
      const snap = await page.evaluate(() => {
        const rm = window.__sk3d.raceManager;
        const st = window.__sk3d.getState ? window.__sk3d.getState() : null;
        return {
          t: rm.elapsed,
          state: st,
          frameN: window.__qaFrameN || 0,
          karts: (rm.karts || []).map((k, i) => ({
            id: i,
            x: k.state.position.x, y: k.state.position.y, z: k.state.position.z,
            heading: k.state.heading, speed: k.state.speed,
            progress: k.state.progress01, lap: k.state.lap,
            offRoad: k.state.offRoad, spin: k.state.spinOut,
            finished: !!k.finished,
          })),
        };
      }).catch((e) => ({ error: String(e) }));
      samples.push({ wallT: elapsed, ...snap });

      if (frameIdx <= FRAMES && elapsed >= 14 + (frameIdx - 2) * 8) {
        await capture(`f${frameIdx}.png`, `~${elapsed.toFixed(0)}s`);
        frameIdx++;
      }
      await new Promise((r) => setTimeout(r, SAMPLE_MS));
    }
    // fN — final mid-race frame if not yet captured
    if (frameIdx <= FRAMES) {
      await capture(`f${frameIdx}.png`, '~28s');
    }

    // telemetry out
    const telFile = path.join(OUT, 'telemetry.jsonl');
    fs.writeFileSync(telFile, samples.map((s) => JSON.stringify(s)).join('\n') + '\n');
    log('telemetry:', telFile, samples.length, 'samples');

    // invariants
    const inv = checkInvariants(samples);
    const okN = inv.filter((r) => r.ok).length;

    // report
    const lines = [];
    lines.push('# Motion QA Report');
    lines.push('');
    lines.push(`URL: ${URL}`);
    lines.push(`Track: ${TRACK} | Paths: ${PATHS_MOD || 'none'} | Samples: ${samples.length} | Frames: f0..f${frameIdx}`);
    lines.push(`Real elapsed: ${((Date.now() - startedAt) / 1000).toFixed(0)}s`);
    lines.push('');
    lines.push('## PROBE — invariantes');
    lines.push('');
    for (const r of inv) lines.push(`- [${r.ok ? 'PASS' : 'FAIL'}] ${r.name}: ${r.detail}`);
    lines.push('');
    lines.push(`**${okN}/${inv.length} invariantes OK**`);
    lines.push('');
    lines.push('## FRAMES');
    lines.push('');
    lines.push('f0 = pré-corrida (grid), f1..fN = mid-race em movimento. Rodar o STRICT CRITIC de movimento (skill game-visual-motion-critic) nos frames f1..fN.');
    fs.writeFileSync(path.join(OUT, 'motion-report.md'), lines.join('\n'));

    console.log('\n' + lines.join('\n'));
    log(`RESULT: ${okN}/${inv.length} invariantes OK — ${okN === inv.length ? 'PASS' : 'FAIL'}`);
    await browser.close();
    process.exit(okN === inv.length ? 0 : 2);
  } catch (e) {
    console.error('RUNNER ERROR:', e && e.stack ? e.stack : e);
    try { fs.appendFileSync(path.join(OUT, 'runner.log'), 'RUNNER ERROR: ' + (e && e.stack ? e.stack : e) + '\n'); } catch {}
    await browser.close().catch(() => {});
    process.exit(1);
  }
})().catch((e) => {
  console.error('FATAL:', e && e.stack ? e.stack : e);
  process.exit(1);
});
