#!/usr/bin/env python3
"""Roda as instâncias de K_q(n, n-2) com M palavras (fib_encode) e confere as provas LRAT.

Igual a `tools/exatos/k742/rodar.py`, generalizado para (q, n, k): uma linha JSON por
instância. Com `--prova`, CaDiCaL `--lrat` + `lrat-check`; `--lrat-py` também passa a prova
pelo verificador Python do k742 (lento: só para provas pequenas ou amostras). Instância SAT:
o código é decodificado, gravado e conferido em todo Z_q^n.

Variáveis de ambiente: CADICAL, KISSAT, LRAT_CHECK.

Uso:
  python3 tools/exatos/fibras/rodar.py --q 5 --n 5 --M 8 --dir v/ --prova
  python3 tools/exatos/fibras/rodar.py --q 7 --n 5 --M 16 --k 2 --dir s/ --prova --descartar -j 8
"""
import argparse
import gzip
import importlib.util
import itertools
import json
import os
import shutil
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import fib_cubos  # noqa: E402
import fib_encode as enc  # noqa: E402


def _mod(nome, caminho):
    spec = importlib.util.spec_from_file_location(nome, caminho)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


K742 = os.path.join(AQUI, "..", "k742")
_rk = _mod("k742_rodar", os.path.join(K742, "rodar.py"))
binario, sha, intervalo = _rk.binario, _rk.sha, _rk.intervalo


def cobre(q, n, palavras, R=None):
    R = n - 2 if R is None else R
    for x in itertools.product(range(q), repeat=n):
        if not any(sum(a != b for a, b in zip(x, c)) <= R for c in palavras):
            return False
    return True


def lrat_py(cnf, prova):
    r = subprocess.run([sys.executable, os.path.join(K742, "lrat.py"), cnf, prova],
                       capture_output=True, text=True)
    return "VERIFICADO" if "VERIFICADO" in r.stdout and r.returncode == 0 else ("FALHOU: " + r.stdout[-200:] + r.stderr[-200:])


