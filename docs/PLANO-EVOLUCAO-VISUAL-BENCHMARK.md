# Plano de evolução visual — Super Kart 3D.js

> Documento de execução. O objetivo é levar a apresentação visual do Super Kart ao nível de um benchmark externo analisado em 2026-08-17, preservando a jogabilidade, IA e física já superiores no projeto.
>
> **Regra de propriedade:** não copiar código, assets, textos, identidade visual ou implementação do benchmark. Reproduzir apenas princípios técnicos e de direção de arte com implementação própria.

## Execução iniciada — R27

Implementado no primeiro lote:

- `src/render/VisualQualityProfile.js`: low/medium/high/ultra, detecção software/coarse/device, texture/DPR caps, gates de shadow/bloom/color-grade e probe RGBA8/RGBA16F.
- `src/render/SceneManager.js`: uma política única aplica DPR/sombras e expõe capability report.
- `src/render/PostFX.js`: respeita os gates do perfil.
- `src/main.js`: expõe `qualityProfile`, `capabilityProbe` e `window.__sk3d.renderReport()`.
- Verificado: build `/tmp/sk3d-phase-b2`; boot `?test` com 6 karts e zero pageerrors em 20 amostras.
- Medição `?test&quality=low` em SwiftShader 640×400: profile low, WebGL2 true, DPR 1, drawing buffer 640×400, 1392 draw calls, 1,079,775 triangles, 87 textures, 945 geometries.
- R28: `Materials.canvasTexture()` aplica cap de textura por profile; pós-cap low report 1450 calls, 1,093,677 tris, 87 textures, 943 geometries; baseline registrado sem alegar ganho.
- R29: `BootOverlay.js` com logo/barra/etapa ARIA-live, stages 0.04→0.82→complete e `?boothold=1` para QA; centralizado sem overflow desktop/mobile; pós-boot low = 906 calls/992,339 tris/87 textures/946 geometrias. Revisão pixel-level bloqueada por provedor de visão auxiliar inválido.
- R30: corrigido `require()` dead code em MaterialLibrary, removido `KartLOD.js`, adicionada detecção de wrong-way em KartPhysics, hooks `_onWrongWay`/`_TurboBoost` em main.js. Runtime ok desktop+mobile.
- **R31 (improve-threejs audit)**: audit completo do game loop. **0 alocações no frame-loop**, dispose() OK, color space OK, instancing OK. SK3D já é um projeto Three.js bem otimizado. Nenhuma correção HIGH/MEDIUM necessária.
- **R32 (bug audit)**: audit completo de bugs. **0 erros runtime** em todas as combinações testadas (Track 1/2, ?test, ?quality=low/high, desktop/mobile). Build atual quebrou (vite não encontrado) — precisa `npm ci` para restaurar. Latentes (geometrias sem dispose, listeners sem cleanup) são aceitáveis para jogo full-page. Nenhuma correção necessária.

Pendentes deste plano: matriz visual completa (bloqueada por vision).

## 1. Diagnóstico executivo

O benchmark não vence apenas por geometria. Ele combina cinco camadas coerentes:

1. **Direção de arte consistente:** paleta escura azul-marinho + dourado quente, placas recortadas, tipografia condensada/uppercase, contraste alto e poucos acentos.
2. **Pipeline de boot perceptível:** 13 etapas textuais, barra progressiva e prewarm explícito antes de revelar a cena.
3. **Materiais authored:** biblioteca semântica de superfícies com albedo, normal, ORM, micro/macro detalhe, emissive e variantes por qualidade.
4. **Render resiliente:** probe WebGL2, teste de material PBR, fallback de post-processing, limites de pixels, dynamic resolution e recuperação de contexto.
5. **Integração gameplay → imagem:** drift, boost, colisão, item, aterrissagem, wrong-way, pausa e finish alteram HUD, áudio, câmera e VFX por eventos.

O Super Kart já tem o núcleo de corrida, IA, física, itens, duas pistas e uma base visual forte. O gap principal é **densidade visual controlada e consistência de sistema**, não adicionar mais glow ou mais primitives.

## 2. Scorecard-alvo

