import bpy
from mathutils import Vector
MD = "/mnt/storage2TB/Coding-Projects/super-kart-3djs/concept-art/the-bubble-bumper/modeling/"
bpy.ops.wm.open_mainfile(filepath=MD + "authored/conjunto-v151.blend")
bpy.context.view_layer.update()
dg = bpy.context.evaluated_depsgraph_get(); sc = bpy.context.scene
DIR = Vector((0,-1,0))
# centro real do elipsoide do ombro
ob = bpy.data.objects.get('P_Shoulder')
pts = [ob.matrix_world @ Vector(c) for c in ob.bound_box]
xs=[p.x for p in pts]; zs_=[p.z for p in pts]; ys=[p.y for p in pts]
print('###SH### P_Shoulder bbox: x %.3f..%.3f  y %.3f..%.3f  z %.3f..%.3f'%(min(xs),max(xs),min(ys),max(ys),min(zs_),max(zs_)))
print('###SH### centro estimado: x=%.3f z=%.3f | semi-eixos: rx=%.3f ry=%.3f rz=%.3f'%(
    (min(xs)+max(xs))/2,(min(zs_)+max(zs_))/2,(max(xs)-min(xs))/2,(max(ys)-min(ys))/2,(max(zs_)-min(zs_))/2))
print('###SH### TOPO do ombro por coluna (1o hit descendo de z=1.08) vs borda do concept:')
# borda do concept medida antes: light acaba em => o ombro comeca abaixo disso
conc = {-0.30:1.040,-0.26:0.980,-0.22:0.940,-0.18:0.920,-0.16:0.918,-0.15:0.915,-0.14:0.912}
for x in (-0.30,-0.26,-0.22,-0.20,-0.18,-0.16,-0.15,-0.14):
    topo=None
    z=1.08
    while z>=0.80:
        ok,loc,nor,idx,obj,mw = sc.ray_cast(dg, Vector((x,2.0,z)), DIR)
        if ok and obj.name=='P_Shoulder':
            topo=z; break
        z=round(z-0.005,4)
    c=conc.get(x)
    if c is not None and topo is not None:
        print('###SH###  x=%+.2f topo_ombro=%.3f  concept_ombro_ate=%.3f  -> precisa DESCER %.3f m'%(x,topo,c,topo-c))
    elif topo is None:
        print('###SH###  x=%+.2f topo_ombro=NAO ENCONTRADO (ombro nao aparece ate z=0.80)'%x)
    else:
        print('###SH###  x=%+.2f topo_ombro=%.3f (sem referencia do concept)'%(x,topo))
