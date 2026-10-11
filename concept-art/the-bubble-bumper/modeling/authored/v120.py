import bpy, bmesh, math
from mathutils import Vector
MD = "/mnt/storage2TB/Coding-Projects/super-kart-3djs/concept-art/the-bubble-bumper/modeling/"
# ===== CONJUNTO v008 — layout MEDIDO do concept (chao em y=484, escala 3,13 mm/px) =====
# wheelbase 1,3625 (front x=+0.5875 | rear x=-0.775) | cowl frontal SOBE ate 0,65
# capacete estacoes 60-70% -> centro x=-0.35 | asa estacoes 86-96% -> x -1.08..-0.85
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene

def mat(n, rgb, rough=0.45, metal=0.0):
    m = bpy.data.materials.get(n) or bpy.data.materials.new(n)
    m.use_nodes = True
    b = m.node_tree.nodes.get("Principled BSDF")
    if b:
        b.inputs["Base Color"].default_value = (rgb[0], rgb[1], rgb[2], 1.0)
        b.inputs["Roughness"].default_value = rough
        b.inputs["Metallic"].default_value = metal
    m.diffuse_color = (rgb[0], rgb[1], rgb[2], 1.0)
    return m

M_BODY = mat("Body_Blue", (0.055, 0.145, 0.62))
M_ACC  = mat("Accent_Yellow", (0.94, 0.76, 0.05))
M_WHITE= mat("Trim_White", (0.92, 0.93, 0.95))
M_SEAT = mat("Seat_Dark", (0.075, 0.078, 0.085), 0.35)   # v081: banco PRETO (concept)
M_TIRE = mat("Tire_Black", (0.028, 0.028, 0.032), 0.85)
M_SUIT = mat("Pilot_Suit", (0.10, 0.28, 0.72))
M_HELM = mat("Helmet_Blue", (0.06, 0.20, 0.70), 0.25)
M_VIS  = mat("Visor_Dark", (0.04, 0.05, 0.07), 0.15)
M_VISL = mat("Visor_Grey", (0.30, 0.33, 0.37), 0.35)   # v086: visor cinza perceptivel
M_METAL= mat("Metal", (0.62, 0.63, 0.66), 0.35, 0.85)
M_CHROME= mat("Chrome", (0.93, 0.94, 0.97), 0.22, 0.30)  # REGRA 246: cromo CARTOON
# REGRA 247: cromo de cartoon com EMISSIVE fraco (0.30) — nunca cai abaixo do fundo em sombra
_e = M_CHROME.node_tree.nodes.new("ShaderNodeEmission")
_e.inputs[0].default_value = (0.93, 0.94, 0.97, 1.0); _e.inputs[1].default_value = 0.35  # REGRA 250: emission 2.2 ESTOURA e mata hierarquia
_mix = M_CHROME.node_tree.nodes.new("ShaderNodeMixShader"); _mix.inputs[0].default_value = 0.25
_out = M_CHROME.node_tree.nodes.get("Material Output")
_bsdf = M_CHROME.node_tree.nodes.get("Principled BSDF")
M_CHROME.node_tree.links.new(_bsdf.outputs[0], _mix.inputs[1])
M_CHROME.node_tree.links.new(_e.outputs[0], _mix.inputs[2])
M_CHROME.node_tree.links.new(_mix.outputs[0], _out.inputs[0])

def ob(bm, name, m, smooth=True):
    me = bpy.data.meshes.new(name + "Mesh"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); sc.collection.objects.link(o)
    o.data.materials.append(m)
    if smooth:
        for p in o.data.polygons: p.use_smooth = True
    return o

def anel3d(n, x, yc, zc, r_out, r_in, w, v=48, m=M_TIRE, rborda=None):
    # rborda: raio de arredondamento das bordas laterais (rodas traseiras) — regra 229
    """PNEU como ANEL (annulus) — cilindro macico esconde o aro (regra 222)."""
    bm = bmesh.new()
    anel_ext, anel_int = [], []
    for lado in (-w / 2, w / 2):
        ext = [bm.verts.new((x + r_out * math.cos(2 * math.pi * k / v), yc + lado, zc + r_out * math.sin(2 * math.pi * k / v))) for k in range(v)]
        itn = [bm.verts.new((x + r_in * math.cos(2 * math.pi * k / v), yc + lado, zc + r_in * math.sin(2 * math.pi * k / v))) for k in range(v)]
        anel_ext.append(ext); anel_int.append(itn)
    for k in range(v):
        k2 = (k + 1) % v
        if not rborda:
            bm.faces.new((anel_ext[0][k], anel_ext[0][k2], anel_int[0][k2], anel_int[0][k]))   # face -y
            bm.faces.new((anel_int[1][k], anel_int[1][k2], anel_ext[1][k2], anel_ext[1][k]))   # face +y
        bm.faces.new((anel_ext[0][k], anel_ext[1][k], anel_ext[1][k2], anel_ext[0][k2]))       # banda externa
        bm.faces.new((anel_int[0][k2], anel_int[1][k2], anel_int[1][k], anel_int[0][k]))       # banda interna
    if rborda:
        # arredondar as bordas: criar anel intermediario
        for lado in (0, 1):
            sgn = -1 if lado == 0 else 1
            meio = []
            for k in range(v):
                vv1 = anel_ext[lado][k]; vv2 = anel_int[lado][k]
                ym = (vv1.co.y + vv2.co.y) / 2
                r_m = (vv1.co.z - zc + vv2.co.z - zc) / 2 if False else abs(vv1.co.z - zc) * 0.5 + abs(vv2.co.z - zc) * 0.5
                import math as _m
                ang = _m.atan2(vv1.co.z - zc, vv1.co.x - x)
                raiom = r_out - rborda * 0.3
                meio.append(bm.verts.new((x + raiom * _m.cos(ang), ym - sgn * rborda * 0.5, zc + raiom * _m.sin(ang))))
            for k in range(v):
                k2 = (k + 1) % v
                A = anel_ext[lado]; B = anel_int[lado]
                bm.faces.new((A[k], A[k2], meio[k2], meio[k]))
                bm.faces.new((meio[k], meio[k2], B[k2], B[k]))
    bm.normal_update()
    o = ob(bm, n, m)
    for p in o.data.polygons: p.use_smooth = False
    return o

def cil(n, x, y, z, r, d, rot=(math.radians(90), 0, 0), v=28, m=M_METAL, smooth=True):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=v, radius1=r, radius2=r, depth=d)
    o = ob(bm, n, m)
    if not smooth:                     # roda: FLAT (quina nitida) senao vira esfera
        for p in o.data.polygons: p.use_smooth = False
    o.rotation_euler = rot; o.location = (x, y, z)
    return o

