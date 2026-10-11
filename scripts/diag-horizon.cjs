// Diagnóstico 7: câmera alta olhando o horizonte distante (sem kart na frente) p/ ver a banda oliva claramente
const { chromium } = require('playwright');
const fs = require('fs');
(async () => {
  const browser = await chromium.launch({ args: ['--use-gl=angle','--use-angle=vulkan','--no-sandbox','--mute-audio'] });
  const page = await (await browser.newContext({ viewport: { width: 960, height: 540 } })).newPage();
  await page.addInitScript(() => localStorage.clear());
  await page.goto(process.argv[2] + '/?test&track=2', { waitUntil: 'domcontentloaded', timeout: 120000 });
  await page.waitForFunction(() => window.__sk3d, null, { timeout: 120000 });
  await page.waitForTimeout(4000);
  await page.evaluate(() => {
    const { scene, camera } = window.__sk3d;
    window.__freezeCam = true;
    // achar o player kart
    const kart = window.__sk3d.playerKart();
    const p = kart.state.position;
    camera.position.set(p.x, 40, p.z + 60);
    camera.lookAt(p.x, 8, p.z - 120);
  });
  await page.waitForTimeout(600);
  const client = await page.context().newCDPSession(page);
  const shot = await client.send('Page.captureScreenshot', { format: 'png' });
  fs.writeFileSync(process.argv[3], Buffer.from(shot.data, 'base64'));
  console.log('saved', process.argv[3]);
  await browser.close();
})();
