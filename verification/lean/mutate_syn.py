#!/usr/bin/env python3
"""Mutações destrutivas dos certificados por síndromes (CoveringLean/Syn*_<tag>*.lean).

Gera, numa pasta à parte (nunca em CoveringLean/), cópias adulteradas dos arquivos GERADOS de um
certificado, com tag nova, para provar que o kernel recusa cada adulteração:

  M1 troca   : L[i] -> w' (mantém L estritamente crescente e PN coerente; w' escolhida para que o
               código adulterado deixe pontos descobertos, conferido pelo tools/verify/verify).
               Copia as folhas cujas testemunhas apontam para o índice i.
  M2 remoção : tira L[i] (e a entrada de PN; cnt = M-1).
               M2a: o teorema continua dizendo M  -> `decide (L.length = M)` tem de falhar;
               M2b: o teorema passa a dizer M-1  -> as folhas B/O (índices deslocados) têm de falhar.
  C0 controle: a folha 0 original com outro nome (tem de COMPILAR; prova que o arranjo funciona).
  M3 tabela  : na folha T do bloco 0, a testemunha do ponto t=0 vira a palavra `negW` do exemplo
               de não-vacuidade (distância > R), sem mexer nos dados.

Uso: mutate_syn.py TAG OUTDIR [--full]   (--full copia todas as folhas e a montagem, para o build
completo do teorema adulterado; sem ele, só as folhas que a adulteração atinge)
Imprime um JSON com o que foi gerado e quais módulos compilar; não compila nada.
"""
import json, os, re, subprocess, sys, tempfile
sys.set_int_max_str_digits(0)

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
tag, outdir = sys.argv[1], sys.argv[2]
full = "--full" in sys.argv
CL = os.path.join(RAIZ, "CoveringLean")
os.makedirs(os.path.join(outdir, "CoveringLean"), exist_ok=True)
data = open(f"{CL}/SynData_{tag}.lean").read()

def field(name):
    return re.search(rf"^\s*{name} := (.+)$", data, re.M).group(1).strip()

q, n, k, R, b, M = (int(field(x)) for x in ("q", "n", "k", "R", "b", "cnt"))
reps = json.loads(field("reps"))
L = [int(x) for x in re.search(rf"def L{tag} : List Nat := \[([^\]]*)\]", data).group(1).split(",")]
assert len(L) == M
leaves = sorted((f for f in os.listdir(CL) if f.startswith(f"SynLeaf_{tag}_")),
                key=lambda f: int(f.rsplit("_", 1)[1][:-5]))
leaf_src = {f: open(f"{CL}/{f}").read() for f in leaves}
syn_src = open(f"{CL}/Syn_{tag}.lean").read()

