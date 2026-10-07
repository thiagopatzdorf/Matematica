"""Contabilidade ponta a ponta: speedup local não pode virar ganho global, nem fase pode sumir da conta."""
import json
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


LOTE = RAIZ / "tools" / "fatoracao" / "baseline" / "cado_legado.jsonl"


def _linhas():
    return [json.loads(l) for l in LOTE.read_text(encoding="utf-8").splitlines() if l.strip()]


def _rodada(digitos=60, achadas=1000, distintas=900, ok=True):
    return {"digitos": digitos, "rels_total": achadas, "rels_unicas": distintas, "fatores_ok": ok}


def test_rodada_que_falhou_soma_no_custo_de_informacao_sem_entrar_no_divisor():
    com_falha = c.custo_informacao([_rodada(), _rodada(), _rodada(achadas=1000, distintas=900, ok=False)])
    sem_falha = c.custo_informacao([_rodada(), _rodada()])
    assert com_falha["falhas"] == 1
    assert com_falha["rels_por_bit"] == pytest.approx(sem_falha["rels_por_bit"] * 3 / 2, rel=1e-12)


def test_lote_inteiro_sem_nenhum_fator_entregue_nao_vira_custo_zero():
    with pytest.raises(ValueError, match="infinito"):
        c.custo_informacao([_rodada(ok=False), _rodada(ok=False)])


def test_registro_com_distintas_maiores_que_achadas_e_recusado_em_vez_de_dar_repeticao_negativa():
    with pytest.raises(ValueError, match="corrompido"):
        c.custo_informacao([_rodada(achadas=1000, distintas=1001)])


def test_tamanhos_misturados_numa_chamada_so_nao_viram_uma_media_sem_sentido():
    with pytest.raises(ValueError, match="misturados"):
        c.custo_informacao([_rodada(digitos=60), _rodada(digitos=65)])


def test_bits_do_menor_fator_de_semiprimo_de_60_digitos_sao_cerca_de_100():
    assert c.bits_do_menor_fator(60) == pytest.approx(99.66, abs=0.01)
    with pytest.raises(ValueError):
        c.bits_do_menor_fator(1)


def test_linha_de_base_congelada_do_cado_inclui_a_falha_do_c90_na_conta():
    por_digitos = {t["digitos"]: t for t in c.tabela_informacao(_linhas())}
    assert sorted(por_digitos) == [60, 65, 70, 75, 80, 85, 90, 95]
    assert por_digitos[60]["rels_por_bit"] == pytest.approx(524, rel=0.005)
    # sem a rodada que falhou daria ~6.600; com ela, o que se pagou de fato
    assert por_digitos[90]["falhas"] == 1 and por_digitos[90]["rels_por_bit"] == pytest.approx(10253, rel=0.005)
    assert por_digitos[95]["rels_por_bit"] == pytest.approx(16259, rel=0.005)


def test_custo_de_informacao_por_bit_cresce_com_o_tamanho_na_linha_de_base():
    custos = [t["rels_por_bit"] for t in c.tabela_informacao(_linhas())]
    assert custos == sorted(custos)
