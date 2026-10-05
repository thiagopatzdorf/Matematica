#!/usr/bin/env python3
"""As relações do GNFS como objeto de estudo: ideais, descasque de singletons e núcleo por prefixo.

    python3 tools/fatoracao/relacoes.py validar <captura>      # reproduz o purge do CADO a partir da captura

Lê a captura de `captura_relacoes.py` (nunca a pasta do CADO). Duas decisões que valem o instrumento inteiro:

* **Coluna é ideal, não primo.** No lado algébrico a relação lista só `p`, mas o ideal é o par `(p, raiz)` com
  `raiz = a * b^-1 mod p` (`raiz = p` para o ponto no infinito, quando `p | b`). Tratar só `p` como coluna funde ideais
  distintos e fabrica colisões que não existem. A prova de que a identidade está certa é exata: o descasque daqui tem de
  parar nas mesmas linhas e colunas que o `purge` do CADO.
* **Relações livres** entram como linhas: para cada primo `p` em que `f` tem todas as raízes, o ideal racional `(0, p)` e os
  `deg f` ideais algébricos `(1, p, r)`.
"""
import gzip
import json
import random
import sys
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

# ---------- polinômios módulo p ----------


def ler_poly(texto):
    """`{f: [c0..cd], Y0, Y1}` do arquivo de polinômio do CADO (poly1 = f algébrico, poly0 = g racional)."""
    campos = {}
    for linha in texto.splitlines():
        if ":" in linha and not linha.startswith("#"):
            k, v = linha.split(":", 1)
            campos[k.strip()] = v.strip()
    f = []
    while f"c{len(f)}" in campos:
        f.append(int(campos[f"c{len(f)}"]))
    return {"f": f, "Y0": int(campos["Y0"]), "Y1": int(campos["Y1"])}


def _trim(a):
    while a and a[-1] == 0:
        a.pop()
    return a


def _mod(a, f, p):
    """`a mod f` em Z/p (f mônico)."""
    a = a[:]
    d = len(f) - 1
    while len(a) - 1 >= d and a:
        c = a[-1]
        if c:
            k = len(a) - 1 - d
            for i, fi in enumerate(f):
                a[k + i] = (a[k + i] - c * fi) % p
        a.pop()
    return _trim(a)


def _mul(a, b, f, p):
    if not a or not b:
        return []
    r = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        if x:
            for j, y in enumerate(b):
                r[i + j] = (r[i + j] + x * y) % p
    return _mod(_trim(r), f, p)


def _pow(base, e, f, p):
    r, b = [1], _mod(base, f, p)
    while e:
        if e & 1:
            r = _mul(r, b, f, p)
        b = _mul(b, b, f, p)
        e >>= 1
    return r


def _gcd(a, b, p):
    a, b = _trim(a[:]), _trim(b[:])
    while b:
        inv = pow(b[-1], -1, p)
        b = [(x * inv) % p for x in b]
        a = _mod_geral(a, b, p)
        a, b = b, a
    return a


def _mod_geral(a, b, p):
    """`a mod b` com b mônico (resto da divisão)."""
    a = a[:]
    d = len(b) - 1
    while len(a) - 1 >= d and a:
        c = a[-1]
        if c:
            k = len(a) - 1 - d
            for i, bi in enumerate(b):
                a[k + i] = (a[k + i] - c * bi) % p
        a.pop()
    return _trim(a)


def _dividir(a, b, p):
    """Quociente de a por b (b mônico), a divisível por b."""
    a, q = a[:], [0] * (len(a) - len(b) + 1)
    d = len(b) - 1
    for k in range(len(a) - 1 - d, -1, -1):
        c = a[k + d]
        q[k] = c
        for i, bi in enumerate(b):
            a[k + i] = (a[k + i] - c * bi) % p
    return q


