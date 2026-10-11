# ADR-004: Simple string state machine

## Status
Accepted

## Context
The game has 5 clear phases (menu, countdown, race, finished) plus pause.
Hierarchical state machines add ceremony; we need something a human can
reason about in `main.js` and debug with one `getState()` call.

## Decision
A tiny module (`GameState.js`) exposing `STATES`, `getState()`, `setState()`.
The main loop branches on `state === STATES.RACE`, etc. Debug hooks expose it
as `window.__sk3d.getState()`.

## Options Considered
1. **HSM / XState** — overkill, external dep. Rejected.
2. **String state + if-branches** — chosen: obvious, testable (`?test`).

## Consequences
- All transitions are explicit `setState` calls in `main.js` — no hidden
  transitions (a bug class eliminated; see `game-quality-gates` rule 1).
- Restart flows through COUNTDOWN again → `raceManager.start()` → RACE.

## Related
- `src/game/GameState.js`, `src/main.js`
