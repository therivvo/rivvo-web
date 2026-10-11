# Super Kart 3D.js — Design & Visual Direction

> The **AAA quality bar** this project holds itself to. The visual QA critic
> scores every capture against the categories below and rejects anything under
> ~9.5/10 per category. Reference standard: the classic arcade kart-racer
> trio — **Mario Kart** (8 Deluxe), **Sonic & All-Stars Racing** and
> **Crash Nitro Kart** — saturated, clean, juicy, but
> browser-renderable.

## Palette (cartoon, saturated, no mud)

- Sky: `#4cc9f0` → `#a8e6ff` horizon; sun glow warm
- Grass/terrain: `#7be36c` light, `#3faf4e` base, `#2f8f43` dark patches
- Road: `#5a6b7d` asphalt blue-grey, lane dashes `#ffd166`, edge stripes
  `#ff5a5f` / `#ffffff` (curb feel)
- Mountains background: `#9a8cff` → `#6b5ce8` (haze layered)
- Water: `#3ec6ff` with `#1e9bd6` depth, white foam edges
- Props: palm trunks `#b07a4f`, leaves `#2fa84f`; rocks `#a9a9b8`
- Karts: one per kart (`CONFIG.kart.playerColors`) with `#1b2a41` dark
  outline; driver skin warm, helmet matches kart

## Shading & materials

- **Toon**: `MeshToonMaterial` + gradient map (3-step) everywhere — no flat
  Phong look. Optional cheap rim via `onBeforeCompile` or a second
  BackSide-inverted hull with `#1b2a41` for cartoon outlines.
- **Outline**: crisp dark outlines on karts and props (inverted-hull scale
  1.03–1.06 or EdgeGeometry lines). Outlines are part of the cartoon identity
  — never skip them on hero objects.
- **Textures**: procedural canvas textures (road stripes, checkered start
  line, gradient sky, palm fronds). No external image assets.

## Lighting & atmosphere

- Warm directional sun (slightly warm `#fff2cc`), soft PCF shadows, ambient
  hemisphere fill (sky/ground bounce).
- Light fog to push background layers; mountains fade into haze.
- Bloom on emissive accents (boosts, stars, neon signs) — subtle, not blown.

## Camera & feel (juice)

- Chase camera with smoothing; slight FOV kick on boost (fov +6 with lerp
  back); screen shake on crashes and shell hits.
- Squash & stretch on kart body: stretch on accel/boost, squash on land/crash.
- Particles: drift smoke (white puffs), boost flame (orange→blue), item
  pickup sparkle, shell trail, star rainbow trail, finish confetti.
- HUD: rounded cartoon chips (Baloo 2 font), bold outlines, position pips,
  speedometer with needle, item slot card, countdown 3-2-1-GO with scale pop.

## World composition

- Closed loop track with elevation (small hills), 2-3 banked curves, tunnel
  or bridge accent, start/finish gantry with checkered banner.
- Props along the road: palms, rocks, fences, crowd flags, billboards with
  game logo. Distance layers: sky dome → mountains → trees → track.
- Animated: clouds drift, water shimmers, flags wave, crowd bounces.

## What "AAA" means here (QA rubric)

| Category | Bar |
|---|---|
| Lighting & mood | Cohesive, warm sun, no flat/black shadows, pleasant contrast |
| Materials & shading | Toon shading consistent, outlines crisp, no z-fighting |
| Composition & camera | Framed gameplay, readable action, no clipping through terrain |
| UI polish | Rounded, legible, consistent font, correct alignment, no raw browser default |
| Coherence | Palette harmony, one art style across all elements |
| Performance | 60fps on decent hardware; graceful on software GL (QA headless) |