def uma(args):
    q, n, M, k, smin, idx, d, prova, solver, tempo, descartar, usar_py, L, ci, sem, ordem = args[:16]
    R = args[16] if len(args) > 16 else n - 2
    _, ins = enc.instancias(q, n, M, k, smin, ordem=ordem)
    pref = ins[idx]
    cnf, x, sim0, ts = enc.codificar(q, n, M, pref, smin, lex="g" not in sem, blocos_h="h" not in sem, R=R)
    base = os.path.join(d, f"K{q}_{n}_{R}_M{M}_k{k}{'_omax' if ordem == 'max' else ''}_i{idx:06d}" + (f"_sem{sem}" if sem else ""))
    rot = f"K_{q}({n},{R}) M={M} k={k} s_min={smin} inst {idx}: {pref}" + (f" sem ({sem})" if sem else "")
    cubo = None
    if L:
        cubo = fib_cubos.atribuicoes_coord1(q, M, ts[0], ts[1], smin, L, blocos_h="h" not in sem)[ci]
        for u in fib_cubos.unitarias(x, cubo):
            cnf.add(u)
        base += f"_L{L}_c{ci:06d}"
        rot += f" cubo L={L} #{ci}: {cubo}"
    with open(base + ".cnf", "w") as f:
        f.write(cnf.dimacs([rot]))
    reg = {"q": q, "n": n, **({"R": R} if R != n - 2 else {}), "M": M, "k": k, "smin": smin, "inst": idx, "sem": sem, "ordem": ordem,
           "tipos": ["".join(map(str, t)) for t in pref], "vars": cnf.nv, "clausulas": len(cnf.cl)}
    if L:
        reg.update(L=L, cubo_idx=ci, cubo="".join(map(str, cubo)))
    t0 = time.time()
    if solver == "kissat" and not prova:
        cmd = [binario("KISSAT", "kissat"), "-q", f"--time={tempo}", base + ".cnf"]
    else:
        cmd = [binario("CADICAL", "cadical"), "-q", "-t", str(tempo), base + ".cnf"]
        if prova:
            cmd += ["--lrat", "--binary=false", base + ".lrat"]
    r = subprocess.run(cmd, capture_output=True, text=True)
    reg["tempo_solver_s"] = round(time.time() - t0, 3)
    reg["rc"] = r.returncode
    if r.returncode == 20:
        reg["resultado"] = "UNSAT"
        if prova:
            t1 = time.time()
            c = subprocess.run([binario("LRAT_CHECK", "lrat-check"), base + ".cnf", base + ".lrat"],
                               capture_output=True, text=True)
            ok = "c VERIFIED" in c.stdout or "s VERIFIED" in c.stdout
            reg["lrat_check"] = "VERIFIED" if ok else ("FALHOU: " + c.stdout[-300:])
            reg["tempo_check_s"] = round(time.time() - t1, 3)
            if usar_py:
                t2 = time.time()
                reg["lrat_py"] = lrat_py(base + ".cnf", base + ".lrat")
                reg["tempo_lrat_py_s"] = round(time.time() - t2, 3)
            for ext in (".cnf", ".lrat"):
                reg["bytes" + ext] = os.path.getsize(base + ext)
                reg["sha256" + ext] = sha(base + ext)
                if descartar:
                    os.remove(base + ext)
                    continue
                with open(base + ext, "rb") as fi, gzip.open(base + ext + ".gz", "wb", 6) as fo:
                    shutil.copyfileobj(fi, fo)
                os.remove(base + ext)
        else:
            os.remove(base + ".cnf")
    elif r.returncode == 10:
        reg["resultado"] = "SAT"
        modelo = [int(t) for ln in r.stdout.splitlines() if ln.startswith("v ")
                  for t in ln[2:].split()]
        pal = enc.decodificar(modelo, x, sim0, q, n, M)
        reg["codigo"] = ["".join(map(str, w)) for w in pal]
        reg["cobre"] = cobre(q, n, pal, R)
        with open(base + ".codigo.txt", "w") as f:
            f.write("\n".join(reg["codigo"]) + "\n")
        os.remove(base + ".cnf")
    else:
        reg["resultado"] = "INDEFINIDO"
        os.remove(base + ".cnf")
        if os.path.exists(base + ".lrat"):
            os.remove(base + ".lrat")
    return reg


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--q", type=int, required=True)
    ap.add_argument("--n", type=int, required=True)
    ap.add_argument("--M", type=int, required=True)
    ap.add_argument("--k", type=int)
    ap.add_argument("--R", type=int, help="raio (padrão: n - 2); R < n - 2 usa projeções de t-uplas")
    ap.add_argument("--smin", type=int, help="força s_min (validação com lema enfraquecido)")
    ap.add_argument("--dir", required=True)
    ap.add_argument("--inst", default="")
    ap.add_argument("--prova", action="store_true")
    ap.add_argument("--descartar", action="store_true")
    ap.add_argument("--lrat-py", action="store_true")
    ap.add_argument("--solver", default="cadical", choices=["cadical", "kissat"])
    ap.add_argument("--tempo", type=int, default=100000)
    ap.add_argument("-j", type=int, default=os.cpu_count())
    ap.add_argument("--cubos", type=int, default=0,
                    help="divide cada instância em cubos pela coordenada 1 das L primeiras palavras")
    ap.add_argument("--ordem", default="min", choices=["min", "max"],
                    help="tipo da coordenada 0: menor (k742) ou maior simetria residual")
    ap.add_argument("--sem", default="", help="controle: omite quebras novas (g = lexicográfica, h = blocos)")
    ap.add_argument("--pular", nargs="*", default=[],
                    help="JSONL já feitos: pula perfis (como multiconjunto de tipos) com UNSAT conferido; "
                         "vale entre ordens diferentes, porque cada perfil é completo sozinho")
    ap.add_argument("--fatia", default="", help="r/m: só instâncias com índice = r (mod m)")
    ap.add_argument("--dificeis-primeiro", action="store_true",
                    help="começa pelos perfis de tipos mais equilibrados (maior simetria residual), "
                         "que são os lentos: evita a cauda no fim")
    ap.add_argument("--faceis-primeiro", action="store_true",
                    help="o contrário de --dificeis-primeiro (para duas VMs se encontrarem no meio)")
    ap.add_argument("--excluir", default="", help="índices a não rodar aqui (ex.: os que outra VM roda inteiros)")
    ap.add_argument("--cubos-sel", default="", help="subconjunto dos cubos (ex.: 0-99)")
    a = ap.parse_args()
    k = a.k or a.n
    R = a.n - 2 if a.R is None else a.R
    smin = a.smin if a.smin is not None else enc.fibra_minima(a.q, a.n, R, a.M)
    os.makedirs(a.dir, exist_ok=True)
    _, ins = enc.instancias(a.q, a.n, a.M, k, smin, ordem=a.ordem)
    idxs = intervalo(a.inst, len(ins))
    if a.excluir:
        fora = set(intervalo(a.excluir, len(ins)))
        idxs = [i for i in idxs if i not in fora]
    if a.fatia:
        r_, m_ = map(int, a.fatia.split("/"))
        idxs = [i for i in idxs if i % m_ == r_]
    if a.dificeis_primeiro:
        idxs.sort(key=lambda i: -sum(enc.simetria_residual(t) for t in ins[i]))
    elif a.faceis_primeiro:
        idxs.sort(key=lambda i: sum(enc.simetria_residual(t) for t in ins[i]))
    suf = ("_omax" if a.ordem == "max" else "") + (f"_L{a.cubos}" if a.cubos else "") + (f"_sem{a.sem}" if a.sem else "")
    log = os.path.join(a.dir, f"K{a.q}_{a.n}_{R}_M{a.M}_k{k}_s{smin}{suf}.jsonl")
    feitos = set()
    if os.path.exists(log):
        for ln in open(log):
            r = json.loads(ln)
            if r["resultado"] != "INDEFINIDO":
                feitos.add((r["inst"], r.get("cubo_idx")))
    pular = set()
    for arq in a.pular:
        for ln in open(arq):
            r = json.loads(ln)
            if r["resultado"] == "UNSAT" and r.get("lrat_check") == "VERIFIED" and r.get("cubo_idx") is None:
                pular.add(tuple(sorted(r["tipos"])))
    tarefas = []
    for i in idxs:
        if pular and tuple(sorted("".join(map(str, t)) for t in ins[i])) in pular:
            continue
        if a.cubos:
            ts = list(ins[i]) + [None] * (a.n - k)
            nc = len(fib_cubos.atribuicoes_coord1(a.q, a.M, ts[0], ts[1], smin, a.cubos, blocos_h="h" not in a.sem))
            cis = intervalo(a.cubos_sel, nc)
        else:
            cis = [None]
        tarefas += [(a.q, a.n, a.M, k, smin, i, a.dir, a.prova, a.solver, a.tempo, a.descartar,
                     a.lrat_py, a.cubos, c, a.sem, a.ordem) + ((R,) if R != a.n - 2 else ())
                    for c in cis if (i, c) not in feitos]
    print(f"K_{a.q}({a.n},{R}) M={a.M} k={k} s_min={smin}: {len(ins)} instâncias, "
          f"{len(tarefas)} a rodar", flush=True)
    cont = {}
    with ProcessPoolExecutor(a.j) as ex, open(log, "a") as f:
        # grava na ordem em que terminam: um perfil lento não segura os outros (nem os perde
        # numa preempção da VM spot)
        for fut in as_completed([ex.submit(uma, t) for t in tarefas]):
            reg = fut.result()
            f.write(json.dumps(reg) + "\n")
            f.flush()
            cont[reg["resultado"]] = cont.get(reg["resultado"], 0) + 1
            extra = reg.get("lrat_check", "") or ("cobre=" + str(reg.get("cobre", "")))
            print(f"i{reg['inst']} c{reg.get('cubo_idx', '-')} {reg['resultado']} {reg['tempo_solver_s']}s {extra}", flush=True)
    print("resumo:", cont)


if __name__ == "__main__":
    main()
