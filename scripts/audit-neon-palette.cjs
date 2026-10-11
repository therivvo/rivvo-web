#!/usr/bin/env node
/** Deterministic runtime audit for Neon skyline window palette distribution. */
function usage() {
  console.log('audit-neon-palette <url> [--track=2]');
  console.log('  Requires Chromium ANGLE/Vulkan and a runtime exposing __sk3dNeonPalette.');
}

if (process.argv.includes('--help') || process.argv.includes('-h')) {
  usage();
  process.exit(0);
}

const baseUrl = process.argv[2];
if (!baseUrl) {
  usage();
  process.exit(2);
}
const { chromium } = require('playwright');
const track = process.argv.find((arg) => arg.startsWith('--track='))?.split('=')[1] || '2';

(async () => {
  const browser = await chromium.launch({
    executablePath: process.env.PLAYWRIGHT_EXECUTABLE_PATH || '/usr/bin/chromium',
    args: [
      '--use-gl=angle',
      '--use-angle=vulkan',
      '--no-sandbox',
      '--mute-audio',
      '--disable-frame-rate-limit',
      '--disable-gpu-vsync',
    ],
  });
  try {
    const context = await browser.newContext({ viewport: { width: 960, height: 540 } });
    await context.addInitScript(() => {
      localStorage.clear();
      window.requestAnimationFrame = (cb) => setTimeout(() => cb(performance.now()), 16);
      window.cancelAnimationFrame = (id) => clearTimeout(id);
    });
    const page = await context.newPage();
    const pageErrors = [];
    page.on('pageerror', (error) => pageErrors.push(error.message));
    const url = `${baseUrl.replace(/\/$/, '')}/?demo&track=${track}`;
    await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 180000 });
    await page.waitForFunction(() => window.__sk3dNeonPalette?.total > 0, null, { timeout: 180000 });
    const gpu = await page.evaluate(() => {
      const canvas = document.createElement('canvas');
      const gl = canvas.getContext('webgl2') || canvas.getContext('webgl');
      const ext = gl?.getExtension('WEBGL_debug_renderer_info');
      return ext ? gl.getParameter(ext.UNMASKED_RENDERER_WEBGL) : 'unknown';
    });
    const first = await page.evaluate(() => window.__sk3dNeonPalette);
    if (!/RADV PHOENIX/i.test(gpu)) throw new Error(`GPU gate failed: ${gpu}`);
    if (first.colors.length !== 5 || first.counts.length !== 5) throw new Error(`palette shape failed: ${JSON.stringify(first)}`);
    if (first.total !== first.counts.reduce((sum, n) => sum + n, 0)) throw new Error('palette total mismatch');
    if (first.counts.some((n) => !Number.isInteger(n) || n < 0)) throw new Error('palette counts invalid');
    await page.reload({ waitUntil: 'domcontentloaded', timeout: 180000 });
    await page.waitForFunction(() => window.__sk3dNeonPalette?.total > 0, null, { timeout: 180000 });
    const second = await page.evaluate(() => window.__sk3dNeonPalette);
    if (JSON.stringify(first) !== JSON.stringify(second)) throw new Error('palette distribution is not deterministic across reload');
    if (pageErrors.length) throw new Error(`pageerrors: ${pageErrors.join(' | ')}`);
    console.log('audit-neon-palette PASS');
    console.log(`GPU: ${gpu}`);
    console.log(`COLORS: ${first.colors.map((c) => `#${c.toString(16).padStart(6, '0')}`).join(',')}`);
    console.log(`COUNTS: ${first.counts.join(',')}`);
    console.log(`TOTAL: ${first.total}`);
    console.log(`ROWS: ${first.rows.length}`);
  } finally {
    await browser.close();
  }
})().catch((error) => {
  console.error(`audit-neon-palette FAIL: ${error.message}`);
  process.exitCode = 1;
});
