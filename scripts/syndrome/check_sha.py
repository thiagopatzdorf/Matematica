#!/usr/bin/env python3
"""Confere que a lista `Syn.L<tag>` de CoveringLean/SynData_<tag>.lean decodifica para o código
com o sha256 canônico esperado (palavras como strings w_0..w_{n-1}, ordenadas, uma por linha,
terminando em \\n).  É a ligação entre o teorema (sobre `codeOf q n L<tag>`) e o arquivo de dados.

Uso: check_sha.py TAG SHA256 [arquivo_do_codigo]
"""
import hashlib, re, sys

sys.set_int_max_str_digits(0)
tag, want = sys.argv[1], sys.argv[2]
src = open(f"CoveringLean/SynData_{tag}.lean").read()
q = int(re.search(r"\n  q := (\d+)", src).group(1))
n = int(re.search(r"\n  n := (\d+)", src).group(1))
L = [int(x) for x in re.search(rf"def L{tag} : List Nat := \[([^\]]*)\]", src).group(1).split(",")]
assert L == sorted(L) and len(set(L)) == len(L) and all(x < q**n for x in L)
words = sorted("".join(str((x // q**i) % q) for i in range(n)) for x in L)
canon = "".join(w + "\n" for w in words)
got = hashlib.sha256(canon.encode()).hexdigest()
print(f"{tag}: M={len(L)} sha256={got}")
assert got == want, "sha256 diferente"
assert want in src, "sha256 ausente do cabeçalho"
if len(sys.argv) > 3:
    file_words = sorted(l.strip() for l in open(sys.argv[3]) if l.strip())
    assert file_words == words, "lista difere do arquivo"
    print("  confere com", sys.argv[3])
