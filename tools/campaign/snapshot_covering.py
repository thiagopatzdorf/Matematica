#!/usr/bin/env python3
"""Congela o estado científico dos códigos de cobertura a partir dos DADOS
(witnesses, verifier_runs, verifiers, formal, claims), nunca de README/paper: editar texto
não muda estado. O estado Lean sai dos REGISTROS FORMAIS ligados ao claim (axiomas medidos,
sorry_free, build limpo), não de texto. Saída: campaigns/covering-codes/snapshot/{SNAPSHOT.json,
SNAPSHOT.csv,SNAPSHOT.md}. Determinístico dado o mesmo estado da campanha."""
import csv, json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CAMP = ROOT / "campaigns" / "covering-codes"
OUT = CAMP / "snapshot"
AXIOMAS_ESPERADOS = {"propext", "Classical.choice", "Quot.sound"}

# Estado de literatura vem das revisões profundas (campaigns/.../_literatura/profunda*/ e STATE_OF_ART.md conferido em
# exp-state-of-art-crosscheck), transcrito aqui à mão: NENHUM é NOVELTY_EXTERNALLY_CONFIRMED (isso não se autoatribui).
LIT = {
 "w-q7-n9-r4-m1137": ("NO_PREDECESSOR_FOUND_IN_REVIEWED_SOURCES", "média", "STATE_OF_ART.md (conferido) + _literatura/profunda", "risco: ADS q=7 931 (<1137) condicional a componentes normais, não verificado; lacunas do STATE_OF_ART (Scholar, bases pagas, teses, periódico)"),
 "w-q7-n9-r4-m1141": ("NO_PREDECESSOR_FOUND_IN_REVIEWED_SOURCES", "média", "STATE_OF_ART.md (conferido) + _literatura/profunda", "superado pelo nosso 1137; mesmo risco ADS 931 condicional"),
 "w-q7-n9-r4-m1285": ("NO_PREDECESSOR_FOUND_IN_REVIEWED_SOURCES", "média", "_literatura/profunda", "risco: ADS q=7 (931/1225/1344) condicional a componentes normais, não verificado; superado pelo nosso 1137"),
 "w-q7-n9-r4-m1351": ("NO_PREDECESSOR_FOUND_IN_REVIEWED_SOURCES", "baixa-média", "_literatura/profunda", "superado pelo nosso 1137"),
 "w-q7-n8-r3-m1887": ("NO_PREDECESSOR_FOUND_IN_REVIEWED_SOURCES", "média", "_literatura/profunda", "risco: ADS (3,1)+(6,2)=1225 condicional a normalidade"),
 "w-q7-n8-r3-m1893": ("NO_PREDECESSOR_FOUND_IN_REVIEWED_SOURCES", "média", "_literatura/profunda", "superado pelo nosso 1887"),
 "w-q5-n10-r4-m625": ("AMBIGUOUS", "baixa", "_literatura/profunda_c", "código linear [10,4,5]_5; tabela ℓ_5(6,4) não encontrada; não alegar novidade"),
 "w-q5-n7-r2-m500": ("AMBIGUOUS", "média", "_literatura/profunda_b", "ADS 478,4 condicional"),
 "w-q4-n10-r4-m192": ("AMBIGUOUS", "média-baixa", "_literatura/profunda_b", "ADS dá exatamente 192, condicional"),
 "w-q5-n9-r4-m250": ("AMBIGUOUS", "média", "_literatura/profunda_b", "ADS 245 condicional"),
 "w-q5-n9-r3-m1250": ("NO_PREDECESSOR_FOUND_IN_REVIEWED_SOURCES", "média", "_literatura/profunda_b", "ADS dá 1275 > nosso"),
 "w-q5-n9-r5-m50": ("NO_PREDECESSOR_FOUND_IN_REVIEWED_SOURCES", "média", "_literatura/profunda_b", "ADS dá 51 > nosso"),
 "w-q2-n6-r1-m12": ("PREDECESSOR_FOUND", "alta", "_literatura/profunda_b", "igualdade com valor clássico (Stanton–Kalbfleisch 1968, não lido; exatidão provada por busca exaustiva própria)"),
}

def jl(p): return json.loads(Path(p).read_text())

def formal_medido(f):
    """Registro formal MEDIDO e limpo (mesma conferência da fronteira do Lean, sem importar a infraestrutura)."""
    return (f.get("axioms") is not None and set(f["axioms"]) <= AXIOMAS_ESPERADOS and f.get("sorry_free") is True and f.get("clean_build") is True
            and all(f.get(k) for k in ("lean_version", "mathlib_commit", "repo_commit")))

