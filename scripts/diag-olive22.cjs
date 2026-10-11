// Diag 22: raycast na banda oliva (NDC 0.45,0.42) chase real — hits com nome de grupo pai
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
    const ray = new THREE.Raycaster();
    ray.setFromCamera(new THREE.Vector2(0.45, 0.42), cam);
    const hits = [];
    scene.traverse((o) => { if (o.isMesh) { const r = ray.intersectObject(o, false); if (r.length) hits.push(...r); } });
    hits.sort((a, b) => a.distance - b.distance);
    const h = hits[0];
    if (!h) return 'miss';
    const mats = Array.isArray(h.object.material) ? h.object.material : [h.object.material];
    const m = mats[0];
    // UV do hit -> pixel da textura
    let uvPix = null;
    if (m && m.map && h.uv) {
      const cv = m.map.image;
      const ctx2 = cv.getContext('2d');
      const u = h.uv.x, v = 1 - h.uv.y;
      const d = ctx2.getImageData(Math.floor(u * cv.width), Math.floor(v * cv.height), 1, 1).data;
      uvPix = [d[0], d[1], d[2]];
    }
    return { d: Math.round(h.distance), col: m && m.color ? '#' + m.color.getHexString() : null, inst: !!h.object.isInstancedMesh, instCol: h.object.instanceColor ? (() => { const a = h.object.instanceColor.array; const i = h.instanceId * 3; return [Math.round(a[i]*255), Math.round(a[i+1]*255), Math.round(a[i+2]*255)]; })() : null, uvPix, p: [Math.round(h.point.x), Math.round(h.point.y), Math.round(h.point.z)] };
  });
  console.log(JSON.stringify(report));
  await browser.close();
})();
