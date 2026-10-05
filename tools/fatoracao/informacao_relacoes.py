#!/usr/bin/env python3
"""Quanta informação nova as relações do GNFS carregam? Curvas, ponto de parada, controles e modelos de I(W).

    python3 tools/fatoracao/informacao_relacoes.py curva <captura> [--pontos 40]

PRÉ-REGISTRO (fixado antes de olhar o conjunto de teste; mudar exige um PR que diga o que mudou e por quê)
----------------------------------------------------------------------------------------------------------
Trabalho `W(t)`: special-q processados até a relação bruta `t` (interpolado dentro do bloco) e, em separado, CPU do crivo.
Nunca tempo de relógio.

Informação `I(t)`, vários proxies independentes, nenhum "bytes comprimidos" sozinho:

* `colunas_nucleo`: colunas do núcleo (descasque de singletons) do prefixo;
* `excesso`: linhas menos colunas do núcleo; é cota inferior da dimensão do espaço de dependências (nulidade >= excesso);
* `ideais_vistos`: ideais distintos já observados (novidade);
* `linhas_nucleo`: linhas do núcleo.

Modelos de `I(W)` (lista FECHADA; ninguém acrescenta modelo depois de ver o resultado):
M1 `I = c*W`; M2 `I = c*W^a`; M3 `I = c*ln(1 + W/w0)`; M4 `I = Iinf*(1 - exp(-W/w0))`; M5 `I = c*max(0, W - W0)`.
Critério: BIC sobre o resíduo relativo ao máximo de `I`, nos mesmos pontos (prefixos de 5% a 100%) para todos os modelos.

Ponto de parada: `t_min` = menor prefixo cujo núcleo tem `excesso >= MANTER` (160, o que o `purge` do CADO mantém por padrão).
Vale só para a instância medida: não é lei geral.
"""
import bz2
import gzip
import json
import lzma
import sys
from pathlib import Path

import numpy as np

import relacoes as rel

MANTER = 160
MODELOS = ("M1_linear", "M2_potencia", "M3_log", "M4_saturacao", "M5_limiar")


def trabalho(dados, t):
    """`(W_sq, W_cpu)` até a relação bruta `t`: soma dos blocos inteiros mais a fração do bloco em curso."""
    w_sq = w_cpu = 0.0
    ini = 0
    for k, fim in enumerate(dados.fim_bloco):
        n, sq, cpu = int(fim - ini), dados.n_sq_bloco[k] or 0, dados.cpu_bloco[k] or 0.0
        if t >= fim:
            w_sq, w_cpu = w_sq + sq, w_cpu + cpu
        else:
            frac = max(0, t - ini) / n if n else 0.0
            return w_sq + sq * frac, w_cpu + cpu * frac
        ini = int(fim)
    return w_sq, w_cpu


def pontos_de_prefixo(n, quantos=40, inicio=0.05):
    ts = sorted({int(round(n * f)) for f in np.linspace(inicio, 1.0, quantos)} | {n})
    return [t for t in ts if t > 0]


def curva(dados, pontos=40, inicio=0.05, modo="paridade"):
    """Uma linha por prefixo: trabalho, núcleo, excesso e novidade. Só usa as relações até `t` (nunca o futuro)."""
    ptr, col = (dados.ptr, dados.col) if modo == "ocorrencia" else (dados.pptr, dados.pcol)
    linhas = []
    for t in pontos_de_prefixo(dados.n_brutas, pontos, inicio):
        ativas, u = rel.mascara_prefixo(dados, t)
        vivas, it = rel.descascar(ptr, col, dados.n_ideais, ativas)
        e = rel.estatisticas(ptr, col, dados.n_ideais, vivas)
        crivo = ativas.copy()
        crivo[dados.n_unicas:] = False  # novidade só conta o que o crivo descobriu: as relações livres já existem
        vistos = int((np.bincount(col[crivo[rel._linhas_do_csr(ptr)]], minlength=dados.n_ideais) > 0).sum())
        w_sq, w_cpu = trabalho(dados, t)
        linhas.append({"t": t, "unicas": u, "duplicatas": t - u, "w_sq": w_sq, "w_cpu": w_cpu, "linhas_nucleo": e["linhas"],
                       "colunas_nucleo": e["colunas"], "excesso": e["excesso"], "ideais_vistos": vistos, "iteracoes": it})
    return linhas


