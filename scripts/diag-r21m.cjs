// Diag R21m: raycast ny POSITIVO (colina está acima do centro da tela)
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
    const found = [];
    for (let nx = -0.6; nx <= 0.6; nx += 0.2) {
      for (let ny = 0.0; ny <= 0.4; ny += 0.1) {
        ray.setFromCamera(new THREE.Vector2(nx, ny), cam);
        let best = null;
        scene.traverse((o) => {
          if (!o.isMesh) return;
          const r = ray.intersectObject(o, false);
          for (const h of r) {
            if (h.distance < 40 || h.distance > 350) continue;
            const mats = Array.isArray(o.material) ? o.material : [o.material];
            const m = mats[0];
            if (!best || h.distance < best.d) {
              best = { d: Math.round(h.distance), col: m && m.color ? '#'+m.color.getHexString() : null, map: !!(m&&m.map), name: o.name || o.parent.name || o.type, p: [Math.round(h.point.x), Math.round(h.point.y), Math.round(h.point.z)] };
            }
          }
        });
        if (best) found.push({ ndc: [nx.toFixed(1), ny.toFixed(1)], ...best });
      }
    }
    return found;
  });
  console.log(JSON.stringify(report));
  await browser.close();
})().catch(e => { console.error(String(e).slice(0,300)); process.exit(1); });
