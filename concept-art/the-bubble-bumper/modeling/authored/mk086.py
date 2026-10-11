s = open('/tmp/v085.py').read()

# (1) FAIXA FRONTAL do capacete: tinha ficado DENTRO da casca (invisivel). Agora FINA, na superficie frontal.
s = s.replace('box("P_StripeF", HEA.x + 0.045, HEA.x + 0.185, -0.028, 0.028, HEA.z - 0.045, HEA.z + 0.120, m=M_ACC, bevel=0.006)',
              'box("P_StripeF", HEA.x + 0.138, HEA.x + 0.176, -0.030, 0.030, HEA.z + 0.052, HEA.z + 0.148, m=M_ACC, bevel=0.008)   # v086: NA CASCA frontal, acima dos olhos')

# (2) VISOR perceptivel: material cinza medio (era escuro e sumia) + envolve a area dos olhos
s = s.replace('M_VIS= mat("Visor_Dark", (0.055, 0.06, 0.085), 0.65)',
              'M_VIS= mat("Visor_Dark", (0.055, 0.06, 0.085), 0.65)\nM_VISL = mat("Visor_Grey", (0.30, 0.33, 0.37), 0.35)   # v086: visor cinza perceptivel (concept tem visor cinza claro)')
s = s.replace('esf("P_Visor", tuple(HEA + Vector((0.098, 0, -0.010))), 0.070, 0.150, 0.095, m=M_VIS, seg=20)',
              'esf("P_Visor", tuple(HEA + Vector((0.086, 0, 0.014))), 0.078, 0.156, 0.082, m=M_VISL, seg=20)   # v086: cinza + acima dos olhos')

s = s.replace('conjunto-v085.blend', 'conjunto-v086.blend')
open('/tmp/v086.py', 'w').write(s)
print('v086.py OK: faixa frontal na casca + visor cinza')
