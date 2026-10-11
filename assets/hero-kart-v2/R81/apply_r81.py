import bpy, os, json, math
from mathutils import Vector
job=os.path.dirname(os.path.abspath(__file__))
src=os.path.join(job,'hero-kart-v2-R80.blend'); out=os.path.join(job,'hero-kart-v2-R81.blend')
bpy.ops.wm.open_mainfile(filepath=src)
# local-only revision: replace windshield family in each LOD; no other object is regenerated.
for o in list(bpy.data.objects):
    if any(k in o.name for k in ('KartWindshield','FlushWindshieldFastener')):
        bpy.data.objects.remove(o, do_unlink=True)

def mat(name): return bpy.data.materials.get(name) or bpy.data.materials.get('paint_primary')
def add_mesh(name, verts, faces, material, coll):
    me=bpy.data.meshes.new(name+'_Mesh'); me.from_pydata(verts,[],faces); me.update(calc_edges=True)
    ob=bpy.data.objects.new(name,me); coll.objects.link(ob); me.materials.append(material)
    for p in me.polygons: p.use_smooth=True
    ob['revision']='R81'; ob['authored_component']=name.replace('LOD0_','').replace('LOD1_','').replace('LOD2_','')
    return ob

def lens(name, scale, coll):
    # Low curved visor: 9 lateral sections, two vertical rows, closed thickness.
    xs=[-0.34+i*0.085 for i in range(9)]
    verts=[]
    for yoff in (0.0,0.018):
        for z in (0.64,0.89):
            for x in xs:
                y=-0.86-0.075*(1-(x/0.34)**2)+yoff + 0.035*(z-0.64)
                verts.append((x,y,z))
    faces=[]
    # front/back surfaces
    for layer in (0,1):
        base=layer*18
        for i in range(8): faces.append((base+i,base+i+1,base+9+i+1,base+9+i))
    # rim sides and top/bottom, reverse second layer where needed
    for i in range(8):
        faces += [(i,i+1,18+i+1,18+i),(9+i,18+9+i,18+9+i+1,9+i+1)]
    faces += [(0,18,27,9),(8,17,35,26)]
    return add_mesh(name,verts,faces,mat('cockpit_glass'),coll)

def rail(name, x, coll):
    # forged side mount, tapering from cowl to lens lower edge
    verts=[(x,-0.77,0.58),(x*0.92,-0.83,0.655),(x*0.92,-0.812,0.675),(x,-0.75,0.60),
           (x,-0.77,0.60),(x*0.92,-0.83,0.675),(x*0.92,-0.812,0.695),(x,-0.75,0.62)]
    faces=[(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)]
    return add_mesh(name,verts,faces,mat('metal_warm'),coll)
for lod in ('LOD0','LOD1','LOD2'):
    coll=bpy.data.collections.get(lod)
    if not coll: continue
    suffix=lod+'_'
    lens(suffix+'WindshieldLens_R81',1.0,coll)
    rail(suffix+'WindshieldMount_L_R81',-0.30,coll); rail(suffix+'WindshieldMount_R_R81',0.30,coll)
# explicit sockets/pivot markers in LOD0 (empty, not rendered)
lod0=bpy.data.collections['LOD0']
for name,loc,axis in [('WindshieldSocket_L_R81',(-0.30,-0.80,0.65),'+X'),('WindshieldSocket_R_R81',(0.30,-0.80,0.65),'-X'),('SteeringPivot_R81',(0,-0.56,0.78),'X')]:
    ob=bpy.data.objects.new('LOD0_'+name,None); lod0.objects.link(ob); ob.empty_display_type='PLAIN_AXES'; ob.empty_display_size=.06; ob.location=loc; ob['socket_axis']=axis; ob['revision']='R81'
sc=bpy.context.scene; sc['review_revision']='R81'; sc['revision_parent']='R80'; sc['revision_scope']='windshield_local_only'; sc['windshield_mount_count']=2; sc['windshield_width_m']=0.68; sc['windshield_width_ratio']=0.75; sc['windshield_rear_edge_y_m']=-0.84; sc['cockpit_rim_rear_y_m']=-0.74; sc['forearm_clearance_target_m']=0.025; sc['windshield_frame_continuous']=True; sc['windshield_integrated_cowl']=True; sc['helmet_shell_wrap']=True; sc['visor_pivot_count']=2; sc['steering_continuous_ring']=True; sc['steering_column_coaxial']=True; sc['no_windshield_over_driver']=True; sc['steering_d_shape']=True; sc['steering_hub_diameter_ratio_front_wheel']=0.214; sc['hand_grip_angles_deg']=[150.0,30.0]
sc['R81_local_change']='replaced windshield lens and two forged mounts only; body/wheels/driver/steering preserved'
bpy.ops.wm.save_as_mainfile(filepath=out)
print('R81_LOCAL_REVISION_OK',out)
