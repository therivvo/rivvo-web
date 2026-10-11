#!/usr/bin/env node
/** QA-only temporal renderer probe. Measures real rAF cadence and renderer cost
 * on the GPU runner without changing game source or gameplay state. */
const fs = require('node:fs');
const path = require('node:path');
const { chromium } = require('/opt/pwtest/node_modules/playwright');

const baseUrl = (process.argv[2] || 'http://127.0.0.1:3457').replace(/\/$/, '');
const outDir = process.argv[3] || path.resolve('qa-gpu-runner/tick-temporal');
const durationMs = Number(process.argv[4] || 8000);
const mode = process.argv[5] || 'baseline';
const dpr = Number(process.env.SK3D_DPR || 1);
const scenarios = [
  { track: 1, name: 'meadow-desktop', width: 1280, height: 720, hasTouch: false },
  { track: 1, name: 'meadow-mobile', width: 390, height: 844, hasTouch: true },
  { track: 2, name: 'neon-desktop', width: 1280, height: 720, hasTouch: false },
  { track: 2, name: 'neon-mobile', width: 390, height: 844, hasTouch: true },
];
const args = ['--use-gl=angle', '--use-angle=vulkan', '--no-sandbox', '--mute-audio', '--disable-frame-rate-limit', '--disable-gpu-vsync'];
fs.mkdirSync(outDir, { recursive: true });

function percentile(values, p) {
  if (!values.length) return null;
  const sorted = [...values].sort((a, b) => a - b);
  return sorted[Math.min(sorted.length - 1, Math.floor((sorted.length - 1) * p))];
}

