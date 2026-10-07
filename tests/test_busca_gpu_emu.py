"""PoC de GPU (tools/busca_gpu/tabu_gpu.cu): o modo EMU roda o MESMO código do kernel em CPU e confere, depois de
cada lançamento, que as contagens incrementais das cascas batem com a recontagem do zero. Se a atualização das
cascas errasse um ponto, o binário sai com ERRO_CONTAGEM; e todo código achado tem de passar no verificador oficial."""
import shutil
import subprocess
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
pytestmark = pytest.mark.skipif(shutil.which("g++") is None or shutil.which("cc") is None, reason="sem g++/cc")


def _compila(tmp_path):
    emu = tmp_path / "tabu_emu"
    subprocess.run(["g++", "-O2", "-DEMU", "-x", "c++", "-o", str(emu), str(RAIZ / "tools/busca_gpu/tabu_gpu.cu")], check=True)
    ver = tmp_path / "verify"
    subprocess.run(["cc", "-O2", "-std=c99", "-o", str(ver), str(RAIZ / "tools/verify/verify.c")], check=True)
    return emu, ver


def test_contagem_incremental_das_cascas_bate_com_a_recontagem_e_o_codigo_passa_no_verificador(tmp_path):
    emu, ver = _compila(tmp_path)
    r = subprocess.run([str(emu), "5", "6", "3", "28", "2", "60", "3", "1", "500", str(tmp_path / "c")],
                       capture_output=True, text=True, timeout=120)
    assert "ERRO_CONTAGEM" not in r.stdout, r.stdout
    assert "ok=2" in r.stdout.splitlines()[-2], r.stdout
    for arq in sorted(tmp_path.glob("c_c*_M28.txt")):
        v = subprocess.run([str(ver), "-q", "5", "-n", "6", "-r", "3", str(arq)], capture_output=True, text=True)
        assert v.returncode == 0 and "uncovered=0" in v.stdout, v.stdout + v.stderr
