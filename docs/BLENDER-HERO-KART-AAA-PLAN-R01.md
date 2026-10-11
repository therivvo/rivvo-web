# Hero Kart AAA — plano de reconstrução r01

## Direção
Reconstruir de fora para dentro. A carroceria contínua define o kart; rodas, suspensão, aero e piloto complementam a forma.

## R115/R116 — loop retomado em 2026-09-11
- R115 foi uma tentativa de camada estrutural sobre R114 e foi rejeitada pelo vision próprio em todas as cinco views: caixas/cilindros fizeram cockpit, piloto e windshield parecerem montagem artificial.
- R116 voltou ao gerador autoral limpo `scripts/blender/hero_kart_v2_build.py`, executou no Blender 4.0.2/LXC105 e gerou cinco renders reais; vision próprio ainda rejeitou por leitura de mannequin, windshield/volante ambíguos e inconsistência estrutural nas vistas.
- Auditoria técnica R116: `all_structural_gates_pass=false`; LOD0 `42892` tri/6 mats/2268 non-manifold, LOD1 `23376`/5/1464, LOD2 `11288`/5/888, COLLISION `36`/manifold. Export/runtime continuam bloqueados.
- Sol foi consultado com `gpt-5.6-sol` + `xhigh` para estratégia visual sobre R114, mas excedeu aproximadamente 10 minutos sem resposta; timeout não é aprovação.
- Próximo experimento obrigatório: corrigir o gerador autoral e o contrato técnico antes de qualquer nova alteração visual; não adicionar primitivas sobre R114/R115.

## Referências de linguagem
- Mario Kart 8 Deluxe: relação carroceria/cockpit/piloto e rodas expostas.
- Sonic & All-Stars Racing: fluxo longitudinal, nariz agressivo e aero funcional.
- Crash Nitro Kart: proporções exageradas e traseira robusta.

## Ordem executável
1. Congelar anchors: quatro centros de roda, solo, banco, volante e `FRONT=-Z`.
2. Criar meia carroceria quad com Mirror, seções nariz/eixo dianteiro/dash/cockpit/cintura/eixo traseiro/cauda.
3. Abrir cockpit na casca, com banco, coluna e pedais.
4. Derivar para-lamas e ombros da casca; proibir cápsulas decorativas.
5. Modelar hubs, uprights, wishbones e amortecedores com endpoints reais.
6. Modelar traseira, difusor, escapes ocos e asa com perfil/endplates.
7. Criar piloto separado e articulado, em pose sentada com mãos/pés em contato.
8. Gerar LODs orientados à silhueta; validar/reimportar GLB.

## Budgets
LOD0 38–52k tris; LOD1 16–22k; LOD2 5–7.5k; até 5 materiais; até 8 draw calls.

## Rejeição imediata
- placa com caixas/cápsulas anexadas;
- cockpit pousado ou fenders colados;
- suspensão/asa/escape sem conexão funcional;
- piloto mannequin/LEGO ou sem contatos;
- falha em ortográficas, budget ou reimportação.

## R46–R53 — loop persistente concluído com aprovação dupla — 2026-09-10
- R46–R52 foram reiniciadas após cada rejeição/falha, sem integração de runtime.
- R53: vision próprio e Sol `gpt-5.6-sol`/`xhigh` aprovaram a mesma versão; sessão Sol `20260910_153744_40deff`.
- Build/render Blender 4.0.2 passaram; validação estrutural continua rc 2 por gates históricos de LOD/topologia e está explicitamente separada da aprovação visual.
- Detalhamento reproduzível: `docs/HERO-KART-V2-R46-R53.md`.

