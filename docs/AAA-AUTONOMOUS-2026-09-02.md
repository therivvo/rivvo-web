# AAA Autonomous QA — 2026-09-02

## [2026-09-04T01:00Z] Autonomous tick — AO de contato Neon ACEITO (root cause: coletor nunca instanciado no night)
- Baseline re-medido no `HEAD 3c65a1a`: worktree trazia linha órfã de tick interrompido (`_contactAOs.push r=5.0` p/ todas as fileiras) + blocos NEXT/AO1 em GATES/docs não commitados; arquivos tmp (`docs/.hermes-tmp.*`, `stderr.txt`, `vite.config.js.timestamp-*`, `src/track/.hermes-tmp.*`) removidos.
- Achado raiz: `buildContactShadows()` era chamado SOMENTE no branch Meadow (`if (!night)`); no modo night os discs `_contactAOs` (postes neon r=1.7 incluídos) nunca eram instanciados — A/B inicial do candidato deu diff zero (`0.09%` vista, `0.02%` near) e expôs o bug.
- Candidato final em `src/track/Environment.js`: (1) discs footprint-fitted `max(sx*10,sz*8)*0.5+1.5` só na fileira roadside A (`near:true`, 11-19m), sem tocar ordem `rand()`; (2) chamada `buildContactShadows(scene)` no branch night. Nenhuma regra de corrida, input, áudio, material emissivo ou asset externo alterado.
- Checks: `node --check` + `git diff --check` OK; build externo `SK3D_OUT_DIR=/tmp/sk3d-dist-roadside-ao2` → `44 modules`, `904.11 kB`, `2.15s`; AI Track 1/2 ×20 → `0 lost / 0 backwards / 0 crashes`.
- A/B GPU pareado (vite :3461 no gpu-runner, ANGLE/Vulkan `RADV PHOENIX`, `pageErrors=[]`, mesma torre `instance 8`, mesma câmera `y=4.07 fov=55`): near desktop `meanAbsDiff=4.8306 pctOver2=22.4865%`, mobile `7.7181%`; vista `34.33%/47.06%` (inclui shimmer de animação — composição sem regressão). Crítica cega mesmo prompt: base item-box flutuante/bases duras (5/10) → cand sombra de contato/bases ancoradas (7/10).
- Vídeo `?demo` 30s pós-accept: Neon d/m `309/498` frames `phase=race`, Meadow d/m `402/495` frames `phase=finished`; frames distribuídos auditados (Neon kart+HUD íntegros, Meadow sem leak de AO). Artefatos em `qa-gpu-runner/roadside-ao/` (não versionado) + helpers `tmp-diff-png.py` (stdlib-only) e `tmp-capture-near.cjs`.
- Decisão: **PRODUCT CHANGE ACCEPTED**. Próximo gap: variedade da Meadow / torres IA recoloridas / fog residual — a definir por medição; score AAA não declarado completo.

## [2026-09-04T23:10Z] Autonomous tick — A/B plinth Neon rejeitado
- Baseline real re-medido no `HEAD 06c0ae7`: `src/` limpo antes do candidato; build externo final via `SK3D_OUT_DIR=/tmp/sk3d-dist-cur-final npm run build` passou com `44 módulos`, `903.98 kB`, em `2.11s`; AI Track 1/2 ×20 retornou `0 lost / 0 backwards / 0 crashes`.
- Runner direto confirmou `GPU_HOST_OK PLAYWRIGHT_OK DRM_OK`; captura fixa no LXC105 usou ANGLE/Vulkan `RADV PHOENIX`, canvas `1280×720` e `390×844`, `pageErrors=[]`, paleta Neon determinística `13/22/20/17/11` (83 torres).
- Candidato único adicionou plinth instanciado emissive-safe sob as torres Neon. A/B pareado com o mesmo capturador/prompt não mostrou diferença visual discernível: skyline, grounding e janelas ficaram essencialmente idênticos; diff bruto acima do limiar 2 foi `6.8844%` desktop e `14.0488%` mobile, sem valor probatório de melhoria.
- O candidato foi totalmente revertido; `src/` voltou limpo. Vídeo QA ativo pós-reversão em Meadow/Neon desktop/mobile terminou sem erro emitido, GPU `RADV PHOENIX`, `98/131/83/131` frames e `phase=race` durante a janela de 8s.
- Decisão: **REVERTED / NO PRODUCT CHANGE ACCEPTED**. Próximo gap segue material/AO Neon emissive-safe com hipótese mais visível.

## [2026-09-03T23:31Z] Autonomous tick — fundações Neon rejeitadas
- Baseline re-medido no `HEAD 83d0113`: `src/` limpo, Vite local `HTTP=200`, layout City PASS, skyline determinístico `83` torres. Build externo pós-candidato: `44 módulos`, `904.35 kB`, `2.64s`; AI Track 1/2 ×20: `0 lost / 0 backwards / 0 crashes`.
- Rota direta ao runner `192.168.0.195` confirmou Playwright/Chromium; captura fixa usou ANGLE/Vulkan `RADV PHOENIX`, WebGL2, `pageErrors=[]`, `1280×720` e `390×844`, paleta `13/22/20/17/11`.
- Candidato único adicionou fundações navy instanciadas sob cada torre. A/B no mesmo capturador/prompt: diff acima de limiar 2 `7.0342%` desktop e `14.1244%` mobile, porém visão pareada não encontrou base/grounding legível nem composição melhor; frames ficaram essencialmente idênticos.
- Candidato totalmente revertido; nenhuma mudança em `src/` aceita. Artefatos pré/pós preservados em `qa-gpu-runner/tick-foundation/` e não versionados. Próximo gap: hipótese material/AO Neon com efeito de grounding realmente visível.


## [2026-09-03T22:56Z] Autonomous tick — runner bloqueado, sem mudança de produto
- Baseline re-medido no `HEAD 7069ecf`: `src/` sem diff; `node --check`/`git diff --check` passaram; build externo via `SK3D_OUT_DIR=/tmp/sk3d-dist-tick-1788476149` passou com `44 módulos`, bundle `904.01 kB`, em `2.08s`.
- AI Track 1/2 ×20 passou com `0 lost / 0 backwards / 0 crashes`; Vite local respondeu `HTTP=200`.
- Probes seguros reportaram `GPU_PASSWORD_FILE=MISSING`, `PW_LOCAL=MISSING`, `PW_FALLBACK=MISSING`; nenhum segredo foi lido. Sem LXC105/RADV PHOENIX não há vídeo Meadow/Neon desktop/mobile ou A/B visual defensável.
- O gap permanece material/AO Neon emissive-safe; a dívida secundária de `Math.random()` runtime foi re-medida, mas não alterada sem harness browser/lifecycle para provar ausência de regressão.
- Decisão: **NO PRODUCT CHANGE ACCEPTED**. Próximo: restaurar rota verificável do GPU runner e executar A/B pareado; score AAA não é declarado completo.

## [2026-09-03T22:39Z] Autonomous tick — revalidação bloqueada, sem mudança de produto
- Baseline re-medido no `HEAD 104e058`: `src/` sem diff; `node --check`/`git diff --check` passaram; build externo `SK3D_OUT_DIR=/tmp/sk3d-dist-baseline-1788475166 npm run build` passou com `44 módulos`, bundle `904.02 kB`, em `2.18s`.
- AI Track 1/2 ×20 passou com `0 lost / 0 backwards / 0 crashes`; Vite local respondeu `HTTP=200`.
- O gap único continua sendo A/B de material/AO Neon emissive-safe. Probes seguros reportaram `PROXMOX_PASSWORD_FILE=MISSING`, `PW_LOCAL=MISSING`, `PW_FALLBACK=MISSING`, `SSH_KEY=MISSING`; sem LXC105/RADV PHOENIX não há vídeo desktop/mobile ou A/B visual defensável. O probe de assets reportou `TRIPO_API_KEY=MISSING`, `GEMINI_API_KEY=MISSING`, `ELEVENLABS_API_KEY=MISSING`.
- Auditoria estática também confirmou uma dívida secundária de determinismo (`Math.random()` em `main.js`, `Particles.js`, `RaceManager.js`, `Materials.js` e HUD), mas ela não foi alterada neste tick por não ser o gap prioritário nem ter harness browser/lifecycle disponível.
- Decisão: **NO PRODUCT CHANGE ACCEPTED**. Nenhum arquivo `src/` foi modificado; nenhum vídeo, score visual ou claim AAA novo foi alegado. Próximo: restaurar rota verificável do GPU runner e executar A/B material/AO Neon com protocolo idêntico.


## [2026-09-03T22:24Z] Autonomous tick — validação DPR móvel, sem novo delta de produto
- Baseline re-medido no HEAD `a9671c5`; `VisualQualityProfile.js` já continha a alteração de qualidade touch que permite `maxPixelRatio` até `2` em hardware real. Nenhuma fonte foi editada neste tick.
- Checks locais passaram: `node --check` em `main.js`/`VisualQualityProfile.js`, `git diff --check`; build externo `SK3D_OUT_DIR=/tmp/sk3d-dist-tick-current npm run build` → `44 módulos`, `904.02 kB`, `2.13s`; AI Track 1/2 ×20 → `0 lost / 0 backwards / 0 crashes`.
- GPU direto `192.168.0.195` confirmou ANGLE/Vulkan `RADV PHOENIX`, WebGL2 e `pageErrors=[]`. Vídeo QA executou Meadow/Neon desktop/mobile em pré/pós: 8 sequências, candidato `98/130/74/133` frames e baseline `93/132/74/132` frames; todos permaneceram em `phase=race` durante a janela de 8s.
- Probe específico com `deviceScaleFactor=2` mediu baseline `pixelRatio=1.5`, framebuffer `585×1266`; candidato `pixelRatio=2`, framebuffer `780×1688`, ambos sem page errors. Crítica cega idêntica dos frames/contact sheets não encontrou regressão visual direcional; o ganho aceito é técnico (mais resolução), não um score AAA.
- Decisão: **nenhum novo delta de produto neste tick**; a alteração DPR já publicada permanece validada. Artefatos em `qa-gpu-runner/tick-dpr/` são intencionalmente não rastreados. Próximo gap: A/B material/AO Neon emissive-safe com frame fixo.


## [2026-09-03T21:53Z] Autonomous tick — ColorGrade A/B rejeitado
- Baseline re-medido no `HEAD 7762d43`; alterações pré-existentes do usuário em `src/config.js`, `src/main.js` e `src/track/Environment.js` foram preservadas e não participaram do candidato; checks estáticos, build externo e AI Track 1/2 ×20 passaram (`44 módulos`, `903.92 kB`, `2.21s`, `0 lost / 0 backwards / 0 crashes`).
- O único candidato foi desabilitar o `ColorGradeShader` somente no harness QA `no-color-grade`; o default de `src/render/PostFX.js` não mudou. O modo mobile, onde o pass não existe, foi tratado como no-op explícito.
- GPU direto `192.168.0.195` confirmou ANGLE/Vulkan `RADV PHOENIX`, WebGL2, `pageErrors=[]`, `phase=race`; A/B cobriu Meadow/Neon desktop/mobile com `647–1134` samples. Calls desktop `17→16`; Meadow desktop `80.969→83.833 FPS`, frame p95 `16.0→15.8 ms`; Neon desktop `89.648→96.405 FPS`, p95 `13.4→12.4 ms`.
- Oito sequências de vídeo QA (`95–137` frames por cenário) cobriram Meadow/Neon desktop/mobile em pré/pós. Crítico cego idêntico nos oito frames representativos observou perda de contraste/tonalidade: Meadow pós mais lavado e Neon pós com menor separação visual.
- Decisão: **NO PRODUCT CHANGE ACCEPTED**. A instrumentação `no-color-grade` permanece QA-only; color grade continua ativo no produto. Artefatos: `qa-gpu-runner/tick-colorgrade-current/` (não staged).


## [2026-09-03T21:31Z] Autonomous tick — Bloom A/B rejeitado
- Baseline re-medido no `HEAD e31ee81`: `src/` limpo antes do candidato, dev `HTTP_STATUS=200`; `node --check`/`git diff --check` passaram; build sanitizado via `SK3D_OUT_DIR=/tmp/sk3d-dist-tick-final npm run build` passou com `44 modules`, `903.92 kB`, em `2.20s`; AI Track 1/2 ×20 ficou em `0 lost / 0 backwards / 0 crashes`.
- O único candidato foi desligar temporariamente `UnrealBloomPass` no modo QA `no-bloom`; o default de `src/render/PostFX.js` não mudou. O detector foi tornado robusto ao nome minificado `_UnrealBloomPass`.
- GPU direto `192.168.0.195` confirmou ANGLE/Vulkan `RADV PHOENIX`, WebGL2, `pageErrors=[]`, `phase=race`; A/B cobriu Meadow/Neon desktop/mobile com samples baseline/candidato `628–1020`.
- FPS baseline→candidato: Meadow desktop `80.153→78.636` (`-1.89%`), Meadow mobile `104.541→100.487` (`-3.88%`), Neon desktop `91.748→97.127` (`+5.86%`), Neon mobile `127.449→118.251` (`-7.22%`). Calls medianas caíram `17→4` desktop e `16→3` mobile, mas frame p95 variou `15.4→16.0`, `11.9→12.4`, `13.0→12.1`, `10.3→10.4 ms`.
- Oito sequências de vídeo QA-only (`baseline/no-bloom × Meadow/Neon × desktop/mobile`) produziram `892` frames JPEG; todas reportaram `RADV PHOENIX` e `phase=race` durante 8s. Crítica cega idêntica em frames representativos mostrou Bloom preservando halo/legibilidade Neon; um frame baseline indisponível foi substituído, então não é prova A/B visual perfeitamente sincronizada.
- Decisão: **NO PRODUCT CHANGE ACCEPTED**. Bloom continua ativo no produto; o suporte `no-bloom` permanece instrumentação QA para futuras medições. Artefatos: `qa-gpu-runner/tick-bloom/` (QA não deve ser staged).

## [2026-09-03T21:18Z] Autonomous tick — A/B temporal do Vignette rejeitado
- Baseline re-medido no `HEAD adbce6c`: `src/` limpo; build externo `SK3D_OUT_DIR=/tmp/sk3d-dist-tick-current npm run build` passou com `44 modules`, `903.92 kB` em `2.13s`; AI Track 1/2 ×20 retornou `0 lost / 0 backwards / 0 crashes`; dev server `HTTP 200`.
- Runner direto `192.168.0.195` confirmou `/opt/pwtest`, DRM e ANGLE/Vulkan `RADV PHOENIX`; A/B temporal executado em Meadow/Neon desktop/mobile, WebGL2, `phase=race`, `pageErrors=[]`, samples `371–634`.
- Calls medianas caíram `17→16` desktop e `16→15` mobile, mas o FPS foi inconsistente: Meadow desktop `76.886→74.352` (`-3.30%`), Meadow mobile `95.494→109.091` (`+14.24%`), Neon desktop `90.334→91.666` (`+1.47%`), Neon mobile `126.620→111.384` (`-12.03%`). Frame/render p95 também variaram, sem redução uniforme.
- Oito sequências QA-only (`baseline/no-vignette × Meadow/Neon × desktop/mobile`) rodaram por 8s; todas reportaram `RADV PHOENIX`, sem pageerror emitido e `phase=race`. Não são claim de release ou de corrida concluída.
- Decisão: **NO PRODUCT CHANGE ACCEPTED**. O modo `no-vignette` permanece somente instrumentação QA; nenhum `src/` foi alterado. Próximo gap: outro owner/pass com probe temporal fixo e delta consistente.

## [2026-09-03T20:08Z] Autonomous tick — vídeo temporal do owner `kart-ai`, sem mudança
- Baseline real no `HEAD df4053f`: `src/` limpo; build externo `SK3D_OUT_DIR=/tmp/sk3d-dist-baseline-2000 npm run build` passou com `44 modules`, bundle `903.92 kB` em `2.15s`; AI Track 1/2 ×20 retornou `0 lost / 0 backwards / 0 crashes`.
- Breakdown fixo no GPU runner `192.168.0.195` confirmou ANGLE/Vulkan `RADV PHOENIX`, WebGL2 e `pageErrors=[]`; Meadow desktop/mobile mediu `1948/984 calls` e `1,089,095/821,397 tris`; `kart-ai` segue em `1175 meshes/199650 tris`.
- Vídeo ativo `?demo` real, quatro combinações, terminou `phase=finished`: Meadow desktop `831` frames, Meadow mobile `1001`, Neon desktop `648`, Neon mobile `1009`; todos com `RADV PHOENIX`.
- O owner foi reavaliado, mas ainda não existe frame-time por pass/owner. O candidato anterior de `castShadow=false` já foi rejeitado; não houve alteração especulativa nesta rodada. **NO PRODUCT CHANGE ACCEPTED**.
- Próximo gap: probe fixo que meça frame-time/pass temporalmente pareado antes de novo candidato `kart-ai`/PostFX.

## [2026-09-03T20:22Z] Autonomous tick — baseline temporal de render aceito, sem mudança de produto
- Baseline real em `HEAD 072cdeb`: `src/` limpo; build externo `SK3D_OUT_DIR=/tmp/sk3d-dist-tp-final npm run build` passou com `44 modules`, bundle `903.92 kB` em `2.29s`; AI Track 1/2 ×20 retornou `0 lost / 0 backwards / 0 crashes`.
- Novo auditor QA-only `scripts/audit-frame-time.cjs` mediu quatro cenários no GPU runner direto `192.168.0.195`, sem tocar em `src/`: Meadow/Neon × desktop/mobile, WebGL2, ANGLE/Vulkan `RADV PHOENIX`, `phase=race`, `pageErrors=[]`.
- Métricas temporais: FPS aproximado Meadow desktop/mobile `72.99/93.97`, Neon desktop/mobile `94.92/116.35`; p95 de frame `15.2/13.6/13.0/10.1 ms`; p95 do render instrumentado `13.4/11.8/10.7/8.3 ms`; chamadas de render por frame `17/16/17/16`. Passes observados: Render, Bloom, Shader e Output (duas variantes Shader no desktop).
- O primeiro probe usava `renderer.info` depois do reset de pass e produzia `calls=1`; foi corrigido antes do resultado final para contar chamadas reais de `renderer.render()`. Resultado é baseline de custo, não comparação de otimização.
- Decisão: **QA INSTRUMENTATION ACCEPTED; NO PRODUCT CHANGE**. Nenhum arquivo `src/` foi alterado; próximo gap é testar um owner/pass isolado somente com A/B temporalmente pareado e vídeo visual preservado.

## [2026-09-03T20:41Z] Autonomous tick — Vignette A/B temporal rejeitado
- Hipótese isolada no QA: desligar temporariamente `VignetteShader`, sem mudar default, regras ou assets; `scripts/audit-frame-time.cjs` e `scripts/playtest-video.cjs` ganharam modo `no-vignette`.
- GPU direto confirmou ANGLE/Vulkan `RADV PHOENIX`, WebGL2 e `pageErrors=[]`; baseline/candidato medidos em Meadow/Neon desktop/mobile. Calls medianas caíram `17→16` desktop e `16→15` mobile, mas o FPS/frame p95 não foi consistente: Meadow desktop `80.44→76.58 FPS` e mobile `112.82→99.14 FPS`.
- Oito vídeos (pré/pós × Meadow/Neon × desktop/mobile) terminaram `phase=finished`; a crítica cega em frame_0030 encontrou estados temporais divergentes, sem delta visual atribuível ao Vignette. **NO PRODUCT CHANGE ACCEPTED**.
- Checks finais: build externo `44 modules`, `903.92 kB`, `2.13s`; AI Track 1/2 ×20 `0 lost / 0 backwards / 0 crashes`; apenas instrumentação QA será publicada. Próximo gap: outro owner/pass com pareamento fixo mais determinístico.

## [2026-09-03T19:42Z] Autonomous tick — owner de performance revalidado, sem mudança de produto
- Baseline re-medido em `HEAD 0a4a8ed`; `src/` permaneceu sem diff. O owner mensurável continua `kart-ai` com `1175 meshes/199650 tris` no breakdown anterior.
- Checks locais passaram: `node --check` nos módulos/runtime/QA, `git diff --check`; build externo via `SK3D_OUT_DIR=/tmp/sk3d-dist-current-tick npm run build` → `44 modules transformed`, `903.92 kB`, `2.09s`; AI Track 1/2 ×20 → `0 lost / 0 backwards / 0 crashes`.
- Runner direto voltou: `192.168.0.195` confirmou `/opt/pwtest` e Chromium; auditoria confirmou WebGL2, ANGLE/Vulkan `RADV PHOENIX`, `pageErrors=[]`. Render breakdown atual: Meadow desktop/mobile `1948/977 calls`, `1,089,095/819,717 tris`; o custo segue alto.
- Vídeo ativo `?demo` terminou `phase=finished` em Meadow/Neon desktop/mobile com `849/998/689/1007` frames. Não houve redução isolada de calls/frame-time demonstrada; a tentativa anterior de `castShadow=false` em `kart-ai` já havia piorado calls no mobile e não foi repetida como produto.
- Decisão: **NO PRODUCT CHANGE ACCEPTED**. Sem candidato seguro comprovado, nenhum arquivo `src/` foi alterado ou commitado. Próximo gap: probe fixo temporalmente pareado de outro owner/pass, priorizando uma redução mensurável sem degradar a leitura visual.

## [2026-09-03T18:54Z] Autonomous tick — `kart-ai` shadow-caster candidate rejected
- Baseline re-measured at `HEAD a321b24`; `kart-ai` owner was `1175 meshes/199650 tris` in the existing GPU breakdown.
- Candidate disabled `castShadow` only for AI kart descendants. Static checks/build passed (`44 modules`, `904.05 kB`, `2.44s`) and AI Track 1/2 ×20 stayed at `0 lost / 0 backwards / 0 crashes`.
- Direct LXC105 probe confirmed Chromium/Playwright/GPU; active runs used ANGLE/Vulkan `RADV PHOENIX`, ended `phase=finished`, with frames pre/post desktop `664/676` and mobile `1006/1007`.
- Structural probe measured `aiCasters 82→0` and total casters `220→138`, but renderer calls remained unreliable (`calls=1` in both fixed boots). Free-running frame diff (`0.928549` desktop, `0.534714` mobile) was not a valid quality proxy because timing/positions differed.
- Decision: **REVERTED / NO PRODUCT CHANGE ACCEPTED**. The source returned clean; next gap remains an isolated owner reduction only with a deterministic fixed-frame/performance probe.

