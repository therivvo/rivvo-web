import bpy
from mathutils import Vector

MD = "/mnt/storage2TB/Coding-Projects/super-kart-3djs/concept-art/the-bubble-bumper/modeling/"
SRC = MD + "authored/conjunto-v168.blend"   # CANDIDATO VALIDO (v169 revertido)
DST = MD + "authored/conjunto-v170.blend"
assert SRC != DST

# DEGRAU MEDIDO: silhueta do modelo em x -0.12..-0.10 = 1.020 vs concept 1.218 (degrau 0.198 m).
# A grade g169 provou VAZIO ali acima de z~1.08 e que o shell do P_Helmet termina em x~-0.13:
# portanto mover vertices existentes nao resolve (v169 regrediu) — e preciso ESTICAR a casca.
# DEFORMACAO: no topo-traseiro, empurrar +x (para tras) e +z (para cima), com peso duplo:
#   wx: 0 em x=-0.16 -> 1 em x=-0.11   (afeta so a parte de tras)
#   wz: 0 em z=1.00  -> 1 em z=1.12    (afeta so o topo)
# Alvo: topo do casco em x=-0.12..-0.10 subir de ~1.02 para ~1.218.
DX_MAX = 0.035
DZ_MAX = 0.100
X0, X1 = -0.160, -0.110
Z0, Z1 = 1.000, 1.120
ALVOS = ["P_Helmet", "P_StripeF", "P_HVent"]


def w01(v, a, b):
    if b == a:
        return 0.0
    return min(1.0, max(0.0, (v - a) / (b - a)))


bpy.ops.wm.open_mainfile(filepath=SRC)
bpy.context.view_layer.update()

for nome in ALVOS:
    ob = bpy.data.objects.get(nome)
    if ob is None:
        print("###V170### AVISO: %s ausente" % nome)
        continue
    mw = ob.matrix_world
    inv = mw.inverted()
    n = 0
    dxm = dzm = 0.0
    for v in ob.data.vertices:
        w = mw @ v.co
        if not (X0 <= w.x <= X1 and w.z >= Z0):
            continue
        wx = w01(w.x, X0, X1)
        wz = w01(w.z, Z0, Z1)
        if wx <= 0 or wz <= 0:
            continue
        dx = DX_MAX * wx * wz
        dz = DZ_MAX * wx * wz
        w.x += dx
        w.z += dz
        v.co = inv @ w
        n += 1
        dxm = max(dxm, dx)
        dzm = max(dzm, dz)
    print("###V170### %-10s verts=%3d | dx max %.3f | dz max %.3f" % (nome, n, dxm, dzm))
    ob.data.update()

bpy.context.view_layer.update()

# CONFERENCIA: silhueta (primeiro hit descendo de z=1.30) nas colunas do degrau
dg = bpy.context.evaluated_depsgraph_get()
sc = bpy.context.scene
print("###V170### silhueta DEPOIS (concept: 1.218 em -0.12..-0.10):")
for x in (-0.15, -0.14, -0.13, -0.12, -0.11, -0.10):
    z = 1.30
    hit = None
    while z > 0.90:
        ok, loc, nor, idx, ob, mw = sc.ray_cast(dg, Vector((x, 5.0, z)), Vector((0, -1, 0)))
        if ok:
            hit = (round(z, 3), ob.name)
            break
        z -= 0.005
    print("###V170###   x%+.2f topo=%s" % (x, hit))

bpy.ops.wm.save_as_mainfile(filepath=DST)
print("###V170### salvo:", DST)
