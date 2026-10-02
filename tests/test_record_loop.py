"""Esqueleto do loop: seco não toca nada; executar registra K_2(4,1) de ponta a ponta."""
import json

import record_loop
import verify_cover
from conftest import RAIZ


def _args(ldir, tmp_path, *extra):
    return ["--celula", "K2(4,1)", "--ledger-dir", str(ldir), "--codes-dir", str(tmp_path / "codes"),
            "--certs-dir", str(tmp_path / "certs"), "--runs-dir", str(tmp_path / "runs"),
            "--agente", "pytest", *extra]


def _foto(ldir):
    return {p.name: p.read_bytes() for p in ldir.iterdir()}


def test_seco_e_o_padrao_e_nao_roda_nem_escreve_nada(ledger_recortado, tmp_path, capsys):
    antes = _foto(ledger_recortado)
    assert record_loop.main(_args(ledger_recortado, tmp_path)) == 0
    assert _foto(ledger_recortado) == antes
    assert not (tmp_path / "runs").exists() and not (tmp_path / "certs").exists()
    assert "SECO" in capsys.readouterr().out


def test_executar_em_k2_4_1_registra_no_ledger_e_prepara_a_pasta_do_certificado(ledger_recortado, tmp_path):
    assert record_loop.main(_args(ledger_recortado, tmp_path, "--executar", "--seed", "7")) == 0
    ours = json.loads((ledger_recortado / "ours.json").read_text())
    comp = ours["cells"]["2,4,1"]["ours_computational"]
    assert comp["M"] == 4
    cel = next(c for c in json.loads((ledger_recortado / "cells.json").read_text())["cells"] if c["id"] == "K2(4,1)")
    assert cel["status"] == "ours_computational" and cel["best"]["beats_published"] is False
    # proveniência com os seis campos preenchidos
    reg = json.loads((ledger_recortado / "provenance.json").read_text())["registros"][comp["provenance"]]
    for campo in ("gerador", "commit", "seed", "comando", "data", "agente"):
        assert reg[campo] not in (None, ""), campo
    assert reg["seed"] == 7 and reg["agente"] == "pytest"
    # pasta do certificado para o agente A
    cert = tmp_path / "certs" / "K2_4_1_M4"
    meta = json.loads((cert / "CERT.json").read_text())
    assert meta["declaracao_prevista"] == "CoveringKernel.K2_4_1_le_4_kernel"
    assert meta["estado"] == "aguardando_lean" and meta["sha256"] == comp["sha256"]
    assert (cert / "code.txt").read_text() == (tmp_path / "codes" / "q2_n4_R1_M4.txt").read_text()
    # a tentativa ficou no log
    runs = [json.loads(x) for x in (ledger_recortado / "runs.jsonl").read_text().splitlines()]
    assert runs[-1]["ok"] is True and runs[-1]["melhora_nosso"] is True


def test_segunda_rodada_igual_nao_reescreve_o_nosso_estado(ledger_recortado, tmp_path):
    record_loop.main(_args(ledger_recortado, tmp_path, "--executar"))
    ours1 = (ledger_recortado / "ours.json").read_bytes()
    assert record_loop.main(_args(ledger_recortado, tmp_path, "--executar")) == 0
    assert (ledger_recortado / "ours.json").read_bytes() == ours1
    runs = (ledger_recortado / "runs.jsonl").read_text().splitlines()
    assert len(runs) == 2 and json.loads(runs[-1])["melhora_nosso"] is False


def test_verificador_que_reprova_nao_toca_o_nosso_estado(ledger_recortado, tmp_path):
    ours = (ledger_recortado / "ours.json").read_bytes()
    reprova = "python3 -c 'import sys; sys.exit(1)'"
    rc = record_loop.main(_args(ledger_recortado, tmp_path, "--executar", "--verificador", reprova))
    assert rc == 4
    assert (ledger_recortado / "ours.json").read_bytes() == ours
    assert not (tmp_path / "certs").exists()
    assert json.loads((ledger_recortado / "runs.jsonl").read_text().splitlines()[-1])["etapa"] == "verificador"


def test_gerador_externo_configuravel_e_aceito(ledger_recortado, tmp_path):
    # gerador "de fora": escreve um código fixo de 4 palavras que cobre K_2(4,1)
    fixo = tmp_path / "fixo.txt"
    fixo.write_text("0000\n0111\n1000\n1111\n")
    ger = f"cp {fixo} {{saida}}"
    assert record_loop.main(_args(ledger_recortado, tmp_path, "--executar", "--gerador", ger)) == 0
    ours = json.loads((ledger_recortado / "ours.json").read_text())
    assert ours["cells"]["2,4,1"]["ours_computational"]["M"] == 4


def test_verificador_padrao_acusa_palavra_descoberta_nos_dois_modos(tmp_path):
    p = tmp_path / "c.txt"
    p.write_text("0000\n1111\n0011\n")  # 3 palavras não cobrem 16 com raio 1
    for puro in (False, True):
        r = verify_cover.verificar(p, 2, 4, 1, puro=puro)
        assert r["ok"] is False and r["descobertas"] > 0
    p.write_text("0000\n0111\n1000\n1111\n")
    assert verify_cover.verificar(p, 2, 4, 1)["ok"] is True
    assert verify_cover.verificar(p, 2, 4, 1, puro=True)["ok"] is True


def test_verificador_padrao_recusa_palavra_repetida(tmp_path):
    p = tmp_path / "c.txt"
    p.write_text("0000\n0111\n1000\n1111\n1111\n")
    assert verify_cover.main([str(p), "2", "4", "1"]) == 1


def test_verificador_padrao_confere_k5_7_2_le_500_do_repositorio():
    r = verify_cover.verificar(RAIZ / "data" / "codes" / "q5_n7_R2_M500.txt", 5, 7, 2)
    assert r == {"ok": True, "q": 5, "n": 7, "R": 2, "M": 500, "distintas": 500, "descobertas": 0}
