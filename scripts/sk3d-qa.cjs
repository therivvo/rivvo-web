// Headless Chromium QA v3 — Super Kart 3D.js backwards-driving fix (integration)
// Usage: NODE_PATH=/home/jarvis/.hermes/node/lib/node_modules node scripts/sk3d-qa.cjs
const { chromium } = require('playwright');
const fs = require('fs');
const OUT = '/tmp/sk3d-qa';
fs.mkdirSync(OUT, { recursive: true });
const log = (...a) => console.log(`[${new Date().toISOString().slice(11,19)}] ${a.join(' ')}`);
setTimeout(() => { log('WATCHDOG 900s'); process.exit(3); }, 900000);

const FLAGS = ['--no-sandbox','--disable-dev-shm-usage','--enable-unsafe-swiftshader','--use-gl=angle',
  '--use-angle=swiftshader','--disable-frame-rate-limit','--disable-gpu-vsync',
  '--disable-background-timer-throttling','--disable-renderer-backgrounding','--mute-audio'];

function dotFor(k, rm) {
  const ks = (k.state && 'speed' in k.state) ? k.state : k;
  try {
    const t = rm.track.path.getTangentAt(Math.min(0.999, Math.max(0.001, ks.progress01 || 0)));
    return { dot: Math.sin(ks.heading || 0) * t.x + Math.cos(ks.heading || 0) * t.z, prog: ks.progress01 || 0, lap: ks.lap || 0, speed: ks.speed || 0, spin: !!ks.spinOut };
  } catch (e) { return { dot: null, prog: 0, lap: 0, speed: 0, spin: false }; }
}

