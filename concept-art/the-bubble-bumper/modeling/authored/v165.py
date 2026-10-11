import bpy

MD = "/mnt/storage2TB/Coding-Projects/super-kart-3djs/concept-art/the-bubble-bumper/modeling/"
SRC = MD + "authored/conjunto-v163.blend"
DST = MD + "authored/conjunto-v165.blend"
assert SRC != DST, "nao sobrescrever"

# (A) TETO POR COLUNA MEDIDO (varredura no concept) — o v161 usou TETO_PAINEL=1.110 fixo e o
#     diagnostico de VIZINHANCA mostrou que o modelo pinta claro ~2px alto em x=-0.30 e x=-0.15
#     (concept 'B' em toda a vizinhanca, modelo 'L'). Colunas -0.21..-0.17 = coroa (1.110, nao mexer).
TETO = {-0.30: 1.095, -0.29: 1.100, -0.28: 1.110, -0.27: 1.110, -0.26: 1.110, -0.25: 1.105,
        -0.24: 1.105, -0.23: 1.100, -0.22: 1.100, -0.16: 1.085, -0.15: 1.085, -0.14: 1.125,
        -0.13: 1.075, -0.12: 1.075}
ZINF = {-0.30: 1.040, -0.29: 1.020, -0.28: 0.985, -0.27: 0.990, -0.26: 0.980, -0.25: 0.965,
        -0.24: 0.960, -0.23: 0.955, -0.22: 0.940, -0.21: 0.935, -0.20: 0.930, -0.19: 0.935,
        -0.18: 0.920, -0.17: 0.915, -0.16: 0.910, -0.15: 0.915, -0.14: 0.900, -0.13: 0.895,
        -0.12: 0.900}
COROA = 1.110
# (B) linha preta: concept so tem preto em x -0.17..-0.14 -> encurtar para nao invadir x=-0.18
LINHA = (-0.163, -0.145, 1.052, 1.078)
ZX0, ZX1, ZZ0, ZZ1 = -0.285, -0.245, 1.048, 1.096   # fenda (aplicada DEPOIS da faixa)


def tab(t, x, padrao):
    k = round(round(x / 0.01) * 0.01, 3)
    return t[k] if k in t else padrao


bpy.ops.wm.open_mainfile(filepath=SRC)
bpy.context.view_layer.update()

helm = bpy.data.objects.get("P_Helmet")
assert helm is not None, "P_Helmet ausente"
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
print("###V165### casco: +%d claras | -%d removidas acima do TETO MEDIDO | %d fenda" % (add, rem, slit))
me.update()

placa = bpy.data.objects.get("P_FacePlate")
assert placa is not None, "P_FacePlate ausente"
ilp = [i for i, s in enumerate(placa.material_slots) if s.material and s.material.name == "Visor_Light"][0]
ibl = [i for i, s in enumerate(placa.material_slots) if s.material and s.material.name == "M_BlackLine"][0]
mwp = placa.matrix_world
nrp = mwp.to_3x3().inverted().transposed()
pl = 0
for p in placa.data.polygons:
    c = mwp @ p.center
    nw = (nrp @ p.normal).normalized()
    if abs(nw.y) <= 0.55:
        continue
    if LINHA[0] <= c.x <= LINHA[1] and LINHA[2] <= c.z <= LINHA[3]:
        if p.material_index != ibl:
            p.material_index = ibl
            pl += 1
    elif p.material_index == ibl:
        p.material_index = ilp
        pl += 1
print("###V165### placa: %d faces ajustadas na linha preta (x %.3f..%.3f)" % (pl, LINHA[0], LINHA[1]))
assert pl >= 2, "linha preta sem ajuste (%d)" % pl
placa.data.update()
bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=DST)
print("###V165### salvo:", DST)
