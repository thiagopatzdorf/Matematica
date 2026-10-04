#!/usr/bin/env python3
"""Compila os módulos `CoveringLean/K742Sat/S<p>/{Data,B<m>,Final}.lean` com `lean` direto,
em paralelo, respeitando as dependências (Data → B* → Final), e registra cada módulo.

    python3 tools/exatos/k742/lean/vm/agendar.py --perfis 55,25,9 --jobs 7

Por que não `lake build`: o lake não tem limite de jobs, e cada `lean` destes usa ~3 GB; aqui o
paralelismo é fixo e cada módulo deixa uma linha em `logs/modulos.jsonl` (tempo de parede,
CPU, pico de RSS medido por `wait4`, código de saída) e a saída inteira em
`logs/mod/<módulo>.log` (com os `#print axioms`). Retomável: módulo com `.olean` e registro
`rc = 0` não roda de novo (preempção da VM spot).

Pré-requisito: `lake build CoveringLean.LratKData CoveringLean.LratKFinal CoveringLean.K742_Cnf`
(feito aqui).
"""
import argparse
import json
import os
import subprocess
import sys
import time

RAIZ = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "..", ".."))
LIB = os.path.join(RAIZ, ".lake", "build", "lib", "lean")


def modulos_perfil(p):
    d = os.path.join(RAIZ, "CoveringLean", "K742Sat", f"S{p}")
    bs = sorted((f for f in os.listdir(d) if f.startswith("B") and f.endswith(".lean")),
                key=lambda f: int(f[1:-5]))
    return ([f"CoveringLean.K742Sat.S{p}.Data"] + [f"CoveringLean.K742Sat.S{p}.{b[:-5]}" for b in bs]
            + [f"CoveringLean.K742Sat.S{p}.Final"])


def caminho(mod, ext):
    return os.path.join(LIB, *mod.split(".")) + ext


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--perfis", required=True)
    ap.add_argument("--jobs", type=int, default=7)
    a = ap.parse_args()
    os.chdir(RAIZ)
    os.makedirs("logs/mod", exist_ok=True)
    env = dict(os.environ)
    env["PATH"] = os.path.expanduser("~/.elan/bin") + ":" + env.get("PATH", "")
    r = subprocess.run(["lake", "build", "CoveringLean.LratKData", "CoveringLean.LratKFinal",
                        "CoveringLean.K742_Cnf"], env=env)
    if r.returncode != 0:
        sys.exit("falhou o build da base")
    env["LEAN_PATH"] = LIB
    feitos = set()
    reg = os.path.join("logs", "modulos.jsonl")
    if os.path.exists(reg):
        for ln in open(reg):
            e = json.loads(ln)
            if e["rc"] == 0 and os.path.exists(caminho(e["modulo"], ".olean")):
                feitos.add(e["modulo"])
    perfis = [int(x) for x in a.perfis.split(",")]
    # fila: Data de todos (na ordem dada: maiores primeiro), depois os B, depois os Final
    deps = {}
    ordem = []
    for p in perfis:
        ms = modulos_perfil(p)
        deps[ms[0]] = []
        for m in ms[1:-1]:
            deps[m] = [ms[0]]
        deps[ms[-1]] = ms[:-1]
        ordem.append(ms)
    fila = [ms[0] for ms in ordem] + [m for ms in ordem for m in ms[1:-1]] + [ms[-1] for ms in ordem]
    fila = [m for m in fila if m not in feitos]
    rodando = {}
    falhou = set()
    while fila or rodando:
        # dispara
        for m in list(fila):
            if len(rodando) >= a.jobs:
                break
            if any(d in falhou for d in deps[m]):
                fila.remove(m)
                falhou.add(m)
                continue
            if all(d in feitos for d in deps[m]):
                fila.remove(m)
                src = os.path.join(RAIZ, *m.split(".")) + ".lean"
                os.makedirs(os.path.dirname(caminho(m, ".olean")), exist_ok=True)
                log = open(os.path.join("logs", "mod", m + ".log"), "w")
                pr = subprocess.Popen(["lean", "--root=.", "-o", caminho(m, ".olean"),
                                       "-i", caminho(m, ".ilean"), src],
                                      stdout=log, stderr=subprocess.STDOUT, env=env)
                rodando[pr.pid] = (m, time.time(), log)
        if not rodando:
            if fila:
                sys.exit(f"impasse: {fila[:5]}")
            break
        pid, status, ru = os.wait4(-1, 0)
        if pid not in rodando:
            continue
        m, t0, log = rodando.pop(pid)
        log.close()
        rc = os.waitstatus_to_exitcode(status)
        e = {"modulo": m, "rc": rc, "parede_s": round(time.time() - t0, 1),
             "cpu_s": round(ru.ru_utime + ru.ru_stime, 1), "rss_gb": round(ru.ru_maxrss / 2**20, 2),
             "fim": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
        with open(reg, "a") as f:
            f.write(json.dumps(e) + "\n")
        print(json.dumps(e), flush=True)
        (feitos if rc == 0 else falhou).add(m)
    print(f"[agendar] fim: {len(feitos)} módulos ok, {len(falhou)} falharam", flush=True)
    sys.exit(1 if falhou else 0)


if __name__ == "__main__":
    main()