def esf(n, loc, rx, ry, rz, m=M_SUIT, seg=24):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=max(8, seg // 2), radius=1.0)
    o = ob(bm, n, m); o.scale = (rx, ry, rz); o.location = loc
    return o

def box(n, x0, x1, y0, y1, z0, z1, m=M_BODY, bevel=0.010, smooth=False):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
    o = ob(bm, n, m, smooth=smooth)
    # REGRA 208: create_cube(size=1.0) tem ARESTA 1 (bbox +-0.5) -> scale = dimensao, NAO dimensao/2
    o.scale = (abs(x1 - x0), abs(y1 - y0), abs(z1 - z0))
    o.location = ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2)
    if bevel > 0:
        b = o.modifiers.new("bev", "BEVEL"); b.width = bevel; b.segments = 2
    return o

def anel(yi, yo, zb, zt, py=0.55, pz=0.55, n=16):
    yc, zc = (yi + yo) / 2, (zb + zt) / 2
    ry, rz = (yo - yi) / 2, (zt - zb) / 2
    pts = []
    for k in range(n):
        a = 2 * math.pi * k / n
        cy, cz = math.cos(a), math.sin(a)
        pts.append((yc + ry * math.copysign(abs(cy) ** py, cy), zc + rz * math.copysign(abs(cz) ** pz, cz)))
    return pts

def loft(n, secoes, m=M_BODY):
    bm = bmesh.new(); rings = []
    for x, pts in secoes:
        rings.append([bm.verts.new((x, y, z)) for (y, z) in pts])
    for i in range(len(rings) - 1):
        a, b = rings[i], rings[i + 1]
        for k in range(len(a)):
            bm.faces.new((a[k], a[(k + 1) % len(a)], b[(k + 1) % len(b)], b[k]))
    bm.faces.new(list(reversed(rings[0]))); bm.faces.new(list(rings[-1]))
    bm.normal_update()
    return ob(bm, n, m)

# ---------- RODAS (medido: front x=+0.5875 d=0.235 | rear x=-0.775 d=0.26 -> usar 0,407 no traseiro) ----------
XF, XR = +0.702, -0.818   # v072: re-medido concept pneu[0.526..0.869] centro~0.70 — overhang 1.175-0.835=0.34 (1.26d)
for tag, x, yc, r, w in (("FL", XF, +0.6390, 0.133, 0.163), ("FR", XF, -0.6390, 0.133, 0.163),
                         ("RL", XR, +0.5600, 0.1775, 0.320), ("RR", XR, -0.5600, 0.1775, 0.320)):
    anel3d("TIRE_" + tag, x, yc, r + 0.002, r, r * 0.60, w, v=48, m=M_TIRE, rborda=(0.046 if "R" in tag else 0.030))   # v082d: furo 0.60r -> 0.28r (banda de PNEU grossa; o aro de 0.30r preenche o furo)
    _s = 1.0 if yc > 0 else -1.0
    cil("RIM_" + tag, x, yc + _s * w * 0.30, r + 0.002, r * 0.62, w * 0.14, m=M_METAL, v=32, smooth=False)   # v082: era r*0.62 (cobria 62% do pneu)   # aro cinza (visivel no anel)
    cil("RING_" + tag, x, yc + _s * w * 0.38, r + 0.002, r * 0.14, w * 0.08, m=M_ACC, v=28, smooth=False)   # v082: era r*0.42     # anel amarelo
    cil("HUB_" + tag, x, yc + _s * w * 0.42, r + 0.002, r * 0.07, w * 0.06, m=M_METAL, v=20, smooth=False)   # v082: era r*0.17   # cubo
print("###W35### rodas: front d=0.266 x=+0.702 | rear d=0.330 x=-0.818 (wheelbase 1.520)")
# v081 (vision P2): SULCOS do pneu = 3 aneis (o TREAD e' o ponto de contato: z min = 0 exato)
for _tag, _x, _yc, _r, _w in (("FL", XF, +0.6390, 0.133, 0.163), ("FR", XF, -0.6390, 0.133, 0.163),
                              ("RL", XR, +0.5600, 0.1775, 0.320), ("RR", XR, -0.5600, 0.1775, 0.320)):
    for _k in (-1, 0, 1):
        anel3d("TRD_%s_%d" % (_tag, _k + 2), _x, _yc + _k * _w * 0.22, _r + 0.002, _r + 0.002, _r * 0.94,
              _w * 0.085, v=32, m=M_METAL)   # v087b: sulco FINO (6% do raio) — 0.80r comia metade da banda de borracha   # v082c: ANEL VAZADO — o cilindro cheio virava DISCO cinza cobrindo o pneu
# v078 (AUDITORIA): as 4 rodas eram ILHAS — 0 de 214 pares tocavam qualquer roda.
# Eixo passando da longarina do chassi (Y=+/-0.205) ate o centro do pneu.
for _tag, _x, _yc, _r in (("F", XF, 0.6390, 0.133), ("R", XR, 0.5780, 0.165)):
    for _s in (+1, -1):
        if _tag == "F":
            cil("AXL_F_%d" % _s, _x, _s * 0.400, _r, 0.030, 0.620, v=16, smooth=False)   # y 0.09..0.71 -> alcanca o RIM diant.
            box("STRUT_F_%d" % _s, _x - 0.045, _x + 0.045, _s * 0.150, _s * 0.260, 0.115, 0.245, m=M_METAL, bevel=0.010)
        else:
            cil("AXL_R_%d" % _s, _x, _s * 0.410, _r, 0.032, 0.580, v=16, smooth=False)   # y 0.12..0.70 -> alcanca o RIM tras.
        box("HUBST_%s_%d" % (_tag, _s), _x - 0.055, _x + 0.055, _s * 0.50, _s * 0.62, _r - 0.055, _r + 0.055,
            m=M_METAL, bevel=0.012)                                                          # stub do cubo (visivel no SIDE)

# ---------- NOSE BAIXO + COWL QUE SOBE (concept: 10%=0.354 -> 30%=0.651) ----------
# NARIZ v039: BAIXO de vez (auditor x3: "bulboso alto"; concept: ponta quase no chao)
# CUNHA com ARESTA RETA (v042): secao TRAPEZOIDAL — topo plano, le de cunha de lado
def trapezio(yi, yo, zb, zt, ztop):
    """secao com base larga, topo plano mais estreito (trapezio) — aresta reta no perfil."""
    pts=[]
    for k in range(4):
        t=k/3.0
        pts.append((yi+(yo*0.55-yi)*t, zb))
    for k in range(4):
        t=k/3.0
        pts.append((yo*0.55+(yo-yo*0.55)*t, ztop))
    # lados
    pts=[(yi,zb),(yo*0.62,zb),(yo*0.80,ztop),(yo,ztop)]
    # duplicar densidade: anel de 12 pontos interpolando
    out=[]
    for k in range(12):
        t=k/11.0
        if t<0.5:
            tt=t*2; out.append((yi+(yo*0.62-yi)*tt, zb))
        else:
            tt=(t-0.5)*2; out.append((yo*0.62+(yo-yo*0.62)*tt, zb+(ztop-zb)*tt))
    return out
