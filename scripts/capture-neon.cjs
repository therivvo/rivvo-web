// Quick Neon City capture (SwiftShader needs long boot + demo delay).
const { chromium } = require('playwright');
const OUT = process.env.CAPTURE_OUT || '/tmp/sk3d-shots/';
const LAUNCH = ['--no-sandbox', '--disable-dev-shm-usage', '--enable-unsafe-swiftshader', '--use-gl=angle', '--use-angle=swiftshader'];
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

(async () => {
  const browser = await chromium.launch({ args: LAUNCH });
  const page = await browser.newPage({ viewport: { width: 1280, height: 800 } });
  page.on('console', (m) => { if (/worldpropkit|error/i.test(m.text())) console.log('PAGE:', m.text()); });
  await page.goto('http://localhost:3457/?demo&track=2', { waitUntil: 'domcontentloaded', timeout: 60000 });
  console.log('loaded, waiting for demo autopilot...');
  await sleep(22000); // boot + demo auto-start + SwiftShader throttle
  const info = await page.evaluate(() => ({ state: window.__sk3d?.state, hasCanvas: !!document.querySelector('canvas') }));
  console.log('NEON state:', JSON.stringify(info));
  try {
    await page.screenshot({ path: OUT + 'neon-desktop.png', timeout: 90000 });
    console.log('NEON DESKTOP OK');
  } catch (e) { console.log('NEON DESKTOP FAIL:', e.message); }
  await browser.close();
})().catch((e) => { console.error('ERR', e.message); process.exit(1); });
