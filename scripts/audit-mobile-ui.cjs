let chromium;
try { ({ chromium } = require('playwright')); } catch { ({ chromium } = require('/opt/pwtest/node_modules/playwright')); }
(async () => {
  const [url, out = 'qa-gpu-runner/mobile-ui-bounds.json'] = process.argv.slice(2);
  const b = await chromium.launch({ executablePath: '/usr/bin/chromium', args: ['--use-gl=angle','--use-angle=vulkan','--no-sandbox','--mute-audio'] });
  const p = await (await b.newContext({ viewport: { width: 390, height: 844 }, hasTouch: true })).newPage();
  await p.goto(`${url}/?demo&track=2`, { waitUntil: 'domcontentloaded', timeout: 120000 });
  await p.waitForTimeout(15000);
  const r = await p.evaluate(() => {
    const sels = ['.sk3d-hud-bottom','.sk3d-hud-bottom-left','.sk3d-hud-bottom-right','.sk3d-item-wrap','.sk3d-speedo','.sk3d-position','.sk3d-touch-left','.sk3d-touch-right','.sk3d-touch-drift','.sk3d-touch-item'];
    return Object.fromEntries(sels.map(s => { const e=document.querySelector(s); const x=e?.getBoundingClientRect(); return [s, x && {x:x.x,y:x.y,w:x.width,h:x.height,bottom:x.bottom,right:x.right}]; }));
  });
  require('fs').writeFileSync(out, JSON.stringify(r,null,2)); console.log(JSON.stringify(r)); await b.close();
})();
