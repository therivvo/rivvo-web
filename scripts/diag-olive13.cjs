// Diagnóstico 13: raycast exato na banda oliva com THREE do jogo + nome do billboard
const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch({ args: ['--use-gl=angle','--use-angle=vulkan','--no-sandbox','--mute-audio'] });
  const page = await (await browser.newContext({ viewport: { width: 960, height: 540 } })).newPage();
  await page.addInitScript(() => localStorage.clear());
  await page.goto(process.argv[2] + '/?test&track=2', { waitUntil: 'domcontentloaded', timeout: 120000 });
  await page.waitForFunction(() => window.__sk3d, null, { timeout: 120000 });
  await page.waitForTimeout(4000);
  // posicionar câmera igual à chase cam e mirar onde a banda aparece
  const report = await page.evaluate(async () => {
    const THREE = await import('/node_modules/three/build/three.module.js');
    const scene = window.__sk3d.scene, cam = window.__sk3d.camera;
    const kart = window.__sk3d.playerKart();
    const p = kart.state.position;
    window.__freezeCam = true;
    cam.position.set(p.x, 2.8, p.z + 4.3);
    cam.lookAt(p.x, 2.0, p.z - 10);
    const out = [];
    for (const [nx, ny] of [[0.0, 0.35], [-0.2, 0.4], [0.2, 0.38], [0.0, 0.5]]) {
      const ray = new THREE.Raycaster();
      ray.setFromCamera(new THREE.Vector2(nx, ny), cam);
      const hits = [];
      scene.traverse((o) => { if (o.isMesh) { const r = ray.intersectObject(o, false); if (r.length) hits.push(...r); } });
      hits.sort((a, b) => a.distance - b.distance);
      out.push(hits.slice(0, 3).map(h => {
        const mats = Array.isArray(h.object.material) ? h.object.material : [h.object.material];
        const m = mats[0];
        const chain = []; let q = h.object; while (q) { chain.push(q.name || q.type); q = q.parent; }
        return { dist: Math.round(h.distance), chain: chain.slice(0, 3).join('<'), color: m && m.color ? '#' + m.color.getHexString() : null, map: !!(m && m.map), mapSrc: m && m.map ? (m.map.image && m.map.image.toDataURL ? m.map.image.toDataURL().slice(0, 60) : '?') : null, fog: m && m.fog, toneMapped: m && m.toneMapped };
      }));
    }
    return out;
  });
  console.log(JSON.stringify(report, null, 1));
  await browser.close();
})();
