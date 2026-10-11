import { createHash } from 'node:crypto';
import { OfflineAudioContext } from '/tmp/sk3d-audio-qa/node_modules/web-audio-api/index.js';
import { renderSfx } from '../src/audio/sfx.js';

const names = [...`engine boost drift uiClick uiSelect driftReleaseMiniBoost offroad itemPickup useItem shell redShell banana star lightning crash driftReady posDown posUp landing countdown go pickup lap finalLap cheer finish victory uiHover musicIntro menuMusic`.split(' ')];
const durationFor = (name) => name === 'engine' ? 2.2 : ['victory', 'star', 'finish'].includes(name) ? 3.2 : 1.5;

async function render(name) {
  const ctx = new OfflineAudioContext(2, Math.ceil(48000 * durationFor(name)), 48000);
  renderSfx(ctx, ctx.destination, name, { volume: 0.8, speed01: 0.65, intensity: 0.8, dur: durationFor(name) });
  return ctx.startRendering();
}
function stats(buffer) {
  let peak = 0;
  const hash = createHash('sha256');
  for (let ch = 0; ch < buffer.numberOfChannels; ch++) {
    const samples = buffer.getChannelData(ch);
    for (const sample of samples) peak = Math.max(peak, Math.abs(sample));
    hash.update(Buffer.from(samples.buffer, samples.byteOffset, samples.byteLength));
  }
  return { peak, hash: hash.digest('hex').slice(0, 16), frames: buffer.length, channels: buffer.numberOfChannels };
}

const results = [];
for (const name of names) {
  const a = stats(await render(name));
  const b = name === 'boost' ? stats(await render(name)) : a;
  results.push({ name, ...a, deterministic: a.hash === b.hash });
}
const maxPeak = Math.max(...results.map((r) => r.peak));
const nondeterministic = results.filter((r) => !r.deterministic);
const pass = results.length === names.length && maxPeak <= 1.0 && nondeterministic.length === 0;
console.log(`AUDIO_DETERMINISM=${pass ? 'PASS' : 'FAIL'} rendered=${results.length}/${names.length} maxPeak=${maxPeak.toFixed(6)} nondeterministic=${nondeterministic.map((r) => r.name).join(',') || 'none'}`);
for (const result of results) console.log(`AUDIO_SFX name=${result.name} peak=${result.peak.toFixed(6)} hash=${result.hash} frames=${result.frames}`);
if (!pass) process.exitCode = 1;
