# Super Kart 3D.js — Art Bible

**Reference standard:** Mario Kart 8 Deluxe / Sonic & All-Stars / Crash Nitro Kart
(cartoon, saturated, readable-at-speed). 100% procedural — the "asset store" is code.

## 1. Palette (SUNSET LOOP theme)
| Role | Color | Hex |
|---|---|---|
| Sky top | deep blue | `#8ecae6` → horizon `#ffe8c9` (warm sunset) |
| Sun/glow | golden | `#ffd166` |
| Asphalt | warm dark gray | `#3d4250` |
| Shoulder/off-road | tan | `#c9a46b` |
| Grass | cartoon green | `#5fbf6a` / `#4fa35b` |
| Checker | near-black / white | `#1b2a41` / `#f4f6f8` |
| Accent (pads) | bright yellow | `#ffd166` |
| Accent (beams/teal) | cyan | `#2ec4ff` |

**Rule:** ≤3 saturated hues per frame; everything reads on dark chips (HUD `#1b2a41` 85% + white text).

## 2. Materials
- Toon-shaded (3-step gradient), dark inverted-hull outlines (cartoonOutline), rim highlight.
- MeshBasicMaterial ONLY for unlit decals (checker banner, turbo pads, distance marks).
- Blob shadows under all karts; soft shadow under environment props.

## 3. Shape language
- Karts: low, wide, chunky wheels (bigger than realistic), rounded chassis, spoiler.
- Drivers: chibi 1:1.5 head:body, big eyes, distinct suit/helmet per character (Turbo red, Comet cyan, Bolt yellow, Daisy green, King purple, Pip orange).
- Props: low-poly but smooth silhouettes; grandstands rounded; trees umbrella/ball.

## 4. Typography (UI)
- Rounded display font (Baloo 2 fallback system-rounded), 800 weight, white with dark outline/shadows.
- HUD chips: translucent dark `rgba(27,42,65,.85)`, 3px cream/white border, pill radius.
- Big numbers (countdown, speedo) ≥ 2rem; secondary labels 0.9-1rem.

## 5. Motion / juice rules
- Every action has feedback: boost → squash+stretch + flames; drift → colored sparks by charge; pickup → pop+sparkle+toast; hit → shake + knock; lightning → screen flash + scale.
- Camera: chase with lead-in; shake on impact; never cuts abruptly.
- Timing: action feedback within 100 ms; UI animations 0.2-0.35 s spring.

## 6. HUD hierarchy
1. **Minimap** (top-center) — track + kart dots, player ring.
2. **Rank + lap** (top-left) — medal for 1-3, lap progress bar.
3. **Timer** (top-right) — race clock.
4. **Speedo + item slot** (bottom-right) — needle + digital km/h, item icon+name.
5. **Toast** — item pickup, above item slot (never screen-center).
6. **Countdown** — giant number with ring pulse; GO burst confetti.

## 7. Audio identity (procedural)
- Engine: sawtooth+octave+combustion noise; pitch = speed; AI quieter (0.35×).
- Pickup: bright arpeggio (C6-E6-G6-C7) + pop; GO: horn + kick; victory: fanfare.
- Music: 3 loops (menu calm / race upbeat / victory) — synthesized, no samples.

## 8. Kill criteria (do NOT ship with)
- Unlit "draft" looking surfaces where toon should be; text illegible at 720p; HUD centered toast; off-key SFX; any frame >33 ms on mobile.
