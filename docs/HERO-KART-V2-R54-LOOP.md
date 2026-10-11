# Hero Kart V2 — Loop R54+

## R72 — aprovação dupla concluída — 2026-09-10
- R70 foi rejeitada pelo Sol por clamps/caminho estrutural pouco contáveis e clearance sem estrutura visível.
- R71 ampliou os quatro clamps, mas vision próprio rejeitou clearance por obstrução do piloto/volante.
- R72 manteve os clamps dedicados e mudou a câmera de clearance para lateral/elevada. Build/render/auditoria no runner `.195` com Blender 4.0.2 passaram com rc 0; `OBJECTS 1135`; P0 `all_pass=true`, 4 mounts, largura `0.7580645`, borda `1.12 m`, hub `0.20D`.
- Vision próprio aprovou beauty/profile/top/clearance. Sol aprovou a mesma R72: `gpt-5.6-sol`, `openai-codex`, `xhigh`, rc 0, sessão `20260910_194209_18c560`.
- Runtime não integrado.

## Estado inicial

R53 foi rejeitada pelo Sol (`gpt-5.6-sol` + `xhigh`) por três bloqueadores P0: para-brisa voando/sem fixação clara; cabeça/capacete artificial; volante estranho. O loop foi reiniciado sem integrar runtime.

## P0 executado

- Para-brisa reconstruído com quatro hardpoints simétricos, suportes seguindo as bordas da lente, largura nominal `0,47 m / 0,62 m = 0,758 Wc`, borda traseira `0,85 m` à frente da borda de referência do cockpit e folga alvo de `0,05 m` por antebraço.
- Capacete reconstruído com volume de cabeça interna, volumes separados de têmpora, mandíbula e nuca, visor com pivôs laterais, queixeira integrada e colar separado.
- Volante reconstruído com hub coaxial/coluna, hub de `0,112 m = 0,20D` do aro de referência, sem a placa rosa; mãos recebem metadados e posições polares `150°/30°`, punho nominal de `8°`.

## Execução reproduzível

1. Copiar `scripts/blender/hero_kart_v2_build.py` para o job do runner `.195`.
2. Executar via `/opt/blender-runner/run_blender.sh` com Blender `4.0.2`.
3. Executar `hero_kart_v2_render.py` para gerar `beauty`, `windshield-profile`, `windshield-top` e `driver-clearance` na mesma revisão.
4. Executar `hero_kart_v2_p0_audit.py`; ele abre o `.blend` real e mede nomes/contagens/metadados no LOD0.
5. Só chamar Sol se meu vision passar nas quatro imagens; Broken pipe nunca conta como aprovação.

## Evidência R54 atual

- Build: Blender `4.0.2`, `1127` objetos, `1111` meshes, `6` materiais; `.blend` e `build-report.json` salvos.
- Auditoria P0 após ajuste do hub: `all_pass=true`; largura `0,7580645`, avanço da borda `0,85 m`, hub `0,20D`, mounts `4`, mãos `[30°,150°]`.
- O primeiro vision R54 encontrou suportes altos/desconectados visualmente; a geometria foi corrigida para que os pickups coincidam com a borda real da lente. A rodada visual pós-correção ainda está pendente.
- Sol R54 foi invocado explicitamente duas vezes com `gpt-5.6-sol`/`xhigh`; ambas falharam com `HTTP 429: The usage limit has been reached`, seguido de `Broken pipe` após 3 retries. Autenticação está válida, mas não há aprovação Sol; o gate G6 permanece pendente.
- Nenhum runtime, segredo ou integração de jogo foi alterado.
