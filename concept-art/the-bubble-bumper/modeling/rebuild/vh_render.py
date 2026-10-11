#!/usr/bin/env python3
"""Renderiza o visual hull (/tmp/vh.obj) nos 4 ortograficos + passe de mascara.
Mesmo enquadramento do builder para o auditor comparar direto.
Uso: blender -b -P vh_render.py -- <VER>
"""
import bpy, sys, os, math

argv = sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else []
VER = argv[0] if argv else "VH1"
OUT = "/opt/blender-runner/outputs"
OBJ = argv[1] if len(argv) > 1 else "/tmp/vh.obj"

def V3(t): return bpy.mathutils.Vector(t) if hasattr(bpy, "mathutils") else __import__("mathutils").Vector(t)

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine = "BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items] else "BLENDER_EEVEE"
sc.render.resolution_percentage = 100
sc.render.image_settings.file_format = "PNG"
try:
    ee = sc.eevee
    for a, v in (("use_raytracing", True), ("use_gtao", True), ("use_shadows", True), ("taa_render_samples", 96)):
        if hasattr(ee, a): setattr(ee, a, v)
except Exception as e:
    print("eevee cfg:", e)

# --- malha ---
bpy.ops.wm.obj_import(filepath=OBJ, forward_axis="Y", up_axis="Z")  # SEM conversao de eixo: o hull ja esta em x=comprimento, y=lateral, z=altura
objs = [o for o in bpy.context.selected_objects if o.type == "MESH"]
if not objs:
    raise SystemExit("OBJ sem mesh")
for o in list(bpy.data.objects):
    if o.type == "MESH" and o not in objs: bpy.data.objects.remove(o, do_unlink=True)
o = objs[0]; o.name = VER + "_hull"
bpy.context.view_layer.objects.active = o
bpy.ops.object.mode_set(mode="OBJECT")
print("hull verts=%d faces=%d" % (len(o.data.vertices), len(o.data.polygons)))

# normais consistentes (surface nets pode ter winding irregular)
bpy.ops.object.mode_set(mode="EDIT")
bpy.ops.mesh.select_all(action="SELECT")
bpy.ops.mesh.normals_make_consistent(inside=False)
# remove_doubles REMOVIDO: reordena/merge faces e desalinha o material por face.
bpy.ops.object.mode_set(mode="OBJECT")
print("after cleanup verts=%d faces=%d" % (len(o.data.vertices), len(o.data.polygons)))

# --- PALETA (indice = ordem usada por vh_color.py) ---
PAL = [("M_Dark",(0.024,0.024,0.030),0.38,0.0),      # sRGB ~45,45,50  -> escuro
       ("M_Plate",(0.140,0.150,0.170),0.45,0.2),     # sRGB ~105,108,114 -> cinza
       ("M_Silver",(0.400,0.410,0.440),0.30,0.85),   # sRGB ~170,172,178 -> claro
       ("M_White",(0.660,0.670,0.690),0.45,0.0),     # sRGB ~215,216,218 -> claro
       ("M_Blue",(0.028,0.108,0.340),0.34,0.0),      # sRGB ~48,92,158   -> azul_med
       ("M_BlueDk",(0.016,0.042,0.108),0.36,0.0),    # sRGB ~35,58,92    -> azul_esq
       ("M_Yellow",(0.900,0.560,0.022),0.32,0.0),    # sRGB ~245,198,42  -> amarelo
       ("M_Gold",(0.470,0.300,0.060),0.30,0.75),     # sRGB ~185,150,70  -> amarelo
       ("M_BlueLt",(0.190,0.300,0.570),0.32,0.0),    # sRGB ~120,150,200 -> azul_clr
       ("M_Visor",(0.260,0.280,0.300),0.18,0.55),    # sRGB ~140,145,150 -> claro
       ("M_Face",(0.780,0.520,0.350),0.55,0.0),      # sRGB ~232,196,166 -> claro
       ("M_Pilot",(0.028,0.108,0.340),0.45,0.0)]
o.data.materials.clear()
for nm, col, rough, metal in PAL:
    mm = bpy.data.materials.get(nm) or bpy.data.materials.new(nm)
    mm.use_nodes = True
    bb = mm.node_tree.nodes.get("Principled BSDF")
    if bb:
        bb.inputs["Base Color"].default_value = (col[0], col[1], col[2], 1.0)
        if "Roughness" in bb.inputs: bb.inputs["Roughness"].default_value = rough
        if "Metallic" in bb.inputs: bb.inputs["Metallic"].default_value = metal
    o.data.materials.append(mm)
import numpy as _np
FM = "/tmp/vh_fmat.npy"
if os.path.exists(FM):
    _m = _np.load(FM)
    if len(_m) == len(o.data.polygons):
        o.data.polygons.foreach_set("material_index", _m.astype(int).tolist())
        o.data.update()
        print("materiais por face aplicados: %d" % len(_m))
    else:
        print("AVISO: %d faces de material vs %d polygons" % (len(_m), len(o.data.polygons)))

