"""Roda a codificação independente (indep_perfil.py) com o kissat numa amostra de perfis de um
JSONL de certificados e grava uma linha JSON por perfil (resultado, tempo, sha256 da CNF).
Binário por variável de ambiente KISSAT.

Uso: indep_amostra.py ARQ.jsonl DIR_TMP tempo_max_s inst1 inst2 ... > saida.jsonl"""
import hashlib
import json
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import indep_perfil  # noqa: E402


def main():
    jsonl, tmp, tmax = sys.argv[1], sys.argv[2], int(sys.argv[3])
    regs = {}
    for l in open(jsonl):
        r = json.loads(l)
        regs[r["inst"]] = r
    for i in map(int, sys.argv[4:]):
        r = regs[i]
        perfil = [tuple(int(ch) for ch in t) for t in r["tipos"]]
        f, _ = indep_perfil.codificar(r["q"], r["n"], r["M"], perfil)
        txt = indep_perfil.dimacs(f, f"indep K_{r['q']}({r['n']},{r['n']-2}) M={r['M']} perfil {','.join(r['tipos'])}")
        cnf = os.path.join(tmp, f"indep_{i}.cnf")
        open(cnf, "w").write(txt)
        t = time.time()
        c = subprocess.run([os.environ["KISSAT"], "-q", f"--time={tmax}", cnf], capture_output=True, text=True)
        res = {10: "SAT", 20: "UNSAT"}.get(c.returncode, "INDEFINIDO")
        print(json.dumps({"inst": i, "tipos": r["tipos"], "resultado": res, "rc": c.returncode,
                          "tempo_s": round(time.time() - t, 1), "tempo_repo_s": r["tempo_solver_s"],
                          "vars": f.nv, "clausulas": len(f.cl),
                          "sha256.cnf": hashlib.sha256(txt.encode()).hexdigest()}), flush=True)
        os.remove(cnf)


if __name__ == "__main__":
    main()
