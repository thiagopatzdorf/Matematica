#!/usr/bin/env python3
"""structure_check.py -- confere a descrição estrutural do witness (não faz parte da prova de cobertura).

H = [I_6 | A], A = '666 065 652 643 621 615' (linha i de A = 3 dígitos), síndrome s(x) = Hx mod 7,
inteira = sum s_j 7^j. Afirmação: 1029 palavras = 3 classes laterais completas (343 cada) do código
C0 = ker H = [9,3]_7, com síndromes {0, 4191, 7708}; as outras 108 são o remendo.
Uso: structure_check.py code_1137.txt"""
import sys, itertools
from collections import Counter
A = [[int(ch) for ch in row] for row in "666 065 652 643 621 615".split()]
H = [[1 if j == i else 0 for j in range(6)] + A[i] for i in range(6)]
def syn(x):
    return sum((sum(H[i][j] * x[j] for j in range(9)) % 7) * 7 ** i for i in range(6))
W = [[int(c) for c in l.strip()] for l in open(sys.argv[1])]
cnt = Counter(syn(w) for w in W)
S = {0, 4191, 7708}
in_cosets = sum(cnt[s] for s in S)
mind = min(sum(1 for v in x if v) for x in itertools.product(range(7), repeat=3)
           if any(x) for x in [[*[(-sum(A[i][k] * x[k] for k in range(3))) % 7 for i in range(6)], *x]])
print(f"|C| = {len(W)}")
print("palavras por síndrome do trio: " + ", ".join(f"{s}: {cnt[s]}" for s in sorted(S)))
print(f"em 3 classes laterais = {in_cosets}; remendo = {len(W) - in_cosets}; síndromes distintas no remendo = {len([s for s in cnt if s not in S])}")
print(f"distância mínima de C0 = {mind} (C0 = [9,3,{mind}]_7)")
ok = all(cnt[s] == 343 for s in S) and len(W) - in_cosets == 108
print("PASS estrutura: 3 x 343 + 108" if ok else "FAIL estrutura")
sys.exit(0 if ok else 1)
