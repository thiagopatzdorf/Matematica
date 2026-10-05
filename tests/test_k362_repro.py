"""Reprodução independente de K_3(6,2) >= 16 (tools/exatos/k362_repro): enumeração por colunas,
canonização por nauty com grafo próprio, e cadeia SAT/PB com prova conferida."""
import itertools
from fractions import Fraction
import os
import random
import shutil
import subprocess
import sys

import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "tools", "exatos", "k362_repro"))
import repro_enumera as enumera  # noqa: E402
import repro_sat as sat  # noqa: E402


def _nauty():
    try:
        import repro_canon as canon
        return canon, canon.binario()
    except (subprocess.CalledProcessError, FileNotFoundError):
        pytest.skip("libnauty-dev/gcc ausente")


def _binarios(formato):
    nomes = ["roundingsat", "veripb"] if formato == "opb" else ["cadical", "lrat-check"]
    d = os.environ.get("K362_REPRO_BIN", "")
    caminhos = {b: os.path.join(d, b) if d else shutil.which(b) for b in nomes}
    if not all(c and os.path.exists(c) for c in caminhos.values()):
        pytest.skip("solver/verificador ausente (defina K362_REPRO_BIN)")
    return caminhos


def _isometria(q, m, rng):
    pi = list(range(m))
    rng.shuffle(pi)
    sig = [rng.sample(range(q), q) for _ in range(m)]
    return lambda p: tuple(sig[i][p[pi[i]]] for i in range(m))


def _num(p, q):
    return sum(v * q ** (len(p) - 1 - i) for i, v in enumerate(p))


@pytest.mark.parametrize("q,m,s", [(3, 3, 2), (3, 3, 3), (3, 4, 4), (2, 4, 3), (2, 5, 4), (3, 5, 3), (3, 5, 4)])
def test_enumeracao_por_colunas_perde_ou_repete_classe_contra_burnside(q, m, s):
    assert len(enumera.classes(q, m, s)) == enumera.burnside_orbitas(q, m, s)


def test_burnside_errado_em_caso_pequeno_contado_a_mao():
    # 2 pontos de Z_3^3: classes = distâncias 1, 2, 3
    assert enumera.burnside_orbitas(3, 3, 2) == 3
    # pontos isolados de Z_q^m: uma classe só
    assert enumera.burnside_orbitas(3, 5, 1) == 1


def test_lema_da_fatia_deixa_numero_errado_de_configuracoes_para_k362_m15():
    vivos = [sum(enumera.passa_filtro(K, 3, 2, 15) for K in enumera.classes(3, 5, s)) for s in (1, 2, 3, 4)]
    assert vivos == [0, 1, 27, 468]
    assert 3 ** 5 > 15 * enumera.volume(5, 1, 3)  # s = 0: a fatia vazia não se cobre


def test_formas_de_colunas_e_de_nauty_discordam_sobre_quais_conjuntos_sao_equivalentes():
    canon, exe = _nauty()
    rng = random.Random(7)
    P = list(itertools.product(range(3), repeat=4))
    conj = [rng.sample(P, 4) for _ in range(150)]
    rng2 = random.Random(8)
    conj += [[_isometria(3, 4, rng2)(p) for p in c] for c in conj[:50]]  # força pares equivalentes
    fc = [enumera.forma(c) for c in conj]
    fn = [f for f, _ in canon.formas([[_num(p, 3) for p in c] for c in conj], 3, 4, exe)]
    pares = list(itertools.combinations(range(len(conj)), 2))
    assert all((fc[i] == fc[j]) == (fn[i] == fn[j]) for i, j in pares)
    assert sum(fc[i] == fc[j] for i, j in pares) >= 50


def test_forma_do_nauty_muda_sob_isometria_aleatoria_de_z3_5():
    canon, exe = _nauty()
    rng = random.Random(11)
    P = list(itertools.product(range(3), repeat=5))
    base = [rng.sample(P, 5) for _ in range(20)]
    imgs = []
    for c in base:
        for _ in range(30):
            g = _isometria(3, 5, rng)  # um elemento do grupo por imagem, aplicado a todos os pontos
            imgs.append((c, [g(p) for p in c]))
    a = canon.formas([[_num(p, 3) for p in c] for c, _ in imgs], 3, 5, exe)
    b = canon.formas([[_num(p, 3) for p in d] for _, d in imgs], 3, 5, exe)
    assert a == b


