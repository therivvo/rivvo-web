# Parecer Sol (gpt-5.6-sol-900k, reasoning medium) — REBOOT DE REPRESENTACAO

> Coletado via `/home/jarvis/.hermes/scripts/deep-analysis-sol.sh` (JOB 9ca145caf13330d699fa26779e191bfa).
> Este documento e o contrato do reinicio: descartar a geometria primaria, preservar builder/medicao/render/QA.

VEREDITO: descarte a geometria primária atual e faça um reboot de representação.

Preserve o builder como sistema de medição, montagem, câmeras, render e QA. Não preserve os blobs como base da nova forma. Eles são uma representação inadequada para a identidade do concept e já foram experimentalmente refutados por 68 builds sem alteração perceptível.

A análise forte foi roteada para gpt-5.6-sol-900k, reasoning medium. O wrapper externo expirou e o job terminou sem resposta coletável; portanto, não vou fingir um “parecer do Sol”. O diagnóstico abaixo está sustentado pelas medições, histórico e falhas instrumentais já verificadas no projeto.

1. CAUSA RAIZ METODOLÓGICA

A causa não é “falta de detalhe”. É uma combinação de quatro erros estruturais.

1.1 Representação errada

Você tentou obter formas autorais alterando uma malha cuja linguagem geométrica já estava decidida pelo gerador:

- seções uniformes;
- distribuição de vértices ditada por loops;
- transições suavizadas genericamente;
- volumes fundidos em blobs;
- ausência de concavidades e planos de construção deliberados.

Um push de vértice modifica coordenadas, mas não muda necessariamente:

- a hierarquia das massas;
- a curvatura dominante;
- o tipo de seção;
- a relação entre volumes;
- os vazios entre as peças.

É como tentar converter um boneco inflável em um kart esculpido empurrando pontos da superfície. Tecnicamente possível em teoria; operacionalmente absurdo.

Regra objetiva:

- erro de posição ou escala local → ajuste paramétrico;
- erro de seção, continuidade ou curvatura → reconstrução da peça;
- erro recorrente de “bloco/blob/placa” → troca da classe de representação.

Após três correções geométricas sem mudança perceptível, o parâmetro deixa de ser suspeito. A representação, oculsão, câmera ou pipeline de render passam a ser os suspeitos.

1.2 Função objetivo incompleta

Você otimizou principalmente contorno, proporções globais e QA técnico. Isso mede apenas uma parte da fidelidade.

Dois modelos podem ter quase o mesmo contorno e serem visualmente completamente diferentes por causa de:

- distribuição interna de massa;
- concavidades;
- vazios;
- posição relativa das peças;
- linguagem de curvatura;
- contatos e encaixes;
- leitura semântica das cores.

Foi exatamente o que aconteceu: o perfil melhorou, mas o modelo continuou parecendo o mesmo.

A função objetivo correta não é um escalar como IoU ou erro médio. É um vetor:

  F = [
    escala global,
    landmarks,
    contornos por faixa,
    massa por região,
    vazios,
    curvatura,
    contatos,
    assinatura semântica,
    legibilidade das features
  ]

Se qualquer componente P0 estiver ruim, o modelo continua reprovado mesmo que a média melhore.

1.3 Ordem de dependências invertida

Você trabalhou em detalhe e deformação local antes de estabilizar:

1. registro das ortográficas;
2. datums;
3. ocupação piloto/kart;
4. volumes primários;
5. vazios e contatos;
6. formas secundárias.

A espuma toroidal, os discos da asa e a grade melhoraram a identidade porque eram assinaturas ausentes. Mas elas não conseguem compensar:

- piloto pequeno ou afundado;
- corpo estreito;
- bumper na altura errada;
- asa com volume ou posição errados.

Detalhe não corrige hierarquia de volume. Só torna um blockout errado mais caro.

1.4 Validação sem observabilidade causal

Muitos builds não respondiam claramente:

