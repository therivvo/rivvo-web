# Super Kart 3D.js

> A cartoon arcade kart racer with **AAA-grade visuals**, power-ups and
> procedural audio — built on Three.js and playable right in the browser
> with **keyboard or touch**. Inspired by the genre's legends: **Mario Kart**,
> **Sonic & All-Stars Racing** and **Crash Nitro Kart**.

<p align="center">
  <a href="https://fecolinhares.github.io/super-kart-3djs/"><img src="https://img.shields.io/badge/play%20now-%23FFD166?style=for-the-badge&logo=githubpages&logoColor=white" alt="Play now"></a>
  <a href="https://github.com/fecolinhares/super-kart-3djs/actions"><img src="https://github.com/fecolinhares/super-kart-3djs/actions/workflows/deploy-pages.yml/badge.svg" alt="CI"></a>
  <a href="LICENSE"><img src="https://img.shields.io/github/license/fecolinhares/super-kart-3djs" alt="License"></a>
</p>

<p align="center">
  <img src="docs/screenshots/gameplay-desktop.png" alt="Desktop gameplay" width="640" />
  <img src="docs/screenshots/gameplay-mobile.png" alt="Mobile gameplay" width="200" />
</p>

## 🎮 Play online

**https://fecolinhares.github.io/super-kart-3djs/** — or run it locally (see [Running](#-running)).

## 🏁 What is this?

A fast, juicy **cartoon kart racer** in the spirit of the genre's legends —
**Mario Kart**, **Sonic & All-Stars Racing** and **Crash Nitro Kart**: drift
around banked curves, smash **item boxes** and use the power-up you get —
mushroom boost, homing shell, banana trap, invincibility star or the dreaded
lightning bolt — with **6 named characters** (Turbo, Comet, Bolt, Daisy, King,
Pip), **turbo pads**, a **live minimap** and AI rivals with rubber-band, to
fight your way from 6th to 1st across **3 laps**. 100% procedural — zero
external assets, MIT, built on Three.js.

Every visual layer targets a **AAA** bar: toon-shaded materials with rim
lighting, saturated palette, post-processing (bloom + color grade + vignette),
particles, squash & stretch, camera shake, procedural sky, animated clouds and
crowd. All audio — engine loops, SFX and the music playlist — is synthesized
in real time with the Web Audio API (zero asset files).

## 🕹️ How to Play

Beat **5 AI rivals** over **3 laps**. Drive through item boxes, then use what
you get. Drift through corners to charge a **mini-boost**.

| Action | Keyboard | Touch (mobile) |
|--------|----------|----------------|
| Steer | `←` / `→` or `A` / `D` | `◀` / `▶` buttons |
| Accelerate | `↑` / `W` | Auto-accelerate |
| Brake / reverse | `↓` / `S` | — |
| Drift | `Shift` + steer | `⟳` button while steering |
| Use item | `Space` | `🎁 ITEM` button |
| Pause | `P` or `Esc` | — |
| Restart | `R` | — |

> **Input isolation**: on desktop only keyboard works (no touch buttons); on
> mobile only the touch buttons control the kart. The modes never mix.

## ✨ Features

- **6 karts** with distinct colors, toon materials, animated driver, squash &
  stretch and drifting with mini-boost (Mario Kart style)
- **Full item arsenal**: 🍄 Mushroom (speed boost), 🐢 Green Shell (straight
  shot), 🐢 Red Shell (homing), 🍌 Banana (trap), ⭐ Star (invincible), ⚡
  Lightning (shrink rivals)
- **5 AI rivals** with progress-anchored navigation (never drives backwards —
  verified by a deterministic sim harness), AI-vs-AI rubber-banding, personal
  racing lanes and smart item usage
- **2 tracks** (menu switch or `?track=2`): **SUNNY MEADOW** — rolling hills,
  guard-rails, sponsor boards, field landmarks (pond, hilltop grove, windmill);
  **NEON CITY** — night circuit with a 48-tower skyline, lit windows, neon
  pink/cyan kerbs, concrete sidewalks and glowing street signs
- **Banked, elevated cartoon track** with procedural toon materials, animated
  clouds, water, palm trees, mountains and crowd
- **Post-processing** — bloom, saturation/contrast grade and vignette
- **Procedural audio** — engine pitch, drift, pickups, explosions and a
  dynamic lo-fi racing playlist (Web Audio, zero files)
- **Responsive** — desktop keyboard and mobile touch layouts
- **`?demo` mode** — cinematic autopilot camera used for screenshots/QA

## 🚀 Running

```bash
npm install
npm run dev        # http://localhost:3457
```

Production build:

```bash
npm run build      # outputs to dist/
npm run preview    # serve the production build
```

> `npm ci` requires a package-lock.json (committed).

## 🗂️ Docs

- [ARCHITECTURE.md](ARCHITECTURE.md) — module contracts, file layout, quality gates
- [DESIGN.md](DESIGN.md) — visual direction & AAA quality bar
- [GDD.md](docs/GDD.md) — game design document (vision, mechanics, track, items, balance)
- [ART-BIBLE.md](docs/ART-BIBLE.md) — visual identity: palette, materials, motion, HUD rules
- [ITEMS-REFERENCE.md](docs/reference/ITEMS-REFERENCE.md) — power-up reference
- [QA-TEST-PLAN.md](docs/QA-TEST-PLAN.md) — automated test matrix + regression notes
- [RELEASE-NOTES.md](docs/RELEASE-NOTES.md) — v0.1.0 release notes

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) and our [Code of Conduct](CODE_OF_CONDUCT.md).
Found a security issue? Read [SECURITY.md](SECURITY.md).

## 📄 License

[MIT](LICENSE) © 2026 Feco Linhares


## Testing

Deterministic headless sims (no browser/WebGL) in `scripts/`:

```bash
node scripts/ai-backwards-test.mjs <seeds> <track 1|2>   # AI backwards-driving stress + detection (0 events = pass)
node scripts/lane-probe.mjs <track> <lookahead> [variant] # lane adherence / wall-bounce A/B
node scripts/procession-probe.mjs                        # standings-change counter (AI-vs-AI rubber band)
node scripts/sk3d-qa.cjs                                  # headless Chromium smoke (?test, boot + page errors)
```