def test_estabilizador_do_nauty_difere_da_forca_bruta_em_z3_3():
    canon, exe = _nauty()
    rng = random.Random(3)
    P = list(itertools.product(range(3), repeat=3))
    grupo = [(pi, sig) for pi in itertools.permutations(range(3))
             for sig in itertools.product(list(itertools.permutations(range(3))), repeat=3)]
    for _ in range(12):
        c = set(rng.sample(P, rng.randint(2, 5)))
        bruto = sum({tuple(sg[i][p[pi[i]]] for i in range(3)) for p in c} == c for pi, sg in grupo)
        assert canon.formas([[_num(p, 3) for p in c]], 3, 3, exe)[0][1] == bruto


def test_classificacao_de_k341_igual_a_9_nao_da_codigo_unico_pelos_dois_metodos():
    canon, exe = _nauty()
    assert len(canon.classificar(3, 4, 1, 9, exe)) == 1
    pytest.importorskip("pysat")
    assert len(canon.classificar_por_reducao(3, 4, 1, 9, exe)) == 1


# Lentos (100 s e 170 s neste container): ligue com K362_REPRO_LENTO=1. Resultados em K3_M15_REPRODUCAO.md.
@pytest.mark.skipif(not os.environ.get("K362_REPRO_LENTO"), reason="lento; K362_REPRO_LENTO=1")
@pytest.mark.parametrize("metodo,q,n,R,M,esperado", [("classificar_por_reducao", 3, 5, 2, 8, 1),
                                                      ("classificar", 3, 6, 3, 6, 28)])
def test_classificacao_publicada_nao_reproduzida(metodo, q, n, R, M, esperado):
    canon, exe = _nauty()
    if metodo == "classificar_por_reducao":
        pytest.importorskip("pysat")
    assert len(getattr(canon, metodo)(q, n, R, M, exe)) == esperado


def _normalizar(C, q, n):
    """Leva uma fibra mínima para (coordenada 0, símbolo 0); devolve (s, K, código transformado)."""
    j, a = min(((j, a) for j in range(n) for a in range(q)), key=lambda t: sum(c[t[0]] == t[1] for c in C))
    ordem = [j] + [i for i in range(n) if i != j]
    D = [tuple((c[i] - a) % q if i == j else c[i] for i in ordem) for c in C]
    K = [c[1:] for c in D if c[0] == 0]
    return len(K), K, D


# código de 17 palavras de K_3(6,2) (dado copiado de tests/test_gaps2.py; achado por recozimento)
C17 = [tuple(map(int, w)) for w in """100112 221220 111001 122120 201021 221122 002200 021110 002102
200100 010021 122222 212011 021212 220001 200202 100210""".split()]
# código de Hamming ternário [4,2,3]: perfeito, raio 1, 9 palavras
HAMMING = [tuple((x * g1 + y * g2) % 3 for g1, g2 in zip((1, 0, 1, 1), (0, 1, 1, 2)))
           for x in range(3) for y in range(3)]


@pytest.mark.parametrize("q,n,R,C", [(3, 4, 1, HAMMING), (3, 6, 2, C17)])
def test_restricao_que_viola_codigo_verdadeiro_tornaria_a_reducao_falsa(q, n, R, C):
    rng = random.Random(5)
    for _ in range(10):
        g = _isometria(q, n, rng)
        s, K, D = _normalizar([g(c) for c in C], q, n)
        M = len(D)
        assert sat.raio(q, n, D) <= R
        livres = [c for c in itertools.product(range(q), repeat=n) if c[0] != 0]
        for completa in (False, True):
            cob, nv, teto, fib = sat.restricoes(q, n, R, M, K, completa)
            if completa:
                um = {livres.index(c) + 1 for c in D if c[0] != 0}
            else:
                P = list(itertools.product(range(q), repeat=n - 1))
                um = {P.index(c[1:]) + 1 for c in D if c[0] != 0}
            assert len(um) <= teto and all(um & set(cl) for cl in cob)
            assert all(len(um & set(lits)) >= k for lits, k in fib)
        assert enumera.forma(K) in {enumera.forma(k) for k in enumera.classes(q, n - 1, s)}