# NARIZ BAIXO-BLUNT (v053, vision 22-25% H): capsula U, topo 0.28, ponta arredondada
def sec_U(yo, zb, zt, p=0.55):
    """secao U arredondada via superelipse (squircle): base e topo largos, cantos arredondados."""
    pts=[]
    n=24
    for k in range(n):
        t=k/(n-1.0)*math.pi   # 0..pi (esq->dir)
        c=math.cos(t); si=math.sin(t)
        # superelipse com expoente p<1 achata cantos -> U
        sc=math.copysign(abs(c)**p, c)
        ss=si**p
        pts.append((yo*sc, zb+(zt-zb)*ss))
    return pts
loft("N_Nose", [
    (1.178, sec_U(0.075, 0.085, 0.190, p=0.88)),
    (1.168, sec_U(0.145, 0.060, 0.230, p=0.88)),
    (1.150, sec_U(0.230, 0.045, 0.268, p=0.88)),
    (1.115, sec_U(0.330, 0.038, 0.300, p=0.88)),
    (1.060, sec_U(0.470, 0.040, 0.322, p=0.88)),
    (0.980, sec_U(0.515, 0.042, 0.316, p=0.88)),
    (0.900, sec_U(0.360, 0.042, 0.302, p=0.88)),
    (0.840, sec_U(0.240, 0.041, 0.292, p=0.88)),
    (0.780, sec_U(0.152, 0.040, 0.278, p=0.88)),
], M_BODY)  # v071: FRENTE VERTICAL ROMBA - capsula curta, nao cone horizontal
# RAMPA AMARELA do concept: reta inclinada 20-25° do topo do nariz ate o cowl
loft("N_Ramp", [
    (0.78, sec_U(0.145, 0.04, 0.278)),  # v116: casa com o fim do nariz (sem degrau)
    (0.60, sec_U(0.155, 0.04, 0.40)),
    (0.42, sec_U(0.160, 0.04, 0.50)),
    (0.24, sec_U(0.168, 0.04, 0.55)),
], M_ACC)
# COWL AUTORAL (v023): estações medidas do concept + seção ELÍPTICA suave (py/pz 0.78/0.70)
COWL = [
    (0.42,  0.160, 0.520, 0.185),   # v054: cowl so' ATRAS da rampa — rampa amarela exposta 0.24..0.78
    (0.235, 0.170, 0.585, 0.185),   # est 40% — topo 0.595
    (0.10,  0.175, 0.630, 0.180),
    (0.10,  0.180, 0.690, 0.172),   # fim do cowl — cockpit aberto dai para tras (regra 233)
]
loft("N_Cowl", [(x, anel(-yo, yo, zb, zt, py=0.78, pz=0.70, n=20)) for (x, zb, zt, yo) in COWL], M_BODY)
esf("N_Tank", (0.30, 0.0, 0.520), 0.095, 0.140, 0.058, m=M_BODY, seg=20)  # v057: tanque ATRAS (sobre o cowl), abaixo do topo da rampa
for _g in range(9):   # v088: GRADE LARGA — medido 8.7% de W no v087 vs 30-35% no concept
    _gy = -0.200 + 0.050 * _g
    box("N_Grill%d" % _g, 1.162, 1.178, _gy - 0.011, _gy + 0.011, 0.055, 0.170, m=M_TIRE, bevel=0.002)
for _s in (+1, -1):   # v088: blocos AMARELOS arredondados ladeando a grade (concept)
    box("N_BumpCap_%d" % _s, 1.150, 1.176, _s * 0.225, _s * 0.360, 0.050, 0.180, m=M_ACC, bevel=0.020)
print("###W34### nariz + cowl subindo (0.36 -> 0.655)")

# ---------- BUMPER em U FINO ----------
# bumper em C (v026): TUBO EM ARCO — revolucao de secao circular, nao caixas com bevel (regra 224)
def arco_tubo(n, r_arco, r_tubo, x_c, y_c, z_c, n_seg=24, m=M_ACC):
    bm = bmesh.new()
    rings = []
    for k in range(n_seg + 1):
        _a = -math.pi / 2 + math.pi * k / n_seg     # -90..+90 graus (semicirculo)
        _cx = x_c + r_arco * math.sin(0)            # arco no plano X constante? NAO: arco em Y-X
        _ax = x_c + r_arco * (1 - math.cos(_a))      # o CENTRO (y=0) avanca r_arco
        _ay = y_c + r_arco * math.sin(_a) * 0        # placeholder
        _yy = r_arco * math.sin(_a)
        ring = []
        for j in range(12):
            _b = 2 * math.pi * j / 12
            # ponto do tubo ao redor do eixo do arco (eixo vertical Z no ponto do arco)
            ring.append((_ax, _yy + r_tubo * math.cos(_b) * 0 + 0.0, z_c + r_tubo * math.sin(_b)))
        # corrigir: tubo circular no plano XZ? o arco vive no plano XY (vista de topo); o tubo em volta
        rings.append(ring)
    # simplificacao correta abaixo (descarta o loop acima)
    bm = bmesh.new()
    rings = []
    for k in range(n_seg + 1):
        _a = -math.pi / 2 + math.pi * k / n_seg
        _ax = x_c + r_arco * (1 - math.sin(abs(_a)))   # avanca maximo no centro
        _ay = r_arco * math.cos(_a) * -1               # y do arco
        _x0 = x_c + r_arco * 0.0
        cx_ = x_c + r_arco * math.sin(_a) * 0.0
        # tubo: centro da secao = ponto do arco; raio r_tubo em torno do eixo tangente (que e Z-up)
        cxs = x_c + r_arco * (1 - math.sin(abs(_a)))
        cys = r_arco * math.cos(_a)
        cys = cys if _a > 0 else -cys
        ring = []
        for j in range(14):
            _b = 2 * math.pi * j / 14
            ring.append((cxs + r_tubo * math.cos(_b) * math.sin(_a) ** 0, cys + 0 * _b, z_c + r_tubo * math.sin(_b)))
        rings.append(ring)
    # facear
    for i in range(len(rings) - 1):
        A, B = rings[i], rings[i + 1]
        for j in range(14):
            bm.faces.new((bm.verts.new(A[j]), bm.verts.new(A[(j + 1) % 14]), bm.verts.new(B[(j + 1) % 14]), bm.verts.new(B[j])))
    o = ob(bm, n, m)
    return o
