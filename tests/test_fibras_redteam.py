"""Red team de K_7(6,4) = 14 (tools/exatos/fibras_redteam): os testes rápidos que sustentam o
relatório docs/exatos/REDTEAM_K764.md. Os que precisam do codificador auditado
(tools/exatos/fibras, PR #56) só rodam quando ele está na árvore."""
import itertools
import random
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
RT = RAIZ / "tools" / "exatos" / "fibras_redteam"
sys.path.insert(0, str(RT))

import canon_corrigido  # noqa: E402
import contraexemplo_h  # noqa: E402
import cota_superior  # noqa: E402
import perfis_indep  # noqa: E402
import predicados  # noqa: E402
from completude import codigo_aleatorio, embaralhar  # noqa: E402

CODIGO_14 = """000000 011111 100011 122200 212222 221122 333333
343444 434455 444366 555534 565643 656665 666556""".split()


def test_codigo_de_14_cobre_z7_6_com_raio_4_e_trocar_uma_palavra_descobre():
    cod = [tuple(int(ch) for ch in p) for p in CODIGO_14]
    _, mult = cota_superior.multiplicidade_de_cobertura(cod, 7, 6, 4)
    assert len(set(cod)) == 14 and mult.min() >= 1
    ruim = cod[:-1] + [(0, 0, 0, 0, 0, 1)]
    _, mult = cota_superior.multiplicidade_de_cobertura(ruim, 7, 6, 4)
    assert (mult == 0).sum() > 0


def test_perfis_de_k7_6_4_com_13_sao_8008_e_de_k7_5_3_com_15_e_um():
    assert len(perfis_indep.tipos_forca_bruta(7, 13, 1)) == 11
    assert len(perfis_indep.perfis(7, 6, 13, 1)) == 8008
    assert perfis_indep.perfis(7, 5, 15, 2) == {((3, 2, 2, 2, 2, 2, 2),) * 5}


def test_guloso_do_repo_viola_h_no_contraexemplo_e_o_corrigido_nao():
    C, q, n = contraexemplo_h.C, contraexemplo_h.Q, contraexemplo_h.N
    assert predicados.viola(contraexemplo_h.FORMA_REPO, q) == ["h0"]
    assert contraexemplo_h.mesma_orbita(C, contraexemplo_h.FORMA_REPO, q, n)
    _, norm = canon_corrigido.canonizar(C, q, n)
    assert predicados.viola(norm, q) == []
    assert contraexemplo_h.mesma_orbita(C, norm, q, n)


@pytest.mark.parametrize("q,n,M,smin", [(4, 3, 10, 1), (5, 4, 11, 1), (7, 5, 15, 2), (7, 6, 13, 1)])
def test_forma_normal_corrigida_satisfaz_a_ate_h_em_codigos_aleatorios(q, n, M, smin):
    rng = random.Random(q * 100 + M)
    for _ in range(300):
        C = embaralhar(codigo_aleatorio(q, n, M, smin, rng), q, n, rng)
        _, norm = canon_corrigido.canonizar(C, q, n)
        assert len(norm) == M
        assert predicados.viola(norm, q) == []
        assert sorted(predicados.tipo(norm, i, q) for i in range(n)) == sorted(predicados.tipo(C, i, q) for i in range(n))


def test_predicado_h_pega_guloso_sem_multiplicidade():
    """Mutante do guloso corrigido (rótulos novos na ordem do índice, como no repo): o predicado
    (h) tem de reprovar ao menos um código numa amostra que contém o padrão do contraexemplo."""
    C = contraexemplo_h.C
    assert predicados.viola(contraexemplo_h.FORMA_REPO, 4) != []
    assert predicados.viola(sorted(C), 4) != []  # o código cru não está em forma normal


def test_lista_de_perfis_de_k7_5_3_com_16_nao_perde_nem_inventa_perfil():
    # 201 376 é o total que o repo afirma ter fechado (registros inteiros + 2 perfis por cubos)
    assert len(perfis_indep.tipos_forca_bruta(7, 16, 1)) == 28
    assert len(perfis_indep.perfis(7, 5, 16, 1)) == 201376


def test_tipo_gravado_sem_separador_com_parte_de_dois_digitos_e_lido_sem_ambiguidade():
    from k753_perfis import ler_tipo
    assert ler_tipo("10111111", 7, 16, 1) == (10, 1, 1, 1, 1, 1, 1)
    assert ler_tipo("3322222", 7, 16, 1) == (3, 3, 2, 2, 2, 2, 2)
    with pytest.raises(ValueError):
        ler_tipo("3322222", 7, 15, 1)  # soma errada: nenhuma leitura


def test_codificacao_independente_reproduz_k4_4_2_igual_a_7():
    pytest.importorskip("pysat")
    import indep_perfil
    from pysat.solvers import Solver

    def sat(q, n, M, p):
        f, X = indep_perfil.codificar(q, n, M, list(p))
        with Solver(name="cadical195", bootstrap_with=f.cl) as s:
            if not s.solve():
                return None
            return indep_perfil.decodificar(s.get_model(), X, q, n, M)

    assert all(sat(4, 4, 6, p) is None for p in perfis_indep.perfis(4, 4, 6, 1))
    achados = [c for c in (sat(4, 4, 7, p) for p in perfis_indep.perfis(4, 4, 7, 1)) if c]
    assert len(achados) == 5
    for C in achados:
        assert all(any(sum(a != b for a, b in zip(v, c)) <= 2 for c in C)
                   for v in itertools.product(range(4), repeat=4))


FIBRAS = RAIZ / "tools" / "exatos" / "fibras"


@pytest.mark.skipif(not (FIBRAS / "fib_encode.py").exists(), reason="codificador do PR #56 ausente")
def test_orbita_do_contraexemplo_satisfaz_a_cnf_do_repo_e_mutante_de_h_e_pego():
    pytest.importorskip("pysat")
    import orbita_fibras
    enc = orbita_fibras.carregar_encode(str(FIBRAS))
    assert orbita_fibras.orbita_sat(enc, contraexemplo_h.C, 4, 3, cobertura=False)
    fonte = (FIBRAS / "fib_encode.py").read_text()
    a = "lex_leq_listas(cnf, [x[w][1] for w in A], [x[w][1] for w in B], q)"
    mut = orbita_fibras.carregar_encode(str(FIBRAS), fonte.replace(a, a + "; " + a.replace("in A]", "in Z]").replace("in B]", "in A]").replace("in Z]", "in B]")), "mut_h")
    assert not orbita_fibras.orbita_sat(mut, contraexemplo_h.C, 4, 3, cobertura=False)
