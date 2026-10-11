import bpy
from mathutils import Vector

MD = "/mnt/storage2TB/Coding-Projects/super-kart-3djs/concept-art/the-bubble-bumper/modeling/"
bpy.ops.wm.open_mainfile(filepath=MD + "authored/conjunto-v138.blend")

helmet = [o for o in bpy.data.objects if o.name.startswith('P_Helmet')]
plate = bpy.data.objects.get('P_FacePlate')
print('###HELM### objetos P_Helmet: %s' % [o.name for o in helmet])
if plate:
    bb = [plate.matrix_world @ Vector(c) for c in plate.bound_box]
    xs = [p.x for p in bb]; ys = [p.y for p in bb]; zs = [p.z for p in bb]
    print('###HELM### P_FacePlate mundo: x %.3f..%.3f | |y|max %.3f | z %.3f..%.3f' % (
        min(xs), max(xs), max(abs(min(ys)), abs(max(ys))), min(zs), max(zs)))

# meia-largura (|y|max) do casco por faixa de x, na altura do painel
binw = 0.02
print('###HELM### P_Helmet: meia-largura por x  (|y|max considerando verts com z em 0.95..1.12)')
for o in helmet:
    mw = o.matrix_world
    pts = [mw @ v.co for v in o.data.vertices]
    pts = [p for p in pts if 0.95 <= p.z <= 1.12]
    if not pts:
        print('   %s: sem verts na faixa de z' % o.name)
        continue
    xs = [p.x for p in pts]
    print('   %s: %d verts na faixa, x %.3f..%.3f' % (o.name, len(pts), min(xs), max(xs)))
    x0 = min(xs)
    for i in range(9):
        a = x0 + i * 0.02
        b = a + 0.02
        sel = [p for p in pts if a <= p.x < b]
        if sel:
            my = max(abs(p.y) for p in sel)
            print('      x %+.3f..%+.3f : |y|max = %.3f  (n=%d)' % (a, b, my, len(sel)))
