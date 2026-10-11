# Item Reference — Super Kart 3D.js

> Design reference for the power-up arsenal (the kart-racer equivalent of the
> gem reference in Match-3D.js). Each item is synthesized in `src/entities/PowerUp.js`
> and rendered as simple cartoon meshes — no external assets.
>
> The item set follows the arcade-kart-racer tradition made famous by
> **Mario Kart**, **Sonic & All-Stars Racing** and **Crash Nitro Kart**:
> a speed boost, straight and homing projectiles, a trap, an invincibility
> star and a shrink bolt.

## Item table

| Item | Emoji | Visual | Effect | Audio (`sfx.js`) |
|------|-------|--------|--------|------------------|
| Mushroom | 🍄 | Red cap with white spots, stem | Instant speed boost (`mushroomBoostMs`) | `boost` |
| Green Shell | 🐢 | Green rounded shell with spikes | Straight projectile that hits the first kart in its path | `shell` |
| Red Shell | 🐢 | Red shell with homing fins | Homing projectile targeting the nearest rival ahead | `redShell` |
| Banana | 🍌 | Yellow curved peel | Trap dropped behind; spin-out on contact | `useItem` / `crash` |
| Star | ⭐ | Golden star, emissive | Invincibility + boost + rainbow trail (`starDurationMs`) | `star` |
| Lightning | ⚡ | Yellow bolt | Shrinks all rival karts (`lightningScale`) for `lightningDurationMs` | `lightning` |

## Pickup weights

Rolled by `RaceManager.pickupItem()` (config in `src/entities/PowerUp.js`):

| Item | Weight |
|------|--------|
| Mushroom | 30% |
| Green Shell | 22% |
| Red Shell | 18% |
| Banana | 15% |
| Star | 8% |
| Lightning | 7% |

## Visual language

- All items use `MeshToonMaterial` + dark `#1b2a41` outline (consistent with karts).
- Emissive accents for readability on the road: star and lightning glow under bloom.
- Item boxes (`src/entities/ItemBox.js`) are glossy cubes with a `?` symbol, bob + spin
  (`itemBoxBobSpeed`), respawn after `itemBoxRespawnMs`.
- Projectiles live at most 8s; homing turn rate `shellHomingTurnRate`.

## Behavioural notes

- The player holds **one item** at a time (`maxHeldItems: 1`); picking a new box
  while holding does nothing until the held item is used.
- AI rivals use items offensively: homing shells target the player, lightning is
  used when close behind, star when trailing.
- `hitShell()` / `hitBanana()` trigger a spin-out (`crashRecoverMs`) plus camera
  shake (`addShake` in main.js).
