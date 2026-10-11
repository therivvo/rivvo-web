import bpy, math, json
L,H,W=2.35,1.2523,1.4411
for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)
def box(n, x0,x1, y0,y1, z0,z1, rot=(0,0,0)):
    cx,cy,cz=(x0+x1)/2,(y0+y1)/2,(z0+z1)/2
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(cx,cy,cz), rotation=rot)
    o=bpy.context.object; o.name=n
    o.scale=(abs(x1-x0), abs(y1-y0), abs(z1-z0))   # DIMENSAO TOTAL (nao metade)
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); return o
def cil(n,x,y,z,r,d):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=d, vertices=32, location=(x,y,z), rotation=(math.radians(90),0,0))
    o=bpy.context.object; o.name=n; return o
def esf(n,loc,rx,ry,rz):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1.0, location=loc)
    o=bpy.context.object; o.name=n; o.scale=(rx,ry,rz)
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); return o
DF,DR=0.420,0.520; tf,tr=0.62,0.74; xf,xr=0.72,-0.62
cil("W_FL",xf, tf/2,DF/2,DF/2,0.170); cil("W_FR",xf,-tf/2,DF/2,DF/2,0.170)
cil("W_RL",xr, tr/2,DR/2,DR/2,0.240); cil("W_RR",xr,-tr/2,DR/2,DR/2,0.240)
# CHASSI real: L=1.95 x W=0.70 x H=0.38, fundo em z=0.12 (VAO LIVRE sob o chassi)
box("T_Chassi", -1.00,0.95, -0.35,0.35, 0.12,0.50)
# cortes: cunha do nariz (topo da frente) e COCKPIT EM U (meio)
box("T_CutNose",    0.45,1.20, -0.60,0.60, 0.40,0.80)
box("T_CutCockpit", -0.55,0.25, -0.26,0.26, 0.26,0.75)
for n in ("T_CutNose","T_CutCockpit"):
    m=bpy.data.objects['T_Chassi'].modifiers.new(name='b_'+n, type='BOOLEAN')
    m.operation='DIFFERENCE'; m.object=bpy.data.objects[n]; m.solver='EXACT'
bpy.context.view_layer.objects.active=bpy.data.objects['T_Chassi']
for n in ("T_CutNose","T_CutCockpit"):
    bpy.ops.object.modifier_apply(modifier='b_'+n)
for n in ("T_CutNose","T_CutCockpit"): bpy.data.objects.remove(bpy.data.objects[n], do_unlink=True)
# PILOTO DENTRO do U
box("P_Hips", -0.48,-0.14, -0.17,0.17, 0.28,0.52)
box("P_Thigh",-0.16,0.44, -0.15,0.15, 0.32,0.52)
box("P_Shin",  0.36,0.56, -0.12,0.12, 0.14,0.42, rot=(0,math.radians(38),0))
box("P_Torso",-0.56,-0.30, -0.16,0.16, 0.44,0.92, rot=(0,math.radians(-45),0))
esf("P_Head", (-0.30,0,1.02), 0.225,0.225,0.225)
box("P_Seat", -0.74,-0.62, -0.21,0.21, 0.30,0.86)
bpy.ops.wm.save_as_mainfile(filepath='/opt/blender-runner/outputs/B006b.blend')
d=bpy.data.objects['T_Chassi']
print('###B006b###', json.dumps({"chassi_v":len(d.data.vertices),"f":len(d.data.polygons)}))
