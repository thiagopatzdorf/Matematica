#!/usr/bin/env python3
"""CNF da construção por blocos para K_q(n, n-2) e decodificação do modelo.

Construção (docs/exatos/FAMILIA_KQ_N_N2.md): Z_q = A_0 ⊔ ... ⊔ A_{k-1}, C = ∪ C_j com C_j ⊂ A_j^n.
Para x ∈ Z_q^n seja S_j(x) = {i : x_i ∈ A_j}. Então

    C cobre Z_q^n (raio n-2)  <=>  para toda partição ordenada (S_0, ..., S_{k-1}) de [n]
                                    existe j com C_j|S_j cobrindo A_j^{S_j} (>= 2 concordâncias).

(<=: o x dado concorda só com palavras do bloco j nas coordenadas S_j. =>: se para cada j há y_j em
A_j^{S_j} descoberto, o x que junta os y_j é descoberto.) A CNF tem:

* x[j,w,i,v]: palavra w do bloco j tem símbolo v na coordenada i (exatamente um v);
* P[j,(i1,i2),(a,b)]: alguma palavra do bloco j tem (a,b) em (i1,i2) (só a direção P -> palavra);
* U[j,S] para lo_j <= |S| <= hi_j: "C_j|S cobre A_j^S", com uma cláusula por ponto y de A_j^S:
  ¬U ∨ OR_{i1<i2 em S} P[j,(i1,i2),(y_i1,y_i2)];
* por partição ordenada σ ∈ [k]^n: OR_j OR_{T ⊆ S_j, lo_j <= |T| <= hi_j} U[j,T] (cobrir T ⊆ S_j já
  cobre S_j). Um bloco de tamanho 1 com 1 palavra é a palavra constante: cobre todo |S| >= 2.

Restringir [lo, hi] só tira soluções (nunca aceita código que não cobre); o código decodificado é
sempre reconferido por cobre_n2.c e por tools/verify/verify.

Uso:
  blocos_sat.py gerar q n a:m[:lo:hi] ... --cnf ARQ      (escreve a CNF e o mapa ARQ.mapa.json)
  blocos_sat.py gerar ... --fixar ARQ  (palavras de ARQ fixam as primeiras colunas, bloco a bloco)
  blocos_sat.py gerar 0 n a:m --t T --cnf ARQ   (modo g(a,n,T): toda projeção em T coordenadas cobre)
  blocos_sat.py decodificar ARQ.mapa.json SAIDA_DO_SOLVER  (imprime o código, uma palavra por linha)
"""
import itertools
import json
import sys

DIG = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"


class CNF:
    def __init__(self):
        self.nv = 0
        self.cl = []

    def var(self):
        self.nv += 1
        return self.nv

    def add(self, c):
        self.cl.append(c)


def gerar(q, n, blocos, quebra=True, fixas=None, familia_t=0):
    f = CNF()
    off = 0
    meta = []
    X = {}
    U = {}
    PP = {}
    ZZ = {}
    for j, (a, m, lo, hi) in enumerate(blocos):
        meta.append({"a": a, "m": m, "off": off, "lo": lo, "hi": hi})
        off += a
        if a == 1:
            continue  # palavra constante, nada a decidir
        for w in range(m):
            for i in range(n):
                vs = [f.var() for _ in range(a)]
                for v in range(a):
                    X[j, w, i, v] = vs[v]
                f.add(vs)
                for v1, v2 in itertools.combinations(vs, 2):
                    f.add([-v1, -v2])
        P = {}
        for i1, i2 in itertools.combinations(range(n), 2):
            for va, vb in itertools.product(range(a), repeat=2):
                p = f.var()
                P[i1, i2, va, vb] = p
                PP[j, i1, i2, va, vb] = p
                zs = []
                for w in range(m):
                    z = f.var()
                    f.add([-z, X[j, w, i1, va]])
                    f.add([-z, X[j, w, i2, vb]])
                    zs.append(z)
                    ZZ[j, w, i1, i2, va, vb] = z
                f.add([-p] + zs)
        for s in range(max(lo, 2), hi + 1):
            for S in itertools.combinations(range(n), s):
                u = f.var()
                U[j, S] = u
                prs = list(itertools.combinations(range(s), 2))
                for y in itertools.product(range(a), repeat=s):
                    f.add([-u] + [P[S[p1], S[p2], y[p1], y[p2]] for p1, p2 in prs])
        if quebra:
            # palavras do bloco em ordem não decrescente na coordenada 0 (reordenar palavras)
            for w in range(m - 1):
                for v in range(a):
                    for v2 in range(v):
                        f.add([-X[j, w, 0, v], -X[j, w + 1, 0, v2]])
            # precedência de valores nas colunas >= 1: renomear os símbolos de uma coluna dentro do
            # bloco é isometria e não mexe na ordem das palavras, então pode-se exigir que v só
            # apareça depois de v-1 (na ordem das palavras); a coluna 0 já está ordenada acima.
            for i in range(1, n):
                for v in range(1, a):
                    for w in range(m):
                        f.add([-X[j, w, i, v]] + [X[j, w2, i, v - 1] for w2 in range(w)])
    if fixas:
        # palavras dadas (prefixo de n0 <= n colunas) fixam as primeiras colunas, bloco a bloco, na
        # ordem do arquivo; serve para perguntar "este código estende por mais colunas?"
        cheio = [0] * len(blocos)
        for pal in fixas:
            d = [DIG.index(ch) for ch in pal]
            j = next(j for j, b in enumerate(meta) if b["off"] <= d[0] < b["off"] + b["a"])
            if blocos[j][0] == 1:
                continue
            w = cheio[j]
            cheio[j] += 1
            for i, v in enumerate(d):
                f.add([X[j, w, i, v - meta[j]["off"]]])
    k = len(blocos)
    if familia_t:
        # modo g(a, n, T): um bloco só, e C|S tem de cobrir A^S para TODO S com |S| = T
        for S in itertools.combinations(range(n), familia_t):
            f.add([U[0, S]])
        sig_todas = []
    else:
        sig_todas = itertools.product(range(k), repeat=n)
    for sig in sig_todas:
        cl = []
        ok = False
        for j, (a, m, lo, hi) in enumerate(blocos):
            Sj = tuple(i for i in range(n) if sig[i] == j)
            if a == 1:
                if len(Sj) >= 2:
                    ok = True
                    break
                continue
            for s in range(max(lo, 2), min(hi, len(Sj)) + 1):
                for T in itertools.combinations(Sj, s):
                    cl.append(U[j, T])
        if ok:
            continue
        if not cl:
            raise SystemExit(f"partição {sig} sem nenhum bloco capaz de cobrir: impossível com esses [lo,hi]")
        f.add(cl)
    mapa = {"q": q, "n": n, "blocos": meta,
            "x": [[j, w, i, v, var] for (j, w, i, v), var in X.items()]}
    vars_ = {"X": X, "P": PP, "Z": ZZ, "U": U}
    return f, mapa, vars_