## Auditoria Sol R53 — bloqueadores reportados — 2026-09-10
- Sessão `20260910_174347_1384c0`, `gpt-5.6-sol`, `xhigh`, vision; nenhum arquivo editado.
- **Para-brisa: REJEITAR.** P0: ancorar em quatro pontos simétricos; eliminar extensão sobre volante/piloto; manter borda traseira ≥ `0,08D` à frente do aro; folga lateral ≥ `0,05D` por antebraço; largura entre `0,72–0,78Wc`; nenhuma travessa terminando suspensa; fixadores espelhados até 2 px; centro alinhado ao kart até `0,01Ws`.
- **Personagem/clearance: REJEITAR.** Centro do pescoço/cabeça/casco com diferença ≤ `0,03Wh`; pescoço visível de `0,12–0,18Hh`; casco envolvendo têmporas, mandíbula e nuca; visor único preso por dois pivôs; queixeira fundida às laterais; folga queixeira–topo do aro ≥ `0,18Hh`.
- **Volante: REJEITAR.** Remover placa rosa; reconstruir coluna coaxial ao hub; hub entre `0,19–0,23D`; aro/raios definitivos antes das mãos; mãos em `150°/30°`, penetração de pegada visível, punhos alinhados aos antebraços em ≤10°; sem colisão com painel/raios.
- P1 posterior: refazer câmeras, HANS/colar, bevels, normais e re-renderizar beauty/profile/top/clearance sem ocultar defeitos.
- Veredito Sol: **R53 REJEITAR**; nenhum bloqueador deve ser tratado como aprovado.

## R45 — micro-canopy elevado rejeitado — 2026-09-10
- Loop reiniciado após R44; viseira elevada acima do volante, com dois apoios e casca curta.
- Vision próprio rejeitou: para-brisa lê como prateleira/placa horizontal; perfil mostra lâmina plana; piloto continua procedural e cockpit perde proporção.
- Sol não foi chamado porque o gate próprio falhou.
- Próximo passo exige abandonar o bloco procedural inteiro e reconstruir cockpit/driver/para-brisa como asset dedicado; não continuar ajustes locais.

## R44 — micro-canopy do Sol rejeitado — 2026-09-10
- Loop reiniciado imediatamente após R43, com micro-canopy curto conforme orientação do Sol: casca fechada fumê, 0,44m de largura, 0,18m de altura/profundidade, dois apoios e sem pedestal.
- Vision próprio: **APROVAR** inicialmente, considerando beauty/profile/top; porém a leitura no beauty ainda é ambígua.
- Sol `gpt-5.6-sol`, `xhigh`, sessão `20260910_130255_a937e4`: **REJEITAR** — peça opaca/facetada em forma de cunha/tablet, sem curvatura fumê contínua nem dois apoios claramente legíveis; piloto/capacete visíveis.
- A validação tripla (`20260910_130138_54c1a3`) falhou por `Broken pipe`; a validação mínima retornou o veredito.
- Hipótese encerrada: ajustes incrementais dessa geometria não estão resolvendo a leitura. Próxima etapa requer reconstrução dedicada do cockpit/para-brisa fora do bloco procedural.

## R43 — monocoque Sol dimensional rejeitada — 2026-09-10
- Implementada a solução dimensional do Sol: casca fechada fumê, largura 0,72m, dois apoios inferiores, sem pedestal central e render dedicado `windshield-top.png`.
- Vision próprio rejeitou todas as vistas: beauty lê painel alto/largo; profile lê placa plana; top lê retângulo/asa; clearance mostra cockpit/personagem ainda sobrepostos.
- Sol não foi chamado nesta R43 porque o gate próprio falhou.
- Após múltiplas tentativas, o bloco procedural atual está esgotado. Próximo passo: reconstrução dedicada do cockpit/driver/para-brisa com asset separado e câmera própria; não continuar variando o mesmo painel.
- Estado: WIP preservado; não integrar nem enviar para aprovação.

## R42 — viseira fumê clara rejeitada — 2026-09-10
- Aplicada a terceira via solicitada ao Sol: casca fechada curta, material Principled opaco claro, sem alpha/transmission, dois apoios e highlight.
- Blender executou e renderizou; vision próprio **REJEITOU**: a peça lê como lâmina/console horizontal diante dos braços, não para-brisa funcional; piloto/capacete ficaram legíveis, mas o cockpit perdeu proporção.
- Sol não foi chamado nesta R42 porque o gate próprio falhou.
- Hipótese confirmada: o bloco procedural atual mistura a viseira com o plano do volante; próxima etapa precisa de um asset dedicado de cockpit/para-brisa com ângulo de montagem e câmera próprios, não novas variações de material.
- WIP preservado; sem aprovação dupla.

