# Super Kart 3D.js — Plano de melhorias F12–F17

Data: 2026-09-09  
Base: auditoria F11 com vídeo GPU + vision + Sol/xhigh  
Sessão Sol: `20260909_060136_d785de`  
Status release atual: **GO final; F12–F20 concluídos; regressão de route cue pós-finish corrigida e revalidada**

## Evidência F11

- Meadow desktop: 887 frames, `finished`.
- Meadow mobile: 937 frames, `finished`.
- Neon desktop: 675 frames, `finished`.
- Neon mobile: 850 frames, `finished`.
- Renderer: RADV PHOENIX; `pageErrors=[]` em 4/4.
- Vision: fluxo grid → race → results íntegro; `Turbo (You)` correto nos resultados; sem clipping maior confirmado.
- Build: 44 módulos, passou.
- AI: 20 seeds por pista, zero lost/backwards/crashes.
- Áudio lifecycle GPU: `9/9 PASS`.
- Frame pacing: Meadow20 p95 `12.9 ms`, máximo isolado `30.2 ms`; sem cauda persistente. Nenhum FPS foi inferido.

## F12 — Identidade do player + semântica HUD — P1 — CONCLUÍDA

### Resultado

- Chip de posição passou a exibir `YOU` separado do ordinal.
- Pílula amarela de alto contraste aplicada globalmente; texto mobile reforçado para `0.78rem`.
- `aria-label` passou a anunciar `Your position: ...`.
- Commits: `d63afa3`, `b74ec38`, `fcc7c1d`.
- Vídeos finais GPU: Meadow desktop/mobile `884/931`; Neon desktop/mobile `661/880`; todos `finished`, `pageErrors=0`.
- Vision nativa 4/4: `YOU` + ordinal legíveis e separados; sem overlap, clipping ou regressão.
- Áudio `9/9 PASS`; AI 20 seeds por pista sem lost/backwards/crashes; build verde.
- Sol F12 `20260909_104105_66c01e` (`gpt-5.6-sol`, `xhigh`): **PASS**.

### Risco residual

Cobertura limitada a quatro execuções GPU; não representa todos os dispositivos reais.


### Objetivo

Tornar inequívoco qual kart é do jogador e o que significam gauge, counters e estados de item.

### Escopo candidato

- marcador discreto `YOU`/chevron acima do kart;
- outline/underglow acessível e não dependente apenas de cor;
- labels ou estados explícitos para velocidade, boost, item e contador;
- consistência entre kart, HUD e results.

### Critérios de aceitação

- revisão cega reconhece o player em Meadow/Neon desktop/mobile sem explicação;
- gauge e counters são compreendidos pelo estado visual, sem legenda externa;
- player marker não cobre pista, kart, rivais ou HUD;
- vídeo temporal inclui grid, pack racing, boost/item e results;
- build, AI, pageErrors e áudio permanecem verdes.

## F13 — Stress mobile de input/safe-area — P1/P2 — CONCLUÍDA

### Resultado

- `TouchControls.resetInput()` agora limpa steer esquerdo/direito, drift, item e classes visuais após blur/visibility loss.
- Pause agora cancela corretamente `pointercancel`/`lostpointercapture` sem disparar pausa.
- Commit: `c8a126b`.
- Probes Meadow/Neon mobile DPR2: blur libera controles; pointercancel libera steer; pause não dispara; targets `64×64px`; margens laterais `20px` e inferiores `18–24px`; pageErrors zero.
- Vídeos humanos Meadow/Neon mobile: `599` frames cada, ambos `finished`, errors zero; vision temporal confirmou countdown → race → results, touch/HUD/safe-area sem overlap/clipping.
- Build 44 módulos, AI zero lost/backwards/crashes, áudio `9/9 PASS`.
- Sol F13 `20260909_105618_8f080c` (`gpt-5.6-sol`, `xhigh`): **PASS**.

### Risco residual

