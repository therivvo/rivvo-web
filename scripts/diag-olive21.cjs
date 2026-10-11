// Diag 21: matColor das 4 rows de towers + qual row tem d4d3d6 (haze lerp)
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
      if (!o.isInstancedMesh) return;
      const mats = Array.isArray(o.material) ? o.material : [o.material];
      const m = mats[0];
      if (!m || !m.map || m.fog !== false) return;
      // hex do matColor
      const hex = m.color.getHexString();
      // janela média do map (window texture) já sabemos: parede 10162a
      out.push({ hex, count: o.count, toneMapped: m.toneMapped });
    });
    return out;
  });
  console.log(JSON.stringify(report));
  await browser.close();
})();
