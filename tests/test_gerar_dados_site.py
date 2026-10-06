"""site/matematica/dados.json: os números da página pública saem do repositório e batem com o ledger."""
import json
import re
import shutil
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "tools" / "site"))
import gerar_dados_site as g  # noqa: E402

FIXO = {"commit": "0" * 40, "gerado_em": "2026-01-01T00:00:00+00:00"}


@pytest.fixture(scope="module")
def dados():
    return g.gerar(**FIXO)


def test_dados_json_versionado_esta_velho_em_relacao_ao_ledger():
    assert g.main(["--verificar"]) == 0


def test_saida_muda_entre_duas_execucoes_no_mesmo_commit(dados):
    assert g.serializar(dados) == g.serializar(g.gerar(**FIXO))


def test_schema_do_contrato_com_a_pagina_perdeu_um_campo(dados):
    for campo in ("gerado_em", "commit", "versao", "doi", "celulas_total", "exatas", "abertas",
                  "superiores_por_estado", "inferiores_por_estado", "destaques", "codigos_verificados"):
        assert campo in dados, campo
    for d in dados["destaques"]:
        assert set(d) == {"celula", "antes", "agora", "estado_lb", "estado_ub", "fonte"}


def test_contagens_por_estado_nao_somam_o_total_de_celulas(dados):
    assert sum(dados["superiores_por_estado"].values()) == dados["celulas_total"]
    assert sum(dados["inferiores_por_estado"].values()) == dados["celulas_total"]
    assert dados["exatas"] + dados["abertas"] == dados["celulas_total"]


def test_estado_inventado_fora_da_escada_do_ledger(dados):
    assert list(dados["superiores_por_estado"]) == g.ESTADOS
    assert list(dados["inferiores_por_estado"]) == g.ESTADOS


def test_os_tres_exatos_potencialmente_novos_somem_dos_destaques(dados):
    por_celula = {d["celula"]: d for d in dados["destaques"]}
    assert por_celula["K3(6,2)"]["agora"] == "K = 17"
    assert por_celula["K7(6,4)"]["agora"] == "K = 14"
    assert por_celula["K7(5,3)"]["agora"] == "K = 17"
    # a superior de K7(5,3) ganhou código próprio de 17 palavras e teorema Lean (PR #87)
    assert por_celula["K7(5,3)"]["estado_ub"] == "INDEPENDENTLY_REPRODUCED"
    assert por_celula["K7(9,4)"]["antes"] == "264 ≤ K ≤ 1475"


def test_contagem_de_codigos_ignora_ou_inventa_arquivo_de_data_codes(dados):
    assert dados["codigos_verificados"] == len(list((RAIZ / "data" / "codes").glob("q*_n*_R*_M*.txt")))


def test_doi_da_versao_ou_de_conceito_trocado(dados):
    assert dados["doi"] == "10.5281/zenodo.23172276"
    assert dados["doi_conceito"] == "10.5281/zenodo.23085769"


def _copia_minima(tmp_path):
    for rel in ("ledger/cells.json", "ledger/COBERTURA.md", ".zenodo.json", "CITATION.cff"):
        (tmp_path / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(RAIZ / rel, tmp_path / rel)
    shutil.copytree(RAIZ / "data" / "codes", tmp_path / "data" / "codes")
    return tmp_path


def test_cobertura_md_divergente_do_cells_json_passa_em_silencio(tmp_path):
    raiz = _copia_minima(tmp_path)
    cob = raiz / "ledger" / "COBERTURA.md"
    texto = cob.read_text(encoding="utf-8")
    m = re.search(r"\| ub \| (\d+) \|", texto)  # lido do arquivo: o número muda a cada cota nova
    assert m, "linha ub não encontrada no COBERTURA.md"
    cob.write_text(texto.replace(m.group(0), f"| ub | {int(m.group(1)) + 1} |", 1), encoding="utf-8")
    with pytest.raises(g.Divergencia):
        g.gerar(raiz, **FIXO)


def test_versao_do_citation_diferente_do_zenodo_passa_em_silencio(tmp_path):
    raiz = _copia_minima(tmp_path)
    zen = raiz / ".zenodo.json"
    d = json.loads(zen.read_text(encoding="utf-8"))
    d["version"] = "9.9.9"
    zen.write_text(json.dumps(d), encoding="utf-8")
    with pytest.raises(g.Divergencia):
        g.gerar(raiz, **FIXO)
