#!/usr/bin/env python3
"""Avaliador exato de fatoração: um divisor não trivial de um número do registro.

    python3 tools/fatoracao/verificar.py --numero rsa-270 --divisor 1234...          # ou @arquivo.txt
    python3 tools/fatoracao/verificar.py --lista

Decide só com aritmética inteira exata, sem juízo de ninguém: `1 < d < N` e `N % d == 0`. Código de saída 0
somente com veredito `ok`. O número vem de `numeros.json`, e o avaliador recusa se o registro não bater com o
próprio `sha256` (cópia corrompida vale menos que nenhuma).

O que isto NÃO prova: que `d` e `N/d` são primos. Para um semiprimo (como o desafio declara) isso decorre de
`d` ser divisor não trivial; mas "semiprimo" é afirmação do desafio, não provada aqui (`semiprimo_declarado`).
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

REGISTRO = Path(__file__).with_name("numeros.json")


def registro():
    return json.loads(REGISTRO.read_text(encoding="utf-8"))["numeros"]


def verificar(ident, divisor, reg=None):
    """Devolve `{veredito, motivo, ...}`; `divisor` é int. Nunca levanta por entrada ruim: recusa com motivo."""
    reg = registro() if reg is None else reg
    if ident not in reg:
        return {"veredito": "recusado", "motivo": f"número desconhecido: {ident}"}
    entrada = reg[ident]
    n = int(entrada["decimal"])
    if hashlib.sha256(entrada["decimal"].encode()).hexdigest() != entrada["sha256"]:
        return {"veredito": "recusado", "motivo": "registro corrompido: o decimal não bate com o sha256"}
    if not isinstance(divisor, int) or isinstance(divisor, bool):
        return {"veredito": "recusado", "motivo": "o divisor precisa ser um inteiro"}
    if not 1 < divisor < n:
        return {"veredito": "recusado", "motivo": "divisor trivial: exige 1 < d < N"}
    if n % divisor:
        return {"veredito": "recusado", "motivo": "d não divide N"}
    cofator = n // divisor
    return {"veredito": "ok", "motivo": "d divide N e 1 < d < N", "numero": ident, "digitos_d": len(str(divisor)),
            "digitos_cofator": len(str(cofator)), "sha256_d": hashlib.sha256(str(divisor).encode()).hexdigest(),
            "semiprimo_declarado": bool(entrada.get("semiprimo_declarado"))}


def ler_divisor(texto):
    bruto = Path(texto[1:]).read_text(encoding="utf-8") if texto.startswith("@") else texto
    return int("".join(bruto.split()))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--numero")
    ap.add_argument("--divisor", help="inteiro decimal, ou @arquivo com ele")
    ap.add_argument("--lista", action="store_true")
    a = ap.parse_args(argv)
    if a.lista:
        for k, v in registro().items():
            print(f"{k}: {v['digitos']} dígitos, {v['bits']} bits, {v['estado']}")
        return 0
    if not (a.numero and a.divisor):
        ap.error("informe --numero e --divisor (ou --lista)")
    try:
        d = ler_divisor(a.divisor)
    except (ValueError, OSError):
        print(json.dumps({"veredito": "recusado", "motivo": "o divisor não é um inteiro decimal legível"}, ensure_ascii=False))
        return 1
    r = verificar(a.numero, d)
    print(json.dumps(r, ensure_ascii=False, indent=2))
    return 0 if r["veredito"] == "ok" else 1


if __name__ == "__main__":
    sys.exit(main())
