# Hero Kart V2 — R125

## Escopo da iteração

R125 promoveu para o gerador canônico (`scripts/blender/hero_kart_v2_build.py`) as correções técnicas do gerador autoral R124: UV por mesh, remapeamento canônico de materiais por LOD, caps triangulados, passagem final de normais e LODs com resolução determinística. A mudança é estrutural de pipeline/contrato, não empilhamento cosmético; R124 foi preservada.

## Artefatos

- Blend: `assets/hero-kart-v2/R125/hero-kart-v2-R125.blend`
- Gerador: `assets/hero-kart-v2/R125/build_r125.py`
- Render script: `assets/hero-kart-v2/R125/render_workbench_r125.py`
- Auditoria: `assets/hero-kart-v2/R125/technical-audit.json`
- Vistas do mesmo blend: `assets/hero-kart-v2/R125/renders/{beauty,profile,top,rear,clearance}.png`
- Runner: Blender 4.0.2 em GPU runner LXC105 (`192.168.0.195`); fallback Workbench surfaceless foi reportado pelo runner.

## Resultado técnico — PASS

- LOD0: 39.832 tri, 5 materiais, 0 n-gons, 0 non-manifold.
- LOD1: 21.098 tri, 4 materiais, 0 n-gons, 0 non-manifold.
- LOD2: 6.028 tri, 3 materiais, 0 n-gons, 0 non-manifold.
- Collision: 36 tri, 0 n-gons, 0 non-manifold.
- `authored_from_scratch=true`, dimensões LOD0 `1,62 × 2,4455 × 1,4093 m`.

## Primary vision — REJECT

As cinco vistas exatas foram analisadas. A revisão não fecha o P0 visual:

- Beauty/clearance: o volume frontal `R125_IntegratedCowlShell` ainda lê como tablet/bubble preto superdimensionado, bloqueando o nariz/cockpit.
- Profile: piloto/cockpit não formam silhueta contínua; cabeça/capacete aparece destacada acima do torso e a construção ainda lê mannequin/procedural.
- Top: simetria e rodas expostas são legíveis, mas o bloco frontal domina a abertura do cockpit.
- Rear: identidade traseira e simetria são legíveis, porém não compensam o P0 do cockpit/piloto.
- Clearance: não há colisão catastrófica aparente, mas a integração perceptual continua montada, não autoral.

## Sol e promoção

- Sol `gpt-5.6-sol` + `xhigh`: **NÃO INVOCADO**, protocolo correto porque o primary vision falhou.
- Exportação GLB/FBX: **BLOQUEADA**.
- Integração runtime: **BLOQUEADA**.

## Próximo experimento

Não fazer novo tuning de material/tamanho da casca. Reconstruir a classe do piloto como figura de corrida sentada, com cabeça/colar/torso/ombros em uma silhueta contínua, e trocar a casca frontal por cowl baixo aberto integrado ao corpo.
