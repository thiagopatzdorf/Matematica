"""Codificação independente (indep_perfil.py: one-hot em todas as coordenadas, totalizador do
pysat, cobertura só no sentido necessário, quebra de simetria só trivial) numa amostra de perfis
de K_7(5,3) M = 16, com o kissat. Lê os registros de uma amostra (k753_amostra.py), tipos com
partes de dois dígitos lidas por k753_perfis.ler_tipo. Pula registros de cubo.

Uso: k753_indep.py AMOSTRA.jsonl DIR_TMP tempo_max_s [max_perfis]"""
import hashlib
import json
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import indep_perfil  # noqa: E402
from k753_perfis import ler_tipo  # noqa: E402


def main():
    amostra, tmp, tmax = sys.argv[1], sys.argv[2], int(sys.argv[3])
    maxp = int(sys.argv[4]) if len(sys.argv) > 4 else 10 ** 9
    feitos = 0
    for ln in open(amostra):
        r = json.loads(ln)
        if r.get("L") or r["tempo_solver_s"] > 100:  # cubos e perfis caros ficam de fora
            continue
        if feitos >= maxp:
            break
        q, n, M, smin = r["q"], r["n"], r["M"], r["smin"]
        perfil = [ler_tipo(s, q, M, smin) for s in r["tipos"]]
        f, _ = indep_perfil.codificar(q, n, M, perfil)
        txt = indep_perfil.dimacs(f, f"indep K_{q}({n},{n-2}) M={M} perfil {','.join(r['tipos'])}")
        cnf = os.path.join(tmp, f"indep753_{r['inst']}.cnf")
        open(cnf, "w").write(txt)
        t = time.time()
        c = subprocess.run([os.environ["KISSAT"], "-q", f"--time={tmax}", cnf], capture_output=True, text=True)
        res = {10: "SAT", 20: "UNSAT"}.get(c.returncode, "INDEFINIDO")
        print(json.dumps({"inst": r["inst"], "ordem": r.get("ordem", "min"), "tipos": r["tipos"],
                          "estrato": r.get("estrato"), "resultado": res, "rc": c.returncode,
                          "tempo_s": round(time.time() - t, 1), "tempo_repo_s": r["tempo_solver_s"],
                          "vars": f.nv, "clausulas": len(f.cl),
                          "sha256.cnf": hashlib.sha256(txt.encode()).hexdigest()}), flush=True)
        os.remove(cnf)
        feitos += 1


if __name__ == "__main__":
    main()
