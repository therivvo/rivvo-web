# Super Kart 3D.js — Technical Architecture

**Version:** 1.0 · **Date:** 2026-08-08 · **Author:** Feco Linhares
**Stack:** Three.js (r164) + Vite 5 · Web · MIT · 100% procedural assets

## Architecture Overview

A single-page WebGL kart racer with a **module-per-system** layout. The
runtime is a plain `requestAnimationFrame` loop (`GameLoop`) driving a small
**state machine** (`BOOT → MENU → COUNTDOWN → RACE → FINISHED`). Every system
(karts, physics, track, items, AI, audio, UI) is an independent ES module with
a documented public contract (see `ARCHITECTURE.md`); `main.js` is the only
wiring file. No game engine, no physics engine — the arcade physics is
hand-rolled in `KartPhysics` for full control of the "juice".

## System Map

| System | Depends On | Used By |
|--------|-----------|---------|
| GameLoop | — | everything (dt-driven) |
| GameState | — | main.js |
| SceneManager / PostFX | Three.js | render |
| TrackBuilder | Materials | raceManager, camera |
| Environment | Materials, TrackBuilder.smoothH | scene |
| Kart | Materials, KartPhysics | raceManager, camera |
| KartPhysics | CONFIG, track path | Kart |
| AIController | track.centerline | raceManager |
| RaceManager | Kart, AIController, ItemBox, PowerUp | main.js |
| ItemBox / PowerUp | CONFIG, Materials | raceManager |
| AudioManager | sfx.js, music.js | main.js, raceManager |
| HUD / Menu / TouchControls | — | main.js |

**Rule:** no circular imports (verified by `game-quality-gates`). `config.js`
is the single tuning source of truth.

## Key Decisions

| ADR | Decision | Status |
|-----|----------|--------|
| ADR-001 | Three.js + Vite, no game engine | Accepted |
| ADR-002 | Hand-rolled arcade physics (no Rapier/Cannon) | Accepted |
| ADR-003 | 100% procedural assets (canvas textures + WebAudio) | Accepted |
| ADR-004 | Simple string state machine, not a HSM | Accepted |
| ADR-005 | dt-clamped loop (headless-friendly, QA via `?test`) | Accepted |

## Critical Paths

- **Core mechanic (drift → mini-boost)** — latency-sensitive: input → physics
  → camera → audio must all update in one frame.
- **Item pickup** — distance check per frame (swept generously at 43 m/s).
- **Audio engine loops** — pitch follows speed; must never restart per frame.

## Performance Targets

- **Platform:** desktop + mobile WebGL (software GL must still boot — QA)
- **Frame budget:** 16 ms desktop, ≤33 ms mobile
- **Draw calls:** < 200 (instanced meshes for forest/crowd/curbs)
- **Memory:** < 200 MB; no per-frame allocations in physics hot path

## Next Steps

- [ ] ADRs for item rubber-band and cruise-mode finish
- [ ] HUD minimap (project karts onto the path)
- [ ] Turbo pads on track (gameplay depth)
