import bpy, math, json
for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)
def box(n,x0,x1,y0,y1,z0,z1,rot=(0,0,0)):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=((x0+x1)/2,(y0+y1)/2,(z0+z1)/2), rotation=rot)
    o=bpy.context.object; o.name=n; o.scale=(abs(x1-x0),abs(y1-y0),abs(z1-z0))
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); return o
def cil(n,x,y,z,r,d):
    bpy.ops.mesh.primitive_cylinder_add(radius=r,depth=d,vertices=32,location=(x,y,z),rotation=(math.radians(90),0,0))
    o=bpy.context.object; o.name=n; return o
def esf(n,loc,rx,ry,rz):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1.0,location=loc); o=bpy.context.object; o.name=n
    o.scale=(rx,ry,rz); bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); return o
DF,DR=0.420,0.520; tf,tr=0.62,0.74; xf,xr=0.72,-0.62
cil("W_FL",xf, tf/2,DF/2,DF/2,0.170); cil("W_FR",xf,-tf/2,DF/2,DF/2,0.170)
cil("W_RL",xr, tr/2,DR/2,DR/2,0.240); cil("W_RR",xr,-tr/2,DR/2,DR/2,0.240)
# CHASSI EM CUNHA: 3 blocos de altura crescente (nariz baixo -> traseira alta) + VAO LIVRE em z=0.14
box("C_Nose", 0.40,0.98, -0.16,0.16, 0.14,0.34)
box("C_Mid", -0.20,0.40, -0.20,0.20, 0.14,0.46)
box("C_Rear",-0.85,-0.20, -0.30,0.30, 0.14,0.62)
# SIDEPODS: massas laterais separadas (o U fica entre elas)
box("SP_L", -0.55,0.30,  0.20,0.52, 0.16,0.52)
box("SP_R", -0.55,0.30, -0.52,-0.20, 0.16,0.52)
# PILOTO DENTRO DO U: bacia baixa entre os sidepods, coxa p/ frente, joelho alto, torso reclinado
box("P_Hips", -0.42,-0.10, -0.17,0.17, 0.30,0.52)
box("P_Thigh",-0.12,0.40, -0.15,0.15, 0.34,0.54)
box("P_Shin",  0.30,0.46, -0.12,0.12, 0.16,0.44, rot=(0,math.radians(40),0))
box("P_Torso",-0.54,-0.28, -0.16,0.16, 0.46,0.94, rot=(0,math.radians(-45),0))
esf("P_Head", (-0.28,0,1.02), 0.225,0.225,0.225)
box("P_Seat", -0.78,-0.64, -0.20,0.20, 0.30,0.88)
bpy.ops.wm.save_as_mainfile(filepath='/opt/blender-runner/outputs/B007_cunha.blend')
print('###B007### ok')
