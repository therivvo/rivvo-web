# Parecer Sol (gpt-5.6-sol-900k, reasoning medium) — 2026-09-20

PROVENIENCIA VERIFICADA:
  JOB_ID=932d7364d5f56318f9dd40c45e227eb5
  STATUS=completed | EXIT_CODE=0 | 15942 bytes
  MODEL=gpt-5.6-sol-900k | PROVIDER=openai-codex | REASONING=medium

NOTA: os dois lancamentos feitos pelo coder (ea78583f 04:42, f7293bac 04:44) morreram com .out VAZIO
(stale_or_finished). O parecer valido veio do job 932d7364, iniciado 04:38, que completou as 04:49.

---
1. Procedural não é o problema; usá-lo como autor da identidade é

O builder deve continuar, mas com responsabilidade reduzida.

Mantenha procedural:

- datums, eixos, escala final e restrição de 2,35 m;
- câmeras, luzes e passes BEAUTY/FLAT/máscara;
- montagem dos 14 objetos;
- materiais, nomes, coleções e export;
- auditoria de bbox, simetria, manifold e proporções;
- peças repetitivas: rodas, fixadores, tubos, parafusos e aletas.

Pare de gerar proceduralmente:

- sidepods;
- nose/cowl e transição para o cockpit;
- cockpit/banheira;
- capacete, rosto, torso e pose;
- carenagem traseira e suas transições.

Essas peças concentram a identidade do Bubble Bumper. Loft genérico, dome, box e sweep conseguem preencher volume, mas não conseguem decidir corretamente onde uma superfície deve comprimir, criar ombro, quebrar curvatura, afundar ou se fundir com outra.

Alternativa concreta: pipeline híbrido com assets autorais por zona

Estrutura recomendada:

    modeling/
      authored/
        cockpit-pilot-v001.blend
        sidepods-v001.blend
        nose-bumper-v001.blend
        rear-module-v001.blend
      contracts/
        zone-landmarks.json
        semantic-materials.json
      builder/
        assemble_bubble_bumper.py
        render_evidence.py
        audit_bb.py

Método por zona:

1. Criar uma cage manual de baixa densidade, alinhada às vistas registradas.
2. Modelar a superfície primária em SubD, com loops colocados onde o concept muda de curvatura.
3. Esculpir apenas para acertar volume e transições.
4. Retopologizar ou corrigir a cage manualmente.
5. Criar recessos e cortes reais, não pintura que finge profundidade.
6. Salvar cada zona como `.blend` versionado.
7. O builder importa essas malhas e aplica somente transformações contratuais.

Para o piloto:

- blockout articulado ou base conectada;
- pose definida por pelvis, coluna, ombros, cotovelos, mãos e capacete;
- sculpt para proporção chibi;
- retopo depois da pose aprovada;
- rosto em UV/textura sobre patch dedicado, não botões geométricos.

Reprodutibilidade não exige que cada vértice seja regenerado por fórmula. Um `.blend` versionado, com transforms aplicados, nomes estáveis e um script determinístico de montagem, é perfeitamente reproduzível.

Critério de aceite da mudança de pipeline:

- rebuild limpo importa os quatro assets autorais sem intervenção;
- dimensões finais continuam L = 2,35 m e x = [-1,20; 1,15];
- cada asset tem versão e hash registrados no manifesto;
- alterar o renderer ou reconstruir a cena não muda a geometria;
- nenhuma forma identitária depende novamente de `pod_e`, `cowl_k` ou dezenas de constantes correlacionadas.

W516 deve ser tratado como último experimento diagnóstico do pod procedural, não como início de outra sequência de ajustes. Se a leitura continuar “mesmo kart com uma bolha diferente”, encerre essa classe de representação.

2. Sequência de maior alavancagem

1) Reconstruir arquitetura de massas e espaços negativos

Mudança:

- cockpit realmente escavado;
- piloto reposicionado como massa vertical dominante;
- quebra de perfil mais marcada;
- largura recuperada no corpo/pods, não aumentando pneus.

Por quê:

O modelo já acertou L/H. O problema não é mais o envelope externo; é onde existe massa e onde deveria existir ar. O concept tem um degrau de perfil de 0,132, enquanto W516 entrega 0,085. Essa suavização excessiva apaga a hierarquia cockpit → piloto → traseira.

Aceite:

