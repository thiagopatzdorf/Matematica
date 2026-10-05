#!/usr/bin/env python3
"""Números do diagnóstico de K_3(6,2), M = 15 (docs/exatos/k362/K3_M15_DIAGNOSIS.md).

Lê a lista de rodar_pb.py --listar e mede, com o nauty (independente de `fatia.forma`):
  * quantas formas distintas há por (s*, blocos), ou seja, se a lista já é uma por órbita;
  * a distribuição de |Stab(K)| em S_3 wr S_5 (simetria que sobra DENTRO de cada instância);
  * a distribuição de |U(K)| no caso equilibrado e quantas instâncias o filtro novo deixa;
  * as invariantes das instâncias duras.

  python3 tools/exatos/k362/orbitas.py --instancias i15.json --duras 7955,9118,10603,11739,11804,11927
"""
import argparse
import json
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import canon  # noqa: E402
import reducao  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--instancias", required=True)
    ap.add_argument("--duras", default="")
    ap.add_argument("--q", type=int, default=3)
    ap.add_argument("--n", type=int, default=6)
    ap.add_argument("--R", type=int, default=2)
    ap.add_argument("--M", type=int, default=15)
    a = ap.parse_args()
    q, n, R, M = a.q, a.n, a.R, a.M
    ins = [(s, tuple(tuple(k) for k in K), tuple(t)) for s, K, t in json.load(open(a.instancias))]
    print(f"instâncias: {len(ins)}")
    grupos = Counter((s, t) for s, _, t in ins)
    info = {}
    for (s, t), c in sorted(grupos.items()):
        Ks = sorted({K for s2, K, t2 in ins if (s2, t2) == (s, t)})
        formas = canon.canon_nauty([list(K) for K in Ks], q, n - 1) if s > 0 else [((), 1)]
        info.update(zip(Ks, formas))
        stabs = Counter(g for _, g in formas)
        print(f"s*={s} blocos={t}: {c} instâncias, {len(Ks)} configurações, "
              f"{len({f for f, _ in formas})} formas nauty distintas; |Stab|: {dict(sorted(stabs.items()))}")
    teto = reducao.limite_U(q, n, R, M)
    eq = [K for s, K, t in ins if reducao.equilibrada(q, M, s)]
    us = {K: reducao.n_descobertos(q, n - 1, R, K) for K in eq}
    hist = Counter(us.values())
    print(f"equilibradas: {len(eq)}; |U| min={min(hist)} max={max(hist)}; teto novo {teto}")
    print("histograma de |U| (faixas de 10):", dict(sorted(Counter(u // 10 * 10 for u in us.values()).items())))
    red = reducao.reduz(q, n, R, M, ins)
    fic = [K for s, K, t in red if reducao.equilibrada(q, M, s)]
    print(f"depois do filtro: {len(red)} instâncias ({len(fic)} equilibradas)")
    for i in [int(x) for x in a.duras.split(",") if x]:
        s, K, t = ins[i]
        u = us.get(K)
        print(f"dura {i}: s*={s} blocos={t} |U|={u} |Stab|={info[K][1]} "
              f"{'FICA' if u is None or u <= teto else 'SAI pelo filtro'} K={[''.join(map(str, k)) for k in K]}")
    duras = [ins[int(x)][1] for x in a.duras.split(",") if x]
    print(f"duras em formas nauty distintas: {len({info[K][0] for K in duras})} de {len(duras)}")


if __name__ == "__main__":
    main()
