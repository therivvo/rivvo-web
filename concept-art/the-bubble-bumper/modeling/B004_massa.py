import bpy, math, json
L,H,W=2.35,1.2523,1.4411
D=0.450; R=D/2.0                 # REGUA = CABECA (capacete 0.45 m) — o gate exigiu: roda ~1x capacete
# limpa tudo e reconstroi (B004)
for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)
def box(n,cx,cy,cz,sx,sy,sz):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(cx,cy,cz))
    o=bpy.context.object; o.name=n; o.scale=(sx,sy,sz)
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); return o
def cil(n,x,y,z,r,d,rot):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=d, vertices=32, location=(x,y,z), rotation=rot)
    o=bpy.context.object; o.name=n; return o
def esf(n,loc,rx,ry,rz):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1.0, location=loc)
    o=bpy.context.object; o.name=n; o.scale=(rx,ry,rz)
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); return o
# --- rodas: hierarquia dianteira menor/estreita, traseira maior/larga (concept) ---
DF, DR = 0.420, 0.520
tf, tr = 0.62, 0.72
xf, xr = 0.72, -0.62
cil("W_FL", xf,  tf/2, DF/2, DF/2, 0.170, (math.radians(90),0,0))
cil("W_FR", xf, -tf/2, DF/2, DF/2, 0.170, (math.radians(90),0,0))
cil("W_RL", xr,  tr/2, DR/2, DR/2, 0.230, (math.radians(90),0,0))
cil("W_RR", xr, -tr/2, DR/2, DR/2, 0.230, (math.radians(90),0,0))
# --- banheira: BLOCO UNICO longo, baixo e largo, do nariz ao motor (o gate exigiu) ---
box("E_Tub", -0.05, 0, 0.21, 1.95, 0.62, 0.42)
# --- piloto: massa SENTADA (quadril + coxa + torso + cabeca) ---
box("P_Hips",  -0.30, 0, 0.52, 0.46, 0.40, 0.30)
box("P_Thigh",  0.02, 0, 0.50, 0.62, 0.34, 0.22)
box("P_Torso", -0.24, 0, 0.70, 0.34, 0.36, 0.30)
esf("P_Head",  (-0.22, 0, 1.03), 0.225, 0.225, 0.225)
bpy.ops.wm.save_as_mainfile(filepath='/opt/blender-runner/outputs/B004_massa.blend')
print('###B004###', json.dumps({"DF":DF,"DR":DR,"tf":tf,"tr":tr,"xf":xf,"xr":xr,"wheelbase":xf-xr}))
