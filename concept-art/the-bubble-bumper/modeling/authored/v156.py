import bpy
from mathutils import Matrix

MD = "/mnt/storage2TB/Coding-Projects/super-kart-3djs/concept-art/the-bubble-bumper/modeling/"
SRC = MD + "authored/conjunto-v155.blend"
DST = MD + "authored/conjunto-v156.blend"
assert SRC != DST, "nao sobrescrever"

DX, DZ = -0.040, 0.040

bpy.ops.wm.open_mainfile(filepath=SRC)
bpy.context.view_layer.update()


def bbox(o):
    mw = o.matrix_world
    ws = [mw @ v.co for v in o.data.vertices]
    return (min(w.x for w in ws), max(w.x for w in ws),
            min(w.z for w in ws), max(w.z for w in ws))


objs = {o.name: o for o in bpy.data.objects}
vis = objs.get("P_Visor")
assert vis is not None, "P_Visor ausente"
antes = bbox(vis)
print("###V156### P_Visor antes:  x %.3f..%.3f  z %.3f..%.3f" % antes)

vis.matrix_world = Matrix.Translation((DX, 0.0, DZ)) @ vis.matrix_world
bpy.context.view_layer.update()          # REGRA 319: matrix_world sem update fica obsoleto
depois = bbox(vis)
print("###V156### P_Visor depois: x %.3f..%.3f  z %.3f..%.3f" % depois)
assert abs((depois[0] - antes[0]) - DX) < 1e-5, "delta X nao aplicado"
assert abs((depois[2] - antes[2]) - DZ) < 1e-5, "delta Z nao aplicado"

# quem e a superficie frontal nas colunas da fenda (autoridade: raycast da camera SIDE)
import mathutils
cam_y = 6.0
for xw in (-0.28, -0.26, -0.24, -0.22, -0.20):
    linha = []
    for zw in (1.00, 1.02, 1.04, 1.06, 1.08, 1.10):
        ok, loc, nrm, idx, obj, mw = bpy.context.scene.ray_cast(
            bpy.context.view_layer.depsgraph, mathutils.Vector((xw, cam_y, zw)),
            mathutils.Vector((0.0, -1.0, 0.0)))
        if ok and idx is not None:
            mi = obj.data.polygons[idx].material_index if idx < len(obj.data.polygons) else 0
            m = obj.material_slots[mi].material if mi < len(obj.material_slots) else None
            linha.append("%.2f:%s" % (zw, (m.name if m else "-")))
        else:
            linha.append("%.2f:-" % zw)
    print("###V156### ray x=%+.2f -> %s" % (xw, " ".join(linha)))

bpy.ops.wm.save_as_mainfile(filepath=DST)
print("###V156### salvo:", DST)
