import bpy, os, math, json
from mathutils import Vector
job=os.path.dirname(os.path.abspath(__file__))
src=os.path.join(job,'hero-kart-v2-R81-baseline.blend')
out=os.path.join(job,'hero-kart-v2-R82.blend')
bpy.ops.wm.open_mainfile(filepath=src)
# R82 is a class change: remove the broad R81 sheet and replace it with an open, low deflector arc.
for o in list(bpy.data.objects):
    if any(k in o.name for k in ('WindshieldLens_R81','WindshieldMount_','WindshieldSocket_','SteeringPivot_R81')):
        bpy.data.objects.remove(o, do_unlink=True)

def getmat(name, fallback='paint_primary'):
    return bpy.data.materials.get(name) or bpy.data.materials.get(fallback)
def add_mesh(name, verts, faces, material, coll):
    me=bpy.data.meshes.new(name+'_Mesh'); me.from_pydata(verts,[],faces); me.update(calc_edges=True)
    ob=bpy.data.objects.new(name,me); coll.objects.link(ob); me.materials.append(material)
    for p in me.polygons: p.use_smooth=True
    ob['revision']='R82'; ob['authored_component']=name.replace('LOD0_','').replace('LOD1_','').replace('LOD2_','')
    return ob
def add_arc(name, scale, coll):
    cu=bpy.data.curves.new(name+'_Curve','CURVE'); cu.dimensions='3D'; cu.resolution_u=2; cu.bevel_depth=0.017*scale; cu.bevel_resolution=2
    sp=cu.splines.new('BEZIER'); sp.bezier_points.add(8)
    for i,p in enumerate(sp.bezier_points):
        x=-0.31+i*(0.62/8); p.co=(x,-0.895-0.035*(1-(x/0.31)**2),0.735+0.070*(1-(x/0.31)**2)); p.handle_left_type='AUTO'; p.handle_right_type='AUTO'
    ob=bpy.data.objects.new(name,cu); coll.objects.link(ob); ob.data.materials.append(getmat('cockpit_glass')); ob['revision']='R82'; ob['authored_component']='low_open_deflector_arc'; return ob
def add_support(name,x,coll):
    # Narrow swept forged support, deliberately following cowl-to-arc instead of a vertical post.
    w=0.026; verts=[(x-w,-0.785,0.585),(x+w,-0.785,0.585),(x+w*0.72,-0.875,0.72),(x-w*0.72,-0.875,0.72),
                   (x-w,-0.765,0.605),(x+w,-0.765,0.605),(x+w*0.72,-0.855,0.74),(x-w*0.72,-0.855,0.74)]
    faces=[(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)]
    return add_mesh(name,verts,faces,getmat('metal_warm'),coll)
for lod in ('LOD0','LOD1','LOD2'):
    coll=bpy.data.collections.get(lod)
    if not coll: continue
    s=1.0 if lod=='LOD0' else (0.82 if lod=='LOD1' else 0.62)
    add_arc(lod+'_WindshieldDeflector_R82',s,coll)
    add_support(lod+'_WindshieldSupport_L_R82',-0.275,coll); add_support(lod+'_WindshieldSupport_R_R82',0.275,coll)
lod0=bpy.data.collections['LOD0']
for name,loc,axis in [('WindshieldSocket_L_R82',(-0.275,-0.79,0.595),'+X'),('WindshieldSocket_R_R82',(0.275,-0.79,0.595),'-X'),('SteeringPivot_R82',(0,-0.56,0.78),'X')]:
    ob=bpy.data.objects.new('LOD0_'+name,None); lod0.objects.link(ob); ob.empty_display_type='PLAIN_AXES'; ob.empty_display_size=.05; ob.location=loc; ob['socket_axis']=axis; ob['revision']='R82'
sc=bpy.context.scene; sc['review_revision']='R82'; sc['revision_parent']='R81'; sc['revision_scope']='windshield_local_only'; sc['windshield_mount_count']=2; sc['windshield_width_m']=0.62; sc['windshield_width_ratio']=0.68; sc['windshield_top_z_m']=0.805; sc['windshield_base_z_m']=0.735; sc['windshield_rear_edge_y_m']=-0.895; sc['forearm_clearance_target_m']=0.025; sc['windshield_frame_continuous']=False; sc['windshield_open_arc']=True; sc['windshield_integrated_cowl']=True; sc['helmet_shell_wrap']=True; sc['visor_pivot_count']=2; sc['steering_continuous_ring']=True; sc['steering_column_coaxial']=True; sc['no_windshield_over_driver']=True; sc['steering_d_shape']=True; sc['steering_hub_diameter_ratio_front_wheel']=0.214; sc['hand_grip_angles_deg']=[150.0,30.0]; sc['R82_local_change']='replaced broad R81 sheet with low open deflector arc and two swept supports; body/wheels/driver/steering preserved'
bpy.ops.wm.save_as_mainfile(filepath=out)
print('R82_LOCAL_REVISION_OK',out)
