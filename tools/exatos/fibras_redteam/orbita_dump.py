"""Roda a órbita por SAT (orbita_fibras) em cada código de um JSONL gravado por
massa_predicados.py --dump (códigos em que a forma normal do repo viola (h)). Se a CNF do repo
perdesse algum deles, a órbita daria UNSAT.

Uso: orbita_dump.py DIR_FIBRAS dump.jsonl [max]"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import orbita_fibras  # noqa: E402

d, arq = sys.argv[1], sys.argv[2]
mx = int(sys.argv[3]) if len(sys.argv) > 3 else 10 ** 9
enc = orbita_fibras.carregar_encode(d)
sys.path.insert(0, d)
import canon_corrigido  # noqa: E402
import fib_canon  # noqa: E402
import fib_encode  # noqa: E402
from checar_cnf import Checador  # noqa: E402
chks = {}
cont = {}
for i, l in enumerate(open(arq)):
    if i >= mx:
        break
    r = json.loads(l)
    C = [tuple(c) for c in r["C"]]
    ordem = r.get("ordem", "min")
    ok = orbita_fibras.orbita_sat(enc, C, r["q"], r["n"], cobertura=False, smin=r["smin"], ordem=ordem)
    # a CNF concorda com o predicado: forma do repo reprovada, forma corrigida aceita
    q, n, M, smin = r["q"], r["n"], r["M"], r["smin"]
    chk = chks.setdefault((q, n, M, smin), Checador(fib_encode, q, n, M, smin))
    pref, norm = canon_corrigido.canonizar(C, q, n, ordem)
    _, nr = fib_canon.canonizar(C, q, n, n, smin, ordem=ordem)
    cnf_corr, cnf_repo = chk.satisfaz(pref, norm, False), chk.satisfaz(pref, nr, False)
    k = f"K_{r['q']}({r['n']},{r['n']-2}) M={r['M']} ordem {ordem}"
    c = cont.setdefault(k, [0, 0, 0, 0])
    c[0] += 1
    c[1] += (not ok)
    c[2] += (not cnf_corr)
    c[3] += cnf_repo
    if not ok:
        print("ORBITA UNSAT", json.dumps(r), flush=True)
print(json.dumps({k: {"codigos": v[0], "orbita_unsat": v[1], "cnf_reprova_corrigida": v[2],
                       "cnf_aceita_forma_do_repo": v[3]} for k, v in cont.items()}))
