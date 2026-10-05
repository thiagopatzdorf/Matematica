#!/usr/bin/env python3
"""Censo da escada de lemas da fatia 0 sobre as configurações K das listas de M = 15 e 16.

Os degraus P1, P2, T e F só dependem de K e do limiar M - s* (não dos blocos t), e as K de M = 15
estão todas na lista de M = 16 (11 496 de 11 592). Por isso o censo roda uma vez por K e decide
os dois M. Uma linha JSON por K: |U|, τ*(U), o maior empacotamento achado (P1: guloso e, se
preciso, MILP de viabilidade), o 2-empacotamento guloso (P2) e, por M, se T e F matam **com
certificado conferido em inteiros** (`lemas.confere_*`). O conjunto do P1 vai no registro.

  python3 tools/exatos/k362/estrutura/censo.py --saida censo_K.jsonl
"""
import argparse
import gzip
import json
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import lemas  # noqa: E402

DADOS = os.path.join(AQUI, "..", "contagem", "dados")
MS = (15, 16)


def configuracoes():
    """Lista de K únicas (na ordem da lista de M = 16) e, por M, os índices de instância de cada K."""
    chaves, por_m = {}, {}
    for M in (16, 15):
        ins = json.loads(gzip.open(os.path.join(DADOS, f"K3_6_2_M{M}_instancias.json.gz")).read())
        for i, (s, K, t) in enumerate(ins):
            k = json.dumps(K)
            chaves.setdefault(k, (s, K))
            por_m.setdefault(k, {}).setdefault(M, []).append(i)
    return [(v[0], v[1], por_m[k]) for k, v in chaves.items()]


def degraus(s, K, Ms):
    r = {"U": len(lemas.U_de(K))}
    v, w = lemas.tau(K)
    r["tau"] = round(v, 6)
    P = lemas.guloso(K, 1)
    alvo = max(M - s + 1 for M in Ms)
    if len(P) < alvo and v >= min(M - s + 1 for M in Ms) - 1e-9:
        for M in sorted(Ms, reverse=True):
            n, Q, _ = lemas.m_empacotamento(K, M, 1, tempo=3, alvo=M - s + 1)
            if n > len(P):
                P = Q
                break
    r["nu_lb"] = len(P)
    r["P1_pontos"] = [list(p) for p in P]
    r["P2_lb"] = len(lemas.guloso(K, 2, tentativas=60))
    for M in Ms:
        m = str(M)
        r["P1_" + m] = lemas.confere_empacotamento(K, M, P, 1)
        r["T_" + m] = lemas.cert_fatia(K, M, (v, w))[1] is not None
        if not r["T_" + m]:
            r["F_" + m] = lemas.cert_fibras(K, M)[1] is not None
    return r


def degrau_que_mata(r, M):
    """O degrau mais legível que mata a configuração K para este M (None se nenhum mata)."""
    m = str(M)
    for d in ("P1", "T", "F"):
        if r.get(f"{d}_{m}"):
            return d
    return None


def resumo(caminho):
    """Tabela por M e s*: quantas K (e quantas instâncias) cada degrau mata primeiro."""
    from collections import Counter
    K_, I_ = Counter(), Counter()
    for ln in open(caminho):
        r = json.loads(ln)
        for m, idx in r["inst"].items():
            d = degrau_que_mata(r, int(m))
            K_[(int(m), r["s"], d)] += 1
            I_[(int(m), r["s"], d)] += len(idx)
    for M in MS:
        print(f"M = {M}   (K / instâncias)")
        for s in sorted({k[1] for k in K_ if k[0] == M}):
            print(f"  s* = {s}: " + "  ".join(f"{d or 'nenhum'} {K_[(M, s, d)]}/{I_[(M, s, d)]}"
                                            for d in ("P1", "T", "F", None) if K_[(M, s, d)]))
        tot = {d: sum(v for k, v in I_.items() if k[0] == M and k[2] == d) for d in ("P1", "T", "F", None)}
        print(f"  total de instâncias: {tot}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--saida", required=True)
    ap.add_argument("--resumo", action="store_true", help="só resume o JSONL já gravado")
    a = ap.parse_args()
    if a.resumo:
        resumo(a.saida)
        return
    feitos = set()
    if os.path.exists(a.saida):
        feitos = {json.loads(ln)["k"] for ln in open(a.saida)}
    with open(a.saida, "a") as f:
        for k, (s, K, idx) in enumerate(configuracoes()):
            if k in feitos:
                continue
            Ms = sorted(int(M) for M in idx)
            r = {"k": k, "s": s, "K": K, "inst": {str(M): idx[M] for M in Ms}}
            r.update(degraus(s, K, Ms))
            f.write(json.dumps(r, separators=(",", ":")) + "\n")
            f.flush()


if __name__ == "__main__":
    main()
