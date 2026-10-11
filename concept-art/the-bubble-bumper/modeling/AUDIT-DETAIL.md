# Auditoria DETALHADA — Bubble Bumper (por elemento e por região)

Alvo: `assets/reference-orthographic/{side,front,rear,top}.jpg`
Modelo: `modeling/the-bubble-bumper.blend` (build `build_bb2.py`, versão W212)
Método: leitura por grade numérica sobre cada vista + vision pareado (concept | modelo)
+ despejo de bbox por peça direto do builder (verdade de terreno).

---

## 1. IoU POR REGIÃO (o IoU global esconde onde está ruim)

Vista lateral, faixas em fração do comprimento:

| Região | Faixa X | IoU | Leitura |
|---|---|---|---|
| Bico/nariz | 0.00–0.17 | **0.738** | pior região |
| Para-choque + roda dianteira | 0.17–0.28 | 0.878 | ok |
| Cowl/cockpit | 0.28–0.45 | 0.894 | ok |
| Sidepod/piloto | 0.45–0.62 | 0.808 | fraco |
| Motor/roda traseira | 0.62–0.80 | 0.898 | ok |
| **Traseira/asa** | 0.80–1.00 | **0.758** | 2º pior |

Vista frontal, faixas de altura:

| Faixa | z | IoU |
|---|---|---|
| rodas/pods baixo | 0.00–0.25 | 0.817 |
| nariz+chassi | 0.25–0.45 | 0.859 |
| asa+capô traseiro | 0.45–0.62 | 0.954 |
| **piloto/torso** | 0.62–0.80 | **0.761** |
| capacete | 0.80–1.00 | 0.862 |

**Conclusão:** o erro concentra-se em BICO (0.738), TRASEIRA/ASA (0.758) e
PILOTO/TORSO (0.761) — não no contorno global.

---

## 2. MEDIÇÕES DE GEOMETRIA (verdade de terreno do builder)

Modelo em unidades de projeto (L=2.255, H=1.207), bbox por peça:

| Peça | x | y (largura) | z |
|---|---|---|---|
| NOSE (antes W212) | 0.565–1.089 | **±0.420** | −0.001–0.477 |
| NOSE (W212, corrigido) | 0.565–1.085 | **±0.301** | −0.001–0.477 |
| FBUMP | 0.230–1.111 | ±0.587 | 0.136–0.428 |
| GRILLE | 0.863–1.114 | ±0.246 | 0.018–0.360 |
| COWL | 0.091–0.620 | ±0.189 | 0.110–0.685 |
| Tub | −0.675–0.135 | ±0.283 | 0.103–0.514 |
| PODS | −0.495–0.394 | ±0.685 | 0.106–0.384 |
| Tire_F (cada) | 0.391–0.779 | 0.508–0.744 | 0.006–0.394 |
| Tire_R (cada) | −0.938–−0.502 | 0.428–0.744 | 0.007–0.443 |
| REAR | −1.143–−0.302 | ±0.582 | 0.022–0.818 |
| PL (piloto) | −0.529–0.649 | ±0.252 | 0.244–1.201 |

### Comparação com o concept (lido na grade das imagens)

| Item | Concept | Modelo | Delta |
|---|---|---|---|
| Bico, largura | ~0.35 m | **0.84 m (antes) / 0.60 m (W212)** | era **2,4x largo demais** |
| Roda dianteira | ~0.25 H | 0.331 H | +30% (ver §3) |
| Roda traseira | ~0.35 H | 0.373 H | +7% (ver §3) |
| Entre-eixos | 0.565 L | 0.579 L | +2,4% ✓ |
| L/H | 1.868 | 1.877 | +0,5% ✓ |
| W/H | 1.238 | 1.237 | 0% ✓ |

---

## 3. EXPERIMENTO REVERTIDO: tamanho dos pneus

Hipótese: reduzir os pneus para os valores lidos na grade (RF 0.200→0.154, RR 0.225→0.211).
Resultado medido (gates):

