# R125 — Dual-vision asset review ledger

- Revision: R125
- Source blend: `assets/hero-kart-v2/R125/hero-kart-v2-R125.blend`
- Exact renders reviewed: beauty, profile, top, rear, clearance
- Primary reviewer: **REJECT**

## Defects confirmed

- `P0-COCKPIT-01` — beauty/clearance: integrated cowl shell lê como tablet/bubble opaco e superdimensionado, ocultando a abertura frontal.
- `P0-PILOT-01` — profile: cabeça/capacete visualmente destacado do torso; piloto não lê como figura de corrida contínua.
- `P0-COCKPIT-02` — top: bloco frontal domina a abertura e mantém leitura de cockpit montado/procedural.

## Sol gate

Not invoked. A rejeição do primary vision bloqueia a chamada Sol; portanto não existe aprovação dupla para R125.

## Technical gate

PASS registrado em `technical-audit.json`: LOD0 39.832 tri/5 mats/0 non-manifold; LOD1 21.098/4/0; LOD2 6.028/3/0; collision 36/0.

## Promotion

Export e integração runtime bloqueados. Checkpoint preservado para comparação; próximo passe deve ser reconstrução de classe do piloto/cowl, não ajuste cosmético.
