"""Forma normal para a quebra de simetria (a)-(h) de `tools/exatos/fibras/fib_encode.py`, escrita
de novo, sem importar `fib_canon.py`, com o guloso do Lema 4 CORRIGIDO.

O guloso do repo (fib_canon.canonizar, commit auditado 58d9993) atribui os rótulos novos da
coordenada 1 na ordem do índice do símbolo; o Lema 4 escrito compara com esse vetor fixo e
afirma que ele é dominado componente a componente pelo vetor do passo seguinte, o que é falso
quando os símbolos novos têm multiplicidades diferentes no bloco (contraexemplo em
`contraexemplo_h.py`). Aqui o guloso escolhe, a cada passo, o MENOR vetor possível sobre blocos
e rotulações admissíveis por (e): dentro de cada classe, os símbolos novos do bloco recebem os
próximos rótulos livres, o mais frequente no bloco primeiro. Com isso vale a prova de
REDTEAM_K764.md, seção 1.4.
"""
import math
from collections import Counter


def tipo(C, i, q):
    return tuple(sorted((Counter(c[i] for c in C).get(a, 0) for a in range(q)), reverse=True))


def residual(t):
    return math.prod(math.factorial(v) for v in Counter(t).values())


def chave(t, ordem="min"):
    return (residual(t), t) if ordem == "min" else (-residual(t), t)


def canonizar(C, q, n, ordem="min"):
    """Devolve (prefixo de tipos, palavras na forma normal) para k = n."""
    C = [tuple(c) for c in C]
    ts = [tipo(C, i, q) for i in range(n)]
    perm = sorted(range(n), key=lambda i: chave(ts[i], ordem))           # (a)
    C = [tuple(c[i] for i in perm) for c in C]
    ts = [ts[i] for i in perm]
    for i in range(n):                                                     # (b)
        cnt = Counter(c[i] for c in C)
        ordem_s = sorted(range(q), key=lambda a: (-cnt.get(a, 0), a))
        ren = {a: r for r, a in enumerate(ordem_s)}
        C = [c[:i] + (ren[c[i]],) + c[i + 1:] for c in C]

    def rotulos_por_classe(i):
        d = {}
        for a in range(q):
            d.setdefault(ts[i][a], []).append(a)
        return d

    # (c)(d)(e)(h): guloso sobre blocos e rotulações da coordenada 1
    livres = rotulos_por_classe(1)
    ren1 = {}
    ren0 = {}
    pos = 0
    t0 = ts[0]

    def melhor_rotulacao(b):
        bloco = [c[1] for c in C if c[0] == b]
        mult = Counter(bloco)
        novos = sorted({s for s in bloco if s not in ren1}, key=lambda s: (-mult[s], s))
        prox = {cl: list(v) for cl, v in livres.items()}
        pot = {}
        for s in novos:
            pot[s] = prox[ts[1][s]].pop(0)
        vet = sorted(ren1[s] if s in ren1 else pot[s] for s in bloco)
        return vet, pot

    while pos < q:
        grupo = [b for b in range(q) if t0[b] == t0[pos]]
        restantes = list(grupo)
        while restantes:
            cand = sorted((melhor_rotulacao(b)[0], b) for b in restantes)
            b = cand[0][1]
            _, pot = melhor_rotulacao(b)
            for s, r in pot.items():
                ren1[s] = r
                livres[ts[1][s]].remove(r)
            ren0[b] = pos
            pos += 1
            restantes.remove(b)
    for s in range(q):
        if s not in ren1:
            ren1[s] = livres[ts[1][s]].pop(0)
    C = [(ren0[c[0]], ren1[c[1]]) + c[2:] for c in C]
    C.sort(key=lambda c: (c[0], c[1]))
    for i in range(2, n):                                                  # (f)
        livres_i = rotulos_por_classe(i)
        ren = {}
        for c in C:
            if c[i] not in ren:
                ren[c[i]] = livres_i[ts[i][c[i]]].pop(0)
        for a in range(q):
            if a not in ren:
                ren[a] = livres_i[ts[i][a]].pop(0)
        C = [c[:i] + (ren[c[i]],) + c[i + 1:] for c in C]
    i = 2                                                                  # (g)
    while i < n:
        j = i
        while j + 1 < n and ts[j + 1] == ts[i]:
            j += 1
        cols = sorted(range(i, j + 1), key=lambda col: [w[col] for w in C])
        ordem_c = list(range(i)) + cols + list(range(j + 1, n))
        C = [tuple(w[col] for col in ordem_c) for w in C]
        i = j + 1
    return tuple(ts), C
