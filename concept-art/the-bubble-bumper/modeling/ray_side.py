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
print("###RAY### detalhe das amostras criticas (x -0.26..-0.22, z 1.02..1.08):")
for x in (-0.26, -0.24, -0.22):
    for z in (1.08, 1.06, 1.04, 1.02):
        ok, loc, nor, idx, obj, mw = sc.ray_cast(dg, Vector((x, Y0, z)), DIR)
        if ok:
            mi = obj.data.polygons[idx].material_index
            mat = obj.material_slots[mi].material.name if mi < len(obj.material_slots) and obj.material_slots[mi].material else '-'
            print("   x=%+.2f z=%.2f -> %-14s mat=%-16s hit_y=%+.3f normal=(%.2f,%.2f,%.2f)" % (
                x, z, obj.name, mat, loc.y, nor.x, nor.y, nor.z))
        else:
            print("   x=%+.2f z=%.2f -> VAZIO" % (x, z))
