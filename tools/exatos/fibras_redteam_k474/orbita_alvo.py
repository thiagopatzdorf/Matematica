#!/usr/bin/env python3
"""Órbita por SAT em códigos ADVERSARIAIS: colunas iguais (empates de (g)), palavras repetidas (empates de
(d)/(h)), colunas copiadas a menos de rotulação, e perfis de maior simetria residual. Só vale para códigos
cujas fibras são todas >= s_min do alvo (fora disso o Lema 1 já os exclui e não há instância).

Uso: python3 orbita_alvo.py Q N R M AMOSTRA SEMENTE [mutante]
"""
import os
import random
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import orbita_indep as o  # noqa: E402
import orbita_massa as om  # noqa: E402


def gerar(q, n, M, smin, rng):
    for _ in range(1000):
        modo = rng.choice(["colunas_copiadas", "palavras_repetidas", "bloco_simetrico", "colunas_copiadas"])
        if modo == "colunas_copiadas":
            base = [rng.randrange(q) for _ in range(M)]
            # fibras desiguais mas simétricas: base balanceada às vezes
            if rng.random() < 0.6:
                base = [w % q for w in range(M)]
                rng.shuffle(base)
            cols = []
            for i in range(n):
                if i < 2 or rng.random() < 0.3:
                    cols.append([rng.randrange(q) for _ in range(M)] if rng.random() < 0.5 else rng.sample(base, M))
                else:
                    p = rng.sample(range(q), q)
                    cols.append([p[b] for b in rng.choice([base, cols[-1]])])
            cod = [tuple(cols[i][w] for i in range(n)) for w in range(M)]
        elif modo == "palavras_repetidas":
            k = rng.randrange(2, M)
            ws = [tuple(rng.randrange(q) for _ in range(n)) for _ in range(max(1, M // k + 1))]
            cod = [rng.choice(ws) for _ in range(M)]
        else:
            # pares/trincas de palavras que diferem em uma coordenada: muitos empates na coordenada 1
            base = [tuple(rng.randrange(q) for _ in range(n)) for _ in range(M // 2 + 1)]
            cod = []
            for w in base:
                cod.append(w)
                v = list(w); v[rng.randrange(n)] = rng.randrange(q); cod.append(tuple(v))
            cod = cod[:M]
        if len(cod) == M and all(min(o.tipo(cod, i, q)) >= smin for i in range(n)):
            return cod
    return None


def main():
    a = sys.argv[1:]
    q, n, R, M, N, sem = map(int, a[:6])
    mut = a[6] if len(a) > 6 else None
    sys.path.insert(0, os.path.join(AQUI, "..", "fibras"))
    enc = om.carregar(mut)
    smin = enc.fibra_minima(q, n, R, M)
    rng = random.Random(sem)
    tot = bad = pulados = 0
    for r in range(N):
        cod = gerar(q, n, M, smin, rng)
        if cod is None:
            pulados += 1
            continue
        for ordem in ("min", "max"):
            ok = o.orbita_sat(enc, q, n, M, R, cod, ordem, com_cobertura=False)
            tot += 1
            if not ok:
                bad += 1
                print("ORBITA_UNSAT", ordem, cod, flush=True)
    print(f"q={q} n={n} R={R} M={M} smin={smin} mutante={mut}: {tot} testes adversariais, {bad} UNSAT, {pulados} sem código")


if __name__ == "__main__":
    main()
