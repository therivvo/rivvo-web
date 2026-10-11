# ADR-003: 100% procedural assets

## Status
Accepted

## Context
Open-source repo, MIT, CI-built, no binary asset pipeline. Bundling GLB/Draco
models or MP3/OGG audio requires a pipeline and bloats the repo. We want zero
"assets" checked in — every texture and sound synthesized at runtime.

## Decision
Generate everything procedurally:
- **Textures:** canvas 2D → `THREE.CanvasTexture` (road, grass, checker,
  banner FINISH, '?' box, number plates).
- **Models:** Three.js primitives composed in code (karts, driver chibi,
  track ribbon, trees, palms, grandstands, crowd).
- **Audio:** WebAudio — 19 SFX recipes + 3 looping music tracks synthesized
  with seeded RNG (offline-renderable, byte-reproducible for QA).

## Options Considered
1. **External art/audio** — better raw fidelity but licensing + pipeline + repo
   weight. Rejected for the open-source goal.
2. **Procedural** — chosen: reproducible, MIT-clean, no binary blobs.

## Consequences
- Quality ceiling is the code, not asset sourcing — polish lives in
  `Materials.js` / `sfx.js` recipes.
- The `?test`/`__freezeCam` QA hooks are essential (software GL is slow).

## Related
- `src/render/Materials.js`, `src/audio/sfx.js`, `src/audio/music.js`
