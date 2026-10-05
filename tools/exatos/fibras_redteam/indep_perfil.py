"""Codificação independente, por perfil, de "existe código de raio n-2 em Z_q^n com M palavras
cujo multiconjunto de tipos de coordenada é P". Não importa nada de tools/exatos/fibras.

Diferenças deliberadas em relação a fib_encode.py:
  * variáveis one-hot para TODAS as coordenadas, inclusive a 0 (fixada por unidades);
  * fibras exatas por totalizador do pysat (o repo usa contador sequencial próprio);
  * cobertura só no sentido necessário: T_ij(a,b) -> OU_w Y_wijab, Y -> X ∧ X (o repo usa
    equivalências), uma cláusula por ponto de Z_q^n;
  * quebra de simetria MÍNIMA e trivialmente válida: (a) a coordenada i recebe o tipo P[i]
    (permutação de coordenadas), (b) o símbolo a da coordenada i tem fibra P[i][a]
    (permutação de símbolos), (c') as palavras em ordem lexicográfica não decrescente
    (reordenação de palavras). Nada de (d)-(h).
Palavras repetidas são permitidas (relaxação), então UNSAT vale para multiconjuntos.

Uso: indep_perfil.py q n M "3322111,3322111,..." saida.cnf
"""
import hashlib
import itertools
import sys



class F:
    def __init__(self):
        self.nv = 0
        self.cl = []

    def var(self):
        self.nv += 1
        return self.nv

    def add(self, c):
        self.cl.append(list(c))


def codificar(q, n, M, perfil):
    """perfil: lista de n tipos (tuplas decrescentes de q fibras somando M)."""
    from pysat.card import CardEnc, EncType  # import tardio (CI sem pysat)

    assert len(perfil) == n and all(len(t) == q and sum(t) == M for t in perfil)
    f = F()
    X = [[[f.var() for _ in range(q)] for _ in range(n)] for _ in range(M)]
    for w in range(M):
        for i in range(n):
            f.add(X[w][i])
            for a, b in itertools.combinations(range(q), 2):
                f.add([-X[w][i][a], -X[w][i][b]])
    for i in range(n):
        for a in range(q):
            enc = CardEnc.equals([X[w][i][a] for w in range(M)], bound=perfil[i][a], top_id=f.nv,
                                 encoding=EncType.totalizer)
            f.nv = max(f.nv, enc.nv)
            for c in enc.clauses:
                f.add(c)
    # coordenada 0 fixada: palavras em ordem lexicográfica e fibras P[0] decrescentes
    w = 0
    for a in range(q):
        for _ in range(perfil[0][a]):
            f.add([X[w][0][a]])
            w += 1
    # (c') palavras em ordem lexicográfica: e[w][r] <- prefixos iguais até r
    for w in range(M - 1):
        e = None
        for r in range(n):
            for a in range(q):
                for b in range(a):
                    f.add(([-e] if e else []) + [-X[w][r][a], -X[w + 1][r][b]])
            if r == n - 1:
                break
            e2 = f.var()
            for a in range(q):
                f.add(([-e] if e else []) + [-X[w][r][a], -X[w + 1][r][a], e2])
            e = e2
    # cobertura por pares
    T = {}
    for i, j in itertools.combinations(range(n), 2):
        for a in range(q):
            for b in range(q):
                t = f.var()
                T[i, j, a, b] = t
                ys = []
                for w in range(M):
                    y = f.var()
                    f.add([-y, X[w][i][a]])
                    f.add([-y, X[w][j][b]])
                    ys.append(y)
                f.add([-t] + ys)
    pares = list(itertools.combinations(range(n), 2))
    for v in itertools.product(range(q), repeat=n):
        f.add([T[i, j, v[i], v[j]] for i, j in pares])
    return f, X


def dimacs(f, comentario=""):
    linhas = [f"c {comentario}", f"p cnf {f.nv} {len(f.cl)}"]
    linhas += [" ".join(map(str, c)) + " 0" for c in f.cl]
    return "\n".join(linhas) + "\n"


def decodificar(modelo, X, q, n, M):
    v = {l for l in modelo if l > 0}
    return [tuple(next(a for a in range(q) if X[w][i][a] in v) for i in range(n)) for w in range(M)]


def ler_perfil(s):
    return [tuple(int(ch) for ch in t) for t in s.split(",")]


if __name__ == "__main__":
    q, n, M = map(int, sys.argv[1:4])
    perfil = ler_perfil(sys.argv[4])
    f, _ = codificar(q, n, M, perfil)
    txt = dimacs(f, f"indep K_{q}({n},{n-2}) M={M} perfil {sys.argv[4]}")
    open(sys.argv[5], "w").write(txt)
    print(f"vars={f.nv} clausulas={len(f.cl)} sha256={hashlib.sha256(txt.encode()).hexdigest()}")
