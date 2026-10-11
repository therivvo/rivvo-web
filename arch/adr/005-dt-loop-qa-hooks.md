# ADR-005: dt-clamped loop + QA hooks

## Status
Accepted

## Context
Headless WebGL (SwiftShader) runs at ~1-2 fps. Playwright-based QA needs the
game to be *drivable and capturable* in that environment, and gameplay logic
must never depend on 60fps (frame-rate independence — `game-quality-gates`).

## Decision
- `GameLoop` clamps `dt` (max 0.05 s) and passes it everywhere — physics is
  frame-rate independent; on slow headless it just runs in slow-motion.
- `?test` URL flag disables PostFX (≈30× faster), shortens the countdown.
- `window.__freezeCam` freezes the chase camera for deterministic close-ups.
- `?demo` drives all karts with AI for deterministic motion capture.

## Consequences
- QA scripts (`sk3d-*.cjs`) can teleport karts, force states, and capture
  frames reliably.
- Real players get a stable 60fps experience with identical physics.

## Related
- `src/main.js` (TEST/DEMO flags), `src/game/GameLoop.js`
