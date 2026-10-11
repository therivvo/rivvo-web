# SK3D Hero Kart — Blender vertical slice v7

Data: 2026-09-10  
Direção Sol: `20260910_004948_020606` (`gpt-5.6-sol`, `xhigh`)  
Validação Sol: `20260910_012628_acf31a` (`gpt-5.6-sol`, `xhigh`)  
Status: **blockout aprovado para integração; não integrado ao runtime ainda**

## Direção aplicada

- Dimensões-alvo: `1.45 × 1.15 × 2.40m`.
- Eixos: `+Y` cima, `-Z` frente, `+X` direita.
- Origem no centro do footprint/contato.
- Wheel radius: `0.33m`.
- Ride height: `0.37m`.
- Três materiais: `M_Body`, `M_Mechanical`, `M_Driver`.
- Silhueta: chassi baixo, nariz frontal, cockpit central, piloto, rodas expostas, asa traseira e escapes duplos.

## Objetos e integração preparados

- `Body_Main`, `Body_Nose`, `Front_Bumper`, `SidePod_L/R`.
- `Cockpit_Opening`, `Seat`, `Driver_Torso`, `Driver_Head`, `Driver_Visor`.
- `Steering_Wheel`, `Steering_Column`.
- `Engine_Block`, `RearWing_Blade`, `RearWing_Post_L/R`.
- `Exhaust_L/R`, `Exhaust_Collar_L/R`.
- `PIV_Wheel_FL/FR/RL/RR`.
- `FX_Exhaust_L/R`, `FX_Boost_Rear`, `FX_Drift_RL/RR`, `FX_Hit_Center`.
- `COL_Body_Box`, `COL_Nose_Box` separados da malha visual.
- Marcadores `LOD1_TARGET_6000_TRIS` e `LOD2_TARGET_2000_TRIS`.

## Validação Blender

- Blender: `4.0.2`.
- Engine de preview: Eevee.
- Resolução: `960×540`.
- Materiais: `3`.
- GLB exportado: `583,668 bytes`.
- SHA-256 do GLB candidato: `b5e9d70c2f38f3df575d0153ab37e0528b36f9e3f00597dd716b888cb8990378`.
- Mesh validation: **PASS**.
  - non-manifold: `0`;
  - n-gons: `0`;
  - colliders separados;
  - rodas e pivôs nomeados.

## Evidência visual

- Preview Eevee: `/tmp/sk3d-hero-kart-v7-real/hero_kart_v7_preview.png`.
- Prancha ortográfica final: `/tmp/sk3d-hero-final/hero_kart_final.png`.
- Vision interna revisou vistas frontal, traseira, superior e prancha multiângulo.
- Sol aprovou o blockout para integração; grounding, volante e escapes permanecem pontos para validar no runtime.

## Limite atual

O candidato ainda não substitui o kart procedural no jogo. Antes de promover:

1. integrar GLB atrás de feature flag;
2. mapear pivôs para `KartPhysics`/câmera;
3. validar rodas, grounding, drift, salto e colisão em Meadow/Neon desktop/mobile;
4. executar A/B com mesma câmera, seed, iluminação e viewport;
5. repetir build, AI, áudio, pageErrors e vision temporal.

## Próximo passo

Integrar o GLB como candidato de player, sem remover o procedural baseline, e executar o slice GPU completo antes de qualquer promoção.
