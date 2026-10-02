#!/usr/bin/env python3
"""Compara exactT, exactT2 e verify_trios classe a classe (conjuntos de órbitas canônicas + órfãs).

Uso: compare_diff.py DIR_DIFF T L1 L2 ...   (arquivos t1_T_L.out, t2_T_L.out, vt_T_L.out)
Sai com 1 se qualquer classe divergir ou faltar saída.
"""
import re
import sys

q, r = 7, 6


def dig(x):
    return [(x // q**i) % q for i in range(r)]


def num(v):
    return sum(d * q**i for i, d in enumerate(v))


def canon(s1, s2):
    P = [dig(0), dig(s1), dig(s2)]
    best = None
    for b in P:
        for lam in range(1, q):
            t = tuple(sorted(num([lam * (p[i] - b[i]) % q for i in range(r)]) for p in P))
            best = t if best is None or t < best else best
    return best


def le_kit(path):
    S, fim = {}, None
    for line in open(path):
        m = re.match(r"TRIO orphans=(\d+) s1=(\d+) s2=(\d+)", line)
        if m:
            k, o = canon(int(m[2]), int(m[3])), int(m[1])
            if S.get(k, o) != o:
                raise SystemExit(f"{path}: órbita com duas contagens")
            S[k] = o
        if '"exact":true' in line:
            fim = line
    if fim is None:
        raise FileNotFoundError(path)
    return S


def le_vt(path):
    S, fim = {}, None
    for line in open(path):
        p = line.split()
        if p and p[0] == "TRIO":
            S[(int(p[2]), int(p[3]), int(p[4]))] = int(p[1])
        if p and p[0] == "MIN":
            fim = line
    if fim is None:
        raise FileNotFoundError(path)
    return S


def main():
    d, T, Ls = sys.argv[1], sys.argv[2], sys.argv[3:]
    ruim = 0
    for L in Ls:
        try:
            a = le_kit(f"{d}/t1_{T}_{L}.out")
            b = le_kit(f"{d}/t2_{T}_{L}.out")
            c = le_vt(f"{d}/vt_{T}_{L}.out")
        except FileNotFoundError as e:
            print(f"L={L}: saída incompleta ({e})")
            ruim += 1
            continue
        igual = a == b == c
        mn = min(a.values()) if a else None
        print(f"L={L} T={T}: órbitas exactT={len(a)} exactT2={len(b)} verify={len(c)} mínimo={mn} -> {'IGUAIS' if igual else 'DIVERGEM'}")
        if not igual:
            ruim += 1
            for nome, x, y in (("exactT-exactT2", a, b), ("exactT-verify", a, c)):
                dif = set(x.items()) ^ set(y.items())
                if dif:
                    print(f"  {nome}: {sorted(dif)[:5]}")
    return 1 if ruim else 0


if __name__ == "__main__":
    sys.exit(main())
