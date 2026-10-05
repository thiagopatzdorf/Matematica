"""Executor da linha de base do CADO-NFS: falha do bloco Wiedemann não pode virar sucesso nem sumir da estatística.

Os logs em tests/fixtures/fatoracao são trechos REAIS de rodadas do CADO-NFS (um c90 que falhou com `nlucky=0` e um c60
que passou); só os prefixos de caminho foram trocados por <CADO> e <TRABALHO>.
"""
import json
import sys

import pytest

from conftest import RAIZ

sys.path.insert(0, str(RAIZ / "tools" / "fatoracao"))
import medir_cado as mc  # noqa: E402
import verificar  # noqa: E402

FIX = RAIZ / "tests" / "fixtures" / "fatoracao"
LOG_FALHA = (FIX / "falha_bwc_nlucky0.log").read_text(encoding="utf-8")
LOG_OK = (FIX / "sucesso_c60.log").read_text(encoding="utf-8")
ITEM = {"digitos": 2, "i": 0, "n": "15", "p": "3", "q": "5"}


def test_log_real_com_nlucky0_e_exit_1_nao_vira_sucesso():
    assert mc.classificar(1, LOG_FALHA, False) == "bwc_nlucky0"


def test_exit_zero_com_fatores_errados_nao_vira_ok():
    assert mc.classificar(0, "", False) == "fatores_errados"
    assert mc.classificar(0, "", True) == "ok"


def test_falha_que_nao_e_nlucky0_nao_manda_repetir_com_outra_semente():
    assert mc.classificar(1, "Segmentation fault", False) == "outra_falha"
    assert not mc.deve_repetir("outra_falha", 1)


def test_nlucky0_repete_ate_acabar_a_lista_de_sementes_e_para():
    assert mc.deve_repetir("bwc_nlucky0", 1) and mc.deve_repetir("bwc_nlucky0", 2)
    assert not mc.deve_repetir("bwc_nlucky0", len(mc.SEMENTES_BWC))


def test_repeticao_com_a_mesma_semente_da_tentativa_anterior():
    sementes = [mc.semente(t) for t in range(1, len(mc.SEMENTES_BWC) + 1)]
    assert len(set(sementes)) == len(sementes)


@pytest.mark.parametrize("saida,esperado", [("3 5", True), ("5 3", True), ("1 15", False), ("3", False), ("3 7", False),
                                            ("tres cinco", False), ("", False)])
def test_conferencia_aceita_fatores_que_nao_sao_os_gerados(saida, esperado):
    assert mc.conferir_fatores(ITEM, saida) is esperado


def test_conferencia_aceita_fatores_que_nao_multiplicam_no_numero():
    item = {"n": "15", "p": "3", "q": "5"}
    assert mc.conferir_fatores({**item, "n": "21"}, "3 5") is False


def test_primalidade_aceita_composto_conhecido():
    for composto in (561, 3215031751, 2 ** 61 + 1):
        assert not mc.eh_primo(composto), composto
    for primo in (2, 97, 2 ** 61 - 1):
        assert mc.eh_primo(primo), primo
    p, q = map(int, verificar.registro()["rsa-260"]["fatores"])
    assert mc.eh_primo(p) and mc.eh_primo(q)


def test_gerador_com_mesma_entrada_devolve_numeros_diferentes():
    a, b = mc.gerar([24, 30], 2), mc.gerar([24, 30], 2)
    assert a == b
    for x in a:
        n, p, q = int(x["n"]), int(x["p"]), int(x["q"])
        assert len(x["n"]) == x["digitos"] and p * q == n and mc.eh_primo(p) and mc.eh_primo(q)
        assert len(x["p"]) == len(x["q"])


def test_metricas_do_log_real_de_sucesso_saem_vazias():
    m = mc.metricas(LOG_OK)
    assert m["rels_total"] == 51191 and m["rels_unicas"] == 47394 and m["matriz_linhas"] == 6310
    assert m["bwc_cpu_s"] is not None and m["sqrt_cpu_s"] is not None


def test_metricas_do_log_real_de_falha_nao_inventam_o_que_nao_rodou():
    m = mc.metricas(LOG_FALHA)
    assert m["bwc_cpu_s"] is None and m["sqrt_cpu_s"] is None


