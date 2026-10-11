import bpy
from mathutils import Vector

MD = "/mnt/storage2TB/Coding-Projects/super-kart-3djs/concept-art/the-bubble-bumper/modeling/"
bpy.ops.wm.open_mainfile(filepath=MD + "authored/conjunto-v167.blend")
bpy.context.view_layer.update()
dg = bpy.context.evaluated_depsgraph_get()
sc = bpy.context.scene

# faixa rasante medida: x -0.22..-0.20, z 0.99..1.04, ny 0.25..0.34
print("###G168### grade COM NOME DO OBJETO (camera -y, origem y=+5)")
print("###G168### colunas x=-0.25..-0.19 (passo 0.01) | linhas z=0.96..1.04 (passo 0.01)")
for zi in range(9):
    z = 0.96 + zi * 0.01
    cel = []
    for xi in range(7):
        x = -0.25 + xi * 0.01
        ok, loc, nor, idx, ob, mw = sc.ray_cast(dg, Vector((x, 5.0, z)), Vector((0, -1, 0)))
        if not ok:
            cel.append("%s:VAZIO" % ("%+.2f" % x))
            continue
        mat = "-"
        if idx >= 0:
            ev = ob.evaluated_get(dg)
            if idx < len(ev.data.polygons):
                mi = ev.data.polygons[idx].material_index
                if mi < len(ob.material_slots) and ob.material_slots[mi].material:
                    mat = ob.material_slots[mi].material.name
        cel.append("%+.2f %s[%s] y%+.3f ny%+.2f" % (x, ob.name, mat, loc.y, nor.y))
    print("###G168### z=%.2f | %s" % (z, " | ".join(cel)))

# quais objetos possuem geometria na janela rasante (candidatos a correcao)
print("###G168### objetos com verts na janela x -0.23..-0.19, z 0.985..1.045:")
for o in sc.objects:
    if o.type != 'MESH' or not o.visible_get():
        continue
    mw = o.matrix_world
    n = 0
    ymax = 0.0
    for v in o.data.vertices:
        w = mw @ v.co
        if -0.23 <= w.x <= -0.19 and 0.985 <= w.z <= 1.045:
            n += 1
            ymax = max(ymax, abs(w.y))
    if n:
        mods = ",".join(m.type for m in o.modifiers) or "sem-mod"
        print("###G168###   %-16s verts=%3d |y|max=%.4f mods=%s" % (o.name, n, ymax, mods))
