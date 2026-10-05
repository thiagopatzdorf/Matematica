#!/usr/bin/env python3
"""Red team K_3(6,2), M = 15: mutações dos certificados do PR #57 contra os dois verificadores.

Cada mutação produz um certificado que NÃO deveria provar a instância (ou deveria provar uma coisa
diferente). Conta quantas mutações cada verificador aceita: `farkas_min` (deste red team) e, se
`--verificar-pr` apontar para o `verificar.py` do PR, a função `folha_ok` dele.

  neg      um y vira -1 (o defeito real que o PR já pegou uma vez)
  sem_fib  o sistema perde as linhas de fibra (certificados que as usam têm de cair)
  troca    certificado da instância i conferido contra a instância i+1 do mesmo s*
  maior_y  some a entrada de y de maior peso
  M16      o mesmo certificado conferido com M = 16 e t_1 + 1 (a instância de M = 16 pode ser
           inviável de verdade, então aceitar não é defeito; conta-se só a concordância)
  folha    as instâncias com ramificação perdem uma folha (árvore incompleta)

Aceitar uma mutação de "troca", "maior_y" ou "M16" não é defeito por si (o certificado pode ter
folga para isso); o relatório mostra a contagem e confere que os dois verificadores concordam.
"neg", "sem_fib" (nas folhas que usam fibra) e "folha" têm de ser recusadas sempre.
"""
import argparse
import copy
import gzip
import importlib.util
import json
import os
import random
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import farkas_min  # noqa: E402


class SemFibra(farkas_min.Sistema):
    def linha_ge(self, k):
        if k >= len(self.pts):
            raise ValueError("linha de fibra retirada")
        return super().linha_ge(k)


def aceita_min(cls, q, n, R, M, inst, folha):
    s, K, t = inst
    try:
        g = farkas_min.folga(cls(q, n, R, M, s, K, t), folha)
    except (ValueError, AssertionError):
        return False
    return g is None or g > 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--instancias", required=True)
    ap.add_argument("--certificados", required=True)
    ap.add_argument("--verificar-pr")
    ap.add_argument("--amostra", type=int, default=400)
    ap.add_argument("--semente", type=int, default=7)
    a = ap.parse_args()
    q, n, R, M = 3, 6, 2, 15
    rng = random.Random(a.semente)
    ins = json.load(open(a.instancias))
    regs = [json.loads(ln) for ln in gzip.open(a.certificados, "rt")]
    pr = None
    if a.verificar_pr:
        spec = importlib.util.spec_from_file_location("verificar_pr", a.verificar_pr)
        pr = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(pr)
        pts, bola = pr.bolas(q, n, R)

    def aceita_pr(MM, inst, folha, sem_fib=False):
        if pr is None:
            return None
        s, K, t = inst
        if sem_fib:
            s = 0  # no verificar.py do PR, s* = 0 é o sistema sem linhas de fibra
        return pr.folha_ok(q, n, MM, s, K, t, pts, bola, folha)

    amostra = rng.sample(regs, a.amostra)
    cont = {}

    def conta(nome, am, ap_):
        c = cont.setdefault(nome, [0, 0, 0])
        c[0] += 1
        c[1] += bool(am)
        c[2] += bool(ap_)

    por_s = {}
    for i, x in enumerate(ins):
        por_s.setdefault(x[0], []).append(i)
    for reg in amostra:
        inst = ins[reg["inst"]]
        for fo in reg["folhas"]:
            # neg
            m = copy.deepcopy(fo)
            k = rng.choice(list(m["y"]))
            m["y"][k] = -1
            conta("neg", aceita_min(farkas_min.Sistema, q, n, R, M, inst, m), aceita_pr(M, inst, m))
            # sem_fib (só folhas que usam fibra)
            if any(int(k) >= q ** n for k in fo["y"]):
                conta("sem_fib", aceita_min(SemFibra, q, n, R, M, inst, fo), aceita_pr(M, inst, fo, True))
            # troca: outra instância do mesmo s*
            j = rng.choice(por_s[inst[0]])
            if j != reg["inst"]:
                conta("troca", aceita_min(farkas_min.Sistema, q, n, R, M, ins[j], fo), aceita_pr(M, ins[j], fo))
            # maior_y
            m = copy.deepcopy(fo)
            k = max(m["y"], key=lambda k: m["y"][k])
            del m["y"][k]
            conta("maior_y", aceita_min(farkas_min.Sistema, q, n, R, M, inst, m), aceita_pr(M, inst, m))
            # M16: mesmo s* e K, bloco 1 com uma palavra a mais (sistema coerente com M = 16)
            i16 = [inst[0], inst[1], [inst[2][0] + 1] + list(inst[2][1:])]
            conta("M16", aceita_min(farkas_min.Sistema, q, n, R, 16, i16, fo), aceita_pr(16, i16, fo))
    # folha: instâncias com ramificação
    for reg in regs:
        if len(reg["folhas"]) > 1:
            for k in range(len(reg["folhas"])):
                m = copy.deepcopy(reg)
                del m["folhas"][k]
                ok_min, _ = farkas_min.conferir_registro(q, n, R, M, ins[reg["inst"]], m)
                ok_pr = pr.arvore_completa([f["fixos"] for f in m["folhas"]]) if pr else None
                conta("folha", ok_min, ok_pr)
    print("mutação: [testadas, aceitas por farkas_min, aceitas pelo verificar.py do PR]")
    for k, v in cont.items():
        print(f"  {k:8s} {v}")
    ruim = any(cont[k][1] or cont[k][2] for k in ("neg", "sem_fib", "folha") if k in cont)
    print("RESULTADO:", "FALHOU (mutação obrigatória aceita)" if ruim else "OK")
    sys.exit(1 if ruim else 0)


if __name__ == "__main__":
    main()