- qual objeto era responsável pela região;
- se o patch realmente executou;
- se a peça estava visível;
- se a métrica tinha resolução suficiente;
- se outro material/objeto dominava a projeção;
- se a câmera comparava ortográfico com ortográfico.

O caso de M_Face dominando a frente prova isso. Você editava “a viseira”, mas a imagem observada era majoritariamente produzida por outra superfície.

A unidade mínima de iteração precisa ser:

  uma hipótese → um owner → um probe grande → uma métrica prevista → um veredito

Sem isso, build vira loteria numerada.

2. POR QUE OS 68 BUILDS NÃO CONVERGIRAM

Eles não foram 68 passos na direção do concept. Foram majoritariamente 68 variações dentro da mesma bacia de solução.

A topologia e os geradores impunham:

- mesmas seções fundamentais;
- mesma distribuição de massa;
- mesma continuidade genérica;
- mesmos volumes dominantes;
- mesma leitura de blob.

Push, clamp e reassign atuavam depois da decisão que realmente importava.

Uma correção só é visualmente relevante quando altera pelo menos uma destas classes:

- silhouette;
- volume;
- void;
- landmark;
- semantic feature.

Mover 2–4 cm em um asset de 2,35 m normalmente é microtuning. Se a forma continua com o mesmo volume aparente, o render continuará essencialmente igual.

O salto do piloto de 45,2% para 56,7% foi real, mas ainda insuficiente frente ao alvo de 69,5%. A razão restante é aproximadamente 1,226×. Isso não significa “escale tudo mais 1,226×”: significa que a distribuição piloto/kart continua errada e precisa ser resolvida por cabeça, torso, assento e linha do cockpit, não por escala global cega.

3. O QUE DESCARTAR E O QUE PRESERVAR

Descartar:

- malha final procedural de 179 mil vértices;
- deformações P1–P101 usadas para “corrigir” os blobs;
- patches que atuam sobre posições derivadas da malha velha;
- parâmetros cuja relação causal com as features não foi demonstrada;
- qualquer target obtido comparando perspectiva com ortográfica.

Preservar:

- fontes ortográficas imutáveis e máscaras validadas;
- câmeras ortográficas, orientação dos eixos e escala oficial;
- extrator de landmarks, perfis, runs e classes de cor;
- sistema de build/render/versionamento;
- QA de manifold, quads, loose vertices e partes separadas.

Reutilizar condicionalmente:

- rodas, tubos, toróides, grade e wing tips somente se passarem isoladamente contra a referência;
- materiais como ponto de partida, não como prova de fidelidade;
- peças existentes apenas quando seu bbox, seção e assinatura visual já coincidirem com o concept.

Critério de reaproveitamento de uma peça:

  reutilizar somente se ela passar forma + dimensão + posição + contato em todas as vistas onde aparece.

“Já está feita” não é critério técnico.

4. PIPELINE CORRETO DO ZERO

4.1 Fase A — contrato e instrumento

Entrada:

- FRONT, SIDE, REAR, TOP originais;
- isométrica separada;
- comprimento oficial de 2,35 m;
- requisitos visuais e QA.

Produzir:

- `reference-contract.json`;
- máscaras e overlays por vista;
- landmarks em coordenadas normalizadas e metros;
- câmeras ortográficas congeladas;
- tabela de autoridade por dimensão.

Travas iniciais recomendadas:

- comprimento: 2,350 m;
- L/H canônico atual: 1,978;
- W/H canônico atual: 1,171;
- altura derivada: aproximadamente 1,188 m;
- largura derivada: aproximadamente 1,391 m;
- ocupação vertical do piloto: 69,5% do envelope da vista relevante.

Esses valores devem ser reemitidos pelo extrator da fonte antes do primeiro build. Não copie números antigos sem proveniência: este projeto já teve targets contaminados e contraditórios.

Gate A:

