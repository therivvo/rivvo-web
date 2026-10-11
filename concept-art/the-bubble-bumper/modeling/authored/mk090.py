import re
s = open('/tmp/v088.py').read()

# ===== v090: ACABAMENTO ORGANICO v2 — SUBSURF so' nas pecas VISIVEIS (nao nas estruturais) =====
# v089 subdividiu PodSup/Rail/R_BumpSup -> encolheram e quebraram 3 contatos (2 componentes).
# Lista BRANCA explicita: apenas carroceria/casco/piloto (superficie visivel).
bloco = '''
# ---------- v090: ACABAMENTO ORGANICO (lista branca: so' superficie visivel) ----------
# v089 tentou por prefixo e subdividiu pecas ESTRUTURAIS (PodSup, Rail, R_BumpSup, R_Spring):
# elas encolheram, perderam contato (30/34) e criaram 2 componentes. Agora: lista explicita.
_VISIVEIS = ('N_Cowl', 'N_Tank', 'N_Nose', 'N_Ramp', 'Sidepod_L', 'Sidepod_R',
             'P_Helmet', 'P_Torso', 'P_Neck', 'P_Shoulder', 'P_Hips', 'P_Waist', 'P_Dash',
             'P_KneeL', 'P_KneeR', 'R_Motor', 'R_Wing', 'R_BumperBar', 'R_UBendTop')
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
'''
ancora = "bpy.ops.wm.save_as_mainfile(filepath="
assert ancora in s, 'ancora'
i = s.index(ancora)
s = s[:i] + bloco + '\n' + s[i:]
s = s.replace('conjunto-v088.blend', 'conjunto-v090.blend')
open('/tmp/v090.py', 'w').write(s)
print('v090.py OK')
