"""K_3(6,1) por sequências (tools/exatos/k361): o sistema de cobertura e a CNF do y-SIP.

O argumento "não existe código de 72 palavras" depende de: (1) a lista de sequências cobrir
todo código (enumeração do sistema de cobertura, módulo o grupo de ordem 72); (2) a CNF de cada
sequência aceitar todo código com aquela sequência; (3) a quebra de simetria (lex-leader) não
perder a classe inteira. (1) é conferido contra as contagens publicadas; (2) e (3) com códigos
conhecidos embaralhados e com a semântica das auxiliares. Sem solver externo.
"""
import itertools
import random
import subprocess
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
K361 = RAIZ / "tools" / "exatos" / "k361"
sys.path.insert(0, str(K361))

import ysip  # noqa: E402


@pytest.fixture(scope="module")
def sistema(tmp_path_factory):
    exe = tmp_path_factory.mktemp("k361") / "sistema"
    subprocess.run(["cc", "-O2", "-o", str(exe), str(K361 / "sistema.c")], check=True)

    def rodar(v, M, p=0, todas=False):
        env = {"TODAS": "1"} if todas else {}
        out = subprocess.run([str(exe), str(v), str(M), str(p), str(p)], capture_output=True,
                             text=True, check=True, env=env).stdout.splitlines()
        seqs = [tuple(map(int, ln.split())) for ln in out if not ln.startswith("#")]
        return seqs, out[-1]
    return rodar


@pytest.mark.parametrize("v,M,p,orbitas", [
    (6, 66, 0, 1674),   # Margot et al. 2003, citado em LMT 2009, seção 3.2
    (6, 66, 20, 797),   # LMT 2009, tabela 2 (cota de fibra y_j >= 20 nas duas coordenadas)
    (6, 67, 20, 1723),  # idem
    (5, 26, 0, 8),
])
def test_sistema_reproduz_contagens_publicadas_de_sequencias(sistema, v, M, p, orbitas):
    seqs, ultima = sistema(v, M, p)
    assert len(seqs) == orbitas, ultima


def _imagem(y, r, s, t):
    z = [0] * 9
    for j in range(3):
        for k in range(3):
            jj, kk = r[j], s[k]
            if t:
                jj, kk = kk, jj
            z[3 * jj + kk] = y[3 * j + k]
    return tuple(z)


def test_representantes_cobrem_todas_as_sequencias_rotuladas(sistema):
    reps, _ = sistema(5, 27)
    todas, _ = sistema(5, 27, todas=True)
    P = list(itertools.permutations(range(3)))
    orbitas = {min(_imagem(y, r, s, t) for r in P for s in P for t in (0, 1)) for y in todas}
    assert orbitas == set(reps)


def _h4xf3():
    h4 = [(a, b, (a + b) % 3, (a + 2 * b) % 3) for a in range(3) for b in range(3)]
    return [h + (c,) for h in h4 for c in range(3)]


def _embaralhar(cod, v, rng):
    perm = list(range(v))
    rng.shuffle(perm)
    sims = [rng.sample(range(3), 3) for _ in range(v)]
    return [tuple(sims[i][c[perm[i]]] for i in range(v)) for c in cod]


def _seq(cod):
    return [sum(1 for c in cod if c[:2] == (j, k)) for j in range(3) for k in range(3)]


def test_codigo_otimo_embaralhado_satisfaz_a_cnf_sem_quebra_de_simetria():
    rng = random.Random(7)
    for _ in range(5):
        cod = _embaralhar(_h4xf3(), 5, rng)
        assert len({u for c in cod for u in ysip.bola(5, c)}) == 243
        y = _seq(cod)
        top, cls, _ = ysip._construir(5, y, 0)
        _, val = ysip.atribuicao(5, y, 0, cod)
        assert ysip.falsas(cls, val) == []