# --- chao ---
bpy.ops.mesh.primitive_plane_add(size=14, location=(0, 0, -0.001))
gnd = bpy.context.active_object; gnd.name = "Ground"
gm = bpy.data.materials.new("M_Ground"); gm.use_nodes = True
gb = gm.node_tree.nodes.get("Principled BSDF")
if gb: gb.inputs["Base Color"].default_value = (0.30, 0.31, 0.34, 1)
gnd.data.materials.append(gm)

# --- luzes / mundo ---
w = sc.world or bpy.data.worlds.new("W"); sc.world = w
w.use_nodes = True
bg = w.node_tree.nodes.get("Background")
if bg:
    bg.inputs[0].default_value = (0.045, 0.048, 0.055, 1.0); bg.inputs[1].default_value = 1.0

def plus_light(nm, loc, size, energy, col):
    ld = bpy.data.lights.new(nm, "AREA"); ld.size = size; ld.energy = energy; ld.color = col
    lo = bpy.data.objects.new(nm, ld); sc.collection.objects.link(lo); lo.location = loc
    lo.rotation_euler = (V3((0, 0, 0.45)) - V3(loc)).to_track_quat("-Z", "Y").to_euler()
plus_light("L_key", (3.4, -2.8, 4.0), 4.4, 900, (1.0, 0.97, 0.93))
plus_light("L_fill", (-3.0, -3.2, 1.8), 6.0, 500, (0.86, 0.91, 1.0))
plus_light("L_rim", (-2.0, 3.8, 2.6), 3.0, 600, (0.95, 0.97, 1.0))
sc.view_settings.view_transform = "Standard"

def render(path, w_=860, h_=860):
    sc.render.resolution_x = w_; sc.render.resolution_y = h_
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)

def cam(name, loc, rot, ortho):
    cd = bpy.data.cameras.new(name); co = bpy.data.objects.new(name, cd)
    sc.collection.objects.link(co); co.location = loc; co.rotation_euler = rot
    cd.type = "ORTHO"; cd.ortho_scale = ortho
    return co

zc = 0.62; OSC = 2.42
VIEWS = [("front", (5.0, 0, zc), (math.radians(90), 0, math.radians(90))),
         ("rear",  (-5.0, 0, zc), (math.radians(90), 0, math.radians(-90))),
         ("side",  (0.0, 5.0, zc), (math.radians(90), 0, math.radians(180))),
         ("top",   (0, 0, 5.0), (0, 0, math.radians(180)))]
for nm, loc, rot in VIEWS:
    sc.camera = cam("CAM_" + nm, loc, rot, OSC)
    render(os.path.join(OUT, "%s-%s.png" % (VER.lower(), nm)))

# iso
for nm, loc, dst, lk in [("isoF", (2.30, -2.30, 1.75), 3.6, 0.42), ("isoR", (-2.35, 2.35, 1.70), 3.6, 0.42)]:
    look = V3((0, 0, lk)); v = V3(loc).normalized() * dst
    cd = bpy.data.cameras.new("C_" + nm); cd.lens = 60
    co = bpy.data.objects.new("C_" + nm, cd); sc.collection.objects.link(co)
    co.location = v; co.rotation_euler = (look - v).to_track_quat("-Z", "Y").to_euler()
    sc.camera = co
    render(os.path.join(OUT, "%s-%s.png" % (VER.lower(), nm)), 880, 660)

# --- mascara ---
gnd.hide_render = True
for ob in list(bpy.data.objects):
    if ob.type == "LIGHT": ob.hide_render = True
if bg: bg.inputs[1].default_value = 0.0
sc.render.film_transparent = True
sc.render.image_settings.color_mode = "RGBA"
for nm, loc, rot in VIEWS:
    sc.camera = cam("CAMM_" + nm, loc, rot, OSC)
    render(os.path.join(OUT, "%sm-%s.png" % (VER.lower(), nm)))
# --- passe FLAT (emissao pura) para o auditor medir COR ---
if bg: bg.inputs[1].default_value = 0.0
sc.render.film_transparent = False
sc.render.image_settings.color_mode = "RGB"
for ob in list(bpy.data.objects):
    if ob.type == "MESH" and ob.name != "Ground":
        for mat in ob.data.materials:
            if mat and mat.use_nodes:
                nt = mat.node_tree
                for n in list(nt.nodes):
                    if n.type == "BSDF_PRINCIPLED":
                        em = nt.nodes.new("ShaderNodeEmission")
                        bc = n.inputs["Base Color"].default_value[:]
                        em.inputs[0].default_value = bc; em.inputs[1].default_value = 1.0
                        out = [x for x in nt.nodes if x.type == "OUTPUT_MATERIAL"]
                        if out:
                            nt.links.new(em.outputs[0], out[0].inputs[0])
                        break
gnd.hide_render = True
for nm, loc, rot in VIEWS:
    sc.camera = cam("CAMF_" + nm, loc, rot, OSC)
    render(os.path.join(OUT, "%sf-%s.png" % (VER.lower(), nm)))
print("DONE", VER)
