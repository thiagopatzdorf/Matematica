"""Lista da fatia mínima com canonização por nauty (tools/exatos/gaps2/nauty_fatia.py).

A lista é parte da prova de inexistência: órbita que falta vira instância que some e certificado
furado; órbita duplicada só custa tempo, mas indica forma canônica errada. Conferências contra
três fontes independentes: Burnside (tools/exatos/k362/redteam/burnside.py), `fatia.py`
(completude provada em docs/exatos/GAPS2_K362.md) e `aumento.py`.
"""
import itertools
import random
import shutil
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "tools" / "exatos" / "gaps2"))
sys.path.insert(0, str(RAIZ / "tools" / "exatos" / "k362" / "redteam"))

pytest.importorskip("numpy")
if not shutil.which("gcc") or not (Path("/usr/include/nauty").exists()
                                   or list(Path("/usr/include").glob("*/nauty/nauty.h"))):
    pytest.skip("sem gcc ou libnauty-dev", allow_module_level=True)

import aumento  # noqa: E402
import burnside  # noqa: E402
import fatia  # noqa: E402
import nauty_fatia as nf  # noqa: E402

GRANDE = 10**6  # cap que não filtra nada


@pytest.mark.parametrize("q,m,ss", [(3, 4, range(1, 6)), (3, 5, range(0, 6)), (3, 6, range(1, 5)),
                                    (2, 5, range(1, 8)), (4, 3, range(1, 6))])
def test_nauty_perde_ou_duplica_orbita_contra_burnside(q, m, ss):
    esperado = burnside.orbitas(q, m, list(ss))
    for s in ss:
        assert nf.contar(q, m, s, 1, GRANDE)[0] == esperado[s], (q, m, s)


def test_contagem_paralela_difere_da_sequencial():
    assert nf.contar(3, 5, 5, 1, GRANDE, j=3, corte=2)[0] == nf.contar(3, 5, 5, 1, GRANDE)[0] == 11075


# (8, 15) e (9, 10) também batem (9 e 16 órbitas), mas aumento.py leva 1 e 11 min neles.
@pytest.mark.parametrize("s,cap", [(4, 50), (5, 40), (6, 30), (7, 20)])
def test_filtro_do_nauty_difere_do_aumento_em_z3_4(s, cap):
    P, G = aumento.grupo(3, 4)
    a = sorted(fatia.forma(K) for K in aumento.configuracoes(3, 4, s, 1, cap, G, P))
    b = sorted(fatia.forma(K) for K in nf.configuracoes(3, 4, s, 1, cap))
    assert a == b


# (5, 2, 20) e (5, 1, 190) também batem, mas fatia.configuracoes leva 1 e 6 min neles.
@pytest.mark.parametrize("s,R,cap", [(3, 1, 150), (4, 1, 199), (4, 2, 40)])
def test_filtro_do_nauty_difere_da_fatia_em_z3_5(s, R, cap):
    a = sorted(fatia.forma(K) for K in fatia.configuracoes(3, 5, s, R, cap))
    b = sorted(fatia.forma(K) for K in nf.configuracoes(3, 5, s, R, cap))
    assert a == b


@pytest.mark.parametrize("q,n,R,M", [(3, 5, 2, 7), (3, 5, 2, 8), (3, 4, 1, 8), (3, 4, 1, 9)])
def test_lista_do_nauty_difere_da_lista_da_fatia(q, n, R, M):
    def formas(lista):
        return sorted((s, fatia.forma(list(K)) if K else (), t) for s, K, t in lista)

    assert formas(nf.instancias(q, n, R, M)) == formas(fatia.instancias(q, n, R, M))


def test_lista_k351_m26_difere_dos_343_do_aumento():
    """K_3(5,1) M = 26: aumento.py deu 343 instâncias (s* = 7: 3, s* = 8: 340) em ~12 min."""
    ins = nf.instancias(3, 5, 1, 26, j=2)
    assert len(ins) == 343
    assert sum(1 for s, _, _ in ins if s == 7) == 3


def _isometria(q, m, rng):
    sigma = list(range(m))
    rng.shuffle(sigma)
    pis = [rng.sample(range(q), q) for _ in range(m)]

    def g(x):
        y = [0] * m
        for i in range(m):
            y[sigma[i]] = pis[i][x[i]]
        return tuple(y)
    return g


def test_forma_do_nauty_muda_sob_isometria():
    rng = random.Random(5)
    pts = list(itertools.product(range(3), repeat=5))
    for _ in range(20):
        X = rng.sample(pts, rng.randint(1, 12))
        g = _isometria(3, 5, rng)
        Y = [g(x) for x in X]
        rng.shuffle(Y)
        assert nf.forma(3, 5, X) == nf.forma(3, 5, Y)


def test_forma_do_nauty_confunde_orbitas_diferentes():
    reps = nf.configuracoes(3, 4, 3, 1, GRANDE)
    assert len({nf.forma(3, 4, K) for K in reps}) == len(reps) == 20


def test_orcamento_negativo_devolve_lista_nao_vazia():
    # K_3(6,1) M = 72 com s* = 17: 17 bolas de 11 pontos não cobrem 243 − 55·1
    assert nf.orcamento(3, 5, 17, 1, 55) < 0
    assert nf.configuracoes(3, 5, 17, 1, 55) == []
