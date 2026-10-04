"""Testes do motor de busca exaustiva com rejeição de isomorfos (tools/exatos/motor).

Rodam em segundos. Conferem o motor contra a literatura (número de códigos ótimos
inequivalentes das tabelas do Kéri, no ledger), contra ele mesmo sem simetria (soma das
órbitas = contagem rotulada) e contra o dfs_cover.c (implementação independente).
"""

import os
import re
import shutil
import subprocess
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
MOTOR_DIR = RAIZ / "tools" / "exatos" / "motor"


def _tem_nauty():
    return any(Path(p).exists() for p in (
        "/usr/include/x86_64-linux-gnu/nauty/nauty.h",
        "/usr/include/aarch64-linux-gnu/nauty/nauty.h",
        "/usr/include/nauty/nauty.h",
    ))


# No CI (variável CI definida) não pula: falta de nauty lá tem de aparecer como falha.
pytestmark = pytest.mark.skipif(not os.environ.get("CI") and
                                not (_tem_nauty() and shutil.which("gcc") and shutil.which("make")),
                                reason="precisa de gcc, make e libnauty-dev")


@pytest.fixture(scope="module")
def motor(tmp_path_factory):
    subprocess.run(["make", "-s", "-B", "-C", str(MOTOR_DIR)], check=True)
    return str(MOTOR_DIR / "motor")


@pytest.fixture(scope="module")
def dfs_cover(tmp_path_factory):
    out = tmp_path_factory.mktemp("dfs") / "dfs"
    subprocess.run(["gcc", "-O2", "-w", "-o", str(out), str(RAIZ / "tools" / "exatos" / "dfs_cover.c")], check=True)
    return str(out)


def rodar(motor, *args):
    p = subprocess.run([motor, *map(str, args)], capture_output=True, text=True, timeout=120)
    assert p.returncode in (0, 10), p.stderr
    return p.stdout


# Número de códigos ótimos inequivalentes, lido das tabelas do Kéri (2011, keri_2_tables.pdf e
# keri_4-5_tables.pdf: o expoente ao lado do valor). Não usamos o campo n_optimal do ledger:
# para valor de um dígito com expoente de vários dígitos ele guarda só o primeiro dígito
# (K4(4,3) "4^79" virou 7; K4(3,2) "4^21" virou 2). Foi este teste que achou isso.
KERI_N_OTIMOS = {
    (2, 4, 1): (4, 2), (2, 5, 1): (7, 1), (2, 6, 1): (12, 2), (2, 6, 2): (4, 4), (2, 7, 1): (16, 1),
    (2, 7, 2): (7, 3), (2, 8, 3): (4, 6), (3, 3, 1): (5, 1), (3, 4, 1): (9, 1), (3, 6, 4): (3, 7),
    (4, 2, 1): (4, 5), (4, 3, 1): (8, 1), (4, 3, 2): (4, 21), (4, 4, 3): (4, 79), (5, 2, 1): (5, 7),
    (5, 3, 1): (13, 1), (5, 3, 2): (5, 54),
}


@pytest.mark.parametrize("q,n,R", sorted(KERI_N_OTIMOS))
def test_classificacao_diverge_do_numero_de_otimos_do_keri(motor, q, n, R):
    K, n_opt = KERI_N_OTIMOS[(q, n, R)]
    out = rodar(motor, q, n, R, K, "--classificar")
    classes = int(re.search(r"classes=(\d+)", out).group(1))
    assert classes == n_opt


@pytest.mark.parametrize("q,n,R,M", [(2, 4, 1, 4), (2, 5, 1, 7), (2, 6, 1, 12), (2, 6, 2, 4),
                                     (2, 7, 1, 16), (3, 3, 1, 5), (3, 4, 1, 9), (4, 3, 1, 8)])
def test_soma_das_orbitas_diverge_da_contagem_rotulada_sem_simetria(motor, q, n, R, M):
    cls = rodar(motor, q, n, R, M, "--classificar")
    soma = int(re.search(r"soma_orbitas=(\d+)", cls).group(1))
    ing = rodar(motor, q, n, R, M, "--ingenuo")
    rot = int(re.search(r"codigos_rotulados=(\d+)", ing).group(1))
    assert soma == rot


