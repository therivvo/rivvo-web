# ADR-002: Hand-rolled arcade physics

## Status
Accepted

## Context
Kart games need *feel* — drift charges, mini-boosts, squash & stretch, wall
bounce, rubber-band AI. General physics engines (Rapier/Cannon/ammo) solve
rigid-body dynamics but fight you on arcade "juice" and are heavy to bundle.

## Decision
Hand-roll the physics in `KartPhysics.js`: heading integration, speed target
(accel/brake/boost/off-road/cruise), drift charge, path-damp steering, wall
bounce, collision circles. ~200 lines, fully tunable via `config.js`.

## Options Considered
1. **Rapier WASM** — real collisions, +300KB, overkill for a circle-vs-road game.
2. **Cannon-es** — same overkill, fewer guarantees.
3. **Custom** — chosen: full control, zero bundle cost, deterministic.

## Consequences
- Off-road/track detection uses the centerline projection (`nearest` on the
  Catmull-Rom path) — cheap and robust.
- **Pitfall encoded:** `brake` accelerates toward `reverseSpeed` (reverse is a
  feature). AI must never "brake to slow down" — it eases the throttle.
- Kart-kart collision is circle-based push-apart (`_resolveKartCollisions`).

## Related
- `src/entities/KartPhysics.js`, `config.js:physics.*`
