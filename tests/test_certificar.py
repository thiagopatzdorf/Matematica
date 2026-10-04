"""Certificação em lote das cotas superiores (tools/certificar/): gerador, avaliador e ledger."""
import json
import sys

import build
from conftest import RAIZ

sys.path.insert(0, str(RAIZ / "tools" / "certificar"))
import buscar  # noqa: E402
import gerar  # noqa: E402

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
    V, _a, _n = gerar.fechar(CELLS, gerar.ler_witnesses())
    for c in CELLS:
        assert V[(c["q"], c["n"], c["R"])] >= c["best"]["ub"], c["id"]


def test_formal_ub_commitado_e_o_que_o_gerador_produz_hoje():
    r = gerar.gerar(CELLS, escrever=False)
    assert r["certificadas"] == len(FORMAL)
    cotas = (RAIZ / "CoveringLean" / "Ledger" / "Cotas.lean").read_text()
    for k, e in FORMAL.items():
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
    for p in (RAIZ / "CoveringLean" / "Ledger").glob("*.lean"):
        t = p.read_text()
        assert "sorry" not in t and "native_decide" not in t and "implemented_by" not in t, p.name
    assert "#print axioms CoveringLedger.todas_as_cotas" in (RAIZ / "CoveringLean/Ledger/Cotas.lean").read_text()
