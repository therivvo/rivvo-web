import bpy
from mathutils import Vector

MD = "/mnt/storage2TB/Coding-Projects/super-kart-3djs/concept-art/the-bubble-bumper/modeling/"
SRC = MD + "authored/conjunto-v177.blend"
OUT = MD + "authored/conjunto-v178.blend"
bpy.ops.wm.open_mainfile(filepath=SRC)

blob = bpy.data.objects.get("P_RearTop")
assert blob is not None, "P_RearTop ausente"
me = blob.data
idx_am = idx_bl = None
for i, s in enumerate(me.materials):
    if s and s.name == "Accent_Yellow":
        idx_am = i
    if s and s.name == "Helmet_Blue":
        idx_bl = i
if idx_am is None:  # material nao esta no slot: criar/adicionar
    mat = bpy.data.materials.get("Accent_Yellow")
    assert mat is not None, "material Accent_Yellow nao existe no arquivo"
    me.materials.append(mat)
    idx_am = len(me.materials) - 1
    for p in me.polygons:
        p.material_index = idx_bl if idx_bl is not None else 0
print("###V178### slots:", [s.material.name for s in blob.material_slots], "amarelo idx=", idx_am)

# o concept pede AMARELO em z 1.10..1.20 e x -0.18..-0.10 (o blob e Helmet_Blue e oculta a faixa).
# Repintar as faces do blob ABAIXO de z=1.19 como Accent_Yellow (o topo segue azul).
n = 0
bpy.context.view_layer.update()
for p in me.polygons:
    c = blob.matrix_world @ p.center
    if c.z < 1.190:
        p.material_index = idx_am
        n += 1
me.update()
print("###V178### faces do blob repintadas para AMARELO:", n, "de", len(me.polygons))
bpy.ops.wm.save_as_mainfile(filepath=OUT)
print("###V178### salvo", OUT)