def test_conjuntos_dev_e_teste_com_prefixos_diferentes_repetem_numeros():
    dev, teste = mc.gerar([30], 3, prefixo="dev"), mc.gerar([30], 3, prefixo="teste")
    assert dev == mc.gerar([30], 3, prefixo="dev")
    assert not ({x["n"] for x in dev} & {x["n"] for x in teste})
    assert mc.gerar([30], 3) == mc.gerar([30], 3, prefixo="gnfs-base")


def linha(d, i, t, classe, real):
    return {"digitos": d, "i": i, "tentativa": t, "classe": classe, "real_s": real}


def test_estatistica_perde_a_falha_da_primeira_tentativa_quando_a_segunda_passa():
    linhas = [linha(90, 0, 1, "bwc_nlucky0", 500.0), linha(90, 0, 2, "ok", 480.0), linha(90, 1, 1, "ok", 476.0)]
    s = mc.estatistica(linhas)[90]
    assert s["numeros"] == 2 and s["falhas_1a_tentativa"] == 1 and s["taxa_falha_1a_tentativa"] == 0.5
    assert s["sem_sucesso"] == 0
    assert s["custo_medio_s"] == 728.0  # (500 + 480 + 476) / 2: a tentativa perdida custa


def test_estatistica_esconde_numero_que_nunca_fechou():
    linhas = [linha(95, 0, t, "bwc_nlucky0", 900.0) for t in (1, 2, 3)]
    assert mc.estatistica(linhas)[95]["sem_sucesso"] == 1


def _cado_de_mentira(tmp_path):
    """Falha com `nlucky=0` na semente 1 e passa nas outras, como o bloco Wiedemann de verdade."""
    script = tmp_path / "cado-nfs.py"
    script.write_text(
        "import sys\n"
        "from pathlib import Path\n"
        "n = int(sys.argv[1])\n"
        "seed = [a for a in sys.argv if a.startswith('tasks.linalg.bwc.seed=')][0].split('=')[1]\n"
        "pasta = Path(sys.argv[sys.argv.index('--workdir') + 1]); pasta.mkdir(parents=True)\n"
        "(pasta / 'c2.poly').write_text('poly ' + seed)\n"
        f"if seed == '1':\n    sys.stderr.write({LOG_FALHA!r}); sys.exit(1)\n"
        "p = next(k for k in range(2, n) if n % k == 0)\n"
        "print(p, n // p)\n", encoding="utf-8")
    return script


def test_nlucky0_na_primeira_tentativa_some_do_registro_quando_a_segunda_passa(tmp_path):
    registro, trabalho = tmp_path / "r.jsonl", tmp_path / "trab"
    mc.medir([ITEM], registro, _cado_de_mentira(tmp_path), trabalho, threads=1)
    t1, t2 = mc.ler_registro(registro)
    assert (t1["tentativa"], t1["classe"], t1["semente_bwc"]) == (1, "bwc_nlucky0", 1)
    assert (t2["tentativa"], t2["classe"], t2["semente_bwc"]) == (2, "ok", 2)
    assert (trabalho / t1["pasta"]).is_dir() and t2["pasta"] is None  # a que falhou fica para auditoria
    assert t1["sha256_log"] == mc.sha256_arquivo(trabalho / "logs" / t1["log"])
    assert t1["sha256_poly"] and t1["sha256_poly"] != t2["sha256_poly"]
    assert mc.estatistica([t1, t2])[2]["falhas_1a_tentativa"] == 1


def test_lote_retomado_nao_roda_de_novo_o_que_ja_fechou(tmp_path):
    registro = tmp_path / "r.jsonl"
    chamadas = []

    def falso(cado, item, tentativa, trabalho, threads):
        chamadas.append(tentativa)
        return {"digitos": 2, "i": 0, "tentativa": tentativa, "classe": "ok", "real_s": 1.0}

    for _ in range(2):
        mc.medir([ITEM], registro, "x", tmp_path, rodar=falso)
    assert chamadas == [1]
    assert len(registro.read_text().splitlines()) == 1


def test_registro_so_tem_json_valido_por_linha(tmp_path):
    registro = tmp_path / "r.jsonl"
    mc.medir([ITEM], registro, _cado_de_mentira(tmp_path), tmp_path / "trab", threads=1)
    for texto in registro.read_text().splitlines():
        assert json.loads(texto)["digitos"] == 2