def lean_state(claim, formal):
    """Estado Lean DERIVADO dos registros formais do claim (evidence.formal e complementary_formal)."""
    if not claim:
        return "no claim", [], [], []
    ids = list(claim["evidence"].get("formal", [])) + list(claim.get("complementary_formal", []))
    medidos = [formal[i] for i in ids if i in formal and formal_medido(formal[i])]
    nao_medidos = [formal[i] for i in ids if i in formal and not formal_medido(formal[i])]
    # medição EXTERNA (VM do autor): existe, mas a guarda não a aceita; estado próprio, nunca PROVED_MEASURED
    externos = [f for f in nao_medidos if (f.get("measured_external") or {}).get("status") == "MEASURED_ON_EXTERNAL_VM"]
    declarados = [f for f in nao_medidos if f not in externos]
    partes = []
    if medidos:
        partes.append("PROVED_MEASURED: " + "; ".join(f"{f['theorem']} (axiomas {sorted(f['axioms'])}, sorry_free, build limpo, {f.get('lean_version','').split(',')[0].replace('Lean (version ','Lean ')})" for f in medidos))
    if externos:
        partes.append("MEASURED_ON_EXTERNAL_VM: " + "; ".join(f"{f['theorem']} (axiomas {sorted(f['measured_external']['axioms'])} e build {f['measured_external']['jobs']} jobs/{f['measured_external']['folhas_falhou']} falhas, "
                      f"medição do autor em VM, commit {f['measured_external']['repo_commit'][:7]}, log sha256 {f['measured_external']['log_sha256_prefixo']}…; não refeita em segundo ambiente; NÃO medido pela campanha)" for f in externos))
    if declarados:
        partes.append("EXISTS_BUILD_NOT_REPRODUCED: " + "; ".join(f"{f['theorem']} (axiomas só declarados {f.get('declared_axioms')}; {f.get('build_status','')[:80]})" for f in declarados))
    if not partes:
        partes.append("no Lean theorem currently registered (verified computational witness only)")
    return " | ".join(partes), [f["theorem"] for f in medidos], [f["theorem"] for f in declarados], [f["theorem"] for f in externos]

