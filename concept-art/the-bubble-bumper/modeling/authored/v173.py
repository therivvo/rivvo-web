import bpy
from mathutils import Vector

MD = "/mnt/storage2TB/Coding-Projects/super-kart-3djs/concept-art/the-bubble-bumper/modeling/"
SRC = MD + "authored/conjunto-v168.blend"
DST = MD + "authored/conjunto-v173.blend"
assert SRC != DST

# 4 tentativas de fechar o degrau falharam (mover, esticar, extrudar regiao, piso de largura).
# A extrusao de REGIAO deu 54 arestas non-manifold: a regiao nao era uma tampa com loop fechado.
# ESTRATEGIA NOVA, segura por construcao: criar um SOLIDO FECHADO NOVO (uv sphere) sobreposto ao
# casco no topo-traseiro. Cada objeto continua manifold (o gate mede por objeto) e o contato mantem
# 1 componente. O solido preenche o degrau: silhueta do modelo 1.020 -> alvo ~1.218 em x -0.12..-0.10.
CX, CZ = -0.115, 1.155
RX, RY, RZ = 0.030, 0.058, 0.062   # alcance: x -0.145..-0.085 | |y|<=0.058 | z 1.093..1.217

bpy.ops.wm.open_mainfile(filepath=SRC)
bpy.context.view_layer.update()

helm = bpy.data.objects.get("P_Helmet")
assert helm is not None
mat = None
for s in helm.material_slots:
    if s.material and s.material.name == "Helmet_Blue":
        mat = s.material
assert mat is not None, "material Helmet_Blue nao encontrado no P_Helmet"

bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=12, radius=1.0, location=(CX, 0.0, CZ))
ob = bpy.context.active_object
ob.name = "P_RearTop"
ob.data.name = "M_RearTop"
ob.scale = (RX, RY, RZ)
ob.rotation_euler = (0.0, 0.0, 0.0)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
ob.data.materials.append(mat)
for p in ob.data.polygons:
    p.material_index = 0
ob.data.update()
bpy.context.view_layer.update()

# conferencia: silhueta por coluna (concept 1.218 em -0.12..-0.10; modelo antes 1.020)
dg = bpy.context.evaluated_depsgraph_get()
sc = bpy.context.scene
print("###V173### P_RearTop criado em (%.3f, 0, %.3f) raios (%.3f,%.3f,%.3f)" % (CX, CZ, RX, RY, RZ))
print("###V173### silhueta DEPOIS (concept 1.218 em -0.12..-0.10 | modelo antes 1.020):")
for x in (-0.15, -0.14, -0.13, -0.12, -0.11, -0.10, -0.09):
    z = 1.35
    hit = None
    while z > 0.95:
        ok, loc, nor, idx, obh, mwd = sc.ray_cast(dg, Vector((x, 5.0, z)), Vector((0, -1, 0)))
        if ok:
            hit = (round(z, 3), obh.name)
            break
        z -= 0.005
    print("###V173###   x%+.2f topo=%s" % (x, hit))
bpy.ops.wm.save_as_mainfile(filepath=DST)
print("###V173### salvo:", DST)
