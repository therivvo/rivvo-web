import bpy
from mathutils import Vector

MD = "/mnt/storage2TB/Coding-Projects/super-kart-3djs/concept-art/the-bubble-bumper/modeling/"
bpy.ops.wm.open_mainfile(filepath=MD + "authored/conjunto-v149.blend")

dg = bpy.context.evaluated_depsgraph_get()
sc = bpy.context.scene
DIR = Vector((0, -1, 0))
Y0 = 2.0

Z_TESTE = 1.05
print("###MAP### A) RAIO: varredura de x em z=%.2f (passo 0.005 m) -> onde HA geometria" % Z_TESTE)
segs = []
atual = None
ini = None
x = -0.40
while x <= -0.05 + 1e-9:
    ok, loc, nor, idx, obj, mw = sc.ray_cast(dg, Vector((x, Y0, Z_TESTE)), DIR)
    key = 'VAZIO' if not ok else obj.name
    if key != atual:
        if atual is not None:
            segs.append((atual, ini, round(x - 0.005, 3)))
        atual = key
        ini = round(x, 3)
    x = round(x + 0.005, 4)
segs.append((atual, ini, -0.05))
for nm, a, b in segs:
    print("   %-14s de x=%+.3f a x=%+.3f" % (nm, a, b))
occ = [s for s in segs if s[0] != 'VAZIO']
if occ:
    print("   >>> FRENTE da silhueta em mundo = x=%+.3f (%s)" % (occ[-1][2], occ[-1][0]))
    print("   >>> TRAS   da silhueta em mundo = x=%+.3f (%s)" % (occ[0][1], occ[0][0]))
print("###MAP### fim do lado A")
