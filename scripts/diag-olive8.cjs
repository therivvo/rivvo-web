// Diagnóstico 8: raycast fino com THREE importado do bundle do jogo (via módulo) + hit exato na banda oliva
const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch({ args: ['--use-gl=angle','--use-angle=vulkan','--no-sandbox','--mute-audio'] });
  const page = await (await browser.newContext({ viewport: { width: 960, height: 540 } })).newPage();
  await page.addInitScript(() => localStorage.clear());
  await page.goto(process.argv[2] + '/?demo&track=2', { waitUntil: 'domcontentloaded', timeout: 120000 });
  await page.waitForFunction(() => window.__sk3d && window.__sk3d.raceManager && window.__sk3d.raceManager.phase === 'race', null, { timeout: 180000 });
  await page.waitForTimeout(8000);
  const report = await page.evaluate(async () => {
    const THREE = await import('/node_modules/three/build/three.module.js');
    const scene = window.__sk3d.scene, cam = window.__sk3d.camera;
    const out = [];
    for (const [nx, ny] of [[0.45, 0.42], [0.5, 0.45], [0.35, 0.4], [0.55, 0.5]]) {
      const ray = new THREE.Raycaster();
      ray.setFromCamera(new THREE.Vector2(nx, ny), cam);
      const hits = [];
      scene.traverse((o) => { if (o.isMesh) { const r = ray.intersectObject(o, false); if (r.length) hits.push(...r); } });
      hits.sort((a, b) => a.distance - b.distance);
      const h = hits[0];
      if (!h) { out.push({ ndc: [nx, ny], miss: true }); continue; }
      const mats = Array.isArray(h.object.material) ? h.object.material : [h.object.material];
      out.push({ ndc: [nx, ny], dist: Math.round(h.distance), name: h.object.name || '(unnamed)', colors: mats.filter(m => m && m.color).map(m => '#' + m.color.getHexString()), maps: mats.map(m => !!m.map), fog: mats.map(m => m.fog), emissive: mats.filter(m=>m.emissive).map(m => '#' + m.emissive.getHexString() + '@' + m.emissiveIntensity), point: h.point ? [Math.round(h.point.x), Math.round(h.point.y), Math.round(h.point.z)] : null });
    }
    return out;
  });
  console.log(JSON.stringify(report, null, 1));
  await browser.close();
})();