O probe sintético não demonstrou dois ponteiros simultâneos mantidos ao mesmo tempo; o fluxo de ponteiro único, cancelamento, blur e vídeos de interação passaram.


### Objetivo

Validar interação real sob multitouch, cancelamento, blur, bordas e safe-area extrema.

### Escopo candidato

- steer + drift simultâneo;
- steer + item/boost simultâneo;
- pointer cancel/up fora do botão;
- troca de foco/aba durante botão pressionado;
- DPR2/DPR3 com canvas efetivo registrado;
- aspect ratios portrait curtos e safe-area simulada.

### Critérios de aceitação

- zero controles presos após `pointerup`, cancel, blur ou mudança de fase;
- zero overlap crítico e targets primários ≥44 px;
- corrida completa nas duas pistas em mobile;
- vídeo demonstra input e resultado, não somente screenshot;
- nenhum ajuste reduz a prioridade visual de pista/kart.

## F14 — Antecipação de rota e landmarks — P1/P2 — CONCLUÍDA

### Resultado

- Cue dinâmico `TURN LEFT/RIGHT` baseado em tangentes da curva, limiar de `12°`, distância aproximada e `pointer-events:none`.
- Commit: `70dccb8`.
- Runtime: Meadow `TURN LEFT` em `14 m`; Neon `TURN RIGHT` em `21 m`; sem errors.
- GPU final: Meadow d/m `896/919`; Neon d/m `1117/846`; todos `finished`, `pageErrors=0`, RADV PHOENIX.
- Vision temporal 4/4: cue/road arrows legíveis, não obstruem HUD/touch/rota; sem regressão de kart/câmera/results.
- Build/AI/áudio verdes; Sol F14 `20260909_111817_fd3883` (`gpt-5.6-sol`, `xhigh`): **PASS**.

### Risco residual

Heurística de tangente pode oscilar em curvas compostas/S ou avisar tarde perto do limiar; `top:116px` deve ser revalidado se o HUD crescer. Frames não são FPS.


### Objetivo

Comunicar curvas, splits, rampas e landmarks antes da entrada, sem esconder gameplay.

### Escopo candidato

- minimap/track ribbon, se necessário;
- chevrons/placas de curva;
- sector/checkpoint landmarks;
- distinção visual entre pista, shoulder, item box e cenário;
- sinais específicos para boost, hazard e shortcut.

### Critérios de aceitação

- curva complexa é legível antes da entrada em ambas as pistas;
- direção não depende apenas de skyline/decoração;
- guidance não encobre kart, pista, HUD ou rivais;
- A/B GPU pareado comprova melhoria direcional em desktop/mobile;
- nenhum aumento especulativo de glow global.

## F15 — Landmarks por setor + ownership temporal de feedback — P2 — CONCLUÍDA / NO-CHANGE

### Resultado

- Auditoria confirmou landmarks funcionais: `START/FINISH`, placas direcionais, turbo pad, item box e Mushroom equipado.
- Drift meter já existe, mas não foi capturado ativo nesta rodada; F16 terá prova temporal dedicada.
- Skyline Neon é repetitivo, porém billboard/estrutura sem ownership de setor aumentaria risco de clutter e oclusão.
- Sol F15 `20260909_112349_f5e3b4` (`gpt-5.6-sol`, `xhigh`): **NO-CHANGE**, risco baixo.
- Nenhum patch de produto nesta fase; build/AI/áudio e ausência de regressão mantidos.

### Critério de aceite

Os quatro vídeos demonstraram landmarks legíveis sem clipping/regressão. FPS não foi medido nem inferido.

### Próximo passo

F17: criar harness manual determinístico de drift; reabrir landmarks apenas se uma auditoria por setor encontrar trecho sem referência dominante.


## F16 — Ownership temporal de drift, boost e item — P2 — CONCLUÍDA / NO-CHANGE

### Resultado