## R41 — monocoque fechada rejeitada pelo vision — 2026-09-10
- Implementada a terceira via do Sol como casca fechada fina, 18 vértices/8 quads, Alpha=1/Transmission=0, dois apoios e sem face inferior.
- Blender executou e renderizou beauty/profile, mas vision próprio **REJEITOU**: a peça continua lendo como painel horizontal/plano e o perfil não mostra um para-brisa funcional; personagem segue com anatomia/capacete de manequim procedural.
- Sol não foi chamado nesta rodada porque meu gate falhou.
- Hipótese confirmada: o bloco procedural atual não consegue atingir a leitura AAA solicitada por ajustes locais. Próxima etapa requer reconstrução dedicada do cockpit e piloto, com geometria de vidro/visor independente e views de revisão específicas.
- Estado: WIP preservado; sem aprovação dupla e sem envio ao Feco.

## R40 — solução Sol monocoque curta rejeitada — 2026-09-10
- A viseira foi reduzida para 18 vértices/8 quads, dois apoios e material fumê opaco conforme o plano do Sol.
- Vision próprio: **REJEITAR**. O resultado virou uma placa horizontal diante do peito, não um para-brisa; piloto/volante/capacete ficaram mais comprometidos na composição.
- Sol não foi chamado nesta R40 porque o gate próprio falhou.
- Hipótese confirmada após várias abordagens: o script procedural atual não consegue representar cockpit/para-brisa AAA com substituições locais. Próximo passo exige reconstrução dedicada do cockpit/driver e uma câmera de revisão própria, não mais ajuste de superfície/material.
- Estado: WIP preservado; não enviar para aprovação nem integrar.

## R39 — terceira via do Sol rejeitada pelo vision — 2026-09-10
- Implementada a recomendação Sol: viseira monocoque fumê com 18 vértices/8 quads, Alpha=1/Transmission=0, sem face inferior, sem pedestal central e dois apoios.
- Blender executou, mas vision próprio **REJEITOU**: o resultado ainda lê como painel vertical escuro, com moldura/apoios pouco funcionais e cockpit bloqueado.
- Sol não foi chamado nesta rodada porque meu gate próprio falhou.
- Após múltiplas abordagens, a hipótese duvidosa está confirmada: este harness procedural não está produzindo uma viseira AAA confiável; a próxima etapa deve reconstruir o cockpit/para-brisa em um asset dedicado e validar perfil/topo antes do beauty.
- WIP preservado; não integrar nem enviar para aprovação.

## R37 — aeroscreen aberto rejeitado — 2026-09-10
- Aplicada a mudança de abordagem indicada pelo Sol: remover a face ampla e usar aro curvo, suportes e reflexos opacos, sem depender de alpha/transmissão.
- Blender executou e o render saiu sem crash, mas vision próprio **REJEITOU**: o conjunto lê como grade/barras dianteiras, não para-brisa/defletor funcional; a moldura compete com volante e personagem.
- Sol não foi chamado nesta rodada porque o gate próprio falhou.
- Após múltiplas linhas de ataque (painel opaco, shader transparente, Glass BSDF, ciclos bloqueado e aeroscreen aberto), hipótese duvidosa: o runner Eevee 4.0.2 não está produzindo uma representação de vidro confiável nesse asset; continuar variando o mesmo conceito não é correção.
- Estado: WIP preservado; integração e aprovação final bloqueadas. Próximo passo requer pipeline de material/render diferente ou modelagem dedicada fora deste harness.

## R36 — teste de transparência e renderer bloqueado — 2026-09-10
- Superfície transparente direta foi testada; o render Eevee mostra fundo/objeto preto através dela e não comprova a lente de forma útil.
- Tentativa alternativa em Cycles CPU falhou com `RuntimeError: Build without OpenImageDenoiser` antes do primeiro frame; harness retornado para Eevee.
- Vision próprio: **REJEITAR** o para-brisa R36; Sol não foi chamado porque o gate próprio falhou.
- Estado: WIP preservado. Próxima solução deve usar material/geometry compatível com Eevee 4.0.2 ou trocar o pipeline de render sem depender de OIDN.

