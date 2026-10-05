#!/usr/bin/env python3
"""Red team K_3(6,2), M = 15: verificador de Farkas mínimo, escrito do zero.

Não importa nada do gerador (`certificar_lp.py`) nem do verificador do PR (`verificar.py`), nem de
`tools/exatos/gaps2`. Lê a instância (s*, K, t), monta as restrições do OPB da fatia mínima como
listas explícitas de coeficientes (dicionários), soma y·linha + mu·igualdade em `Fraction` e
confere, para cada folha da árvore:

    y_k inteiro >= 0 (só linhas ">=") ;  mu inteiro livre (linhas "=")
    lado direito combinado  >  max_{z na caixa} (coeficientes combinados)·z

A caixa é [0,1] por variável, com a fatia 0 fixada pela instância e as fixações do ramo. Caixa
vazia = folha vazia (nada a provar). A completude da árvore é conferida SEMANTICAMENTE: toda
atribuição 0/1 das variáveis ramificadas cai em pelo menos uma folha (enumeração explícita).

Convenção de índices do certificado (do formato do PR #57): linha k < q^n é a cobertura do ponto de
índice k na ordem de itertools.product; linha q^n + (j-1)·q + a é a fibra (j, a), j >= 1; mu =
[tamanho, bloco 1, ..., bloco q-1].
"""
import argparse
import gzip
import hashlib
import itertools
import json
import sys
from fractions import Fraction


_BOLAS = {}


class Sistema:
    """Restrições da instância como (coef: dict ponto->int, sentido, rhs)."""

    def __init__(self, q, n, R, M, s, K, t):
        self.q, self.n, self.R, self.M, self.s = q, n, R, M, s
        self.pts = [tuple(p) for p in itertools.product(range(q), repeat=n)]
        self.idx = {p: i for i, p in enumerate(self.pts)}
        self.K = {(0,) + tuple(k) for k in K}
        assert len(self.K) == s == len(K), "K precisa ter s pontos distintos"
        self.t = tuple(t)
        assert len(self.t) == q - 1 and sum(self.t) == M - s

    def linha_ge(self, k):
        """Linha ">=" de índice k (cobertura ou fibra)."""
        q, n, N = self.q, self.n, len(self.pts)
        if k < N:
            chave = (q, n, self.R, k)
            if chave not in _BOLAS:  # cache só de desempenho: a bola não depende da instância
                x = self.pts[k]
                _BOLAS[chave] = {c: 1 for c in self.pts if sum(a != b for a, b in zip(c, x)) <= self.R}
            return dict(_BOLAS[chave]), 1
        r = k - N
        if self.s == 0 or r >= (n - 1) * q:
            raise ValueError(f"linha {k} não existe")
        j, a = 1 + r // q, r % q
        return {c: 1 for c in self.pts if c[j] == a}, self.s

    def linha_eq(self, i):
        if i == 0:
            return {c: 1 for c in self.pts}, self.M
        return {c: 1 for c in self.pts if c[0] == i}, self.t[i - 1]

    def caixa(self, fixos):
        """Limites [lo, hi] por ponto; None se a caixa é vazia."""
        lo = {c: 0 for c in self.pts}
        hi = {c: 1 for c in self.pts}
        for c in self.pts:
            if c[0] == 0:
                v = 1 if c in self.K else 0
                lo[c] = hi[c] = v
        for k, v in fixos:
            if v not in (0, 1):
                raise ValueError("fixação fora de {0,1}")
            c = self.pts[k]
            lo[c], hi[c] = max(lo[c], v), min(hi[c], v)
            if lo[c] > hi[c]:
                return None
        return lo, hi


