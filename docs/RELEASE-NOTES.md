# Release Notes — Super Kart 3D.js

**feat(R29) — boot overlay com progresso (2026-08-17)**
- `src/ui/BootOverlay.js`: overlay de primeiro paint com logo "SUPER KART", barra de progresso, etapa descritiva (ARIA-live) e fade-out no boot.
- `main.js`: stages progressivos ao longo do boot (renderer→circuit→world→effects→race systems→HUD) + `complete()`; hook `?boothold=1` congela o overlay para QA visual e `release()` libera; listener de `error` global exibe "boot error — reload to retry".
- Verificação CDP em SwiftShader: card centralizado desktop 1280×800 e mobile 390×844, sem overflow horizontal; overlay some após boot (`cleared=true` em ambos).
- Nota: revisão visual pixel-level bloqueada — provedor de visão auxiliar (endpoint OpenAI-compatible) retornou resposta inválida; validação estrutural registrada.
- Pós-boot `?test&quality=low`: 906 calls, 992,339 triangles, 87 textures, 946 geometries (qualidade aplicada reduz chamadas vs 1450 baseline da fase anterior).

**fix(R28) — cap de texturas procedurais por quality profile (2026-08-17)**
- `Materials.canvasTexture()` agora respeita `window.__sk3dQualityProfile.textureCap`, mantendo mínimo 64px e passando o tamanho resolvido ao gerador procedural.
- O cap evita criar CanvasTextures de 1024/2048px em perfis low/medium; não altera física, IA ou gameplay.
- Verificação: build `/tmp/sk3d-r27-texturecap`; `?test&quality=low` sem pageerrors, report WebGL2/DPR1/640×400; métricas pós: 1450 calls, 1,093,677 triangles, 87 textures, 943 geometries. A contagem é baseline de runtime e será otimizada na fase LOD/instancing, não foi vendida como ganho.

**fix(R27) — perfil de qualidade e capability report (2026-08-17)**
- Adicionado `src/render/VisualQualityProfile.js`: perfis low/medium/high/ultra, detecção coarse/software/device capabilities, texture cap, DPR cap, pixel policy, shadow/bloom/color-grade gates e probes RGBA8/RGBA16F.
- `SceneManager` aplica uma única política ao DPR/sombras e expõe capability/quality report; `PostFX` usa o mesmo perfil; `window.__sk3d.renderReport()` disponibiliza calls, triangles, textures, geometries, renderer e drawing buffer.
- Verificação: build `/tmp/sk3d-phase-b2`; boot `?test` com 6 karts e zero pageerrors por 20 amostras.
- Medição `?test&quality=low` em SwiftShader 640×400: WebGL2 true, DPR 1, 1392 draw calls, 1,079,775 triangles, 87 textures, 945 geometries.


**docs(R26) — apêndice forense de física e corrida (2026-08-17)**
- Expandido `docs/PLANO-EVOLUCAO-VISUAL-BENCHMARK.md` com a extração estática de estados, checkpoints, substeps, suspensão, pneus, superfícies, drift/hop/boost, colisões, respawn, wrong-way e stats/AI.
- O plano agora separa evidência estática de gameplay vision/GPU real e define os limites de validação sem source map.
- A implementação proposta preserva a física/IA do Super Kart; importa apenas padrões comprovados de integração visual, feedback e render resilience.

**docs(R25) — plano de evolução visual por benchmark externo (2026-08-17)**
- Adicionado `docs/PLANO-EVOLUCAO-VISUAL-BENCHMARK.md` com diagnóstico, scorecard-alvo, arquitetura e fases P0/P1/P2 para elevar materiais, boot, render resilience, LOD/instancing, mundo, câmera, VFX, HUD/mobile e áudio.
- O plano preserva física, IA, colisões, itens e corrida atuais; não publica a identificação da referência externa.
- A análise visual final continua condicionada a capturas vision representativas e GPU real para framing, bloom e sombras.

**fix(R24) — boot de teste e auto-instancing render-safe (2026-08-17)**
- `?test`/`?demo` chamava `startRace()` antes da inicialização de `startRacePending`, causando `ReferenceError` e abortando o boot. Estado movido para antes do auto-start.
- `src/perf/instancing.js` agora inclui textura, alpha/normal maps, roughness, metalness, opacity, side, flatShading e vertexColors na chave. Antes, meshes com mesma cor/tipo mas materiais/texturas diferentes podiam ser mescladas e assumir o material do primeiro mesh.
- Verificação: build em `SK3D_OUT_DIR=/tmp/sk3d-audit-r24`; `ai-backwards-test` 0/8; lane-probe Meadow 0–1 e Neon 0–2 bounces; procession 749 mudanças de ordem/60s.

**tooling(R23) — captura SwiftShader genérica via CDP (2026-08-17)**
- Adicionado `game-visual-qa-kit/scripts/capture-active.cjs`: captura gameplay ativa genérica via `Page.captureScreenshot`, sem `page.screenshot()`; limpa localStorage, suporta desktop/mobile, chama hooks opcionais SK3D (`skipCountdown`, `autoAccel`) e espera movimento/progresso.
- Verificado: captura Neon desktop/mobile via CDP sem `pageerror`; o timeout de fonts/context foi eliminado. Limitação: SwiftShader ainda pode avançar o relógio do jogo muito lentamente; framing final deve ser confirmado no GPU real.

**fix(R22a) — hairpins Neon sem bounce de IA (2026-08-17)**
- `lane-probe` mostrou Neon com **32 bounces/kart em 90s** nos hairpins; Meadow já estava em 0–1.
- Causa: IA mantinha cruise de 100% mesmo com curvas compactas; throttle reduzido sozinho não baixava o envelope de velocidade.
- Fix: Neon agora limita `cruiseSpeed` a 88% em trecho normal e 78% quando o erro angular passa de 0.35 rad. Resultado: Neon kart0 bounces **32→0**, kart1 **31→0**, demais 1–2 no spawn/primeiro frame.

**fix(R21a-e) — auditoria cross-track compartilhada (2026-08-17)**
- Resize/orientação: `SceneManager` agora atualiza renderer e câmera em `window.resize`; PostFX já redimensionava apenas o composer.
- Touch multitouch: LEFT/RIGHT agora mantêm estados independentes; soltar um dedo não zera o outro.
- Road ribbon: o segundo vértice agora aplica `lat` também no eixo Z; elimina ribbons laterais enviesadas em curvas.
- Dashes: elevadas 5mm acima do asfalto para reduzir z-fighting em ângulo raso.
- HUD: speedlines limpam o canvas mesmo quando a velocidade cai abaixo do limiar.

**fix(R20a-c) — auditoria cruzada 2 pistas × desktop/mobile (2026-08-17)**
- IA: lane spread reduzido de ±1.2m para ±0.6m; `lane-probe` Meadow caiu de 9 bounces do kart0 para 0, evitando que rivais busquem o guardrail.
- Neon: letreiros eram rejeitados por `_onTrack(..., 6)` apesar de estarem no sidewalk; rejeição reduzida para 1.2m, liberando street signage fora do asfalto.
- Câmera: Neon ganhou +0.55m de distância de chase para revelar rota/rails sem alterar Meadow.
- R20b: AI Neon recebe steering adicional em curvas e throttle 0.72 durante erro alto; `KartPhysics` usa referência de progresso para colisão em hairpins, evitando selecionar segmento próximo errado e atravessar/ricochetear no rail.

**fix(R19a) — loop desktop/mobile sem bloqueio por `requestAnimationFrame` (2026-08-17)**
- O harness 2×pista/2×viewport mostrou que o carregamento podia permanecer em `Loading race…` e capturas Neon podiam expirar quando a construção aguardava `requestAnimationFrame` em SwiftShader/mobile.
- A construção incremental de karts agora cede ao event loop via `setTimeout(0)`, mantendo o browser responsivo mesmo quando o rAF é throttled. O fluxo de corrida não depende mais de rAF para avançar fases de inicialização.
- QA: sem `pageerror`; o harness ainda tem risco de timeout de screenshot em SwiftShader Neon, tratado como limitação do ambiente, não como aprovação visual.

**fix(R18a-d) — auditoria completa da pista Neon (2026-08-17)**
- Superfície: removidas as três faixas escuras, manchas radiais grandes e streaks fortes de `cityRoadTexture`; base única azul-carvão com reflexos neon pequenos.
- Racing line: desativada na Neon porque o overlay de largura total criava a divisão esquerda/direita; Meadow mantém a linha de desgaste.
- Edge seam: sombra de junção reduzida para 0.10 na Neon; guardrail prateado ganhou contraste/emissive sutil.
- Auditoria visual pós-correção: sem bolha translúcida ou costura forte; ficam riscos P1 de cenário boxy/câmera de chase em baixa velocidade para rodada própria.

