"""Fatia mínima (tools/exatos/gaps2): completude da redução e do filtro de contagem.

A inexistência de K_3(6,2) com M palavras depende de (1) toda configuração da fatia mínima
estar na lista (`fatia.configuracoes`, uma por classe de isometria), (2) o filtro de contagem
ser válido e (3) todo código cair numa instância cujo OPB ele satisfaz. Os testes conferem
(1) contra a contagem de órbitas por força bruta e (3) construtivamente com códigos
embaralhados por isometrias aleatórias. Nada aqui precisa de solver (os que precisam pulam).
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

import canon_fatia  # noqa: E402
import fatia  # noqa: E402
import fatia_pb  # noqa: E402

pytest.importorskip("numpy")

# código ternário de comprimento 6, raio 2, 17 palavras (achado por recozimento; K_3(6,2) <= 17)
C17 = """100112 221220 111001 122120 201021 221122 002200 021110 002102 200100 010021 122222
212011 021212 220001 200202 100210""".split()


def isometria_aleatoria(cod, q, n, rng):
    perm = list(range(n))
    rng.shuffle(perm)
    sims = [rng.sample(range(q), q) for _ in range(n)]
    out = [tuple(sims[i][c[perm[i]]] for i in range(n)) for c in cod]
    rng.shuffle(out)
    return out


def orbitas_forca_bruta(q, m, s):
    """Número de classes de conjuntos de s pontos de Z_q^m sob S_q wr S_m (força bruta)."""
    pts = list(itertools.product(range(q), repeat=m))
    grupo = [(perm, sims) for perm in itertools.permutations(range(m))
             for sims in itertools.product(itertools.permutations(range(q)), repeat=m)]
    vistos, classes = set(), 0
    for S in itertools.combinations(pts, s):
        if S in vistos:
            continue
        classes += 1
        for perm, sims in grupo:
            img = tuple(sorted(tuple(sims[i][p[perm[i]]] for i in range(m)) for p in S))
            vistos.add(img)
    return classes


@pytest.mark.parametrize("q,m,s", [(3, 3, 2), (3, 3, 3), (3, 3, 4), (2, 4, 3), (2, 4, 4), (3, 2, 3)])
def test_configuracoes_tem_uma_por_orbita_nem_mais_nem_menos(q, m, s):
    assert len(fatia.configuracoes(q, m, s)) == orbitas_forca_bruta(q, m, s)


def test_configuracoes_com_filtro_so_descartam_o_que_a_contagem_exclui():
    todas = fatia.configuracoes(3, 5, 2)
    filtradas = fatia.configuracoes(3, 5, 2, 2, 13 * 11)
    esperado = [K for K in todas if len(fatia.descobertos(3, 5, 2, K)) <= 13 * 11]
    assert sorted(map(fatia.forma, filtradas)) == sorted(map(fatia.forma, esperado))
    # duas palavras na fatia mínima de K_3(6,2), M = 15: só a distância 5 sobra (|U| = 141)
    assert [max(fatia.dist(*K) for _ in [0]) for K in filtradas] == [5]


def test_filtro_de_contagem_de_k362_m15_exclui_fibras_0_e_1():
    ins = fatia.instancias(3, 6, 2, 15) if os.environ.get("GAPS2_LENTO") else None
    for s in (0, 1):
        K = [] if s == 0 else [(0,) * 5]
        assert len(fatia.descobertos(3, 5, 2, K)) > (15 - s) * 11
    if ins is not None:
        assert min(i[0] for i in ins) == 2


def checar(cod, q, n, R, cobre):
    M = len(cod)
    inst, norm = canon_fatia.normalizar(cod, q, n)
    assert sorted(norm) != [] and len(set(norm)) == M
    ruins = canon_fatia.restricoes_violadas(q, n, R, M, inst, norm)
    if cobre:
        assert ruins == []
        # a instância é uma das de fatia.instancias: representante canônico da classe, passa
        # no filtro de contagem e tem blocos válidos (montar a lista inteira é lento)
        s, K, t = inst
        assert list(K) == fatia.de_colunas(fatia.forma(list(K))) if s else K == ()
        assert len(fatia.descobertos(q, n - 1, R, K)) <= (M - s) * fatia.vol(n - 1, R - 1, q)
        assert t in fatia.blocos_restantes(q, M, s)
    else:
        assert ruins and all(ln.endswith(">= 1 ;") and ln.count("x") == fatia.vol(n, R, q)
                             for ln in ruins)
    return inst


def test_codigo_de_17_palavras_cai_numa_instancia_satisfeita_sob_isometrias_aleatorias():
    rng = random.Random(7)
    cod = [tuple(map(int, w)) for w in C17]
    for _ in range(4):
        inst = checar(isometria_aleatoria(cod, 3, 6, rng), 3, 6, 2, True)
        assert inst[0] == 3 and inst[2] == (7, 7)


def test_hamming_ternario_cai_numa_instancia_satisfeita():
    # [4,2,3]_3 de Hamming: perfeito, K_3(4,1) = 9
    G = [(1, 0, 1, 1), (0, 1, 1, 2)]
    cod = [tuple((a * G[0][i] + b * G[1][i]) % 3 for i in range(4)) for a in range(3) for b in range(3)]
    rng = random.Random(1)
    for _ in range(5):
        checar(isometria_aleatoria(cod, 3, 4, rng), 3, 4, 1, True)


def test_codigo_que_nao_cobre_so_viola_cobertura():
    rng = random.Random(5)
    for _ in range(5):
        cod = rng.sample(list(itertools.product(range(3), repeat=6)), 15)
        checar(cod, 3, 6, 2, False)


def test_mutacao_ordem_errada_dos_blocos_e_pega():
    """Se a normalização trocasse a ordem dos blocos da coordenada 0, o OPB recusaria."""
    cod = [tuple(map(int, w)) for w in C17]
    inst, norm = canon_fatia.normalizar(cod, 3, 6)
    s, K, t = inst
    errado = (s, K, (t[0] + 1, t[1] - 1))
    assert canon_fatia.restricoes_violadas(3, 6, 2, 17, errado, norm)


RS = os.environ.get("ROUNDINGSAT") or shutil.which("roundingsat")
VP = os.environ.get("VERIPB") or shutil.which("veripb")


@pytest.mark.skipif(not (RS and VP), reason="roundingsat/veripb ausentes")
@pytest.mark.parametrize("q,n,R,M,esperado", [(3, 4, 1, 8, "UNSAT"), (3, 4, 1, 9, "SAT"),
                                              (3, 5, 2, 7, "UNSAT"), (2, 6, 1, 11, "UNSAT")])
def test_pb_reproduz_valores_conhecidos(tmp_path, q, n, R, M, esperado):
    res = set()
    for i, inst in enumerate(fatia.instancias(q, n, R, M)):
        txt, _ = fatia_pb.opb(q, n, R, M, inst)
        f = tmp_path / f"i{i}.opb"
        f.write_text(txt)
        r = subprocess.run([RS, str(f), f"--proof-log={tmp_path}/p{i}"], capture_output=True, text=True)
        st = [ln for ln in r.stdout.splitlines() if ln.startswith("s ")][0]
        if "UNSAT" in st:
            prova = next(p for p in (tmp_path / f"p{i}.pbp", tmp_path / f"p{i}") if p.exists())
            c = subprocess.run([VP, str(f), str(prova)], capture_output=True, text=True)
            assert "s VERIFIED UNSATISFIABLE" in c.stdout
            res.add("UNSAT")
        else:
            res.add("SAT")
    assert ("SAT" in res) == (esperado == "SAT")