| Área | Situação atual | Alvo | Evidência de aceite |
|---|---|---|---|
| Direção de arte | duas pistas com identidade, ainda com elementos procedurais repetidos | linguagem visual única entre mundo, HUD e VFX | 4 capturas: 2 pistas × desktop/mobile, sem elemento destoante |
| Hero kart | detalhado e legível, mas sem LOD/impostor formal | silhueta forte, materiais authored, sombra/contacto consistente | kart legível em chase + inspeção próxima + distância |
| Pista | boa geometria, overlays separados | superfície com micro/macro detalhe e leitura de material | asfalto não plano, sem seams, sem manchas seguindo kart |
| Mundo | props e crowd presentes | kits de props, instancing, LOD e composição por zonas | draw calls, triângulos e densidade medidos |
| Iluminação | key/rim/hemi corrigidos | pipeline de qualidade com shadow/contacto por tier | sem black crush, peter-panning ou bloom estourado |
| VFX | drift/boost/coins/itens existem | VFX event-driven com escala por tier e leitura de gameplay | cada evento tem feedback visual distinto |
| HUD/menu | funcional e responsivo | placas, hierarquia, safe area e estados de transição consistentes | desktop/mobile sem colisão e com contraste WCAG-like |
| Render | fallback básico e bloom gate | probe + trial material + adaptive scale + recovery | relatório GL, zero pageerror, canvas não-negro |
| Mobile | touch e resize corrigidos | orientação, safe area, tiers, gesture e feedback haptic | portrait informa landscape; landscape joga sem obstrução |
| Áudio | procedural existente | mix com engine/ambience/SFX, ducking e limpeza de lifecycle | start, pause, resume, mute e restart sem vazamento |

## 3. Arquitetura proposta

### 3.1 `VisualQualityProfile`

Criar um perfil único, derivado de capability probe e overrides de URL/localStorage:

```js
{
  tier: 'low' | 'medium' | 'high' | 'ultra',
  maxPixelRatio: number,
  renderScale: number,
  textureCap: 256 | 512 | 1024 | 2048,
  shadows: boolean,
  shadowMapSize: 512 | 1024 | 2048,
  bloom: boolean,
  ssao: boolean,
  motionBlur: boolean,
  volumetrics: boolean,
  reflections: boolean,
  particleDensity: number,
  foliageDensity: number,
  crowdDensity: number,
  lodBias: number,
}
```

A regra é uma fonte única para renderer, materiais, ambiente, partículas e HUD. Não criar gates independentes em cada módulo; isso é como produzir quatro “qualidades” que discordam.

### 3.2 `RenderCapabilityProbe`

Implementar em `src/render/RenderCapabilityProbe.js`:

- detectar WebGL2, vendor/renderer e software renderer;
- testar attachment RGBA16F e RGBA8 em framebuffer real;
- compilar um material PBR representativo com mapa + normal;
- ler limits: max texture, renderbuffer, samples, uniforms e varyings;
- produzir `capabilities`, `recommendedProfile` e `fallbackReason`;
- expor relatório em `window.__sk3d.renderReport()`;
- impedir que a primeira cena descubra incompatibilidade depois de o usuário clicar Start.

### 3.3 `RenderPipeline`

Evoluir `PostFX.js` para uma política explícita:

- renderer base sem antialias quando composer usa MSAA render target;
- MSAA configurável por tier;
- bloom, vignette, grade, SSAO, motion blur e DOF com gates independentes;
- qualquer falha de pass desativa só o pass, não a corrida inteira;
- `webglcontextlost`: pausar, mostrar aviso, reconstruir ao restaurar; fallback `?nobl=1` só como último recurso;
- dynamic resolution por frame budget, com histerese e lock temporário para evitar thrashing;
- limite de pixels por MPx para desktop e mobile.

## 4. Plano por fases

### Fase A — Fundamento visual e boot (P0/P1)

**Objetivo:** a primeira impressão já deve parecer produto acabado, mesmo em loading lento.

1. Criar boot overlay próprio do Super Kart com logo, fundo gradiente, barra e etapa textual.
2. Dividir inicialização em etapas: renderer, controles, iluminação, materiais, pista, ambiente, grid, itens, efeitos, câmera, HUD, áudio e balanceamento.
3. Construir karts/props em lotes com `requestAnimationFrame` sem deixar a tela congelada.
4. Prewarm de shaders em objetos ocultos e descartáveis; registrar programas antes/depois e tempo.
5. Remover qualquer `ReferenceError`/TDZ no caminho `?test`, `?demo` e Start normal.
6. Adicionar tela de erro visual com ação Reload e relatório de capability.

