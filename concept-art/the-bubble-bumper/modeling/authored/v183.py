import bpy
from mathutils import Vector

MD = "/mnt/storage2TB/Coding-Projects/super-kart-3djs/concept-art/the-bubble-bumper/modeling/"
SRC = MD + "authored/conjunto-v182.blend"
OUT = MD + "authored/conjunto-v183.blend"
bpy.ops.wm.open_mainfile(filepath=SRC)

# rampa do concept (topo do amarelo medido por coluna)
RAMP = [(-0.18, 1.218), (-0.16, 1.205), (-0.15, 1.199), (-0.14, 1.196), (-0.13, 1.183),
        (-0.12, 1.174), (-0.11, 1.164), (-0.10, 1.148), (-0.09, 1.126), (-0.08, 1.098),
        (-0.07, 1.086)]


def topo_alvo(x):
    if x <= RAMP[0][0]:
        return RAMP[0][1]
    if x >= RAMP[-1][0]:
        return RAMP[-1][1]
    for i in range(len(RAMP) - 1):
        (xa, za), (xb, zb) = RAMP[i], RAMP[i + 1]
        if xa <= x <= xb:
            t = (x - xa) / (xb - xa)
            return za + t * (zb - za)
    return RAMP[-1][1]


for nome in ("P_StripeF", "P_Stripe", "P_RearTop"):
    o = bpy.data.objects.get(nome)
    if o is None:
        print("###V183### %s ausente" % nome)
        continue
    mw = o.matrix_world.copy(); inv = mw.inverted()
    bb = [mw @ Vector(c) for c in o.bound_box]
    z0 = max(v.z for v in bb)
    n = 0
    for v in o.data.vertices:
        w = mw @ v.co
        alvo = topo_alvo(w.x)
        if w.z > alvo:
            w.z = alvo; n += 1
            v.co = inv @ w
    o.data.update()
    bpy.context.view_layer.update()
    bb = [mw @ Vector(c) for c in o.bound_box]
    print("###V183### %-10s z_topo %.3f -> %.3f | verts achatados=%d" % (nome, z0, max(v.z for v in bb), n))

bpy.ops.wm.save_as_mainfile(filepath=OUT)
print("###V183### salvo", OUT)
