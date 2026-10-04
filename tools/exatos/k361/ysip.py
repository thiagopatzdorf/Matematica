"""y-SIP de K_3(v,1): existe código de raio 1 em Z_3^v com y[j][k] palavras de prefixo (j,k)?

É o subproblema (2.3) de Linderoth–Margot–Thain 2009, com as cotas de fibra de todas as
coordenadas como restrições extras (válidas para qualquer código, ver README). Duas saídas:

* ``cnf(v, y, p)`` -> (num_vars, cláusulas): CNF para CaDiCaL --lrat (prova conferível);
* ``cpsat(v, y, p, tempo)`` -> "SAT" | "UNSAT" | "DESCONHECIDO" (sem certificado, só medição).
"""
from __future__ import annotations

import itertools

from pysat.card import CardEnc, EncType


def palavras(v: int) -> list[tuple[int, ...]]:
    return list(itertools.product(range(3), repeat=v))


def bola(v: int, w: tuple[int, ...]) -> list[tuple[int, ...]]:
    b = [w]
    for i in range(v):
        for a in range(3):
            if a != w[i]:
                b.append(w[:i] + (a,) + w[i + 1:])
    return b


def _indice(v: int) -> dict[tuple[int, ...], int]:
    return {w: i + 1 for i, w in enumerate(palavras(v))}


def cnf(v: int, y: list[int], p: int = 0) -> tuple[int, list[list[int]]]:
    """CNF do y-SIP. Variável i+1 = palavra i (ordem lexicográfica) está no código.

    Restrições: cobertura (uma cláusula por ponto), contagem exata por bloco de prefixo
    (j,k) e, se p > 0, toda fibra (coordenada i >= 2, símbolo a) com pelo menos p palavras.
    As fibras das coordenadas 0 e 1 já são somas de linhas/colunas de y.
    """
    idx = _indice(v)
    cls: list[list[int]] = [[idx[u] for u in bola(v, w)] for w in palavras(v)]
    top = 3 ** v
    for j in range(3):
        for k in range(3):
            lits = [idx[w] for w in palavras(v) if w[0] == j and w[1] == k]
            enc = CardEnc.equals(lits=lits, bound=y[3 * j + k], top_id=top, encoding=EncType.seqcounter)
            if enc.nv > top:
                top = enc.nv
            cls.extend(enc.clauses)
    if p > 0:
        for i in range(2, v):
            for a in range(3):
                lits = [idx[w] for w in palavras(v) if w[i] == a]
                enc = CardEnc.atleast(lits=lits, bound=p, top_id=top, encoding=EncType.seqcounter)
                if enc.nv > top:
                    top = enc.nv
                cls.extend(enc.clauses)
    return top, cls


def escrever_dimacs(caminho: str, nv: int, cls: list[list[int]]) -> None:
    with open(caminho, "w") as f:
        f.write(f"p cnf {nv} {len(cls)}\n")
        for c in cls:
            f.write(" ".join(map(str, c)) + " 0\n")


def cpsat(v: int, y: list[int], p: int = 0, tempo: float = 60.0, nucleos: int = 1) -> tuple[str, float]:
    from ortools.sat.python import cp_model

    W = palavras(v)
    m = cp_model.CpModel()
    x = {w: m.NewBoolVar("") for w in W}
    for w in W:
        m.AddBoolOr([x[u] for u in bola(v, w)])
    for j in range(3):
        for k in range(3):
            m.Add(sum(x[w] for w in W if w[0] == j and w[1] == k) == y[3 * j + k])
    if p > 0:
        for i in range(2, v):
            for a in range(3):
                m.Add(sum(x[w] for w in W if w[i] == a) >= p)
    s = cp_model.CpSolver()
    s.parameters.max_time_in_seconds = tempo
    s.parameters.num_workers = nucleos
    st = s.Solve(m)
    nome = {cp_model.OPTIMAL: "SAT", cp_model.FEASIBLE: "SAT", cp_model.INFEASIBLE: "UNSAT"}.get(st, "DESCONHECIDO")
    return nome, s.WallTime()


# --- quebra de simetria (lex-leader) -------------------------------------------------------
#
# Para uma permutação pi das palavras que preserva o y-SIP, x <=lex x∘pi vale no menor
# elemento lexicográfico de cada órbita; logo acrescentar essas cláusulas para qualquer
# conjunto de automorfismos não perde nenhuma classe de códigos (Crawford et al. 1996).


def _estab_y(y: list[int]) -> list[tuple[tuple[int, ...], tuple[int, ...], int]]:
    """Elementos (r, s, t) do grupo de ordem 72 do prefixo que fixam y (sem a identidade)."""
    out = []
    for r in itertools.permutations(range(3)):
        for s in itertools.permutations(range(3)):
            for t in (0, 1):
                if r == (0, 1, 2) and s == (0, 1, 2) and t == 0:
                    continue
                z = [0] * 9
                for j in range(3):
                    for k in range(3):
                        jj, kk = r[j], s[k]
                        if t:
                            jj, kk = kk, jj
                        z[3 * jj + kk] = y[3 * j + k]
                if z == list(y):
                    out.append((r, s, t))
    return out


def _prefixo(r, s, t):
    def g(w):
        jj, kk = r[w[0]], s[w[1]]
        if t:
            jj, kk = kk, jj
        return (jj, kk) + w[2:]
    return g


def automorfismos(v: int, y: list[int]) -> list[dict[tuple[int, ...], tuple[int, ...]]]:
    """Automorfismos do y-SIP usados no lex-leader, como mapas palavra -> palavra.

    Sufixo (coordenadas 2..v-1): transposições de coordenadas vizinhas e de símbolos em cada
    coordenada. Prefixo: o estabilizador de y no grupo de ordem 72.
    """
    W = palavras(v)
    perms = []
    for i in range(2, v - 1):
        perms.append({w: w[:i] + (w[i + 1], w[i]) + w[i + 2:] for w in W})
    for i in range(2, v):
        for a, b in ((0, 1), (1, 2), (0, 2)):
            tr = {a: b, b: a}
            perms.append({w: w[:i] + (tr.get(w[i], w[i]),) + w[i + 1:] for w in W})
    for r, s, t in _estab_y(y):
        g = _prefixo(r, s, t)
        perms.append({w: g(w) for w in W})
    return perms


def lex_leader(v: int, perms, top: int) -> tuple[int, list[list[int]]]:
    """Cláusulas de x <=lex x∘pi para cada pi (cadeia de igualdade de prefixo)."""
    idx = _indice(v)
    W = palavras(v)
    cls: list[list[int]] = []
    for pi in perms:
        e = None  # literal "prefixo igual até aqui"; None = verdadeiro
        for w in W:
            a, b = idx[w], idx[pi[w]]
            if a == b:
                continue
            pre = [] if e is None else [-e]
            cls.append(pre + [-a, b])
            top += 1
            cls.append(pre + [a, b, top])
            cls.append(pre + [-a, -b, top])
            e = top
    return top, cls


def cnf_sb(v: int, y: list[int], p: int = 0) -> tuple[int, list[list[int]]]:
    nv, cls = cnf(v, y, p)
    nv, sb = lex_leader(v, automorfismos(v, y), nv)
    return nv, cls + sb
