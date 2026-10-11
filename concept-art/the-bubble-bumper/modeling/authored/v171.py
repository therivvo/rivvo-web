import bpy
import bmesh
from mathutils import Vector

MD = "/mnt/storage2TB/Coding-Projects/super-kart-3djs/concept-art/the-bubble-bumper/modeling/"
SRC = MD + "authored/conjunto-v168.blend"
DST = MD + "authored/conjunto-v171.blend"
assert SRC != DST

# O degrau (0.198 m em x -0.12..-0.10) nao fecha movendo/esticando verts (v169 e v170 regrediram).
# Agora: CRIAR geometria — extrusao da regiao traseira-ALTA do casco, depois transladar para tras/cima.
ZMIN = 1.040          # so a parte alta do casco
DXT = 0.050           # para tras
DZT = 0.110           # para cima (alvo: silhueta 1.02 -> ~1.218)

bpy.ops.wm.open_mainfile(filepath=SRC)
bpy.context.view_layer.update()

helm = bpy.data.objects.get("P_Helmet")
assert helm is not None, "P_Helmet ausente"
mw = helm.matrix_world
bpy.context.view_layer.objects.active = helm
helm.select_set(True)

bm = bmesh.new()
bm.from_mesh(helm.data)
bm.verts.ensure_lookup_table()
bm.faces.ensure_lookup_table()

# 1) medir a extensao traseira do casco na parte alta
altos = [mw @ v.co for v in bm.verts if (mw @ v.co).z >= ZMIN]
assert altos, "nenhum vert acima de z=%.3f" % ZMIN
xmax = max(w.x for w in altos)
print("###V171### casco: %d verts em z>=%.2f | x max na parte alta = %.4f" % (len(altos), ZMIN, xmax))

# 2) selecionar as faces da tampa traseira-alta (a ultima fatia em x)
XCAP = xmax - 0.012
alvo = []
for f in bm.faces:
    c = mw @ f.calc_center_median()
    if c.z >= ZMIN and c.x >= XCAP:
        alvo.append(f)
print("###V171### faces na tampa traseira-alta: %d (x >= %.4f)" % (len(alvo), XCAP))
assert len(alvo) >= 1, "nenhuma face na tampa — ajustar XCAP"

# 3) extrudar a regiao e transladar
res = bmesh.ops.extrude_face_region(bm, geom=alvo)
novos_verts = [e for e in res["geom"] if isinstance(e, bmesh.types.BMVert)]
print("###V171### verts criados pela extrusao: %d" % len(novos_verts))
assert novos_verts, "extrusao nao criou verts"
for v in novos_verts:
    v.co = v.co + Vector((DXT, 0.0, DZT))
bm.normal_update()
me_nova = bpy.data.meshes.new("tmp_helmet_v171")
bm.to_mesh(me_nova)
bm.free()
helm.data = me_nova
helm.data.update()
bpy.context.view_layer.update()

# 4) conferencia da silhueta por coluna (mesma janela do degrau)
dg = bpy.context.evaluated_depsgraph_get()
sc = bpy.context.scene
print("###V171### silhueta DEPOIS (concept: 1.218 em -0.12..-0.10; modelo antes: 1.020):")
for x in (-0.14, -0.13, -0.12, -0.11, -0.10):
    z = 1.35
    hit = None
    while z > 0.95:
        ok, loc, nor, idx, ob, mwd = sc.ray_cast(dg, Vector((x, 5.0, z)), Vector((0, -1, 0)))
        if ok:
            hit = (round(z, 3), ob.name)
            break
        z -= 0.005
    print("###V171###   x%+.2f topo=%s" % (x, hit))

bpy.ops.wm.save_as_mainfile(filepath=DST)
print("###V171### salvo:", DST)