def test_cobertura_codificada_exatamente_uma_clausula_por_ponto_descoberto():
    rng = random.Random(3)
    W = ysip.palavras(5)
    for _ in range(5):
        cod = rng.sample(W, 26)
        y = _seq(cod)
        top, cls, _ = ysip._construir(5, y, 0)
        _, val = ysip.atribuicao(5, y, 0, cod)
        descobertos = 243 - len({u for c in cod for u in ysip.bola(5, c)})
        assert len(ysip.falsas(cls, val)) == descobertos


def test_cota_de_fibra_falha_quando_uma_fibra_tem_menos_que_p():
    cod = _h4xf3()  # cada fibra tem 9 palavras
    y = _seq(cod)
    top, cls, _ = ysip._construir(5, y, 10)
    _, val = ysip.atribuicao(5, y, 10, cod)
    assert len(ysip.falsas(cls, val)) == 9  # 3 coordenadas de sufixo x 3 símbolos


def test_lex_leader_mantem_o_menor_elemento_da_orbita():
    W = ysip.palavras(5)
    idx = {w: i for i, w in enumerate(W)}
    rng = random.Random(11)
    cod = _embaralhar(_h4xf3(), 5, rng)
    y = _seq(cod)
    P = [[idx[pi[w]] for w in W] for pi in ysip.automorfismos(5, y)]
    ini = frozenset(idx[c] for c in cod)
    vistos, fronteira = {ini}, [ini]
    while fronteira:
        nova = []
        for S in fronteira:
            for p in P:
                T = frozenset(p[i] for i in S)
                if T not in vistos:
                    vistos.add(T)
                    nova.append(T)
        fronteira = nova
    menor = min(vistos, key=lambda S: tuple(int(i in S) for i in range(len(W))))
    cls, val = ysip.atribuicao(5, y, 0, [W[i] for i in menor])
    assert ysip.falsas(cls, val) == []
    # e corta: algum outro elemento da órbita viola o lex-leader
    outros = [S for S in vistos if S != menor]
    assert any(ysip.falsas(*ysip.atribuicao(5, y, 0, [W[i] for i in S])) for S in outros[:20])


def test_automorfismos_preservam_cobertura_blocos_e_fibras():
    rng = random.Random(5)
    W = ysip.palavras(6)
    for y in ([8, 8, 8, 8, 8, 8, 8, 8, 8], [6, 6, 8, 6, 7, 10, 9, 7, 7]):
        for pi in ysip.automorfismos(6, y):
            assert sorted(pi.values()) == W
            w = rng.choice(W)
            assert sorted(pi[u] for u in ysip.bola(6, w)) == sorted(ysip.bola(6, pi[w]))
            for j in range(3):
                for k in range(3):
                    bloco = [w for w in W if w[:2] == (j, k)]
                    destino = {pi[w][:2] for w in bloco}
                    assert len(destino) == 1
                    (jj, kk), = destino
                    assert y[3 * jj + kk] == y[3 * j + k]


def test_cota_auto_do_sufixo_vale_depois_de_escolher_as_coordenadas_de_menor_fibra():
    import amostra

    rng = random.Random(13)
    W = ysip.palavras(6)
    for _ in range(200):
        cod = rng.sample(W, rng.randint(54, 80))

        def menor_fibra(i):
            return min(sum(1 for c in cod if c[i] == a) for a in range(3))
        ordem = sorted(range(6), key=menor_fibra)  # coordenada 0: menor fibra; 1: a seguinte
        cod2 = [tuple(c[i] for i in ordem) for c in cod]
        y = _seq(cod2)
        # o representante canônico é uma imagem de y pelo grupo de ordem 72
        P = list(itertools.permutations(range(3)))
        rep = list(min(_imagem(y, r, s, t) for r in P for s in P for t in (0, 1)))
        cota = amostra.cota_sufixo(rep, 0, "auto")
        for i in range(2, 6):
            for a in range(3):
                assert sum(1 for c in cod2 if c[i] == a) >= cota
