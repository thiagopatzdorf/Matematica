"""O conteúdo da página em três línguas não pode divergir nos fatos.

As versões pt/en/fr de site/matematica/conteudo.*.json são recriadas (não traduzidas palavra por
palavra), e é exatamente aí que um número escorrega: um "487" vira "478" numa língua só. Este teste
confere, campo a campo, que as três têm a mesma estrutura e os mesmos números, que conteudo.json é
a cópia do pt (o front-end lê esse nome) e que a frase oficial do ledger está nas três, em inglês.
"""
import json
import re
from collections import Counter
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
PASTA = RAIZ / "site" / "matematica"
LINGUAS = ("pt", "en", "fr")
FRASE = "A machine-checked ledger of covering-code upper bounds, with formally certified exact entries."
CHAVES = {"titulo", "subtitulo", "manifesto", "principios", "metodo", "milenio", "james", "keri",
          "lacunas", "links", "explicando", "glossario"}
# Separador de milhar (espaço, fino ou inseparável) antes de um grupo de três dígitos: "12 049" = 12049.
MILHAR = re.compile(r"(?<=\d)[   ](?=\d{3}(?!\d))")


def carregar(lingua: str) -> dict:
    return json.loads((PASTA / f"conteudo.{lingua}.json").read_text(encoding="utf-8"))


def numeros(texto: str) -> Counter:
    return Counter(re.findall(r"\d+", MILHAR.sub("", texto)))


def folhas(valor, caminho="$"):
    """Gera (caminho, texto) de cada string, para comparar as línguas campo a campo."""
    if isinstance(valor, dict):
        for k in sorted(valor):
            yield from folhas(valor[k], f"{caminho}.{k}")
    elif isinstance(valor, list):
        for i, v in enumerate(valor):
            yield from folhas(v, f"{caminho}[{i}]")
    else:
        yield caminho, str(valor)


def forma(valor):
    """A estrutura sem o texto: chaves dos dicionários e tamanho das listas."""
    if isinstance(valor, dict):
        return {k: forma(v) for k, v in valor.items()}
    if isinstance(valor, list):
        return [forma(v) for v in valor]
    return type(valor).__name__


def test_conteudo_json_diverge_da_versao_pt_que_o_front_end_espera():
    assert json.loads((PASTA / "conteudo.json").read_text(encoding="utf-8")) == carregar("pt")


@pytest.mark.parametrize("lingua", LINGUAS)
def test_versao_sem_alguma_secao_do_schema(lingua):
    d = carregar(lingua)
    assert set(d) == CHAVES
    assert len(d["milenio"]) == 7
    assert len(d["explicando"]["camadas"]) == 4
    for camada in d["explicando"]["camadas"]:
        assert set(camada) == {"nivel", "titulo", "texto", "analogia", "exemplo"}


@pytest.mark.parametrize("lingua", LINGUAS)
def test_frase_oficial_do_ledger_traduzida_ou_ausente(lingua):
    assert FRASE in carregar(lingua)["subtitulo"]


@pytest.mark.parametrize("lingua", ("en", "fr"))
def test_estrutura_difere_entre_linguas(lingua):
    assert forma(carregar(lingua)) == forma(carregar("pt"))


@pytest.mark.parametrize("lingua", ("en", "fr"))
def test_numero_diferente_entre_linguas_no_mesmo_campo(lingua):
    pt = dict(folhas(carregar("pt")))
    outra = dict(folhas(carregar(lingua)))
    diferentes = [f"{c}: pt {sorted(numeros(pt[c]).elements())} != {lingua} "
                  f"{sorted(numeros(outra[c]).elements())}"
                  for c in pt if numeros(pt[c]) != numeros(outra[c])]
    assert not diferentes, "\n".join(diferentes)


def test_total_de_celulas_citado_diverge_do_ledger():
    celulas = json.loads((RAIZ / "ledger" / "cells.json").read_text(encoding="utf-8"))["cells"]
    assert str(len(celulas)) in carregar("pt")["keri"]["resumo"]


def test_contagem_de_numeros_ignora_so_o_separador_de_milhar():
    assert numeros("12 049 e 37,8 e K₃(6,2) = 17") == Counter(["12049", "37", "8", "6", "2", "17"])
    assert numeros("37.8") == numeros("37,8")
    assert numeros("de 2 a 21") == Counter(["2", "21"])
