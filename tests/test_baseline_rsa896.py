"""Baseline congelado do polinômio do recorde RSA-896: adulterar um dígito tem de reprovar a conferência."""
import copy
import json
import re
import sys
from fractions import Fraction

from conftest import RAIZ

sys.path.insert(0, str(RAIZ / "tools" / "fatoracao"))
import baseline_rsa896 as b  # noqa: E402

ARQUIVO = RAIZ / "tools" / "fatoracao" / "baseline" / "rsa896.json"
DADOS = json.loads(ARQUIVO.read_text(encoding="utf-8"))


def test_baseline_congelado_com_conferencia_que_nao_fecha():
    falhas = [k for k, v in b.conferencias(DADOS).items() if not v]
    assert falhas == []


def test_resultante_do_codigo_difere_de_uma_conta_independente_com_fracoes():
    p = DADOS["poly"]
    raiz = Fraction(-p["Y0"], p["Y1"])
    independente = p["Y1"] ** 6 * sum(c * raiz ** i for i, c in enumerate(p["c"]))
    assert independente.denominator == 1 and int(independente) == b.resultante(p)


def test_coeficiente_adulterado_continua_valendo_para_o_n():
    d = copy.deepcopy(DADOS)
    d["poly"]["c"][3] += 1
    r = b.conferencias(d)
    assert not r["resultante_multiplo_de_n"] and not r["resultante_igual_ao_declarado"]


def test_fator_adulterado_continua_multiplicando_em_n():
    d = copy.deepcopy(DADOS)
    d["p"] = str(int(d["p"]) + 2)
    assert not b.conferencias(d)["p_vezes_q_igual_n"]


def test_fator_composto_passa_por_primo():
    d = copy.deepcopy(DADOS)
    d["p"], d["q"] = "9", "15"
    r = b.conferencias(d)
    assert not r["p_primo"] and not r["q_primo"]


def test_n_diferente_do_da_lista_do_desafio_passa_como_igual():
    d = copy.deepcopy(DADOS)
    d["n_lista"] = str(int(d["n_lista"]) + 1)
    assert not b.conferencias(d)["n_igual_ao_da_lista"]


def test_parametros_do_murphy_nao_seguem_a_regra_do_cado():
    # cadotask.py: area = 2^A * qmin, Bf = 2^lpb1 (lado algébrico), Bg = 2^lpb0 (lado racional)
    m = b.parametros_murphy({"A": 33, "qmin": 6.0e9, "lpb0": 37, "lpb1": 40})
    assert m == {"area": 2.0 ** 33 * 6.0e9, "Bf": float(2 ** 40), "Bg": float(2 ** 37)}


def test_baseline_nao_registra_qual_cado_reproduziu_as_medidas():
    r = DADOS["reproduzido_com_cado"]
    assert re.fullmatch(r"[0-9a-f]{40}", r["cado_commit"])
    assert b.bate(r["alpha"], DADOS["declarado"]["alpha"], 5e-3) and b.bate(r["murphy_e"], DADOS["declarado"]["murphy_e"])


POST = """<pre>RSA-896 = \n1\n5</pre>
<pre>p =\n3\nq =\n5\n</pre>
<pre>\nY0: -1\nY1: 1\nc0: 7\nc1: 0\nc2: 0\nc3: 0\nc4: 0\nc5: 0\nc6: -9\nskew: 1.5\n</pre>
<pre>\n  side 0 (rational)    side 1 (algebraic, degree 6)\n  lim  1   1\n  lpb  37   40\n  Special-q:  prime, on side 1\n  qmin:       6.0e9\n</pre>
<p>Sieve area: A = 33, a fixed region. alpha -11.12, Murphy E 5.293e-10, Res(f,g) = -8N, and was this</p>"""


def test_numero_quebrado_em_varias_linhas_do_post_perde_digitos():
    d = b.extrair_post(POST)
    assert (d["n"], d["p"], d["q"]) == (15, 3, 5)
    assert d["poly"]["c"][0] == 7 and d["poly"]["c"][6] == -9 and d["poly"]["Y0"] == -1 and d["poly"]["skew"] == 1.5
    assert d["crivo"] == {"A": 33, "qmin": 6.0e9, "lpb0": 37, "lpb1": 40}
    assert d["declarado"] == {"alpha": -11.12, "murphy_e": 5.293e-10, "resultante_sobre_n": -8}


def test_verificar_sai_com_zero_mesmo_com_arquivo_adulterado(tmp_path):
    ruim = copy.deepcopy(DADOS)
    ruim["poly"]["c"][0] += 1
    arq = tmp_path / "ruim.json"
    arq.write_text(json.dumps(ruim), encoding="utf-8")
    assert b.main(["verificar", str(arq)]) == 1
    assert b.main(["verificar", str(ARQUIVO)]) == 0
