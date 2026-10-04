"""Lema das fibras geral e redução por prefixo de tipos (tools/exatos/fibras): completude.

Como em tests/test_k742.py, a completude da quebra de simetria é conferida de forma
construtiva: códigos de cobertura de raio n-2, embaralhados por elementos aleatórios de
S_q wr S_n (e ordem aleatória das palavras), são levados à forma normal e a atribuição tem de
satisfazer todas as cláusulas da CNF da sua instância. Sem solver externo.
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


def cobre_ponto(w, c, R):
    return sum(a != b for a, b in zip(w, c)) <= R


def codigo_guloso(q, n, rng):
    """Código de raio n-2 por guloso aleatório: um ponto descoberto, a melhor palavra entre
    algumas candidatas vizinhas. Só serve de entrada para os testes de completude."""
    R = n - 2
    pts = list(itertools.product(range(q), repeat=n))
    desc = set(pts)
    cod = []
    while desc:
        alvo = rng.choice(sorted(desc))
        cands = [tuple(rng.randrange(q) if rng.random() < 0.5 else a for a in alvo) for _ in range(40)]
        melhor = max(cands, key=lambda c: sum(1 for w in desc if cobre_ponto(w, c, R)))
        cod.append(melhor)
        desc = {w for w in desc if not cobre_ponto(w, melhor, R)}
    return sorted(set(cod))


def embaralhar(cod, q, n, rng):
    perm = list(range(n))
    rng.shuffle(perm)
    sims = [rng.sample(range(q), q) for _ in range(n)]
    out = [tuple(sims[i][c[perm[i]]] for i in range(n)) for c in cod]
    rng.shuffle(out)
    return out


def checar(cod, q, n, k, exige_cobertura=True, quebra_mutante=None):
    M = len(cod)
    smin = min(min(canonizar.tipo_da_coord(cod, i, q)) for i in range(n))
    idx, norm = canonizar.canonizar(cod, q, n, k, smin)
    _, ins = encode.instancias(q, n, M, k, smin)
    cnf, x, sim0, _ = encode.codificar(q, n, M, ins[idx], smin)
    if quebra_mutante:
        quebra_mutante(cnf, x, q, n, M, ins[idx])
    val = canonizar.atribuicao(cnf, x, norm, q, n)
    assert len(val) == cnf.nv, "variável auxiliar não ficou determinada"
    ruins = canonizar.violadas(cnf, val)
    if exige_cobertura:
        assert ruins == [], f"{len(ruins)} cláusulas violadas"
    else:
        npares = n * (n - 1) // 2
        assert all(len(c) == npares and all(l > 0 for l in c) for c in ruins)
        assert len(ruins) == canonizar.descobertos(norm, q, n) == canonizar.descobertos(cod, q, n)
    return norm


def test_lema_geral_reproduz_o_k742_em_k_q_4_2():
    for q, M, s in [(7, 17, 2), (7, 18, 2), (7, 19, 1), (8, 22, 2), (5, 10, 1)]:
        assert encode.fibra_minima(q, 4, 2, M) == s
    assert len(encode.instancias(7, 4, 17, 4)[1]) == 15
    assert len(encode.instancias(7, 4, 18, 4)[1]) == 70


def test_lema_geral_nos_alvos_da_triagem():
    assert encode.fibra_minima(7, 5, 3, 15) == 2   # K_7(5,3): uma instância só
    assert encode.contar_instancias(7, 5, 15, 5, 2) == (1, 1)
    assert encode.fibra_minima(7, 5, 3, 16) == 1   # K_6(4,2) = 15 <= 15: o lema cai para 1
    assert encode.fibra_minima(16, 4, 2, 86) == 4
    assert encode.contar_instancias(16, 4, 86, 4, 4)[1] > 10 ** 10
    # o lema sozinho prova K_6(5,3) >= 12 (s_min = 2, 6 * 2 > 11); K_5(5,3) >= 9 precisa de
    # SAT: s_min = 1 e 21 perfis (validação da família)
    assert encode.fibra_minima(6, 5, 3, 11) * 6 > 11
    assert encode.fibra_minima(5, 5, 3, 8) == 1
    assert encode.contar_instancias(5, 5, 8, 5, 1) == (3, 21)


@pytest.mark.parametrize("q,n,k,semente", [(4, 5, 5, 1), (4, 5, 2, 2), (5, 5, 1, 3), (3, 6, 6, 4),
                                            (3, 6, 3, 5), (5, 4, 4, 6), (4, 5, 3, 7)])
def test_codigo_embaralhado_satisfaz_a_cnf_da_sua_instancia(q, n, k, semente):
    rng = random.Random(semente)
    cod = codigo_guloso(q, n, rng)
    for _ in range(3):
        norm = checar(embaralhar(cod, q, n, rng), q, n, k)
        assert len(norm) == len(cod)


@pytest.mark.parametrize("q,n,k,semente", [(4, 5, 5, 11), (4, 5, 2, 12), (3, 6, 4, 13)])
def test_codigo_que_nao_cobre_viola_so_cobertura_um_por_ponto(q, n, k, semente):
    rng = random.Random(semente)
    cod = codigo_guloso(q, n, rng)
    for _ in range(3):
        quase = embaralhar(cod, q, n, rng)
        quase[0] = tuple(rng.randrange(q) for _ in range(n))  # pode descobrir pontos
        if min(min(canonizar.tipo_da_coord(quase, i, q)) for i in range(n)) == 0:
            continue
        checar(quase, q, n, k, exige_cobertura=False)


def mutante_precedencia_entre_classes(cnf, x, q, n, M, prefixo):
    """Quebra de simetria ERRADA: precedência entre símbolos de classes diferentes."""
    if len(prefixo) < 3:
        return
    for a in range(q - 1):
        for w in range(M):
            cnf.add([-x[w][2][a + 1]] + [x[ww][2][a] for ww in range(w)])


def test_mutante_da_quebra_de_simetria_e_pego():
    rng = random.Random(21)
    pegos = 0
    for _ in range(6):
        cod = codigo_guloso(4, 5, rng)
        try:
            checar(embaralhar(cod, 4, 5, rng), 4, 5, 5, quebra_mutante=mutante_precedencia_entre_classes)
        except AssertionError:
            pegos += 1
    assert pegos >= 1


def mutante_lex_invertido(cnf, x, q, n, M, prefixo):
    """Ordem lexicográfica ERRADA: também coluna 3 <=lex coluna 2 (força colunas iguais)."""
    encode.lex_leq(cnf, x, q, M, 3, 2)


@pytest.mark.parametrize("k", [2, 5])
def test_mutante_da_ordem_lexicografica_e_pego(k):
    rng = random.Random(31 + k)
    pegos = 0
    for _ in range(4):
        cod = codigo_guloso(4, 5, rng)
        try:
            checar(embaralhar(cod, 4, 5, rng), 4, 5, k, quebra_mutante=mutante_lex_invertido)
        except AssertionError:
            pegos += 1
    assert pegos >= 1


def test_ordem_lexicografica_e_exercitada_nas_colunas_livres():
    rng = random.Random(41)
    cod = codigo_guloso(4, 5, rng)
    smin = min(min(canonizar.tipo_da_coord(cod, i, 4)) for i in range(5))
    _, norm = canonizar.canonizar(embaralhar(cod, 4, 5, rng), 4, 5, 2, smin)
    cols = [[w[c] for w in norm] for c in range(2, 5)]
    assert cols == sorted(cols)


import fib_cubos  # noqa: E402


def _valida_coord1(q, M, t0, t1, smin, pal):
    """Condições da coordenada 1 escritas de outro jeito (força bruta)."""
    bl = encode.blocos(t0)
    cnt = [pal.count(a) for a in range(q)]
    if t1 is None:
        if min(cnt) < smin:
            return False
    elif cnt != list(t1):
        return False
    for B in bl:
        ws = list(B)
        if any(pal[w] > pal[w + 1] for w in ws[:-1]):
            return False
    for b in range(q - 1):
        if t0[b] == t0[b + 1] and t0[b] > 0 and [pal[w] for w in bl[b]] > [pal[w] for w in bl[b + 1]]:
            return False
    cls = encode.classes(q, t1)
    primeiro_bloco = {}
    for b, B in enumerate(bl):
        for w in B:
            primeiro_bloco.setdefault(pal[w], b)
    for a in range(q - 1):
        if cls[a] == cls[a + 1] and a + 1 in primeiro_bloco:
            if a not in primeiro_bloco or primeiro_bloco[a] > primeiro_bloco[a + 1]:
                return False
    return True


@pytest.mark.parametrize("q,M,t0,t1,smin", [
    (3, 6, (2, 2, 2), (3, 2, 1), 1), (3, 6, (3, 2, 1), (2, 2, 2), 1),
    (3, 7, (3, 2, 2), None, 2), (4, 6, (2, 2, 1, 1), (2, 2, 1, 1), 1)])
def test_cubos_da_coordenada_1_sao_exatamente_as_atribuicoes_validas(q, M, t0, t1, smin):
    bruto = sorted(p for p in itertools.product(range(q), repeat=M)
                   if _valida_coord1(q, M, t0, t1, smin, list(p)))
    assert fib_cubos.atribuicoes_coord1(q, M, t0, t1, smin) == bruto
    for L in range(1, M):
        assert fib_cubos.atribuicoes_coord1(q, M, t0, t1, smin, L) == sorted({p[:L] for p in bruto})


@pytest.mark.parametrize("k,semente", [(5, 51), (2, 52)])
def test_forma_normal_cai_em_algum_cubo(k, semente):
    rng = random.Random(semente)
    for _ in range(3):
        cod = codigo_guloso(4, 5, rng)
        smin = min(min(canonizar.tipo_da_coord(cod, i, 4)) for i in range(5))
        idx, norm = canonizar.canonizar(embaralhar(cod, 4, 5, rng), 4, 5, k, smin)
        _, ins = encode.instancias(4, 5, len(cod), k, smin)
        pref = list(ins[idx]) + [None] * (5 - k)
        L = min(6, len(cod))
        cubos = fib_cubos.atribuicoes_coord1(4, len(cod), pref[0], pref[1], smin, L)
        assert tuple(w[1] for w in norm[:L]) in cubos


def test_ordem_dos_blocos_h_precisa_do_guloso():
    """Sem o guloso do Lema 4 a forma normal viola (h) em algum código: as cláusulas (h)
    restringem de verdade, e é o guloso que as torna completas."""
    rng = random.Random(61)
    falhas = 0
    for _ in range(8):
        cod = embaralhar(codigo_guloso(4, 5, rng), 4, 5, rng)
        M = len(cod)
        smin = min(min(canonizar.tipo_da_coord(cod, i, 4)) for i in range(5))
        idx, norm = canonizar.canonizar(cod, 4, 5, 5, smin, usar_h=False)
        _, ins = encode.instancias(4, 5, M, 5, smin)
        cnf, x, _, _ = encode.codificar(4, 5, M, ins[idx], smin)
        val = canonizar.atribuicao(cnf, x, norm, 4, 5)
        falhas += bool(canonizar.violadas(cnf, val))
        checar(cod, 4, 5, 5)  # com o guloso, nada é violado
    assert falhas >= 1
