import bpy, json, os
from mathutils import Vector
job = os.path.dirname(os.path.abspath(__file__))
blend = os.path.join(job, 'hero-kart-v2-R80.blend')
out = os.path.join(job, 'r80-inspection.json')
bpy.ops.wm.open_mainfile(filepath=blend)
objects=[]
for o in bpy.data.objects:
    if o.type=='MESH':
        objects.append({'name':o.name,'collection':[c.name for c in o.users_collection],'parent':o.parent.name if o.parent else None,'verts':len(o.data.vertices),'polys':len(o.data.polygons),'materials':[m.name for m in o.data.materials],'dims':[round(x,5) for x in o.dimensions],'loc':[round(x,5) for x in o.matrix_world.translation]})
collections={c.name:len(c.objects) for c in bpy.data.collections}
report={'revision':bpy.context.scene.get('review_revision'),'blender':bpy.app.version_string,'scene':bpy.context.scene.name,'objects':objects,'collections':collections,'custom_properties':{k:bpy.context.scene[k] for k in bpy.context.scene.keys()},'cameras':[o.name for o in bpy.data.objects if o.type=='CAMERA'],'materials':[m.name for m in bpy.data.materials]}
with open(out,'w') as f: json.dump(report,f,indent=2,default=str)
print('R80_INSPECTION_WRITTEN',out,len(objects),len(collections))
