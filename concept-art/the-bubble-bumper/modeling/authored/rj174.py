import bpy, math, json, os, hashlib
from mathutils import Vector
MD = "/mnt/storage2TB/Coding-Projects/super-kart-3djs/concept-art/the-bubble-bumper/modeling/"
ALVO = MD + "authored/conjunto-v174.blend"
assert os.path.exists(ALVO)
H_ALVO = hashlib.md5(open(ALVO, "rb").read()).hexdigest()[:10]
bpy.ops.wm.open_mainfile(filepath=ALVO)
n_obj = len([o for o in bpy.context.scene.objects if o.type == "MESH"])
print("###R42### abri %s (md5=%s) | objetos=%d" % (os.path.basename(ALVO), H_ALVO, n_obj))
sc = bpy.context.scene
sc.render.engine = "BLENDER_EEVEE"
sc.render.resolution_x = 620; sc.render.resolution_y = 620
sc.view_settings.view_transform = "Standard"
sc.world = bpy.data.worlds.new("W"); sc.world.use_nodes = True
sc.world.node_tree.nodes["Background"].inputs[0].default_value = (0.075, 0.078, 0.085, 1)
sc.world.node_tree.nodes["Background"].inputs[1].default_value = 1.0
for i, (loc, en, ang) in enumerate((((2.5, -2.0, 4.0), 3.2, 12), ((-3.0, 1.5, 2.5), 1.1, 30), ((0.5, 3.2, 1.8), 0.5, 45))):
    lt = bpy.data.lights.new("S%d" % i, "SUN"); lt.energy = en; lt.angle = math.radians(ang)
    o = bpy.data.objects.new("S%d" % i, lt); sc.collection.objects.link(o); o.location = loc
    o.rotation_euler = (Vector((0, 0, 0.55)) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
bpy.context.view_layer.update()
mins = [1e9] * 3; maxs = [-1e9] * 3
for ob in sc.objects:
    if ob.type != "MESH": continue
    for c in ob.bound_box:
        w = ob.matrix_world @ Vector(c)
        for i in range(3):
            mins[i] = min(mins[i], w[i]); maxs[i] = max(maxs[i], w[i])
cx, cy, cz = [(mins[i] + maxs[i]) / 2 for i in range(3)]
ext = max(maxs[0] - mins[0], maxs[1] - mins[1], maxs[2] - mins[2])
cam = bpy.data.cameras.new("C"); cam.type = "ORTHO"; cam.ortho_scale = ext * 1.30
co = bpy.data.objects.new("Cam", cam); sc.collection.objects.link(co); sc.camera = co
VIEWS = (("FRONT", (cx + ext * 2, cy, cz), (math.radians(90), 0, math.radians(90)), 0),
         ("SIDE", (cx, cy + ext * 2, cz), (math.radians(90), 0, math.radians(180)), 1),
         ("REAR", (cx - ext * 2, cy, cz), (math.radians(90), 0, math.radians(-90)), 0),
         ("TOP", (cx, cy, cz + ext * 2), (0, 0, math.radians(180)), 0))
for tag, loc, rot, sinal in VIEWS:
    for o in bpy.data.objects:
        o.hide_render = False
    if sinal:
        for o in bpy.data.objects:
            if o.type != "MESH": continue
            bb = [o.matrix_world @ Vector(c) for c in o.bound_box]
            ymed = (max(v.y for v in bb) + min(v.y for v in bb)) / 2
            if (o.name.endswith("_L") or o.name.endswith("_1")) and ymed > 0.30:
                o.hide_render = True
    co.location = loc; co.rotation_euler = rot
    sc.render.filepath = "/tmp/R174_%s.png" % tag
    bpy.ops.render.render(write_still=True)
    print("###R42### render", tag)
for o in bpy.data.objects:
    o.hide_render = False
json.dump({"cx": cx, "cz": cz, "OS": ext * 1.30, "RES": 620, "md5": H_ALVO}, open("/tmp/r174_map.json", "w"))
print("###R42### BBOX L=%.3f W=%.3f H=%.3f" % (maxs[0] - mins[0], maxs[1] - mins[1], maxs[2] - mins[2]))
