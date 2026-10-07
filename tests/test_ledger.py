"""Ledger de células: build.py e targets.py, sem rede (fontes recortadas)."""
import hashlib
import json

import pytest

import build
import targets
from conftest import FONTES, RAIZ


def _celulas(ldir):
    return {(c["q"], c["n"], c["R"]): c for c in build.carregar(ldir / "cells.json")["cells"]}


def test_k7_9_4_publicado_e_marosi_1475_mas_o_melhor_conhecido_e_o_nosso_1134_no_lean(ledger_recortado):
    c = _celulas(ledger_recortado)[(7, 9, 4)]
    assert c["published"]["ub"] == {"value": 1475, "source": "marosi_2026", "ref": build.ROTULO["marosi_2026"]}
    assert c["published"]["sources"]["keri_2011"]["ub"] == 1843
    assert c["published"]["lb"]["value"] == 264
    assert c["ours_lean"]["M"] == 1134 and c["ours_lean"]["declaration"] == "Syn.K7_9_4_le_1134_syn"
    assert c["best"] == {"ub": 1134, "holder": "ours_lean", "beats_published": True}
    assert c["status"] == "ours_lean"
    assert c["marosi_attacked"]["ub"] is True


def test_cota_inferior_de_gijswijt_polak_vence_a_do_keri_em_k5_10_4(ledger_recortado):
    c = _celulas(ledger_recortado)[(5, 10, 4)]
    assert c["published"]["lb"]["value"] == 177
    assert c["published"]["lb"]["source"] == "gijswijt_polak_2025"
    assert c["published"]["sources"]["keri_2011"]["lb"] == 162


def test_compilacao_pos_keri_so_leva_credito_quando_estritamente_melhor(ledger_recortado):
    cs = _celulas(ledger_recortado)
    # Wu–Chen 2024 só aparece na compilação do Florath: 348 > 342 do Kéri.
    assert cs[(2, 12, 1)]["published"]["lb"]["source"] == "literatura_pos_keri"
    assert cs[(2, 12, 1)]["published"]["lb"]["value"] == 348
    # Mesmo valor do GP: o crédito fica com a fonte primária.
    assert cs[(5, 10, 4)]["published"]["lb"]["source"] == "gijswijt_polak_2025"


def test_k2_6_1_exata_nao_conta_como_melhora_da_literatura(ledger_recortado):
    c = _celulas(ledger_recortado)[(2, 6, 1)]
    assert c["published"]["exact"] is True
    assert c["ours_lean"]["declaration"] == "SC.K_2_6_1_eq12"
    assert c["best"]["beats_published"] is False


def test_celula_nossa_fora_da_tabela_do_keri_aborta_o_build():
    sources = json.loads((RAIZ / "ledger" / "sources.json").read_text())
    ours = {"cells": {"99,1,1": {"ours_lean": {"M": 1}}}}
    with pytest.raises(SystemExit, match="fora da tabela"):
        build.construir(build.ler_fontes(FONTES, sources), ours, sources)


def test_build_gera_os_mesmos_bytes_duas_vezes(tmp_path):
    for i in (1, 2):
        build.main(["--fonte", str(FONTES), "--saida", str(tmp_path / f"c{i}.json")])
    assert (tmp_path / "c1.json").read_bytes() == (tmp_path / "c2.json").read_bytes()


def test_ledger_commitado_bate_com_o_recortado_nas_celulas_do_recorte(ledger_recortado):
    """O cells.json do repositório (fontes inteiras) e o da fixture (recorte)
    têm de concordar célula a célula: senão a fixture envelheceu."""
    inteiro = _celulas(RAIZ / "ledger")
    for k, c in _celulas(ledger_recortado).items():
        assert inteiro[k] == c, k


