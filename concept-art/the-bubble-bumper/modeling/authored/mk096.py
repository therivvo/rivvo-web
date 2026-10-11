s = open('/tmp/v095.py').read()

# (1) CRISTA visivel no TOP: estava fina (y +-0.020) -> alargar para +-0.038 e alongar
old = '''box("P_HCrest", HEA.x - 0.130, HEA.x + 0.075, -0.020, 0.020, HEA.z + 0.127, HEA.z + 0.169,
    m=M_ACC, bevel=0.012)   # crista central no topo do capacete'''
new = '''box("P_HCrest", HEA.x - 0.145, HEA.x + 0.085, -0.038, 0.038, HEA.z + 0.118, HEA.z + 0.169,
    m=M_ACC, bevel=0.014)   # v096: crista ALARGADA (0.038) — com 0.020 sumia na vista TOP'''
assert old in s, 'crista'
s = s.replace(old, new)

# (2) AERO FRONTAL amarela (asa/ductos) do concept — o vision pede em v095
old2 = 'box("P_HCrest"'
new2 = '''# ---------- v096: AERO FRONTAL (ducos/defletores amarelos ladeando o nariz) ----------
# vision v095: "concept tem asa/ductos amarelos distintos; a aero frontal do modelo esta subdefinida"
for _s2 in (+1, -1):
    box("F_Duct_%d" % _s2, 0.905, 1.090, _s2 * 0.135, _s2 * 0.330, 0.300, 0.352,
        m=M_ACC, bevel=0.018)    # defletor/asa lateral
    box("F_WingTip_%d" % _s2, 0.985, 1.075, _s2 * 0.330, _s2 * 0.392, 0.312, 0.344,
        m=M_ACC, bevel=0.012)    # ponta da asa
box("F_DuctBar", 0.930, 0.975, -0.135, 0.135, 0.310, 0.346, m=M_BODY, bevel=0.014)  # barra central

box("P_HCrest"'''
assert old2 in s, 'ancora aero'
s = s.replace(old2, new2, 1)
s = s.replace('conjunto-v095.blend', 'conjunto-v096.blend')
open('/tmp/v096.py', 'w').write(s)
print('v096.py OK: crista alargada + aero frontal amarela')
