#!/usr/bin/env node
/**
 * Deterministic Neon skyline capture for paired material A/B review.
 * The camera is derived from the loaded track, not a guessed world offset.
 */
const fs = require('node:fs');
const path = require('node:path');
const { chromium } = require('playwright');

const baseUrl = (process.argv[2] || 'http://127.0.0.1:3457').replace(/\/$/, '');
const outDir = process.env.CAPTURE_OUT || path.resolve('qa-gpu-runner/skyline-fixed');
const mobile = process.argv.includes('--mobile');
const width = mobile ? 390 : 1280;
const height = mobile ? 844 : 720;
const viewport = { width, height };
const launchArgs = [
  '--use-gl=angle', '--use-angle=vulkan', '--no-sandbox', '--mute-audio',
  '--disable-frame-rate-limit', '--disable-gpu-vsync',
];

(async () => {
  fs.mkdirSync(outDir, { recursive: true });
  const browser = await chromium.launch({
    executablePath: process.env.PLAYWRIGHT_EXECUTABLE_PATH || '/usr/bin/chromium',
    args: launchArgs,
  });
  const context = await browser.newContext({ viewport, hasTouch: mobile, isMobile: false });
  await context.addInitScript(() => {
    localStorage.clear();
    // The game creates procedural canvas textures during boot. Seed Math.random
    // in this QA-only context so independent boots produce identical pixels.
    let state = 0x6d2b79f5;
    Math.random = () => {
      state |= 0;
      state = (state + 0x6d2b79f5) | 0;
      let t = Math.imul(state ^ (state >>> 15), 1 | state);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  });
  const page = await context.newPage();
  const pageErrors = [];
  page.on('pageerror', (error) => pageErrors.push(error.message));
  await page.goto(`${baseUrl}/?test&track=2`, { waitUntil: 'domcontentloaded', timeout: 180000 });
  await page.waitForFunction(() => window.__sk3d?.track?.path && window.__sk3dNeonPalette?.total > 0, null, { timeout: 180000 });
  await page.waitForTimeout(1500);

  const probe = await page.evaluate(() => {
    const game = window.__sk3d;
    const path = game.track.path;
    const p = path.getPointAt(0.5);
    const t = path.getTangentAt(0.5).normalize();
    const normal = { x: -t.z, y: 0, z: t.x };
    const camera = game.camera;
    const target = { x: p.x, y: p.y + 14, z: p.z };
    camera.position.set(p.x + normal.x * 48, p.y + 30, p.z + normal.z * 48);
    camera.lookAt(target.x, target.y, target.z);
    camera.fov = 48;
    camera.updateProjectionMatrix();
    window.__freezeCam = true;
    game.updateCamera = () => {};
    // Freeze simulation and presentation after boot: without stopping the
    // loop, wind/turbo/UI animation advances between setup and CDP capture.
    game.loop?.stop();
    game.raceManager.phase = 'idle';
    const style = document.createElement('style');
    style.dataset.sk3dFixedCapture = 'true';
    style.textContent = '* { animation: none !important; transition: none !important; }\n' +
      'body > :not(#app) { display: none !important; }';
    document.head.appendChild(style);
    // Use the real post-processing path; direct renderer.render() made this
    // harness disagree with the player-facing frame when bloom was enabled.
    game.postfx?.render?.();
    if (!game.postfx?.enabled) game.renderer.render(game.scene, game.camera);
    const canvas = document.querySelector('canvas');
    const gl = canvas?.getContext('webgl2') || canvas?.getContext('webgl');
    const ext = gl?.getExtension('WEBGL_debug_renderer_info');
    const rect = canvas?.getBoundingClientRect();
    return {
      gpu: ext ? gl.getParameter(ext.UNMASKED_RENDERER_WEBGL) : 'unknown',
      palette: gameNeonPalette(),
      camera: { x: camera.position.x, y: camera.position.y, z: camera.position.z, fov: camera.fov },
      target,
      canvas: canvas ? { width: canvas.width, height: canvas.height } : null,
      // Keep A/B focused on the actual game framebuffer. The DOM HUD/menu has
      // independent compositor timing and made an otherwise fixed scene look
      // unstable; the runtime page remains unchanged.
      canvasClip: rect ? { x: rect.left, y: rect.top, width: rect.width, height: rect.height, scale: 1 } : null,
    };

    function gameNeonPalette() { return window.__sk3dNeonPalette; }
  });
  if (!/RADV PHOENIX/i.test(probe.gpu)) throw new Error(`GPU gate failed: ${probe.gpu}`);
  const cdp = await context.newCDPSession(page);
  await new Promise((resolve) => setTimeout(resolve, 250));
  const screenshot = await cdp.send('Page.captureScreenshot', {
    format: 'png',
    fromSurface: true,
    captureBeyondViewport: false,
    ...(probe.canvasClip ? { clip: probe.canvasClip } : {}),
  });
  const outPath = path.join(outDir, mobile ? 'neon-skyline-mobile.png' : 'neon-skyline-desktop.png');
  fs.writeFileSync(outPath, Buffer.from(screenshot.data, 'base64'));
  const report = { ...probe, viewport, pageErrors, outPath };
  fs.writeFileSync(path.join(outDir, mobile ? 'neon-skyline-mobile.json' : 'neon-skyline-desktop.json'), `${JSON.stringify(report, null, 2)}\n`);
  if (pageErrors.length) throw new Error(`pageerrors: ${pageErrors.join(' | ')}`);
  console.log(JSON.stringify(report));
  await browser.close();
})().catch((error) => {
  console.error(`capture-skyline-fixed FAIL: ${error.message}`);
  process.exitCode = 1;
});
