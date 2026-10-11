import bpy
from mathutils import Vector

MD = "/mnt/storage2TB/Coding-Projects/super-kart-3djs/concept-art/the-bubble-bumper/modeling/"
SRC = MD + "authored/conjunto-v167.blend"
DST = MD + "authored/conjunto-v168.blend"
assert SRC != DST

# CAUSA CONFIRMADA (grade g168 COM nome do objeto): a faixa rasante em z 1.00..1.03, x -0.22..-0.20
# e do P_Visor[Visor_Light] — NAO do P_Helmet. O v167 achatou o objeto errado, e por isso os y
# ficaram IDENTICOS. O P_Visor (115 verts, |y|max 0.156) PROTAI ate y=0.153 enquanto a P_FacePlate
# vizinha esta em y=0.108 -> os flancos do visor ficam com ny 0.25..0.34 (quase edge-on) e renderizam
# escuros, virando '.' no classificador. O concept ali e um painel frontal plano e claro.
# CORRECAO: achatar o bulbo do P_Visor ao nivel da placa (|y| <= 0.112) na janela medida.
X0, X1 = -0.235, -0.195
Z0, Z1 = 0.985, 1.045
YCAP = 0.112

bpy.ops.wm.open_mainfile(filepath=SRC)
bpy.context.view_layer.update()

vis = bpy.data.objects.get("P_Visor")
assert vis is not None, "P_Visor ausente"
mwh = vis.matrix_world
inv = mwh.inverted()
n = 0
ys = []
for v in vis.data.vertices:
    w = mwh @ v.co
    if X0 <= w.x <= X1 and Z0 <= w.z <= Z1 and 0.02 < abs(w.y) < 0.17:
        ys.append(abs(w.y))
        if abs(w.y) > YCAP:
            s = 1.0 if w.y > 0 else -1.0
            w.y = s * YCAP
            v.co = inv @ w
            n += 1
print("###V168### P_Visor: %d verts achatados (y antes min %.4f max %.4f -> cap %.3f)" %
      (n, min(ys) if ys else -1, max(ys) if ys else -1, YCAP))
assert n >= 2, "nada achatado no visor (%d)" % n
vis.data.update()
bpy.context.view_layer.update()

dg = bpy.context.evaluated_depsgraph_get()
sc = bpy.context.scene
print("###V168### grade DEPOIS (antes: P_Visor ny 0.25/0.34/0.25 em z=1.00; 0.34/0.65/0.34 em z=1.01):")
for z in (1.00, 1.01, 1.02, 1.03):
    cel = []
    for xi in range(4):
        x = -0.23 + xi * 0.01
        ok, loc, nor, idx, ob, mw = sc.ray_cast(dg, Vector((x, 5.0, z)), Vector((0, -1, 0)))
        cel.append("%+.2f %s y%+.3f ny%+.2f" % (x, ob.name if ok else "VAZIO", loc.y, nor.y) if ok else "%+.2f VAZIO" % x)
    print("###V168### z=%.2f | %s" % (z, " | ".join(cel)))

bpy.ops.wm.save_as_mainfile(filepath=DST)
print("###V168### salvo:", DST)
