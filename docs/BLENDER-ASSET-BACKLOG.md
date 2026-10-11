# Super Kart 3D.js — backlog de assets Blender

Data: 2026-09-10  
Fonte de direção: análise independente Sol `20260910_000044_71e2ac` (`gpt-5.6-sol`, `xhigh`)  
Escopo: elementos 3D que podem substituir primitivas/procedural sem mexer no HUD  
Regra: nenhum asset entra no produto sem A/B visual desktop/mobile, mesma câmera/seed/pista e validação de colisão.

## Critério de ordenação

Prioridade = impacto na leitura do jogador × repetição em tela × ganho de autoria visual × segurança de integração. Os budgets abaixo são alvos iniciais, não licença para reduzir geometria sem evidência.

## Backlog ordenado

### P0 — Kart herói procedural → asset Blender modular

**Por que:** é o elemento do jogador; vision apontou identidade fraca durante gameplay e grounding pouco explícito.

**Diretriz de arte do Sol:** kart arcade premium, silhueta agressiva e reconhecível sem depender da pintura; cockpit baixo, para-lamas largos, escapamento e traseira icônica; proporções coerentes com as rodas atuais.

**Escopo Blender:** chassi modular, quatro rodas separadas, volante, piloto simplificado, para-choques e asa traseira; três kits cosméticos intercambiáveis; pivôs, escala e footprint padronizados.

**Budget inicial:** LOD0 ≤12k tris; LOD1 ≤6k; LOD2 ≤2k; até três materiais; atlas 1024²; GLB ≤2.5MB; LOD1 padrão no mobile.

**Risco:** alto — pivôs das rodas, dimensões, suspensão e origem precisam coincidir com `KartPhysics`/câmera.

**Aceitação:** silhueta identificável frente/lateral/traseira; quatro rodas apoiadas; sombra de contato contínua; zero clipping em drift, salto e colisão; player distinguível dos rivais em A/B desktop/mobile.

### P0 — Rampas e boost pads

**Por que:** vision apontou rampas com aparência de placa plana e pouca integração física.

**Diretriz de arte do Sol:** rampa com espessura, estrutura inferior e perfil de lançamento evidente; boost pad como módulo tecnológico embutido, não placa colada.

**Escopo Blender:** rampas curta/média/larga, transições de entrada/saída, laterais, suportes e pad emissivo separado para animação/material.

**Budget inicial:** cada módulo ≤2.5k tris; colisão convexa ≤24 faces; até dois materiais; atlas 512²; instancing obrigatório.

**Risco:** alto — superfície visual precisa coincidir com inclinação, colisão e trajetória.

**Aceitação:** perfil legível a 25m; rodas acompanham a superfície; salto produz arco visual coerente; zero degrau invisível, z-fighting ou descontinuidade; boost preserva legibilidade mobile.

### P0 — Skyline Neon modular

**Por que:** skyline repetitivo e fachadas genéricas reduzem diferenciação da Neon City.

**Diretriz de arte do Sol:** skyline cyberpunk em camadas, com torres de coroamento distinto, passarelas, antenas e volumes assimétricos; evitar blocos repetidos e fachadas genéricas.

**Escopo Blender:** kit de oito módulos combináveis: quatro torres, dois mid-rises, uma passarela e um rooftop; sockets para sinais/antenas; bases fechadas para grounding.

**Budget inicial:** torres LOD0 ≤4k tris e LOD1 ≤1.2k; módulos distantes ≤500 tris; um atlas 1024²; até dois materiais; instancing por módulo.

**Risco:** médio — pode conflitar com fog, enquadramento e geração procedural existente.

**Aceitação:** pelo menos seis silhuetas distintas visíveis por volta; nenhuma repetição adjacente; foreground/midground/background separados; bases não parecem flutuar; A/B mantém custo e leitura mobile.

### P1 — Sinalização e chevrons

