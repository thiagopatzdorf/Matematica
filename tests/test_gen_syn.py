"""Testes do gerador de certificados por síndromes (scripts/syndrome/gen_syn.py).

O gerador nasceu para K_7(9,4); a v0.6 o usa em K_5(10,5), K_5(11,4) e K_7(10,4). Estes testes
fixam que ele não assume q = 7 nem n = 9 e que listas grandes (M > 2048) saem com o maxRecDepth
que a elaboração do Lean exige, sem mudar os certificados antigos.
"""
import itertools
import json
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
GEN = RAIZ / "scripts" / "syndrome" / "gen_syn.py"


def rodar(spec, tag, out):
    r = subprocess.run([sys.executable, str(GEN), str(spec), tag, "--out", str(out)],
                       capture_output=True, text=True, cwd=RAIZ)
    return r


def test_gerador_que_assume_q7_n9_nao_reproduz_o_certificado_q5_n10_commitado(tmp_path):
    r = rodar(RAIZ / "data/structured/q5_n10_R5_M162.json", "K162", tmp_path)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "q=5 n=10 k=3 R=5" in r.stdout
    gerados = sorted(p.name for p in tmp_path.glob("*.lean"))
    assert gerados, "nada gerado"
    for nome in gerados:
        assert (tmp_path / nome).read_bytes() == (RAIZ / "CoveringLean" / nome).read_bytes(), nome
    syn = (tmp_path / "Syn_K162.lean").read_text()
    assert "theorem K5_10_5_le_162_syn" in syn
    assert "∃ C : Finset (Fin 10 → ZMod 5), C.card = 162 ∧ CoveringA2.Covers 5 C" in syn


def test_lista_com_mais_de_2048_palavras_sem_maxRecDepth_estoura_a_elaboracao(tmp_path):
    # [8,2]_4 com 130 classes laterais: M = 2080 > 2048, raio 3 cobre com folga.
    q, n = 4, 8
    gen = ["10" + "123012", "01" + "231103"]
    reps = []
    for t in itertools.product(range(q), repeat=n - 2):
        reps.append("00" + "".join(map(str, t)))
        if len(reps) == 130:
            break
    spec = tmp_path / "spec.json"
    spec.write_text(json.dumps({"q": q, "n": n, "R": 3, "generator": gen,
                                "coset_reps": reps, "patch_words": []}))
    out = tmp_path / "out"
    out.mkdir()
    r = rodar(spec, "KT", out)
    assert r.returncode == 0, r.stdout + r.stderr
    data = (out / "SynData_KT.lean").read_text()
    assert "M=2080" in data
    assert "set_option maxRecDepth 100000 in\ndef LKT : List Nat" in data


def test_certificado_antigo_com_lista_pequena_nao_ganha_set_option_e_fica_byte_a_byte_igual():
    data = (RAIZ / "CoveringLean" / "SynData_K1887.lean").read_text()
    assert "set_option" not in data
