// Diag: cor média do terreno Neon renderizado — sample de pixels em área de chão distante
const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch({ args: ['--use-gl=angle','--use-angle=vulkan','--no-sandbox','--mute-audio'] });
  const page = await (await browser.newContext({ viewport: { width: 960, height: 540 } })).newPage();
  await page.addInitScript(() => localStorage.clear());
  await page.goto(process.argv[2] + '/?demo&track=2', { waitUntil: 'domcontentloaded', timeout: 120000 });
  await page.waitForFunction(() => window.__sk3d && window.__sk3d.raceManager && window.__sk3d.raceManager.phase === 'race', null, { timeout: 180000 });
  await page.waitForTimeout(10000);
  const report = await page.evaluate(() => {
    const { scene, camera, renderer } = window.__sk3d;
    renderer.render(scene, camera);
    const gl = renderer.getContext();
    const px = new Uint8Array(4);
    // grid na metade superior-central (onde a faixa oliva do chão aparece)
    const rows = [];
    for (let y = 360; y >= 240; y -= 30) {
      const row = [];
      for (let x = 300; x <= 660; x += 60) {
        gl.readPixels(x, y, 1, 1, gl.RGBA, gl.UNSIGNED_BYTE, px);
        row.push(`${px[0]},${px[1]},${px[2]}`);
      }
      rows.push(`y=${y}: ${row.join(' | ')}`);
    }
    return rows.join('\n');
  });
  console.log(report);
  await browser.close();
})();
