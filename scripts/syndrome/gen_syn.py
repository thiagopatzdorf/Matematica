#!/usr/bin/env python3
"""Gerador do certificado por síndromes (CoveringLean/Syn*.lean).

Formato coberto: código C = (união de cosets completos de um código linear C0 = <G>) ∪ remendo.
Entrada: JSON `covering-code/v1` (docs/code-format.md, data/structured/*.json) ou o formato simples:

    {"q": 7, "n": 9, "R": 4,
     "generator": ["100620621", ...],      # k linhas, dígitos w_0..w_{n-1}  (ou "A" para G=[I|A])
     "coset_reps": ["000...", ...],          # opcional: senão, detecta os cosets completos no código
     "code_file": "data/codes/q7_n9_R4_M1351.txt"}   # ou "patch_words": [...] (+ coset_reps)

O certificado não depende de G estar em forma sistemática nas primeiras coordenadas: o script
escalona G e procura um bloco contíguo de informação [o, o+k).  Ele emite

    CoveringLean/SynData_<tag>.lean   parâmetros (Syn.Spec) e a lista ordenada L do código
    CoveringLean/SynLeaf_<tag>_<i>.lean   folhas `decide +kernel` (só núcleo, importam SynCheck)
    CoveringLean/Syn_<tag>.lean       montagem + teorema final via Syn.syn_cert (Mathlib)

e confere que L decodifica para o arquivo com o sha256 canônico (palavras ordenadas como
strings w_0..w_{n-1}, uma por linha, terminando em \\n).

Uso: gen_syn.py spec.json tag [--chunk 4096] [--per-file 4] [--expect-sha HEX]
"""
import argparse, hashlib, itertools, json, os, sys
sys.set_int_max_str_digits(0)
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("spec"); ap.add_argument("tag")
ap.add_argument("--chunk", type=int, default=4096)
ap.add_argument("--per-file", type=int, default=4)
ap.add_argument("--expect-sha", default=None)
ap.add_argument("--out", default=os.path.join(os.path.dirname(__file__), "..", "..", "CoveringLean"))
ap.add_argument("--wrong", action="store_true", help="teste negativo: remove uma palavra do código")
a = ap.parse_args()
LIST_RECDEPTH_THRESHOLD = 2048
J = json.load(open(a.spec))
q, n, R = J["q"], J["n"], J["R"]
base_dir = os.path.dirname(os.path.abspath(a.spec))

def parse(s): return [int(c) for c in s]
def enc(v): return sum(int(d) * q**i for i, d in enumerate(v))

# ---------- formato covering-code/v1 (docs/code-format.md, agente B) ----------
if J.get("format") == "covering-code/v1":
    lb = J["linear_base"]
    J["generator"] = lb["generator"]
    cc = lb["check_columns"]
    reps_txt = []
    for syn in lb.get("coset_syndromes", []):
        r = [0] * n
        for i, c in enumerate(cc): r[c] = int(syn[i])
        reps_txt.append("".join(map(str, r)))
    reps_txt += lb.get("coset_reps", [])
    J["coset_reps"] = reps_txt
    Gl = [parse(g) for g in lb["generator"]]
    base = set()
    for u in itertools.product(range(q), repeat=len(Gl)):
        c0 = [sum(u[i] * Gl[i][j] for i in range(len(Gl))) % q for j in range(n)]
        for r in reps_txt:
            base.add("".join(str((int(r[j]) + c0[j]) % q) for j in range(n)))
    extra = list(J.get("patch_words", []))
    for blk in J.get("subcode_cosets", []):
        gens = [parse(g) for g in blk["generators"]]
        span = {tuple([0] * n)}
        for g in gens:
            span = {tuple((v[j] + c * g[j]) % q for j in range(n)) for v in span for c in range(q)}
        for r in blk["reps"]:
            extra += ["".join(str((int(r[j]) + v[j]) % q) for j in range(n)) for v in span]
    J["patch_words"] = sorted(set(extra) - base)
    if a.expect_sha is None: a.expect_sha = J.get("canonical_sha256")

