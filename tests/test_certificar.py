"""Certificação em lote das cotas superiores (tools/certificar/): gerador, avaliador e ledger."""
import itertools
import json
import sys

import build
from conftest import RAIZ

sys.path.insert(0, str(RAIZ / "tools" / "certificar"))
import buscar  # noqa: E402
import gerar  # noqa: E402
import lineares  # noqa: E402

CELLS = build.carregar(RAIZ / "ledger" / "cells.json")["cells"]
FORMAL = json.loads((RAIZ / "ledger" / "formal_ub.json").read_text())["cells"]


def test_avaliador_reprova_codigo_que_deixa_ponto_descoberto():
    assert buscar.cobre(2, 3, 1, [[0, 0, 0], [1, 1, 1]])
    assert not buscar.cobre(2, 3, 1, [[0, 0, 0], [1, 1, 0]])
    assert not buscar.cobre(2, 3, 1, [[0, 0, 0], [0, 0, 0], [1, 1, 1]]), "palavra repetida"


def test_todo_witness_versionado_cobre_o_espaco_pelo_avaliador_python():
    """Segundo verificador, independente do kernel: reconfere cada código em todo pytest."""
    wits = gerar.ler_witnesses()
    assert len(wits) >= 50
    for (q, n, R), (M, p, idx) in wits.items():
        code = [[(w // q**k) % q for k in range(n)] for w in idx]
        assert len(code) == M and buscar.cobre(q, n, R, code), p.name


def test_regras_nunca_dao_cota_abaixo_da_melhor_conhecida():
    V, _a, _n = gerar.fechar(CELLS, gerar.ler_witnesses(), lineares.ler_lineares())
    for c in CELLS:
        assert V[(c["q"], c["n"], c["R"])] >= c["best"]["ub"], c["id"]


def test_formal_ub_commitado_e_o_que_o_gerador_produz_hoje():
    r = gerar.gerar(CELLS, escrever=False)
    assert r["certificadas"] == len(FORMAL)
    for k, e in FORMAL.items():
        cotas = (RAIZ / e["arquivo"]).read_text()
        assert f"theorem {e['declaration'].split('.')[-1]} : K " in cotas, k


def test_palavras_constantes_certificam_k2_3_1_e_vao_para_formalized_no_ledger():
    c = {x["id"]: x for x in CELLS}["K2(3,1)"]
    assert FORMAL["2,3,1"]["construcao"] == "palavras constantes (pombal)"
    assert c["certification"]["ub"]["state"] == "FORMALIZED"
    assert c["certification"]["ub"]["provenance"]["lean"]["declaration"] == "CoveringLedger.K2_3_1_le_2"


def test_witness_explicito_chega_a_independently_reproduced_e_regra_pura_nao():
    por_estado = {}
    for c in CELLS:
        k = f"{c['q']},{c['n']},{c['R']}"
        if k in FORMAL and c["certification"]["ub"]["provenance"]["lean"]["declaration"] == FORMAL[k]["declaration"]:
            por_estado.setdefault(bool(FORMAL[k]["witness"]), set()).add(c["certification"]["ub"]["state"])
    assert por_estado[True] == {"INDEPENDENTLY_REPRODUCED"}
    assert por_estado[False] == {"FORMALIZED"}


def test_cota_formal_maior_que_a_melhor_nao_sobe_o_estado():
    c = {x["id"]: x for x in CELLS}["K3(6,1)"]  # football pool: 73, nenhum certificado nosso
    assert c["certification"]["ub"]["state"] == "CLAIMED"
    assert "3,6,1" not in FORMAL


def test_familia_da_particao_q42_entra_com_a_cota_do_keri_ate_o_teto_de_custo_do_kernel():
    assert FORMAL["10,4,2"]["M"] == 34 and FORMAL["10,4,2"]["witness"].endswith("K10_4_2_M34.txt")
    # q = 21: 21^4 · 147 ≈ 2,9·10^7 passa do teto (o kernel não fecha aqui); o witness fica versionado.
    assert (RAIZ / "tools/certificar/witnesses/K21_4_2_M147.txt").exists() and "21,4,2" not in FORMAL
    assert 21**4 * 147 > gerar.CUSTO_MAX


def test_lean_gerado_nao_tem_atalho_fora_do_kernel():
    for p in [*(RAIZ / "CoveringLean" / "Ledger").glob("*.lean"), *(RAIZ / "CoveringLean" / "LedgerExt").glob("*.lean")]:
        t = p.read_text()
        assert "sorry" not in t and "native_decide" not in t and "implemented_by" not in t, p.name
    assert "#print axioms CoveringLedger.todas_as_cotas" in (RAIZ / "CoveringLean/Ledger/Cotas.lean").read_text()



def test_avaliador_de_sindromes_reprova_codigo_linear_que_nao_cobre():
    hamming = [[1, 0, 0, 0, 0, 1, 1], [0, 1, 0, 0, 1, 0, 1], [0, 0, 1, 0, 1, 1, 0], [0, 0, 0, 1, 1, 1, 1]]
    assert lineares.cobre_por_sindromes(2, 7, 1, hamming)
    estragado = [list(g) for g in hamming]
    estragado[3][6] = 0  # duas colunas de H iguais: uma síndrome fica sem líder de peso 1
    assert not lineares.cobre_por_sindromes(2, 7, 1, estragado)


def test_todo_codigo_linear_versionado_cobre_pelas_sindromes_e_pela_forca_bruta_quando_cabe():
    """Dois avaliadores Python, independentes do kernel e entre si: síndromes sempre; e, para
    espaço pequeno, a lista inteira de q^k palavras no avaliador de buscar.py."""
    lins = lineares.ler_lineares()
    assert len(lins) >= 10
    for (q, n, R), (M, p, G, _c) in lins.items():
        assert lineares.cobre_por_sindromes(q, n, R, G), p.name
        assert len(lineares.testemunhas(q, n, R, G)) == q ** (n - len(G)), p.name
        if q**n <= 40_000:
            k = len(G)
            code = [[sum(u[j] * G[j][i] for j in range(k)) % q for i in range(n)]
                    for u in itertools.product(range(q), repeat=k)]
            assert len(code) == M and buscar.cobre(q, n, R, code), p.name


def test_testemunha_do_transversal_falta_quando_o_raio_e_pequeno_demais():
    G = json.loads((RAIZ / "tools/certificar/lineares/K5_6_1_M625.json").read_text())["gerador"]
    try:
        lineares.testemunhas(5, 6, 0, G)
    except ValueError as e:
        assert "não cobre" in str(e)
    else:
        raise AssertionError("raio 0 não cobre com 625 palavras")


def test_golay_hamming_e_lineares_do_keri_entram_no_lote_com_segundo_verificador():
    for k, chave in (("2,23,3", "h"), ("3,11,2", "h"), ("2,15,1", "h"), ("7,6,2", "p"), ("13,8,2", "p")):
        e = FORMAL[k]
        assert e["witness"].startswith("tools/certificar/lineares/") and e["verificador"] == lineares.VERIFICADOR
        c = {f"{x['q']},{x['n']},{x['R']}": x for x in CELLS}[k]
        assert c["published"]["sources"]["keri_2011"]["ub_key"] == chave
        assert c["certification"]["ub"]["state"] == "INDEPENDENTLY_REPRODUCED"
    # Célula derivada por regra de um código linear: FORMALIZED, sem segundo verificador.
    assert FORMAL["7,9,3"]["construcao"] == "soma direta de K7(3,1) ≤ 25 e K7(6,2) ≤ 343"
    assert {x["id"]: x for x in CELLS}["K7(9,3)"]["certification"]["ub"]["state"] == "FORMALIZED"


def test_chave_do_keri_declarada_no_json_do_codigo_linear_e_a_do_ledger():
    por_id = {(c["q"], c["n"], c["R"]): c for c in CELLS}
    for (q, n, R), (_M, p, _G, _c) in lineares.ler_lineares().items():
        d = json.loads(p.read_text(encoding="utf-8"))
        assert d["chave_keri"] == por_id[(q, n, R)]["published"]["sources"]["keri_2011"]["ub_key"], p.name


def test_celula_que_so_sai_de_base_externa_vai_para_o_lote_ext_com_a_lib_dele():
    # K2(16,2) ≤ 768: coordenada muda sobre K2(15,2) ≤ 384, que é certificado por síndromes (Syn_K2_15_2_384).
    e = FORMAL["2,16,2"]
    assert e["lib"] == "CoveringLedgerExt" and e["arquivo"] == "CoveringLean/LedgerExt/Cotas.lean"
    assert e["construcao"] == "coordenada muda (t = 1) de K2(15,2) ≤ 384"
    c = {x["id"]: x for x in CELLS}["K2(16,2)"]
    assert c["certification"]["ub"]["state"] == "FORMALIZED"
    assert c["certification"]["ub"]["provenance"]["lean"] == {"declaration": "CoveringLedgerExt.K2_16_2_le_768",
                                                              "lib": "CoveringLedgerExt"}


def test_lote_principal_nao_importa_modulo_de_base_externa():
    """O CoveringLedger tem de continuar barato: as bases externas (KO05 ~30 min, síndromes) só entram
    no CoveringLedgerExt."""
    cotas = (RAIZ / "CoveringLean" / "Ledger" / "Cotas.lean").read_text()
    assert "Literatura" not in cotas and "Syn_K" not in cotas
    assert "#print axioms CoveringLedgerExt.todas_as_cotas" in (RAIZ / "CoveringLean/LedgerExt/Cotas.lean").read_text()


def test_bases_externas_nao_mudam_o_lote_principal():
    sem = gerar.gerar(CELLS, escrever=False, externos={})
    com = gerar.gerar(CELLS, escrever=False)
    assert sem["externas"]["certificadas"] == 0
    assert com["por_regra"] == sem["por_regra"]
    assert com["certificadas"] == sem["certificadas"] + com["externas"]["certificadas"]
    assert sum(1 for e in FORMAL.values() if e.get("lib") == "CoveringLedgerExt") == com["externas"]["certificadas"]


def test_base_externa_de_lib_pesada_ou_de_enunciado_desconhecido_fica_de_fora():
    ext = gerar.ler_externos()
    # K5(9,3) ≤ 1250 vive em K3_K5_9_3_Final (CoveringHeavy, ~13 h de CPU): não pode virar base.
    assert (5, 9, 3) not in ext and "lib pesada" in gerar.RECUSADOS["5,9,3"]
    assert ext[(2, 15, 2)] == (384, "UB.of_exists Syn.K2_15_2_le_384_syn", "CoveringLean.Syn_K2_15_2_384")
    assert ext[(8, 5, 2)] == (128, "K_le_iff.mp CoveringLit.K8_5_2_le_128", "CoveringLean.Literatura.KO05")
    assert all(not m.startswith(("CoveringLedger", "CoveringLedgerExt")) for _M, p, m in ext.values() for _ in [p])


def test_teorema_externo_com_nome_de_outra_celula_e_recusado(tmp_path):
    ours = {"cells": {"8,5,2": {"ours_lean": {"M": 128, "declaration": "CoveringLit.K9_5_2_le_189"}}}}
    arq = tmp_path / "ours.json"
    arq.write_text(json.dumps(ours))
    assert gerar.ler_externos(arq) == {}
    assert "enunciado fora das duas formas" in gerar.RECUSADOS["8,5,2"]
