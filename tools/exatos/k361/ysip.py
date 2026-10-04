"""y-SIP de K_3(v,1): existe código de raio 1 em Z_3^v com y[j][k] palavras de prefixo (j,k)?

É o subproblema (2.3) de Linderoth–Margot–Thain 2009, com as cotas de fibra de todas as
coordenadas como restrições extras (válidas para qualquer código, ver README). Duas saídas:

* ``cnf(v, y, p)`` -> (num_vars, cláusulas): CNF para CaDiCaL --lrat (prova conferível);
* ``opb(v, y, p)``: o mesmo em pseudo-booleano para o RoundingSat (prova VeriPB);
* ``scip(v, y, p, tempo)``: PLI no SCIP, só medição.
"""
from __future__ import annotations

import itertools



class _Contador:
    """Contador sequencial com equivalências (sem dependências externas).

    r[i][j] <-> "pelo menos j dos i primeiros literais são verdadeiros", j = 1..K. Como todas
    as variáveis auxiliares têm semântica fixa, ``avaliar`` reconstrói a atribuição completa a
    partir de x e confere cláusula por cláusula (os testes usam isso nos dois sentidos).
    """

    def __init__(self, lits: list[int], K: int, top: int):
        self.lits, self.K, self.top = lits, K, top
        self.cls: list[list[int]] = []
        self.aux: list[tuple[int, int, int]] = []  # (var, i, j): i literais, pelo menos j
        ant = {0: True}  # j -> literal (int) ou constante bool, para i-1
        for i, x in enumerate(lits, start=1):
            cur = {0: True}
            for j in range(1, min(i, K) + 1):
                a = ant.get(j, False)      # r[i-1][j]
                b = ant.get(j - 1, False)  # r[i-1][j-1]
                self.top += 1
                r = self.top
                self.aux.append((r, i, j))
                cur[j] = r
                self._imp([a], r)
                self._imp([b, x], r)
                self._imp_ou(r, [a, x])
                self._imp_ou(r, [a, b])
            ant = cur
        self.final = ant

    def _imp(self, conj, r):
        if any(c is False for c in conj):
            return
        self.cls.append([-c for c in conj if c is not True] + [r])

    def _imp_ou(self, r, disj):
        if any(d is True for d in disj):
            return
        self.cls.append([-r] + [d for d in disj if d is not False])

    def pelo_menos(self, b: int) -> list[list[int]]:
        f = self.final.get(b, False)
        return [] if f is True else [[f]] if f is not False else [[]]

    def no_maximo(self, b: int) -> list[list[int]]:
        f = self.final.get(b + 1, False)
        return [] if f is False else [[-f]]


def _card(lits: list[int], top: int, minimo: int | None, maximo: int | None):
    K = (maximo + 1) if maximo is not None else minimo
    c = _Contador(lits, K, top)
    cls = list(c.cls)
    if minimo:
        cls += c.pelo_menos(minimo)
    if maximo is not None:
        cls += c.no_maximo(maximo)
    return c, cls


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


def _construir(v: int, y: list[int], p: int):
    idx = _indice(v)
    W = palavras(v)
    cls: list[list[int]] = [[idx[u] for u in bola(v, w)] for w in W]
    top = 3 ** v
    contadores = []
    for j in range(3):
        for k in range(3):
            lits = [idx[w] for w in W if w[0] == j and w[1] == k]
            c, cc = _card(lits, top, y[3 * j + k], y[3 * j + k])
            top = c.top
            contadores.append(c)
            cls.extend(cc)
    if p > 0:
        for i in range(2, v):
            for a in range(3):
                lits = [idx[w] for w in W if w[i] == a]
                c, cc = _card(lits, top, p, None)
                top = c.top
                contadores.append(c)
                cls.extend(cc)
    return top, cls, contadores


def cnf(v: int, y: list[int], p: int = 0) -> tuple[int, list[list[int]]]:
    """CNF do y-SIP. Variável i+1 = palavra i (ordem lexicográfica) está no código.

    Restrições: cobertura (uma cláusula por ponto), contagem exata por bloco de prefixo
    (j,k) e, se p > 0, toda fibra (coordenada i >= 2, símbolo a) com pelo menos p palavras.
    As fibras das coordenadas 0 e 1 são somas de linhas/colunas de y (vêm do sistema).
    """
    top, cls, _ = _construir(v, y, p)
    return top, cls


def escrever_dimacs(caminho: str, nv: int, cls: list[list[int]]) -> None:
    with open(caminho, "w") as f:
        f.write(f"p cnf {nv} {len(cls)}\n")
        for c in cls:
            f.write(" ".join(map(str, c)) + " 0\n")


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


