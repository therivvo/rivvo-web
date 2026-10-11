import bpy
from mathutils import Vector

MD = "/mnt/storage2TB/Coding-Projects/super-kart-3djs/concept-art/the-bubble-bumper/modeling/"
SRC = MD + "authored/conjunto-v179.blend"
OUT = MD + "authored/conjunto-v180.blend"
bpy.ops.wm.open_mainfile(filepath=SRC)

mb = bpy.data.objects.get("P_MidBand")
assert mb is not None, "P_MidBand ausente"
bb = [mb.matrix_world @ Vector(c) for c in mb.bound_box]
x0, x1 = min(v.x for v in bb), max(v.x for v in bb)
print("###V180### P_MidBand ANTES x=%.3f..%.3f" % (x0, x1))

# concept mede amarelo em x -0.14 e -0.12 (4 e 3 amostras) -> alvo x -0.148..-0.112
ALVO0, ALVO1 = -0.148, -0.112
mw = mb.matrix_world.copy(); inv = mw.inverted()
cx_atual = (x0 + x1) / 2.0
cx_alvo = (ALVO0 + ALVO1) / 2.0
fator = (ALVO1 - ALVO0) / (x1 - x0)
for v in mb.data.vertices:
    w = mw @ v.co
    w.x = cx_alvo + (w.x - cx_atual) * fator
    v.co = inv @ w
mb.data.update()
bpy.context.view_layer.update()
bb = [mb.matrix_world @ Vector(c) for c in mb.bound_box]
print("###V180### P_MidBand DEPOIS x=%.3f..%.3f z=%.3f..%.3f" %
      (min(v.x for v in bb), max(v.x for v in bb), min(v.z for v in bb), max(v.z for v in bb)))
bpy.ops.wm.save_as_mainfile(filepath=OUT)
print("###V180### salvo", OUT)