**Por que:** sinais atuais são funcionais, porém repetitivos e visualmente próximos de placas planas.

**Diretriz de arte do Sol:** sinalização de corrida robusta, inclinada e iluminada, com chevrons volumétricos e linguagem específica por pista.

**Escopo Blender:** chevrons simples/duplos, placas de curva, postes, bases e seis molduras variantes; faces gráficas separadas para atlas/decal.

**Budget inicial:** peça ≤800 tris; LOD distante ≤120; um atlas 512² por pista; instancing obrigatório.

**Risco:** médio — orientação path-relative, legibilidade noturna e prevenção de placas embutidas.

**Aceitação:** direção correta em 100% das curvas amostradas; legível a 30m; suportes tocam o solo; zero placas invertidas/embutidas; sem sequência de três cópias idênticas.

### P1 — Landmarks e foliage Meadow

**Por que:** Meadow precisa de identidade por setor; vegetação procedural repetida não cria marcos memoráveis.

**Diretriz de arte do Sol:** campo alpino estilizado com marcos memoráveis e massas orgânicas: moinho, celeiro, rochedos, árvores e arbustos de silhuetas variadas.

**Escopo Blender:** três landmarks e oito módulos de vegetação/rocha; clusters com pivô no solo e variações de escala/cor preparadas.

**Budget inicial:** landmark ≤5k tris com LOD1 ≤1.5k; cluster ≤350 tris; atlas 1024²; alpha overdraw mínimo; instancing obrigatório.

**Risco:** médio — foliage pode ocultar pista, aumentar overdraw mobile ou atravessar barreiras.

**Aceitação:** pelo menos três landmarks reconhecíveis por volta; ausência de padrão repetitivo evidente; faixa permanece legível; zero vegetação flutuante ou invadindo a pista.

### P2 — Start/finish gantry

**Por que:** é o landmark dominante de largada/chegada e hoje depende de volumes simples.

**Diretriz de arte do Sol:** pórtico icônico de automobilismo futurista, estrutura mecânica crível, massa superior controlada e leitura clara de largada/chegada.

**Escopo Blender:** estrutura modular, pilares, travessa, luminárias, painel central e suportes; colisão simplificada independente.

**Budget inicial:** LOD0 ≤6k tris; LOD1 ≤2k; LOD2 ≤500; até três materiais; atlas 1024²; GLB ≤1.5MB.

**Risco:** médio — clearance, alinhamento com spline e compatibilidade com efeitos FINISH existentes.

**Aceitação:** centralizado sobre a pista; clearance seguro para kart/câmera; pilares apoiados; texto/luzes legíveis sem bloquear HUD/horizonte.

### P2 — Item box / pickup

**Por que:** item boxes atuais funcionam, mas são oportunidades de silhueta e feedback material mais autorais.

**Diretriz de arte do Sol:** pickup facetado com núcleo energético, moldura física e silhueta reconhecível sem emissive; coerente com Neon e Meadow.

**Escopo Blender:** caixa externa, núcleo separado, aro/base e três variantes de moldura; pivô central para rotação.

**Budget inicial:** LOD0 ≤1.5k tris; LOD1 ≤400; até dois materiais; atlas 512²; emissive sem transparência pesada; instancing obrigatório.

**Risco:** baixo-médio — escala, pivot, hitbox e rotação/respawn.

**Aceitação:** identificável a 20m sem bloom; base/sombra ancora o pickup; rotação sem wobble; coleta e respawn sem mesh residual.

### P3 — Guardrails e props de borda

**Por que:** repetição de borda e props genéricos afetam acabamento, mas têm menor impacto que kart/pista/skyline.

**Diretriz de arte do Sol:** kit de borda funcional e variado, com guardrails segmentados, postes, pneus, cones e barreiras reforçando velocidade sem poluir a composição.

**Escopo Blender:** trechos reto/curvo, terminal, poste, stack de pneus, cone e barreira; sockets e dimensões comuns para montagem procedural.

