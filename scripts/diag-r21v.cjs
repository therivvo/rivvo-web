// Diag R21v: com ?noinst, achar meshes BoxGeometry(10,14,8) individuais e suas cores
const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch({ args: ['--use-gl=angle','--use-angle=vulkan','--no-sandbox','--mute-audio'] });
  const page = await (await browser.newContext({ viewport: { width: 960, height: 540 } })).newPage();
  await page.addInitScript(() => localStorage.clear());
  await page.goto(process.argv[2] + '/?demo&track=2&noinst', { waitUntil: 'domcontentloaded', timeout: 120000 });
  await page.waitForFunction(() => window.__sk3d && window.__sk3d.raceManager && window.__sk3d.raceManager.phase === 'race', null, { timeout: 180000 });
  await page.waitForTimeout(6000);
  const report = await page.evaluate(async () => {
    const scene = window.__sk3d.scene;
    const out = [];
    scene.traverse((o) => {
      if (!o.isMesh || o.isInstancedMesh) return;
      const p = o.geometry && o.geometry.parameters;
      if (!p || p.width !== 10 || p.height !== 14 || p.depth !== 8) return;
      const mats = Array.isArray(o.material) ? o.material : [o.material];
      const m = mats[0];
      const chain = []; let q = o; while (q && chain.length < 4) { chain.push(q.name || q.type); q = q.parent; }
      out.push({ col: m && m.color ? '#'+m.color.getHexString() : null, pos: [Math.round(o.position.x), Math.round(o.position.y), Math.round(o.position.z)], chain: chain.join('<') });
    });
    return out.slice(0, 15);
  });
  console.log(JSON.stringify(report));
  await browser.close();
})().catch(e => { console.error(String(e).slice(0,300)); process.exit(1); });
