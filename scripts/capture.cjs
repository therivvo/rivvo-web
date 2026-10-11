// Headless capture for Super Kart 3D.js (desktop + mobile).
// Usage:
//   NODE_PATH=/home/jarvis/.hermes/node/lib/node_modules \
//   CAPTURE_URL=http://localhost:3457/?demo CAPTURE_OUT=/tmp/sk3d-shots/ \
//   timeout 120 node scripts/capture.js
// Drives the demo autopilot (all karts AI) so frames are deterministic and
// the scene shows action without needing input.
const { chromium } = require('playwright');

const BASE = process.env.CAPTURE_URL || 'http://localhost:3457/?demo';
const OUT = process.env.CAPTURE_OUT || '/tmp/sk3d-shots/';
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

const LAUNCH_ARGS = [
  '--no-sandbox',
  '--disable-dev-shm-usage',
  '--enable-unsafe-swiftshader',
  '--use-gl=angle',
  '--use-angle=swiftshader',
];

async function driveDesktop(page) {
  await sleep(7000); // boot + demo auto-start (menu shows first otherwise)
  const info = await page.evaluate(() => {
    const s = window.__sk3d;
    return { state: s ? s.getState() : null, demo: s ? s.DEMO : false };
  });
  if (!info.demo) {
    const startBtn = page.locator('.sk3d-primary-btn, button');
    if (await startBtn.count()) await startBtn.first().evaluate((n) => n.click());
    await sleep(2000);
  }
  // Let the countdown + early race run (headless software GL is slow-mo).
  await sleep(9000);
}

async function driveMobile(page) {
  await driveDesktop(page);
}

async function run(mode) {
  const browser = await chromium.launch({ headless: true, args: LAUNCH_ARGS });
  try {
    let page;
    if (mode === 'desktop') {
      page = await browser.newPage({ viewport: { width: 1280, height: 800 } });
      await page.goto(BASE, { waitUntil: 'domcontentloaded' });
      await driveDesktop(page);
      await page.screenshot({ path: OUT + 'desktop.png' });
    } else {
      const context = await browser.newContext({
        viewport: { width: 390, height: 844 },
        hasTouch: true,
        userAgent:
          'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
      });
      page = await context.newPage();
      await page.goto(BASE, { waitUntil: 'domcontentloaded' });
      await driveMobile(page);
      await page.screenshot({ path: OUT + 'mobile.png' });
    }
    const info = await page.evaluate(() => {
      const s = window.__sk3d;
      return { state: s ? s.getState() : null, hasCanvas: !!document.querySelector('canvas') };
    });
    console.log(mode.toUpperCase() + ' OK state=' + JSON.stringify(info));
  } finally {
    await browser.close();
  }
}

(async () => {
  const fs = require('fs');
  fs.mkdirSync(OUT, { recursive: true });
  try { await run('desktop'); } catch (e) { console.error('DESKTOP FAIL:', e.message); }
  try { await run('mobile'); } catch (e) { console.error('MOBILE FAIL:', e.message); }
  console.log('DONE');
  process.exit(0);
})();
