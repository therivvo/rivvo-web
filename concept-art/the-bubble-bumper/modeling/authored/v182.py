import bpy
from mathutils import Vector

MD = "/mnt/storage2TB/Coding-Projects/super-kart-3djs/concept-art/the-bubble-bumper/modeling/"
SRC = MD + "authored/conjunto-v181.blend"
OUT = MD + "authored/conjunto-v182.blend"
bpy.ops.wm.open_mainfile(filepath=SRC)

blob = bpy.data.objects.get("P_RearTop")
assert blob is not None
mw = blob.matrix_world.copy(); inv = mw.inverted()
me = blob.data

# topo alvo do CONCEPT por coluna (medido, rampa):
ALVO = [(-0.18, 1.227), (-0.16, 1.215), (-0.14, 1.199), (-0.12, 1.180),
        (-0.10, 1.158), (-0.09, 1.136), (-0.08, 1.117), (-0.07, 1.086)]


def topo_alvo(x):
    if x <= ALVO[0][0]:
        return ALVO[0][1]
    if x >= ALVO[-1][0]:
        return ALVO[-1][1]
    for i in range(len(ALVO) - 1):
        (xa, za), (xb, zb) = ALVO[i], ALVO[i + 1]
        if xa <= x <= xb:
            t = (x - xa) / (xb - xa)
            return za + t * (zb - za)
    return ALVO[-1][1]


# medir estado atual por coluna (teto do blob)
bb = [mw @ Vector(c) for c in blob.bound_box]
Z0, Z1 = min(v.z for v in bb), max(v.z for v in bb)
print("###V182### P_RearTop ANTES z=%.3f..%.3f" % (Z0, Z1))

# amostra o topo atual por x (vertices mais altos por coluna)
def topo_atual(x):
    vs = [mw @ v.co for v in me.vertices]
    xs = [w.x for w in vs]
    zs = [w.z for w in vs]
    cand = [z for xx, z in zip(xs, zs) if abs(xx - x) < 0.008]
    return max(cand) if cand else Z1


# APLANA: para cada vertice ACIMA do plano de corte do concept, abaixa ate o alvo
# manter o solido FECHADO: escala nao-uniforme em Z com centro na BASE do topo (z base = topo_alvo(x)-folga)
PLANO_CENTRO = 1.10  # regiao ficar intacta abaixo disto
mudados = 0
for v in me.vertices:
    w = mw @ v.co
    alvo = topo_alvo(w.x)
    if w.z > alvo:  # acima do topo do concept: trazer para o alvo
        w.z = alvo
        mudados += 1
        v.co = inv @ w
me.update()
bpy.context.view_layer.update()
bb = [mw @ Vector(c) for c in blob.bound_box]
print("###V182### P_RearTop DEPOIS z=%.3f..%.3f | vertices achatados=%d de %d" %
      (min(v.z for v in bb), max(v.z for v in bb), mudados, len(me.vertices)))
bpy.ops.wm.save_as_mainfile(filepath=OUT)
print("###V182### salvo", OUT)
