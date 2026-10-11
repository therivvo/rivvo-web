import bpy

MD = "/mnt/storage2TB/Coding-Projects/super-kart-3djs/concept-art/the-bubble-bumper/modeling/"
SRC = MD + "authored/conjunto-v160.blend"
DST = MD + "authored/conjunto-v161.blend"
assert SRC != DST, "nao sobrescrever"

# ---- MEDIDO no concept (python do sistema) ----
# fenda: RGB medio (73,77,78) soma 229 -> 'o' | modelo rende 177..211 -> 'D' -> M_Slit 0.17 -> 0.25
# faixa clara em x=-0.22: concept (137,147,157) 441 em TODA a altura | modelo 289..299 em face
#   angulada (ny 0.73..0.79) -> base do M_VILL 0.62..0.73 -> 0.95..1.00 (maximo fisico da base)
# linha preta de ventilacao: concept (0,0,4) / (16,17,19) / (10,11,15) em x -0.17..-0.14, z 1.06..1.07
#   -> base ~0.02 (preto real, nao tom)
SLIT_BASE = 0.25
VILL_BASE = (0.95, 0.97, 1.00)
LINHA = (-0.175, -0.135, 1.052, 1.078)   # x0, x1, z0, z1 da linha preta
# z_inf MEDIDO por coluna (borda inferior da faixa clara)
ZINF = {-0.30: 1.040, -0.29: 1.020, -0.28: 0.985, -0.27: 0.990, -0.26: 0.980, -0.25: 0.965,
        -0.24: 0.960, -0.23: 0.955, -0.22: 0.940, -0.21: 0.935, -0.20: 0.930, -0.19: 0.935,
        -0.18: 0.920, -0.17: 0.915, -0.16: 0.910, -0.15: 0.915, -0.14: 0.900, -0.13: 0.895,
        -0.12: 0.900}
TETO_PAINEL = 1.110


def zinf_de(x):
    k = round(round(x / 0.01) * 0.01, 3)
    if k in ZINF:
        return ZINF[k]
    ks = sorted(ZINF)
    return ZINF[min(ks, key=lambda c: abs(c - x))]


bpy.ops.wm.open_mainfile(filepath=SRC)
bpy.context.view_layer.update()
dg = bpy.context.view_layer.depsgraph


def setbase(nome, rgb, rough=None):
    m = bpy.data.materials.get(nome)
    assert m is not None, "material %s ausente" % nome
    b = m.node_tree.nodes.get("Principled BSDF")
    assert b is not None, "sem Principled em %s" % nome
    ant = tuple(round(v, 3) for v in b.inputs["Base Color"].default_value)
    b.inputs["Base Color"].default_value = (rgb[0], rgb[1], rgb[2], 1.0)
    if rough is not None and "Roughness" in b.inputs:
        b.inputs["Roughness"].default_value = rough
    print("###V161### %s base %s -> %s%s" % (nome, ant, tuple(round(v, 3) for v in rgb),
                                             (" rough=%.2f" % rough) if rough is not None else ""))


setbase("M_Slit", (SLIT_BASE, SLIT_BASE, SLIT_BASE + 0.02))
setbase("Visor_Light", VILL_BASE, rough=0.30)

# material da linha preta
mat = bpy.data.materials.get("M_BlackLine")
if mat is None:
    mat = bpy.data.materials.new("M_BlackLine")
    mat.use_nodes = True
    b = mat.node_tree.nodes.get("Principled BSDF")
    if b:
        b.inputs["Base Color"].default_value = (0.02, 0.02, 0.02, 1.0)
        if "Roughness" in b.inputs:
            b.inputs["Roughness"].default_value = 0.5
print("###V161### M_BlackLine criado/ok")

# ---- 1) LINHA PRETA na placa ----
placa = bpy.data.objects.get("P_FacePlate")
assert placa is not None, "P_FacePlate ausente"
nomes = [s.material.name for s in placa.material_slots if s.material]
if "M_BlackLine" not in nomes:
    placa.data.materials.append(mat)
import bmesh
bm = bmesh.new(); bm.from_mesh(placa.data)
bmesh.ops.subdivide_edges(bm, edges=bm.edges[:], cuts=24, use_grid_fill=True)
bm.to_mesh(placa.data); bm.free(); placa.data.update()
print("###V161### placa subdividida: faces=%d (a placa vinha com 6, o quad frontal era unico)" % len(placa.data.polygons))
si = [i for i, s in enumerate(placa.material_slots) if s.material and s.material.name == "M_BlackLine"][0]
mw = placa.matrix_world
nrm = mw.to_3x3().inverted().transposed()
pint = 0
for p in placa.data.polygons:
    c = mw @ p.center
    nw = (nrm @ p.normal).normalized()
    if LINHA[0] <= c.x <= LINHA[1] and LINHA[2] <= c.z <= LINHA[3] and abs(nw.y) > 0.55:
        p.material_index = si
        pint += 1
print("###V161### faces da placa pintadas de PRETO (linha): %d" % pint)
assert pint >= 2, "linha preta sem faces (%d)" % pint

# ---- 2) FAIXA do casco re-derivada pela TABELA MEDIDA ----
helm = bpy.data.objects.get("P_Helmet")
assert helm is not None, "P_Helmet ausente"
me = helm.data
mwh = helm.matrix_world
nrh = mwh.to_3x3().inverted().transposed()
il = [i for i, s in enumerate(helm.material_slots) if s.material and s.material.name == "Visor_Light"][0]
ia = [i for i, s in enumerate(helm.material_slots) if s.material and s.material.name == "Helmet_Blue"][0]
add = rem = 0
for p in me.polygons:
    c = mwh @ p.center
    nw = (nrh @ p.normal).normalized()
    if not (-0.31 <= c.x <= -0.115):
        continue
    dentro = (zinf_de(c.x) <= c.z <= TETO_PAINEL) and abs(nw.y) > 0.55
    if dentro and p.material_index != il:
        p.material_index = il
        add += 1
    elif (not dentro) and p.material_index == il:
        p.material_index = ia
        rem += 1
print("###V161### casco: +%d faces claras | -%d claras removidas (tabela medida)" % (add, rem))
me.update()
bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=DST)
print("###V161### salvo:", DST)
