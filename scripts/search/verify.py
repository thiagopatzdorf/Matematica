#!/usr/bin/env python3
"""verify.py -- verificador independente de coberturas q-árias (numpy).

Uso: verify.py q n R arquivo.txt

Não reaproveita nada de base_search.c / patch_opt.c: lê as palavras (uma por linha,
dígitos 0..q-1), marca-as num tensor booleano de forma (q,)*n e faz R dilatações de
Hamming (cada dilatação = OU sobre todas as coordenadas e todos os deslocamentos não
nulos mod q, via np.roll). O código cobre se, ao fim, todo o espaço estiver marcado.
Também confere linhas mal formadas e duplicatas. Imprime o sha256 do arquivo canônico
(palavras ordenadas, uma por linha, terminando em \\n). Sai com 0 só se for válida.
"""
import hashlib
import sys

import numpy as np


def main():
    q, n, R = map(int, sys.argv[1:4])
    path = sys.argv[4]
    words, bad = [], 0
    for line in open(path):
        s = line.strip()
        if not s:
            continue
        if len(s) != n or any(c not in "0123456789"[:q] for c in s):
            bad += 1
            continue
        words.append(s)
    uniq = sorted(set(words))
    dup = len(words) - len(uniq)
    cov = np.zeros((q,) * n, dtype=bool)
    idx = np.array([[int(c) for c in w] for w in uniq], dtype=np.int64)
    cov[tuple(idx.T)] = True
    for _ in range(R):
        nxt = cov.copy()
        for ax in range(n):
            for sh in range(1, q):
                nxt |= np.roll(cov, sh, axis=ax)
        cov = nxt
    unc = int(cov.size - np.count_nonzero(cov))
    canon = "".join(w + "\n" for w in uniq).encode()
    ok = unc == 0 and dup == 0 and bad == 0
    print(f"q={q} n={n} R={R} M={len(uniq)} duplicates={dup} badlines={bad} uncovered={unc} "
          f"sha256_canon={hashlib.sha256(canon).hexdigest()} => {'VALID' if ok else 'INVALID'}")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
