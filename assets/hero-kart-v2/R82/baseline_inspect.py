import bpy, json, os
job=os.path.dirname(os.path.abspath(__file__)); blend=os.path.join(job,'hero-kart-v2-R81-baseline.blend'); out=os.path.join(job,'baseline-inspection.json')
bpy.ops.wm.open_mainfile(filepath=blend)
objects=[]
for o in bpy.data.objects:
    if o.type=='MESH': objects.append({'name':o.name,'collections':[c.name for c in o.users_collection],'parent':o.parent.name if o.parent else None,'verts':len(o.data.vertices),'polys':len(o.data.polygons),'dims':[round(x,5) for x in o.dimensions],'loc':[round(x,5) for x in o.matrix_world.translation]})
report={'revision':bpy.context.scene.get('review_revision'),'blender':bpy.app.version_string,'objects':objects,'collections':{c.name:len(c.objects) for c in bpy.data.collections},'materials':[m.name for m in bpy.data.materials],'scene_properties':{k:bpy.context.scene[k] for k in bpy.context.scene.keys()}}
with open(out,'w') as f: json.dump(report,f,indent=2,default=str)
print('R82_BASELINE_INSPECTION_OK',len(objects),len(report['collections']))
