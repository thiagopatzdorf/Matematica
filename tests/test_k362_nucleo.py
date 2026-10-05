"""K_3(6,2), M = 15, frente núcleo (tools/exatos/k362): grupo, forma canônica e escolha canônica da fibra.

O que precisa valer para a redução ser completa: (1) o grupo age por isometrias (preserva
distância, logo raio de cobertura e tamanho); (2) a forma canônica do nauty separa exatamente as
classes (conferida contra a força bruta sobre o grupo e contra `fatia.forma`); (3) o lema da soma
vale em códigos que cobrem; (4) todo código equilibrado normalizado pela fibra de menor |U| cai
numa instância que sobrevive ao filtro novo e satisfaz o OPB reduzido. Docs: docs/exatos/k362/.
"""
import itertools
import os
import random
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "tools" / "exatos" / "gaps2"))
sys.path.insert(0, str(RAIZ / "tools" / "exatos" / "k362"))

pytest.importorskip("numpy")
import canon  # noqa: E402
import fatia  # noqa: E402
import grupo  # noqa: E402
import reducao  # noqa: E402

TEM_NAUTY = bool(os.environ.get("DREADNAUT") or shutil.which("dreadnaut"))
nauty = pytest.mark.skipif(not TEM_NAUTY, reason="dreadnaut (nauty) ausente")

C17 = [tuple(map(int, w)) for w in """100112 221220 111001 122120 201021 221122 002200 021110 002102
200100 010021 122222 212011 021212 220001 200202 100210""".split()]
HAMMING_3_4 = [tuple(map(int, w)) for w in "0000 0111 0222 1012 1120 1201 2021 2102 2210".split()]
K2_6_1_12 = [tuple(map(int, w)) for w in
             "010101 101010 110110 111100 001111 000100 110000 000011 011010 111011 100101 001001".split()]


def raio(cod, q, n):
    return max(min(fatia.dist(x, c) for c in cod) for x in itertools.product(range(q), repeat=n))


def test_composicao_e_inverso_do_grupo_agem_como_homomorfismo():
    rng = random.Random(1)
    for _ in range(2000):
        g, h = grupo.aleatorio(3, 6, rng), grupo.aleatorio(3, 6, rng)
        c = tuple(rng.randrange(3) for _ in range(6))
        assert grupo.aplica(grupo.compoe(g, h), c) == grupo.aplica(g, grupo.aplica(h, c))
        assert grupo.aplica(grupo.inverso(g), grupo.aplica(g, c)) == c
    assert grupo.ordem(3, 6) == 33_592_320


def test_toda_transformacao_do_grupo_preserva_distancia_tamanho_e_raio():
    rng = random.Random(2)
    for _ in range(200):
        g = grupo.aleatorio(3, 6, rng)
        img = grupo.aplica_codigo(g, C17)
        assert len(set(img)) == 17 and raio(img, 3, 6) == 2
        a, b = rng.sample(C17, 2)
        assert fatia.dist(grupo.aplica(g, a), grupo.aplica(g, b)) == fatia.dist(a, b)


@nauty
@pytest.mark.parametrize("s", [2, 3, 4])
def test_forma_do_nauty_separa_exatamente_as_classes_da_forca_bruta(s):
    pts = list(itertools.product(range(3), repeat=3))
    conj = list(itertools.combinations(pts, s))
    nau = canon.canon_nauty(conj, 3, 3)
    rng = random.Random(s)
    amostra = rng.sample(range(len(conj)), 60)
    fb = {i: canon.canon_forca_bruta(conj[i], 3, 3) for i in amostra}
    for i, k in itertools.combinations(amostra, 2):
        assert (nau[i][0] == nau[k][0]) == (fb[i] == fb[k])
    for i in amostra[:15]:
        assert nau[i][1] == canon.estabilizador_forca_bruta(conj[i], 3, 3)
    assert len({f for f, _ in nau}) == len(fatia.configuracoes(3, 3, s))


@nauty
def test_forma_do_nauty_nao_muda_sob_milhares_de_transformacoes_aleatorias():
    rng = random.Random(3)
    pts = list(itertools.product(range(3), repeat=5))
    base = [rng.sample(pts, 5) for _ in range(20)]
    lotes = [K for K in base for _ in range(150)]
    gs = [grupo.aleatorio(3, 5, rng) for _ in lotes]  # um elemento do grupo por imagem
    imgs = [[grupo.aplica(g, p) for p in K] for g, K in zip(gs, lotes)]
    f0 = canon.canon_nauty(lotes, 3, 5)
    f1 = canon.canon_nauty(imgs, 3, 5)
    assert all(a == b for a, b in zip(f0, f1))  # 3000 pares (forma e |Stab|)


@nauty
def test_representantes_nao_equivalentes_tem_formas_diferentes_no_nauty():
    reps = fatia.configuracoes(3, 4, 4)
    formas = [f for f, _ in canon.canon_nauty(reps, 3, 4)]
    assert len(set(formas)) == len(reps)


@pytest.mark.parametrize("cod,q,n,R", [(C17, 3, 6, 2), (HAMMING_3_4, 3, 4, 1), (K2_6_1_12, 2, 6, 1)])
def test_lema_da_soma_nao_falha_em_codigo_que_cobre(cod, q, n, R):
    rng = random.Random(4)
    pts = list(itertools.product(range(q), repeat=n))
    for extra in range(3):
        C = cod + rng.sample([p for p in pts if p not in cod], extra)
        soma_d = sum(min(fatia.dist(x, c) for c in C) for x in pts)
        assert sum(reducao.U_fibras(q, n, R, C).values()) <= soma_d <= R * (q ** n - len(C))


