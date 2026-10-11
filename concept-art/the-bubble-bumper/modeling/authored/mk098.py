s = open('/tmp/v097.py').read()

# v098 — REAR era 7,0: "escapamento/internos sem detalhe". Adicionar juntas, abracadeiras e
# slats reais no difusor (sem ocluir as bocas em x=-0.948).
old = 'cil("R_CringC", -0.948, 0.000, 0.330, 0.064, 0.022, rot=(0, math.radians(90), 0), m=M_CHROME, v=20)'
new = '''# ---------- v098: DETALHE REAL DO ESCAPAMENTO (vision v097: "internos sem detalhe") ----------
cil("R_ExhJoinC", -0.862, 0.0, 0.400, 0.099, 0.024, rot=(0, math.radians(90), 0), m=M_CHROME, v=24)      # junta do tubo central
box("R_ExhClampC", -0.880, -0.844, -0.022, 0.022, 0.382, 0.418, m=M_METAL, bevel=0.006)                 # abracadeira
for _s4 in (+1, -1):
    cil("R_ExhJoinL_%d" % _s4, -0.848, _s4 * 0.275, 0.470, 0.079, 0.022,
        rot=(0, math.radians(90), math.radians(-12 * _s4)), m=M_CHROME, v=20)                            # junta lateral
    box("R_ExhClampL_%d" % _s4, -0.868, -0.830, _s4 * 0.252, _s4 * 0.298, 0.452, 0.488, m=M_METAL, bevel=0.006)
for _d in range(4):                                                                                      # slats REAIS no difusor
    box("R_DifSlat%d" % _d, -1.055, -1.020, -0.185 + 0.123 * _d, -0.125 + 0.123 * _d, 0.108, 0.168,
        m=M_TIRE, bevel=0.004)
box("R_HeatShield", -0.845, -0.815, -0.170, 0.170, 0.300, 0.470, m=M_METAL, bevel=0.008)                # protecao termica
cil("R_CringC", -0.948, 0.000, 0.330, 0.064, 0.022, rot=(0, math.radians(90), 0), m=M_CHROME, v=20)'''
assert old in s, 'anchor escape'
s = s.replace(old, new, 1)
s = s.replace('conjunto-v097.blend', 'conjunto-v098.blend')
open('/tmp/v098.py', 'w').write(s)
print('v098.py OK: juntas + abracadeiras + slats do difusor + protecao termica')
