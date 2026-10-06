"""Códigos de cobertura de segunda ordem (segunda_ordem/): cada teste nomeia a falha que impede.

Rápido de propósito (sem RoundingSat nem VeriPB): os certificados de cota inferior são conferidos
por fora (ver segunda_ordem/README.md); aqui se confere o que dá para refazer em segundos.
"""
import json
import random
from itertools import combinations, product
from math import ceil
from pathlib import Path

import pytest

from segunda_ordem.busca import Projecoes, recozimento
from segunda_ordem.codificacao import Codificacao
from segunda_ordem.raio2 import (
    cota_esfera,
    de_inteiros,
    para_inteiro,
    r1_rapido,
    r2_bruto,
    r2_rapido,
    raiz_teto,
)
from segunda_ordem import tabela

RAIZ = Path(__file__).resolve().parents[1]
DADOS = RAIZ / "segunda_ordem" / "dados"


def _codigo_aleatorio(rng, q, n, M):
    return de_inteiros(rng.sample(range(q**n), M), q, n)


# --- os dois verificadores --------------------------------------------------------------------

def test_verificador_rapido_diverge_do_ingenuo_em_codigo_aleatorio():
    rng = random.Random(20261006)
    for _ in range(150):
        q = rng.choice([2, 2, 3])
        n = rng.randint(1, 3 if q == 3 else 4)
        M = rng.randint(1, min(6, q**n))
        C = _codigo_aleatorio(rng, q, n, M)
        assert r2_bruto(C, q, n) == r2_rapido(C, q, n), (q, n, C)


def test_r2_fora_do_intervalo_entre_r_e_2r():
    # R(C) <= R_2(C) <= 2 R(C): u1 = u2 dá a primeira; c1, c2 mais próximos dão a segunda.
    rng = random.Random(7)
    for _ in range(80):
        q = rng.choice([2, 3])
        n = rng.randint(2, 5 if q == 2 else 4)
        C = _codigo_aleatorio(rng, q, n, rng.randint(1, min(10, q**n)))
        r1, r2 = r1_rapido(C, q, n), r2_rapido(C, q, n)
        assert r1 <= r2 <= 2 * r1


def test_hamming_7_4_nao_tem_r2_igual_a_2_como_no_exemplo_de_efs():
    # Elimelech–Firer–Schwartz (IEEE TIT 2021), Exemplo 3: o código de Hamming tem R_t = t.
    G = [(1, 0, 0, 0, 1, 1, 0), (0, 1, 0, 0, 1, 0, 1), (0, 0, 1, 0, 0, 1, 1), (0, 0, 0, 1, 1, 1, 1)]
    H = {tuple(sum(m[i] * G[i][j] for i in range(4)) % 2 for j in range(7))
         for m in product(range(2), repeat=4)}
    assert r1_rapido(sorted(H), 2, 7) == 1
    assert r2_rapido(sorted(H), 2, 7) == 2


def test_palavra_unica_nao_tem_r2_igual_a_n():
    for q, n in ((2, 4), (3, 3)):
        assert r2_rapido([(0,) * n], q, n) == n


def test_codigo_constante_nao_tem_r2_igual_a_n_menos_teto_de_n_sobre_q2():
    # 0000 e 1111 (q=2, n=4): no par (0011, 0101) as colunas (0,0),(0,1),(1,0),(1,1) são todas
    # distintas e cada par de palavras constantes acerta só uma delas, então R_2 = 4 − 1 = 3.
    assert r2_bruto([(0,) * 4, (1,) * 4], 2, 4) == 3
    assert r2_rapido([(0,) * 4, (1,) * 4], 2, 4) == 3


# --- formulação por projeções (busca e codificação) -------------------------------------------

def test_custo_por_projecoes_discorda_do_raio_exato():
    rng = random.Random(11)
    for _ in range(120):
        q = rng.choice([2, 3])
        n = rng.randint(2, 5 if q == 2 else 4)
        r = rng.randint(1, n - 1)
        idx = rng.sample(range(q**n), rng.randint(1, min(12, q**n)))
        pj = Projecoes(q, n, r)
        for c in idx:
            pj.mudar(c, +1)
        assert (pj.custo() == 0) == (r2_rapido(de_inteiros(idx, q, n), q, n) <= r)


def _minimo_por_forca_bruta(q, n, r):
    for M in range(1, q**n + 1):
        for comb in combinations(range(q**n), M):
            if r2_rapido(de_inteiros(comb, q, n), q, n) <= r:
                return M
    raise AssertionError


