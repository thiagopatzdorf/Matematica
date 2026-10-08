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
 "w-q7-n9-r4-m1137": ("NO_PREDECESSOR_FOUND_IN_REVIEWED_SOURCES", "média", "STATE_OF_ART.md (conferido) + _literatura/profunda", "superado pelo nosso 1134; risco: ADS q=7 931 (<1137) condicional a componentes normais, não verificado; lacunas do STATE_OF_ART (Scholar, bases pagas, teses, periódico)"),
 "w-q7-n9-r4-m1141": ("NO_PREDECESSOR_FOUND_IN_REVIEWED_SOURCES", "média", "STATE_OF_ART.md (conferido) + _literatura/profunda", "superado pelo nosso 1134; mesmo risco ADS 931 condicional"),
 "w-q7-n9-r4-m1285": ("NO_PREDECESSOR_FOUND_IN_REVIEWED_SOURCES", "média", "_literatura/profunda", "risco: ADS q=7 (931/1225/1344) condicional a componentes normais, não verificado; superado pelo nosso 1134"),
 "w-q7-n9-r4-m1351": ("NO_PREDECESSOR_FOUND_IN_REVIEWED_SOURCES", "baixa-média", "_literatura/profunda", "superado pelo nosso 1134"),
 "w-q7-n8-r3-m1887": ("NO_PREDECESSOR_FOUND_IN_REVIEWED_SOURCES", "média", "_literatura/profunda", "risco: ADS (3,1)+(6,2)=1225 condicional a normalidade"),
 "w-q7-n8-r3-m1893": ("NO_PREDECESSOR_FOUND_IN_REVIEWED_SOURCES", "média", "_literatura/profunda", "superado pelo nosso 1887"),
 "w-q5-n10-r4-m625": ("AMBIGUOUS", "baixa", "_literatura/profunda_c", "código linear [10,4,5]_5; tabela ℓ_5(6,4) não encontrada; não alegar novidade"),
 "w-q5-n7-r2-m500": ("AMBIGUOUS", "média", "_literatura/profunda_b", "ADS 478,4 condicional"),
 "w-q4-n10-r4-m192": ("AMBIGUOUS", "média-baixa", "_literatura/profunda_b", "ADS dá exatamente 192, condicional"),
 "w-q5-n9-r4-m250": ("AMBIGUOUS", "média", "_literatura/profunda_b", "ADS 245 condicional"),
 "w-q5-n9-r3-m1250": ("NO_PREDECESSOR_FOUND_IN_REVIEWED_SOURCES", "média", "_literatura/profunda_b", "ADS dá 1275 > nosso"),
 "w-q5-n9-r5-m50": ("NO_PREDECESSOR_FOUND_IN_REVIEWED_SOURCES", "média", "_literatura/profunda_b", "ADS dá 51 > nosso"),
 "w-q2-n6-r1-m12": ("PREDECESSOR_FOUND", "alta", "_literatura/profunda_b", "igualdade com valor clássico (Stanton–Kalbfleisch 1968, não lido; exatidão provada por busca exaustiva própria)"),
 "w-q7-n9-r4-m1134": ("NO_PREDECESSOR_FOUND_IN_REVIEWED_SOURCES", "média", "STATE_OF_ART.md (2026-10-02, anterior ao 1134: não achou nada <= 1137) + _literatura/profunda", "menor código da célula; risco: ADS q=7 931 (<1134) condicional a componentes normais, não verificado; lacunas do STATE_OF_ART (Scholar, bases pagas, teses, periódico)"),
}

def literatura_padrao(lc):
    """Estado de literatura de um código SEM linha à mão em LIT (ex.: entrou no main depois da revisão Lit-CC): derivado da comparação numérica contra a literatura REGISTRADA
    na campanha, com confiança baixa e a ressalva de que a fonte primária não foi relida. Nunca NOVELTY_EXTERNALLY_CONFIRMED (isso não se autoatribui)."""
    v = (lc or {}).get("veredito")
    fontes = "; ".join((lc or {}).get("melhor_registrada_fonte") or []) or "sem registro"
    if v == "melhor_que_a_registrada":
        return ("NO_PREDECESSOR_FOUND_IN_REVIEWED_SOURCES", "baixa", f"literature/ da campanha ({fontes})",
                "derivado da comparação com a literatura registrada; fontes primárias das chaves do Kéri e trabalhos pós-2011 não lidos (res-confirmar-<célula>)")
    if v == "igual":
        return ("PREDECESSOR_FOUND", "média", f"literature/ da campanha ({fontes})", "igual ao valor registrado")
    return ("?", "?", "", "sem comparação com a literatura registrada")

