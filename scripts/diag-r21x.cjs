// Diag R21x: raycast na colina + sample da textura no UV exato do hit
const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch({ args: ['--use-gl=angle','--use-angle=vulkan','--no-sandbox','--mute-audio'] });
  const page = await (await browser.newContext({ viewport: { width: 960, height: 540 } })).newPage();
  await page.addInitScript(() => localStorage.clear());
  await page.goto(process.argv[2] + '/?demo&track=2', { waitUntil: 'domcontentloaded', timeout: 120000 });
  await page.waitForFunction(() => window.__sk3d && window.__sk3d.raceManager && window.__sk3d.raceManager.phase === 'race', null, { timeout: 180000 });
  // amostrar vários ticks para pegar ângulos diferentes
  const results = [];
  for (let tick = 0; tick < 6; tick++) {
    await page.waitForTimeout(4000);
    const r = await page.evaluate(async () => {
      const THREE = await import('/node_modules/three/build/three.module.js');
      const scene = window.__sk3d.scene, cam = window.__sk3d.camera;
      cam.updateMatrixWorld();
      const ray = new THREE.Raycaster();
      const out = [];
      for (let nx = -0.4; nx <= 0.4; nx += 0.2) {
        for (let ny = 0.0; ny <= 0.3; ny += 0.1) {
          ray.setFromCamera(new THREE.Vector2(nx, ny), cam);
          let best = null;
          scene.traverse((o) => {
            if (!o.isMesh) return;
            const rr = ray.intersectObject(o, false);
            for (const h of rr) {
              if (h.distance < 40 || h.distance > 350) continue;
              if (!best || h.distance < best.distance) best = h;
            }
          });
          if (best) {
            const o = best.object;
            const mats = Array.isArray(o.material) ? o.material : [o.material];
            const m = mats[0];
            let texPx = null;
            if (m && m.map && m.map.image && m.map.image.getContext && best.uv) {
              const cv = m.map.image; const g = cv.getContext('2d');
              const x = Math.floor(best.uv.x * cv.width), y = Math.floor((1-best.uv.y) * cv.height);
              const d = g.getImageData(Math.min(cv.width-1,x), Math.min(cv.height-1,y), 1, 1).data;
              texPx = [d[0], d[1], d[2]];
            }
            out.push({ d: Math.round(best.distance), col: m && m.color ? '#'+m.color.getHexString() : null, texPx, mapW: m&&m.map&&m.map.image?m.map.image.width:null, geo: o.geometry.type, inst: !!o.isInstancedMesh, name: o.name || o.type });
          }
        }
      }
      return out;
    });
    results.push(...r.filter(x => x.texPx));
    if (results.length > 8) break;
  }
  console.log(JSON.stringify(results));
  await browser.close();
})().catch(e => { console.error(String(e).slice(0,300)); process.exit(1); });