# arco: centro x=1.02, raio 0.50 (bitola 1.0 < rodas 1.13), tubo r=0.045, z centro 0.17
# PARA-CHOQUE GORDO (v058, vision: 70% Lk, h~0.21m, U baixo com caps amarelos)
box("N_GrillBG", 1.160, 1.162, -0.225, 0.225, 0.052, 0.175, m=M_TIRE, bevel=0.004)   # v088: recesso acompanha a grade  # v070: recesso na face do BLOCO (topo 0.15)
loft("F_Bow", [
    (1.175, sec_U(0.500, 0.025, 0.190, p=0.45)),
    (1.155, sec_U(0.492, 0.025, 0.191, p=0.45)),
    (1.120, sec_U(0.470, 0.027, 0.192, p=0.45)),
    (1.060, sec_U(0.420, 0.035, 0.180, p=0.45)),
    (1.000, sec_U(0.340, 0.038, 0.182, p=0.45)),
    (0.980, sec_U(0.300, 0.040, 0.184, p=0.45)),
], M_BODY)  # v071: CINTA CURTA x[0.98..1.175] - fim do trilho longo; base 0.03 < bloco 0.05 (overlap real)
# pads amarelos nas pontas do arco
for sgn in (+1, -1):
    box("F_Pad_%d" % sgn, 0.680, 0.855, sgn * 0.150, sgn * 0.490, 0.075, 0.245, m=M_ACC, bevel=0.030)  # v074: SECAO larga (vision lia esfera como FAROL)
# bracos do arco ate o nariz
for sgn in (+1, -1):
    box("F_ArmU_%d" % sgn, 0.630, 0.98, sgn * 0.130, sgn * 0.46, 0.035, 0.135, m=M_METAL, bevel=0.012)  # v072: EMBUTIDO na cinta (fim do trilho solto)
# ---------- PODS (entre os eixos, baixos) ----------
# SIDEPOD em GOTA 3D (v024): loft com ombro arredondado — o cowl provou que elipse leitura
# v025 TRAVA DIMENSIONAL (TOP do concept): pod max |y|=0.50 (nao 0.72!) e topo 0.44 (nao 0.51)
# v060 GOTA GORDA (vision side: x[+0.45..-0.50] z[0.12..0.44], frente cunha, tras redonda alta)
# v066 GOTa ASSIMETRICA (vision: "frente fina, TRASEIRA ALTA redonda" — topo sobe ate' atras)
_PY = 0.73   # v088: pods contidos (concept TOP: corpo 0.938 m; o modelo tinha 1.17 m)
POD = [(0.45, 0.140 * _PY, 0.230, 0.300), (0.34, 0.260 * _PY, 0.180, 0.360), (0.18, 0.360 * _PY, 0.150, 0.415),
       (0.00, 0.415 * _PY, 0.135, 0.445), (-0.20, 0.430 * _PY, 0.130, 0.470), (-0.38, 0.400 * _PY, 0.135, 0.490), (-0.50, 0.300 * _PY, 0.155, 0.465)]
for sgn in (+1, -1):
    pts = [(x, [(sgn * y, z) for (y, z) in anel(0.155, yo, zb, zt, py=0.72, pz=0.62, n=18)]) for (x, yo, zb, zt) in POD]
    loft("Sidepod_%s" % ("L" if sgn > 0 else "R"), pts, M_ACC)
    # v100: OMBRO de transicao cockpit->tanque (o crop A/B apontou "salto de altura/fenda")
    box("Shld_%s" % ("L" if sgn > 0 else "R"), -0.220, 0.100, sgn * 0.158, sgn * 0.300,
        0.500, 0.600, m=M_BODY, bevel=0.020)
    # v099: faixa azul no TOPO do pod (concept: azul = espinha dorsal sobre os tanques)
    for _pb, (_px0, _px1, _pyo, _pzb, _pzt) in enumerate((
            (0.250, 0.400, 0.205, 0.262, 0.335),
            (-0.050, 0.200, 0.278, 0.352, 0.438),
            (-0.350, -0.050, 0.302, 0.412, 0.498))):
        box("PodBlue_%s_%d" % ("L" if sgn > 0 else "R", _pb), _px0, _px1,
            sgn * (_pyo - 0.072), sgn * (_pyo + 0.072), _pzb, _pzt, m=M_BODY, bevel=0.012)
print("###W34### 2 pods")

box("Floor", -1.01, 0.86, -0.27, 0.27, 0.055, 0.085, m=M_WHITE, bevel=0.006)
for sgn in (+1, -1):
    box("PodSup_%d" % sgn, -0.32, -0.20, sgn * 0.170, sgn * 0.330, 0.078, 0.205, m=M_METAL, bevel=0.008)
box("CowlWall", 0.28, 0.80, -0.185, 0.185, 0.075, 0.240, m=M_BODY, bevel=0.010)  # parede do cowl ate o assoalho
for sgn in (+1, -1):
    cil("Chassis_%d" % sgn, 0.30, sgn * 0.205, 0.235, 0.055, 1.62, rot=(0, math.radians(90), 0), m=M_BODY, v=14, smooth=False)
    cil("ChassisLow_%d" % sgn, 0.30, sgn * 0.205, 0.118, 0.046, 1.55, rot=(0, math.radians(90), 0), m=M_BODY, v=12, smooth=False)

# ---------- MOTOR + 3 ESCAPES ----------
box("R_Motor", -0.90, -0.60, -0.190, 0.190, 0.20, 0.50, m=M_METAL, bevel=0.030)
# ---------- v097: CARENAGEM DO MOTOR (o vision v096: "massa blocky sem refinamento") ----------
for _s3 in (+1, -1):
    esf("R_MCowl_%d" % _s3, (-0.745, _s3 * 0.185, 0.365), 0.185, 0.062, 0.150, m=M_METAL, seg=22)   # lateral da carenagem
esf("R_MCowlTop", (-0.760, 0.0, 0.500), 0.160, 0.180, 0.055, m=M_METAL, seg=22)                      # tampa superior
esf("R_MCowlBack", (-0.560, 0.0, 0.360), 0.055, 0.175, 0.145, m=M_METAL, seg=20)                    # traseira da carenagem
box("R_MFinTop", -0.900, -0.830, -0.022, 0.022, 0.490, 0.560, m=M_ACC, bevel=0.008)                # aleta superior
box("R_MFin_1", -0.880, -0.700, 0.238, 0.268, 0.300, 0.470, m=M_ACC, bevel=0.010)                  # aleta lateral
box("R_MFin_-1", -0.880, -0.700, -0.268, -0.238, 0.300, 0.470, m=M_ACC, bevel=0.010)  # v078: Y +/-0.19 -> toca a longarina
for _k in range(4):
    box("R_Fin%d" % _k, -0.88 + 0.06 * _k, -0.855 + 0.06 * _k, -0.135, 0.135, 0.495, 0.545, m=M_METAL, bevel=0.005)
for _s in (+1, -1):
    cil("R_InT_%d" % _s, -0.72, _s * 0.105, 0.560, 0.028, 0.170, m=M_CHROME, v=14)
