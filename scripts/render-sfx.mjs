// ============================================================
// Super Kart 3D.js — scripts/render-sfx.mjs
// QA renderer: renders every procedural SFX and every music track
// to PCM16 WAV files using OfflineAudioContext.
//
// BROWSER-ONLY (requires WebAudio — OfflineAudioContext does not
// exist in plain Node). Run it in a headless browser page; the
// module exposes window.__sk3dSfxRender() and hands each WAV to a
// save sink injected by the controller.
//
// Controller (Node + Playwright) example:
//   import { chromium } from 'playwright';
//   import fs from 'node:fs';
//   const outDir = process.env.SFX_OUT || '/tmp/sk3d-sfx';
//   fs.mkdirSync(outDir, { recursive: true });
//   const browser = await chromium.launch();
//   const page = await browser.newPage();
//   await page.exposeFunction('__sk3dSfxSave', (filename, b64) => {
//     fs.writeFileSync(`${outDir}/${filename}`, Buffer.from(b64, 'base64'));
//   });
//   await page.addScriptTag({ path: 'scripts/render-sfx.mjs', type: 'module' });
//   await page.waitForFunction(() => window.__sk3dSfxRender);
//   const summary = await page.evaluate(() => window.__sk3dSfxRender());
//   console.log(JSON.stringify(summary, null, 2));
//   await browser.close();
//
// Output directory resolution: process.env.SFX_OUT (when a Node
// runner evaluates this in a browser context) →
// window.__sk3dSfxOut → '/tmp/sk3d-sfx'.
// ============================================================

import { renderSfx } from '../src/audio/sfx.js';
import { MusicEngine } from '../src/audio/music.js';

const OUT_DIR =
  (typeof process !== 'undefined' && process.env && process.env.SFX_OUT) ||
  (typeof window !== 'undefined' && window.__sk3dSfxOut) ||
  '/tmp/sk3d-sfx';

const SAMPLE_RATE = 44100;
const MUSIC_CYCLES = 2;   // QA render window per track
const MUSIC_SEED = 12345; // deterministic music render
const MUSIC_TAIL = 3.5;   // seconds of decay tail after the last step

// Render windows and per-recipe options for each SFX name.
const SFX_SPECS = [
  { name: 'engine', duration: 2.0, opts: { speed01: 0.65 } },
  { name: 'boost', duration: 1.2 },
  { name: 'drift', duration: 1.0 },
  { name: 'itemPickup', duration: 0.7 },
  { name: 'useItem', duration: 0.3 },
  { name: 'shell', duration: 0.8 },
  { name: 'redShell', duration: 0.7 },
  { name: 'banana', duration: 0.7 },
  { name: 'star', duration: 1.2 },
  { name: 'lightning', duration: 1.0 },
  { name: 'crash', duration: 0.8 },
  { name: 'countdown', duration: 0.5 },
  { name: 'go', duration: 0.8 },
  { name: 'lap', duration: 1.0 },
  { name: 'finish', duration: 1.5 },
  { name: 'victory', duration: 3.2 },
  { name: 'uiClick', duration: 0.25 },
  { name: 'uiHover', duration: 0.25 },
  { name: 'musicIntro', duration: 2.2 },
  { name: 'menuMusic', duration: 2.2 },
];

/**
 * Renders one SFX into an OfflineAudioContext and returns the
 * resulting AudioBuffer.
 * @param {string} name
 * @param {Object} [opts] { sampleRate, duration, opts }
 */
export async function renderSfxName(name, { sampleRate = SAMPLE_RATE, duration = 1.0, opts = {} } = {}) {
  const ctx = new OfflineAudioContext(2, Math.ceil(sampleRate * duration), sampleRate);
  renderSfx(ctx, ctx.destination, name, opts);
  return ctx.startRendering();
}

/**
 * Renders one music track (cycles repetitions of the progression)
 * into an OfflineAudioContext and returns the AudioBuffer.
 * @param {string} name
 * @param {Object} [opts] { sampleRate, cycles, seed }
 */
export async function renderMusicTrack(name, { sampleRate = SAMPLE_RATE, cycles = MUSIC_CYCLES, seed = MUSIC_SEED } = {}) {
  const duration = MusicEngine.trackDuration(name, cycles) + MUSIC_TAIL;
  const ctx = new OfflineAudioContext(2, Math.ceil(sampleRate * duration), sampleRate);
  MusicEngine.renderOffline(ctx, ctx.destination, name, seed, cycles);
  return ctx.startRendering();
}

/**
 * Encodes an AudioBuffer as a 16-bit PCM WAV file (ArrayBuffer).
 * @param {AudioBuffer} buffer
 */
