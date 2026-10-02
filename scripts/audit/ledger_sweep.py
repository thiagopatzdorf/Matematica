#!/usr/bin/env python3
"""Ledger auditável da varredura exactT/exactT2 das classes de [9,3]_7 (K_7(9,4), 3 classes laterais).

Uso: ledger_sweep.py DIR_FAZENDA [--saida ledger.jsonl] [--local-import LISTA_DIR]
  DIR_FAZENDA contém classes_sorted.jsonl e os diretórios fz-01, fz-02, ... com c_L.out.

Para cada L em 1..N (N = linhas de classes_sorted.jsonl) exige EXATAMENTE um resultado:
  - a última linha do arquivo é JSON com "exact": true e T = 8;
  - o "A" do arquivo é o "A" da linha L da lista (a classe avaliada é a classe pedida);
  - registra: L, A, sha256(A), nBc, órfãs (-1 = nenhum trio com <= T), trios listados, shard (diretório),
    horário (mtime), versão inferida pelo período e sha256 do arquivo.
Duplicatas (o mesmo L em dois diretórios) são aceitas só se o resultado for idêntico, e contadas.
Sai com código 1 se faltar classe, sobrar arquivo estranho, houver divergência ou A trocado.
"""
import argparse
import datetime as dt
import glob
import hashlib
import json
import os
import re
import sys

# Períodos de cada binário (UTC, 2026-10-02) -- docs/audit/exactT2_correctness.md, "Proveniência".
PERIODOS = [
    ("2026-10-02T11:50", "2026-10-02T13:03:33", "exactT m=200", "be52cc2"),
    ("2026-10-02T13:03:33", "2026-10-02T13:36:00", "exactT2 sym=1", "75a844b"),
    ("2026-10-02T13:37:00", "2026-10-02T23:59", "exactT2 sym=1 SWAR", "3c4ed99"),
]


def versao(mtime, local):
    if local:
        return "exactT2 sym=1 (contêiner local)", "75a844b"
    t = dt.datetime.fromtimestamp(mtime, dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
    for a, b, v, c in PERIODOS:
        if a <= t < b:
            return v, c
    return "desconhecida", None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dir")
    ap.add_argument("--saida", default="ledger.jsonl")
    ap.add_argument("--local-import", default=None, help="diretório com as cópias dos resultados locais")
    a = ap.parse_args()
    classes = [json.loads(l) for l in open(os.path.join(a.dir, "classes_sorted.jsonl"))]
    N = len(classes)
    locais = set()
    if a.local_import:
        locais = {os.path.basename(f) for f in glob.glob(os.path.join(a.local_import, "c_*.out"))}
    achados = {}
    estranhos, divergentes, a_trocado, nao_exato, dup = [], [], [], [], 0
    for f in sorted(glob.glob(os.path.join(a.dir, "fz-*", "*"))):
        nome = os.path.basename(f)
        m = re.fullmatch(r"c_(\d+)\.out", nome)
        if not m:
            if nome != "DONE":
                estranhos.append(f)
            continue
        L = int(m[1])
        if not 1 <= L <= N:
            estranhos.append(f)
            continue
        linhas = open(f).read().splitlines()
        try:
            d = json.loads(linhas[-1])
        except Exception:
            nao_exato.append(f)
            continue
        if d.get("exact") is not True or d.get("T") != 8:
            nao_exato.append(f)
            continue
        if d["A"] != classes[L - 1]["A"]:
            a_trocado.append((L, f))
            continue
        trios = [l for l in linhas if l.startswith("TRIO")]
        reg = {
            "L": L, "A": d["A"], "sha256_A": hashlib.sha256(d["A"].encode()).hexdigest(),
            "nBc": d["nBc"], "orphans": d["orphans"], "T": d["T"], "trios": len(trios),
            "coset_syndromes": d["coset_syndromes"], "shard": os.path.basename(os.path.dirname(f)),
            "mtime_utc": dt.datetime.fromtimestamp(os.path.getmtime(f), dt.timezone.utc).isoformat(),
            "sha256_file": hashlib.sha256(open(f, "rb").read()).hexdigest(),
        }
        reg["versao"], reg["commit"] = versao(os.path.getmtime(f), nome in locais)
        if d["nBc"] != classes[L - 1]["nBc"]:
            divergentes.append((L, "nBc", f))
        if L in achados:
            dup += 1
            ant = achados[L]
            if (ant["orphans"], ant["nBc"]) != (reg["orphans"], reg["nBc"]):
                divergentes.append((L, "duplicata com resultado diferente", f))
            continue
        achados[L] = reg
    faltando = [L for L in range(1, N + 1) if L not in achados]
    with open(a.saida, "w") as out:
        for L in sorted(achados):
            out.write(json.dumps(achados[L], ensure_ascii=False) + "\n")
    resumo = {
        "expected_classes": N, "processed_classes": len(achados), "missing": len(faltando),
        "duplicates": dup, "divergent": len(divergentes), "A_mismatch": len(a_trocado),
        "not_exact_or_bad_T": len(nao_exato), "stray_files": len(estranhos),
        "sha256_classes_sorted": hashlib.sha256(open(os.path.join(a.dir, "classes_sorted.jsonl"), "rb").read()).hexdigest(),
        "sha256_ledger": hashlib.sha256(open(a.saida, "rb").read()).hexdigest(),
    }
    hist = {}
    for r in achados.values():
        hist[r["orphans"]] = hist.get(r["orphans"], 0) + 1
    resumo["histogram_T8"] = {str(k): v for k, v in sorted(hist.items())}
    vers = {}
    for r in achados.values():
        vers[r["versao"]] = vers.get(r["versao"], 0) + 1
    resumo["por_versao"] = vers
    print(json.dumps(resumo, ensure_ascii=False, indent=1))
    for x in (faltando[:20], divergentes[:20], a_trocado[:20], nao_exato[:20], estranhos[:20]):
        if x:
            print("DETALHE:", x, file=sys.stderr)
    ok = not (faltando or divergentes or a_trocado or nao_exato or estranhos)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