- pico do capacete na mesma fração longitudinal do concept;
- pelvis dentro da banheira, não sobre o kart;
- mãos alcançando o volante;
- espaço negativo legível entre braço, coluna, joelho e sidepod;
- degrau principal com pelo menos 85% da amplitude medida no concept;
- em thumbnail de 256 px, o piloto deve parecer ereto e encaixado sem zoom.

2) Substituir os sidepods por superfície autoral de duas camadas

Construção correta:

- corpo externo amarelo baixo, longo e bulboso;
- laterais relativamente planas;
- ponta dianteira em cunha descendente;
- ombro/corcova traseira controlada;
- rebaixo azul central fisicamente escavado;
- transição suave para o cockpit, sem meia-esfera.

Por quê:

Os sidepods ocupam uma fração enorme da lateral e do topo. São assinatura visual barata de corrigir em relação ao piloto. W508 estava subdimensionado; W515 inflou o volume errado. Isso prova que falta controle local de superfície, não mais amplitude global.

Aceite:

- corpo amarelo e cobertura/rebaixo azul aparecem como dois níveis;
- o azul não cobre toda a superfície superior;
- perfil não lê como caixa nem meia-esfera;
- nenhum trecho reto longo domina o topo;
- largura corporal aumenta sem deslocar o limite externo dos pneus;
- diferença de área semântica amarelo/azul da zona ≤ 5 pontos percentuais por vista;
- vision pareada classifica o componente como “PARECIDO” ou “IGUAL” em SIDE e TOP.

3) Reconstruir nose + bumper como um único gesto de design

Mudança:

- bico baixo, volumoso e pontudo;
- shell azul/amarelo;
- bumper azul, integrado à frente;
- pads amarelos claros e semanticamente separados;
- remover leitura de barra prata reta.

Por quê:

A frente é a “cara” do veículo. Hoje ela comunica outro material, outra construção e outra época de design. Mesmo com perfil correto, o modelo parece outro kart porque o primeiro landmark é semanticamente errado.

Aceite:

- bumper não pode ser classificado visualmente como cromado/prateado;
- bico termina em cunha ou cápsula baixa, não em barra;
- pads amarelos permanecem legíveis nas vistas FRONT, SIDE e ISO;
- bumper possui sockets/transições, sem tubos apenas atravessando carenagem;
- a composição continua reconhecível com material clay e no BEAUTY.

4) Refazer piloto, capacete e rosto como um conjunto

Mudança:

- tronco mais ereto e compacto;
- capacete alto/arredondado conforme o concept;
- faixa amarela larga e contínua;
- olhos grandes, separados e com sorriso;
- queixeira com volume;
- volante, mãos e coluna formando cadeia funcional.

Por quê:

O piloto é o landmark de maior saliência semântica. “Capacete achatado + dois botões brancos + corpo reclinado” muda personagem, pose e personalidade ao mesmo tempo.

Aceite:

- ângulo do torso dentro de ±5° do concept lateral;
- centro das mãos dentro de 3% da altura/comprimento normalizados do alvo;
- faixa amarela ocupa a proporção medida no capacete, com tolerância de ±10%;
- dois olhos e sorriso legíveis a 256 px;
- capacete continua reconhecível em SIDE, FRONT e ISO;
- não existem interseções aparentes entre mãos, volante, braços e cockpit.

5) Reconstruir traseira e só depois fazer o passe AAA

Mudança estrutural:

- plástico azul fechado;
- três escapamentos, com boca central dominante;
- coletores e sockets coerentes;
- eliminar chassis tubular aberto que não existe;
- remover molas douradas expostas quando contradizem a referência;
- limpar pneus e retirar listras brancas inexistentes.

Passe AAA posterior:

- bevels dependentes da escala;
- espessura real em bordas;
- seams e junções;
- variação moderada de roughness;
- cavidades, lips e sockets;
- normais limpas e materiais semanticamente coerentes.

Aceite:

- traseira reconhecível como a mesma arquitetura em REAR e ISO;
- três bocas contáveis sem zoom, central claramente maior;
- ausência de peças inventadas;
- nenhuma peça parece flutuar ou apenas atravessar outra;
- detalhe secundário somente depois de todas as cinco vistas passarem o blockout estrutural.

3. Métricas que correlacionam melhor com percepção

Não substitua a EMA atual por outro número único. Use um vetor de métricas com pisos obrigatórios por zona. Otimizar uma média única só cria um Goodhart mais sofisticado.

A. Erro de landmarks

Para cada vista e componente, marque pontos como:

- ponta do bico;
- centros de roda;
- extremos dos pods;
- abertura do cockpit;
- centro e topo do capacete;
- volante;
- centros dos três escapes.