def test_ledger_commitado_tem_1145_celulas_e_sha256_dos_nossos_codigos_confere():
    led = build.carregar(RAIZ / "ledger" / "cells.json")
    assert led["meta"]["n_cells"] == len(led["cells"]) == 1145
    nossos = [c for c in led["cells"] if c["status"] != "published"]
    # 15 no Lean (K7(6,4) <= 14 na v0.9, PR #76; K7(5,3) <= 17 com código nosso) + 95 dos artigos de
    # data/literatura/ (79 pelo Corolário 3 de Kéri–Östergård, 16 binárias), todas teoremas do kernel;
    # mais K4(7,4) <= 10 só computacional (código em data/codes/, ainda sem teorema, 2026-10-07).
    assert len(nossos) == 111
    assert [c["id"] for c in nossos if c["status"] != "ours_lean"] == ["K4(7,4)"]
    assert next(c for c in nossos if c["id"] == "K4(7,4)")["status"] == "ours_computational"
    lean = [c for c in nossos if c["status"] == "ours_lean"]
    lit = [c for c in lean if c["ours_lean"]["declaration"].startswith(("CoveringLit.", "Syn.K2_"))]
    assert len(lit) == 95
    # Com código em data/codes/ (25) a cota sobe a INDEPENDENTLY_REPRODUCED; sem, fica FORMALIZED.
    assert sum(1 for c in lit if c["certification"]["ub"]["state"] == "INDEPENDENTLY_REPRODUCED") == 25
    for c in nossos:
        for lado in ("ours_computational", "ours_lean"):
            e = c[lado]
            if e and e.get("file"):
                dados = (RAIZ / e["file"]).read_bytes()
                assert hashlib.sha256(dados).hexdigest() == e["sha256"], e["file"]
                linhas = [x for x in dados.decode().splitlines() if x.strip()]
                assert len(linhas) == e["M"], e["file"]


def test_todo_codigo_nosso_tem_registro_de_proveniencia_com_os_seis_campos():
    prov = json.loads((RAIZ / "ledger" / "provenance.json").read_text())
    ours = json.loads((RAIZ / "ledger" / "ours.json").read_text())
    for c in ours["cells"].values():
        for lado in ("ours_computational", "ours_lean"):
            e = c.get(lado)
            if e and e.get("file"):
                reg = prov["registros"][e["provenance"]]
                faltando = [f for f in prov["campos"] if reg.get(f) is None]
                # Campo nulo só é aceito com a lacuna declarada.
                assert not faltando or reg.get("lacuna"), (e["file"], faltando)


def test_alvo_que_ninguem_atacou_vem_antes_do_que_o_marosi_atacou(ledger_recortado):
    cells = build.carregar(ledger_recortado / "cells.json")["cells"]
    r = {t["id"]: t for t in targets.ranquear(cells)}
    # K7(10,4) era o exemplo de intocada até a v0.6, que a fez nossa (≤ 5616): agora é K6(9,3).
    assert r["K6(9,3)"]["camada"] == 0
    assert r["K7(10,4)"]["camada"] == 2  # nossa desde a v0.6
    assert r["K10(8,4)"]["camada"] == 1  # sweep_targets.json, sem melhora
    assert r["K10(9,5)"]["camada"] == 2  # varrida e melhorada pelo Marosi (1088 -> 1055)
    assert r["K6(9,3)"]["rank"] < r["K10(8,4)"]["rank"] < r["K10(9,5)"]["rank"]
    assert "ninguém atacou desde 2011" in r["K6(9,3)"]["justificativa"]


def test_alvo_fechado_grande_demais_ou_nosso_nao_vai_para_o_topo(ledger_recortado):
    cells = build.carregar(ledger_recortado / "cells.json")["cells"]
    r = {t["id"]: t for t in targets.ranquear(cells, max_espaco=1e8)}
    assert "K2(4,1)" not in r  # exata (4 = 4)
    assert "K7(10,4)" not in r  # 7^10 > 1e8
    assert r["K7(9,4)"]["camada"] == 2  # nossa
    assert r["K6(10,4)"]["camada"] == 2  # Marosi melhorou


def test_targets_imprime_tabela_com_top_pedido(ledger_recortado, capsys):
    targets.main(["--ledger", str(ledger_recortado / "cells.json"), "--top", "3"])
    linhas = capsys.readouterr().out.strip().splitlines()
    assert len(linhas) == 4 and linhas[1].split()[0] == "1"