KRUNS = {}  # execuções externas do kernel (kernel_runs/), preenchido em main()

def jl(p): return json.loads(Path(p).read_text())

def formal_medido(f):
    """Registro formal MEDIDO e limpo (mesma conferência da fronteira do Lean, sem importar a infraestrutura)."""
    return (f.get("axioms") is not None and set(f["axioms"]) <= AXIOMAS_ESPERADOS and f.get("sorry_free") is True and f.get("clean_build") is True
            and all(f.get(k) for k in ("lean_version", "mathlib_commit", "repo_commit")))

_HEX64 = __import__("re").compile(r"^[0-9a-f]{64}$")

def nivel_kernel_run(r):
    """Nível de UMA execução externa lida do registro (sem importar a infraestrutura). É APROXIMAÇÃO da regra de factory_cauteloso.matematica.kernel.avaliar:
    KERNEL_VERIFIED só com o log persistido, hash de 64 hex e uri E proveniência capturada pela ferramenta (host com id numérico de instância; toolchain
    com árvore limpa); senão EXTERNAL_RUN_REPORTED. Quem decide é a infraestrutura (`... camadas`); o teste
    tests/test_campaign_kernel_migration.py confere que as duas concordam quando a infraestrutura está disponível."""
    lg = r.get("raw_log") or {}
    hp = (r.get("host") or {}).get("provenance") or {}
    tp = r.get("toolchain_provenance") or {}
    capturada = (hp.get("captured_by_tool") is True and bool(hp.get("provider")) and bool(hp.get("project_id")) and bool(hp.get("numeric_instance_id"))
                 and tp.get("captured_by_tool") is True and tp.get("tree_clean") is True)
    ok = lg.get("persisted") is True and bool(_HEX64.match(str(lg.get("sha256") or ""))) and bool(lg.get("uri")) and capturada
    return "KERNEL_VERIFIED" if ok else "EXTERNAL_RUN_REPORTED"

