"""Publicação: Zenodo (sem rede, com HTTP falso) e página da Genesis."""
import io
from collections import Counter
import json
import re
import urllib.error

import pytest

import genesis_page
import zenodo_newversion as zn
from conftest import RAIZ

TOKEN = "tok-SEGREDO-de-teste-1234567890"


def _ledger_com(kernel: int, claimed: int, destino) -> str:
    """cells.json mínimo com `kernel` cotas FORMALIZED e `claimed` CLAIMED (o que o --publicar lê)."""
    cells = [{"certification": {"ub": {"state": "FORMALIZED" if i < kernel else "CLAIMED"}}}
             for i in range(kernel + claimed)]
    p = destino / "cells.json"
    p.write_text(json.dumps({"cells": cells}))
    return str(p)


def _contagem_do_paper():
    tex = (RAIZ / "paper" / "main.tex").read_text(encoding="utf-8").replace(r"\allowbreak ", "")
    k = int(re.search(r"\$(\d+)\$ of the \$\d+\$ upper bounds", tex).group(1))
    c = int(re.search(r"The other \$(\d+)\$ upper bounds are only claimed", tex).group(1))
    return k, c


_LEDGER_DO_PAPER = None


def _args(*extra, ledger=None):
    # Por padrão, um ledger com exatamente a contagem do paper: os testes do fluxo de publicação não
    # dependem de a main estar entre lançamentos (aí o ledger real anda na frente do paper).
    global _LEDGER_DO_PAPER
    if ledger is None:
        if _LEDGER_DO_PAPER is None:
            import tempfile
            from pathlib import Path
            _LEDGER_DO_PAPER = _ledger_com(*_contagem_do_paper(), Path(tempfile.mkdtemp()))
        ledger = _LEDGER_DO_PAPER
    return ["--record", "23085770", "--pdf", str(RAIZ / "paper" / "main.pdf"),
            "--zenodo-json", str(RAIZ / ".zenodo.json"), "--data-publicacao", "2026-10-02",
            "--ledger", ledger, *extra]


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
    assert falso.chamadas[3][1].endswith("/covering-codes-lean-kernel-v0.9.1.pdf")
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


def test_publicar_com_paper_atras_do_ledger_passa(capsys, tmp_path):
    """O paper pode ficar atrás do ledger entre lançamentos, mas não no lançamento: com uma cota a mais
    no kernel do que o paper e o .zenodo.json dizem, --publicar recusa antes de abrir rede."""
    k, c = _contagem_do_paper()
    led = _ledger_com(k + 1, c - 1, tmp_path)
    assert zn.main(_args("--publicar", ledger=led), abrir=_rede_proibida, ambiente={"ZENODO_TOKEN": TOKEN}) == 2
    err = capsys.readouterr().err
    assert "contagem diverge do ledger" in err and f"{k + 1} no kernel" in err
    # O seco continua só mostrando o plano (não publica, não precisa da igualdade).
    assert zn.main(_args(ledger=led), abrir=_rede_proibida, ambiente={"ZENODO_TOKEN": TOKEN}) == 0


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


def test_pagina_genesis_mostra_as_quinze_cotas_lean_e_nenhuma_so_computacional(ledger_recortado, tmp_path):
    saida = tmp_path / "p.html"
    genesis_page.main(["--ledger", str(ledger_recortado / "cells.json"), "--doi", "10.5281/zenodo.23092580",
                       "--tag", "v0.8.0", "--data", "2026-10-04", "--saida", str(saida)])
    html = saida.read_text()
    status = Counter(c["status"] for c in json.loads((ledger_recortado / "cells.json").read_text())["cells"])
    # Uma linha por célula nossa: as 15 da v0.9.1 (K7(4,2) é uma linha só: ≤ 19 na v0.7 e = 19 na v0.8)
    # e as que os códigos dos artigos (data/literatura/) trouxeram, Lean ou só computacionais.
    assert status["ours_lean"] >= 15
    assert html.count('<span class="ok">Lean kernel</span>:') == status["ours_lean"]
    assert html.count('<span class="cp">computer only</span> (not yet a Lean theorem)') == status["ours_computational"]
    # K7(6,4) <= 14 virou teorema do kernel (v0.9, PR #76): não pode mais aparecer como só computacional.
    assert "q7_n6_R4_M14.txt</code> (computer only" not in html
    assert "q7_n6_R4_M14.txt" in html
    # K7(5,3) <= 17: igual à publicada, com código nosso e teorema do kernel publicado na v0.9.1.
    assert "q7_n5_R3_M17.txt" in html and "<code>CoveringK753.K_7_5_3_le_17</code> (v0.9.1)" in html
    for decl in ("Syn.K7_9_4_le_1134_syn", "Syn.K7_8_3_le_1887_syn", "SC.K_2_6_1_eq12", "CoveringKernel.K5_9_5_le_50_kernel",
                 "Syn.K5_10_5_le_162_syn", "Syn.K5_11_4_le_2875_syn", "Syn.K7_10_4_le_5607_syn", "K742.K_7_4_2_le_19",
                 "K742.K_7_4_2_eq_19", "CoveringK764.K_7_6_4_le_14", "CoveringK753.K_7_5_3_le_17"):
        assert decl in html
    assert "<b>≤ 1134</b>" in html and "<b>≤ 1887</b>" in html and "<b>≤ 5607</b>" in html
    assert "<b>= 19</b>" in html and "<b>≤ 19</b>" not in html  # K_7(4,2) = 19 inteiro no kernel (v0.8)
    assert 'name="citation_doi" content="10.5281/zenodo.23092580"' in html
    assert "1475 <span" in html  # a melhor superior publicada que batemos em K7(9,4)
    assert "the origin of the 322 greedily added words was not recorded" in html