def test_n_optimal_truncado_pelo_coldcase_volta_ao_valor_da_tabela_do_keri():
    assert build.corrigir_n_optimal({"q": 4, "n": 4, "R": 3, "n_optimal": 7})["n_optimal"] == 79
    assert build.corrigir_n_optimal({"q": 5, "n": 4, "R": 3, "n_optimal": 471})["n_optimal"] == 471
    assert build.corrigir_n_optimal({"q": 3, "n": 6, "R": 1, "n_optimal": None})["n_optimal"] is None


def test_n_optimal_com_truncamento_diferente_do_esperado_aborta_o_build():
    with pytest.raises(SystemExit):
        build.corrigir_n_optimal({"q": 4, "n": 4, "R": 3, "n_optimal": 5})


# ------------------------------------------------------------ certificação (estado + proveniência)


def test_k7_4_2_exata_19_com_as_duas_cotas_formalized_e_inferior_sem_hipotese_pendente(ledger_recortado):
    c = _celulas(ledger_recortado)[(7, 4, 2)]
    cert = c["certification"]
    assert cert["exact"] is True and cert["ub"]["value"] == cert["lb"]["value"] == 19
    assert cert["ub"]["state"] == "FORMALIZED"
    assert cert["ub"]["provenance"]["lean"]["declaration"] == "K742.K_7_4_2_le_19"
    # A superior 19 é do Kéri–Östergård: o crédito da fonte original fica com a tabela.
    assert cert["ub"]["provenance"]["fonte"]["source"] == "keri_2011"
    lb = cert["lb"]
    assert lb["state"] == "FORMALIZED", "K742.K_7_4_2_eq_19 é incondicional no kernel (v0.8)"
    assert lb["provenance"]["lean"] == {"declaration": "K742.K_7_4_2_eq_19", "tag": "v0.8.0"}
    assert "condicional" not in lb["provenance"]["lean"]
    # não sobe para INDEPENDENTLY_REPRODUCED: a codificação independente não tem LRAT (ledger/README.md)
    assert lb["provenance"]["verificador_independente"] and lb["provenance"]["reproducao_independente"]
    assert c["published"]["exact"] is False and c["published"]["lb"]["value"] == 17


def test_registro_que_chama_de_formalized_um_teorema_condicional_aborta_o_build():
    sources = json.loads((RAIZ / "ledger" / "sources.json").read_text())
    ours = json.loads((RAIZ / "ledger" / "ours.json").read_text())
    ours["cells"]["7,4,2"]["lb"]["estado"] = "FORMALIZED"
    ours["cells"]["7,4,2"]["lb"]["lean"]["condicional"] = ["Ponte18 (hipótese pendente)"]
    with pytest.raises(SystemExit, match="condicional"):
        build.construir(build.ler_fontes(FONTES, sources), ours, sources)


def test_cota_inferior_nossa_acima_da_superior_aborta_o_build():
    sources = json.loads((RAIZ / "ledger" / "sources.json").read_text())
    ours = json.loads((RAIZ / "ledger" / "ours.json").read_text())
    ours["cells"]["7,4,2"]["lb"]["value"] = 20
    with pytest.raises(SystemExit, match="superior"):
        build.construir(build.ler_fontes(FONTES, sources), ours, sources)


def test_cota_so_publicada_fica_claimed_com_versao_da_tabela_congelada_no_meta(ledger_recortado):
    led = build.carregar(ledger_recortado / "cells.json")
    c = {x["id"]: x for x in led["cells"]}["K6(9,3)"]
    ub = c["certification"]["ub"]
    assert ub["state"] == "CLAIMED" and ub["provenance"]["lacuna"]
    v = led["meta"]["versoes"][ub["provenance"]["versao"]]
    assert v["commit"] and len(v["sha256"]) == 64 and v["arquivo"]


def test_superior_com_codigo_em_data_codes_e_lean_chega_a_independently_reproduced(ledger_recortado):
    ub = _celulas(ledger_recortado)[(7, 9, 4)]["certification"]["ub"]
    assert ub["state"] == "INDEPENDENTLY_REPRODUCED"
    assert ub["provenance"]["witness"] == "data/codes/q7_n9_R4_M1134.txt"
    assert ub["provenance"]["fonte"]["source"] == "nosso"


