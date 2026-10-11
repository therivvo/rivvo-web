# Gates: Bubble Bumper — fidelidade ESTRITA ao concept

PERGUNTA (escrita ANTES do trabalho — unlazy rule 1):
  "Atingir 100% de fidelidade ao concept do Bubble Bumper."

OPERACIONALIZACAO: o auditor antigo (qa_bb.py) era LENIENTE e reportava
IOU_MEDIA=0.823 quando a medicao honesta da 0.806. Dois defeitos:
  (1) testava o concept ESPELHADO e tomava max() sobre o flip (qa_bb.py linhas 37-45);
  (2) esticava as duas mascaras para o MESMO bbox (linha 34), destruindo a informacao
      de proporcao — um modelo largo demais era espremido ate "casar".
O auditor estrito (audit_bb.py) remove os dois, alinha por ESCALA UNICA e reporta,
por regiao, IoU + EXCESSO de volume + FALTA de volume + distancia de cor (TV) +
n de aberturas. EXCESSO/FALTA dao a DIRECAO do erro — era isso que faltava.

TETO DECLARADO: IoU = 1.000 e inalcancavel entre um render 3D sombreado e um desenho
a mao (borda, sombra e antialiasing divergem por construcao). "100%" = todos os gates
satisfeitos, incluindo a auditoria de vision por regiao aprovando cada peca critica.

VERSao MEDIDA: W404 (base corrente). Candidatos medidos: w393, w401, w402, w403, W404.

## LEDGER HISTORICO (G1-G12) — auditoria quantitativa
- [x] G1: auditor estrito roda e reporta as metricas novas
  EVIDENCE: `python3 audit_bb.py w295` emitiu 9 chaves AUD_ (IOU_MEDIA 0.807, IOU_PIOR 0.630@side_TRASEIRA, COR_TV 0.286, EXCESSO 14.2, FALTA 8.2)
- [ ] G2: IoU media estrita >= 0.900
  EVIDENCE: pendente — W404 = 0.816
- [ ] G3: pior regiao estrita >= 0.850
  EVIDENCE: pendente — W404 pior = 0.645 (side/TRASEIRA)
- [ ] G4: ZERO regioes abaixo de 0.80
  EVIDENCE: pendente — W404 = 9 regioes
- [ ] G5: no maximo 3 regioes abaixo de 0.90
  EVIDENCE: FALSO — medido 21 regioes abaixo de 0.90 no W404. Gate estava marcado [x] com
  evidencia que contradiz o EXPECT; corrigido para [ ] (nao mascarar com check invalido).
- [ ] G6: EXCESSO medio de volume <= 5%
  EVIDENCE: pendente — W404 = 12.3%
- [ ] G7: distancia de cor media (TV) <= 0.080
  EVIDENCE: pendente — W404 = 0.265 (W393 0.256; hull com cor amostrada chegou a 0.170)
- [ ] G8: as 4 vistas com IoU >= 0.880
  EVIDENCE: pendente — nenhuma vista chega a 0.880
- [x] G9: QA de malha intacto (0 non-manifold, quads >= 95%)
  EVIDENCE: W404 qa.aprovado=true, non_manifold 0, pct_quads 98.2, pct_valence4 96.2
- [ ] G10: auditoria de VISION por regiao aprova as pecas criticas
  EVIDENCE: pendente — ultimo veredito SIDE 6 / REAR 7.5 / TOP 6
- [ ] G11: nenhuma regiao com EXCESSO > 20%
  EVIDENCE: pendente — REGIOES_EXCESSO_ALTO=4
- [x] G12: nenhuma regiao com FALTA > 20%
  EVIDENCE: REGIOES_FALTA_ALTA=0

## T — TECNICA (ciclo 2026-09-19)
- [x] T1 volume derivado de medicao do concept, nao de chute
  EVIDENCE: fracao do pico do perfil SIDE: concept 0.622 == builder 0.622 (delta 0.000);
  hull 0.749 (+30 cm) -> hull rejeitado como base
- [x] T2 pecas com envelope MEDIDO
  EVIDENCE: part_bbox por peca no build (NOSE/FBUMP/COWL/Tub/PODS/CH/REAR/PL)
- [x] T3 suavizacao de curvatura aplicada antes do join
  EVIDENCE: `smooth: pecas_suavizadas=14` no build (shade_auto_smooth + apply_mods ANTES do join)
- [x] T4 QA de malha aprovado no candidato corrente
  EVIDENCE: W404 qa.aprovado=true, 0 non-manifold, 98.2% quads
- [x] T5 pecas como OBJETOS SEPARADOS no .blend (regra da skill: o join unico faz o auditor ver monobloco)
  EVIDENCE: W405 `sep_parts=14` — QA por peca: NOSE 2916v/96.4%quads/0nm, Tub 14994v/99.5%/0nm,
  PODS 14452v/97.4%/0nm, 4 pneus 97.8-97.9%/0nm, CH 98.2%, REAR 17672v/97.9%/0nm, PL 49536v/98.5%/0nm.
  Metrica IDENTICA ao W404 (0.816/0.756/0.265/12.3/8.7/9) => mudou so a estrutura, nao a forma.
  Pendencia anotada: Tub e PODS com has_uv=false.

## R — REGIOES (pior primeiro)
- [x] R1 side/TRASEIRA (pior regiao historica) melhorada de forma sustentada
  EVIDENCE: 0.636 (w393) -> 0.645 (W404); era a pior regiao desde W357
- [x] R2 top/ASA
  EVIDENCE: 0.653 (w393) -> 0.700 (W404)
- [x] R3 rear/ESCAPES tipologia: 3 ponteiras visiveis
  EVIDENCE: vision zoom 4x W404: "Da para contar 3, claramente... cilindros com boca escura redonda"
- [x] R4 top/MOTOR — diagnosticado por RUN COUNT e corrigido
  EVIDENCE: TOP xf 0.72-0.80: concept 1 run contiguo vs modelo 3 runs (vao |y| 0.30-0.51).
  Causa: `Rear_Axle` ia so ate +-0.240 (nao alcancava a face interna do pneu, 0.494).
  Fix axle_w=0.520 (W407): run count xf 0.76/0.78 => **3 -> 1** (igual ao concept);
  IoU 0.816 -> 0.818, falta 8.8 -> 8.6, regioes <0.80: 8 -> 7. xf 0.72 ainda com 3 runs (aberto).
- [ ] R5 rear/PILOTO_COSTAS 0.800 e top/BICO_U 0.838

## V — VISION
- [x] V1 vision proprio nas vistas-chave com recorte correto
  EVIDENCE: SIDE/REAR/TOP W402-W404; REAR zoom 4x W403 e W404 (diagnostico dos escapes)
- [ ] V2 aprovacao do vision proprio nas 4 vistas (mesmo objeto, sem regiao reprovada)
  EVIDENCE: pendente — ultimo veredito SIDE 6 / REAR 7.5 / TOP 6

## A — AUDITOR SUBAGENT (so apos V2)
- [ ] A1 subagent auditor com vision aprovando o mesmo candidato
  EVIDENCE: pendente — nao acionado (regra: so apos V2)

## ABANDON
ABANDON: G-IOU-100 IoU 1.000 e matematicamente impossivel: as 4 vistas do concept concordam entre si
  em ~95% (aspecto FRONT -5.4%, SIDE -4.0%, TOP -4.0%, REAR -0.5%; TOP desenhado 17% menor e REAR 16%
  maior na grade; 1 quad = 2.5 cm). Teto real por vista ~0.95.
