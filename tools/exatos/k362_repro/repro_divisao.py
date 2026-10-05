"""Divisão de uma instância (s, K) pelos tamanhos exatos das fibras, para instâncias que resistem inteiras.

Completude (ver K3_M15_REPRODUCAO.md, "M = 16, divisão"): num código de M palavras normalizado com fibra
mínima F(0,0) de tamanho s, cada coordenada j tem fibras (f_0, f_1, f_2) com f_a >= s e soma M. Na
coordenada 0, f_0 = s e, como trocar os símbolos 1 e 2 ali fixa {0} x K e preserva tudo, podemos supor
f_1 >= f_2. Cada ramo fixa (f_0, f_1, f_2) para as coordenadas 0..d-1; os ramos cobrem todos os casos.
Cada folha é decidida pelo RoundingSat com prova VeriPB ou, se resistir, por certificado de Farkas.
"""
import itertools
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import repro_farkas as farkas  # noqa: E402
import repro_sat as sat  # noqa: E402


def distribuicoes(total, s, q=3):
    if q == 1:
        return [(total,)] if total >= s else []
    return [(f,) + r for f in range(s, total + 1) for r in distribuicoes(total - f, s, q - 1)]


def opcoes(j, M, s, q=3):
    return [f for f in distribuicoes(M, s, q) if j or (f[0] == s and f[1] >= f[2])]


class Instancia:
    def __init__(self, q, n, R, M, K):
        self.q, self.n, self.R, self.M, self.K, self.s = q, n, R, M, K, len(K)
        self.cob, self.nv, self.teto, self.fib = sat.restricoes(q, n, R, M, K, True)
        P = [c for c in itertools.product(range(q), repeat=n) if c[0] != 0]
        self.grupo = {(j, a): [i + 1 for i, c in enumerate(P) if c[j] == a] for j in range(n) for a in range(q)}
        self.fora = {(j, a): sum(1 for k in K if k[j - 1] == a) if j else (self.s if a == 0 else 0)
                     for j in range(n) for a in range(q)}

    def iguais(self, div):
        """[(literais, t)] com sum = t: as fibras fixadas pela divisão, descontada a fatia fixa."""
        return [(self.grupo[(j, a)], f[a] - self.fora[(j, a)]) for j, f in div for a in range(self.q)
                if not (j == 0 and a == 0)]

    def opb(self, div):
        eq = self.iguais(div)
        txt = sat.opb(self.cob, self.nv, self.teto, self.fib + eq)
        L = txt.splitlines()
        L += [" ".join("-1 x%d" % v for v in lits) + " >= %d ;" % -t for lits, t in eq]
        return "* #variable= %d #constraint= %d #equal= 0 intsize= 8\n" % (self.nv, len(L) - 1) + "\n".join(L[1:]) + "\n"

    def linhas(self, div):
        return farkas.linhas(self.cob, self.nv, self.teto, self.fib, self.iguais(div))


def resolver(inst, binarios, tempo, prof_min=1, prof_max=4, log=print):
    """Árvore de divisão. Folha: PB com prova; se TEMPO/PROVA_GRANDE, tenta Farkas; se ainda resistir, divide.
    Devolve (fechou?, registros)."""
    regs = []

    def rec(div):
        if len(div) >= prof_min:
            r = sat.resolver(inst.opb(div), "opb", binarios, inst.nv, tempo)
            r.pop("modelo", None)
            r.update(metodo="pb", divisao=[[j, list(f)] for j, f in div])
            if r["veredito"] == "UNSAT" and r.get("verificador") == "VERIFIED":
                regs.append(r)
                log(r)
                return True
            if r["veredito"] == "SAT":
                regs.append(r)
                log("ATENCAO SAT", r)
                return False
            L = inst.linhas(div)
            y = farkas.gerar(L, inst.nv)
            if y is not None:
                folga = farkas.confere(L, inst.nv, farkas.racionalizar(y))
                if folga > 0:
                    regs.append({"metodo": "farkas", "divisao": r["divisao"], "folga": str(folga), "pb": r["veredito"]})
                    log(regs[-1])
                    return True
            log("resiste", r["divisao"], r["veredito"])
        if len(div) >= min(prof_max, inst.n):
            return False
        return all([rec(div + [(len(div), f)]) for f in opcoes(len(div), inst.M, inst.s, inst.q)])
    return rec([]), regs


def _uma(args):
    q, n, R, M, K, binarios, tempo, pmin, pmax = args
    inst = Instancia(q, n, R, M, K)
    ok, regs = resolver(inst, binarios, tempo, pmin, pmax, log=lambda *a: print(*a, flush=True))
    return {"s": len(K), "K": ",".join("".join(map(str, k)) for k in K), "fechou": ok, "folhas": regs}


def main(argv=None):
    """python3 repro_divisao.py REGISTRO.jsonl.gz --bin DIR --saida X.jsonl [--proc 2 --tempo 1200 --prof-min 2]
    Roda a divisão nas instâncias do registro que não ficaram UNSAT VERIFIED (ex.: PROVA_GRANDE de M = 16)."""
    import argparse
    import gzip
    import json
    import multiprocessing as mp
    ap = argparse.ArgumentParser()
    ap.add_argument("registro")
    ap.add_argument("--bin", required=True)
    ap.add_argument("--saida", required=True)
    ap.add_argument("--M", type=int, default=16)
    ap.add_argument("--proc", type=int, default=2)
    ap.add_argument("--tempo", type=float, default=1200)
    ap.add_argument("--prof-min", type=int, default=2)
    ap.add_argument("--prof-max", type=int, default=4)
    a = ap.parse_args(argv)
    abertas = []
    for r in map(json.loads, gzip.open(a.registro, "rt")):
        final = r[3] or r[2]
        if final[1:3] != ["UNSAT", "VERIFIED"]:
            abertas.append([tuple(map(int, w)) for w in r[1].split(",")])
    b = {x: os.path.join(a.bin, x) for x in ("roundingsat", "veripb")}
    tarefas = [(3, 6, 2, a.M, K, b, a.tempo, a.prof_min, a.prof_max) for K in abertas]
    print("abertas", len(tarefas), flush=True)
    with mp.Pool(a.proc) as pool, open(a.saida, "a") as f:
        for reg in pool.imap_unordered(_uma, tarefas):
            f.write(json.dumps(reg) + "\n")
            f.flush()
            print("INSTANCIA", reg["K"], "fechou" if reg["fechou"] else "ABERTA", len(reg["folhas"]), flush=True)


if __name__ == "__main__":
    main()