def test_prova_lean_do_florath_fica_registrada_mas_nao_sobe_o_estado(ledger_recortado):
    lb = _celulas(ledger_recortado)[(8, 4, 2)]["certification"]["lb"]
    assert lb["value"] == 23 and lb["state"] == "CLAIMED"
    assert lb["provenance"]["formalizacao_externa"]["source"] == "florath_lean"


def test_toda_cota_do_ledger_tem_estado_valido_e_os_seis_campos_de_proveniencia():
    led = build.carregar(RAIZ / "ledger" / "cells.json")
    assert led["meta"]["estados"] == list(build.ESTADOS)
    for c in led["cells"]:
        for lado in ("ub", "lb"):
            b = c["certification"][lado]
            assert b["state"] in build.ESTADOS, c["id"]
            p = b["provenance"]
            assert set(build.CAMPOS_PROVENIENCIA) <= set(p), c["id"]
            if b["state"] == "CLAIMED":
                assert p["fonte"] and p["versao"] in led["meta"]["versoes"], c["id"]
            else:
                assert p["lean"] or p["witness"], c["id"]


def test_sha256_de_todo_witness_do_ledger_confere_com_o_arquivo():
    led = build.carregar(RAIZ / "ledger" / "cells.json")
    vistos = 0
    for c in led["cells"]:
        for lado in ("ub", "lb"):
            p = c["certification"][lado]["provenance"]
            if p["witness"] and p["sha256"]:
                assert hashlib.sha256((RAIZ / p["witness"]).read_bytes()).hexdigest() == p["sha256"], p["witness"]
                vistos += 1
    assert vistos >= 13


def test_cobertura_commitada_bate_com_a_gerada_do_ledger():
    import cobertura

    led = build.carregar(RAIZ / "ledger" / "cells.json")
    assert (RAIZ / "ledger" / "COBERTURA.md").read_text(encoding="utf-8") == cobertura.relatorio(led)


def test_cobertura_conta_k7_4_2_entre_as_exatas_e_usa_a_frase_aprovada():
    import cobertura

    texto = cobertura.relatorio(build.carregar(RAIZ / "ledger" / "cells.json"))
    assert "A machine-checked ledger of covering-code upper bounds, with formally certified exact entries." in texto
    assert "| K7(4,2) | 19 | FORMALIZED | 19 | FORMALIZED | sim |" in texto
    assert "entire covering-code table has been formally verified" not in texto


def test_celula_fechada_por_nos_sai_dos_alvos(ledger_recortado):
    cells = build.carregar(ledger_recortado / "cells.json")["cells"]
    assert "K7(4,2)" not in {t["id"] for t in targets.ranquear(cells)}


# ---------------------------------------------------------------- CERTIFICATE_VERIFIED (v0.9)

EXATAS_POR_CERTIFICADO = {
    # célula: (valor, tipo de certificado, PR do certificado, PR do red team, estado da superior)
    (3, 6, 2): (17, ["Farkas"], [60], 61, "INDEPENDENTLY_REPRODUCED"),
    (7, 6, 4): (14, ["LRAT"], [56], 62, "INDEPENDENTLY_REPRODUCED"),
    (7, 5, 3): (17, ["LRAT"], [56], 67, "INDEPENDENTLY_REPRODUCED"),
    # 2026-10-07, por decisão do dono: o "red team" é a dupla checagem do autor no #111 (o registro diz isso);
    # a superior é o código de data/codes/ sem teorema Lean, logo WITNESS_CHECKED
    (4, 7, 4): (10, ["LRAT"], [103, 111], 111, "WITNESS_CHECKED"),
}


def test_k4_6_3_inferior_12_por_certificado_sem_virar_exata(ledger_recortado):
    c = _celulas(ledger_recortado)[(4, 6, 3)]
    cert = c["certification"]
    assert cert["lb"]["value"] == 12 and cert["lb"]["state"] == "CERTIFICATE_VERIFIED"
    assert cert["ub"]["value"] == 14 and cert["ub"]["state"] == "CLAIMED" and cert["exact"] is False
    k = cert["lb"]["provenance"]["certificado"]
    assert "PENDENTE" in k["red_team"]["veredito"].upper()
    for arq, sha in k["arquivos"].items():
        assert hashlib.sha256((RAIZ / arq).read_bytes()).hexdigest() == sha, arq


