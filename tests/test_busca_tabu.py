"""tools/busca_direta/tabu.c: busca tabu direta para K_q(n,R).

Gabaritos (instâncias minúsculas, valores exatos clássicos das tabelas de códigos de cobertura):
K_2(5,1) = 7, K_3(4,1) = 9 (código de Hamming ternário perfeito) e K_3(5,1) = 27. A busca tem de achar
exatamente esses números e NUNCA menos (menos que o ótimo seria um código falso, ou seja, um defeito na
conta incremental das cascas). Todo arquivo que o programa grava tem de passar pelo verificador oficial.
"""
import os
import shutil
import subprocess

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "tools", "busca_direta", "tabu.c")
VERIFY = os.path.join(ROOT, "tools", "verify", "verify.c")


@pytest.fixture(scope="module")
def bins(tmp_path_factory):
    d = tmp_path_factory.mktemp("bin")
    cc = os.environ.get("CC") or shutil.which("cc") or shutil.which("gcc")
    if not cc:
        pytest.skip("sem compilador C")
    out = {"tabu": str(d / "tabu"), "tabu16": str(d / "tabu16"), "verify": str(d / "verify")}
    subprocess.run([cc, "-O2", "-std=gnu99", "-Wall", "-Werror", "-o", out["tabu"], SRC], check=True)
    subprocess.run([cc, "-O2", "-std=gnu99", "-Wall", "-Werror", "-DCNT16", "-o", out["tabu16"], SRC], check=True)
    subprocess.run([cc, "-O2", "-o", out["verify"], VERIFY], check=True)
    return out


def _roda(bins, tmp_path, q, n, R, M, segundos=2.0, extra=(), prog="tabu"):
    prefixo = str(tmp_path / f"q{q}_n{n}_R{R}")
    r = subprocess.run([bins[prog], str(q), str(n), str(R), str(M), str(segundos), "1", prefixo, *extra],
                       capture_output=True, text=True, check=True)
    achados = sorted(int(linha.split()[0]) for linha in r.stdout.splitlines() if linha.strip())
    return prefixo, achados


@pytest.mark.parametrize("q,n,R,M,otimo", [(2, 5, 1, 10, 7), (3, 4, 1, 12, 9), (3, 5, 1, 32, 27)])
def test_tabu_acha_um_codigo_abaixo_do_otimo_conhecido(bins, tmp_path, q, n, R, M, otimo):
    prefixo, achados = _roda(bins, tmp_path, q, n, R, M)
    assert achados, "a busca não achou nem o código inicial"
    assert min(achados) >= otimo, f"achou M={min(achados)} < K_{q}({n},{R}) = {otimo}: conta incremental errada"
    assert min(achados) == otimo, f"não chegou ao ótimo {otimo} em 2 s (parou em {min(achados)})"


def test_codigo_gravado_pelo_tabu_reprovado_pelo_verificador_oficial(bins, tmp_path):
    prefixo, achados = _roda(bins, tmp_path, 3, 5, 2, 12)
    assert achados
    for m in achados:
        arq = f"{prefixo}_M{m}.txt"
        r = subprocess.run([bins["verify"], "-q", "3", "-n", "5", "-r", "2", "-m", str(m), arq],
                           capture_output=True, text=True)
        assert r.returncode == 0, r.stdout + r.stderr


def test_variante_cnt16_com_amostragem_de_candidatos_erra_o_otimo(bins, tmp_path):
    # -DCNT16 e max_cand mudam só desempenho: o ótimo de K_2(5,1) continua 7 e nunca menos
    _, achados = _roda(bins, tmp_path, 2, 5, 1, 10, extra=("2", "3"), prog="tabu16")
    assert min(achados) == 7


def test_modo_com_pesos_acha_codigo_menor_que_o_otimo(bins, tmp_path):
    # pesos = 1 (argumento 10) muda só a escolha do movimento; K_2(5,1) = 7 continua sendo o piso
    _, achados = _roda(bins, tmp_path, 2, 5, 1, 10, extra=("1", "0", "1"))
    assert achados and min(achados) == 7


def test_m_grande_sem_cnt16_e_recusado_em_vez_de_estourar_contagem(bins, tmp_path):
    r = subprocess.run([bins["tabu"], "2", "10", "1", "300", "1", "1", str(tmp_path / "x")],
                       capture_output=True, text=True)
    assert r.returncode == 2 and "CNT16" in r.stderr


# ---------------------------------------------------------------- tabu_grupo.c (órbitas por um grupo)
SRC_G = os.path.join(ROOT, "tools", "busca_direta", "tabu_grupo.c")


@pytest.fixture(scope="module")
def grupo_bin(tmp_path_factory, bins):
    d = tmp_path_factory.mktemp("bing")
    cc = os.environ.get("CC") or shutil.which("cc") or shutil.which("gcc")
    out = str(d / "tabu_grupo")
    subprocess.run([cc, "-O2", "-std=gnu99", "-Wall", "-Werror", "-o", out, SRC_G], check=True)
    return out


def _roda_grupo(grupo_bin, tmp_path, q, n, R, nrep, geradores, segundos=2.0):
    prefixo = str(tmp_path / f"g{q}_{n}_{R}")
    r = subprocess.run([grupo_bin, str(q), str(n), str(R), str(nrep), str(segundos), "1", prefixo, geradores],
                       capture_output=True, text=True, check=True)
    achados = sorted(int(linha.split()[0]) for linha in r.stdout.splitlines() if linha.strip())
    return prefixo, achados


def test_grupo_trivial_acha_codigo_abaixo_de_k3_4_1(grupo_bin, tmp_path):
    _, achados = _roda_grupo(grupo_bin, tmp_path, 3, 4, 1, 12, "0,1,2,3")
    assert achados and min(achados) == 9


def test_grupo_do_complemento_aceita_codigo_impar_em_k2_5_1(grupo_bin, tmp_path):
    # o complemento (x -> x + 11111) não tem ponto fixo em F_2^5: todo código invariante tem M par,
    # então o ótimo invariante é 8, nunca o 7 sem simetria
    prefixo, achados = _roda_grupo(grupo_bin, tmp_path, 2, 5, 1, 6, "0,1,2,3,4:1,1,1,1,1")
    assert achados and min(achados) == 8
    assert all(m % 2 == 0 for m in achados)


def test_codigo_do_grupo_sem_simetria_ou_reprovado_pelo_verificador(grupo_bin, bins, tmp_path):
    # translação por 111111 em F_3^6 (ordem 3) e troca cíclica: o código gravado tem de ser invariante
    # pelos geradores e passar no verificador oficial
    for ger, perm, soma in (("0,1,2,3,4,5:1,1,1,1,1,1", list(range(6)), [1] * 6),
                            ("1,2,3,4,5,0", [1, 2, 3, 4, 5, 0], [0] * 6)):
        prefixo, achados = _roda_grupo(grupo_bin, tmp_path, 3, 6, 1, 40, ger)
        assert achados
        m = min(achados)
        arq = f"{prefixo}_M{m}.txt"
        r = subprocess.run([bins["verify"], "-q", "3", "-n", "6", "-r", "1", "-m", str(m), arq],
                           capture_output=True, text=True)
        assert r.returncode == 0, r.stdout + r.stderr
        palavras = set(open(arq).read().split())
        imagem = {"".join(str((int(w[perm[i]]) + soma[i]) % 3) for i in range(6)) for w in palavras}
        assert imagem == palavras, f"código de {ger} não é invariante"