Normalize por largura ou altura da própria vista:

    E_landmark = mediana(||p_modelo - p_concept|| / extensão_da_vista)

Reporte também o pior landmark.

Gate recomendado:

- mediana ≤ 2,5%;
- nenhum P0 > 5%;
- landmarks compartilhados devem concordar em pelo menos duas vistas.

B. Distribuição de massa por faixas

Divida cada vista em uma grade semântica, por exemplo 12 × 8. Para cada célula, calcule a fração ocupada:

    O[i,j] = pixels_da_silhueta_na_célula / pixels_da_célula

Compare concept e modelo por L1 ou Earth Mover Distance.

Isso detecta:

- piloto baixo demais;
- traseira vazia;
- pods ocupando altura errada;
- massa excessiva no chassi;
- frente fechada quando deveria haver ar.

Gate:

- diferença média de ocupação ≤ 8 pontos percentuais;
- nenhuma célula P0 > 15 pontos;
- reporte excesso e falta separadamente.

C. Perfil de curvatura e assinatura de degraus

Reamostre o contorno por comprimento de arco e calcule:

    κ(s) = |x' y'' - y' x''| / (x'² + y'²)^(3/2)

Não compare cada pixel. Compare:

- quantidade de picos relevantes;
- posição normalizada dos picos;
- sinal da curvatura;
- amplitude dos 5–8 picos principais;
- maior degrau;
- comprimento de trechos quase retos.

Para W516, o dado decisivo já existe:

- modelo: degrau 0,085;
- concept: 0,132.

Gate inicial:

- posições dos picos principais dentro de ±3% do comprimento;
- amplitudes dentro de ±15%;
- maior degrau ≥ 85% do alvo;
- nenhum trecho reto criado onde o concept possui uma curva identitária.

D. Espaços negativos e concavidades

Crie máscaras específicas para:

- abertura do cockpit;
- vão braço/volante;
- vão roda/carenagem;
- rebaixo azul do pod;
- bocas dos escapes;
- cavidades frontal e traseira.

Meça:

- área normalizada;
- centroide;
- aspect ratio;
- número de runs por faixa;
- profundidade visível em uma passagem de normals/clay.

Gate:

- área de cada vazio P0 dentro de ±10%;
- mesmo número de componentes/runs;
- centroide dentro de 3% da vista;
- rebaixo deve alterar a silhueta interna e o normal pass, não apenas a cor.

E. Assinatura semântica de cor por zona

No FLAT, classifique pixels por família e luminância:

- azul escuro/médio/claro;
- amarelo;
- neutro escuro/médio/claro;
- outros.

Faça isso por componente, não globalmente.

Exemplo:

    C[zona, classe] = pixels_da_classe / pixels_da_zona

Além da fração, calcule a interseção espacial por classe. Duas zonas com 40% amarelo não são equivalentes se o amarelo está no lugar errado.

Gate:

- fração por família dentro de ±5 pontos percentuais;
- IoU espacial da cor dominante ≥ 0,80;
- nenhuma inversão semântica, como corpo azul onde o concept possui shell amarelo;
- FLAT usado somente para cor; BEAUTY continua obrigatório para forma.

F. Silhueta multi-escala

Use signed distance transform ou IoU em três escalas:

- 64 px: leitura global/thumbnail;
- 256 px: massas secundárias;
- resolução nativa: bordas e detalhes.

Uma forma útil:

    E_sil = média(|SDT_modelo - SDT_concept|) / diagonal_da_bbox

Gate:

- 64 px precisa passar primeiro;
- nenhuma região com IoU < 0,75;
- regiões P0 desejavelmente ≥ 0,82;
- uma melhora na escala nativa não compensa regressão em 64 px.

G. Relações e oclusões

Represente o design como grafo:

    mão → volante
    volante → coluna
    coluna → cockpit
    pod → shell
    escape → coletor → housing
    bumper → socket → nose

Para cada aresta, registre:

- contato;
- gap;
- interseção;
- oclusão esperada;
- visibilidade por vista.

Essa métrica captura “montagem de peças” versus objeto projetado.

Gate:

- 100% das relações P0 comprovadas em pelo menos uma vista;
- zero partes flutuantes;
- zero conexões realizadas apenas por interpenetração visual.

Agregação sem Goodhart

Não use:

    score_final = 0,3 IoU + 0,2 cor + ...

Use ordem lexicográfica:

1. identidade em thumbnail;
2. landmarks e massas;
3. vazios/concavidades;
4. curvatura e linguagem de forma;
5. cor semântica;
6. detalhe e QA técnico.

