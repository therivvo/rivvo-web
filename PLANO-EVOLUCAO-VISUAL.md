# Plano de Evolução Visual — Super Kart 3D.js

Plano de upgrade visual contínuo usando as skills `threejs-aaa-graphics-builder`,
`threejs-game-director`, `taste-design`, `shadcn-ui` e `game-design-*`.
Objetivo: levar de "MVP completo" → "Premium/Showcase" na Visual Scorecard
(`threejs-aaa-graphics-builder/references/visual-scorecard.md`).

## Status do ambiente de QA (blocker conhecido)

- **Vision provider**: intermitente (404/500/timeout) — não confiável para
  aprovação visual nesta sessão. Validação visual em GPU real fica a cargo do
  Feco (hardware real) ou quando o vision voltar.
- **Headless SwiftShader**: `requestAnimationFrame` throttled a ~1fps no
  Chromium headless com ANGLE/SwiftShader. Countdown de TEST mode (~1s real)
  leva ~30s em throttle. Capturas de corrida ativa exigem poll longo.
- **Build**: `SK3D_OUT_DIR=/tmp/sk3d-build npm run build` contorna o bug EPERM
  de cópia de `public/favicon.svg` → `dist/`.

## Ordem de execução (por dependência/senso)

| # | Item | Skill | Estado | Commit |
|---|------|-------|--------|--------|
| A | Baseline visual (screenshot desktop/mobile) | qa-release | ✅ capturado | — |
| B | D2 VFX (shield/near-miss/combo) | aaa-graphics | ✅ done | `cbdf703` |
| C | E1 HUD/menu/mobile | aaa-graphics | ✅ auditado (touch≥44px, safe-area) | — |
| D | C1 MaterialLibrary roles | aaa-graphics | ✅ done (MATERIAL_ROLES) | `f3e80a1` |
| E | B3 Render pipeline | aaa-graphics | ✅ auditado (PostFX/SceneManager) | — |
| F | D1 Pista/câmera | aaa-graphics | ⏳ pending | — |
| G | F1/F2/F3 regression + QA + vision | qa-release | ⏳ pending (vision down) | — |

## Visual Scorecard (baseline, estado menu — não active-play)

| Categoria | Score | Evidência (menu) |
|-----------|-------|-----------------|
| Art direction | 2 | tema neon/meadow coerente, paleta signal |
| Hero/player | 2 | kart authored (asa, vidro, motor) |
| Obstacles/enemies | 2 | cones, brake boards, item boxes |
| Rewards/interactables | 2 | coins, item boxes com bob/spin |
| World/environment | 2 | track + rails + terrain + props |
| Materials/textures | 2 | toon PBR, racing line, decals |
| Lighting/render | 2 | ACES + bloom gated + vignette |
| VFX/motion | 2 | partículas event-driven (boost/pickup/hit) + shield/near-miss/combo |
| UI/HUD | 2 | HUD genre-specific, touch targets |
| Performance | 2 | calls 363 / tris 573k / tex 36 / geo 175 (menu, low/SwiftShader) |

**Measured Evidence (inspector canvas, screenshot menu)**:
- Desktop: colorEntropy 3.01, edgeDensity 0.118, lumContrast 225.9, domColor 0.393
- Mobile: colorEntropy 4.68, edgeDensity 0.120, lumContrast 251.2, domColor 0.300
- Todos acima dos limiares de alerta da skill (entropia<3, edge<0.04, lum<60, dom>0.6).

## Blocker honesto

Sem GPU real + vision estável, o "Fresh-Eyes Review" e a confirmação visual
de active-play não podem ser fechados nesta sessão. O código segue a skill;
a aprovação visual final é delegada ao Feco em hardware real.

## Próximos passos (F)

- F1: auditar pista (TrackBuilder) por legibilidade de route + parallax.
- F2: câmera (follow distance, FOV, shake clamp) por track.
- F3: regression sim (ai-backwards) + QA browser (capture-active) em GPU real.