def digits(x): return [(x // q**i) % q for i in range(n)]
def s(x): return "".join(map(str, digits(x)))

def uncovered(words):
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
        f.write("".join(s(w) + "\n" for w in sorted(words, key=s)))
    r = subprocess.run([f"{RAIZ}/tools/verify/verify", "-q", str(q), "-n", str(n), "-r", str(R), f.name],
                       capture_output=True, text=True)
    os.unlink(f.name)
    return int(re.search(r"uncovered=(\d+)", r.stdout).group(1))

def retag(src, new):
    # troca todo identificador/módulo da tag velha pela nova (PK1134 -> PK1134M1 etc.)
    return re.sub(rf"(?<=[A-Za-z_]){tag}(?![0-9])", new, src)

def write_data(new, Lnew, cnt=None):
    PN = sum(x << (b * i) for i, x in enumerate(Lnew))
    src = retag(data, new)
    src = re.sub(r"^(\s*PN := ).+$", lambda m: m.group(1) + str(PN), src, flags=re.M)
    src = re.sub(r"^(\s*cnt := ).+$", lambda m: m.group(1) + str(len(Lnew) if cnt is None else cnt), src, flags=re.M)
    src = re.sub(rf"def L{new} : List Nat := \[[^\]]*\]", f"def L{new} : List Nat := {Lnew}", src)
    open(f"{outdir}/CoveringLean/SynData_{new}.lean", "w").write(src)

def leaf_entries(st):
    """(tipo, B, base, N) de cada folha `chkX P B ... N = true`."""
    m = re.match(r"chk(\w) P\S+ (\d+) (.*) (\d+) = true", st)
    if m is None:   # chkPiv P q^k = true
        return "V", 0, "", 0
    return m.group(1), int(m.group(2)), m.group(3), int(m.group(4))

def leaves_pointing_to(i):
    """Arquivos de folha com alguma folha O/B cuja testemunha seja o índice i de L."""
    hit = []
    for f, src in leaf_src.items():
        for st in re.findall(r"theorem \S+ : (.+?) := by decide \+kernel", src):
            kind, B, mid, N = leaf_entries(st)
            if kind not in "OB": continue
            cnt = int(mid.split()[1])
            ws = [(N // B**j) % B for j in range(cnt)]
            if i in ws: hit.append(f); break
    return hit

def copy_leaves(files, new):
    mods = []
    for f in files:
        nf = f.replace(tag, new, 1)
        open(f"{outdir}/CoveringLean/{nf}", "w").write(retag(leaf_src[f], new))
        mods.append("CoveringLean." + nf[:-5])
    return mods

base = set()
plan = {"tag": tag, "q": q, "n": n, "R": R, "M": M, "mutations": {}}

# ---- M1: troca uma palavra -----------------------------------------------------------------
Lset = set(L)
best = None
for i in sorted(range(M), key=lambda i: (i * 7919) % M)[:200]:
    lo = L[i - 1] + 1 if i else 0
    hi = L[i + 1] - 1 if i + 1 < M else q**n - 1
    for w2 in (lo, (lo + hi) // 2, hi):
        if w2 == L[i] or w2 in Lset or not lo <= w2 <= hi: continue
        unc = uncovered(L[:i] + [w2] + L[i + 1:])
        if unc > 0:
            best = (i, w2, unc); break
    if best: break
i, w2, unc = best
new = f"{tag}M1"
write_data(new, L[:i] + [w2] + L[i + 1:])
targets = leaves if full else leaves_pointing_to(i)
mods = copy_leaves(targets, new)
if full:
    open(f"{outdir}/CoveringLean/Syn_{new}.lean", "w").write(retag(syn_src, new))
    mods.append(f"CoveringLean.Syn_{new}")
plan["mutations"]["M1_troca"] = {"index": i, "old": s(L[i]), "new": s(w2), "uncovered_points": unc,
                                  "modules": [f"CoveringLean.SynData_{new}"] + mods}

# ---- M2: remove uma palavra ----------------------------------------------------------------
j = i
L2 = L[:j] + L[j + 1:]
unc2 = uncovered(L2)
new = f"{tag}M2"
write_data(new, L2)
card = f"{outdir}/CoveringLean/Card_{new}.lean"
open(card, "w").write(f"import CoveringLean.SynData_{new}\n\nnamespace Syn\n\n"
                      f"-- M2a: o teorema original exige `L.length = {M}` (hlen); com a palavra removida isso é falso.\n"
                      f"example : L{new}.length = {M} := by decide +kernel\n\nend Syn\n")
# M2b: com M-1 no enunciado, os índices de L a partir de j deslocam: folhas B/O com testemunha >= j
hit = set()
for f, src in leaf_src.items():
    for st in re.findall(r"theorem \S+ : (.+?) := by decide \+kernel", src):
        kind, B, mid, N = leaf_entries(st)
        if kind in "OB":
            cnt = int(mid.split()[1])
            if any((N // B**t) % B >= j for t in range(cnt)): hit.add(f)
targets = leaves if full else sorted(hit, key=lambda f: int(f.rsplit("_", 1)[1][:-5]))[:2]
mods = copy_leaves(targets, new)
if full:
    src = retag(syn_src, new)
    src = src.replace(f"C.card = {M}", f"C.card = {M - 1}").replace(f"le_{M}_syn", f"le_{M - 1}_syn")
    open(f"{outdir}/CoveringLean/Syn_{new}.lean", "w").write(src)
    mods.append(f"CoveringLean.Syn_{new}")
plan["mutations"]["M2_remocao"] = {"index": j, "removed": s(L[j]), "uncovered_points": unc2,
                                    "modules_card": [f"CoveringLean.SynData_{new}", f"CoveringLean.Card_{new}"],
                                    "modules_cover": [f"CoveringLean.SynData_{new}"] + mods}

# ---- M3: testemunha da tabela de cobertura -------------------------------------------------
negW = int(re.search(rf"example : okT P{tag} 0 (\d+) = false", syn_src).group(1))
f0 = next(f for f in leaves if re.search(rf"theorem T{tag}_0 :", leaf_src[f]))
src = leaf_src[f0]
m = re.search(rf"(theorem T{tag}_0 : chkT P{tag} (\d+) (\d+) 0 )(\d+)( = true)", src)
B, N = int(m.group(2)), int(m.group(4))
old_w = N % B
N2 = N - old_w + negW
assert negW < B and old_w != negW
new = f"{tag}M3"
src2 = src[:m.start()] + m.group(1) + str(N2) + m.group(5) + src[m.end():]
src2 = re.sub(rf"theorem (\w+){tag}_", rf"theorem \g<1>{new}_", src2)   # só os nomes; dados = os originais
src2 = src2.replace(f"import CoveringLean.SynData_{tag}\n", f"import CoveringLean.SynData_{tag}\n", 1)
nf = f"SynLeaf_{new}_0.lean"
open(f"{outdir}/CoveringLean/{nf}", "w").write(src2)
plan["mutations"]["M3_tabela"] = {"leaf": f"T{tag}_0", "point_t": 0, "old_witness": old_w, "new_witness": negW,
                                  "modules": ["CoveringLean." + nf[:-5]]}
# ---- controle positivo: a mesma folha 0, só com nomes trocados, TEM de compilar -------------
ctl = re.sub(rf"theorem (\w+){tag}_", rf"theorem \g<1>{tag}C0_", src)
nf = f"SynLeaf_{tag}C0_0.lean"
open(f"{outdir}/CoveringLean/{nf}", "w").write(ctl)
plan["control"] = {"modules": ["CoveringLean." + nf[:-5]]}
print(json.dumps(plan, indent=1))
