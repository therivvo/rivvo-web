import bpy
from mathutils import Vector

MD = "/mnt/storage2TB/Coding-Projects/super-kart-3djs/concept-art/the-bubble-bumper/modeling/"
SRC = MD + "authored/conjunto-v174.blend"
OUT = MD + "authored/conjunto-v177.blend"
bpy.ops.wm.open_mainfile(filepath=SRC)


def bbox(o):
    bb = [o.matrix_world @ Vector(c) for c in o.bound_box]
    return (min(v.x for v in bb), max(v.x for v in bb),
            min(v.y for v in bb), max(v.y for v in bb),
            min(v.z for v in bb), max(v.z for v in bb))


def mover_z(o, dz):
    mw = o.matrix_world.copy()
    inv = mw.inverted()
    for v in o.data.vertices:
        v.co = inv @ (mw @ v.co + Vector((0, 0, dz)))
    o.data.update()


def escalar_x(o, fator, x_ref):
    mw = o.matrix_world.copy()
    inv = mw.inverted()
    for v in o.data.vertices:
        w = mw @ v.co
        w.x = x_ref + (w.x - x_ref) * fator
        v.co = inv @ w
    o.data.update()


# 1) P_Stripe: descer 0.045 m (concept pede z 1.10..1.20; modelo estava 1.178..1.235)
s = bpy.data.objects.get("P_Stripe")
assert s is not None, "P_Stripe ausente"
b0 = bbox(s)
mover_z(s, -0.045)
b1 = bbox(s)
print("###V177### P_Stripe z %.3f..%.3f -> %.3f..%.3f" % (b0[4], b0[5], b1[4], b1[5]))

# 2) P_StripeF: descer 0.045 m e ESTENDER em +x ate -0.098 (concept pede x ate -0.10)
f = bpy.data.objects.get("P_StripeF")
assert f is not None, "P_StripeF ausente"
b0 = bbox(f)
mover_z(f, -0.045)
alvo = -0.098
atual = b0[1]  # max x atual
ext = (alvo - b0[0]) / (b0[1] - b0[0])  # fator sobre a largura atual
escalar_x(f, ext, b0[0])  # mantem o lado -x fixo, estende o +x
b1 = bbox(f)
print("###V177### P_StripeF x %.3f..%.3f -> %.3f..%.3f | z %.3f..%.3f -> %.3f..%.3f" %
      (b0[0], b0[1], b1[0], b1[1], b0[4], b0[5], b1[4], b1[5]))

bpy.context.view_layer.update()
print("###V177### P_Stripe  final x=%.3f..%.3f z=%.3f..%.3f" % (bbox(s)[0], bbox(s)[1], bbox(s)[4], bbox(s)[5]))
print("###V177### P_StripeF final x=%.3f..%.3f z=%.3f..%.3f" % (bbox(f)[0], bbox(f)[1], bbox(f)[4], bbox(f)[5]))
bpy.ops.wm.save_as_mainfile(filepath=OUT)
print("###V177### salvo", OUT)