- Quatro vídeos controlados Meadow/Neon desktop/mobile chegaram a `finished`, `599` frames cada, errors zero.
- Vision não observou drift meter, sparks ou ready/release; runtime mostrou meter hidden sob `?demo` porque autopilot impede reprodução física determinística.
- O código já possui `HUD.setDriftCharge()` e ready cue; não há falha reproduzida para corrigir.
- Sol F16 `20260909_113529_c9f70a` (`gpt-5.6-sol`, `xhigh`): **NO-CHANGE**, risco médio.
- Nenhum patch de produto nesta fase; FPS não foi medido nem inferido.

### Risco residual

O comportamento real do drift permanece sem evidência visual; patch agora seria especulativo e poderia fabricar estado apenas para QA.

## F17 — Harness manual determinístico de drift — P1/P2 — CONCLUÍDA / PASS

### Resultado

- Harness versionado em `scripts/manual-drift-harness.cjs`, sem `?demo`/autopilot.
- Meadow/Neon desktop/mobile: `playerAI=false`, 23 ciclos, cerca de 900 frames por vídeo, `pageErrors=[]`.
- Meter visível temporalmente: Meadow mobile/desktop `70/74` amostras, máximo `41/44%`; Neon mobile/desktop `147/144`, máximo `88/86%`, classe ready em 4 amostras por cenário.
- DOM nativo Neon mobile: meter `104×15px`, `display:block`, `visibility:visible`, `opacity:1`; carga `7→16→25→34→43%` e ready `79%`.
- Vision não leu o meter nas pranchas por escala, mas o frame nativo/DOM/timeline refutaram falha funcional.
- Sol F17 `20260909_115333_9d09d0` (`gpt-5.6-sol`, `xhigh`): **PASS**, risco baixo.
- Nenhum patch de produto; o harness agora permite reproduzir o estado sem autopilot.

## F18 — Results, foco e microtexto — P2 — CONCLUÍDA / PASS

### Resultado

- Corrigido consumo global de `Tab` e `Space`: agora só ocorre em `RACE/COUNTDOWN`; results recupera navegação nativa.
- Corrigida regra visual `:focus-visible` para `.sk3d-finish-btn` e `.sk3d-menu-btn`.
- Harness `scripts/results-focus-harness.cjs` versionado em `a80245a`; DOM passou Meadow/Neon desktop/mobile: foco inicial `Race Again`, Tab→`Menu`, Shift+Tab→`Race Again`, Enter→`countdown`, `gotoMenu()`→`state=menu`, errors zero.
- Vision nativa Meadow mobile POST confirmou ring ciano distinto, `Turbo (You)`, safe-area e clipping PASS; demais combinações passaram DOM e captures results.
- Sol F18 `20260909_121338_625cdf` (`gpt-5.6-sol`, `xhigh`): **PASS**, risco baixo.
- Commits atômicos: `93bf042` input focus, `501b7fe` focus ring, `a80245a` harness.

## F19 — Grounding e composição — P2 — CONCLUÍDA / NO-CHANGE

### Resultado

- Probe relativo progress/path: Meadow max `0.303m`, p95 `0.233m`; Neon max `1.79–1.84m`, p95 `0.55–0.61m`, padrão localizado compatível com falso positivo de hairpin/progress stale.
- Vision GPU 4/4 não encontrou kart flutuando/embutido, sombra desconectada ou clipping de câmera; saltos/banking/respawn não foram visualmente exercitados.
- `KartPhysics` já usa groundY relativo, clamp e ramp lift; nenhum patch de produto seguro foi identificado.
- Sol F19 `20260909_122740_ffd5c9` (`gpt-5.6-sol`, `xhigh`): **NO-CHANGE**, risco médio-baixo.
- Auditoria final obrigatória: saltos/banking/respawn, finished/pageErrors, frame pacing/DPR/buffer, build/AI/áudio, Sol final e HEAD remoto.

## F20 — Regressão pós-release — CONCLUÍDA / PASS

### Resultado

