"""rodar_pb (tools/exatos/gaps2): a lista de instâncias e o registro por instância.

O registro JSONL é a evidência do resultado: uma instância SAT tem de trazer o código e a
conferência de cobertura; uma UNSAT, o veredito do VeriPB e o sha256 do OPB e da prova.
"""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
SCRIPT = RAIZ / "tools" / "exatos" / "gaps2" / "rodar_pb.py"
sys.path.insert(0, str(SCRIPT.parent))

import fatia  # noqa: E402

pytest.importorskip("numpy")

RS = os.environ.get("ROUNDINGSAT") or shutil.which("roundingsat")
VP = os.environ.get("VERIPB") or shutil.which("veripb")


def test_listar_grava_exatamente_as_instancias_da_fatia(tmp_path):
    out = tmp_path / "i.json"
    subprocess.run([sys.executable, str(SCRIPT), "--q", "3", "--n", "4", "--R", "1", "--M", "8",
                    "--listar", str(out)], check=True, capture_output=True)
    lidas = [(s, tuple(map(tuple, K)), tuple(t)) for s, K, t in json.loads(out.read_text())]
    assert lidas == [(s, tuple(K), t) for s, K, t in fatia.instancias(3, 4, 1, 8)]


@pytest.mark.skipif(not (RS and VP), reason="roundingsat/veripb ausentes")
@pytest.mark.parametrize("M,sat", [(8, False), (9, True)])
def test_registro_de_k341_traz_prova_conferida_ou_codigo_que_cobre(tmp_path, M, sat):
    lista = tmp_path / "i.json"
    base = [sys.executable, str(SCRIPT), "--q", "3", "--n", "4", "--R", "1", "--M", str(M)]
    subprocess.run(base + ["--listar", str(lista)], check=True, capture_output=True)
    env = dict(os.environ, ROUNDINGSAT=RS, VERIPB=VP)
    subprocess.run(base + ["--instancias", str(lista), "--dir", str(tmp_path / "s"), "-j", "2",
                           "--descartar"], check=True, capture_output=True, env=env)
    regs = [json.loads(ln) for ln in (tmp_path / "s" / f"K3_4_1_M{M}.jsonl").read_text().splitlines()]
    assert len(regs) == len(json.loads(lista.read_text()))
    for r in regs:
        if r["resultado"] == "UNSATISFIABLE":
            assert r["veripb"] == "VERIFIED" and len(r["sha256.pbp"]) == 64
        else:
            assert r["resultado"] == "SATISFIABLE" and r["cobre"] is True and len(r["codigo"]) == M
    assert any(r["resultado"] == "SATISFIABLE" for r in regs) == sat
