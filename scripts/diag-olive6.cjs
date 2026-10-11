// Diagnóstico 8: cor média do terreno em pixels renderizados — readPixels em pontos do chão distante
const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch({ args: ['--use-gl=angle','--use-angle=vulkan','--no-sandbox','--mute-audio'] });
  const page = await (await browser.newContext({ viewport: { width: 960, height: 540 } })).newPage();
  await page.addInitScript(() => localStorage.clear());
  await page.goto(process.argv[2] + '/?test&track=2', { waitUntil: 'domcontentloaded', timeout: 120000 });
  await page.waitForFunction(() => window.__sk3d, null, { timeout: 120000 });
  await page.waitForTimeout(4000);
  const report = await page.evaluate(() => {
    const scene = window.__sk3d.scene, cam = window.__sk3d.camera, r = window.__sk3d.renderer;
    const kart = window.__sk3d.playerKart();
    const p = kart.state.position;
    window.__freezeCam = true;
    cam.position.set(p.x, 40, p.z + 60);
    cam.lookAt(p.x, 8, p.z - 120);
    r.render(scene, cam);
    // projetar um ponto do terreno a 150m à frente e ler o pixel via raycast+cor do material*fog
    const THREE = window.__sk3d.scene.constructor.constructor; // hack inútil; usar raycast
    const dir = new (Object.getPrototypeOf(cam.position)).constructor(0, -0.21, -1).normalize();
    const ray = { origin: cam.position.clone(), direction: dir };
    // raycast manual via three já importado no módulo — usar scene.raycast não existe; usar Raycaster via window
    return { camPos: [Math.round(cam.position.x), Math.round(cam.position.y), Math.round(cam.position.z)] };
  });
  console.log(JSON.stringify(report));
  await browser.close();
})();
