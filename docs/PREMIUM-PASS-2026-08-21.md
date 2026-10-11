# Relatório — Premium Pass Super Kart 3D.js (2026-08-21)

Sessão autônoma: skills threejs-* carregadas (director, aaa-graphics-builder
+ 5 referências, ui-designer + patterns, qa-release, debug-profiler,
gameplay-systems + game-feel + game-design), unlazy, game-visual-qa-kit.

## O que mudou (6 commits, todos pushed)

1. **7760a5a premium(sky)** — Domo do céu substituído por ShaderMaterial
   procedural (cookbook gradient-sky): gradiente 3-stop contínuo (sem
   banding nem a "faixa branca" da textura canvas), sol/lua com disc+halo
   físicos (pow), banda warm de sunset no horizonte dia, estrelas hash com
   twinkle na noite. O sol do céu usa a MESMA direção da key light — o que
   se vê é de onde a luz vem. 1 draw call, zero texturas (texs 87→86).

2. **9e033b4 premium(wind)** — applyWindSway() em Materials.js: injeção
   onBeforeCompile com fase POR INSTÂNCIA (instanceMatrix[3]) e base
   plantada. Grama da beira (0.10/1.6), meadow (0.12/1.4), palmeiras
   (0.05). updateWind(t) no loop principal. customProgramCacheKey único por
   (strength,speed) — pitfall do cookbook evitado. A/B congelado: 3.09% dos
   pixels animam.

3. **ae045f9 premium(kart+IBL)** — Rodas MK8: ombro arredondado GEOMÉTRICO
   (torus mesmo material do pneu nas 2 bordas — não é decal/anéis sidewall,
   lição R80 respeitada), 6 raios duplos em V, disco de freio ventilado no
   lado interno. IBL do dia reescrito p/ casar com o novo domo (horizonte
   #ffe3c2 warm) — clearcoat/chrome refletem o céu que se vê.

4. **06ca4a1 premium(grade)** — ColorGradeShader ganhou warmth 0.06:
   realce quente proporcional à luminância (só altas luzes; sombras
   preservadas). Gated GPU-only como o bloom (headless não vê).

5. **c3299dd premium(vfx)** — Speedlines simétricas nos DOIS lados do kart
   (antes só um lado alternado) + tom quente/densas durante boost = leitura
   de turbo MK8.

6. **59561f3 docs(GATES)** — ledger completo 9/9.

## Evidência medida

- Baseline → After (SwiftShader low, 960×540): calls 1478→1719 (+16%,
  shoulders/spokes/discs), tris 742k→795k (+7%, orçamento desktop ~800k ok),
  geometries 1074→1085, textures 87→86 (céu shader compensou).
- Zero pageerror em todos os probes (?demo track 1 e 2).
- Visão validou: gradiente smooth sem faixa, lua+estrelas+neon pop na noite,
  ombros arredondados legíveis no close.

## Scorecard (adversarial self-review — fallback documentado)

| Categoria | Antes* | Depois | Nota |
|---|---|---|---|
| Art direction | 2 | 2 | tema consistente; montanhas cinzas limitam |
| Hero/player | 2 | 2.5 | rodas autoradas; corpo ainda caixa+esferas de perto |
| Obstacles/karts IA | 1.5 | 1.5 | MESMO mesh recolorido — fraco conhecido |
| Rewards/interactables | 2 | 2 | item box beam + coins ok |
| World/environment | 1.5→2 | 2 | camadas + balloons + haze rings |
| Materials/textures | 1.5→2 | 2 | PBR+clearcoat+IBL+canvas procedural |
| Lighting/render | 2 | 2.5 | key/fill/rim/ACES + IBL casado + sol visível |
| VFX/motion | 2 | 2.5 | speedlines duplas hot, sway vivo |
| UI/HUD | 2.5 | 2.5 | MK8-like, minimap circular, speedo analógico |
| Performance evidence | 2 | 2 | medido antes/depois |

Média: ~1.8 → **~2.15**. Threshold premium (≥2.3) ainda não atingido —
gargalos declarados: karts IA sem variante de silhueta, sem normal maps,
landmarks esparsos por setor.

\* antes estimado do crítico baseline (sem scorecard formal prévio).

## Fresh-eyes review

Subagente independente foi despachado mas TRAVOU (vision_analyze retorna
payload ~500KB/imagem no transcript — 4 imagens estouraram o contexto).
Fallback adversarial aplicado (frases por categoria no log da sessão).
Pitfall registrado na skill threejs-aaa-graphics-builder para próximas
sessões: downscale <100KB + steer imediato, ou fallback direto.

## Pendências / riscos

- **GPU real obrigatório**: bloom, color grade warmth, e o brilho real dos
  materiais clearcoat NÃO aparecem no SwiftShader (gate software). O Feco
  precisa validar em GPU: céu/sol, reflexos das rodas, grade quente.
- Karts IA recoloridos = ✅ FEITO 2026-08-22 (famílias de silhueta, `docs/PREMIUM-PASS-2026-08-22.md`, commit 670e932).
- Normal maps procedurais asfalto/concreto (Fase B do plano R27) — PENDENTE.
- Landmark memorável por setor (Fase D) — PENDENTE.