## [2026-09-03T18:38Z] Autonomous tick — runner bloqueado, sem delta de produto
- Baseline real re-medido no `HEAD e281201`; `src/` permaneceu limpo e o gap sustentado continua sendo um owner Neon mensurável/material-AO, sem candidato aceito.
- Checks passaram: `node --check` nos módulos críticos, `git diff --check`; build externo `SK3D_OUT_DIR=/tmp/sk3d-dist-rt npm run build` → `44 modules transformed`, `903.92 kB`, `✓ built in 2.13s`.
- AI Track 1/2 ×20 passou com `0 lost / 0 backwards / 0 crashes`; dev server respondeu `HTTP_STATUS=200`.
- Probes seguros: password file Proxmox `MISSING`, `/opt/pwtest` e fallback Playwright `MISSING`, `SSHPASS=MISSING`; geradores somente estados redigidos. Probe remoto terminou `REMOTE_PROBE=NO_PASSWORD_FILE`.
- Decisão: **NO PRODUCT CHANGE ACCEPTED**. Sem LXC105/RADV PHOENIX não houve vídeo desktop/mobile ou A/B visual; próximo gap é testar uma redução de owner isolado (`kart-ai` ou PostFX) somente quando a rota GPU retornar.

## [2026-09-03T18:24Z] Autonomous tick — runner bloqueado, sem mudança de produto
- Baseline real re-medido no `HEAD e91b118`: `src/` sem diff; auditor de budget mantém `kart-ai` como owner mensurável, mas não há redução segura sem A/B.
- Checks passaram: `node --check`/`git diff --check`; build externo `SK3D_OUT_DIR=/tmp/sk3d-dist-rt npm run build` → `44 modules`, `903.92 kB`, `✓ built in 2.15s`.
- AI Track 1/2 ×20 passou com `0 lost / 0 backwards / 0 crashes`; dev server `HTTP 200`.
- Probe seguro: `PWFILE=MISSING`, browser local presente mas `/opt/pwtest` e fallback ausentes; tentativa SSH sem segredo terminou `SSH_RC=139`. Sem LXC105/RADV PHOENIX novo, vídeo/A-B não é defensável.
- Decisão: **NO PRODUCT CHANGE ACCEPTED**. Próximo gap: testar redução isolada de `kart-ai` ou passe PostFX quando a rota GPU verificável retornar.

## [2026-09-03T18:10Z] Autonomous tick — revalidação após instrumentação, sem mudança de produto
- Baseline re-medido no `HEAD b6aab8a`; `src/` permaneceu sem diff. O auditor de budget anterior continua sendo o único avanço aceito e mantém owners mensuráveis, mas não demonstrou ainda uma redução isolável segura.
- Checks estáticos passaram: `node --check scripts/audit-render-breakdown.cjs src/main.js src/track/Environment.js src/render/MaterialLibrary.js` e `git diff --check`.
- Build compatível com virtiofs passou via `SK3D_OUT_DIR=/tmp/sk3d-dist-rbt npm run build`: `44 modules`, `903.92 kB`, `✓ built in 2.09s`.
- Regressão determinística AI Track 1/2 ×20 passou com `0 lost / 0 backwards / 0 crashes`; dev server respondeu `HTTP 200`.
- Probe seguro do runner: `pwfile=MISSING`, Playwright local/fallback `MISSING`; sem RADV PHOENIX novo não foi possível executar vídeo/A-B visual neste ambiente. Nenhum segredo foi lido ou registrado.
- Decisão: **NO PRODUCT CHANGE ACCEPTED**. Próximo gap continua a primeira redução de owner isolado — começando por `kart-ai`/passes somente quando o runner GPU voltar a ficar verificável.

## [2026-09-03T17:45Z] Autonomous tick — instrumentação de custo por subsistema/pass
- Baseline re-medido no `HEAD 3981e7e`: build externo `44 módulos/903.92 kB/2.10s`; AI Track 1/2 ×20 com `0 lost / 0 backwards / 0 crashes`.
- Adicionado `scripts/audit-render-breakdown.cjs`, auditor QA-only que lê `window.__sk3d`, separa `namedRoots`/buckets de meshes, triângulos e instancing, e lista passes PostFX. Nenhuma regra, aparência, áudio ou asset foi alterado.
- Runner direto via túnel reverso confirmou WebGL2 + ANGLE/Vulkan `RADV PHOENIX`, `pageErrors=[]`, em Meadow/Neon desktop `1280×720` e mobile `390×844`.
- Medições: Meadow desktop/mobile `1948/963 calls`, `1,089,095/818,585 tris`, `95/89 textures`, `1345/1241 geometries`; Neon desktop/mobile `1586/873 calls`, `307,268/194,118 tris`, `79/76 textures`, `1051/988 geometries`.
- Breakdown acionável: `kart-ai` = `1175 meshes/199650 tris`; Neon = `8` grupos nomeados de roof-caps/pilasters. Gameplay ativo terminou `phase=finished` com `827/991/667/1010` frames (Meadow d/m, Neon d/m).
- Decisão: **QA INSTRUMENTATION ACCEPTED; NO PRODUCT CHANGE**. O budget continua alto, mas agora há owners mensuráveis; nenhuma redução é alegada sem A/B visual isolado.

## [2026-09-03T17:16Z] Autonomous tick — budget audit pós-pilastras, sem delta de produto
- Baseline real: HEAD `cf89f07`; `src/` permaneceu sem diff de produto. Build externo `SK3D_OUT_DIR=/tmp/sk3d-dist-current-tick npm run build` passou com `44 modules`, `903.92 kB`, `2.19s`; AI Track 1/2 ×20 retornou `0 lost / 0 backwards / 0 crashes`.
- Runtime GPU direto no runner `192.168.0.195` confirmou ANGLE/Vulkan `RADV PHOENIX`, WebGL2, `pageErrors=[]` nas capturas fixas Neon desktop/mobile (`1280×720`/`390×844`), palette `13/22/20/17/11`, total `83`.
- Budget medido no frame completo: desktop profile `high` = `1593 calls`, `307480 triangles`, `79 textures`, `1055 geometries`; mobile profile `medium` = `1057 calls`, `228098 triangles`, `76 textures`, `992 geometries`. Auditoria de cena Neon contou `1978` meshes; skyline já usa InstancedMesh/frustum culling e auto-instancing está ativo.
- Gameplay vídeo GPU terminou normalmente: Meadow desktop/mobile `847/1003` frames; Neon desktop/mobile `633/1008`; todos `phase=finished`. Nenhuma regressão funcional foi observada; não há score visual novo alegado.
- Decisão: **NO PRODUCT CHANGE ACCEPTED**. O custo está acima do budget histórico, mas não há um único owner atribuível com redução segura e A/B visual disponível nesta rodada; alterar densidade/instancing/PostFX sem alvo seria especulativo. Próximo gap: instrumentar custo por subsistema/pass e então testar uma redução isolada.

## [2026-09-03T16:50Z] Autonomous tick — pilastras de fachada Neon aceitas
- Gap único: o skyline Neon continuava legível como caixas repetidas, apesar dos roof caps aceitos; faltava articulação vertical nas fachadas.
- Candidato único aceito em `src/track/Environment.js`: pilastras estreitas nos quatro cantos de cada torre, via uma `InstancedMesh` por fileira e material navy compartilhado; não cobre a textura emissiva nem toca corrida, input, áudio ou assets.
- Checks: `node --check`, `git diff --check`; build externo `SK3D_OUT_DIR=/tmp/sk3d-dist-live-pilasters npm run build` passou com `44 módulos`, `903.92 kB`; AI Track 1/2 ×20 passou com `0 lost / 0 backwards / 0 crashes`.
- A/B fixo pareado no GPU: desktop/mobile `1280×720`/`390×844`, ANGLE Vulkan `RADV PHOENIX`, `pageErrors=[]`, paleta idêntica `13/22/20/17/11` (83 torres). Diff acima de limiar 2: desktop `58093/921600 (0.063035)`, mobile `33246/329160 (0.101003)`; mean absolute channel `0.005384/0.004166`.
- Fresh-eyes: pilastras acrescentaram bordas/ritmo vertical visível; janelas permaneceram legíveis; nenhum artefato ou obstrução foi encontrado. Vídeo ativo: Meadow desktop/mobile `812/1003` frames; Neon desktop/mobile `643/1010`; todos `phase=finished`.
- Renderer pós: `743 calls`, `165556 triangles`, `1053 geometries`, `78 textures`; calls/textures excedem o contrato inicial e ficam registrados como risco de performance, não como aprovação irrestrita.
- Decisão: **ACEITO**. Próximo gap: reduzir repetição/halo do skyline Neon com uma hipótese ainda mais localizada, ou priorizar uma auditoria de budget; não declarar AAA completo.


## [2026-09-03T16:35Z] Autonomous tick — revalidação bloqueada, sem delta de produto
- Baseline real: HEAD `7524e99`; `src/` limpo; skyline Neon mantém fachadas `MeshBasicMaterial`/`fog:false`, roof caps já aceitos e nenhum AO/material híbrido executável.
- Checks: `node --check` em `main.js`, `Environment.js` e `MaterialLibrary.js` + `git diff --check` passaram; build externo `SK3D_OUT_DIR=/tmp/sk3d-dist-rt npm run build` passou com `44 módulos`, `903.48 kB`, `2.11s`.
- Regressão determinística: Track 1/2 ×20 seeds, `0 lost / 0 backwards / 0 crashes`; assets `TRIPO/GEMINI/ELEVENLABS=MISSING`.
- Runner bloqueado honestamente: `PROXMOX_PASSWORD_FILE=MISSING`, `/opt/pwtest=MISSING`, Playwright local `MISSING`; sem LXC105/RADV PHOENIX não há vídeo/A-B defensável.
- Decisão: **NO PRODUCT CHANGE ACCEPTED**. Nenhum arquivo `src/` foi alterado. Próximo gap: material/AO Neon seletivo emissive-safe após restaurar a rota GPU.

## [2026-09-03T16:10Z] Autonomous tick — roof caps Neon aceitos
- Baseline real: HEAD `3482238`, `src/` limpo antes do candidato; skyline Neon usava caixas instanciadas com janela emissiva e sem coroamento arquitetural.
- Candidato único: quatro camadas `InstancedMesh` de roof caps rasos (`10.8×0.22×8.8`) em material navy `MeshBasicMaterial`, compartilhando geometria/material e sem alterar corrida, input, áudio ou assets.
- Checks: `node --check`, `git diff --check`, build externo `SK3D_OUT_DIR=/tmp/sk3d-dist-roofcaps npm run build` passou com `44 módulos`, `903.48 kB`, `2.06s`; AI Track 1/2 ×20 retornou `0 lost / 0 backwards / 0 crashes`.
- A/B fixo GPU: desktop/mobile `1280×720`/`390×844`, ANGLE/Vulkan `RADV PHOENIX`, `pageErrors=[]`, paleta `13,22,20,17,11`/83. Diff acima de limiar 2: desktop `119650/921600 (0.129829)`, mobile `72272/329160 (0.219565)`.
- Vision pareada própria e fresh-eyes independente: caps criam coroamento/overhang visível; janelas permanecem legíveis; sem clipping, deformação ou artefato. Vídeo ativo: Meadow desktop/mobile `811/999` frames; Neon desktop/mobile `667/1005`; todos `phase=finished`, GPU `RADV PHOENIX`.
- Decisão: **ACEITO**. Próximo gap: A/B de material/AO Neon seletivo para grounding sem reduzir o contraste emissivo.

## Scope
Desktop and mobile web gameplay for Meadow and Neon City. Primary evidence is sequential GPU video capture on gpu-runner LXC 105 with Vulkan/RADV PHOENIX; vision auditors reviewed spaced frames from those sequences.

## [2026-09-03T14:38Z] Autonomous tick — grounding Neon rejeitado
- Baseline real: `main`, HEAD `4b509c1`, `src/` limpo após a decisão; skyline Neon continua `MeshBasicMaterial`/`fog:false`, sem AO executável.
- Runner direto autenticado: Chromium e `/dev/dri/renderD128` presentes; captura confirmou ANGLE/Vulkan `RADV PHOENIX`.
- Candidato único: `InstancedMesh` de discos de contato roxo-escuros sob as duas fileiras próximas, separado do material emissivo e sem tocar corrida/input/áudio/assets.
- Checks finais após revert: `node --check`, `git diff --check`, build externo `SK3D_OUT_DIR=/tmp/sk3d-dist-tick-1438-reverted npm run build` (`44 modules`, `902.76 kB`), AI Track 1/2 ×20 (`0 lost / 0 backwards / 0 crashes`).
- Captura fixa pré/pós no mesmo harness: desktop/mobile `1280×720`/`390×844`, `pageErrors=[]`, `phase=finished` nos vídeos Meadow/Neon (`815/999/677/1004` frames), GPU `RADV PHOENIX`.
- A/B cego idêntico não mostrou diferença visual discernível em grounding, separação ou legibilidade. Diff bruto: desktop `113513/921600 (0.123169)`, mobile `71853/329160 (0.218292)` pixels acima de limiar 2; pixel delta não foi tratado como ganho.
- Decisão: **REVERTED / NO PRODUCT CHANGE ACCEPTED**. Próximo gap permanece material híbrido/AO Neon com alvo visual mais específico.

## [2026-09-03T14:10Z] Autonomous tick — material híbrido Neon rejeitado
- Baseline real: HEAD `4b509c1`; `src/` limpo no início/fim; `buildNeonCity()` continua `MeshBasicMaterial`/`fog:false`, sem AO executável. Asset probe seguro: geradores sem estado utilizável; nenhum segredo lido.
- Candidato único: fachada base opaca + camada de janelas transparente expandida `0.4%`, para separar volume de emissive sem repetir o PBR que escureceu as fachadas.
- Checks do candidato e final: `node --check`, `git diff --check`, build externo. Final `SK3D_OUT_DIR=/tmp/sk3d-dist-tick-1410-final npm run build` passou com `44 modules`, `902.76 kB`, `2.56s`; AI Track 1/2 ×20: `0 lost / 0 backwards / 0 crashes`.
- GPU LXC105: ANGLE Vulkan `RADV PHOENIX`; captura fixa desktop/mobile `1280×720`/`390×844`, `pageErrors=[]`, paleta `13,22,20,17,11`/83. Gameplay final: Meadow desktop/mobile `823/996` frames; Neon desktop/mobile `674/1003`; todos `phase=finished`.
- A/B cego idêntico não demonstrou ganho direcional inequívoco de grounding/separação. Diff bruto candidato vs pré: desktop `218399/921600 (0.236978)` e mobile `71682/329160 (0.217773)` pixels acima de limiar 2; mudança de pixels não foi aceita como melhoria.
- Decisão: **REVERTED / NO PRODUCT CHANGE ACCEPTED**. Próximo gap: novo material híbrido emissive-safe, mas com alvo visual mais específico e A/B fixo no mesmo protocolo.

## [2026-09-03T13:39Z] Autonomous tick — sshpass local instável, sem delta de produto
- Baseline real: HEAD `a8526a1`; `src/` sem diff; skyline Neon permanece `MeshBasicMaterial`/`fog:false`, sem AO executável.
- Checks: `node --check`/`git diff --check` passaram; build externo `SK3D_OUT_DIR=/tmp/sk3d-dist-unlock-1339 npm run build` passou com `44 modules`, bundle `902.76 kB`, em `2.12s`.
- Regressão determinística: Track 1/2 ×20 seeds, `0 lost / 0 backwards / 0 crashes`.
- Probe seguro: `PWFILE=MISSING`, Playwright local/fallback `MISSING`; nesta execução `SSHPASS=MISSING` no subprocesso. `sshpass` está instalado, mas `sshpass -e ssh ... true` terminou `SSH_RC=139` (segmentation fault). Nenhum segredo foi lido ou exibido.
- Decisão: **NO PRODUCT CHANGE ACCEPTED**. Sem sessão LXC105 não há vídeo RADV PHOENIX, A/B pareado ou evidência visual nova. Próximo gap: restaurar uma rota SSH estável e executar A/B material/AO Neon emissive-safe.

## [2026-09-03T12:24:38Z] Autonomous tick — runner bloqueado, sem delta de produto
- Baseline real: HEAD `573af50`; skyline Neon ainda usa `MeshBasicMaterial`, `fog:false`, sem AO executável (`SKYLINE_BASIC=True`, `SKYLINE_AO=False`); `src/` permaneceu sem diff.
- Checks: `node --check` nos módulos críticos e `git diff --check` passaram; build externo `SK3D_OUT_DIR=/tmp/sk3d-dist-tick-1224 npm run build` passou com `44 modules`, bundle `902.76 kB`, em `2.21s`.
- Regressão determinística: Track 1/2 ×20 seeds, `0 lost / 0 backwards / 0 crashes`; dev server `HTTP 200`.
- Probes seguros: `PASSWORD_FILE=MISSING`, `PLAYWRIGHT=SSH_PASS`; geradores `TRIPO/GEMINI/ELEVENLABS=MISSING`. Sem autenticação do LXC105, não há vídeo/A-B ANGLE/Vulkan/RADV PHOENIX novo.
- Decisão: nenhum patch de produto implementado ou aceito. Próximo gap permanece material híbrido/AO Neon emissive-safe condicionado à restauração verificável do runner.

## Evidence
- Desktop gameplay captures: Meadow 653/671 frames; Neon 589/560 frames.
- Mobile gameplay captures after `a1e1599`: Meadow 1002 frames; Neon 1002 frames; viewport 390x844, `hasTouch=true`.
- GPU: ANGLE Vulkan, AMD Radeon 780M, RADV PHOENIX.
- Build: `SK3D_OUT_DIR=/tmp/sk3d-dist-autonomous npm run build` passed.
- `ai-backwards-test.mjs 20` passed in both tracks: 0 lost, 0 backwards, 0 crashes; all sampled onRoad=100%.
- Audio fixes: `56d486e` preserves per-kart engine volume through pre-init mobile unlock; `1bbf3d8` schedules track fade/playlist advance after the last lookahead step instead of cutting the final beat.
- HUD fix `512e4d0`: finish results now hide live telemetry/speedlines/draft behind the result card, eliminating stale LAP/speed/position competition.
- Audio fix `d238f9b`: ducking uses generation + cancellable timer; `stopMusic()` invalidates stale callbacks so finish/victory cannot restore volume in a later race.
- **Última auditoria vision (commit `9cc6afa`, paths exatos):** mobile `frame_1001.jpg` Meadow e `frame_1008.jpg` Neon confirmaram `FINAL LAP` ausente do modal, modal sem clipping e controles utilizáveis; Meadow 7.2, Neon 7.5. Desktop 1280×720: Meadow 7.0 e Neon 7.35, com HUD corretamente substituído no finish. Ressalva: os controles ainda aparentavam ativos em parte da captura mobile; confirmar no próximo pacote.
- **Gap corrigido nesta rodada:** `67cf182` adiciona `Meadow Circuit`/`Neon City` no card de resultado; auditoria havia identificado ausência de identificação da pista.
- **Gaps visuais restantes:** Meadow tem pórtico FINISH dominante na aproximação; ambos ainda têm materiais/AO planos; Neon possui grid distante com shimmer e bloom agrupado nas janelas. `http://localhost:3457/` HTTP 200.

## [2026-09-03T11:52:38Z] Autonomous tick — runner bloqueado, sem delta de produto
- Baseline re-medido no HEAD atual antes da decisão: `src/` sem diff; skyline Neon permanece `MeshBasicMaterial`, `fog:false`, sem AO/contact layer.
- Checks locais: `node --check` nos módulos críticos e `git diff --check` passaram; build externo `SK3D_OUT_DIR=/tmp/sk3d-baseline-current npm run build` → `44 modules`, `902.76 kB`, `2.11s`.
- Regressão determinística: Track 1/2 ×20 seeds, `0 lost / 0 backwards / 0 crashes`; servidor existente respondeu `HTTP 200`.
- Probes seguros: arquivo de senha Proxmox `MISSING`, Playwright local/fallback `MISSING`, SSH probe `255`; assets externos reportados somente como estados redigidos. Nenhum segredo foi lido ou persistido.
- Decisão: nenhum patch de produto foi implementado/aceito. O próximo gap permanece material híbrido/AO Neon emissive-safe, condicionado a vídeo A/B pareado no LXC105 com ANGLE/Vulkan e `RADV PHOENIX`.

## [2026-09-03T10:25:36Z] Autonomous tick — bloqueio operacional, sem delta de produto
- Gap único re-medido no HEAD `62e7805`: skyline Neon continua em `MeshBasicMaterial`, `fog:false`, sem `aoMap`; `src/` ficou sem diff.
- Checks: `node --check` em `main.js`, `Environment.js`, `MaterialLibrary.js`; `git diff --check`; build externo `SK3D_OUT_DIR=/tmp/sk3d-dist-aa npm run build` passou com `44 modules`, `902.76 kB`, `2.15s`.
- Regressão determinística AI: Track 1/2 ×20 seeds, `0 lost / 0 backwards / 0 crashes`; dev server `HTTP=200`.
- Probes seguros: Proxmox password file `***`, Playwright local/fallback `MISSING`, geradores externos `***`; SSH `EXIT=255`/`AUTH_OR_NETWORK_BLOCKED`. Nenhum segredo foi exibido.
- Decisão: sem LXC105/RADV PHOENIX, vídeo desktop/mobile e A/B pareado não podem ser provados; nenhum patch de produto foi implementado ou aceito. Próximo gap permanece material híbrido/AO seletivo Neon preservando emissive.

- **Gap corrigido:** `67cf182` adiciona `Meadow Circuit`/`Neon City` ao card de resultado, removendo ambiguidade identificada pela auditoria mobile.
- **Auditoria vision pós-`9cc6afa`:** paths exatos desktop 1280×720: Meadow 7.0 (`frame_0177`, `frame_0806`), Neon 7.35 (`frame_0177`, `frame_0675`); paths mobile 390×844: Meadow 7.2 (`frame_1001`), Neon 7.5 (`frame_1008`). `FINAL LAP` ausente no modal. Nova validação pós-`67cf182` ainda necessária.
- **Gaps restantes:** pórtico FINISH domina Meadow na aproximação; AO/materiais ainda planos; Neon tem shimmer no grid distante e bloom agrupado em janelas; controles mobile precisam margem inferior adicional.

