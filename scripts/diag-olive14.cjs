// Diagnóstico 14: o InstancedMesh d4d3d6 (21 instâncias) — onde estão as instâncias? escala? É o skyline row B?
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
      // sample das 5 primeiras matrizes
      const dummy = o.instanceMatrix; // só para ter fromArray? não — usar array direto
      const samples = [];
      const arr = o.instanceMatrix.array;
      for (let i = 0; i < Math.min(4, o.count); i++) {
        const e = arr; // base
        const off = i * 16;
        samples.push([Math.round(arr[off+12]), Math.round(arr[off+13]), Math.round(arr[off+14])]);
      }
      out.push({ color: '#' + m.color.getHexString(), count: o.count, samples, toneMapped: m.toneMapped, mapW: m.map.image.width });
    });
    return out;
  });
  console.log(JSON.stringify(report, null, 1));
  await browser.close();
})();
