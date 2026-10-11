// Diag 18: o sky dome está interceptando o ray a 537m? checar raio do domo + cor no horizonte
const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch({ args: ['--use-gl=angle','--use-angle=vulkan','--no-sandbox','--mute-audio'] });
  const page = await (await browser.newContext({ viewport: { width: 960, height: 540 } })).newPage();
  await page.addInitScript(() => localStorage.clear());
  await page.goto(process.argv[2] + '/?test&track=2', { waitUntil: 'domcontentloaded', timeout: 120000 });
  await page.waitForFunction(() => window.__sk3d, null, { timeout: 120000 });
  await page.waitForTimeout(4000);
  const report = await page.evaluate(() => {
    const scene = window.__sk3d.scene;
    const out = [];
    scene.traverse((o) => {
      if (!o.isMesh || !o.geometry) return;
      if (o.geometry.type === 'SphereGeometry' && o.geometry.parameters && o.geometry.parameters.radius > 400) {
        out.push({ radius: o.geometry.parameters.radius, y: o.position.y, mat: o.material.type, uniforms: o.material.uniforms ? Object.keys(o.material.uniforms) : null });
      }
    });
    return out;
  });
  console.log(JSON.stringify(report));
  await browser.close();
})();
