// Diagnóstico 15: ler pixel real do WebGL canvas via preserveDrawingBuffer hack — usar gl.readPixels logo após render
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
    // centro-baixo da tela (banda oliva): x=480, y=540-230=310
    const pts = [[480, 310], [480, 270], [400, 300], [480, 200]];
    return pts.map(([x, y]) => {
      gl.readPixels(x, y, 1, 1, gl.RGBA, gl.UNSIGNED_BYTE, px);
      return { x, y, rgba: [px[0], px[1], px[2], px[3]] };
    });
  });
  console.log(JSON.stringify(report));
  await browser.close();
})();
