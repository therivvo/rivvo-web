// Diag R22g: raycast no pixel exato da área oliva (0.6, -0.04 NDC) com screenshot sincronizado
const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch({ args: ['--use-gl=angle','--use-angle=vulkan','--no-sandbox','--mute-audio'] });
  const page = await (await browser.newContext({ viewport: { width: 960, height: 540 } })).newPage();
  await page.addInitScript(() => localStorage.clear());
  await page.goto(process.argv[2] + '/?demo&track=2', { waitUntil: 'domcontentloaded', timeout: 120000 });
  await page.waitForFunction(() => window.__sk3d && window.__sk3d.raceManager && window.__sk3d.raceManager.phase === 'race', null, { timeout: 180000 });
  for (let i = 0; i < 4; i++) {
    await page.waitForTimeout(5000);
    const r = await page.evaluate(async () => {
      const THREE = await import('/node_modules/three/build/three.module.js');
      const scene = window.__sk3d.scene, cam = window.__sk3d.camera;
      cam.updateMatrixWorld();
      const ray = new THREE.Raycaster();
      // NDC para pixel (0.6w, 0.52h de cima) → ndcY = 1 - 2*0.52 = -0.04
      ray.setFromCamera(new THREE.Vector2(0.2, -0.04), cam);
      let best = null;
      scene.traverse((o) => {
        if (!o.isMesh) return;
        for (const h of ray.intersectObject(o, false)) {
          if (!best || h.distance < best.distance) best = h;
        }
      });
      if (!best || best.distance < 30 || best.distance > 400) return null;
      const o = best.object;
      const mats = Array.isArray(o.material) ? o.material : [o.material];
      const m = mats[0];
      return {
        d: Math.round(best.distance),
        col: m.color ? '#' + m.color.getHexString() : null,
        opacity: m.opacity,
        transparent: m.transparent,
        blending: m.blending,
        toneMapped: m.toneMapped,
        emissive: m.emissive ? '#' + m.emissive.getHexString() : null,
        mapW: m.map && m.map.image ? m.map.image.width : null,
        geo: o.geometry.type,
        name: o.name || '(anon)',
      };
    });
    if (r) console.log(JSON.stringify(r));
  }
  await browser.close();
})().catch(e => { console.error(String(e).slice(0,300)); process.exit(1); });