export function encodeWav(buffer) {
  const numCh = buffer.numberOfChannels;
  const sampleRate = buffer.sampleRate;
  const len = buffer.length;
  const bytesPerSample = 2;
  const blockAlign = numCh * bytesPerSample;
  const dataSize = len * blockAlign;
  const ab = new ArrayBuffer(44 + dataSize);
  const dv = new DataView(ab);
  const writeStr = (off, s) => {
    for (let i = 0; i < s.length; i++) dv.setUint8(off + i, s.charCodeAt(i));
  };
  writeStr(0, 'RIFF');
  dv.setUint32(4, 36 + dataSize, true);
  writeStr(8, 'WAVE');
  writeStr(12, 'fmt ');
  dv.setUint32(16, 16, true);
  dv.setUint16(20, 1, true); // PCM
  dv.setUint16(22, numCh, true);
  dv.setUint32(24, sampleRate, true);
  dv.setUint32(28, sampleRate * blockAlign, true);
  dv.setUint16(32, blockAlign, true);
  dv.setUint16(34, 16, true);
  writeStr(36, 'data');
  dv.setUint32(40, dataSize, true);
  const chans = [];
  for (let c = 0; c < numCh; c++) chans.push(buffer.getChannelData(c));
  let off = 44;
  for (let i = 0; i < len; i++) {
    for (let c = 0; c < numCh; c++) {
      const s = Math.max(-1, Math.min(1, chans[c][i]));
      dv.setInt16(off, s < 0 ? s * 0x8000 : s * 0x7fff, true);
      off += 2;
    }
  }
  return ab;
}

/** Peak sample amplitude (0..1) across all channels — QA signal. */
function peakOf(buffer) {
  let peak = 0;
  for (let c = 0; c < buffer.numberOfChannels; c++) {
    const data = buffer.getChannelData(c);
    for (let i = 0; i < data.length; i++) {
      const a = Math.abs(data[i]);
      if (a > peak) peak = a;
    }
  }
  return peak;
}

/** ArrayBuffer -> base64 (chunked so large WAVs don't blow the stack). */
function abToBase64(buffer) {
  const bytes = new Uint8Array(buffer);
  let bin = '';
  const CHUNK = 0x8000;
  for (let i = 0; i < bytes.length; i += CHUNK) {
    bin += String.fromCharCode.apply(null, bytes.subarray(i, i + CHUNK));
  }
  return btoa(bin);
}

/**
 * Hands a rendered file to the controller. Prefers the injected
 * window.__sk3dSfxSave(filename, base64) sink; falls back to a
 * browser download (headed QA).
 * @returns {boolean|string} true if saved via sink, 'download' on
 *   browser fallback, false if neither is available.
 */
function saveFile(filename, b64) {
  const sink = typeof window !== 'undefined' ? window.__sk3dSfxSave : null;
  if (typeof sink === 'function') {
    sink(filename, b64);
    return true;
  }
  if (typeof document !== 'undefined') {
    const a = document.createElement('a');
    a.href = 'data:audio/wav;base64,' + b64;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();
    return 'download';
  }
  return false;
}

/**
 * Renders every SFX and every music track, saving one WAV per file.
 * @returns {Promise<Array<Object>>} Summary rows for the controller:
 *   { type, name, duration, channels, peak, saved } or { name, error }.
 */
export async function main() {
  const results = [];

  // --- SFX ---
  for (const spec of SFX_SPECS) {
    try {
      const buffer = await renderSfxName(spec.name, { sampleRate: SAMPLE_RATE, duration: spec.duration, opts: spec.opts });
      const filename = `sfx-${spec.name}.wav`;
      const saved = saveFile(filename, abToBase64(encodeWav(buffer)));
      results.push({
        type: 'sfx',
        name: spec.name,
        duration: +buffer.duration.toFixed(3),
        channels: buffer.numberOfChannels,
        peak: +peakOf(buffer).toFixed(4),
        saved,
      });
    } catch (err) {
      results.push({ type: 'sfx', name: spec.name, error: String(err) });
    }
  }

  // --- Music ---
  for (const name of MusicEngine.trackNames()) {
    try {
      const buffer = await renderMusicTrack(name, { sampleRate: SAMPLE_RATE, cycles: MUSIC_CYCLES, seed: MUSIC_SEED });
      const filename = `music-${name.replace(/\s+/g, '-').toLowerCase()}.wav`;
      const saved = saveFile(filename, abToBase64(encodeWav(buffer)));
      results.push({
        type: 'music',
        name,
        duration: +buffer.duration.toFixed(3),
        channels: buffer.numberOfChannels,
        peak: +peakOf(buffer).toFixed(4),
        saved,
      });
    } catch (err) {
      results.push({ type: 'music', name, error: String(err) });
    }
  }

  if (typeof console !== 'undefined') {
    console.log(`[render-sfx] rendered ${results.length} files into ${OUT_DIR}`);
    for (const r of results) {
      if (r.error) console.warn(`[render-sfx] ${r.type} ${r.name}: ${r.error}`);
    }
  }
  return results;
}

// Browser entry point for the controller:
//   await page.evaluate(() => window.__sk3dSfxRender());
if (typeof window !== 'undefined') {
  window.__sk3dSfxRender = main;
  window.__sk3dSfx = { renderSfxName, renderMusicTrack, encodeWav };
}
