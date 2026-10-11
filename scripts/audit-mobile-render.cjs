// Diagnostic only: compare mobile canvas/composer dimensions against a PNG screenshot.
let chromium;
try { ({ chromium } = require('playwright')); }
catch { ({ chromium } = require('/opt/pwtest/node_modules/playwright')); }
const fs = require('fs');
(async () => {
  const [url, outdir = 'qa-gpu-runner/mobile-render-probe'] = process.argv.slice(2);
  fs.mkdirSync(outdir, { recursive: true });
  const browser = await chromium.launch({
    executablePath: process.env.PLAYWRIGHT_EXECUTABLE_PATH || '/usr/bin/chromium',
    args: ['--use-gl=angle', '--use-angle=vulkan', '--no-sandbox', '--mute-audio'],
  });
  const ctx = await browser.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 3, hasTouch: true, isMobile: false });
  const page = await ctx.newPage();
  await page.addInitScript(() => localStorage.clear());
  await page.goto(`${url}/?demo&track=2`, { waitUntil: 'domcontentloaded', timeout: 120000 });
  await page.waitForTimeout(15000);
  const metrics = await page.evaluate(() => {
    const c = document.querySelector('canvas');
    const r = window.__sk3d?.renderer;
    const cam = window.__sk3d?.camera;
    const fx = window.__sk3d?.postFX;
    return {
      inner: [innerWidth, innerHeight],
      dpr: devicePixelRatio,
      canvas: c && { client: [c.clientWidth, c.clientHeight], backing: [c.width, c.height], rect: c.getBoundingClientRect().toJSON() },
      rendererSize: r && [r.domElement.clientWidth, r.domElement.clientHeight],
      drawingBuffer: r && [r.getContext().drawingBufferWidth, r.getContext().drawingBufferHeight],
      cameraAspect: cam?.aspect,
      quality: window.__sk3d?.renderReport?.(),
      composer: fx?.composer && { width: fx.composer.readBuffer?.width, height: fx.composer.readBuffer?.height },
      pageErrors: window.__pageErrors || [],
    };
  });
  fs.writeFileSync(`${outdir}/metrics.json`, JSON.stringify(metrics, null, 2));
  await page.screenshot({ path: `${outdir}/page.png`, fullPage: false });
  console.log(JSON.stringify(metrics));
  await browser.close();
})();
