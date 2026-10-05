#!/usr/bin/env python3
"""Lista da fatia mínima por aumento canônico, para s* grande e espaço pequeno.

`fatia.configuracoes` percorre multiconjuntos de colunas RGS: o número de padrões cresce como o
número de Bell em s*, e para s* >= 7 a lista não termina (K_3(5,1) com M = 26 pede s* = 7 e 8).
Aqui os representantes saem nível a nível: de cada representante com k pontos, acrescenta-se
cada ponto de Z_q^m e guarda-se a forma canônica, que é o menor conjunto ordenado de índices
sobre o grupo inteiro S_q wr S_m (tabela de permutações em numpy). Só serve quando o grupo cabe
em memória (m <= 4 para q = 3: 31 104 elementos).

Completude. Seja S um conjunto de s pontos que passa no filtro |U(S)| <= cap, e tire um ponto
qualquer: o subconjunto T cobre pelo menos |cob(S)| - V(m,R) pontos. Por indução, todo
subconjunto de S com k pontos cobre pelo menos (q^m - cap) - (s - k)V(m,R) pontos; essa é a poda
aplicada no nível k, então ela nunca descarta um subconjunto de um conjunto válido. Se T tem
representante g(T) no nível k, então g(S) = g(T) + {g(p)} é gerado no nível k+1 e a forma
canônica o leva ao representante da órbita de S. A forma é invariante por construção (mínimo
sobre o grupo inteiro), então cada órbita aparece uma vez.

  python3 tools/exatos/gaps2/aumento.py --q 3 --n 5 --R 1 --M 26 --listar inst.json
"""
import argparse
import itertools
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fatia  # noqa: E402


def grupo(q, m):
    """Tabela (|G|, q^m): imagem de cada ponto (índice na ordem de itertools.product)."""
    P = np.array(list(itertools.product(range(q), repeat=m)))
    pesos = q ** np.arange(m - 1, -1, -1)
    linhas = []
    for perm in itertools.permutations(range(m)):
        for sims in itertools.product(list(itertools.permutations(range(q))), repeat=m):
            S = np.array(sims)  # S[i][v] = novo símbolo de v na coordenada i
            img = np.stack([S[i][P[:, perm[i]]] for i in range(m)], axis=1)
            linhas.append(img @ pesos)
    return P, np.array(linhas, dtype=np.int32)


def forma(G, conj):
    imgs = np.sort(G[:, list(conj)], axis=1)
    return tuple(int(v) for v in imgs[np.lexsort(imgs.T[::-1])[0]])


def configuracoes(q, m, s, R, cap, G=None, P=None):
    """Representantes das órbitas de conjuntos de s pontos com |U| <= cap."""
    if G is None:
        P, G = grupo(q, m)
    N = len(P)
    if s == 0:
        return [[]] if N <= cap else []  # U é o espaço inteiro
    B = np.array([(P != P[i]).sum(1) <= R for i in range(N)])
    V = int(B[0].sum())
    alvo = N - cap
    nivel = {forma(G, (0,))}
    for k in range(2, s + 1):
        novo = set()
        for rep in nivel:
            cob = B[list(rep)].any(0)
            for p in range(N):
                if p in rep:
                    continue
                c = int((cob | B[p]).sum())
                if c + (s - k) * V < alvo:
                    continue
                novo.add(forma(G, rep + (p,)))
        nivel = novo
    out = []
    for rep in sorted(nivel):
        if N - int(B[list(rep)].any(0).sum()) <= cap:
            out.append([tuple(int(v) for v in P[i]) for i in rep])
    return out


def instancias(q, n, R, M):
    P, G = grupo(q, n - 1)
    out = []
    for s in range(0, M // q + 1):
        cap = (M - s) * fatia.vol(n - 1, R - 1, q)
        for K in configuracoes(q, n - 1, s, R, cap, G, P):
            for t in fatia.blocos_restantes(q, M, s):
                out.append((s, tuple(K), t))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    for k in ("q", "n", "R", "M"):
        ap.add_argument("--" + k, type=int, required=True)
    ap.add_argument("--listar", required=True)
    a = ap.parse_args()
    ins = instancias(a.q, a.n, a.R, a.M)
    json.dump([[s, [list(k) for k in K], list(t)] for s, K, t in ins], open(a.listar, "w"))
    print(f"{len(ins)} instâncias -> {a.listar}")


if __name__ == "__main__":
    main()
