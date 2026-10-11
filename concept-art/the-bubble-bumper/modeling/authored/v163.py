import bpy

MD = "/mnt/storage2TB/Coding-Projects/super-kart-3djs/concept-art/the-bubble-bumper/modeling/"
SRC = MD + "authored/conjunto-v162.blend"
DST = MD + "authored/conjunto-v163.blend"
assert SRC != DST, "nao sobrescrever"

# A repintura por TABELA do v161 pintou Visor_Light POR CIMA dos faces escuros da fenda
# (dentro = zinf <= z <= 1.110 and |ny|>0.55 nao excluia a zona da fenda) -> a fenda passou a 'L'.
# Correcao: aplicar a fenda DEPOIS da faixa. Base medida: concept (73,77,78) soma 229 -> 'o'.
SLIT_BASE = 0.20
ZX0, ZX1 = -0.285, -0.245
ZZ0, ZZ1 = 1.048, 1.096

bpy.ops.wm.open_mainfile(filepath=SRC)
bpy.context.view_layer.update()
helm = bpy.data.objects.get("P_Helmet")
assert helm is not None, "P_Helmet ausente"
mat = bpy.data.materials.get("M_Slit")
assert mat is not None, "M_Slit ausente"
b = mat.node_tree.nodes.get("Principled BSDF")
ant = tuple(round(v, 3) for v in b.inputs["Base Color"].default_value)
b.inputs["Base Color"].default_value = (SLIT_BASE, SLIT_BASE, SLIT_BASE + 0.02, 1.0)
print("###V163### M_Slit base %s -> %.2f" % (ant, SLIT_BASE))

me = helm.data
mw = helm.matrix_world
nrm = mw.to_3x3().inverted().transposed()
si = [i for i, s in enumerate(helm.material_slots) if s.material and s.material.name == "M_Slit"][0]
pint = 0
for p in me.polygons:
    c = mw @ p.center
    nw = (nrm @ p.normal).normalized()
    if ZX0 <= c.x <= ZX1 and ZZ0 <= c.z <= ZZ1 and abs(nw.y) > 0.55:
        p.material_index = si
        pint += 1
print("###V163### faces da FENDA repintadas no casco: %d" % pint)
assert pint >= 2, "fenda sem faces (%d)" % pint
me.update()
bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=DST)
print("###V163### salvo:", DST)
