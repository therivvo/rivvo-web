# Contrato geométrico medido — The Bubble Bumper

Extraído por segmentação de silhueta das 4 ortográficas (`assets/reference-orthographic/`), 18/09/2026.
Máscaras: `/tmp/g_{side,top,front,rear}.npy`. Nada aqui é estimativa de vision: são pixels.

## 1. Razões globais (sem escala — cada vista tem zoom próprio)

| Medida | Valor medido |
|---|---|
| SIDE L/H | **1,973** |
| TOP W/L | **0,624** |
| FRONT W/H | **1,171** |
| REAR W/H | **1,319** |

**As vistas não estão na mesma escala** (spread 1,16x em H, 1,43x em W, 1,20x em L).

## 2. Perfil lateral — altura do contorno em fração de H, por posição em fração de L

Frente = 0%L (ponta do nariz) · Traseira = 100%L.

| x (%L) | topo (%H) | leitura |
|---|---|---|
| 0,05 | **0,276** | nariz (nose cone) |
| 0,10 | 0,289 | nariz |
| 0,15 | 0,311 | nariz → cowl |
| 0,20 | 0,368 | subida do cowl / roda dianteira |
| 0,25 | 0,423 | roda dianteira / cowl |
| 0,30 | 0,522 | topo do cowl |
| 0,35 | **0,537** | topo do cowl |
| 0,40 | 0,475 | **depressão → cockpit aberto** |
| 0,45 | 0,575 | borda do cockpit / antebraço |
| 0,50 | 0,567 | cockpit / tronco |
| 0,55 | **0,968** | começo do capacete |
| 0,60 | **0,995** | topo do capacete (máximo) |
| 0,65 | 0,985 | capacete |
| 0,70 | 0,856 | fim do capacete |
| 0,75 | 0,592 | corpo traseiro |
| 0,80 | 0,532 | corpo traseiro |
| 0,85 | **0,515** | topo mínimo da traseira |
| 0,90 | 0,689 | asa/barra traseira |
| 0,95 | 0,706 | asa/ponteira |

### Conclusões que mudam o modelo

1. **O capacete ocupa 0,55–0,75 %L** e é o único elemento que chega a 1,0 H. O piloto senta
   **atrás do meio**, não à frente.
2. **O corpo sem piloto tem topo máximo ≈ 0,59 H** — o kart é baixo.
3. **O nariz tem só 0,28 H de altura** em 0,05 %L. Um bico alto/bojudo (≥0,40 H) está errado.
4. Há uma **depressão real em 0,40 %L** (0,475 H entre picos de 0,537 e 0,575) → é o cockpit escavado
   aparecendo no perfil. Prova que a banheira existe no desenho.

## 3. Tabela de marcos para dimensionar o modelo (quando houver âncora)

Escolhido L (comprimento total), derive:

| Elemento | Regra |
|---|---|
| H (altura total) | L / 1,973 |
| W total (bitola traseira) | 0,624 · L |
| centro da roda dianteira | 0,27 · L medido do nariz |
| centro da roda traseira | 0,80 · L medido do nariz |
| entre-eixos | 0,53 · L |
| bitola dianteira | 0,509 · L (medida no top) |
| topo do capacete | 1,0 · H |
| topo do corpo (sem piloto) | 0,59 · H |
| altura do nariz | 0,28 · H |
| asa traseira | 0,69–0,71 · H, em 0,90–0,95 · L |

**Falta:** a âncora de escala (L real, ou diâmetro de roda). Sem ela o modelo pode ser correto em
proporção mas arbitrário em tamanho absoluto.

## 4. Estado do modelo V088–V106

- Gate técnico: 0 non-manifold nas 20 peças · 54.684 verts · 97,6% quads · UV · 11 materiais.
- Gate visual independente (subagente auditor, V099): **REJECT global, média 3,4/10**
  (FRONT 4,0 · SIDE 3,0 · REAR 5,0 · TOP 2,0 · ISO 3,0).
- Top-5 do auditor: (1) pod sem anel/colchão rebaixado; (2) sem banheira escavada nem joelhos/pernas;
  (3) fenders azuis inventados sobre as rodas + rodas dianteiras ocluídas; (4) escapamentos atrofiados;
  (5) capacete sem olhos legíveis / crista fragmentada.
- Corrigido desde então (V104–V106): fenders removidos, nariz afinado, cores do concept aplicadas,
  olhos com pupila (55% do disco branco), piloto reclinado, barra traseira engrossada.
