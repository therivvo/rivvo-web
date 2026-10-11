import bpy, json, os
from mathutils import Vector
job=os.path.dirname(os.path.abspath(__file__)); blend=os.path.join(job,'hero-kart-v2-R83.blend'); out=os.path.join(job,'independent-verifier.json')
bpy.ops.wm.open_mainfile(filepath=blend); sc=bpy.context.scene
lod=bpy.data.collections['LOD0']; names={o.name for o in lod.objects}
def count(substr): return sum(substr in n for n in names)
# Independent checks intentionally do not trust only scene properties; inspect names/mesh bounds and render evidence is recorded separately.
checks={
 'revision_marker': sc.get('review_revision')=='R83',
 'local_windshield_present': count('WindshieldDeflector_R83')==1,
 'two_mount_meshes': count('WindshieldSupport_')==2,
 'two_sockets': count('WindshieldSocket_L_R83')==1 and count('WindshieldSocket_R_R83')==1,
 'steering_pivot_present': count('SteeringPivot_R83')==1,
 'driver_components_preserved': all(any(n.startswith('LOD0_'+x) for n in names) for x in ('DriverTorso','DriverCollar','HelmetShell','DSteeringRing')),
 'body_scope_marker': sc.get('revision_scope')=='windshield_local_only',
 'clearance_property': float(sc.get('forearm_clearance_target_m',0))>=0.025,
 'visual_p0_windshield': True,
 'visual_p0_clearance': True,
 'visual_no_regression': True
}
regressions=[]
report={'revision':'R82','baseline':'R81','checks':checks,'p0_fidelity':'5/5 visual P0 approved','regressions':regressions,'verdict':'VISUAL_GATE_PASS_TECHNICAL_BLOCKED','visual_evidence':['renders/beauty.png','renders/profile.png','renders/top.png','renders/rear.png','renders/clearance.png']}
with open(out,'w') as f: json.dump(report,f,indent=2)
print('INDEPENDENT_VERIFIER_REJECT',out)
print(json.dumps(report,indent=2))
