#!/usr/bin/env python3
"""Congela o estado científico dos códigos de cobertura a partir dos DADOS
(witnesses, verifier_runs, formal, claims), nunca de README/paper: editar texto
não muda estado. Saída: campaigns/covering-codes/snapshot/{SNAPSHOT.json,
SNAPSHOT.csv,SNAPSHOT.md}. Determinístico dado o mesmo estado da campanha."""
import csv, json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CAMP = ROOT / "campaigns" / "covering-codes"
OUT = CAMP / "snapshot"

# Estado de literatura vem das revisões profundas (campaigns/.../_literatura/profunda*/),
# transcrito aqui à mão: NENHUM é NOVELTY_EXTERNALLY_CONFIRMED (isso não se autoatribui).
LIT = {
 "w-q7-n9-r4-m1285": ("NO_PREDECESSOR_FOUND_IN_REVIEWED_SOURCES", "média", "_literatura/profunda", "risco: ADS q=7 (931/1225/1344) condicional a componentes normais, não verificado"),
 "w-q7-n9-r4-m1351": ("NO_PREDECESSOR_FOUND_IN_REVIEWED_SOURCES", "baixa-média", "_literatura/profunda", "superado pelo nosso 1285"),
 "w-q7-n8-r3-m1887": ("NO_PREDECESSOR_FOUND_IN_REVIEWED_SOURCES", "média", "_literatura/profunda", "risco: ADS (3,1)+(6,2)=1225 condicional a normalidade"),
 "w-q7-n8-r3-m1893": ("NO_PREDECESSOR_FOUND_IN_REVIEWED_SOURCES", "média", "_literatura/profunda", "superado pelo nosso 1887"),
 "w-q5-n10-r4-m625": ("NO_PREDECESSOR_FOUND_IN_REVIEWED_SOURCES", "baixa-média", "_literatura/profunda", "código linear [10,4,5]_5; tabela ℓ_5(6,4) não encontrada; não alegar novidade"),
 "w-q5-n7-r2-m500": ("AMBIGUOUS", "média", "_literatura/profunda_b", "ADS 478,4 condicional"),
 "w-q4-n10-r4-m192": ("AMBIGUOUS", "média-baixa", "_literatura/profunda_b", "ADS dá exatamente 192, condicional"),
 "w-q5-n9-r4-m250": ("AMBIGUOUS", "média", "_literatura/profunda_b", "ADS 245 condicional"),
 "w-q5-n9-r3-m1250": ("NO_PREDECESSOR_FOUND_IN_REVIEWED_SOURCES", "média", "_literatura/profunda_b", "ADS dá 1275 > nosso"),
 "w-q5-n9-r5-m50": ("NO_PREDECESSOR_FOUND_IN_REVIEWED_SOURCES", "média", "_literatura/profunda_b", "ADS dá 51 > nosso"),
 "w-q2-n6-r1-m12": ("PREDECESSOR_FOUND", "alta", "_literatura/profunda_b", "igualdade com valor clássico (Stanton–Kalbfleisch 1968, não lido; exatidão provada por busca exaustiva própria)"),
}

def jl(p): return json.loads(Path(p).read_text())

