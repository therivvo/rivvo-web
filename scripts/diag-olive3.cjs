// Diagnóstico 3: raycast do horizonte — o que está atrás da pista na direção do olhar
const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch({ args: ['--use-gl=angle','--use-angle=vulkan','--no-sandbox','--mute-audio'] });
  const page = await (await browser.newContext({ viewport: { width: 960, height: 540 } })).newPage();
  await page.addInitScript(() => localStorage.clear());
  await page.goto(process.argv[2] + '/?test&track=2', { waitUntil: 'domcontentloaded', timeout: 120000 });
  await page.waitForFunction(() => window.__sk3d, null, { timeout: 120000 });
  await page.waitForTimeout(4000);
  const report = await page.evaluate(async () => {
    const THREE = window.__sk3d.THREE || (await import('/node_modules/three/build/three.module.js'));
    const scene = window.__sk3d.scene, cam = window.__sk3d.camera;
    // ray para frente da câmera, levemente para baixo (direção do "horizonte" visível)
    const dir = new THREE.Vector3();
    cam.getWorldDirection(dir);
    dir.y = -0.06; dir.normalize();
    const ray = new THREE.Raycaster(cam.position.clone(), dir, 1, 600);
    const hits = [];
    scene.traverse(o => { if (o.isMesh && !o.isSprite) { const r = ray.intersectObject(o, false); if (r.length) hits.push(...r); } });
    hits.sort((a, b) => a.distance - b.distance);
    const top = hits.slice(0, 8);
    return top.map(h => {
      const m = h.object.material;
      const mat = Array.isArray(m) ? m[0] : m;
      return { name: h.object.name || '(unnamed)', dist: Math.round(h.distance), color: mat && mat.color ? '#' + mat.color.getHexString() : null, map: !!(mat && mat.map), fog: mat ? mat.fog : null, type: h.object.isInstancedMesh ? 'inst' : 'mesh' };
    });
  });
  console.log(JSON.stringify(report, null, 1));
  await browser.close();
})();
