/**
 * Super Kart 3D.js — Canvas inspector (Measured Evidence para threejs-aaa-graphics-builder).
 * Carrega um screenshot (PNG) num canvas 2D, amostra pixels e calcula:
 *   - colorEntropyBits: entropia de cor média (baixo = cena plana/vazia)
 *   - edgeDensity: densidade de bordas (baixo = primitive-dominant/empty)
 *   - luminance.contrast: contraste de luminância (baixo = fog/darkness compression)
 *   - dominantColorShare: fração da cor dominante (alto = cena esparsa/plana)
 * Uso: node scripts/inspect-canvas-metrics.cjs <screenshot.png> [label]
 * Requer Playwright (NODE_PATH aponta para o global do Hermes).
 */
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const file = process.argv[2];
const label = process.argv[3] || path.basename(file);

(async () => {
  if (!file || !fs.existsSync(file)) { console.error('USO: node inspect-canvas-metrics.cjs <png> [label]'); process.exit(1); }
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  const b64 = fs.readFileSync(file).toString('base64');
  const metrics = await page.evaluate(async (dataUrl) => {
    const img = new Image();
    await new Promise((res, rej) => { img.onload = res; img.onerror = rej; img.src = dataUrl; });
    const W = img.width, H = img.height;
    const cv = document.createElement('canvas');
    cv.width = W; cv.height = H;
    const ctx = cv.getContext('2d');
    ctx.drawImage(img, 0, 0);
    const N = Math.min(W * H, 200 * 200); // amostra até 40k px p/ velocidade
    const stepX = Math.max(1, Math.floor(W / 200));
    const stepY = Math.max(1, Math.floor(H / 200));
    const px = ctx.getImageData(0, 0, W, H).data;
    // luminance + histograma de cor quantizada
    const lum = [];
    const colorCounts = new Map();
    let edgeCount = 0, edgeSamples = 0;
    const grid = [];
    for (let y = 0; y < H; y += stepY) {
      const row = [];
      for (let x = 0; x < W; x += stepX) {
        const i = (y * W + x) * 4;
        const r = px[i], g = px[i + 1], b = px[i + 2];
        const L = 0.2126 * r + 0.7152 * g + 0.0722 * b;
        row.push(L);
        lum.push(L);
        const q = ((r >> 4) << 8) | ((g >> 4) << 4) | (b >> 4);
        colorCounts.set(q, (colorCounts.get(q) || 0) + 1);
      }
      grid.push(row);
    }
    // edge density (Sobel simplificado em grid amostrado)
    for (let y = 1; y < grid.length - 1; y++) {
      for (let x = 1; x < grid[y].length - 1; x++) {
        const gx = grid[y][x + 1] - grid[y][x - 1];
        const gy = grid[y + 1][x] - grid[y - 1][x];
        const mag = Math.abs(gx) + Math.abs(gy);
        edgeSamples++;
        if (mag > 40) edgeCount++;
      }
    }
    // entropia de cor
    let total = 0; for (const c of colorCounts.values()) total += c;
    let ent = 0;
    for (const c of colorCounts.values()) { const p = c / total; if (p > 0) ent -= p * Math.log2(p); }
    // contraste de luminância
    const minL = Math.min(...lum), maxL = Math.max(...lum);
    const contrast = maxL - minL;
    // cor dominante
    let dom = 0, domC = 0; for (const [k, v] of colorCounts) if (v > domC) { domC = v; dom = k; }
    const dominantColorShare = domC / total;
    return {
      width: W, height: H,
      sampledPixels: total,
      colorEntropyBits: +ent.toFixed(3),
      edgeDensity: +(edgeCount / edgeSamples).toFixed(4),
      luminanceContrast: +contrast.toFixed(1),
      dominantColorShare: +dominantColorShare.toFixed(3),
    };
  }, 'data:image/png;base64,' + b64);
  await browser.close();
  console.log(JSON.stringify({ label, metrics }, null, 2));
})().catch(e => { console.error('ERR', e.message); process.exit(1); });