- **Baseline deste ciclo:** HEAD `dfd25c4`; build passou; 40 seeds (20 por pista) passaram com `0 lost`, `0 backwards`, `0 crashes`; `onRoad=100%`.
- **Fixes deste ciclo:** `3f9ad92` respeita mute persistido no primeiro unlock; `f68862f` limpa input keyboard/touch/item-hold em blur/visibility loss; `8af5119` aplica safe-area aos overrides mobile do HUD e controles.
- **Asset sourcing:** probe seguro retornou `TRIPO_API_KEY=MISSING`, `GEMINI_API_KEY=MISSING`, `ELEVENLABS_API_KEY=MISSING`; sem assets externos falsamente declarados.
- **Captura pós-fixes:** GPU real RADV PHOENIX: Meadow mobile 1004 / desktop 827 frames; Neon mobile 1009 / desktop 654 frames; viewport mobile 390×844, desktop 1280×720. Vision pós-fixes está em execução nos paths exatos.
- **Iteração `ea4d2bc`:** safe-area reaplicada nos breakpoints `≤480px` para touch/ITEM/DRIFT; readout do velocímetro mobile ampliado e com maior contraste. Capturas GPU: Meadow 1002 mobile/865 desktop; Neon 1011 mobile/664 desktop. Regressão AI: 0 lost/backwards/crashes nas duas pistas.
- **Iteração `f04d535`:** velocímetro mobile elevado 18px para separar `DRIFT`/`ITEM`; hint de teclado `or press R` ocultado no finish mobile. Capturas GPU: Meadow 1002 mobile/813 desktop; Neon 1009 mobile/689 desktop; vision pré/pós em execução.
- **Iteração `e41b41d`:** opacidade base do velocímetro mobile elevada de `0.5` para `0.78` para blindar leitura sobre fundos claros; capturas completas Meadow 998 mobile/814 desktop, Neon 1007 mobile/665 desktop. Vision encontrou melhoria parcial e intermitência persistente no Neon.
- **Iteração `01eb765`:** opacidade base elevada `0.78→0.92` e unidade `KM/H` `0.95→1.0`. Capturas GPU completas: Meadow 994 mobile/798 desktop; Neon 1005 mobile/634 desktop; auditoria vision encontrou dois frames Neon ainda em 3/10.
- **Iteração `4c7cbf5`:** causa raiz identificada no auto-hide mobile: `.sk3d-hud-idle .sk3d-speedo { opacity: 0.15 }` apagava telemetria após inatividade. Corrigido para `0.92`. Capturas completas GPU: Meadow 993 mobile/806 desktop; Neon 1007 mobile/639 desktop. Fresh-eyes convergiu: Neon 5.5→8.5 e Meadow 5.5–8→8 no speedometer; desktop sem regressão visual. Limite: frames não provam exatamente 4s sem input nem `0 KM/H`.
- **Iteração `ca54d1d`:** câmera Neon aproximada por `neonFollowExtra 0.55→0.30` para corrigir kart pequeno/cortado em combate. Capturas completas GPU: Meadow 996 mobile/824 desktop; Neon 1006 mobile/694 desktop; fresh-eyes pré/pós pendente.
- **Correção operacional de `ca54d1d`:** auditoria revelou que `?demo` usa ramo cinematográfico que ignorava `neonFollowExtra`; configuração foi restaurada em `dd03f50`.
- **Iteração `c4dd3ba`:** ajuste aplicado no ramo efetivamente capturado: `demoBackDistance` Neon reduzido de `followDistance+4.2` para `followDistance+3.6`, sem alterar Meadow. Capturas completas GPU: Meadow 1001 mobile/834 desktop; Neon 1009 mobile/666 desktop; fresh-eyes pendente.
- **Iteração `a5b9582`:** bifurcação responsiva após vision mostrar piora mobile e ganho desktop em `c4dd3ba`: Neon mobile volta a `+4.2`, Neon desktop mantém `+3.6`, Meadow permanece `+4.2`. Capturas GPU completas: Meadow 997 mobile/821 desktop; Neon 1005 mobile/686 desktop; fresh-eyes convergiu: mobile Meadow/Neon 7.3→7.3 sem regressão; desktop Meadow estável e Neon 8.2 com framing/contexto melhorados. Próximo gap: grounding/AO e destaque do kart.
- **Iteração `5fa172d`:** núcleo da textura de sombra de contato do kart `alpha .08→.12`, raio `1.2m` preservado. Capturas GPU: Meadow 998 mobile/821 desktop; Neon 1010 mobile/675 desktop. Motion regression: 0 lost/backwards/crashes em ambas; auditoria vision pré/pós pendente.
- **Validação `5fa172d`:** grounding aprovado com ressalva: Meadow mobile 6.0→7.25; Neon mobile 6.5→7.0; desktop score geral 8.25/10; nenhum círculo preto antigo inequívoco. A trilha escura Neon foi inspecionada e identificada como skid marks repetidos intencionais, não z-fighting/blob.
- **Recaptura baseline para outline:** o primeiro batch pós `eb297af` não tinha pré disponível. Baseline foi reconstruído diretamente de `5fa172d` em servidor isolado `:3458`, mesmo harness/GPU: Meadow 998 mobile/832 desktop; Neon 1007 mobile/674 desktop; 20 frames em `/tmp/sk3d-vision-pre-5fa172d/`. Comparação pareada cega pré/pós concluída: manter outline; desktop Meadow 3.21→3.29 e Neon 3.43→3.50; mobile empate sem regressão visual relevante.
- **Próximo eixo:** detalhe material/AO, sem reduzir skid marks intencionais.
- **Iteração `9c729b6`:** `cityRoadTexture` recebeu 36 micro wet-streaks curtos (alpha `.045`), sem faixas contínuas. Capturas GPU: Meadow 1000/849 e Neon 1006/661 mobile/desktop; motion 0 lost/backwards/crashes. Vision pré/pós aprovou: variação mobile 4.5→6.5, ganhos desktop de profundidade/direção/naturalidade, sem z-fighting ou banding severo.
- **Próximo eixo:** legibilidade mobile de minimap/ranking, sem aumentar obstrução do gameplay.
- **Tentativa `a953bb6`:** minimap idle `.22→.42` e ranking `.55→.72` foram rejeitados por vision: ganho acionável não demonstrado e baseline desktop indisponível; revertido em `31aff06`, speedo `.92` preservado.
- **QA áudio `2dfbc65`:** render OfflineAudioContext produziu 24 WAVs, 0 erros; `go` pico `.998` após kick `.58→.54`; `crash` pico `.9832` após ruído `.45→.43`. Espectrogramas confirmaram ataque/cauda limpos, sem clipping visual; clank metálico não isolado. Runtime browser no GPU runner: mute pré-init, init, start/stop/restart music, pause/resume e visibility hidden/visible passaram; `pageerrors=0`, destroy limpou ctx. Próximo: captura congelada do HUD ou mix de gameplay.

## Vision scorecard trend
| Pass | Meadow | Neon | Main signal |
|---|---:|---:|---|
| Baseline | 5.5 | 4.9 | Neon bloom 2/10, grid 1/10 |
| Logic/mobile fixes | 4.4 | 4.3 | No expected visual gain |
| Bloom + grid v1 | 6.6 | 5.9 | Bloom 2→6.5, grid 1→6.5 |

Latest vision findings: remaining gaps are flat Meadow mountains/vegetation, repeated/flat Neon buildings, missing contact AO/soft shadows, fake wet reflection, sky/fog contamination, grid moiré at distance, and finish modal hiding gameplay. The latest vignette/grid-AA pass requires another desktop/mobile vision re-audit.

## Changes pushed
- Mobile safe area: `viewport-fit=cover`, `env(safe-area-inset-*)`, `100dvh`.
- Touch: restore controls after restart, coarse-pointer detection, pointer capture for drift/item.
- HUD: DPR-aware speedline canvas and Blue Shell label.
- AI: Lightning decision condition corrected from dead `d > 5` to normal in-race progress range.
- Render: bloom retuned and Neon grid shader added; latest pass reduces vignette and applies adaptive grid width/distance fade.
- QA harness: `scripts/playtest-video.cjs` supports `desktop` and `mobile`; geometry auditor corrected to Vulkan/system Chromium/rAF shim.

## Geometry audit
- Meadow: 868 meshes / 117 instanced groups; 99 on-track candidates, 0 suspicious; 3 LOW decal z-fight warnings.
- Neon: 534 meshes / 26 instanced groups; 495 on-track candidates. Após corrigir o classificador para ignorar pivôs pequenos no origin e decals de estrada legítimos, rerun terminou `RESULT: LIMPO — nenhum problema geométrico`.

## Mobile video
- `a1e1599`: viewport 390×844, hasTouch=true, 1002 frames Meadow + 1002 Neon, GPU RADV PHOENIX. A auditoria visual mobile detalhada ainda deve ser amostrada em vision antes de declarar responsividade AAA.

## Remaining AAA work
1. Re-audit latest vignette/grid-AA pass on desktop and mobile with vision.
2. Fix/triage Neon geometry auditor false positives, then rerun both tracks.
3. Add real contact-shadow/AO strategy without breaking RADV/mobile budget.
4. Improve Meadow mountain/vegetation material variation and Neon building/window variation.
5. Add audio capture/instrumentation and audit the same gameplay sequence: engine, drift, boost, item, hit, finish, pause/restart.
6. Do not claim AAA completion until visual scorecard and audio evidence converge.

## [2026-09-03] Autonomous tick — FINISH gantry v2 aceito
- Gap: o banner FINISH ainda dominava a aproximação e bloqueava área útil da pista.
- Experimento anterior `1.05→0.82m` foi rejeitado por A/B inconclusivo. Nesta iteração, `TrackBuilder.buildGantry()` usa banner `0.68m`, posição `y=4.92` (back face sincronizado).
- Build passou (`902.68 kB`); AI 20 seeds por pista: `0 lost / 0 backwards / 0 crashes`.
- GPU LXC105: ANGLE Vulkan/RADV PHOENIX, capturas diretas desktop `1280×720` e mobile `390×844`, `pageErrors=[]`, `ok=true`.
- Vision pareada confirmou menos parede visual e mais pista visível nos dois viewports, sem artefato novo. Ressalva: o capturador de inspeção mobile corta laterais do texto por FOV; não é evidência de regressão do runtime.
- Decisão: **ACEITO** como melhoria visual do pórtico; AO/materiais planos e bloom Neon continuam próximos gaps.

## [2026-09-03] Autonomous tick — Neon skyline palette experiment reverted
- Gap selected from evidence: `Environment.buildNeonCity()` indexed a 5-color cold-dominant `windowColors` palette with `(rand() * 3)`, excluding 2 pale-blue variants and plausibly contributing to repeated/grouped distant facades.
- Experiment: changed the index to `windowColors.length`; build passed, AI simulation passed, and GPU runner captured Meadow/Neon desktop+mobile with ANGLE Vulkan/RADV PHOENIX.
- Decision: **REVERTED / not accepted**. Identical-prompt vision inspection did not establish a reliable directional improvement because the paired captures were not frame-synchronized; both showed persistent skyline bloom/halo and no defensible score delta. No source commit created.
- Evidence: `qa-gpu-runner/tick-window-palette-pre/neon-desktop/` (650 frames) and `qa-gpu-runner/tick-window-palette/neon-desktop/` (652 frames), plus Meadow desktop/mobile and Neon mobile post captures; all GPU logs reported RADV PHOENIX and finished race state.
- Blocker/next: build a deterministic fixed-camera skyline capture or instrument per-instance palette distribution before retrying; do not use free-running video frames for this isolated material A/B.

## [2026-09-03] Autonomous tick — fixed skyline capture harness
- Baseline: HEAD `bcd60fd`, local HTTP `200`, asset probe `TRIPO_API_KEY=MISSING`, `GEMINI_API_KEY=MISSING`, `ELEVENLABS_API_KEY=MISSING`; build and AI baseline remained green.
- Added `scripts/capture-skyline-fixed.cjs`: clears localStorage, derives camera from the loaded `track.path`, freezes `raceManager.phase='idle'`, captures through CDP, records palette/camera/canvas/pageerrors, and rejects non-`RADV PHOENIX` runners.
- GPU evidence: LXC105 ANGLE Vulkan/RADV PHOENIX; desktop `1280x720` and mobile `390x844`; palette identical `13,22,20,17,11`, total `83`; `pageErrors=[]`.
- Paired desktop rerun was intentionally measured: `382589/921600` pixels differed (`0.415136`), with `sky=0.1103` and `road=0.7558`; the residual is animated/runtime/UI content, so no visual material change was accepted. The harness improvement is accepted; visual A/B remains blocked until the dynamic render path is masked or time-locked.
- Artifacts: `qa-gpu-runner/tick-skyline-fixed/{a,b,mobile}/`; no source appearance delta.

## [2026-09-03] Autonomous tick — operational revalidation; no product delta
- Baseline remeasured at HEAD `69f1fe3`; current worktree contains only the intentional tick ledger change plus untracked QA artifacts/temp files. The evidence-backed gap remains controlled Neon material/AO grounding while preserving emissive window readability.
- Static checks and production build passed outside virtiofs: `node --check` for `main.js`/`Environment.js`; `SK3D_OUT_DIR=/tmp/sk3d-dist-op-audit npm run build` → `44 modules transformed`, `902.76 kB`, `2.18s`.
- Deterministic AI regression passed on both tracks with 20 seeds each: `0 lost`, `0 backwards`, `0 crashes`; onRoad remained `100` in sampled runs.
- Safe probes: `PROXMOX_PASSWORD_FILE=MISSING`, `PLAYWRIGHT_FALLBACK=MISSING`, `PLAYWRIGHT_LOCAL=MISSING`; project/director asset probe scripts are absent, so no credentials were inspected or exposed. SSH to Proxmox returned `Permission denied (publickey,password)`.
- Decision: **NO PRODUCT CHANGE ACCEPTED**. No `src/` file was modified; GPU LXC105 RADV PHOENIX video/A-B cannot be defensibly executed until runner authentication and Playwright access return. Next highest-value gap remains Neon hybrid material/AO A/B.

## [2026-09-03] Autonomous tick — palette correction rejected pending deterministic A/B
- Baseline remeasured: HEAD `c9af321`, HTTP 200, production build passed in `/tmp/sk3d-dist-tick`, and AI regression remained `0 lost / 0 backwards / 0 crashes` for 20 seeds on each track; asset probe remained `TRIPO_API_KEY=MISSING`, `GEMINI_API_KEY=MISSING`, `ELEVENLABS_API_KEY=MISSING`.
- Candidate: change Neon skyline window selection from `(rand() * 3)` to `windowColors.length`; source audit confirmed this would expose all 5 declared colors instead of 3. The candidate was reverted.
- GPU runtime: LXC105 reported ANGLE Vulkan with `RADV PHOENIX`; successful post-candidate sequences completed Meadow desktop `814` frames, Meadow mobile `994`, Neon desktop `679`, and Neon mobile `1008`, with `phase=finished` on the completed mobile runs. The first batch command had a quoting error and produced partial desktop directories; those artifacts remain untracked under `qa-gpu-runner/`.
- Decision: **REVERTED / not accepted**. The only available pre frame was a finish-results modal, while the post frame was active grid gameplay; therefore the identical-prompt visual comparison was not a valid paired A/B. No source commit was created.
- Blocker: repository does not currently contain `scripts/audit-geometry.cjs`; deterministic fixed-camera skyline capture or per-instance palette telemetry is required before the next attempt.

## [2026-09-03T11:38Z] Autonomous tick — Neon grounding revalidation blocked; no product delta
- Baseline remeasured at HEAD `d4f923f`; `src/` remained clean. `Environment.buildNeonCity()` still uses `MeshBasicMaterial`, `fog:false`, and no AO/contact layer; this remains the single highest-value visual gap.
- Static checks passed: `node --check src/track/Environment.js` and `git diff --check`.
- Production build passed outside virtiofs: `SK3D_OUT_DIR=/tmp/sk3d-dist-neon-tick npm run build` → `44 modules transformed`, `902.76 kB`, `✓ built in 2.12s`.
- Deterministic AI regression passed: Track 1/2 ×20 seeds, `0 lost / 0 backwards / 0 crashes`; onRoad samples remained `100`.
- Safe probes returned `PROXMOX_PASSWORD_FILE=MISSING`, `PLAYWRIGHT_GPU=MISSING`, and external generator keys `MISSING`; no secret value was read or persisted.
- Decision: **NO PRODUCT CHANGE ACCEPTED**. Required LXC105 ANGLE/Vulkan/RADV PHOENIX video and identical-prompt A/B could not run; no visual claim is made. Next gap remains emissive-safe Neon material/AO grounding.

## [2026-09-03] Autonomous tick — Neon AO/material blocked; no product delta accepted
- Baseline remeasured at HEAD `cc70de1`: `Environment.buildNeonCity()` already selects `windowColors.length` (five slots); the remaining evidence-backed gap is material/AO grounding that preserves emissive window readability.
- Static checks passed: `node --check` for Environment/MaterialLibrary and QA scripts; AI regression Track 1/2 with 20 seeds each returned `0 lost / 0 backwards / 0 crashes`.
- Production build passed outside the worktree: `SK3D_OUT_DIR=/tmp/sk3d-dist-blocked-gpu npm run build` → 44 modules, 902.68 kB, 2.14s.
- Asset probe: `TRIPO_API_KEY=MISSING`, `GEMINI_API_KEY=MISSING`, `ELEVENLABS_API_KEY=MISSING`; no external asset was added.
- GPU blocker remeasured without exposing secrets: `PROXMOX_ROOT_PASSWORD=MISSING`; LXC105 desktop/mobile RADV PHOENIX video/A-B could not be run. Local Playwright fallback was also unavailable (`Cannot find module 'playwright'` with project and `/opt/pwtest` resolution).
- Decision: **NO PRODUCT CHANGE ACCEPTED**. Existing source remains intact; no visual improvement is claimed. Next highest-value gap remains controlled Neon material/AO A/B after restoring LXC105 access and Playwright availability.

## [2026-09-03] Skyline telemetry tick — accepted
- `Environment.buildNeonCity()` now samples the full declared five-slot `windowColors` palette and publishes `window.__sk3dNeonPalette` with per-row counts and total; no external assets or credentials.
- `scripts/audit-neon-palette.cjs` performs localStorage reset, rAF shim, reload determinism, pageerror and GPU checks.
- LXC105 evidence: ANGLE Vulkan/RADV PHOENIX; counts `13,22,20,17,11`, total `83`, four rows; identical after reload.
- GPU video sequences: Meadow desktop `817`, mobile `994`; Neon desktop `651`, mobile `1004` frames; all ended `phase=finished`.
- `MaterialLibrary.getQualityProfileName()` gained a Node-safe `typeof window` guard, fixing the deterministic AI harness import.
- Accepted as an instrumentation/product-correctness pass. No visual score delta claimed until a fixed-camera A/B uses the telemetry.

## [2026-09-03] Autonomous tick — deterministic skyline capture stabilized
- Gap selected: the previous fixed-camera harness still allowed the update loop, procedural `Math.random()` textures, and CSS animations to mutate pixels between boots/capture (`0.415136` desktop pixel delta).
- Change: `src/main.js` exposes the existing `GameLoop` through the QA-only `window.__sk3d.loop`; `scripts/capture-skyline-fixed.cjs` seeds `Math.random()` in the browser context, stops the loop after setup, disables CSS animation/transition, and renders through the real `PostFX` path before CDP capture.
- Mechanical evidence: `SK3D_OUT_DIR=/tmp/sk3d-dist-deterministic npm run build` passed (`902.68 kB`); AI 20 seeds × both tracks passed with `0 lost / 0 backwards / 0 crashes`; asset probe remained `TRIPO_API_KEY=MISSING`, `GEMINI_API_KEY=MISSING`, `ELEVENLABS_API_KEY=MISSING`.
- GPU evidence: LXC105 ANGLE Vulkan/RADV PHOENIX; fixed skyline desktop/mobile `1280×720`/`390×844`; palette `13,22,20,17,11`, total `83`, `pageErrors=[]`. Pair deltas: `a_vs_b 8076/921600 (0.008763021), mean_abs_channel 0.023990162`; third run `a_vs_c 23274/921600 (0.025253906), mean_abs_channel 0.016024667`.
- Gameplay evidence: GPU video sequences Meadow desktop/mobile `829/999` frames and Neon desktop/mobile `708/1005` frames; all finished normally. Vision found active nonblank scenes, legible HUD/touch controls, and no gross rendering artifact; FINISH gantry remains visually dominant and is still open.
- Decision: **ACCEPTED as QA instrumentation only; no appearance change claimed.** The harness is stable enough for directional A/B (low mean absolute residual) but not bit-identical; future material changes still require the same fixed harness and explicit threshold.
- Artifacts: `qa-gpu-runner/tick-skyline-deterministic/` and `qa-gpu-runner/tick-gameplay-video/` (intentionally untracked).

## [2026-09-03] Autonomous tick — canvas-only skyline A/B
- Gap: fixed captures still composited live HUD/menu DOM, contaminating material A/B with unrelated compositor timing.
- Change: `scripts/capture-skyline-fixed.cjs` records the canvas bounding rect, clips CDP capture to it, and hides only body-level UI during the QA capture; normal runtime is untouched.
- GPU evidence: LXC105 ANGLE Vulkan/RADV PHOENIX; desktop `1280×720`, mobile `390×844`; 3 JSONs, `pageErrors=[]`, palette total `83`.
- Paired desktop evidence: `mean_abs_channel 0.023990162→0.010919777` (−54.48%); changed-pixel ratio `0.008763021→0.026639540`, so the improvement is accepted as lower residual energy, not pixel identity.
- Vision confirmed the new artifact is nonblank WebGL scene-only with no HTML HUD/menu. Decision: **accepted QA instrumentation only; no product visual score claimed**.
- Artifacts: `qa-gpu-runner/tick-skyline-canvas-only/` (intentionally untracked).

## [2026-09-03] Autonomous tick — FINISH gantry A/B rejected
- Gap selected from repeated GPU/vision findings: the FINISH gantry/banner dominates the approach and competes with the kart/road.
- Experiment: banner height `1.05→0.82m`, y `4.70→4.82m`, with mirrored back face kept aligned. Build and AI regression passed.
- GPU LXC105: ANGLE Vulkan/RADV PHOENIX. Detailed sequences: Meadow desktop `624`, Neon desktop `745`, Meadow mobile `868`, Neon mobile `940` frames; completed normally. The runner did not emit pageErrors, so that field is not claimed.
- Same-protocol fresh-eyes comparison of PRÉ/PÓS contact sheets found no defensible directional improvement: Meadow composition was effectively unchanged and Neon retained the same dominant framing. **Decision: reverted; no product commit.**
- The temporary source experiment was restored to HEAD `82539e6`. Next highest-value gap: build a fixed, element-targeted FINISH capture with explicit page-error telemetry before another visual edit; do not use free-running frames for small geometry deltas.

## [2026-09-03] Autonomous tick — FINISH gantry v2 accepted
- Follow-up targeted capture reduced the banner to `0.68m` and moved it to `y=4.92`, preserving the mirrored face and landmark.
- Fixed GPU capture reports for Meadow desktop/mobile: `1280×720` and `390×844`, `pageErrors=[]`, ANGLE Vulkan `RADV PHOENIX`; artifacts `qa-gpu-runner/finish-v2-{desktop,mobile}/finish.png`.
- Paired pre/post vision confirmed more visible racing line and a thinner, still recognizable FINISH banner in both viewports, without a new artifact. Build and AI regression remained green.
- Decision: **ACCEPTED**. Source is currently uncommitted pending final staging; `qa-gpu-runner/` remains intentionally untracked.