# ESCAPES ASSINATURA (v039 real): central GROSSO escuro (medido: boca ~0.23) + 2 laterais finos
cil("R_ExhC", -0.755, 0.0, 0.400, 0.086, 0.535, rot=(0, math.radians(90), 0), m=M_CHROME, v=26)  # v082: maior + protruso (x=-1.02) + agrupado/mais alto
# LATERAIS em V para fora (concept: inclinados para fora) + mais longos para lerem no REAR
cil("R_ExhL_1", -0.735, 0.275, 0.470, 0.066, 0.545, rot=(0, math.radians(90), math.radians(-12)), m=M_CHROME, v=18)  # v082: maior + protruso
cil("R_ExhL_-1", -0.735, -0.275, 0.470, 0.066, 0.545, rot=(0, math.radians(90), math.radians(12)), m=M_CHROME, v=18)
# bocas escavadas (furo): anel preto na ponta de cada escape
cil("R_MouthC", -1.034, 0.0, 0.400, 0.072, 0.030, rot=(0, math.radians(90), 0), m=M_TIRE, v=24)   # v082: boca central maior, na ponta
cil("R_RimC", -1.008, 0.0, 0.400, 0.088, 0.014, rot=(0, math.radians(90), 0), m=M_CHROME, v=26)  # v082: borda prateada da boca
for _s in (+1, -1):
    cil("R_RimL_%d" % _s, -0.978, _s * 0.330, 0.470, 0.074, 0.020, rot=(0, math.radians(90), math.radians(-12 * _s)), m=M_CHROME, v=20)
for _s in (+1, -1):   # v083b: BOCA escura dos laterais (faltava o oco — vision REAR)
    cil("R_MouthL_%d" % _s, -0.992, _s * 0.335, 0.470, 0.052, 0.026, rot=(0, math.radians(90), math.radians(-12 * _s)), m=M_TIRE, v=20)
# ---------- v098: DETALHE REAL DO ESCAPAMENTO (vision v097: "internos sem detalhe") ----------
cil("R_ExhJoinC", -0.862, 0.0, 0.400, 0.099, 0.024, rot=(0, math.radians(90), 0), m=M_CHROME, v=24)      # junta do tubo central
box("R_ExhClampC", -0.880, -0.844, -0.022, 0.022, 0.382, 0.418, m=M_METAL, bevel=0.006)                 # abracadeira
for _s4 in (+1, -1):
    cil("R_ExhJoinL_%d" % _s4, -0.848, _s4 * 0.275, 0.470, 0.079, 0.022,
        rot=(0, math.radians(90), math.radians(-12 * _s4)), m=M_CHROME, v=20)                            # junta lateral
    box("R_ExhClampL_%d" % _s4, -0.868, -0.830, _s4 * 0.252, _s4 * 0.298, 0.452, 0.488, m=M_METAL, bevel=0.006)
box("R_DifBase", -1.055, -0.950, -0.255, 0.255, 0.100, 0.116, m=M_TIRE, bevel=0.004)   # v098b: placa que LIGA os 4 slats (o 3o ficava ilha solta)
for _d in range(4):                                                                                      # slats REAIS no difusor
    box("R_DifSlat%d" % _d, -1.055, -0.955, -0.185 + 0.123 * _d, -0.125 + 0.123 * _d, 0.108, 0.168,
        m=M_TIRE, bevel=0.004)
box("R_HeatShield", -0.845, -0.815, -0.170, 0.170, 0.300, 0.470, m=M_METAL, bevel=0.008)
# ---------- v103: MECANICA PRATEADA EXPOSTA na regiao do meio-alto ----------
# MEDICAO (concept SIDE, meio): topo 0-50% altura = azul 38-42% E CINZA 35-41%; base 75-100% = amarelo 48%.
# O modelo tinha cinza 10% no meio (concept 23%) -> faltava mecanica visivel.
for _s5 in (+1, -1):
    cil("R_Damper_%d" % _s5, -0.585, _s5 * 0.205, 0.480, 0.060, 0.290, rot=(0, 0, 0), m=M_CHROME, v=20)   # amortecedor vertical
    cil("R_DampRod_%d" % _s5, -0.585, _s5 * 0.160, 0.640, 0.016, 0.150, rot=(0, 0, 0), m=M_METAL, v=12)   # haste
box("CH_PlateR", -0.630, -0.420, -0.152, 0.152, 0.205, 0.252, m=M_METAL, bevel=0.008)   # chassi exposto (prata)                # protecao termica
cil("R_CringC", -0.948, 0.000, 0.330, 0.064, 0.022, rot=(0, math.radians(90), 0), m=M_CHROME, v=20)  # v077: aro cromado grosso (le como CANO)  # REGRA 251: boca A FRENTE do motor
cil("R_MouthL_1", -0.955, 0.345, 0.390, 0.044, 0.030, rot=(0, math.radians(90), math.radians(-12)), m=M_TIRE, v=16)
cil("R_CringL_1", -0.948, 0.343, 0.390, 0.056, 0.022, rot=(0, math.radians(90), math.radians(-12)), m=M_CHROME, v=18)  # v073: boca 1.4x
cil("R_MouthL_-1", -0.955, -0.345, 0.390, 0.044, 0.030, rot=(0, math.radians(90), math.radians(12)), m=M_TIRE, v=16)
cil("R_CringL_-1", -0.948, -0.343, 0.390, 0.056, 0.022, rot=(0, math.radians(90), math.radians(12)), m=M_CHROME, v=18)
# DIFUSOR: 5 aletas verticais azuis (medido no REAR concept)
for _k in range(5):
    _yy = -0.10 + 0.05 * _k
    box("R_Dif%d" % _k, -1.02, -0.80, _yy - 0.009, _yy + 0.009, 0.10, 0.26, m=M_TIRE, bevel=0.004)
# v078 (AUDITORIA): conjunto traseiro (motor/escapes/difusor/barra) era ilha com 0.25 m de vao
for _s in (+1, -1):
    cil("Rail_R_%d" % _s, -0.820, _s * 0.205, 0.235, 0.050, 0.680, rot=(0, math.radians(90), 0), m=M_METAL, v=14, smooth=False)
cil("R_BumperBar", -1.139, 0.0, 0.140, 0.038, 1.20, rot=(math.radians(90), 0, 0), m=M_METAL, v=14)  # v082: CINZA tubular (concept) — barra ABAIXO dos escapes
for _s in (+1, -1):   # v082: U-bend — o quadro cinza curva para cima nas duas pontas (concept)
    cil("R_UBend_%d" % _s, -1.139, _s * 0.585, 0.275, 0.038, 0.350, rot=(0, 0, 0), v=14, m=M_METAL)
cil("R_UBendTop", -1.139, 0.0, 0.450, 0.038, 1.170, rot=(math.radians(90), 0, 0), m=M_METAL, v=14)   # v083b: barra SUPERIOR fecha o U (concept)   # v082b: VERTICAL (rot default X90 punha o eixo em Y) e cruzando a barra
box("R_Grille", -1.055, -1.005, -0.330, 0.330, 0.360, 0.560, m=M_TIRE, bevel=0.010)   # v082: painel AZUL acima da barra
for _k in range(5):   # v082: grade (slats verticais) no painel azul
    box("R_GrSlat%d" % _k, -1.078, -0.998, -0.295 + 0.148 * _k, -0.245 + 0.148 * _k, 0.372, 0.548, m=M_METAL, bevel=0.004)   # v083: protrusos 23 mm