**fix(R17a-b) — dashes retangulares + colisão com guardrail (2026-08-17)**
- Tracejado: o screenshot mostrou quadriláteros/paralelogramos irregulares. A combinação `lookAt()` + `rotateX()` estava orientando o plano duas vezes e a textura/grime adicionava bordas visuais estranhas. Agora os cards usam rotação Euler direta pelo tangente e cor sólida, sem textura de desgaste: retângulos consistentes nas duas pistas.
- Guardrail: o limite usava a posição antiga antes da integração e permitia atravessar um frame; além disso, calculava o rail em `roadWidth/2 + 1.05`, enquanto o visual está em `+0.45`, sem reservar o raio das rodas. Agora reamostra após mover, limita o centro do kart a `railCenter - 1.08m` e aplica bounce mais forte.
- Build: `npm run build` passou em `/tmp/sk3d-r17-trackfix-dist`.

**fix(R16g-h) — Neon + Start Race (2026-08-16)**
- Neon: o screenshot mostrou os lane dashes como retângulos escuros no asfalto molhado. A causa era material PBR/toon com borda marrom desgastada e iluminação da pista neon. O modo Neon agora usa textura limpa amarelo-clara + `MeshBasicMaterial` não iluminado; Meadow mantém o acabamento desgastado. Sem propriedade `emissive` ad-hoc: isso quebrava o shader Basic com `uniform.value` indefinido.
- Start Race: o pré-warm de shaders renderizava karts ocultos e gerava erro WebGL em alguns drivers; foi desativado. A limpeza antiga percorria/dispunha todos os meshes no clique; agora grupos antigos são removidos imediatamente e dispostos em baixa prioridade depois. A construção do jogador e de cada AI cede um frame (`requestAnimationFrame`) entre instâncias. O botão mostra `Loading race…` e bloqueia duplo clique.
- QA local: build Vite passou em `/tmp/sk3d-r16gh-dist`; captura Neon sem erro de página após o fix; o teste headless concluiu a construção da corrida e ocultou o menu.

### Round 13 (2026-08-16) — auditoria com câmeras de INSPEÇÃO + fix chevrons

Ferramenta melhorada (capture-inspect no kit): câmeras de perto nos alvos dos
bugs (roda, billboard, item box, asfalto, grandstand, pad) — o crítico agora
vê o que o GPU real mostra. Validações: wheel_rear 7/10, wheel_front 6/10
(sem anel), board_close 8/10 (textura limpa), itembox 7/10 (sem círculo
branco), asphalt uniforme, grandstand 7/10 (plateia OK).

**fix(R13c) `9f6ce34`**: turbo pad ribbon — chevrons INVISÍVEIS. A ribbon do
pad (R12i) aparecia lisa: o UV é `(t-uvBias)*repeatU` no sub-trecho t0..t1
(~0.0456) e o repeatU antigo (spanLen*0.055) mapeava só ~4.5% da textura —
os chevrons (fx 0.26/0.50/0.74) ficavam fora. Fix: repeatU = 1/(t1-t0) —
textura inteira (3 chevrons) por pad. Mesmo fix no glow. Validado: crítico
4→7/10 (chevrons visíveis, pad segue a pista).

**fix(R13d) `289b80c` + fix(R13e) `6e15d2b`**: 'anel nas rodas' = SOMBRA, não
peça 3D. O playtest-sim (corrigido: startRace→1500ms→skipCountdown→2500ms →
chase cam real) provou que o 'anel preto' do Feco é a SOMBRA PROJETADA do
kart no chão — elipse escura sob a roda com borda dura (lê como anel na chase
cam) + o blob (sombra de contato) com núcleo 0.45 lia como círculo preto
colado sob os karts AI no grid. Fixes: shadow radius 4.5→9 (penumbra suave);
blob núcleo 0.45→0.16 + raio 1.8 (o kart já tem castShadow real — blob era
redundante). Validado: playtest 5→6/10, 'sem anéis anormais'.

**fix(R13f-h) `49969f3`** — os 3 bugs PERSISTENTES, causa raiz final (GPU real):
1. **Item box círculo branco**: o ring era TorusGeometry(size×1.15) dourado
   com AdditiveBlending+toneMapped:false+opacity 0.95 — com bloom ESTOURA EM
   BRANCO PURO (círculo ~15% maior que o box). O flare R12f só expandia esse
   ring; o anel BASE era a causa. MK8 não tem torus no box → removido.
2. **Anel preto nos pneus**: tread ribs (3 torus) + groove (1 torus) = 4 anéis
   concêntricos escuros na lateral do pneu — liam como anel preto no GPU.
   MK8: borracha única uniforme → removidos (pneu liso + aro cromado).
3. **Asfalto mudando de cor seguindo o corredor**: borda do shadow map a 70m
   do kart (frustum ±70m) — a chase cam olha ~80-100m à frente, a borda (que
   se move com o kart) cruza a pista no frame. Frustum ±130m (borda fora do
   alcance) + sun a 150m (a 90m a luz caía dentro do quadrado).

**fix(R14a-b) `940ed86`** — os 2 que PERSISTIRAM após R13f-h (causas ocultas):
1. **Item box círculo branco**: era o BEAM, não o ring. Coluna de luz
   (CylinderGeometry) com AdditiveBlending+toneMapped:false+opacity 0.65. No
   headless SwiftShader o additive fica PRETO (o crítico nunca via); no GPU
   real com bloom ESTOURA EM BRANCO — vista da chase cam (de cima/trás) lê
   como círculo branco no chão com o box dentro. MK8 não tem coluna de luz →
   beam removido por completo (box+outline+sparkles).
2. **Asfalto mudando de cor**: as 3 PointLights do kart (rimLight azul
   4.2/9m, rimLightWarm laranja 2.4/8m, pilotFill creme 2.6/6m, decay 1.4)
   iluminavam o CHÃO com cores diferentes — como seguem o kart, o asfalto
   mudava de cor acompanhando o corredor. São rim light do kart, não luz de
   pista → alcance ~2m (só até o kart) + intensidade reduzida.

**LIÇÃO R14**: additive+toneMapped:false+bloom = estoura em BRANCO no GPU
real (invisível/preto no SwiftShader headless); point lights parented ao
player derramam cor no chão — limite o alcance ao objeto.

**fix(R15a-b) `4797f9c`** — mobile (screenshot do Feco):
1. **Asfalto azulado junto ao kart**: o vision no screenshot confirmou "faixa
   mais clara e azulada, formato alongado, sob e à esquerda do kart" = o
   rimLight azul (0x66e0ff) AINDA derramava no chão mesmo com alcance 2.2m
   (R14b). QUALQUER PointLight parented no kart ilumina o chão ao redor (não
   tem como excluir o chão) → **as 3 PointLights REMOVIDAS por completo**;
   rim light do piloto virou emissive (separação visual sem luz física).
2. **Beam menor**: o Feco pediu "o beam pode existir mas tem que ser MENOR
   que a item box" — recriado com raio máximo 0.55× o box (antes 1.05× =
   maior que o box), opacity 0.35, SEM toneMapped:false (lição R14). Brilho
   de chão contido.

**feat(R16) `ae11d92` + `6bbda58`** — Loop Director AAA
(threejs-aaa-graphics-builder, scorecard baseline 1.6/3; cat fracas: Lighting
1, Rewards 1, Materials 1, VFX 1):
- R16a: contrast lighting — hemi 0.35→0.22, rim 0.7→0.9, key sun 2.0→2.6.
  Crítico: luz 5→7/10.
- R16b: coins emissive 0.35→0.9 + halo sprite dourado (sem toneMapped:false).
- R16c: boost flame 0.34→0.42 + vel 9.5; drift smoke 0.3→0.38 + 2 puffs.
- R16d: hero emissive — carPaint 0.32→0.45, helmet 0.18/0.4→0.28/0.5 (pop
  sem PointLight que suje o asfalto).
NOTA scorecard headless: `?test` desliga bloom + color grade (config já tem
colorGradeSaturation 1.45 pronto p/ GPU real) e frames capturam speed 0 —
o GPU real do Feco é o árbitro final para re-scorar.

### Round 12 — AAA audit loop 3: 18 proposals (mecânica, densidade, imersão) (Jarvis, 2026-08-16)
Terceiro fan-out dirigido pelo crítico cego da R11 (kart 5.5 'modelagem simples',
meadow 6 'grama esparsa', Neon 7 'densidade urbana', 'interface reduz imersão').
3 commits atômicos + push (c274229 kart, 6bbb140 pista, 64833c5 hud):

**Kart/mecânica (6):**
- Suspensão exposta: wishbone do corpo ao cubo (esterça com a knuckle) +
  amortecedor metálico na traseira — roda deixa de flutuar.