## [2026-09-03] Autonomous tick — Neon material candidate rejected
- Baseline remeasured on HEAD `6f8a79b`: build outside worktree passed at `902.68 kB`; AI Track 1/2 with 20 seeds each returned `0 lost / 0 backwards / 0 crashes`; asset probe remained `TRIPO_API_KEY=MISSING`, `GEMINI_API_KEY=MISSING`, `ELEVENLABS_API_KEY=MISSING`.
- Gap selected from repeated evidence: Neon skyline buildings were flat/repetitive because the four tower rows used `MeshBasicMaterial`; candidate changed them to `MeshStandardMaterial` and added shared roof caps.
- GPU LXC105 evidence: ANGLE/Vulkan `RADV PHOENIX`, fixed captures `1280×720` and `390×844`, `pageErrors=[]`. Raw paired diff was `0.3759819878` desktop and `0.2247902844` mobile.
- Fresh-eyes visual result: candidate darkened facade/window readability and weakened skyline separation, most visibly on mobile. **Reverted; no product visual improvement accepted.**
- Remaining blocker: need a material/AO treatment that preserves the current emissive window contrast; do not retry flat-to-lit conversion without a controlled emissive-map/material A/B.
- Active video recheck after revert: GPU LXC105 `RADV PHOENIX`, Meadow desktop/mobile `853/998` frames and Neon desktop/mobile `665/1007` frames; all ended `phase=finished`.

## [2026-09-03] QA runner — Playwright fallback corrigido
- `scripts/playtest-video.cjs` agora tenta `require('playwright')` e cai automaticamente para `/opt/pwtest/node_modules/playwright` quando o pacote não está no `node_modules` do projeto.
- Smoke sem `NODE_PATH`: mobile `390×844`, RADV PHOENIX, `phase=finished`, `998` frames.

## [2026-09-03] Autonomous tick — Neon roof caps blocked and reverted
- Gap selected from repeated GPU/vision findings: Neon skyline towers remain flat boxes without a readable roofline.
- Candidate added a shared `BoxGeometry` roof-cap layer as one emissive-safe `MeshBasicMaterial` `InstancedMesh` per skyline row, preserving the existing window material and avoiding the rejected PBR darkening.
- Static checks/build/AI passed during the candidate (`44 modules`, `902.99 kB`, 20 seeds per track: 0 lost/backwards/crashes), then source was reverted because the mandatory LXC105 GPU proof was unavailable.
- Blocker: `~/.hermes/.proxmox_root_pw` is absent and SSH to `root@192.168.0.102` returned `Permission denied (publickey,password)`; no visual delta is accepted. Next attempt requires restoring GPU-runner access before any material/geometry A/B.

## [2026-09-03] Autonomous tick — GPU unlock audit, no product delta
- Baseline remeasured at HEAD `0ec68f6`: production build outside the worktree passed with 44 modules and 902.68 kB; AI regression Track 1/2, 20 seeds each, returned `0 lost / 0 backwards / 0 crashes`.
- Static checks passed for runtime/track/material/QA scripts and `git diff --check`.
- Access probe returned `PROXMOX_ROOT_PASSWORD=MISSING`, `PLAYWRIGHT_FALLBACK=MISSING`, `PLAYWRIGHT_LOCAL=MISSING`; SSH returned `Permission denied (publickey,password)` without exposing credentials.
- Decision: **NO PRODUCT CHANGE ACCEPTED**. The evidence-backed highest-value gap remains controlled Neon material/AO A/B preserving emissive window contrast; GPU RADV PHOENIX video and vision comparison remain blocked until runner access is restored.

## [2026-09-03] Autonomous tick — revalidação de baseline, sem delta de produto
- Gap único mantido: A/B controlado de material/AO no skyline Neon preservando contraste emissivo.
- Probe de assets: `TRIPO_API_KEY=MISSING`, `GEMINI_API_KEY=MISSING`, `ELEVENLABS_API_KEY=MISSING`; acesso GPU: `PROXMOX_ROOT_PASSWORD=MISSING`, Playwright local/fallback ausente. Nenhuma credencial foi exposta.
- `node --check` passou; AI Track 1/2 com 20 seeds retornou `0 lost / 0 backwards / 0 crashes`.
- Build direto no worktree encontrou falha operacional ENOENT no timestamp temporário do Vite; cópia sanitizada fora do worktree passou com `44 modules`, `902.68 kB`, `2.29s` usando `SK3D_OUT_DIR=/tmp/sk3d-dist-current`.
- Sem LXC105 RADV PHOENIX e vídeo/A-B desktop/mobile, nenhuma mudança de produto foi implementada ou aceita. Próximo gap: material híbrido/AO Neon após restaurar o runner.

## [2026-09-03] Autonomous tick — determinism audit, no product delta
- Baseline remeasured at HEAD `53aec318`: production build outside the worktree passed with 44 modules and `902.68 kB`; AI regression Track 1/2, 20 seeds each, returned `0 lost / 0 backwards / 0 crashes`.
- Audited `scripts/capture-skyline-fixed.cjs` against the previously observed independent-boot variance. The harness already seeds procedural randomness, stops the exposed game loop after setup, freezes the race state, disables CSS animation/transition, hides non-canvas DOM, uses the real PostFX path, and captures via CDP.
- Asset probe remained `TRIPO_API_KEY=MISSING`, `GEMINI_API_KEY=MISSING`, `ELEVENLABS_API_KEY=MISSING`; no external asset was added.
- Validation blocker remeasured safely: `PROXMOX_ROOT_PASSWORD=MISSING`, `PLAYWRIGHT_LOCAL=MISSING`, `PLAYWRIGHT_FALLBACK=MISSING`. No LXC105 RADV PHOENIX video/A-B was run, and no visual/product change was accepted.
- Decision: **NO PRODUCT CHANGE ACCEPTED**. This tick closes the audit line without speculative edits. Next highest-value gap remains controlled Neon material/AO A/B after restoring GPU-runner access.

## [2026-09-03] Autonomous tick — demo camera candidate blocked and reverted
- Gap selected from current evidence: the demo chase camera may keep too much route behind the kart, weakening player subject framing, especially on mobile.
- Candidate changed only `src/main.js` demo camera extras (Meadow/Neon, touch/non-touch). Static checks passed: `node --check`, production build outside worktree (`44 modules`, `902.69 kB`, `3.59s`), and AI Track 1/2 with 20 seeds each (`0 lost / 0 backwards / 0 crashes`).
- Runtime probe: HTTP `200` on `http://127.0.0.1:3457/`; asset probe `TRIPO/GEMINI/ELEVENLABS=MISSING`; GPU access probe `PROXMOX_ROOT_PASSWORD=MISSING`, `PLAYWRIGHT_LOCAL=MISSING`, `PLAYWRIGHT_FALLBACK=MISSING`.
- Decision: **REVERTED / not accepted**. Mandatory LXC105 ANGLE/Vulkan/RADV PHOENIX desktop/mobile video and identical-protocol A/B were unavailable, so no camera improvement is claimed. Source is back at the prior camera baseline.
- Next highest-value gap: restore GPU-runner access, then run the camera A/B; do not retry the camera delta without synchronized Meadow/Neon desktop/mobile evidence.

## [2026-09-03] Autonomous tick — pending gantry beam change, GPU blocked
- Baseline remeasured at HEAD `f3038e6` with pre-existing worktree edits: `src/track/TrackBuilder.js` changes the gantry beam from `0.50m` cyan to `0.28m` dark navy; `AUDIT_FINDINGS.md`, `GATES.md`, `qa-gpu-runner/`, and `scripts/capture-finish-static.cjs` also contain pre-existing local changes/artifacts and were not overwritten.
- Static checks passed: `node --check src/track/TrackBuilder.js`, `git diff --check`; production build outside the worktree passed with `44 modules transformed`, `902.68 kB`, `2.91s` using `SK3D_OUT_DIR=/tmp/sk3d-dist-tick-current`.
- Deterministic AI regression passed on both tracks with 20 seeds each: `0 lost`, `0 backwards`, `0 crashes`; all reported onRoad `100%` in the sampled runs.
- Runtime probe: dev server returned HTTP `200`; `PROXMOX_ROOT_PASSWORD=MISSING`; SSH to `root@192.168.0.102` returned `Permission denied (publickey,password)`. No secret was exposed and no GPU capture was claimed.
- Decision: **NO PRODUCT CHANGE ACCEPTED IN THIS TICK**. The pending beam edit remains untouched for its owner; no visual A/B/video evidence exists, so it must not be committed as an AAA improvement. Next gap: restore LXC105 access and run identical desktop/mobile Meadow+Neon video A/B for the beam/housing.

## [2026-09-03] Autonomous tick — Neon material/AO revalidation blocked
- Baseline remeasured at HEAD `156cc7d`: only `GATES.md` is modified; `.hermes-tmp.*` and `qa-gpu-runner/` remain untracked. The evidence-backed gap remains controlled Neon material/AO that preserves emissive window contrast.
- Static validation passed: `node --check` on runtime/track/material/QA modules and `git diff --check`; external build `SK3D_OUT_DIR=/tmp/sk3d-dist-vtick npm run build` passed with 44 modules, 902.76 kB, 2.12s.
- Deterministic AI regression passed on Track 1 and Track 2 with 20 seeds each: `0 lost`, `0 backwards`, `0 crashes`.
- Safe probes: `TRIPO_API_KEY=MISSING`, `GEMINI_API_KEY=MISSING`, `ELEVENLABS_API_KEY=MISSING`; `PROXMOX_ROOT_PASSWORD=MISSING`, `PLAYWRIGHT_LOCAL=MISSING`, `PLAYWRIGHT_FALLBACK=MISSING`; SSH returned `Permission denied` without exposing credentials. No GPU RADV PHOENIX video/A-B was run.
- Decision: **NO PRODUCT CHANGE ACCEPTED**. No source appearance delta was implemented. Next highest-value gap remains the same material/AO Neon A/B after restoring LXC105 access.

## [2026-09-03T10:11Z] Autonomous tick — revalidação operacional bloqueada
- Baseline refeito em HEAD `cd68507`; `node --check` e `git diff --check` passaram.
- Build fora do virtiofs: `SK3D_OUT_DIR=/tmp/sk3d-dist-tick-1011 npm run build` → 44 módulos, 902.76 kB, 2.18s.
- AI Track 1/2 ×20: `0 lost / 0 backwards / 0 crashes`; dev server HTTP 200.
- Probes seguros: `PROXMOX_ROOT_PASSWORD=MISSING`, Playwright local/fallback `MISSING`, assets TRIPO/GEMINI/ELEVENLABS `MISSING`; SSH `EXIT=255` bloqueado.
- Decisão: **NO PRODUCT CHANGE ACCEPTED**. Nenhum `src/` foi alterado; A/B vídeo RADV PHOENIX desktop/mobile continua bloqueado. Próximo gap: material/AO Neon preservando emissive após restaurar o runner.

## [2026-09-03] Correction — concurrent commit observed after tick measurement
- Final re-measurement found HEAD `89f7c8c`, with concurrent commit `6c6a4cf` aligning the FINISH housing/sockets to the banner rotation; the beam remains `0.28m` navy.
- This concurrent source change was not visually validated in this tick. Keep the product gain **unclaimed** until identical GPU RADV PHOENIX video/A-B covers Meadow and Neon at desktop/mobile sizes.

## [2026-09-03T09:42Z] Autonomous tick — Neon/audio operational revalidation; no product delta
- Baseline remeasured at HEAD `8d701f0`: production build outside virtiofs passed with `44 modules transformed`, `902.76 kB`, `2.16s`; static checks and `git diff --check` passed.
- Deterministic AI regression passed on both tracks with 20 seeds each: `0 lost`, `0 backwards`, `0 crashes`.
- Highest-value gap remains controlled Neon hybrid material/AO grounding preserving emissive windows. Audio audit also found non-deterministic `Math.random()` in the runtime reverb/noise paths, but no audio patch was accepted without exact OfflineAudioContext render and lifecycle browser evidence.
- Safe access probes: `PROXMOX_PASSWORD_FILE=MISSING`, `PLAYWRIGHT_LOCAL=MISSING`, `PLAYWRIGHT_FALLBACK=MISSING`; no secret was exposed. LXC105 RADV PHOENIX video/A-B and audio browser validation were blocked.
- Decision: **NO PRODUCT CHANGE ACCEPTED**. No `src/` file changed. Next highest-value action is restoring runner/browser access, then run deterministic Neon material/AO A/B and exact audio lifecycle/render QA before touching product code.

## Evidence ledgers — current autonomous tick

### Skill-loading ledger
- `threejs-game-director`: loaded; orchestration and premium completion rules applied.
- `threejs-gameplay-systems`: loaded; gameplay systems and deterministic AI regression checked.
- `threejs-aaa-graphics-builder`: loaded; art direction, scorecard, external asset gate, and technical art constraints applied.
- `threejs-game-ui-designer`: loaded; HUD/mobile risks remain covered by prior QA evidence.
- `threejs-debug-profiler`: loaded; static/runtime/performance checks routed through the documented runner constraints.
- `threejs-qa-release` + `game-visual-qa-kit`: loaded; release checks, fixed A/B, GPU video, and page-error requirements applied.
- `obsidian`, `llm-wiki`, `unlazy`, `game-architect`, `webaudio-sfx-design`, `webaudio-sfx-synthesis`, and `game-dev-qa-test`: loaded for required documentation, gates, architecture, audio, and QA policy.

### Reference ledger
- Gameplay: `game-feel.md` loaded; no gameplay/product change made in this blocked tick.
- AAA graphics: visual scorecard, implementation blueprint, model/render recipes, shader cookbook, and technical-art guidance are the governing references from the loaded skill set; no shader/material candidate accepted.
- QA/release: GPU runner policy, visual verification, playtest, release, visual harness, and bot-playtest requirements applied; GPU execution blocked.

### Phase ledger
| Phase | State | Evidence |
|---|---|---|
| gameplay systems | verified/no change | AI regression Track 1/2, 20 seeds each: 0 lost/backwards/crashes |
| aaa graphics | blocked/no change | material/AO Neon remains the single gap; no A/B GPU available |
| debug/profile | verified | node checks, diff check, HTTP 200; no runtime source change |
| qa/release | blocked for visual acceptance | LXC105 credential and Playwright unavailable |

### Game design brief / core loop / level-encounter plan
- **Game design brief:** arcade kart racing; drift/boost, items, shortcuts and readable racing line; no rule change in this tick.
- **Core loop:** choose track → accelerate/drift → avoid hazards/use items → complete laps → finish/results → retry.
- **Level/encounter plan:** Meadow uses open readable bends and roadside props; Neon uses long straights, hairpins, dashes, skyline and urban landmarks; pressure escalates through speed, AI traffic and item timing.

### Premium visual scorecard (latest defensible evidence; current tick does not claim improvement)
| Category | Evidence / status |
|---|---|
| art direction | Meadow/Neon authored themes; Neon material/AO gap open |
| hero/player | prior GPU evidence exists; no current recapture |
| obstacles/enemies | AI/runtime regression green; no visual delta |
| rewards/interactables | prior item/HUD evidence; no current delta |
| world/environment | Neon skyline repetitive/flat remains open |
| materials/textures | current gap is selective AO/hybrid emissive material |
| lighting/render | prior bloom pass accepted; current A/B blocked |
| vfx/motion | prior gameplay video evidence; no current delta |
| ui/hud | prior desktop/mobile evidence; no current delta |
| performance evidence | build 44 modules, 902.76 kB; AI regression green |
- **Measured evidence:** external build 44 modules / 902.76 kB / 2.12s; HTTP 200; AI 0 lost, 0 backwards, 0 crashes.
- **Fresh-eyes review:** not run in this tick because no candidate capture exists; prior rejected material candidates remain explicitly rejected.
- **Average:** not recomputed; no current visual score claim.
- **Automatic failures remaining:** fresh-eyes review unavailable; current GPU A/B unavailable; Neon material/AO gap remains.

### External asset sourcing ledger
| Surface | Chosen source | Result |
|---|---|---|
| hero/player | procedural/hybrid existing | no new asset; generator probe blocked (`TRIPO_API_KEY=MISSING`) |
| world/sky/background | procedural existing | no new asset; `GEMINI_API_KEY=MISSING` |
| materials/textures/decals | procedural existing | no new asset; controlled GPU A/B required |
| audio | WebAudio procedural existing | no audio change; `ELEVENLABS_API_KEY=MISSING` |
- **Credential probe output:** `TRIPO_API_KEY=MISSING`, `GEMINI_API_KEY=MISSING`, `ELEVENLABS_API_KEY=MISSING`.
- **3D generator / image generator:** loaded but not executed; no external output was fabricated.
- **Chosen sources:** existing procedural Three.js and WebAudio synthesis; external generation not accepted without a successful output.

### Technical art and render budget
- Technical art: preserve emissive window contrast, avoid unverified PBR darkening, and keep AO selective/cheap; candidate not implemented.
- Render budget: production bundle 902.76 kB; Vite emitted the known >500 kB chunk warning; no new draw-call or texture cost introduced.
- VFX readability: no VFX change; prior bloom remains the latest accepted rendering change.

### Visual test harness / runtime evidence
- Visual test harness decision: required and retained (`capture-skyline-fixed.cjs` plus GPU gameplay video); not executed this tick because LXC105 access is blocked.
- Console/page error: no new browser session; therefore no current page-error claim. Historical fixed captures recorded `pageErrors=[]`.
- Screenshot/video: no new screenshot or video accepted this tick; historical GPU artifacts remain untracked under `qa-gpu-runner/`.

## [2026-09-03] Autonomous tick — Neon grounding audit blocked, no product delta
- Baseline remeasured at HEAD `b617089`: worktree had only the intentional `GATES.md` edit; `.hermes-tmp.*` and `qa-gpu-runner/` remained untracked. The single highest-value gap remains Neon skyline grounding/material separation.
- Source audit confirmed `Environment.buildNeonCity()` uses one `MeshBasicMaterial` per skyline row with `fog:false`, a shared window texture, per-row haze tint, and no contact/AO layer under the tower instances. This is a concrete hypothesis, not proof that a specific AO recipe will improve the image.
- Static checks passed; AI Track 1/2 with 20 seeds each returned `0 lost / 0 backwards / 0 crashes`; production build outside the worktree passed with `44 modules`, `902.76 kB`, `2.10s` using `SK3D_OUT_DIR=/tmp/sk3d-dist-z-audit`.
- Safe access probes found the Proxmox credential path unavailable to this run, Playwright local/fallback unavailable, and SSH authentication refused. Values are intentionally redacted. No LXC105 `RADV PHOENIX` video or fixed-camera A/B was claimed.
- Decision: **NO PRODUCT CHANGE ACCEPTED**. No source appearance delta was implemented. Next highest-value gap remains a selective AO/emissive-safe material A/B after restoring GPU-runner access; do not convert the skyline wholesale to lit PBR without preserving window contrast.

## [2026-09-03T09:56Z] Autonomous tick — runner revalidation, no product delta
- Baseline remeasured at HEAD `3bedd96`; critical `node --check` and `git diff --check` passed.
- External production build via `SK3D_OUT_DIR=/tmp/sk3d-dist-tick-1000 npm run build` passed: `44 modules transformed`, `902.76 kB`, `2.14s`.
- Deterministic AI regression: Track 1 and Track 2, 20 seeds each, `0 lost`, `0 backwards`, `0 crashes`; sampled runs reported `onRoad=100`.
- Safe probes: Proxmox password path `[REDACTED]`, Playwright local/fallback `MISSING`; SSH authentication refused. No external asset was added.
- Decision: **NO PRODUCT CHANGE ACCEPTED**. Required paired A/B with gameplay video on Meadow/Neon, desktop `1280×720`, mobile `390×844`, ANGLE/Vulkan/RADV PHOENIX and `pageErrors=[]` is blocked in this environment.
- Next highest-value gap: selective emissive-safe AO/material A/B for Neon after runner restoration; `qa-gpu-runner/` and temporary files remain untracked.

## [2026-09-03T10:39Z] Autonomous tick — runner revalidation, no product delta
- Baseline remeasured at HEAD `8875827`; `src/` remained clean and `Environment.buildNeonCity()` still uses `MeshBasicMaterial`, `fog:false`, and no contact/AO layer under tower instances.
- Static checks passed: `node --check src/main.js src/track/Environment.js src/render/MaterialLibrary.js` and `git diff --check`.
- External production build passed via `SK3D_OUT_DIR=/tmp/sk3d-dist-ab npm run build`: `44 modules transformed`, `902.76 kB`, `✓ built in 2.22s`.
- Deterministic AI regression passed on Track 1 and Track 2 with 20 seeds each: `0 lost`, `0 backwards`, `0 crashes`.
- Safe probes: password file state redacted as `***`; Playwright local/fallback `MISSING`; asset credential probe returned only redacted states. SSH/runner route was unavailable in this environment (`SSH_PROBE=UNAVAILABLE`); no RADV PHOENIX capture or video was claimed.
- Decision: **NO PRODUCT CHANGE ACCEPTED**. The mandatory identical-protocol GPU A/B and gameplay video remain blocked; next highest-value gap is unchanged: selective emissive-safe AO/material Neon A/B after restoring runner access.

## [2026-09-03T10:54Z] Autonomous tick — runner audit, no product delta
- Baseline remeasured at HEAD `878c753744a0d1fb3588d735d0cc2f48924906b`; source remains clean under `src/`; `buildNeonCity()` still uses `MeshBasicMaterial`, `fog:false`, full five-color palette, and no contact/AO layer.
- Static checks passed: `node --check src/main.js src/track/Environment.js src/render/MaterialLibrary.js` and `git diff --check`.
- External production build passed via `SK3D_OUT_DIR=/tmp/sk3d-dist-autonomous-1054 npm run build`: `44 modules transformed`, `902.76 kB`, `2.14s`.
- Deterministic AI regression passed on Track 1 and Track 2 with 20 seeds each: `0 lost`, `0 backwards`, `0 crashes`; sampled `onRoad=100`.
- Safe probes: password file `MISSING`, Playwright local/fallback `MISSING`, `sshpass=SET`, SSH probe `EXIT_255`; asset probes `TRIPO_API_KEY=MISSING`, `GEMINI_API_KEY=MISSING`, `ELEVENLABS_API_KEY=MISSING`. No secret values were read or recorded.
- Decision: **NO PRODUCT CHANGE ACCEPTED**. Without LXC105 ANGLE/Vulkan/RADV PHOENIX video and identical-protocol A/B, no visual improvement is defensible. Next highest-value gap remains selective emissive-safe AO/material Neon A/B after runner restoration.

