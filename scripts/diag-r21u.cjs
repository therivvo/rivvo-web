// Diag R21u: cadeia completa de parents + userData do InstancedMesh #bcbcc0
const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch({ args: ['--use-gl=angle','--use-angle=vulkan','--no-sandbox','--mute-audio'] });
  const page = await (await browser.newContext({ viewport: { width: 960, height: 540 } })).newPage();
  await page.addInitScript(() => localStorage.clear());
  await page.goto(process.argv[2] + '/?demo&track=2', { waitUntil: 'domcontentloaded', timeout: 120000 });
  await page.waitForFunction(() => window.__sk3d && window.__sk3d.raceManager && window.__sk3d.raceManager.phase === 'race', null, { timeout: 180000 });
  await page.waitForTimeout(8000);
  const report = await page.evaluate(async () => {
    const scene = window.__sk3d.scene;
    const out = [];
    scene.traverse((o) => {
      if (!o.isInstancedMesh) return;
      const mats = Array.isArray(o.material) ? o.material : [o.material];
      const m = mats[0];
      const col = m && m.color ? '#'+m.color.getHexString() : null;
      if (col !== '#bcbcc0' && col !== '#8b8a92' && col !== '#555364') return;
      const chain = []; let q = o; while (q && chain.length < 6) { chain.push((q.name||q.type) + (q.isInstancedMesh?'*':'')); q = q.parent; }
      // posição da primeira instância
      const arr = o.instanceMatrix.array;
      const px = Math.round(arr[12]), py = Math.round(arr[13]), pz = Math.round(arr[14]);
      out.push({ col, count: o.count, chain: chain.join('<'), inst0: [px,py,pz], geoParams: o.geometry.parameters ? [o.geometry.parameters.width, o.geometry.parameters.height, o.geometry.parameters.depth] : null });
    });
    return out;
  });
  console.log(JSON.stringify(report));
  await browser.close();
})().catch(e => { console.error(String(e).slice(0,300)); process.exit(1); });
