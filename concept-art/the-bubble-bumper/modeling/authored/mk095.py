s = open('/tmp/v094.py').read()

# (1) CINTURA: o vision pede a curvatura do sueter azul (cintura mais estreita que os ombros)
old = 'esf("P_Waist", tuple(HIP + (SHO - HIP) * 0.75), 0.085, 0.145, 0.115, m=M_SUIT, seg=18)'
new = ('esf("P_Waist", tuple(HIP + (SHO - HIP) * 0.75), 0.085, 0.118, 0.105, m=M_SUIT, seg=18)   # v095: cintura estreitada\n'
       'esf("P_Chest", tuple(HIP + (SHO - HIP) * 0.45), 0.098, 0.152, 0.128, m=M_SUIT, seg=20)      # v095: peito cheio (sueter)')
assert old in s, 'cintura'
s = s.replace(old, new)

# (2) CAPACETE: crista + spoiler traseiro (o concept tem desenho aerodinamico, nao uma esfera lisa)
old2 = 'esf("P_Shoulder", tuple(SHO + Vector((-0.02, 0, 0.01))), 0.145, 0.255, 0.085, m=M_ACC, seg=20)'
new2 = old2 + '''
# ---------- v095: CAPACETE AERODINAMICO (crista + spoiler) ----------
# O vision (v094): "o capacete e' uma esfera simples com estampilha, nao replica o desenho
# aerodinamico do concept". O concept tem crista central no topo e spoiler na nuca.
box("P_HCrest", HEA.x - 0.130, HEA.x + 0.075, -0.020, 0.020, HEA.z + 0.130, HEA.z + 0.172,
    m=M_ACC, bevel=0.012)   # crista central no topo do capacete
box("P_HSpoil", HEA.x - 0.185, HEA.x - 0.125, -0.070, 0.070, HEA.z - 0.055, HEA.z + 0.055,
    m=M_ACC, bevel=0.014)   # spoiler/carenagem na nuca
esf("P_HVent", tuple(HEA + Vector((0.120, 0, 0.075))), 0.030, 0.055, 0.022, m=M_VISL, seg=14)  # tomada de ar'''
assert old2 in s, 'capacete'
s = s.replace(old2, new2)
s = s.replace('conjunto-v094.blend', 'conjunto-v095.blend')
open('/tmp/v095.py', 'w').write(s)
print('v095.py OK: crista + spoiler do capacete + peito/cintura')