def raizes_mod_p(f, p, semente=0):
    """Raízes de `f` em Z/p (distintas), por Cantor-Zassenhaus. Para p pequeno, força bruta."""
    f = _trim([c % p for c in f])
    if not f:
        raise ValueError("polinômio nulo módulo p")
    if p < 200 or len(f) <= 1:
        return [x for x in range(p) if sum(c * pow(x, i, p) for i, c in enumerate(f)) % p == 0]
    inv = pow(f[-1], -1, p)
    f = [(c * inv) % p for c in f]
    xp = _pow([0, 1], p, f, p)
    dif = _trim([(xp[i] if i < len(xp) else 0) - (1 if i == 1 else 0) for i in range(max(len(xp), 2))])
    dif = [c % p for c in dif]
    g = _gcd(f, dif, p) if dif else f  # produto dos fatores lineares distintos
    rng = random.Random(semente + p)

    def separar(h):
        if len(h) <= 1:
            return []
        if len(h) == 2:
            return [(-h[0] * pow(h[1], -1, p)) % p]
        while True:
            a = rng.randrange(p)
            t = _pow([a, 1], (p - 1) // 2, h, p)
            t = [c % p for c in t] + [0] * (1 - len(t))
            t[0] = (t[0] - 1) % p
            d = _gcd(h, _trim(t), p)
            if 1 < len(d) < len(h):
                return separar(d) + separar(_dividir(h, d, p))

    return sorted(separar(g))


# ---------- leitura da captura ----------


@dataclass
class Dados:
    n_brutas: int
    n_unicas: int
    n_livres: int
    n_ideais: int
    bloco: np.ndarray            # por relação bruta: índice do bloco
    q: np.ndarray                # special-q de cada relação bruta
    a: np.ndarray
    b: np.ndarray
    eh_dup: np.ndarray           # a (a,b) já tinha aparecido antes na ordem canônica
    unica_de: np.ndarray         # por relação bruta: índice da relação única correspondente
    ptr: np.ndarray              # CSR das colunas por linha: únicas e depois livres (ideais distintos, expoente ignorado)
    col: np.ndarray
    pptr: np.ndarray             # CSR só dos ideais com expoente ímpar (a matriz módulo 2 de verdade)
    pcol: np.ndarray
    ideal_lado: np.ndarray
    ideal_p: np.ndarray
    n_sq_bloco: list = field(default_factory=list)
    cpu_bloco: list = field(default_factory=list)
    fim_bloco: np.ndarray = None  # índice bruto (exclusivo) onde cada bloco termina
    manifesto: dict = field(default_factory=dict)
    ideais_ruins_conhecidos: bool = False  # `badideais.txt` presente: sem ele, ideal ruim vira uma coluna só
    inercias_conhecidas: bool = False  # `inercias.txt` presente (arquivo vazio = calculado, nenhuma inércia excepcional)
    livres_discrepantes: list = field(default_factory=list)  # primos de relações livres com ideal ruim (ver `carregar`)


def ler_badideais(texto):
    """`<nome>.badidealinfo` do CADO -> {(p, r): [(k, rk, v)]}: os ramos de cada ideal ruim `(p, r)`.

    Linha de dados: `p k rk lado v_1 ... v_nbad`. O CADO troca a coluna única de um ideal ruim por `nbad` colunas e escolhe o
    ramo pela classe de `(a:b)` módulo `p^k`; `v_j >= 0` é o expoente fixo na coluna j e `v_j < 0` vale `e + v_j`, com `e` o
    expoente de `p` na relação (utils/renumber.cpp, `indices_from_p_a_b`). `r` (classe comum aos ramos) é `p` para o ponto no infinito.
    """
    ruins = {}
    for linha in texto.splitlines():
        if not linha.strip() or linha.lstrip().startswith("#"):
            continue
        p, k, rk, lado, *v = (int(x) for x in linha.split())
        r = rk % p if rk < p ** k else p
        ruins.setdefault((p, r), []).append((k, rk, v))
    return ruins


def ler_inercias(texto):
    """Saída de `cado/inercia.cpp` -> {(p, r): inércia} dos ideais algébricos com inércia != 1 (linha: `lado p r inercia`)."""
    saida = {}
    for linha in texto.splitlines():
        if linha.strip():
            lado, p, r, f = (int(x) for x in linha.split())
            if lado == 1:
                saida[(p, r)] = f
    return saida


def colunas_do_ideal_ruim(ramos, p, a, b, e):
    """[(j, expoente)] das colunas do ideal ruim para a relação `(a, b)` com `p^e` no lado algébrico."""
    for k, rk, v in ramos:
        pk = p ** k
        u, w = (rk, 1) if rk < pk else (1, rk - pk)
        if (a * w - b * u) % pk == 0:
            return [(j, x if x >= 0 else e + x) for j, x in enumerate(v)]
    raise ValueError(f"(a,b)=({a},{b}) não cai em nenhum ramo do ideal ruim p={p}")


def carregar(pasta, com_livres=True):
    """Lê a captura. Ideais: `(0, p)` no lado racional e `(1, p, raiz)` no algébrico."""
    pasta = Path(pasta)
    man = json.loads((pasta / "manifest.json").read_text(encoding="utf-8"))
    poly = ler_poly((pasta / "poly.txt").read_text(encoding="utf-8"))
    arqs = json.loads((pasta / "arquivos.json").read_text(encoding="utf-8"))
    arq_ruins = pasta / "badideais.txt"
    ruins = ler_badideais(arq_ruins.read_text(encoding="utf-8")) if arq_ruins.is_file() else {}
    arq_inercias = pasta / "inercias.txt"
    inercias = ler_inercias(arq_inercias.read_text(encoding="utf-8")) if arq_inercias.is_file() else {}
    ids, lado_l, p_l = {}, [], []

    def ideal(chave):
        i = ids.get(chave)
        if i is None:
            i = ids[chave] = len(ids)
            lado_l.append(chave[0])
            p_l.append(chave[1])
        return i

    bloco, q, a, b, dup, uniq = [], [], [], [], [], []
    vistos, ptr, col, pptr, pcol = {}, [0], [], [0], []
    with gzip.open(pasta / "relacoes.tsv.gz", "rt", encoding="utf-8") as fh:
        for linha in fh:
            if linha[0] == "#":
                continue
            _, k, qq, _, aa, bb, s0, s1 = linha.rstrip("\n").split("\t")
            aa, bb = int(aa), int(bb)
            bloco.append(int(k))
            q.append(int(qq))
            a.append(aa)
            b.append(bb)
            u = vistos.get((aa, bb))
            if u is not None:
                dup.append(True)
                uniq.append(u)
                continue
            u = vistos[(aa, bb)] = len(vistos)
            dup.append(False)
            uniq.append(u)
            exp = {}
            for t in s0.split(","):
                chave = (0, int(t, 16), 0)
                exp[chave] = exp.get(chave, 0) + 1
            for t in s1.split(","):
                pr = int(t, 16)
                raiz = pr if bb % pr == 0 else (aa * pow(bb, -1, pr)) % pr
                chave = (1, pr, raiz)
                exp[chave] = exp.get(chave, 0) + 1
            for chave, e in exp.items():
                if chave[0] == 1 and (chave[1], chave[2]) in ruins:
                    for j, x in colunas_do_ideal_ruim(ruins[(chave[1], chave[2])], chave[1], aa, bb, e):
                        if x > 0:
                            i = ideal(chave + (j,))
                            col.append(i)
                            if x & 1:
                                pcol.append(i)
                    continue
                if chave[0] == 1 and (chave[1], chave[2]) in inercias:
                    # o dup2 divide o expoente pela inércia do ideal (renumber.cpp, `inertia_from_p_r`): p^2 | lc(f), por exemplo
                    f_in = inercias[(chave[1], chave[2])]
                    if e % f_in:
                        raise ValueError(f"expoente {e} de p={chave[1]} não é múltiplo da inércia {f_in}")
                    e //= f_in
                i = ideal(chave)
                col.append(i)
                if e & 1:
                    pcol.append(i)
            ptr.append(len(col))
            pptr.append(len(pcol))
    n_unicas, n_livres, discrepantes = len(vistos), 0, []
    if com_livres:
        with gzip.open(pasta / "livres.tsv.gz", "rt", encoding="utf-8") as fh:
            for linha in fh:
                if linha[0] == "#":
                    continue
                pr, n_idx = (int(x) for x in linha.split("\t"))
                raizes = raizes_mod_p(poly["f"], pr)
                chaves = [(0, pr, 0)]
                if poly["f"][-1] % pr == 0:  # p | lc(f): o ponto no infinito é mais um ideal acima de p (coluna da relação livre)
                    raizes = list(raizes) + [pr]
                for r in raizes:
                    if (pr, r) in ruins:  # relação livre: todas as colunas do ideal ruim, cada uma com expoente 1
                        chaves += [(1, pr, r, j) for j in range(len(ruins[(pr, r)][0][2]))]
                    else:
                        chaves.append((1, pr, r))
                if len(chaves) != n_idx:
                    # o CADO lista mais ou menos índices do que o modelo prevê: o caso é contado, nunca escondido.
                    discrepantes.append(pr)
                for chave in chaves:
                    col.append(ideal(chave))
                    pcol.append(ids[chave])
                ptr.append(len(col))
                pptr.append(len(pcol))
                n_livres += 1
    fim, acc = [], 0
    for x in arqs:
        acc += x["n_relacoes"]
        fim.append(acc)
    return Dados(
        n_brutas=len(bloco), n_unicas=n_unicas, n_livres=n_livres, n_ideais=len(ids),
        bloco=np.array(bloco, dtype=np.int32), q=np.array(q, dtype=np.int64), a=np.array(a, dtype=np.int64),
        b=np.array(b, dtype=np.int64), eh_dup=np.array(dup, dtype=bool), unica_de=np.array(uniq, dtype=np.int64),
        ptr=np.array(ptr, dtype=np.int64), col=np.array(col, dtype=np.int64), pptr=np.array(pptr, dtype=np.int64),
        pcol=np.array(pcol, dtype=np.int64), ideal_lado=np.array(lado_l, dtype=np.int8), ideal_p=np.array(p_l, dtype=np.int64),
        n_sq_bloco=[x["n_sq"] for x in arqs], cpu_bloco=[x["cpu_s"] for x in arqs], fim_bloco=np.array(fim, dtype=np.int64),
        manifesto=man, livres_discrepantes=discrepantes, ideais_ruins_conhecidos=arq_ruins.is_file(),
        inercias_conhecidas=arq_inercias.is_file())


# ---------- descasque de singletons ----------


def _linhas_do_csr(ptr):
    return np.repeat(np.arange(len(ptr) - 1), np.diff(ptr))


def descascar(ptr, col, n_cols, ativas):
    """Remoção de singletons até o ponto fixo: tira a linha que tem uma coluna presente em exatamente uma linha ativa.

    `ativas` é a máscara das linhas que entram. Devolve `(vivas, iteracoes)`. O ponto fixo é único, então a ordem de remoção
    não muda o resultado.
    """
    lin = _linhas_do_csr(ptr)
    vivas = ativas.copy()
    it = 0
    while True:
        m = vivas[lin]
        peso = np.bincount(col[m], minlength=n_cols)
        ruim = np.zeros(len(vivas), dtype=bool)
        ruim[lin[m & (peso[col] == 1)]] = True
        if not ruim.any():
            return vivas, it
        vivas &= ~ruim
        it += 1


def estatisticas(ptr, col, n_cols, vivas):
    lin = _linhas_do_csr(ptr)
    m = vivas[lin]
    cols = int((np.bincount(col[m], minlength=n_cols) > 0).sum())
    linhas = int(vivas.sum())
    return {"linhas": linhas, "colunas": cols, "excesso": linhas - cols}


def mascara_prefixo(dados, t_brutas):
    """Linhas ativas depois de `t_brutas` relações brutas: as únicas já vistas e todas as livres (não vêm do crivo)."""
    u = int((~dados.eh_dup[:t_brutas]).sum())
    ativas = np.zeros(len(dados.ptr) - 1, dtype=bool)
    ativas[:u] = True
    ativas[dados.n_unicas:] = True
    return ativas, u


def nucleo(dados, t_brutas=None, modo="paridade"):
    """Núcleo (descasque de singletons) do prefixo de `t_brutas` relações.

    `modo`: `paridade` (como o CADO: o dup2 guarda só os expoentes ímpares, `pe.e &= 1`) ou `ocorrencia` (suporte, expoente par incluído).
    """
    t = dados.n_brutas if t_brutas is None else t_brutas
    ativas, _ = mascara_prefixo(dados, t)
    ptr, col = (dados.ptr, dados.col) if modo == "ocorrencia" else (dados.pptr, dados.pcol)
    vivas, it = descascar(ptr, col, dados.n_ideais, ativas)
    return {**estatisticas(ptr, col, dados.n_ideais, vivas), "iteracoes": it}, vivas


def reproduz_purge_do_cado(dados):
    """Prova de que a identidade dos ideais está certa: início e fim do descasque iguais aos do `purge` do CADO."""
    cado = dados.manifesto["purge"]
    ativas = np.ones(len(dados.ptr) - 1, dtype=bool)
    inicio = estatisticas(dados.pptr, dados.pcol, dados.n_ideais, ativas)
    fim, _ = nucleo(dados)
    esperado_i, esperado_f = cado["inicio"], cado["apos_singletons"]
    return {"inicio_bate": (inicio["linhas"], inicio["colunas"]) == (esperado_i["nrows"], esperado_i["ncols"]),
            "fim_bate": (fim["linhas"], fim["colunas"]) == (esperado_f["nrows"], esperado_f["ncols"]),
            "meu": {"inicio": inicio, "fim": fim}, "cado": {"inicio": esperado_i, "fim": esperado_f}}


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if argv[:1] == ["validar"] and len(argv) == 2:
        r = reproduz_purge_do_cado(carregar(argv[1]))
        print(json.dumps(r, indent=1))
        return 0 if r["inicio_bate"] and r["fim_bate"] else 1
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
