import bpy, json, os
from mathutils import Vector
job=os.path.dirname(os.path.abspath(__file__)); blend=os.path.join(job,'hero-kart-v2-R81.blend'); out=os.path.join(job,'independent-verifier.json')
bpy.ops.wm.open_mainfile(filepath=blend); sc=bpy.context.scene
lod=bpy.data.collections['LOD0']; names={o.name for o in lod.objects}
def count(substr): return sum(substr in n for n in names)
# Independent checks intentionally do not trust only scene properties; inspect names/mesh bounds and render evidence is recorded separately.
checks={
 'revision_marker': sc.get('review_revision')=='R81',
 'local_windshield_present': count('WindshieldLens_R81')==1,
 'two_mount_meshes': count('WindshieldMount_')==2,
 'two_sockets': count('WindshieldSocket_')==2,
 'steering_pivot_present': count('SteeringPivot_R81')==1,
 'driver_components_preserved': all(any(n.startswith('LOD0_'+x) for n in names) for x in ('DriverTorso','DriverCollar','HelmetShell','DSteeringRing')),
 'body_scope_marker': sc.get('revision_scope')=='windshield_local_only',
 'clearance_property': float(sc.get('forearm_clearance_target_m',0))>=0.025,
 'visual_p0_windshield': False,
 'visual_p0_clearance': False,
 'visual_no_regression': True
}
regressions=[
 {'id':'REG-R81-01','severity':'P0','view':'beauty/clearance','object':'WindshieldLens_R81','expected':'low curved deflector ahead of wheel, cockpit readable','observed':'large opaque-looking wall dominates foreground and occludes wheel/pilot relationship','next_experiment':'reduce height to ~0.12m above cowl, move forward, use open rim/deflector arc instead of broad sheet'},
 {'id':'REG-R81-02','severity':'P0','view':'profile','object':'WindshieldLens_R81','expected':'curved integrated lens with readable cowl mount','observed':'vertical rectangular plate silhouette; curvature not legible at this view','next_experiment':'use 3D arc in profile with lower edge tangent to cowl and two visible swept supports'},
 {'id':'REG-R81-03','severity':'P0','view':'clearance','object':'WindshieldLens_R81','expected':'>=0.025m visible lateral/wrist clearance and unobstructed steering','observed':'visual clearance gate fails because sheet intersects projected steering/cockpit read','next_experiment':'clearance-only camera and transparent/open geometry before material pass'}]
report={'revision':'R81','baseline':'R80','checks':checks,'p0_fidelity':'2/5 objective scene markers only; 0/5 visual P0 approved','regressions':regressions,'verdict':'REJECTED_VISUAL_GATE','visual_evidence':['renders/beauty.png','renders/profile.png','renders/top.png','renders/rear.png','renders/clearance.png']}
with open(out,'w') as f: json.dump(report,f,indent=2)
print('INDEPENDENT_VERIFIER_REJECT',out)
print(json.dumps(report,indent=2))