def t_minimo(curva_pontos, manter=MANTER):
    """Primeiro ponto da curva com excesso >= manter. Devolve o ponto, ou None se a instância nunca chegou lá."""
    for p in curva_pontos:
        if p["excesso"] >= manter:
            return p
    return None


def refinar_t_minimo(dados, anterior_t, atual_t, manter=MANTER, modo="paridade"):
    """Bisseção entre dois pontos da curva (assume monotonia dentro do trecho: é uma aproximação declarada)."""
    ptr, col = (dados.ptr, dados.col) if modo == "ocorrencia" else (dados.pptr, dados.pcol)
    lo, hi = anterior_t, atual_t
    while hi - lo > max(1, dados.n_brutas // 2000):
        meio = (lo + hi) // 2
        ativas, _ = rel.mascara_prefixo(dados, meio)
        vivas, _ = rel.descascar(ptr, col, dados.n_ideais, ativas)
        if rel.estatisticas(ptr, col, dados.n_ideais, vivas)["excesso"] >= manter:
            hi = meio
        else:
            lo = meio
    return hi


# ---------- controles aleatórios ----------


def _sistema_aleatorio(dados, semente, modo_nulo):
    """`(ptr, col)` de um sistema nulo com as mesmas linhas.

    `configuracao`: as ocorrências de ideais de cada lado são embaralhadas entre as linhas das relações do crivo, mantendo o
    tamanho de cada linha por lado e o grau de cada ideal (modelo de configuração); relações livres ficam como são.
    `ordem`: as mesmas relações em ordem aleatória (testa se a ordem de descoberta importa).
    """
    rng = np.random.default_rng(semente)
    nu = dados.n_unicas
    if modo_nulo == "ordem":
        perm = rng.permutation(nu)
        comp = np.diff(dados.ptr)
        novo = [dados.col[dados.ptr[i]:dados.ptr[i + 1]] for i in perm]
        ptr = np.concatenate([[0], np.cumsum([len(x) for x in novo])])
        col = np.concatenate(novo) if novo else np.zeros(0, dtype=np.int64)
        livres = dados.col[dados.ptr[nu]:]
        ptr = np.concatenate([ptr, ptr[-1] + np.cumsum(comp[nu:])])
        return ptr, np.concatenate([col, livres])
    fim = dados.ptr[nu]
    col = dados.col.copy()
    lin = rel._linhas_do_csr(dados.ptr)[:fim]
    lado = dados.ideal_lado[col[:fim]]
    for s in (0, 1):
        pos = np.nonzero(lado == s)[0]
        col[pos] = col[pos][rng.permutation(len(pos))]
    # um ideal pode ter caído duas vezes na mesma linha: mantém uma (a coluna conta presença, não expoente)
    ordem = np.lexsort((col[:fim], lin))
    c, l = col[:fim][ordem], lin[ordem]
    manter = np.ones(len(c), dtype=bool)
    manter[1:] = (l[1:] != l[:-1]) | (c[1:] != c[:-1])
    c, l = c[manter], l[manter]
    contagem = np.bincount(l, minlength=nu)
    ptr = np.concatenate([[0], np.cumsum(contagem)])
    livres = col[fim:]
    ptr = np.concatenate([ptr, ptr[-1] + np.cumsum(np.diff(dados.ptr)[nu:])])
    return ptr, np.concatenate([c, livres])


def curva_nulo(dados, modo_nulo, semente=0, pontos=40, inicio=0.05):
    """Mesma curva do núcleo sobre um sistema nulo. O prefixo é por número de relações únicas (sem duplicatas no nulo)."""
    ptr, col = _sistema_aleatorio(dados, semente, modo_nulo)
    nu = dados.n_unicas
    linhas = []
    for u in pontos_de_prefixo(nu, pontos, inicio):
        ativas = np.zeros(len(ptr) - 1, dtype=bool)
        ativas[:u] = True
        ativas[nu:] = True
        vivas, it = rel.descascar(ptr, col, dados.n_ideais, ativas)
        e = rel.estatisticas(ptr, col, dados.n_ideais, vivas)
        linhas.append({"unicas": u, "linhas_nucleo": e["linhas"], "colunas_nucleo": e["colunas"], "excesso": e["excesso"]})
    return linhas


# ---------- modelos de I(W) ----------


def _bic(residuo, n, k):
    s = max(float(np.mean(residuo ** 2)), 1e-300)
    return n * np.log(s) + k * np.log(n)


def ajustar_modelos(w, i):
    """Ajusta M1 a M5 a `(W, I)` e devolve BIC e parâmetros. A amplitude sai de mínimos quadrados; o resto, de grade."""
    w, i = np.asarray(w, dtype=float), np.asarray(i, dtype=float)
    esc = float(i.max()) or 1.0
    y = i / esc
    n = len(w)
    wn = w / (float(w.max()) or 1.0)
    saida = {}

    def amplitude(x):
        d = float(x @ x)
        c = float(x @ y) / d if d > 0 else 0.0
        return c, y - c * x

    c, r = amplitude(wn)
    saida["M1_linear"] = {"bic": _bic(r, n, 1), "params": {"c": c * esc / (float(w.max()) or 1.0)}}
    melhor = None
    for a in np.linspace(0.1, 1.5, 57):
        c, r = amplitude(wn ** a)
        b = _bic(r, n, 2)
        if melhor is None or b < melhor[0]:
            melhor = (b, {"c": c * esc, "a": float(a)})
    saida["M2_potencia"] = {"bic": melhor[0], "params": melhor[1]}
    melhor = None
    for w0 in np.geomspace(1e-3, 10, 60):
        c, r = amplitude(np.log1p(wn / w0))
        b = _bic(r, n, 2)
        if melhor is None or b < melhor[0]:
            melhor = (b, {"c": c * esc, "w0": float(w0) * float(w.max())})
    saida["M3_log"] = {"bic": melhor[0], "params": melhor[1]}
    melhor = None
    for w0 in np.geomspace(1e-2, 20, 60):
        c, r = amplitude(1 - np.exp(-wn / w0))
        b = _bic(r, n, 2)
        if melhor is None or b < melhor[0]:
            melhor = (b, {"i_inf": c * esc, "w0": float(w0) * float(w.max())})
    saida["M4_saturacao"] = {"bic": melhor[0], "params": melhor[1]}
    melhor = None
    for w_lim in np.linspace(0.0, 0.98, 99):
        c, r = amplitude(np.maximum(0.0, wn - w_lim))
        b = _bic(r, n, 2)
        if melhor is None or b < melhor[0]:
            melhor = (b, {"c": c * esc / (float(w.max()) or 1.0), "w_limiar": float(w_lim) * float(w.max())})
    saida["M5_limiar"] = {"bic": melhor[0], "params": melhor[1]}
    vencedor = min(saida, key=lambda k: saida[k]["bic"])
    return {"modelos": saida, "vencedor": vencedor, "n_pontos": n}


# ---------- novidade (Heaps) ----------


def heaps(pontos_curva, de=0.10):
    """Expoente de `ideais_vistos ~ K * unicas^beta` por regressão em log-log, de `de` do total até o fim."""
    u = np.array([p["unicas"] for p in pontos_curva], dtype=float)
    v = np.array([p["ideais_vistos"] for p in pontos_curva], dtype=float)
    m = u >= de * u.max()
    beta, logk = np.polyfit(np.log(u[m]), np.log(v[m]), 1)
    fim = pontos_curva[-1]
    antes = pontos_curva[-2]
    marginal = (fim["ideais_vistos"] - antes["ideais_vistos"]) / max(1, fim["unicas"] - antes["unicas"])
    return {"beta": float(beta), "K": float(np.exp(logk)), "ideais_novos_por_relacao_no_ultimo_trecho": float(marginal)}


# ---------- destino de cada relação ----------

DESTINOS = {0: "duplicata", 1: "unica_removida_nos_singletons", 2: "nucleo_cortada_pelos_cliques",
            3: "purgada_fora_da_matriz", 4: "na_matriz"}


def destinos(dados, pasta):
    """Destino de cada relação ÚNICA do crivo, a partir do que o próprio CADO produziu (purged.gz e index.gz).

    1 removida pelo descasque de singletons; 2 estava no núcleo e o CADO cortou nos cliques para manter o excesso;
    3 purgada mas sem linha na matriz; 4 usada em alguma linha da matriz. Duplicatas ficam de fora (destino 0 no nível bruto).
    """
    pasta = Path(pasta)
    nu = dados.n_unicas
    primeiras = np.nonzero(~dados.eh_dup)[0]
    chave = {(int(dados.a[r]), int(dados.b[r])): k for k, r in enumerate(primeiras)}
    purgadas = []
    with gzip.open(pasta / "purgadas.tsv.gz", "rt", encoding="utf-8") as fh:
        for linha in fh:
            if linha[0] != "#":
                a, b = linha.split()
                purgadas.append((int(a), int(b)))
    usadas = set()
    with gzip.open(pasta / "index.gz", "rt", encoding="utf-8") as fh:
        fh.readline()
        for linha in fh:
            usadas.update(int(x, 16) for x in linha.split()[1:])
    destino = np.full(nu, 1, dtype=np.int8)
    nucleo_proprio, vivas = rel.nucleo(dados)
    destino[vivas[:nu]] = 2
    for pos, ab in enumerate(purgadas):
        k = chave.get(ab)
        if k is None:  # relação livre (b = 0), não vem do crivo
            continue
        destino[k] = 4 if pos in usadas else 3
    return destino, {"nucleo": nucleo_proprio, "purgadas": len(purgadas), "usadas": len(usadas)}


# ---------- características online ----------


def caracteristicas_online(dados, grande_bits=None):
    """Matriz `(n_unicas, k)` de características que existem NO MOMENTO em que a relação é encontrada (só o passado).

    As colunas dependentes do histórico (novidade dos ideais) contam apenas relações anteriores na ordem canônica.
    """
    nu = dados.n_unicas
    fim = dados.ptr[nu]
    col = dados.col[:fim]
    lin = rel._linhas_do_csr(dados.ptr)[:fim]
    lado = dados.ideal_lado[col]
    logp = np.log2(dados.ideal_p[col].astype(float))
    grande = limite_de_grande(dados)[col] if grande_bits is None else logp >= grande_bits
    ordem = np.argsort(col, kind="stable")  # estável: dentro de cada ideal, mantém a ordem das relações
    c_ord = col[ordem]
    inicio = np.concatenate([[0], np.nonzero(c_ord[1:] != c_ord[:-1])[0] + 1])
    ranque = np.arange(len(c_ord)) - np.repeat(inicio, np.diff(np.concatenate([inicio, [len(c_ord)]])))
    previa = np.empty(len(col), dtype=np.int64)
    previa[ordem] = ranque
    seg = dados.ptr[:nu]
    grande_inf = np.where(grande, previa, 10 ** 9)
    primeiras = np.nonzero(~dados.eh_dup)[0]
    cols = {
        "log2_abs_a": np.log2(np.abs(dados.a[primeiras]).astype(float) + 1.0),
        "log2_b": np.log2(dados.b[primeiras].astype(float) + 1.0),
        "log2_q": np.log2(np.maximum(dados.q[primeiras], 1).astype(float)),
        "n_ideais_lado0": np.bincount(lin, weights=(lado == 0), minlength=nu),
        "n_ideais_lado1": np.bincount(lin, weights=(lado == 1), minlength=nu),
        "maior_primo_lado0": np.maximum.reduceat(np.where(lado == 0, logp, 0.0), seg),
        "maior_primo_lado1": np.maximum.reduceat(np.where(lado == 1, logp, 0.0), seg),
        "n_ideais_novos": np.bincount(lin, weights=(previa == 0), minlength=nu),
        "n_grandes_novos": np.bincount(lin, weights=((previa == 0) & grande), minlength=nu),
        "n_grandes": np.bincount(lin, weights=grande, minlength=nu),
        "soma_log_previa": np.bincount(lin, weights=np.log1p(previa), minlength=nu),
        "minima_previa_dos_grandes": np.minimum(np.minimum.reduceat(grande_inf, seg), 50).astype(float),
    }
    return np.column_stack(list(cols.values())), list(cols)


def auc(escore, rotulo):
    """Área sob a curva ROC (probabilidade de um positivo ter escore maior que um negativo; empates valem 1/2)."""
    escore, rotulo = np.asarray(escore, dtype=float), np.asarray(rotulo, dtype=bool)
    n1, n0 = int(rotulo.sum()), int((~rotulo).sum())
    if n1 == 0 or n0 == 0:
        return float("nan")
    ordem = np.argsort(escore, kind="mergesort")
    ranque = np.empty(len(escore))
    s = escore[ordem]
    i = 0
    r = np.empty(len(escore))
    while i < len(s):
        j = i
        while j + 1 < len(s) and s[j + 1] == s[i]:
            j += 1
        r[i:j + 1] = (i + j) / 2.0 + 1.0
        i = j + 1
    ranque[ordem] = r
    return float((ranque[rotulo].sum() - n1 * (n1 + 1) / 2.0) / (n1 * n0))


def ajustar_logistica(x, y, ridge=1.0, iteracoes=30):
    """Regressão logística com ridge por Newton (IRLS); padroniza as colunas. Devolve `(pesos, media, desvio)`."""
    x = np.asarray(x, dtype=float)
    mu, sd = x.mean(axis=0), x.std(axis=0)
    sd[sd == 0] = 1.0
    z = np.column_stack([np.ones(len(x)), (x - mu) / sd])
    w = np.zeros(z.shape[1])
    reg = ridge * np.eye(z.shape[1])
    reg[0, 0] = 0.0
    y = np.asarray(y, dtype=float)
    for _ in range(iteracoes):
        eta = np.clip(z @ w, -30, 30)
        p = 1.0 / (1.0 + np.exp(-eta))
        grad = z.T @ (p - y) + reg @ w
        hess = (z * (p * (1 - p))[:, None]).T @ z + reg
        passo = np.linalg.solve(hess, grad)
        w -= passo
        if np.max(np.abs(passo)) < 1e-8:
            break
    return w, mu, sd


def prever_logistica(modelo, x):
    w, mu, sd = modelo
    z = np.column_stack([np.ones(len(x)), (np.asarray(x, dtype=float) - mu) / sd])
    return z @ w


def ponto_de_operacao(escore, rotulo_descarte, util, recall_util_minimo=0.99):
    """Limiar que rejeita o máximo de relações perdendo no máximo `1 - recall_util_minimo` das úteis. Só descreve, não decide."""
    escore, descarte, util = np.asarray(escore), np.asarray(rotulo_descarte, dtype=bool), np.asarray(util, dtype=bool)
    if not util.any():
        return None
    limiar = float(np.quantile(escore[util], recall_util_minimo))  # rejeita o que pontua acima do quantil das úteis
    rejeitadas = escore > limiar
    return {"limiar": limiar, "fracao_rejeitada": float(rejeitadas.mean()),
            "precisao_da_rejeicao": float(descarte[rejeitadas].mean()) if rejeitadas.any() else float("nan"),
            "uteis_perdidas": float((rejeitadas & util).sum() / util.sum()),
            "descartaveis_pegos": float((rejeitadas & descarte).sum() / max(1, descarte.sum()))}


# ---------- hipergrafo ----------


def componentes(dados, pontos=12, inicio=0.1):
    """Fração de ideais vistos na maior componente, por prefixo (união-busca sobre as relações únicas do crivo)."""
    nu = dados.n_unicas
    pai = list(range(dados.n_ideais))
    tam = [1] * dados.n_ideais
    visto = bytearray(dados.n_ideais)
    n_vistos = 0
    grande = 1
    ptr, col = dados.ptr, dados.col.tolist()
    alvos = sorted({max(1, int(round(nu * f))) for f in np.linspace(inicio, 1.0, pontos)} | {nu})
    saida, k = [], 0

    def raiz(x):
        while pai[x] != x:
            pai[x] = pai[pai[x]]
            x = pai[x]
        return x

    for u in range(1, nu + 1):
        ids = col[ptr[u - 1]:ptr[u]]
        for c in ids:
            if not visto[c]:
                visto[c] = 1
                n_vistos += 1
        r0 = raiz(ids[0])
        for c in ids[1:]:
            r = raiz(c)
            if r != r0:
                if tam[r] > tam[r0]:
                    r, r0 = r0, r
                pai[r] = r0
                tam[r0] += tam[r]
        grande = max(grande, tam[r0])
        if u == alvos[k]:
            saida.append({"unicas": u, "ideais_vistos": n_vistos, "maior_componente": grande, "fracao_na_maior": grande / n_vistos})
            k += 1
    return saida


def distribuicao_de_grau(dados, minimo=3):
    """Grau de cada ideal (em quantas relações únicas aparece) e inclinação da cauda em log-log (ideais com grau >= minimo)."""
    nu = dados.n_unicas
    grau = np.bincount(dados.col[:dados.ptr[nu]], minlength=dados.n_ideais)
    grau = grau[grau > 0]
    vals, cont = np.unique(grau, return_counts=True)
    m = vals >= minimo
    inclinacao = float(np.polyfit(np.log(vals[m]), np.log(cont[m]), 1)[0]) if m.sum() >= 3 else float("nan")
    return {"n_ideais": int(len(grau)), "grau_1": int((grau == 1).sum()), "grau_2": int((grau == 2).sum()),
            "grau_maximo": int(grau.max()), "inclinacao_da_cauda": inclinacao}


def limite_de_grande(dados, folga=2):
    """Ideal "grande": `p >= 2^(lpb - folga)` do seu lado. Pré-registrado: folga 2, escolhida no conjunto `dev`.

    Com folga 5 (ou 3) os ideais de 2^13 a 2^15 funcionam como hubs e o grafo vira uma componente só em qualquer prefixo; com folga 2
    sobra o regime em que a colisão é rara e domina a transição. Sem `lpb` no manifesto, o quantil 0,9 de log2 p."""
    par = dados.manifesto.get("parametros", {})
    lpb = {0: par.get("tasks.lpb0"), 1: par.get("tasks.lpb1")}
    if all(v is not None for v in lpb.values()):
        corte = np.array([2.0 ** (int(lpb[0]) - folga), 2.0 ** (int(lpb[1]) - folga)])
        return dados.ideal_p >= corte[dados.ideal_lado.astype(int)]
    return np.log2(dados.ideal_p.astype(float)) >= np.quantile(np.log2(dados.ideal_p.astype(float)), 0.9)


def componentes_grandes(dados, pontos=12, inicio=0.1, folga=2):
    """Como `componentes`, mas só liga ideais GRANDES: os pequenos aparecem em quase toda relação e ligam tudo (hubs)."""
    grande = limite_de_grande(dados, folga)
    nu = dados.n_unicas
    pai = list(range(dados.n_ideais))
    tam = [1] * dados.n_ideais
    visto = bytearray(dados.n_ideais)
    n_vistos, maior = 0, 1
    ptr, col, g = dados.ptr, dados.col.tolist(), grande.tolist()
    alvos = sorted({max(1, int(round(nu * f))) for f in np.linspace(inicio, 1.0, pontos)} | {nu})
    saida, k = [], 0

    def raiz(x):
        while pai[x] != x:
            pai[x] = pai[pai[x]]
            x = pai[x]
        return x

    for u in range(1, nu + 1):
        ids = [c for c in col[ptr[u - 1]:ptr[u]] if g[c]]
        for c in ids:
            if not visto[c]:
                visto[c] = 1
                n_vistos += 1
        if ids:
            r0 = raiz(ids[0])
            for c in ids[1:]:
                r = raiz(c)
                if r != r0:
                    if tam[r] > tam[r0]:
                        r, r0 = r0, r
                    pai[r] = r0
                    tam[r0] += tam[r]
            maior = max(maior, tam[r0])
        if u == alvos[k]:
            raizes = {raiz(x) for x in np.nonzero(np.frombuffer(visto, dtype=np.uint8))[0].tolist()}
            saida.append({"unicas": u, "grandes_vistos": n_vistos, "componentes": len(raizes), "maior_componente": maior,
                          "fracao_na_maior": maior / n_vistos if n_vistos else 0.0})
            k += 1
    return saida


# ---------- compressibilidade (evidência auxiliar, não prova de compressibilidade algorítmica) ----------


def _texto_de_ideais(dados, ptr, col, max_rel=None):
    """Uma linha por relação do crivo (as `max_rel` primeiras): primos do lado 0 e do lado 1 em hexadecimal, ordenados."""
    linhas = []
    for i in range(dados.n_unicas if max_rel is None else min(dados.n_unicas, max_rel)):
        ids = col[ptr[i]:ptr[i + 1]]
        s0 = sorted(int(dados.ideal_p[c]) for c in ids if dados.ideal_lado[c] == 0)
        s1 = sorted(int(dados.ideal_p[c]) for c in ids if dados.ideal_lado[c] == 1)
        linhas.append(",".join(f"{x:x}" for x in s0) + ":" + ",".join(f"{x:x}" for x in s1))
    return ("\n".join(linhas) + "\n").encode("ascii")


def razoes_de_compressao(texto):
    """`bits comprimidos / bits brutos` por gzip, bzip2 e lzma. Menor é mais comprimível."""
    n = len(texto)
    return {"bytes": n, "gzip": len(gzip.compress(texto, 9)) / n, "bzip2": len(bz2.compress(texto, 9)) / n,
            "lzma": len(lzma.compress(texto, preset=9 | lzma.PRESET_EXTREME)) / n}


def bits_adaptativos(dados, ptr, col, n_candidatos):
    """Bits por relação para descrever as listas de ideais sob um modelo adaptativo de frequência com escape (estilo PPM-C).

    Ideal já visto: `-log2(c / (T + D + 1))`; ideal novo: custo do escape mais `log2(candidatos restantes do lado)`.
    `n_candidatos[lado]` é o número de ideais possíveis do lado (aproximação declarada). Só olha o passado.
    """
    nu = dados.n_unicas
    fim = ptr[nu]
    c = col[:fim]
    lado = dados.ideal_lado[c].astype(int)
    ordem = np.argsort(c, kind="stable")
    co = c[ordem]
    ini = np.concatenate([[0], np.nonzero(co[1:] != co[:-1])[0] + 1])
    ranque = np.arange(len(co)) - np.repeat(ini, np.diff(np.concatenate([ini, [len(co)]])))
    previa = np.empty(len(c), dtype=np.int64)
    previa[ordem] = ranque
    bits = 0.0
    for s in (0, 1):
        m = lado == s
        novo = (previa[m] == 0)
        t = np.arange(m.sum())                       # fichas já vistas neste lado
        d = np.concatenate([[0], np.cumsum(novo)[:-1]])  # ideais distintos já vistos neste lado
        visto_custo = -np.log2(np.maximum(previa[m], 1) / (t + d + 1.0))
        novo_custo = -np.log2(1.0 / (t + d + 1.0)) + np.log2(np.maximum(n_candidatos[s] - d, 2.0))
        bits += float(np.where(novo, novo_custo, visto_custo).sum())
    return bits / nu


def compressibilidade(dados, semente=0, max_rel=None):
    """Compressores gerais e código adaptativo, sobre os dados reais e sobre dois controles de mesma massa de informação:
    `ordem` (as mesmas relações em ordem aleatória) e `configuracao` (grau de cada ideal preservado, pareamento aleatório)."""
    par = dados.manifesto.get("parametros", {})
    cand = []
    for s in (0, 1):
        lpb = int(par.get(f"tasks.lpb{s}", 18))
        x = 2.0 ** lpb
        cand.append(x / np.log(x))
    saida = {}
    for nome, (ptr, col) in {"real": (dados.ptr, dados.col), "ordem": _sistema_aleatorio(dados, semente, "ordem"),
                             "configuracao": _sistema_aleatorio(dados, semente, "configuracao")}.items():
        saida[nome] = {"compressores": razoes_de_compressao(_texto_de_ideais(dados, ptr, col, max_rel)),
                       "bits_por_relacao": bits_adaptativos(dados, ptr, col, cand)}
    return saida


# ---------- posto exato módulo 2 (tamanhos pequenos) ----------


def posto_gf2(linhas, n_cols):
    """Posto módulo 2 de uma matriz esparsa dada por listas de colunas. Eliminação com linhas empacotadas em uint64."""
    r = len(linhas)
    if r == 0 or n_cols == 0:
        return 0
    palavras = (n_cols + 63) // 64
    m = np.zeros((r, palavras), dtype=np.uint64)
    for i, cs in enumerate(linhas):
        for c in cs:
            m[i, c >> 6] ^= np.uint64(1) << np.uint64(c & 63)
    posto, topo = 0, 0
    for j in range(n_cols):
        w, bit = j >> 6, np.uint64(j & 63)
        cand = np.nonzero((m[topo:, w] >> bit) & np.uint64(1))[0]
        if len(cand) == 0:
            continue
        piv = topo + int(cand[0])
        if piv != topo:
            m[[topo, piv]] = m[[piv, topo]]
        abaixo = topo + 1 + np.nonzero((m[topo + 1:, w] >> bit) & np.uint64(1))[0]
        if len(abaixo):
            m[abaixo] ^= m[topo]
        topo += 1
        posto += 1
        if topo == r:
            break
    return posto


def posto_do_prefixo(dados, t_brutas, limite_linhas=40000):
    """Posto EXATO da matriz módulo 2 do prefixo: linhas removidas pelo descasque de paridade (cada uma soma 1) mais o posto do núcleo.

    Uma linha com uma coluna ímpar presente em nenhuma outra linha ativa é independente das demais, então sai e soma 1.
    Devolve `None` no posto do núcleo se ele passar de `limite_linhas` (a eliminação densa fica cara).
    """
    ativas, u = rel.mascara_prefixo(dados, t_brutas)
    vivas, _ = rel.descascar(dados.pptr, dados.pcol, dados.n_ideais, ativas)
    removidas = int(ativas.sum() - vivas.sum())
    idx = np.nonzero(vivas)[0]
    if len(idx) > limite_linhas:
        return {"linhas": int(ativas.sum()), "removidas": removidas, "nucleo_linhas": len(idx), "posto": None, "nulidade": None}
    cols = sorted({int(c) for i in idx for c in dados.pcol[dados.pptr[i]:dados.pptr[i + 1]]})
    mapa = {c: k for k, c in enumerate(cols)}
    linhas = [[mapa[int(c)] for c in dados.pcol[dados.pptr[i]:dados.pptr[i + 1]]] for i in idx]
    pn = posto_gf2(linhas, len(cols))
    total = int(ativas.sum())
    return {"linhas": total, "removidas": removidas, "nucleo_linhas": len(idx), "nucleo_colunas": len(cols),
            "posto": removidas + pn, "nulidade": total - (removidas + pn)}


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) >= 2 and argv[0] == "curva":
        quantos = int(argv[argv.index("--pontos") + 1]) if "--pontos" in argv else 40
        dados = rel.carregar(argv[1])
        c = curva(dados, quantos)
        print(json.dumps({"pontos": c, "t_min": t_minimo(c)}, indent=1))
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
