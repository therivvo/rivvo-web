# Hero Kart V2 — Loop R46–R53

Data: 2026-09-10
Escopo: somente asset Blender; nenhum runtime foi integrado.

## Resultado final

- R53 recebeu aprovação dupla na mesma versão:
  - vision independente: APROVAR;
  - Sol `gpt-5.6-sol`, `xhigh`, vision: APROVAR;
  - sessão Sol: `20260910_153744_40deff`.
- R53 corrigiu a leitura do para-brisa com casca contínua convexa, arco em planta, material Eevee `BLEND`, alpha 0.34 e cockpit visível.
- Build Blender remoto: rc 0; render set: rc 0; Blender 4.0.2 no runner `192.168.0.195`.
- Artefatos finais: `assets/hero-kart-v2/hero-kart-v2.blend`, `assets/hero-kart-v2/metrics.json`, `assets/hero-kart-v2/renders/beauty.png` e o conjunto `r53-*.png`.

## Iterações e decisões

- R46: rejeitada por vision e Sol — ainda parecia placa vertical; render/validação executaram.
- R47: rejeitada por vision e Sol — inclinação melhorou, mas a lente ainda era uma placa opaca.
- R48: rejeitada por vision e Sol — material transparente virou superfície preta/opaca.
- R49: vision rejeitou por leitura de lâmina; Sol teve `Broken pipe` em duas tentativas.
- R50: vision rejeitou suportes desconectados; Sol teve `Broken pipe`.
- R51: vision rejeitou A-pillars cruzando/saindo da borda; Sol teve `Broken pipe`.
- R52: vision aprovou a direção visual, mas Sol rejeitou por granulação/facetas e encaixe pouco definido.
- R53: alpha suave eliminou a granulação; ambos aprovaram a mesma versão.

## Validação técnica honesta

`metrics.json` confirma Blender 4.0.2, LOD0 42.872 triângulos/6 materiais, LOD1 23.740/5, LOD2 11.532/5 e COLLISION 36/manifold. O script de validação retornou rc 2 porque os gates históricos de budget/material/manifold/normais para LOD0–LOD2 ainda falham; isso não bloqueou a aprovação visual solicitada, mas impede declarar o asset tecnicamente pronto para integração.

## Reprodução

1. Copiar `scripts/blender/hero_kart_v2_build.py`, `hero_kart_v2_render.py` e `hero_kart_v2_validate.py` para o runner Blender 4.0.2.
2. Executar build e render sob o lock `/opt/blender-runner/locks/blender.lock`.
3. Validar `metrics.json` e inspecionar `beauty`, `windshield-profile`, `windshield-top` e `driver-clearance`.
4. Exigir vision e Sol aprovando o mesmo Rxx antes de qualquer integração.
