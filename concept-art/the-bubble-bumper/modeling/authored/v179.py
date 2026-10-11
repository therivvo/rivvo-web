import bpy
from mathutils import Vector

MD = "/mnt/storage2TB/Coding-Projects/super-kart-3djs/concept-art/the-bubble-bumper/modeling/"
SRC = MD + "authored/conjunto-v178.blend"
OUT = MD + "authored/conjunto-v179.blend"
bpy.ops.wm.open_mainfile(filepath=SRC)
deps = bpy.context.evaluated_depsgraph_get()

# medir a superficie mais a DIREITA (+x) do conjunto por (x,z) do lado do conceito,
# para saber ate onde o amarelo de topo pode subir sem sair do casco
def z_max_em(x, z_lo, z_hi):
    melhor = -999
    for z in [z_lo + i * 0.005 for i in range(int((z_hi - z_lo) / 0.005) + 1)]:
        ok, *_ = bpy.context.scene.ray_cast(deps, Vector((x, 5.0, z)), Vector((0, -1, 0)))
        if ok:
            melhor = z
    return melhor

print("###V179### teto do conjunto por coluna (raycast, envio y=+5):")
teto = {}
for x in (-0.18, -0.16, -0.15, -0.14, -0.13, -0.12, -0.11, -0.10, -0.09):
    t = z_max_em(x, 1.05, 1.24)
    teto[x] = t
    print("###V179###   x=%+.2f topo=%.3f" % (x, t))

# 1) P_StripeF: rampa - topo segue o teto medido, base continua 1.090
sf = bpy.data.objects.get("P_StripeF")
me = sf.data
idx_am = None
for i, s in enumerate(me.materials):
    if s and s.name == "Accent_Yellow":
        idx_am = i
assert idx_am is not None
bpy.context.view_layer.update()
n = 0
for p in me.polygons:
    c = sf.matrix_world @ p.center
    pz = teto.get(round(c.x / 0.01) * 0.01, 1.18)
    # topo da faixa nesta coluna = minimo entre o teto medido e a rampa do concept
    rampa = 1.19 - (c.x + 0.18) / ( -0.10 - (-0.18) ) * (1.19 - 1.08) if -0.18 <= c.x <= -0.10 else 1.19
    topo = min(pz if pz > 0 else 9, rampa)
    if 1.090 <= c.z <= topo:
        p.material_index = idx_am; n += 1
me.update()
print("###V179### P_StripeF faces repintadas (rampa):", n)

# 2) nova banda media amarela: esfera UV fechada em x=-0.115, z=0.845 (concept z 0.80..0.88)
#    usar o mesmo material Accent_Yellow e o solido fechado (regra 8)
bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=12, location=(-0.115, 0.0, 0.845))
mb = bpy.context.active_object
mb.name = "P_MidBand"
mb.scale = (0.055, 0.120, 0.045)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
# aplicar material
mat = bpy.data.materials.get("Accent_Yellow")
mb.data.materials.clear(); mb.data.materials.append(mat)
# manter em 1 componente: sobrepoe com a asa/casco (contato geom. validado pelo gate)
bpy.context.view_layer.update()
bb = [mb.matrix_world @ Vector(c) for c in mb.bound_box]
print("###V179### P_MidBand bbox x=%.3f..%.3f y=%.3f..%.3f z=%.3f..%.3f" %
      (min(v.x for v in bb), max(v.x for v in bb), min(v.y for v in bb), max(v.y for v in bb),
       min(v.z for v in bb), max(v.z for v in bb)))

bpy.ops.wm.save_as_mainfile(filepath=OUT)
print("###V179### salvo", OUT)
