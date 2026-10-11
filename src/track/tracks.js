/**
 * Super Kart 3D.js — track registry (single source of truth).
 *
 * Every track = a layout + race settings + a look:
 *   points       closed control-point loop (Vector3[]) for TrackBuilder
 *   laps         race length for this track (CONFIG.game.totalLaps at boot)
 *   turboPadTs   turbo-pad cluster centres, normalized lap position 0..1
 *                (put them on straights)
 *   rampTs       optional launch-ramp positions. Real circuits have none, so
 *                no track sets this; TrackBuilder still supports it.
 *   theme        'meadow' (day world) or 'neon' (night city world)
 *   palette      optional colour overrides layered on top of the theme
 *                (sky / fog / light / ground). See Environment.buildEnvironment.
 *
 * Scale is real karting: 0.9-1.8 km laps, a 10 m road, corner radii from
 * ~15 m hairpins to 60 m sweepers (cornering speed √(grip × R), see
 * CONFIG.physics). New layouts are written as recipes (see loopBuilder.js)
 * so lengths and corners can be tuned by editing a number. Ids are what ?track=<id> and
 * localStorage 'sk3d.track' store; never renumber an existing track.
 */
import { TRACK_PATH, CITY_PATH } from './TrackBuilder.js';
import { buildLoop } from './loopBuilder.js';

/** Uniformly scale a hand-made loop in plan (x/z); heights are kept. */
function scaleLoop(points, k) {
  return points.map((p) => p.clone().set(p.x * k, p.y, p.z * k));
}