(async () => {
  const browser = await chromium.launch({ executablePath: process.env.PLAYWRIGHT_EXECUTABLE_PATH || '/usr/bin/chromium', headless: true, args });
  const results = [];
  try {
    for (const scenario of scenarios) {
      const context = await browser.newContext({ viewport: { width: scenario.width, height: scenario.height }, deviceScaleFactor: dpr, hasTouch: scenario.hasTouch, isMobile: false });
      await context.addInitScript(() => {
        try { localStorage.clear(); } catch {}
      });
      const page = await context.newPage();
      const pageErrors = [];
      page.on('pageerror', (error) => pageErrors.push(String(error && error.stack || error)));
      await page.goto(`${baseUrl}/?demo&track=${scenario.track}`, { waitUntil: 'domcontentloaded', timeout: 180000 });
      await page.waitForFunction(() => window.__sk3d?.renderer && window.__sk3d?.raceManager, null, { timeout: 180000 });
      await page.waitForTimeout(2500);
      const data = await page.evaluate(async ({ duration, mode, deviceDpr }) => {
        const game = window.__sk3d;
        if (mode === 'no-vignette') {
          const vignette = game.postfx?.composer?.passes?.find((pass) => pass.material?.uniforms?.offset && pass.material?.uniforms?.darkness);
          if (!vignette) throw new Error('VignetteShader pass not found');
          vignette.enabled = false;
        } else if (mode === 'no-color-grade') {
          const grade = game.postfx?.composer?.passes?.find((pass) => pass.material?.uniforms?.saturation && pass.material?.uniforms?.contrast);
          if (grade) grade.enabled = false;
        } else if (mode === 'no-bloom') {
          const bloom = game.postfx?.composer?.passes?.find((pass) => pass.constructor?.name && /BloomPass/.test(pass.constructor.name));
          if (!bloom) throw new Error('UnrealBloomPass not found');
          bloom.enabled = false;
        }
        const percentile = (values, p) => {
          if (!values.length) return null;
          const sorted = [...values].sort((a, b) => a - b);
          return sorted[Math.min(sorted.length - 1, Math.floor((sorted.length - 1) * p))];
        };
        const gl = game.renderer.getContext();
        const ext = gl.getExtension('WEBGL_debug_renderer_info');
        const gpu = ext ? String(gl.getParameter(ext.UNMASKED_RENDERER_WEBGL)) : 'unavailable';
        const originalRender = game.renderer.render.bind(game.renderer);
        let frameRenderCalls = 0;
        let frameRenderMs = 0;
        game.renderer.render = (...args) => {
          const start = performance.now();
          frameRenderCalls++;
          const result = originalRender(...args);
          frameRenderMs += performance.now() - start;
          return result;
        };
        const originalRAF = window.requestAnimationFrame.bind(window);
        const samples = [];
        let last = null;
        let wrapped = true;
        window.requestAnimationFrame = (callback) => originalRAF((timestamp) => {
          const start = performance.now();
          callback(timestamp);
          const end = performance.now();
          if (last !== null) samples.push({ frameMs: timestamp - last, callbackMs: end - start, calls: frameRenderCalls, renderMs: frameRenderMs, triangles: game.renderer.info.render.triangles });
          frameRenderCalls = 0;
          frameRenderMs = 0;
          last = timestamp;
        });
        await new Promise((resolve) => setTimeout(resolve, duration));
        window.requestAnimationFrame = originalRAF;
        const frameMs = samples.map((s) => s.frameMs).filter((n) => Number.isFinite(n) && n > 0 && n < 250);
        const callbackMs = samples.map((s) => s.callbackMs).filter((n) => Number.isFinite(n) && n >= 0 && n < 250);
        const renderMs = samples.map((s) => s.renderMs).filter((n) => Number.isFinite(n) && n >= 0 && n < 250);
        const calls = samples.map((s) => s.calls).filter((n) => Number.isFinite(n));
        const triangles = samples.map((s) => s.triangles).filter((n) => Number.isFinite(n));
        return {
          gpu,
          deviceDpr,
          effectivePixelRatio: game.renderer.getPixelRatio(),
          drawingBuffer: { width: gl.drawingBufferWidth, height: gl.drawingBufferHeight },
          webgl: gl instanceof WebGL2RenderingContext ? 'webgl2' : 'webgl',
          phase: game.raceManager?.phase,
          passes: game.postfx?.composer?.passes?.map((pass) => ({ type: pass.constructor?.name || 'unknown', enabled: pass.enabled !== false })) || [],
          samples: samples.length,
          fpsApprox: frameMs.length ? 1000 / (frameMs.reduce((a, b) => a + b, 0) / frameMs.length) : 0,
          frameMs: { p50: percentile(frameMs, 0.50), p95: percentile(frameMs, 0.95), max: frameMs.length ? Math.max(...frameMs) : null },
          callbackMs: { p50: percentile(callbackMs, 0.50), p95: percentile(callbackMs, 0.95), max: callbackMs.length ? Math.max(...callbackMs) : null },
          renderMs: { p50: percentile(renderMs, 0.50), p95: percentile(renderMs, 0.95), max: renderMs.length ? Math.max(...renderMs) : null },
          renderCalls: { median: percentile(calls, 0.50), max: calls.length ? Math.max(...calls) : null },
          triangles: { median: percentile(triangles, 0.50), max: triangles.length ? Math.max(...triangles) : null },
          wrapped,
        };
      }, { duration: durationMs, mode, deviceDpr: dpr });
      const result = { mode, dpr, scenario, ...data, pageErrors };
      results.push(result);
      fs.writeFileSync(path.join(outDir, `${scenario.name}.json`), `${JSON.stringify(result, null, 2)}\n`);
      console.log(JSON.stringify(result));
      await context.close();
    }
  } finally {
    await browser.close();
  }
  const gpuOk = results.length === scenarios.length && results.every((r) => /RADV PHOENIX/i.test(r.gpu) && r.pageErrors.length === 0 && r.samples > 30 && r.phase === 'race');
  const summary = { gpu_ok: gpuOk, scenarios: results, generatedAt: new Date().toISOString() };
  fs.writeFileSync(path.join(outDir, 'summary.json'), `${JSON.stringify(summary, null, 2)}\n`);
  if (!gpuOk) process.exitCode = 1;
})().catch((error) => { console.error(error.stack || error); process.exitCode = 1; });