def main():
    commit = subprocess.check_output(["git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True).strip()
    runs = {}
    for f in sorted((CAMP / "verifier_runs").glob("*.json")):
        r = jl(f); runs.setdefault(r["subject_id"], {})[r["verifier_id"]] = r  # a última corrida por verificador (ordem do nome = ordem do tempo)
    vers = {jl(f).get("verifier_id", f.stem): jl(f) for f in (CAMP / "verifiers").glob("*.json")}
    claims = {c["claim_id"]: c for c in (jl(f) for f in (CAMP / "claims").glob("*.json"))}
    formal = {f["formal_id"]: f for f in (jl(p) for p in (CAMP / "formal").glob("*.json"))}
    rows = []
    for wf in sorted((CAMP / "witnesses").glob("*.json")):
        w = jl(wf); wid = wf.stem; p = w["parameters"]
        ub = [c for c in claims.values() if c["kind"] != "conjecture" and c.get("bound", {}) and c["bound"].get("direction") == "upper"
              and {k: p[k] for k in "qnR"} == c["bound"]["parameters"] and c["bound"]["value"] == p["M"] and wid in c["evidence"].get("witnesses", [])]
        c = ub[0] if ub else None
        if wid == "w-q2-n6-r1-m12":  # K_2(6,1): o witness é complementar do claim ub (fora de evidence.witnesses de propósito)
            c = claims.get("k2-6-1-ub-12")
        lc = (c or {}).get("literature_comparison", {})
        best = lc.get("melhor_registrada")
        r = runs.get(wid, {})
        lean, lean_ok, lean_decl, lean_ext = lean_state(c, formal)
        if wid == "w-q2-n6-r1-m12":  # K_2(6,1) = 12: o claim de igualdade guarda o Lean pesado; o teorema medido do 12 é o do claim ub
            c_eq = claims.get("k2-6-1-eq-12")
            lean2, ok2, decl2, ext2 = lean_state(claims.get("k2-6-1-ub-12"), formal)
            lean, lean_ok = lean2, ok2
            _, _, decl_eq, ext_eq = lean_state(c_eq, formal)
            lean_decl, lean_ext = decl_eq, ext_eq
            lean += (" | igualdade K_2(6,1)=12: " + ("MEASURED_ON_EXTERNAL_VM: " + "; ".join(ext_eq) + " (build do CoveringHeavy só na VM do autor, não refeito aqui)" if ext_eq else
                     "EXISTS_BUILD_NOT_REPRODUCED: " + "; ".join(decl_eq) + " (CoveringHeavy não construído aqui)") + "; K_2(6,1) >= 11 PROVED_MEASURED separadamente (alvo padrão)")
        st, conf, src, note = LIT.get(wid, ("?", "?", "", ""))
        cnt = {k: v["result"] for k, v in r.items()}
        autores = {k: vers.get(k, {}).get("implemented_by") for k in cnt}
        criador = (c or {}).get("created_by")
        # componentes independentes por AUTOR (a guarda da infraestrutura também usa grupo/fonte/hash; aqui só o que o snapshot consegue ler dos dados)
        passam = sorted(k for k, v in cnt.items() if v == "PASS")
        autores_validos = sorted({autores[k] for k in passam if autores[k] and autores[k] != criador})
        rows.append({
            "witness_id": wid, "q": p["q"], "n": p["n"], "R": p["R"], "size": p["M"],
            "witness_path": w["path"], "sha256_file": w["sha256"], "sha256_canonical": w["canonical_sha256"],
            "created": w.get("created"), "witness_producer": w.get("produced_by"),
            "containing_commit": commit,
            "verifier_results": cnt, "verifier_authors": autores,
            "independent_authors_passing": autores_validos,
            "independence_note": f"autor do claim: {criador}; verificadores PASS cujo autor não é o do claim: {autores_validos}; verificadores do mesmo autor contam como um só; "
                                 "agentes do mesmo modelo ≠ independência cognitiva total",
            "claim_id": c["claim_id"] if c else None, "claim_status": c["status"] if c else None,
            "equality_claim_status": claims["k2-6-1-eq-12"]["status"] if wid == "w-q2-n6-r1-m12" else None,
            "lean": lean, "lean_theorems_measured": lean_ok, "lean_theorems_declared_only": lean_decl, "lean_theorems_external_vm": lean_ext,
            "best_recorded_bound": best.get("value") if isinstance(best, dict) else best,
            "best_recorded_source": lc.get("melhor_registrada_fonte"),
            "diff_abs": ((best.get("value") if isinstance(best, dict) else best) - p["M"]) if best else None,
            "diff_pct": round(100 * ((best.get("value") if isinstance(best, dict) else best) - p["M"]) / (best.get("value") if isinstance(best, dict) else best), 2) if best else None,
            "literature_state": st, "literature_confidence": conf, "literature_source": src, "literature_note": note,
            "classification": "apparent improvement over the currently recorded bound; novelty not yet established" if lc.get("veredito") == "melhor_que_a_registrada" else (lc.get("veredito") or "igual/sem comparação"),
        })
    OUT.mkdir(exist_ok=True)
    (OUT / "SNAPSHOT.json").write_text(json.dumps({"repo_commit": commit, "rows": rows}, indent=1, ensure_ascii=False, sort_keys=True) + "\n")
    flat = [{k: (json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else v) for k, v in r.items()} for r in rows]
    with open(OUT / "SNAPSHOT.csv", "w", newline="") as fh:
        wr = csv.DictWriter(fh, fieldnames=list(flat[0])); wr.writeheader(); wr.writerows(flat)
    vids = sorted({v for r in rows for v in r["verifier_results"]})
    md = ["# Snapshot científico (gerado por tools/campaign/snapshot_covering.py)", "", f"Commit-base: `{commit}`. Fonte: dados da campanha, não texto.", "",
          "| Código | Tamanho | Estado do claim | Melhor registrada (Δ) | Verificadores (PASS/total) | Lean | Literatura |", "|---|---|---|---|---|---|---|"]
    for r in rows:
        d = f"{r['best_recorded_bound']} (−{r['diff_abs']}, {r['diff_pct']}%)" if r["best_recorded_bound"] else "—"
        vr = r["verifier_results"]
        lean_curto = "PROVED_MEASURED" if r["lean_theorems_measured"] else ("MEASURED_ON_EXTERNAL_VM" if r["lean_theorems_external_vm"] else ("EXISTS_BUILD_NOT_REPRODUCED" if r["lean_theorems_declared_only"] else "sem teorema"))
        if r["lean_theorems_measured"] and (r["lean_theorems_declared_only"] or r["lean_theorems_external_vm"]):
            lean_curto += " (+ pesado " + ("medido só em VM externa" if r["lean_theorems_external_vm"] else "declarado") + ")"
        md.append(f"| K_{r['q']}({r['n']},{r['R']}) | {r['size']} | {r['claim_status']}{(' (só ≤12; igualdade ' + r['equality_claim_status'] + ')') if r['equality_claim_status'] else ''} | {d} | {sum(v == 'PASS' for v in vr.values())}/{len(vr)} | {lean_curto} | {r['literature_state']} ({r['literature_confidence']}) |")
    md += ["", "Verificadores registrados: " + ", ".join(f"`{v}`" for v in vids) + ". Os `verify-val-*` só se aplicam a K_7(9,4) (q, n cravados no código).", "",
           "Independência: verify-py-dilation tem o autor dos claims (PASS não conta); os `verify-val-*` têm o autor de verify.c (contam junto com ele, num componente só). "
           "O teorema Lean MEDIDO vem de `#print axioms` real na campanha; `CoveringHeavy` (~9,3 h de CPU) tem UMA medição externa do autor numa VM (`_fatos/medicao_heavy_vm.json`), não refeita em segundo ambiente nem reproduzível neste container: estado MEASURED_ON_EXTERNAL_VM, abaixo de PROVED_MEASURED.", "",
           "Classificação: apparent improvement over the currently recorded bound; novelty not yet established. Nenhum código tem NOVELTY_EXTERNALLY_CONFIRMED."]
    (OUT / "SNAPSHOT.md").write_text("\n".join(md) + "\n")
    print(f"{len(rows)} códigos congelados em {OUT}")

if __name__ == "__main__":
    sys.exit(main())
