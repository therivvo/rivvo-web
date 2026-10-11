// Diag R21t: identificar o InstancedMesh #555364 — nome, textura sample e contagem
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
    // achar TODOS InstancedMesh com material.color ~0x555364 ou deitados grandes
    const out = [];
    scene.traverse((o) => {
      if (!o.isInstancedMesh) return;
      const mats = Array.isArray(o.material) ? o.material : [o.material];
      const m = mats[0];
      const col = m && m.color ? '#'+m.color.getHexString() : null;
      o.geometry.computeBoundingSphere();
      const r = o.geometry.boundingSphere.radius;
      if (r < 2 || r > 60) return; // decais médios
      let texAvg = null;
      if (m && m.map && m.map.image && m.map.image.getContext) {
        try {
          const cv = m.map.image; const g = cv.getContext('2d');
          const d = g.getImageData(0, 0, cv.width, cv.height).data;
          let rr=0,gg=0,bb=0,n=0;
          for (let i=0;i<d.length;i+=400){rr+=d[i];gg+=d[i+1];bb+=d[i+2];n++;}
          texAvg = [Math.round(rr/n), Math.round(gg/n), Math.round(bb/n)];
        } catch {}
      }
      out.push({ name: o.name || '(sem nome)', count: o.count, col, radius: Math.round(r), mapW: m&&m.map&&m.map.image?m.map.image.width:null, mapH: m&&m.map&&m.map.image?m.map.image.height:null, texAvg, transparent: m.transparent, opacity: m.opacity });
    });
    return out;
  });
  console.log(JSON.stringify(report));
  await browser.close();
})().catch(e => { console.error(String(e).slice(0,300)); process.exit(1); });
