"""Pipeline congelado da linha de base de informação: invariantes, transferência entre tamanhos e inclinação com intervalo."""
import json
import sys

import numpy as np
import pytest

from conftest import RAIZ

sys.path.insert(0, str(RAIZ / "tools" / "fatoracao"))
import baseline_informacao as b  # noqa: E402
import relacoes as rel  # noqa: E402

FIXTURE = RAIZ / "tests" / "fixtures" / "fatoracao" / "captura_c30"


@pytest.fixture(scope="module")
def instancia():
    return b.analisar_instancia(FIXTURE, "dev")


def test_pipeline_que_aceita_instancia_cujo_descasque_nao_reproduz_o_cado(instancia):
    r, _ = instancia
    assert r["valida_o_purge_do_cado"] is True and r["livres_com_ideal_ruim"] == 0


def test_destinos_das_unicas_que_nao_somam_um(instancia):
    r, m = instancia
    assert sum(r["destinos_das_unicas"].values()) == pytest.approx(1.0)
    assert len(m["dest"]) == r["n_unicas"] and len(m["x"]) == r["n_unicas"]


def test_ponto_de_parada_que_nao_vem_depois_do_fim_nem_antes_da_emergencia(instancia):
    r, _ = instancia
    p = r["parada"]
    assert 0 < p["emergencia"]["fracao_das_brutas"] <= p["t_min"]["fracao_das_brutas"] <= 1.0
    assert p["emergencia"]["fracao_das_brutas"] <= p["excesso_zero"]["fracao_das_brutas"] <= p["t_min"]["fracao_das_brutas"]
    assert p["margem_de_parada"] == pytest.approx(1.0 - p["t_min"]["fracao_das_brutas"])


