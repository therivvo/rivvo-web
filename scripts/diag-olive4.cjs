// Diagnóstico 4: amostrar cor de pixel do framebuffer na banda oliva + identificar terreno
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
    // achar o terreno (mesh grande com map, y ~0, PlaneGeometry 460)
    const found = [];
    scene.traverse((o) => {
      if (!o.isMesh) return;
      const g = o.geometry;
      if (!g || !g.boundingSphere) g.computeBoundingSphere();
      const r = g.boundingSphere.radius;
      // terreno = esfera gigante plana
      if (r > 200) {
        const mats = Array.isArray(o.material) ? o.material : [o.material];
        for (const m of mats) {
          if (!m || !m.color) continue;
          found.push({ name: o.name || '(unnamed)', radius: Math.round(r), color: '#' + m.color.getHexString(), map: !!m.map, mapRepeat: m.map && m.map.repeat ? [m.map.repeat.x, m.map.repeat.y] : null, fog: m.fog, emissive: m.emissive ? '#' + m.emissive.getHexString() + '/' + m.emissiveIntensity : null, roughness: m.roughness, envMapIntensity: m.envMapIntensity });
        }
      }
    });
    return found;
  });
  console.log(JSON.stringify(report, null, 1));
  await browser.close();
})();