## R35 — transparência Eevee bloqueada — 2026-09-10
- Tentativa: Principled translúcido com `Alpha=0.05`, transmissão e `DITHERED`; Blender executou sem erro.
- Vision próprio: **REJEITAR** — o para-brisa continua como painel ciano uniforme; braços/torso/volante não ficam visíveis através da lente.
- Sol não foi chamado nesta R35 porque o gate próprio falhou. Hipótese duvidosa confirmada: o material/transparência do Eevee 4.0.2 neste pipeline não produz evidência visual confiável.
- Próximo ataque deve trocar a abordagem: separar lente renderizável do painel, usar geometria de vidro dedicada compatível com o runner ou validar em outro renderer; não continuar ajustando alpha às cegas.

## R29 — para-brisa rejeitado — 2026-09-10
- Tentativa final aumentou a curvatura vertical e em planta para nove seções, mas o resultado visual virou um volume em cunha opaco no perfil.
- Vision próprio: **REJEITAR**. A peça não lê como vidro/defletor AAA; o piloto/cockpit ficam parcialmente ocultos.
- Sol ainda não foi chamado nesta R29 porque meu gate próprio falhou.
- Hipótese confirmada: variações incrementais da mesma lâmina não resolvem. Próxima etapa precisa substituir a superfície por geometria de arco/curva dedicada, provavelmente um defletor em seção cilíndrica com perfil lateral separado e materiais/review camera próprios.
- Estado: WIP preservado; sem aprovação visual dupla e sem integração.

## R27 — para-brisa rejeitado pelo Sol — 2026-09-10
- R27 adicionou superfície de 9×3 seções com arco quadrático forte em planta e perfil, `Solidify`, `Bevel` e render dedicado `windshield-profile.png`.
- Vision próprio: **APROVAR** o para-brisa; o perfil mostra arco e espessura suficientes para leitura de defletor.
- Sol `gpt-5.6-sol`, `xhigh`, sessão `20260910_102322_44b604`: **REJEITAR**; o painel ainda aparenta placa escura/plana/angular, sem curvatura 3D, transparência ou ancoragem convincente.
- A análise tripla anterior (`20260910_102210_63fa19`) falhou por `Broken pipe`; somente a análise mínima retornou veredito.
- Estado: WIP salvo, sem aprovação dupla. Próxima hipótese: abandonar a lâmina como painel e usar uma geometria de arco/visor com perfil lateral explicitamente curvo e enquadramento dedicado.

## R25 — para-brisa rejeitado novamente pelo Sol — 2026-09-10
- Implementada superfície de nove seções com arco quadrático forte em planta/topo, centro avançado e laterais retornadas; Blender executou e renderizou beauty/top.
- Vision próprio: ainda não comprova o arco com segurança no beauty; top mostra o volume, mas o cockpit fica comprimido.
- Sol `gpt-5.6-sol`, `xhigh`, sessão `20260910_101452_474d84`: **REJEITAR** — a peça continua parecendo placa plana/opaca, sem curvatura 3D claramente perceptível.
- Outra sessão (`20260910_101347_842b9d`) não executou vision e respondeu apenas “How can I help?”.
- Próximo: abandonar a placa como superfície principal e construir uma lente curva contínua com perfil lateral/topo dedicado; incluir render de perfil/topo em escala de revisão. WIP não aprovado.

