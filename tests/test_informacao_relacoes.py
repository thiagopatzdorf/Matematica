"""Métricas de informação das relações: prefixo sem vazar o futuro, posto exato, controles e modelos de I(W)."""
import gzip
import json
import random
import shutil
import sys

import numpy as np
import pytest

from conftest import RAIZ

sys.path.insert(0, str(RAIZ / "tools" / "fatoracao"))
import informacao_relacoes as inf  # noqa: E402
import relacoes as rel  # noqa: E402

FIXTURE = RAIZ / "tests" / "fixtures" / "fatoracao" / "captura_c30"
PURGE_VAZIO = {"inicio": {"nrows": 0, "ncols": 0, "excess": 0}, "apos_singletons": {"nrows": 0, "ncols": 0, "excess": 0},
               "final": {"nrows": 0, "ncols": 0, "excess": 0}}


def capturar(tmp_path, relacoes, nome="cap"):
    d = tmp_path / nome
    d.mkdir()
    linhas = ["#ordem\tbloco\tq\trho\ta\tb\tp0\tp1"] + [f"{i}\t0\t11\t3\t{a}\t{b}\t{p0}\t{p1}" for i, (a, b, p0, p1) in enumerate(relacoes)]
    with gzip.open(d / "relacoes.tsv.gz", "wt", encoding="utf-8") as fh:
        fh.write("\n".join(linhas) + "\n")
    with gzip.open(d / "livres.tsv.gz", "wt", encoding="utf-8") as fh:
        fh.write("#p\tn_indices\n")
    (d / "poly.txt").write_text("n: 15\nskew: 1.0\nc0: 1\nc1: 0\nc2: 1\nY0: -3\nY1: 4\n", encoding="utf-8")
    (d / "arquivos.json").write_text(json.dumps([{"nome": "x", "n_relacoes": len(relacoes), "n_sq": 10, "cpu_s": 5.0}]))
    (d / "manifest.json").write_text(json.dumps({"purge": PURGE_VAZIO}))
    return d


def sintetica(n, semente=0, n_primos=60):
    """Relações com 3 ideais cada, no lado 1, sorteados de `n_primos` primos (as colisões fazem o núcleo aparecer)."""
    rng = random.Random(semente)
    primos = [p for p in range(1009, 4000) if all(p % q for q in range(2, int(p ** 0.5) + 1))][:n_primos]
    rels = []
    for i in range(n):
        ps = rng.sample(primos, 3)
        rels.append((1000 + i, 1 + i % 7, "3", ",".join(f"{p:x}" for p in ps)))
    return rels


def _truncar(origem, destino, t):
    shutil.copytree(origem, destino)
    with gzip.open(origem / "relacoes.tsv.gz", "rt") as fh:
        linhas = fh.read().splitlines()
    with gzip.open(destino / "relacoes.tsv.gz", "wt") as fh:
        fh.write("\n".join(linhas[:t + 1]) + "\n")
    return destino


