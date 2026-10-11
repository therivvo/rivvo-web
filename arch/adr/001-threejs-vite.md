# ADR-001: Three.js + Vite, no game engine

## Status
Accepted

## Context
A WebGL kart racer that must run on desktop and mobile, deploy to GitHub
Pages, and stay 100% open-source with zero third-party runtime assets.
Candidate engines: Phaser, Babylon, Godot (Web export), custom Three.js.

## Decision
Use **Three.js (r164) + Vite 5**. Three.js is a rendering library, not a game
engine — we own the loop, the state machine, and the physics. Vite gives fast
dev (`:3457`), `base: './'` for Pages subpath builds, and trivial CI.

## Options Considered
1. **Phaser** — great 2D, weak 3D. Rejected: the game is 3D cartoon.
2. **Babylon** — heavier, engine idioms, less familiar. Rejected.
3. **Godot Web export** — large WASM payload, no npm workflow. Rejected.
4. **Three.js** — chosen: full control, tiny footprint, procedural-friendly.

## Consequences
- We implement loop/state/AI ourselves (more code, full control).
- Software GL (SwiftShader) renders ~1-2 fps — QA needs the `?test` fast mode
  (PostFX off) and `__freezeCam` hooks.
- WebGL1 fallback impossible — accepted (WebGL2 baseline).

## Related
- `docs/ARCHITECTURE.md` — module contracts
