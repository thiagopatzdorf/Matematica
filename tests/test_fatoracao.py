"""Domínio fatoração de inteiros: registro de números, avaliador exato e importador."""
import hashlib
import json
import sys

import pytest

from conftest import RAIZ

sys.path.insert(0, str(RAIZ / "tools" / "fatoracao"))
import importar_rsa  # noqa: E402
import verificar  # noqa: E402

REG = verificar.registro()


def primos_ate(limite):
    crivo = bytearray([1]) * (limite + 1)
    crivo[0:2] = b"\x00\x00"
    for i in range(2, int(limite ** 0.5) + 1):
        if crivo[i]:
            crivo[i * i::i] = bytearray(len(crivo[i * i::i]))
    return [i for i, e in enumerate(crivo) if e]


@pytest.mark.parametrize("ident", sorted(REG))
def test_numero_do_registro_com_tamanho_ou_hash_que_nao_bate(ident):
    e = REG[ident]
    n = int(e["decimal"])
    assert len(e["decimal"]) == e["digitos"] and n.bit_length() == e["bits"]
    assert hashlib.sha256(e["decimal"].encode()).hexdigest() == e["sha256"]


@pytest.mark.parametrize("ident", [k for k, v in REG.items() if v["estado"] == "fatorado"])
def test_fatores_publicados_que_nao_multiplicam_no_numero(ident):
    p, q = map(int, REG[ident]["fatores"])
    assert p * q == int(REG[ident]["decimal"])


def test_rsa_270_com_fator_pequeno_indica_copia_corrompida():
    # um semiprimo de desafio não tem fator de 20 bits; se tiver, o dígito errado está no registro
    n = int(REG["rsa-270"]["decimal"])
    assert [p for p in primos_ate(1_000_000) if n % p == 0] == []


def test_avaliador_aceita_o_fator_real_de_um_numero_ja_fatorado():
    p, q = map(int, REG["rsa-260"]["fatores"])
    assert verificar.verificar("rsa-260", p)["veredito"] == "ok"
    assert verificar.verificar("rsa-260", q)["veredito"] == "ok"


@pytest.mark.parametrize("divisor,trecho", [(1, "trivial"), (3, "não divide"), (-7, "trivial"), (True, "inteiro"), ("12", "inteiro")])
def test_avaliador_aceita_divisor_que_nao_e_fator_do_rsa_270(divisor, trecho):
    r = verificar.verificar("rsa-270", divisor)
    assert r["veredito"] == "recusado" and trecho in r["motivo"]


def test_avaliador_aceita_o_proprio_numero_como_divisor():
    assert verificar.verificar("rsa-270", int(REG["rsa-270"]["decimal"]))["veredito"] == "recusado"


def test_avaliador_aceita_o_fator_mais_dois_de_um_numero_fatorado():
    p, _ = map(int, REG["rsa-260"]["fatores"])
    assert verificar.verificar("rsa-260", p + 2)["veredito"] == "recusado"


def test_avaliador_usa_registro_com_decimal_adulterado():
    adulterado = json.loads(json.dumps(REG))
    adulterado["rsa-270"]["decimal"] = adulterado["rsa-270"]["decimal"][:-1] + "9"
    r = verificar.verificar("rsa-270", 3, reg=adulterado)
    assert r["veredito"] == "recusado" and "corrompido" in r["motivo"]


def test_avaliador_com_numero_desconhecido():
    assert "desconhecido" in verificar.verificar("rsa-999", 3)["motivo"]


MINI = """=== RSA-999 ===
RSA-999 has 2 decimal digits (4 bits).

 RSA-999 = 15

 RSA-999 = 3
         × 5
"""


def test_importador_extrai_valor_e_fatores_do_formato_da_wikipedia():
    assert importar_rsa.extrair(MINI, "RSA-999") == (15, 3, 5, 2, 4)


def test_importador_aceita_texto_em_que_p_vezes_q_nao_e_n():
    with pytest.raises(ValueError, match="p\\*q != N"):
        importar_rsa.extrair(MINI.replace("× 5", "× 7"), "RSA-999")


def secao(nome, n, fatores=None):
    texto = f"=== {nome} ===\n{nome} has {len(str(n))} decimal digits ({n.bit_length()} bits).\n\n {nome} = {n}\n"
    if fatores:
        texto += f"\n {nome} = {fatores[0]}\n         × {fatores[1]}\n"
    return texto


# 15 = 3*5 e 21 = 3*7 fazem de RSA-100 e RSA-260; 91 faz de RSA-270, aberto (sem fatores no texto)
WIKI = secao("RSA-100", 15, (3, 5)) + secao("RSA-260", 21, (3, 7)) + secao("RSA-270", 91)


def test_importador_grava_numero_aberto_sem_segunda_fonte():
    with pytest.raises(ValueError, match="exige --segunda"):
        importar_rsa.montar(WIKI, None)


def test_importador_grava_numero_aberto_quando_as_fontes_divergem():
    with pytest.raises(ValueError, match="divergem"):
        importar_rsa.montar(WIKI, "RSA-270 = 93 (2 digits, checksum = 7)")


def test_importador_nao_marca_como_aberto_o_que_bate_nas_duas_fontes():
    dados = importar_rsa.montar(WIKI, "RSA-270 = 91 (2 digits, checksum = 7)")["numeros"]
    assert dados["rsa-270"]["estado"] == "aberto" and dados["rsa-270"]["checksum_rsa_labs"] == 7
    assert dados["rsa-260"]["estado"] == "fatorado" and dados["rsa-260"]["fatores"] == ["3", "7"]
