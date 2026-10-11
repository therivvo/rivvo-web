// Diagnóstico 9: identificar o mesh #d4d3d6 — nome, geometria, pai, textura
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
      if (!o.isMesh) return;
      const mats = Array.isArray(o.material) ? o.material : [o.material];
      for (const m of mats) {
        if (m && m.color && m.color.getHexString() === 'd4d3d6') {
          // cadeia de pais
          const chain = [];
          let p = o;
          while (p) { chain.push(p.name || p.type); p = p.parent; }
          out.push({ chain: chain.join('<'), geo: o.geometry.type, mapSize: m.map ? m.map.image.width + 'x' + m.map.image.height : null, fog: m.fog, pos: o.getWorldPosition(new (o.position.constructor)(0,0,0)).toArray().map(Math.round) });
          break;
        }
      }
    });
    return out.slice(0, 10);
  });
  console.log(JSON.stringify(report, null, 1));
  await browser.close();
})();
