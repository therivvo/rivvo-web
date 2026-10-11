import bpy
import mathutils

MD = "/mnt/storage2TB/Coding-Projects/super-kart-3djs/concept-art/the-bubble-bumper/modeling/"
SRC = MD + "authored/conjunto-v155.blend"
DST = MD + "authored/conjunto-v158.blend"
assert SRC != DST, "nao sobrescrever"

# Zona da fenda MEDIDA no concept (python do sistema/PIL): x -0.280..-0.250  z 1.055..1.090
zx0, zx1 = -0.280, -0.250
zz0, zz1 = 1.055, 1.090
CX, CZ = (zx0 + zx1) / 2.0, (zz0 + zz1) / 2.0

bpy.ops.wm.open_mainfile(filepath=SRC)
dg = bpy.context.view_layer.depsgraph
bpy.context.view_layer.update()

# ---- RAYCAST decide QUAL OBJETO e a superficie externa na fenda (regra 324: geometria antes de material)
ok, loc, nrm, idx, obj, mw = bpy.context.scene.ray_cast(
    dg, mathutils.Vector((CX, 6.0, CZ)), mathutils.Vector((0.0, -1.0, 0.0)))
assert ok and obj is not None, "raycast nao achou superficie na fenda"
mi = obj.data.polygons[idx].material_index
mat_antes = obj.material_slots[mi].material.name if mi < len(obj.material_slots) and obj.material_slots[mi].material else "-"
print("###V158### RAYCAST na fenda (x=%.3f z=%.3f): objeto=%s  material=%s  (y=%.3f)"
      % (CX, CZ, obj.name, mat_antes, loc.y))

alvo = obj
me = alvo.data
print("###V158### alvo %s: faces=%d verts=%d" % (alvo.name, len(me.polygons), len(me.vertices)))

mat = bpy.data.materials.get("M_Slit")
if mat is None:
    mat = bpy.data.materials.new("M_Slit")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (0.10, 0.10, 0.12, 1.0)
        if "Roughness" in bsdf.inputs:
            bsdf.inputs["Roughness"].default_value = 0.45
nomes = [s.material.name for s in alvo.material_slots if s.material]
if mat.name not in nomes:
    me.materials.append(mat)
si = [i for i, s in enumerate(alvo.material_slots) if s.material and s.material.name == mat.name][0]
print("###V158### slot M_Slit = %d | slots antes: %s" % (si, nomes))

mw = alvo.matrix_world
nrm3 = mw.to_3x3().inverted().transposed()
pintadas = 0
for p in me.polygons:
    c = mw @ p.center
    nw = (nrm3 @ p.normal).normalized()
    if zx0 - 0.006 <= c.x <= zx1 + 0.006 and zz0 - 0.005 <= c.z <= zz1 + 0.005 and abs(nw.y) > 0.55:
        p.material_index = si
        pintadas += 1
print("###V158### faces pintadas na fenda em %s: %d" % (alvo.name, pintadas))
assert pintadas >= 2, "poucas faces pintadas (%d)" % pintadas

bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=DST)
print("###V158### salvo:", DST)