# (q, n, R, K): K é o valor exato do ledger; M = K existe, M = K - 1 não existe
EXATAS = [(2, 6, 1, 12), (2, 7, 2, 7), (3, 4, 1, 9), (3, 5, 2, 8), (4, 4, 2, 7), (2, 8, 3, 4),
          (3, 6, 4, 3), (4, 5, 3, 4)]
VARIANTES = [["--D", "2"], ["--D", "3", "--corte", "5"], ["--D", "2", "--ordem", "inv"],
             ["--D", "3", "--sem-dual"]]


@pytest.mark.parametrize("q,n,R,K", EXATAS)
@pytest.mark.parametrize("var", VARIANTES, ids=lambda v: "_".join(v))
def test_existencia_em_K_e_inexistencia_em_K_menos_1_quebradas(motor, q, n, R, K, var):
    sim = rodar(motor, q, n, R, K, *var)
    assert "EXISTE" in sim and "NAO_EXISTE" not in sim
    nao = rodar(motor, q, n, R, K - 1, *var)
    assert "NAO_EXISTE" in nao


def test_codigo_achado_deixa_ponto_descoberto_no_verificador(motor, tmp_path):
    out = rodar(motor, 3, 5, 2, 8, "--D", "3")
    palavras = [ln for ln in out.splitlines() if re.fullmatch(r"[0-9]{5}", ln)]
    assert len(palavras) <= 8
    arq = tmp_path / "q3_n5_R2.txt"
    arq.write_text("\n".join(palavras) + "\n")
    verify = tmp_path / "verify"
    subprocess.run(["gcc", "-O2", "-o", str(verify), str(RAIZ / "tools" / "verify" / "verify.c")], check=True)
    p = subprocess.run([str(verify), "-q", "3", "-n", "5", "-r", "2", str(arq)], capture_output=True, text=True)
    assert p.returncode == 0, p.stdout + p.stderr


@pytest.mark.parametrize("q,n,R,M", [(2, 6, 1, 11), (2, 7, 2, 6), (3, 4, 1, 8), (2, 6, 1, 12), (3, 5, 2, 7)])
def test_motor_e_dfs_cover_discordam(motor, dfs_cover, q, n, R, M):
    a = rodar(motor, q, n, R, M, "--D", "3", "--corte", "6")
    b = subprocess.run([dfs_cover, str(q), str(n), str(R), str(M)], capture_output=True, text=True, timeout=120).stdout
    assert ("NAO_EXISTE" in a) == ("NAO_EXISTE" in b)


def test_metodos_de_ganho_dao_arvores_diferentes(motor):
    nos = set()
    for m in ("0", "1", "2"):
        out = rodar(motor, 2, 6, 1, 12, "--ingenuo", "--metodo-ganho", m)
        nos.add(re.search(r"nos=(\d+)", out).group(1))
    assert len(nos) == 1
    nos = set()
    for m in ("0", "1", "2"):
        out = rodar(motor, 4, 3, 1, 8, "--ingenuo", "--metodo-ganho", m)
        nos.add(re.search(r"nos=(\d+)", out).group(1))
    assert len(nos) == 1


def test_execucao_em_partes_perde_nos_ou_representantes(motor, tmp_path):
    reps = tmp_path / "r.reps"
    rodar(motor, 3, 5, 2, 7, "--D", "3", "--reps-out", reps)
    inteira = rodar(motor, 3, 5, 2, 7, "--reps-in", reps, "--corte", "6")
    total = int(re.search(r"nos_fundo=(\d+)", inteira).group(1))
    feitos = int(re.search(r"reps_feitos=(\d+)", inteira).group(1))
    soma = soma_reps = 0
    for i in range(3):
        cert = tmp_path / f"c{i}.txt"
        out = rodar(motor, 3, 5, 2, 7, "--reps-in", reps, "--corte", "6", "--parte", f"{i}/3", "--cert", cert)
        assert "NAO_EXISTE" in out
        soma += int(re.search(r"nos_fundo=(\d+)", out).group(1))
        linhas = [ln for ln in cert.read_text().splitlines() if re.match(r"^\d+ ", ln)]
        soma_reps += len(linhas)
        assert sum(int(re.search(r"nos=(\d+)", ln).group(1)) for ln in linhas) == \
            int(re.search(r"nos_fundo=(\d+)", out).group(1))
    assert soma == total and soma_reps == feitos