- F20 descobriu route cue `TURN LEFT/RIGHT` que reaparecia em frames tardios de results.
- Causa: `showFinish()` escondia o cue, mas `_updateRouteCue()` o reexibia no loop seguinte.
- Correções atômicas: `58678dc` (hide no finish) e `29edca8` (guard enquanto finish ativo).
- Regressão revalidada em quatro vídeos GPU: Meadow d/m `1002/1002`, Neon d/m `899/1169`; todos `finished`, `pageErrors=[]`.
- Vision final 4/4 confirmou zero cue residual em results, identidade `YOU/Turbo (You)`, grounding, touch e safe-area sem regressão.
- Pacing final (frame-time p95/max): Meadow d/m `13.3/16.5ms`, `11.6/16.1ms`; Neon d/m `12.1/23.3ms`, `11.3/15.0ms`.
- Build 44, AI zero lost/backwards/crashes, áudio `9/9`, DPR efetivo `1`, buffers desktop `1280×720` e mobile `390×844`.
- Sol F20 `20260909_185139_3646fb` (`gpt-5.6-sol`, `xhigh`): **PASS**.
## F21 — auditoria adversarial pós-F20 — PASS

- Vision F21 inicial encontrou dois apontamentos úteis: results continuava animando e o display inicial podia mostrar `LAP 0/3`.
- Probe confirmou results não-terminal: em 2s Meadow desktop player mudou `~60m`, câmera `~56m`, elapsed `~2s`.
- Correção `f2ed57c`: `RaceManager` terminal, câmera/ambiente/vento/particles/skids congelados em `FINISHED`.
- Probe pós-fix Meadow/Neon desktop/mobile: `elapsed`, posição e câmera delta `0` em 2s.
- Probe DOM confirmou e correção `b9dda75`: `LAP 1/3` estável desde boot/countdown/GO; sem alterar contagem interna.
- Vídeos humanos GPU pós-fix Meadow d/m `916/1007`, Neon d/m `1171/1508`; 4/4 `finished`, errors0; vision 4/4 sem stale overlay, results frozen, identity/grounding/touch/safe-area PASS.
- Build 44, AI zero lost/backwards/crashes, áudio `9/9`, pageErrors0.
- Frame-time p95/max: Meadow d/m `13.9/29.6ms`, `12.1/16.3ms`; Neon d/m `12.9/26.5ms`, `11.1/15.1ms`; não reportar FPS.
- Sol F21 `20260909_212400_db0cae` (`gpt-5.6-sol`, `xhigh`): **PASS**, sem apontamento adicional reproduzível.
## F22 — auditoria de identidade, feedback e restart — PASS

- Vídeos humanos GPU Meadow/Neon desktop/mobile: `1001/1510/916/1108` frames, 4/4 `finished`, errors0; vision sem regressão concreta.
- Results `Race Again` → countdown/race e `Menu` → menu passaram em 4/4; foco e botões válidos.
- Vision observou identidade/HUD/grounding como gaps de observabilidade, não bugs reproduzíveis; results estático esperado.
- DOM pós-restart mantém elementos históricos ocultos, sem foco/atividade; Sol decidiu não patchar limpeza arquitetural.
- Build44, AI zero, áudio9/9, pageErrors0; frame-time p95/max Md14.0/30.2 Mm11.0/14.1 Nd11.7/15.1 Nm9.6/14.0ms.
- Sol `20260909_224635_6b636f` (`gpt-5.6-sol`, `xhigh`): **PASS**, sem issue de alta confiança. Próximo F23: assertion barata de hidden/inert/aria-hidden.

## F23 — assertion de acessibilidade e lifecycle — PASS