def _minimo_por_sat(q, n, r, simetria=False):
    from pysat.card import CardEnc, EncType
    from pysat.solvers import Solver

    cod = Codificacao(q, n, r, fixar_zero=True)
    if simetria:
        cod.quebrar_simetria(extras=20)
    for M in range(1, q**n + 1):
        card = CardEnc.atmost(lits=list(range(1, cod.N + 1)), bound=M, top_id=cod.nvars,
                              encoding=EncType.seqcounter)
        with Solver(name="minisat22", bootstrap_with=cod.clausulas + card.clauses) as s:
            if s.solve():
                C = de_inteiros(cod.codigo_de(s.get_model()), q, n)
                assert r2_rapido(C, q, n) <= r
                return M
    raise AssertionError


@pytest.mark.parametrize("q,n,r", [(2, 2, 1), (2, 3, 1), (2, 3, 2), (2, 4, 2), (2, 4, 3), (3, 2, 1)])
def test_codificacao_booleana_diverge_da_forca_bruta_em_celula_pequena(q, n, r):
    pytest.importorskip("pysat")
    assert _minimo_por_sat(q, n, r) == _minimo_por_forca_bruta(q, n, r)


@pytest.mark.parametrize("q,n,r", [(2, 3, 1), (2, 4, 1), (2, 4, 2), (2, 5, 2), (3, 2, 1), (3, 3, 1), (3, 3, 2)])
def test_quebra_de_simetria_muda_o_minimo(q, n, r):
    pytest.importorskip("pysat")
    assert _minimo_por_sat(q, n, r, simetria=True) == _minimo_por_sat(q, n, r)


def test_opb_com_cabecalho_que_nao_bate_com_o_numero_de_restricoes():
    cod = Codificacao(2, 3, 1, fixar_zero=True)
    texto = cod.opb().splitlines()
    assert texto[0].startswith(f"* #variable= {cod.nvars} #constraint= {len(cod.clausulas)} ")
    assert texto[1].startswith("min: ")
    assert len(texto) == 2 + len(cod.clausulas)


def test_recozimento_devolve_codigo_que_nao_cobre():
    C = recozimento(2, 5, 2, 6, passos=20000, semente=1)
    assert C is not None and len(C) == 6
    assert r2_rapido(de_inteiros(C, 2, 5), 2, 5) <= 2


# --- cotas livres ----------------------------------------------------------------------------

def test_cota_da_esfera_errada():
    # M^2 * V >= q^{2n}; q=2, n=3, r=1: V = 1 + 3*3 = 10, 64/10 -> M >= 3.
    assert cota_esfera(2, 3, 1) == 3
    assert raiz_teto(16) == 4 and raiz_teto(17) == 5


def test_c2_nao_e_isometrico_ao_codigo_produto_sobre_q2():
    # |C^2| = |C|^2 e R_2(C) = raio de C⊗C em H(n, q^2): logo |C|^2 >= K_{q^2}(n, R_2(C)).
    rng = random.Random(3)
    for _ in range(30):
        n = rng.randint(2, 4)
        C = _codigo_aleatorio(rng, 2, n, rng.randint(1, min(6, 2**n)))
        pares = {tuple(2 * a + b for a, b in zip(c1, c2)) for c1 in C for c2 in C}
        assert len(pares) == len(C) ** 2
        assert r1_rapido(sorted(pares), 4, n) == r2_rapido(C, 2, n)


@pytest.mark.parametrize("q,n", [(2, 2), (2, 3), (2, 4), (2, 5), (3, 2), (3, 3)])
def test_teorema_das_q_palavras_falha_por_forca_bruta(q, n):
    # min R_2 sobre códigos de q palavras = n − ⌈n/q²⌉, e nenhum código com menos de q palavras
    # tem R_2 < n. Confere por enumeração de todos os códigos com q palavras contendo 0.
    melhor = min(r2_rapido([(0,) * n] + de_inteiros(resto, q, n), q, n)
                 for resto in combinations(range(1, q**n), q - 1))
    assert melhor == n - ceil(n / q**2)
    if q == 3:
        assert min(r2_rapido([(0,) * n] + de_inteiros([x], q, n), q, n)
                   for x in range(1, q**n)) == n


# --- dados publicados ------------------------------------------------------------------------

def test_testemunha_publicada_nao_cobre_ou_esta_malformada():
    test = json.loads((DADOS / "testemunhas.json").read_text(encoding="utf-8"))
    assert test, "sem testemunhas"
    for k, t in test.items():
        q, n, r = map(int, k.split(","))
        assert tabela.conferir_testemunha(q, n, r, t["palavras"]) <= r, k
        assert t["M"] == len(t["palavras"])


