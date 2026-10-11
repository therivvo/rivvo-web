# The Bubble Bumper — Sol-assisted modeling plan

## Objective

Create the first modeled kart of the new concept-art lineup, matching the approved The Bubble Bumper reference rather than reusing the abandoned Hero Kart direction.

## Source

`concept-art/the-bubble-bumper/assets/the-bubble-bumper.jpg`

The source contains five labeled panels: TOPO, LATERAL, FRENTE, TRÁS and ISOMÉTRICO. Labels/grid/floor lines are reference-only and must not enter the asset.

## Planned organization

```text
concept-art/the-bubble-bumper/
├── assets/the-bubble-bumper.jpg
├── MODELING-PLAN.md
├── MODELING-GATES.md
├── modeling/
│   ├── build_bubble_bumper.py
│   ├── render_bubble_bumper.py
│   ├── bubble-bumper.blend
│   └── renders/
└── reviews/
    ├── coder-visual-qa.md
    └── sol-visual-qa.md
```

## Required loop

1. Measure source and freeze proportion contract.
2. Build primary forms only.
3. Render the five fixed views.
4. Coder vision reviews the renders; rejection returns to modeling.
5. Sol reviews the same renders plus the original source; rejection returns to modeling.
6. Add secondary forms only after both visual approvals.
7. Repeat coder → Sol for secondary forms.
8. Apply materials and custom color channels.
9. Run technical gates only after visual approval.
10. Send final five-view render to Feco via Telegram and wait for explicit approval.

## Non-negotiable visual hierarchy

1. Rounded blue/yellow bumper.
2. Large smooth tires.
3. Open cockpit with visible pilot and thick steering wheel.
4. Rounded side pods.
5. Exposed gray mechanical rear with transverse bar, springs and dual exhausts.

## Current state

V067 foi rejeitada pelo vision por visual-hull/voxelização e inconsistência multivista. V068 foi um reset autoral experimental, mas permaneceu rejeitada por shell/nose genérico, bumper visualmente separado, pods volumosos e piloto sem fidelidade extrema. V069 recuperou a construção manual de v045 e é a melhor base visual disponível: `modeling/bubble-bumper-v069.blend`, `modeling/v069-contact-sheet.png` e `modeling/renders-v069/`.

V069 ainda está **CODER_REJECT**; não foi enviada ao Sol para aprovação de asset. O job `gpt-5.6-sol/xhigh` disponível analisou a representação e confirmou SubD/manual + curvas com sockets + base humana rigada, mas não aprovou nenhum asset. Próximo experimento obrigatório: substituir as transições genéricas de shell/cowl e a base do piloto por malhas autorais SubD/rigadas, recalibrar câmeras por landmarks e repetir coder gate. Integração/export permanecem bloqueados.
