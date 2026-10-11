s = open('/tmp/v096.py').read()

# (1) MOTOR: o vision (SIDE) ve' "massa blocky sem refinamento". Dar carenagem orgânica ao redor
# do bloco, SEM cobrir as bocas dos escapes (x=-0.948) nem o topo dos tubos.
old = 'box("R_Motor", -0.90, -0.60, -0.190, 0.190, 0.20, 0.50, m=M_METAL, bevel=0.030)'
new = old + '''
# ---------- v097: CARENAGEM DO MOTOR (o vision v096: "massa blocky sem refinamento") ----------
for _s3 in (+1, -1):
    esf("R_MCowl_%d" % _s3, (-0.745, _s3 * 0.185, 0.365), 0.185, 0.062, 0.150, m=M_BODY, seg=22)   # lateral da carenagem
esf("R_MCowlTop", (-0.760, 0.0, 0.500), 0.160, 0.180, 0.055, m=M_BODY, seg=22)                      # tampa superior
esf("R_MCowlBack", (-0.560, 0.0, 0.360), 0.055, 0.175, 0.145, m=M_BODY, seg=20)                    # traseira da carenagem
box("R_MFinTop", -0.900, -0.830, -0.022, 0.022, 0.490, 0.560, m=M_ACC, bevel=0.008)                # aleta superior
box("R_MFin_1", -0.880, -0.700, 0.238, 0.268, 0.300, 0.470, m=M_ACC, bevel=0.010)                  # aleta lateral
box("R_MFin_-1", -0.880, -0.700, -0.268, -0.238, 0.300, 0.470, m=M_ACC, bevel=0.010)'''
assert old in s, 'motor'
s = s.replace(old, new)

# (2) TORSO: vision (FRONT): "overly wide and shapeless, quebra a silhueta compacta do concept"
s = s.replace('_dT.length / 2 + 0.05, 0.155, 0.135, m=M_SUIT, seg=24)',
              '_dT.length / 2 + 0.05, 0.126, 0.128, m=M_SUIT, seg=24)   # v097: torso estreitado (era 0.155)')
s = s.replace('esf("P_Shoulder", tuple(SHO + Vector((-0.02, 0, 0.01))), 0.145, 0.255, 0.085, m=M_ACC, seg=20)',
              'esf("P_Shoulder", tuple(SHO + Vector((-0.02, 0, 0.01))), 0.140, 0.222, 0.082, m=M_ACC, seg=20)   # v097: ombros 0.255->0.222')
s = s.replace('conjunto-v096.blend', 'conjunto-v097.blend')
open('/tmp/v097.py', 'w').write(s)
print('v097.py OK: carenagem do motor + torso/ombros estreitados')
