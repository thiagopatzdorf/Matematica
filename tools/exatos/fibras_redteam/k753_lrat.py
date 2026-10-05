"""Reconfere registros de K_7(5,3) M = 16 (perfis inteiros e cubos): regenera a CNF com o
codificador auditado (mesmo rótulo do rodar.py, inclusive `ordem` e cubo), compara sha256 com o
registro, roda CaDiCaL --lrat, compara o sha256 da prova (bit a bit) e confere com lrat-check e
cake_lpr. Binários: CADICAL, LRAT_CHECK, CAKE_LPR.

Uso: k753_lrat.py DIR_FIBRAS AMOSTRA.jsonl DIR_TMP [--max-bytes B]"""
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


def cnf_do_registro(enc, cubos, r):
    q, n, M, k, smin, i = r["q"], r["n"], r["M"], r["k"], r["smin"], r["inst"]
    ordem = r.get("ordem", "min")
    _, ins = enc.instancias(q, n, M, k, smin, ordem=ordem)
    pref = ins[i]
    assert ["".join(map(str, t)) for t in pref] == r["tipos"], (i, ordem)
    cnf, x, sim0, ts = enc.codificar(q, n, M, pref, smin)
    rot = f"K_{q}({n},{n-2}) M={M} k={k} s_min={smin} inst {i}: {pref}"
    if r.get("L"):
        cubo = cubos.atribuicoes_coord1(q, M, ts[0], ts[1], smin, r["L"])[r["cubo_idx"]]
        assert "".join(map(str, cubo)) == r["cubo"]
        for u in cubos.unitarias(x, cubo):
            cnf.add(u)
        rot += f" cubo L={r['L']} #{r['cubo_idx']}: {cubo}"
    return cnf.dimacs([rot])


def main():
    d, amostra, tmp = sys.argv[1:4]
    maxb = int(sys.argv[sys.argv.index("--max-bytes") + 1]) if "--max-bytes" in sys.argv else 1 << 62
    sys.path.insert(0, d)
    import fib_cubos
    import fib_encode as enc
    for ln in open(amostra):
        r = json.loads(ln)
        out = {"inst": r["inst"], "ordem": r.get("ordem", "min"), "cubo_idx": r.get("cubo_idx"),
               "tipos": r["tipos"], "estrato": r.get("estrato")}
        if r.get("bytes.lrat", 0) > maxb:
            out["pulado"] = f"prova de {r['bytes.lrat']} bytes > {maxb}"
            print(json.dumps(out), flush=True)
            continue
        base = os.path.join(tmp, f"k753_{out['ordem']}_{r['inst']}_{r.get('cubo_idx')}")
        open(base + ".cnf", "w").write(cnf_do_registro(enc, fib_cubos, r))
        out["sha_cnf_igual"] = sha(base + ".cnf") == r["sha256.cnf"]
        t = time.time()
        c = subprocess.run([os.environ["CADICAL"], "-q", base + ".cnf", "--lrat", "--binary=false", base + ".lrat"],
                           capture_output=True, text=True)
        out["cadical_rc"] = c.returncode
        out["cadical_s"] = round(time.time() - t, 1)
        if c.returncode == 20:
            out["sha_lrat_igual"] = sha(base + ".lrat") == r["sha256.lrat"]
            out["bytes.lrat"] = os.path.getsize(base + ".lrat")
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