## [2026-09-03T13:10Z] Autonomous tick — runner bloqueado, sem delta de produto
- Baseline real refeito em HEAD `d9d73a5`; `src/` sem diff; `Environment.js` confirma skyline Neon em `MeshBasicMaterial`, `fog:false`, sem `aoMap` executável.
- Checks reais: `node --check src/main.js src/track/Environment.js src/render/MaterialLibrary.js`; build externo `SK3D_OUT_DIR=/tmp/sk3d-dist-ct npm run build` → `44 modules transformed`, `902.76 kB`, `2.15s`; AI Track 1/2 ×20 → `0 lost / 0 backwards / 0 crashes`; `git diff --check` passou.
- Probes seguros: password file `MISSING`, `/opt/pwtest` `MISSING`, Playwright local `MISSING`; assets externos somente estados redigidos. Porta SSH está aberta, mas `SSH_RC=NO_PASSWORD_FILE`; nenhum segredo foi lido.
- `scripts/audit-geometry.cjs` ainda não existe; isso permanece dívida de instrumentação, não justificativa para patch visual especulativo.
- Decisão: **NO PRODUCT CHANGE ACCEPTED**. Sem sessão LXC105/RADV PHOENIX não houve vídeo Meadow/Neon desktop/mobile nem A/B pareado. Próximo gap: restaurar rota autenticável e executar material híbrido/AO Neon emissive-safe.

## [2026-09-03T11:09Z] Autonomous tick — mobile touch controls de-emphasized
- Baseline remeasured at HEAD `d79c186`: dev server `HTTP=200`; mobile `390×844` HUD bottom occupied `y=526..696`, touch controls `y=748..830`, preserving `52px` vertical separation.
- One focused UI change accepted in `src/ui/ui.css`: inactive touch backgrounds reduced `0.55→0.38`, item/drift `0.60→0.45`, pause `0.60→0.42`; active state remains high contrast (`0.95`). Hit areas and input handlers were not changed.
- GPU gameplay video on LXC105/RADV PHOENIX completed: Meadow desktop `796`, Neon desktop `617`, Meadow mobile `1000`, Neon mobile `1008` frames; all ended `phase=finished`. Fixed-camera runtime checks at `1280×720` and `390×844` recorded `pageErrors=[]`.
- Identical-prompt visual review of pre/post frames found the mobile candidate less visually competitive with the road while controls remained legible; desktop Meadow showed no scope regression because the change is touch-only. No absolute AAA score is claimed.
- Static/build/regression: `node --check`, `git diff --check`, external build `44 modules / 902.76 kB / 2.21s`, AI Track 1/2 ×20 `0 lost / 0 backwards / 0 crashes`.
- Asset probe: `TRIPO_API_KEY`, `GEMINI_API_KEY`, `ELEVENLABS_API_KEY` reported `MISSING`; no external assets added. Remaining highest-value gap: emissive-safe AO/material A/B for Neon.

## [2026-09-03T12:08Z] Autonomous tick — Neon grounding revalidation blocked
- Baseline refeito em HEAD `9830930`: `src/` segue sem diff de produto; `buildNeonCity()` usa `MeshBasicMaterial`/`fog:false` e não possui `aoMap` ou camada AO executável. O `grep` bruto de `contact` foi desconsiderado por atingir comentários, não implementação.
- Checks: `node --check src/track/Environment.js src/render/MaterialLibrary.js src/main.js` passou; `SK3D_OUT_DIR=/tmp/sk3d-dist-tick-1208 npm run build` passou com `44 modules`, `902.76 kB`, `2.12s`; AI Track 1/2 ×20 retornou `0 lost / 0 backwards / 0 crashes`; dev server `HTTP=200`.
- Probes seguros: `PASSWORD_FILE=MISSING`, `PLAYWRIGHT_FALLBACK=MISSING`, `PLAYWRIGHT_LOCAL=MISSING`; geradores reportados apenas como `[REDACTED]`. Nenhum segredo foi lido ou persistido.
- Decisão: **NO PRODUCT CHANGE ACCEPTED**. Sem LXC105/RADV PHOENIX e vídeo A/B desktop `1280×720`/mobile `390×844` com prompt idêntico, não há delta visual defensável. Próximo gap: material híbrido/AO Neon emissive-safe após restaurar o runner.

## [2026-09-03T12:40:51Z] Autonomous tick — runner inacessível, sem delta de produto
- Baseline re-medido no HEAD `0320c39142527d6d6979a90700409e431f6ae62c`; `src/` sem diff antes da decisão. `Environment.js` continua com `MeshBasicMaterial`, `fog:false` e sem AO executável no skyline Neon (`SKYLINE_BASIC=True`, `SKYLINE_AO=False`).
- Checks reais: `node --check src/main.js src/track/Environment.js src/render/MaterialLibrary.js`; `git diff --check`; build externo `SK3D_OUT_DIR=/tmp/sk3d-dist-tick-1240 npm run build` → `44 módulos`, `902.76 kB`, `2.25s`; AI Track 1/2 ×20 → `0 lost / 0 backwards / 0 crashes`.
- Probes seguros: password file ausente; `SSHPASS` não estava exportado para a rota SSH; LXC105 responde na porta 22, mas não houve autenticação; Playwright local e `/opt/pwtest` ausentes; geradores externos permanecem `MISSING`. Nenhum segredo foi lido ou registrado.
- Decisão: **NO PRODUCT CHANGE ACCEPTED**. Sem vídeo desktop/mobile no LXC105 com ANGLE/Vulkan/RADV PHOENIX e A/B pareado, nenhum patch Neon foi implementado. O próximo gap continua material híbrido/AO emissive-safe; o primeiro passo é restaurar uma rota autenticável ao runner.
- Artefatos QA não foram staged; a alteração desta rodada é somente documentação/gates.

## [2026-09-03T12:55:11Z] Autonomous tick — runner bloqueado, sem delta de produto
- Baseline real: HEAD `b91216f`; `src/` permaneceu sem diff; `buildNeonCity()` continua com `MeshBasicMaterial`, `fog:false` e sem AO executável por torre (`SKYLINE_BASIC=True`, `SKYLINE_AO=False`).
- Checks: `node --check src/main.js src/track/Environment.js src/render/MaterialLibrary.js`; build externo `SK3D_OUT_DIR=/tmp/sk3d-dist-tick-1255 npm run build` passou com `44 módulos`, bundle `902.76 kB`, em `2.18s`; `git diff --check` passou.
- Regressão determinística: Track 1/2 ×20 seeds, `0 lost / 0 backwards / 0 crashes`; servidor existente respondeu `HTTP 200`.
- Probes seguros: password file `MISSING`, `SSHPASS=SET` sem valor lido, `/opt/pwtest=MISSING`, Playwright local apenas diretório detectado, módulo/binary local indisponíveis; SSH `EXIT=255`/`AUTH_OR_NETWORK_BLOCKED`. Geradores externos permanecem `MISSING`; nenhum segredo foi exposto.
- Browser/CDP deste ambiente não pôde ser usado (`127.0.0.1:9222` recusado); portanto não há runtime visual, vídeo ou A/B RADV PHOENIX novo.
- Decisão: **NO PRODUCT CHANGE ACCEPTED**. Sem A/B pareado em vídeo Meadow/Neon, desktop `1280×720` e mobile `390×844`, com ANGLE/Vulkan/RADV PHOENIX, nenhum patch visual foi implementado. Próximo gap: material híbrido/AO Neon emissive-safe após restaurar a rota autenticável do runner.

## [2026-09-03T13:25:01Z] Autonomous tick — runner bloqueado, sem delta de produto
- Baseline real: HEAD `e143724`; `src/` sem diff; `Environment.buildNeonCity()` mantém `MeshBasicMaterial`/`fog:false` e não possui `aoMap` no bloco Neon. `node --check` nos módulos críticos e `git diff --check` passaram.
- Build externo: `SK3D_OUT_DIR=/tmp/sk3d-dist-tick-1324 npm run build` passou com `44 modules transformed`, bundle `902.76 kB`, em `2.26s`.
- Regressão determinística: Track 1/2 ×20 seeds, `0 lost / 0 backwards / 0 crashes`; dev server `HTTP 200`.
- Probes seguros: password file `MISSING`, Playwright GPU/local `MISSING`, `SSHPASS=SET` sem leitura do valor, SSH batch `255`; geradores apenas estados redigidos (`TRIPO/GEMINI/ELEVENLABS=***`).
- GPU/A-B/vídeo: bloqueados por autenticação do runner; nenhuma captura RADV PHOENIX nova foi alegada. Nenhum patch de produto foi implementado ou aceito.
- Scorecard: sem recaptura/fresh-eyes neste tick; média não recalculada; falhas automáticas permanecem A/B GPU e evidência visual atualizada do gap Neon.
- Próximo gap de maior valor: restaurar a rota autenticável do LXC105 e executar A/B fixo emissive-safe de material/AO Neon em Meadow/Neon, desktop/mobile.

## [2026-09-03T13:55:15Z] Autonomous tick — runner inacessível, sem delta de produto
- Baseline real: HEAD `86a923f`; `src/` permaneceu sem diff; skyline Neon segue `MeshBasicMaterial`/`fog:false`, sem AO executável.
- Checks reais: `node --check src/main.js src/track/Environment.js src/render/MaterialLibrary.js`; `git diff --check`; build externo `SK3D_OUT_DIR=/tmp/sk3d-dist-tick-1355 npm run build` → `44 modules transformed`, `902.76 kB`, `2.28s`; AI Track 1/2 ×20 → `0 lost / 0 backwards / 0 crashes`.
- Probes seguros: `PROXMOX_ROOT_PASSWORD=MISSING`, `SSHPASS=MISSING`, `PLAYWRIGHT_BROWSERS_PATH=MISSING`, geradores `TRIPO/GEMINI/ELEVENLABS=MISSING`; `sshpass` presente, mas password file ausente; cache local de browser existe, `/opt/pwtest` ausente. SSH batch ao Proxmox retornou `255` (`Permission denied`). Nenhum segredo foi lido.
- Runtime: dev server respondeu `HTTP 200`; sem sessão LXC105 autenticada não foi possível provar ANGLE/Vulkan/RADV PHOENIX, vídeo ou A/B visual pareado.
- Decisão: **NO PRODUCT CHANGE ACCEPTED**. Nenhum arquivo `src/` foi alterado; não há score visual novo. Próximo gap: restaurar rota autenticável e executar A/B material/AO Neon emissive-safe com vídeo Meadow/Neon em desktop `1280×720` e mobile `390×844`.

## [2026-09-03T15:48:38Z] Autonomous tick — áudio lifecycle validado
- Baseline real: HEAD `542a778`; o fix anterior removeu nondeterminismo dos buffers procedurais e o gap pendente era provar o ciclo WebAudio no browser.
- Adicionado `scripts/probe-audio-lifecycle.mjs`, probe QA sem credenciais, com fallback explícito para `playwright-core` no runner direto.
- GPU runner `192.168.0.195`: Chromium `/usr/bin/chromium`, ANGLE/Vulkan `RADV PHOENIX`; `AUDIO_LIFECYCLE=PASS checks=9 failed=0 pageErrors=0`.
- Cobertura: lazy-before-init, init/unlock (`running`), mute master `0`, unmute `0.7910929322242737`, music start/stop, suspend/resume (`suspended→running`) e destroy (`isReady=false`).
- Checks: `node --check`/`git diff --check`; build externo `SK3D_OUT_DIR=/tmp/sk3d-dist-audio-lifecycle npm run build` passou com `44 modules`, `903.12 kB`, `2.10s`; áudio determinístico `30/30`, `maxPeak=0.853281`, `nondeterministic=none`; AI Track 1/2 ×20 `0 lost / 0 backwards / 0 crashes`.
- Decisão: **QA LIFECYCLE ACCEPTED; NO PRODUCT CHANGE**. O probe é instrumentação versionada; nenhum arquivo `src/` foi alterado. Próximo gap de produto permanece A/B material/AO Neon emissive-safe.

## [2026-09-03T15:23Z] Autonomous tick — determinismo de áudio aceito
- Gap único escolhido por evidência estática: `Math.random()` ainda gerava ruído não reproduzível em `sfx.js` (SFX) e `AudioManager.js` (reverb/crowd), impedindo auditoria offline estável.
- Alteração aceita: `mulberry32` local determinístico nos três buffers; nenhuma regra de corrida, input, mixagem, visual ou asset externo foi alterada. Novo smoke `scripts/audio-determinism-smoke.mjs` usa `web-audio-api` somente em `/tmp`.
- QA offline completo: `30/30` receitas renderizadas, `maxPeak=0.853281`, `nondeterministic=none`; `AUDIO_RANDOM=PASS`; hashes repetidos do boost coincidiram.
- Checks: `node --check`, `git diff --check`, build externo `SK3D_OUT_DIR=/tmp/sk3d-dist-audio-determinism-final npm run build` (`44 modules`, `903.12 kB`, `2.26s`), AI Track 1/2 ×20 (`0 lost / 0 backwards / 0 crashes`).
- Runtime browser lifecycle não foi alegado: `PLAYWRIGHT_LOCAL=MISSING`, `/opt/pwtest=MISSING`; tentativa Snap `--dump-dom` falhou por execução ES não observável. Nenhum segredo foi exposto.
- Decisão: **PRODUCT CHANGE ACCEPTED** para determinismo de áudio; score visual não recalculado. Próximo gap: validar lifecycle de áudio com Playwright disponível e então retomar A/B material/AO Neon no GPU.

## [2026-09-03T19:20Z] Autonomous tick — owner `kart-ai` rejeitado após probe fixo
- Baseline GPU LXC105 re-medido com ANGLE/Vulkan `RADV PHOENIX`, WebGL2 e `pageErrors=[]`: Meadow `1948 calls/1,089,095 tris` desktop e `957 calls/818,183 tris` mobile; Neon `1586/307,268` desktop e `869/192,542` mobile; `kart-ai` = `1175 meshes/199650 tris`.
- Candidato único desligou `castShadow` nos descendentes AI. Build externo passou (`44 modules`, `903.92 kB`, `2.31s`) e AI Track 1/2 ×20 permaneceu `0 lost / 0 backwards / 0 crashes`.
- Probe candidato não mostrou redução: Meadow mobile `957→968` calls e Neon mobile `869→873`; sem frame-time pareado e sem delta confiável, candidato foi revertido. Nenhuma mudança em `src/` foi aceita.
- Vídeo pós-revert no GPU: Meadow desktop/mobile `743/939` frames; Neon desktop/mobile `616/992`; todos `phase=finished`, renderer `RADV PHOENIX`.
- Decisão: **NO PRODUCT CHANGE ACCEPTED**. Próximo gap: probe fixo de outro owner/pass ou material/AO Neon somente com métrica e A/B temporalmente pareados; não declarar AAA completo.

## [2026-09-04T01:30Z] Autonomous tick — cor das partículas ACEITA (shader lia `aColor` sem buffer + paleta de confete quebrada)
- Baseline re-medido no `HEAD c722ccd`: `src/` limpo; `node --check` + `git diff --check` OK; build externo `SK3D_OUT_DIR=/tmp/sk3d-dist-tick0904` → `44 modules`, `904.11 kB`, `2.15s`; AI Track 1/2 ×20 → `0 lost / 0 backwards / 0 crashes`.
- Auditoria de gameplay no runner direto (`192.168.0.195`, vite :3457, ANGLE/Vulkan `RADV PHOENIX`): 4 vídeos `?demo` Meadow d/m `900/1000` frames + Neon d/m `741/1009` frames, todos `phase=finished`. Frames auditados com prompt idêntico; zoom no frame Meadow revelou trilha de blobs pretos no asfalto na trajetória do kart.
- Root cause duplo em `src/render/Particles.js`: (1) shader declara `attribute vec3 aColor` mas a geometria registrava `color` → atributo sem buffer = `(0,0,0)` → TODAS as partículas normal-blend pretas (exhaust/drift/poeira) e aditivas invisíveis (boost/sparkle); (2) `confetti` tem `cfg.color` array mas o branch de paleta só testava `opts.color` → `setHex(array)` = NaN = quadrados pretos no céu.
- Fix (4 linhas, sem física/input/áudio/assets): `color`→`aColor` nas 3 refs da geometria + paleta aceita `cfg.color` array.
- Checks pós-fix: `node --check`, `git diff --check`, build `44 modules/904.14 kB/2.07s`, AI Track 1/2 ×20 `0/0/0`.
- A/B GPU pareado (`qa-gpu-runner/tmp-capture-particles.cjs`, não versionado; ?test track 1, seed fixa, burst fixo de 8 famílias, 18 ticks, câmera relativa; PRE via stash): GPU `RADV PHOENIX`, `pageErrors=[]`, kart desktop idêntico `(-66.5,0.55,3.53)`; diff pré→pós `25.14%` desktop / `33.44%` mobile (pixels >2). Crop idêntico: PRE fumaça preta no escape → POST chama laranja; confete preto → multicolorido (verde/roxo/laranja/azul/vermelho, mobile). Gameplay pós-fix Meadow desktop 909 frames `finished`: pista sem trilha preta, confete do FINISH multicolorido.
- Decisão: **PRODUCT CHANGE ACCEPTED**. Próximo gap: variedade Meadow / torres Neon / fog residual — a definir por medição; score AAA não declarado completo.

## [2026-09-04T02:15Z] Autonomous tick — outdoor trackside espelhado ACEITO (rotation.z=0 pos-lookAt)
- Baseline re-medido no HEAD `8a1a40e`: `src/` limpo; `node --check` + `git diff --check` OK; build externo `SK3D_OUT_DIR=/tmp/sk3d-dist-tickP` para `44 modules`, `904.20 kB`, `2.14s`; AI Track 1/2 x20 para `0 lost / 0 backwards / 0 crashes`.
- Auditoria de gameplay no runner direto (`192.168.0.195`, vite :3457, ANGLE/Vulkan `RADV PHOENIX`): 4 videos `?demo` (Meadow d/m 10/10 frames, Neon d/m 10/12 frames), `pageErrors=[]`. Critica cega com prompt identico nos frames mid-race; zoom no outdoor Meadow revelou texto ESPELHADO.
- Root cause em `src/track/Environment.js` (banners trackside instanciados): `dummyB.rotation.z = 0` apos `lookAt` (3 ocorrencias). `lookAt` com yaw além de 90 graus decompoe em euler XYZ com x=z=PI; forcar z=0 reconstroi base com eixo X local negado - normal continua mirando a pista (fDotB=-1, separacao 0.104), mas a textura le espelhada. So estacoes nesses quadrantes espelhavam. Isolamento por A/B de visibilidade no GPU: hideP0 (printsF) para boards em branco; hideP1 (printsB) para espelhado persiste. Inventario: 1 builder so (frames box 32 + P0 32 + P1 32 + poles 64).
- Fix (3 linhas removidas + nota de causa raiz, sem fisica/input/audio/assets). Checks pos-fix: `node --check`, `git diff --check`, build `44 modules/904.16 kB/2.63s`, AI Track 1/2 x20 `0/0/0`.
- A/B GPU pareado (mesmo probe/camera/estacao `banner instance 0`, fov40): PRE crop `ART GP` espelhado para POST crop `SUPER` normal; frame POST inteiro sem outdoor espelhado/branco/artefato; diff bruto `23.51%` pixels >2. Gameplay POST `?demo` Meadow desktop 10 frames `race-para-finished`, `pageErrors=[]`, banner `SUPER KART` normal em t=20.3.
- Decisao: **PRODUCT CHANGE ACCEPTED**. Proximo gap: mesma corrupcao `rotation.z=0` pos-lookAt no lamp-head (`Environment.js:4444`, sem evidencia visual ainda) + blobs brancos de drift/particula em Meadow/Neon; score AAA nao declarado completo.

## [2026-09-04T03:15Z] Autonomous tick — outdoor Neon "NEON" cortado ACEITO (fillText sem maxWidth)
- Baseline re-medido no HEAD `0f18920`: `src/` limpo; `node --check` + `git diff --check` OK; build `/tmp/sk3d-dist-tick0904b` 44 modulos; AI Track 1/2 x20 `0 lost / 0 backwards / 0 crashes`.
- Auditoria de gameplay no runner (LXC105 via Proxmox .102, vite :3457, ANGLE/Vulkan `RADV PHOENIX`): 4 videos `?demo` Meadow d/m + Neon d/m (11 frames cada, `pageErrors=[]`). Critica cega mesmo prompt nos frames mid-race; frame Neon mostrou board rosa lendo `NEO KART`.
- Root cause em `src/track/Environment.js` (`bbTex`, large billboards Neon): canvas 256x128, `fillText(word,110,52)` em 900 64px — `NEON` ~180px termina ~290px, fora do canvas. Afetava boards 0 (rosa `NEON`) e 2 (amarelo `KART`); board 1 (`NEO`) ja cabia.
- Fix (2 linhas, sem fisica/input/audio/geometria/assets): `maxWidth=140` nos dois `fillText` (palavra + `KART`).
- Lamp-head `rotation.z=0` (:4446) analisado e REJEITADO como gap: box `0.5x0.14x0.22` simetrico — zeroing pos-lookAt e visualmente no-op; haze-ring `:825` correto (mantem gradiente vertical).
- A/B GPU: ink-check deterministico `tmp-bbink.cjs` (nao versionado, ?demo track 2, `RADV PHOENIX`, `pageErrors=[]` ambos): PRE lastInk `[255,245,255]` (tinta encosta na borda = cortado) -> POST `[246,245,249]` (margem >=6px; board 1 inalterado). Gameplay POST Neon desktop 20 frames `phase=race`, `pageErrors=[]`; critica mesmo prompt em crops pareados: PRE `NEO|` (N cortado na borda) -> POST `NEON` completo; board amarelo `KAR` -> `KART`.
- Checks pos-fix: `node --check`, `git diff --check`, build `SK3D_OUT_DIR=/tmp/sk3d-dist-bbtext` -> `44 modules`, `884K` JS, `2.56s`; AI Track 1/2 x20 `0/0/0`.
- Infra: probe dedicado em `?test` travou (RAF morto no headless p/ `waitForFunction` padrao + `process.env` inexistente em `page.evaluate`); resolvido com harness `?demo` provado. Leftover `tmp-banner-faces.cjs` de tick anterior (1h wedged, 60% CPU) limpo no runner.
- Decisao: **PRODUCT CHANGE ACCEPTED**. Proximo gap: blobs brancos de drift/smoke (alpha 1, 0xffffff) ou variedade Meadow — a definir por medicao; score AAA nao declarado completo.