def folga(sis, folha):
    """(lado direito combinado) - max(coef·z na caixa). > 0 = folha inviável. None = caixa vazia."""
    cx = sis.caixa(folha["fixos"])
    if cx is None:
        return None
    lo, hi = cx
    coef = {c: Fraction(0) for c in sis.pts}
    rhs = Fraction(0)
    for k, v in folha["y"].items():
        if type(v) is not int or v < 0:
            raise ValueError(f"y[{k}] = {v!r} não é inteiro >= 0")
        linha, b = sis.linha_ge(int(k))
        for c, a in linha.items():
            coef[c] += v * a
        rhs += v * b
    mu = folha["mu"]
    if len(mu) != sis.q or any(type(v) is not int for v in mu):
        raise ValueError("mu inválido")
    for i, v in enumerate(mu):
        linha, b = sis.linha_eq(i)
        for c, a in linha.items():
            coef[c] += v * a
        rhs += v * b
    melhor = sum(max(coef[c] * lo[c], coef[c] * hi[c]) for c in sis.pts)
    return rhs - melhor


def arvore_cobre(fixos_por_folha):
    """Toda atribuição 0/1 das variáveis ramificadas satisfaz as fixações de alguma folha.

    Conferência semântica, sem supor estrutura de árvore: as folhas são cubos (atribuições
    parciais) e a pergunta é se a união deles é {0,1}^vars. Divide-se por uma variável que aparece
    em algum cubo e se recursa nos dois lados com os cubos compatíveis; um cubo sem fixações cobre
    tudo, e nenhum cubo não cobre nada. É exato (equivale a enumerar as atribuições), mas não
    explode com árvores de 30+ variáveis distintas, como as de M = 16.
    """
    cubos = []
    for f in fixos_por_folha:
        c = {}
        for k, v in f:
            if c.get(k, v) != v:
                c = None  # folha contraditória: cubo vazio, não cobre nada
                break
            c[k] = v
        if c is not None:
            cubos.append(c)

    def cobre(cs):
        if any(not c for c in cs):
            return True
        if not cs:
            return False
        var = next(iter(cs[0]))
        return all(cobre([{k: w for k, w in c.items() if k != var} for c in cs if c.get(var, b) == b])
                   for b in (0, 1))

    return cobre(cubos)


def conferir_registro(q, n, R, M, inst, reg):
    s, K, t = inst
    if [reg["s"], reg["K"], reg["t"]] != [s, K, t] or not reg.get("folhas"):
        return False, "registro não corresponde à instância"
    if not arvore_cobre([f["fixos"] for f in reg["folhas"]]):
        return False, "árvore incompleta"
    sis = Sistema(q, n, R, M, s, K, t)
    for f in reg["folhas"]:
        try:
            g = folga(sis, f)
        except (ValueError, AssertionError) as e:
            return False, str(e)
        if g is not None and g <= 0:
            return False, f"folga {g} <= 0"
    return True, "ok"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    for k, v in (("q", 3), ("n", 6), ("R", 2), ("M", 15)):
        ap.add_argument("--" + k, type=int, default=v)
    ap.add_argument("--instancias", required=True)
    ap.add_argument("--certificados", required=True)
    ap.add_argument("--sha256")
    a = ap.parse_args()
    bruto = open(a.instancias, "rb").read()
    print("sha256 da lista:", hashlib.sha256(bruto).hexdigest())
    if a.sha256 and hashlib.sha256(bruto).hexdigest() != a.sha256:
        sys.exit("sha256 não confere")
    ins = json.loads(bruto)
    vistos, ruins, folhas = set(), [], 0
    for linha in gzip.open(a.certificados, "rt"):
        reg = json.loads(linha)
        i = reg["inst"]
        if i in vistos or not 0 <= i < len(ins):
            ruins.append((i, "índice repetido ou fora da lista"))
            continue
        vistos.add(i)
        ok, msg = conferir_registro(a.q, a.n, a.R, a.M, ins[i], reg)
        folhas += len(reg.get("folhas") or [])
        if not ok:
            ruins.append((i, msg))
    faltam = set(range(len(ins))) - vistos
    ok = not ruins and not faltam
    print(f"{len(vistos)} de {len(ins)} instâncias, {folhas} folhas, recusadas {ruins[:10]}, "
          f"faltam {sorted(faltam)[:10]} -> {'TODAS INVIÁVEIS' if ok else 'FALHOU'}")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
