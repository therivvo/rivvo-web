import bpy, math, json
L,H,W,D,R = 2.35,1.2523,1.4411,0.703,0.3515
# B002: rodas e envelopes (Sol: cilindros-envelope SEM tread; tread so em B009)
# centros: x dianteiro/traseiro medidos no painel SIDE pelo eixo; y pela BITOLA (80% de W, Gate B)
track = 0.800*W/2.0
wf, wr = 0.4825, -0.6900
cz = R                      # roda apoia no chao
def roda(nome, x, y):
    bpy.ops.mesh.primitive_cylinder_add(radius=R, depth=0.215, vertices=32, location=(x,y,cz), rotation=(math.radians(90),0,0))
    o=bpy.context.object; o.name=nome; return o
for n,x,y in (("W_FL",wf,track),("W_FR",wf,-track),("W_RL",wr,track),("W_RR",wr,-track)):
    roda(n,x,y)
# envelope do corpo (banheira) e do piloto, como massas simples na CLASSE correta
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-0.15,0,0.30)); b=bpy.context.object; b.name="E_Tub"
b.scale=(L*0.30/2, W*0.42/2, 0.30/2)
bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
bpy.ops.mesh.primitive_uv_sphere_add(radius=H*0.14, location=(-0.15,0,H-H*0.14)); s=bpy.context.object; s.name="E_Pilot"
bpy.ops.wm.save_as_mainfile(filepath='/opt/blender-runner/outputs/B002_envelopes.blend')
D={"D_roda":D,"R":R,"track":track,"wf":wf,"wr":wr,"wheelbase":wf-wr,"n":len([o for o in bpy.data.objects if o.type=='MESH'])}
print('###B002###', json.dumps(D))
