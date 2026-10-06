"""Codificação booleana de "existe C ⊆ Z_q^n com |C| ≤ M e R_2(C) ≤ r".

Formulação por projeções (equivalente à definição): R_2(C) ≤ r se e só se, para todo par
(u1,u2), existe um conjunto S de n−r coordenadas tal que u1|_S e u2|_S são ambos projeções de
palavras de C em S. (Se c1 concorda com u1 em S e c2 concorda com u2 em S, a união dos suportes
cabe no complemento de S, que tem r coordenadas; e vice-versa, o complemento da união contém
algum S com n−r elementos.)

Variáveis:
* x_c   — a palavra c está em C (c = 0..q^n−1, índice na base q);
* y_S,a — o padrão a ∈ Z_q^S aparece na projeção de C em S (só a implicação y → ∨ x é usada);
* z_S,ab — os padrões a e b (par não ordenado) aparecem ambos em S (z → y_a, z → y_b).

Cláusulas de cobertura: para cada par não ordenado {u1,u2} (inclusive u1 = u2),
∨_S z_{S, u1|S, u2|S}. Só as implicações "para baixo" (z → y → x) são necessárias: elas garantem
que toda atribuição satisfatória descreve um código que cobre, e todo código que cobre se estende
a uma atribuição satisfatória. Logo SAT/UNSAT da fórmula responde exatamente a pergunta.
"""
from __future__ import annotations

from itertools import combinations


