"""Propagador de cotas (tools/propagar/): regras na direção certa, ponto fixo e o ledger real."""
import json
import sys

from conftest import RAIZ

sys.path.insert(0, str(RAIZ / "tools" / "propagar"))
import propagar as p  # noqa: E402

CELLS = json.loads((RAIZ / "ledger" / "cells.json").read_text())["cells"]


def cel(q, n, R, lb, ub):
    return {"q": q, "n": n, "R": R, "certification": {"lb": {"value": lb}}, "best": {"ub": ub}}


def test_alongamento_livre_baixa_a_superior_do_vizinho_e_sobe_a_inferior_do_outro():
    e = p.propagar(p.carregar([cel(3, 4, 1, 9, 9), cel(3, 5, 2, 2, 27)]))
    assert e.ub[(3, 5, 2)] <= 9, "K(n+1,R+1) <= K(n,R)"
    e = p.propagar(p.carregar([cel(3, 4, 1, 1, 81), cel(3, 5, 2, 7, 27)]))
    assert e.lb[(3, 4, 1)] >= 7, "contrapositiva: lb(n,R) >= lb(n+1,R+1)"


def test_coordenada_muda_divide_a_inferior_por_q_arredondando_para_cima():
    e = p.propagar(p.carregar([cel(2, 5, 1, 7, 7), cel(2, 6, 1, 13, 16)]))
    assert e.lb[(2, 5, 1)] >= 7 and e.ub[(2, 6, 1)] <= 14, "K(n+1,R) <= q K(n,R)"
    regra, prem = e.por[("ub", (2, 6, 1))]
    assert regra == "muda" and prem == [("ub", (2, 5, 1))]
    e = p.propagar(p.carregar([cel(2, 5, 1, 1, 7), cel(2, 6, 1, 13, 16)]))
    assert e.lb[(2, 5, 1)] == 7, "lb(n,R) >= ceil(lb(n+1,R)/q) = ceil(13/2)"


def test_projecao_nunca_passa_a_superior_do_alfabeto_menor_para_o_maior():
    e = p.propagar(p.carregar([cel(2, 3, 1, 2, 2), cel(3, 3, 1, 3, 5)]))
    assert e.ub[(3, 3, 1)] == 5, "K_2 <= K_3 não dá cota superior para K_3"
    e = p.propagar(p.carregar([cel(2, 3, 1, 2, 2), cel(3, 3, 1, 1, 5)]))
    assert e.lb[(3, 3, 1)] >= 2, "mas a inferior do alfabeto menor sobe para o maior"


def test_soma_direta_multiplica_superiores_e_a_contrapositiva_divide_pela_superior_do_outro():
    e = p.propagar(p.carregar([cel(2, 3, 1, 2, 2), cel(2, 6, 2, 4, 64)]))
    assert e.ub[(2, 6, 2)] <= 4
    e = p.propagar(p.carregar([cel(2, 3, 1, 1, 2), cel(2, 6, 2, 5, 64)]))
    assert e.lb[(2, 3, 1)] >= 3, "lb(3,1) >= ceil(lb(6,2) / ub(3,1)) = ceil(5/2)"


def test_dado_contraditorio_aparece_como_inconsistencia_com_as_duas_cadeias():
    e = p.propagar(p.carregar([cel(3, 4, 2, 9, 9), cel(3, 5, 2, 2, 5)]))
    assert (3, 4, 2) in p.inconsistencias(e), "punção: K(4,2) <= K(5,2) = 5 < 9"
    assert any("ledger" in passo for passo in p.cadeia(e, "ub", (3, 4, 2)))


def test_ledger_atual_e_resultados_novos_nao_se_contradizem():
    rel = p.relatorio(CELLS)
    assert rel["a_inconsistencias"] == [] and rel["b_inconsistencias"] == []


def test_ledger_atual_nao_e_fechado_pelas_regras_em_k17_7_2_e_k17_8_4():
    """Regressão: as duas melhorias implicadas medidas em 2026-10-05.

    Quando o ledger absorver uma delas (ou corrigir o dado de origem), atualize aqui.
    """
    rel = p.relatorio(CELLS)
    got = {d["celula"]: (d["lb"][1], d["ub"][1]) for d in rel["a_melhorias_sobre_ledger"]}
    assert got.get("K17(7,2)", (None, None))[1] == 17 * 14424
    assert got.get("K17(8,4)", (None, None))[0] == 1507


def test_cadeia_de_toda_melhoria_termina_em_fatos_de_base():
    rel = p.relatorio(CELLS)
    for d in rel["a_melhorias_sobre_ledger"] + rel["b_melhorias_por_consequencia"]:
        passos = d["cadeia_lb"] + d["cadeia_ub"]
        assert passos and any(b in passos[0] for b in ("ledger", "novo", "esfera", "trivial", "raio_grande"))


def test_ler_novos_recusa_lado_desconhecido():
    assert p.ler_novos(["7,6,4:lb=14,ub=14"]) == {(7, 6, 4): {"ref": "7,6,4:lb=14,ub=14", "lb": 14, "ub": 14}}
    try:
        p.ler_novos(["7,6,4:exato=14"])
    except ValueError:
        return
    raise AssertionError("aceitou lado inválido")