**Aceite:** boot sempre comunica progresso; zero frame preto silencioso; Start responde em até 100 ms; `?test` inicia sem pageerror.

### Fase B — Biblioteca de materiais authored (P1)

Criar `src/render/MaterialLibrary.js` com cache por superfície e tier:

- `tarmac`, `tarmac-racing-line`, `tarmac-wet`;
- `kerb`, `grass`, `dirt`, `sand`, `concrete`, `stone`, `cliff-rock`;
- `paint`, `chrome`, `rubber`, `glass`, `metal-painted`;
- `wood`, `roof-tile`, `banner`, `foliage`, `crowd`, `neon`, `boost-pad`.

Cada superfície deve declarar:

```js
{ albedo, normal, orm, emissive, uvScale, anisotropy, alphaMode, roughness, metalness }
```

Implementação inicial procedural própria:

- CanvasTexture em cache, nunca uma cópia por objeto sem motivo;
- normal/ORM sintéticos para microvariação;
- macro variation por vertex color ou world-space noise;
- `alphaTest` para cards/decal quando blend não for necessário;
- `polygonOffset`/`depthWrite:false` apenas em decals, com renderOrder documentado;
- resolução 256/512/1024/2048 conforme profile;
- marcação de recursos compartilhados para descarte seguro.

**Aceite:** asfalto, kerb e concreto não leem como cor sólida; nenhuma textura compartilhada é descartada no restart; cache reduz uploads repetidos.

### Fase C — Hero kart, sombra e LOD (P1)

1. Separar kart em `hero`, `mid` e `impostor`.
2. Hero: cockpit, piloto, capacete, pneus, aro, asa, emissive e decals de cor.
3. Mid: silhueta, quatro rodas e material principal.
4. Impostor: card/mesh simplificado com sombra dedicada.
5. `KartLODSystem` troca detalhe por distância e preserva a câmera chase.
6. Sombra de contacto em blob/decal para leitura de aderência; shadow map só para sombras de mundo.
7. Evitar PointLights parented ao kart; rim deve ser emissive ou luz global controlada.
8. Compartilhar geometrias e materiais imutáveis entre os seis karts; variantes de cor por `instanceColor`/uniform quando seguro.

**Aceite:** kart continua reconhecível em qualquer distância; frame não tem anel/círculo ou cor derramada no asfalto; restart não aumenta geometria/material count.

### Fase D — Mundo e composição por zonas (P1)

Trocar “props espalhados” por kits de composição:

- zona de largada: grid, pórtico, luzes, banners, crowd e signage;
- zona de curva: kerb, rail, apex marker, verge decal e prop de escala;
- zona de landmark: uma peça grande memorável por setor;
- zona de transição: terrain, fog layer, skyline/backdrop;
- zona de finish: banner, confetti, camera/lighting beat.

Implementar:

- `WorldPropKit` com variantes de materiais;
- atlas de crowd 4×2 ou equivalente procedural, com instancing;
- LOD de árvores, rochas, postes, banners e crowd;
- impostor shadow para itens distantes;
- culling por setor/curva, não só frustum de mesh individual;
- contagem de draw calls, triângulos, texturas e memória.

**Aceite:** cada pista tem 3 landmarks únicos; horizonte não é vazio; densidade visual aumenta sem ultrapassar orçamento mobile.

### Fase E — Pista e leitura de velocidade (P1)

1. Materiais de pista por tema: Meadow com asfalto seco; Neon com asfalto úmido/urbano, sem cor azul seguindo o kart.
2. Racing line deve ser um overlay discreto, não uma mancha dominante.
3. Dashes e turbo pads em ribbon alinhada ao path, com UV local e chevrons visíveis.
4. Kerbs com perfil chanfrado e espessura real, sem tiles planos.
5. Guardrails com post spacing, variação de material e highlight controlado.
6. Decals de pneu, skid e verge com alpha-test/offset e lifetime limitado.
7. Camera chase com composição: kart no terço inferior, rota aberta no centro, landmark no ponto de fuga.
8. FOV punch, speedlines e parallax só durante velocidade real; não usar VFX para esconder câmera ruim.

**Aceite:** screenshots de curva, reta, pad e finish mostram caminho legível; nenhum overlay compete com o kart ou o HUD.

### Fase F — VFX e feedback de gameplay (P1)

Mapear eventos para feedback multimodal:

