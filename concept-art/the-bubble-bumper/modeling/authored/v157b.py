import bpy
import bmesh

MD = "/mnt/storage2TB/Coding-Projects/super-kart-3djs/concept-art/the-bubble-bumper/modeling/"
SRC = MD + "authored/conjunto-v155.blend"
DST = MD + "authored/conjunto-v157.blend"
assert SRC != DST, "nao sobrescrever"

# Zona da fenda MEDIDA no concept com o python do sistema (PIL), injetada como literal:
#   ###FENDA### x -0.280..-0.250  z 1.055..1.090  (22 amostras)
zx0, zx1 = -0.280, -0.250
zz0, zz1 = 1.055, 1.090
print("###V157### zona da fenda (medida no concept): x %.3f..%.3f z %.3f..%.3f" % (zx0, zx1, zz0, zz1))

bpy.ops.wm.open_mainfile(filepath=SRC)
bpy.context.view_layer.update()
objs = {o.name: o for o in bpy.data.objects}
plate = objs.get("P_FacePlate")
assert plate is not None, "P_FacePlate ausente"
me = plate.data
print("###V157### P_FacePlate antes: faces=%d verts=%d" % (len(me.polygons), len(me.vertices)))

bm = bmesh.new()
bm.from_mesh(me)
bmesh.ops.subdivide_edges(bm, edges=bm.edges[:], cuts=24, use_grid_fill=True)
bm.to_mesh(me)
bm.free()
me.update()
print("###V157### P_FacePlate depois da subdivisao: faces=%d verts=%d" % (len(me.polygons), len(me.vertices)))

mat = bpy.data.materials.get("M_Slit")
if mat is None:
    mat = bpy.data.materials.new("M_Slit")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (0.10, 0.10, 0.12, 1.0)
        if "Roughness" in bsdf.inputs:
            bsdf.inputs["Roughness"].default_value = 0.45
nomes = [s.material.name for s in plate.material_slots if s.material]
if mat.name not in nomes:
    plate.data.materials.append(mat)
si = [i for i, s in enumerate(plate.material_slots) if s.material and s.material.name == mat.name][0]
print("###V157### slot M_Slit = %d | slots antes: %s" % (si, nomes))

mw = plate.matrix_world
nrm = mw.to_3x3().inverted().transposed()
pintadas = 0
for p in me.polygons:
    c = mw @ p.center
    nw = (nrm @ p.normal).normalized()
    if zx0 - 0.005 <= c.x <= zx1 + 0.005 and zz0 - 0.004 <= c.z <= zz1 + 0.004 and abs(nw.y) > 0.55:
        p.material_index = si
        pintadas += 1
print("###V157### faces pintadas na fenda: %d" % pintadas)
assert pintadas >= 4, "poucas faces pintadas (%d)" % pintadas

bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=DST)
print("###V157### salvo:", DST)
