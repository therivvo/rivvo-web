// Diag R22h: raycast com filtro de distância 60-350 (o hit a 34m é o terreno próximo)
const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch({ args: ['--use-gl=angle','--use-angle=vulkan','--no-sandbox','--mute-audio'] });
  const page = await (await browser.newContext({ viewport: { width: 960, height: 540 } })).newPage();
  await page.addInitScript(() => localStorage.clear());
  await page.goto(process.argv[2] + '/?demo&track=2', { waitUntil: 'domcontentloaded', timeout: 120000 });
  await page.waitForFunction(() => window.__sk3d && window.__sk3d.raceManager && window.__sk3d.raceManager.phase === 'race', null, { timeout: 180000 });
  for (let i = 0; i < 6; i++) {
    await page.waitForTimeout(5000);
    const r = await page.evaluate(async () => {
      const THREE = await import('/node_modules/three/build/three.module.js');
      const scene = window.__sk3d.scene, cam = window.__sk3d.camera;
      cam.updateMatrixWorld();
      const ray = new THREE.Raycaster();
      const hits = [];
      for (const [nx, ny] of [[0.2,-0.04],[0.1,0.02],[0.3,-0.1],[0.15,0.08]]) {
        ray.setFromCamera(new THREE.Vector2(nx, ny), cam);
        let best = null;
        scene.traverse((o) => {
          if (!o.isMesh) return;
          for (const h of ray.intersectObject(o, false)) {
            if (h.distance < 55) continue; // pular terreno próximo
            if (!best || h.distance < best.distance) best = h;
          }
        });
        if (!best || best.distance > 420) { hits.push(null); continue; }
        const o = best.object;
        const mats = Array.isArray(o.material) ? o.material : [o.material];
        const m = mats[0];
        hits.push({
          ndc: [nx, ny], d: Math.round(best.distance),
          col: m.color ? '#' + m.color.getHexString() : null,
          opacity: m.opacity, transparent: m.transparent, blending: m.blending,
          toneMapped: m.toneMapped,
          emissive: m.emissive ? '#' + m.emissive.getHexString() : null,
          mapW: m.map && m.map.image ? m.map.image.width : null,
          geo: o.geometry.type, name: o.name || '(anon)',
        });
      }
      return hits;
    });
    console.log(JSON.stringify(r));
  }
  await browser.close();
})().catch(e => { console.error(String(e).slice(0,300)); process.exit(1); });
