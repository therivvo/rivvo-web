// Diagnóstico 10: o mesh d4d3d6 é InstancedMesh? listar TODOS os meshes com fog:false + map
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
      if (!o.isMesh) return;
      const mats = Array.isArray(o.material) ? o.material : [o.material];
      for (const m of mats) {
        if (m && m.map && m.fog === false) {
          const chain = [];
          let p = o;
          while (p) { chain.push(p.name || p.type); p = p.parent; }
          out.push({ chain: chain.slice(0,3).join('<'), inst: !!o.isInstancedMesh, color: m.color ? '#' + m.color.getHexString() : null, toneMapped: m.toneMapped, geo: o.geometry.type, count: o.count || 1 });
          break;
        }
      }
    });
    // dedup por chain+color
    const u = {}; out.forEach(r => { u[r.chain + r.color + r.inst] = r; });
    return Object.values(u);
  });
  console.log(JSON.stringify(report, null, 1));
  await browser.close();
})();