def _ours_e_sources():
    return (json.loads((RAIZ / "ledger" / "ours.json").read_text()),
            json.loads((RAIZ / "ledger" / "sources.json").read_text()))


def test_escada_sem_certificate_verified_entre_witness_checked_e_formalized_falha():
    e = build.ESTADOS
    assert "CERTIFICATE_VERIFIED" in e
    assert e.index("WITNESS_CHECKED") < e.index("CERTIFICATE_VERIFIED") < e.index("FORMALIZED")
    assert set(build.TIPOS_CERTIFICADO) == {"LRAT", "VeriPB", "Farkas"}


def test_cobertura_com_lista_de_estados_propria_divergiria_do_build():
    import cobertura

    assert cobertura.ESTADOS == build.ESTADOS and set(cobertura.CURTO) == set(build.ESTADOS)


@pytest.mark.parametrize("campo", ["red_team", "verificadores", "arquivos", "pr", "tipo"])
def test_certificate_verified_sem_campo_de_proveniencia_aborta_o_build(campo):
    ours, sources = _ours_e_sources()
    del ours["cells"]["7,5,3"]["lb"]["certificado"][campo]
    with pytest.raises(SystemExit, match="CERTIFICATE_VERIFIED sem proveniência completa"):
        build.construir(build.ler_fontes(FONTES, sources), ours, sources)


def test_certificate_verified_com_tipo_de_certificado_fora_da_lista_aborta_o_build():
    ours, sources = _ours_e_sources()
    ours["cells"]["3,6,2"]["lb"]["certificado"]["tipo"] = ["DRAT"]
    with pytest.raises(SystemExit, match="certificado.tipo"):
        build.construir(build.ler_fontes(FONTES, sources), ours, sources)


def test_certificate_verified_com_teorema_lean_aborta_porque_seria_formalized():
    ours, sources = _ours_e_sources()
    ours["cells"]["7,6,4"]["lb"]["lean"] = {"declaration": "K764.K_7_6_4_ge_14", "tag": None}
    with pytest.raises(SystemExit, match="FORMALIZED"):
        build.construir(build.ler_fontes(FONTES, sources), ours, sources)


@pytest.mark.parametrize("q,n,R", sorted(EXATAS_POR_CERTIFICADO))
def test_celula_exata_por_certificado_perde_lb_igual_ub_ou_proveniencia(ledger_recortado, q, n, R):
    valor, tipo, prs, red_team, estado_ub = EXATAS_POR_CERTIFICADO[(q, n, R)]
    c = _celulas(ledger_recortado)[(q, n, R)]
    cert = c["certification"]
    assert cert["exact"] is True and cert["lb"]["value"] == cert["ub"]["value"] == valor
    assert c["published"]["exact"] is False, "antes destas provas a célula estava aberta"
    assert cert["ub"]["state"] == estado_ub
    lb = cert["lb"]
    assert lb["state"] == "CERTIFICATE_VERIFIED" and lb["provenance"]["lean"] is None
    p = lb["provenance"]
    assert set(build.CAMPOS_PROVENIENCIA) <= set(p)
    assert p["witness"] and p["verificador_independente"] and p["fonte"]["source"] == "nosso"
    assert hashlib.sha256((RAIZ / p["witness"]).read_bytes()).hexdigest() == p["sha256"]
    k = p["certificado"]
    assert k["tipo"] == tipo and k["pr"] == prs and k["red_team"]["pr"] == red_team
    assert (RAIZ / k["red_team"]["doc"]).exists() and k["verificadores"]
    arquivos = dict(k["arquivos"])
    arquivos.update((k.get("reproducao_independente") or {}).get("arquivos", {}))
    assert p["witness"] in k["arquivos"]
    for arq, sha in arquivos.items():
        assert hashlib.sha256((RAIZ / arq).read_bytes()).hexdigest() == sha, arq


def test_k3_6_2_registra_a_reproducao_independente_do_pr_66():
    ours, _ = _ours_e_sources()
    rep = ours["cells"]["3,6,2"]["lb"]["certificado"]["reproducao_independente"]
    assert rep["pr"] == 66 and set(rep["tipo"]) == {"VeriPB", "Farkas"}