def decodificar(mapa, modelo):
    q, n = mapa["q"], mapa["n"]
    pos = {abs(l) for l in modelo if l > 0}
    pal = {}
    for j, w, i, v, var in mapa["x"]:
        if var in pos:
            pal.setdefault((j, w), [None] * n)[i] = mapa["blocos"][j]["off"] + v
    out = []
    for j, b in enumerate(mapa["blocos"]):
        for w in range(b["m"]):
            if b["a"] == 1:
                out.append(DIG[b["off"]] * n)
            else:
                out.append("".join(DIG[c] for c in pal[j, w]))
    return out


def familia_de(code, a, n, S):
    """True sse code (palavras em Z_a^n) cobre Z_a^S com >= 2 concordâncias."""
    for y in itertools.product(range(a), repeat=len(S)):
        if not any(sum(w[i] == v for i, v in zip(S, y)) >= 2 for w in code):
            return False
    return True


def normalizar(blocos_palavras):
    """Leva um código por blocos à forma que a quebra de simetria da CNF exige.

    blocos_palavras: lista (por bloco) de listas de palavras com símbolos locais 0..a-1. Ordena as
    palavras pela coordenada 0 e renomeia cada coluna >= 1 pela ordem da primeira aparição. As duas
    operações são isometrias que preservam os blocos, então todo código tem uma forma assim: é o
    argumento de que a quebra não perde solução, e os testes conferem com ele.
    """
    out = []
    for pal in blocos_palavras:
        pal = sorted(pal, key=lambda w: w[0])
        n = len(pal[0])
        cols = [[w[0] for w in pal]]
        for i in range(1, n):
            ren = {}
            col = []
            for w in pal:
                if w[i] not in ren:
                    ren[w[i]] = len(ren)
                col.append(ren[w[i]])
            cols.append(col)
        out.append([tuple(cols[i][r] for i in range(n)) for r in range(len(pal))])
    return out


def ler_modelo(path):
    lits = []
    for line in open(path):
        if line.startswith("v "):
            lits += [int(t) for t in line.split()[1:]]
    return lits


def main(argv):
    if argv[1] == "gerar":
        q, n = int(argv[2]), int(argv[3])
        blocos = []
        cnf = None
        fixas = None
        familia_t = 0
        args = argv[4:]
        while args:
            t = args.pop(0)
            if t == "--fixar":
                fixas = [l.strip() for l in open(args.pop(0)) if l.strip()]
                continue
            if t == "--t":
                familia_t = int(args.pop(0))
                continue
            if t == "--cnf":
                cnf = args.pop(0)
                continue
            p = [int(v) for v in t.split(":")]
            a, m = p[0], p[1]
            lo, hi = (p[2], p[3]) if len(p) == 4 else (2, n)
            blocos.append((a, m, lo, hi))
        assert familia_t or sum(b[0] for b in blocos) == q, "soma dos blocos != q"
        if familia_t:
            blocos = [(blocos[0][0], blocos[0][1], familia_t, familia_t)]
        f, mapa, _ = gerar(q, n, blocos, quebra=not fixas, fixas=fixas, familia_t=familia_t)
        with open(cnf, "w") as o:
            o.write(f"p cnf {f.nv} {len(f.cl)}\n")
            for c in f.cl:
                o.write(" ".join(map(str, c)) + " 0\n")
        json.dump(mapa, open(cnf + ".mapa.json", "w"))
        print(f"vars={f.nv} clausulas={len(f.cl)}", file=sys.stderr)
    elif argv[1] == "decodificar":
        mapa = json.load(open(argv[2]))
        for w in decodificar(mapa, ler_modelo(argv[3])):
            print(w)


if __name__ == "__main__":
    main(sys.argv)
