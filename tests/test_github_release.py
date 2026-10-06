"""Release do GitHub nasce junto com o DOI (v0.8.0 e v0.9.0 ficaram sem página de release)."""
import json
import subprocess

import pytest

import github_release as gr
import zenodo_newversion as zn
from conftest import RAIZ
from test_publish import TOKEN, ZenodoFalso, _args

Z = json.loads((RAIZ / ".zenodo.json").read_text(encoding="utf-8"))
DOI = "10.5281/zenodo.23178159"


class GhFalso:
    def __init__(self, codigo=0):
        self.chamadas = []
        self.codigo = codigo

    def __call__(self, cmd, input, text, capture_output):
        self.chamadas.append((cmd, input))
        return subprocess.CompletedProcess(cmd, self.codigo, stdout="https://github.com/x/releases/tag/v",
                                           stderr="tag não existe")


def _proibido(*a, **k):
    raise AssertionError("seco não pode chamar o gh")


def test_notas_da_release_perdem_a_novidade_da_versao_a_frase_do_ledger_ou_os_dois_dois():
    tag, titulo, notas = gr.montar(Z, DOI)
    assert tag == f"v{Z['version']}" and titulo == tag
    assert gr.novidades(Z["description"], Z["version"]) in notas
    assert gr.FRASE_LEDGER in notas
    assert f"https://doi.org/{DOI}" in notas and f"https://doi.org/{gr.DOI_CONCEITO}" in notas
    assert "<" not in notas  # HTML da descrição do Zenodo não vaza para o markdown


def test_novidade_da_versao_atual_engole_o_trecho_de_uma_versao_anterior():
    desc = "Base. New in version 1.0.0: velho. New in version 1.1.0: novo de verdade."
    assert gr.novidades(desc, "1.1.0") == "novo de verdade."
    assert gr.novidades(desc, "1.0.0") == "velho."


def test_descricao_sem_novidade_da_versao_cria_release_vazia_em_silencio():
    with pytest.raises(gr.ErroRelease, match="New in version 9.9.9"):
        gr.montar({**Z, "version": "9.9.9"}, DOI)


def test_doi_conceito_ou_lixo_no_lugar_do_doi_da_versao_passa():
    with pytest.raises(gr.ErroRelease):
        gr.montar(Z, "")
    with pytest.raises(gr.ErroRelease):
        gr.montar(Z, "doi.org/10.5281/zenodo.1")


def test_seco_chama_o_gh_e_cria_release_sem_pedir(capsys):
    assert gr.main(["--zenodo-json", str(RAIZ / ".zenodo.json"), "--doi", DOI], rodar=_proibido) == 0
    assert "SECO" in capsys.readouterr().out


def test_criar_nao_marca_latest_nem_exige_a_tag_ja_enviada():
    gh = GhFalso()
    assert gr.main(["--zenodo-json", str(RAIZ / ".zenodo.json"), "--doi", DOI, "--criar"], rodar=gh) == 0
    cmd, entrada = gh.chamadas[0]
    assert cmd[:4] == ["gh", "release", "create", f"v{Z['version']}"]
    assert "--latest" in cmd and "--verify-tag" in cmd
    assert gr.FRASE_LEDGER in entrada


def test_publicar_no_zenodo_com_release_github_esquece_de_criar_a_release_com_o_doi_cunhado(capsys):
    gh = GhFalso()
    assert zn.main(_args("--publicar", "--release-github"), abrir=ZenodoFalso(),
                   ambiente={"ZENODO_TOKEN": TOKEN}, rodar=gh) == 0
    assert len(gh.chamadas) == 1
    assert "https://doi.org/10.5281/zenodo.1 " in gh.chamadas[0][1]  # DOI devolvido pelo publish
    assert gh.chamadas[0][0][-1].endswith("main.pdf")
    out = capsys.readouterr()
    assert TOKEN not in out.out + out.err


def test_publicar_sem_release_github_chama_o_gh_mesmo_assim():
    assert zn.main(_args("--publicar"), abrir=ZenodoFalso(), ambiente={"ZENODO_TOKEN": TOKEN},
                   rodar=_proibido) == 0


def test_gh_falhando_depois_do_zenodo_publicado_sai_como_sucesso(capsys):
    assert zn.main(_args("--publicar", "--release-github"), abrir=ZenodoFalso(),
                   ambiente={"ZENODO_TOKEN": TOKEN}, rodar=GhFalso(codigo=1)) == 3
    err = capsys.readouterr().err
    assert "Zenodo já publicado" in err and TOKEN not in err
