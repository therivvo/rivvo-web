import bpy, math, json
L,H,W=2.35,1.2523,1.4411
for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)
def box(n,cx,cy,cz,sx,sy,sz,rot=(0,0,0)):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(cx,cy,cz), rotation=rot)
    o=bpy.context.object; o.name=n; o.scale=(sx,sy,sz)
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); return o
def cil(n,x,y,z,r,d):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=d, vertices=32, location=(x,y,z), rotation=(math.radians(90),0,0))
    o=bpy.context.object; o.name=n; return o
def esf(n,loc,rx,ry,rz):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1.0, location=loc)
    o=bpy.context.object; o.name=n; o.scale=(rx,ry,rz)
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); return o
DF,DR=0.420,0.520; tf,tr=0.62,0.72; xf,xr=0.72,-0.62
cil("W_FL",xf, tf/2,DF/2,DF/2,0.170); cil("W_FR",xf,-tf/2,DF/2,DF/2,0.170)
cil("W_RL",xr, tr/2,DR/2,DR/2,0.230); cil("W_RR",xr,-tr/2,DR/2,DR/2,0.230)
# BANHEIRA com nariz AFUNILADO e ALARGANDO atras + RECORTE do cockpit (blocos separados, sem boolean)
box("T_Nose",  0.86, 0, 0.19, 0.50, 0.40, 0.34)      # nariz estreito
box("T_Front", 0.36, 0, 0.21, 0.56, 0.56, 0.40)      # frente
box("T_Mid_L",-0.14, 0.34, 0.21, 0.72, 0.22, 0.40)   # lateral esq (deixa o cockpit vazio)
box("T_Mid_R",-0.14,-0.34, 0.21, 0.72, 0.22, 0.40)   # lateral dir
box("T_Floor",-0.14, 0, 0.06, 0.72, 0.72, 0.11)      # assoalho (cockpit fundo)
box("T_Rear", -0.86, 0, 0.23, 0.68, 0.78, 0.44)      # traseira larga
# PILOTO SENTADO: quadril BAIXO, coxa HORIZONTAL, torso RECLINADO 60 graus, cabeca a frente do encosto
box("P_Hips", -0.34, 0, 0.36, 0.40, 0.38, 0.26)
box("P_Thigh", 0.06, 0, 0.34, 0.74, 0.34, 0.20)      # coxa horizontal para FRENTE (+x)
box("P_Torso",-0.40, 0, 0.62, 0.30, 0.34, 0.52, rot=(0, math.radians(-28), 0))   # reclinado
esf("P_Head", (-0.30, 0, 1.00), 0.225, 0.225, 0.225)
box("P_Seat", -0.62, 0, 0.60, 0.16, 0.44, 0.60)      # encosto
bpy.ops.wm.save_as_mainfile(filepath='/opt/blender-runner/outputs/B005_pose.blend')
print('###B005###', json.dumps({"nota":"piloto sentado: quadril z=0.36 coxa horizontal x0.06 torso reclinado 28deg"}))
