import bpy
import mathutils

MD = "/mnt/storage2TB/Coding-Projects/super-kart-3djs/concept-art/the-bubble-bumper/modeling/"
BLEND = MD + "authored/conjunto-v160.blend"

# Cada celula que falha na grade SIDE (amostra "dentro -0.15"), com o que o CONCEPT pede:
FALHAS = [
    (1.12, -0.15, 'B'), (1.10, -0.30, 'B'), (1.10, -0.15, 'B'),
    (1.08, -0.26, 'o'), (1.06, -0.26, 'o'), (1.06, -0.22, 'L'),
    (1.06, -0.15, 'D'), (1.04, -0.22, 'L'), (1.02, -0.26, 'L'),
    (1.00, -0.26, 'L'), (1.00, -0.22, 'L'), (0.96, -0.15, '.'),
    (0.94, -0.22, 'L'),
]

bpy.ops.wm.open_mainfile(filepath=BLEND)
dg = bpy.context.view_layer.depsgraph
bpy.context.view_layer.update()

print("###DIAG### celula -> superficie REAL (objeto[material]) | o que o concept pede")
resumo = {}
for z, x, quer in FALHAS:
    ok, loc, nrm, idx, obj, mw = bpy.context.scene.ray_cast(
        dg, mathutils.Vector((x, 6.0, z)), mathutils.Vector((0.0, -1.0, 0.0)))
    if not ok or obj is None:
        txt = "VAZIO (sem geometria)"
        resumo.setdefault('VAZIO', []).append((z, x, quer))
    else:
        ev = obj.evaluated_get(dg)          # MODIFIER: indice do ray e do mesh AVALIADO
        mev = ev.data
        if idx is None or idx >= len(mev.polygons):
            mi, nor = 0, mathutils.Vector((0.0, 0.0, 1.0))
        else:
            mi = mev.polygons[idx].material_index
            nor = mev.polygons[idx].normal
        mat = obj.material_slots[mi].material.name if mi < len(obj.material_slots) and obj.material_slots[mi].material else "-"
        nw = (mw.to_3x3().inverted().transposed() @ nor).normalized()
        txt = "%s[%s] y=%.3f ny=%.2f" % (obj.name, mat, loc.y, nw.y)
        resumo.setdefault(obj.name + "[" + mat + "]", []).append((z, x, quer))
    print("###DIAG### z=%.2f x=%+.2f quer=%-2s -> %s" % (z, x, quer, txt))

print()
print("###DIAG### AGRUPADO POR SUPERFICIE (alvo de cada correcao):")
for k, v in sorted(resumo.items(), key=lambda kv: -len(kv[1])):
    print("###DIAG###   %-28s %d celulas: %s" % (k, len(v), " ".join("(z%.2f,x%+.2f,%s)" % t for t in v)))