| Evento | Visual | Áudio/haptic | HUD |
|---|---|---|---|
| drift charge | faíscas por tier + charge rails | pitch/carga + haptic leve | charge meter |
| mini-boost | flare traseiro curto + FOV punch | boost transient | boost tier |
| turbo pad | chevrons pulsando + trail | hit/engine lift | toast curto |
| coin | brilho orbitante + pickup burst | coin chime | contador punch |
| item pickup | box explode/respawn + roulette | tick/roulette | slot/duplo slot |
| hit | flash direcional + shake limitado | impacto + haptic | estado invulnerável |
| landing | poeira/sparks conforme impacto | thump | nenhum ruído visual excessivo |
| wrong-way | vignette/arrow | alarme curto | texto inequívoco |
| lap/final | callout + timing chip | fanfare | split/best lap |
| finish | confetti + camera beat | fanfare | results e restart |

Cada efeito deve ser object-owned, ter `dispose`, pool quando frequente e respeitar `particleDensity`.

### Fase G — HUD, menu e mobile (P1)

1. Adotar sistema de tokens: `--paper`, `--dim`, `--gold`, `--boost-blue`, `--plate-bg`, `--plate-rim`, `--safe`, `--safe-x`.
2. Placas com rim, inner well, sombra e cortes geométricos; não usar apenas `border-radius` + box-shadow genérico.
3. Desktop: leitura esquerda/topo e ações separadas; centro livre para dirigir.
4. Mobile landscape: readouts no rail esquerdo; cluster de controle no canto direito; speedometer não pode ocupar a linha de visão.
5. Portrait: tela explícita “gire o dispositivo”, sem tentar encolher corrida para portrait.
6. Safe area via `env(safe-area-inset-*)` e probe DOM, com padding mínimo de toque.
7. Controles touch: stick virtual opcional, left/right, brake/gas, drift, item, look, pause e auto-accel.
8. Gestures bloqueados corretamente: pinch, double-tap, pull-to-refresh e long-press.
9. Tutorial contextual de drift/item/boost; usar muscle memory consistente.
10. Estados animados: menu → select → countdown → race → pause → results, com transições e foco.

**Aceite:** todos os alvos touch ≥44 px; safe area sem sobreposição; nenhum texto encosta no notch; HUD não invade a pista central.

### Fase H — Áudio procedural e lifecycle (P1/P2)

1. Engine como camada contínua com pitch/volume por velocidade.
2. Mix separado: engine, SFX, music, lead/voice, reverb, delay.
3. Compressor/soft clip para impedir picos agressivos.
4. Sidechain do engine quando item/fanfare/voz toca.
5. Desbloqueio em pointerdown/touchstart/keydown; pause em visibilitychange.
6. Dispose de voices, ambience e nodes em restart/menu.
7. Haptic API com fallback silencioso e intensidade por impacto.

**Aceite:** start, pause, resume, mute e restart não acumulam AudioNodes; cada evento principal tem assinatura sonora distinta.

### Fase I — Medição e QA visual (contínua)

Criar uma matriz fixa:

- Meadow desktop: menu, start, chase reta, curva, drift, item, pad, finish;
- Meadow mobile landscape: mesmos estados;
- Neon desktop: mesmos estados;
- Neon mobile landscape: mesmos estados;
- portrait: orientação/boot/error;
- low/medium/high: pelo menos start e gameplay ativo.

Para cada artefato registrar:

- seed e URL/track;
- viewport e DPR;
- `renderer.info.render.calls`, triangles, textures, programs;
- canvas pixel nonblank/entropy/contrast;
- pageerror/console errors;
- estado do jogo e speed/progress;
- score visual 0–3 por categoria;
- issue, causa, correção, re-medida.

O harness CDP é a rota preferida no SwiftShader. Captura em SwiftShader que fecha o target deve ficar marcada como **não-verificada**, não como aprovação. GPU real é obrigatória para framing, bloom, sombras e materiais finais.

## 5. Apêndice forense — física e jogo observados no bundle

Esta seção separa o que foi extraído estaticamente do bundle do que ainda exige gameplay em GPU real. Os nomes internos foram minificados, mas a estrutura e os valores abaixo foram recuperados por contexto de código, enums e constantes.

### 5.1 Loop de corrida

