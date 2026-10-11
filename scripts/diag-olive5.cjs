// Diagnóstico 5: ler a textura do concreto e computar cor média real
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
    let out = null;
    scene.traverse((o) => {
      if (!o.isMesh || out) return;
      const g = o.geometry;
      if (!g.boundingSphere) g.computeBoundingSphere();
      if (g.boundingSphere.radius <= 200) return;
      const m = o.material;
      const cv = m.map.image;
      const ctx2 = cv.getContext('2d');
      const d = ctx2.getImageData(0, 0, cv.width, cv.height).data;
      let r = 0, gg = 0, b = 0, n = 0;
      for (let i = 0; i < d.length; i += 4) { r += d[i]; gg += d[i+1]; b += d[i+2]; n++; }
      out = { size: cv.width + 'x' + cv.height, avg: [Math.round(r/n), Math.round(gg/n), Math.round(b/n)] };
    });
    return out;
  });
  console.log(JSON.stringify(report));
  await browser.close();
})();