def _avalia(txt, z):
    ruins = []
    for ln in txt.splitlines()[1:]:
        tok = ln.rstrip(" ;").split()
        op, rhs = tok[-2], int(tok[-1])
        lhs = sum(int(tok[k]) * z[int(tok[k + 1][1:])] for k in range(0, len(tok) - 2, 2))
        if not (lhs >= rhs if op == ">=" else lhs == rhs):
            ruins.append(ln)
    return ruins


def _valores(q, n, R, var, cod):
    """z do código e w exato (x não coberto pela própria fibra na coordenada j)."""
    z = {v: int(c in set(cod)) for c, v in var.items()}
    k = len(var)
    for x in itertools.product(range(q), repeat=n):
        for j in range(n):
            k += 1
            z[k] = int(all(fatia.dist(c, x) > R for c in cod if c[j] == x[j]))
    return z


def _na_lista_reduzida(q, n, R, M, inst):
    """Mesmo critério de fatia.instancias + reducao.reduz, sem enumerar: K é o representante
    canônico da sua classe, passa no filtro de contagem e no teto novo de |U|."""
    s, K, t = inst
    u = reducao.n_descobertos(q, n - 1, R, K)
    return (tuple(fatia.de_colunas(fatia.forma(list(K)))) == K and t in fatia.blocos_restantes(q, M, s)
            and u <= (M - s) * fatia.vol(n - 1, R - 1, q) and u <= reducao.limite_U(q, n, R, M))


@pytest.mark.parametrize("regra", ["min", "max"])
@pytest.mark.parametrize("cod,q,n,R", [(HAMMING_3_4, 3, 4, 1), (K2_6_1_12, 2, 6, 1)])
def test_codigo_equilibrado_que_cobre_cai_em_instancia_reduzida_e_satisfaz_o_opb(cod, q, n, R, regra):
    M = len(cod)
    rng = random.Random(5)
    for _ in range(10):
        img = grupo.aplica_codigo(grupo.aleatorio(q, n, rng), cod)
        inst, norm = reducao.normalizar_canonica(img, q, n, R, regra)
        if regra == "min":
            assert _na_lista_reduzida(q, n, R, M, inst)
        txt, var = reducao.opb(q, n, R, M, inst, regra)
        assert _avalia(txt, _valores(q, n, R, var, norm)) == []


def test_lista_reduzida_do_hamming_ternario_bate_com_o_criterio_sem_enumerar():
    lista = reducao.reduz(3, 4, 1, 9, fatia.instancias(3, 4, 1, 9))
    assert lista and all(_na_lista_reduzida(3, 4, 1, 9, i) for i in lista)


def _equilibrado_aleatorio(rng):
    while True:
        cols = [rng.sample([0] * 5 + [1] * 5 + [2] * 5, 15) for _ in range(6)]
        cod = [tuple(c[k] for c in cols) for k in range(15)]
        if len(set(cod)) == 15:
            return cod


@pytest.mark.parametrize("regra", ["min", "max"])
def test_normalizacao_errada_de_proposito_viola_a_quebra_de_simetria(regra):
    # fibra 0 escolhida pela regra oposta: alguma restrição de |U| tem de falhar (o código não
    # cobre, então as de cobertura também falham; as de w e de fibra, nunca)
    rng = random.Random(6)
    while True:
        cod = _equilibrado_aleatorio(rng)
        if len(set(reducao.U_fibras(3, 6, 2, cod).values())) > 1:
            break
    certo, norm = reducao.normalizar_canonica(cod, 3, 6, 2, regra)
    oposta = "max" if regra == "min" else "min"
    errado, norm_e = reducao.normalizar_canonica(cod, 3, 6, 2, oposta)
    def fora_da_cobertura(inst, cd):
        txt, z = _texto_e_valores(inst, cd, regra)
        cobertura = set(txt.splitlines()[1:1 + 3 ** 6])  # fatia_pb escreve a cobertura primeiro
        return [r for r in _avalia(txt, z) if r not in cobertura]
    assert fora_da_cobertura(certo, norm) == []
    assert fora_da_cobertura(errado, norm_e) != []


def _texto_e_valores(inst, norm, regra):
    txt, var = reducao.opb(3, 6, 2, 15, inst, regra)
    return txt, _valores(3, 6, 2, var, norm)


def test_teto_de_U_para_k362_m15_e_79():
    assert reducao.limite_U(3, 6, 2, 15) == 79
    assert reducao.equilibrada(3, 15, 5) and not reducao.equilibrada(3, 15, 4)


@pytest.mark.skipif(not os.environ.get("ROUNDINGSAT"), reason="ROUNDINGSAT ausente")
@pytest.mark.parametrize("regra", ["min", "max"])
@pytest.mark.parametrize("q,n,R,M", [(3, 4, 1, 9), (2, 4, 1, 4)])
def test_reducao_nao_perde_o_codigo_que_existe(q, n, R, M, regra, tmp_path):
    achou = False
    lista = fatia.instancias(q, n, R, M)
    for inst in (reducao.reduz(q, n, R, M, lista) if regra == "min" else lista):
        p = tmp_path / "x.opb"
        p.write_text(reducao.opb(q, n, R, M, inst, regra)[0])
        out = subprocess.run([os.environ["ROUNDINGSAT"], str(p)], capture_output=True, text=True).stdout
        achou |= "s SATISFIABLE" in out
    assert achou
