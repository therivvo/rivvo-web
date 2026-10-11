import bpy
from mathutils import Vector

MD = "/mnt/storage2TB/Coding-Projects/super-kart-3djs/concept-art/the-bubble-bumper/modeling/"
bpy.ops.wm.open_mainfile(filepath=MD + "authored/conjunto-v146.blend")

dg = bpy.context.evaluated_depsgraph_get()
sc = bpy.context.scene
DIR = Vector((0, -1, 0))   # camera SIDE olha de +y para -y
Y0 = 2.0

xs = [-0.30, -0.28, -0.26, -0.24, -0.22, -0.20, -0.18]
zs = [1.08, 1.06, 1.04, 1.02]

print("###RAY### SIDE: objeto visivel por (x,z)  [primeiro hit vindo de +y]")
print("###RAY###  x\\z    " + "   ".join("z=%.2f" % z for z in zs))
for x in xs:
    row = []
    for z in zs:
        ok, loc, nor, idx, obj, mw = sc.ray_cast(dg, Vector((x, Y0, z)), DIR)
        if not ok:
            row.append("VAZIO")
            continue
        mat = None
        if obj and obj.type == 'MESH' and idx is not None and idx < len(obj.data.polygons):
            mi = obj.data.polygons[idx].material_index
            if mi < len(obj.material_slots) and obj.material_slots[mi].material:
                mat = obj.material_slots[mi].material.name
        nm = obj.name if obj else "?"
        row.append("%s[%s]" % (nm, mat or "-"))
    print("x=%+.2f  " % x + "  ".join(row))

print()
print("###RAY### POR QUE NAO FOI PINTADA: face atingida, centro em mundo e teste da zona")
print("###RAY### zona de pintura: x -0.307..-0.137 | z 0.960..1.100 | |n.y| > 0.60")

for x in (-0.26, -0.24, -0.22):
    for z in (1.08, 1.06, 1.04, 1.02):
        ok, loc, nor, idx, obj, mw = sc.ray_cast(dg, Vector((x, Y0, z)), DIR)
        if ok:
            mi = obj.data.polygons[idx].material_index
            mat = obj.material_slots[mi].material.name if mi < len(obj.material_slots) and obj.material_slots[mi].material else '-'
            p = obj.data.polygons[idx]
            c = obj.matrix_world @ p.center
            n = (obj.matrix_world.to_3x3() @ p.normal)
            n = n / n.length if n.length > 1e-9 else n
            inx = -0.307 <= c.x <= -0.137
            inz = 0.960 <= c.z <= 1.100
            inny = abs(n.y) > 0.60
            print("   x=%+.2f z=%.2f -> %-12s mat=%-14s | face#%d centro=(%+.3f,%+.3f) n.y=%+.2f | inX=%d inZ=%d inNY=%d -> %s" % (
                x, z, obj.name, mat, idx, c.x, c.z, n.y, inx, inz, inny,
                "PINTARIA" if (inx and inz and inny) else "NAO PINTARIA"))
        else:
            print("   x=%+.2f z=%.2f -> VAZIO" % (x, z))