def test_trabalho_que_nao_soma_os_blocos_nem_interpola_dentro_do_bloco():
    d = rel.carregar(FIXTURE)
    assert inf.trabalho(d, 0) == (0.0, 0.0)
    assert inf.trabalho(d, d.n_brutas)[0] == sum(d.n_sq_bloco)
    meio = inf.trabalho(d, int(d.fim_bloco[0]) // 2)
    assert meio[0] == pytest.approx(d.n_sq_bloco[0] / 2, rel=0.01)
    assert inf.trabalho(d, 100)[0] < inf.trabalho(d, 20000)[0] < inf.trabalho(d, d.n_brutas)[0]


def test_curva_cujo_ultimo_ponto_difere_do_nucleo_completo():
    d = rel.carregar(FIXTURE)
    c = inf.curva(d, 12)
    fim, _ = rel.nucleo(d)
    assert c[-1]["t"] == d.n_brutas and c[-1]["linhas_nucleo"] == fim["linhas"] and c[-1]["excesso"] == fim["excesso"]
    assert all(p["excesso"] == p["linhas_nucleo"] - p["colunas_nucleo"] for p in c)
    assert [p["t"] for p in c] == sorted(p["t"] for p in c) and [p["ideais_vistos"] for p in c] == sorted(p["ideais_vistos"] for p in c)


def test_prefixo_da_curva_que_olha_relacoes_do_futuro(tmp_path):
    d = rel.carregar(FIXTURE)
    pontos = [p for p in inf.curva(d, 8) if p["linhas_nucleo"] > 0 and p["t"] < d.n_brutas]
    assert pontos
    for k, ponto in enumerate(pontos[:2]):
        truncada = rel.carregar(_truncar(FIXTURE, tmp_path / f"t{k}", ponto["t"]))
        st, _ = rel.nucleo(truncada)
        assert (ponto["linhas_nucleo"], ponto["colunas_nucleo"], ponto["excesso"]) == (st["linhas"], st["colunas"], st["excesso"])
        assert ponto["ideais_vistos"] == int(np.count_nonzero(np.bincount(truncada.col[:truncada.ptr[truncada.n_unicas]], minlength=truncada.n_ideais)))


def test_caracteristica_online_que_muda_quando_relacoes_posteriores_somem(tmp_path):
    d = rel.carregar(FIXTURE)
    t = 15000
    cheia, nomes = inf.caracteristicas_online(d)
    trunc = rel.carregar(_truncar(FIXTURE, tmp_path / "t", t))
    parcial, _ = inf.caracteristicas_online(trunc, grande_bits=None)
    u = trunc.n_unicas
    # a mesma definição de "grande" depende dos ideais vistos; compara só as colunas que dependem apenas do passado e da relação
    for nome in ("log2_abs_a", "log2_b", "n_ideais_lado0", "n_ideais_lado1", "n_ideais_novos", "soma_log_previa"):
        j = nomes.index(nome)
        assert np.allclose(cheia[:u, j], parcial[:, j]), nome


def test_controle_de_ordem_que_muda_o_conjunto_de_linhas(tmp_path):
    d = rel.carregar(capturar(tmp_path, sintetica(300)))
    ptr, col = inf._sistema_aleatorio(d, 1, "ordem")
    antes = sorted(tuple(sorted(d.col[d.ptr[i]:d.ptr[i + 1]])) for i in range(d.n_unicas))
    depois = sorted(tuple(sorted(col[ptr[i]:ptr[i + 1]])) for i in range(d.n_unicas))
    assert antes == depois
    ptr2, col2 = inf._sistema_aleatorio(d, 1, "ordem")
    assert (ptr == ptr2).all() and (col == col2).all()
    assert not (col == d.col).all()


def test_controle_de_configuracao_que_nao_preserva_o_grau_de_cada_ideal(tmp_path):
    d = rel.carregar(capturar(tmp_path, sintetica(300)))
    ptr, col = inf._sistema_aleatorio(d, 2, "configuracao")
    grau_real = np.bincount(d.col, minlength=d.n_ideais)
    grau_nulo = np.bincount(col, minlength=d.n_ideais)
    assert abs(int(grau_nulo.sum()) - int(grau_real.sum())) <= 0.02 * grau_real.sum()  # só as repetições na mesma linha somem
    assert np.corrcoef(grau_real, grau_nulo)[0, 1] > 0.98
    assert not all(np.array_equal(np.sort(d.col[d.ptr[i]:d.ptr[i + 1]]), np.sort(col[ptr[i]:ptr[i + 1]])) for i in range(d.n_unicas))
    assert (np.diff(ptr) >= 1).all()


def test_modelo_de_limiar_confundido_com_curva_suave():
    w = np.linspace(0, 100, 40)
    assert inf.ajustar_modelos(w, np.maximum(0, w - 60) * 2.0)["vencedor"] == "M5_limiar"
    assert inf.ajustar_modelos(w, 50 * np.log1p(w / 5.0))["vencedor"] in ("M3_log", "M2_potencia")
    assert inf.ajustar_modelos(w, 10 * w)["vencedor"] == "M1_linear"
    assert inf.ajustar_modelos(w, 80 * (1 - np.exp(-w / 20)))["vencedor"] == "M4_saturacao"


def test_auc_que_discorda_da_contagem_direta_de_pares():
    rng = np.random.default_rng(0)
    e = rng.integers(0, 6, 300).astype(float)  # muitos empates
    y = rng.random(300) < 0.4
    pos, neg = e[y], e[~y]
    direto = (np.sum(pos[:, None] > neg[None, :]) + 0.5 * np.sum(pos[:, None] == neg[None, :])) / (len(pos) * len(neg))
    assert inf.auc(e, y) == pytest.approx(direto)
    assert inf.auc(np.arange(10.0), np.arange(10) >= 5) == 1.0 and inf.auc(np.zeros(10), np.arange(10) >= 5) == 0.5
    assert np.isnan(inf.auc(np.arange(5.0), np.ones(5, dtype=bool)))


def test_logistica_que_nao_aprende_o_sinal_da_caracteristica_informativa():
    rng = np.random.default_rng(1)
    x = rng.normal(size=(2000, 3))
    y = (x[:, 0] * 2.0 + rng.normal(size=2000) * 0.5) > 0
    m = inf.ajustar_logistica(x, y)
    assert m[0][1] > 0.5 and abs(m[0][2]) < 0.3 and abs(m[0][3]) < 0.3
    assert inf.auc(inf.prever_logistica(m, x), y) > 0.9


def test_ponto_de_operacao_que_perde_mais_uteis_do_que_o_prometido():
    rng = np.random.default_rng(2)
    descarte = rng.random(5000) < 0.5
    escore = rng.normal(size=5000) + 1.5 * descarte
    util = ~descarte
    for alvo in (0.9, 0.99):
        op = inf.ponto_de_operacao(escore, descarte, util, alvo)
        assert op["uteis_perdidas"] <= (1 - alvo) + 0.01
    assert inf.ponto_de_operacao(escore, descarte, util, 0.9)["fracao_rejeitada"] > inf.ponto_de_operacao(escore, descarte, util, 0.99)["fracao_rejeitada"]


def test_heaps_com_expoente_conhecido():
    curva = [{"unicas": u, "ideais_vistos": int(3 * u ** 0.6)} for u in range(1000, 20001, 1000)]
    assert inf.heaps(curva)["beta"] == pytest.approx(0.6, abs=0.01)


def _posto_referencia(linhas):
    """Eliminação de Gauss módulo 2 com inteiros de Python como vetores de bits."""
    base = {}
    for cs in linhas:
        v = 0
        for c in cs:
            v ^= 1 << int(c)
        while v:
            alto = v.bit_length() - 1
            if alto in base:
                v ^= base[alto]
            else:
                base[alto] = v
                break
    return len(base)


def test_posto_empacotado_que_difere_da_eliminacao_de_referencia():
    rng = random.Random(4)
    for n_cols, n_lin in ((40, 30), (70, 120), (130, 90), (64, 64)):
        linhas = [rng.sample(range(n_cols), rng.randrange(1, 6)) for _ in range(n_lin)]
        assert inf.posto_gf2(linhas, n_cols) == _posto_referencia(linhas)


def test_posto_do_prefixo_que_nao_soma_as_linhas_removidas_ao_posto_do_nucleo(tmp_path):
    d = rel.carregar(capturar(tmp_path, sintetica(160, semente=3, n_primos=45)))
    for t in (40, 90, 160):
        r = inf.posto_do_prefixo(d, t)
        ativas, _ = rel.mascara_prefixo(d, t)
        linhas = [list(d.pcol[d.pptr[i]:d.pptr[i + 1]]) for i in np.nonzero(ativas)[0]]
        ref = _posto_referencia(linhas)
        assert r["posto"] == ref and r["nulidade"] == int(ativas.sum()) - ref, (t, r, ref)


def test_destinos_que_nao_particionam_as_relacoes_unicas():
    d = rel.carregar(FIXTURE)
    dest, info = inf.destinos(d, FIXTURE)
    assert set(np.unique(dest)) <= {1, 2, 3, 4} and len(dest) == d.n_unicas
    n_purgadas_do_crivo = info["purgadas"] - sum(1 for p in range(d.n_livres))  # tolera: livres purgadas não têm destino
    assert int((dest >= 3).sum()) <= info["purgadas"] and n_purgadas_do_crivo <= info["purgadas"]
    assert int((dest == 1).sum()) == d.n_unicas - int(rel.nucleo(d)[0]["linhas"] - sum(1 for _ in range(0)) - _livres_no_nucleo(d))


def _livres_no_nucleo(d):
    _, vivas = rel.nucleo(d)
    return int(vivas[d.n_unicas:].sum())


def test_componentes_de_ideais_grandes_que_juntam_o_que_nao_tem_ideal_em_comum(tmp_path):
    # A e B dividem o ideal grande (0x401, raiz 2): a=2 e a=1027 dão a mesma raiz módulo 1025. C só tem um grande próprio.
    rels = [(2, 1, "3", "401,403"), (1027, 1, "3", "401,405"), (6, 1, "3", "407")]
    d = rel.carregar(capturar(tmp_path, rels))
    d.manifesto["parametros"] = {"tasks.lpb0": "12", "tasks.lpb1": "12"}  # grande: p >= 2^(12-2) = 1024
    cg = inf.componentes_grandes(d, pontos=3, inicio=0.34)
    assert cg[-1]["grandes_vistos"] == 4 and cg[-1]["maior_componente"] == 3 and cg[-1]["componentes"] == 2
