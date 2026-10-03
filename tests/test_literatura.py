"""Testes do caçador de menções da varredura de literatura (tools/literatura/varredura.py).

O que importa é não perder uma cota publicada por causa de como o pdftotext quebra
o subscrito, e não confundir a célula com outra de mesmos números.
"""
import importlib.util
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("varredura", RAIZ / "tools" / "literatura" / "varredura.py")
varredura = importlib.util.module_from_spec(spec)
spec.loader.exec_module(varredura)

K794 = {"id": "K7(9,4)", "q": 7, "n": 9, "R": 4, "numeros_alvo": [1475]}


def tipos(texto, cel=K794):
    return [a["tipo"] for a in varredura.procurar_mencoes(texto, cel)]


def test_acha_subscrito_quebrado_pelo_pdftotext():
    assert "celula" in tipos("we show K 7 (9, 4) <= 1475 here")
    assert "celula" in tipos("bound K_{7}(9,4) holds")
    assert "celula" in tipos("K7(9,4)")


def test_nao_confunde_q_diferente_com_mesma_celula():
    assert "celula" not in tipos("K5(9,4) <= 300")
    assert "celula" not in tipos("K_7(9,3) <= 8575")


def test_forma_sem_q_so_conta_com_q_no_contexto():
    assert "celula_sem_q" in tipos("for q = 7 we get K(9,4) <= 1475")
    assert "celula_sem_q" not in tipos("binary K(9,4) is small")


def test_numero_alvo_exige_covering_e_parametros_por_perto():
    assert "numero:1475" in tipos("covering code of length 9 and radius 4 with 1475 words")
    assert "numero:1475" not in tipos("in 1475 the printing press was used")
    assert "numero:1475" not in tipos("page 14750 covering")


def test_norm_arxiv_tira_versao_e_prefixo():
    assert varredura.norm_arxiv("https://arxiv.org/abs/2608.19872v3") == "2608.19872"
    assert varredura.norm_arxiv("arXiv:2504.01932") == "2504.01932"


def test_base_funde_registros_da_mesma_obra_por_doi(tmp_path, monkeypatch):
    monkeypatch.setenv("LIT_DIR", str(tmp_path))
    b = varredura.Base()
    b.poe({"id": "W1", "openalex": "W1", "doi": "10.1/x", "titulo": "A", "fontes": ["openalex"], "score": 3}, "m1")
    b.poe({"id": "zb_1", "doi": "10.1/x", "zbmath": "1", "titulo": "A", "fontes": ["zbmath"], "score": 7}, "m2")
    assert len(b.obras) == 1
    w = b.obras["W1"]
    assert w["zbmath"] == "1" and w["score"] == 7 and w["motivos"] == ["m1", "m2"]
