"""Reconfere uma amostra dos certificados de um JSONL do rodar.py: regenera a CNF com o
codificador auditado (mesmo rótulo do rodar.py), compara o sha256 com o do JSONL, roda o CaDiCaL
com --lrat, compara o sha256 da prova e confere a prova com DOIS verificadores: lrat-check
(drat-trim) e cake_lpr (verificado em CakeML). Binários por variável de ambiente: CADICAL,
LRAT_CHECK, CAKE_LPR.

Uso: lrat_amostra.py DIR_FIBRAS ARQ.jsonl DIR_TMP inst1 inst2 ..."""
import hashlib
import json
import os
import subprocess
import sys
import time


def sha(caminho):
    h = hashlib.sha256()
    with open(caminho, "rb") as f:
        for bloco in iter(lambda: f.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()


def main():
    d, jsonl, tmp = sys.argv[1:4]
    insts = [int(x) for x in sys.argv[4:]]
    sys.path.insert(0, d)
    import fib_encode as enc
    regs = {}
    for l in open(jsonl):
        r = json.loads(l)
        regs[r["inst"]] = r
    for i in insts:
        r = regs[i]
        q, n, M, k, smin = r["q"], r["n"], r["M"], r["k"], r["smin"]
        _, ins = enc.instancias(q, n, M, k, smin)
        pref = ins[i]
        assert ["".join(map(str, t)) for t in pref] == r["tipos"]
        cnf, *_ = enc.codificar(q, n, M, pref, smin)
        rot = f"K_{q}({n},{n-2}) M={M} k={k} s_min={smin} inst {i}: {pref}"
        base = os.path.join(tmp, f"rt_{q}{n}{M}_{i}")
        open(base + ".cnf", "w").write(cnf.dimacs([rot]))
        out = {"inst": i, "tipos": r["tipos"], "sha_cnf_ok": sha(base + ".cnf") == r["sha256.cnf"]}
        t = time.time()
        c = subprocess.run([os.environ["CADICAL"], "-q", base + ".cnf", "--lrat", "--binary=false", base + ".lrat"],
                           capture_output=True, text=True)
        out["cadical_rc"] = c.returncode
        out["cadical_s"] = round(time.time() - t, 1)
        if c.returncode == 20:
            out["sha_lrat_igual"] = sha(base + ".lrat") == r["sha256.lrat"]
            t = time.time()
            c = subprocess.run([os.environ["LRAT_CHECK"], base + ".cnf", base + ".lrat"], capture_output=True, text=True)
            out["lrat_check"] = "VERIFIED" if "VERIFIED" in c.stdout and "NOT VERIFIED" not in c.stdout else c.stdout[-200:]
            out["lrat_check_s"] = round(time.time() - t, 1)
            t = time.time()
            c = subprocess.run([os.environ["CAKE_LPR"], base + ".cnf", base + ".lrat"], capture_output=True, text=True)
            out["cake_lpr"] = c.stdout.strip().splitlines()[-1] if c.stdout.strip() else c.stderr[-200:]
            out["cake_lpr_s"] = round(time.time() - t, 1)
        for ext in (".cnf", ".lrat"):
            if os.path.exists(base + ext):
                os.remove(base + ext)
        print(json.dumps(out), flush=True)


if __name__ == "__main__":
    main()