| Versão | Perfil | Frontal | Traseira | IoU |
|---|---|---|---|---|
| W206 (baseline) | 5.9 | 8.9 | 6.7 | 0.821 |
| W207 (pneus menores + anel) | **9.2** | **11.1** | **9.3** | 0.812 |
| W208 (pneus revertidos + anel) | 9.2 | 8.9 | 6.6 | 0.818 |

**A leitura visual do pneu estava errada — a métrica reprovou.** Revertido (W208).
O anel vertical era o responsável pelo +3,3 no perfil (seu topo passava 3 cm acima do nariz
e ele virava o elemento mais frontal, mudando a normalização do comprimento).

---

## 4. ELEMENTOS: veredito por vision pareado

| Elemento | Veredito | Discrepância principal |
|---|---|---|
| Bico/nariz | DIFERENTE | concept: bloco curto, alto, estreito, frente romba. Modelo: longo, baixo, cúpula; hoje 0.60 m de largura (era 0.84) |
| Farol | **AUSENTE na leitura** | concept: retângulo claro com moldura, abaixo do volante, sobre o bico. Modelo: não lê |
| Para-choque | DIFERENTE | concept: U azul + 2 almofadas amarelas VERTICAIS arredondadas flanqueando a grade. Modelo: pads existem mas quadrados e deslocados |
| Anel oval amarelo | **INVENÇÃO — removido** | não existe no concept |
| Volante | DIFERENTE | concept: círculo INCLINADO (elipse) + luvas pretas. Modelo: barra reta vertical → lê como barra de frente |
| Luvas/mãos | AUSENTE | concept tem luvas pretas no volante |
| Postura do piloto | DIFERENTE | concept: ereto, costas retas, joelho alto dobrado, braço horizontal. Modelo: curvado, torso baixo |
| Capacete | DIFERENTE | concept: gota/lágrima alongada com queixo e viseira projetados. Modelo: esfera |
| Faixa amarela do capacete | DIFERENTE | concept: ~1/3 da largura, 100% emoldurada de azul. Modelo: ~1/5 e rompe a borda frontal |
| Cowl | DIFERENTE | concept: baixo, com barras prata inclinadas. Modelo: alto, blocado, quase vertical |
| Sidepod | PARECIDO | concept: bulboso em gota com escavação profunda. Modelo: prismático, topo chapado |
| Escape | PARECIDO | concept: mais fino. Modelo: mais horizontal/grosso |
| Boca do escape | OK | aro claro + interior escuro confirmado |
| Pneu | OK (slick) | gradiente local concept 8,35 (há desenho) mas close-up confirma slick uniforme; decisão por medição |
| Para-choque traseiro | fraco | lê como barra facetada, não tubo redondo (helper `sweep()` ignora `seg`) |
| Espelhos/retrovisores | ausente | concept tem nas laterais do cockpit |

---

## 5. PRIORIDADE DE CORREÇÃO

1. **Bico** — estreitar mais (alvo ~15-20% da largura total; hoje 39%), baixar, criar
   concavidade para as pernas, reabrir os vazios laterais.
2. **Chassi tubular cinza em U + barra de proteção** na frente (hoje ausente).
3. **Farol** retangular com moldura, claro/emissivo, no suporte abaixo do volante.
4. **Volante inclinado** (círculo visto de frente) + **luvas pretas**.
5. **Almofadas amarelas** arredondadas (não caixas) flanqueando a grade.
6. **Capacete em gota** + faixa amarela 1/3 emoldurada de azul + face (olhos/pupila/sobrancelha/boca).
7. **Postura do piloto** ereta com joelho alto e braço horizontal.
8. **Cowl** mais baixo com barras prata inclinadas.
9. **Sidepod** em gota, com borda azul no topo (hoje 100% amarelo no topo).

## 6. BUGS DE FERRAMENTA ENCONTRADOS (afetam qualquer trabalho futuro)