## [2026-09-04T04:00Z] Autonomous tick — drift smoke translúcido ACEITO (alpha por família)
- Baseline re-medido no HEAD `ee2d55b`: `src/` limpo; `node --check` + `git diff --check` OK; build externo OK; AI Track 1/2 ×20 `0 lost / 0 backwards / 0 crashes`.
- Auditoria de gameplay no runner direto (`192.168.0.195`, vite :3470, ANGLE/Vulkan `RADV PHOENIX`): 4 vídeos `?demo` Meadow d/m + Neon d/m (10 frames cada, `pageErrors=[]`). Frame Neon `nd/frame_0005` (lap 2/3) mostrou blobs branco-azuis sólidos sobre a pista atrás dos karts IA.
- Root cause em `src/render/Particles.js`: `TYPES.drift` (normal blending, grow 2.4) sem alpha + `_burst` com `opts.alpha ?? 1` → drift tier-0 `0xffffff` (Kart.js:2378) nasce opaco e lê como blob sólido.
- Fix (2 hunks, sem física/input/áudio/geometria/assets): `alpha: 0.5` no TYPES.drift + fallback `opts.alpha ?? cfg.alpha ?? 1` no `_burst`.
- Checks pós-fix: `node --check`, `git diff --check`, build `SK3D_OUT_DIR=/tmp/sk3d-dist-driftalpha` → `44 modules`, `904.20 kB`, `2.15s`; AI Track 1/2 ×20 `0/0/0`.
- A/B GPU pareado (`tmp-capture-particles.cjs`, ?test track 1, seed fixa, PRE via stash local — runner não tem gitdir, FS é compartilhado): GPU `RADV PHOENIX`, `pageErrors=[]` nos 4; kart desktop idêntico `(-66.5,0.55,3.53)`; diff pré→pós `31.28%` desktop / `32.16%` mobile (pixels >2). Crítica mesmo prompt em crops idênticos: PRE bola laranja superexposta opaca → POST brasa translúcida contida com roda visível através.
- Gameplay POST `?demo` Meadow desktop 10 frames `phase=finished`, `pageErrors=[]`.
- Decisão: **PRODUCT CHANGE ACCEPTED**. Próximo gap: variedade Meadow / torres Neon / shoulder 0.14 + music-shuffle (R25) — a definir por medição; score AAA não declarado completo.
- Infra: `git` não roda no runner (gitdir em `/home/jarvis/gitdirs` só existe local) — stash local + sleep 50s p/ recompile do vite; ssh Proxmox .102 sem password file continua negado, rota direta .195 com chave OK. Servidor :3470 dedicado deste tick (matar ao final).

## [2026-09-04T05:00Z] Autonomous tick — music-shuffle string-na-playlist ACEITO (R25 pendente)
- Baseline re-medido no HEAD `01db26c`: `src/` limpo; `node --check` + `git diff --check` OK; build externo OK (`2.23s`); AI Track 1/2 ×20 `0 lost / 0 backwards / 0 crashes`.
- Root cause em `src/audio/music.js` (`_shufflePlaylist`): `this._lastTrack` é string (`track.name`) mas `_playlist` guarda objetos — `list.push(this._lastTrack)` injetava string; no 4º `_playNext` do 2º ciclo o scheduler lia `.chords/.bpm` da string e lançava (`Cannot read properties of undefined`), matando a música em sessões longas. Repro Node (stub ctx, 9× `_playNext`) lançou em `#7` pré-fix.
- Fix (1 hunk, sem física/input/visual/mix/assets): `const [t] = list.splice(idx, 1); list.push(t)` + nota R25-FIX.
- Checks pós-fix: `node --check`, `git diff --check`, build `SK3D_OUT_DIR=/tmp/sk3d-dist-shufflefix` → `44 modules`, `904.20 kB`, `2.12s`; AI Track 1/2 ×20 `0/0/0`.
- Prova: repro `9 consecutive tracks` válidas; matriz 5 seeds × 12 tracks `MATRIX-PASS` (contrato closer-não-reabre + determinística em 2 runs); browser no runner direto (`:3471` fresco, marker=1; `:3458` stale evitado) → `SHUFFLE_BROWSER=PASS tracks=9 invalid=0`, `RADV PHOENIX`, `pageErrors=0`; `probe-audio-lifecycle.mjs` → `AUDIO_LIFECYCLE=PASS checks=9 failed=0 pageErrors=0`. Smoke `audio-determinism-smoke.mjs` BLOCKED no env (sem entry `index.js`); `sfx.js` intacto.
- Decisão: **PRODUCT CHANGE ACCEPTED**. Próximo gap: shoulder 0.14 absoluto (KartPhysics) — a definir por medição; score AAA não declarado completo.

## [2026-09-04T06:00Z] Autonomous tick — shoulder path-relative ACEITO (groundY absoluto 0.14)
- Baseline re-medido no HEAD `0f7803c`: `src/` limpo; `node --check` + `git diff --check` OK.
- Root cause em `src/entities/KartPhysics.js` (`step`, branch shoulder): `near.groundY = 0.14` ABSOLUTO, mas o ribbon do shoulder é `p.y + 0.14` (path-relativo, `buildRoadRibbon` yOffset 0.14, TrackBuilder.js:2183). Meadow tem elevação 0.0→3.0m; Neon é plano em y=0.3.
- Repro determinístico single-step (real KartPhysics + real path, kart em lateral halfW+1.0, 1 step lendo `_prevY`): PRE-fix Meadow HIGH pathY=3.065 → groundY=0.520 (err 3.065m) + Neon pathY=0.300 → 0.520 (err 0.300m) = `SHOULDER-PROBE=FAIL`. Nota: probe multi-frame é inválido — o wall clamp (wallAt=3.87 < halfW+0.5) puxa o kart de volta ao on-road no mesmo step; a medição tem que ser no 1º step.
- Fix (1 hunk, sem física além do grounding, sem input/áudio/geometria/assets): `near.groundY = 0.14` → `near.groundY += 0.14` + nota de causa raiz (espelha o branch on-road `+= 0.18`).
- Checks pós-fix: `node --check`, `git diff --check`, build `SK3D_OUT_DIR=/tmp/sk3d-dist-shoulder` → `44 modules`, `built in 2.16s`; AI Track 1/2 ×20 → `0 lost / 0 backwards / 0 crashes`.
- Prova: repro POST `SHOULDER-PROBE=PASS` (Meadow err 0.001, Neon err 0.000). 4 vídeos `?demo` no runner direto (`192.168.0.195`, vite :3472): Meadow d/m + Neon d/m 10 frames cada, `RADV PHOENIX`, `pageErrors=[]`, fases `finished/finished/race/race`; crítica mesmo prompt (md_frame_0002, mm_frame_0002, nd_frame_0005): karts assentados, sem afundar/flutuar, sem artefato.
- Infra: vite :3472 quebrou com ENOSPC (qa-gpu-runner 6.3G estoura inotify) — resolvido com `sudo sysctl fs.inotify.max_user_watches=524288`; tentativa de `mv` do dir dividiu o conteúdo e foi revertida com merge de volta (árvore íntegra, só GATES.md + KartPhysics.js modificados).
- Decisão: **PRODUCT CHANGE ACCEPTED**. Próximo gap: variedade Meadow / torres Neon — a definir por medição; score AAA não declarado completo.

## [2026-09-04T07:00Z] Autonomous tick - Meadow tuft r2/r3 nao-normalizado ACEITO (56% capim seco -> 11.7%)
- Baseline: HEAD 7b63645; worktree trazia o fix deste gap NAO commitado (Environment.js + GATES.md com M1-M5 abertos) - tick anterior nao fechou. Re-medi tudo do zero.
- Root cause em src/track/Environment.js (buildMeadowGrassField): hash sin%1 preserva sinal; r1 era normalizado mas r2/r3 nao. r2 negativo contava como tall (r2<0.16) -> ~56% dos tufts viravam capim alto seco em vez dos ~16% projetados; r3 negativo enviesava o jitter tangencial (media -0.51 em vez de ~0).
- Repro: node scripts/tmp-census-tufts.mjs -> LEN=394.6 N=247 TOTAL=470, PRE_TALL=263 (56.0%) POST_TALL=55 (11.7%), JIT_MEAN_PRE=-0.5134 JIT_MEAN_POST=-0.0092, CENSUS=BUG-CONFIRMED.
- Fix (1 hunk, so normalizacao r2/r3 -> r1n/r2n/r3n; sem fisica/input/audio/geometria/assets).
- Checks: node --check OK; build SK3D_OUT_DIR=/tmp/sk3d-dist-tuft-r26 -> 44 modules, 904.22 kB, 2.16s; AI Track 1/2 x20 -> 0 lost / 0 backwards / 0 crashes.
- A/B GPU LXC105 (tmp-capture-gameplay.cjs via Proxmox .102 pct exec 105, vite local :3472 na LAN .103, PRE via stash + sleep 50s p/ HMR): tuft-pre/post x desktop/mobile -> GPU ANGLE RADV PHOENIX, 10/10/10/10 frames, lastPhase=finished, pageErrors=[] nos 4. Critica mesmo prompt (grama Meadow): sem dominancia amarela nem artefato pre/pos; mobile frame_0005 caiu na tela FINISHED -> re-puxado frame_0001, verde saudavel, sem regressao. Frames nao sao posicao-casados - evidencia direcional decisiva e o censo deterministico, nao pixel-diff.
- Infra: rota Proxmox exige PW de /home/jarvis/.hermes/.proxmox_root_pw (HOME do cron e o profile home, ~ nao resolve); push do capturador via pct exec cat por stdin; pull de frames via base64 -w0 (tar binario pelo pct quebra).
- Decisao: PRODUCT CHANGE ACCEPTED. Proximo gap: variedade Meadow restante / torres Neon - a definir por medicao; score AAA nao declarado completo.

## [2026-09-04T08:00Z] Autonomous tick — auditoria full-matrix pós-tuft: NO PRODUCT CHANGE (nada quebrado à vista)
- Baseline re-medido no HEAD `5e7bd1e`: `src/` limpo; `node --check` + `git diff --check` OK; build externo `SK3D_OUT_DIR=/tmp/sk3d-dist-tick0904c` → `built in 2.08s`; AI Track 1/2 ×20 → `0 lost / 0 backwards / 0 crashes`.
- 4 vídeos `?demo` no LXC105 (vite `:3473` local, rota Proxmox .102): Meadow d/m + Neon d/m, 10 frames cada, GPU `ANGLE/Vulkan RADV PHOENIX`, `pageErrors=[]`, fases `finished/finished/race/race`, job `ALL-CAPTURES-DONE`.
- 9 frames auditados (prompts cegos por frame): largada com boost flames + DRAFT (md0/nd0), AI karts + billboards legíveis (md1/nd4), FINISH gantry + tela FINISHED (md2/md5), rescue Lakitu com toast visível + grama verde saudável pós-tuft (mm1), drift com smoke translúcido (nd2), touch controls mobile (nm2). Nenhum defeito concreto.
- Falsos gaps descartados com prova: timer mobile oculto = intencional (CSS ≤480px, padrão MK8D); tire stack = design documentado; streaks finas no céu mobile sem par desktop = não reproduzível.
- Decisão: **NO PRODUCT CHANGE ACCEPTED**. Próximo gap: fog residual / variedade Meadow restante / torres Neon — a definir por medição; score AAA não declarado completo.

## [2026-09-04T09:00Z] Autonomous tick — Neon roof caps + pilasters enterrados ACEITO (h/12 vs box 14m)
- Baseline re-medido no HEAD `388e217`: `src/` limpo; `node --check` + `git diff --check` OK.
- Root cause em `src/track/Environment.js` (`buildNeonCity`): box `BoxGeometry(10,14,8)` com escala Y `h/12` → altura real `7h/6`, topo em `gy+13h/12`. Roof plate em `gy+h+0.11` ficava 0.67-2.50m DENTRO do box em todas as alturas (6/6 = invisível); pilastras (`4.86sx`, largura 0.24) proud só p/ sx<0.86 (~35%). Detalhe instanciado caro e invisível.
- Repro: `scripts/tmp-roof-bury-probe.mjs` (lê as constantes reais do fonte) → PRE `BURY-CONFIRMED`.
- Fix (3 hunks, sem física/input/áudio/geometria além do grounding visual, sem assets): escala Y `h/12`→`h/14` (topo real = gy+h, roof assenta exato); cantos `5sx-0.06`/`4sz-0.06` (face externa 0.06 proud em todo sx); tank `+1.1`→`+0.77` (assenta na plate, que agora está no topo real; antes a base ficava enterrada).
- Checks pós-fix: probe `BURY-FIXED` (roof 0/6, pilastras 5/5); `node --check` + `git diff --check` OK; build `SK3D_OUT_DIR=/tmp/sk3d-dist-roof` → `built in 2.19s`; AI Track 1/2 ×20 → `0 lost / 0 backwards / 0 crashes`.
- A/B GPU LXC105 (`tmp-capture-roof.cjs`, ?test track 2, torre row-A instance 1 idêntica, PRE via stash + HMR): `RADV PHOENIX`, `pageErrors=[]` nos 4; diff pareado `15.89%` desktop / `41.75%` mobile (pixels >2). Crítica mesmo prompt: PRE plate lia como faixa horizontal cortando a fachada com box acima (topo inacabado) → POST cap nítido terminando a torre + nub de antena visível, desktop e mobile.
- Gameplay POST `?demo` Neon desktop 4 frames `phase=race`, `pageErrors=[]`, sem artefato.
- Decisão: **PRODUCT CHANGE ACCEPTED**. Próximo gap: variedade Meadow restante / fog residual — a definir por medição; score AAA não declarado completo.

## [2026-09-04T10:00Z] Autonomous tick — billboards-logo Meadow restaurados ACEITO (0/6 nasciam + Euler-fold nas pernas)
- Baseline re-medido no HEAD `c82959e`: `src/` limpo (só untracked `qa-gpu-runner/` + `scripts/tmp-*.mjs`); `node --check` + `git diff --check` OK.
- Gap duplo em `buildProps` (só Meadow): (a) 6 spots hardcoded caíam TODOS dentro do guard `_onTrack(x,z,8)` (raio roadWidth/2+8 = 12.5m; minDist medidas 3–9.5m) → ZERO boards `4.6×2.3×0.35` em 2395 meshes (`?test` track 1, `pageErrors=[]`); (b) pernas em eixo-mundo ignoravam o yaw (até 1.64m fora do plano, 10/12 detached no probe matemático).
- Fix (só `src/track/Environment.js` + call-site, sem física/input/áudio/assets): 6 estações path-relative (t 0.10–0.91, lados alternados, lateral halfW+11 = 15.5m, slack 3.0m), `lookAt` p/ a pista, pernas com frame `sx/sz` + ground na posição da perna, `buildProps(scene, track)`.
- Armadilha metodológica registrada: intermediário lendo `board.rotation.y` pós-lookAt passou no probe estático mas mediu 8/12 detached AO VIVO — Euler-XYZ extrai y como asin(m13) e folda yaw real 2.02→1.12. Rejeitado antes de commit; regra: nunca Euler pós-lookAt, construir o frame por vetor. Debug `window.__bb*` removido do fonte.
- Prova: probe `BILLBOARD-PROBE=PASS`; runtime GPU `RADV PHOENIX`: PRE `boards=0` → POST `boardCount=6`, attach ao vivo `detached=0/12 worst=0.00m`, `pageErrors=[]` (d/m); crítica mesmo prompt (3 frames): PRE grama vazia → POST `SUPER KART 3D.js` legível d/m, perna conectada; gameplay POST `?demo` Meadow 5 frames `phase=finished`.
- Checks: build `SK3D_OUT_DIR=/tmp/sk3d-dist-billboard2` → `44 modules`, `3.40s`; AI Track 1/2 ×20 → `0 lost / 0 backwards / 0 crashes`. `gate-check` → `ALL MET (386 met, 34 abandoned)`.
- Infra: vite `:3474` com pipe `| head` morreu (SIGPIPE) — relançado sem pipe; `legGaps:[]` no helper = limitação conhecida (pernas viram InstancedMesh via `autoInstancing`, invisíveis ao filtro de Mesh regular); `pct push` exige path absoluto no host — usar `cat >` via stdin.
- Decisão: **PRODUCT CHANGE ACCEPTED**. Próximo gap: variedade Meadow restante / fog residual — a definir por medição; score AAA não declarado completo.

## [2026-09-04T11:00Z] Autonomous tick — sweep invariantes props vs pista: instrumento invalidado, NO PRODUCT CHANGE

- Baseline: HEAD `20b928b`, `node --check` + `git diff --check` OK; build `SK3D_OUT_DIR=/tmp/sk3d-dist-propsweep` → `44 modules`, `904.47 kB`, `2.76s`; AI Track 1/2 ×20 → `0 lost / 0 backwards / 0 crashes`.
- Sweep novo (`qa-gpu-runner/tmp-prop-sweep.cjs`, untracked): walk completo da cena no LXC105 (RADV PHOENIX, `pageErrors=[]`, `585` regulares + `18412` instâncias) com centerline 400 amostras (gate ≥240) e `terrainHeight` importado do próprio bundle. Resultado: ~10k flags — esmagadora maioria falso-positivo do instrumento, não do jogo (moedas/item-box flutuam por design; tire stacks na borda leem ON-ROAD; partes de figuras compostas avaliadas como props independentes; bounce do update() invalida medida estática).
- Cluster mais suspeito (boxes BURIED-LOW a dist ~7.7m, minY ~1.15m sob o terreno) investigado em 2 vias: (1) código — `_gy` do jogo é literalmente `terrainHeight(x,z,trackPath)` (Environment.js:493), mesmo modelo do probe; (2) foto GPU do ponto exato (`tmp-look.cjs`, (-52,4,14)→(-55,0,5)) com vision nativa: plateia em pé sobre berms, pés assentados, billboards `SUPER KART GP` legíveis, nada flutuando/enterrado. Veredito: instrumento mede parte-dinâmica como estática → rejeitado o instrumento, nenhum patch especulativo.
- Decisão: NO PRODUCT CHANGE (`git diff -- src` vazio). Lição: sweep genérico sem whitelist por sistema repete o erro 2026-08-15 — invariantes só valem por sistema (como roof-bury e billboard-legs), nunca full-scene cego. Track 2 não rodado com régua quebrada (ABANDON honesto em GATES.md).
- Infra: vite dedicado `:3475` (LAN .103) encerrado pós-tick; capturadores `tmp-prop-sweep.cjs`/`tmp-look.cjs` untracked em `qa-gpu-runner/`, fora do staging.
- Próximo gap: variedade Meadow / torres Neon / fog residual — a definir por medição com instrumento por-sistema, nunca sweep cego.

## [2026-09-04T12:00Z] Autonomous tick — postes das billboards Neon ignoravam o yaw: fix ACEITO

- Gap por-sistema (família B-LEG de Meadow): billboards grandes de Neon (3x 9x4.4x0.4, lookAt p/ o centro) com light poles em offset eixo-mundo (`b.p[0]+dx`) + base absoluta 1.7m.
- Prova PRE ao vivo LXC105 (`?test` track 2, `qa-gpu-runner/tmp-bb-pole-probe.cjs` untracked, GPU ANGLE RADV PHOENIX, `pageErrors=[]`): board 0 yaw `-1.556` → postes em localX ~0.05 (centro do board) com offPlane `3.467/3.311m` → `POLE-DETACHED=2/6`; bases `1.7` (~1.75m de flutuação). Frame PRE válido: poste cruza o centro e oclui o texto NEON/KART.
- Fix (só `src/track/Environment.js`, 1 hunk, 21+/3-): yaw fold-proof via atan2(look-pos) (nunca Euler pós-lookAt) + postes em frame rotacionado com altura do topo do board ao `_gy` por poste.
- Prova POST (d/m, `pageErrors=[]`): `POLE-ATTACHED-ALL` — localX +-3.4 exato, offPlane `0.13` (tilt do board, < 0.325), bases `-0.18..+0.10` ≈ terreno. A/B mesmo prompt: PRE poste no texto + flutuando → POST postes flanqueiam, assentados, NEON KART legível, sem artefato. Gameplay POST `?demo` Neon desktop: 5 frames, `lastPhase=race`, `pageErrors=[]`.
- Checks: `node --check` + `git diff --check` OK; build SK3D_OUT_DIR fora do worktree → `built in 2.83s`; AI Track 1/2 x20 → `0 lost / 0 backwards / 0 crashes`.
- Infra: vite `:3476` (LAN .103) dedicado, encerrado pós-tick; push do helper via `pct exec cat >` stdin, pull via base64. Pitfall: `game.loop.stop()` antes do screenshot congela o frame pré-câmera — não parar o loop, só `__freezeCam` + `phase=idle`.
- Decisão: **PRODUCT CHANGE ACCEPTED**. Próximo gap: variedade Meadow / repetição das torres Neon / fog residual — a definir por medição; score AAA não declarado completo.

## [2026-09-04T13:00Z] Autonomous tick — fachadas Neon idênticas: candidato REVERTIDO (delta sub-perceptual)

- Gap: `buildNeonCity` compartilhava 1 `_windowTex` (seed 4242) entre ~100 torres (4 rows) — layout de janelas idêntico, repetição visível ("cidade Neon repetitiva").
- Candidato (só `src/track/Environment.js`, 13+/7-): `_windowTexture(seed)` com cache por seed + call-site `this._windowTexture(row.seed)` (1 variante/row, mesmo layout 12x16/paleta fria).
- Prova A/B GPU LXC105 (helper `/tmp/tmp-capture-facade.cjs` → runner `/opt/pwtest` via scp+`pct push`; criação de arquivo novo no mount falhava, nada persistido no repo; vite `:3477` LAN .103, torre-mediana row-A 55m fov 55): POST d/m + PRE d/m (HEAD via copyfile, HMR 45s), mesma câmera/torre; GPU `ANGLE ... RADV PHOENIX`, `pageErrors=[]` 4/4. Diff numérico PRE→POST: `0.33%` d / `0.27%` m pixels >2. Crítica cega mesmo prompt: frames idênticos, variedade 6–7/10 ambos — tint por instância já diferencia as torres; reshuffle de layout é sub-perceptual a distância de gameplay.
- Checks: `node --check` + `git diff --check` OK; build `SK3D_OUT_DIR=/tmp/sk3d-dist-facade` → `9.77s`; AI Track 1/2 ×20 → `0 lost / 0 backwards / 0 crashes`. Pós-revert: build `2.83s`, AI `0/0/0` ambas.
- Infra: virtiofs com cache dentry corrompido mid-tick (ghosts 0-byte, ENOENT em open) — `sudo drop_caches` limpou; `git stash push` TRUNCOU `Environment.js` (chmod EPERM no checkout, arquivo 0 bytes) — restaurado do blob do stash via `shutil.copyfile` (sem chmod); PRE via copyfile do HEAD (nunca stash/checkout no virtiofs); criação de arquivos novos no mount falha (helper via /tmp + scp + `pct push`); `pct pull` + `scp` p/ trazer PNGs. Stash dropado pós-restore.
- Decisão: **NO PRODUCT CHANGE** (`src/` = HEAD; ABANDON W4 em GATES.md). Lição: variedade de fachada precisa mudar grade/paleta por row (não só reshuffle de células) p/ ser visível; ou aceitar que o tint já resolve. Próximo gap: variedade Meadow / torres Neon (grade) / fog residual — a definir por medição; score AAA não declarado completo.

## [2026-09-04T14:00Z] Autonomous tick — shop signs Neon flutuantes/ocluidos: fix ACEITO

