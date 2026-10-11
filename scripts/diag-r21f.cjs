// Diag R21f: raycast na faixa oliva MAS com todos os hits (não só 3) + filtrar o terreno (y=0)
const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch({ args: ['--use-gl=angle','--use-angle=vulkan','--no-sandbox','--mute-audio'] });
  const page = await (await browser.newContext({ viewport: { width: 960, height: 540 } })).newPage();
  await page.addInitScript(() => localStorage.clear());
  await page.goto(process.argv[2] + '/?demo&track=2', { waitUntil: 'domcontentloaded', timeout: 120000 });
  await page.waitForFunction(() => window.__sk3d && window.__sk3d.raceManager && window.__sk3d.raceManager.phase === 'race', null, { timeout: 180000 });
  await page.waitForTimeout(9000);
  const report = await page.evaluate(async () => {
    const THREE = await import('/node_modules/three/build/three.module.js');
    const scene = window.__sk3d.scene, cam = window.__sk3d.camera;
    const ray = new THREE.Raycaster();
    ray.setFromCamera(new THREE.Vector2(0.55, -0.25), cam);
    const hits = [];
    scene.traverse((o) => {
      if (!o.isMesh) return;
      // pular os decals próximos (pavimento/wet/pools) — queremos o que está ATRÁS
      const r = ray.intersectObject(o, false);
      for (const h of r) {
        const mats = Array.isArray(o.material) ? o.material : [o.material];
        const m = mats[0];
        hits.push({ d: Math.round(h.distance), y: Math.round(h.point.y), col: m && m.color ? '#' + m.color.getHexString() : null, map: !!(m && m.map), fog: m && m.fog, op: m && m.opacity, blend: m && m.blending, name: o.name || o.parent.name || o.type });
      }
    });
    hits.sort((a, b) => a.d - b.d);
    return hits.slice(0, 12);
  });
  console.log(JSON.stringify(report));
  await browser.close();
})().catch(e => { console.error(String(e).slice(0,300)); process.exit(1); });
