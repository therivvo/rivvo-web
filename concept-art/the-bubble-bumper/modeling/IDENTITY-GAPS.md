# IDENTITY-GAPS — veredito visual do MEU vision sobre W543 (2026-09-20)

Prancha pareada: /tmp/board-w543-pareado.png (3 linhas SIDE/FRONT/REAR, 2 colunas CONCEPT | MODELO)

## Veredito geral
"MODELO nao e producao AAA fiel. E blockout/prototipo procedural com primitives: tubos, esferas,
caixas, sem secondary shapes, sem silhueta toy, sem bevel, sem materiais PBR, sem decals. Silhueta
CONCEPT e cheia, baixa, larga, arredondada; MODELO e magro, alto, tubular, vazio. Para AAA precisa
remodelar 80%."

## *** A LICAO CENTRAL ***
O scorecard da 9/9 landmarks OK **e ao mesmo tempo** o modelo e "vazio, ve-se atraves".
Os landmarks medem o CONTORNO (perfil). Contorno certo NAO significa forma certa.
Um bloqueio pode acertar a silhueta e nao ter VOLUME nenhum. Metrica de silhueta nao substitui
leitura visual de forma — as duas sao necessarias e nao intercambiaveis.

## Gaps por item (CONCEPT -> MODELO -> o que falta)

### 1. NOSE/PARA-CHOQUE
- CONCEPT: carenagem FECHADA, volumosa, baixa e larga; corpo azul + labio/borda AMARELA espessa em U
  abracando a frente; intake central com grade de lamelas verticais; 2 aletas amarelas laterais.
- MODELO: barra/tubo PRATEADO fino, reto, flutuante, separado do chassi; 2 tocos amarelos cilindricos.
- FALTA: deletar o tubo placeholder; modelar carenagem fechada com bevel toy; labio amarelo com
  espessura; intake central rebaixado com grade de 5-6 lamelas azuis; 2 aletas amarelas verticais.

### 2. SIDEPOD
- CONCEPT: cunha AMARELA hero, inflada, alta ate a altura do joelho, arredondada, com rebaixo/sombra
  AZUL no topo onde encaixa a perna. Da largura e leitura toy ao perfil.
- MODELO: faixa amarela CHAPADA, fina, baixa, sem projecao lateral, sem altura, sem rebaixo.
  Parece textura pintada numa caixa, nao geometria.
- FALTA: extrudar lateral 2x mais largo; topo concavo azul para a perna; frente afunilada; traseira
  cheia encostando na roda traseira; edge arredondado.

### 3. ESCAPAMENTOS
- CONCEPT: 3 ponteiras GROSSAS, altas, atras do banco, leitura imediata; laterais inclinadas ~20
  para fora; parede grossa metalica; boca interna PRETA profunda.
- MODELO: ILEGIVEIS. No SIDE somem atras do motor; no REAR sao 3 caninhos brancos FINOS, retos,
  verticais, escala metade, plastico fosco, sem boca, sem inclinacao.
- FALTA: diametro +200%; inclinar laterais ~20 para fora; tubo interno escuro; anel de borda;
  material metal escovado; elevar ate a linha do banco.

### 4. REAR
- CONCEPT: hierarquia clara: (1) spoiler/apoio amarelo + barra azul ALTA com endplates amarelos
  grossos, (2) bloco central FECHADO com os 3 escapes, (3) traseira fechada + difusor azul escuro
  largo com lamelas verticais, (4) para-choque tubular duplo.
- MODELO: hierarquia QUEBRADA. Barra azul fina de vassoura; endplates minusculos; sem massa traseira;
  tudo vazado; difusor cinza claro em U aberto com lamelas apagadas; para-choque fino simples.
- FALTA: reconstruir traseira FECHADA; engrossar barra 3x + endplates capsula amarela; recolocar
  spoiler amarelo; fechar caixa traseira; difusor azul marinho com 5 lamelas; duplo tubo cinza.

### 5. PILOTO/CAPACETE
- CONCEPT: postura legivel e ativa: tronco inclinado, bracos esticados, joelhos dobrados altos, bota
  PRETA com sola sobre a pedaleira, luva preta, pescoco, macacao com dobras, gola e faixa amarela.
  Capacete: volume ovo, viseira CINZA grande envelopando, olho cartoon com brilho, faixa amarela,
  queixeira amarela.
- MODELO: bloco generico fundido. Pernas retas (tabua), sem joelho, sem bota, sem pe; bracos fundidos
  ao corpo; sem maos/luvas; volante sumiu (virou mancha amarela); capacete esfera lisa azul escura
  sem viseira, sem faixa, sem queixeira; olhos sao 2 discos brancos chapados; cockpit sem banco-cova.
- FALTA: nova rig de pose; modelar botas, luvas, volante toroide preto + coluna; capacete com viseira
  mesh separada cinza gloss + decal de olho + faixa amarela + queixeira.

## GATES DESTA FASE (por ordem de impacto na leitura)
- G26 nose: carenagem FECHADA com labio amarelo em U + intake com lamelas (nao tubo)
- G27 sidepod: volume extrudado 2x com topo concavo azul e traseira cheia
- G28 escapes: diametro 2x, inclinados 20, boca interna escura, material metalico
- G29 rear: traseira fechada + hierarquia completa (barra grossa, endplates, difusor com lamelas)
- G30 piloto: postura com bota/luva/volante + capacete com viseira separada e decals
- G31 meu vision APROVA a prancha pareada nova; SO ENTAO Sol avalia a MESMA imagem

## Nota de metodo
Usar o scorecard de silhueta (9/9) como gate de CONTORNO e o veredito visual pareado como gate de
FORMA. Nenhum dos dois substitui o outro. Um build que fecha contorno e nao le forma nao avanca.
