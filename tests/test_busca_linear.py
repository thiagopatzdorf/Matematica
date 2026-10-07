"""Busca de códigos lineares (tools/certificar/busca_linear.py e .c): gerador burro, juiz exato."""
import shutil
import sys

import pytest
from conftest import RAIZ

sys.path.insert(0, str(RAIZ / "tools" / "certificar"))
import busca_linear  # noqa: E402
import lineares  # noqa: E402


@pytest.mark.skipif(shutil.which("cc") is None, reason="sem compilador C")
def test_busca_acha_o_hamming_7_4_e_o_json_gravado_passa_no_avaliador(tmp_path, monkeypatch):
    monkeypatch.setattr(busca_linear, "BIN", tmp_path / "busca_linear")
    monkeypatch.setattr(lineares, "LIN", tmp_path)
    busca_linear.compilar()
    A = busca_linear.buscar(2, 7, 3, 1, 5)
    assert A is not None and len(A) == 4 and all(len(c) == 3 for c in A)
    p = busca_linear.gravar(2, 7, 1, A, "h")
    assert p.name == "K2_7_1_M16.json"
    d = __import__("json").loads(p.read_text())
    assert lineares.cobre_por_sindromes(2, 7, 1, d["gerador"])


def test_codigo_proposto_que_nao_cobre_nao_vira_arquivo(tmp_path, monkeypatch):
    monkeypatch.setattr(lineares, "LIN", tmp_path)
    # duas colunas de H iguais: a síndrome (0,0,1) não tem líder de peso 1
    A = [[0, 1, 1], [1, 1, 1], [1, 1, 0], [1, 1, 0]]
    with pytest.raises(ValueError, match="não cobre"):
        busca_linear.gravar(2, 7, 1, A, None)
    assert not list(tmp_path.iterdir())


def test_alvo_so_e_celula_fora_do_lote_com_cota_potencia_de_q():
    import build
    cells = build.carregar(RAIZ / "ledger" / "cells.json")["cells"]
    por = {(c["q"], c["n"], c["R"]): c for c in cells}
    formal = __import__("json").loads((RAIZ / "ledger" / "formal_ub.json").read_text())["cells"]
    lista = busca_linear.alvos(cells)
    assert lista, "a tabela do Kéri ainda tem cotas q^k sem código linear aqui"
    for q, n, r, R, _ch in lista:
        assert por[(q, n, R)]["best"]["ub"] == q ** (n - r) and q**r <= busca_linear.TETO
        assert f"{q},{n},{R}" not in formal, "célula já certificada pelo lote não é alvo"