class Codificacao:
    def __init__(self, q: int, n: int, r: int, fixar_zero: bool = False):
        if not 0 <= r < n:
            raise ValueError("a codificação é para 0 ≤ r < n (r ≥ n é trivial: |C| = 1)")
        self.q, self.n, self.r = q, n, r
        self.N = q**n
        self.prox = self.N + 1  # x_c = c + 1
        self.clausulas: list[list[int]] = []
        k = n - r
        self.conjuntos = list(combinations(range(n), k))
        # índice c ↔ tupla com coordenada i = dígito i da base q (igual a raio2.de_inteiros)
        palavras = [tuple((c // q**i) % q for i in range(n)) for c in range(self.N)]
        self.palavras = palavras
        self.y: dict[tuple, int] = {}
        self.z: dict[tuple, int] = {}
        for S in self.conjuntos:
            grupos: dict[tuple, list[int]] = {}
            for c, w in enumerate(palavras):
                grupos.setdefault(tuple(w[i] for i in S), []).append(c + 1)
            for a, xs in grupos.items():
                v = self._nova()
                self.y[(S, a)] = v
                self.clausulas.append([-v] + xs)
        for u1i in range(self.N):
            for u2i in range(u1i, self.N):
                u1, u2 = palavras[u1i], palavras[u2i]
                cl = []
                for S in self.conjuntos:
                    a = tuple(u1[i] for i in S)
                    b = tuple(u2[i] for i in S)
                    cl.append(self._z(S, a, b))
                self.clausulas.append(cl)
        if fixar_zero:
            self.clausulas.append([1])

    def _nova(self) -> int:
        v = self.prox
        self.prox += 1
        return v

    def _z(self, S, a, b) -> int:
        if a == b:
            return self.y[(S, a)]
        chave = (S, min(a, b), max(a, b))
        v = self.z.get(chave)
        if v is None:
            v = self._nova()
            self.z[chave] = v
            self.clausulas.append([-v, self.y[(S, a)]])
            self.clausulas.append([-v, self.y[(S, b)]])
        return v

    @property
    def nvars(self) -> int:
        return self.prox - 1

    def codigo_de(self, modelo) -> list[int]:
        pos = {v for v in modelo if v > 0}
        return [c for c in range(self.N) if c + 1 in pos]

    # --- quebra de simetria (lex-leader) ---------------------------------------------------
    def permutacao_palavras(self, perm_coord, perm_simb) -> list[int]:
        """Imagem de cada palavra sob g: coordenada i vai para perm_coord[i], com o símbolo
        trocado por perm_simb[i]. É isometria do 2-peso (aplicada às duas linhas ao mesmo tempo),
        logo preserva R_2."""
        q, n = self.q, self.n
        img = []
        for w in self.palavras:
            v = [0] * n
            for i in range(n):
                v[perm_coord[i]] = perm_simb[i][w[i]]
            img.append(sum(v[i] * q**i for i in range(n)))
        return img

    def geradores(self) -> list[list[int]]:
        """Transposições de coordenadas e transposições de símbolos numa coordenada."""
        q, n = self.q, self.n
        ident = [list(range(q)) for _ in range(n)]
        gs = []
        for i in range(n):
            for j in range(i + 1, n):
                pc = list(range(n))
                pc[i], pc[j] = j, i
                gs.append(self.permutacao_palavras(pc, ident))
        for i in range(n):
            for a in range(q):
                for b in range(a + 1, q):
                    ps = [list(range(q)) for _ in range(n)]
                    ps[i][a], ps[i][b] = b, a
                    gs.append(self.permutacao_palavras(list(range(n)), ps))
        return gs

    def quebrar_simetria(self, extras: int = 0, semente: int = 0) -> int:
        """Acrescenta x ≥_lex g(x) para cada gerador g (e ``extras`` produtos aleatórios).

        Ordem lexicográfica: x_0, x_1, ... (palavra 0 primeiro). Correção: em toda órbita sob o
        grupo de automorfismos do espaço de Hamming, o vetor lexicograficamente máximo satisfaz
        x ≥_lex g(x) para TODO g do grupo ao mesmo tempo; logo, se existe código bom de tamanho
        ≤ M, existe um que satisfaz todas as restrições acrescentadas (Crawford, Ginsberg, Luks e
        Roy, KR 1996). Devolve quantas restrições entraram.
        """
        import random

        gs = self.geradores()
        rng = random.Random(semente)
        base = list(gs)
        for _ in range(extras):
            a, b = rng.choice(base), rng.choice(base)
            gs.append([a[b[c]] for c in range(self.N)])
        vistos = set()
        for g in gs:
            t = tuple(g)
            if t in vistos or all(g[c] == c for c in range(self.N)):
                continue
            vistos.add(t)
            self._lex_maior_igual(g)
        return len(vistos)

    def _lex_maior_igual(self, g):
        # Compara x com o vetor (x_{g(k)})_k, que é o indicador de g^{-1}(C). Vale para qualquer
        # elemento do grupo, e g^{-1} percorre o grupo junto com g, então a correção não muda.
        e_prev = None  # None = verdadeiro
        for k in range(self.N):
            a, b = k + 1, g[k] + 1
            if a == b:
                continue
            pre = [] if e_prev is None else [-e_prev]
            self.clausulas.append(pre + [a, -b])          # prefixo igual → a_k ≥ b_k
            e = self._nova()
            self.clausulas.append(pre + [-a, -b, e])      # prefixo igual e a=b=1 → continua igual
            self.clausulas.append(pre + [a, b, e])        # prefixo igual e a=b=0 → continua igual
            e_prev = e

    def dimacs(self, limite: int) -> str:
        """CNF DIMACS: as cláusulas mais Σ x_c ≤ limite (contador sequencial do PySAT)."""
        from pysat.card import CardEnc, EncType

        card = CardEnc.atmost(lits=list(range(1, self.N + 1)), bound=limite, top_id=self.nvars,
                              encoding=EncType.seqcounter)
        todas = self.clausulas + card.clauses
        nv = max([self.nvars] + [abs(v) for cl in card.clauses for v in cl])
        linhas = [f"p cnf {nv} {len(todas)}"] + [" ".join(map(str, cl)) + " 0" for cl in todas]
        return "\n".join(linhas) + "\n"

    def opb(self, limite: int | None = None) -> str:
        """Texto OPB: minimizar Σ x_c (ou, com ``limite``, Σ x_c ≤ limite sem objetivo)."""
        linhas = [f"* #variable= {self.nvars} #constraint= {len(self.clausulas) + (limite is not None)}"
                  " #equal= 0 intsize= 64"]
        xs = " ".join(f"+1 x{c + 1}" for c in range(self.N))
        if limite is None:
            linhas.append(f"min: {xs} ;")
        else:
            linhas.append(" ".join(f"-1 x{c + 1}" for c in range(self.N)) + f" >= {-limite} ;")
        for cl in self.clausulas:
            termos = " ".join(f"+1 x{v}" if v > 0 else f"+1 ~x{-v}" for v in cl)
            linhas.append(f"{termos} >= 1 ;")
        return "\n".join(linhas) + "\n"


def minimo_sat(q: int, n: int, r: int, inicio: int = 1, solver: str = "cadical195",
               fixar_zero: bool = True):
    """Menor M com código de tamanho M e R_2 ≤ r, por SAT incremental em M (sem certificado).

    Devolve (M, código como lista de índices). ``fixar_zero`` é sem perda: translação por v
    (u ↦ u + v em cada linha) é isometria do 2-peso, então todo código ótimo tem um transladado
    que contém a palavra 0.
    """
    from pysat.card import CardEnc, EncType
    from pysat.solvers import Solver

    cod = Codificacao(q, n, r, fixar_zero=fixar_zero)
    M = max(1, inicio)
    while True:
        card = CardEnc.atmost(lits=list(range(1, cod.N + 1)), bound=M, top_id=cod.nvars,
                              encoding=EncType.seqcounter)
        with Solver(name=solver, bootstrap_with=cod.clausulas + card.clauses) as s:
            if s.solve():
                codigo = cod.codigo_de(s.get_model())
                return M, codigo
        M += 1
