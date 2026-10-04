#!/usr/bin/env python3
"""Gera `tools/fatoracao/numeros.json` a partir do texto cru da Wikipedia (artigo "RSA numbers").

    curl -A "<seu-agente>" "https://en.wikipedia.org/w/index.php?title=RSA_numbers&action=raw" -o wiki.txt
    python3 tools/fatoracao/importar_rsa.py wiki.txt [--segunda lista.txt]

Por que existe: número digitado à mão erra, e um dígito errado no meio de 270 passa por qualquer
conferência de tamanho. Aqui o número sai do texto por regra, e cada um se prova de um jeito:

* **fatorado** (RSA-100, RSA-260): `p * q == N` é identidade exata; se o texto tiver um dígito errado em
  qualquer dos três, o script recusa.
* **aberto** (RSA-270): não há identidade para conferir, então é preciso uma SEGUNDA cópia independente
  (`--segunda`, a lista do desafio com checksum) e a comparação é dígito a dígito. Sem ela, recusa.
"""
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

NUMEROS = {"rsa-100": "RSA-100", "rsa-260": "RSA-260", "rsa-270": "RSA-270"}
SAIDA = Path(__file__).with_name("numeros.json")
DIGITOS = r"(\d[\d\s]*)"  # uma classe só: (\s*\d+)+ aninhado explode em backtracking exponencial


def so_digitos(texto):
    return int(re.sub(r"\s+", "", texto))


def secao(texto, nome):
    i = texto.index(f"=== {nome} ===")
    j = texto.find("\n===", i + 10)
    return texto[i:j if j >= 0 else len(texto)]


def extrair(texto, nome):
    """(N, p, q, digitos, bits) da seção `nome`; p e q são None quando o número está aberto."""
    sec = secao(texto, nome)
    cab = re.search(r"has (\d+) decimal digits \((\d+) bits\)", sec)
    valor = re.search(rf"{nome} = {DIGITOS}", sec)
    if not (cab and valor):
        raise ValueError(f"{nome}: não achei o cabeçalho ou o valor no texto")
    n = so_digitos(valor.group(1))
    fat = re.search(rf"{nome} = {DIGITOS}\s*×\s*{DIGITOS}", sec)
    p = q = None
    if fat:
        p, q = so_digitos(fat.group(1)), so_digitos(fat.group(2))
        if p * q != n:
            raise ValueError(f"{nome}: p*q != N, o texto está errado em algum dígito")
    return n, p, q, int(cab.group(1)), int(cab.group(2))


def da_segunda_fonte(texto, nome):
    m = re.search(rf"{nome} = (\d+) \((\d+) digits, checksum = (\d+)\)", texto)
    if not m:
        raise ValueError(f"{nome}: ausente na segunda fonte")
    return int(m.group(1)), int(m.group(3))


def montar(wiki, segunda=None):
    out = {}
    for ident, nome in NUMEROS.items():
        n, p, q, dig, bits = extrair(wiki, nome)
        if len(str(n)) != dig or n.bit_length() != bits:
            raise ValueError(f"{nome}: tamanho não bate com o cabeçalho ({len(str(n))} dígitos, {n.bit_length()} bits)")
        reg = {"decimal": str(n), "digitos": dig, "bits": bits, "sha256": hashlib.sha256(str(n).encode()).hexdigest(),
               "semiprimo_declarado": True}
        if p:
            reg.update(estado="fatorado", fatores=[str(min(p, q)), str(max(p, q))],
                       conferencia="p*q == N (identidade exata)")
        else:
            if segunda is None:
                raise ValueError(f"{nome}: aberto, exige --segunda para a conferência dígito a dígito")
            n2, checksum = da_segunda_fonte(segunda, nome)
            if n2 != n:
                raise ValueError(f"{nome}: as duas fontes divergem")
            reg.update(estado="aberto", checksum_rsa_labs=checksum,
                       conferencia="idêntico dígito a dígito em duas fontes independentes")
        out[ident] = reg
    return {"formato": "numeros-fatoracao/v1", "numeros": out}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("wikitext")
    ap.add_argument("--segunda")
    ap.add_argument("--saida", default=str(SAIDA))
    a = ap.parse_args(argv)
    segunda = Path(a.segunda).read_text(encoding="utf-8", errors="replace") if a.segunda else None
    dados = montar(Path(a.wikitext).read_text(encoding="utf-8"), segunda)
    Path(a.saida).write_text(json.dumps(dados, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("ok", a.saida, {k: v["estado"] for k, v in dados["numeros"].items()})


if __name__ == "__main__":
    try:
        main()
    except ValueError as e:
        sys.exit(f"RECUSADO: {e}")