box("R_BumpSup_L", -1.12, -0.86, 0.100, 0.160, 0.140, 0.300, m=M_METAL, bevel=0.008)
box("R_BumpSup_R", -1.12, -0.86, -0.160, -0.100, 0.140, 0.300, m=M_METAL, bevel=0.008)

# ---------- ASA (estacoes 86-96% -> x -1.08..-0.85) em 2 PILONES ----------
# ASA TRASEIRA AUTORAL v033: perfil em GOTA — extrusao transversal com bordo arredondado
def perfil_asa(x, zt, corda):
    """secao da asa no plano YZ: gota com bordo de ataque redondo e saida fina."""
    pts=[]
    n=12
    for j in range(n):
        a=2*math.pi*j/n
        yy=0.475*math.cos(a)  # v078 AUDITORIA: concept 0.945-0.9685 m (66-67%W) por 2 metodos; 0.586 era ERRO
        # espessura: maxima na frente (x maior), afinando para tras
        t=(a%(2*math.pi))/(2*math.pi)
        zz=zt - 0.068*abs(math.sin(a))*(1.0-0.55*(1-yy/0.44 if yy>0 else 0))
        pts.append((x, yy, zt if math.sin(a)>0 else zt-0.068))
    return pts
# ASA v034: GOTA REAL — espessura varia DENTRO da secao (bordo 2x a saida) e corda maior
bmA=bmesh.new()
rings=[]
CORDA=0.26
# v119: contorno de LENTE no plano lateral (espessura 0 nas DUAS pontas, maxima no meio) ->
# o vision diz que no concept a asa e' um OVAL ACHATADO (bordas arredondadas), nao uma cunha com aresta
EST=[-0.900,-0.933,-0.967,-1.000,-1.033,-1.067,-1.100,-1.133,-1.160]
for (x) in EST:
    t=(-0.900-x)/CORDA if x<-0.900 else 0.0
    t=min(max(t,0.0),1.0)
    ring=[]
    n=14
    for j in range(n):
        a=2*math.pi*j/n
        yy=0.475*math.cos(a)
        esp=0.105*max(1.0-(2*t-1)**2,0.0)**0.55
        ztop=0.838-0.020*t+0.024*max(1.0-(2*t-1)**2,0.0)**0.55   # v120: topo TAMBEM curvo (lente/folha)
        zz=ztop-esp*0.5*(1.0-math.cos(a))
        ring.append(bmA.verts.new((x, yy, zz)))
    rings.append(ring)
for i in range(len(rings)-1):
    A,B=rings[i],rings[i+1]
    for j in range(14):
        bmA.faces.new((A[j],A[(j+1)%14],B[(j+1)%14],B[j]))
bmA.faces.new(list(reversed(rings[0]))); bmA.faces.new(list(rings[-1]))
o_A=ob(bmA,"R_Wing",M_ACC)  # v112: ASA AMARELA — vision confirma que no concept a asa traseira e a peca AMARELA curva (a leitura invertida do v107 tinha mantido azul)
for sgn in (+1, -1):
    box("R_Endp_%d" % sgn, -1.165, -0.890, sgn * 0.453, sgn * 0.478, 0.70, 0.93, m=M_ACC, bevel=0.006)  # v078: pontas da asa 0.95
    box("R_Pylon_%d" % sgn, -1.075, -0.965, sgn * 0.140, sgn * 0.270, 0.19, 0.86, m=M_METAL, bevel=0.010)  # v078: desce ate a longarina (era ilha)
# ---------- BANCO + PILOTO (capacete centro x=-0.35, estacoes 60-70%) ----------
box("Seat_Back", -0.30, -0.46, -0.145, 0.145, 0.14, 0.62, m=M_SEAT, bevel=0.022)  # reclinado ~40°
box("Seat_Base", -0.48, 0.05, -0.145, 0.145, 0.070, 0.55, m=M_SEAT, bevel=0.015)  # v062: sobe ao torso
# ===== PILOTO v029: CAIXA-ESQUELETO ARTICULADA (regra 231 — retas e angulos, nao blobs) =====
HIP = Vector((-0.26, 0.0, 0.495))  # MANTIDO: concept capacete est 60-65% (perfil) — o erro era o COWL engolindo as pernas            # quadril fixo no banco
def _box_v(n, p0, p1, esp, m, bevel=0.004):
    """caixa orientada de p0 a p1 com espessura esp (retas legiveis)."""
    d = p1 - p0
    L = d.length
    o = box(n, -esp, esp, -esp / 2, esp / 2, 0, L, m=m, bevel=bevel)
    o.location = (p0 + p1) / 2
    o.rotation_euler = d.to_track_quat("Z", "Y").to_euler()
    return o
# tronco: quadril -> ombro, INCLINADO 48° para tras (ombro atras e acima)
# ===== PILOTO v062: forma CHIBI com cadeias ELIPTICAS TAPERED (não caixas) =====
# concept: torso chibi (peito gordo em cima, cintura fina), cabeça dominante, membros tábuas com taper
def _elip_chain(n, joints, radii, m, seg=20):
    """cadeia de elipsoides tapering ao longo de uma articulacao."""
    for i, ((p0, p1), (r0, r1)) in enumerate(zip(joints, radii)):
        d = p1 - p0; L = max(d.length, 1e-4)
        # elipsoide alongado ao longo de d com taper r0->r1
        o = esf("%s_%d" % (n, i), tuple((p0 + p1) / 2), L / 2, min(r0, r1) * 1.4, min(r0, r1), m=m, seg=seg)
        o.rotation_euler = d.to_track_quat("X", "Z").to_euler()