(async () => {
  const pageErrors = [], consoleErrors = [];
  const browser = await chromium.launch({ args: FLAGS });
  const ctx = await browser.newContext({ viewport: { width: 800, height: 600 } });
  const page = await ctx.newPage();
  page.setDefaultTimeout(20000);
  await page.route('**fonts.googleapis.com/**', r => r.abort());
  await page.route('**fonts.gstatic.com/**', r => r.abort());
  page.on('pageerror', e => { const m = String((e && e.stack) || e); pageErrors.push(m); log('PAGEERROR:', m.slice(0, 220)); });
  page.on('console', m => { if (m.type() === 'error') { consoleErrors.push(m.text()); log('CONSOLE-ERR:', m.text().slice(0, 220)); } });
  page.on('crash', () => log('PAGE CRASHED'));

  const summary = {};
  for (const trackId of [1, 2]) {
    const url = trackId === 1 ? 'http://localhost:3457/?test' : 'http://localhost:3457/?test&track=2';
    log(`=== TRACK ${trackId}: ${url} ===`);
    const resp = await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 40000 }).then(r => r && r.status()).catch(e => 'GOTO_ERR ' + e.message.split('\n')[0]);
    log('goto:', resp);
    const booted = await page.waitForFunction(() => window.__sk3d && window.__sk3d.raceManager && window.__sk3d.raceManager.karts && window.__sk3d.raceManager.karts.length > 0, null, { timeout: 90000, polling: 1500 }).then(() => true).catch(() => false);
    log('booted:', booted);
    if (!booted) { summary[trackId] = { booted: false }; continue; }
    // QA hook: fast-forward the 3-2-1 countdown (headless rAF is too slow)
    const skipped = await page.evaluate(() => { if (window.__sk3d.skipCountdown) { window.__sk3d.skipCountdown(); return true; } return false; }).catch(() => false);
    log('countdown skipped:', skipped);
    // AUDIT (Jarvis QA loop 2026-08-11): SwiftShader advances the game clock
    // ~0.05-0.1s per real second — the old elapsed>0.5 gate timed out on
    // slow frames (race never "started" in 90s real). Gate on actual kart
    // speed with a generous timeout instead.
    const started = await page.waitForFunction(() => { const rm = window.__sk3d.raceManager; return rm && rm.karts && rm.karts.some(k => Math.abs((k.state && k.state.speed) || 0) > 8); }, null, { timeout: 240000, polling: 1500 }).then(() => true).catch(() => false);
    log('race started:', started);

    // rAF rate probe (game-time/sec) — MUST resolve even if rAF stalls
    const fps = await page.evaluate(() => new Promise(res => {
      let n = 0; const t0 = performance.now();
      function tick() { n++; if (performance.now() - t0 < 3000) requestAnimationFrame(tick); else res((n / 3).toFixed(1)); }
      setTimeout(() => res(n ? (n / 3).toFixed(1) : 'stalled'), 6000);
      requestAnimationFrame(tick);
    })).catch(e => 'ERR ' + String(e).slice(0, 60));
    log('rAF fps ~', fps);

    const tr = { backwards: [], reverse: [], maxSpeed: 0, lapsSeen: {}, restart: null, samples: 0 };
    const bwd = new Map();
    const SAMPLES = trackId === 1 ? 22 : 16; // ~4.5min track1, ~3min track2 (real)
    for (let s = 0; s < SAMPLES; s++) {
      await new Promise(r => setTimeout(r, 4000));
      const snap = await page.evaluate(() => {
        const rm = window.__sk3d && window.__sk3d.raceManager;
        if (!rm) return null;
        const arr = [];
        for (const k of (rm.karts || [])) {
          const ks = (k.state && 'speed' in k.state) ? k.state : k;
          arr.push({ isPlayer: !!k.isPlayer, speed: +(ks.speed || 0).toFixed(2), lap: ks.lap || 0, progress01: +((ks.progress01 || 0)).toFixed(4), spinOut: !!ks.spinOut });
        }
        return { elapsed: rm.elapsed, karts: arr, standings: (() => { try { return rm.getStandings().map(x => x.position); } catch (e) { return []; } })() };
      }).catch(() => null);
      if (!snap) continue;
      tr.samples++;
      for (let i = 0; i < snap.karts.length; i++) {
        const k = snap.karts[i];
        tr.maxSpeed = Math.max(tr.maxSpeed, Math.abs(k.speed));
        const d = await page.evaluate((idx) => {
          const rm = window.__sk3d.raceManager;
          const kk = rm.karts[idx];
          const ks = (kk.state && 'speed' in kk.state) ? kk.state : kk;
          try {
            const t = rm.track.path.getTangentAt(Math.min(0.999, Math.max(0.001, ks.progress01 || 0)));
            return { dot: Math.sin(ks.heading || 0) * t.x + Math.cos(ks.heading || 0) * t.z, prog: ks.progress01 || 0 };
          } catch (e) { return { dot: null, prog: 0 }; }
        }, i).catch(() => ({ dot: null, prog: 0 }));
        if (d.dot !== null && d.dot < -0.45 && Math.abs(k.speed) > 8) {
          const key = i;
          if (!bwd.has(key)) bwd.set(key, { t: snap.elapsed, minDot: d.dot });
          else bwd.get(key).minDot = Math.min(bwd.get(key).minDot, d.dot);
        } else if (bwd.has(i)) {
          const ep = bwd.get(i); bwd.delete(i);
          if (snap.elapsed - ep.t >= 0.7) tr.backwards.push({ kart: i, from: +ep.t.toFixed(1), to: +snap.elapsed.toFixed(1), minDot: +ep.minDot.toFixed(2) });
        }
        if (k.speed < -5) tr.reverse.push({ kart: i, t: +snap.elapsed.toFixed(1), v: k.speed });
        tr.lapsSeen[i] = Math.max(tr.lapsSeen[i] || 0, k.lap);
      }
      if (s % 6 === 0) log(`  t=${snap.elapsed.toFixed(1)}s karts=[${snap.karts.map(k => k.speed.toFixed(0)).join(',')}] laps=${snap.karts.map(k => k.lap).join(',')} stand=${snap.standings.join(',')}`);
    }
    // restart test
    const restarted = await page.evaluate(() => { const rm = window.__sk3d.raceManager; if (rm && typeof rm.restart === 'function') { rm.restart(); return true; } return false; }).catch(() => false);
    log('restart called:', restarted);
    await new Promise(r => setTimeout(r, 10000));
    const afterRestart = await page.evaluate(() => { const rm = window.__sk3d.raceManager; return rm ? { elapsed: rm.elapsed, karts: rm.karts.length } : null; }).catch(() => null);
    log('after restart:', JSON.stringify(afterRestart));
    tr.restart = { called: restarted, after: afterRestart };
    summary[trackId] = tr;
  }

  log('=== SUMMARY ===');
  console.log(JSON.stringify({ summary, pageErrors, consoleErrors }, null, 1));
  fs.writeFileSync('/tmp/sk3d-qa/result.json', JSON.stringify({ summary, pageErrors, consoleErrors }, null, 1));
  const anyBackwards = Object.values(summary).some(t => t && Array.isArray(t.backwards) && t.backwards.length > 0);
  const anyErrors = pageErrors.length > 0 || consoleErrors.filter(e => !e.includes('Failed to load resource')).length > 0;
  log('RESULT:', anyBackwards ? 'BACKWARDS-DETECTED' : (anyErrors ? 'ERRORS' : 'PASS'));
  await browser.close();
  process.exit(anyBackwards ? 2 : (anyErrors ? 1 : 0));
})();
