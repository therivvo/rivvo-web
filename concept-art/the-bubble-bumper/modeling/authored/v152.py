import bpy
from mathutils import Vector

MD = "/mnt/storage2TB/Coding-Projects/super-kart-3djs/concept-art/the-bubble-bumper/modeling/"
bpy.ops.wm.open_mainfile(filepath=MD + "authored/conjunto-v151.blend")
bpy.context.view_layer.update()

ob = bpy.data.objects.get('P_Shoulder')
assert ob is not None and ob.type == 'MESH', 'P_Shoulder ausente'
ob.data = ob.data.copy()  # nao compartilhar mesh
me = ob.data
mw = ob.matrix_world.copy()
inv = mw.inverted()

pts = [mw @ Vector(c) for c in ob.bound_box]
x0 = min(p.x for p in pts); x1 = max(p.x for p in pts)
z0 = min(p.z for p in pts); z1 = max(p.z for p in pts)
print("###V152### P_Shoulder antes: x %.3f..%.3f | z %.3f..%.3f" % (x0, x1, z0, z1))

# perfis medidos: (t, queda) -> alvos do concept (descer 0.035 em x=-0.18, 0.017 em x=-0.16)
# t = (x - x0)/(x1 - x0)
def alvo_t(x):
    return (x - x0) / (x1 - x0)

t_ini, t_035, t_017, t_fim = 0.78, alvo_t(-0.18), alvo_t(-0.16), 0.99
print("###V152### t: inicio=%.3f | x=-0.18 -> %.3f | x=-0.16 -> %.3f | fim=%.3f" % (t_ini, t_035, t_017, t_fim))
assert t_ini < t_035 < t_017 < t_fim, 'ordem dos t invalida'

def queda(t):
    if t <= t_ini or t >= t_fim:
        return 0.0
    if t <= t_035:
        return 0.035 * (t - t_ini) / (t_035 - t_ini)
    if t <= t_017:
        return 0.035 + (0.017 - 0.035) * (t - t_035) / (t_017 - t_035)
    return 0.017 * (1.0 - (t - t_017) / (t_fim - t_017))

zspan = z1 - z0
afetados = 0
for v in me.vertices:
    w = mw @ v.co
    t = (w.x - x0) / (x1 - x0)
    d = queda(t)
    if d <= 0:
        continue
    h = (w.z - z0) / zspan if zspan > 0 else 1.0
    peso = max(0.0, min(1.0, (h - 0.5) * 2.0))  # so a metade de cima
    if peso <= 0:
        continue
    w.z -= d * peso
    v.co = inv @ w
    afetados += 1
me.update()
bpy.context.view_layer.update()
print("###V152### vertices deformados: %d de %d" % (afetados, len(me.vertices)))

pts2 = [ob.matrix_world @ Vector(c) for c in ob.bound_box]
print("###V152### P_Shoulder depois: x %.3f..%.3f | z %.3f..%.3f" % (
    min(p.x for p in pts2), max(p.x for p in pts2), min(p.z for p in pts2), max(p.z for p in pts2)))

# mede o TOPO por coluna no estado deformado
dg = bpy.context.evaluated_depsgraph_get(); sc = bpy.context.scene
DIR = Vector((0, -1, 0))
print("###V152### topo do ombro DEPOIS (alvo entre parenteses):")
for x, alvo in ((-0.22, 0.940), (-0.20, 0.930), (-0.18, 0.920), (-0.16, 0.918), (-0.15, 0.915)):
    topo = None
    z = 1.08
    while z >= 0.80:
        ok, loc, nor, idx, obj, m = sc.ray_cast(dg, Vector((x, 2.0, z)), DIR)
        if ok and obj.name == 'P_Shoulder':
            topo = z
            break
        z = round(z - 0.005, 4)
    print("###V152###   x=%+.2f -> topo=%s (alvo %.3f)" % (x, ('%.3f' % topo) if topo else 'ausente', alvo))

assert 'conjunto-v151.blend' not in str(ob), 'sanidade'
bpy.ops.wm.save_as_mainfile(filepath=MD + "authored/conjunto-v152.blend")
print("###V152### salvo conjunto-v152.blend")
