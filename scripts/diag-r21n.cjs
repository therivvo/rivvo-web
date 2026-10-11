// Diag R21n: identificar o mesh da colina — cadeia completa de parents + geometria
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
    // mira o NDC que pegou #bcbcc0 a 46m: (0.4, 0.2)
    ray.setFromCamera(new THREE.Vector2(0.4, 0.2), cam);
    const hits = [];
    scene.traverse((o) => {
      if (!o.isMesh) return;
      const r = ray.intersectObject(o, false);
      for (const h of r) {
        if (h.distance < 40 || h.distance > 350) continue;
        const mats = Array.isArray(o.material) ? o.material : [o.material];
        const m = mats[0];
        const chain = []; let q = o; while (q && chain.length < 5) { chain.push(q.name || q.type); q = q.parent; }
        hits.push({ d: Math.round(h.distance), col: m && m.color ? '#'+m.color.getHexString() : null, map: !!(m&&m.map), mapName: m&&m.map&&m.map.image ? (m.map.image.width+'x'+m.map.image.height) : null, chain: chain.join('<'), geo: o.geometry.type, verts: o.geometry.attributes.position.count, p: [Math.round(h.point.x), Math.round(h.point.y), Math.round(h.point.z)] });
      }
    });
    hits.sort((a,b)=>a.d-b.d);
    return hits.slice(0, 5);
  });
  console.log(JSON.stringify(report));
  await browser.close();
})().catch(e => { console.error(String(e).slice(0,300)); process.exit(1); });
