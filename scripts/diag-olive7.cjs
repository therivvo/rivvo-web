// Diagnóstico 7b: raycast do centro da tela na banda oliva (chase cam real em corrida ativa)
const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch({ args: ['--use-gl=angle','--use-angle=vulkan','--no-sandbox','--mute-audio'] });
  const page = await (await browser.newContext({ viewport: { width: 960, height: 540 } })).newPage();
  await page.addInitScript(() => localStorage.clear());
  await page.goto(process.argv[2] + '/?demo&track=2', { waitUntil: 'domcontentloaded', timeout: 120000 });
  await page.waitForFunction(() => window.__sk3d && window.__sk3d.raceManager && window.__sk3d.raceManager.phase === 'race', null, { timeout: 180000 });
  await page.waitForTimeout(8000);
  const report = await page.evaluate(() => {
    const scene = window.__sk3d.scene, cam = window.__sk3d.camera;
    // NDC do centro-baixo da tela onde a banda oliva aparece (x~0.45, y~0.45 → tela)
    const results = [];
    for (const [nx, ny] of [[0.45, 0.42], [0.5, 0.45], [0.4, 0.4]]) {
      const ray = new (cam.position.constructor ? Object : Object)();
    }
    // usar Raycaster via setFromCamera precisa de THREE; importar do bundle do jogo não é possível — usar cam.unproject
    function rayFromNDC(nx, ny) {
      const v = cam.position.clone();
      // construir direção: unproject ponto NDC
      const vec = new v.constructor(nx, ny, 0.5).unproject(cam);
      const dir = vec.sub(cam.position).normalize();
      return dir;
    }
    const vProto = Object.getPrototypeOf(cam.position);
    const out = [];
    for (const [nx, ny] of [[0.45, 0.42], [0.5, 0.45], [0.35, 0.4]]) {
      const dir = rayFromNDC(nx, ny);
      const origin = cam.position.clone();
      let best = null;
      scene.traverse((o) => {
        if (!o.isMesh || !o.geometry) return;
        if (!o.geometry.boundingBox && !o.geometry.boundingSphere) o.geometry.computeBoundingSphere();
        // ray-sphere grosseiro
        const bs = o.geometry.boundingSphere;
        // world sphere
        const wc = bs.center.clone().applyMatrix4(o.matrixWorld);
        const wr = bs.radius;
        const oc = origin.clone().sub(wc);
        const b = oc.dot(dir);
        const c = oc.dot(oc) - wr * wr;
        if (c > 0 && b > 0) return; // miss
        const disc = b*b - c;
        if (disc < 0) return;
        const t = -b - Math.sqrt(disc);
        if (t < 0) return;
        const dist = t;
        if (!best || dist < best.dist) {
          const mats = Array.isArray(o.material) ? o.material : [o.material];
          best = { dist: Math.round(dist), name: o.name || '(unnamed)', colors: mats.filter(m=>m&&m.color).map(m => '#' + m.color.getHexString()) };
        }
      });
      out.push({ ndc: [nx, ny], best });
    }
    return out;
  });
  console.log(JSON.stringify(report, null, 1));
  await browser.close();
})();