def nivel_kernel_claim(claim_id):
    """Nível do eixo do kernel de um claim, lido de kernel_runs/ (aproximação da regra de `kernel.nivel_do_claim`, igual a `nivel_kernel_run`):
    NONE sem execução que o cubra; EXTERNAL_RUN_REPORTED / KERNEL_VERIFIED pelo melhor nível; KERNEL_INDEPENDENTLY_REPRODUCED se há duas execuções
    KERNEL_VERIFIED com host.id, run_id e log distintos, mesmo commit e instâncias numéricas distintas. O teste de migração confere contra a infraestrutura."""
    rs = [r for r in KRUNS.values() if claim_id in (r.get("claim_ids") or [])]
    if not rs:
        return "NONE"
    kv = [r for r in rs if nivel_kernel_run(r) == "KERNEL_VERIFIED"]
    for i, a in enumerate(kv):
        for b in kv[i + 1:]:
            ia, ib = ((x["host"].get("provenance") or {}).get("numeric_instance_id") for x in (a, b))
            if (a["run_id"] != b["run_id"] and a["host"]["id"] != b["host"]["id"] and ia != ib and a["raw_log"]["sha256"] != b["raw_log"]["sha256"]
                    and a["commit_sha"] == b["commit_sha"]):
                return "KERNEL_INDEPENDENTLY_REPRODUCED"
    return "KERNEL_VERIFIED" if kv else "EXTERNAL_RUN_REPORTED"

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
        niveis = {f["formal_id"]: nivel_kernel_run(KRUNS[f["kernel_run"]]) if f.get("kernel_run") in KRUNS else "sem kernel_run" for f in externos}
        partes.append("EXTERNAL_KERNEL_RUN: " + "; ".join(f"{f['theorem']} (Kernel evidence: {niveis[f['formal_id']]}; axiomas {sorted(f['measured_external']['axioms'])} e build {f['measured_external']['jobs']} jobs/{f['measured_external']['folhas_falhou']} falhas, "
                      f"relato do autor em VM, commit {f['measured_external']['repo_commit'][:7]}, log sha256 {f['measured_external']['log_sha256_prefixo']}…, log bruto NÃO persistido, host só declarado (id da instância NÃO capturado); NÃO é reprodução independente; NÃO medido pela campanha)" for f in externos))
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
    KRUNS.clear()
    KRUNS.update({r["run_id"]: r for r in (jl(p) for p in sorted((CAMP / "kernel_runs").glob("*.json")))} if (CAMP / "kernel_runs").is_dir() else {})
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
            lean += (" | igualdade K_2(6,1)=12: " + ("EXTERNAL_KERNEL_RUN (Kernel evidence: EXTERNAL_RUN_REPORTED; log bruto NÃO persistido; NÃO é reprodução independente): " + "; ".join(ext_eq) + " (build do CoveringHeavy só na VM do autor, não refeito aqui)" if ext_eq else
                     "EXISTS_BUILD_NOT_REPRODUCED: " + "; ".join(decl_eq) + " (CoveringHeavy não construído aqui)") + "; K_2(6,1) >= 11 PROVED_MEASURED separadamente (alvo padrão)")
        kn = nivel_kernel_claim(c["claim_id"]) if c else "NONE"
        if lean_ok and kn != "NONE":  # execuções de kernel em VM que cobrem um teorema medido aqui: o nível é do eixo do kernel, nunca do claim
            lean += f" | Kernel evidence: {kn} (execuções em VM; ver kernel_runs/ e _fatos/TESTE_PONTA_A_PONTA.md; 'capturada' não é 'atestada')"
        st, conf, src, note = LIT.get(wid) or literatura_padrao(lc)
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
            "lean": lean, "kernel_evidence": kn, "lean_theorems_measured": lean_ok, "lean_theorems_declared_only": lean_decl, "lean_theorems_external_vm": lean_ext,
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
          "| Código | Tamanho | Claim state | Melhor registrada (Δ) | Verificadores (PASS/total) | Lean (Kernel evidence) | Literatura |", "|---|---|---|---|---|---|---|"]
    for r in rows:
        d = f"{r['best_recorded_bound']} (−{r['diff_abs']}, {r['diff_pct']}%)" if r["best_recorded_bound"] else "—"
        vr = r["verifier_results"]
        lean_curto = "PROVED_MEASURED" if r["lean_theorems_measured"] else ("Kernel evidence: EXTERNAL_RUN_REPORTED" if r["lean_theorems_external_vm"] else ("EXISTS_BUILD_NOT_REPRODUCED" if r["lean_theorems_declared_only"] else "sem teorema"))
        if r["lean_theorems_measured"] and (r["lean_theorems_declared_only"] or r["lean_theorems_external_vm"]):
            lean_curto += " (+ pesado " + ("relato de VM externa, log não persistido" if r["lean_theorems_external_vm"] else "declarado") + ")"
        md.append(f"| K_{r['q']}({r['n']},{r['R']}) | {r['size']} | {r['claim_status']}{(' (só ≤12; igualdade ' + r['equality_claim_status'] + ')') if r['equality_claim_status'] else ''} | {d} | {sum(v == 'PASS' for v in vr.values())}/{len(vr)} | {lean_curto} | {r['literature_state']} ({r['literature_confidence']}) |")
    md += ["", "Verificadores registrados: " + ", ".join(f"`{v}`" for v in vids) + ". Os `verify-val-*` só se aplicam a K_7(9,4) (q, n cravados no código).", "",
           "Independência: verify-py-dilation tem o autor dos claims (PASS não conta); os `verify-val-*` têm o autor de verify.c (contam junto com ele, num componente só). "
           "O teorema Lean MEDIDO vem de `#print axioms` real na campanha; `CoveringHeavy` (~9,3 h de CPU) tem UMA medição externa do autor numa VM (`_fatos/medicao_heavy_vm.json`), não refeita em segundo ambiente nem reproduzível neste container, e o log bruto não foi persistido nem o id da instância capturado: Kernel evidence: EXTERNAL_RUN_REPORTED (eixo do kernel, abaixo de KERNEL_VERIFIED, que exige log guardado com hash de 64 hex e proveniência capturada pela ferramenta; muito abaixo de KERNEL_INDEPENDENTLY_REPRODUCED), abaixo de PROVED_MEASURED. Claim state: nenhum estado de claim mudou por isso.", "",
           "Classificação: apparent improvement over the currently recorded bound; novelty not yet established. Nenhum código tem NOVELTY_EXTERNALLY_CONFIRMED."]
    (OUT / "SNAPSHOT.md").write_text("\n".join(md) + "\n")
    print(f"{len(rows)} códigos congelados em {OUT}")

if __name__ == "__main__":
    sys.exit(main())
