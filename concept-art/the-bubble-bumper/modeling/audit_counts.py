#!/usr/bin/env python3
"""Contadores das regioes do auditor estrito — saida CHAVE=valor para os gates.

Uso: python3 audit_counts.py <versao>
"""
import sys, os, subprocess, re

VER = (sys.argv[1] if len(sys.argv) > 1 else "w282")
MD = os.path.dirname(os.path.abspath(__file__))
out = subprocess.run([sys.executable, os.path.join(MD, "audit_bb.py"), VER],
                     capture_output=True, text=True).stdout
exc_alto = 0
fal_alto = 0
n = 0
for ln in out.splitlines():
    m = re.match(r"^([a-z]+)/(\S+)\s+([0-9.]+)\s+([0-9.]+)%\s+([0-9.]+)%", ln)
    if not m:
        continue
    n += 1
    if float(m.group(4)) > 20.0:
        exc_alto += 1
    if float(m.group(5)) > 20.0:
        fal_alto += 1
print("REGIOES=%d" % n)
print("REGIOES_EXCESSO_ALTO=%d" % exc_alto)
print("REGIOES_FALTA_ALTA=%d" % fal_alto)
# repassa as metricas globais
for ln in out.splitlines():
    if ln.startswith("AUD_"):
        print(ln)
