# -*- coding: utf-8 -*-
"""v079: fecha os contatos que o gate2 apontou (eixos x aro, strut x chassi, mola x eixo, boca x placa)."""
s = open('/tmp/v078.py').read()

# 1+2) EIXOS mais longos: precisam ALCANCAR o aro (o pneu e' anel — o eixo passa pelo furo)
old = '''        cil("AXL_%s_%d" % (_tag, _s), _x, _s * 0.40, _r, 0.030, 0.52, v=16, smooth=False)   # eixo (default rot X90 -> ao longo de Y)
        box("HUBST_%s_%d" % (_tag, _s), _x - 0.055, _x + 0.055, _s * 0.50, _s * 0.62, _r - 0.055, _r + 0.055,
            m=M_METAL, bevel=0.012)                                                          # stub do cubo (visivel no SIDE)'''
new = '''        if _tag == "F":
            cil("AXL_F_%d" % _s, _x, _s * 0.400, _r, 0.030, 0.620, v=16, smooth=False)   # y 0.09..0.71 -> alcanca o RIM diant.
            box("STRUT_F_%d" % _s, _x - 0.045, _x + 0.045, _s * 0.150, _s * 0.260, 0.115, 0.245, m=M_METAL, bevel=0.010)
        else:
            cil("AXL_R_%d" % _s, _x, _s * 0.410, _r, 0.032, 0.580, v=16, smooth=False)   # y 0.12..0.70 -> alcanca o RIM tras.
        box("HUBST_%s_%d" % (_tag, _s), _x - 0.055, _x + 0.055, _s * 0.50, _s * 0.62, _r - 0.055, _r + 0.055,
            m=M_METAL, bevel=0.012)                                                          # stub do cubo (visivel no SIDE)'''
assert old in s, 'eixos'
s = s.replace(old, new)

# 3) MOLAS VERTICAIS (o default de cil e' rot X90 -> estavam DEITADAS) — descem ate o eixo
s = s.replace('    cil("R_Spring_%d" % _s, -0.820, _s * 0.285, 0.3375, 0.034, 0.325, m=M_ACC, v=14)  # v078: desce ate o eixo (z 0.175..0.50)',
              '    cil("R_Spring_%d" % _s, -0.820, _s * 0.285, 0.3400, 0.036, 0.330, rot=(0, 0, 0), m=M_ACC, v=16)  # v079: VERTICAL (default era deitado) z 0.175..0.505')
s = s.replace('    cil("R_SprD1_%d" % _s, -0.820, _s * 0.285, 0.365, 0.047, 0.020, m=M_ACC, v=16)',
              '    cil("R_SprD1_%d" % _s, -0.820, _s * 0.285, 0.255, 0.049, 0.020, rot=(0, 0, 0), m=M_ACC, v=16)')
s = s.replace('    cil("R_SprD2_%d" % _s, -0.820, _s * 0.285, 0.465, 0.047, 0.020, m=M_ACC, v=16)',
              '    cil("R_SprD2_%d" % _s, -0.820, _s * 0.285, 0.470, 0.049, 0.020, rot=(0, 0, 0), m=M_ACC, v=16)')

# 4) BOCAS: precisam CRUZAR a face da placa (x=0.048) — contidas dentro = sem interseccao
s = s.replace('box("P_Mouth_M", 0.008, 0.040, -0.035, 0.035, 1.000, 1.013, m=M_TIRE, bevel=0.006)',
              'box("P_Mouth_M", 0.032, 0.064, -0.035, 0.035, 1.000, 1.013, m=M_TIRE, bevel=0.006)')
s = s.replace('box("P_Mouth_%d" % _s, 0.008, 0.040, _s * 0.035, _s * 0.066, 1.007, 1.023, m=M_TIRE, bevel=0.006)',
              'box("P_Mouth_%d" % _s, 0.032, 0.064, _s * 0.035, _s * 0.066, 1.007, 1.023, m=M_TIRE, bevel=0.006)')

# 5) VOLANTE: era tubo ABERTO (48 boundary) — tampar as duas pontas
old = '''for j in range(segs):
    bmT.faces.new((ringsW[0][j],ringsW[0][(j+1)%segs],ringsW[1][(j+1)%segs],ringsW[1][j]))'''
new = '''for j in range(segs):
    bmT.faces.new((ringsW[0][j],ringsW[0][(j+1)%segs],ringsW[1][(j+1)%segs],ringsW[1][j]))
bmT.faces.new(list(reversed(ringsW[0]))); bmT.faces.new(list(ringsW[1]))   # v079: tampar (era casca aberta)'''
assert old in s, 'volante'
s = s.replace(old, new)

s = s.replace('conjunto-v078.blend', 'conjunto-v079.blend')
open('/tmp/v079.py', 'w').write(s)
print('v079.py OK: eixos alcancam o aro | strut diant.->chassi | molas VERTICAIS | bocas cruzam a placa | volante tampado')
