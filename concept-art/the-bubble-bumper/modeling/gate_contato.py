"""Gate v2 (pos-auditoria): ILHAS (conectividade), MANIFOLD e CONTATO incluindo RODAS.
Substitui o gate_contato.py legado (nomes antigos -> falso-PASS)."""
import bpy, sys, json
from mathutils.bvhtree import BVHTree

BASE = sys.argv[-1] if sys.argv[-1].endswith('.blend') else '/mnt/storage2TB/Coding-Projects/super-kart-3djs/concept-art/the-bubble-bumper/modeling/authored/conjunto-v078.blend'
bpy.ops.wm.open_mainfile(filepath=BASE)
bpy.context.view_layer.update()
dg = bpy.context.evaluated_depsgraph_get()

def tv(o):
    oe = o.evaluated_get(dg)
    me = oe.to_mesh()
    verts = [o.matrix_world @ v.co for v in me.vertices]
    faces = [list(p.vertices) for p in me.polygons]
    t = BVHTree.FromPolygons(verts, faces) if faces else None
    oe.to_mesh_clear()
    return t

objs = [o for o in bpy.data.objects if o.type == 'MESH']
trees = {}
for o in objs:
    t = tv(o)
    if t:
        trees[o.name] = t
names = sorted(trees)
print("###CT### base:", BASE.split('/')[-1], "| meshes:", len(names))

# ---- conectividade (union-find por overlap BVH) ----
pai = {n: n for n in names}
def find(a):
    while pai[a] != a:
        pai[a] = pai[pai[a]]; a = pai[a]
    return a
def uni(a, b):
    ra, rb = find(a), find(b)
    if ra != rb:
        pai[rb] = ra

pares_ok = []
for i in range(len(names)):
    for j in range(i + 1, len(names)):
        a, b = names[i], names[j]
        if trees[a].overlap(trees[b]):
            uni(a, b)
            pares_ok.append((a, b))
from collections import defaultdict
comp = defaultdict(list)
for n in names:
    comp[find(n)].append(n)
comps = sorted(comp.values(), key=len, reverse=True)
print("###CT### COMPONENTES:", len(comps), "| tamanhos:", [len(c) for c in comps][:14])
main = set(comps[0])
for c in comps[1:]:
    print("###CT### ILHA (%d): %s" % (len(c), ', '.join(sorted(c)[:14])))
print("###CT### pares com contato real:", len(pares_ok))

# ---- manifold / loose ----
import bmesh
piores = []
for o in objs:
    bm = bmesh.new(); bm.from_mesh(o.data)
    nm = sum(1 for e in bm.edges if not e.is_manifold)
    lv = sum(1 for v in bm.verts if not v.link_edges)
    op = sum(1 for e in bm.edges if len(e.link_faces) == 1)
    if nm or lv or op:
        piores.append((nm, o.name, lv, op))
    bm.free()
piores.sort(reverse=True)
print("###CT### NON-MANIFOLD: total %d arestas em %d objetos" % (sum(p[0] for p in piores), len(piores)))
for nm, n, lv, op in piores[:6]:
    print("###CT###   %-16s nm=%d loose=%d boundary=%d" % (n, nm, lv, op))

# ---- contato nomeado (inclui RODAS) ----
PARES = [("P_Torso", "P_Shoulder"), ("P_Shoulder", "P_Neck"), ("P_Neck", "P_Helmet"),
         ("P_Torso", "Seat_Base"), ("Seat_Base", "Floor"), ("P_Helmet", "P_Visor"),
         ("Sidepod_L", "PodSup_1"), ("PodSup_1", "Floor"),
         ("R_Motor", "R_BumpSup_L"), ("R_BumpSup_L", "R_BumperBar"),
         ("R_Wing", "R_Pylon_1"), ("CowlWall", "Floor"), ("F_ArmU_1", "N_Ramp"), ("F_ArmU_1", "N_Nose"),
         ("AXL_F_1", "STRUT_F_1"), ("AXL_F_-1", "STRUT_F_-1"), ("AXL_F_1", "RIM_FL"), ("AXL_F_-1", "RIM_FR"), ("STRUT_F_1", "Chassis_1"),
         ("AXL_R_1", "Rail_R_1"), ("AXL_R_-1", "Rail_R_-1"), ("AXL_R_1", "RIM_RL"), ("AXL_R_-1", "RIM_RR"),
         ("R_Spring_1", "AXL_R_1"), ("R_Spring_-1", "AXL_R_-1"), ("R_Spring_1", "TIRE_RL"),
         ("R_Pylon_1", "Rail_R_1"), ("Rail_R_1", "Chassis_1"), ("Rail_R_1", "R_Motor"),
         ("Rail_R_1", "R_BumpSup_L"), ("P_Eye_1", "P_FacePlate"), ("P_Mouth_M", "P_FacePlate"),
         ("P_FacePlate", "P_Helmet"), ("P_FacePlate", "P_Visor")]
ok = aus = flut = 0
falhas = []
for a, b in PARES:
    ta, tb = trees.get(a), trees.get(b)
    if ta is None or tb is None:
        print("###CT### %-34s AUSENTE" % ("%s <-> %s" % (a, b))); aus += 1; continue
    h = ta.overlap(tb)
    if h:
        ok += 1
    else:
        flut += 1; falhas.append("%s<->%s" % (a, b))
        print("###CT### %-34s FLUTUANDO" % ("%s <-> %s" % (a, b)))
print("###CT### CONTATO: %d/%d em contato | ausentes=%d | falhas=%s" % (ok, len(PARES), aus, falhas if falhas else 'nenhuma'))
json.dump({"base": BASE.split('/')[-1], "componentes": len(comps), "tamanhos": [len(c) for c in comps],
           "pares_contato": len(pares_ok), "par_nomeado_ok": ok, "falhas": falhas, "ausentes": aus},
          open('/tmp/gate2_%s.json' % BASE.split('/')[-1].replace('.blend', ''), 'w'), indent=1)
