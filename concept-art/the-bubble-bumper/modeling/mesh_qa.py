#!/usr/bin/env python3
"""QA de malha do Bubble Bumper — le o log do ultimo build que contem a versao.

Emite QA_MALHA_NONMANIFOLD e QA_MALHA_QUADS (greppable pelos gates).
Uso: python3 mesh_qa.py <versao>
"""
import sys, os, re, glob
VER = (sys.argv[1] if len(sys.argv) > 1 else "w282").lower()
J = "/opt/blender-runner/jobs/"
cands = sorted(glob.glob(J + "*"), key=lambda p: os.path.getmtime(p), reverse=True)
for d in cands:
    lg = os.path.join(d, "blender.log")
    if not os.path.exists(lg):
        continue
    txt = open(lg, errors="ignore").read()
    m = re.search(r'"' + VER.upper() + r'_body":\s*\{([^}]*)\}', txt)
    if not m:
        m = re.search(r'"([^"]*_body)":\s*\{([^}]*)\}', txt)
        if not m:
            continue
        body = m.group(2)
    else:
        body = m.group(1)

    def g(k, dflt="NA"):
        mm = re.search(k + r'"\s*:\s*([0-9.]+)', body)
        return mm.group(1) if mm else dflt
    print("QA_MALHA_VERSAO=%s" % VER)
    print("QA_MALHA_NONMANIFOLD=%s" % g("non_manifold"))
    print("QA_MALHA_QUADS=%s" % g("pct_quads"))
    print("QA_MALHA_VALENCE4=%s" % g("pct_valence4"))
    print("QA_MALHA_VERTS=%s" % g("verts"))
    print("QA_MALHA_NGONS=%s" % g("ngons"))
    sys.exit(0)
print("QA_MALHA_VERSAO=%s" % VER)
print("QA_MALHA_NONMANIFOLD=NA")
print("QA_MALHA_QUADS=NA")
sys.exit(0)
