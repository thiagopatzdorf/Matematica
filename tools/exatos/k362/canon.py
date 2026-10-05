#!/usr/bin/env python3
"""Forma canônica de conjuntos de pontos de Z_q^m sob S_q wr S_m, independente do SAT e de
`fatia.forma` (docs/exatos/k362/K3_M15_CANONICAL.md).

Implementação 1 (`canon_nauty`): grafo colorido com três cores de vértice,
  * cor 0: um vértice por ponto;
  * cor 1: um vértice por coordenada i;
  * cor 2: um vértice por par (i, a), ligado à coordenada i;
e o ponto p ligado a (i, p_i) para todo i. Um isomorfismo que respeita as cores leva blocos de
coordenada em blocos de coordenada (cada (i, a) tem um único vizinho de cor 1), ou seja, é uma
permutação de coordenadas com uma permutação de símbolos em cada uma, e leva pontos em pontos com
as mesmas incidências. Como os pontos são distintos, isso é exatamente S_q wr S_m agindo no
conjunto; e grpsize do nauty é |Stab(K)|. Roda o `dreadnaut` (nauty) num processo só, em lote.

Implementação 2 (`canon_forca_bruta`): mínimo lexicográfico da imagem ordenada sobre o grupo
inteiro. Só para m pequeno; é o árbitro dos testes.
"""
import os
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import grupo  # noqa: E402


def _grafo(pontos, q, m):
    s = len(pontos)
    coord = lambda i: s + i  # noqa: E731
    simb = lambda i, a: s + m + q * i + a  # noqa: E731
    adj = [[] for _ in range(s + m + q * m)]
    for k, p in enumerate(pontos):
        for i in range(m):
            adj[k].append(simb(i, p[i]))
    for i in range(m):
        for a in range(q):
            adj[coord(i)].append(simb(i, a))
    nv = len(adj)
    lst = "; ".join(" ".join(map(str, sorted(v))) for v in adj)
    cel = lambda a, b: ",".join(map(str, range(a, b)))  # noqa: E731
    part = f"[{cel(0, s)}|{cel(s, s + m)}|{cel(s + m, nv)}]"
    return f"n={nv} g {lst}. f={part} c x b\n", nv


def canon_nauty(conjuntos, q, m):
    """Lista de (forma, |Stab|) para cada conjunto de pontos (todos com o mesmo tamanho)."""
    exe = os.environ.get("DREADNAUT") or shutil.which("dreadnaut")
    if not exe:
        raise RuntimeError("dreadnaut (nauty) não encontrado: apt-get install nauty")
    textos, nvs = zip(*(_grafo(K, q, m) for K in conjuntos)) if conjuntos else ((), ())
    out = subprocess.run([exe], input="-a -m l=100000\n" + "".join(textos),
                         capture_output=True, text=True, check=True).stdout.splitlines()
    res, i = [], 0
    for nv in nvs:
        while "grpsize=" not in out[i]:
            i += 1
        gs = round(float(out[i].split("grpsize=")[1].split(";")[0]))
        i += 1
        while out[i].startswith("canupdates") or out[i].startswith("[") or not out[i].strip():
            i += 1
        i += 1  # rótulo canônico (não entra na forma)
        res.append((tuple(out[i:i + nv]), gs))
        i += nv
    return res


def canon_forca_bruta(pontos, q, m):
    return min(tuple(sorted(grupo.aplica(g, p) for p in pontos)) for g in grupo.todos(q, m))


def estabilizador_forca_bruta(pontos, q, m):
    alvo = tuple(sorted(pontos))
    return sum(1 for g in grupo.todos(q, m) if tuple(sorted(grupo.aplica(g, p) for p in pontos)) == alvo)


def classificar(q, n, R, M, lote=20000):
    """Classes de códigos de raio R com M palavras, por geração nível a nível com a forma do nauty:
    cada conjunto não cobridor ramifica nas palavras que cobrem o menor ponto descoberto do SEU
    representante; filhos são deduplicados pela forma. Completo: se C cobre e S ⊂ g(C) é o
    representante guardado, g(C) tem uma palavra fora de S que cobre esse ponto. Poda: as l palavras
    que faltam cobrem no máximo l·V(n,R) pontos. Devolve um representante por classe."""
    import itertools
    from math import comb
    pts = list(itertools.product(range(q), repeat=n))
    V = sum(comb(n, i) * (q - 1) ** i for i in range(R + 1))
    d = lambda a, b: sum(x != y for x, y in zip(a, b))  # noqa: E731
    nivel, cobridores = [[pts[0]]], {}
    for k in range(1, M):
        filhos, cand = {}, []
        for S in nivel:
            p = next(x for x in pts if all(d(x, c) > R for c in S))
            cand += [sorted(S + [w]) for w in pts if d(w, p) <= R and w not in S]
        for i in range(0, len(cand), lote):  # um dreadnaut por lote, não por conjunto
            parte = cand[i:i + lote]
            for T, (f, _) in zip(parte, canon_nauty(parte, q, n)):
                filhos.setdefault(f, T)
        nivel = []
        for f, T in filhos.items():
            desc = sum(1 for x in pts if all(d(x, c) > R for c in T))
            if desc == 0:
                if k + 1 == M:
                    cobridores[f] = T
            elif (M - k - 1) * V >= desc:
                nivel.append(T)
    return list(cobridores.values())


if __name__ == "__main__":
    q, n, R, M = map(int, sys.argv[1:5])
    print(f"K_{q}({n},{R}) M={M}: {len(classificar(q, n, R, M))} classes")
