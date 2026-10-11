// Close-up probe das famílias de silhueta AAA-2 (v3, determinístico):
// modo ?test = main.js sobrescreve controles com input vazio por frame →
// após o GO os karts FICAM PARADOS no grid. Congela a câmera, dá o GO,
// fotografa com o pack estático.
// Usage: NODE_PATH=/home/jarvis/.hermes/node/lib/node_modules PROBE_OUT=/tmp/k.png node scripts/probe-karts.cjs
const { chromium } = require('playwright');
const OUT = process.env.PROBE_OUT || '/tmp/sk3d-karts.png';
const TRACK = process.env.PROBE_TRACK || '1';
const log = (...a) => console.log(new Date().toISOString().slice(11, 19), ...a);
const FLAGS = ['--no-sandbox', '--disable-dev-shm-usage', '--enable-unsafe-swiftshader', '--use-gl=angle',
  '--use-angle=swiftshader', '--disable-frame-rate-limit', '--disable-gpu-vsync',
  '--disable-background-timer-throttling', '--disable-renderer-backgrounding', '--mute-audio'];

(async () => {
  const browser = await chromium.launch({ args: FLAGS });
  const page = await browser.newPage({ viewport: { width: 1280, height: 800 } });
  page.setDefaultTimeout(30000);
  await page.route('**fonts.googleapis.com/**', (r) => r.abort());
  await page.route('**fonts.gstatic.com/**', (r) => r.abort());
  const errs = [];
  page.on('pageerror', (e) => errs.push(String(e).slice(0, 200)));
  const url = TRACK === '2' ? 'http://localhost:3457/?test&track=2' : 'http://localhost:3457/?test';
  await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 });
  await page.waitForFunction(() => window.__sk3d && window.__sk3d.raceManager &&
    window.__sk3d.raceManager.karts && window.__sk3d.raceManager.karts.length > 0,
  null, { timeout: 120000, polling: 1000 });
  // congela chase cam e enquadra o grid (posição lida AINDA no countdown)
  const info = await page.evaluate(() => {
    const s = window.__sk3d;
    window.__freezeCam = true; // QA hook REAL do main.js (linha ~1036)
    const karts = s.raceManager.karts;
    let cx = 0, cz = 0, cy = 0;
    for (const k of karts) { cx += k.group.position.x; cz += k.group.position.z; cy += k.group.position.y; }
    cx /= karts.length; cz /= karts.length; cy /= karts.length;
    const hdg = karts[0].state.heading;
    const fx = Math.sin(hdg), fz = Math.cos(hdg);
    const sx = fz, sz2 = -fx;
    // vista FRONTAL 3/4 elevada sobre o asfalto (offset lateral ≤1.2m)
    s.camera.position.set(cx + fx * 5.0 - sx * 1.2, cy + 1.55, cz + fz * 5.0 - sz2 * 1.2);
    s.camera.lookAt(cx - fx * 5, cy + 0.55, cz - fz * 5);
    return { n: karts.length, names: karts.map((k) => k.characterName) };
  });
  log('framed:', JSON.stringify(info));
  await page.evaluate(() => { try { window.__sk3d.skipCountdown(); } catch {} });
  await page.waitForFunction(() => window.__sk3d.getState() === 'race', null, { timeout: 60000, polling: 300 }).catch(() => {});
  log('race on — karts idle (?test empty controls)');
  await page.waitForTimeout(600); // deixa o primeiro frame pós-GO renderizar
  // PROBE_VIEW=high → vista ALTA/larga (pack inteiro); default = baixa.
  if (process.env.PROBE_VIEW === 'high') {
    await page.evaluate(() => {
      const s = window.__sk3d;
      const karts = s.raceManager.karts;
      let cx = 0, cz = 0, cy = 0;
      for (const k of karts) { cx += k.group.position.x; cz += k.group.position.z; cy += k.group.position.y; }
      cx /= karts.length; cz /= karts.length; cy /= karts.length;
      const hdg = karts[0].state.heading;
      const fx = Math.sin(hdg), fz = Math.cos(hdg);
      const sx = fz, sz2 = -fx;
      s.camera.position.set(cx + fx * 8.5 - sx * 4.5, cy + 3.4, cz + fz * 8.5 - sz2 * 4.5);
      s.camera.lookAt(cx - fx * 2, cy + 0.3, cz - fz * 2);
    });
    await page.waitForTimeout(300);
  }
  await page.screenshot({ path: OUT, timeout: 150000 });
  log('pageerrors:', errs.length, '| saved', OUT);
  await browser.close();
})().catch((e) => { console.error('FATAL', e); process.exit(1); });
