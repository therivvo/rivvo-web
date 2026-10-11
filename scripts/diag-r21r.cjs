// Diag R21r: raycast no pixel da colina verde (x=830,y=330 de 960x540 → NDC 0.73,-0.22) sincronizado
const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch({ args: ['--use-gl=angle','--use-angle=vulkan','--no-sandbox','--mute-audio'] });
  const page = await (await browser.newContext({ viewport: { width: 960, height: 540 } })).newPage();
  await page.addInitScript(() => localStorage.clear());
  await page.goto(process.argv[2] + '/?demo&track=2', { waitUntil: 'domcontentloaded', timeout: 120000 });
  await page.waitForFunction(() => window.__sk3d && window.__sk3d.raceManager && window.__sk3d.raceManager.phase === 'race', null, { timeout: 180000 });
  // esperar o kart chegar num trecho similar ao frame_0200 (~17s de demo)
  await page.waitForTimeout(17000);
  const report = await page.evaluate(async () => {
    const THREE = await import('/node_modules/three/build/three.module.js');
    const scene = window.__sk3d.scene, cam = window.__sk3d.camera;
    const ray = new THREE.Raycaster();
    const out = [];
    // varrer a região direita da tela onde a colina aparece
    for (const [nx, ny] of [[0.73,-0.22],[0.6,-0.15],[0.8,-0.1],[0.66,-0.3]]) {
      ray.setFromCamera(new THREE.Vector2(nx, ny), cam);
      const hits = [];
      scene.traverse((o) => {
        if (!o.isMesh) return;
        const r = ray.intersectObject(o, false);
        for (const h of r) {
          if (h.distance < 25 || h.distance > 400) continue;
          const mats = Array.isArray(o.material) ? o.material : [o.material];
          const m = mats[0];
          hits.push({ d: Math.round(h.distance), col: m && m.color ? '#'+m.color.getHexString() : null, mapW: m&&m.map&&m.map.image?m.map.image.width:null, inst: !!o.isInstancedMesh, geo: o.geometry.type, name: o.name || o.parent.name || o.type, p: [Math.round(h.point.x), Math.round(h.point.y), Math.round(h.point.z)] });
        }
      });
      hits.sort((a,b)=>a.d-b.d);
      out.push({ ndc: [nx, ny], hits: hits.slice(0,4) });
    }
    return out;
  });
  console.log(JSON.stringify(report));
  await browser.close();
})().catch(e => { console.error(String(e).slice(0,300)); process.exit(1); });
