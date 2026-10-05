"""Linha de base de informação das relações: o documento só diz o que o JSON de resultados diz, e a evidência de parada confere."""
import json
import re
import sys

from conftest import RAIZ

sys.path.insert(0, str(RAIZ / "tools" / "fatoracao"))
import baseline_informacao as b  # noqa: E402
import relacoes as rel  # noqa: E402

BASE = RAIZ / "tools" / "fatoracao" / "baseline"
RES = json.loads((BASE / "informacao_resultados.json").read_text(encoding="utf-8"))
DOC = (RAIZ / "docs" / "fatoracao" / "RELATION_INFORMATION_BASELINE.md").read_text(encoding="utf-8")


def test_documento_com_tabela_que_nao_vem_do_json_de_resultados():
    bloco = re.search(r"<!-- gen:resultados -->\n(.*?)\n<!-- /gen -->", DOC, flags=re.S)
    assert bloco, "falta o bloco <!-- gen:resultados -->"
    assert bloco.group(1) == b.relatorio(RES)


def test_captura_c60_com_ideal_ruim_e_inercia_que_nao_reproduz_o_purge_do_cado():
    d = rel.carregar(RAIZ / "tests" / "fixtures" / "fatoracao" / "captura_c60_0")
    r = rel.reproduz_purge_do_cado(d)
    assert r["inicio_bate"] and r["fim_bate"] and d.livres_discrepantes == [], r
    assert d.ideais_ruins_conhecidos and d.inercias_conhecidas


def test_previsao_de_parada_que_nao_bate_com_o_experimento_do_cado():
    exp = json.loads((BASE / "parada_c60_0.json").read_text(encoding="utf-8"))
    r = next(x for x in RES["instancias"] if x["id"] == "c60_0_t1" and x["conjunto"] == "dev")
    assert exp["previsao_do_pipeline"]["t_min_brutas"] == r["parada"]["t_min"]["t"]
    assert exp["previsao_do_pipeline"]["n_brutas_original"] == r["n_brutas"]
    por = {e["rels_wanted"]: " ".join(e["linhas_do_log"]) for e in exp["execucoes"]}
    assert "Have enough relations" in por[46100] and "Not enough relations" not in por[46100]
    assert "Not enough relations" in por[43000] and "excess -" in por[43000]
    assert exp["fatores_iguais_aos_gerados_com_rels_wanted_46100"] is True


def test_resultados_com_instancia_cujo_purge_nao_reproduz_o_cado():
    assert all(r["valida_o_purge_do_cado"] for r in RES["instancias"])
    assert {r["conjunto"] for r in RES["instancias"]} == {"dev", "teste"}