def main():
    commit = subprocess.check_output(["git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True).strip()
    runs = {}
    for f in sorted((CAMP / "verifier_runs").glob("*.json")):
        r = jl(f); runs.setdefault(r["subject_id"], {})[r["verifier_id"]] = r  # a última corrida por verificador
    vers = {jl(f)["verifier_id"] if "verifier_id" in jl(f) else f.stem: jl(f) for f in (CAMP / "verifiers").glob("*.json")}
    claims = {c["claim_id"]: c for c in (jl(f) for f in (CAMP / "claims").glob("*.json"))}
    formal = [jl(f) for f in (CAMP / "formal").glob("*.json")]
    rows = []
    for wf in sorted((CAMP / "witnesses").glob("*.json")):
        w = jl(wf); wid = wf.stem; p = w["parameters"]
        ub = [c for c in claims.values() if c["kind"] != "conjecture" and c.get("bound", {}) and c["bound"].get("direction") == "upper"
              and {k: p[k] for k in "qnR"} == c["bound"]["parameters"] and c["bound"]["value"] == p["M"] and wid in c["evidence"].get("witnesses", [])]
        c = ub[0] if ub else None
        lc = (c or {}).get("literature_comparison", {})
        best = lc.get("melhor_registrada")
        r = runs.get(wid, {})
        lean = [f for f in formal if c and f.get("formal_id", "").startswith("f-k7-9-4-le") and p == {"q": 7, "n": 9, "R": 4, "M": 1351}] if False else []
        lean_state = "no Lean theorem currently exists (verified computational witness only)"
        if wid == "w-q7-n9-r4-m1351":
            lean_state = "EXISTS_BUILD_NOT_REPRODUCED: theorem K3_K7_9_4_Final declared; CoveringHeavy (~12.4 h CPU) not built here; axioms declared, not measured"
        if wid == "w-q2-n6-r1-m12":
            lean_state = "EXISTS_BUILD_NOT_REPRODUCED: K_2(6,1)=12 via CoveringHeavy chunks not built here; lower bound 11 PROVED separately (default build)"
        st, conf, src, note = LIT.get(wid, ("?", "?", "", ""))
        cnt = {k: v["result"] for k, v in r.items()}
        rows.append({
            "witness_id": wid, "q": p["q"], "n": p["n"], "R": p["R"], "size": p["M"],
            "witness_path": w["path"], "sha256_file": w["sha256"], "sha256_canonical": w["canonical_sha256"],
            "created": w.get("created"), "witness_producer": w.get("produced_by"),
            "containing_commit": commit,
            "verify_c": cnt.get("verify-c"), "verify_rust": cnt.get("verify-rust"),
            "verify_py_dilation": cnt.get("verify-py-dilation"),
            "verifier_authors": {k: vers.get(k, {}).get("implemented_by") for k in ("verify-c", "verify-rust", "verify-py-dilation")},
            "independence_note": "contam como independentes C (thiagopatzdorf) e Rust (agente-verif-rust); Python é do mesmo autor da afirmação (agente-c): PASS não conta; agentes do mesmo modelo ≠ independência cognitiva total",
            "claim_id": c["claim_id"] if c else None, "claim_status": c["status"] if c else None,
            "lean": lean_state,
            "best_recorded_bound": best, "best_recorded_source": lc.get("melhor_registrada_fonte"),
            "diff_abs": (best - p["M"]) if best else None,
            "diff_pct": round(100 * (best - p["M"]) / best, 2) if best else None,
            "literature_state": st, "literature_confidence": conf, "literature_source": src, "literature_note": note,
            "classification": "apparent improvement over the currently recorded bound; novelty not yet established" if lc.get("veredito") == "melhor_que_a_registrada" else (lc.get("veredito") or "igual/sem comparação"),
        })
    OUT.mkdir(exist_ok=True)
    (OUT / "SNAPSHOT.json").write_text(json.dumps({"repo_commit": commit, "rows": rows}, indent=1, ensure_ascii=False, sort_keys=True) + "\n")
    flat = [{k: (json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else v) for k, v in r.items()} for r in rows]
    with open(OUT / "SNAPSHOT.csv", "w", newline="") as fh:
        wr = csv.DictWriter(fh, fieldnames=list(flat[0])); wr.writeheader(); wr.writerows(flat)
    md = ["# Snapshot científico (gerado por tools/campaign/snapshot_covering.py)", "", f"Commit-base: `{commit}`. Fonte: dados da campanha, não texto.", "",
          "| Código | Tamanho | Melhor registrada (Δ) | C | Rust | Python* | Lean | Literatura |", "|---|---|---|---|---|---|---|---|"]
    for r in rows:
        d = f"{r['best_recorded_bound']} (−{r['diff_abs']}, {r['diff_pct']}%)" if r["best_recorded_bound"] else "—"
        md.append(f"| K_{r['q']}({r['n']},{r['R']}) | {r['size']} | {d} | {r['verify_c']} | {r['verify_rust']} | {r['verify_py_dilation']} | {r['lean'].split(':')[0].split(' (')[0]} | {r['literature_state']} ({r['literature_confidence']}) |")
    md += ["", "*Python: mesmo autor da afirmação; PASS não conta para independência.", "",
           "Em 1285 e 1887: **verified computational witness; no Lean theorem currently exists.** Ausência de formalização não é falha do witness, e verificação computacional não é prova formal.", "",
           "Classificação: apparent improvement over the currently recorded bound; novelty not yet established."]
    (OUT / "SNAPSHOT.md").write_text("\n".join(md) + "\n")
    print(f"{len(rows)} códigos congelados em {OUT}")

if __name__ == "__main__":
    sys.exit(main())
