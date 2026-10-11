# Game Design Document — Super Kart 3D.js

> Version 0.1.0 · Status: **in development** · Platform: Web (Three.js + Vite)
> Genre: arcade cartoon kart racer · Reference: Mario Kart / Sonic & All-Stars
> Racing / Crash Nitro Kart (inspired by, not copying).

## 1. Vision

A fast, juicy, **cartoon arcade kart racer** that runs anywhere a browser does.
One-liner: *"Mario-Kart-style power-up racing, 100% procedural — zero art or
audio assets, built with Three.js."* The game must feel **forgiving and fun**
(strong track guidance, rubber-band AI, generous item boxes), never punishing
or realistic.

## 2. Pillars (design goals)

1. **Juice over realism** — squash & stretch, drift sparks, GO confetti,
   bloom, camera shake, engine pitch. Every action should feel alive.
2. **Readability at speed** — road edges, kerbs, item boxes and HUD are
   readable in a glance; the player never stops to "figure out" the scene.
3. **Comeback-friendly** — position-aware item drops + rubber-band AI keep
   every race winnable until the last corner.
4. **Open-source clean** — 100% procedural assets, MIT, no secrets, docs in
   English, CI-published to GitHub Pages.

## 3. Player experience

- **Session**: menu (pick kart color) → 3-2-1-GO → 3 laps vs 5 AI → podium.
- **Lap target**: ~50-60s on a clean lap; ~1:30 full race; short enough to
  re-race immediately.
- **Skill curve**: hold W + steer is enough to finish; drift mini-boost +
  item timing is how you win.

## 4. Core mechanics

| Mechanic | Design | Implementation note |
|---|---|---|
| Steering | Arcade, forgiving | `steerSpeed 1.9 rad/s` + damp toward path tangent (0.45 on-road, 0.1 off-road) |
| Acceleration | 0→42 m/s in ~1.6 s | `acceleration 26` |
| Off-road | −55% max speed on grass | `offRoadMaxSpeedFactor 0.45` |
| Drift | Hold drift in a corner → charge → mini-boost on release | `driftChargeRate 1.0`, release boost ≥ 0.75 |
| Items | 6 power-ups, position-aware roll | see §6 |
| Collisions | Circle collision, push-apart + nudge | `_resolveKartCollisions` |

### 4.1 Drift (the skill mechanic)
Hold drift through a committed corner (`absErr > 0.55`, speed > 12). The kart
turns tighter (`driftSteer 3.6`) and charges a boost meter. Release with
charge ≥ 0.75 to exit with a mini-boost. **Pitfall**: braking is reverse —
never use brake to slow down in air/grass.

## 5. Track ("Sunset Loop")

- Closed Catmull-Rom loop, ~340 m, 11 control points, elevation 0→3 m.
- Road width 9 m + 1.7 m brown shoulders (off-road zone).
- Start grid: 2 rows × 3 karts behind the gantry.
- Landmarks: start gantry (waving checkered FINISH banner + start lights),
  forest, palms, grandstands, crowd blocks, mountains, balloons.
- **Item placement**: a side-by-side PAIR right before turn 1 (classic),
  then 10 singles alternating sides.
- **Turbo pads**: 2 clusters of 4 yellow chevron pads (t≈0.18 and t≈0.72) —
  touching one gives a 1.2 s speed burst.
- **Dressing**: painted checkered finish line on the asphalt under the gantry,
  white direction chevrons at the sharpest corners, yellow lane dashes,
  tire-stack barriers (3 high) on the outside of corners.
- **Flow**: gentle S out of the grid → elevation climb → sweeping left →
  downhill right → long right-hander into the finish straight. No flat
  sections longer than ~4 s.

## 5b. Characters

Six distinct racers (body/suit/helmet colors + stat spread):

| Name | Body | Stats (speed/accel/handling) |
|---|---|---|
| Turbo | red | 8 / 5 / 7 |
| Comet | blue | 9 / 4 / 5 |
| Bolt | yellow | 6 / 9 / 5 |
| Daisy | green | 5 / 6 / 9 |
| King | purple | 6 / 7 / 7 |
| Pip | orange | 5 / 8 / 7 |

## 6. Power-ups (position-aware rubber-band)

Roll table by placement (`position01` = 0 leader … 1 last):

| Item | Mid-pack | Leader (defensive) | Tail (comeback) |
|---|---|---|---|
| Mushroom (boost) | 30% | 14% | 26% |
| Green Shell (straight) | 22% | 30% | 14% |
| Red Shell (homing) | 18% | 28% | 10% |
| Banana (trap) | 15% | 20% | 12% |
| Star (invincible) | 8% | 5% | 22% |
| Lightning (shrink all) | 7% | 3% | 16% |

Rules: max 1 held item; boxes respawn in 6 s; pickup radius 2.8 m (swept
generously for 43 m/s × 0.05 s frames).

## 7. AI opponents

- 5 rivals, waypoint steering, look-ahead 6 m, rubber-band throttle
  (`rubberBandFactor 0.5` — speed up when behind, ease off when ahead).
- **Never brake** (brake = reverse in this physics); slow by easing throttle.
- Item usage ~0.5/s when holding an item.

## 8. Feel & audio

- **Visual juice**: squash & stretch on boost, drift sparks, GO burst
  (smoke + confetti), blob shadows, bloom + vignette, camera shake on hits.
- **Audio (100% procedural WebAudio)**: engine loop (saw + octave + combustion
  noise, pitch = speed), 19 synthesized SFX, 3 looping music tracks.
- **HUD**: rank medal chip, lap counter + progress bar, timer, circular
  **minimap** (track + kart dots), speedometer needle + digital readout,
  item slot with icon + name, countdown overlay, item toast.

## 9. Mobile

- Touch buttons (LEFT / RIGHT / ITEM, 86 px) via pointer capture (multi-touch).
- iOS: AudioContext resumes on first interaction; audio suspends when tab
  hidden (`visibilitychange`).
- Menu has a solid fallback (no `backdrop-filter` dependency) for WebView.

## 10. Quality gates (non-negotiable)

Apply `game-quality-gates` before any deploy: single cleanup entry point,
dt-based logic, timers follow lifecycle, dispose trio on scene switch,
audio lifecycle, input safety. See `docs/ARCHITECTURE.md` + `DESIGN.md` for
implementation contracts and the visual quality bar.

## 11. Roadmap

- v0.1.0 — core loop, 1 track, 6 karts, all items, AI, audio, mobile (current)
- v0.2.0 — 2nd track, item roulette spin, time trial, best-lap ghosts
- v0.3.0 — local 2P hot-seat, track editor (node-based), leaderboards (server)
