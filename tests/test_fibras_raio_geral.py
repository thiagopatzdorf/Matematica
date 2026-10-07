"""Lema 2' (R < n - 2): cobertura por projeções de t-uplas, t = n - R, no codificador de fibras.

Mesma bateria do `test_fibras.py` para o caminho novo de `fib_encode.codificar(..., R=...)`:
completude (código de cobertura embaralhado satisfaz a CNF da sua instância) e exatidão da
cobertura (código que não cobre viola só cláusulas de cobertura, uma por ponto descoberto).
"""
import itertools
import random
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "tools" / "exatos" / "fibras"))

import fib_canon as canonizar  # noqa: E402
import fib_encode as encode  # noqa: E402


def dist(a, b):
    return sum(x != y for x, y in zip(a, b))


def codigo_guloso(q, n, R, rng):
    pts = list(itertools.product(range(q), repeat=n))
    desc = set(pts)
    cod = []
    while desc:
        alvo = rng.choice(sorted(desc))
        cands = [tuple(rng.randrange(q) if rng.random() < 0.5 else a for a in alvo) for _ in range(40)]
        melhor = max(cands, key=lambda c: sum(1 for w in desc if dist(w, c) <= R))
        cod.append(melhor)
        desc = {w for w in desc if dist(w, melhor) > R}
    return sorted(set(cod))


def embaralhar(cod, q, n, rng):
    perm = list(range(n))
    rng.shuffle(perm)
    sims = [rng.sample(range(q), q) for _ in range(n)]
    out = [tuple(sims[i][c[perm[i]]] for i in range(n)) for c in cod]
    rng.shuffle(out)
    return out


def checar(cod, q, n, R, k, exige_cobertura=True, ordem="min"):
    M = len(cod)
    smin = min(min(canonizar.tipo_da_coord(cod, i, q)) for i in range(n))
    idx, norm = canonizar.canonizar(cod, q, n, k, smin, ordem=ordem)
    _, ins = encode.instancias(q, n, M, k, smin, ordem=ordem)
    cnf, x, sim0, _ = encode.codificar(q, n, M, ins[idx], smin, R=R)
    val = canonizar.atribuicao(cnf, x, norm, q, n)
    assert len(val) == cnf.nv, "variável auxiliar não ficou determinada"
    ruins = canonizar.violadas(cnf, val)
    if exige_cobertura:
        assert ruins == [], f"{len(ruins)} cláusulas violadas"
    else:
        largura = len(list(itertools.combinations(range(n), n - R)))
        assert all(len(c) == largura and all(l > 0 for l in c) for c in ruins)
        assert len(ruins) == canonizar.descobertos(norm, q, n, R) == canonizar.descobertos(cod, q, n, R)
        assert len(ruins) > 0
    return norm


CASOS = [(3, 5, 2, 5, 1), (3, 5, 2, 2, 2), (3, 6, 3, 6, 3), (4, 5, 2, 5, 4), (4, 5, 2, 3, 5),
         (3, 6, 2, 6, 6), (2, 7, 3, 7, 7), (4, 6, 3, 2, 8)]


@pytest.mark.parametrize("q,n,R,k,semente", CASOS)
def test_codigo_de_raio_menor_que_n_menos_2_embaralhado_satisfaz_a_cnf_de_tuplas(q, n, R, k, semente):
    rng = random.Random(semente)
    cod = codigo_guloso(q, n, R, rng)
    for ordem in ("min", "max"):
        for _ in range(2):
            norm = checar(embaralhar(cod, q, n, rng), q, n, R, k, ordem=ordem)
            assert len(norm) == len(cod)


@pytest.mark.parametrize("q,n,R,k,semente", CASOS[:6])
def test_cnf_de_tuplas_aponta_exatamente_uma_clausula_por_ponto_descoberto(q, n, R, k, semente):
    rng = random.Random(100 + semente)
    cod = codigo_guloso(q, n, R, rng)
    feitos = 0
    for _ in range(20):
        quase = embaralhar(cod, q, n, rng)
        del quase[rng.randrange(len(quase))]
        if min(min(canonizar.tipo_da_coord(quase, i, q)) for i in range(n)) == 0:
            continue
        if canonizar.descobertos(quase, q, n, R) == 0:
            continue
        checar(quase, q, n, R, rng.randint(1, n), exige_cobertura=False)
        feitos += 1
    assert feitos > 0, "nenhum caso exercitado: troque a semente"


def test_raio_n_menos_2_explicito_gera_a_mesma_cnf_que_o_padrao():
    _, ins = encode.instancias(5, 5, 8, 5, 1)
    a = encode.codificar(5, 5, 8, ins[3], 1)[0]
    b = encode.codificar(5, 5, 8, ins[3], 1, R=3)[0]
    assert a.cl == b.cl and a.nv == b.nv


def test_lema_das_fibras_nos_alvos_de_raio_menor():
    # K_4(7,4), M = 9: K_4(6,3) >= 11 > 9 exclui fibra vazia; K_3(6,3) = 6 <= 8 deixa s = 1
    assert encode.fibra_minima(4, 7, 4, 9) == 1
    assert encode.contar_instancias(4, 7, 9, 7, 1) == (6, 792)
    # K_3(7,3), M = 11: K_3(6,2) >= 15 > 11; K_2(6,2) = 4 <= 10
    assert encode.fibra_minima(3, 7, 3, 11) == 1
    assert encode.contar_instancias(3, 7, 11, 7, 1) == (10, 11440)