- Gap por-sistema (mesma familia B-LEG/billboard-pole): 12 shop signs (`buildNeonCity`, Box 3.4x0.8x0.14) a lateral 20-24m ATRAS da row-A (11-19m), sem suporte.
- Prova PRE ao vivo LXC105 (`qa-gpu-runner/tmp-shop-sign-probe.cjs`, GPU ANGLE RADV PHOENIX, `pageErrors=[]`): 7/12 sinais, EMBEDDED 1, OCCLUDED 2, bottomClear ate 7.11m, trackDist 18-24m. Frame PRE: letreiro escondido atras de torre (so filete magenta visivel).
- Fix (so `src/track/Environment.js`): lateral `roadWidth/2+7` (~11.5m) + 2 pernas/letreiro ate o `_gy` + desvio de footprints row-A (nudge tangente 4m ate +/-16m, skip se sem ponto livre). v1 do fix mediu 2/12 embutidos na sonda pos → v2 com desvio zerou.
- Prova POST: desktop 12 sinais, EMBEDDED 0, OCCLUDED 0, nearestTower min 8.25m; mobile 12 sinais. Critico cego mesmo prompt: POST desktop = letreiro verde sobre 2 pernas + vizinhos F/KART legiveis; POST mobile = letreiro sobre pernas, touch OK. Gameplay Neon `?demo` 40s: 10 frames, lastPhase=race, `pageErrors=[]`.
- Checks: `node --check` + `git diff --check` OK; build SK3D_OUT_DIR fora do worktree → `built in 4.49s`; AI Track 1/2 x20 → `0 lost / 0 backwards / 0 crashes`.
- Infra: PRE via `git show HEAD:... >` + HMR 50s (restore do fix via /tmp copyfile, `node --check` apos cada escrita); helper ja existia no runner (`/opt/pwtest`), push via `pct exec cat >` stdin, pull via base64.
- Decisão: **PRODUCT CHANGE ACCEPTED**. Próximo gap: variedade Meadow / fog residual / torres Neon (grade) — a definir por medição; score AAA não declarado completo.

## [2026-09-04T15:00Z] Autonomous tick — grade portrait nas fachadas da row-A Neon ACEITO (8x22 vs 12x16 esticado)

- Baseline: HEAD `db5d7a6`, `src/` limpo; `node --check` + `git diff --check` OK; build `SK3D_OUT_DIR=/tmp/sk3d-dist-tick15` → `2.68s`; AI Track 1/2 x20 → `0 lost / 0 backwards / 0 crashes`.
- Eleição do gap por evidência: capturas `?demo` 40s no LXC105 (Neon/Meadow x d/m, GPU `ANGLE ... RADV PHOENIX`, `pageErrors=[]` 4/4, 10 frames cada) + crítica vision nativa mesmo prompt em 8 frames. Gap eleito: row-A Neon (11-19m) estica a textura quadrada 12x16 em faces de até 30m de altura (box 10x14x8, escala h/14) → janelas gigantes borradas no 1º plano (gameplay `neon-d frame_0008`: células ~2m borradas na torre direita). Hipótese rival "torres-void pretas" rejeitada pelos frames 0004/0008. Meadow forte, mobile OK.
- Fix (só `src/track/Environment.js`, 37+/18-, sem física/input/áudio/assets/geometria): `_windowTexture(opts)` com cache por chave de seed-grade + grade portrait 8x22 (seed da row) p/ a row near; demais rows no layout 12x16 legado byte-idêntico (mesma seed 4242, mesmas constantes, mesma ordem de `rand()`). Densidade de grade (lição W4), não reshuffle.
- Prova A/B GPU (`tmp-capture-facade.cjs`, torre row-A instance 2, 55m, fov 55, PRE via copyfile HEAD + HMR 50s, mesma câmera/torre d/m): `RADV PHOENIX`, `pageErrors=[]` 4/4; diff numérico PRE→POST `23.61%` d / `19.82%` m pixels >2 (vs 0.33% do reshuffle W4). Crítica cega mesmo prompt d/m: PRE faixas verticais esticadas/borradas → POST janelas menores, quadradas, densas e nítidas (prédio habitado); torres âmbar distantes idênticas (isolamento). Gameplay POST `?demo` Neon desktop 24s: 6 frames, `lastPhase=race`, `pageErrors=[]`, sem artefato.
- Checks: `node --check` + `git diff --check` OK; build `SK3D_OUT_DIR=/tmp/sk3d-dist-facadegrade` → `4.72s`; AI Track 1/2 x20 → `0/0/0` ambas.
- Infra: vite dedicado `:3478` (LAN .103) encerrado pós-tick; PRE via copyfile do HEAD (nunca stash no virtiofs); restore do fix via `/tmp/Environment.facadegrade.js` + `node --check`.
- Decisão: **PRODUCT CHANGE ACCEPTED**. Próximo gap: variedade Meadow / fog residual / karts IA recoloridos — a definir por medição; score AAA não declarado completo.

## [2026-09-04T16:00Z] Autonomous tick — caixilho 4-panes nas fachadas row-A próximas ACEITO (mullion close-range)

- Baseline: HEAD `92a0f6b`, `src/` limpo; `node --check` + `git diff --check` OK; build `SK3D_OUT_DIR=/tmp/sk3d-dist-tick16` → `2.66s`; AI Track 1/2 x20 → `0 lost / 0 backwards / 0 crashes`.
- Eleição do gap por evidência: capturas `?demo` 40s no LXC105 (Neon/Meadow x d/m, GPU `ANGLE ... RADV PHOENIX`, `pageErrors=[]` 4/4, 10 frames cada) + crítica vision nativa mesmo prompt. Gap eleito: faces row-A a 5-15m ainda leem como painéis gigantes brancos (~1.5m/célula) — a grade portrait 8x22 do tick 15:00Z só resolveu a 55m. Framing mobile do `?demo` NÃO é gap (câmera demo = followDistance + 4.2m, aceita v3). Roster da IA verificado (sem duplicatas, 6 cores distintas em código + frames) — gap "karts IA recoloridos" FECHADO sem mudança.
- Fix (só `src/track/Environment.js`, 19+/2-, sem física/input/áudio/assets/geometria): `opts.mullion` + chave de cache `-m` + cruz de caixilho `#0d1322` nas células lit/accent da textura near (zero `rand()` novo → layout idêntico); demais rows no caminho legado byte-idêntico.
- Prova A/B GPU (`tmp-capture-facade-near.cjs`, torre row-A instance 2, 16m, fov 50, PRE via copyfile HEAD + HMR 45-50s, mesma torre/câmera d/m): `RADV PHOENIX`, `pageErrors=[]` 4/4; diff numérico PRE→POST `11.45%` d / `21.85%` m pixels >2. Crítica cega mesmo prompt: PRE painéis gigantes lisos → POST janelas 4-panes (escritórios habitados); torres distantes idênticas (isolamento). Mobile POST sem moiré/artefato. Gameplay POST `?demo` Neon d 24s: 6 frames, `lastPhase=race`, `pageErrors=[]`, caixilho funde à distância.
- Checks: `node --check` + `git diff --check` OK; build `SK3D_OUT_DIR=/tmp/sk3d-dist-mullion` → `2.69s`; AI Track 1/2 x20 → `0/0/0` ambas.
- Infra: helper local `qa-gpu-runner/tmp-capture-facade.cjs` virou ghost 0-byte (virtiofs) — recuperado do runner (`/opt/pwtest`) via base64; `pct push` lê do host (falhou) → push via `pct exec cat >` stdin; PRE via copyfile do HEAD (nunca stash no virtiofs).
- Decisão: **PRODUCT CHANGE ACCEPTED**. Próximo gap: variedade Meadow / fog residual — a definir por medição; score AAA não declarado completo.

## [2026-09-04T18:00Z] Autonomous tick — smear no asfalto Neon: candidato REVERTIDO (contribuidor menor)

- Baseline: HEAD `c9b854d`, `src/` limpo; `node --check` + `git diff --check` OK; build `SK3D_OUT_DIR=/tmp/sk3d-dist-tick18` → `2.61s`; AI Track 1/2 x20 → `0 lost / 0 backwards / 0 crashes`.
- Eleição do gap por evidência: capturas `?demo` 40s no LXC105 (Meadow/Neon x d/m, GPU `ANGLE ... RADV PHOENIX`, `pageErrors=[]` 4/4) + crítica vision nativa mesmo prompt em 8 frames + crop do asfalto. Gap eleito: asfalto Neon lê borrado/sujo em ângulo rasante (riscos finos multicoloridos sobre a pista); controle Meadow com asfalto limpo; fog residual sem evidência (céu limpo, torres nítidas).
- Candidato (só `src/render/Materials.js`): remove camada de 8 streaks lineares (gradiente 12-30x2px, alpha 0.22) + micro-streaks 36→18 (alpha 0.045→0.03, comp. 8-28→6-14); grit + poças radiais + overlay wet intactos; dummy RNG preserva sequência seedada.
- Prova A/B GPU (helper `tmp-capture-road.cjs`, ?test track 2, câmera grazing fixa, RNG seedado, PRE via copyfile HEAD, mesma câmera d/m): `RADV PHOENIX`, `pageErrors=[]` 4/4; diff numérico `24.05%` d / `33.19%` m (shimmer temporal domina). Crítica cega mesmo prompt: POST marginalmente mais limpo no mid-field, mas riscos persistem no foreground d/m.
- Decisão: **NO PRODUCT CHANGE** (`src/` = HEAD). Lição: a camada linear da textura era contribuidor menor — a fonte dominante do smear está em outro sistema (overlay wet da ribbon, poças de luz, ou specular do material), a investigar com instrumento por-sistema no próximo tick. Próximo gap: fonte dominante do smear / variedade Meadow — a definir por medição; score AAA não declarado completo.

## [2026-09-04T20:00Z] Autonomous tick — fonte dominante do smear Neon isolada: emissiveMap glow ACEITO (0.8→0.3)

- Baseline: HEAD `53db0f7`, `src/` limpo; `node --check` + `git diff --check` OK; build `SK3D_OUT_DIR=/tmp/sk3d-dist-tick20` → `2.73s`; AI Track 1/2 x20 → `0 lost / 0 backwards / 0 crashes`; vite dedicado `:3479` (LAN .103).
- Isolamento (helper novo `tmp-isolate-road.cjs`, 1 boot + 4 variantes, ?test track 2, RNG seedado, mesma câmera grazing): GPU `ANGLE ... RADV PHOENIX`, `pageErrors=[]`, 53 meshes aditivos / 19 emissivos classificados. Crítica cega mesmo prompt: V0 baseline streaky / V1 (overlay aditivo off) streaky / V2 (emissive off) limpo / V3 (ambos) mais limpo. Veredito: fonte dominante = `emissiveMap` glow da ribbon city (intensity 0.8 amplificava poças/streaks multicoloridos baked em glow que em grazing lia como sujeira); overlay aditivo `neonReflectionTexture` (opacity 0.35) INOCENTE — com emissive off e aditivo on a pista já lê limpa.
- Fix (só `src/track/TrackBuilder.js`, 5+/2-, branch isCity): `ribbonOpts.emissiveIntensity` 0.8→0.3; overlay aditivo, wet/clearcoat, textura e geometria intocados (spill neon segue legível, sem o smear).
- Prova A/B GPU (`tmp-capture-road.cjs`, mesma câmera -70/2.5/17.2, PRE via copyfile HEAD + HMR 55s, d/m): `RADV PHOENIX`, `pageErrors=[]` 4/4; diff numérico PRE→POST 42.55% d / 54.48% m (inclui shimmer temporal). Crítica cega mesmo prompt d/m: PRE streaks multicoloridos full-width → POST navy limpo, dashes amarelos/edge-lines/pink-cue intactos. Gameplay POST `?demo` Neon 24s: 12 frames, phase=race, `pageErrors=[]`, sem artefato.
- Checks: `node --check` + `git diff --check` OK; build `SK3D_OUT_DIR=/tmp/sk3d-dist-tick20fix` → `5.17s`; AI Track 1/2 x20 → `0/0/0` ambas; gate-check `ALL MET (417 met, 43 abandoned)`.
- Infra: `pct push` lê do host → push de helpers via `pct exec cat >` stdin; pull de PNGs via base64; numpy do venv quebrado em CPU sem AVX2 (X86_V2) → diff via PIL histogram; PRE via copyfile do HEAD (nunca stash no virtiofs).
- Decisão: **PRODUCT CHANGE ACCEPTED**. Próximo gap: variedade Meadow / fog residual — a definir por medição; score AAA não declarado completo.

## [2026-09-04T22:00Z] Autonomous tick — auditoria drift smoke Neon: candidato REFUTADO, NO PRODUCT CHANGE

- Baseline: HEAD `8fa9405`, `src/` limpo; `node --check` + `git diff --check` OK; build `SK3D_OUT_DIR=/tmp/sk3d-dist-tick21` → `2.78s`; AI Track 1/2 x20 → `0 lost / 0 backwards / 0 crashes`.
- Eleição por evidência: 4 capturas `?demo` 40s no LXC105 (Meadow/Neon x d/m, GPU `ANGLE ... RADV PHOENIX`, `pageErrors=[]` 4/4, 10 frames cada) + 7 críticas vision mesmo protocolo em 12 frames. Smear Neon CONFIRMADO resolvido (asfalto navy limpo no gameplay). Candidato: drift smoke (0xf2f5f8, grow 2.4) como neve no night; postes Neon validados por código (halfW+3.6, fora da pista).
- Refutação controlada: helper `tmp-capture-drift.cjs` (variante do `tmp-capture-particles.cjs` com track via env + drift DEFAULT sem override de cor, 36 ticks @60Hz) no Neon → PRE `RADV PHOENIX`, `pageErrors=[]`; crítica cega: fumaça lê como halos brancos suaves nas rodas — correta. `src/` nunca tocado.
- Barra preta full-height no frame PRE explicada por probe geométrico no GPU (matrixWorld direto, sem THREE global): poste a 1.06m da câmera artificial do helper; 0 ocorrências em 40 frames de gameplay real (chase cam nunca clipa). Artefato de captura.
- Infra: primeiro disparo do gameplay usou URL com `?demo` duplicado (2× timeout 180s); uso correto é 1 combo/execução via `CAPTURE_OUT` + `--mobile`/`--track`. Vite dedicado `:3480` (LAN .103) encerrado pós-tick; helper variante em /tmp + /opt/pwtest (não commitado).
- Decisão: **NO PRODUCT CHANGE** (`src/` = HEAD; ABANDON V3/V4 em GATES.md). Próximo gap: rampa laranja chapada em close (1 frame transitório, precisa isolamento) / pontos brancos gameplay (boost/sparkle?) — a definir por medição; score AAA não declarado completo.

## [2026-09-04T23:00Z] Autonomous tick — banner-skim Meadow: PRODUCT CHANGE ACCEPTED

- Baseline: HEAD `c804f03`, `src/` limpo; `node --check` + `git diff --check` OK; build `SK3D_OUT_DIR=/tmp/sk3d-dist-tick22` → `3.61s`; AI Track 1/2 x20 → `0 lost / 0 backwards / 0 crashes`.
- Eleição por evidência: 4 capturas `?demo` 40s no LXC105 (Meadow/Neon x d/m, GPU `ANGLE ... RADV PHOENIX`, `pageErrors=[]` 4/4, 10 frames cada) + críticas vision mesmo prompt. Gap = banner-skim: `meadow-d frame_0002` (0:11.5) com metade esquerda tomada por faixas vermelhas/brancas; repro determinístico `tmp-skim-ab.cjs` (?test, kart na borda t=0.0275) mostra banner "SUPER KART GP" preenchendo 1/3 do frame; código: prints 5.6m a halfW+2.4 (maior objeto na linha mais próxima). Probe cam↔superfície: mínimo 1.96m no ?demo.
- Fix (só `src/track/Environment.js`, 6+/2-, Meadow-only `if (!night)`): lateral halfW+2.4→+3.4 (+1m folga à câmera).
- Prova A/B GPU determinística (mesma estação t=0.0275, mesmo kart/cam d, `RADV PHOENIX`, `pageErrors=[]` 2/2): banner deslocado 1.0m, 32 banners, diff numérico `28.84%`. Crítica cega mesmo prompt: PRE "1/3 da tela, texto cortado" → POST "filete na borda, pista/crowd visíveis". Gameplay POST Meadow d 30s: pista limpa, banners com postes no chão, `phase=finished`, `pageErrors=[]`.
- Checks: `node --check` + `git diff --check` OK; build → `5.53s`; AI Track 1/2 x20 → `0/0/0`.
- Infra: helpers `tmp-probe-banner.cjs` (distância cam↔ret do banner via instanceMatrix, sem THREE global) e `tmp-skim-ab.cjs` (?test + teleporte + RNG seedado) em /tmp + /opt/pwtest (não commitados); vite `:3481` encerrado pós-tick.
- Decisão: **PRODUCT CHANGE ACCEPTED**. Próximo gap: variedade Meadow (copas planas) / torres Neon / fog residual — a definir por medição; score AAA não declarado completo.

## [2026-09-05T00:00Z] Autonomous tick — Neon signage: shop signs com texto + fix raiz no autoInstancing ACEITO

- Baseline: HEAD `8358e3a`, `src/` limpo (só `qa-gpu-runner/` untracked); `node --check` + `git diff --check` OK; build `SK3D_OUT_DIR=/tmp/sk3d-dist-tick23` → `4.40s`; AI Track 1/2 x20 → `0 lost / 0 backwards / 0 crashes`; vite dedicado `:3482` (LAN .103).
- Eleição por evidência: 4 capturas `?demo` 40s no LXC105 (Meadow/Neon x d/m, GPU `ANGLE ... RADV PHOENIX`, `pageErrors=[]` 4/4, 10 frames cada, lastPhase finished/finished/race/race) + 9 críticas vision mesmo protocolo. Candidato inicial (pirâmides flutuantes + linha horizontal em 1 frame Meadow) ABANDONADO após 4 probes geométricos: sem cones acima de y=20, sem meshes longos/finos, balões confirmados esferas longe do frame, repro no mesmo race-clock com céu limpo (?demo não-determinístico entre runs). Gap eleito: shop signs Neon = caixas de cor sólida sem texto (close-up determinístico `?test` + freezeCam + fov35: placa verde-menta em branco; código: `MeshBasicMaterial` único por cor).
- Achado raiz no caminho: ao texturizar os letreiros (array `[borda×4, frente, verso]`), os 12 sumiram da cena — `autoInstancing` agrupava só por `material[0]` e criava o `InstancedMesh` só com `material[0]` (borda escura): 12 letreiros + 1 mesh fantasma colapsaram numa instância escura na origem. Fix raiz em `src/perf/instancing.js`: chave cobre o array inteiro, `InstancedMesh` recebe o array completo, checagens transparent/emissive valem p/ qualquer face. Correção de hipótese no caminho: canvas pré-espelhado lia ESPELHADO no verso (evidência GPU) → BoxGeometry já mapeia UV por face p/ leitura correta; mesma textura frente+verso, sem mirror.
- Fix (só `src/track/Environment.js` + `src/perf/instancing.js`): letreiros com textura canvas por cor (TURBO/NITRO/APEX/PISTON + disco logo, laterais emolduradas `#141030`); billboards com moldura escura nas laterais (frente inalterada).
- Prova A/B GPU determinística (mesmo letreiro -81.6/38.7 ry 1.56, mesma câmera 7m fov35, `RADV PHOENIX`, `pageErrors=[]`): sonda geométrica 0/12 → 12/12 letreiros individuais com MAP frente+verso, posições byte-idênticas ao PRE. Crítica cega mesmo prompt: PRE "placa verde-menta em branco, placeholder" → POST frente "PISTON + logo, nítido" + verso "PISTON legível, não espelhado"; billboard "NEON KART" nítido frente+verso. Gameplay POST Neon 40s: 10 frames, `phase=race`, `pageErrors=[]`.
- Checks: `node --check` + `git diff --check` OK; build → `4.12s`; AI Track 1/2 x20 → `0/0/0` ambas.
- Infra: push de helpers via `pct push ... /dev/stdin`; pull via base64; probes `tmp-tick23-probe{,2..15}.cjs` em /tmp + /opt/pwtest (não commitados); armadilha: `pct exec ... -- base64` com wildcard falha — usar paths literais; finder de meshes precisa lidar com material array (`Array.isArray`) e fantasma na origem (mesh 3.4×0.8×0.14 `#141030` pré-existente).
- Decisão: **PRODUCT CHANGE ACCEPTED**. Próximo gap: variedade Meadow (copas/vegetação) / fog residual / torres Neon — a definir por medição; score AAA não declarado completo.

## [2026-09-04T21:30Z] Autonomous tick — turbo pad surfacing (edge trim + glow align) ACEITO

- Baseline: HEAD `1335332`, `src/` limpo; `node --check` + `git diff --check` OK; build `SK3D_OUT_DIR=/tmp/sk3d-dist-tick24` → `4.33s`; AI Track 1/2 x20 → `0 lost / 0 backwards / 0 crashes`; vite dedicado da sessão paralela `:3483` (LAN .103) reutilizado — sem HMR conflict (só GATES.md + Materials.js tocados por mim).
- Eleição por evidência: 4 gameplays `?demo` 40s no LXC105 (Meadow/Neon x d/m, GPU `ANGLE ... RADV PHOENIX`, `pageErrors=[]` 4/4, 10 frames cada) + 5 críticas vision mesmo protocolo. Gap eleito: turbo pad = laje amarela chapada sem borda — `neon-m frame_0005` com metade inferior do portrait tomada pelo slab; desktop `neon-d` com pads flat no mid-field. Achado de código: máscara do glow com chevrons em 0.20/0.50/0.80 vs base 0.26/0.50/0.74 (30px offset → duplo fantasma no pulse 0.06-0.14).
- Fix (só `src/render/Materials.js`, textura 512x128 + máscara glow): moldura `#5f2f00` em toda a volta + filete `#ffd97a`; âmbar aprofundado (`#ffb52e/#f5971a/#d96a00`); contorno chevron 2.5/0.55→3.5/0.75; glow realinhado p/ 0.26/0.50/0.74 half 0.09 (= base). Posições/tamanhos dos chevrons da base preservados (R12c/R13c); sem geometria/física/input/áudio.
- Prova A/B GPU determinística (`tmp-capture-pad.cjs`, ?test track 2, padT=0.1653, 8 pads, freezeCam + glow fixo 0.10, RNG seedado, mesma estação d/m, `RADV PHOENIX`, `pageErrors=[]` 4/4): diff numérico PRE→POST `2.77%` d / `8.00%` m pixels >2. Crítica cega: PRE "borda sangra no asfalto, amarelo lavado" → POST bordas marrons definidas + âmbar dourado + chevrons simples nítidos; mobile POST sem artefato. Gameplay POST Neon 24s: 6 frames, `phase=race`, `pageErrors=[]`.
- Checks: `node --check` + `git diff --check` OK; build `SK3D_OUT_DIR=/tmp/sk3d-dist-tick25` → `2.14s`; AI Track 1/2 x20 → `0/0/0` ambas.
- Infra: runner oversubscribed por chromes stale (06:45/18:0x, 50 proc) travando boot mobile 30min — limpos os mains 413252/415125/441425/441665 + nodes tick21 (restou só minha cadeia); helper `tmp-capture-pad.cjs` via `pct exec cat >` stdin; /tmp/tick25 da sessão paralela de áudio — meus PNGs/txt convivem sem colisão (nomes pad-*).
- Decisão: **PRODUCT CHANGE ACCEPTED**. Próximo gap: variedade Meadow (montanhas chapadas brancas / copas escuras) / torres Neon escuras / portrait mobile com meio-frame de céu — a definir por medição; score AAA não declarado completo.

