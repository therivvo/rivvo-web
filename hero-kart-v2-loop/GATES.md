# Gates: Hero Kart V2 — Loop persistente de aprovação dupla
Escopo: revisão R54+; reconstrução geométrica do asset Blender, sem integração de runtime.

- [ ] G0: Estado inicial R53 rejeitado e escopo P0 registrado
  CHECK: python3 - <<'PY'
from pathlib import Path
p=Path('docs/HERO-KART-V2-R54-LOOP.md')
print('R53_REJECTED_P0_RECORDED' if p.exists() else 'MISSING')
PY
  EXPECT: R53_REJECTED_P0_RECORDED
  EVIDENCE: pending

- [ ] G1: Reconstrução P0 implementada no script e no blend salvo
  CHECK: test -s assets/hero-kart-v2/hero-kart-v2.blend && python3 - <<'PY'
from pathlib import Path
s=Path('scripts/blender/hero_kart_v2_build.py').read_text()
need=['WindshieldMount','HelmetTemple','HelmetJaw','HelmetNape','HelmetVisorPivot','SteeringHub','DriverCollar']
print('P0_SYMBOLS_OK' if all(x in s for x in need) else 'P0_SYMBOLS_MISSING')
PY
  EXPECT: P0_SYMBOLS_OK
  EVIDENCE: pending

- [ ] G2: Blender 4.0.2 executou a reconstrução sem traceback e salvou o artefato
  CHECK: python3 - <<'PY'
import json
from pathlib import Path
p=Path('assets/hero-kart-v2/build-report.json')
print('BUILD_REPORT_OK' if p.exists() and p.stat().st_size>0 else 'MISSING')
PY
  EXPECT: BUILD_REPORT_OK
  EVIDENCE: pending

- [ ] G3: Beauty/profile/top/clearance pertencem à mesma revisão e existem
  CHECK: test -s assets/hero-kart-v2/renders/beauty.png && test -s assets/hero-kart-v2/renders/windshield-profile.png && test -s assets/hero-kart-v2/renders/windshield-top.png && test -s assets/hero-kart-v2/renders/driver-clearance.png
  EXPECT:
  EVIDENCE: pending

- [ ] G4: Auditoria geométrica P0 mensurável passa
  CHECK: python3 - <<'PY'
import json
p=json.load(open('assets/hero-kart-v2/p0-metrics.json'))
print('P0_METRICS_PASS' if p.get('all_pass') else 'P0_METRICS_FAIL')
PY
  EXPECT: P0_METRICS_PASS
  EVIDENCE: pending

- [ ] G5: Vision independente aprova a mesma revisão
  EVIDENCE: pending

- [ ] G6: Sol gpt-5.6-sol + xhigh aprova a mesma revisão após vision próprio
  EVIDENCE: pending

- [ ] G7: Repo, vault, wiki/index/log/entidade e memória atualizados sem secrets
  EVIDENCE: pending

- [ ] G8: Cada commit atômico foi pushado e remote verificado
  CHECK: test "$(git rev-parse HEAD)" = "$(git ls-remote origin refs/heads/main | cut -f1)"
  EXPECT:
  EVIDENCE: pending
