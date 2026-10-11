import bpy

MD = "/mnt/storage2TB/Coding-Projects/super-kart-3djs/concept-art/the-bubble-bumper/modeling/"
SRC = MD + "authored/conjunto-v158.blend"
DST = MD + "authored/conjunto-v159.blend"
assert SRC != DST, "nao sobrescrever"

NOVO_SLIT = 0.17   # 0.10 rendeu 'D' (soma<200); o concept classifica a fenda como 'o' (200..300)

bpy.ops.wm.open_mainfile(filepath=SRC)
bpy.context.view_layer.update()

# (a) clarear a fenda
mat = bpy.data.materials.get("M_Slit")
assert mat is not None, "M_Slit ausente"
bsdf = mat.node_tree.nodes.get("Principled BSDF")
antes = tuple(round(v, 3) for v in bsdf.inputs["Base Color"].default_value)
bsdf.inputs["Base Color"].default_value = (NOVO_SLIT, NOVO_SLIT, NOVO_SLIT + 0.02, 1.0)
print("###V159### M_Slit base: %s -> %s" % (antes, tuple(round(v, 3) for v in bsdf.inputs["Base Color"].default_value)))

# (b) P_Visor deixa de pintar escuro: a fenda agora vem do casco (v158). Stray 'o' em x=-0.22 era ele.
luz = bpy.data.materials.get("Visor_Light")
assert luz is not None, "Visor_Light ausente"
vis = bpy.data.objects.get("P_Visor")
assert vis is not None, "P_Visor ausente"
n = 0
for i, s in enumerate(vis.material_slots):
    ant = s.material.name if s.material else "-"
    if s.link == 'DATA':
        vis.data.materials[i] = luz
    else:
        s.material = luz
    n += 1
    print("###V159### P_Visor slot %d: %s -> Visor_Light" % (i, ant))
print("###V159### slots do visor reatribuidos: %d" % n)
assert n >= 1, "visor sem slots"

bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=DST)
print("###V159### salvo:", DST)