def test_ponto_de_parada_que_nao_tem_excesso_minimo_no_prefixo_devolvido(instancia):
    r, _ = instancia
    d = rel.carregar(FIXTURE)
    t = r["parada"]["t_min"]["t"]
    assert rel.nucleo(d, t)[0]["excesso"] >= b.MANTER
    assert rel.nucleo(d, t - d.n_brutas // 1000 - 2)[0]["excesso"] < b.MANTER


def test_excesso_zero_que_conta_o_nucleo_vazio(instancia):
    r, _ = instancia
    d = rel.carregar(FIXTURE)
    t = r["parada"]["excesso_zero"]["t"]
    st = rel.nucleo(d, t)[0]
    assert st["linhas"] > 0 and st["excesso"] >= 0


def test_modelos_de_i_de_w_com_curva_de_tamanho_diferente_dos_pontos(instancia):
    r, _ = instancia
    assert len(r["curva"]) >= 30
    assert set(r["modelos_I_de_W"]) == {"excesso", "colunas_nucleo", "linhas_nucleo", "ideais_vistos"}
    assert all(v["vencedor"] in inf_modelos() for v in r["modelos_I_de_W"].values())


def inf_modelos():
    import informacao_relacoes as inf
    return set(inf.MODELOS)


def test_controles_sem_o_mesmo_prefixo_e_a_mesma_semente(instancia):
    r, _ = instancia
    again = b._nulos(rel.carregar(FIXTURE), [{"linhas_nucleo": r["curva"][-1]["linhas_nucleo"], "excesso": r["curva"][-1]["excesso"]}])
    assert again["configuracao"] == r["controles"]["configuracao"] and again["ordem"] == r["controles"]["ordem"]


def test_resultado_que_nao_vira_json(instancia):
    r, _ = instancia
    assert json.loads(json.dumps(r))["id"] == "captura_c30"


def _fake(digitos, conjunto, margem, emerg=0.7, tmin=0.9):
    return {"conjunto": conjunto, "digitos": digitos, "id": f"{conjunto}{digitos}", "fracao_duplicatas": 0.07, "w_sq_por_coluna_final": 1.0,
            "parada": {"emergencia": {"fracao_das_brutas": emerg}, "t_min": {"fracao_das_brutas": tmin}, "margem_de_parada": margem},
            "destinos_das_unicas": {"unica_removida_nos_singletons": 0.3, "nucleo_cortada_pelos_cliques": 0.2, "purgada_fora_da_matriz": 0.0,
                                    "na_matriz": 0.5},
            "novidade": {"beta": 0.8}, "curva": [{"excesso": 100, "linhas_nucleo": 1000}],
            "controles": {"real": {"excesso_final": 100, "linhas_nucleo_final": 1000},
                          "configuracao": {"excesso_final": 140, "linhas_nucleo_final": 990}}}


def test_intervalo_da_inclinacao_que_cobre_menos_do_que_promete():
    """Cobertura do IC de 95% sobre 60 simulações com inclinação verdadeira 0,01: tem de ficar perto de 95%, nunca perto de 50%."""
    # a semente varia a amostra; o intervalo é determinístico
    cobriu = 0
    for semente in range(60):
        rng = np.random.default_rng(semente)
        pares = [(d, 0.5 + 0.01 * d + rng.normal(0, 0.02)) for d in (60, 70, 80, 90) for _ in range(4)]
        r = b.inclinacao(pares)
        cobriu += r["ic95"][0] <= 0.01 <= r["ic95"][1]
    assert cobriu / 60 >= 0.85


def test_inclinacao_cuja_estimativa_nao_acompanha_a_tendencia():
    pares = [(d, 0.5 + 0.01 * d) for d in (60, 70, 80, 90) for _ in range(3)]
    assert b.inclinacao(pares)["inclinacao_por_digito"] == pytest.approx(0.01)


def test_inclinacao_com_dois_tamanhos_ou_menos_de_quatro_pontos_so_devolve_numero():
    assert b.inclinacao([(60, 1.0), (60, 2.0), (70, 3.0), (70, 3.5)]) is None
    assert b.inclinacao([(60, 1.0), (70, 2.0), (80, 3.0)]) is None


def test_agregado_que_mistura_dev_e_teste():
    inst = [_fake(d, "dev", m) for d, m in ((60, 0.05), (60, 0.05), (70, 0.06), (70, 0.06), (80, 0.07), (80, 0.07))]
    inst += [_fake(60, "teste", 0.04), _fake(70, "teste", 0.04)]
    ag = b.agregar(inst)
    assert set(ag["por_tamanho"]) == {"dev", "teste"}
    assert ag["por_tamanho"]["dev"]["margem_de_parada"]["70"]["media"] == pytest.approx(0.06)
    assert ag["por_tamanho"]["teste"]["margem_de_parada"].keys() == {"60", "70"}
    assert ag["inclinacao"]["teste"]["margem_de_parada"] is None  # só 2 tamanhos no teste
    assert ag["inclinacao"]["dev"]["margem_de_parada"]["inclinacao_por_digito"] == pytest.approx(0.001)
    assert ag["por_tamanho"]["dev"]["excesso_real_menos_configuracao"]["60"]["media"] == pytest.approx((100 - 140) / 1000)


def test_transferencia_que_treina_e_testa_no_mesmo_conjunto():
    rng = np.random.default_rng(1)

    def mat(d, conj, n=800):
        x = rng.normal(size=(n, 3))
        x[:, 1] = rng.normal(size=n)
        dest = np.where(x[:, 0] + 0.3 * rng.normal(size=n) > 0, 1, 4)
        nomes = ["a", "maior_primo_lado1", "c"]
        x[:, 1] = x[:, 0]
        return {"id": f"{conj}{d}", "digitos": d, "conjunto": conj, "x": x, "nomes": nomes, "dest": dest}

    mats = [mat(60, "dev"), mat(70, "dev"), mat(70, "teste"), mat(80, "teste")]
    t = b.transferencia(mats)
    assert {(x["treino_digitos"], x["teste_digitos"]) for x in t} == {(60, 70), (60, 80), (70, 70), (70, 80)}
    assert all(x["auc_logistica"] > 0.9 for x in t)
    assert all(0 <= x["fracao_rejeitada"] <= 1 for x in t)


def test_transferencia_que_deixa_vazar_o_conjunto_de_teste_para_o_treino():
    """No teste a relação característica -> destino está INVERTIDA: quem só viu o dev vai mal; quem viu o teste iria bem."""
    rng = np.random.default_rng(3)

    def mat(d, conj, sinal, n=1500):
        x = rng.normal(size=(n, 3))
        dest = np.where(sinal * x[:, 0] + 0.2 * rng.normal(size=n) > 0, 1, 4)
        return {"id": f"{conj}{d}", "digitos": d, "conjunto": conj, "x": x, "nomes": ["a", "maior_primo_lado1", "c"], "dest": dest}

    t = b.transferencia([mat(60, "dev", +1), mat(60, "teste", -1)])
    assert t[0]["auc_logistica"] < 0.2


def test_agregado_com_alguma_metrica_escalar_que_nao_bate_com_o_valor_conhecido():
    ag = b.agregar([_fake(60, "dev", 0.05)])["por_tamanho"]["dev"]
    esperado = {"emergencia_fracao": 0.7, "t_min_fracao": 0.9, "margem_de_parada": 0.05, "fracao_duplicatas": 0.07,
                "fracao_removida_nos_singletons": 0.3, "fracao_cortada_pelos_cliques": 0.2, "fracao_na_matriz": 0.5,
                "beta_de_heaps": 0.8, "excesso_final_sobre_linhas": 0.1, "w_sq_por_coluna_final": 1.0,
                "excesso_real_menos_configuracao": -0.04}
    assert set(ag) == set(esperado)
    for nome, valor in esperado.items():
        assert ag[nome]["60"]["media"] == pytest.approx(valor), nome



def _res(emerg, margem, ven_exc="M5_limiar", ven_id="M3_log", real=10, conf=20, bits=(100, 100)):
    return {"id": "x", "conjunto": "teste", "parada": {"emergencia": {"fracao_das_brutas": emerg}, "margem_de_parada": margem},
            "modelos_I_de_W": {"excesso": {"vencedor": ven_exc}, "ideais_vistos": {"vencedor": ven_id}},
            "controles": {"real": {"excesso_final": real}, "configuracao": {"excesso_final": conf}},
            "compressibilidade": {"real": {"bits_por_relacao": bits[0]}, "configuracao": {"bits_por_relacao": bits[1]}}}


def test_veredicto_que_deixa_passar_transicao_fora_do_intervalo_previsto():
    res = {"instancias": [_res(0.9, 0.05), _res(0.95, 0.05), _res(0.6, 0.05)], "transferencia": [], "agregado": {"inclinacao": {}}}
    v = b.veredictos(res)
    assert v["P1"]["passa"] is False and len(v["P1"]["fora_de_0.5_0.85"]) == 2


def test_veredicto_de_transferencia_que_reprova_sem_dado_ou_com_auc_baixa():
    base = {"instancias": [_res(0.6, 0.05)], "agregado": {"inclinacao": {}}}
    assert b.veredictos({**base, "transferencia": []})["P4"]["passa"] is None
    ruim = {"treino_digitos": 70, "teste_digitos": 80, "auc_logistica": 0.6, "fracao_rejeitada": 0.05}
    assert b.veredictos({**base, "transferencia": [ruim]})["P4"]["passa"] is False
    bom = {**ruim, "auc_logistica": 0.8}
    assert b.veredictos({**base, "transferencia": [bom]})["P4"]["passa"] is True


def test_veredicto_de_margem_que_conta_instancia_sem_t_min_como_margem_larga():
    res = {"instancias": [_res(0.6, None), _res(0.6, None)], "transferencia": [], "agregado": {"inclinacao": {}}}
    assert b.veredictos(res)["P3"]["passa"] is False


def test_veredicto_de_nulo_que_exige_excesso_real_menor_e_compressibilidade_parecida():
    res = {"instancias": [_res(0.6, 0.05, real=30, conf=20)], "transferencia": [], "agregado": {"inclinacao": {}}}
    assert b.veredictos(res)["P5"]["passa"] is False
    res = {"instancias": [_res(0.6, 0.05, bits=(120, 100))], "transferencia": [], "agregado": {"inclinacao": {}}}
    assert b.veredictos(res)["P5"]["passa"] is False
