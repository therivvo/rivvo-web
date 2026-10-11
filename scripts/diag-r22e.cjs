// Diag R22e: todos os meshes transparentes/emissivos com bounding sphere > 30 na cena
const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch({ args: ['--use-gl=angle','--use-angle=vulkan','--no-sandbox','--mute-audio'] });
  const page = await (await browser.newContext({ viewport: { width: 960, height: 540 } })).newPage();
  await page.addInitScript(() => localStorage.clear());
  await page.goto(process.argv[2] + '/?demo&track=2', { waitUntil: 'domcontentloaded', timeout: 120000 });
  await page.waitForFunction(() => window.__sk3d && window.__sk3d.raceManager && window.__sk3d.raceManager.phase === 'race', null, { timeout: 180000 });
  await page.waitForTimeout(5000);
  const r = await page.evaluate(async () => {
    const scene = window.__sk3d.scene;
    const out = [];
    scene.traverse((o) => {
      if (!o.isMesh) return;
      const mats = Array.isArray(o.material) ? o.material : [o.material];
      const m = mats[0];
      if (!m) return;
      const isTransparent = m.transparent || m.blending === 2;
      if (!isTransparent) return;
      o.geometry.computeBoundingSphere();
      const bs = o.geometry.boundingSphere;
      if (bs.radius < 25) return;
      out.push({
        r: Math.round(bs.radius),
        pos: [Math.round(o.position.x), Math.round(o.position.y), Math.round(o.position.z)],
        col: m.color ? '#' + m.color.getHexString() : null,
        opacity: m.opacity,
        blending: m.blending,
        mapW: m.map && m.map.image ? m.map.image.width : null,
        fog: m.fog,
        name: o.name || o.type,
        inst: !!o.isInstancedMesh,
        count: o.count || null,
      });
    });
    return out;
  });
  console.log(JSON.stringify(r));
  await browser.close();
})().catch(e => { console.error(String(e).slice(0,300)); process.exit(1); });
