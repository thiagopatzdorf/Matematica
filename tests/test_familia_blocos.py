"""Construção por blocos para K_q(n, n-2) (docs/exatos/FAMILIA_KQ_N_N2.md).

Confere: o critério exato do Teorema 1 contra força bruta; que a CNF de blocos_sat.py aceita o código
de 14 palavras de K_7(6,4) (e cópias dele embaralhadas por isometrias que preservam os blocos) depois
da normalização, ou seja, que a quebra de simetria não perde solução; que um código que não cobre
viola a CNF; o verificador cobre_n2.c contra força bruta; e a propagação do lema das fibras.
"""
import itertools
import pathlib
import random
import shutil
import subprocess
import sys

import pytest

RAIZ = pathlib.Path(__file__).resolve().parents[1]
FAM = RAIZ / "tools" / "exatos" / "familia"
sys.path.insert(0, str(FAM))

import blocos_sat  # noqa: E402
import propaga_fibras  # noqa: E402

C14 = """000000 011111 100011 122200 212222 221122 333333
343444 434455 444366 555534 565643 656665 666556""".split()
BLOCOS_K764 = [(3, 6, 2, 6), (4, 8, 2, 6)]


def cobre_forca_bruta(code, q, n):
    desc = 0
    for x in itertools.product(range(q), repeat=n):
        if not any(sum(a == b for a, b in zip(x, w)) >= 2 for w in code):
            desc += 1
    return desc


def por_blocos(code_str, offs):
    """separa palavras (strings) em blocos com símbolos locais."""
    out = [[] for _ in offs]
    for w in code_str:
        d = [int(c) for c in w]
        j = max(k for k, (o, a) in enumerate(offs) if d[0] >= o)
        out[j].append(tuple(v - offs[j][0] for v in d))
    return out


def atribuicao(vars_, blocos_palavras, blocos, n):
    """atribuição induzida pelo código: x, z = x∧x, P = OR z, U = cobertura exata."""
    val = {}
    for (j, w, i, v), var in vars_["X"].items():
        val[var] = blocos_palavras[j][w][i] == v
    for (j, w, i1, i2, va, vb), var in vars_["Z"].items():
        val[var] = blocos_palavras[j][w][i1] == va and blocos_palavras[j][w][i2] == vb
    for (j, i1, i2, va, vb), var in vars_["P"].items():
        val[var] = any(p[i1] == va and p[i2] == vb for p in blocos_palavras[j])
    for (j, S), var in vars_["U"].items():
        val[var] = blocos_sat.familia_de(blocos_palavras[j], blocos[j][0], n, S)
    return val


def clausulas_violadas(f, val):
    ruins = 0
    for c in f.cl:
        if not any((val[abs(l)] if l > 0 else not val[abs(l)]) for l in c):
            ruins += 1
    return ruins


def test_contagem_por_blocos_bate_forca_bruta_em_codigos_aleatorios():
    rng = random.Random(3)
    for _ in range(6):
        q, n = 5, 4
        tam = [2, 3]
        code = []
        for j, a in enumerate(tam):
            off = sum(tam[:j])
            for _ in range(rng.randint(2, 6)):
                code.append(tuple(off + rng.randrange(a) for _ in range(n)))
        code = sorted(set(code))
        # Teorema 1: Σ_{partições ordenadas} Π_j u_j(S_j)
        blocos_cod = [[tuple(v - sum(tam[:j]) for v in w) for w in code if sum(tam[:j]) <= w[0] < sum(tam[:j + 1])
                       and all(sum(tam[:j]) <= v < sum(tam[:j + 1]) for v in w)] for j in range(2)]
        if sum(len(b) for b in blocos_cod) != len(code):
            continue
        tot = 0
        for sig in itertools.product(range(2), repeat=n):
            prod = 1
            for j, a in enumerate(tam):
                S = [i for i in range(n) if sig[i] == j]
                u = sum(1 for y in itertools.product(range(a), repeat=len(S))
                        if not any(sum(w[i] == v for i, v in zip(S, y)) >= 2 for w in blocos_cod[j]))
                prod *= u
            tot += prod
        assert tot == cobre_forca_bruta(code, q, n)


def test_cnf_de_blocos_aceita_o_codigo_de_14_e_isometrias_dele_normalizadas():
    f, mapa, vars_ = blocos_sat.gerar(7, 6, BLOCOS_K764)
    rng = random.Random(11)
    base = por_blocos(C14, [(0, 3), (3, 4)])
    for rodada in range(4):
        bl = []
        perm_col = list(range(6))
        if rodada:
            rng.shuffle(perm_col)
        for j, (a, m, _, _) in enumerate(BLOCOS_K764):
            sig = [rng.sample(range(a), a) if rodada else list(range(a)) for _ in range(6)]
            pal = [tuple(sig[i][w[perm_col[i]]] for i in range(6)) for w in base[j]]
            rng.shuffle(pal)
            bl.append(pal)
        norm = blocos_sat.normalizar(bl)
        assert clausulas_violadas(f, atribuicao(vars_, norm, BLOCOS_K764, 6)) == 0


def test_cnf_de_blocos_rejeita_codigo_que_nao_cobre():
    f, mapa, vars_ = blocos_sat.gerar(7, 6, BLOCOS_K764)
    ruim = list(C14)
    ruim[-1] = "666666"  # troca uma palavra do bloco B: o código passa a ter pontos descobertos
    assert cobre_forca_bruta([tuple(map(int, w)) for w in ruim], 7, 6) > 0
    norm = blocos_sat.normalizar(por_blocos(ruim, [(0, 3), (3, 4)]))
    assert clausulas_violadas(f, atribuicao(vars_, norm, BLOCOS_K764, 6)) > 0


@pytest.mark.skipif(shutil.which("cc") is None, reason="sem compilador C")
def test_cobre_n2_conta_descobertos_igual_a_forca_bruta(tmp_path):
    exe = tmp_path / "cobre_n2"
    subprocess.run(["cc", "-O2", "-std=c99", "-o", str(exe), str(FAM / "cobre_n2.c")], check=True)
    rng = random.Random(5)
    for q, n, m in [(4, 4, 5), (5, 4, 7), (3, 5, 3), (7, 6, 14)]:
        if (q, n, m) == (7, 6, 14):
            code = [tuple(map(int, w)) for w in C14]
        else:
            code = sorted({tuple(rng.randrange(q) for _ in range(n)) for _ in range(m)})
        arq = tmp_path / "c.txt"
        arq.write_text("\n".join("".join(map(str, w)) for w in code) + "\n")
        out = subprocess.run([str(exe), str(q), str(n), str(arq)], capture_output=True, text=True).stdout
        assert f"uncovered={cobre_forca_bruta(code, q, n)} " in out


def test_propagacao_das_fibras_sobe_k8_7_5_com_k7_6_4_igual_a_14():
    lb, ub = propaga_fibras.carregar()
    lb[(7, 6, 4)] = 14
    lb[(7, 5, 3)] = 16
    novas = propaga_fibras.propagar(lb, ub)
    assert novas[(8, 7, 5)][1] == 15
    assert novas[(9, 8, 6)][1] == 16
    assert novas[(10, 9, 7)][1] == 17


def test_propagacao_das_fibras_so_com_o_ledger_ja_da_k8_6_4_maior_ou_igual_a_16():
    lb, ub = propaga_fibras.carregar()
    novas = propaga_fibras.propagar(lb, ub)
    assert novas[(8, 6, 4)][1] >= 16
