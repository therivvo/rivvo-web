// Diag R21w: a textura do terreno é grama ou concreto? (cor média + nome)
const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch({ args: ['--use-gl=angle','--use-angle=vulkan','--no-sandbox','--mute-audio'] });
  const page = await (await browser.newContext({ viewport: { width: 960, height: 540 } })).newPage();
  await page.addInitScript(() => localStorage.clear());
  await page.goto(process.argv[2] + '/?demo&track=2', { waitUntil: 'domcontentloaded', timeout: 120000 });
  await page.waitForFunction(() => window.__sk3d && window.__sk3d.raceManager && window.__sk3d.raceManager.phase === 'race', null, { timeout: 180000 });
  await page.waitForTimeout(6000);
  const report = await page.evaluate(async () => {
    const scene = window.__sk3d.scene;
    const out = [];
    scene.traverse((o) => {
      if (!o.isMesh || o.isInstancedMesh) return;
      o.geometry.computeBoundingSphere();
      const bs = o.geometry.boundingSphere;
      if (bs.radius < 100) return;
      const mats = Array.isArray(o.material) ? o.material : [o.material];
      const m = mats[0];
      let avg = null;
      if (m && m.map && m.map.image && m.map.image.getContext) {
        const cv = m.map.image; const g = cv.getContext('2d');
        const d = g.getImageData(0, 0, cv.width, cv.height).data;
        let r=0,gg=0,b=0,n=0;
        for (let i=0;i<d.length;i+=400){r+=d[i];gg+=d[i+1];b+=d[i+2];n++;}
        avg = [Math.round(r/n), Math.round(gg/n), Math.round(b/n)];
      }
      out.push({ r: Math.round(bs.radius), texAvg: avg, vertexColors: m.vertexColors });
    });
    return out;
  });
  console.log(JSON.stringify(report));
  await browser.close();
})().catch(e => { console.error(String(e).slice(0,300)); process.exit(1); });