def lex_leader(v: int, perms, top: int, aux: list | None = None) -> tuple[int, list[list[int]]]:
    """Cláusulas de x <=lex x∘pi para cada pi (cadeia de igualdade de prefixo).

    Ordem das variáveis: a das palavras (lexicográfica). A variável auxiliar criada na palavra
    w vale "x e x∘pi coincidem em todas as palavras até w, inclusive"; se ``aux`` é uma lista,
    recebe (var, índice de pi, posição de w) para a reconstrução em ``atribuicao``.
    """
    idx = _indice(v)
    W = palavras(v)
    cls: list[list[int]] = []
    for n, pi in enumerate(perms):
        e = None  # literal "prefixo igual até aqui"; None = verdadeiro
        for pos, w in enumerate(W):
            a, b = idx[w], idx[pi[w]]
            if a == b:
                continue
            pre = [] if e is None else [-e]
            cls.append(pre + [-a, b])
            top += 1
            cls.append(pre + [a, b, top])
            cls.append(pre + [-a, -b, top])
            if aux is not None:
                aux.append((top, n, pos))
            e = top
    return top, cls


def cnf_sb(v: int, y: list[int], p: int = 0) -> tuple[int, list[list[int]]]:
    nv, cls = cnf(v, y, p)
    nv, sb = lex_leader(v, automorfismos(v, y), nv)
    return nv, cls + sb


def atribuicao(v: int, y: list[int], p: int, codigo) -> tuple[list[list[int]], dict[int, bool]]:
    """(cláusulas de cnf_sb, atribuição completa induzida pelo código).

    As auxiliares recebem o valor da sua semântica, então uma cláusula falsa aponta um defeito
    real: ou o código viola a restrição, ou a codificação está errada.
    """
    top, cls, contadores = _construir(v, y, p)
    W = palavras(v)
    cod = set(codigo)
    val = {i + 1: (w in cod) for i, w in enumerate(W)}
    for c in contadores:
        soma = [0]
        for x in c.lits:
            soma.append(soma[-1] + val[x])
        for r, i, j in c.aux:
            val[r] = soma[i] >= j
    perms = automorfismos(v, y)
    meta: list = []
    top, sb = lex_leader(v, perms, top, meta)
    idx = _indice(v)
    igual_ate: dict[int, list[bool]] = {}
    for n, pi in enumerate(perms):
        acc, lst = True, []
        for w in W:
            acc = acc and val[idx[w]] == val[idx[pi[w]]]
            lst.append(acc)
        igual_ate[n] = lst
    for r, n, pos in meta:
        val[r] = igual_ate[n][pos]
    return cls + sb, val


def falsas(cls: list[list[int]], val: dict[int, bool]) -> list[list[int]]:
    return [c for c in cls if not any((lit > 0) == val[abs(lit)] for lit in c)]


def scip(v: int, y: list[int], p: int = 0, tempo: float = 60.0) -> tuple[str, float, int]:
    """Mesmo y-SIP como PLI no SCIP (com o tratamento de simetria padrão dele). Só medição.

    Devolve (status, segundos, nós). É o análogo moderno do branch-and-bound com poda de
    isomorfos e cota de PL de LMT 2009.
    """
    from pyscipopt import Model, quicksum

    W = palavras(v)
    m = Model()
    m.hideOutput()
    m.setParam("limits/time", tempo)
    m.setParam("parallel/maxnthreads", 1)
    x = {w: m.addVar(vtype="B") for w in W}
    for w in W:
        m.addCons(quicksum(x[u] for u in bola(v, w)) >= 1)
    for j in range(3):
        for k in range(3):
            m.addCons(quicksum(x[w] for w in W if w[0] == j and w[1] == k) == y[3 * j + k])
    if p > 0:
        for i in range(2, v):
            for a in range(3):
                m.addCons(quicksum(x[w] for w in W if w[i] == a) >= p)
    m.optimize()
    st = m.getStatus()
    nome = {"infeasible": "UNSAT", "optimal": "SAT", "timelimit": "TEMPO"}.get(st, st.upper())
    return nome, m.getSolvingTime(), m.getNNodes()


def opb(v: int, y: list[int], p: int = 0, sb: bool = True) -> str:
    """O y-SIP em OPB (pseudo-booleano linear) para solvers de planos de corte (RoundingSat).

    Contagens e fibras ficam como restrições lineares nativas (sem contador); a cobertura e o
    lex-leader entram como cláusulas.
    """
    idx = _indice(v)
    W = palavras(v)
    linhas: list[str] = []

    def lit(n: int) -> str:
        return f"x{n}" if n > 0 else f"~x{-n}"
    for w in W:
        linhas.append(" ".join(f"+1 {lit(idx[u])}" for u in bola(v, w)) + " >= 1 ;")
    for j in range(3):
        for k in range(3):
            t = " ".join(f"+1 x{idx[w]}" for w in W if w[0] == j and w[1] == k)
            linhas.append(f"{t} = {y[3 * j + k]} ;")
    if p > 0:
        for i in range(2, v):
            for a in range(3):
                linhas.append(" ".join(f"+1 x{idx[w]}" for w in W if w[i] == a) + f" >= {p} ;")
    nv = 3 ** v
    if sb:
        nv, cls = lex_leader(v, automorfismos(v, y), nv)
        for c in cls:
            linhas.append(" ".join(f"+1 {lit(t)}" for t in c) + " >= 1 ;")
    neq = sum(1 for ln in linhas if " = " in ln)
    # cabeçalho completo: o log de prova do RoundingSat exige #equal= e intsize=
    return (f"* #variable= {nv} #constraint= {len(linhas)} #equal= {neq} intsize= 64\n"
            + "\n".join(linhas) + "\n")