# ---------- código ----------
if "code_file" in J:
    p = J["code_file"]
    if not os.path.isabs(p): p = os.path.join(base_dir, p)
    words = [l.strip() for l in open(p) if l.strip()]
else:
    words = None
if "generator" in J:
    G = np.array([parse(g) for g in J["generator"]], dtype=np.int64)
else:  # G = [I_k | A]
    A = np.array([parse(r) for r in J["A"]], dtype=np.int64)
    G = np.concatenate([np.eye(A.shape[0], dtype=np.int64), A], axis=1)
k = G.shape[0]
inv = lambda x: pow(int(x), -1, q)

def systematic(G, o):
    M = G.copy() % q
    for r in range(k):
        c = o + r
        piv = [i for i in range(r, k) if M[i, c]]
        if not piv: return None
        M[[r, piv[0]]] = M[[piv[0], r]]
        M[r] = (M[r] * inv(M[r, c])) % q
        for i in range(k):
            if i != r and M[i, c]: M[i] = (M[i] - M[i, c] * M[r]) % q
    return M

for o in range(n - k + 1):
    Gs = systematic(G, o)
    if Gs is not None: break
else:
    sys.exit("nenhum bloco contíguo de informação")
msgs = np.array([[(m // q**j) % q for j in range(k)] for m in range(q**k)], dtype=np.int64)
C0 = (msgs @ Gs) % q                         # índice m = mensagem m (dígito j = coeficiente da linha j)
assert len({tuple(r) for r in C0}) == q**k

def zero_block_rep(v):
    v = np.array(v) % q
    return (v - v[o:o + k] @ Gs) % q

if words is None:
    reps0 = [np.array(parse(r)) for r in J["coset_reps"]]
    words = set()
    for r in reps0:
        words |= {"".join(map(str, (r + c) % q)) for c in C0}
    pw = J["patch_words"]; words |= set(pw.split() if isinstance(pw, str) else pw)
    words = sorted(words)
W = np.array([parse(w) for w in words], dtype=np.int64)
assert W.shape[1] == n
if "coset_reps" in J:
    reps = [zero_block_rep(parse(r)) for r in J["coset_reps"]]
else:
    from collections import Counter
    cnt = Counter(tuple(zero_block_rep(w)) for w in W)
    reps = [np.array(r) for r, c in cnt.items() if c == q**k]
reps = sorted({tuple(r) for r in reps})
reps = [np.array(r) for r in reps]
Wset = {tuple(w) for w in W}
for r in reps:
    assert all(tuple((r + c) % q) in Wset for c in C0), "coset incompleto"
if a.wrong:   # remove uma palavra de remendo (fora dos cosets) para o teste negativo
    base = {tuple((r + c) % q) for r in reps for c in C0}
    drop = next(tuple(w) for w in W if tuple(w) not in base)
    W = np.array([w for w in W if tuple(w) != drop]); print("removida", drop)
Lint = sorted(enc(w) for w in W)
M = len(Lint)
canon = "".join("".join(str((x // q**i) % q) for i in range(n)) + "\n"
                for x in sorted(Lint, key=lambda x: "".join(str((x // q**i) % q) for i in range(n))))
sha = hashlib.sha256(canon.encode()).hexdigest()
print(f"q={q} n={n} k={k} R={R} o={o} M={M} cosets={len(reps)} sha256={sha}")
if a.expect_sha and not a.wrong: assert sha == a.expect_sha, "sha diferente do esperado"
Lpos = {x: i for i, x in enumerate(Lint)}
Ld = np.array([[(x // q**i) % q for i in range(n)] for x in Lint], dtype=np.int64)

# ---------- transversal ----------
nt = q**(n - k)
def ydigits(t):
    out = []
    for i in range(n):
        if i < o: out.append((t // q**i) % q)
        elif i < o + k: out.append(0)
        else: out.append((t // q**(i - k)) % q)
    return out
Y = np.array([ydigits(t) for t in range(nt)], dtype=np.int64)
Bw = np.concatenate([(r + C0) % q for r in reps])          # índice s*q^k + m
ORPH = len(reps) * q**k
witT = np.full(nt, ORPH, dtype=np.int64)
for s0 in range(0, nt, 2048):
    d = (Y[s0:s0 + 2048, None, :] != Bw[None, :, :]).sum(-1)
    j = d.argmin(1); ok = d[np.arange(len(j)), j] <= R
    witT[s0:s0 + 2048][ok] = j[ok]
orphs = [int(t) for t in np.where(witT == ORPH)[0]]
print("órfãos", len(orphs), "pontos", len(orphs) * q**k)
witO = {}
for t in orphs:
    pts = (Y[t][None, :] + C0) % q
    d = (pts[:, None, :] != Ld[None, :, :]).sum(-1)
    j = d.argmin(1)
    if not (d[np.arange(len(j)), j] <= R).all():
        bad = int((d.min(1) > R).sum()); print(f"FALHA: órfão t={t} com {bad} pontos descobertos")
        witO[t] = None
    else:
        witO[t] = [int(x) for x in j]
witB = [[Lpos[enc((r + c) % q)] for c in C0] for r in reps]

# ---------- emissão ----------
b = (q**n - 1).bit_length()
PN = sum(x << (b * i) for i, x in enumerate(Lint))
def bitsfor(mx): return max(1, int(mx).bit_length())
def pack(ws, bits): return sum(int(w) << (bits * i) for i, w in enumerate(ws))
T = f"S{a.tag}"
grow = [enc(g) for g in Gs]
repsN = [enc(r) for r in reps]
out = a.out
hdr = "-- gerado por scripts/syndrome/gen_syn.py; não editar à mão\n"
with open(f"{out}/SynData_{a.tag}.lean", "w") as f:
    f.write(hdr + "import CoveringLean.SynCheck\n\n")
    f.write(f"/-! Dados do certificado `{a.tag}`: q={q}, n={n}, R={R}, M={M}.\n"
            f"sha256 canônico do código (palavras como strings w_0..w_(n-1), ordenadas, uma por linha): {sha}\n"
            f"C0 = [{n},{k}]_{q}, bloco de informação [{o},{o+k}), {len(reps)} cosets completos, "
            f"{len(orphs)} síndromes órfãs ({len(orphs)*q**k} pontos). -/\n\n")
    f.write("namespace Syn\n\n")
    f.write(f"def P{a.tag} : Spec where\n  q := {q}\n  n := {n}\n  k := {k}\n  o := {o}\n  R := {R}\n"
            f"  Gs := {grow}\n  reps := {repsN}\n  orphs := {orphs}\n  PN := {PN}\n  b := {b}\n  cnt := {M}\n\n")
    # Literal de lista com mais de ~2000 elementos estoura o maxRecDepth padrão (512) na elaboração
    # (medido: K5(11,4) com M=2875 falhou em SynData). Só acima do limiar, para que os certificados
    # antigos (M <= 1887) continuem saindo byte a byte iguais.
    if M > LIST_RECDEPTH_THRESHOLD: f.write("set_option maxRecDepth 100000 in\n")
    f.write(f"def L{a.tag} : List Nat := {Lint}\n\nend Syn\n")

leaves = []   # (nome, enunciado)
BT = bitsfor(ORPH)
for c0 in range(0, nt, a.chunk):
    ws = witT[c0:c0 + a.chunk]
    leaves.append((f"T{a.tag}_{c0 // a.chunk}",
                   f"chkT P{a.tag} {2**BT} {len(ws)} {c0} {pack(ws, BT)} = true"))
BO = bitsfor(M - 1)
for i, t in enumerate(orphs):
    ws = witO[t] if witO[t] is not None else [0] * q**k
    leaves.append((f"O{a.tag}_{i}", f"chkO P{a.tag} {2**BO} {t} {q**k} 0 {pack(ws, BO)} = true"))
for s, ws in enumerate(witB):
    leaves.append((f"B{a.tag}_{s}", f"chkB P{a.tag} {2**BO} {s} {q**k} 0 {pack(ws, BO)} = true"))
leaves.append((f"V{a.tag}", f"chkPiv P{a.tag} {q**k} = true"))
files = [leaves[i:i + a.per_file] for i in range(0, len(leaves), a.per_file)]
for fi, grp in enumerate(files):
    with open(f"{out}/SynLeaf_{a.tag}_{fi}.lean", "w") as f:
        f.write(hdr + f"import CoveringLean.SynData_{a.tag}\n\nnamespace Syn\n\n")
        for nm, st in grp:
            f.write(f"theorem {nm} : {st} := by decide +kernel\n\n")
        f.write("end Syn\n")
nT = (nt + a.chunk - 1) // a.chunk
negT = 0
dd = (Y[negT][None, :] != Bw).sum(-1)
negW = int(np.argmax(dd)); negD = int(dd[negW]); assert negD > R
thm = f"K{q}_{n}_{R}_le_{M}_syn"
with open(f"{out}/Syn_{a.tag}.lean", "w") as f:
    f.write(hdr + "import CoveringLean.SynBridge\n")
    for fi in range(len(files)): f.write(f"import CoveringLean.SynLeaf_{a.tag}_{fi}\n")
    f.write(f"""
/-! # K_{q}({n},{R}) ≤ {M} pelo certificado por síndromes

Código: `Syn.L{a.tag}` (sha256 canônico {sha}), união de {len(reps)} cosets completos de um
`[{n},{k}]_{q}` (bloco de informação [{o},{o+k})) com {M - len(reps) * q**k} palavras de remendo;
{len(orphs)} síndromes órfãs ({len(orphs) * q**k} pontos checados um a um).
-/

namespace Syn

set_option maxRecDepth 100000

theorem hT{a.tag} : ∀ t < {nt}, ∃ w, okT P{a.tag} t w = true :=
  all_of_chunks (fun t => ∃ w, okT P{a.tag} t w = true) {a.chunk} {nT} {nt} (by norm_num) (by
    intro c hc
    match c, hc with
""")
    for c in range(nT):
        f.write(f"    | {c}, _ => exact fun i _ hlt => chkT_sound P{a.tag} _ _ _ _ T{a.tag}_{c} i (by omega)\n")
    f.write(f"""    | c + {nT}, h => exact absurd h (by omega))

theorem hO{a.tag} : ∀ i < P{a.tag}.orphs.length, ∀ a < {q**k}, ∃ j, okO P{a.tag} (P{a.tag}.orphs.getD i 0) a j = true := by
  intro i hi
  match i, hi with
""")
    for i in range(len(orphs)):
        f.write(f"  | {i}, _ => exact chkO_sound P{a.tag} _ _ _ _ O{a.tag}_{i}\n")
    f.write(f"""  | i + {len(orphs)}, h => exact absurd h (by have : P{a.tag}.orphs.length = {len(orphs)} := rfl; omega)

theorem hB{a.tag} : ∀ s < P{a.tag}.reps.length, ∀ m < {q**k}, ∃ j, okB P{a.tag} s m j = true := by
  intro s hs
  match s, hs with
""")
    for s_ in range(len(reps)):
        f.write(f"  | {s_}, _ => exact chkB_sound P{a.tag} _ _ _ _ B{a.tag}_{s_}\n")
    f.write(f"""  | s + {len(reps)}, h => exact absurd h (by have : P{a.tag}.reps.length = {len(reps)} := rfl; omega)

/-- Não-vacuidade: o verificador recusa uma testemunha errada (ponto `t = {negT}`, palavra
`{negW}` a distância {negD} > {R}). -/
example : okT P{a.tag} {negT} {negW} = false := by decide +kernel

/-- `K_{q}({n},{R}) ≤ {M}`: o código `L{a.tag}` tem {M} palavras e cobre com raio {R}. -/
theorem {thm} :
    ∃ C : Finset (Fin {n} → ZMod {q}), C.card = {M} ∧ CoveringA2.Covers {R} C :=
  syn_cert P{a.tag} L{a.tag} rfl rfl rfl ⟨rfl, by decide⟩ V{a.tag} hT{a.tag} hO{a.tag} hB{a.tag}
    (by decide +kernel) (by decide +kernel) (by decide +kernel)

end Syn

#print axioms Syn.{thm}
""")
print("folhas", len(leaves), "arquivos", len(files))
if any(v is None for v in witO.values()): print("CERTIFICADO FALHA (órfão descoberto)"); sys.exit(2)
