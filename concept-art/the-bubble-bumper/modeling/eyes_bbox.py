import bpy
from mathutils import Vector

MD = "/mnt/storage2TB/Coding-Projects/super-kart-3djs/concept-art/the-bubble-bumper/modeling/"
bpy.ops.wm.open_mainfile(filepath=MD + "authored/conjunto-v149.blend")
bpy.context.view_layer.update()

NOMES = ['P_Helmet', 'P_FacePlate', 'P_Visor', 'P_Eye_1', 'P_Eye_-1', 'P_Pup_1', 'P_Pup_-1', 'P_Neck', 'P_Shoulder']

print("###EYE### bbox em MUNDO (frente do modelo = x MINIMO, nariz em x=-1.178)")
print("###EYE### nome            x_min    x_max    y_min    y_max    z_min    z_max")
res = {}
for nm in NOMES:
    ob = bpy.data.objects.get(nm)
    if ob is None:
        print("###EYE### %-14s NAO EXISTE" % nm)
        continue
    mw = ob.matrix_world
    pts = [mw @ Vector(c) for c in ob.bound_box]
    xs = [p.x for p in pts]; ys = [p.y for p in pts]; zs = [p.z for p in pts]
    res[nm] = (min(xs), max(xs), min(ys), max(ys), min(zs), max(zs))
    print("###EYE### %-14s %+.3f  %+.3f  %+.3f  %+.3f  %+.3f  %+.3f" % (
        nm, min(xs), max(xs), min(ys), max(ys), min(zs), max(zs)))

if 'P_Eye_1' in res and 'P_Helmet' in res:
    fr_e = min(res['P_Eye_1'][0], res['P_Eye_-1'][0])
    fr_h = res['P_Helmet'][0]
    fr_f = res['P_FacePlate'][0]
    print()
    print("###EYE### frente do OLHO  em x=%+.3f" % fr_e)
    print("###EYE### frente do CAPACETE em x=%+.3f" % fr_h)
    print("###EYE### frente do FACEPLATE em x=%+.3f" % fr_f)
    print("###EYE### olho esta %+.3f m a frente do capacete" % (fr_h - fr_e))
    print("###EYE### olho esta %+.3f m a frente do faceplate" % (fr_f - fr_e))
    print("###EYE### RECUO NECESSARIO para o olho nao passar do capacete: %.3f m (x += %+.3f)" % (fr_h - fr_e, fr_h - fr_e))
    # faixa de z do olho x faixa do faceplate
    print("###EYE### z do olho: %.3f..%.3f | z do faceplate: %.3f..%.3f" % (
        res['P_Eye_1'][4], res['P_Eye_1'][5], res['P_FacePlate'][4], res['P_FacePlate'][5]))

# raio: em que x a superficie frontal do capacete esta por faixa de z
dg = bpy.context.evaluated_depsgraph_get()
sc = bpy.context.scene
DIR = Vector((0, -1, 0))
print()
print("###EYE### frente da silhueta (raio de +y) por z, de x=-0.45 a x=-0.02:")
for z in [0.98, 1.00, 1.02, 1.04, 1.06, 1.08, 1.10]:
    frente = None; quem = None
    x = -0.45
    while x <= -0.02 + 1e-9:
        ok, loc, nor, idx, obj, mw = sc.ray_cast(dg, Vector((x, 2.0, z)), DIR)
        if ok:
            frente = x; quem = obj.name
        x = round(x + 0.005, 4)
    print("###EYE###   z=%.2f -> frente em x=%+.3f (%s)" % (z, frente if frente else 0, quem or 'VAZIO'))
