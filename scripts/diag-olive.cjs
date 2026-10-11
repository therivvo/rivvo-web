// Diagnóstico: qual mesh produz a banda oliva no horizonte do Neon City?
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
      if (!o.isMesh && !o.isInstancedMesh) return;
      const mat = o.material;
      const mats = Array.isArray(mat) ? mat : [mat];
      for (const m of mats) {
        if (!m || !m.color) continue;
        const c = m.color;
        // procurar materiais esverdeados/oliva (g alto, b baixo relativo)
        if (c.g > 0.25 && c.g > c.b * 1.6 && c.r > c.b * 0.9) {
          out.push({ name: o.name || '(unnamed)', type: o.isInstancedMesh ? 'inst' : 'mesh', color: '#' + c.getHexString(), fog: m.fog, transparent: m.transparent, opacity: m.opacity, pos: o.position ? [o.position.x|0, o.position.y|0, o.position.z|0] : null });
        }
      }
    });
    return out.slice(0, 40);
  });
  console.log(JSON.stringify(report, null, 1));
  await browser.close();
})();
