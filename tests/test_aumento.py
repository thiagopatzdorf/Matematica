"""Lista da fatia mínima por aumento canônico (tools/exatos/gaps2/aumento.py).

A lista é parte da prova de inexistência: se faltar uma órbita, uma instância some e o
certificado vira furado. Os testes comparam com `fatia.py`, cuja completude já está provada
(docs/exatos/GAPS2_K362.md) e conferida por Burnside.
"""
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "tools" / "exatos" / "gaps2"))

pytest.importorskip("numpy")

import aumento  # noqa: E402
import fatia  # noqa: E402


@pytest.fixture(scope="module")
def grupo34():
    return aumento.grupo(3, 4)


def test_aumento_perde_ou_duplica_orbita_de_subconjuntos_de_z3_4(grupo34):
    P, G = grupo34
    assert len(G) == 6 ** 4 * 24
    for s in range(1, 5):
        assert len(aumento.configuracoes(3, 4, s, 1, 81, G, P)) == len(fatia.configuracoes(3, 4, s))


@pytest.mark.parametrize("q,n,R,M", [(3, 5, 2, 7), (3, 5, 2, 8), (3, 4, 1, 8), (3, 4, 1, 9)])
def test_lista_por_aumento_difere_da_lista_da_fatia(q, n, R, M):
    def formas(lista):
        return sorted((s, fatia.forma(list(K)) if K else (), t) for s, K, t in lista)

    assert formas(aumento.instancias(q, n, R, M)) == formas(fatia.instancias(q, n, R, M))


def test_poda_do_aumento_descarta_conjunto_valido(grupo34):
    """Com a poda hereditária ligada, nenhum conjunto que passa no filtro pode sumir: o mesmo
    filtro calculado só no fim (cap enorme na poda, filtro depois) dá as mesmas órbitas."""
    P, G = grupo34
    cap = 50
    com_poda = aumento.configuracoes(3, 4, 4, 1, cap, G, P)
    sem_poda = [K for K in aumento.configuracoes(3, 4, 4, 1, 81, G, P)
                if len(fatia.descobertos(3, 4, 1, K)) <= cap]
    f = lambda L: sorted(fatia.forma(list(K)) for K in L)  # noqa: E731
    assert f(com_poda) == f(sem_poda)
