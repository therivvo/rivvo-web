// Diag R21o: o mesh #bcbcc0 — UV offset/repeat da textura 256x256 + posição world exata
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
    ray.setFromCamera(new THREE.Vector2(0.4, 0.2), cam);
    const hits = [];
    scene.traverse((o) => {
      if (!o.isMesh) return;
      const r = ray.intersectObject(o, false);
      for (const h of r) {
        if (h.distance < 40 || h.distance > 350) continue;
        const mats = Array.isArray(o.material) ? o.material : [o.material];
        const m = mats[0];
        hits.push({
          d: Math.round(h.distance),
          col: m && m.color ? '#'+m.color.getHexString() : null,
          mapRepeat: m && m.map ? [m.map.repeat.x, m.map.repeat.y] : null,
          toneMapped: m ? m.toneMapped : null,
          fog: m ? m.fog : null,
          blending: m ? m.blending : null,
          transparent: m ? m.transparent : null,
          opacity: m ? m.opacity : null,
          emissive: m && m.emissive ? '#'+m.emissive.getHexString() : null,
          geoSize: o.geometry.parameters ? [o.geometry.parameters.width, o.geometry.parameters.height, o.geometry.parameters.depth] : null,
          wp: [Math.round(o.getWorldPosition(new THREE.Vector3()).x), Math.round(o.getWorldPosition(new THREE.Vector3()).y), Math.round(o.getWorldPosition(new THREE.Vector3()).z)],
        });
      }
    });
    hits.sort((a,b)=>a.d-b.d);
    return hits.slice(0, 3);
  });
  console.log(JSON.stringify(report));
  await browser.close();
})().catch(e => { console.error(String(e).slice(0,300)); process.exit(1); });
