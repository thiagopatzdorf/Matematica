"""Publicação: Zenodo (sem rede, com HTTP falso) e página da Genesis."""
import io
import json
import urllib.error

import pytest

import genesis_page
import zenodo_newversion as zn
from conftest import RAIZ

TOKEN = "tok-SEGREDO-de-teste-1234567890"


def _args(*extra):
    return ["--record", "23085770", "--pdf", str(RAIZ / "paper" / "main.pdf"),
            "--zenodo-json", str(RAIZ / ".zenodo.json"), "--data-publicacao", "2026-10-02", *extra]


class Resp:
    def __init__(self, status, corpo):
        self.status = status
        self._b = json.dumps(corpo).encode()

    def read(self):
        return self._b

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


class ZenodoFalso:
    def __init__(self, falhar_em=None):
        self.chamadas = []
        self.falhar_em = falhar_em

    def __call__(self, req, timeout):
        url = req.full_url
        self.chamadas.append((req.get_method(), url, req.headers.get("Authorization")))
        if self.falhar_em and self.falhar_em in url:
            # O corpo do erro ecoa o token: tem de ser redigido antes de ir para a tela.
            raise urllib.error.HTTPError(url, 403, "proibido", {}, io.BytesIO(f"token {TOKEN} inválido".encode()))
        base = zn.API["zenodo"]
        if url.endswith("/actions/newversion"):
            return Resp(201, {"links": {"latest_draft": f"{base}/999"}})
        if url == f"{base}/999" and req.get_method() == "GET":
            return Resp(200, {"id": 999, "files": [{"id": "f1"}], "links": {"bucket": "https://zenodo.org/api/files/b"}})
        if "/files/" in url and req.get_method() == "DELETE":
            return Resp(204, {})
        if url.startswith("https://zenodo.org/api/files/b/"):
            return Resp(201, {"checksum": "md5:abc"})
        if url == f"{base}/999" and req.get_method() == "PUT":
            return Resp(200, {})
        if url.endswith("/999/actions/publish"):
            return Resp(202, {"doi": "10.5281/zenodo.1", "conceptdoi": "10.5281/zenodo.23085769",
                              "links": {"record_html": "https://zenodo.org/records/1"}})
        raise AssertionError(f"chamada inesperada {req.get_method()} {url}")


def _rede_proibida(req, timeout):
    raise AssertionError("seco não pode abrir rede")


def test_seco_e_o_padrao_e_nao_abre_rede_nem_com_token(capsys):
    assert zn.main(_args(), abrir=_rede_proibida, ambiente={"ZENODO_TOKEN": TOKEN}) == 0
    out = capsys.readouterr().out
    assert "SECO" in out and TOKEN not in out
    assert f"presente, {len(TOKEN)} caracteres" in out


def test_publicar_faz_newversion_apaga_herdado_sobe_pdf_metadados_e_publica_nessa_ordem(capsys):
    falso = ZenodoFalso()
    assert zn.main(_args("--publicar"), abrir=falso, ambiente={"ZENODO_TOKEN": TOKEN}) == 0
    metodos = [(m, u.rsplit("/", 2)[-2:]) for m, u, _ in falso.chamadas]
    assert [m for m, _ in metodos] == ["POST", "GET", "DELETE", "PUT", "PUT", "POST"]
    assert falso.chamadas[0][1].endswith("/23085770/actions/newversion")
    assert falso.chamadas[3][1].endswith("/covering-codes-lean-kernel-v0.3.0.pdf")
    assert all(auth == f"Bearer {TOKEN}" for _, _, auth in falso.chamadas)
    out = capsys.readouterr()
    assert "PUBLICADO 10.5281/zenodo.1" in out.out
    assert TOKEN not in out.out + out.err


def test_erro_http_que_ecoa_o_token_sai_redigido(capsys):
    falso = ZenodoFalso(falhar_em="newversion")
    assert zn.main(_args("--publicar"), abrir=falso, ambiente={"ZENODO_TOKEN": TOKEN}) == 2
    out = capsys.readouterr()
    assert TOKEN not in out.out + out.err
    assert "***" in out.err and "HTTP 403" in out.err


def test_publicar_sem_token_falha_antes_de_qualquer_chamada(capsys):
    assert zn.main(_args("--publicar"), abrir=_rede_proibida, ambiente={}) == 2
    assert "ZENODO_TOKEN ausente" in capsys.readouterr().err


def test_zenodo_json_sem_campo_obrigatorio_e_recusado():
    with pytest.raises(zn.ErroZenodo, match="version"):
        zn.montar_metadados({"title": "t", "description": "d", "creators": [{}], "keywords": ["k"]}, "2026-10-02")


def test_descricao_ganha_paragrafo_html_e_data_vem_do_argumento():
    z = json.loads((RAIZ / ".zenodo.json").read_text())
    m = zn.montar_metadados(z, "2026-10-09")
    assert m["description"].startswith("<p>") and m["publication_date"] == "2026-10-09"
    assert m["related_identifiers"] == z["related_identifiers"]


def test_nenhum_segredo_no_codigo_de_publicacao():
    fonte = (RAIZ / "scripts" / "publish" / "zenodo_newversion.py").read_text()
    assert "vault" not in fonte and "get_secret" not in fonte
    assert 'environ.get("ZENODO_TOKEN"' in fonte or "ZENODO_TOKEN" in fonte


def test_pagina_genesis_mostra_as_nove_cotas_lean_e_as_duas_so_computacionais(ledger_recortado, tmp_path):
    saida = tmp_path / "p.html"
    genesis_page.main(["--ledger", str(ledger_recortado / "cells.json"), "--doi", "10.5281/zenodo.23092580",
                       "--tag", "v0.3.0", "--data", "2026-10-02", "--saida", str(saida)])
    html = saida.read_text()
    assert html.count('<span class="ok">Lean kernel</span>:') == 9
    assert html.count('<span class="cp">computer only</span> (not yet a Lean theorem)') == 2
    for decl in ("CoveringKernel.K7_9_4_le_1351_kernel", "SC.K_2_6_1_eq12", "CoveringKernel.K5_9_5_le_50_kernel"):
        assert decl in html
    assert "<b>≤ 1285</b>" in html and "<b>≤ 1887</b>" in html
    assert 'name="citation_doi" content="10.5281/zenodo.23092580"' in html
    assert "1475 <span" in html  # a melhor superior publicada que batemos em K7(9,4)
    assert "the origin of the 322 greedily added words was not recorded" in html


def test_pagina_genesis_escapa_texto_vindo_do_zenodo_json():
    led = {"meta": {"fontes": {}}, "cells": []}
    zen = {"title": "<script>x</script>", "description": "a & b", "creators": [{"name": "N"}], "version": "1"}
    html = genesis_page.gerar(led, zen, {"registros": {}}, "10.1/x", None, "v1", "2026-10-02")
    assert "<script>x</script>" not in html and "&lt;script&gt;" in html
