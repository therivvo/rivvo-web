import bpy, json, math
L=2.3500; H=1.1881; W=1.3912; P=0.8257
X0, X1 = -L/2.0, L/2.0
Y0, Y1 = -W/2.0, W/2.0
Z0, Z1 = 0.0, H
D = {}
def mk(nome, loc):
    e = bpy.data.objects.new(nome, None)
    e.empty_display_type = 'PLAIN_AXES'; e.empty_display_size = 0.06
    e.location = loc; bpy.context.scene.collection.objects.link(e); return e
mk('D_Ground', (0,0,0)); mk('D_CenterPlane', (0,0,0))
mk('D_LengthFront', (X1,0,0)); mk('D_LengthRear', (X0,0,0))
mk('D_WidthL', (0,Y1,0)); mk('D_WidthR', (0,Y0,0))
mk('D_Top', (0,0,Z1)); mk('D_PilotBase', (0,0,Z1-P))
mk('D_WheelFL', (0.4825, 0.5565, 0.1715)); mk('D_WheelFR', (0.4825, -0.5565, 0.1715))
mk('D_WheelRL', (-0.6900, 0.5565, 0.1715)); mk('D_WheelRR', (-0.6900, -0.5565, 0.1715))
mk('D_AxleFront', (0.4825,0,0.1715)); mk('D_AxleRear', (-0.6900,0,0.1715))
mk('D_CockpitTop', (-0.05,0,Z1-P+0.10)); mk('D_HelmetCenter', (-0.05,0,Z1-0.11))
mk('D_BumperSpine', (X1-0.05,0,0.235)); mk('D_WingAxis', (X0+0.14,0,0.665))
def cam(nome, loc, rot, ortho):
    cd = bpy.data.cameras.new(nome); cd.type = 'ORTHO'; cd.ortho_scale = ortho
    o = bpy.data.objects.new(nome, cd); o.location = loc; o.rotation_euler = rot
    bpy.context.scene.collection.objects.link(o); return o
cam('CAM_FRONT', (6,0,0.6), (math.radians(90),0,math.radians(90)), L*1.05)
cam('CAM_BACK', (-6,0,0.6), (math.radians(90),0,math.radians(-90)), L*1.05)
cam('CAM_SIDE', (0,-6,0.6), (math.radians(90),0,0), L*1.05)
cam('CAM_TOP', (0,0,6), (0,0,0), L*1.05)
D.update({'L':L,'H':H,'W':W,'pilot':P,'X0':X0,'X1':X1,'Z1':Z1,'n_obj':len(bpy.data.objects)})
bpy.ops.wm.save_as_mainfile(filepath='/opt/blender-runner/outputs/B001_datums.blend')
print('###B001###', json.dumps(D))