def test_tabela_publicada_diverge_do_que_os_dados_geram():
    publicada = json.loads((DADOS / "tabela.json").read_text(encoding="utf-8"))
    assert publicada == json.loads(json.dumps(tabela.montar(), sort_keys=True, ensure_ascii=False))


def test_celula_exata_sem_cota_inferior_justificada():
    tab = tabela.montar()
    for k, c in tab["celulas"].items():
        assert c["lb"] <= c["ub"], k
        if c["exato"]:
            assert c["origem_lb"], k
            assert c["origem_ub"] == "testemunha", k


def test_certificado_registrado_sem_verificador_aceitar_ou_acima_da_testemunha():
    cert = json.loads((DADOS / "certificados.json").read_text(encoding="utf-8"))
    test = json.loads((DADOS / "testemunhas.json").read_text(encoding="utf-8"))
    for k, c in cert.items():
        assert c["verificado"] is True and c["metodo"] in ("veripb", "drat"), k
        if c["metodo"] == "drat":
            assert c["unsat_ate"] == c["lb"] - 1, k
        assert c["lb"] <= test[k]["M"], k
        if "prova_gz" in c:
            assert (RAIZ / "segunda_ordem" / c["prova_gz"]).exists(), k


def test_tabela_nao_e_monotona_em_n_e_r():
    # K^(2)(n−1, r) <= K^(2)(n, r) (furar uma coordenada) e K^(2)(n, r+1) <= K^(2)(n, r).
    tab = tabela.montar()["celulas"]
    for k, c in tab.items():
        q, n, r = c["q"], c["n"], c["r"]
        acima = tab.get(tabela.chave(q, n, r + 1))
        if acima:
            assert acima["lb"] <= c["ub"], k
        menor = tab.get(tabela.chave(q, n - 1, r))
        if menor:
            assert menor["lb"] <= c["ub"], k


def test_cota_livre_usada_acima_do_que_o_ledger_diz_hoje():
    # O ledger só melhora cotas inferiores; se a tabela usou um valor maior que o atual, errou.
    tab = json.loads((DADOS / "tabela.json").read_text(encoding="utf-8"))["celulas"]
    agora = tabela._ledger_lb()
    for k, c in tab.items():
        q, n, r = c["q"], c["n"], c["r"]
        livres = c["cotas_livres"]
        if "K_q2_lb" in livres:
            assert livres["K_q2_lb"] <= agora[f"K{q * q}({n},{r})"], k
        if "K_q" in livres:
            assert livres["K_q"] <= agora[f"K{q}({n},{r})"], k


def test_indice_e_tupla_nao_fazem_ida_e_volta():
    for q, n in ((2, 5), (3, 4)):
        for x in range(q**n):
            assert para_inteiro(de_inteiros([x], q, n)[0], q) == x


def test_testemunha_do_lean_diverge_da_testemunha_publicada():
    import re

    lean = (RAIZ / "segunda_ordem" / "lean" / "SegundaOrdemUB.lean").read_text(encoding="utf-8")
    test = json.loads((DADOS / "testemunhas.json").read_text(encoding="utf-8"))
    achados = re.findall(r"def C_(\d)_(\d)_(\d) : List Nat := \[([\d, ]+)\]", lean)
    assert len(achados) == 2
    assert "sorry" not in lean and "native_decide" not in lean
    for q, n, r, lista in achados:
        q, n, r = int(q), int(n), int(r)
        idx = sorted(int(x) for x in lista.split(","))
        publicados = sorted(para_inteiro(tuple(int(ch) for ch in w), q) for w in test[f"{q},{n},{r}"]["palavras"])
        assert idx == publicados, (q, n, r)


def test_prova_comprimida_orfa_ou_faltando():
    cert = json.loads((DADOS / "certificados.json").read_text(encoding="utf-8"))
    citadas = {Path(c["prova_gz"]).name for c in cert.values() if "prova_gz" in c}
    no_disco = {p.name for p in (DADOS / "provas").glob("*.gz")}
    assert citadas == no_disco


def test_tabela_do_readme_diverge_dos_dados():
    readme = (RAIZ / "segunda_ordem" / "README.md").read_text(encoding="utf-8")
    assert tabela.bloco_readme(tabela.montar()) in readme, "rode: python3 -m segunda_ordem.tabela readme"


def test_celula_exata_com_cota_inferior_so_do_ledger():
    # Exato exige as duas cotas conferidas aqui; cota do ledger (literatura) sozinha não basta.
    nossas = {"teorema_q_palavras", "veripb", "drat", "esfera", "q_palavras"}
    for k, c in tabela.montar()["celulas"].items():
        if c["exato"]:
            assert nossas & set(c["origem_lb"]), k
