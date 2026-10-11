import bpy, bmesh
from mathutils import Vector

MD = "/mnt/storage2TB/Coding-Projects/super-kart-3djs/concept-art/the-bubble-bumper/modeling/"
SRC = MD + "authored/conjunto-v174.blend"   # CANDIDATO (borda 85%, dentro 95%)
OUT = MD + "authored/conjunto-v176.blend"
bpy.ops.wm.open_mainfile(filepath=SRC)

placa = bpy.data.objects.get("P_FacePlate")
assert placa is not None, "P_FacePlate ausente"
me = placa.data
print("###V176### faces ANTES:", len(me.polygons))

# 1) subdividir as faces da placa que estao na zona da linha preta (x -0.19..-0.12, z 1.02..1.11)
bpy.context.view_layer.objects.active = placa
placa.select_set(True)
bm = bmesh.new(); bm.from_mesh(me)
alvo = []
for f in bm.faces:
    c = placa.matrix_world @ f.calc_center_median()
    if -0.19 <= c.x <= -0.12 and 1.02 <= c.z <= 1.11:
        alvo.append(f)
print("###V176### faces na zona:", len(alvo))
for _ in range(3):
    bmesh.ops.subdivide_edges(bm, edges=list({e for f in alvo for e in f.edges}),
                              cuts=1, use_grid_fill=True)
    alvo = [f for f in bm.faces if all(-0.20 <= (placa.matrix_world @ v.co).x <= -0.11 and
                                       1.01 <= (placa.matrix_world @ v.co).z <= 1.12 for v in f.verts)]
print("###V176### faces na zona apos subdiv:", len(alvo))
bm.to_mesh(me); bm.free(); me.update()
print("###V176### faces DEPOIS:", len(me.polygons))
assert len(me.polygons) > 3750, "subdivisao nao aumentou faces"

# 2) pintar a faixa preta: z 1.052..1.075 (>= 0.030 m), x -0.170..-0.140, so na superficie externa
idx_black = None
for i, s in enumerate(me.materials):
    if s and s.name == "M_BlackLine":
        idx_black = i
assert idx_black is not None, "M_BlackLine ausente"
n = 0
bpy.context.view_layer.update()
for p in me.polygons:
    c = placa.matrix_world @ p.center
    nw = (placa.matrix_world.to_3x3() @ p.normal).normalized()
    if (-0.170 <= c.x <= -0.140 and 1.052 <= c.z <= 1.075
            and abs(c.y) > 0.05 and abs(nw.y) > 0.30):
        p.material_index = idx_black; n += 1
print("###V176### faces pretas na faixa:", n)
me.update()

bpy.ops.wm.save_as_mainfile(filepath=OUT)
print("###V176### salvo", OUT)
