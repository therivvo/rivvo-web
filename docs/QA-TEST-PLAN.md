# QA Test Plan — Super Kart 3D.js v0.1.0

> Follows the `game-dev-qa-test` workflow: test plans, smoke, regression, bug triage.
> Headless QA scripts live in the agent's cache (`/home/jarvis/.cache/sk3d-*.cjs`)
> and drive the game via Playwright against `?test` (PostFX off, fast countdown).

## 1. Scope
Release-critical checks for v0.1.0: boot, race loop, input, restart, items,
audio lifecycle, HUD, mobile basics, performance budget.

## 2. Test matrix

| ID | Area | Test | Method | Status |
|----|------|------|--------|--------|
| T01 | Boot | Game boots with 6 karts, track, no console errors | `sk3d-smoke.cjs` | ✅ PASS |
| T02 | Input | +steer turns the kart RIGHT (Three.js convention) | `sk3d-steer-test.cjs` | ✅ PASS |
| T03 | Items | Teleport onto item box → kart holds item, box deactivates | `sk3d-pickup-test.cjs` | ✅ PASS |
| T04 | Restart | Teleport far + R → kart returns to grid, lap 0, speed 0 | `sk3d-restart4.cjs` | ✅ PASS |
| T05 | Toast | Item toast shows icon+name above item slot (not screen-center) | `sk3d-toast-test.cjs` | ✅ PASS |
| T06 | Finish | Player finish → FINISHED state, cruise AI drives at 60%, music swells, no engine screech | manual + code audit | ✅ PASS |
| T07 | Audio | UI sounds on menu; off-road rumble; mini-boost SFX on drift release | code audit + manual | ✅ PASS |
| T08 | Mobile | Touch buttons (LEFT/RIGHT/ITEM) via pointer capture; AudioContext resumes on first gesture; menu has solid fallback (no backdrop-filter dependency) | code audit | ✅ PASS |
| T09 | Performance | Build < 200 draw calls (instanced), 60fps desktop, ≤33ms mobile | code audit + profiler | ⚠️ TBD manual |
| T10 | Restart control | Finish-cruise AIController REMOVED on restart (player regains input — the "game drives the car" bug) | `sk3d-restart-sig-test.cjs` (playerAIControlled false→true→false) | ✅ PASS |
| T11 | Trick ramp | Kart CLIMBS the wedge and launches airborne (vY>1, airTime>0.15) | `sk3d-ramp-unit-test.cjs` (physics unit test) | ✅ PASS |
| T12 | Smoke | Boot → race state, 6 karts, no errors (robust, waits for race) | `sk3d-smoke-robust.cjs` | ✅ PASS |
| T13 | AI backwards | Sim stress (shoves, launches, spins, rear-ends, Lakitu rescue) → 0 sustained backwards runs | `scripts/ai-backwards-test.mjs` (80 seeds × 2 tracks) | ✅ PASS |
| T14 | AI lanes | Lane adherence / wall bounces within stable corridor | `scripts/lane-probe.mjs` | ✅ PASS |
| T15 | AI passing | City standings change > 100/60s (no procession) | `scripts/procession-probe.mjs` (580/3600 frames) | ✅ PASS |
| T16 | Browser smoke | `?test` boots, race runs, NO page errors (headless Chromium) | `scripts/sk3d-qa.cjs` | ✅ PASS |
| T17 | Kerbs | Yaw-only alignment (0.0° up-vector deviation), MK8D proportions 0.9×0.6×0.17, 10% overlap (no curve/seam gaps) | geometry probe (`_kerb-probe`) | ✅ PASS |
| T18 | Finish line | Checker cells SQUARE (9×2.25m plane → 1.125m cells), opacity 1.0 | geometry probe | ✅ PASS |
| T19 | Item box | 256px texture, pure white panel, #ef233c glyph, gold trim | code + screenshot | ✅ PASS |
| T20 | Crowd jump | 2.0 Hz rectified pulse, per-part bob/phase sync, organic phases | code audit (Environment) | ✅ PASS |
| T21 | Items FX | Shell: PBR+outline+spin+84 m/s; banana: 0.72m+hop+minimap dot; lightning: 3-axis shrink+electric flash; star: rainbow paint | code + harness (0 events) | ✅ PASS |
| T22 | Neon redesign | '2' layout: start left straight UP (+Z), clockwise, 630m, 0 crossings, corners 4-8m (drift-clean) | `scripts/city-layout-probe.mjs` + harness | ✅ PASS |
| T23 | Neon props | Ramps curvature-checked on straights; turbo 0.78 bottom straight; item boxes off corners; lights/billboards/cranes path-driven | code probe (buildNeonCity) | ✅ PASS |
| T24 | Bots stuck | NO kart crawls <1 m/s for 2.5s+ (was: crashUntil ms-vs-s bug froze bots forever after any hit) | harness STUCK detection, 100 seeds × 2 tracks | ✅ PASS |
| T25 | Road clean | No painted text/logo decals on the asphalt (sponsor decals removed); kerbs slimmed to 0.55×0.5×0.14 | screenshot + code | ✅ PASS |
| T26 | City arcs | '2' layout rebuilt from straights + true circle arcs (R=14m): centerline ≥12m, kerb-edge folds 0/0 (inner kerb no longer crosses), start UP, 0 self-crossings, 677m | city-layout-probe (fold gate) + harness 30×2 | ✅ PASS |
| T27 | Item box 3D | Per-face shading (6-tone material array) + outline 1.06 — reads as a cube from the chase camera, not a placard | code + vision | ✅ PASS |
| T28 | Crash recovery | crashRecoverMs 500 (AI re-grips 0.5s after spin); harness injects real 1500-2100ms item hits; STUCK exempts post-hit recovery | harness 40×2 (long spins) | ✅ PASS |

