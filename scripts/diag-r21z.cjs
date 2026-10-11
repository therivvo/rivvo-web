// Diag R21z: fingerprint da textura do terreno — compara com grass/dirt/concrete geradas
const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch({ args: ['--use-gl=angle','--use-angle=vulkan','--no-sandbox','--mute-audio'] });
  const page = await (await browser.newContext({ viewport: { width: 960, height: 540 } })).newPage();
  await page.addInitScript(() => localStorage.clear());
  await page.goto(process.argv[2] + '/?demo&track=2', { waitUntil: 'domcontentloaded', timeout: 120000 });
  await page.waitForFunction(() => window.__sk3d && window.__sk3d.raceManager && window.__sk3d.raceManager.phase === 'race', null, { timeout: 180000 });
  await page.waitForTimeout(6000);
  const report = await page.evaluate(async () => {
    // gerar as 3 texturas candidatas via import e comparar histograma com a do terreno
    const M = await import('/src/render/Materials.js');
    const scene = window.__sk3d.scene;
    let terrainTex = null;
    scene.traverse((o) => {
      if (!o.isMesh || o.isInstancedMesh || terrainTex) return;
      o.geometry.computeBoundingSphere();
      if (o.geometry.boundingSphere.radius < 100) return;
      const mats = Array.isArray(o.material) ? o.material : [o.material];
      if (mats[0] && mats[0].map) terrainTex = mats[0].map;
    });
    if (!terrainTex) return 'no terrain tex';
    const fp = (cv) => {
      const g = cv.getContext('2d');
      const d = g.getImageData(0, 0, cv.width, cv.height).data;
      let r=0,gg=0,b=0,n=0;
      for (let i=0;i<d.length;i+=400){r+=d[i];gg+=d[i+1];b+=d[i+2];n++;}
      return [Math.round(r/n), Math.round(gg/n), Math.round(b/n)];
    };
    return {
      terrain: fp(terrainTex.image),
      grass: fp(M.grassTexture().image),
      dirt: fp(M.dirtTexture().image),
      concrete: fp(M.concreteTexture().image),
      sameAsGrass: terrainTex.image === M.grassTexture().image,
      sameAsDirt: terrainTex.image === M.dirtTexture().image,
      sameAsConcrete: terrainTex.image === M.concreteTexture().image,
    };
  });
  console.log(JSON.stringify(report));
  await browser.close();
})().catch(e => { console.error(String(e).slice(0,300)); process.exit(1); });
