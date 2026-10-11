import bpy
import bmesh
from mathutils import Vector

MD = "/mnt/storage2TB/Coding-Projects/super-kart-3djs/concept-art/the-bubble-bumper/modeling/"
SRC = MD + "authored/conjunto-v180.blend"
OUT = MD + "authored/conjunto-v181.blend"
bpy.ops.wm.open_mainfile(filepath=SRC)
deps = bpy.context.evaluated_depsgraph_get()

# rampa medida no concept: topo amarelo descendo de 1.148 (x=-0.10) ate 1.086 (x=-0.07)
RAMP = [(-0.120, 1.174), (-0.110, 1.164), (-0.100, 1.148), (-0.090, 1.126),
        (-0.080, 1.098), (-0.070, 1.086)]
def rampa(x):
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


def z_topo_conunto(x, z_lo=1.05, z_hi=1.24):
    melhor = -999
    for i in range(int((z_hi - z_lo) / 0.005) + 1):
        z = z_lo + i * 0.005
        ok, *_ = bpy.context.scene.ray_cast(deps, Vector((x, 5.0, z)), Vector((0, -1, 0)))
        if ok:
            melhor = z
    return melhor


# estende P_StripeF em +x ate -0.075 (concept tem amarelo ate -0.08) e tenta pintar rampa
sf = bpy.data.objects.get("P_StripeF")
assert sf is not None, "P_StripeF ausente"
me = sf.data
idx_am = next((i for i, s in enumerate(me.materials) if s and s.name == "Accent_Yellow"), None)
assert idx_am is not None

# 1) escalar +x
bb = [sf.matrix_world @ Vector(c) for c in sf.bound_box]
b0 = (min(v.x for v in bb), max(v.x for v in bb), min(v.z for v in bb), max(v.z for v in bb))
alvo = -0.075
if b0[1] < alvo:
    mw = sf.matrix_world.copy(); inv = mw.inverted()
    f = (alvo - b0[0]) / (b0[1] - b0[0])
    for v in sf.data.vertices:
        w = mw @ v.co
        w.x = b0[0] + (w.x - b0[0]) * f
        v.co = inv @ w
    sf.data.update()
bpy.context.view_layer.update()
bb = [sf.matrix_world @ Vector(c) for c in sf.bound_box]
print("###V181### P_StripeF x %.3f..%.3f -> %.3f..%.3f" % (b0[0], b0[1], min(v.x for v in bb), max(v.x for v in bb)))

# 2) subdividir as faces da stripe na janela x -0.16..-0.07 para ter resolucao de pintura
bpy.context.view_layer.objects.active = sf
sf.select_set(True)
bm = bmesh.new(); bm.from_mesh(sf.data)
alvo_f = [f for f in bm.faces if all(-0.17 <= (sf.matrix_world @ v.co).x <= -0.06 and
                                     (sf.matrix_world @ v.co).z > 1.05 for v in f.verts)]
print("###V181### faces na janela antes:", len(alvo_f))
for _ in range(2):
    bmesh.ops.subdivide_edges(bm, edges=list({e for f in alvo_f for e in f.edges}), cuts=1, use_grid_fill=True)
    alvo_f = [f for f in bm.faces if all(-0.17 <= (sf.matrix_world @ v.co).x <= -0.06 and
                                         (sf.matrix_world @ v.co).z > 1.05 for v in f.verts)]
bm.to_mesh(sf.data); bm.free(); sf.data.update()
print("###V181### faces na janela depois:", len(alvo_f), "| total stripe:", len(sf.data.polygons))

# 3) pintar rampa: topo = min(teto do conjunto, rampa do concept)
bpy.context.view_layer.update()
n = 0
for p in sf.data.polygons:
    c = sf.matrix_world @ p.center
    if not (-0.16 <= c.x <= -0.075):
        continue
    teto = z_topo_conunto(round(c.x, 3))
    topo = min(teto if teto > 0 else 9, rampa(c.x))
    if 1.085 <= c.z <= topo:
        p.material_index = idx_am; n += 1
sf.data.update()
print("###V181### faces amarelas na rampa:", n)

bpy.ops.wm.save_as_mainfile(filepath=OUT)
print("###V181### salvo", OUT)
