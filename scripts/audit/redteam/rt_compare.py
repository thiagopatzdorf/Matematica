#!/usr/bin/env python3
"""rt_compare.py -- red team: compara conjuntos de órbitas de trios (com órfãs) entre saídas.

Aceita os dois formatos: do base_search ("TRIO orphans=o s1=.. s2=..", canonizado aqui com o
canon() do compare_diff.py) e do verify_trios / rt_fft_trios ("TRIO o a b c", já canônico).
Uso: rt_compare.py arq1 arq2 [arq3 ...]   -> sai 1 se algum conjunto divergir do primeiro.
"""
import os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from compare_diff import canon  # noqa: E402  (reuso: mesma canonização da auditoria)


def le(path):
    S = {}
    for line in open(path):
        m = re.match(r"TRIO orphans=(\d+) s1=(\d+) s2=(\d+)", line)
        if m:
            k, o = canon(int(m[2]), int(m[3])), int(m[1])
        else:
            p = line.split()
            if not (len(p) == 5 and p[0] == "TRIO"):
                continue
            k, o = (int(p[2]), int(p[3]), int(p[4])), int(p[1])
        if S.get(k, o) != o:
            raise SystemExit(f"{path}: órbita {k} com duas contagens")
        S[k] = o
    return S


sets = [(p, le(p)) for p in sys.argv[1:]]
ref_p, ref = sets[0]
ruim = 0
for p, s in sets:
    dif = set(s.items()) ^ set(ref.items())
    hist = {}
    for o in s.values():
        hist[o] = hist.get(o, 0) + 1
    print(f"{os.path.basename(p)}: órbitas={len(s)} min={min(s.values()) if s else None} "
          f"{'IGUAL' if not dif else 'DIVERGE (%d)' % len(dif)} hist={dict(sorted(hist.items()))}")
    if dif:
        ruim = 1
        print("   ", sorted(dif)[:5])
sys.exit(ruim)
