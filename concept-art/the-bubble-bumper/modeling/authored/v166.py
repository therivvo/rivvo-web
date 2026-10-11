import bpy
from mathutils import Vector

MD = "/mnt/storage2TB/Coding-Projects/super-kart-3djs/concept-art/the-bubble-bumper/modeling/"
SRC = MD + "authored/conjunto-v165.blend"
DST = MD + "authored/conjunto-v166.blend"
assert SRC != DST

# (c) teto -0.006 nas 2 colunas que ainda leem 1 px alto (modelo termina ~1.098, concept 1.095/1.085)
TETO = {-0.30: 1.089, -0.29: 1.094, -0.28: 1.110, -0.27: 1.110, -0.26: 1.110, -0.25: 1.105,
        -0.24: 1.105, -0.23: 1.100, -0.22: 1.100, -0.16: 1.085, -0.15: 1.079, -0.14: 1.125,
        -0.13: 1.075, -0.12: 1.075}
ZINF = {-0.30: 1.040, -0.29: 1.020, -0.28: 0.985, -0.27: 0.990, -0.26: 0.980, -0.25: 0.965,
        -0.24: 0.960, -0.23: 0.955, -0.22: 0.940, -0.21: 0.935, -0.20: 0.930, -0.19: 0.935,
        -0.18: 0.920, -0.17: 0.915, -0.16: 0.910, -0.15: 0.915, -0.14: 0.900, -0.13: 0.895,
        -0.12: 0.900}
COROA = 1.110
ZX0, ZX1, ZZ0, ZZ1 = -0.285, -0.245, 1.048, 1.096


def tab(t, x, padrao):
    k = round(round(x / 0.01) * 0.01, 3)
    return t[k] if k in t else padrao


bpy.ops.wm.open_mainfile(filepath=SRC)
bpy.context.view_layer.update()

# ---------- DIAGNOSTICO PRIMEIRO: o que existe em x -0.25..-0.19, z 0.96..1.04 ----------
print("###DIAG166### grade de raycast (camera olha -y, origem y=+5):")
dg = bpy.context.evaluated_depsgraph_get()
sc = bpy.context.scene
objs = [o for o in sc.objects if o.type == 'MESH' and o.visible_get()]
for zi in range(9):
    z = 0.96 + zi * 0.01
    linha = []
    for xi in range(7):
        x = -0.25 + xi * 0.01
        ok, loc, nor, idx, ob, mw = sc.ray_cast(dg, Vector((x, 5.0, z)), Vector((0, -1, 0)))
        if not ok:
            linha.append("VAZIO    ")
        else:
            mat = "-"
            if idx >= 0:
                ev = ob.evaluated_get(dg)
                if idx < len(ev.data.polygons):
                    mi = ev.data.polygons[idx].material_index
                    if mi < len(ob.material_slots) and ob.material_slots[mi].material:
                        mat = ob.material_slots[mi].material.name
            linha.append("%-9s%+5.3f ny%+4.2f" % (mat, loc.y, nor.y))
    print("###DIAG166### z=%.2f | %s" % (z, " | ".join(linha)))

# ---------- (c) teto medido atualizado ----------
helm = bpy.data.objects.get("P_Helmet")
assert helm is not None
me = helm.data
mwh = helm.matrix_world
nrh = mwh.to_3x3().inverted().transposed()
il = [i for i, s in enumerate(helm.material_slots) if s.material and s.material.name == "Visor_Light"][0]
ia = [i for i, s in enumerate(helm.material_slots) if s.material and s.material.name == "Helmet_Blue"][0]
isl = [i for i, s in enumerate(helm.material_slots) if s.material and s.material.name == "M_Slit"][0]
add = rem = slit = 0
for p in me.polygons:
    c = mwh @ p.center
    nw = (nrh @ p.normal).normalized()
    if not (-0.31 <= c.x <= -0.115):
        continue
    if ZX0 <= c.x <= ZX1 and ZZ0 <= c.z <= ZZ1 and abs(nw.y) > 0.55:
        if p.material_index != isl:
            p.material_index = isl
            slit += 1
        continue
    dentro = (tab(ZINF, c.x, 0.90) <= c.z <= tab(TETO, c.x, COROA)) and abs(nw.y) > 0.55
    if dentro and p.material_index != il:
        p.material_index = il
        add += 1
    elif (not dentro) and p.material_index == il:
        p.material_index = ia
        rem += 1
print("###V166### casco: +%d claras | -%d removidas (teto -0.006 em -0.30/-0.29/-0.15) | %d fenda" % (add, rem, slit))
me.update()
bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=DST)
print("###V166### salvo:", DST)
