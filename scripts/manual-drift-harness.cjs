// F17 manual drift harness: no ?demo/autopilot. Captures video + state timeline.
let chromium;
try { ({ chromium } = require('playwright')); } catch { ({ chromium } = require('/opt/pwtest/node_modules/playwright')); }
const fs = require('fs');
const out = process.argv[2] || '/tmp/sk3d-f17';
const track = process.argv[3] || '1';
const viewportName = process.argv[4] || 'mobile';
const mobile = viewportName === 'mobile';
const url = `http://192.168.0.103:3457/?track=${track}`;
(async () => {
  const browser = await chromium.launch({ executablePath: process.env.PLAYWRIGHT_EXECUTABLE_PATH || '/usr/bin/chromium', args: ['--use-gl=angle', '--use-angle=vulkan', '--no-sandbox', '--mute-audio'] });
  const context = await browser.newContext({ viewport: mobile ? { width: 390, height: 844 } : { width: 1280, height: 720 }, deviceScaleFactor: mobile ? 2 : 1, hasTouch: mobile });
  const page = await context.newPage();
  const errors = [];
  page.on('pageerror', e => errors.push(String(e.message || e)));
  fs.mkdirSync(out, { recursive: true });
  await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 120000 });
  await page.waitForFunction(() => window.__sk3d?.startRace && window.__sk3d?.playerKart, { timeout: 180000 });
  await page.evaluate(() => { window.__sk3d.startRace(); window.__sk3d.skipCountdown(); });
  await page.waitForFunction(() => window.__sk3d?.raceManager?.phase === 'race', { timeout: 180000 });
  const client = await page.context().newCDPSession(page);
  await client.send('Page.startScreencast', { format: 'jpeg', quality: 70, maxWidth: 1280, maxHeight: 720, everyNthFrame: 4 });
  let frames = 0;
  client.on('Page.screencastFrame', event => { frames++; fs.writeFileSync(`${out}/frame_${String(frames).padStart(4, '0')}.jpg`, Buffer.from(event.data, 'base64')); client.send('Page.screencastFrameAck', { sessionId: event.sessionId }).catch(() => {}); });
  const timeline = [];
  const sample = setInterval(async () => {
    try { timeline.push(await page.evaluate(() => { const p = window.__sk3d.playerKart(); const st = p?.state || {}; const meter = document.querySelector('.sk3d-drift-meter'); return { t: performance.now(), phase: window.__sk3d.raceManager?.phase, playerAI: window.__sk3d.playerAIControlled, speed: st.speed, steer: st.steer, drift: st.drift, charge: st.driftCharge, meter: meter?.className, fill: document.querySelector('.sk3d-drift-fill')?.style.width || '' }; })); } catch {}
  }, 100);
  const press = async (selector, type, pointerId) => page.locator(selector).dispatchEvent(type, { pointerId, pointerType: 'touch', bubbles: true, cancelable: true });
  const controls = mobile ? { left: '.sk3d-touch-left', drift: '.sk3d-touch-drift' } : null;
  const end = Date.now() + 60000;
  let phase = 0;
  while (Date.now() < end) {
    try {
      if (mobile) {
        await press(controls.left, 'pointerdown', 31); await press(controls.drift, 'pointerdown', 32);
      } else { await page.keyboard.down('ArrowUp'); await page.keyboard.down('ArrowLeft'); await page.keyboard.down('Shift'); }
      await page.waitForTimeout(1800);
      if (mobile) { await press(controls.drift, 'pointerup', 32); await press(controls.left, 'pointerup', 31); }
      else { await page.keyboard.up('Shift'); await page.keyboard.up('ArrowLeft'); }
      await page.waitForTimeout(800);
      phase++;
    } catch { break; }
  }
  if (!mobile) { await page.keyboard.up('Shift'); await page.keyboard.up('ArrowLeft'); await page.keyboard.up('ArrowUp'); }
  clearInterval(sample);
  await client.send('Page.stopScreencast').catch(() => {});
  const final = await page.evaluate(() => ({ phase: window.__sk3d.raceManager?.phase, playerAI: window.__sk3d.playerAIControlled, speed: window.__sk3d.playerKart()?.state?.speed }));
  fs.writeFileSync(`${out}/drift-timeline.json`, JSON.stringify({ track, viewportName, errors, cycles: phase, final, samples: timeline }, null, 2));
  console.log(JSON.stringify({ track, viewportName, frames, errors, cycles: phase, final, samples: timeline.length }));
  await browser.close();
})().catch(error => { console.error(error); process.exit(1); });
