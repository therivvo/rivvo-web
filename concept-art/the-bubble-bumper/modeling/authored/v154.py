import bpy
from mathutils import Vector

MD = "/mnt/storage2TB/Coding-Projects/super-kart-3djs/concept-art/the-bubble-bumper/modeling/"
SRC = MD + "authored/conjunto-v153.blend"
DST = MD + "authored/conjunto-v154.blend"
assert SRC != DST, 'nao sobrescrever'
bpy.ops.wm.open_mainfile(filepath=SRC)
bpy.context.view_layer.update()

# v154 SURGERY B: em x=-0.18 e -0.16 o pixel de z=0.94 e FUNDO (sem geometria). A placa termina em
# z=0.960 e o concept tem CLARO ate 0.920/0.910. Primeiro falta GEOMETRIA, depois material.
ob = bpy.data.objects.get('P_FacePlate')
assert ob is not None and ob.type == 'MESH', 'P_FacePlate ausente'
ob.data = ob.data.copy()
me = ob.data
mw = ob.matrix_world.copy()
inv = mw.inverted()

pts = [mw @ Vector(c) for c in ob.bound_box]
z0 = min(p.z for p in pts); z1 = max(p.z for p in pts)
x0 = min(p.x for p in pts); x1 = max(p.x for p in pts)
print("###V154### P_FacePlate antes: x %.3f..%.3f | z %.3f..%.3f | verts=%d" % (x0, x1, z0, z1, len(me.vertices)))

NOVO_FUNDO = 0.905
delta = NOVO_FUNDO - z0
assert delta < 0, 'delta deveria ser negativo'
moveram = 0
for v in me.vertices:
    w = mw @ v.co
    if abs(w.z - z0) < 0.006:      # so o fundo da placa
        w.z += delta
        v.co = inv @ w
        moveram += 1
me.update()
bpy.context.view_layer.update()
print("###V154### verts do fundo movidos: %d | delta %.3f" % (moveram, delta))

pts2 = [ob.matrix_world @ Vector(c) for c in ob.bound_box]
z0b = min(p.z for p in pts2); z1b = max(p.z for p in pts2)
print("###V154### P_FacePlate depois: z %.3f..%.3f (alvo fundo %.3f)" % (z0b, z1b, NOVO_FUNDO))
assert abs(z0b - NOVO_FUNDO) < 0.002, 'fundo nao chegou no alvo'

# confere por raio o que aparece nas colunas onde faltava claro
dg = bpy.context.evaluated_depsgraph_get(); sc = bpy.context.scene
DIR = Vector((0, -1, 0))
def mat_de(o, idx):
    try:
        mi = o.data.polygons[idx].material_index
        if 0 <= mi < len(o.data.materials) and o.data.materials[mi]:
            return o.data.materials[mi].name
    except Exception:
        pass
    return '-'
print("###V154### raio depois (x, z) -> objeto[material]:")
for x in (-0.20, -0.18, -0.16, -0.15):
    for z in (0.92, 0.94, 0.96):
        ok, loc, nor, idx, obj, m = sc.ray_cast(dg, Vector((x, 2.0, z)), DIR)
        if ok:
            print("###V154###   x=%+.2f z=%.2f -> %-13s [%s]" % (x, z, obj.name, mat_de(obj, idx)))
        else:
            print("###V154###   x=%+.2f z=%.2f -> VAZIO" % (x, z))

bpy.ops.wm.save_as_mainfile(filepath=DST)
print("###V154### salvo %s" % DST.split('/')[-1])