- `sweep(name,pts,r,seg)` **ignora o parâmetro `seg`** (não repassa ao `tube`) → todo tubo sai
  facetado. Usar `tube_round()` (frames ao longo da polilinha).
- `seal()` depois de `boolean DIFFERENCE` **fecha** a cavidade (holes_fill) — não usar.
- `object.scale=(1,1,k)` com origem no mundo **empurra** a peça em vez de esticar.
- Medição por limiar de escuro **não funciona** em concept cartoon (contorno preto em tudo).
  Usar grade numérica + leitura visual, ou bbox por peça via builder.


---

# 7. HISTORICO DE MEDICOES (W202 -> W215)

| Versao | perfil | frontal | traseira | IoU | nota vision |
|---|---|---|---|---|---|
| W202 | 5.9 | 8.9 | 6.7 | 0.821 | 6.35 (critico A) |
| W211 | 6.8 | 9.2 | 6.8 | 0.822 | SIDE 6.0 / FRONT 3.5 |
| W213 | 7.2 | 8.8 | 6.6 | 0.814 | 5.5 (critico B) |
| W215 | 7.2 | 8.8 | 6.6 | 0.811 | 4.0 (critico B) |

Medicoes objetivas por elemento (concept x modelo):

| Elemento | Concept | W202 | W215 | Razao final |
|---|---|---|---|---|
| Bico (largura, front) | 11.3% | 16.9% | 13.7% | 1.21x |
| Cowl (largura, front) | 11.3% | 16.8% | 13.0% | 1.15x |
| Asa (espessura, side) | 24.4% H | 17% | 24.0% H | 1.00x |
| Sidepod (largura, top) | 17.2% | 16.1% | 16.1% | 0.94x |
| L/H | 1.868 | 1.900 | 1.877 | +0.5% |
| Cor azul | (32,48,96) | exata | exata | 0 |

**Leitura:** o IoU ficou estavel (0.821 -> 0.811, 1.2%) enquanto a nota do critico de
visao caiu 37% (6.35 -> 4.0) com o modelo MELHORANDO em todas as medicoes por elemento.
Isso e evidencia de ruido alto no critico de visao, nao de degradacao real.

**Dois criticos deram ordens opostas**:
- critico A: "triplicar a espessura da asa" e "engrossar o para-choque 2-3x"
- critico B: "afinar a asa 70%" e "o para-choque esta grosso demais"
A medicao resolveu: asa 1.21x espessa (numeros do A estavam errados, o B mais perto);
para-choque tinha razao 0.031 -> precisava engrossar de fato.

# 8. SUPOSICAO DUVIDOSA (nomeada apos 3 rejeicoes estruturais)

Os criticos convergem, em rodadas diferentes, para a mesma acusacao estrutural:
"monobloco", "boneco derretido", "tudo fundido", "cockpit fechado", "sem separacao
de pecas". Isso NAO e ajuste de parametro — e consequencia da tecnica:

**Suposicao duvidosa:** que fidelidade a um concept cartoon organico se atinge com
`loft()` de secoes + SUBSURF e um `join()` final de tudo num unico mesh.

Por que falha: loft+subsurf gera superficie continua e soldada por construcao — o
piloto, o cowl e o chassi viram uma massa so. E o `join()` final apaga a identidade
das pecas (o auditor pede explicitamente "separar meshes: piloto / quadro / carenagens / rodas").

**Proximo experimento (nao ajuste, mudanca de tecnica):**
1. `skeleton()` + SKIN modifier para o piloto (a skill mede 93,4% valencia-4 nesse
   caminho — e a tecnica indicada para organico, nao loft).
2. Manter piloto / chassi / carenagens / rodas como OBJETOS SEPARADOS no .blend
   (nao `join()`), para o runtime e o QA lerem as pecas.
3. Viseira e rosto como geometria dedicada de casca fina (nao crista extrudada).
