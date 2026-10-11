# AAA-2 — Rodada 2026-08-22: famílias de silhueta nos karts

Continuação de `PREMIUM-PASS-2026-08-21.md`. Loop implementação → auditoria
com gates em `GATES.md` (rodada "AAA-2"). Sessão interrompida a pedido do
Feco (shutdown do servidor) após completar R1.

## Feito nesta sessão

### R0 — Baseline re-medido (corrida ativa)
- Novo runner `scripts/capture-active.cjs`: espera `state=race` via
  `skipCountdown()`, captura N frames espaçados por track + renderer.info.
- Descoberta de QA: `renderer.info` lê LIXO quando o render passa pelo
  EffectComposer (`calls=1, tris=1`) — diagnóstico de orçamento headless
  precisa de `__sk3d.renderReport()` ou leitura pré-composer. Fica p/ GPU real.
- Baseline visual (visão nativa sobre frames t1/t2 × f0-f3): karts IA
  recoloridos (mesma silhueta), asfalto liso à distância, mundo repetitivo —
  confirma os 3 gargalos declarados no premium pass anterior.

### R1 — Famílias de silhueta por personagem ✅ (commit `670e932`, pushed)
- `Kart._applyBodyClass(character)` muta FORMA, não só cor:
  - **Comet (speed)**: casco alongado/baixo (hull scale .94/.66/1.62), asa
    larga/rasa elevada a y .80, rodas traseiras gordas (root.scale.x=2 —
    escala NÃO-uniforme no root inteiro mantém pneu+aro+disco num frame só).
  - **King (heavy)**: casco alto/largo (1.12/.86/1.42), asa dupla (2º blade
    pintado com ângulo invertido), sidepods esféricos inflados, piloto ×1.12.
  - **Bolt/Pip (compact)**: casco curto (1.02/.84/1.28), asa estreita ALTA
    (y 1.04) com pylon esticado, lip duckbill no nariz, rodas ×0.9.
  - Turbo/Daisy: padrão (sem mutação).
- Zero pageerror em ?test/?demo, tracks 1 e 2.
- Validação visual (probe `scripts/probe-karts.cjs`, vista alta do grid):
  3+ silhuetas distintas no mesmo frame, sem peça atravessada/flutuante.

## Ferramental QA novo (reuso na próxima sessão)

| Script | Uso |
|---|---|
| `scripts/capture-active.cjs` | captura corrida ativa determinística (?demo → state race) + renderer.info; CAPTURE_OUT/CAPTURE_FRAMES |
| `scripts/probe-karts.cjs` | grid congelado p/ inspeção: `?test` + `window.__freezeCam=true` (hook real do main.js) + PROBE_VIEW=high |

Lição crítica de headless desta sessão:
- **Screenshot sob SwiftShader leva 30-90s** — timeout ≥150s obrigatório;
  qualquer coisa que mova os karts entre o clique e o PNG estraga o frame.
- **`?test` = controles vazios por frame** (main.js sobrescreve) → após o GO
  os karts ficam PARADOS no grid: o único jeito determinístico de fotografar
  o pack. `?demo` acelera antes do screenshot sair.
- **`__freezeCam` é flag booleana global** (`window.__freezeCam = true`),
  não override de `updateCamera` (que é chamado direto no módulo).
- Vista frontal do grid: câmera À FRENTE do pack (atrás tem grade de
  público); offset lateral ≤1.2m senão cai no gramado.

## Pendente (próxima sessão, nesta ordem)

1. **R2 — micro-detalhe asfalto/concreto**: normal map procedural para
   `roadTexture()`/`concreteTexture()` em Materials.js (onBeforeCompile +
   customProgramCacheKey; cookbook recipe).
2. **R3 — landmark por setor**: buildFieldLandmarks cobre longe (>60m);
   faltam peças PRÓXIMAS à pista, uma memorável por setor (Fase D).
3. **R4/R6 — fresh-eyes subagent** com imagens <100KB (lição runner-side:
   payload grande mata o filho) + scorecard medido antes/depois.
4. Validação GPU real pelo Feco (silhuetas, proporções das rodas).

Scorecard estimado (não medido): obstáculos ~1→~2; média ~2.15→~2.25.
Premium (≥2.3) requer R2+R3.
