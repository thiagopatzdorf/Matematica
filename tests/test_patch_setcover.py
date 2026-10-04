"""tools/patch_setcover: gerador de instância (patch_inst.c) e busca RWLS (rwls.c).

Ótimos usados como gabarito (instâncias minúsculas, cada teste < 2 s):
  K_2(5,1) = 7 e K_3(3,1) = 5 (tabelas clássicas de códigos de cobertura); com base vazia o
  "remendo" é o código inteiro, então a busca tem de achar exatamente esses números e nunca
  menos.
"""
import itertools
import json
import os
import shutil
import subprocess
import sys

import numpy as np
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "tools", "patch_setcover")
sys.path.insert(0, SRC)
import psc_io  # noqa: E402


@pytest.fixture(scope="module")
def bins(tmp_path_factory):
    d = tmp_path_factory.mktemp("bin")
    cc = os.environ.get("CC") or shutil.which("cc") or shutil.which("gcc")
    out = {}
    for name in ("patch_inst", "rwls"):
        out[name] = str(d / name)
        subprocess.run([cc, "-O2", "-std=gnu99", "-Wall", "-Werror", "-o", out[name],
                        os.path.join(SRC, name + ".c")], check=True)
    return out


def words_to_ints(path, q, n):
    return [sum(int(c) * q**k for k, c in enumerate(w)) for w in open(path).read().split()]


def covers(words, q, n, R):
    pts = np.array(list(itertools.product(range(q), repeat=n)))
    C = np.array([[(w // q**k) % q for k in range(n)] for w in words])
    d = (pts[:, None, :] != C[None, :, :]).sum(2).min(1)
    return int(d.max()) <= R


@pytest.mark.parametrize("q,n,R,opt", [(2, 5, 1, 7), (3, 3, 1, 5)])
def test_busca_acha_o_otimo_conhecido_e_nao_menos(bins, tmp_path, q, n, R, opt):
    base = tmp_path / "vazia.txt"; base.write_text("")
    inst = tmp_path / "i.bin"; out = tmp_path / "best.txt"
    r = subprocess.run([bins["patch_inst"], str(q), str(n), str(R), str(base), "1", str(inst)],
                       capture_output=True, text=True, check=True)
    npts = int(r.stdout.split()[0]); assert npts == q**n
    r = subprocess.run([bins["rwls"], str(inst), "-t", "1.5", "-s", "3", "-o", str(out), "-q"],
                       capture_output=True, text=True, check=True)
    res = json.loads(r.stdout.strip().splitlines()[-1])
    assert res["best"] == opt
    w = words_to_ints(out, q, n)
    assert len(w) == opt and covers(w, q, n, R)


def test_residuo_e_conjuntos_batem_com_forca_bruta(bins, tmp_path):
    q, n, R = 3, 4, 1
    base = tmp_path / "b.txt"; base.write_text("0000\n1111\n2222\n0120\n")
    inst = tmp_path / "i.bin"
    subprocess.run([bins["patch_inst"], str(q), str(n), str(R), str(base), "1", str(inst)],
                   capture_output=True, check=True)
    d = psc_io.load(str(inst))
    pts = list(itertools.product(range(q), repeat=n))
    B = [tuple(int(c) for c in w) for w in base.read_text().split()]
    dist = lambda a, b: sum(x != y for x, y in zip(a, b))  # noqa: E731
    enc = lambda v: sum(c * q**k for k, c in enumerate(v))  # noqa: E731
    U = sorted(enc(p) for p in pts if min(dist(p, b) for b in B) > R)
    assert list(d["pts"]) == U
    for j, w in enumerate(d["sets"]):
        wv = [(int(w) // q**k) % q for k in range(n)]
        got = {int(d["pts"][i]) for i in d["elem"][d["off"][j]:d["off"][j + 1]]}
        want = {u for u in U if dist(wv, [(u // q**k) % q for k in range(n)]) <= R}
        assert got == want


def test_corte_T_descarta_conjuntos_pequenos_e_inviavel_e_recusado(bins, tmp_path):
    base = tmp_path / "vazia.txt"; base.write_text("")
    inst = tmp_path / "i.bin"
    subprocess.run([bins["patch_inst"], "2", "4", "1", str(base), "1", str(inst)], capture_output=True, check=True)
    r = subprocess.run([bins["rwls"], str(inst), "-T", "6", "-t", "0.2"], capture_output=True, text=True)
    assert r.returncode == 3 and "sem candidato" in r.stderr


def test_alvo_k_para_cedo_e_inicial_e_respeitada(bins, tmp_path):
    base = tmp_path / "vazia.txt"; base.write_text("")
    inst = tmp_path / "i.bin"; ini = tmp_path / "ini.txt"; out = tmp_path / "o.txt"
    subprocess.run([bins["patch_inst"], "2", "5", "1", str(base), "1", str(inst)], capture_output=True, check=True)
    ini.write_text("".join(format(i, "05b")[::-1] + "\n" for i in range(32)))   # código = espaço inteiro
    r = subprocess.run([bins["rwls"], str(inst), "-i", str(ini), "-k", "8", "-t", "5", "-o", str(out)],
                       capture_output=True, text=True, check=True)
    lines = r.stdout.strip().splitlines()
    assert lines[0].startswith("best ") and int(lines[0].split()[1]) <= 32
    res = json.loads(lines[-1]); assert res["best"] <= 8 and res["secs"] < 5
    assert covers(words_to_ints(out, 2, 5), 2, 5, 1)


def test_or_library_unicusto_ignora_custos(tmp_path):
    # 3 linhas, 4 colunas; col 4 cobre tudo (custo alto ignorado): ótimo unicusto = 1
    txt = tmp_path / "scp.txt"
    txt.write_text("3 4\n1 1 1 99\n2 1 4\n2 2 4\n2 3 4\n")
    out = tmp_path / "o.bin"
    assert psc_io.from_orlib(str(txt), str(out)) == (3, 4)
    d = psc_io.load(str(out))
    sizes = np.diff(d["off"]).tolist()
    assert sizes == [1, 1, 1, 3]
