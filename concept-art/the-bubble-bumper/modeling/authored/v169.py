import bpy
from mathutils import Vector

MD = "/mnt/storage2TB/Coding-Projects/super-kart-3djs/concept-art/the-bubble-bumper/modeling/"
SRC = MD + "authored/conjunto-v168.blend"
DST = MD + "authored/conjunto-v169.blend"
assert SRC != DST

# CAUSA MEDIDA: medicao de silhueta por coluna (concept vs R168) -> em x -0.12..-0.10 o topo do
# modelo DESPENCA para 1.020 enquanto o concept fica em 1.218: DEGRAU DE 0.198 m. A grade g169
# confirma VAZIO em x -0.14..-0.11 acima de z~1.08 (nenhum objeto) — nao e material nem rasancia.
# CORRECAO: subir o topo-traseiro do P_Helmet nas colunas x -0.145..-0.09, com peso por coluna
# (integral a esquerda, zero em x=-0.09 para nao criar degrau novo na juncao).
ZALVO = 1.218
X0, X1 = -0.150, -0.090   # janela de subida
ZMIN = 0.990              # so o que esta acima disso (topo-traseiro)

bpy.ops.wm.open_mainfile(filepath=SRC)
bpy.context.view_layer.update()

helm = bpy.data.objects.get("P_Helmet")
assert helm is not None, "P_Helmet ausente"
mwh = helm.matrix_world
inv = mwh.inverted()
# altura atual da silhueta do casco na janela, para calcular o dz necessario
topo_atual = {}
for v in helm.data.vertices:
    w = mwh @ v.co
    if X0 <= w.x <= X1 and w.z >= ZMIN:
        k = round(w.x, 2)
        topo_atual[k] = max(topo_atual.get(k, 0.0), w.z)
print("###V169### topo atual do casco na janela:", {k: round(v, 3) for k, v in sorted(topo_atual.items())})

n = 0
dz_max = 0.0
for v in helm.data.vertices:
    w = mwh @ v.co
    if not (X0 <= w.x <= X1) or w.z < ZMIN:
        continue
    # peso: 1.0 em x <= -0.12 ; 0.0 em x = -0.09
    wgt = min(1.0, max(0.0, (-0.09 - w.x) / 0.03))
    if wgt <= 0.0:
        continue
    dz = (ZALVO - 1.020) * wgt
    w.z += dz
    v.co = inv @ w
    n += 1
    dz_max = max(dz_max, dz)
print("###V169### %d verts subidos | dz max %.3f" % (n, dz_max))
assert n >= 3, "poucos verts na janela (%d)" % n
helm.data.update()
bpy.context.view_layer.update()

dg = bpy.context.evaluated_depsgraph_get()
sc = bpy.context.scene
print("###V169### silhueta DEPOIS (alvo concept: 1.218 em x -0.12..-0.10):")
for x in (-0.14, -0.13, -0.12, -0.11, -0.10):
    ok, loc, nor, idx, ob, mw = sc.ray_cast(dg, Vector((x, 5.0, 1.15)), Vector((0, -1, 0)))
    print("###V169###   x%+.2f z=1.15 -> %s" % (x, ("%s[%s] y%+.3f" % (ob.name, ob.material_slots[ob.evaluated_get(dg).data.polygons[idx].material_index].material.name, loc.y)) if ok and idx >= 0 else "VAZIO"))
bpy.ops.wm.save_as_mainfile(filepath=DST)
print("###V169### salvo:", DST)