def test_k7_6_4_superior_14_e_teorema_lean_com_o_codigo_de_data_codes_e_bate_a_publicada_15(ledger_recortado):
    c = _celulas(ledger_recortado)[(7, 6, 4)]
    assert c["published"]["ub"]["value"] == 15 and c["best"] == {
        "ub": 14, "holder": "ours_lean", "beats_published": True}
    assert c["ours_lean"]["declaration"] == "CoveringK764.K_7_6_4_le_14"
    assert c["certification"]["ub"]["provenance"]["witness"] == "data/codes/q7_n6_R4_M14.txt"


def test_k7_5_3_superior_17_deixou_de_ser_so_anunciada_e_e_teorema_lean_com_codigo_nosso(ledger_recortado):
    c = _celulas(ledger_recortado)[(7, 5, 3)]
    assert c["published"]["ub"]["value"] == 17 and c["best"] == {
        "ub": 17, "holder": "ours_lean", "beats_published": False}
    assert c["ours_lean"]["declaration"] == "CoveringK753.K_7_5_3_le_17"
    assert c["ours_computational"]["provenance"] == "P-753-17"
    ub = c["certification"]["ub"]
    assert ub["state"] == "INDEPENDENTLY_REPRODUCED"
    assert ub["provenance"]["witness"] == "data/codes/q7_n5_R3_M17.txt"


def test_cobertura_lista_as_tres_exatas_por_certificado():
    import cobertura

    texto = cobertura.relatorio(build.carregar(RAIZ / "ledger" / "cells.json"))
    assert "| K3(6,2) | 17 | INDEPENDENTLY_REPRODUCED | 17 | CERTIFICATE_VERIFIED | sim |" in texto
    assert "| K7(5,3) | 17 | INDEPENDENTLY_REPRODUCED | 17 | CERTIFICATE_VERIFIED | sim |" in texto
    assert "| K7(6,4) | 14 | INDEPENDENTLY_REPRODUCED | 14 | CERTIFICATE_VERIFIED | sim |" in texto


def test_chave_do_keri_sem_tabela_e_ambigua_por_isso_a_proveniencia_nomeia_tabela_e_legenda():
    """A letra `f` é "van Wee, 1988" na tabela q=2 e "direct sum" na de q≥6: sem a tabela, a
    referência não identifica a fonte."""
    leg = build.legendas_keri({"keys": [
        {"src": "keri_6-21_tables.pdf", "lower": {}, "upper": {"f": "direct sum", "unmarked": "trivial"}}]})
    assert build.ref_keri(7, "ub", "f", leg) == "chave 'f' da tabela do Kéri para q≥6 (direct sum)"
    assert build.ref_keri(2, "ub", "f", leg) == "chave 'f' da tabela do Kéri para q=2 (van Wee, 1988)"
    assert build.ref_keri(9, "ub", None, leg) == "sem chave na tabela do Kéri para q≥6 (trivial)"
    # Tabela sem legenda transcrita (q=3 aqui): diz a tabela, sem inventar referência.
    assert build.ref_keri(3, "ub", "v", leg) == "chave 'v' da tabela do Kéri para q=3"
    assert [build.tabela_keri(q) for q in (2, 3, 4, 5, 6, 21)] == ["q=2", "q=3", "q=4–5", "q=4–5", "q≥6", "q≥6"]


def test_ledger_publicado_diz_a_tabela_do_keri_em_toda_cota_que_vem_dela():
    cells = build.carregar(RAIZ / "ledger" / "cells.json")["cells"]
    vistos = 0
    for c in cells:
        for lado in ("ub", "lb"):
            b = c["certification"][lado]
            f = (b or {}).get("provenance", {}).get("fonte") or {}
            if f.get("source") == "keri_2011":
                vistos += 1
                assert f"tabela do Kéri para {build.tabela_keri(c['q'])}" in f["ref"], c["id"]
    assert vistos > 1000
    d = {c["id"]: c for c in cells}
    assert d["K7(9,3)"]["published"]["sources"]["keri_2011"]["ub_ref"] == \
        "chave 'f' da tabela do Kéri para q≥6 (direct sum)"
