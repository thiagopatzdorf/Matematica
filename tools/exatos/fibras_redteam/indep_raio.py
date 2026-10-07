#!/usr/bin/env python3
"""Codificação INDEPENDENTE de um perfil de fibras para K_q(n,R), qualquer R (dupla checagem).

Escrita do zero, sem importar nada de `tools/exatos/fibras` nem do k742, para conferir os UNSAT de
`fib_encode` (projeções de t-uplas + quebras (c)–(h)) por um caminho diferente:

* cobertura DIRETA pela distância: z[w,v] -> "w concorda com v em >= t = n - R coordenadas",
  escrito como "todo (n - t + 1)-subconjunto de coordenadas contém uma concordância" (pombal),
  e uma cláusula OR_w z[w,v] por ponto v. Nada de projeções;
* quebra de simetria MÍNIMA, só a que vem do perfil: na coordenada i o símbolo a tem exatamente
  t_i[a] palavras (relabelar símbolos por coordenada e permutar coordenadas é isometria) e as
  palavras são ordenadas pelo símbolo da coordenada 0 (permutar palavras). Sem (d)–(h).
* cardinalidade exata por contador sequencial próprio.

Um perfil (multiconjunto de n tipos) UNSAT aqui prova a mesma afirmação que o registro do
rodar.py, com menos hipóteses (só o Lema 1 e a ordem do perfil).

Uso: indep_raio.py --q 4 --n 7 --R 4 --M 9 --tipos 3321,3321,... [--saida x.cnf]
"""
import argparse
import itertools
import sys


class F:
    def __init__(self):
        self.nv, self.cl = 0, []

    def v(self):
        self.nv += 1
        return self.nv


def exatamente(f, xs, k):
    """sum(xs) == k, contador sequencial s[i][j] <-> 'entre xs[0..i] há >= j+1 verdadeiros'."""
    n = len(xs)
    if k > n:
        f.cl.append([])
        return
    if k == 0:
        for x in xs:
            f.cl.append([-x])
        return
    s = [[f.v() for _ in range(k + 1)] for _ in range(n)]   # até k+1 para proibir excesso
    for i in range(n):
        for j in range(k + 1):
            a = s[i][j]
            ant = s[i - 1][j] if i else None
            antm = (s[i - 1][j - 1] if j else None) if i else None
            # a <-> ant OR (antm AND x)   (com j == 0: antm verdadeiro; com i == 0: ant falso)
            alt = []
            if ant:
                f.cl.append([-ant, a])
                alt.append(ant)
            if j == 0:
                f.cl.append([-xs[i], a])
                f.cl.append([-a] + alt + [xs[i]])
            elif antm:
                f.cl.append([-antm, -xs[i], a])
                f.cl.append([-a] + alt + [antm])
                f.cl.append([-a] + alt + [xs[i]])
            else:
                f.cl.append([-a] + alt)
    f.cl.append([s[n - 1][k - 1]])
    f.cl.append([-s[n - 1][k]])


def cnf(q, n, R, M, tipos):
    t = n - R
    f = F()
    x = [[[f.v() for _ in range(q)] for _ in range(n)] for _ in range(M)]
    for w in range(M):
        for i in range(n):
            f.cl.append(list(x[w][i]))
            for a, b in itertools.combinations(range(q), 2):
                f.cl.append([-x[w][i][a], -x[w][i][b]])
    for i in range(n):
        assert sum(tipos[i]) == M and len(tipos[i]) == q
        for a in range(q):
            exatamente(f, [x[w][i][a] for w in range(M)], tipos[i][a])
    w = 0
    for a in range(q):                       # palavras em ordem pelo símbolo da coordenada 0
        for _ in range(tipos[0][a]):
            f.cl.append([x[w][0][a]])
            w += 1
    subs = list(itertools.combinations(range(n), n - t + 1))
    for v in itertools.product(range(q), repeat=n):
        zs = []
        for w in range(M):
            z = f.v()
            for S in subs:
                f.cl.append([-z] + [x[w][i][v[i]] for i in S])
            zs.append(z)
        f.cl.append(zs)
    return f


def main():
    ap = argparse.ArgumentParser()
    for k in ("q", "n", "R", "M"):
        ap.add_argument("--" + k, type=int, required=True)
    ap.add_argument("--tipos", required=True, help="n tipos separados por vírgula, dígitos (q <= 10, partes <= 9)")
    ap.add_argument("--saida")
    a = ap.parse_args()
    tipos = [tuple(int(c) for c in s) for s in a.tipos.split(",")]
    assert len(tipos) == a.n
    f = cnf(a.q, a.n, a.R, a.M, tipos)
    out = open(a.saida, "w") if a.saida else sys.stdout
    out.write(f"c indep_raio K_{a.q}({a.n},{a.R}) M={a.M} tipos={a.tipos}\np cnf {f.nv} {len(f.cl)}\n")
    for c in f.cl:
        out.write(" ".join(map(str, c)) + " 0\n")


if __name__ == "__main__":
    main()
