"""Formato estruturado de código de cobertura (covering-code/v1): leitura, expansão e utilitários.

Só biblioteca padrão. A especificação está em docs/code-format.md; este módulo é a referência
executável dela. Convenção de dígitos (a mesma dos C1_Data_*.lean):

    palavra como texto  s = s[0] s[1] ... s[n-1]   (um caractere '0'..'9' por coordenada)
    palavra como inteiro w = sum_k s[k] * q^k        (little-endian: dígito k = (w // q^k) % q)

Forma canônica de um código: as palavras como texto, ordenadas por byte (para comprimento fixo é
o mesmo que ordenar pelo inteiro lido com s[0] como dígito MAIS significativo), unidas por LF e
com LF final. `canonical_sha256` é o sha256 desses bytes.
"""
from __future__ import annotations

import hashlib
import json

FORMAT = "covering-code/v1"


class FormatError(ValueError):
    """JSON ou lista de palavras que viola o formato (o defeito vem descrito na mensagem)."""


# --------------------------------------------------------------------------- palavras
def parse_word(s: str, q: int, n: int) -> tuple[int, ...]:
    if len(s) != n:
        raise FormatError(f"palavra {s!r}: comprimento {len(s)} != n={n}")
    if not s.isdigit():
        raise FormatError(f"palavra {s!r}: caractere que não é dígito")
    v = tuple(int(c) for c in s)
    if any(c >= q for c in v):
        raise FormatError(f"palavra {s!r}: dígito >= q={q}")
    return v


def word_str(v) -> str:
    return "".join(str(c) for c in v)


def word_int(v, q: int) -> int:
    return sum(c * q**k for k, c in enumerate(v))


def canonical_text(words) -> str:
    """words: iterável de strings. Erro se houver duplicata (código é conjunto)."""
    lst = sorted(words)
    for a, b in zip(lst, lst[1:]):
        if a == b:
            raise FormatError(f"palavra duplicada: {a}")
    return "".join(w + "\n" for w in lst)


def canonical_sha256(words) -> str:
    return hashlib.sha256(canonical_text(words).encode()).hexdigest()


def read_txt(path: str, q: int, n: int) -> list[str]:
    """Lê um .txt de data/codes (uma palavra por linha; linhas vazias ignoradas)."""
    out = []
    with open(path) as f:
        for line in f:
            s = line.strip()
            if s:
                parse_word(s, q, n)
                out.append(s)
    return out


def parse_cell_name(path: str) -> tuple[int, int, int, int]:
    """'.../q7_n9_R4_M1351.txt' -> (7, 9, 4, 1351)."""
    import os
    import re

    m = re.fullmatch(r"q(\d+)_n(\d+)_R(\d+)_M(\d+)\.(txt|json)", os.path.basename(path))
    if not m:
        raise FormatError(f"nome fora do padrão q<q>_n<n>_R<R>_M<M>: {path}")
    return tuple(int(m.group(i)) for i in range(1, 5))  # type: ignore[return-value]


# --------------------------------------------------------------------------- álgebra em Z_q^n
# Grupo aditivo do alfabeto. "Zq": soma mod q (para q primo, GF(q)). "xor": q = 2^m e o dígito é
# lido como vetor de m bits, soma = ou-exclusivo (a soma de GF(2^m); é o caso do K_4(10,4) <= 192).
GROUPS = ("Zq", "xor")


def add(a, b, q, group="Zq"):
    if group == "xor":
        return tuple(x ^ y for x, y in zip(a, b))
    return tuple((x + y) % q for x, y in zip(a, b))


def sub(a, b, q, group="Zq"):
    if group == "xor":
        return tuple(x ^ y for x, y in zip(a, b))
    return tuple((x - y) % q for x, y in zip(a, b))


def is_prime(q: int) -> bool:
    return q >= 2 and all(q % p for p in range(2, int(q**0.5) + 1))


def span(gens, q: int, n: int, group: str = "Zq") -> list[tuple[int, ...]]:
    """Subgrupo aditivo de Z_q^n gerado por gens (para q primo, o subespaço gerado).

    A ordem da lista é determinística (função só de gens); quem precisa de ordem canônica ordena.
    """
    zero = (0,) * n
    seen = {zero}
    out = [zero]
    for g in gens:
        base = list(out)  # subgrupo já gerado; base + <g> também é subgrupo
        m = tuple(g)
        while m != zero:
            for x in base:
                y = add(x, m, q, group)
                if y not in seen:
                    seen.add(y)
                    out.append(y)
            m = add(m, g, q, group)
    return out


def rref_right(rows, q: int, n: int):
    """Forma escalonada reduzida sobre GF(q) com pivôs escolhidos da DIREITA para a esquerda.

    Devolve (G, P): G com k linhas independentes, P = colunas-pivô em ordem crescente, e
    G[i][P[j]] = [i == j]. Pivôs à direita fazem a matriz de checagem sair na forma [I | A]
    sempre que as k últimas colunas são um conjunto de informação (o caso dos nossos códigos).
    """
    if not is_prime(q):
        raise FormatError(f"rref só sobre corpo primo; q={q}")
    M = [list(r) for r in rows]
    piv = []
    r = 0
    for c in range(n - 1, -1, -1):
        p = next((i for i in range(r, len(M)) if M[i][c] % q), None)
        if p is None:
            continue
        M[r], M[p] = M[p], M[r]
        inv = pow(M[r][c], q - 2, q)
        M[r] = [(x * inv) % q for x in M[r]]
        for i in range(len(M)):
            if i != r and M[i][c]:
                f = M[i][c]
                M[i] = [(x - f * y) % q for x, y in zip(M[i], M[r])]
        piv.append(c)
        r += 1
    G = M[:r]
    order = sorted(range(r), key=lambda i: piv[i])
    return [tuple(G[i]) for i in order], sorted(piv)


