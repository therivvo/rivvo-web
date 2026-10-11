# Super Kart 3D.js — Architecture & Module Contracts

> Internal contract document. Sub-agents implementing a module MUST keep the
> public signatures below stable — other modules depend on them. Implement the
> body, never change the interface without updating this document.

## Game vision

Cartoon arcade kart racer in the style of the genre's classics — **Mario
Kart**, **Sonic & All-Stars Racing** and **Crash Nitro Kart** (Mario Kart 8 /
Crash Team Racing visual language): vibrant saturated colors, smooth
toon-shaded materials with subtle rim highlights, low-poly-but-clean geometry
with no jaggies, juicy juice everywhere (particles, screen shake, squash &
stretch, camera shake, bloom). Target visual bar: **AAA** — the QA critic
compares screenshots side by side against reference standards and rejects
anything below ~9.5/10 per category.

UI copy is 100% English. Project is open source — no secrets, no local-only
paths, no absolute paths in docs or code.

## File layout

```
index.html              — entry, SEO/OG meta, fonts
src/
  main.js               — bootstrap & wiring (controller-owned)
  config.js             — CONFIG tuning constants (controller-owned)
  game/
    GameState.js        — state machine (controller-owned)
    GameLoop.js         — rAF loop, dt clamp (controller-owned)
    RaceManager.js      — race orchestration (powerups agent)
  entities/
    Kart.js             — kart mesh + state (kart agent)
    KartPhysics.js      — arcade physics (kart agent)
    AIController.js     — AI drivers (powerups agent)
    ItemBox.js          — item boxes (powerups agent)
    PowerUp.js          — item logic + projectiles (powerups agent)
  track/
    TrackBuilder.js     — track geometry + waypoints (track agent)
    Environment.js      — sky, light, props, fog (track agent)
  render/
    SceneManager.js     — renderer/scene/camera (controller-owned)
    PostFX.js           — bloom/color grade/vignette (track agent)
    Materials.js        — toon materials + canvas textures (track agent)
    Particles.js        — particle system (kart agent)
  audio/
    AudioManager.js     — manager, lazy context (audio agent)
    sfx.js              — pure SFX recipes (audio agent)
    music.js            — procedural music engine (audio agent)
  ui/
    Menu.js             — title menu overlay (ui agent)
    HUD.js              — in-race HUD (ui agent)
    TouchControls.js    — mobile touch buttons (ui agent)
    ui.css              — all UI styling (ui agent)
public/
  favicon.svg, og-image.png
docs/ screenshots, reference (ITEMS-REFERENCE.md)
```
ARCHITECTURE.md, DESIGN.md live at the repo root (same layout as Match-3D.js).

## Module contracts

### GameLoop (done)
- `start(updateFn)` — begin rAF; `updateFn(dt, t)` each frame, `dt` clamped to 0.05.
- `stop()`.

### SceneManager (done)
- `createScene(container)` → `{ scene, camera, renderer }`.
- Camera: PerspectiveCamera 62° FOV. Renderer: WebGLRenderer, antialias, shadows, pixelRatio cap 2.
- Handles resize.

### RaceManager
- `new RaceManager(scene, camera)`
- `init({ track, playerKart, aiKarts, itemBoxes, audio, particles })`
- `start()`, `restart()`, `update(dt)`
- `getStandings()` → `[{ kart, position, lap, progress01, finished }]` sorted by race progress.
- **`aiControllers` is the single source of truth for AI drivers** (created in
  `init()`, updated in `update()`). main.js must NOT keep its own controller
  array — the finish-cruise controller (player kart after the line) is pushed
  here and `restart()` drops it (`filter(c => c.kart !== player || _playerAI)`),
  which is what guarantees the player regains control on `Race Again`/`R`.
- `onPlayerFinish(place, totalTime)` — called once when player crosses the finish line.
- Exposes `player`, `karts`, `track`, `elapsed`, `raceOver`.

### TrackBuilder
- `buildTrack(scene)` → `{ group, path, waypoints, startLine, length }`
  - `path`: THREE.Curve usable with `path.getPointAt(t)` / `getTangentAt(t)`.
  - `waypoints`: `THREE.Vector3[]` closed loop for AI steering.
  - `startLine`: `{ position: Vector3, direction: Vector3, width }`.
  - Track must be a closed loop with elevation, banked curves, toon materials.
- Exports `TRACK_PATH` (waypoint array) for AI + `getRoadWidthAt(t)`.

### Environment
- `buildEnvironment(scene)` — sky dome/skybox, directional light + shadows, fog,
  clouds, mountains, trees/palms, water, crowd props. Cartoon saturated style.
- `update(dt, t)` — animate clouds, water, flags.

### Kart
- `new Kart({ color, isPlayer, startPosition, startHeading })`
- `.group` — root Object3D (kart + driver + wheels).
- `setControls({ steer, throttle, brake, drift, useItem })` — player input; steer in [-1,1].
- `update(dt, ctx)` — ctx `{ track, raceManager, particles }`.
- Effects API: `applyBoost(durationMs)`, `setStarred(bool)`, `applyScale(scale, durationMs)`,
  `hitBanana()`, `hitShell()`, `setInvincible(bool)`, `nudge(dir)`.
- `.state` — `{ speed, position: Vector3, heading, drifting, driftCharge,
  boost, offRoad, spinOut, lap, progress01, finished }`.
- `.finished`, `.position` (race rank int), `.totalTime`.

### KartPhysics
- `step(kart, input, dt, track)` — pure-ish physics step mutating `kart.state`.
  Arcade model: steer-rate scales with speed, drift with charge → mini-boost,
  off-road slowdown, wall bounce at track edges, gravity on ramps, squash &
  stretch on accel/boost.