- Bloco do motor com aletas + difusor carbon sob a cauda (metal usinado escuro).
- Grade texturizada nos side intakes (Materials.grilleTexture canvas 64px).
- Livery xadrez nas endplates + listras accent no blade (reusa bannerChecker).
- Cockpit com painel display (número + barra throttle) + botões no volante.
- Barbatana dorsal de carenagem + struts entre os blades da asa.

**Pista/densidade (6):**
- Meadow: grama densa (beira 4.5m/5 cones + novo buildMeadowGrassField varre
  4.5-22m ~1 tuft/1.6m + 16% capim alto seco, rnd local preserva _rand).
- Copas two-tone luz/sombra por camada (±14% lightness + hue/sat jitter) +
  pinheiro 24 segs.
- Neon: carros VIVOS (paleta taxi neon, 14→22, mais perto, faróis+lanternas
  emissivos + reflexo wet aditivo por carro).
- Street furniture: 14 hidrantes + 5 semáforos (3 discos acesos) + postes neon
  40→22m.
- 2ª camada de névoa BAIXA (buildGroundHaze: Meadow R100, Neon R72).
- Flores densas (patches 12→9m, 2-3 clusters, 4-7/cada).

**HUD/imersão (6):**
- AUTO-HIDE do HUD no touch: 4s sem input → ghost (placas 0.25, minimap 0.22,
  speedo 0.15, posição 0.55); qualquer toque/tecla restaura.
- Chips translúcidos 0.5 + compactos (lap bar 56px, position 58×44).
- Speedo ghost 112px: 0.5 repouso, acende 1.0 em boost/drift.
- Minimap menor (84/64px) COM zoom local 2.1× centrado no jogador.
- Cronômetro e rótulos ITEM/DRIFT somem no phone (MK8D).
- Touch buttons 0.55-0.6 + glow ring no toque (hit areas 44-56px intactos).

**Validação:** build ✓ · audit-geometry 0 CRIT ×2 tracks ✓ (whitelist de haze
rings adicionada ao kit) · crítico cego em andamento · deploy Pages verde.

### Round 11 — AAA audit loop 2: 18 proposals from 3 specialist auditors (Jarvis, 2026-08-16)
Segundo fan-out (kart/piloto · pista/ambiente · itens/HUD/FX) dirigido pelas notas
do crítico cego da Round 10 (kart 5/10, Neon 6/10, meadow 4/10). 18 propostas em
3 commits atômicos + push (07e06c6, 2aecddc, 1f329e9):

**Kart/piloto (6):**
- Asa traseira DESCE (1.02→0.84, blade 0.15) + piloto SOBE (capacete 0.185 em
  y1.38, ombros 1.02) — a capa plana do wing ocultava os ombros na chase cam;
  agora silhueta MK8 (capacete+ombros acima da aero). glowBar que estava
  oculto atrás da asa volta a aparecer.
- Sombra de contato com núcleo escuro 0.92 + penumbra curta (raio 1.0,
  opacity 0.18) — ancora o kart no asfalto.
- Pneus MUITO escuros (0x252b34) vs aro satin 0.9 + hubCap maior — roda lê
  com contraste e o giro aparece.
- Bitola larga (wx 0.765, flares acompanham) — traseira wide stance MK8.
- Paint envMap 3.2 + emissive 1.0 + outline na asa — silhueta definida.
- Placa de número maior (0.44×0.50 y0.66) + brake lamps 1.3 + flare 1.8.

**Pista/ambiente (6):**
- Poças neon MK8: elipsoidais (2.8×7.2m), núcleo quente 0.95 + streak
  especular da lâmpada + smear do poste, jitter determinístico.
- Asfalto MOLHADO na city: clearcoat 0.85 + sheen 0.55/0.15 + reflexo das
  janelas ADITIVO toneMapped=false — reflexos contínuos.
- Kerb vira PEDRA 3D (256×32: zebra no topo, pedra escura nas laterais).
- Flores no meadow (6 cores, ~1/2.5m, InstancedMesh) — fim da grama uniforme.
- Anel de nevoeiro atmosférico (haze banding em 3 planos, 26-30 placas).
- Skyline Neon vivo: bruma roxa 0x241f42 + janelas toneMapped=false.

**Itens/HUD/UI/FX (6):**
- Speedo REATIVO ao boost (dial dourado pulsa — MK8D).
- Floater +N de ganho de moeda.
- Shake no slot ao CONSUMIR item (uso sem feedback antes).
- Minimap mobile: dot do jogador 4→5.5 (a 72px sumia no traçado).
- ItemBox flare do anel no pickup (1→3.2× em 0.4s).
- Skid marks escalam com driftCharge + faíscas laranja no tier 3.

**Validação:** build ✓ · audit-geometry 0 CRIT ×2 tracks ✓ · crítico cego em
andamento (kart_chase/driver_close/meadow/neon) · deploy Pages verde.
Assets 100% procedural/WebAudio (TRIPO/GEMINI/ELEVENLABS = MISSING).

### Round 10 — AAA audit loop: 18 proposals from 3 specialist auditors (Jarvis, 2026-08-15)
Fan-out de 3 subagentes (kart / pista+ambiente / itens+HUD+UI+áudio) usando as
skills threejs-* (director, gameplay, aaa-graphics, ui, debug, qa-release) →
18 propostas com patches, aplicadas em 18 commits atômicos + push:

**Itens/HUD/UI/áudio (6):**
- HUD mobile: top row (lap+time+lapsplit | minimap+coins) estourava o viewport
  ≤480px — lapsplit oculto no phone, minimap 72px, coins compactos.
- Áudio: moeda tocava a FANFARRA de item box e o box tocava o blip de moeda —
  trocados (moeda=blip 0.55, box=fanfarra 0.6).
- Item box: beam dourado 50% mais fraco que o projetado (0.2-0.4, update
  sobrescrevia o construtor 0.65) → 0.4-0.7; pickup agora encolhe em ~0.18s
  (MK8D comprime no grab) + pop-in no respawn.
- UI state: slot reserva ganhou o pop (era mudo), swap com slots vazios agora
  treme o mini-slot (no-op visível), pause entra com fade+scale.
- Partículas: chama de boost encolhia (grow -0.25) → abre em leque (grow 1.2);
  fumaça de drift duplicada no centro do kart removida.
- Banana: orientação perpendicular ao tráfego (pontas de lado a lado, MK8) +
  sombra de contato que segue o hop.

**Kart/piloto (6):**
- Sombra de contato ancorada NO CHÃO — o blob era child do group e "cavalgava"
  no pulo/rampa (kart parecia flutuar); agora y local cancela a altitude e
  opacidade+tamanho somem com a altura.
- Chamas de boost SÓLIDAS nos escapamentos (2 cones aditivos com textura de
  gradiente) — turbo pad era invisível (zero feedback visual); partículas de
  boost também disparam no turbo pad.
- Capacete com clearcoat polido (era toon matte 0.82) + macacão com clearcoat
  leve; emissive suavizado (o highlight separa cabeça do corpo escuro).
- Speed lines em alta velocidade (>0.78× maxSpeed) — cue de vento MK8.
- Event juice: landing dust na aterrissagem de rampa, sparkle no rising edge
  do boost, sparks por tier de drift (branco→amarelo→laranja).
- Cockpit afundado NA carenagem — a banheira escura flutuava 0.13m acima do
  domo fechado (piloto "sentado em cima"); agora emerge do tub (silhueta MK8).

**Pista/ambiente (6):**
- Neon City: piscinas de luz neon NA PISTA MOLHADA (8 pools aditivos sob as
  lâmpadas — a luz dos postes nunca pousava no asfalto).
- Meadow: a floresta NUNCA projetava sombra (palmeiras sim) → castShadow em
  trunks/canopies/branches = dappled light no infield.
- Neon City: linhas de borda brancas sólidas (identidade de rua, não circuito).
- Neon City: 14 carros estacionados preenchem a faixa morta 9-16m entre
  calçada e torres (lia vazio urbano).
- Meadow: placas de freada 30/20/10 na borda externa das 3 curvas mais
  fechadas (cue de zona de freada MK8).
- Sombras de contato (fake-AO) para postes/banners/pneus/feno/placas/
  bandeiras — a mobília engineered ficava sem ancoragem na grama.

**Validação:** build ✓ · audit-geometry 0 CRIT (whitelist de itens coletáveis:
item boxes + coins ficam na pista por design) · deploy Pages automático.
Assets 100% procedural/WebAudio (TRIPO/GEMINI/ELEVENLABS = MISSING).

