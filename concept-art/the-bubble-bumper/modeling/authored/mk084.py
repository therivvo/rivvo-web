s = open('/tmp/v083.py').read()

# (1) BOCAS ESCURAS nos escapamentos LATERAIS (concept: os 3 tem oco escuro visivel)
old = '''for _s in (+1, -1):
    cil("R_RimL_%d" % _s, -0.978, _s * 0.330, 0.415, 0.074, 0.020, rot=(0, math.radians(90), math.radians(-12 * _s)), m=M_CHROME, v=20)'''
new = old + '''
for _s in (+1, -1):   # v083b: BOCA escura dos laterais (faltava o oco — vision REAR)
    cil("R_MouthL_%d" % _s, -0.992, _s * 0.335, 0.415, 0.052, 0.026, rot=(0, math.radians(90), math.radians(-12 * _s)), m=M_TIRE, v=20)'''
assert old in s, 'riml'
s = s.replace(old, new)

# (2) BARRA SUPERIOR do quadro (concept: U envolvendo o painel, nao so' barra reta)
old2 = '''for _s in (+1, -1):   # v082: U-bend — o quadro cinza curva para cima nas duas pontas (concept)
    cil("R_UBend_%d" % _s, -1.139, _s * 0.585, 0.275, 0.038, 0.350, rot=(0, 0, 0), v=14, m=M_METAL)'''
new2 = old2 + '''
cil("R_UBendTop", -1.139, 0.0, 0.450, 0.038, 1.170, rot=(math.radians(90), 0, 0), m=M_METAL, v=14)   # v083b: barra SUPERIOR fecha o U (concept)'''
assert old2 in s, 'ubend'
s = s.replace(old2, new2)

# (3) PNEU TRASEIRO maior (concept: pneus dominantes vs corpo) — largura p/ dentro, W segue 1.4411
s = s.replace('("RL", XR, +0.5780, 0.165, 0.285), ("RR", XR, -0.5780, 0.165, 0.285))',
              '("RL", XR, +0.5600, 0.1775, 0.320), ("RR", XR, -0.5600, 0.1775, 0.320))')
# o eixo traseiro sobe junto (o pneu cresce p/ cima: centro z = r)
s = s.replace('cil("AXL_R_%d" % _s, XR, _s * 0.41, 0.165, 0.032, 0.58,', 'cil("AXL_R_%d" % _s, XR, _s * 0.41, 0.1775, 0.032, 0.58,')

s = s.replace('conjunto-v083.blend', 'conjunto-v084.blend')
open('/tmp/v084.py', 'w').write(s)
print('v084.py OK: bocas laterais | barra superior do U | pneu traseiro 0.355x0.320')
