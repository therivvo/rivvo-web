# Super Kart 3D.js — auditoria visual POV do jogador

Data: 2026-09-03
Escopo: gameplay real no GPU runner LXC 105, ANGLE/Vulkan, RADV PHOENIX; Meadow e Neon; desktop 1280x720 e mobile 390x844.

## Evidência executada

Capturas de vídeo reais via `scripts/playtest-video.cjs`, sem `NODE_PATH`:

- Meadow desktop: `qa-gpu-runner/audit-player-meadow-desktop/` — `phase=finished`, 824 frames.
- Meadow mobile: `qa-gpu-runner/audit-player-meadow-mobile/` — `phase=finished`, 997 frames.
- Neon desktop: `qa-gpu-runner/audit-player-neon-desktop/` — `phase=finished`, 677 frames.
- Neon mobile: `qa-gpu-runner/audit-player-neon-mobile/` — `phase=finished`, 1006 frames.
- GPU reportado em todas: `RADV PHOENIX`.

As capturas tardias de resultado foram separadas das capturas de gameplay; não são usadas como prova de render durante corrida.

## Achados priorizados

### P1 — Mobile: framing do jogador e artefato do screencast

A captura PNG direta em `qa-gpu-runner/mobile-render-probe/page.png` provou que o mundo 3D é contínuo: `inner=390×844`, canvas client/backing `390×844`, drawing buffer `390×844`, câmera aspect `0.462085`, sem page errors. Portanto, a fragmentação vertical vista em alguns frames de `Page.startScreencast` é artefato do capturador portrait e não defeito do renderer.

O problema de produto que permanece é composição: o kart fica parcialmente coberto pelo pelotão em mobile e o velocímetro/controles ocupam a faixa inferior. Isso reduz a leitura da trajetória e deve ser auditado com gameplay temporal e câmera chase, não com o screencast isolado.

Probe executado: PNG direto fora do screencast; resultado refuta o P0 de pipeline quebrado.

### P1 — Bloom: halo global e perda de separação — DESLIGADO

O bloom global foi desligado no gameplay: `strength=0`, `radius=0`, `threshold=1.50`, incluindo o override Neon. PNG direto GPU após a alteração mostra kart, prédios e pista muito mais nítidos; build passou (`44 modules`, `903.92 kB`) e AI Track 1/2 passou `20 seeds` com `0 lost / 0 backwards / 0 crashes`.

O véu residual persistia mesmo sem bloom e foi separado como novo loop de fog/overlay; não será atribuído ao bloom sem evidência.

Matriz GPU DPR3 isolou a causa: `no-fog`, `no-vignette` e `no-speedlines` mantêm o haze; `no-postfx` remove-o. O composer completo estava suavizando a imagem mesmo com BloomPass desligado. O runtime agora faz bypass de PostFX quando `bloomStrength<=0`; captura final ficou nítida e contínua.

### P1 — Linha de chegada e sinais: beam e módulo corrigidos

Beam v3 (`0,28m`, navy escuro) eliminou a parede ciano. O passe v4 sincronizou o yaw de housing, moldura e braçadeiras com o banner; captura estática POV confirmou housing alinhado, cinco lâmpadas legíveis e `FINISH` claro. **ACCEPTED**. Próximo gap visual independente: faixa inferior do HUD/touch em mobile.

### P1 — Neon: cidade procedural parece repetitiva e sem escala

A visão chase mostra prédios altos com janelas retangulares repetidas, pouca variação de silhueta e pouca ancoragem no chão. A cidade lê como paredes instanciadas, não como ambiente urbano. O problema é visual e de composição: janelas competem com a pista, mas os edifícios não fornecem profundidade graduada.

### P1 — Câmera chase: kart perde protagonismo em alta velocidade — CORRIGIDO NO DEMO

Neon usava distância extra excessiva no demo e altura/look target altos. O ajuste aceito usa extra de `0,8 m` mobile / `1,6 m` desktop no Neon e reduz a altura cinematográfica em `1,0 m`. PNG direto mobile em 15 s: `83 km/h`, kart inteiro e reconhecível, estrada à frente legível, sem crop do sujeito. O pelotão deixa de dominar a composição.

Ressalva: a faixa inferior ainda concentra velocímetro, posição, item e controles touch; isso é um achado separado de layout mobile.

### P2 — Meadow: props e vegetação sem variedade de silhueta

A variedade percebida depende demais de copas/escala. Troncos e bases de árvores aparentam compartilhar geometria/material, reduzindo a leitura de espécies e fazendo o acostamento parecer procedural repetido.

### P2 — Itens e feedback

Caixas de item são legíveis, mas os sinais de pickup/roulette não dominam claramente a pista em movimento. O efeito de brilho deve permanecer localizado; não pode contaminar kerbs, HUD ou linha de visão. Shell/banana/star e confetti não foram considerados comprovados nesta amostra quando não estavam simultaneamente visíveis; precisam de passes temporais dedicados.

### P2 — HUD/mobile: densidade perceptual, sem overlap CSS

O PNG mostra a faixa inferior visualmente carregada, mas o probe DOM real refuta colisão: HUD `y=526..696`, touch `y=748..830` (52 px de folga); speedo `112×112`; botões entre `74×74` e `80×80`, todos acima do mínimo de toque. Classificado P2 de densidade, não bug estrutural. Qualquer redesign deve preservar essas áreas e ser validado com gameplay ativo.

## Ordem do próximo loop

1. Auditar e corrigir a faixa FINISH/sinais com hierarquia estrutural.
2. Reorganizar HUD/controles mobile para liberar a faixa inferior sem perder áreas de toque.
3. Revalidar Neon com cidade procedural e grounding/AO seletivo.
4. Rodar itens, drift, turbo pads e confetti em sequências dedicadas.
5. Auditar variedade de silhueta Meadow e materiais de props.

Nenhuma conclusão de screenshot tardio foi usada para declarar qualidade de gameplay.