### Round 9 — Full QA loop: layout kinks, OOB rescue, countdown crash (Jarvis audit loop, 2026-08-11)
- **CRITICAL — Neon City centerline kinks <1m made karts fly off the map**: the '2'-layout's S-curves (straight→arc reversions, ~169° at vertices) put min-radius 0.1-0.5m on the racing line — SIM seed 2918 showed a kart driving away to z=-126 with progress frozen (0 laps, onRoad 63%). City rebuilt as 4-level circuit (top 50 / mid 26 / bottom 2 / lower -28) with true 90° circle arcs (R=8m, tangent-aligned, sampled on the circle) and no S-curves: **min radius ≥4.5m, kerb-edge folds 0, self-crossings 0, 614m**. SIM 16 seeds: 6/16 problem seeds → **0 lost karts, onRoad 100% all** (commit 6622be1).
- **CRITICAL — countdown rendered a giant "undefined" overlay**: the first rAF timestamp can predate the GameLoop's `performance.now()` in start() → negative dt → `countdownT += dt` ran the 3-2-1 counter at -0.5s → `COUNTDOWN_MARKS[negativeIdx]` = undefined. Fixed: dt clamped ≥0 + idx guard ≥0 (commit 60fd4e0).
- **Out-of-bounds Lakitu rescue**: a kart flung past the map edge (hard shove/boost at a corner) used to drive away forever — the <3 m/s stuck rescue never fired at 4.6 m/s. Any kart beyond |x|>95 / |z|>62 now gets rescued after 1s grace (commit 58e3aaf).
- **Harness upgrade**: new LOST-KART detector (off-road + progress frozen >0.5s, or out-of-bounds) — the 0-lap karts were invisible to the old stuck/backwards detectors; total accumulator fixed.
- **QA tooling**: motion-qa-runner `--cam-behind` (forces chase cam — SwiftShader's dt-based camera lerp takes minutes to catch the player, frames came out as blank sky) + first-render wait for f0; sk3d-qa.cjs speed-gate timing fix + 900s watchdog.
- **Regression suite**: mobile touch/menu PASS, items (shell/banana) PASS, smoke PASS, pause/resume PASS, toast PASS, restart/finish PASS (countdown "3").
- Verified: **PROBE 7/7 invariants both tracks** (0/78 wrong-way, 0/78 off-road per run), **SIM 32/32 seeds clean** (0 lost, 0 backwards, 0 stuck, onRoad 100%).

### Round 9g — pad lê como pintura no asfalto (Feco QA, 2026-08-12)
- O pad com o fundo #ffd94a + glow wash + setas brancas = blob branco
  "blown out" — o cérebro lê como objeto sólido/plataforma flutuante (e as
  setas somem). Agora: âmbar MÉDIO (#ffc233→#e87800) + glow das setas
  reduzido — as setas brancas CONTRASTAM e o pad lê como faixa PINTADA no
  asfalto (MK8). Validação vision: "wide flat amber strip painted onto the
  road... white arrows contrast clearly... functions as a road-surface pad".
- Pad alargado para 4.5m (largura de faixa) + moldura branca removida.

### Round 9f — pad colado na pista (Feco QA, 2026-08-12)
- Pad flutuava 3cm acima do asfalto (y+0.21 vs a ribbon em y+0.18) — a câmera
  chase lia como "voando". Agora o pad fica EXATAMENTE na superfície (y+0.18)
  e o lookAt mira o y da pista à frente (acompanha declives).
- 5 chevrons → 3 GRANDES (o MK8 usa 2-3 setas; 5 pequenas criavam a ilusão de
  "escada de setas" empilhadas na perspectiva).

### Round 9e — pad 18m (MK8 ribbon) + kart rear cleanup (Feco QA, 2026-08-12)
- Turbo pad ainda lia como QUADRADO: 11.2m de comprimento a 10m da câmera
  chase (4m de altura) comprime ~4m aparente = igual à largura. MK8 usa
  ribbons de 15-20m — pad agora 18m × 3.2m, textura 5.5:1 (512×92, 5 setas).
- Detecção de boost movida para a ENTRADA do pad (4 spots ~3m apart a partir
  do início) — o turbo dispara ao tocar o pad (MK8 feel).
- Kart: removidos os side-exhaust barrels cromados deitados na traseira —
  liam como "2 anéis cinzas girando na horizontal" (chrome + perspectiva +
  partículas). Traseira agora limpa (só os 2 exhausts escuros centrais).

### Round 9d2 — turbo pad MK8 look corrigido (Feco QA 2026-08-12)
- O pad lia como laje transversal marrom: o chain lookAt+rotateX(-90)+rotateZ(-90)
  INVERTE os eixos do plane (X vira profundidade) — geometria agora 11.2m
  (direção da pista) × 3.6m (largura), textura 3:1 (384×128) sem distorção.
- toneMapped=false no material base e no glow: o ACES tone mapping escurecia o
  âmbar para marrom; agora o pad brilha na saturação exata (MK8).
- Validado por captura headless (teleporte no pad): faixa longa âmbar brilhante,
  chevrons para frente, glow pulsante.

### Round 9d — MK8 turbo boost strips (Feco QA, 2026-08-12)
- Turbo pads viram FAIXAS longas (11.2m × 3.6m) no lugar dos quadrados 1.2×1.4:
  uma ribbon âmbar por cluster com 4 chevrons ">>>" brancos com glow, bordas
  brilhantes e textura 1:3 (sem distorção). Overlay aditivo que PULSA no loop
  (opacity 0.16-0.30, ~2.4s/ciclo) — o pad respira como o MK8.
- Física intacta: os 4 ts de detecção por cluster continuam os mesmos.
- Rampas ganharam decal próprio (turboPadChevronTexture — 3 chevrons num
  quadrado) para a textura comprida não espremer no plano da rampa.

### Round 9c — visual: zebra kerb gaps + turbo pad chevrons (Feco QA, 2026-08-12)
- **Zebra kerb buracos nas curvas**: stones retos num raio de 8m abriam gap
  triangular de ~1.6cm em cada junta (overlap era só 1cm) — parecia furo no
  zebrado. Agora segEff = 0.90 (overlap 5cm) fecha em todas as curvas; jitter
  lateral reduzida (desalinhamento quase invisível).
- **Marcações amarelas = TURBO PADS**: os chevrons estavam empilhados na
  vertical (cy 0.26/0.50/0.74) — lidos como zigue-zague/W pela câmera chase.
  Redesenhados lado a lado numa linha (padrão MK8 ">>>"), pontas +X (o
  rotateZ do buildTurboPads já aponta para a direção da pista; rampas seguem
  o mesmo padrão).

### Round 9b — CRITICAL: banana TDZ freeze (Feco bug report via GitHub Pages, 2026-08-11)
- **O jogo congelava segundos após a largada no GitHub Pages**: `ReferenceError:
  Cannot access 'm' before initialization` no `Banana.update` — o `const m = this.mesh`
  era declarado no FIM do update mas usado pelo bloco de arremesso (throw hop) acima.
  Toda banana arremessada (this._vY truthy) crashava o frame → o loop morria → freeze.
  Mesma classe de bug do Shell (fix r5) que nunca foi hoisted aqui. Corrigido (m hoisted).
- O error overlay (41a235a) revelou o erro real — o freeze passou de mistério a stack trace.
- Também: handler `webglcontextlost` (reload com ?nobl se não restaurar) + null-guard em
  playerKart.setControls (41a235a).

### Round 8 — City arcs + recovery tuning + item-box depth (audit loop, 2026-08-11)
- Neon City rebuilt from straights + true 90° circle arcs (R=14m): the flanged-vertex version had centerline radius dipping to 2.5m at apexes (CatmullRom concentrates curvature at sharp vertices) — smaller than the 4.65m kerb offset, so the INNER kerb edge self-intersected (stones crossed every lap). Now ≥12m everywhere; kerb-edge folds 0/0; city-layout-probe gains a permanent fold gate.
- crashRecoverMs 1200→500: AI re-grips 0.5s after a spin (MK8-like). Harness injects REAL item-hit spins (1500-2100ms, was 550-950ms) and the STUCK detector exempts post-hit recovery (no false positives).
- Item box: per-face shading (6-tone material array) + thicker outline — reads 3D from the chase camera.
- Audit sweep found + fixed the same ms-vs-s bug class in the race timeout (elapsed vs raceTimeoutMs fired after 83 HOURS — now 5 min).
- Verified: 0 backwards / 0 stuck / 0 crashes across every stress batch this session (600+ simulated races).

### Round 7 — Bots frozen fix + road cleanup (Feco QA, 2026-08-11)
- **CRITICAL — bots froze forever after any hit**: `crashUntil = now + crashRecoverMs` mixed SECONDS (raceManager.elapsed) with MILLISECONDS (1200) — the recovery window became ~1200 SECONDS (20 min), so after a spin/hit the AI released controls permanently and the kart stood still (throttle 0, steer 0). New harness STUCK detection (|speed|<1 for 2.5s) reproduced it: 320 stuck events / 80 seeds × 2 tracks → **0 after the fix** (`crashRecoverMs / 1000`). The previously-frozen kart's avgV rose 28.5 → 38.4.
- **Road cleanup**: painted 'sponsor' decals (read as smudged "MARIO KART" text on the racing line) removed entirely; kerbs slimmed 0.9×0.6×0.17 → 0.55×0.5×0.14 (thin MK8D zebra edge, still arc-length-spaced on the kerb edge).
- Final stress: **0 backwards events, 0 stuck / 100 seeds × 2 tracks**.

### Round 6 — Neon City redesign to the '2' layout (Feco reference, 2026-08-11)
- New CITY_PATH: start on the LEFT straight (x=-70) launching UP (+Z), clockwise — top straight, upper-right return, mid-upper straight, mid-left return, mid-lower straight, lower-right corner, bottom straight, 90° lower-left corner. Seam at t=0 mid-start-straight (colinear, no fold). 630m, 0 self-crossings, corners 4-8m radius (AI drifts them cleanly at 40+ m/s; harness 0 backwards events).
- Ramp ts moved off the corner (0.30 was inside the new top-right return!) to straights (0.20/0.57) + curvature-checked per track.
- Turbo cluster 0.72 (corner apex) -> 0.78 (bottom straight); item boxes off the corner apexes.
- City props (neon lights, billboards, cranes) now PATH-DRIVEN — two lamps had landed dead-center on the new asphalt, four in the void.
- `scripts/city-layout-probe.mjs`: reusable geometry gate for track designs.
- Kerb stones spaced on the KERB EDGE arc-length (inner corners no longer pile 0.6m stones 0.4m into each other); finish-line checker 12x2 (0.75m square cells, opacity 0.9).

### Round 5 — Visual/feedback pass (Feco screenshot QA, 2026-08-11, 9 commits)
- **Kerbs**: root cause of the "holes" was a lookAt pitch bug (every stone tilted ~11° nose-down); now yaw-only (verified 0.00° up-vector at matrix level). Proportions corrected to MK8D slabs (0.9 lat × 0.6 long × 0.17), saturated zebra palette with tight ±5% tint, jitter trimmed, and stones overlap 10% so curves and the start seam have no gaps.
- **Finish line**: checker cells were 1.25×0.8m (stretched); now 9×2.25m plane → square 1.125m cells, opacity 1.0.
- **Item box**: 256px texture, pure white panel with gold trim, vivid #ef233c '?' (was beige, blurred halo).
- **Crowd**: jump frequency 0.51 Hz → 2.0 Hz rectified pulse (grounded pause + gravity rise); per-part bob/phase sync so heads don't detach; organic per-figure phases; cheer amplitude 0.26.
- **Green shell**: PBR toon + outline, 24×16 segments, MK8 spike layout, 3 rev/s travel-axis spin, speed 46 → 84 m/s (~2× kart).
- **Banana**: 0.72m with outline + PBR sheen, 130ms pop-in + throw hop; MINIMAP now draws active items (yellow bananas, colored shells).
- **Lightning**: shrink on all 3 axes (was Y-only pancake) + electric screen flash/thunder/shake for the player.
- **Star**: kart body hue-cycles rainbow while active.

### Round 4 — AI reliability (Feco bug report, 2026-08-11, 16 commits)
- **"Adversários correm pra trás" ELIMINADO** — 3 root causes:
  1. Steering reference was a rolling distance window that lagged behind the
     kart after shoves/ramp launches/off-road excursions → the look-ahead
     target sat BEHIND the kart and the AI drove backwards. Now
     PROGRESS-ANCHORED: the target derives from the kart's arc-length
     `progress01` and can never sit behind race progress.
  2. Crash recovery BRAKED after a spin — in this physics brake = REVERSE, so
     karts reversed at -12 m/s for ~1.2s. Now controls are released (brake 0).
  3. The nearest-sample full-scan was distance-only — a 30m+ lateral offset on
     a curved loop picked the WRONG track segment (inverted tangent), corrupting
     progress01. Now heading-biased. (Bonus: the old fallback referenced an
     out-of-scope variable — a latent freeze, never exercised.)
- **Hard speed cap** — accel was out-running the over-target approach step, so
  speed crept past 42 m/s (sim: 86-113 m/s); rubber-band/coins were meaningless.
- **AI-vs-AI rubber band** — City order used to freeze into a procession
  (45 standings changes / 4500 frames); now 580 / 3600 (verified by
  `scripts/procession-probe.mjs`).
- **Lane offsets scaled to ±1.2m** (clamping collapsed two rivals onto one lane);
  look-ahead 6m → 10m (cleaner cornering, esp. Neon City); speed-stat spread
  restored for leaders; steer-assist progress-anchored; single AI update per frame.
- **Deterministic QA harnesses** added to `scripts/` (sim + lane + procession +
  browser smoke); sim: **0 backwards events / 80 seeds × 2 tracks**, detector
  re-validated against the original brake bug.
- Shipped as 16 atomic commits, main `747f42a` (previously `02d7fc8`).

### Round 3 — AAA polish loop (auditor-driven, 2026-08-09)
- **Round 16 — FECO critical pass (vs MK8D/Sonic Team Racing)**:
  - Crowd: paper billboards REPLACED by dense 3D spectators (instanced
    body + head + raised arms, 3 rows, grounded, bounce preserved).
  - Foliage: canopy segments up (pine 14), per-tree tone jitter ±8%,
    bushes as 2-3 sphere clusters, fake-AO base discs under trees.
  - Banners: gantry FINISH rebuilt as crisp 512px canvas, finish checker
    1024px, banner/flag textures 512px — no stretched look.
  - Audio: 8-bit beeps replaced by fat modern arcade SFX (noise sweeps,
    layered hits, filter sweeps, reverb + master compressor).
  - Rims: satin silver (no per-spoke mirror reflections).
- **Round 17-18 — Feco structural pass (3 critical vision agents)**:
  - Camera: MK8D chase (5.2m/2.6m/FOV 68) — the kart fills the frame;
    the gantry no longer dominates.
  - Color grade: saturation 1.45 / contrast 1.25 — ACES tone mapping was
    eating the grade (measured washed 87/255 + 21% dead-grey on the real
    GPU); the grade now fights ACES for the MK8 punch.
  - Gantry: banner 1.55m raised to y5.15, pillars 6.1m — reads as a
    finish structure, not a wall in the driver's face.
  - Terrain: broad hills ±5.0m — rolling field, not a carpet.
  - HUD: rank + item slots BOTTOM-LEFT (MK8D), unified card language.
  - Mountains: irregular ridgelines, broken snowlines, 3 value-contrast
    layers, distance haze.
  - Grid: wider spacing (row 4.6m / col 3.4m) — no more wheel-merge.
  - **Round 19 — fix-check regressions**: terrain scaled to ~±5m (was
    ±8.4m — ridge walls), off-road karts ride the rolling terrain
    (terrainHeight beyond the corridor), camera pullback 0.35→0.15
    (kart keeps the MK8D frame share at top speed).
  - **Round 20-21 — auditor MEDs**: terrain mesh matches physics (×0.7,
    no sink/float), camera 5.7m (no bottom crop), minimap darker bg,
    mountain mid-band haze reduced, gantry pillar flush (y3.05),
    5-lamp start countdown (MK8D), night skyline per-row haze.
  - **Round 22 — results screen**: the finish card now shows the FULL
    final standings (position + driver + time) from getStandings —
    MK8D's results screen. (Audit r21: 2 of 3 MEDs were false
    positives — the rocket start exists and no glider code is dead.)
- **Round 15 — audit r9 fixes**: third drift spark tier (purple @ 0.9),
  blue-shell splash (knocks karts near the leader), color-grade restored
  on real GPUs (software GL stays safe), high-speed wind streaks.
- **Round 14 — audit r8 fixes**: coin drop on hit (up to 3, respawned),
  blue-shell dodge counterplay (trick/item-box invincibility window),
  item roulette anticipation (0.45s shuffle), floating rank arrows
  (1-8) above every kart.
- **Round 13 — audit r7 fixes**: AI defensive rear-item play (chased AI
  drops/throws backward), shell motion trails, start-grid pole numbers,
  cloud shadows, sun lens flare, finished-kart wheelie + checkered flag,
  Lakitu toast wired, blue shell leader-only collision.
- **Round 12 — audit r6 fixes**: crowd figures get volume (2 crossed
  planes, terrain-grounded), 3D grass tufts in the infield, banner
  texture 512px, Lakitu clears the held item, AI rocket start at GO,
  blue shell re-targets the current leader each frame, AI uses its
  reserve item slot.
- **Round 10-11 — FECO review fixes**:
  - AI reverse bug: nearest-sample fallback could land on the opposite side
    of the loop (AI drove backwards) — now snaps to the progress point.
  - Crowd orientation: billboard figures now face the track with explicit
    roll-free yaw (no more upside-down/paper figures).
  - Finish line: 512px 8x2 crisp checker (was 256px 6x2 stretched).
  - Trackside banners: print only on the ±Z faces (side strips were
    distorted); chrome rims toned down.
  - Full-screen RACERS screen (character cards + stats + kart silhouette)
    and TRACKS screen (canvas-drawn track layout + START marker).
  - Premium karts: expressive driver face, gloves, wing endplates,
    exhausts, canards, brake calipers, accent hub caps, fake AO.
  - 3D instanced grass blades, gravel verge strip, bush tone variation.
- **Round 9 — convergence fixes**: blue-shell ARC TDZ crash (froze the race
  on every blue shell — fixed + live-tested), AI throttle clamp, turbo pads
  fire mid-boost, draft exit-kick player-only, boost ignores off-road
  slowdown, duplicate key light zeroed.
- **Blue shell ARC (r8)**: flies high with a ground-shadow warning, then
  dives on the leader — the MK8 doom cue, no more blue-painted red shell.
- **Off-track rescue (r8)**: 2s stuck off-road + slow → Lakitu respawn on
  the racing line with a hop.
- **Lap splits (r8)**: per-lap + best-lap chip under the timer, green
  flash on a new best.
- **Mow stripes (r8)**: deterministic terrain vertex-color bands — the
  field no longer reads as one flat green.
- **Backward item throw (r7)**: hold ITEM ~0.35s arms rear, release fires
  shells/bananas backward — the MK8D core skill; touch long-press.
- **Driver selection (r7)**: character cards with stat bars in the menu —
  roster speed/accel/handling now apply to the player, persisted.
- **Post-hit i-frames (r7)**: 2s invincibility after any hit + 2s spawn
  protection at GO — no chain-stun pinning.
- **Lighting contrast (r7)**: shadow sun is the sole key, hemi/fill cut —
  lit/shadow ratio >2:1; soft penumbra shadows (radius 4.5).
- **Mountain variety (r7)**: per-peak stretch → ridge walls, flat buttes,
  varied snow lines.
- **Castle texture (r7)**: stone-block + moss, red tile roofs, emissive
  windows, logo banner — the landmark reads at race distance.
- **Item depth (r6)**: second held-item slot + swap key; coin pickups
  (+1% maxSpeed each, cap +10%); triple item boxes (~1/6) with queued
  uses — the MK8 hold/swap + collect economy.
- **Castle landmark** in the Meadow infield (keep + 4 turrets + cone
  roofs + pennant) — the course's identity piece.
- **CC selector (50/100/150)** + auto-accelerate + steer-assist + player
  stats applied — difficulty/accessibility layer; speedo gauge rescales
  with the engine class.
- **Off-road exit kick** — held grass dives pay a recovery boost.
- **AI avoids hazards**, targets the rival ahead (standings), rocket
  start is a timing skill, menu music + music intensity arc, sponsor
  boards read clean (no more fake "checker corruption"), grass mow
  variation, prop contact shadows, deterministic world.
- **Black artifacts eliminated**: snow-cap faces with inverted windings got
  averaged normals pointing INWARD → weak-emissive faces rasterized black
  ('jagged black triangular patches on peaks' — every critic round). Ridged
  cones now use RADIAL normals (outward in XZ) + snow emissive lifted
  (0.35-0.42). Gantry diagonal cross-braces removed (the X across the
  racing line read as broken geometry).
- **Forest instancing fixed**: trees were piled at world origin (matrices
  written into dead meshes) — the visible blob is gone.
- **AI no longer trains**: lane offsets seeded from roster index (golden-ratio
  spread) instead of a zeroed position; leaders cap their speed at 1.0×.
- **Shadow camera follows the player** (±28m tight frustum, ~2.7cm texels)
  instead of one ±90m frustum over the loop (blurry blob shadows).
- **Asphalt specular**: racing-line overlay is now MeshPhysicalMaterial
  (clearcoat 0.35, envMapIntensity 1.1) — polished-rubber sheen, not flat
  matte; leftover MeshToonMaterial (water/pond/billboard) → PBR Standard.
- **Drift tiers + auto mini-turbo** (MK8D cadence): spark/beep at 0.33/0.66,
  full-charge auto-release after a grace window.
- **Kart contact physics**: lateral closing speed → spin-out + collision SFX +
  camera shake; positional snap clamped (no teleporting).
- **AI items target the nearest rival ahead** (not always the player).
- **Camera swing**: lateral offset ∝ steer while drifting, distance ∝ speed,
  kick on mini-boost.
- **Positional audio**: AI engine loops panned/spaced from the camera bearing;
  crowd ambience wash + cheer bursts; engine gear map with upshift drops;
  final-lap jingle + triangle fallback (no 8-bit leakage).
- **Pause UX**: Restart / Sound / Menu buttons in the pause overlay (touch
  players can leave mid-race); restart hygiene clears trick/draft state.

### Gameplay round-2 (auditor-driven)
- **Trick ramps now actually launch the kart** — unit test proved the launch
  never fired (the airborne threshold ate the vY the same frame). Karts now
  CLIMB the wedge (ground height interpolates the ramp slope) and launch off
  the top into a real ~0.4s arc — the mid-air trick + landing boost works.
- **Kart collisions are speed-aware**: rear-ender shoves the front kart less
  and pays a small speed penalty; finished karts are separated but never
  accelerated (were rammed like targets).
- **AI controllers unified** on `raceManager.aiControllers` (single source of
  truth) — kills the duplicate per-frame AI update and the cruise-controller
  leak at its root.
- **Restart hygiene**: `lastHeldItem`/`offroadT` reset so no stale item toast
  or gravel rumble bleeds into the new race.
- **Mobile UX**: touch buttons hide on pause (they blocked tap-to-resume) and
  when returning to the menu (they floated over the card).
- **Sky dome** 64×32 segments (24 faceted the horizon).

### Bug fixes (user-reported)
- **Restart regains player control**: the finish-cruise AIController attached
  to the player kart is now removed on restart (`Race Again` / `R`) — the AI
  no longer fights your steering after a reset ("the game was driving the car").
  Regression-tested by signature (`playerAIControlled` false→true→false).
- **Trick ramps flush with the road**: ramps are now wedges (bottom face flat
  on the asphalt, slope baked into the geometry) instead of boxes rotated
  around their center — the low end no longer sinks into the tarmac or floats.
- **Crowd off the racing line**: fixed the wrap-segment sampling bug that
  scattered the "start straight" spectators across the whole circuit (and into
  curves); rows pushed outside the guard-rail line; grandstands check all four
  corners against the track.

### Visual — MK8D bar
- **Track rebuild (authored MK8D circuit)**: racing-line wear overlay (wet
  polished rubber sheen over the asphalt), worn 4-tone beveled kerbs with
  per-stone jitter, armco guard rails (main rail + lower line + box posts +
  footing plates), painted-on markings with grime, 6 road sponsor decals on
  the straights, asphalt edge shadow lines, structural gantry with cross-
  braces.
- **Environment density**: ridged/vertex-jittered mountains (snow cap drapes
  the ridge — no more plain cones), 3D grass tufts along both verges, hay
  bales, sponsor boards on 3D frames, corner marshal flags, reflective water,
  sun glow billboard.
- **Post pipeline stability fix**: UnrealBloomPass AND SSAO rendered BLACK on
  software GL (SwiftShader/llvmpipe) once the scene moved to PBR — the
  composer now detects the software rasterizer (WEBGL_debug_renderer_info)
  and drops bloom there; hardware GPUs keep it. The custom ColorGradeShader
  was also removed (bloom→colorgrade→vignette chained passes broke software
  GL) — ACES tone mapping in OutputPass carries the grade. Contact grounding
  comes from the kart blob shadow + PCF shadow maps.
- **Kart rebuild (premium MK8D)**: 48-seg molded shell with side intakes,
  front splitter, fender flares + panel-line seams; wheels with tread ribs +
  sidewall stripes + 5-spoke chrome rims + hub caps; curved spoiler blade +
  splitter + endplates + pylon; driver with bent arms gripping a 3-spoke
  wheel (9-and-3), helmet visor, bucket seat + headrest; distinct PBR
  materials (clearcoat paint 2.2 / matte rubber / chrome metal / PBR glass).
- **Material pipeline rebuilt toon→PBR**: `toonMaterial()` now returns
  `MeshStandardMaterial` (continuous PBR shading, responds to the sunny-sky
  IBL) — the 3-band cel gradient that read as "low poly" is gone; hemi/key
  lifted for the PBR response, exposure 1.12, item boxes shrunk 2m→1.4m.
- **Karts rebuilt**: LatheGeometry molded shell (nose→body→tail lozenge)
  replaces the box chassis; cockpit tub + seat/headrest; shaped spoiler blade
  with struts + endplates; wheels with tread ribs, chrome disc rims + hub caps
  that roll with the tire; chrome metal for rims/exhaust; fine outlines on
  painted panels so clearcoat shows (envMapIntensity 2.0).
- **Track**: beveled/chamfered curb profile (rounded kerb stones, not flat
  tiles); guard rails with support posts every ~4m; trick ramp presence
  increased; asphalt reworked to 512px with dashed broken tire-wear ribbons
  (kills the horizontal banding) + racing-line rubber buildup.
- **Environment**: FOUR depth-banded mountain ranges with distinct hues,
  warm horizon haze rings, clouds in organized sky lanes (fog:false), two-layer
  water with shimmer, denser grandstand/crowd.
- **Post-processing**: composer now renders into a HalfFloat MSAA target
  (samples:4) — clean edges through bloom; bloom tamed (0.38/0.95) so whites
  don't blow out; brighter sunny-sky IBL with a hard sun core for defined
  clearcoat/chrome reflections.

### Audio — no more "8-bit"
- **Master chain**: EQ (hp28 + presence + high shelf) → soft tanh waveshaper →
  compressor, plus a procedural convolution reverb send (generated IR) so SFX
  and music share a believable space.
- **Engine loops**: sine sub-oscillator + per-voice saturation — real
  combustion body instead of a thin 2-osc synth buzz.
- **SFX**: raw squares replaced (hover/click/use-item/pos-change/countdown/
  mini-boost) with triangle/sine + chime bodies.
- **Music**: sidechain-style kick duck (~12% pump), kick click transient,
  snare body tone — the mix breathes.

---

## 🏁 Track 2: NEON CITY (menu track switch or `?track=2`)
- Tight urban circuit (649m — long straights + hairpins, same physics).
- Night theme: dark purple-blue sky + glowing moon, building skyline with
  lit windows (3 depth layers, 48+ towers), neon pink/cyan poles, dark asphalt
  with BAKED neon spill (cityRoadTexture), neon kerbs, metallic guard-rails
  with emissive top strip, concrete sidewalks, glowing street signs + shop
  signs on the close towers, night IBL so clearcoat/chrome reflect the city,
  and its own **Neon Nights** soundtrack (dark Dm sawtooth, 142bpm).

## AUDIT round — gameplay + visual + UX fixes (real findings, verified)
- **HIGH gameplay**: landing squash no longer taxes speed (lightning slow moved to a
  dedicated `_slowFactor` — every jump used to cut top speed 6-8% via the shared
  visual squash field).
- **HIGH ux**: pause "Sound" button no longer resumes the race (click bubble stopped).
- **Gameplay MED**: AI hazard dodge weakened (bananas land now), leading AI drops
  bananas in-lap (was lap-ahead only), AI coins+rubber capped at +12% total, off-road
  exit kick now audible (+dust), sub-threshold drift release no fake boost cue.
- **Visual MED**: night IBL reflects a moon (not a day sun), 4 neon lights added to the
  east/north arc (full circuit coverage), skyline footprint variation + roof antennas,
  first tower row pulled to 11m (no dead band).
- **UX MED**: mute unified + persisted, finish fanfare uses a temporary duck (no volume
  leak), touch controls hidden at FINISHED, help table lists Tab swap item.

## AUDIT v2+v3 — verification + polish
- **11/11 prior fixes verified by code signature** (gameplay 6/6, visual 5/5, UX 5/5).
- **NEW**: menu mute label reconciles with audio on show (no stale "Sound on" after
  pause-mute); reserve/swap slot 44→56px on touch (only swap path); swap tap always
  acknowledges (uiClick — empty-reserve swap was silent).
- **NEON CITY: 5.0 → 6.5/10** (vision STRICT CRITIC): night IBL moon killed the
  daylight cue on karts (8/10), 10 neon point lights give full-circuit colored light
  (8/10), skyline footprint variation reads less procedural (6.5/10).
- **Neon spill pass**: point lights 3.0/66m (bounce lands on karts/road), asphalt
  spill 9 radial patches at 0.5 alpha, night fog carries a purple hue — the "color
  never lands on geometry" gap.

## AUDIT v2b+v3 — verification + new fixes
- **Verified**: 11/11 v2 fixes by signature + 3/3 v3 MEDs + terrain sanity (±5m matches intent).
- **HIGH**: reserve/swap slot stays 56px on phones — a later `(max-width:768px)` query was
  re-declaring it at 36px (below the 48px min), silently reverting the touch fix.
- **MED game**: rubber-band cap no longer erases the difficulty-150 speed curve (cap now
  relative to base, which carries the AI statScale); neon light fixtures (visible lamp
  poles at every light — no more light from empty air); AI hits got a spark burst + thud
  (hits on rivals were invisible).
- **MED ux**: mute button plays uiClick (unmuting gave zero confirmation); dead
  `fogDensity` config removed.

## NEON CITY emissive pass — 7/10 peak
- Asphalt emissive 1.15 + emissiveMap (the baked neon patches GLOW across the
  surface — light alone lost it under the dim night key), city floor faint cool
  glow, cranes flank the start straight. Vision range 4.5-7/10 across frames
  (night identity 9/10, floor 8/10 on the best frame).

## AUDIT v5 — volume + feedback
- **Master volume slider** in the menu (persisted `sk3d.volume`, updates the unmute
  restore target) — audio was binary mute-only.
- **Verified**: AI-hit uses the real banana sfx (bananaBoing was dead code), unmute
  ack plays after the gain ramp.

## 🐛 User bug fixes (2026-08-10)
- **Kart sinks under the track at corners**: the kart body rode the path height
  (y=0) while the visible ribbon sits at y+0.18 — the body sank into the asphalt,
  and the MK8 banking pushed the outer wheel ~0.4m below the surface in corners.
  On-road groundY now rides the ribbon; off-road groundY is clamped 0.6m below
  the track so the rolling terrain can't swallow a corner-cut.
- **Menu/HUD bigger than the screen (mobile Chrome)**: the menu card had no
  height cap — 736px on a 640px viewport with the top (logo) cut off. Capped at
  `100dvh - 16px` with an internal scroll.
- **Pause button dead**: `.sk3d-touch-pause` had no `pointer-events:auto` — the
  touch container is `pointer-events:none` and this button isn't `.sk3d-touch-btn`,
  so taps never reached it. Reproduced headless, fixed, re-verified (tap → paused).

## 📱 RACERS/TRACKS screens cut on mobile — fixed
- The carousel strips showed the FIRST card at x=0 so the NEXT card poked in
  half-cut from the right edge; the JS center only ran on user clicks (and
  clamped to 0 for card 0). Strips now pad inline to center the first card.
- Track cards capped at 74vw (82vw poked 20px past a 360px screen).
- Screen cards use 100dvh (mobile Chrome toolbar makes 100vh overshoot).

## 🐛 Crash + wheel fixes (2026-08-10)
- **Freeze right after the start**: the off-road groundY clamp referenced a
  variable local to another function (`sp`) — the moment any kart left the
  track the step threw, killing the render loop. Fixed (near.groundY - 0.6).
- **Wheel sidewall rings**: the accent + wall-band torus rings (r 0.24/0.27)
  floated inside the r=0.34 tire — 8 small rings per kart read as stray
  artifacts. Moved to the tire-wall edge (r 0.30/0.32).

## 🔄 Wheel rings orientation — fixed
- All torus rings on the wheels (tread ribs, groove, sidewall stripe, wall
  band) spun SIDEWAYS: the default torus encircles the Z axis but the tire
  rolls on X. `rotation.x = PI/2` (in the wheel group) maps the ring onto the
  wheel face. Verified by world-matrix: all wheel-ring normals are ~X.

## 🔧 Chrome rim lip ring — fixed
- The chrome rim LIP ring (r=0.215) sat EDGE-ON: `rotation.z` spins a torus in
  its own plane. Under the `spin` group it needs `rotation.y = PI/2` (the
  wheel-face plane). Verified by world matrix — all wheel rings now ~X.

## 🌱 Track-edge sink — fixed
- Roadside terrain base -0.25 → -0.05 (the 0.43m step below the road read as
  karts diving into the earth at the edge; now a kerb-like ~0.23m step).
- Off-road physics sink clamp -0.6 → -0.3m.

## 🛡️ Guard rail + shoulder fixes
- **Karts pierced the guard rail** on wide sections: the physics wall used the
  LOCAL road width (up to 6.9m) while the rail sits at roadW/2+1.1 (5.6m) —
  clamped to just inside the rail.
- **Shoulder sink**: karts rode the terrain (-0.05) on the dirt shoulder (0.14)
  — they now ride the shoulder while on it.

## 🛡️ Guard rail — body-width fix
- The wall limited the kart CENTER to 5.4m but the 1.05m-wide body reached
  0.3m through the rail. The wall now pulls in by the body half-width.

## 🛡️ Guard rail — tire-width fix
- The outer WHEEL edge is 1.04m from center (axle + tire radius) — wider than
  the body. The wall pulls in 0.85m so the tire clears the rail (5.59 < 5.6)
  while the shoulder stays drivable.

## 🎨 5 visual fixes
- Wheel rim enlarged to fill the tire (the small gray ring at the rear).
- Item-box light beam ends AT the road (was piercing below ground).
- Kerbs: classic red/white zebra slabs (was 4-color 1.7m blocks).
- Spectators human-proportioned (was tall square blocks with small heads).
- Tree geometry quality bumped (pine 18 segs, oak 20x14, palm 10x8).

## 🧍 Crowd + kart polish (vision-guided)
- Spectators now have TWO LEGS + angled arms — they read as people, not
  colored blocks with heads.
- Kart exhaust barrels darkened (chrome read as floating white rings).

## 🧍 Crowd — human-read loop (multi-agent, 3 rounds)
- Spectators: smaller head (0.22) + neck + feet + per-figure contact shadow —
  they stand on the grass, not float.
- 4 pose variants (cheer/relax/wave/lean) + cloth-tone palette — a dressed
  crowd, not clones or candy blobs.
- Leg/grounding bug fixed (short figures no longer sink their feet).
- Grandstand crowd matches the roadside proportions.

## 🧍 Crowd — bounce bug + berm (multi-agent rounds 4-5)
- Critical: the crowd-bounce teleported LEGS into the torso every frame (they
  were invisible) — legs/neck/feet now bounce on their own baseline.
- Seated pose variant, per-pose bounce amplitude, clumped gap runs, and a
  raised berm strip — the crowd stands on a visible bank with feet planted.

## 🧍 Crowd — full agent pass (round 6)
- Positional jitter (no picket fence), family-clustered heights, striped
  shirts on 30% of the crowd. All multi-agent proposals applied.

## 🏁 Track 1: SUNNY MEADOW (default)
- Rolling-hill field with re-grounded landmarks (pond, hilltop grove, rock
  formation, windmill), sponsor boards, corner cones, flower/rock groups,
  guard-rails, 3-point lighting, layered mountains + 3 tree species.

- **6 named characters** with distinct suits/helmets/stats: Turbo, Comet, Bolt,
  Daisy, King, Pip. Driver stats are APPLIED: speed/accel/handling shape each
  AI rival's cruise speed, throttle eagerness and steering authority.
- **Full item arsenal** with position-aware rubber-band: Mushroom, Green Shell
  (follows the racing line — MK8 behavior), Red Shell (homing), Banana,
  Star (invincible + rainbow trail), Lightning (shrink + slow + electric burst),
  **Blue Shell** (Spiny-style: homes in on the race leader — the tail-ender's
  anti-leader pressure valve). Holding a shell/banana behind **blocks an
  incoming hit** (MK8 item-hold pillar).
- **Slipstream drafting**: ride in a rival's wake (~2.5m, +8% top speed) with
  wake streak particles + a pulsing DRAFT indicator; **leaving a wake grants
  a 600ms slingshot boost** (3s cooldown) — the core non-item comeback tool.
- **Rocket start**: hold throttle at GO for a 900ms launch boost — the
  MK8/CTR signature opening skill.
- **Trick ramps**: 2 launch ramps on straights (toon orange + painted chevrons);
  press throttle mid-air to arm a trick → landing mini-boost. Ramp launch and
  the arm window are tuned so the trick reliably fires.
- **Blue Shell** bypasses held-item blocking (only star/invincibility protects
  — MK8 spiny behavior), so the leader can't passively shield it.
- **Held-item bubbles** on every kart (colored orb + ring, spinning) — rivals'
  shields are readable; **brake lights** flare on braking/spin-out; lightning
  knocks held items away + a shock hop.
- **Drift mini-boost** charge-scaled (300–750ms by charge) with charge-colored
  sparks and a satisfying release SFX (`driftReleaseMiniBoost`, player + AI
  with stereo pan). Charge-scaled drama: bigger charge = louder pop + more
  sparks.
- **Turbo pads** (2 clusters × 4 chevrons) for speed bursts.
- **Track dressing**: painted checkered finish line on the asphalt, big
  direction chevrons at the sharpest corners, tire-stack barriers (3 high),
  yellow lane dashes, **corner warning signs** (pole + arrow panel),
  **100m/200m distance boards**, **roadside light poles on straights**,
  textured dirt shoulders.
- **AAA material pipeline**: karts use MeshPhysicalMaterial clearcoat (real
  painted-plastic reflections from a procedural sunny-sky IBL environment),
  chrome metalness exhausts, denser geometry (28-segment hood/tail, 24-seg
  tires, rear spoiler wing + struts, hood/rear specular highlights). 256px
  asphalt with cracks/grime, 256px grass with blade strokes, sky dome with
  painted sun + haze.
- **AAA world (redesign v1+v2)**: continuous low guard-rails along both road
  edges (below the chase camera, never obstructing), 3-point lighting rig
  (warm key + cool fill + shadow sun with PCF+radius soft shadows),
  2-layer mountains (rock base + snow caps) at 3 depth bands, forest with
  3 species of LAYERED canopy trees (pine/oak/palm), organized prop clusters
  (seeded deterministic placement — same world every load), grass with
  fine stipple patches (no flat green, no banding), kart contact shadows as
  soft radial-gradient ovals (no decal look), corner signs + distance boards
  + light poles on straights, **dense organized roadside** (sponsor boards on
  straights, flower patches + grass tufts along both rails, corner cone
  markers at apexes — all below the camera line).
- **MK8-style item boxes** (white panel, bold red '?', spinning + bobbing,
  golden ring + beam + sparkles), molded karts + oversized chibi driver,
  2.5D painted spectator crowd on 6 track segments + grandstands,
  hot-air balloons, wildflowers.
- **Gameplay feedback**: drift charge meter, speed-based camera FOV, skid
  marks, confetti at the line, **position-change chip pop + posUp/posDown
  SFX** (overtakes are audible), lap fanfare, item pickup fanfare, landing
  thump, drift tire screech, mini-boost sparkle bursts, **MK8 item roulette**
  (the slot cycles icons ~0.7s before revealing the pickup), **PLAYER HIT
  feedback** (red screen flash + "BANANA!/SHELL HIT!" label + camera shake),
  **item-use toast** (🍄 MUSHROOM! / 🐢 SHELL! etc) + spark bursts on use,
  **tire speed-dust + subtle exhaust puffs** (karts feel alive at speed).
- **Quality of life**: Pause (P/Esc or ⏸ button on mobile, tap-to-resume),
  "Race Again" + **"Menu"** buttons on the finish screen, touch **DRIFT
  button** (hold-to-drift on mobile), **kart color + mute state persisted**
  (localStorage, menu picker stays in sync), **audio mute toggle** on the
  menu, **rising countdown pitch** 3-2-1, UI hover sounds, one-time drift
  onboarding tip, drift meter flashes + beeps at the release point, AI drift
  sounds, mobile perf tier (pixelRatio cap on coarse pointers).
- **Live minimap**, lap progress bar, medal rank, polished speedometer + item slot.
- **5 AI rivals** with real rubber-band (cruiseSpeed override capped +12%,
  true top-speed comeback), per-driver stats (speed/accel/handling),
  per-driver lateral lane offsets (no train formation), corner-lift throttle,
  item usage, quiet panned drift screech.
- **Difficulty honesty**: overtakes never feel like cheats — rubber-band is
  capped and drivers hold personal racing lines.
- **Finish cruise mode**: after the line, AI drives the player at 60% while music swells.
- **Audio 100% procedural WebAudio**: engine loops (pitch = speed), 32+ SFX,
  3 music tracks, auto-pause on tab hidden.
- **Mobile**: touch controls (multi-touch, drift button), AudioContext resume
  on first gesture.

## QA
- Smoke, steering, item pickup, restart, pause, shell-hit — all automated ✅
- Vision critic (strict, vs MK8 bar): overall 7/10 polished arcade racer,
  gloss/clearcoat visible up close, kerbs/dashes/boxes/spectators 9/10.
- See `docs/QA-TEST-PLAN.md`.

## Known issues
- Minimap legibility (v0.2).
- Software-GL is slow — `?test` mode exists for QA.

## Roadmap
- v0.2.0 — 2nd track, item roulette spin, time trial + best-lap ghosts.
- v0.3.0 — local 2P hot-seat, track editor, leaderboards.

**feat(D) — wrong-way detection and turbo boost feedback (2026-08-17)
- Added wrong-way detection in KartPhysics.js: dot product between heading and track tangent, threshold -0.2, min speed 2.0, time needed 0.55s, cooldown 2.0s.
- Added kart._onWrongWay hook in main.js: plays audio, shows HUD message, adds screen shake.
- Added kart._onTurboBoost call in KartPhysics.js when turbo boost is activated.
- Added playerKart._onTurboBoost hook in main.js: plays audio, adds screen shake.
- Other feedback hooks (_onSwap, _onMiniBoost, _onDriftTier, _onLap, _onDraftExit, _onGrassExit) already stubbed in main.js.