## Diagnóstico Sol — R18 — 2026-09-10
- Sessão `20260910_095223_36678c`, `gpt-5.6-sol`, `xhigh`, vision; nenhum arquivo editado.
- Para-brisa: painel frontal transparente integralmente à frente do volante, maior que o aro em largura aparente, topo acima das mãos/aro, base contínua na carenagem; reflexo de borda e transmissão ampla visíveis.
- Personagem: substituir montagem de primitivas por cadeia pelve→torso→ombros→cotovelos→punhos→mãos; mãos envolvem o aro 9h/3h, dedos cobrem >50% da seção, desvio de punho <15°, cintos atrás do cubo.
- Capacete: casco único envolvendo cabeça interna com 8–14 px de folga, abertura facial, visor curvo com espessura/pivôs, queixeira rígida ligada às laterais e colar separado; face dentro da abertura.
- Clearance: recuar 20–30%, mostrar capacete/para-brisa completos e validar thumbnail de 320 px; não aceitar peças tangentes/flutuantes.

## Consulta estratégica Sol — 2026-09-10 — bloqueada
- Foi solicitado ao Sol (`gpt-5.6-sol`, `xhigh`) um plano acionável baseado em vision para reconstruir o personagem/cockpit, sem editar arquivos.
- Sessão `20260910_093911_1bae15` permaneceu sem resposta por ~567 s e foi encerrada.
- Nenhuma estratégia nova foi recebida; não atribuir ao Sol recomendações que ele não entregou. O diagnóstico acionável anterior continua vigente: reconstrução estrutural do piloto, não incrementos de primitivas.

## R17 — vision próprio rejeita personagem — 2026-09-10
- Aplicados P0 derivados do Sol: cadeia anatômica, câmera de clearance recuada, pescoço, face interna, casco menor, mãos/volante e para-brisa frontal.
- Vision próprio continua **REJEITANDO**: piloto lê como manequim procedural, braços/mãos e torso não têm anatomia AAA, capacete ainda desproporcional/sem vestibilidade convincente em contexto e clearance não comprova uma pose natural sem oclusão.
- Após múltiplas correções incrementais, hipótese rejeitada: adicionar esferas/tubos ao blockout não resolve. Próxima etapa precisa reconstruir o personagem como asset coerente (pelvis/torso/ombros/braços/mãos/cabeça/casco) e separar o cockpit em uma composição de revisão dedicada.
- Não pedir nova validação Sol enquanto o meu vision não passar; não integrar nem enviar como aprovado.

## Diagnóstico Sol acionável — cockpit — 2026-09-10
- Sessão `20260910_091420_95e211`, `gpt-5.6-sol`, `xhigh`, vision; nenhum arquivo editado pelo Sol.
- Ordem espacial exigida: carenagem frontal → base/painel do para-brisa → aro/cubo → mãos envolvendo o aro → antebraços → queixeira/viseira → face dentro da abertura → crânio/casco → encosto.
- Para-brisa: geometria integralmente à frente do volante; maior que o volante em largura aparente; topo acima do aro; reflexo contínuo em uma borda e área ampla de transmissão; câmera deve mostrar a peça inteira.
- Personagem: casco como silhueta única contínua envolvendo a face; viseira presa aos dois lados; face dentro da abertura; queixeira integrada; encosto atrás sem interseção; câmera de clearance recuada 20–30%.
- Mãos devem envolver o tubo do aro; antebraços não podem atravessar cubo/raios; cintos partem dos ombros e não passam à frente do cubo.
- Critério P0: confirmar tudo em beauty e clearance, inclusive thumbnail de 320 px, antes de nova aprovação dupla.

## Solicitação de diagnóstico Sol — 2026-09-10 — bloqueada
- Foi solicitado ao Sol (`gpt-5.6-sol`, `xhigh`) que usasse vision para indicar exatamente as correções do para-brisa, personagem e capacete, sem editar arquivos.
- Sessão `20260910_084641_5b1bce` permaneceu ativa por ~559 s sem produzir resposta ou recomendação; foi encerrada para evitar processo zumbi.
- Nenhuma orientação adicional do Sol foi recebida. Não alterar o asset com base em uma resposta inexistente; próxima tentativa deve usar uma sessão Sol curta e focada somente no render/arquivo.