- self-test máscara×ela mesma: IoU 1,0 e erros zero;
- estabilidade dos ratios em múltiplos thresholds;
- orientação sem flip;
- overlays cobrindo o veículo, não grade/cotas;
- transformação pixel→metro validada por dois landmarks.

4.2 Fase B — datums

Crie empties ou estruturas numéricas para:

- chão e plano central;
- quatro centros de roda;
- eixos dianteiro e traseiro;
- extremos longitudinal e lateral;
- abertura do cockpit;
- centro do capacete;
- spine e sockets do bumper;
- eixo e altura da asa.

Não modele superfície ainda.

Gate B:

- cada datum dentro de ±1% do comprimento/altura da referência;
- simetria lateral dos datums centrais;
- wheelbase e tracks coerentes em SIDE/TOP/FRONT/REAR;
- projeções dos datums sobrepostas nas quatro referências.

4.3 Fase C — envelopes primários

Modele somente massas opacas simples, mas já com a classe correta:

- envelope da banheira/chassi;
- quatro envelopes de roda;
- envelope do piloto;
- sidepods;
- bumper e asa apenas como volumes aproximados.

Não use caixas genéricas se a feature é tubular. Mesmo em blockout, use:

- tubo variável para bumper;
- cunha arredondada para sidepod;
- cilindro para asa;
- elipsoide/cage para capacete;
- banheira com abertura real.

Gate C:

- razões globais em ±2%;
- landmarks P0 em ±3%;
- piloto entre 67% e 72% da ocupação-alvo;
- nenhum envelope flutuante;
- pior faixa de contorno dentro de ±12%.

4.4 Fase D — primary forms autorais

Reconstrua por zonas, não como monólito procedural:

- tub/nose/cockpit;
- sidepod esquerdo;
- sidepod direito;
- piloto e capacete;
- frente/bumper;
- traseira/asa.

Ferramentas headless adequadas:

- `mesh_from()` para cages explícitas;
- lofts com seções desenhadas por landmark;
- SubD com loops de suporte deliberados;
- bmesh inset/extrude para recessos;
- shrinkwrap/projeção sobre cages de referência;
- curves/tubes com raio por estação;
- SKIN apenas para massas orgânicas conectadas do piloto.

O shell precisa ser autoral no sentido real: seções escolhidas pela referência, não geradas uniformemente só porque um loop é conveniente.

Gate D:

- clay ortográfico em quatro vistas;
- ISO para linguagem volumétrica;
- contorno superior e inferior por estação;
- concavidade do cockpit visível;
- leitura em thumbnail;
- nenhum detalhe decorativo usado para esconder forma ruim.

4.5 Fase E — secundários e aparência

Só depois do primary PASS:

- grade com cinco divisões;
- tread em V;
- toróides amarelos;
- endplates em disco;
- sockets, suportes, volante e encaixes;
- viseira, faixa, queixeira e rosto.

Depois:

- materiais semânticos;
- toon em 2–3 bandas;
- outline;
- transparência controlada;
- iluminação fixa de avaliação.

Gate E:

- features count-sensitive verificadas em close;
- cada feature com pelo menos 30 px na evidência;
- cor medida no flat pass;
- volume julgado no beauty pass;
- outline não pode alterar a máscara usada pelo gate geométrico.

5. COMO USAR AS ORTOGRÁFICAS COMO BLUEPRINT

5.1 Registre cada painel separadamente

Não trate os quatro arquivos como se tivessem o mesmo zoom.

Para cada painel:

1. remova moldura, grid, texto, centro e cotas da máscara;
2. detecte landmarks compartilhados;
3. ajuste transformação de similaridade;
4. valide o ajuste num terceiro landmark;
5. salve a transformação, nunca apenas a imagem redimensionada.

Transformação por painel:

  p_mundo = s_vista · R_vista · p_pixel + t_vista

Para ortográficas alinhadas, R normalmente é discreta: troca/inversão de eixos, não rotação livre arbitrária.

