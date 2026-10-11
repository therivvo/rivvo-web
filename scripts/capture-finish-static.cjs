// GPU visual probe: freeze a player-facing camera at the start/finish line.
let chromium;
try { ({ chromium } = require('playwright')); }
catch { ({ chromium } = require('/opt/pwtest/node_modules/playwright')); }
const fs = require('fs');
(async () => {
  const [url, outdir = 'qa-gpu-runner/finish-static'] = process.argv.slice(2);
  fs.mkdirSync(outdir, { recursive: true });
  const browser = await chromium.launch({ executablePath: '/usr/bin/chromium', args: ['--use-gl=angle','--use-angle=vulkan','--no-sandbox','--mute-audio'] });
  const page = await (await browser.newContext({ viewport: { width: 1280, height: 720 } })).newPage();
  await page.addInitScript(() => localStorage.clear());
  await page.goto(`${url}/?test&track=1`, { waitUntil: 'domcontentloaded', timeout: 120000 });
  await page.waitForFunction(() => window.__sk3d?.track?.startLine, null, { timeout: 120000 });
  await page.waitForTimeout(4000);
  const metrics = await page.evaluate(() => {
    const s = window.__sk3d; const p = s.track.startLine.position; const d = s.track.startLine.direction;
    s.loop.stop?.(); window.__freezeCam = true;
    s.camera.position.set(p.x - d.x * 13, p.y + 4.2, p.z - d.z * 13);
    s.camera.lookAt(p.x, p.y + 3.0, p.z);
    return { camera: s.camera.position.toArray(), target: [p.x, p.y + 3, p.z], phase: s.raceManager.phase };
  });
  await page.waitForTimeout(300);
  await page.screenshot({ path: `${outdir}/finish-static.png` });
  fs.writeFileSync(`${outdir}/metrics.json`, JSON.stringify(metrics, null, 2));
  console.log(JSON.stringify(metrics));
  await browser.close();
})();
