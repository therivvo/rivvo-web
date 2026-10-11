// Diagnóstico 2: raycast da câmera chase na direção do horizonte + amostra do terreno distante
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
      const m = o.material;
      const mats = Array.isArray(m) ? m : [m];
      for (const mat of mats) {
        if (!mat || !mat.color) continue;
        const hex = '#' + mat.color.getHexString();
        // concreto do chão: 0x4a4d5c base mas toonMaterial multiplica... procurar materiais com MAP concrete + qualquer cor
        if (mat.map && mat.map.image && mat.map.image.width === 64) { /* textureCap low? */ }
        out.push({ hex, map: !!mat.map, name: o.name || '-', fog: mat.fog !== false, emissive: mat.emissive ? '#' + mat.emissive.getHexString() : null, type: o.isInstancedMesh ? 'inst' : 'mesh' });
      }
    });
    // agrupar
    const uniq = {};
    for (const r of out) { const k = r.hex + '|' + r.map + '|' + r.fog; uniq[k] = (uniq[k] || 0) + 1; }
    return uniq;
  });
  console.log(JSON.stringify(report, null, 1));
  await browser.close();
})();