@pytest.mark.parametrize("formato", ["opb", "cnf"])
def test_cadeia_nao_reproduz_k352_igual_a_8(formato, tmp_path):
    import repro_rodar as rodar
    b = _binarios(formato)
    d = os.path.dirname(next(iter(b.values())))
    assert rodar.main(["3", "5", "2", "7", "--formato", formato, "--bin", d, "--saida", str(tmp_path / "a")]) \
        == {("UNSAT", "VERIFIED"): 5}
    rodar.main(["3", "5", "2", "8", "--formato", formato, "--bin", d, "--saida", str(tmp_path / "b")])
    import json
    regs = [json.loads(ln) for ln in open(tmp_path / "b")]
    sats = [r for r in regs if r["veredito"] == "SAT"]
    assert sats and all(r["codigo_confere"] for r in sats)


def test_registro_de_m15_tem_instancia_faltando_ou_sem_prova_conferida():
    """O registro versionado cobre exatamente a lista de instâncias, e cada uma tem prova VeriPB aceita."""
    import gzip
    import json
    import repro_rodar as rodar
    reg = os.path.join(RAIZ, "tools", "exatos", "k362_repro", "registros", "K3_6_2_M15_opb.jsonl.gz")
    linhas = [json.loads(ln) for ln in gzip.open(reg, "rt")]
    assert all((r[3] or r[2])[1:3] == ["UNSAT", "VERIFIED"] for r in linhas)
    lista = {(s, ",".join("".join(map(str, k)) for k in K)) for s, K in rodar.instancias(3, 6, 2, 15)}
    assert {(r[0], r[1]) for r in linhas} == lista and len(linhas) == len(lista) == 11496
    # a fórmula é determinística: o sha256 regenerado bate com o registrado
    for r in random.Random(1).sample(linhas, 15):
        K = [tuple(map(int, k)) for k in r[1].split(",")]
        texto = sat.opb(*sat.restricoes(3, 6, 2, 15, K, False))
        assert __import__("hashlib").sha256(texto.encode()).hexdigest() == r[2][0]


def test_ramo_da_divisao_por_fibras_exclui_o_proprio_codigo():
    """O código de 17 palavras, normalizado (f_1 >= f_2 na coordenada 0), satisfaz todas as linhas do ramo
    que a divisão lhe atribui; e os ramos de cada coordenada cobrem a sua distribuição real."""
    import repro_divisao as div
    rng = random.Random(9)
    for _ in range(5):
        g = _isometria(3, 6, rng)
        s, K, D = _normalizar([g(c) for c in C17], 3, 6)
        if sum(c[0] == 1 for c in D) < sum(c[0] == 2 for c in D):
            D = [((3 - c[0]) % 3,) + c[1:] for c in D]
        dist = [tuple(sum(c[j] == a for c in D) for a in range(3)) for j in range(6)]
        assert all(dist[j] in div.opcoes(j, 17, s) for j in range(6))
        inst = div.Instancia(3, 6, 2, 17, K)
        livres = [c for c in itertools.product(range(3), repeat=6) if c[0] != 0]
        x = {livres.index(c) + 1 for c in D if c[0] != 0}
        for idx, a, r in inst.linhas([(j, dist[j]) for j in range(3)]):
            assert a * len(x & set(idx)) >= r


def test_verificador_de_farkas_aceita_certificado_adulterado():
    import repro_farkas as fk
    L = [([1], 1, 1), ([1], -1, 0)]  # x1 >= 1 e x1 <= 0
    assert fk.confere(L, 1, [Fraction(1), Fraction(1)]) > 0
    assert fk.confere(L, 1, [Fraction(1), Fraction(0)]) <= 0  # sem o segundo multiplicador não prova
    assert fk.confere(L, 1, [Fraction(1), Fraction(-1)]) < 0  # multiplicador negativo é recusado


def test_farkas_nao_fecha_o_ramo_8_4_da_instancia_s4_de_m16():
    pytest.importorskip("scipy")
    import repro_divisao as div
    import repro_farkas as fk
    K = [tuple(map(int, w)) for w in "00000,00111,00222,11012".split(",")]
    inst = div.Instancia(3, 6, 2, 16, K)
    L = inst.linhas([(0, (4, 8, 4))])
    y = fk.racionalizar(fk.gerar(L, inst.nv))
    assert fk.confere(L, inst.nv, y) > 0
    y[max(range(len(y)), key=lambda i: y[i])] = Fraction(0)  # tirar o maior multiplicador quebra a prova
    assert fk.confere(L, inst.nv, y) <= 0
