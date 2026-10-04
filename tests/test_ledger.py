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
    assert len(nossos) == 12
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
