// Diag R21s: screenshot E raycast sincronizados no mesmo estado
const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch({ args: ['--use-gl=angle','--use-angle=vulkan','--no-sandbox','--mute-audio'] });
  const page = await (await browser.newContext({ viewport: { width: 960, height: 540 } })).newPage();
  await page.addInitScript(() => localStorage.clear());
  await page.goto(process.argv[2] + '/?demo&track=2', { waitUntil: 'domcontentloaded', timeout: 120000 });
  await page.waitForFunction(() => window.__sk3d && window.__sk3d.raceManager && window.__sk3d.raceManager.phase === 'race', null, { timeout: 180000 });
  await page.waitForTimeout(15000);
  // pausar o loop de render para congelar a cena? Não dá — mas raycast+screenshot
  // no mesmo evaluate ficam dentro do mesmo frame aproximadamente.
  const report = await page.evaluate(async () => {
    const THREE = await import('/node_modules/three/build/three.module.js');
    const scene = window.__sk3d.scene, cam = window.__sk3d.camera;
    cam.updateMatrixWorld();
    const ray = new THREE.Raycaster();
    const out = [];
    for (const [nx, ny] of [[0.7,-0.2],[0.75,-0.25],[0.65,-0.18]]) {
      ray.setFromCamera(new THREE.Vector2(nx, ny), cam);
      const hits = [];
      scene.traverse((o) => {
        if (!o.isMesh) return;
        const r = ray.intersectObject(o, false);
        for (const h of r) {
          if (h.distance < 20 || h.distance > 400) continue;
          const mats = Array.isArray(o.material) ? o.material : [o.material];
          const m = mats[0];
          hits.push({ d: Math.round(h.distance), col: m && m.color ? '#'+m.color.getHexString() : null, mapW: m&&m.map&&m.map.image?m.map.image.width:null, op: m.opacity, blend: m.blending, inst: !!o.isInstancedMesh, name: o.name || o.parent.name || o.type, uv: h.uv ? [+h.uv.x.toFixed(2), +h.uv.y.toFixed(2)] : null, p: [Math.round(h.point.x), Math.round(h.point.y), Math.round(h.point.z)] });
        }
      });
      hits.sort((a,b)=>a.d-b.d);
      out.push({ ndc:[nx,ny], top: hits.slice(0,5) });
    }
    return out;
  });
  console.log(JSON.stringify(report));
  await page.screenshot({ path: '/tmp/r21s.png' });
  await browser.close();
})().catch(e => { console.error(String(e).slice(0,300)); process.exit(1); });
