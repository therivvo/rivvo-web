import bpy

MD = "/mnt/storage2TB/Coding-Projects/super-kart-3djs/concept-art/the-bubble-bumper/modeling/"
SRC = MD + "authored/conjunto-v159.blend"
DST = MD + "authored/conjunto-v160.blend"
assert SRC != DST, "nao sobrescrever"

# TETO MEDIDO no concept (varredura de colunas, python do sistema) -> ###TETO###
# Aplicado como REDUCAO: ceiling(x) = min(1.100, z_sup medido). Colunas -0.21..-0.17 tem luz ate
# 1.18-1.20 (coroa do capacete, outra feature) -> min() mantem 1.100 e nao altera nada.
TETO = {
    -0.30: 1.095, -0.29: 1.100, -0.28: 1.110, -0.27: 1.110, -0.26: 1.110,
    -0.25: 1.105, -0.24: 1.105, -0.23: 1.100, -0.22: 1.100,
    -0.16: 1.085, -0.15: 1.085, -0.14: 1.125, -0.13: 1.075, -0.12: 1.075,
}
LIMITE = 1.100


def teto_de(x):
    k = round(round(x / 0.01) * 0.01, 3)
    v = TETO.get(k)
    return LIMITE if v is None else min(LIMITE, v)


bpy.ops.wm.open_mainfile(filepath=SRC)
bpy.context.view_layer.update()
helm = bpy.data.objects.get("P_Helmet")
assert helm is not None, "P_Helmet ausente"
me = helm.data
mw = helm.matrix_world
nrm = mw.to_3x3().inverted().transposed()

idx_luz = [i for i, s in enumerate(helm.material_slots) if s.material and s.material.name == "Visor_Light"]
idx_azul = [i for i, s in enumerate(helm.material_slots) if s.material and s.material.name == "Helmet_Blue"]
assert idx_luz and idx_azul, "slots Visor_Light/Helmet_Blue ausentes"
il, ia = idx_luz[0], idx_azul[0]

removidas = 0
for p in me.polygons:
    if p.material_index != il:
        continue
    c = mw @ p.center
    if c.z > teto_de(c.x) + 0.004:
        p.material_index = ia
        removidas += 1
print("###V160### faces de claro REMOVIDAS acima do teto medido: %d" % removidas)
assert removidas >= 1, "nenhuma face removida (teto sem efeito)"

me.update()
bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=DST)
print("###V160### salvo:", DST)
