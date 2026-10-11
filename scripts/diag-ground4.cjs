// Diag: UV do hit na row B (d4d3d6) — pixel da textura de janelas naquele ponto
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
    ray.setFromCamera(new THREE.Vector2(-0.125, 0.222), cam);
    const hits = [];
    scene.traverse((o) => { if (o.isMesh) { const r = ray.intersectObject(o, false); if (r.length) hits.push(...r); } });
    hits.sort((a, b) => a.distance - b.distance);
    const h = hits[0];
    const m = Array.isArray(h.object.material) ? h.object.material[0] : h.object.material;
    const cv = m.map.image;
    const ctx2 = cv.getContext('2d');
    // média 16x16 em volta do UV
    const u = h.uv.x, v = 1 - h.uv.y;
    const d = ctx2.getImageData(Math.floor(u*cv.width)-8, Math.floor(v*cv.height)-8, 16, 16).data;
    let r=0,g=0,b=0,n=d.length/4;
    for (let i=0;i<d.length;i+=4){r+=d[i];g+=d[i+1];b+=d[i+2];}
    const instCol = h.object.instanceColor ? (()=>{const a=h.object.instanceColor.array;const i=h.instanceId*3;return [Math.round(a[i]*255),Math.round(a[i+1]*255),Math.round(a[i+2]*255)];})() : null;
    return { uv: [u.toFixed(2), v.toFixed(2)], texAvg: [Math.round(r/n), Math.round(g/n), Math.round(b/n)], instCol, dist: Math.round(h.distance) };
  });
  console.log(JSON.stringify(report));
  await browser.close();
})();
