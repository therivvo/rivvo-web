## ESTADO ATUAL — W282 (2026-09-19)

Medido por: `python3 qa_bb.py W282`

| metrica | valor | gate | passa |
|---|---|---|---|
| IOU_MEDIA | 0.823 | >=0.830 | NAO |
| IOU_P10_MEDIA | 0.768 | >=0.800 | NAO |
| IOU_MENOR_REGIAO | 0.714 | >=0.780 | NAO |
| PERFIL_LAT_PCT | 6.0 | <=6.5 | SIM |
| FRONTAL_PCT | 7.1 | <=9.5 | SIM |
| TRASEIRA_PCT | 8.1 | <=9.5 | SIM |
| COR_MAXDELTA | 5 | <=5 | SIM |
| QA (non-manifold) | 0, 98.4% quads | 0 | SIM |

5 de 14 gates. Baseline da sessao (W265) era IOU 0.813 / ASA 0.697; W282 = 0.823 / 0.777.

# GATES — Bubble Bumper: fidelidade ao concept

**PERGUNTA (rule one):** o modelo 3D deve ser a versão 3D do concept art — mesma forma,
mesmas proporções, mesmas peças, mesma leitura em todas as vistas.
Todo gate abaixo é uma medida dessa pergunta.

Baseline medido: **W233** = IoU media 0.809 · **pior região 0.680** (FRONT/CAPACETE)
· P10 media 0.743 · perfil 7.4% · frontal 11.5% · traseira 10.7% · cor Δ7 · 0 non-manifold

QA executável: `cd modeling && python3 qa_bb.py <versao>`
Checker: `cd modeling && node ~/.hermes/profiles/coder/skills/unlazy/scripts/gate-check.mjs GATES.md`

---

- [x] G1: QA tecnico aprovado no build (0 non-manifold, >=95% quads)
  EVIDENCE: W250 aprovado=true, verts=86212, non_manifold=0, pct_quads=98.4, valence4 96.8 (log job 20260919-045200-b3f7c5)

- [ ] G2: pior regiao (menor IoU parte x vista) >= 0.780  [baseline W233 0.684 -> W253 0.705]
  CHECK: python3 qa_bb.py W282 | grep ^IOU_MENOR_REGIAO
  EXPECT: IOU_MENOR_REGIAO=0\.[789]

- [ ] G3: media das 10 piores regioes >= 0.800  [baseline W233 0.740 -> W253 0.748]
  CHECK: python3 qa_bb.py W282 | grep ^IOU_P10_MEDIA
  EXPECT: IOU_P10_MEDIA=0\.[89]

- [ ] G4: IoU de silhueta media >= 0.830  [baseline W233 0.809 -> W253 0.808]
  CHECK: python3 qa_bb.py W282 | grep ^IOU_MEDIA
  EXPECT: IOU_MEDIA=0\.8[3-9]

- [x] G5: erro do perfil lateral <= 6.5%  [baseline W184 16.7 -> W258 5.9]
  EVIDENCE: qa_bb.py W258 -> PERFIL_LAT_PCT=5.9 (asa comprida: o contorno superior em xf 0.88-0.99 passou a ter a asa, que o concept tem)

- [x] G6: erro da vista frontal <= 9.5%
  EVIDENCE: qa_bb.py W265 -> FRONTAL_PCT=7.1

- [x] G7: erro da vista traseira <= 9.5%
  EVIDENCE: qa_bb.py W265 -> TRASEIRA_PCT=8.1

- [x] G8: desvio de cor por canal <= 5
  EVIDENCE: qa_bb.py W265 -> COR_MAXDELTA=5

- [ ] G9: TOP/ASA >= 0.780 (planta traseira: asa fina, nao chapa)  [baseline W233 0.684 -> W253 0.705]
  CHECK: python3 qa_bb.py W282 | grep ^IOU_TOP_ASA
  EXPECT: IOU_TOP_ASA=0\.[789]

- [ ] G10: TOP/BICO_U >= 0.780 (planta dianteira)  [baseline W233 0.693 -> W253 0.716]
  CHECK: python3 qa_bb.py W282 | grep ^IOU_TOP_BICO_U
  EXPECT: IOU_TOP_BICO_U=0\.[789]

- [ ] G11: FRONT/PARACH >= 0.780 (para-choque visto de frente)  [baseline W233 0.702 -> W253 0.706]
  CHECK: python3 qa_bb.py W282 | grep ^IOU_FRONT_PARACH
  EXPECT: IOU_FRONT_PARACH=0\.[789]

- [ ] G12: SIDE/TRASEIRA >= 0.780 (silhueta traseira de perfil)  [baseline W233 0.708 -> W253 0.708]
  CHECK: python3 qa_bb.py W282 | grep ^IOU_SIDE_TRASEIRA
  EXPECT: IOU_SIDE_TRASEIRA=0\.[789]

- [ ] G13: auditor independente sem contexto do autor confirma fidelidade
  EVIDENCE: pending

- [ ] G14: modelo, builder, ficha, gates e provas commitados no repo
  EVIDENCE: pending

<!--
HISTORICO (nao apagar): W184 7.1/22.7/18.8/0.786 -> W202 5.9/8.9/6.7/0.821 -> W233 7.4/11.5/10.7/0.809.
CORRECAO DE INSTRUMENTO (importante): ate W233 as regioes de FRONT/REAR do qa_bb usavam faixas no eixo
ERRADO (colunas = largura, nao altura). Isso fazia FRONT_CAPACETE marcar 0.680 constante em 4 geometrias
diferentes — probe quebrado, nao achado. Com o eixo correto, FRONT_CAPACETE = 0.984 (o MELHOR, nao o pior)
e o pior real e TOP_ASA 0.684. Regra: metrica que nao responde a uma mudanca real de geometria esta quebrada.
As notas do critico de visao oscilaram 3-8 na mesma peca enquanto as metricas melhoravam: nota = ruido.
Gate impossivel: usar linha propria "ABANDON: G<n> <motivo>".
-->
