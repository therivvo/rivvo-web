// Diag 20: qual InstancedMesh branco fog:false está em (-45,22,-40)? listar todos os instanced fog:false com instanceColor médio e posição média
const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch({ args: ['--use-gl=angle','--use-angle=vulkan','--no-sandbox','--mute-audio'] });
  const page = await (await browser.newContext({ viewport: { width: 960, height: 540 } })).newPage();
  await page.addInitScript(() => localStorage.clear());
  await page.goto(process.argv[2] + '/?test&track=2', { waitUntil: 'domcontentloaded', timeout: 120000 });
  await page.waitForFunction(() => window.__sk3d, null, { timeout: 120000 });
  await page.waitForTimeout(4000);
  const report = await page.evaluate(() => {
    const scene = window.__sk3d.scene;
    const out = [];
    scene.traverse((o) => {
      if (!o.isInstancedMesh) return;
      const mats = Array.isArray(o.material) ? o.material : [o.material];
      const m = mats[0];
      if (!m || m.fog !== false) return;
      const arr = o.instanceMatrix.array;
      let sx = 0, sy = 0, sz = 0;
      const n = Math.min(o.count, 30);
      for (let i = 0; i < n; i++) { sx += arr[i*16+12]; sy += arr[i*16+13]; sz += arr[i*16+14]; }
      let ic = null;
      if (o.instanceColor) {
        const a = o.instanceColor.array;
        let r=0,g=0,b=0; for (let i=0;i<n;i++){r+=a[i*3];g+=a[i*3+1];b+=a[i*3+2];}
        ic = [Math.round(r/n*255), Math.round(g/n*255), Math.round(b/n*255)];
      }
      out.push({ col: '#' + m.color.getHexString(), count: o.count, avgPos: [Math.round(sx/n), Math.round(sy/n), Math.round(sz/n)], instCol: ic, map: !!m.map, geo: o.geometry.type, tm: m.toneMapped });
    });
    return out;
  });
  console.log(JSON.stringify(report, null, 1));
  await browser.close();
})();