**Budget inicial:** segmento ≤700 tris; props ≤300; LOD distante ≤100; atlas 512²; colisores simples; instancing obrigatório.

**Risco:** médio — continuidade em curvas, colisões falsas, clipping e repetição.

**Aceitação:** juntas sem gaps; props apoiados; zero invasão da pista; variantes quebram repetição sem aumentar draw calls; A/B preserva leitura da rota.

## Pipeline recomendado

1. Criar especificação e escala a partir dos footprints atuais.
2. Modelar em Blender com pivôs explícitos e coleções `LOD0`, `LOD1`, `LOD2`, `COLLISION`.
3. Aplicar transforms, validar manifold/normais/n-gons/escala e salvar `.blend` checkpoint.
4. Renderizar preview Eevee e revisar silhueta/grounding antes do export.
5. Exportar GLB com materiais mínimos, atlas e nomes estáveis.
6. Integrar atrás de feature flag ou candidato QA, sem substituir baseline imediatamente.
7. Testar A/B em Meadow/Neon desktop/mobile com mesma seed/câmera/viewport.
8. Só promover após vision temporal, custo medido, colisão e regressão AI/áudio/build.

## Fora do escopo Blender

- HUD, lap, posição, tipografia, touch controls e focus ring: são UI/DOM/CSS.
- Fog, bloom, ColorGrade e pós-processamento: são render pipeline.
- GroundY, respawn e física: são lógica/colisão; o Blender fornece apenas malha visual e colisores compatíveis.

## Próximo asset recomendado

Começar pelo **kart herói P0**, porque resolve simultaneamente identidade, silhueta, grounding e leitura de player. O primeiro protótipo deve ser um único kart completo com preview turntable, LODs, colisão e A/B no player; não modelar oito assets em paralelo.

## Revisão do plano pelo Sol — 2026-09-10

Sessão: `20260910_002508_48b7e3` (`gpt-5.6-sol`, `xhigh`)

### Ordem revisada

1. P0.1 kart herói
2. P0.2 rampas + grounding
3. P0.3 skyline modular
4. P1 sinais e landmarks Meadow
5. P2 gantry e item box
6. P3 guardrails

### Primeiro vertical slice

Um kart herói + uma família de rampas + três silhuetas de torre Neon, todos com LODs, colisão simples separada, GLB e A/B GPU desktop/mobile com câmera, iluminação e seed fixas.

### Budgets revisados

- Rampas: `3k/1.2k/300 tris` por módulo (LOD0/1/2).
- Torres: `4k/1.2k/300 tris`.
- Landmarks: `5k/1.5k/400 tris`.
- Item box: `1.5k/400/100 tris`.
- Os demais budgets originais permanecem válidos como alvo inicial.

### Riscos e decisões

- O budget deve limitar também materiais e draw calls, não apenas triângulos.
- Detalhe não substitui silhueta: o kart precisa continuar reconhecível.
- Grounding depende de sombra, pivô, escala e contato das rodas.
- A/B só é válido com enquadramento, iluminação e estado equivalentes.
- Gantry, item box e guardrails não entram no primeiro slice.
- Collider deve ser uma malha simples separada, nunca a malha visual diretamente.

## Execução do primeiro asset — v7

- `SK3D_HeroKart_v7.blend` criado no Blender 4.0.2 com chassi, cockpit, piloto, volante, rodas/pivôs, asa, escapes, sockets FX e colliders separados.
- `mesh_validate`: PASS, zero non-manifold e zero n-gons após triangulação de export.
- GLB candidato exportado: `583,668 bytes`; SHA-256 documentado em `docs/BLENDER-HERO-KART-V1.md`.
- Vision interna e Sol aprovaram o blockout para integração, não como arte final.
- Runtime integration ainda pendente: validar grounding, drift, salto, colisão e A/B GPU antes de promover.