- `8faa5f8`: `gotoMenu()` agora define `raceManager.phase=idle` e limpa `raceOver`; evita estado lógico `menu + finished`.
- Assertion 4/4 desktop/mobile: results → Race Again chega a countdown/race; results → Menu chega a `state=menu`, `phase=idle`; HUD root oculto, route hidden, erros0.
- Vídeos humanos GPU pós-fix Meadow/Neon d/m `927/1002/1119/1506`, 4/4 finished/errors0; vision 4/4 sem overlay stale, freeze/lap/grounding/touch regressivo.
- Build44, AI zero, áudio9/9, pageErrors0; frame p95/max Md14.0/30.2 Mm11.0/14.1 Nd11.7/15.1 Nm9.6/14.0ms.
- Sol `20260909_232003_cc0c89` (`gpt-5.6-sol`, `xhigh`): **PASS**; tipografia mobile e identity observability ficam no backlog.

## F24 — legibilidade mobile e identidade — NO-CHANGE / PASS

- Probe nativo 4/4: lap `15.2px` mobile/`16.8px` desktop; touch targets `64×64px`; `aria-label` de posição presente e autoritativo.
- Vídeos humanos GPU Meadow/Neon d/m `996/1510/932/1099` frames, todos `finished`, errors0; vision4/4 não confirmou bug funcional.
- Identity observability e tipografia mobile foram observações de UX, sem threshold ou regressão reproduzível; grounding, touch, lap e results passaram.
- Build44, AI zero lost/backwards/crashes, áudio9/9, pageErrors0; frame p95/max Md14.0/30.2 Mm11.0/14.1 Nd11.7/15.1 Nm9.6/14.0ms.
- Sol `20260909_234955_9c3d53` (`gpt-5.6-sol`, `xhigh`): **PASS**; NO-CHANGE, backlog preservado.

- Sol `20260910_000044_71e2ac` (`gpt-5.6-sol`, `xhigh`): backlog ordenado em `docs/BLENDER-ASSET-BACKLOG.md`; P0 kart herói, rampas/boost e skyline Neon; P1 sinais/chevrons e landmarks Meadow; P2 gantry/item box; P3 guardrails/props. HUD/física/pós-processamento ficam fora do Blender.

## Revisão Sol do backlog Blender — 2026-09-10

- Sessão `20260910_002508_48b7e3` (`gpt-5.6-sol`, `xhigh`) manteve a ordem geral e definiu o vertical slice: 1 kart herói + 1 família de rampas + 3 silhuetas de torre Neon.
- Slice exige LODs, collider separado, GLB e A/B GPU desktop/mobile com câmera, iluminação e seed fixas.
- Budgets revisados: rampas `3k/1.2k/300`, torres `4k/1.2k/300`, landmarks `5k/1.5k/400`, item box `1.5k/400/100` tris.
- Gantry, item box e guardrails ficam fora do primeiro slice; collider nunca é derivado diretamente da malha visual.
- Budget deve controlar também materiais e draw calls; identidade depende de silhueta, grounding depende de sombra/pivô/escala/rodas.

## Primeiro asset Blender — Hero Kart v7

- Sol arte `20260910_004948_020606`: especificação de proporções, pivôs, 3 materiais, sockets FX, collider separado e LODs.
- Modelo criado em Blender 4.0.2: `SK3D_HeroKart_v7.blend`; GLB candidato `583,668 bytes`; `mesh_validate PASS`, zero n-gons/non-manifold.
- Vision interna revisou preview Eevee e vistas ortográficas; Sol `20260910_012628_acf31a` aprovou o blockout para integração.
- Estado: candidato Blender validado, ainda não promovido ao runtime. Próximo: feature flag, integração Three.js e A/B GPU Meadow/Neon desktop/mobile.

1. Uma fase por vez; não misturar fases no mesmo patch.
2. Antes de editar: probe que pode refutar o achado.
3. Correção aceita somente com vídeo GPU desktop/mobile e vision temporal.
4. Fases de diagnóstico podem terminar sem patch quando a hipótese for refutada.
5. Cada correção aceita recebe commit atômico e push imediato.
6. Após cada fase: build, AI, pageErrors, áudio quando aplicável, documentação, vault, wiki e memória.
7. Rivais cortados, curb/grid occlusion, contact shadows genéricas e foco não são bugs até reprodução isolada.
