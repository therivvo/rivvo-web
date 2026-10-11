import bpy, math, json
for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)
def box(n,x0,x1,y0,y1,z0,z1,rot=(0,0,0)):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=((x0+x1)/2,(y0+y1)/2,(z0+z1)/2), rotation=rot)
    o=bpy.context.object; o.name=n; o.scale=(abs(x1-x0),abs(y1-y0),abs(z1-z0))
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); return o
def cil(n,x,y,z,r,d,rot=(math.radians(90),0,0)):
    bpy.ops.mesh.primitive_cylinder_add(radius=r,depth=d,vertices=32,location=(x,y,z),rotation=rot)
    o=bpy.context.object; o.name=n; return o
def esf(n,loc,rx,ry,rz):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1.0,location=loc); o=bpy.context.object; o.name=n
    o.scale=(rx,ry,rz); bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); return o
# RODAS: dianteira pequena/ESTREITA, bitola estreita; traseira grande/LARGA, bitola LARGA (concept)
DF,DR,WDF,WDR = 0.400,0.540,0.150,0.290
TF,TR = 0.60,0.86
xf,xr = 0.70,-0.60
cil("W_FL",xf, TF/2,DF/2,DF/2,WDF); cil("W_FR",xf,-TF/2,DF/2,DF/2,WDF)
cil("W_RL",xr, TR/2,DR/2,DR/2,WDR); cil("W_RR",xr,-TR/2,DR/2,DR/2,WDR)
# ASSOALHO CENTRAL BAIXO E ESTREITO (a calha) — a base do U
box("C_Floor", -0.80,0.55, -0.22,0.22, 0.13,0.26)
# PAREDES LATERAIS = SIDEPODS altos e afastados (o VAZIO fica entre eles)
box("SP_L", -0.62,0.34,  0.22,0.54, 0.15,0.58)
box("SP_R", -0.62,0.34, -0.54,-0.22, 0.15,0.58)
# NARIZ em cunha (baixo) + TRASEIRA alta
box("C_Nose", 0.55,0.98, -0.20,0.20, 0.13,0.32)
box("C_Rear",-0.98,-0.62, -0.34,0.34, 0.13,0.66)
# PARA-CHOQUE DIANTEIRO em C (U largo, definidor de silhueta)
box("B_Front", 0.94,1.14, -0.62,0.62, 0.14,0.34)
box("B_EarL",  0.80,1.14,  0.40,0.62, 0.14,0.50)
box("B_EarR",  0.80,1.14, -0.62,-0.40, 0.14,0.50)
# PILOTO AFUNDADO 35% NA CALHA: bacia no assoalho, pernas p/ frente, tronco reclinado 45, volante inclinado
box("P_Hips", -0.50,-0.18, -0.19,0.19, 0.26,0.48)
box("P_Thigh",-0.20,0.34, -0.16,0.16, 0.26,0.44)
box("P_Shin",  0.28,0.42, -0.13,0.13, 0.14,0.42, rot=(0,math.radians(45),0))
box("P_Torso",-0.62,-0.38, -0.17,0.17, 0.42,0.90, rot=(0,math.radians(-45),0))
esf("P_Head", (-0.36,0,0.98), 0.225,0.225,0.225)
box("P_Seat", -0.86,-0.72, -0.21,0.21, 0.26,0.86)
cil("P_Wheel", 0.14,0,0.56, 0.13,0.05, rot=(0,math.radians(62),0))   # volante inclinado
bpy.ops.wm.save_as_mainfile(filepath='/opt/blender-runner/outputs/B008_calha.blend')
print('###B008### ok')
