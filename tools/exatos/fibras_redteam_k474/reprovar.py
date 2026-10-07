#!/usr/bin/env python3
"""Reprova registros do certificado do zero: regenera a CNF (fib_encode, só para regenerar), compara o
sha256, roda CaDiCaL --lrat, compara o sha256 da prova com o do registro (determinismo bit a bit),
confere com lrat-check (drat-trim 2e3b2dc) E com lrat-trim (b30f400, que também checa as cláusulas),
e, se KISSAT existir, roda o kissat (sem prova) na mesma CNF. Descarta CNF e prova no fim.

Variáveis de ambiente: CADICAL, LRAT_CHECK, LRAT_TRIM, KISSAT (opcional), TRAB (diretório de trabalho).
Uso: python3 reprovar.py CERT.jsonl.xz q n R M SAIDA.jsonl  inteiro:INST:ORDEM | cubos:INST:ORDEM | cubo:INST:ORDEM:IDX ...
"""
import hashlib
import json
import lzma
import os
import subprocess
import sys
import time

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, "..", "fibras"))
import fib_cubos  # noqa: E402
import fib_encode as enc  # noqa: E402


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()


def reprovar(r, q, n, R, M, smin, trab):
    ordem = r["ordem"]
    _, ins = enc.instancias(q, n, M, n, smin, ordem=ordem)
    pref = ins[r["inst"]]
    cnf, x, _, ts = enc.codificar(q, n, M, pref, smin, R=R)
    rot = f"K_{q}({n},{R}) M={M} k={n} s_min={smin} inst {r['inst']}: {pref}"
    base = os.path.join(trab, f"rp_{q}_{n}_{M}_{r['inst']}_{ordem}" + (f"_c{r['cubo_idx']}" if r.get("L") else ""))
    if r.get("L"):
        cubo = fib_cubos.atribuicoes_coord1(q, M, ts[0], ts[1], smin, r["L"])[r["cubo_idx"]]
        assert "".join(map(str, cubo)) == r["cubo"], "cubo_idx não corresponde à string gravada"
        for u in fib_cubos.unitarias(x, cubo):
            cnf.add(u)
        rot += f" cubo L={r['L']} #{r['cubo_idx']}: {cubo}"
    with open(base + ".cnf", "w") as f:
        f.write(cnf.dimacs([rot]))
    out = {"inst": r["inst"], "ordem": ordem, "cubo_idx": r.get("cubo_idx"), "tipos": r["tipos"],
           "cnf_sha_igual": sha(base + ".cnf") == r["sha256.cnf"], "tempo_original_s": r["tempo_solver_s"]}
    t = time.time()
    c = subprocess.run([os.environ["CADICAL"], "-q", base + ".cnf", "--lrat", "--binary=false", base + ".lrat"],
                       capture_output=True, text=True)
    out["cadical_rc"] = c.returncode
    out["cadical_s"] = round(time.time() - t, 1)
    if c.returncode == 20:
        out["veredito"] = "UNSAT"
        out["prova_sha_igual"] = sha(base + ".lrat") == r["sha256.lrat"]
        out["bytes_lrat"] = os.path.getsize(base + ".lrat")
        t = time.time()
        k = subprocess.run([os.environ["LRAT_CHECK"], base + ".cnf", base + ".lrat"], capture_output=True, text=True)
        out["lrat_check"] = "VERIFIED" if ("c VERIFIED" in k.stdout or "s VERIFIED" in k.stdout) else "FALHOU " + k.stdout[-200:]
        out["lrat_check_s"] = round(time.time() - t, 1)
        if os.environ.get("LRAT_TRIM"):
            t = time.time()
            tr = subprocess.run([os.environ["LRAT_TRIM"], "-q", "-f", "-a", base + ".cnf", base + ".lrat", base + ".trim"],
                                capture_output=True, text=True)
            out["lrat_trim_rc"] = tr.returncode
            out["lrat_trim_s"] = round(time.time() - t, 1)
            if tr.returncode == 0 and os.path.exists(base + ".trim"):
                k2 = subprocess.run([os.environ["LRAT_CHECK"], base + ".cnf", base + ".trim"], capture_output=True, text=True)
                out["lrat_check_da_prova_aparada"] = "VERIFIED" if "VERIFIED" in k2.stdout and "NOT" not in k2.stdout else "FALHOU"
    elif c.returncode == 10:
        out["veredito"] = "SAT"
    else:
        out["veredito"] = "INDEFINIDO"
    if os.environ.get("KISSAT"):
        t = time.time()
        k = subprocess.run([os.environ["KISSAT"], "-q", base + ".cnf"], capture_output=True, text=True)
        out["kissat_rc"] = k.returncode
        out["kissat_s"] = round(time.time() - t, 1)
    for ext in (".cnf", ".lrat", ".trim"):
        if os.path.exists(base + ext):
            os.remove(base + ext)
    return out


def main():
    arq, q, n, R, M, saida, *picks = sys.argv[1:]
    q, n, R, M = map(int, (q, n, R, M))
    smin = enc.fibra_minima(q, n, R, M)
    regs = [json.loads(l) for l in lzma.open(arq, "rt")]
    trab = os.environ.get("TRAB", "/tmp")
    for p in picks:
        partes = p.split(":")
        tipo, inst, ordem = partes[0], int(partes[1]), partes[2]
        if tipo == "inteiro":
            alvos = [r for r in regs if not r.get("L") and r["inst"] == inst and r["ordem"] == ordem]
        elif tipo == "cubos":
            alvos = [r for r in regs if r.get("L") and r["inst"] == inst and r["ordem"] == ordem]
        else:
            alvos = [r for r in regs if r.get("L") and r["inst"] == inst and r["ordem"] == ordem and r["cubo_idx"] == int(partes[3])]
        assert alvos, p
        for r in sorted(alvos, key=lambda r: r.get("cubo_idx") or 0):
            o = reprovar(r, q, n, R, M, smin, trab)
            with open(saida, "a") as f:
                f.write(json.dumps(o) + "\n")
            print(json.dumps(o), flush=True)


if __name__ == "__main__":
    main()
