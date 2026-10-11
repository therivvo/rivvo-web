import bpy
from mathutils import Vector

MD = "/mnt/storage2TB/Coding-Projects/super-kart-3djs/concept-art/the-bubble-bumper/modeling/"
SRC = MD + "authored/conjunto-v168.blend"   # CANDIDATO VALIDO
DST = MD + "authored/conjunto-v172.blend"
assert SRC != DST

# CAUSA MEDIDA (grade g169, com nome de objeto): em z 1.10..1.14 o topo-traseiro do P_Helmet AFINA
# para uma aresta — y cai de 0.086 (x=-0.17) para 0.020 (x=-0.15) e ny cai de 0.49 para 0.13. Uma
# superficie que afina vira rampa rasante -> renderiza escura -> o classificador le '.' onde o concept
# tem 'B'. CORRECAO (mesma classe que funcionou no v168): impor PISO DE LARGURA — a rampa vira PAREDE
# (y constante => normal aponta para a camera, ny ~ 1).
X0, X1 = -0.190, -0.130
Z0, Z1 = 1.080, 1.170
YFLOOR = 0.060
ALVOS = ["P_Helmet", "P_StripeF", "P_HVent"]


def w01(v, a, b):
    return 0.0 if b == a else min(1.0, max(0.0, (v - a) / (b - a)))


bpy.ops.wm.open_mainfile(filepath=SRC)
bpy.context.view_layer.update()

for nome in ALVOS:
    ob = bpy.data.objects.get(nome)
    if ob is None:
        continue
    mw = ob.matrix_world
    inv = mw.inverted()          # REGRA v171: transladar/mover SEMPRE via espaco local correto
    n = 0
    ymin = 9.9
    for v in ob.data.vertices:
        w = mw @ v.co
        if not (X0 <= w.x <= X1 and Z0 <= w.z <= Z1):
            continue
        if abs(w.y) >= YFLOOR or abs(w.y) < 0.004:
            continue
        ymin = min(ymin, abs(w.y))
        s = 1.0 if w.y >= 0 else -1.0
        w.y = s * YFLOOR
        v.co = inv @ w
        n += 1
    print("###V172### %-10s verts=%3d | |y| min antes=%.4f -> piso %.3f" % (nome, n, ymin if n else -1, YFLOOR))
    ob.data.update()
bpy.context.view_layer.update()

dg = bpy.context.evaluated_depsgraph_get()
sc = bpy.context.scene
print("###V172### grade DEPOIS (antes: z=1.12 ny 0.49/0.34/0.13 em x -0.17/-0.16/-0.15):")
for z in (1.10, 1.12, 1.14):
    cel = []
    for x in (-0.17, -0.16, -0.15):
        ok, loc, nor, idx, ob, mwd = sc.ray_cast(dg, Vector((x, 5.0, z)), Vector((0, -1, 0)))
        cel.append("%+.2f %s y%+.3f ny%+.2f" % (x, ob.name if ok else "VAZIO", loc.y, nor.y) if ok else "%+.2f VAZIO" % x)
    print("###V172### z=%.2f | %s" % (z, " | ".join(cel)))
bpy.ops.wm.save_as_mainfile(filepath=DST)
print("###V172### salvo:", DST)
