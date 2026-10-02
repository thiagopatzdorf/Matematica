#!/usr/bin/env python3
"""Verificador simples de cobertura: o código cobre Z_q^n com raio R?

Padrão do record_loop enquanto o tools/verify (agente B) não chega. Método:
dilatação no grafo de Hamming. Parte do conjunto dos códigos, e a cada passo
marca tudo que está a distância 1 do que já está marcado (soma de s mod q em
uma coordenada). Depois de R passos, o código cobre se e só se tudo está
marcado. Com numpy é um vetor booleano de q^n posições; sem numpy, cai num
laço puro em Python (só para espaços pequenos).

Formato do arquivo: uma palavra por linha; dígitos colados quando q <= 10
("0123"), ou inteiros separados por espaço/vírgula. Linhas vazias e
comentários (#) são ignorados.

Saída: uma linha JSON {"ok", "q", "n", "R", "M", "distintas", "descobertas"} e
código de saída 0 só quando cobre, sem palavra repetida e sem símbolo fora
de Z_q.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def ler_codigo(caminho: Path, q: int, n: int) -> list[tuple[int, ...]]:
    palavras = []
    for nl, linha in enumerate(caminho.read_text().splitlines(), 1):
        s = linha.split("#", 1)[0].strip()
        if not s:
            continue
        if any(c in s for c in " ,\t"):
            w = tuple(int(x) for x in s.replace(",", " ").split())
        else:
            w = tuple(int(c) for c in s)
        if len(w) != n:
            raise ValueError(f"linha {nl}: comprimento {len(w)} != n={n}")
        if any(not 0 <= x < q for x in w):
            raise ValueError(f"linha {nl}: símbolo fora de Z_{q}")
        palavras.append(w)
    return palavras


def indice(w: tuple[int, ...], q: int) -> int:
    i = 0
    for x in w:
        i = i * q + x
    return i


def descobertas_numpy(palavras, q: int, n: int, R: int) -> int:
    import numpy as np

    marc = np.zeros((q,) * n, dtype=bool)
    for w in palavras:
        marc[w] = True
    for _ in range(R):
        novo = marc.copy()
        for eixo in range(n):
            for s in range(1, q):
                novo |= np.roll(marc, s, axis=eixo)
        marc = novo
    return int(marc.size - np.count_nonzero(marc))


def descobertas_puro(palavras, q: int, n: int, R: int) -> int:
    total = q**n
    pot = [q ** (n - 1 - j) for j in range(n)]
    marc = bytearray(total)
    fronteira = []
    for w in palavras:
        i = indice(w, q)
        if not marc[i]:
            marc[i] = 1
            fronteira.append(i)
    for _ in range(R):
        prox = []
        for i in fronteira:
            for j in range(n):
                d = (i // pot[j]) % q
                base = i - d * pot[j]
                for s in range(q):
                    k = base + s * pot[j]
                    if not marc[k]:
                        marc[k] = 1
                        prox.append(k)
        fronteira = prox
    return total - sum(marc)


def verificar(caminho: Path, q: int, n: int, R: int, puro: bool = False) -> dict:
    palavras = ler_codigo(caminho, q, n)
    distintas = len(set(palavras))
    if puro:
        desc = descobertas_puro(palavras, q, n, R)
    else:
        try:
            desc = descobertas_numpy(palavras, q, n, R)
        except ImportError:
            desc = descobertas_puro(palavras, q, n, R)
    return {"ok": desc == 0 and distintas == len(palavras), "q": q, "n": n, "R": R,
            "M": len(palavras), "distintas": distintas, "descobertas": desc}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Confere se um código cobre Z_q^n com raio R.")
    ap.add_argument("arquivo", type=Path)
    ap.add_argument("q", type=int)
    ap.add_argument("n", type=int)
    ap.add_argument("R", type=int)
    ap.add_argument("--puro", action="store_true", help="sem numpy")
    a = ap.parse_args(argv)
    try:
        r = verificar(a.arquivo, a.q, a.n, a.R, a.puro)
    except (OSError, ValueError) as e:
        print(json.dumps({"ok": False, "erro": str(e)}, ensure_ascii=False))
        return 2
    print(json.dumps(r))
    return 0 if r["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
