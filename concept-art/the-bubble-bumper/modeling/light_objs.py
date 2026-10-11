import bpy
from mathutils import Vector

MD = "/mnt/storage2TB/Coding-Projects/super-kart-3djs/concept-art/the-bubble-bumper/modeling/"
bpy.ops.wm.open_mainfile(filepath=MD + "authored/conjunto-v141.blend")

X0, X1 = -0.360, -0.160
Z0, Z1 = 0.940, 1.120

def base_col(mat):
    try:
        n = mat.node_tree.nodes.get("Principled BSDF")
        if n:
            c = n.inputs["Base Color"].default_value
            return (round(c[0], 2), round(c[1], 2), round(c[2], 2))
    except Exception:
        pass
    return None

print("###LISTA### objetos com bbox intersectando x %.2f..%.2f  z %.2f..%.2f" % (X0, X1, Z0, Z1))
rows = []
for o in bpy.data.objects:
    if o.type != 'MESH':
        continue
    mw = o.matrix_world
    xs = []; ys = []; zs = []
    for c in o.bound_box:
        w = mw @ Vector(c)
        xs.append(w.x); ys.append(w.y); zs.append(w.z)
    if max(xs) < X0 or min(xs) > X1 or max(zs) < Z0 or min(zs) > Z1:
        continue
    mats = [ms.material.name for ms in o.material_slots if ms.material]
    col = base_col(o.material_slots[0].material) if o.material_slots and o.material_slots[0].material else None
    lum = sum(col) / 3.0 if col else -1
    rows.append((min(xs), o.name, mats, col, lum, min(zs), max(zs), max(abs(min(ys)), abs(max(ys)))))

for r in sorted(rows):
    print("  x %+.3f | %-16s | mat=%-22s | base=%s L=%.2f | z %.3f..%.3f | |y|max %.3f" % (
        r[0], r[1], ",".join(r[2])[:22], str(r[3]), r[4], r[5], r[6], r[7]))

print("###LISTA### total %d objetos na zona" % len(rows))
print("###LISTA### SOMENTE CLAROS (L >= 0.45):")
for r in sorted(rows):
    if r[4] >= 0.45:
        print("  CLARO: %-16s mat=%-20s base=%s L=%.2f | x %+.3f | z %.3f..%.3f | |y|max %.3f" % (
            r[1], ",".join(r[2])[:20], str(r[3]), r[4], r[0], r[5], r[6], r[7]))
