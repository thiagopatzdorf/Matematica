"""As páginas de filosofia em três línguas não podem divergir na forma nem nos fatos.

docs/FILOSOFIA.md (pt), docs/PHILOSOPHY.md (en) e docs/PHILOSOPHIE.md (fr) são recriadas, não traduzidas
palavra por palavra: é aí que uma seção some numa língua só, uma imagem fica para trás ou um "487" vira
"478". Confere a mesma sequência de seções, as mesmas imagens (com hero claro/escuro), as mesmas notas
de rodapé, os mesmos números e a frase oficial do ledger, em inglês, nas três.
"""
import re
from collections import Counter
from pathlib import Path

import pytest

DOCS = Path(__file__).resolve().parents[1] / "docs"
PAGINAS = {"pt": "FILOSOFIA.md", "en": "PHILOSOPHY.md", "fr": "PHILOSOPHIE.md"}
FRASE = "A machine-checked ledger of covering-code upper bounds, with formally certified exact entries."


def ler(lingua: str) -> str:
    return (DOCS / PAGINAS[lingua]).read_text(encoding="utf-8")


def secoes(texto: str) -> list[str]:
    """Só o numeral romano de cada seção: o título muda de língua, a ordem não."""
    return re.findall(r"^## ([IVX]+)\. ", texto, re.M)


def imagens(texto: str) -> list[str]:
    return re.findall(r'(?:src|srcset)="([^"]+)"', texto)


def numeros(texto: str) -> Counter:
    sem_links = re.sub(r"\]\([^)]*\)|https?://\S+|\b[0-9a-f]{40}\b", "", texto)
    return Counter(re.findall(r"\d+", sem_links))


@pytest.mark.parametrize("lingua", PAGINAS)
def test_frase_oficial_do_ledger_traduzida_ou_ausente(lingua):
    assert FRASE in ler(lingua)


@pytest.mark.parametrize("lingua", PAGINAS)
def test_hero_sem_versao_clara_e_escura(lingua):
    texto = ler(lingua)
    assert '<source media="(prefers-color-scheme: dark)" srcset="assets/filosofia-escuro.png">' in texto
    assert '<source media="(prefers-color-scheme: light)" srcset="assets/filosofia-claro.png">' in texto
    for img in imagens(texto):
        assert (DOCS / img).exists(), img


@pytest.mark.parametrize("lingua", ("en", "fr"))
def test_secao_ou_imagem_faltando_numa_lingua(lingua):
    pt, outra = ler("pt"), ler(lingua)
    assert secoes(outra) == secoes(pt) == ["I", "II", "III", "IV", "V", "VI", "VII", "VIII"]
    assert imagens(outra) == imagens(pt)
    assert re.findall(r"^\[\^(\w+)\]:", outra, re.M) == re.findall(r"^\[\^(\w+)\]:", pt, re.M)


@pytest.mark.parametrize("lingua", ("en", "fr"))
def test_numero_diferente_entre_linguas(lingua):
    assert numeros(ler(lingua)) == numeros(ler("pt"))


def test_proposicao_de_cotas_formalizadas_atrasada_em_relacao_ao_ledger():
    """O #87 subiu o ledger de 487 para 488 e as três páginas ficaram para trás: o número sai de COBERTURA.md."""
    cobertura = (DOCS.parent / "ledger" / "COBERTURA.md").read_text(encoding="utf-8")
    colunas = re.search(r"^\| ub \| (\d+) \| (\d+) \| (\d+) \| (\d+) \| (\d+) \|", cobertura, re.M).groups()
    formalizadas = int(colunas[3]) + int(colunas[4])
    for lingua in PAGINAS:
        assert re.search(rf"\*\*{formalizadas} \S+ \S+ 1145 ", ler(lingua)), lingua
