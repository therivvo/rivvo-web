import bpy
from mathutils import Vector

MD = "/mnt/storage2TB/Coding-Projects/super-kart-3djs/concept-art/the-bubble-bumper/modeling/"
SRC = MD + "authored/conjunto-v173.blend"   # CANDIDATO (degrau fechado)
DST = MD + "authored/conjunto-v174.blend"
assert SRC != DST

# A celula (1.12,-0.15) le '.' (escuro) mesmo com o topo do modelo em 1.233 ali: e superficie escura,
# nao ausencia de geometria, e o v172 provou que mexer na ORIENTACAO piora (luminancia 125 -> 118.5).
# MESMA TECNICA DO v173 (a que funcionou): solido fechado novo, agora MAIOR, cobrindo tambem x=-0.15.
CX, CZ = -0.130, 1.150
RX, RY, RZ = 0.045, 0.062, 0.075   # x -0.175..-0.085 | |y|<=0.062 | z 1.075..1.225

bpy.ops.wm.open_mainfile(filepath=SRC)
bpy.context.view_layer.update()

antigo = bpy.data.objects.get("P_RearTop")
assert antigo is not None, "P_RearTop ausente no v173"
mat = antigo.data.materials[0]
print("###V174### removendo P_RearTop antigo (verts=%d)" % len(antigo.data.vertices))
bpy.data.objects.remove(antigo, do_unlink=True)

bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=12, radius=1.0, location=(CX, 0.0, CZ))
ob = bpy.context.active_object
ob.name = "P_RearTop"
ob.data.name = "M_RearTop"
ob.scale = (RX, RY, RZ)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
ob.data.materials.append(mat)
for p in ob.data.polygons:
    p.material_index = 0
ob.data.update()
bpy.context.view_layer.update()

dg = bpy.context.evaluated_depsgraph_get()
sc = bpy.context.scene
print("###V174### silhueta (concept 1.218 em -0.12..-0.10):")
for x in (-0.17, -0.16, -0.15, -0.14, -0.13, -0.12, -0.11, -0.10):
    z = 1.35
    hit = None
    while z > 0.95:
        ok, loc, nor, idx, obh, mwd = sc.ray_cast(dg, Vector((x, 5.0, z)), Vector((0, -1, 0)))
        if ok:
            hit = (round(z, 3), obh.name)
            break
        z -= 0.005
    print("###V174###   x%+.2f topo=%s" % (x, hit))
print("###V174### checando a celula (1.12,-0.15):")
for z in (1.10, 1.12, 1.14):
    ok, loc, nor, idx, obh, mwd = sc.ray_cast(dg, Vector((-0.15, 5.0, z)), Vector((0, -1, 0)))
    if ok and idx >= 0:
        ev = obh.evaluated_get(dg)
        mi = ev.data.polygons[idx].material_index
        nome = obh.material_slots[mi].material.name if mi < len(obh.material_slots) else "-"
        print("###V174###   z=%.2f -> %s[%s] y%+.3f ny%+.2f" % (z, obh.name, nome, loc.y, nor.y))
    else:
        print("###V174###   z=%.2f -> VAZIO" % z)
bpy.ops.wm.save_as_mainfile(filepath=DST)
print("###V174### salvo:", DST)