5.2 Calibração por dois pontos

Escolha dois landmarks distantes e inequívocos:

- centro do eixo dianteiro;
- centro do eixo traseiro;
- ou extremos do comprimento dimensionado.

Então:

  escala = distância_mundo / distância_pixels

Use um terceiro ponto como validação. Não derive escala da largura do seu próprio modelo; isso torna o target circular.

5.3 Autoridade por eixo

Quando os painéis discordarem:

- SIDE governa comprimento, altura longitudinal, wheelbase e perfil;
- TOP governa largura ao longo do comprimento e tracks;
- FRONT governa largura/altura frontal e simetria;
- REAR governa traseira, asa, escapes e tracks traseiros;
- ISO governa curvatura, sobreposição, profundidade e linguagem de forma.

A isométrica não deve sobrescrever uma dimensão ortográfica estável. Ela desempata volume e transições que a silhueta ortográfica não revela.

Registre conflitos explicitamente:

  feature: sidepod shoulder
  ortho: largura e posição obrigatórias
  iso: curvatura mais inflada
  decisão: manter extents ortográficos; usar ISO para seção/curvatura

5.4 Perfis por faixas

Use pelo menos 100 estações no eixo dominante, não 21 ou 41 quando a peça tem poucos centímetros.

Por estação, extraia:

- top;
- bottom;
- left;
- right;
- número de runs;
- classe semântica dominante.

SIDE deve ter `z_top(x)` e `z_bottom(x)`.
TOP deve ter `y_left(x)` e `y_right(x)`.
FRONT/REAR devem ter larguras por faixa de altura.

Não reporte apenas erro médio. Registre mediana, p95, máximo e localização do pior erro.

5.5 Landmarks mínimos

Inclua, no mínimo:

- quatro centros e diâmetros de roda;
- ponta do nariz e extremos do bumper;
- cockpit front/rear/top/bottom;
- centro e extremos do capacete;
- centro, altura e envergadura da asa.

Cada landmark deve conter:

  vista, pixel, fração do painel, posição em metros, confiança, fonte e tolerância.

6. MÉTRICAS E TOLERÂNCIAS

Use gates graduais, não um limiar final desde o primeiro build.

Blockout:

- L/H e W/H: ±2%;
- wheel centers e peak fraction: ±2% do comprimento;
- piloto: ±3 pontos percentuais de ocupação;
- pior faixa de envelope: ±12%;
- simetria central: erro ≤1%.

Primary forms:

- mediana de contorno: ≤5%;
- p95: ≤10%;
- nenhuma faixa P0 acima de 12%;
- pior IoU regional ≥0,74;
- landmarks P0 em ±2%;
- excesso e falta reportados separadamente.

Secondary forms:

- contagem exata das features;
- dimensão de feature em ±5%;
- posição em ±3% do eixo dominante;
- legibilidade ≥30 px;
- contato/clearance dentro de 5–10 mm onde deve haver união.

Não transforme esses thresholds em religião. Primeiro meça a inconsistência interna dos painéis. O gate nunca pode exigir precisão maior que a própria referência permite.

Agregação correta:

- gate global só passa se o pior P0 passa;
- média serve para tendência;
- p95 serve para qualidade geral;
- máximo localizado serve para decidir a próxima peça;
- score visual não substitui nenhum dos três.

7. ERROS CLÁSSICOS DE BLOCKOUT

7.1 Escala global correta, massa interna errada

Sintoma: L/H passa, mas piloto continua pequeno e kart vazio.

Detecção: ocupação piloto, centroide por classe e área relativa piloto/chassi.

7.2 Silhueta correta com concavidade ausente

Sintoma: IoU razoável, mas cockpit parece bloco sólido.

Detecção: run count, máscara de vazio, depth/normal pass e seção transversal.

7.3 Detalhe antes de primary forms

Sintoma: grade, tread e parafusos existem, mas a leitura geral continua genérica.