## 3. Regression notes (this release)
- **2026-08-11 — "opponents run backwards" fix (16 commits)**: steering is
  progress-anchored (arc-length progress01 → centerline index), crash recovery
  never brakes (brake = reverse in this physics), the nearest-sample full-scan
  is heading-biased, the speed cap is hard (was leaking past 42 m/s), the
  navigation cache is built before the AI controllers, AI updates once per
  frame, and the rubber band now includes AI-vs-AI (no more City procession).
  Detector re-validation: re-introducing the old brake bug is DETECTED by the
  harness. See `RELEASE-NOTES.md` and the `game-aaa-audit-loop` skill
  (`references/sk3d-ai-backwards-fix.md`).
- Deterministic sim harnesses moved INTO the repo: `scripts/ai-backwards-test.mjs`,
  `scripts/lane-probe.mjs`, `scripts/procession-probe.mjs`, `scripts/sk3d-qa.cjs`
  (previously the agent's cache `sk3d-*.cjs`).
- `Kart.restart()` now uses the SAVED startPosition — restart actually resets (bug fixed).
- Item toast keys are lowercase (PowerUpType VALUES) — slot + toast icons finally match.
- Finish cruise mode replaces the engine screech (AI drives player, music swells).
- `?test` / `__freezeCam` QA hooks are stable; vision critic re-scores HUD 7.5/10, banner 8/10.
- v0.2.0: `raceManager.aiControllers` is the single source of truth (no duplicate
  array in main.js); `restart()` drops the player's cruise controller itself.
- v0.2.0: ramp launch anchors past the airborne threshold — the trick was silently
  dead before (unit test caught it); karts now climb + launch.

## 4. Known issues (accepted for v0.1.0)
- Software-GL headless is ~1-5 fps — QA requires `?test` (documented, by design).
- Minimap reads "radar-like" at a glance; route legibility is a v0.2 item.
- Speedometer shows 0 km/h in static captures (correct — kart parked in QA frames).