Uma revisão só avança se nenhum P0 estiver abaixo do piso. A média não pode esconder uma traseira errada porque quatro rodas estão perfeitas.

Mantenha a ISO como holdout: não use a vista isométrica para ajustar coordenadas. Use-a apenas para verificar se as quatro ortográficas produziram um volume tridimensional coerente.

4. Onde o procedural para

Mover uma zona para modelagem autoral quando qualquer dois destes sinais ocorrerem:

1. Três variações reais da zona não mudam o veredito visual.
2. Mudanças de 2–5 cm melhoram métrica, mas são imperceptíveis na prancha.
3. A correção exige concavidade, ombro, pinching ou transição localizada.
4. Um parâmetro melhora uma vista e destrói outra porque controla área demais.
5. O componente possui duas superfícies semânticas dentro do mesmo contorno, como shell amarelo + rebaixo azul.
6. O crítico repete termos de classe: “caixa”, “meia-esfera”, “tubo”, “chapado”, “parece outro kart”.
7. O contorno está próximo, mas o componente continua semanticamente errado.
8. A peça precisa ser corrigida por sculpt após cada geração.

Checklist da fronteira:

Procedural pode continuar se:

- a geometria é repetitiva;
- sua identidade vem de dimensões simples;
- os parâmetros têm efeitos locais e previsíveis;
- a peça não governa o reconhecimento do kart;
- duas ou mais vistas respondem corretamente ao mesmo parâmetro.

Manual/autoral começa se:

- a transição entre superfícies é parte da identidade;
- existe recess/pinching/coroa/ombro específico;
- a peça domina thumbnail ou postura;
- a curvatura precisa ser editada localmente;
- a mesma bbox admite formas perceptualmente muito diferentes;
- a peça já falhou duas revisões estruturais na mesma classe.

O builder não deve morrer. Ele deixa de “inventar o kart” e passa a “montar, provar e reproduzir o kart”.

5. Cinco defeitos que mais produzem “não é AAA”

1) Linguagem de forma genérica nas massas primárias

Causa:

- lofts, domes e sweeps produzem volumes matematicamente limpos, mas sem transições autorais;
- perfil excessivamente suave;
- caixa, bolha e tubo usados onde o concept possui cunha, ombro, depressão e rebaixo.

Correção:

- cages SubD autorais para shell, pods, nose e rear;
- clay gate antes de materiais.

2) Piloto/capacete sem postura e personalidade do concept

Causa:

- piloto reclinado;
- capacete achatado;
- rosto reduzido a dois pontos;
- mãos/volante/cockpit sem cadeia funcional.

Correção:

- reconstruir pose inteira de pelvis até capacete;
- face via UV;
- validar SIDE, FRONT e ISO em conjunto.

3) Frente semanticamente errada

Causa:

- bumper parece cromado;
- bico parece barra;
- pads e transição azul/amarelo não comunicam a “cara” do design.

Correção:

- nose e bumper como conjunto integrado;
- materiais corretos;
- sockets e espessuras reais.

4) Sidepods com volume e divisão de cor errados

Causa:

- W508 fino demais;
- W515 inflado como meia-esfera;
- ausência do rebaixo azul central;
- uma única massa tentando representar duas peças.

Correção:

- shell amarelo autoral + rebaixo/cobertura azul separado;
- validação SIDE e TOP por massa, curvatura e cor.

5) Traseira sem arquitetura coerente e com detalhes inventados

Causa:

- bloco/chassis tubular aberto;
- molas e listras que contradizem o concept;
- escapamentos pequenos e sem hierarquia;
- falta de housing e sockets.

Correção:

- módulo traseiro fechado;
- três bocas, central maior;
- eliminar peças sem contraparte;
- materiais metálicos restritos à mecânica real.

Resultado da análise profunda:

- diagnóstico confirmado: o problema é de representação, não de mais precisão no perfil;
- L/H está resolvido; W/H ainda exige redistribuição de massa, mas não justifica outro sweep de pneus;
- o wrapper gpt-5.6-sol/medium excedeu o timeout externo e não retornou parecer coletável nesta janela; nenhuma conclusão foi atribuída falsamente a ele;
- ledger executável: 6/6 gates atendidos em `/home/jarvis/consultas/bubble-bumper-strategy-2026-09-20/GATES.md`.

Próxima ação em menos de 2 minutos: congele W516 como baseline e crie `sidepods-v001.blend`; não rode W517 alterando `pod_e`.