SHO = HIP + Vector((-0.05, 0.0, 0.330))   # v068: ombro a FRENTE (concept ombro x~-0.25; -0.50 = GIR AFA)
HEA = SHO + Vector((0.16, 0.0, 0.2578))  # v068: ombro->cabeca 0.11 ≈ concept 0.10; topo=0.825+0.2578+0.1695=1.2523
# tronco ELIPSE: peito largo cima, cintura fina embaixo — chibi "pear-shape"
TORSO = HIP + (SHO - HIP) * 0.40
_dT = SHO - HIP; _dTn = _dT.normalized()
_oT = esf("P_Torso", tuple(TORSO + Vector((0, 0, 0.02))), _dT.length / 2 + 0.05, 0.126, 0.128, m=M_SUIT, seg=24)   # v097: torso estreitado (era 0.155)   # v066: barril ALINHADO ao tronco deitado
_oT.rotation_euler = _dTn.to_track_quat("X", "Z").to_euler()
esf("P_Waist", tuple(HIP + (SHO - HIP) * 0.75), 0.085, 0.118, 0.105, m=M_SUIT, seg=18)   # v095: cintura estreitada
esf("P_Chest", tuple(HIP + (SHO - HIP) * 0.45), 0.098, 0.152, 0.128, m=M_SUIT, seg=20)      # v095: peito cheio (sueter)     # cintura fina
esf("P_Hips", tuple(HIP + Vector((0, 0, -0.02))), 0.095, 0.165, 0.095, m=M_SUIT, seg=18)   # bacia
# pescoco curto + cabeca GRANDE (chibi: absorve a massa)
# v067h: pescoco ALINHADO p0(dentro do ombro)->p1(dentro do helmet): pontas cruzam as
# superficies dos dois — interseccao BVH garantida em ambos os pares
# v068: pescoco MINIMO — ombro(-0.31,0.835) e cabeca(-0.15,1.083) agora PROXIMOS (gap 4cm)
_oN = esf("P_Neck", (-0.23, 0.0, 0.92), 0.090, 0.075, 0.055, m=M_SUIT, seg=14)
esf("P_Helmet", tuple(HEA + Vector((-0.01, 0, 0.012))), 0.163, 0.170, 0.1575, m=M_HELM, seg=28)  # topo=1.2523
esf("P_Visor", tuple(HEA + Vector((0.086, 0, 0.014))), 0.078, 0.156, 0.082, m=M_VISL, seg=20)   # v086: cinza + acima dos olhos
box("P_Stripe", HEA.x - 0.165, HEA.x + 0.165, -0.026, 0.026, HEA.z + 0.095, HEA.z + 0.152, m=M_ACC, bevel=0.004)
box("P_StripeF", HEA.x + 0.138, HEA.x + 0.176, -0.030, 0.030, HEA.z + 0.052, HEA.z + 0.148, m=M_ACC, bevel=0.008)   # v086: NA CASCA frontal, acima dos olhos   # v085: faixa desce pela FRENTE do capacete
# membros ELIPTICOS com taper: coxa gorda -> canela fina -> pe
KNE = HIP + Vector((0.42, 0.0, 0.08)); FOO = KNE + Vector((0.34, 0.0, -0.30))
ELB = SHO + Vector((0.21, 0.0, -0.25))   # v076: braco RELAXADO (vision: rigido)
WHE = Vector((0.35, 0.0, 0.62))           # volante
for sgn in (+1, -1):
    # coxa GORDA: taper 0.13 -> 0.075
    _elip_chain("P_Thigh_%d" % sgn, [(HIP + Vector((0, sgn * 0.09, 0)), KNE + Vector((0, sgn * 0.09, 0)))], [(0.130, 0.075)], M_SUIT, 18)
    # canela FINA: taper 0.075 -> 0.055
    _elip_chain("P_Shin_%d" % sgn, [(KNE + Vector((0, sgn * 0.085, 0)), FOO + Vector((0, sgn * 0.085, 0)))], [(0.072, 0.054)], M_SUIT, 16)
    # bota: pe GORDO na frente
    esf("P_Boot_%d" % sgn, tuple(FOO + Vector((0.10, sgn * 0.085, 0))), 0.155, 0.050, 0.045, m=M_VIS, seg=14)
    # braco: taper 0.09 -> 0.065
    _elip_chain("P_Arm_%d" % sgn, [(SHO + Vector((0, sgn * 0.17, 0)), ELB + Vector((0, sgn * 0.14, 0)))], [(0.088, 0.066)], M_SUIT, 16)
    # antebraco: taper 0.065 -> 0.050, ate a mao no volante
    _elip_chain("P_Fore_%d" % sgn, [(ELB + Vector((0, sgn * 0.14, 0)), WHE + Vector((0, sgn * 0.09, 0.02)))], [(0.064, 0.048)], M_SUIT, 14)
# ombreira amarela (concept: "ombreira amarela")
esf("P_Shoulder", tuple(SHO + Vector((-0.02, 0, 0.01))), 0.140, 0.222, 0.082, m=M_ACC, seg=20)   # v097: ombros 0.255->0.222
# ---------- v095: CAPACETE AERODINAMICO (crista + spoiler) ----------
# O vision (v094): "o capacete e' uma esfera simples com estampilha, nao replica o desenho
# aerodinamico do concept". O concept tem crista central no topo e spoiler na nuca.
# ---------- v096: AERO FRONTAL (ducos/defletores amarelos ladeando o nariz) ----------
# vision v095: "concept tem asa/ductos amarelos distintos; a aero frontal do modelo esta subdefinida"
for _s2 in (+1, -1):
    # v096b: atravessa o nariz (y desde 0.060=DENTRO) para garantir contato — antes comecava em 0.135 e ficava ilha
    # v096c: N_Nose termina em z=0.279 (medido) — o ducto em z 0.300-0.352 flutuava 2 cm acima
    box("F_Aero_%d" % _s2, 0.870, 1.090, _s2 * 0.055, _s2 * 0.330, 0.240, 0.292,
        m=M_ACC, bevel=0.016)
    box("F_AeroTip_%d" % _s2, 0.975, 1.075, _s2 * 0.318, _s2 * 0.392, 0.252, 0.284,
        m=M_ACC, bevel=0.010)

box("P_HCrest", HEA.x - 0.145, HEA.x + 0.085, -0.038, 0.038, HEA.z + 0.118, HEA.z + 0.169,
    m=M_ACC, bevel=0.014)   # v096: crista ALARGADA (0.038) — com 0.020 sumia na vista TOP
box("P_HSpoil", HEA.x - 0.185, HEA.x - 0.125, -0.070, 0.070, HEA.z - 0.055, HEA.z + 0.055,
    m=M_ACC, bevel=0.014)   # spoiler/carenagem na nuca
esf("P_HVent", tuple(HEA + Vector((0.120, 0, 0.075))), 0.030, 0.055, 0.022, m=M_VISL, seg=14)  # tomada de ar
# VOLANTE TORO 3D v033: tubo circular (nao anel plano)
bmT=bmesh.new()
segs=18
ring_pts=[]
for j in range(segs):
    a=2*math.pi*j/segs
    ring_pts.append((0.30+0.098*math.cos(a), 0.098*math.sin(a), 0.648))
ringsW=[]
_ang=math.radians(-25); _ca,_sa=math.cos(_ang),math.sin(_ang)
for dz in (-0.028, 0.028):
    rw=[]
    for j in range(segs):
        a=2*math.pi*j/segs
        _yv=0.1225*math.sin(a); _xv=0.30+0.1225*math.cos(a)
        rw.append(bmT.verts.new((_xv, _yv*_ca-dz*_sa, 0.648+_yv*_sa+dz*_ca)))
    ringsW.append(rw)
for j in range(segs):
    bmT.faces.new((ringsW[0][j],ringsW[0][(j+1)%segs],ringsW[1][(j+1)%segs],ringsW[1][j]))
