import bpy
import numpy as np

MD = "/mnt/storage2TB/Coding-Projects/super-kart-3djs/concept-art/the-bubble-bumper/modeling/"
bpy.ops.wm.open_mainfile(filepath=MD + "authored/conjunto-v175.blend")
print("###COR### cores base dos materiais envolvidos:")
for nome in ("M_BlackLine", "M_Slit", "Visor_Light", "M_VILL", "Helmet_Blue", "Accent_Yellow"):
    m = bpy.data.materials.get(nome)
    if m is None:
        print("###COR###   %-14s AUSENTE" % nome)
        continue
    bsdf = None
    if m.use_nodes:
        for n in m.node_tree.nodes:
            if n.type == 'BSDF_PRINCIPLED':
                bsdf = n
                break
    if bsdf is None:
        print("###COR###   %-14s sem Principled (diffuse=%.3f)" % (nome, m.diffuse_color[0]))
        continue
    c = bsdf.inputs["Base Color"].default_value
    r = bsdf.inputs["Roughness"].default_value if "Roughness" in bsdf.inputs else -1
    print("###COR###   %-14s base=(%.3f, %.3f, %.3f) roughness=%.2f" % (nome, c[0], c[1], c[2], r))
