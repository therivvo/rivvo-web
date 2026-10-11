# MAPA PREFIXO->COR VALIDADO CONTRA O CONCEPT (fracao de azul casou: 58,6-61,2%% vs 62-63%%)
import bpy, math
sc=bpy.context.scene; sc.render.resolution_x=1100; sc.render.resolution_y=1100
sc.render.film_transparent=True
try: sc.render.engine='BLENDER_EEVEE_NEXT'
except Exception: sc.render.engine='BLENDER_EEVEE'
def mat(nome,cor):
    m=bpy.data.materials.new(nome); m.use_nodes=True; nt=m.node_tree; nt.nodes.clear()
    d=nt.nodes.new('ShaderNodeBsdfDiffuse'); d.inputs[0].default_value=cor
    o=nt.nodes.new('ShaderNodeOutputMaterial'); nt.links.new(d.outputs[0],o.inputs['Surface']); return m
REG=[('P_Thigh',(0.16,0.16,0.19,1)),('P_Shin',(0.16,0.16,0.19,1)),('P_Boot',(0.10,0.10,0.12,1)),('W_',(0.04,0.04,0.04,1)),('P_Head',(0.10,0.35,0.85,1)),('P_Visor',(0.03,0.03,0.05,1)),
     ('P_',(0.10,0.35,0.85,1)),('SP_',(0.95,0.80,0.12,1)),('C_Floor',(0.04,0.05,0.08,1)),
     ('C_',(0.90,0.90,0.93,1)),('B_',(0.60,0.60,0.64,1)),('R_',(0.66,0.66,0.70,1))]
def cor(n):
    for p,c in REG:
        if n.startswith(p): return c
    return (0.5,0.5,0.52,1)
for o in bpy.data.objects:
    if o.type=='MESH':
        o.data.materials.clear(); o.data.materials.append(mat('M_'+o.name, cor(o.name)))
sc.world=bpy.data.worlds.new('W'); sc.world.use_nodes=True
sc.world.node_tree.nodes['Background'].inputs[0].default_value=(0.94,0.95,0.97,1)
sc.world.node_tree.nodes['Background'].inputs[1].default_value=0.7
bpy.ops.object.light_add(type='SUN', location=(3,-4,6)); L=bpy.context.object
L.data.energy=3.8; L.rotation_euler=(math.radians(50),0,math.radians(35))
bpy.ops.object.light_add(type='SUN', location=(-4,3,5)); L2=bpy.context.object
L2.data.energy=1.4; L2.rotation_euler=(math.radians(60),0,math.radians(205))
def cam(nome,loc,rot,ortho):
    cd=bpy.data.cameras.new(nome); cd.type='ORTHO'; cd.ortho_scale=ortho
    o=bpy.data.objects.new(nome,cd); o.location=loc; o.rotation_euler=rot
    sc.collection.objects.link(o); return o
# CAMERAS PADRAO (sem rotacao exotica): frente = -X (para o lado +X), lado = -Y, topo = -Z
Cm={'front':cam('CF',(6,0,0.50),(math.radians(90),0,math.radians(90)),2.55),
    'side' :cam('CS',(0,6,0.50),(math.radians(90),0,math.radians(180)),2.55),
    'rear' :cam('CB',(-6,0,0.50),(math.radians(90),0,math.radians(-90)),2.55),
    'top'  :cam('CT',(0,0,6),(0,0,0),2.55)}
for k,c in Cm.items():
    sc.camera=c; sc.render.filepath='/tmp/B013s_%s.png'%k; bpy.ops.render.render(write_still=True)
print('RENDER_S OK')
