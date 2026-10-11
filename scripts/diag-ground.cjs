// Diagnóstico 6b: capturar frame com a câmera apontando SÓ para o terreno distante (sem pista)
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
    const p = window.__sk3d.playerKart().state.position;
    // câmera baixa rente ao chão olhando o horizonte lateral (para fora da pista)
    camera.position.set(p.x + 8, 2.5, p.z + 8);
    camera.lookAt(p.x + 60, 4, p.z + 60); // para fora, diagonal
  });
  await page.waitForTimeout(500);
  const client = await page.context().newCDPSession(page);
  const shot = await client.send('Page.captureScreenshot', { format: 'png' });
  fs.writeFileSync(process.argv[3], Buffer.from(shot.data, 'base64'));
  console.log('saved', process.argv[3]);
  await browser.close();
})();