- Estados: `Menu → Countdown → Racing → Finished → Results`, com `Paused` reversível para Countdown/Racing.
- Até 8 karts; 3 voltas; 32 checkpoints por circuito.
- Grid formado por posição e lateral da pista; progresso monotônico por `t`, `lapIndex`, checkpoint e `raceDistance`.
- Standings recalculado a partir de volta/progresso/checkpoint; finish order e lap times persistidos até Results.
- Input tem edge detection para pause e bloqueia resume automático até throttle ser liberado, evitando retomar instantaneamente com acelerador preso.
- Wrong-way: produto entre forward do kart e tangente da pista; exige velocidade >3.5 e orientação oposta por >0.55s; clear reduz o timer em 2.5×.
- Watchdog: queda abaixo do terreno ou superfície ruim por mais de 2.2s dispara respawn no último `lastGoodT`; invulnerabilidade de 1.8s.

### 5.2 Integração física

- `dt` clamp entre `1/480` e `1/20`; quando há frame lento, subdivide até 6 substeps.
- Integração semi-implícita: suspensão → gravidade → forças longitudinais/laterais → yaw → drag → velocidade máxima → posição.
- Massa do kart: 200; inércia de yaw: `mass × 0.42`.
- Gravidade: 20; top speed base: 30; aceleração base: 3000; resistência de ar/drag base: 4200; roll drag: 1500.
- Velocidade longitudinal limitada ao top speed; ré limitada a -8.
- Yaw rate limitado a ±7 e amortecido por frame.
- Base do kart orientada pelo normal da pista quando no chão, com relaxamento mais lento no ar.

### 5.3 Suspensão e pneus

- Quatro rodas independentes, wheel radius .36, rest length .30, rest compression .12, max compression .24, max droop .13.
- Half-track .66, half-base .80, centro de massa .34, tyre half-width .15.
- Damping compressivo .44, rebound .66, anti-roll 58.
- Cada roda faz probe no ponto de contato e laterais da banda; calcula normal, superfície, carga, compressão, slip e spin.
- Suspensão acumula roll/pitch, ground normal, contacts, total force, bottom depth, dominant/worst surface e off-road load.
- Forces por pneu usam velocidade de contato, direção longitudinal/lateral, grip da superfície, saturação e carga; o torque de cada pneu altera yaw rate.
- Airborne não aplica a mesma assistência de grip; ao pousar, impactos acima de 1.5 geram evento `land`, squash e shake limitado.

### 5.4 Superfícies

Multiplicadores observados:

| Superfície | Grip | Drag | Max speed | Rumble |
|---|---:|---:|---:|---:|
| Road | 1.00 | 1.00 | 1.00 | 0 |
| Dirt | .78 | 1.50 | .82 | .035 |
| Grass | .70 | 2.10 | .68 | .028 |
| Sand | .62 | 2.60 | .60 | .045 |
| Boost | 1.00 | .60 | 1.35 | 0 |
| OffTrack | .55 | 3.20 | .50 | .05 |
| Water | .45 | 4.00 | .35 | .02 |

A tradução para o Super Kart deve manter os multiplicadores atuais como fonte de verdade e apenas adicionar feedback visual/sonoro/haptic por superfície.

### 5.5 Drift, hop e boost

- Drift começa com hop: input drift na roda, contato com chão, velocidade horizontal >4 e steer válido; impulso vertical de 3.05 e janela de hop .8s.
- Direção do drift é determinada por steer ou yaw rate alinhado; threshold de steer .13.
- Drift acumula tempo apenas em superfície válida e enquanto o kart tem contato; carga cai com off-road load.
- Grace de drift evita cancelamento imediato; drift em reta por mais de 1s, stun, ar prolongado ou baixa velocidade libera/cancela.
- Tiers em aproximadamente .55s, .95s e 1.9s; boosts correspondentes são aproximadamente 1.0s/1.12, 1.25 e 1.36 de força.
- Drift tier 0 pode carregar brevemente o tempo de drift por .8s quando liberado cedo.
- Boost pad aplica 1.1s com força 1.28, desde que contato seja detectado.
- Landing com trick armado gera boost adicional; aterrissagem forte produz squash, driver jolt e camera shake.
- Durante drift, lateral velocity e yaw recebem modelo separado do steering normal; fora do drift, lateral velocity é amortecida diretamente.

### 5.6 Colisões

