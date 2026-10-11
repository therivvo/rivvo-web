s = open('/tmp/v087.py').read()

# (1) GRADE FRONTAL: medido 8.7% de W (concept 30-35%) -> 9 slats cobrindo 0.42 m = 29% W
old = '''for _g in range(5):
    _gy = -0.052 + 0.026 * _g
    box("N_Grill%d" % _g, 1.162, 1.178, _gy - 0.011, _gy + 0.011, 0.06, 0.15, m=M_TIRE, bevel=0.002)  # v070: grade na face do bloco (regra 251)'''
new = '''for _g in range(9):   # v088: GRADE LARGA — medido 8.7% de W no v087 vs 30-35% no concept
    _gy = -0.200 + 0.050 * _g
    box("N_Grill%d" % _g, 1.162, 1.178, _gy - 0.011, _gy + 0.011, 0.055, 0.170, m=M_TIRE, bevel=0.002)
for _s in (+1, -1):   # v088: blocos AMARELOS arredondados ladeando a grade (concept)
    box("N_BumpCap_%d" % _s, 1.150, 1.176, _s * 0.225, _s * 0.360, 0.050, 0.180, m=M_ACC, bevel=0.020)'''
assert old in s, 'grade'
s = s.replace(old, new)
s = s.replace('box("N_GrillBG", 1.160, 1.162, -0.150, 0.150, 0.06, 0.15, m=M_TIRE, bevel=0.004)',
              'box("N_GrillBG", 1.160, 1.162, -0.225, 0.225, 0.052, 0.175, m=M_TIRE, bevel=0.004)   # v088: recesso acompanha a grade')

# (2) PODS: medido no concept TOP = 0.938 m de largura de corpo; o modelo tem 1.17 m -> estreitar 27%
old2 = '''POD = [(0.45, 0.140, 0.230, 0.300), (0.34, 0.260, 0.180, 0.360), (0.18, 0.360, 0.150, 0.415),
       (0.00, 0.415, 0.135, 0.445), (-0.20, 0.430, 0.130, 0.470), (-0.38, 0.400, 0.135, 0.490), (-0.50, 0.300, 0.155, 0.465)]'''
new2 = '''_PY = 0.73   # v088: pods contidos (concept TOP: corpo 0.938 m; o modelo tinha 1.17 m)
POD = [(0.45, 0.140 * _PY, 0.230, 0.300), (0.34, 0.260 * _PY, 0.180, 0.360), (0.18, 0.360 * _PY, 0.150, 0.415),
       (0.00, 0.415 * _PY, 0.135, 0.445), (-0.20, 0.430 * _PY, 0.130, 0.470), (-0.38, 0.400 * _PY, 0.135, 0.490), (-0.50, 0.300 * _PY, 0.155, 0.465)]'''
assert old2 in s, 'pods'
s = s.replace(old2, new2)

s = s.replace('conjunto-v087.blend', 'conjunto-v088.blend')
open('/tmp/v088.py', 'w').write(s)
print('v088.py OK: grade 29% W + caps amarelos | pods estreitados (0.73x)')
