#!/usr/bin/env python3
"""Gera paper/evidence_table.tex a partir de snapshot/SNAPSHOT.json: a tabela do
paper não é digitada à mão, então não diverge dos dados da campanha."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
rows = json.loads((ROOT / "campaigns/covering-codes/snapshot/SNAPSHOT.json").read_text())["rows"]
LIT = {"NO_PREDECESSOR_FOUND_IN_REVIEWED_SOURCES": "NPF", "AMBIGUOUS": "AMB", "PREDECESSOR_FOUND": "PF"}

def lean(r):
    if r["size"] == 12:
        return "12-word cover built; $=12$ heavy, not rebuilt"
    if r["lean_theorems_measured"]:
        return "PROVED (syndromes, built)" if any(".Syn." in "." + t or t.startswith("Syn.") for t in r["lean_theorems_measured"]) else "PROVED (built)"
    if r["lean_theorems_declared_only"]:
        return "theorem; heavy build not rebuilt here"
    return "not formalized"

out = [r"\begin{table}[ht]", r"\centering", r"\scriptsize", r"\setlength{\tabcolsep}{3pt}",
       r"\begin{tabular}{@{}lrllllllll@{}}", r"\toprule",
       r"cell & size & witness & C & Rust & Go & Py$^\dagger$ & Lean & published & lit. \\", r"\midrule"]
for r in sorted(rows, key=lambda r: (r["q"], r["n"], r["R"], r["size"])):
    pub = f"{r['best_recorded_bound']}" if r["best_recorded_bound"] else "12 (exact)"
    v = r["verifier_results"]
    out.append(f"$K_{{{r['q']}}}({r['n']},{r['R']})$ & {r['size']} & \\texttt{{{r['sha256_canonical'][:8]}}} & "
               f"{v.get('verify-c', '-')} & {v.get('verify-rust', '-')} & {v.get('verify-cleanroom', '-')} & {v.get('verify-py-dilation', '-')} & {lean(r)} & {pub} & {LIT[r['literature_state']]} \\\\")
out += [r"\bottomrule", r"\end{tabular}",
        r"\caption{Central evidence table, generated from the campaign data. Witness: first 8 hex digits of the canonical SHA-256. "
        r"C, Rust, Go: verifiers counted as independent by author and implementation group (the Go one was written from the specification alone). "
        r"$^\dagger$Python: PASS, but written by the author of the claim, so not counted for independence. "
        r"All verifiers are programs written by agents of one model family: this is independence of implementation, not full cognitive independence. "
        r"Lean: ``PROVED (built)'' = theorem whose build and \texttt{\#print axioms} were measured in the campaign; ``theorem; heavy build not rebuilt here'' = declared in the repository, build of \texttt{CoveringHeavy} (about $9.3$ CPU-hours) not reproduced there. "
        r"``Published'': best bound recorded in the sources we read (K\'eri 2009/2011, Marosi v3). "
        r"Lit.: PF = predecessor found; NPF = no predecessor found in the reviewed sources (not a claim that none exists); AMB = ambiguous (amalgamated direct sums or unread tables, see text). "
        r"No cell is marked as externally confirmed new.}", r"\label{tab:evidence}", r"\end{table}"]
(ROOT / "paper/evidence_table.tex").write_text("\n".join(out) + "\n")
print("ok")
