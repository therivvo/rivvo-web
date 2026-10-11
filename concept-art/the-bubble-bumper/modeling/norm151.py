import bpy
from mathutils import Vector

MD = "/mnt/storage2TB/Coding-Projects/super-kart-3djs/concept-art/the-bubble-bumper/modeling/"
bpy.ops.wm.open_mainfile(filepath=MD + "authored/conjunto-v151.blend")
bpy.context.view_layer.update()

dg = bpy.context.evaluated_depsgraph_get()
sc = bpy.context.scene
DIR = Vector((0, -1, 0))
Y0 = 2.0


def mat_real(ob, idx):
    """Regra 320: com link='DATA' o material que o render usa esta em ob.data.materials."""
    mat = '-'
    try:
        pol = ob.data.polygons
        if idx is None or not (0 <= idx < len(pol)):
            return mat
        mi = pol[idx].material_index
        if 0 <= mi < len(ob.data.materials) and ob.data.materials[mi]:
            mat = ob.data.materials[mi].name
    except Exception:
        mat = 'ERR'
    return mat


print("###NORM### faixa inferior da banda clara | condicao: z >= 0.924-0.778*(x+0.15), |ny|>0.60")
print("###NORM###  x      z     objeto        material        n.y    n.z   | passaZ passaNY -> veredito")
for x in (-0.20, -0.18, -0.16, -0.15, -0.14):
    zmin = 0.924 - 0.778 * (x + 0.15)
    for z in (0.90, 0.92, 0.93, 0.94, 0.95, 0.96, 0.97, 0.98, 1.00):
        ok, loc, nor, idx, obj, mw = sc.ray_cast(dg, Vector((x, Y0, z)), DIR)
        if not ok:
            print("###NORM### %+.2f  %.2f   VAZIO" % (x, z))
            continue
        n = (obj.matrix_world.to_3x3() @ nor)
        n = n / n.length if n.length > 1e-9 else n
        pz = z >= zmin
        pn = abs(n.y) > 0.60
        print("###NORM### %+.2f  %.2f   %-13s %-14s %+.2f %+.2f |   %s      %s   -> %s" % (
            x, z, obj.name, mat_real(obj, idx), n.y, n.z,
            'S' if pz else 'N', 'S' if pn else 'N',
            'PINTARIA' if (pz and pn) else ('falta Z' if not pz else 'falta NORMAL')))
    print("###NORM###   (z_min exigido nessa coluna = %.3f)" % zmin)