## R14 — aprovação visual dupla dos ajustes — 2026-09-10
- Ajustes finais: aro D ciano ampliado e separado das mãos, hub metálico central, coluna coral contínua até bracket/dash; para-brisa menor e deslocado para frente, com lente translúcida/moldura/reflexos; helmet shell/visor/queixeira/colar separados.
- Vision próprio: **APROVAR** os três itens.
- Sol `gpt-5.6-sol`, `xhigh`, sessão `20260910_082702_0748c5`: **APROVAR** direção, para-brisa e capacete; veredito geral **APROVAR**.
- Validação estrutural R14: `RC=2`, `all_structural_gates_pass=false`; LOD0 `41.474 tri/6 mats/1.696 não-manifold`, LOD1 `23.100/5/1.098`, LOD2 `11.148/5/666`, COLLISION `36 tri/manifold`, `.blend` `678.925 bytes`.
- Escopo aprovado: somente os três ajustes visuais solicitados. Integração final continua bloqueada pelos gates estruturais já conhecidos; não mascarar como asset de produção.

## Auditoria R9 — vision próprio + Sol — 2026-09-10
- Vision próprio: para-brisa lê como defletor translúcido pequeno; capacete melhorou com visor compacto; volante ainda parece controle estreito e a estrutura compete com a moldura.
- Sol (`gpt-5.6-sol`, `xhigh`, sessão `20260910_073812_8af2ee`): **0/3 aprovados**. Para-brisa: rejeitado por não comprovar lente/ancoragem AAA; capacete: rejeitado por visor/queixeira/colar sugeridos, sem integração construtiva suficiente; volante: rejeitado por aro D e cadeia volante→hub→coluna→dash não distinguíveis.
- Próxima reconstrução deve separar visualmente as funções com cores/planos distintos, remover sobreposição entre moldura e direção, usar aro D completo visível e refazer casco/visor/queixeira/colar como volumes contínuos.

## Auditoria Sol — para-brisa e capacete — 2026-09-10
- Sessão `20260910_071201_45d493`, `gpt-5.6-sol`, `xhigh`; auditoria sem edição nas capturas `beauty.png` e `driver-clearance.png`.
- **Para-brisa: REJEITAR.** O Sol confirmou leitura de placa/tela escura, sem transparência, espessura ou ancoragem construtiva convincentes; moldura e suporte competem com o volante e bloqueiam a leitura do cockpit.
- **Capacete: REJEITAR.** Silhueta esférica genérica; visor como placa escura rasa; queixeira tubular desconectada; faixa superior parece colada; falta pescoço/colar e recorte inferior integrados.
- Correções P0: refazer casco com testa/coroa/laterais/nuca/colar, trocar tubo por queixeira volumétrica integrada, criar lente curva com espessura/vedação/pivôs e revisar folgas com ombros/encosto. Para-brisa deve ser lente curva realmente transparente, menor e claramente presa ao dash.
- Estado: WIP rejeitado; não integrar nem declarar aprovação antes de nova modelagem e dupla validação visual.

## Iteração cockpit — 2026-09-10 — WIP rejeitado por vision próprio e Sol
- Pedido aplicado: coluna/yoke do volante estendidos até o dash, mini para-brisa à frente do volante e capacete com visor/moldura/queixeira redesenhados.
- Vision próprio: capacete melhorou e está integrado; coluna ficou mais legível, mas o para-brisa continua parecendo painel escuro e a conexão volante–dash ainda não é inequívoca.
- Sol (`gpt-5.6-sol`, `xhigh`) confirmou: **REJEITAR** para volante/coluna e para-brisa; **APROVAR** para capacete/visor/queixeira.
- Correções posteriores reduziram a opacidade do shader e trocaram a lâmina por um painel fino, porém a captura Eevee ainda não demonstra transparência. Após três tentativas, a hipótese duvidosa é a configuração de transparência do material no Eevee 4.0.2 do runner.
- O `.blend`, renders, métricas e script permanecem salvos como WIP; não integrar até nova solução de vidro/coluna e aprovação dupla.

