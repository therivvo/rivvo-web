// Diag R21g: screenshot com postfx OFF (?test) — a faixa oliva persiste?
const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch({ args: ['--use-gl=angle','--use-angle=vulkan','--no-sandbox','--mute-audio'] });
  const page = await (await browser.newContext({ viewport: { width: 960, height: 540 } })).newPage();
  await page.addInitScript(() => localStorage.clear());
  await page.goto(process.argv[2] + '/?test&track=2', { waitUntil: 'domcontentloaded', timeout: 120000 });
  await page.waitForFunction(() => window.__sk3d && window.__sk3d.raceManager && window.__sk3d.raceManager.phase === 'race', null, { timeout: 180000 });
  await page.waitForTimeout(8000);
  await page.screenshot({ path: '/tmp/r21g-notestfx.png' });
  // amostra pixels do infield
  const px = await page.evaluate(() => {
    const c = document.querySelector('canvas');
    const gl = c.getContext('webgl2') || c.getContext('webgl');
    // preserveDrawingBuffer pode ser false; tenta readPixels via 2d copy
    const out = {};
    const cv2 = document.createElement('canvas');
    cv2.width = c.width; cv2.height = c.height;
    const g2 = cv2.getContext('2d');
    g2.drawImage(c, 0, 0);
    const pts = [[300, 350], [250, 400], [700, 300], [650, 260]];
    for (const [x, y] of pts) {
      const d = g2.getImageData(Math.floor(x * c.width / 960), Math.floor(y * c.height / 540), 1, 1).data;
      out[`${x},${y}`] = [d[0], d[1], d[2]];
    }
    return out;
  });
  console.log(JSON.stringify(px));
  await browser.close();
})().catch(e => { console.error(String(e).slice(0,300)); process.exit(1); });