bmT.faces.new(list(reversed(ringsW[0]))); bmT.faces.new(list(ringsW[1]))   # v079: tampar (era casca aberta)
# v077: 3 RAIOS do volante (vision: "spokeless steering wheel") — laminas no plano inclinado
for _k in range(3):
    _th=2*math.pi*_k/3.0
    _px,_py=math.cos(_th),math.sin(_th)
    _qx,_qy=-math.sin(_th),math.cos(_th)
    _ra=0.030; _rb=0.1225
    _ny,_nz=-_sa,_ca            # normal do plano do anel (dava espessura -> prisma fechado)
    _cam=[]
    for _d in (+1,-1):
        _q=[]
        for (_r,_sg) in ((_ra,+1),(_ra,-1),(_rb,-1),(_rb,+1)):
            _vx=0.30+_px*_r+_qx*_sg*0.011
            _vy=_py*_r+_qy*_sg*0.011
            _wz=0.648+_vy*_sa
            _wy=_vy*_ca
            _q.append(bmT.verts.new((_vx,_wy+_d*_ny*0.004,_wz+_d*_nz*0.004)))
        _cam.append(_q)
    _A,_B=_cam[0],_cam[1]
    bmT.faces.new(_A); bmT.faces.new(list(reversed(_B)))     # v080: PRISMA (era lamina de 1 face = boundary)
    for _j in range(4):
        _j2=(_j+1)%4
        bmT.faces.new((_A[_j],_A[_j2],_B[_j2],_B[_j]))
o_W=ob(bmT,"P_Wheel",M_METAL)
esf("P_Hub", (0.30, 0.0, 0.655), 0.052, 0.052, 0.018, m=M_ACC, seg=18)
# v078 (AUDITORIA): boca/olhos 27 mm A FRENTE do capacete = ilhas soltas. Face-plate liga tudo.
box("P_FacePlate", -0.040, 0.010, -0.108, 0.108, 0.995, 1.142, m=M_VIS, bevel=0.010)   # v085: recuada (antes cobria os olhos)
# v076: MOLAS AMARELAS sobre o eixo traseiro (concept SIDE) — visiveis acima do pneu (z>0.33)
for _s in (+1, -1):
    cil("R_Spring_%d" % _s, -0.820, _s * 0.285, 0.3400, 0.058, 0.330, rot=(0, 0, 0), m=M_CHROME, v=16)  # v079: VERTICAL (default era deitado) z 0.175..0.505
    cil("R_SprD1_%d" % _s, -0.820, _s * 0.285, 0.255, 0.049, 0.020, rot=(0, 0, 0), m=M_ACC, v=16)
    cil("R_SprD2_%d" % _s, -0.820, _s * 0.285, 0.470, 0.049, 0.020, rot=(0, 0, 0), m=M_ACC, v=16)
# v076: LUVAS do piloto no volante (concept: "hands with gloves visible")
for _s in (+1, -1):
    esf("P_Glove_%d" % _s, (0.35, _s * 0.095, 0.630), 0.058, 0.052, 0.052, m=M_ACC, seg=16)
# v075: FACE CARTOON (gap nomeado pelo vision: "simplified non-cartoon driver face")
# frente do visor (x>0.018), zona z[0.98..1.17]; olhos brancos com pupila + sorriso em arco
for _s in (+1, -1):
    esf("P_Eye_%d" % _s, (0.045, _s * 0.062, 1.118), 0.038, 0.038, 0.038, m=M_WHITE, seg=18)   # v085: maiores + à frente da placa
    esf("P_Pup_%d" % _s, (0.072, _s * 0.062, 1.116), 0.021, 0.021, 0.021, m=M_TIRE, seg=14)
box("P_Mouth_M", 0.000, 0.082, -0.042, 0.042, 0.998, 1.014, m=M_TIRE, bevel=0.006)   # v085: sorriso mais largo
for _s in (+1, -1):
    box("P_Mouth_%d" % _s, 0.000, 0.082, _s * 0.042, _s * 0.074, 1.006, 1.024, m=M_TIRE, bevel=0.006)
for sgn in (+1,-1):
    esf("P_Grip_%d" % sgn, (0.30, sgn*0.104, 0.655), 0.030, 0.022, 0.022, m=M_VIS, seg=12)
box("P_Dash", 0.150, 0.235, -0.105, 0.105, 0.600, 0.700, m=M_WHITE, bevel=0.010)
esf("P_KneeL", (0.055, +0.082, 0.560), 0.078, 0.075, 0.078, m=M_SUIT, seg=18)
esf("P_KneeR", (0.055, -0.082, 0.560), 0.078, 0.075, 0.078, m=M_SUIT, seg=18)
print("###W34### banco + piloto (capacete x=-0.35)")

bpy.context.view_layer.update()
mins = [1e9] * 3; maxs = [-1e9] * 3
for o in sc.objects:
    if o.type != "MESH": continue
    for c in o.bound_box:
        w = o.matrix_world @ Vector(c)
        for i in range(3):
            mins[i] = min(mins[i], w[i]); maxs[i] = max(maxs[i], w[i])
print("###W34### BBOX X %.3f..%.3f (L=%.3f | alvo 2.350) | Y %.3f..%.3f (W=%.3f | alvo 1.4411) | Z %.3f..%.3f (H=%.3f | alvo 1.2523)" % (
    mins[0], maxs[0], maxs[0] - mins[0], mins[1], maxs[1], maxs[1] - mins[1], mins[2], maxs[2], maxs[2] - mins[2]))
print("###W34### objetos: %d" % len([o for o in sc.objects if o.type == "MESH"]))

# ---------- v090: ACABAMENTO ORGANICO (lista branca: so' superficie visivel) ----------
# v089 tentou por prefixo e subdividiu pecas ESTRUTURAIS (PodSup, Rail, R_BumpSup, R_Spring):
# elas encolheram, perderam contato (30/34) e criaram 2 componentes. Agora: lista explicita.
_VISIVEIS = ('P_Helmet', 'P_Torso', 'P_Neck', 'P_Shoulder', 'Sidepod_L', 'Sidepod_R')
_tot = 0
for _n in _VISIVEIS:
    o = bpy.data.objects.get(_n)
    if not o or o.type != 'MESH':
        continue
    try:
        md = o.modifiers.new('ss', 'SUBSURF')
        md.levels = 2
        md.render_levels = 2
        bpy.context.view_layer.objects.active = o
        bpy.ops.object.modifier_apply(modifier='ss')
        bpy.ops.object.shade_smooth()
        _tot += 1
    except Exception as _e:
        print('###W90### subsurf falhou em', _n, _e)
print('###W90### subsurf aplicado em', _tot, 'pecas visiveis')

bpy.ops.wm.save_as_mainfile(filepath=MD + "authored/conjunto-v120.blend")
# REGRA 230: verificar no ARTEFATO
chk = [o.name for o in bpy.data.objects if o.name.startswith('R_ExhC') or o.name.startswith('R_Dif') or o.name.startswith('N_Grill')]
print('###V39CHK### escapes/difusor no blend:', chk)
print("###W34### salvo")
