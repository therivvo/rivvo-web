import bpy, bmesh, json, os
from mathutils import Vector
job=os.path.dirname(os.path.abspath(__file__)); blend=os.path.join(job,'hero-kart-v2-R83.blend'); out=os.path.join(job,'technical-audit.json')
bpy.ops.wm.open_mainfile(filepath=blend)
report={'revision':'R83','blender':bpy.app.version_string,'blend':blend,'collections':{},'materials':[m.name for m in bpy.data.materials],'uv':{},'mounts':[],'sockets':[],'pivots':[]}
for cn in ('LOD0','LOD1','LOD2','COLLISION'):
 c=bpy.data.collections.get(cn); tris=verts=faces=ngons=nm=0; mats=set(); uv_missing=[]; lo=[1e9]*3; hi=[-1e9]*3
 if c:
  for o in c.objects:
   if o.type!='MESH': continue
   me=o.data; me.calc_loop_triangles(); tris+=len(me.loop_triangles); verts+=len(me.vertices); faces+=len(me.polygons); ngons+=sum(len(p.vertices)>4 for p in me.polygons); mats.update(m.name for m in me.materials if m)
   if len(me.uv_layers)==0: uv_missing.append(o.name)
   bm=bmesh.new(); bm.from_mesh(me); nm+=sum(not e.is_manifold for e in bm.edges); bm.free()
   for v in o.bound_box:
    w=o.matrix_world@Vector(v)
    for i in range(3): lo[i]=min(lo[i],w[i]); hi[i]=max(hi[i],w[i])
 report['collections'][cn]={'mesh_objects':sum(1 for o in c.objects if o.type=='MESH') if c else 0,'vertices':verts,'faces':faces,'triangles':tris,'materials':sorted(mats),'material_count':len(mats),'ngons':ngons,'non_manifold_edges':nm,'uv_missing_objects':uv_missing,'dimensions_m':[round(hi[i]-lo[i],4) for i in range(3)] if verts else [0,0,0]}
for o in bpy.data.objects:
 if 'Mount' in o.name: report['mounts'].append({'name':o.name,'parent':o.parent.name if o.parent else None,'loc':[round(x,4) for x in o.location]})
 if 'Socket' in o.name: report['sockets'].append({'name':o.name,'axis':o.get('socket_axis'),'loc':[round(x,4) for x in o.location]})
 if 'Pivot' in o.name: report['pivots'].append({'name':o.name,'axis':o.get('axle_axis_local',o.get('socket_axis')),'loc':[round(x,4) for x in o.location]})
report['scene_properties']={k:bpy.context.scene[k] for k in bpy.context.scene.keys() if k in ('review_revision','revision_parent','revision_scope','windshield_mount_count','windshield_width_m','windshield_width_ratio','windshield_rear_edge_y_m','cockpit_rim_rear_y_m','forearm_clearance_target_m','visor_pivot_count','steering_hub_diameter_ratio_front_wheel')}
report['export']='NOT_ATTEMPTED_TECHNICAL_GATE_BLOCKED'
report['technical_gates']={'lod0_budget':38000<=report['collections']['LOD0']['triangles']<=52000,'lod1_budget':16000<=report['collections']['LOD1']['triangles']<=22000,'lod2_budget':5000<=report['collections']['LOD2']['triangles']<=7500,'max_materials':len(report['collections']['LOD0']['materials'])<=5,'no_ngons':all(v['ngons']==0 for v in report['collections'].values()),'manifold':all(v['non_manifold_edges']==0 for v in report['collections'].values()),'uv_complete':all(not v['uv_missing_objects'] for v in report['collections'].values())}
report['technical_pass']=all(report['technical_gates'].values())
with open(out,'w') as f: json.dump(report,f,indent=2)
print('TECHNICAL_AUDIT_WRITTEN',out); print(json.dumps(report,indent=2))
