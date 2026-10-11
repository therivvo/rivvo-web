# Hero Kart V2 R81 — Agentic Modeling Gates
Escopo: revisão local única no cockpit/driver; sem runtime, HUD, gameplay ou infra.

- [x] R81-01 Contrato machine-readable e scene graph com P0/P1, relações, mounts/sockets/pivots/clearances e vistas
  EVIDENCE: agentic-contract.json e scene-graph.json criados e validados no repo.
- [x] R81-02 Inspeção do R80 antes da edição registrada
  EVIDENCE: r80-inspection.json; Blender 4.0.2 abriu R80, 1041 meshes, 5 coleções, 6 materiais.
- [x] R81-03 Uma revisão local estrutural executada sobre cópia/checkpoint, sem regenerar asset inteiro
  EVIDENCE: apply_r81.py alterou somente a família KartWindshield/FlushWindshield e criou objetos R81; checkpoint local separado.
- [x] R81-04 Blockout/silhouette gate: beauty/profile/top/rear/clearance presentes e criticados
  EVIDENCE: cinco PNGs em renders/; vision rejeitou a lente como parede/placa e bloqueou cockpit/volante.
- [x] R81-05 Blender headless checkpoint novo salvo e reaberto com sucesso
  EVIDENCE: Blender 4.0.2 runner `.195`; MCP save_blend_checkpoint retornou `/opt/blender-runner/jobs/super-kart-r81/hero-kart-v2-R81-R81-rejected-visual.blend`, 655210 bytes.
- [x] R81-06 Inspeção, mesh validation e export executados quando aplicável
  EVIDENCE: MCP scene_inspect e mesh_validate executados; validation pass=false. Export não aplicável após falha visual e foi explicitamente bloqueado.
- [x] R81-07 Crítica visual multi-vista registrada; verificador independente confirmou P0 e regressões
  EVIDENCE: independent-verifier.json; 0/5 P0 visuais aprovados, 3 regressões P0, verdict REJECTED_VISUAL_GATE.
- [x] R81-08 Relatório final contém p0_fidelity, regressions, dimensions, mounts, sockets, pivots, clearance, triângulos, materiais, UV, manifold, export e tempo até primeira ferramenta
  EVIDENCE: independent-verifier.json + technical-audit.json; tempo até primeira ferramenta ~0s após início da sessão (primeira tool foi skill_view).
- [x] R81-09 Wiki/vault/nota de projeto atualizados sem segredos
  EVIDENCE: vault coding/Super-Kart-3Djs.md, coding/_index.md; wiki entity/index/log atualizados; memória atualizada.

VERDICT: BLOCKED_REJECTED — revisão real executada, mas não aprovada. R80 preservada.
