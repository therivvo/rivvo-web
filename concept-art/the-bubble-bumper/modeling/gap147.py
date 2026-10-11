import bpy
from mathutils import Vector

MD = "/mnt/storage2TB/Coding-Projects/super-kart-3djs/concept-art/the-bubble-bumper/modeling/"
bpy.ops.wm.open_mainfile(filepath=MD + "authored/conjunto-v147.blend")

dg = bpy.context.evaluated_depsgraph_get()
sc = bpy.context.scene
DIR = Vector((0, -1, 0))
Y0 = 2.0

xs = [-0.30, -0.26, -0.22, -0.18, -0.14]
z0, z1, dz = 0.90, 1.16, 0.01

def amostra(x, z):
    ok, loc, nor, idx, obj, mw = sc.ray_cast(dg, Vector((x, Y0, z)), DIR)
    if not ok:
        return None, None
    mat = '-'
    try:
        pol = obj.data.polygons
        if idx is not None and 0 <= idx < len(pol):
            mi = pol[idx].material_index
            if 0 <= mi < len(obj.material_slots) and obj.material_slots[mi].material:
                mat = obj.material_slots[mi].material.name
    except Exception as e:
        mat = 'ERR'
    return obj.name, mat

print("###GAP### perfil de superficie SIDE (raio de +y): OBJETO[MATERIAL] por z")
print("###GAP### VAZIO = nenhuma geometria naquele pixel da silhueta")

# mapa de vazios por coluna
vazios = {}
for x in xs:
    z = z0
    segs = []
    atual = None
    ini = None
    while z <= z1 + 1e-9:
        o, m = amostra(x, round(z, 3))
        key = 'VAZIO' if o is None else (m or o)
        if key != atual:
            if atual is not None:
                segs.append((atual, ini, round(z - dz, 2)))
            atual = key
            ini = round(z, 2)
        z = round(z + dz, 4)
    segs.append((atual, ini, round(z1, 2)))
    vazios[x] = [s for s in segs if s[0] == 'VAZIO']
    print("x=%+.2f: " % x + " | ".join("%s %.2f-%.2f" % s for s in segs))

print()
print("###GAP### INTERVALOS VAZIOS (a causa raiz do defeito em z=1.00):")
algum = False
for x in xs:
    if vazios[x]:
        algum = True
        for _, a, b in vazios[x]:
            print("   x=%+.2f -> VAZIO de z=%.2f a z=%.2f  (altura %.2f m)" % (x, a, b, b - a))
if not algum:
    print("   nenhum vazio: o defeito em z=1.00 NAO e geometria ausente -> investigar material/sombra")

print()
print("###GAP### transicao azul->claro em cada coluna (concept tem claro em z 0.96..1.10):")
for x in xs:
    z = z0
    while z <= z1 + 1e-9:
        o, m = amostra(x, round(z, 3))
        if m and 'Light' in m:
            print("   x=%+.2f primeiro CLARO em z=%.2f" % (x, z))
            break
        z = round(z + dz, 4)
    else:
        print("   x=%+.2f NENHUM claro ate z=%.2f" % (x, z1))
