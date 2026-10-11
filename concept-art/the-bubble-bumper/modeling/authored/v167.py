import bpy
from mathutils import Vector

MD = "/mnt/storage2TB/Coding-Projects/super-kart-3djs/concept-art/the-bubble-bumper/modeling/"
SRC = MD + "authored/conjunto-v166.blend"
DST = MD + "authored/conjunto-v167.blend"
assert SRC != DST

# CAUSA MEDIDA (grade de raycast do v166): existe um BULBO local no casco em x -0.22..-0.20,
# z 0.99..1.04. Os flancos desse bulbo ficam com ny 0.25..0.34 (quase edge-on) e por isso renderizam
# escuros -> o classificador le fundo ('.'), quando o concept ali tem PAINEL FRONTAL PLANO e claro.
# Superficie medida: x=-0.23 -> y=0.108 (ny=1.00, correto) | x=-0.22 -> y=0.119 (ny=0.25) |
# x=-0.21 -> y=0.128 (ny=0.34) | x=-0.20 -> y=0.113 (ny=0.25) | x=-0.19 -> y=0.108 (ny=1.00).
# CORRECAO: achatar o bulbo ao nivel dos vizinhos sadios (y <= 0.112) nessa janela.
X0, X1 = -0.226, -0.194
Z0, Z1 = 0.985, 1.045
YCAP = 0.112

bpy.ops.wm.open_mainfile(filepath=SRC)
bpy.context.view_layer.update()

helm = bpy.data.objects.get("P_Helmet")
assert helm is not None, "P_Helmet ausente"
me = helm.data
mwh = helm.matrix_world
inv = mwh.inverted()
n_achat = 0
y_antes = []
for v in me.vertices:
    w = mwh @ v.co
    if X0 <= w.x <= X1 and Z0 <= w.z <= Z1 and 0.05 < abs(w.y) < 0.145:
        y_antes.append(abs(w.y))
        if abs(w.y) > YCAP:
            s = 1.0 if w.y > 0 else -1.0
            w.y = s * YCAP
            v.co = inv @ w
            n_achat += 1
print("###V167### vertices achatados: %d | y antes: min %.4f max %.4f" %
      (n_achat, min(y_antes) if y_antes else -1, max(y_antes) if y_antes else -1))
assert n_achat >= 2, "nenhum vertice do bulbo achatado (%d)" % n_achat
me.update()
bpy.context.view_layer.update()

# CONFERENCIA: repetir a grade de raycast da janela para provar que ny subiu
dg = bpy.context.evaluated_depsgraph_get()
sc = bpy.context.scene
print("###V167### grade DEPOIS (ny antes: x-0.22 -> 0.25 | x-0.21 -> 0.34 | x-0.20 -> 0.25):")
for z in (0.99, 1.00, 1.02, 1.04):
    linha = []
    for xi in range(4):
        x = -0.23 + xi * 0.01
        ok, loc, nor, idx, ob, mw = sc.ray_cast(dg, Vector((x, 5.0, z)), Vector((0, -1, 0)))
        linha.append("x%+.2f y%+.3f ny%+.2f" % (x, loc.y, nor.y) if ok else "x%+.2f VAZIO" % x)
    print("###V167### z=%.2f | %s" % (z, " | ".join(linha)))

bpy.ops.wm.save_as_mainfile(filepath=DST)
print("###V167### salvo:", DST)
