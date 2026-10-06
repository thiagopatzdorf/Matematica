"""Guardas da identidade visual em docs/assets/ (geradas por docs/assets/gerar_identidade.py).

Sem rede e sem dependência: só lê os arquivos já gerados e confere o contrato que o README e a página usam.
"""

import struct
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

ASSETS = Path(__file__).resolve().parents[1] / "docs" / "assets"
SVGS = ["logo.svg", "colapso.svg", "escada-de-estados.svg", "cubo-cobertura.svg", "torres.svg", "quatro-causas.svg"]
NS = "{http://www.w3.org/2000/svg}"


@pytest.mark.parametrize("nome", SVGS)
def test_svg_sem_title_ou_desc_fica_mudo_para_leitor_de_tela(nome):
    raiz = ET.parse(ASSETS / nome).getroot()
    titulo, desc = raiz.find(f"{NS}title"), raiz.find(f"{NS}desc")
    assert titulo is not None and titulo.text and titulo.text.strip()
    assert desc is not None and desc.text and len(desc.text.strip()) > 20
    assert raiz.get("role") == "img"


@pytest.mark.parametrize("nome", SVGS)
def test_svg_acima_de_60_kb_pesa_no_readme(nome):
    assert (ASSETS / nome).stat().st_size < 60_000


@pytest.mark.parametrize("nome", SVGS)
def test_svg_nao_depende_de_webfont_nem_de_recurso_externo(nome):
    # SVG dentro de <img> no GitHub não carrega fonte nem imagem externa: o texto precisa ser contorno
    texto = (ASSETS / nome).read_text(encoding="utf-8")
    assert "<text" not in texto
    assert "@font-face" not in texto and "http://" not in texto.replace("http://www.w3.org/2000/svg", "")
    assert "https://" not in texto


def _png(nome):
    dados = (ASSETS / nome).read_bytes()
    assert dados[:8] == b"\x89PNG\r\n\x1a\n"
    return struct.unpack(">II", dados[16:24]), len(dados)


@pytest.mark.parametrize("nome", ["banner-claro.png", "banner-escuro.png"])
def test_banner_fora_da_proporcao_1280x400_quebra_o_hero_do_readme(nome):
    (largura, altura), tamanho = _png(nome)
    assert largura * 400 == altura * 1280 and largura >= 1280  # 2x para tela de alta densidade
    assert tamanho < 1_000_000


@pytest.mark.parametrize("nome", ["filosofia-claro.png", "filosofia-escuro.png"])
def test_hero_da_filosofia_fora_da_proporcao_4x1_quebra_o_topo_das_paginas(nome):
    (largura, altura), tamanho = _png(nome)
    assert largura == 4 * altura and largura >= 2560  # 2x de 1280x320
    assert tamanho < 1_000_000


def test_social_preview_fora_do_formato_do_github_e_recortado():
    (largura, altura), tamanho = _png("social-preview.png")
    assert (largura, altura) == (1280, 640)
    assert tamanho < 1_000_000


def test_escada_com_estado_que_o_build_nao_conhece_mente_sobre_o_ledger():
    import sys

    sys.path.insert(0, str(ASSETS.parents[1] / "ledger"))
    import build

    texto = (ASSETS / "escada-de-estados.svg").read_text(encoding="utf-8")
    desc = ET.fromstring(texto).find(f"{NS}desc").text
    posicoes = [desc.index(f" {e}:") for e in build.ESTADOS]
    assert posicoes == sorted(posicoes), "a escada precisa seguir a ordem de ledger/build.py"