def parity_from_generator(G, P, q: int, n: int):
    """Matriz de checagem H com identidade nas colunas N = complemento de P (ordem crescente).

    Com x = u G: x_P = u e x_N = u G_N, logo H x = x_N - G_N^T x_P = 0.
    Linha i de H: H[i][N[i]] = 1, H[i][P[j]] = -G[j][N[i]], resto 0.
    """
    N = [c for c in range(n) if c not in P]
    H = []
    for i, c in enumerate(N):
        row = [0] * n
        row[c] = 1
        for j, pc in enumerate(P):
            row[pc] = (-G[j][c]) % q
        H.append(tuple(row))
    return H, N


def syndrome(H, x, q):
    return tuple(sum(h * v for h, v in zip(row, x)) % q for row in H)


# --------------------------------------------------------------------------- expansão
def _rows(field, q, n, what):
    try:
        return [parse_word(s, q, n) for s in field]
    except FormatError as e:
        raise FormatError(f"{what}: {e}") from None


def expand(doc: dict) -> list[str]:
    """JSON do formato -> lista de palavras (texto), na ordem canônica. Determinística.

    Confere tudo o que o formato promete: H G^T = 0, identidade de H nas colunas de checagem,
    blocos disjuntos (nenhuma palavra gerada duas vezes) e len == M. Erro -> FormatError.
    O sha256 NÃO é conferido aqui (ver check_doc), para expand servir também ao structure.py.
    """
    if doc.get("format") != FORMAT:
        raise FormatError(f"format != {FORMAT!r}")
    q, n, M = doc["q"], doc["n"], doc["M"]
    group = doc.get("group", "Zq")
    if group not in GROUPS:
        raise FormatError(f"group {group!r} desconhecido")
    if group == "xor" and q & (q - 1):
        raise FormatError("group xor exige q potência de 2")
    words: list[str] = []

    lb = doc.get("linear_base")
    if lb is not None:
        if not is_prime(q) or group != "Zq":
            raise FormatError("linear_base exige q primo e group Zq (senão use subcode_cosets)")
        G = _rows(lb["generator"], q, n, "linear_base.generator")
        H = _rows(lb["parity_check"], q, n, "linear_base.parity_check")
        N = lb["check_columns"]
        k = lb["k"]
        if len(G) != k or len(H) != n - k or len(N) != n - k:
            raise FormatError("linear_base: k, generator, parity_check e check_columns não batem")
        for h in H:
            for g in G:
                if sum(a * b for a, b in zip(h, g)) % q:
                    raise FormatError("linear_base: H G^T != 0")
        for i, row in enumerate(H):
            for c in N:
                if row[c] != (1 if c == N[i] else 0):
                    raise FormatError("linear_base: H não é identidade nas check_columns")
        code = span(G, q, n)
        if len(code) != q**k:
            raise FormatError("linear_base: geradores dependentes")
        reps = []
        for s in lb.get("coset_syndromes", []):
            sv = parse_word(s, q, n - k)
            r = [0] * n
            for i, c in enumerate(N):
                r[c] = sv[i]
            reps.append(tuple(r))
        reps += _rows(lb.get("coset_reps", []), q, n, "linear_base.coset_reps")
        for r in reps:
            words += [word_str(add(r, c, q)) for c in code]

    for j, blk in enumerate(doc.get("subcode_cosets", [])):
        gens = _rows(blk["generators"], q, n, f"subcode_cosets[{j}].generators")
        sub_code = span(gens, q, n, group)
        for r in _rows(blk["reps"], q, n, f"subcode_cosets[{j}].reps"):
            words += [word_str(add(r, c, q, group)) for c in sub_code]

    pw = doc.get("patch_words", [])
    _rows(pw, q, n, "patch_words")
    words += pw

    text = canonical_text(words)  # levanta FormatError em duplicata (blocos que se sobrepõem)
    out = text.split()
    if len(out) != M:
        raise FormatError(f"expansão tem {len(out)} palavras, M={M}")
    return out


def check_doc(doc: dict) -> list[str]:
    """expand + confere canonical_sha256. Devolve as palavras."""
    words = expand(doc)
    got = canonical_sha256(words)
    if got != doc.get("canonical_sha256"):
        raise FormatError(f"sha256 canônico {got} != declarado {doc.get('canonical_sha256')}")
    return words


def load(path: str) -> dict:
    with open(path) as f:
        return json.load(f)


def dump(doc: dict) -> str:
    """Serialização estável: chaves na ordem do documento, listas de palavras uma por linha."""
    return json.dumps(doc, indent=1, ensure_ascii=False) + "\n"


__all__ = [n for n in dir() if not n.startswith("_") and n != "annotations"]
