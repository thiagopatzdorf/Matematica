"""Contraexemplo à PROVA do Lema 4 (quebra (h)) de docs/exatos/FIBRAS_GERAL.md, commit 58d9993.

Código C em Z_4^3 com 10 palavras, coordenada 0 do tipo 3322 e coordenada 1 do tipo 3331. O
guloso de fib_canon.canonizar (símbolos novos rotulados na ordem do índice) produz a forma normal
FORMA_REPO abaixo, em que o bloco 0 da coordenada 1 é (0,1,1) e o bloco 1 é (0,0,2): (h) violada.
O passo errado da prova é "o vetor ordenado de Y domina u componente a componente": u rotulou o
símbolo de multiplicidade 1 com o menor rótulo, e depois o de multiplicidade 2 ficou com ele.

O ENUNCIADO do Lema 4 continua valendo para C: por força bruta sobre o grupo, há forma normal
(FORMA_CORRIGIDA, a do guloso corrigido) que satisfaz (a)-(h).
"""
import itertools
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import canon_corrigido  # noqa: E402
import predicados  # noqa: E402

C = [(0, 1, 0), (0, 2, 0), (0, 2, 0), (1, 0, 1), (1, 1, 1), (1, 1, 1), (2, 0, 2), (2, 2, 2), (3, 0, 2), (3, 3, 3)]
Q, N = 4, 3
# saída de fib_canon.canonizar(C, 4, 3, 3, 1) no commit 58d9993 (medida; ver REDTEAM_K764.md)
FORMA_REPO = [(0, 0, 0), (0, 1, 0), (0, 1, 0), (1, 0, 1), (1, 0, 1), (1, 2, 1), (2, 1, 2), (2, 2, 2), (3, 2, 2), (3, 3, 3)]


def mesma_orbita(A, B, q, n):
    """Força bruta: B = imagem de A por (S_n nas coordenadas) x (S_q por coordenada), como multiconjunto."""
    from collections import Counter
    alvo = Counter(B)
    for perm in itertools.permutations(range(n)):
        Ap = [tuple(c[perm[i]] for i in range(n)) for c in A]

        def rec(i, atual):
            if i == n:
                return Counter(atual) == alvo
            for s in itertools.permutations(range(q)):
                nov = [c[:i] + (s[c[i]],) + c[i + 1:] for c in atual]
                if Counter(c[: i + 1] for c in nov) == Counter(c[: i + 1] for c in B) and rec(i + 1, nov):
                    return True
            return False
        if rec(0, Ap):
            return True
    return False


def existe_forma_normal_forca_bruta(A, q, n):
    """Procura, em toda a órbita (S_n x S_q^n; a ordem das palavras é a ordenação lexicográfica e as
    colunas >= 2 de mesmo tipo podem ser permutadas), alguma forma que satisfaça (a)-(h)."""
    achadas = []
    for perm in itertools.permutations(range(n)):
        Ap = [tuple(c[perm[i]] for i in range(n)) for c in A]
        for sims in itertools.product(itertools.permutations(range(q)), repeat=n):
            B = sorted(tuple(sims[i][c[i]] for i in range(n)) for c in Ap)
            if not predicados.viola(B, q):
                achadas.append(B)
                return achadas
    return achadas


if __name__ == "__main__":
    print("forma do repo, violações:", predicados.viola(FORMA_REPO, Q), "mesma órbita:", mesma_orbita(C, FORMA_REPO, Q, N))
    pref, norm = canon_corrigido.canonizar(C, Q, N)
    print("forma corrigida:", norm, "violações:", predicados.viola(norm, Q), "mesma órbita:", mesma_orbita(C, norm, Q, N))
    print("força bruta acha forma normal:", bool(existe_forma_normal_forca_bruta(C, Q, N)))
