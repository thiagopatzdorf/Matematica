#!/usr/bin/env python3
"""Verificador LRAT mínimo em Python (só passos RUP com dicas e deleções), independente do
drat-trim. Lento: serve para os testes e para conferir certificados pequenos ou uma amostra.

Uso: python3 tools/exatos/k742/lrat.py arquivo.cnf arquivo.lrat[.gz]
Sai com 0 e imprime 'VERIFICADO' se a prova deriva a cláusula vazia.
"""
import gzip
import sys


def abrir(p):
    return gzip.open(p, "rt") if p.endswith(".gz") else open(p)


def ler_cnf(p):
    cls, atual = [], []
    with abrir(p) as f:
        for ln in f:
            if ln.startswith(("c", "p")):
                continue
            for t in ln.split():
                v = int(t)
                if v == 0:
                    cls.append(atual)
                    atual = []
                else:
                    atual.append(v)
    return cls


def verificar(cnf_path, lrat_path):
    db = {i + 1: c for i, c in enumerate(ler_cnf(cnf_path))}
    with abrir(lrat_path) as f:
        for num, ln in enumerate(f, 1):
            t = ln.split()
            if not t or t[0] == "c":
                continue
            cid = int(t[0])
            if t[1] == "d":
                for x in t[2:]:
                    if x != "0":
                        db.pop(int(x), None)
                continue
            vals = list(map(int, t[1:]))
            z = vals.index(0)
            clause, dicas = vals[:z], vals[z + 1:]
            if dicas and dicas[-1] == 0:
                dicas = dicas[:-1]
            verd = {-l for l in clause}  # literais atribuídos verdadeiros: negação da cláusula
            conflito = False
            for h in dicas:
                if h < 0:
                    raise ValueError(f"linha {num}: passo RAT não suportado")
                c = db[h]
                livres = [l for l in c if l not in verd and -l not in verd]
                if any(l in verd for l in c):
                    continue  # cláusula satisfeita pela atribuição: dica inútil
                if not livres:
                    conflito = True
                    break
                if len(livres) == 1:
                    verd.add(livres[0])
                else:
                    raise ValueError(f"linha {num}: dica {h} não é unitária")
            if not conflito:
                raise ValueError(f"linha {num}: RUP falhou para a cláusula {cid}")
            if not clause:
                return True
            db[cid] = clause
    return False


def main():
    ok = verificar(sys.argv[1], sys.argv[2])
    print("VERIFICADO" if ok else "NAO VERIFICADO (sem cláusula vazia)")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
