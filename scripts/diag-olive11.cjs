// Diagnóstico 11: instanceColor dos towers — quais cores por row
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
      if (!m || !m.map || m.fog !== false || !o.instanceColor) return;
      // média das instance colors
      const arr = o.instanceColor.array;
      let r = 0, g = 0, b = 0, n = o.count;
      for (let i = 0; i < n; i++) { r += arr[i*3]; g += arr[i*3+1]; b += arr[i*3+2]; }
      out.push({ matColor: '#' + m.color.getHexString(), avgInst: [Math.round(r/n*255), Math.round(g/n*255), Math.round(b/n*255)], count: n, toneMapped: m.toneMapped });
    });
    return out;
  });
  console.log(JSON.stringify(report, null, 1));
  await browser.close();
})();
