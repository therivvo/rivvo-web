// Diagnóstico 16: grid de pixels da tela inteira para mapear a banda oliva
const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch({ args: ['--use-gl=angle','--use-angle=vulkan','--no-sandbox','--mute-audio'] });
  const page = await (await browser.newContext({ viewport: { width: 960, height: 540 } })).newPage();
  await page.addInitScript(() => localStorage.clear());
  await page.goto(process.argv[2] + '/?test&track=2', { waitUntil: 'domcontentloaded', timeout: 120000 });
  await page.waitForFunction(() => window.__sk3d, null, { timeout: 120000 });
  await page.waitForTimeout(4000);
  const report = await page.evaluate(() => {
    const { scene, camera, renderer } = window.__sk3d;
    const kart = window.__sk3d.playerKart();
    const p = kart.state.position;
    window.__freezeCam = true;
    camera.position.set(p.x, 2.8, p.z + 4.3);
    camera.lookAt(p.x, 2.0, p.z - 10);
    renderer.render(scene, camera);
    const gl = renderer.getContext();
    const px = new Uint8Array(4);
    const rows = [];
    for (let y = 380; y >= 160; y -= 20) {
      const row = [];
      for (let x = 200; x <= 760; x += 40) {
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