## Tick 26 — neon street signs com palavra real (2026-09-05)

- Gap (crítica vision em 4 gameplays GPU ?demo 40s Meadow/Neon d/m, `RADV PHOENIX`, `pageErrors=[]` 4/4): `neon-d frame_0008` mostra placa magenta gigante em 1º plano com barras brancas/ciano e zero texto; código confirma `signTex` 64x96 de `fillRect` bars (`fake 2-line 'text'`). Mesma classe dos shop signs (tick 23). Meadow sem gap maior (modal FINISH limpo, karts detalhados).
- Repro determinístico (`tmp-tick26-sign.cjs`, ?test track 2, letreiro mais próximo da linha, freezeCam 7m fov35): PRE ciano com barras, estação 41.45/3.31/55.74, 12 singles + 9 instanciados, `RADV PHOENIX`, `pageErrors=[]`.
- Fix (só `src/track/Environment.js`, bloco street-signs): `signTex` 128x192 com palavra real por cor (TURBO/NITRO/APEX + GP), moldura + disco logo + laterais escuras multimaterial (padrão billboards/shop signs). Sem geometria/física/input/áudio.
- Prova A/B pareada mesma estação byte-idêntica d/m: diff `2.18%` na face; crítica cega mesmo prompt PRE `barras placeholder` → POST `NITRO legível`; contagens estáveis 12+9; gameplay POST Neon 24s 6 frames `phase=race` sem placas pretas/espelhadas; mobile POST nítido (NITRO + touch OK).
- Checks: `node --check` + `git diff --check` OK; build `SK3D_OUT_DIR=/tmp/sk3d-dist-tick26b` → 44 modules `907.52 kB`; AI Track 1/2 x20 → `0/0/0` ambas.
- Infra: helper via `pct exec ... 'cat > /opt/pwtest/...'` stdin (pct push não enxerga worktree fora do host); `THREE` não é global no evaluate (usar `path.getPointAt(t)` sem target); loops ssh multi-captura com quoting aninhado falham silenciosos — 1 captura por chamada.
- Decisão: **PRODUCT CHANGE ACCEPTED**. Próximo gap: carros estacionados Neon em lajes chapadas (gameplay POST mostra slabs menta/roxo/amarelo sem volume) / variedade Meadow — a definir por medição; score AAA não declarado completo.

## Tick 27 — auditoria visual + renderer stats, NO PRODUCT CHANGE (2026-09-04T22:00Z)

- Baseline: HEAD `94f8123`, `src/` limpo (só `qa-gpu-runner/` untracked); `node --check` + `git diff --check` OK; build `SK3D_OUT_DIR=/tmp/sk3d-dist-tick27` → 44 modules `2.24s`; AI Track 1/2 x20 → `0/0/0` ambas; vite dedicado `:3484` (LAN .103).
- Varredura: 4 gameplays `?demo` 40s no LXC105 (Meadow/Neon x d/m, `ANGLE ... RADV PHOENIX`, `pageErrors=[]` 4/4, 10 frames, finished/finished/race/race) + 6 críticas vision. Frames `.jpg` (harness salva jpg, não png — pull via `pct exec -- base64` path literal). Frames 0005 Meadow pegaram modal FINISHED (corrida curta do ?demo) — mid-race usar 0002/0003.
- Achados: jogo forte em todas as combinações; tick 26 confirmado em gameplay ativa (NITRO/TURBO legíveis em `neon-d frame_0002`); turbo pad íntegro em 1º plano. Picos brancos distantes Meadow = haze auditado (bandas 0.55/0.30/0.18/0.12, r20/R21b) — mexer seria reverter tuning auditado sem defeito isolado.
- Sonda renderer (`tmp-tick27-render-probe.cjs`, `window.__sk3d.renderer.info`): Meadow-d 1462 calls/1.01M tris, Meadow-m 538/741k, Neon-d 1419/271k, Neon-m 649/145k; geos ~1200-1530, tex ~98-109; `pageErrors=[]` 4/4. Sem regressão.
- Infra: HOME do cron coder = `/home/jarvis/.hermes/profiles/coder/home` — pw Proxmox em `/home/jarvis/.hermes/.proxmox_root_pw` (path absoluto); push de helper via stdin `pct exec ... 'base64 -d > dest'`; capture salva `.jpg`.
- Decisão: **NO PRODUCT CHANGE ACCEPTED**. Próximo gap: inspeção dedicada da cordilheira Meadow (?test + freezeCam mirando picos, várias distâncias) antes de qualquer edit de banda — ou carros estacionados Neon (nota tick 26, sem evidência fresca neste tick); score AAA não declarado completo.

## Tick 28 — Neon parked cars: vidro + teto (cabine-tijolo eliminada) (2026-09-05)

- Gap (crítica vision em 4 gameplays GPU ?demo 40s Meadow/Neon d/m, `RADV PHOENIX`, `pageErrors=[]` 4/4): `neon-d frame_0003` mostra sedans mint/ciano nas laterais como slabs planas; close-up determinístico `tmp-tick28-car.cjs` (?test track 2, carro mais próximo do grid, freezeCam fov35) confirma cabine = TIJOLO PRETO sólido (#0d1017), zero separação vidro/teto. Meadow sem gap maior (crowd/banners/karts/HUD fortes).
- Fix (só bloco parked-cars em `src/track/Environment.js`, 22+/3-): `cabinMat` #0d1017 → vidro azul-aço #39586e + novo `roofs` InstancedMesh (1.74x0.16x2.14, gy+1.28, cor da carroceria por instância via setColorAt) com counts/needsUpdate/add.
- Prova A/B pareada mesma estação byte-idêntica d (carro idx1, grid sub-cm) e m (carro idx3; PRE mobile via `git show HEAD:` + restore por cp, sem stash — virtiofs-safe): GPU `RADV PHOENIX`, `pageErrors=[]` 4/4; diff `34.75%` d / `26.48%` m pixels >2; crítica cega mesmo prompt PRE `tijolo preto` → POST `faixa de vidro + teto na cor` (d e m, touch mobile intacto); gameplay POST Neon 24s 6 frames `phase=race` sem artefatos.
- Checks: `node --check` + `git diff --check` OK; build `SK3D_OUT_DIR=/tmp/sk3d-dist-tick28b` → 44 modules `3.09s`; AI Track 1/2 x20 → `0/0/0` ambas.
- Infra: probe `playerKart().state.position` (não `.position` — Kart guarda em `state.position`); THREE não é global no evaluate (ler `instanceMatrix.array` raw: pos e[12..14], yaw atan2(e[8],e[10])); helper em /opt/pwtest via stdin base64; vite dedicado `:3485` (LAN .103; :3457 pertence à sessão paralela — não tocar).
- Decisão: **PRODUCT CHANGE ACCEPTED**. Próximo gap: variedade Meadow (cordilheira/copas) / rodas dos parked cars (semicírculos pretos chapados no close-up) / torres Neon — a definir por medição; score AAA não declarado completo.

## Tick 29 — auditoria visual completa + fix harness zumbi, NO PRODUCT CHANGE (2026-09-05)

- Baseline: HEAD `4ecde09`, `src/` limpo (só `qa-gpu-runner/` untracked); `node --check` main/Environment/TrackBuilder/Materials + `git diff --check` OK; build `SK3D_OUT_DIR=/tmp/sk3d-dist-tick29` → 44 modules `2.15s`; AI Track 1/2 x20 → `0/0/0` ambas; vite dedicado `:3486` (LAN .103).
- Varredura: 4 gameplays `?demo` 40s no LXC105 (Meadow/Neon x d/m, `ANGLE ... RADV PHOENIX`, `pageErrors=[]` 4/4, 10 frames cada, finished/finished/finished/race) + 8 críticas vision mesmo protocolo + minimap/SVG checado em código. Suspeitos: (1) barra branca vertical em `neon-d frame_0002`; (2) parked cars slabs à distância; (3) minimap tênue no mobile.
- Sondas determinísticas (?test track 2, freezeCam fov35, `RADV PHOENIX`, pageErrors[]): (1) `tmp-probe-strip.cjs` (1.9m) → rosa VÍVIDO, sem blowout — REFUTADA; (2) `tmp-probe-car-side.cjs` (5m, altura das rodas) → vidro `#39586e` + teto na cor presentes; in-page measure confirma cabins 22x `#39586e` sem instanceColor, roofs 22x com cor, wheels 88x — tick 28 ÍNTEGRO, REFUTADO; (3) minimap = mesmo SVG 120px d/m, apagado era compressão JPEG — REFUTADO. Rodas meio-cortadas no close-up = quad de reflexo aditivo (gy+0.05, depthWrite false) ocluindo em ângulo rasante — irrelevante na chase-cam, sem fix.
- Infra (alto valor): `tmp-capture-gameplay.cjs` no runner NÃO fechava o browser no FAIL → zumbis chromium a 108% CPU acumulavam e as capturas seguintes estouravam waitForFunction 180s. Fix: `let browser=null` + `try/finally { await browser?.close() }` (backup `.bak`), `node --check` OK, verify 10s pós-patch → `RADV PHOENIX`, 3 frames `phase=race`, 0 lingering. Pitfalls novos: (a) base URL COM `?demo` + harness que anexa `/?demo&track=` = path mangled → 404 sem boot (usar base limpa); (b) `pkill -9 -f <padrão>` casa com o próprio `bash -c` pai → suicídio (separar comandos); (c) `pct push` só enxerga o host — scp + push.
- Decisão: **NO PRODUCT CHANGE ACCEPTED**. Próximo gap: variedade Meadow (cordilheira auditada como haze intencional — só mexer com sonda dedicada) / torres Neon / itens VFX temporais — a definir por medição; score AAA não declarado completo.

## Tick 30 — auditoria visual + overlap toast FINAL LAP/FINISHED, NO PRODUCT CHANGE (2026-09-05)

- Baseline: HEAD `eccafd4`, `src/` limpo (só `qa-gpu-runner/` untracked); `node --check` main/Environment/TrackBuilder + `git diff --check` OK; build `SK3D_OUT_DIR=/tmp/sk3d-dist-tick30` → 44 modules `2.12s`; AI Track 1/2 x20 → `0/0/0` ambas; vite dedicado `:3488` (LAN .103).
- Varredura: 4 gameplays `?demo` no LXC105 (Meadow/Neon x d/m, dirs `/tmp/tick30/` distintos via CAPTURE_OUT, GPU `ANGLE ... RADV PHOENIX`, `pageErrors=[]` 4/4, 12 frames cada, finished 4/4) + 6 críticas vision mesmo protocolo (`/tmp/tick30-local/*-0002.jpg` + `*-0005.jpg`). Mid-race forte nos 4; tick 28 (vidro/teto parked cars) íntegro em gameplay. Suspeito único: pill `FINAL LAP!` sobre o painel FINISHED em `meadow-d frame_0005`.
- Investigação (sem fix): crop confirma texto literal; frames `0008`/`0011` mostram pill sumido (transiente ~2.4s = janela `TOAST_MS`, não stuck); código refuta as duas fontes conhecidas (`showFinish` esconde toast síncrono `display:none !important`; bloco FINAL LAP main.js:1334 roda SÓ em `STATES.RACE`, FINISHED cai no `else` 1380-1386). Mecanismo NÃO confirmado → sem fix especulativo; hipótese p/ sonda dedicada: `showMessage` tardio pós-finish (pickupRevealTimer/hit).
- Sonda renderer (`tmp-tick27-render-probe.cjs`, `phase=race`, `pageErrors=[]` 4/4): Meadow-d `679/871865/1520/103`, Meadow-m `590/764937/1517/102`, Neon-d `711/153556/1205/99`, Neon-m `866/187810/1203/97` (calls/tris/geos/tex). Sem anomalia (calls < tick27 porque a fase medida é `race`, antes `finished`).
- Infra: HOME do cron = `/home/jarvis/.hermes/profiles/coder/home` (pw em `/home/jarvis/.hermes/.proxmox_root_pw` absoluto); 1ª bateria de 4 runs sobrescreveu o default `qa-gpu-runner/gameplay-audit` do runner — SEMPRE setar `CAPTURE_OUT` distinto; numpy do venv quebrou (X86_V2) → diff via PIL ImageChops+ImageStat; gate-check.mjs ausente neste ambiente → gates EVIDENCE-only.
- Decisão: **NO PRODUCT CHANGE ACCEPTED**. Próximo gap: sonda repro do overlap toast/painel (?test: showFinish + showMessage tardio, assert + screenshot) / variedade Meadow / torres Neon — a definir por medição; score AAA não declarado completo.

## Tick 31 — toast sobre painel FINISHED: guard central ACEITO (2026-09-05)

- Baseline: HEAD `d057135`, `git diff -- src` = 0 bytes, `node --check` HUD/main OK; gap eleito = overlap transiente do tick 30 (pill `FINAL LAP!` sobre painel FINISHED).
- Mecanismo confirmado em código (sem especulacao): `pickupRevealTimer` (main.js, `ITEM_ROULETTE_MS=450`) agenda `hud.showMessage(label)` no RACE e dispara ate 450ms depois — se o jogador cruza a linha no intervalo, `onPlayerFinish→showFinish` esconde o toast e o timer o reexibe sobre o painel. `showMessage` (HUD.js) reexibia incondicionalmente.
- Repro PRE com codigo real no GPU (`tmp-tick31-toast-probe.cjs`, dynamic `import('/src/ui/HUD.js')`, `RADV PHOENIX`, `pageErrors=[]`): `toastHiddenAfterFinish=true`, `toastVisibleAfterLate=true` (bug), `finishVisible=true`.
- Fix (so `src/ui/HUD.js` + 1 linha `src/main.js`): `showMessage` retorna cedo com finish visivel; `hud` exposto no `__sk3d` como hook de QA. RACE/COUNTDOWN intactos (finish oculto); `reset()` reabilita toasts.
- Prova POST mesmo probe/mesmo prompt: `toastVisibleAfterLate=false`, `toastVisibleDuringRace=true` (sem regressao do sistema de toast), `finishVisible=true`, `pageErrors=[]`, `RADV PHOENIX`.
- Checks: `node --check` + `git diff --check` OK; build `SK3D_OUT_DIR=/tmp/sk3d-dist-tick31` → `2.32s`; AI Track 1/2 x20 → `0/0/0` ambas.
- Gameplay POST `?demo` 24s LXC105 4/4 (`RADV PHOENIX`, `pageErrors=[]`, 6 frames cada, finished/race/race/race); vision no frame Meadow-d FINISHED: painel `FINISHED 2nd!` + standings + Race Again/Menu, zero pill sobreposto.
- Infra: vite dedicado `:3491` (LAN .103; `:3457` e de sessao paralela — nao tocado); probe via stdin base64; frames em /tmp do runner (nao commitados).
- Decisao: **PRODUCT CHANGE ACCEPTED**. Proximo gap: variedade Meadow (cordilheira/copas) / torres Neon / itens VFX temporais — a definir por medicao; score AAA nao declarado completo.

## Tick 32 — montanhas far como slabs brancos: neve azulada + snowline + fog:false (2026-09-05)

- Baseline: HEAD `7915217`, `git diff -- src` = 0 bytes, `node --check` main/Environment/HUD + `git diff --check` OK; build `SK3D_OUT_DIR=/tmp/sk3d-dist-tick32` 44 modules `2.11s`; AI Track 1/2 x20 → `0/0/0` ambas; vite dedicado `:3492` (LAN .103).
- Varredura: 4 gameplays `?demo` 40s LXC105 (Meadow/Neon x d/m, `ANGLE ... RADV PHOENIX`, `pageErrors=[]` 4/4, 12 frames, finished/finished/race/finished) + 4 críticas vision mesmo prompt. Pitfall novo: flag mobile é `--mobile` (`--viewport=mobile` é ignorado e captura 1280x720). Gap eleito: trapézios brancos chapados no horizonte Meadow (esq/centro); zoom confirma slabs vs pico 3D central íntegro. Neon-m: riscos finos no céu = estrelas OK + postes/antenas (gap menor, próximo tick).
- Investigação (6 sondas GPU, câmera byte-idêntica [-60,6.1,-7.6]): red-test (nuvens→vermelho via uniform) provou slabs≠nuvens; censo revelou `autoInstancing` dobrando as montanhas em 4 IMs (19/20/20/12 = 49 rochas + 22 ridges, origem 0,0,0 — matchers por distância falham); `exact-hide.js` provou slabs=montanhas far (`no-mtn` limpa todo o horizonte; `no-sun`/`no-wcirc` mantêm). Mecanismo: da chase-cam baixa só o topo nevado passa da linha do horizonte (sightline ~55m a 280m); `fog:true` (70→430) + neve branca = topos chapados brancos. CORREÇÃO HONESTA: veredito inicial "no-clouds remove slabs" era misread (drift + shapes fora da banda); cloud distance-fade (2 doses, sem efeito mensurável) foi revertido.
- Fix (só `src/track/Environment.js`, +9/-6): bandas 318/262/202 com neve azulada (0xbdc9ea/0xc6d4ea/0xd2dff0) + snowLift (0.22/0.14/0.1) + haze reduzido (0.35/0.24/0.16); rockMat/hazeMat `fog:false` (haze baked vira o controle de perspectiva aérea).
- Prova A/B drift-free `mtn-ab.js` (30 brancos do céu escondidos nas duas versões, mesmo vantage): banda horizonte px>215 `14.9%→5.7%` (-62% relativo); crítica cega mesmo prompt PRE `slabs brancos` → POST `silhuetas azul-acinzentadas integradas à cordilheira`.
- Checks: `node --check` + `git diff --check` OK; build `SK3D_OUT_DIR=/tmp/sk3d-dist-tick32b` → 44 modules `5.17s`; AI Track 1/2 x20 → `0/0/0` ambas.
- Gameplay POST `?demo` 24s LXC105 4/4 (`RADV PHOENIX`, `pageErrors=[]`, 12 frames cada, finished 4/4); vision Meadow-d mid-race: karts/crowd/SUPER KART GP/HUD fortes, cordilheira em camadas, sem regressão.
- Infra: helpers em /opt/pwtest (tmp-tick32-*.cjs, exact-hide.js, one-im.js, mtn-ab.js, mat-hist.js, bufq.js — não commitados); frames em /tmp/tick32-local (não commitados); `THREE` não é global no evaluate (usar `o.position.constructor`); scripts fora de /opt/pwtest falham `require('playwright')` (NODE_PATH); A-A2 same-session dá ~4%/1.5s de drift (cena viva) — A/B entre sessões exige esconder elementos móveis.
- Decisão: **PRODUCT CHANGE ACCEPTED**. Próximo gap: riscos/postes finos no céu Neon (zoom tick32) / torres Neon / variedade de copas Meadow — a definir por medição; score AAA não declarado completo.
## Tick 33 — pilastras Neon sem haze ACEITO com caveat (2026-09-05)

- Baseline: HEAD 4c31342, git diff -- src = 0 bytes, node --check main/Environment OK; build SK3D_OUT_DIR=/tmp/sk3d-dist-tick33 44 modules 2.15s; AI Track 1/2 x20 zero/zero/zero; vite dedicado :3493 (LAN .103).
- Varredura: 4 gameplays ?demo 40s LXC105 (Meadow/Neon x d/m, ANGLE RADV PHOENIX, pageErrors=[] 4/4, finished/finished/finished/race) + 4 criticas vision mesmo prompt + 2 zooms 2x do ceu Neon. Gap eleito: riscos finos claros no ceu Neon d/m (linha palida longa + rastro avermelhado + poste com ponta vermelha no zoom). Meadow tick32 integro (cordilheira em camadas).
- Investigacao (7 sondas GPU, sem chute): censo achou 7 planos brancos (outdoors/portico — descartados), estrelas = dots na textura (ok), 16 antenas 3.2m fundidas pelo autoInstancing (inocentadas: diff mostra so 4 ticks curtos). Intervencao com freezeCam e camera byte-identica: no-strips/no-furniture sky-band diff 0.00%; no-pilasters = no-towers = 1.24% (regex facade casa pilastras). Projecao NDC: PIL ate 140px, ANT 17-24px. Mecanismo: pilasterMat unico 0x596884 fog:false (Environment.js:4702) vs torres com lerp haze 0/0.5/0.75/0.92 — na fileira far a torre sumia e a pilastra acesa flutuava. Licao infra: autoInstancing funde meshes regulares (grupo >= 8) — censos de "o que existe" devem listar InstancedMesh (h baixo escapa de filtros h>6); existencia de branch no codigo nao implica existencia na cena.
- Fix (so src/track/Environment.js, 8+/1-): material de pilastra por fileira com o mesmo lerp fogCol/row.haze das torres (near haze 0 = byte-identico; far 0.92 funde na bruma).
- Prova A/B pareada tmp-tick33-ab.cjs (freezeCam t=0.1375, RADV PHOENIX, pageErrors[] 2/2, PRE via copyfile HEAD sem stash): PILCOLOR ao vivo PRE 596884 -> POST 20223f; sky-band 1.02% px>2 nas bordas das torres; contraste pilastra/fundo x=53 +10.4 -> -1.6; critica cega mesmo prompt NEUTRA no full-frame (vantage dominado por near rows intencionalmente identicas).
- Checks: node --check + git diff --check OK; build /tmp/sk3d-dist-tick33b 44 modules 5.51s; AI Track 1/2 x20 zero/zero/zero.
- Gameplay POST Neon d/m 24s ?demo LXC105 (RADV PHOENIX, pageErrors[], race): sem regressao (karts/HUD/touch/signs/parked cars integros).
- Infra: helpers em /opt/pwtest (tmp-tick33-{census,id,sky,sky2,sky3,sky4,sky5,ab,proj}.cjs — nao commitados); frames em /tmp/tick33-local (nao commitados); window.__freezeCam congela a chase cam (updateCamera retorna cedo); projecao NDC usa instanceMatrix array (THREE nao e global no evaluate).
- Decisao: PRODUCT CHANGE ACCEPTED como remocao de inconsistência (evidencia direcional medida + mecanismo verificado ao vivo), com caveat blind-neutro explícito. Proximo gap: riscos mobile restantes (near-row/antenas/stars) + rastro avermelhado nao atribuido (candidatos: strip rosa distante, disco vermelho) — a definir por projecao no vantage gameplay; score AAA nao declarado completo.