Detecção: thumbnail de 128–192 px e clay sem materiais. Se não reconhece o asset, detalhe está proibido.

7.4 Peça “correta” porém enterrada ou ocluída

Sintoma: objeto existe e QA passa, mas pixels não aparecem.

Detecção: object-ID pass, bbox por material/objeto e contagem de pixels visíveis. Meça a superfície hospedeira e a protrusão real.

7.5 Ajustar a peça errada

Sintoma: parâmetro muda muito, métrica fica idêntica.

Detecção: probe grande, face count antes/depois, owner map da região e teste de visibilidade. Se a geometria mudou e pixels não, há oclusão ou métrica errada.

8. LOOP DE ITERAÇÃO SEM BUILDS CEGOS

Cada build deve ter uma ficha deste tipo:

  revision: B004
  hipótese: piloto parece afundado porque helmet_top está 8% abaixo do target
  owner: PilotCage + SeatDatum
  mudanças permitidas: somente esses dois componentes
  probe: elevar 12% H, deliberadamente grande
  métrica prevista: pilot_occupancy +8..12 pp
  regressões protegidas: L/H, cockpit opening, wheel landmarks
  aceitar: target melhora e nenhuma regressão P0 >2%
  reverter: target piora ou regressão excede limite
  resetar representação: probe executa, mas leitura visual não muda

Regras operacionais:

1. Uma hipótese estrutural por build.
2. Probe primeiro; microajuste depois.
3. Resultado byte-idêntico exige provar que o patch executou.
4. Três rejeições da mesma classe exigem troca de representação.
5. Cada build emite relatório machine-readable e comparação com a revisão anterior.

Antes de renderizar:

- assert do revision stamp;
- assert de nomes esperados;
- assert de bboxes alterados;
- assert de face count do owner;
- assert de arquivos esperados.

Depois:

- quatro vistas ortográficas;
- ISO;
- máscaras;
- métricas;
- paired board;
- veredito aceitar/reverter.

9. PRIMEIROS 10 BUILDS DO REBOOT

B001 — Instrumento vazio

Objetivo: câmeras, unidades, eixos, chão, escala e overlays.
Geometria: apenas datums.
Proibido: modelar shell ou piloto.

B002 — Rodas e envelopes

Objetivo: quatro centros, diâmetros, larguras, wheelbase e tracks.
Geometria: cilindros-envelope sem tread.
Gate: projeções em SIDE/TOP/FRONT/REAR.

B003 — Massa piloto versus massa kart

Objetivo: acertar 69,5% de ocupação e posição do pico.
Geometria: cages simples de cabeça, torso e tub.
Proibido: rosto, viseira e roupa.

B004 — Tub/cockpit autoral

Objetivo: banheira, abertura, dip e relação assento/piloto.
Geometria: cage explícita com SubD e recessos reais.
Gate: top e bottom profiles mais máscara de vazio.

B005 — Nose e bumper

Objetivo: nariz, tubo frontal, altura, profundidade e sockets.
Geometria: shell autoral + tube de raio variável.
Proibido: pads amarelos e grade.

B006 — Sidepods

Objetivo: cunha inflada, comprimento, vale da perna e contatos.
Geometria: dois cages espelhados inicialmente, mas independentes.
Gate: SIDE/TOP/FRONT e continuidade com tub.

B007 — Piloto conectado

Objetivo: pose sentada, mãos/volante, torso, helmet e cockpit.
Geometria: SKIN/cage conectado, depois refinamento autoral.
Proibido: olhos, sorriso, stripe e material final.

B008 — Traseira e asa

Objetivo: massa traseira, suporte, cilindro alto e discos laterais.
Gate: REAR/SIDE/TOP, altura e envergadura medidas.

B009 — Assinaturas P0

Objetivo: duas espumas toroidais, grade 5 divisões, tread em V, wing discs, viseira e queixeira.
Gate: contagem exata, posição e legibilidade em crops diretos.

