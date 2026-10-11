// Active-race capture for SK3D AAA-2 round (baseline + post-change).
// Waits for state=racing (skipping countdown), collects N spaced frames per
// track + renderer.info, saves PNGs + metrics JSON.
// Usage: NODE_PATH=/home/jarvis/.hermes/node/lib/node_modules \
//   CAPTURE_OUT=/home/jarvis/.cache/sk3d-aaa2/baseline timeout 900 node scripts/capture-active.cjs
const { chromium } = require('playwright');
const fs = require('fs');
const OUT = process.env.CAPTURE_OUT || '/tmp/sk3d-active/';
const FRAMES = Number(process.env.CAPTURE_FRAMES || 4);
fs.mkdirSync(OUT, { recursive: true });
const log = (...a) => console.log(`[${new Date().toISOString().slice(11, 19)}]`, ...a);

const FLAGS = ['--no-sandbox', '--disable-dev-shm-usage', '--enable-unsafe-swiftshader', '--use-gl=angle',
  '--use-angle=swiftshader', '--disable-frame-rate-limit', '--disable-gpu-vsync',
  '--disable-background-timer-throttling', '--disable-renderer-backgrounding', '--mute-audio'];

(async () => {
  const browser = await chromium.launch({ args: FLAGS });
  const summary = { tracks: {} };
  const ctx = await browser.newContext({
    // Lição SK3D (memória): headless NÃO vê GPU real — SwiftShader único;
    // capture 640×400 p/ não OOM e p/ o screenshot caber num frame lento.
    viewport: { width: 640, height: 400 },
    userAgent: 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/126 Safari/537.36',
  });
  const page = await ctx.newPage();
  page.setDefaultTimeout(30000);
  await page.route('**fonts.googleapis.com/**', (r) => r.abort());
  await page.route('**fonts.gstatic.com/**', (r) => r.abort());
  const pageErrors = [];
  page.on('pageerror', (e) => { pageErrors.push(String(e && e.stack || e).slice(0, 300)); });

  for (const trackId of [1, 2]) {
    const url = trackId === 1 ? 'http://localhost:3457/?demo' : 'http://localhost:3457/?demo&track=2';
    log(`track ${trackId}: ${url}`);
    await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 });
    const booted = await page.waitForFunction(() => window.__sk3d && window.__sk3d.raceManager &&
      window.__sk3d.raceManager.karts && window.__sk3d.raceManager.karts.length > 0,
    null, { timeout: 120000, polling: 1000 }).then(() => true).catch(() => false);
    log('booted:', booted);
    if (!booted) { summary.tracks[trackId] = { booted: false }; continue; }
    // skip countdown → racing fast
    let st = await page.evaluate(() => { try { window.__sk3d.skipCountdown(); return window.__sk3d.getState(); } catch { return '?'; } });
    log('state after skip:', st);
    const racing = await page.waitForFunction(() => {
      const s = window.__sk3d;
      if (s && s.getState() === 'race') return true;
      try { s.skipCountdown(); } catch {}
      return false;
    }, null, { timeout: 120000, polling: 800 }).then(() => true).catch(() => false);
    log('racing:', racing);
    if (!racing) { summary.tracks[trackId] = { booted: true, racing: false }; continue; }
    const frames = [];
    for (let f = 0; f < FRAMES; f++) {
      // wait so the race progresses between frames (game clock is ~slow-mo)
      await page.waitForTimeout(6000);
      const shot = `${OUT}t${trackId}_f${f}.png`;
      // timeout 120s: um frame sob SwiftShader em corrida pode levar dezenas
      // de segundos (lição R-sessões anteriores: timeouts ×20 no headless).
      await page.screenshot({ path: shot, timeout: 120000 });
      const info = await page.evaluate(() => {
        const s = window.__sk3d;
        const r = s.renderer.info;
        const karts = s.raceManager.karts.map((k) => ({
          n: k.characterName, prog: +(k.state.progress01 || 0).toFixed(3),
          spd: Math.round(k.state.speed || 0),
        }));
        let camPos = null, playerProg = null;
        try {
          camPos = s.camera.position.toArray().map((v) => +v.toFixed(1));
          playerProg = +(s.playerKart().state.progress01 || 0).toFixed(3);
        } catch {}
        return { calls: r.render.calls, tris: r.render.triangles, geoms: r.memory.geometries, texs: r.memory.textures, karts, camPos, playerProg };
      }).catch((e) => ({ err: String(e).slice(0, 120) }));
      frames.push({ shot, info });
      log(`frame ${f}: prog=${info.playerProg} calls=${info.calls} tris=${info.tris}`);
    }
    summary.tracks[trackId] = { booted: true, racing: true, frames, pageErrors: pageErrors.splice(0) };
  }
  fs.writeFileSync(`${OUT}metrics.json`, JSON.stringify(summary, null, 1));
  log('DONE →', `${OUT}metrics.json`);
  await browser.close();
})().catch((e) => { console.error('FATAL', e); process.exit(1); });
