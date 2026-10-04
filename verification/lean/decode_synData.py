#!/usr/bin/env python3
"""Independent check: decode the codeword list from CoveringLean/SynData_K1137.lean
(both the literal list LK1137 and the packed PN field of PK1137) and compare with
data/codes/q7_n9_R4_M1137.txt and the canonical sha256.

Word encoding (from SynCheck.lean `D q w i = w / q^i % q` and C1_CoverCheck `dig`):
integer w = sum_i w_i * 7^i, coordinate i = base-7 digit i (little-endian).
Canonical form: each word as the string w_0 w_1 ... w_8, sorted, one per line, '\n'-terminated.
Written from scratch; does not import or reuse scripts/syndrome/*.
"""
import hashlib, re, sys
sys.set_int_max_str_digits(0)

q, n, R, M = 7, 9, 4, 1137
EXPECT = "df3e8d527bc393a9680fe4b2b39e7bde088ab6a02f2f94ee26019a5efc05a102"

# Uso: decode_synData.py [repo] [--tag K1137] [--cover]
#   --tag: certificado CoveringLean/SynData_<tag>.lean; q, n, R e M saem dos campos do Spec e o
#   código esperado é data/codes/q<q>_n<n>_R<R>_M<M>.txt; o arquivo pode estar fora de ordem, então
#   compara-se a forma canônica (linhas ordenadas) dele com a decodificada do .lean.
#   Sem --tag, mantém o comportamento original (K1137, sha fixo df3e8d52...).
args = [x for x in sys.argv[1:] if not x.startswith("--")]
repo = args[0] if args and not args[0].startswith("K") else "."
tag = sys.argv[sys.argv.index("--tag") + 1] if "--tag" in sys.argv else "K1137"
src = open(f"{repo}/CoveringLean/SynData_{tag}.lean").read()
def field(name):
    m = re.search(rf"^\s*{name} := (.+)$", src, re.M)
    return m.group(1).strip()

if tag == "K1137":
    assert int(field("q")) == q and int(field("n")) == n and int(field("R")) == R
    assert int(field("cnt")) == M
else:
    q, n, R, M = (int(field(x)) for x in ("q", "n", "R", "cnt"))
CODE = f"{repo}/data/codes/q{q}_n{n}_R{R}_M{M}.txt"
def canon_of_file(path):
    ws = sorted(l.strip() for l in open(path) if l.strip() and not l.startswith("#"))
    return "".join(w + "\n" for w in ws)
if tag != "K1137":
    EXPECT = hashlib.sha256(canon_of_file(CODE).encode()).hexdigest()
print(f"tag={tag} q={q} n={n} R={R} M={M}")
b = int(field("b")); PN = int(field("PN"))
L = [int(x) for x in re.search(rf"def L{tag} : List Nat := \[([^\]]*)\]", src).group(1).split(",")]

# 1. literal list
print(f"len(L{tag}) =", len(L))
assert len(L) == M
assert all(L[i] < L[i + 1] for i in range(M - 1)), "not strictly increasing"
assert len(set(L)) == M and all(0 <= w < q**n for w in L)
# 2. packed PN, b bits per entry (pget/unpack in SynCheck.lean)
U = [(PN >> (b * j)) & ((1 << b) - 1) for j in range(M)]
assert PN >> (b * M) == 0, "PN has extra high bits beyond cnt entries"
print(f"unpack(PN) == L{tag}:", U == L)
assert U == L

def s(w): return "".join(str((w // q**i) % q) for i in range(n))
canon = "".join(x + "\n" for x in sorted(s(w) for w in L))
h = hashlib.sha256(canon.encode()).hexdigest()
print("sha256(canonical from .lean) =", h)
ftxt = open(CODE).read() if tag == "K1137" else canon_of_file(CODE)
hf = hashlib.sha256(ftxt.encode()).hexdigest()
print(f"sha256(canônico de {CODE}) =", hf)
print("canonical == file bytes:", canon == ftxt)
print("matches expected:", h == EXPECT and hf == EXPECT)
assert h == EXPECT and hf == EXPECT and canon == ftxt

# 3. optional: independent brute-force covering check over all q^n points (numpy)
if "--cover" in sys.argv:
    import numpy as np, itertools
    pw = np.array([q**i for i in range(n)], dtype=np.int64)
    # ball offsets: all error vectors of weight <= R, as digit arrays
    offs = []
    for wt in range(R + 1):
        for pos in itertools.combinations(range(n), wt):
            for vals in itertools.product(range(1, q), repeat=wt):
                e = [0] * n
                for p, v in zip(pos, vals): e[p] = v
                offs.append(e)
    E = np.array(offs, dtype=np.int64)
    print("ball size =", len(E))
    covered = np.zeros(q**n, dtype=bool)
    for w in L:
        c = np.array([(w // q**i) % q for i in range(n)], dtype=np.int64)
        for e0 in range(0, len(E), 200000):   # em blocos: a bola de K7(10,4) tem 1,2 M pontos
            covered[((E[e0:e0 + 200000] + c) % q) @ pw] = True
    print("points covered:", int(covered.sum()), "of", q**n)
    assert covered.all()
print("OK")