B010 — Appearance e QA de produção

Objetivo: cel shading, outline, transparência, materiais, união técnica e 14 partes.
Gate: visual multivista primeiro; manifold/quads/loose/sep_parts depois.

10. COMO CUMPRIR `sep_parts == 14` SEM PARECER PRIMITIVE STACK

Não modele pensando “preciso de 14 objetos”. Modele pensando em superfícies e assemblies coerentes. Só depois compile o resultado técnico em 14 ilhas watertight.

Uma decomposição defensável:

1. tub + nose + cockpit;
2. sidepod esquerdo;
3. sidepod direito;
4. bumper tubular;
5. espuma frontal esquerda;
6. espuma frontal direita;
7. roda dianteira esquerda;
8. roda dianteira direita;
9. roda traseira esquerda;
10. roda traseira direita;
11. corpo do piloto;
12. capacete/visor/queixeira;
13. asa com endplates unidos;
14. módulo mecânico traseiro.

Dentro de cada parte:

- tread deve ser integrado à roda ou unido por boolean;
- grade deve nascer integrada ao tub/nose;
- sockets devem ter transição ou encaixe físico;
- endplates precisam tocar e unir ao cilindro da asa;
- detalhes de material não precisam criar novas ilhas.

Pipeline técnico:

  authored objects
  → QA por objeto
  → boolean/bridge dentro de cada assembly
  → exatamente 14 sólidos manifold
  → join sem soldar assemblies entre si
  → `loose_parts(final) == 14`

`join()` sozinho não reduz ilhas. `remove_doubles` também não une superfícies apenas intersectadas. Use boolean union, bridge loops ou topologia contínua dentro de cada assembly.

O gate deve verificar ambos:

- `len(loose_parts(final)) == 14`;
- cada ilha individualmente manifold e sem vértices soltos.

Aparência de primitive stack é evitada por:

- interfaces com sockets/recessos;
- continuidade tangencial deliberada;
- espessuras coerentes;
- overlap construtivo controlado;
- sombras de contato reais.

11. TOON E OUTLINE

Não use toon/outline para resgatar forma ruim.

Ordem correta:

1. clay beauty para volume;
2. silhouette/mask para geometria;
3. flat pass para cor;
4. toon para linguagem;
5. outline para acabamento.

O outline deve ser excluído da máscara geométrica; caso contrário ele infla artificialmente IoU e dimensões.

Para Blender headless:

- Shader to RGB/ColorRamp quando o engine permitir;
- alternativa robusta: ramp de iluminação no material;
- outline por Freestyle/Line Art ou shell invertida somente após prova de que o engine respeita culling;
- viseira em material separado, com transmissão controlada e prova de que olhos/rosto continuam legíveis.

12. REGRA DE CONVERGÊNCIA

Pare de perguntar “a nota subiu?”. Pergunte:

- o pior landmark melhorou?
- o pior band error caiu?
- a massa mudou na direção prevista?
- o vazio correto apareceu?
- a feature ficou legível?
- alguma vista protegida regrediu?

Aceite uma revisão somente quando:

  target melhorou
  AND nenhum P0 regrediu
  AND mudança é perceptível
  AND mecanismo foi comprovado

Se o número melhora mas o render parece igual, a mudança ficou abaixo do limiar perceptivo ou a métrica está otimizando algo irrelevante.

Se o render melhora e um agregado cai marginalmente, examine a região e a linguagem de forma antes de reverter. Uma média não tem autoridade para restaurar uma primitiva visualmente errada.

Gates verificados: 8/8, `ALL MET`.

Próxima ação em menos de dois minutos: renomeie o build atual como `LEGACY_REFERENCE_ONLY` e crie `reference-contract.json` com os quatro valores iniciais: `length_m=2.35`, `target_L_H=1.978`, `target_W_H=1.171`, `pilot_height_fraction=0.695`.
