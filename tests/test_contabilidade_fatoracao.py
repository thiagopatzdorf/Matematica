"""Contabilidade ponta a ponta: speedup local não pode virar ganho global, nem fase pode sumir da conta."""
import sys

import pytest

from conftest import RAIZ

sys.path.insert(0, str(RAIZ / "tools" / "fatoracao"))
import contabilidade as c  # noqa: E402


def test_speedup_local_de_100x_em_1_por_cento_nao_vale_100x():
    ganho = c.ganho_amdahl({"a": 0.01, "b": 0.99}, {"a": 100})
    assert ganho == pytest.approx(1 / 0.9901, rel=1e-12) and round(ganho, 4) == 1.0100


def test_fase_inteira_a_custo_zero_passa_do_teto_de_amdahl():
    sh = c.participacoes(c.RSA896_HORAS)
    teto = c.teto_por_fase(sh)
    assert teto["polyselect"] < 1.08 and 1.55 < teto["crivo"] < 1.7
    assert c.ganho_amdahl(sh, {"crivo": 1e9}) == pytest.approx(teto["crivo"], rel=1e-6)


def test_participacoes_que_nao_somam_um_passam_na_conta():
    with pytest.raises(ValueError, match="somam"):
        c.ganho_amdahl({"a": 0.5, "b": 0.4}, {"a": 2})


def test_razao_ponta_a_ponta_aceita_novo_metodo_sem_a_fase_de_algebra_linear():
    base = {f: 10.0 for f in c.FASES}
    novo = {f: 1.0 for f in c.FASES if f != "algebra_linear"}
    with pytest.raises(ValueError, match="algebra_linear"):
        c.razao_fim_a_fim(base, novo)


def test_razao_ponta_a_ponta_com_custo_negativo_ou_zero_vira_ganho_infinito():
    base = {f: 1.0 for f in c.FASES}
    with pytest.raises(ValueError):
        c.razao_fim_a_fim(base, {**base, "crivo": -1.0})
    with pytest.raises(ValueError):
        c.razao_fim_a_fim(base, {f: 0.0 for f in c.FASES})


def test_razao_soma_as_fases_e_nao_a_media_das_razoes():
    base = {"polyselect": 1.0, "crivo": 98.0, "filtragem": 0.5, "algebra_linear": 0.5, "raiz": 0.0}
    novo = {"polyselect": 0.01, "crivo": 98.0, "filtragem": 0.5, "algebra_linear": 0.5, "raiz": 0.0}  # só a fase de 1% melhorou 100×
    assert c.razao_fim_a_fim(base, novo) == pytest.approx(100.0 / 99.01, rel=1e-9)


def test_degrau_decidido_pela_estimativa_pontual_e_nao_pelo_limite_inferior():
    estimativa, inferior, _ = 12.0, 4.0, 30.0
    assert c.degrau(inferior).startswith("2×") and not c.degrau(estimativa).startswith("2×")
    assert c.degrau(0.9).startswith("abaixo") and c.degrau(1.0).startswith("1×")
    assert c.degrau(100).startswith("100×") and c.degrau(999).startswith("100×") and c.degrau(1000).startswith("1000×")


def test_intervalo_de_confianca_de_metodos_iguais_nao_exclui_a_razao_1():
    base = [100.0, 120.0, 90.0, 110.0, 105.0, 95.0]
    estimativa, inferior, superior = c.ic_razao(base, list(base))
    assert estimativa == pytest.approx(1.0) and inferior < 1.0 < superior


def test_intervalo_de_confianca_muda_com_a_semente_da_reamostragem():
    base, novo = [100.0, 130.0, 90.0, 140.0], [10.0, 13.0, 9.0, 14.0]
    assert c.ic_razao(base, novo, semente=3) == c.ic_razao(base, novo, semente=3)
    est, inf, sup = c.ic_razao(base, novo)
    assert est == pytest.approx(10.0) and inf < est < sup


def test_intervalo_de_confianca_com_uma_so_replica_devolve_intervalo():
    with pytest.raises(ValueError, match="réplicas"):
        c.ic_razao([100.0], [10.0, 11.0])