## Estado atual do asset — WIP verificável — 2026-09-10
- O Sol criou o script autoral `scripts/blender/hero_kart_v2_build.py`; o runner Blender 4.0.2 executou esse script após um fix mínimo de compatibilidade para inicializar `scene.world`.
- Artefatos copiados para `assets/hero-kart-v2/`: `.blend`, `metrics.json`, `renders/` com beauty, black-fill, clay, wireframe, vistas ortográficas/3⁄4, driver-clearance, underside e comparação LOD.
- Vision próprio: beauty lê como kart arcade AAA estilizado e está muito acima do cubo anterior; falhas: black-fill não está realmente preto, encaixe do piloto ainda precisa refinamento, asa domina a traseira e a identidade traseira é genérica sem aero.
- Validação estrutural real: LOD0 `39.268` triângulos/5 materiais, mas `1.692` arestas não-manifold e normais negativas; LOD1 `21.952` triângulos/5 materiais (limite 4), não-manifold; LOD2 `10.364` triângulos/5 materiais (limite 7.500/3), não-manifold; COLLISION `36` triângulos/manifold.
- Veredito: **WIP REJEITADO PARA INTEGRAÇÃO FINAL**. O arquivo está salvo para continuação, mas exige limpeza de topologia/normais, redução real de LOD1/LOD2, black-fill correto e nova validação visual independente.

## Evidência Sol
Sessão de planejamento: `20260910_040509_cc8ad5`, `gpt-5.6-sol`, `xhigh`.

## Execução Sol direta — 2026-09-10 — bloqueada
- Tentativa corrigida via CLI direta com `gpt-5.6-sol`, `xhigh`, `--safe-mode` e `terminal,file,vision`.
- Houve escrita transitória de `assets/hero-kart-v2/renders/`, mas após ~13m40s não havia Blender ativo nem `.blend`, script, render final, métricas ou commit; o processo foi encerrado para evitar processo zumbi.
- O runner Blender/SSH permanece saudável; o bloqueio está na execução do agente Sol, que não conclui a primeira cadeia de ferramentas.

## Execução Default → Sol — 2026-09-10 — bloqueio confirmado
- O `default` verificou runner Blender/SSH saudável; o bloqueio não é GPU, RAM ou Blender.
- Mesmo com `--safe-mode`, `--yolo`, `terminal/file/vision`, `gpt-5.6-sol` e `xhigh`, o Sol não executou a primeira ferramenta dentro do orçamento.
- Nenhum `.blend`, script ou render foi criado; gate-check `assets/hero-kart-v2/GATES.md`: `UNMET: 8 (met: 0)`.
- `origin/main` verificado em `2290ff8`; nenhum commit/push de asset existe.

## Execução 2026-09-10 — bloqueada
- O modelo procedural anterior foi visualmente rejeitado: não atingia a distância AAA das referências.
- Foi solicitado ao Sol (`gpt-5.6-sol`, `xhigh`) que executasse a modelagem real no runner Blender, salvasse `assets/hero-kart-v2/hero-kart-v2.blend`, renders, LODs e collider, e fizesse commits/push atômicos.
- A primeira sessão esgotou aproximadamente 563 s no preflight sem criar projeto, script, LOD, render, commit ou push.
- A segunda sessão começou e criou somente `assets/hero-kart-v2/GATES.md`; após aproximadamente 750 s não havia `.blend`, script ou render e o processo foi encerrado por timeout operacional.
- Nenhuma aprovação visual foi emitida. Nenhum asset foi exportado ou integrado ao runtime.
- Estado de retomada: executar a modelagem customizada no runner Blender com sessão Sol funcional; somente depois validar com vision, salvar o `.blend` no repo e fazer commits/push.

## R80 — reconstrução de capacete/volante rejeitada — 2026-09-10
- R80 removeu duplicações de capacete, trocou shell por casco compacto, fechou aro D e reduziu hub/coluna; para-brisa permaneceu baixo no cowl.
- Vision próprio: **REJEITAR**. Para-brisa ainda lê como placa suspensa; capacete como esfera/goggles sem full-face natural; volante/mãos continuam artificiais.
- Sol não foi chamado porque o gate próprio falhou.
- Hipótese confirmada: reconstrução dedicada de cockpit/personagem é necessária; não mais ajustes locais.
