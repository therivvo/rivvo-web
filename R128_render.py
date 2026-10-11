import bpy, os
from mathutils import Vector
job=os.path.dirname(os.path.abspath(__file__)); blend=os.path.join(job,'assets/hero-kart-v2/R128/hero-kart-v2-R128.blend'); out=os.path.join(job,'assets/hero-kart-v2/R128/renders'); os.makedirs(out,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=blend); sc=bpy.context.scene; sc.render.engine='BLENDER_EEVEE'; sc.render.resolution_x=960; sc.render.resolution_y=720; sc.render.resolution_percentage=100; sc.render.image_settings.file_format='PNG'; sc.render.film_transparent=False
for n in ('LOD0','LOD1','LOD2'): bpy.data.collections[n].hide_render=(n!='LOD0')
cam=sc.camera
def aim(pos,target,lens): cam.location=pos; cam.rotation_euler=(Vector(target)-Vector(pos)).to_track_quat('-Z','Y').to_euler(); cam.data.lens=lens
views={'beauty':((3.05,-3.55,2.05),(0,0,.58),50),'profile':((3.9,0,.95),(0,0,.58),55),'top':((0,0,5.15),(0,0,.35),55),'rear':((0,4.15,.88),(0,.22,.54),55),'clearance':((2.65,-2.90,1.62),(0,-.05,.90),52)}
for name,(pos,target,lens) in views.items(): aim(pos,target,lens); sc.render.filepath=os.path.join(out,name+'.png'); bpy.ops.render.render(write_still=True); print('R128_RENDERED',name)
print('R128_RENDER_SET_OK',out)
