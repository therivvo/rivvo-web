// Diag R21k: ?nobl (bloom off, grade on) — a colina verde é o bloom?
const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch({ args: ['--use-gl=angle','--use-angle=vulkan','--no-sandbox','--mute-audio'] });
  const page = await (await browser.newContext({ viewport: { width: 960, height: 540 } })).newPage();
  await page.addInitScript(() => localStorage.clear());
  await page.goto(process.argv[2] + '/?demo&track=2&nobl', { waitUntil: 'domcontentloaded', timeout: 120000 });
  await page.waitForFunction(() => window.__sk3d && window.__sk3d.raceManager && window.__sk3d.raceManager.phase === 'race', null, { timeout: 180000 });
  await page.waitForTimeout(16000);
  await page.screenshot({ path: '/tmp/r21k-nobloom.png' });
  console.log('saved');
  await browser.close();
})().catch(e => { console.error(String(e).slice(0,300)); process.exit(1); });
