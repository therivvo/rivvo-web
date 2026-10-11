import bpy
from mathutils import Vector

MD = "/mnt/storage2TB/Coding-Projects/super-kart-3djs/concept-art/the-bubble-bumper/modeling/"
SRC = MD + "authored/conjunto-v174.blend"   # CANDIDATO (dentro 95%)
DST = MD + "authored/conjunto-v175.blend"
assert SRC != DST

# (3) LINHA PRETA: o concept tem 'D' em (1.06,-0.15); o modelo tem 'L'. O v165 encurtou a linha para
# x -0.163..-0.145 e "passou do ponto". Reestender para x -0.170..-0.142 (faixa do preto no concept).
X0, X1 = -0.170, -0.142
Z0, Z1 = 1.050, 1.080

bpy.ops.wm.open_mainfile(filepath=SRC)
bpy.context.view_layer.update()

# DIAGNOSTICO: quem ocupa o pixel (1.06,-0.15) hoje?
dg = bpy.context.evaluated_depsgraph_get()
sc = bpy.context.scene
print("###V175### quem ocupa x=-0.15 nas alturas 1.04..1.10:")
for z in (1.04, 1.05, 1.06, 1.07, 1.08, 1.10):
    ok, loc, nor, idx, obh, mwd = sc.ray_cast(dg, Vector((-0.15, 5.0, z)), Vector((0, -1, 0)))
    if ok and idx >= 0:
        ev = obh.evaluated_get(dg)
        mi = ev.data.polygons[idx].material_index
        nome = obh.material_slots[mi].material.name if mi < len(obh.material_slots) else "-"
        print("###V175###   z=%.2f -> %s[%s] y%+.3f ny%+.2f" % (z, obh.name, nome, loc.y, nor.y))
    else:
        print("###V175###   z=%.2f -> VAZIO" % z)

# repintar a linha preta na P_FacePlate na janela medida
placa = bpy.data.objects.get("P_FacePlate")
assert placa is not None
ibl = [i for i, s in enumerate(placa.material_slots) if s.material and s.material.name == "M_BlackLine"][0]
ilp = [i for i, s in enumerate(placa.material_slots) if s.material and s.material.name == "Visor_Light"][0]
mwp = placa.matrix_world
nrp = mwp.to_3x3().inverted().transposed()
add = rem = 0
for p in placa.data.polygons:
    c = mwp @ p.center
    nw = (nrp @ p.normal).normalized()
    if abs(nw.y) <= 0.55:
        continue
    dentro = X0 <= c.x <= X1 and Z0 <= c.z <= Z1
    if dentro and p.material_index != ibl:
        p.material_index = ibl
        add += 1
    elif (not dentro) and p.material_index == ibl:
        p.material_index = ilp
        rem += 1
print("###V175### placa: +%d pretas | -%d revertidas para claro (janela x %.3f..%.3f, z %.3f..%.3f)" %
      (add, rem, X0, X1, Z0, Z1))
placa.data.update()
bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=DST)
print("###V175### salvo:", DST)