- **Trick ramps**: the kart's ground height interpolates the ramp wedge slope
  (via `track.ramps[].length/height` + `point/dir`), so it CLIMBS the ramp
  visually; the launch fires near the top (`vY=6.5`, position anchored past the
  airborne threshold) into a ~0.4s arc — the mid-air trick + landing boost.

### AIController
- `new AIController(kart, track, raceManager)`
- `update(dt)` — sets `kart.setControls(...)` with PROGRESS-ANCHORED navigation:
  the steering reference derives from the kart's arc-length `state.progress01`
  mapped onto the 240-point centerline (`RaceManager.centerline`,
  `getSpacedPoints(240).slice(0,240)`), so the look-ahead target can never sit
  behind the kart (fixes the "opponents run backwards" bug). Rubber-banding vs
  the player AND vs the rival immediately ahead (AI-vs-AI chase, up to +6%),
  personal racing lanes (±1.2m golden-ratio scale), item usage targeting the
  rival ahead, and crash recovery that NEVER brakes (in this physics
  brake = reverse).

### ItemBox
- `createItemBoxes(track)` → `ItemBox[]` placed along the track.
- `update(dt, karts)` — bob + spin animation, pickup detection, respawn timer.
- On pickup: callback into `RaceManager.pickupItem(kart)` which rolls a
  `PowerUpType` and calls `kart.heldItem = type`.

### PowerUp (item logic)
- `PowerUpType = { MUSHROOM, SHELL, RED_SHELL, BANANA, STAR, LIGHTNING }`.
- `useItem(kart, ctx)` — applies effect; spawns `ShellProjectile` / `Banana` in scene.
- `ShellProjectile`: straight or homing (RED targets nearest kart ahead), hits karts → `kart.hitShell()`.
- `Banana`: dropped behind kart; collision → `kart.hitBanana()` (spin-out).
- `STAR`: kart invincible + boost for `starDurationMs`, rainbow trail.
- `LIGHTNING`: shrink ALL rival karts for `lightningDurationMs` (`kart.applyScale`).

### PostFX
- `new PostFX(renderer, scene, camera)`
- `render(dt)` — EffectComposer chain: RenderPass → UnrealBloomPass → ColorGrade/ShaderPass (saturation/contrast) → Vignette → Output.
- Knobs from `CONFIG.render`.

### Materials
- `toonMaterial(color, opts)` — MeshToonMaterial / Lambert with gradient map.
- `cartoonOutline(mesh, color, thickness)` — inverted-hull outline or
  EdgeGeometry+LineSegments helper for crisp cartoon silhouettes.
- `canvasTexture(size, drawFn)` — procedural textures (road, grass, checker, gradient).

### Particles
- `new ParticleSystem(scene)`
- `emit(type, position, opts)` — `exhaust`, `boost` (flame), `drift` (smoke),
  `pickup` (sparkle), `explosion`, `confetti`, `starTrail`, `lightning`.
- `update(dt)`.

### AudioManager
- `new AudioManager()`
- `init()` — called on first user gesture (autoplay policy). Builds master chain
  (volume → DynamicsCompressor → destination).
- `play(name, opts)` — one-shot SFX (name from sfx.js).
- `startMusic()`, `stopMusic()`, `nextTrack()`.
- `setEngineLoop(kartId, speed01)` — continuous engine sound per kart.
- `setMasterVolume(v)`, `setMusicVolume(v)`.
- Engine/UI play calls MUST be safe before `init()` (no-op, not throw).

### sfx.js
- `renderSfx(ctx, out, name, opts)` — pure recipes accepting ANY BaseAudioContext
  (OfflineAudioContext for QA). Names: `engine`, `boost`, `drift`, `itemPickup`,
  `useItem`, `shell`, `redShell`, `banana`, `star`, `lightning`, `crash`,
  `countdown`, `go`, `lap`, `finish`, `victory`, `uiClick`, `uiHover`, `menuMusic`.

### music.js
- `MusicEngine` — procedural lo-fi/hype playlist (patterns from match-3djs music.js).
- `start()`, `stop()`, `next()`, `renderOffline(ctx, out, trackName, seed, cycles)`.

### Menu
- `new Menu({ onStart })`
- `show()`, `hide()`.
- Title screen: game logo, "Start Race", "How to Play" (controls table), kart color
  picker, credit footer. Cartoon styling, animated entrance.

### HUD
- `new HUD()`
- `show()`, `hide()`, `reset()`.
- `update(raceManager, player)` — position pips (1st/6th), lap counter, total time,
  speedometer (km/h style), held item slot icon.
- `countdown(n|'GO')`, `showFinish(place, time)`, `showMessage(text)`.

### TouchControls
- `new TouchControls({ onSteer, onItem })`
- `show()` only when touch device (innerWidth <= 768 or pointer coarse).
- Big (>=56px) left/right steer buttons + item button; no keyboard mixing.

### main.js wiring
- Boot: SceneManager → Environment → TrackBuilder → PostFX → AudioManager →
  RaceManager → Menu/HUD/TouchControls.
- `?demo` query param: enables cinematic autopilot (all karts AI, camera swoops)
  — used by visual QA to capture beautiful frames deterministically.

## Quality gates (visual critic)

The QA critic sub-agent runs headless captures (desktop + mobile), analyzes
with vision, and scores: Lighting & Mood, Materials & Shading, Composition &
Camera, UI Polish, Coherence, Performance (fps). Reject < 9.5 any category →
file-specific fix list → implementer loop → re-capture. Blind side-by-side
against reference: judge which looks better, say why.
