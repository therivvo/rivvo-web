#!/usr/bin/env node
/**
 * QA-only render budget breakdown for Super Kart 3D.js.
 * No product behavior is changed: this only reads the live scene and renderer.
 * Usage: node scripts/audit-render-breakdown.cjs <url> <outdir>
 */
const fs = require('node:fs');
const path = require('node:path');
const { chromium } = require('/opt/pwtest/node_modules/playwright');

const url = process.argv[2] || 'http://127.0.0.1:3457/?test';
const outDir = process.argv[3] || path.resolve('qa-render-breakdown');
fs.mkdirSync(outDir, { recursive: true });

const viewports = [
  { name: 'desktop', width: 1280, height: 720, hasTouch: false },
  { name: 'mobile', width: 390, height: 844, hasTouch: true },
];
const launchArgs = ['--use-gl=angle', '--use-angle=vulkan', '--no-sandbox', '--disable-gpu-vsync', '--disable-frame-rate-limit'];

function classify(name) {
  const n = String(name || '').toLowerCase();
  if (/sky|dome|sun|moon|flare|horizon/.test(n)) return 'sky-lighting';
  if (/road|track|asphalt|kerb|curb|rail|ribbon|finish|gantry|ramp|pad|dash/.test(n)) return 'track-kit';
  if (/city|tower|building|window|skyline|neon|billboard|facade|roof|pilaster|crane/.test(n)) return 'neon-city';
  if (/tree|grass|flower|bush|rock|meadow|terrain|mountain|cloud|palm|vegetation/.test(n)) return 'meadow-world';
  if (/kart|wheel|tire|pilot|driver|vehicle|car/.test(n)) return 'karts';
  if (/item|coin|shell|banana|star|boost|power|pickup|lightning/.test(n)) return 'items-vfx';
  if (/crowd|stand|spectator|marshal|cone|bollard|prop/.test(n)) return 'crowd-props';
  return 'unclassified';
}

(async () => {
  const browser = await chromium.launch({ executablePath: process.env.PLAYWRIGHT_EXECUTABLE_PATH || '/usr/bin/chromium', headless: true, args: launchArgs });
  try {
    for (const vp of viewports) {
      const context = await browser.newContext({ viewport: { width: vp.width, height: vp.height }, hasTouch: vp.hasTouch });
      await context.addInitScript(() => {
        try { localStorage.clear(); } catch {}
        const raf = window.requestAnimationFrame;
        window.requestAnimationFrame = (cb) => setTimeout(() => cb(performance.now()), 16);
        window.cancelAnimationFrame = (id) => clearTimeout(id);
        window.__qaOriginalRaf = raf;
      });
      const page = await context.newPage();
      const pageErrors = [];
      page.on('pageerror', (err) => pageErrors.push(String(err && err.stack || err)));
      await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 180000 });
      await page.waitForFunction(() => window.__sk3d && window.__sk3d.renderer, null, { timeout: 180000 });
      await page.waitForTimeout(2500);
      const result = await page.evaluate(({ name, width, height }) => {
        const sk = window.__sk3d;
        const scene = sk.scene;
        const buckets = Object.fromEntries(['sky-lighting','track-kit','neon-city','meadow-world','karts','items-vfx','crowd-props','unclassified'].map((k) => [k, { objects: 0, meshes: 0, instanced: 0, triangles: 0 }]));
        const namedRoots = {};
        let totalMeshes = 0;
        let totalInstanced = 0;
        let totalTriangles = 0;
        const classify = (value) => {
          const n = String(value || '').toLowerCase();
          if (/sky|dome|sun|moon|flare|horizon/.test(n)) return 'sky-lighting';
          if (/road|track|asphalt|kerb|curb|rail|ribbon|finish|gantry|ramp|pad|dash/.test(n)) return 'track-kit';
          if (/city|tower|building|window|skyline|neon|billboard|facade|roof|pilaster|crane/.test(n)) return 'neon-city';
          if (/tree|grass|flower|bush|rock|meadow|terrain|mountain|cloud|palm|vegetation/.test(n)) return 'meadow-world';
          if (/kart|wheel|tire|pilot|driver|vehicle|car/.test(n)) return 'karts';
          if (/item|coin|shell|banana|star|boost|power|pickup|lightning/.test(n)) return 'items-vfx';
          if (/crowd|stand|spectator|marshal|cone|bollard|prop/.test(n)) return 'crowd-props';
          return 'unclassified';
        };
        scene.traverse((obj) => {
          let ancestor = obj;
          const names = [];
          while (ancestor && names.length < 8) { if (ancestor.name) names.push(ancestor.name); ancestor = ancestor.parent; }
          const bucket = buckets[classify(names.join('/'))];
          bucket.objects++;
          const namedRoot = names[names.length - 1] || '(unnamed)';
          namedRoots[namedRoot] = namedRoots[namedRoot] || { objects: 0, meshes: 0, instanced: 0, triangles: 0 };
          namedRoots[namedRoot].objects++;
          if (obj.isMesh) {
            bucket.meshes++;
            namedRoots[namedRoot].meshes++;
            totalMeshes++;
            if (obj.isInstancedMesh) {
              bucket.instanced++;
              namedRoots[namedRoot].instanced++;
              totalInstanced++;
            }
            const index = obj.geometry?.index;
            const position = obj.geometry?.attributes?.position;
            const vertices = position?.count || 0;
            const triangles = index ? index.count / 3 : vertices / 3;
            bucket.triangles += triangles;
            namedRoots[namedRoot].triangles += triangles;
            totalTriangles += triangles;
          }
        });
        const gl = sk.renderer.getContext();
        const dbg = gl.getExtension('WEBGL_debug_renderer_info');
        const rendererName = dbg ? String(gl.getParameter(dbg.UNMASKED_RENDERER_WEBGL)) : 'unavailable';
        const passes = sk.postfx?.composer?.passes?.map((pass) => ({ type: pass.constructor?.name || 'unknown', enabled: pass.enabled !== false })) || [];
        return {
          viewport: { name, width, height },
          gpu: rendererName,
          webgl: gl instanceof WebGL2RenderingContext ? 'webgl2' : 'webgl',
          pageErrors: [],
          rendererReport: sk.renderReport?.() || null,
          sceneTotals: { objects: scene.children.length, meshes: totalMeshes, instanced: totalInstanced, triangles: totalTriangles },
          namedRoots,
          buckets,
          postfx: { enabled: !!sk.postfx?.enabled, passes },
        };
      }, vp);
      result.pageErrors = pageErrors;
      fs.writeFileSync(path.join(outDir, `${vp.name}.json`), JSON.stringify(result, null, 2));
      console.log(JSON.stringify(result));
      await context.close();
    }
  } finally {
    await browser.close();
  }
})().catch((err) => { console.error(err.stack || err); process.exitCode = 1; });