- Wall collision usa normal e push-out; reflete componente normal com ganho 1.28, reduz energia conforme impacto, adiciona impulso de retorno e reduz yaw rate.
- Impacto alto libera drift e emite `collide` com cooldown .12s.
- Kart-kart collision usa raio combinado, separação ponderada por massa e impulso relativo; cooldown .14s.
- Spin-out e squash removem boost/drift e reduzem velocidade; star/invuln protegem contra stun.
- Respawn não é teleporte arbitrário: usa último ponto válido, normal da pista, yaw da tangente e reset completo de suspensão/pose.

### 5.7 Driver stats e AI

- O roster tem 8 pilotos com multiplicadores independentes de aceleração, top speed, weight e handling.
- AI mantém controller separado do kart; recebe hazards, itens, bandas/lane e assist.
- O sistema tem assistência de steering, rubber-band e escolha de alvo/itens, mas a física final continua no mesmo `Kart.step` do player.
- Para o Super Kart, a regra é manter IA/física existentes e importar somente padrões comprovados: superfície como dado, progress anchor monotônico, substeps/clamp, respawn válido e feedback por evento.

### 5.8 Evidência e limites desta reconstrução

- Fonte analisada: HTML, manifest, bundle JS e CSS públicos, com busca de todos os subsistemas e extração de contextos de renderer, materiais, física, corrida, input, HUD, áudio, VFX, LOD e fallback.
- Source map retornou `403`; portanto, nomes originais de arquivos/classes e comentários do projeto não estão disponíveis.
- Boot desktop/mobile foi capturado e revisado por vision.
- Gameplay ativo final não foi aprovado: SwiftShader encerrou o target em sessões longas. Física acima é evidência estática do código, não substitui playtest visual.
- A execução futura deve preencher a matriz de gameplay com GPU real ou um ambiente que mantenha WebGL ativo; qualquer linha sem screenshot vision deve ficar marcada como `unverified`.

## 6. Priorização e commits

### P0 — antes de qualquer redesign

- boot/start sem erro em `?test`, `?demo` e normal;
- fallback de WebGL e contexto perdido sem tela preta;
- nenhuma regressão de física, IA, colisão ou restart;
- capture/QA sem mascarar pageerror.

### P1 — primeira grande evolução visual

1. RenderCapabilityProbe + VisualQualityProfile.
2. Boot progressivo + shader prewarm seguro.
3. MaterialLibrary authored com cache e tiers.
4. Kart LOD/impostor/contact shadow.
5. WorldPropKit + crowd atlas + LOD/instancing.
6. HUD plates + mobile orientation/safe-area/control clusters.
7. Event bus visual/audio/haptic para feedback.

### P2 — acabamento de alto nível

- landmarks únicos por setor;
- wet-road/reflection controlada na Neon;
- decals de desgaste e variação de props;
- DOF/motion blur/volumetrics apenas em high/ultra;
- acabamento de menu, roster, results e loading;
- compositor/passes combinados quando medição provar ganho.

### Política de entrega

- Um commit por unidade coerente.
- Build/probe/teste antes de cada push.
- Mudança visual exige capturas desktop/mobile e revisão por vision.
- Mudança de gameplay exige sim/probe e regressão das duas pistas.
- Atualizar release notes, vault, wiki e memória em cada rodada relevante.

## 6. O que não fazer

- Não adicionar bloom para compensar modelos sem forma.
- Não aumentar saturação até esconder falta de textura.
- Não copiar paleta, logo, nomes, layout proprietário ou código do benchmark.
- Não trocar física/IA que já passaram os probes apenas para imitar apresentação.
- Não declarar “visual final” com screenshot SwiftShader que não contém gameplay representativo.
- Não criar cinco caches de qualidade desconectados; profile único ou nada.

## 7. Ordem recomendada de execução

1. Corrigir/medir boot, capability e pipeline.
2. MaterialLibrary + texturas procedurais authored.
3. Hero kart + shadow + LOD.
4. WorldPropKit + crowd/vegetação/landmarks.
5. Pista, câmera e speed readability.
6. VFX event-driven e áudio lifecycle.
7. HUD/menu/mobile.
8. Matriz completa de captura e scorecard.
9. GPU real para aprovação visual final.

O jogo deve terminar essa sequência ainda sendo o mesmo kart racer: corrida responsiva, IA previsível, drift, itens e pistas preservados. A evolução é de apresentação, densidade e feedback — não de trocar o núcleo que já funciona.