export const TRACKS = [
  {
    id: 1,
    name: 'Meadow Circuit',
    icon: '🌇',
    desc: 'Rolling sunny hills and fast sweeping bends. 1.2 km.',
    // Original layout ×3: ~1.2 km, 36 m minimum radius — a fast flowing track.
    points: scaleLoop(TRACK_PATH, 3),
    laps: 3,
    turboPadTs: [0.18, 0.78],
    theme: 'meadow',
  },
  {
    id: 2,
    name: 'Neon City',
    icon: '🌆',
    desc: 'Street circuit — long straights and tight 16 m hairpins under the neon. 1.3 km.',
    // Original layout ×2: ~1.3 km, 16 m hairpins.
    points: scaleLoop(CITY_PATH, 2),
    laps: 3,
    turboPadTs: [0.18, 0.78],
    theme: 'neon',
    music: 'Neon Nights',
  },
  {
    id: 3,
    name: 'Desert Canyon',
    icon: '🏜️',
    desc: 'Sun-baked sand and the longest straights in the cup. 1.7 km.',
    // ~1.74 km: long outer straights, a canyon notch and a kinked back straight.
    points: buildLoop({
      name: 'desert',
      elev: [0, 4, 1.5],
      segs: [['A', 250], [90, 40], ['B', 100], [90, 35], [80], [-90, 30], [40], [-90, 30], [80], [90, 35], [60], [90, 45], [150], [45, 60], [-45, 60], [60], [90, 45], [300], [90, 40]],
    }),
    laps: 3,
    turboPadTs: [0.53, 0.79],
    theme: 'meadow',
    palette: {
      fog: 0xf1d6a4, skyTop: 0x3d8ed4, skyMid: 0x9ccdec, skyHorizon: 0xf6dfb4, sun: 0xfff0c0,
      hemiSky: 0xfff0d8, hemiGround: 0xd8b07a,
      ground: 0xe2c08a, groundFlat: true, noWater: true,
      ibl: ['#3d8ed4', '#9ccdec', '#f6dfb4', '#d8b07a'],
    },
  },
  {
    id: 4,
    name: 'Snow Peak',
    icon: '🏔️',
    desc: 'Mountain pass — a 10 m climb, switchbacks and tight hairpins. 1.1 km.',
    // ~1.07 km: east climb, then three stacked switchback rows back down.
    points: buildLoop({
      name: 'snow',
      elev: [0, 9, 2],
      segs: [['A', 160], [90, 30], ['B', 150], [90, 18], [220], [180, 16], [110], [-180, 16], [110], [90, 18], [60], [90, 30]],
    }),
    laps: 3,
    turboPadTs: [0.19, 0.38],
    theme: 'meadow',
    palette: {
      fog: 0xe4edf8, skyTop: 0x5a8cc6, skyMid: 0xa8c7e8, skyHorizon: 0xeef4fb, sun: 0xf4f8ff,
      hemiSky: 0xeef4ff, hemiGround: 0xc8d4e8,
      ground: 0xf4f7fc, groundFlat: true,
      ibl: ['#5a8cc6', '#a8c7e8', '#eef4fb', '#dfe7f2'],
    },
  },
  {
    id: 5,
    name: 'Beach Bay',
    icon: '🏖️',
    desc: 'Sunset by the sea — short, flowing S-curves. Great first race. 0.9 km.',
    // ~0.92 km: two S-bends on the north side, a wiggle down the west.
    points: buildLoop({
      name: 'beach',
      elev: [0, 2, 1],
      segs: [['A', 160], [90, 35], ['B', 120], [90, 35], [60], [-60, 40], [60, 40], [40], [90, 35], [80], [-45, 40], [45, 40], [40], [90, 35]],
    }),
    laps: 4,
    turboPadTs: [0.24, 0.68],
    theme: 'meadow',
    palette: {
      fog: 0xffc8a0, skyTop: 0x4b6cc0, skyMid: 0xee9f84, skyHorizon: 0xffd4a4, sun: 0xffb46e,
      hemiSky: 0xffd8b8, hemiGround: 0x9cc88a,
      ground: 0xfff0d0,
      ibl: ['#4b6cc0', '#ee9f84', '#ffd4a4', '#9cc88a'],
    },
  },
  {
    id: 6,
    name: 'Volcano Night',
    icon: '🌋',
    desc: 'Lava-lit and technical — chicanes and stacked hairpins. Hardest track. 1.2 km.',
    // ~1.18 km: chicanes on both long sides, a stepped hairpin ladder up top.
    points: buildLoop({
      name: 'volcano',
      elev: [0, 6, 2],
      segs: [['A', 250], [90, 25], ['B', 80], [60, 30], [-60, 30], [70], [90, 25], [50], [-90, 18], [50], [90, 18], [20], [90, 18], [50], [-90, 18], [50], [90, 25], [70], [-60, 28], [60, 28], [90], [90, 25]],
    }),
    laps: 3,
    turboPadTs: [0.17, 0.82],
    theme: 'neon',
    music: 'Neon Nights',
    palette: {
      fog: 0x2a0d0a, skyTop: 0x1c0707, skyMid: 0x3c100a, skyHorizon: 0x5c1c0c, sun: 0xffb080,
      hemiSky: 0x7a3020, hemiGround: 0x1a0808,
      ground: 0x5a3a36,
      ibl: ['#1c0707', '#3c100a', '#7a2a10', '#140606'],
    },
  },
];

/** Registry lookup; unknown ids fall back to the Meadow Circuit. */
export function getTrack(id) {
  return TRACKS.find((t) => t.id === Number(id)) || TRACKS[0];
}

/** True when the id names a real track. */
export function isTrackId(id) {
  return TRACKS.some((t) => t.id === Number(id));
}

/**
 * Which track this page load races on. Same precedence the game always used:
 * the menu's in-memory pick (window.__sk3dTrack), then the persisted choice
 * (localStorage 'sk3d.track'), then the ?track= query param.
 */
export function resolveTrackId() {
  if (typeof window !== 'undefined' && isTrackId(window.__sk3dTrack)) return Number(window.__sk3dTrack);
  try {
    const saved = Number(localStorage.getItem('sk3d.track'));
    if (isTrackId(saved)) return saved;
  } catch { /* private mode */ }
  try {
    const q = Number(new URLSearchParams(location.search).get('track'));
    if (isTrackId(q)) return q;
  } catch { /* no location */ }
  return 1;
}
