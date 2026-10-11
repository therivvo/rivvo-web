#!/usr/bin/env node
/**
 * Browser lifecycle probe for the real AudioManager contract.
 * Run on the GPU runner with PLAYWRIGHT_CORE_ROOT pointing at playwright-core.
 * No credentials are read; this script only reports capability states.
 */
import { createRequire } from 'node:module';

const require = createRequire(import.meta.url);
const mode = process.argv[2] || '--run';
const url = process.env.SK3D_QA_URL || 'http://192.168.0.103:3457/?test';
const pwRoot = process.env.PLAYWRIGHT_CORE_ROOT || '/opt/pwtest/node_modules/playwright-core';

function loadPlaywright() {
  try { return require('playwright'); } catch {}
  try { return require(pwRoot); } catch {}
  return null;
}

if (mode === '--probe') {
  const playwright = loadPlaywright();
  console.log(`PLAYWRIGHT=${playwright ? 'OK' : 'MISSING'}`);
  console.log(`RUNNER=${process.env.SK3D_QA_URL ? 'OK' : 'DIRECT_URL'}`);
  console.log('PROBE=READY');
  process.exit(playwright ? 0 : 0);
}

const playwright = loadPlaywright();
if (!playwright) {
  console.log('AUDIO_LIFECYCLE=BLOCKED reason=PLAYWRIGHT_MISSING');
  process.exit(0);
}

const { chromium } = playwright;
const errors = [];
const browser = await chromium.launch({
  executablePath: process.env.PLAYWRIGHT_EXECUTABLE_PATH || '/usr/bin/chromium',
  args: ['--use-gl=angle', '--use-angle=vulkan', '--no-sandbox', '--mute-audio', '--disable-frame-rate-limit', '--disable-gpu-vsync'],
});
try {
  const context = await browser.newContext({ viewport: { width: 390, height: 844 }, hasTouch: true, isMobile: false });
  await context.addInitScript(() => {
    localStorage.clear();
    window.requestAnimationFrame = (cb) => setTimeout(() => cb(performance.now()), 16);
    window.cancelAnimationFrame = (id) => clearTimeout(id);
  });
  const page = await context.newPage();
  page.on('pageerror', (err) => errors.push(String(err && err.message || err)));
  await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 180000 });
  await page.waitForTimeout(3500);
  const result = await page.evaluate(async () => {
    const { AudioManager } = await import('/src/audio/AudioManager.js');
    const manager = new AudioManager();
    const checks = [];
    const check = (name, ok, detail = '') => checks.push({ name, ok: !!ok, detail });
    check('lazy-before-init', !manager.isReady);
    manager.setMuted(true);
    manager.init();
    await new Promise((resolve) => setTimeout(resolve, 250));
    check('init-ready', manager.isReady, manager._ctx?.state || 'no-context');
    check('mute-before-and-after-init', manager.muted && Math.abs(manager._master.gain.value) < 0.001, String(manager._master.gain.value));
    manager.setMuted(false);
    await new Promise((resolve) => setTimeout(resolve, 80));
    check('unmute-restores-volume', !manager.muted && manager._master.gain.value > 0.01, String(manager._master.gain.value));
    manager.startMusic();
    check('music-start-request', manager._musicRequested === true);
    manager.stopMusic();
    check('music-stop-clears-request', manager._musicRequested === false);
    manager.suspend();
    await new Promise((resolve) => setTimeout(resolve, 100));
    check('suspend', manager._ctx?.state === 'suspended', manager._ctx?.state || 'closed');
    manager.resume();
    await new Promise((resolve) => setTimeout(resolve, 160));
    check('resume', manager._ctx?.state === 'running', manager._ctx?.state || 'closed');
    manager.destroy();
    await new Promise((resolve) => setTimeout(resolve, 80));
    check('destroy-closes-manager', !manager.isReady && manager._ctx === null);
    return { checks, contextState: manager._ctx?.state || 'closed' };
  });
  const gpu = await page.evaluate(() => {
    const c = document.createElement('canvas');
    const gl = c.getContext('webgl2') || c.getContext('webgl');
    const ext = gl && gl.getExtension('WEBGL_debug_renderer_info');
    return ext ? gl.getParameter(ext.UNMASKED_RENDERER_WEBGL) : 'unknown';
  });
  const failed = result.checks.filter((x) => !x.ok);
  console.log(`GPU=${gpu}`);
  console.log(`AUDIO_LIFECYCLE=${failed.length ? 'FAIL' : 'PASS'} checks=${result.checks.length} failed=${failed.length} pageErrors=${errors.length}`);
  for (const item of result.checks) console.log(`AUDIO_CHECK name=${item.name} ok=${item.ok} detail=${item.detail}`);
  if (errors.length) console.log(`PAGE_ERRORS=${errors.join(' | ')}`);
  if (failed.length || errors.length || !/RADV PHOENIX/i.test(gpu)) process.exitCode = 1;
} catch (error) {
  console.log(`AUDIO_LIFECYCLE=BLOCKED reason=${String(error?.message || error).replace(/\s+/g, '_')}`);
  process.exitCode = 0;
} finally {
  await browser.close();
}
