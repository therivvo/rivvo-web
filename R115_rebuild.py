import bpy, bmesh, os, math
from mathutils import Vector
job=os.path.dirname(os.path.abspath(__file__))
src=os.path.join(job,'assets/hero-kart-v2/R114/hero-kart-v2-R114.blend')
outdir=os.path.join(job,'assets/hero-kart-v2/R115')
os.makedirs(os.path.join(outdir,'renders'),exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=src)
# Keep R114 immutable in its own folder; new structural layer is clearly named and parented.
col=bpy.data.collections.get('LOD0')
# materials copied from the canonical palette

def mat(name, base, metallic=0.0, rough=.35):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.diffuse_color=(*base,1)
    m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value=(*base,1)
    bs.inputs['Metallic'].default_value=metallic
    bs.inputs['Roughness'].default_value=rough
    return m
paint=mat('paint_primary',(0.055,0.32,0.40),.15,.27)
dark=mat('cockpit_carbon',(0.018,0.035,0.045),.45,.24)
accent=mat('accent_emissive',(1.0,.16,.025),.1,.22)
rubber=mat('rubber_dark',(.018,.022,.028),.0,.5)

def finish(o,name,material,bev=.03):
    o.name='LOD0_R115_'+name
    o.data.materials.append(material)
    if col and o.name not in col.objects: col.objects.link(o)
    for c in list(o.users_collection):
        if c!=col: c.objects.unlink(o)
    if bev:
        mod=o.modifiers.new('R115_edge_softening','BEVEL'); mod.width=bev; mod.segments=3
    return o

def cube(name,loc,scale,material,bev=.03):
    bpy.ops.mesh.primitive_cube_add(location=loc); o=finish(bpy.context.object,name,material,bev); o.scale=scale; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); return o

def sphere(name,loc,scale,material):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=16, location=loc); o=finish(bpy.context.object,name,material,0); o.scale=scale; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); bpy.ops.object.shade_smooth(); return o

def beam(name,a,b,r,material):
    a,b=Vector(a),Vector(b); d=b-a
    bpy.ops.mesh.primitive_cylinder_add(vertices=20, radius=r, depth=d.length, location=(a+b)/2)
    o=finish(bpy.context.object,name,material,.015); o.rotation_euler=d.to_track_quat('Z','Y').to_euler(); return o

def torus(name,loc,major,minor,material,rot=(math.pi/2,0,0)):
    bpy.ops.mesh.primitive_torus_add(major_radius=major,minor_radius=minor,major_segments=32,minor_segments=10,location=loc,rotation=rot)
    o=finish(bpy.context.object,name,material,0); bpy.ops.object.shade_smooth(); return o
# Structural cockpit: side consoles rise from the existing rolled rim and terminate at the cowl.
cube('CockpitSideConsole_L',(-.39,-.18,.72),(.095,.43,.13),dark,.045)
cube('CockpitSideConsole_R',(.39,-.18,.72),(.095,.43,.13),dark,.045)
cube('CockpitNoseBridge',(0,-.72,.66),(.34,.10,.08),paint,.035)
# Four visible windshield mounts connect the lens to the nose bridge; no floating plate.
for side in (-1,1):
    x=.29*side
    beam('WindshieldMountFront_'+('L' if side<0 else 'R'),(x,-.73,.70),(x,-.69,1.03),.035,accent)
    beam('WindshieldMountRear_'+('L' if side<0 else 'R'),(x,-.18,.75),(x,-.36,1.02),.032,accent)
# A compact curved-looking lens made from a rounded solid shell, with a dark frame and clear boundaries.
lens=cube('WindshieldLensIntegrated',(0,-.53,1.02),(.29,.055,.28),dark,.075); lens.rotation_euler[0]=-.16
frame=torus('WindshieldFrame',(0,-.53,1.02),.285,.022,accent,(0,math.pi/2,0)); frame.scale=(1,.72,1); bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
# Vest/torso and shoulder harness give the driver a seated, armored relationship to the tub.
cube('DriverSeatBack',(0,.19,1.08),(.25,.075,.33),dark,.07)
cube('DriverChestArmor',(0,-.04,1.38),(.22,.12,.24),paint,.06)
for side in (-1,1):
    beam('HarnessShoulder_'+str(side),(side*.19,-.03,1.54),(side*.31,-.20,1.27),.025,accent)
# Replace bald reading with a layered helmet shell, brow and jaw guard around the existing head.
sphere('HelmetOuterShell',(0,.02,1.82),(.19,.16,.23),dark)
sphere('HelmetBrow',(0,-.145,1.86),(.16,.035,.07),accent)
cube('HelmetChinGuard',(0,-.12,1.68),(.13,.065,.055),dark,.03)
beam('HelmetNeckRing',(-.11,.02,1.62),(.11,.02,1.62),.028,accent)
# Steering now has a visibly connected column and two-handed grip relationship.
beam('SteeringColumn',(0,-.47,.72),(0,-.50,1.16),.035,dark)
beam('SteeringDashMount',(0,-.72,.70),(0,-.47,.72),.045,dark)
torus('SteeringGrip',(0,-.52,1.18),.18,.035,dark,(math.pi/2,0,0))
sphere('SteeringHubCap',(0,-.52,1.18),(.055,.04,.055),accent)
# Rear identity: integrated tail spine, diffuser strakes and exhaust surrounds, tied to the body.
cube('RearTailSpine',(0,.92,.73),(.30,.32,.12),paint,.08)
for side in (-1,1):
    cube('RearDiffuserStrake_'+str(side),(side*.22,1.04,.48),(.035,.23,.16),dark,.02)
    beam('RearExhaustSupport_'+str(side),(side*.18,.83,.78),(side*.24,1.03,.72),.025,accent)
# Add explicit review metadata and sockets.
sc=bpy.context.scene; sc['review_revision']='R115'; sc['revision_parent']='R114'; sc['revision_scope']='structural_cockpit_shell_driver_steering_rear_identity'; sc['windshield_mount_count']=4; sc['steering_column_connected']=True; sc['helmet_shell_layers']=4
for o in bpy.data.objects:
    if o.type=='MESH':
        bm=bmesh.new(); bm.from_mesh(o.data); bmesh.ops.recalc_face_normals(bm,faces=bm.faces); bm.to_mesh(o.data); bm.free(); o.data.update()
dst=os.path.join(outdir,'hero-kart-v2-R115.blend'); bpy.ops.wm.save_as_mainfile(filepath=dst); print('R115_REBUILD_OK',dst)