def test_pagina_genesis_escapa_texto_vindo_do_zenodo_json():
    led = {"meta": {"fontes": {}}, "cells": []}
    zen = {"title": "<script>x</script>", "description": "a & b", "creators": [{"name": "N"}], "version": "1"}
    html = genesis_page.gerar(led, zen, {"registros": {}}, "10.1/x", None, "v1", "2026-10-02")
    assert "<script>x</script>" not in html and "&lt;script&gt;" in html


def _paper_sem_quebras():
    """main.tex com \\allowbreak removido, para casar nomes de declaração do Lean."""
    return (RAIZ / "paper" / "main.tex").read_text(encoding="utf-8").replace(r"\allowbreak ", "")


def test_contagem_do_paper_e_do_zenodo_diverge_do_ledger():
    # Na v0.9.0 o paper dizia "the other 659 upper bounds are only claimed" com 658 CLAIMED no
    # ledger: a contagem escrita à mão tem de fechar com o total, no paper e no .zenodo.json.
    # O paper descreve a versão lançada e o ledger da main anda na frente entre lançamentos (códigos
    # novos sobem de estado antes da próxima release): o paper pode ficar atrás, nunca afirmar mais
    # teoremas do kernel do que o ledger tem, e o paper e o .zenodo.json dizem o mesmo número.
    from collections import Counter
    cells = json.loads((RAIZ / "ledger" / "cells.json").read_text(encoding="utf-8"))["cells"]
    ub = Counter(c["certification"]["ub"]["state"] for c in cells)
    kernel = ub["FORMALIZED"] + ub["INDEPENDENTLY_REPRODUCED"]
    tex = _paper_sem_quebras()
    total = len(cells)
    ditos = re.findall(r"\$(\d+)\$ of the \$(\d+)\$ upper bounds", tex)
    assert len(ditos) == 2 and len(set(ditos)) == 1, ditos  # resumo e seção do ledger, iguais
    k_paper, t_paper = (int(x) for x in ditos[0])
    assert t_paper == total and k_paper <= kernel
    claimed_paper = int(re.search(r"The other \$(\d+)\$ upper bounds are only claimed", tex).group(1))
    assert k_paper + claimed_paper == total
    z = json.loads((RAIZ / ".zenodo.json").read_text(encoding="utf-8"))
    assert f"{k_paper} of the {total} upper bounds are theorems of the Lean kernel" in z["description"]


def test_paper_com_versao_diferente_do_zenodo_ou_sem_a_frase_do_ledger():
    tex = _paper_sem_quebras()
    versao = json.loads((RAIZ / ".zenodo.json").read_text(encoding="utf-8"))["version"]
    assert f"(version~{versao})}}" in tex
    assert "tag \\texttt{v" + versao + "}" in tex
    assert "A machine-checked ledger of covering-code upper bounds, with formally certified exact entries." in tex
    assert not re.search(r"whole table (is|was|has been) (formally )?verified", tex)


def test_cota_superior_nossa_no_lean_some_do_paper():
    # As cotas superiores nossas da seção da fibra, K7(6,4) <= 14 e K7(5,3) <= 17, têm de estar no paper
    # como teorema do kernel (seção da fibra e lista do #print axioms), não mais como cota só citada.
    tex = _paper_sem_quebras()
    for decl in ("CoveringK764.K\\_7\\_6\\_4\\_le\\_14", "CoveringK753.K\\_7\\_5\\_3\\_le\\_17"):
        assert tex.count(decl) >= 2, decl  # na seção da fibra e na lista do #print axioms
    assert "is the announced bound of~\\cite{keri}" not in tex
