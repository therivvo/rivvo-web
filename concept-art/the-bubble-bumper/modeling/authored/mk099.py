s = open('/tmp/v098.py').read()

# v099 — TOP: o crop A/B mostrou "no concept o AZUL e' espinha dorsal continua cobrindo o TOPO dos
# tanques laterais; no modelo o centro/topos sao blocos amarelos rigidos desalinhados".
# FIX: faixa azul (M_BODY) dorsal ao longo do topo de cada pod, acompanhando a curva do sidepod.
old = 'loft("Sidepod_%s" % ("L" if sgn > 0 else "R"), pts, M_ACC)'
new = old + '''
    # v099: faixa azul no TOPO do pod (concept: azul = espinha dorsal sobre os tanques)
    for _pb, (_px0, _px1, _pyo, _pzb, _pzt) in enumerate((
            (0.250, 0.400, 0.205, 0.262, 0.335),
            (-0.050, 0.200, 0.278, 0.352, 0.438),
            (-0.350, -0.050, 0.302, 0.412, 0.498))):
        box("PodBlue_%s_%d" % ("L" if sgn > 0 else "R", _pb), _px0, _px1,
            sgn * (_pyo - 0.072), sgn * (_pyo + 0.072), _pzb, _pzt, m=M_BODY, bevel=0.012)'''
assert old in s, 'sidepod anchor'
s = s.replace(old, new, 1)
s = s.replace('conjunto-v098.blend', 'conjunto-v099.blend')
open('/tmp/v099.py', 'w').write(s)
print('v099.py OK: faixa azul dorsal nos pods (3 blocos por lado)')
