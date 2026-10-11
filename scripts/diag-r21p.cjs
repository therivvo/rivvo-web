// Diag R21p: screenshot + raycast no MESMO tick (sincronizados) mirando a colina
const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch({ args: ['--use-gl=angle','--use-angle=vulkan','--no-sandbox','--mute-audio'] });
  const page = await (await browser.newContext({ viewport: { width: 960, height: 540 } })).newPage();
  await page.addInitScript(() => localStorage.clear());
  await page.goto(process.argv[2] + '/?demo&track=2', { waitUntil: 'domcontentloaded', timeout: 120000 });
  await page.waitForFunction(() => window.__sk3d && window.__sk3d.raceManager && window.__sk3d.raceManager.phase === 'race', null, { timeout: 180000 });
  await page.waitForTimeout(15000);
  const report = await page.evaluate(async () => {
    const THREE = await import('/node_modules/three/build/three.module.js');
    const scene = window.__sk3d.scene, cam = window.__sk3d.camera;
    // renderizar um frame congelado mentalmente: raycast em grid denso cobrindo
    // a região central-superior onde a colina aparece nos frames
    const ray = new THREE.Raycaster();
    const found = [];
    for (let nx = -0.5; nx <= 0.5; nx += 0.1) {
      for (let ny = -0.1; ny <= 0.35; ny += 0.09) {
        ray.setFromCamera(new THREE.Vector2(nx, ny), cam);
        let best = null;
        scene.traverse((o) => {
          if (!o.isMesh || o.isInstancedMesh) return;
          const r = ray.intersectObject(o, false);
          for (const h of r) {
            if (h.distance < 30 || h.distance > 350) continue;
            if (!best || h.distance < best.d) best = h;
          }
        });
        if (best && !found.some(f => f.p[0] === Math.round(best.point.x) && f.p[2] === Math.round(best.point.z))) {
          const o = best.object;
          const mats = Array.isArray(o.material) ? o.material : [o.material];
          const m = mats[0];
          found.push({ ndc: [+nx.toFixed(1), +ny.toFixed(1)], d: Math.round(best.distance), col: m && m.color ? '#'+m.color.getHexString() : null, mapW: m&&m.map&&m.map.image?m.map.image.width:null, geo: o.geometry.type, name: o.name || o.parent.name || o.type, p: [Math.round(best.point.x), Math.round(best.point.y), Math.round(best.point.z)] });
        }
      }
    }
    return found;
  });
  console.log(JSON.stringify(report));
  await page.screenshot({ path: '/tmp/r21p.png' });
  await browser.close();
})().catch(e => { console.error(String(e).slice(0,300)); process.exit(1); });
