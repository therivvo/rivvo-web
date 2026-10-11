// Diagnóstico 6: capturar frame com postfx OFF para isolar se a banda oliva vem do bloom/colorGrade
const { chromium } = require('playwright');
const fs = require('fs');
(async () => {
  const browser = await chromium.launch({ args: ['--use-gl=angle','--use-angle=vulkan','--no-sandbox','--mute-audio'] });
  const page = await (await browser.newContext({ viewport: { width: 960, height: 540 } })).newPage();
  await page.addInitScript(() => localStorage.clear());
  await page.goto(process.argv[2] + '/?test&track=2', { waitUntil: 'domcontentloaded', timeout: 120000 });
  await page.waitForFunction(() => window.__sk3d, null, { timeout: 120000 });
  await page.waitForTimeout(4000);
  await page.evaluate(() => { window.__sk3d.postfx.enabled = false; });
  await page.waitForTimeout(800);
  const client = await page.context().newCDPSession(page);
  const shot = await client.send('Page.captureScreenshot', { format: 'png' });
  fs.writeFileSync(process.argv[3], Buffer.from(shot.data, 'base64'));
  console.log('saved', process.argv[3]);
  await browser.close();
})();
