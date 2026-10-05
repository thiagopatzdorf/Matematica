#!/usr/bin/env python3
"""Roda RoundingSat (OPB), CaDiCaL e kissat (CNF do totalizador) com orçamento fixo e extrai as
estatísticas: veredito, tempo de CPU, conflitos, decisões, propagações, cláusulas aprendidas e,
dos solvers CNF, a última linha de relatório (nível de decisão médio e glue/LBD médio).

  CADICAL=... KISSAT=... ROUNDINGSAT=... python3 solvers.py --instancias i15.json \
      --idx 11927 --tempo 60 --rs-tempo 300 --dir tmp >> stats.jsonl
"""
import argparse
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import autopsia as au  # noqa: E402


def num(txt, chave):
    m = re.search(r"^c " + chave + r":?\s+([\d.]+)", txt, re.M)
    return float(m.group(1)) if m else None


def veredito(txt):
    m = re.search(r"^s (\S+)", txt, re.M)
    return m.group(1) if m else "UNKNOWN"


def relatorio(txt, campos):
    """Última linha de relatório 'c <letra> v1 v2 ...' mapeada para os nomes das colunas."""
    linhas = [ln.split()[2:] for ln in txt.splitlines() if re.match(r"^c [a-zA-Z?] +\d", ln)]
    if not linhas:
        return {}
    ult = linhas[-1]
    return {k: ult[i] for k, i in campos.items() if i < len(ult)}


# colunas (CaDiCaL 2.x / kissat 4.x, cabeçalho intercalado em três linhas)
CAD = {"nivel": 2, "glue": 10, "trail": 13}
KIS = {"nivel": 2, "glue": 11, "trail": 14}


def rodar(cmd, tempo):
    r = subprocess.run(["timeout", str(tempo + 30)] + cmd, capture_output=True, text=True)
    return r.stdout + r.stderr


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--instancias", required=True)
    ap.add_argument("--idx", type=int, required=True)
    ap.add_argument("--tempo", type=int, default=60)
    ap.add_argument("--rs-tempo", type=int, default=300)
    ap.add_argument("--dir", required=True)
    ap.add_argument("--opb-extra", help="OPB alternativo para o RoundingSat (ex.: com lex-leader)")
    a = ap.parse_args()
    inst = au.instancia(json.load(open(a.instancias)), a.idx)
    livres, cons = au.reduzir(inst)
    os.makedirs(a.dir, exist_ok=True)
    base = os.path.join(a.dir, f"i{a.idx}")
    out = {"idx": a.idx}
    if a.opb_extra:
        opb = a.opb_extra
    else:
        opb = base + ".opb"
        open(opb, "w").write(au.opb(inst)[0])
        nv, cls = au.cnf(livres, cons)
        with open(base + ".cnf", "w") as f:
            f.write(f"p cnf {nv} {len(cls)}\n")
            f.writelines(" ".join(map(str, c)) + " 0\n" for c in cls)
        for nome, cmd, cols in (
                ("cad", [os.environ["CADICAL"], "-t", str(a.tempo), base + ".cnf"], CAD),
                ("kis", [os.environ["KISSAT"], f"--time={a.tempo}", base + ".cnf"], KIS)):
            txt = rodar(cmd, a.tempo)
            out[nome] = {"s": veredito(txt), "cpu": num(txt, "total process time since initialization") or
                         num(txt, r"process-time:\s+\S+"),
                         **{k: num(txt, k) for k in ("conflicts", "decisions", "propagations")},
                         "aprendidas": num(txt, "learned"), **relatorio(txt, cols)}
        os.remove(base + ".cnf")
    txt = rodar([os.environ["ROUNDINGSAT"], opb, f"--time-limit={a.rs_tempo}", "--print-sol=0"],
                a.rs_tempo)
    out["rs"] = {"s": veredito(txt), "cpu": num(txt, "cpu time"),
                 **{k: num(txt, k) for k in ("conflicts", "decisions", "propagations", "restarts")},
                 "aprendidas": num(txt, "learned constraints"),
                 "tam_medio_aprendida": num(txt, "learned average constraint length")}
    if not a.opb_extra:
        os.remove(opb)
    print(json.dumps(out), flush=True)


if __name__ == "__main__":
    main()
