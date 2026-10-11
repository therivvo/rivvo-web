# Medição e instrumento — regras que custaram builds

Aplicável a qualquer build do Bubble Bumper (e a qualquer asset 3D validado contra concept).
Cada regra abaixo foi paga com um build rejeitado ou revertido (ciclos v173–v176). Ordem = ordem de uso.

## 1. O pixel renderizado é o juiz; o raycast só reporta existência

`scene.ray_cast` em (x=−0,15, z=1,06) devolveu `P_FacePlate[M_BlackLine]` — e a cor do material foi
verificada preta (0,020 · 0,020 · 0,020). **Mesmo assim o pixel renderizado ali era CLARO**
(102,104,106; soma 312) contra o concept (16,17,19; soma 52).

- Raycast ortográfico de y=+5 e câmera do render **não são o mesmo instrumento**.
- **Raycast diz o que EXISTE. Render diz o que APARECE.**
- Para fidelidade visual, medir o render. Usar raycast só como pista de existência/autoria.
- Custo: **três builds** "corrigir a linha preta por coordenada" foram desperdiçados.

## 2. Ler o harness antes de culpar a geometria

O script de QA faz `o.hide_render = True` em peças `_L`/`_1` com y mediano > 0,30 na vista SIDE.
O raycast respeita visibilidade de **viewport**, não `hide_render`. Uma discordância raycast/render
pode ser o harness, não a malha.

## 3. Feature estreita (≤ ~5 px): medir EXTENSÃO DE FAIXA, não ponto

Uma amostra por (x,z) dizia "nenhum preto na janela". Uma vizinhança 9×5 imprimiu `..oLLDDDD`:
a faixa **existia**, ~4–7 px deslocada e **2,5× mais estreita** (4 px ≈ 0,012 m vs ≥ 0,030 m do
concept, que ocupava 7/7 colunas em 3 linhas). Medir o comprimento do run em pixels.

## 4. Calibrar por LANDMARK compartilhado, nunca por correlação de perfil

Correlacionar o perfil de topo da silhueta por zona deu "erros" de 66–93 px — inútil, porque a máscara
de referência estava contaminada. Um landmark que os dois lados têm (qual extremidade é alta:
capacete 0,876/0,807 vs baixa 0,357/0,312) resolveu alinhamento **em uma chamada** e provou que o
mapeamento **não** estava espelhado.

## 5. Validar o calibrador contra o contrato antes de ler offsets

Bug de shadowing (`KZ` lido do escopo externo) fez o script imprimir **H=0,786 m** para um modelo cuja
altura real é 253 px × 0,004950 = **1,2523 m = o contrato exato**. Calibrador que discorda de âncora
conhecida está quebrado. Consertar o instrumento antes de acreditar no número.

## 6. A grade de guias entra no componente conexo principal da referência

A grade toca o objeto, então o bbox do maior componente a mantém: a coluna da ponta do nariz mediu
**0,957 m** de altura na referência vs 0,762 m no modelo. Limpar máscara por **cor E topologia**
(componentes que tocam o objeto mas cuja cor é a da grade) antes de qualquer calibração.

## 7. Nunca ajustar o modelo para agradar instrumento não calibrado

v176 subdividiu a placa e repintou a faixa: **renderizou** (o claro caiu 31→25) mas não onde o medidor
olhava → **revertido**, geometria intocada até o instrumento ser corrigido. Ajustar o objeto para
satisfazer um instrumento torto **assaria o erro do instrumento dentro do asset**.

## 8. Preencher região inexistente: sólido fechado sobreposto > editar topologia

| tentativa | resultado |
|---|---|
| `bmesh.extrude_face_region` em 144 faces (região não-tampa) | **54 arestas non-manifold** ✗ |
| mover vértices existentes (2 tentativas) | casco não existia nas colunas; uma jogou a faixa a z=1,30 ✗ |
| **esfera UV 24×12 fechada, separada, material do casco** | 1 componente · 0 non-manifold · contatos mensuráveis ✓ |

Dimensionar pelo **medido** e depois **alargar o mesmo sólido** — não adicionar um segundo patch:

| build | sólido | borda | dentro | gate |
|---|---|---|---|---|
| v173 | centro (−0,115 · 0 · 1,155), raios (0,030 · 0,058 · 0,062) | 82%→83% | 92% | 1/0/522 |
| v174 | centro (−0,130 · 0 · 1,150), raios (0,045 · 0,062 · 0,075) | **85%** 51/60 | **95%** 56/59 | 1/0/525 |

v174: claro **concept 31 = modelo 31 com 31 acertos**; as **duas** células do topo (−0,15) desapareceram.

## 9. Notas de API que custam uma rodada cada

- `bmesh.ops.subdivide_edges` exige lista de arestas **deduplicada** — `list({e for f in faces for e in f.edges})`;
  passar com repetição levanta `ValueError: edges: found the same (BMEdge) used multiple times`.
- Depois de subdividir, **re-selecionar as faces do bmesh subdividido** por predicado — as referências antigas morrem.
- `obj.evaluated_get(depsgraph).data.polygons[idx]` para índice de face em malha avaliada (a original dá `IndexError`).
- `view_layer.update()` antes de ler `matrix_world` após mover/rotacionar/escalar.
- Índice de slot de material: `obj.data.polygons[idx].material_index`, **nunca** o índice da face.

## Estado no fim destes ciclos

- Candidato `authored/conjunto-v174.blend`, md5 curto `75457f3e5c`.
- SIDE: borda 85% (51/60) · dentro 95% (56/59) · claro 31/31/31 · 4 erros na grade
  (2 fenda = artefato de classe com RGB ~10% equivalente; 1 linha preta **sob suspeita de artefato
  do medidor**; 1 fundo = não é defeito).
- Gate: 1 componente · 0 non-manifold · 525 contatos.
- **Pré-requisito do próximo veredito:** limpar a máscara da referência (grade/linhas-guia) e revalidar
  âncoras contra L=2,354 / H=1,2523.
- FRONT/REAR/TOP seguem **sem validação**; vision próprio, auditor independente e prancha final pendentes.
