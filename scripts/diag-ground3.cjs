// Diag: raycast na área de chão oliva (y=330, x=420) chase real
const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch({ args: ['--use-gl=angle','--use-angle=vulkan','--no-sandbox','--mute-audio'] });
  const page = await (await browser.newContext({ viewport: { width: 960, height: 540 } })).newPage();
  await page.addInitScript(() => localStorage.clear());
  await page.goto(process.argv[2] + '/?demo&track=2', { waitUntil: 'domcontentloaded', timeout: 120000 });
  await page.waitForFunction(() => window.__sk3d && window.__sk3d.raceManager && window.__sk3d.raceManager.phase === 'race', null, { timeout: 180000 });
  await page.waitForTimeout(10000);
  const report = await page.evaluate(async () => {
    const THREE = await import('/node_modules/three/build/three.module.js');
    const scene = window.__sk3d.scene, cam = window.__sk3d.camera;
    // NDC: x=420/960*2-1=-0.125, y=330/540*2-1=0.222
    const ray = new THREE.Raycaster();
    ray.setFromCamera(new THREE.Vector2(-0.125, 0.222), cam);
    const hits = [];
    scene.traverse((o) => { if (o.isMesh) { const r = ray.intersectObject(o, false); if (r.length) hits.push(...r); } });
    hits.sort((a, b) => a.distance - b.distance);
    return hits.slice(0, 3).map(h => {
      const mats = Array.isArray(h.object.material) ? h.object.material : [h.object.material];
      const m = mats[0];
      return { d: Math.round(h.distance), col: m && m.color ? '#' + m.color.getHexString() : null, map: !!(m && m.map), inst: !!h.object.isInstancedMesh, p: [Math.round(h.point.x), Math.round(h.point.y), Math.round(h.point.z)] };
    });
  });
  console.log(JSON.stringify(report));
  await browser.close();
})();
