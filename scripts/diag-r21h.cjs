// Diag R21h: raycast na colina verde (NDC ~0.17,-0.17) — qual mesh é?
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
    const out = [];
    for (const [nx, ny] of [[0.17, -0.17], [0.25, -0.22], [0.1, -0.12]]) {
      ray.setFromCamera(new THREE.Vector2(nx, ny), cam);
      const hits = [];
      scene.traverse((o) => {
        if (!o.isMesh) return;
        const r = ray.intersectObject(o, false);
        for (const h of r) {
          const mats = Array.isArray(o.material) ? o.material : [o.material];
          const m = mats[0];
          let mapAvg = null;
          if (m && m.map && m.map.image) {
            try {
              const cv = m.map.image; const g = cv.getContext('2d');
              const d = g.getImageData(0, 0, cv.width, cv.height).data;
              let rr=0,gg=0,bb=0,n=0;
              for (let i=0;i<d.length;i+=400){rr+=d[i];gg+=d[i+1];bb+=d[i+2];n++;}
              mapAvg = [Math.round(rr/n), Math.round(gg/n), Math.round(bb/n)];
            } catch {}
          }
          hits.push({ d: Math.round(h.distance), col: m && m.color ? '#'+m.color.getHexString() : null, map: !!(m&&m.map), mapAvg, name: o.name || o.parent.name || o.type, p: [Math.round(h.point.x), Math.round(h.point.y), Math.round(h.point.z)] });
        }
      });
      hits.sort((a,b)=>a.d-b.d);
      out.push(hits.slice(0,3));
    }
    return out;
  });
  console.log(JSON.stringify(report));
  await browser.close();
})().catch(e => { console.error(String(e).slice(0,300)); process.exit(1); });
