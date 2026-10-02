#!/usr/bin/env python3
"""run_mutations.py -- testes destrutivos do witness.

Gera mutações de code_1137.txt e passa cada uma pelo validador de formato (validate_witness.py) e,
quando o formato é válido, pelo verificador de cobertura C (BFS) com o tamanho da mutação.
Uma mutação PASSA no teste destrutivo quando é REJEITADA (formato inválido ou cobertura falha).
Uso: run_mutations.py <code_1137.txt> <binário verify_bfs> <dir de trabalho>
"""
import os, random, subprocess, sys

src, bfs, work = sys.argv[1:4]
os.makedirs(work, exist_ok=True)
here = os.path.dirname(os.path.abspath(__file__))
L = open(src).read().split("\n")[:-1]
rng = random.Random(20261002)


def canon(ws):
    return "".join(w + "\n" for w in sorted(ws))


def other_digit(d):
    return str((int(d) + rng.randrange(1, 7)) % 7)


muts = {}
i = rng.randrange(len(L)); muts["remove_one_word"] = (canon(L[:i] + L[i + 1:]), f"removida a palavra {L[i]}")
idx = sorted(rng.sample(range(len(L)), 5)); muts["remove_5_words"] = (canon([w for k, w in enumerate(L) if k not in idx]), "removidas " + ",".join(L[k] for k in idx))
a, b = rng.sample(range(len(L)), 2); m = L[:]; m[b] = L[a]; muts["duplicate_one_word_and_remove_another"] = ("".join(w + "\n" for w in m), f"{L[b]} trocada por cópia de {L[a]}")
i, j = rng.randrange(len(L)), rng.randrange(9); w = L[i][:j] + other_digit(L[i][j]) + L[i][j + 1:]
m = L[:]; m[i] = w; muts["change_coordinate"] = (canon(m) if w not in L else "".join(x + "\n" for x in m), f"{L[i]} -> {w}")
while True:
    w = "".join(str(rng.randrange(7)) for _ in range(9))
    if w not in L: break
i = rng.randrange(len(L)); m = L[:]; m[i] = w; muts["replace_word"] = (canon(m), f"{L[i]} -> {w} (aleatória)")
i = rng.randrange(len(L)); m = L[:]; m[i] = L[i][:8]; muts["truncate_word"] = ("".join(x + "\n" for x in m), f"{L[i]} -> {L[i][:8]}")
i, j = rng.randrange(len(L)), rng.randrange(9); m = L[:]; m[i] = L[i][:j] + "7" + L[i][j + 1:]; muts["value_7"] = ("".join(x + "\n" for x in m), f"{L[i]} -> {m[i]}")
i = rng.randrange(len(L)); m = L[:]; m[i] = "-1" + L[i][2:]; muts["negative_value"] = ("".join(x + "\n" for x in m), f"{L[i]} -> {m[i]}")

allok = True
print("| mutação | o que mudou | formato | cobertura (BFS) | rejeitada? |")
print("|---|---|---|---|---|")
for name, (text, what) in muts.items():
    p = os.path.join(work, name + ".txt"); open(p, "w").write(text)
    n = text.count("\n")
    fmt = subprocess.run([sys.executable, os.path.join(here, "validate_witness.py"), p, str(n)], capture_output=True, text=True)
    fmt_ok = fmt.returncode == 0
    rejected = not fmt_ok
    cov = ""
    if fmt_ok:
        r = subprocess.run([bfs, p, str(n)], capture_output=True, text=True)
        g = dict(l.split(" = ", 1) for l in r.stdout.splitlines() if " = " in l)
        cov = f"tamanho={g.get('|C|')} uncovered={g.get('uncovered')} max_d={g.get('max_distance')} -> {'PASS' if r.returncode == 0 else 'FAIL'}"
        rejected = r.returncode != 0
    allok &= rejected
    reason = "; ".join(l.strip() for l in fmt.stdout.splitlines() if l.startswith("  ")) if not fmt_ok else "PASS"
    if not fmt_ok:                       # o parser do verificador C também precisa recusar sozinho
        r = subprocess.run([bfs, p, str(n)], capture_output=True, text=True)
        cov = f"BFS recusa (saída {r.returncode}: {r.stderr.strip()})" if r.returncode else "BFS ACEITOU"
        rejected = rejected and r.returncode != 0
    print(f"| {name} | {what} | {reason} | {cov} | {'sim' if rejected else 'NÃO'} |")
print("\nPASS: todas as mutações foram rejeitadas" if allok else "\nATENÇÃO: alguma mutação foi aceita")
sys.exit(0 if allok else 1)
