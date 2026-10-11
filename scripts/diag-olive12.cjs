// Diagnóstico FINAL: ler pixels reais do canvas na região da banda oliva (toDataURL + canvas 2d)
const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch({ args: ['--use-gl=angle','--use-angle=vulkan','--no-sandbox','--mute-audio'] });
  const page = await (await browser.newContext({ viewport: { width: 960, height: 540 } })).newPage();
  await page.addInitScript(() => localStorage.clear());
  await page.goto(process.argv[2] + '/?demo&track=2', { waitUntil: 'domcontentloaded', timeout: 120000 });
  await page.waitForFunction(() => window.__sk3d && window.__sk3d.raceManager && window.__sk3d.raceManager.phase === 'race', null, { timeout: 180000 });
  await page.waitForTimeout(8000);
  const report = await page.evaluate(() => {
    const canvas = document.querySelector('canvas');
    // WebGL canvas: usar gl.readPixels não dá preserveDrawingBuffer; alternativa: screenshot do elemento via 2d draw
    const tmp = document.createElement('canvas');
    tmp.width = canvas.width; tmp.height = canvas.height;
    // fallback: reportar tamanho e deixar o screenshot do playwright falar
    return { cw: canvas.width, ch: canvas.height };
  });
  console.log(JSON.stringify(report));
  await page.screenshot({ path: process.argv[3] });
  await browser.close();
})();
