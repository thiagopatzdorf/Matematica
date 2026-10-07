#!/usr/bin/env python3
"""Contagem de perfis e cubos de K_4(7,4) M=9 e K_4(6,3) M=11, recalculada à parte.

1. s_min pelo Lema 1 com a tabela de cotas inferiores declarada AQUI (fonte de cada número comentada).
2. Tipos = partições de M em q partes >= s_min, por estrelas e barras (sem a recursão do repo);
   perfis = multiconjuntos de n tipos (itertools.combinations_with_replacement sobre índices).
3. Compara com o certificado .jsonl.xz: faltando, sobrando, duplicado, `tipos` coerente com `inst`.
4. Cubos: o conjunto dos prefixos (comprimento L) da coordenada 1 que satisfazem, escrito direto das
   regras do doc (uma palavra por símbolo, fibras exatas, (d), (e), (h)), por força bruta com poda;
   compara com os `cubo` do certificado (faltando = o cubo não cobre tudo; sobrando = inofensivo).

Uso: python3 perfis_cubos.py CERT.jsonl.xz q n R M
"""
import itertools
import json
import os
import lzma
import math
import sys
from collections import Counter, defaultdict

# Cotas inferiores usadas SÓ para decidir s_min (lado "excluir fibra de tamanho s": K_{q-s}(n-1,R-1) > M-s).
# valor: (cota, de onde vem)
LB = {
    (4, 6, 3): (11, "HSPQ 2008/9 (ledger, CLAIMED); o repo prova >= 12 a partir de K_4(5,2) >= 16"),
    (4, 5, 2): (16, "HSPQ 2008/9 (ledger, CLAIMED); esfera dá só 10"),
    (3, 5, 2): (8, "Östergård–Hämäläinen 1993 (ledger, CLAIMED); só afeta s_min se M-1 < 8"),
    (3, 6, 3): (6, "Bhandari–Durairajan 1996 (CLAIMED); só afeta s_min se M-1 < 6"),
}


def s_min(q, n, R, M, lb=LB):
    s = 0
    while s < q:
        K = lb[(q - s, n - 1, R - 1)][0] if (q - s, n - 1, R - 1) in lb else 1
        if K <= M - s:
            return s
        s += 1
    return q


def tipos(q, M, smin):
    out = []
    extra = M - q * smin
    for comp in itertools.product(range(extra + 1), repeat=q):
        if sum(comp) == extra and all(comp[i] >= comp[i + 1] for i in range(q - 1)):
            out.append(tuple(c + smin for c in comp))
    return out


def sim_res(t):
    return math.prod(math.factorial(c) for c in Counter(t).values())


def blocos(t0):
    ini = 0
    for s in t0:
        yield range(ini, ini + s)
        ini += s


def coord1_validas(q, M, t0, t1):
    """Todas as atribuições (tuplas de M símbolos) da coordenada 1 que satisfazem as regras do doc."""
    bl = list(blocos(t0))
    blk = [b for b, B in enumerate(bl) for _ in B]
    out = []
    pal, cnt = [], [0] * q

    def rec(w):
        if w == M:
            if all(cnt[a] == t1[a] for a in range(q)) and ok_e_h(tuple(pal)):
                out.append(tuple(pal))
            return
        lo = pal[-1] if w > 0 and blk[w - 1] == blk[w] else 0          # (d)
        for a in range(lo, q):
            if cnt[a] >= t1[a]:
                continue
            cnt[a] += 1
            pal.append(a)
            rec(w + 1)
            pal.pop()
            cnt[a] -= 1

    def ok_e_h(p):
        # (e): para a, a+1 de mesma classe (mesma fibra) e toda palavra w do bloco bi com símbolo a+1:
        # a aparece em algum bloco <= bi (inclusive o próprio)
        for a in range(q - 1):
            if t1[a] != t1[a + 1]:
                continue
            for bi, B in enumerate(bl):
                ate = [w for bb in bl[: bi + 1] for w in bb]
                if any(p[w] == a + 1 for w in B) and not any(p[w] == a for w in ate):
                    return False
        # (h): blocos consecutivos de mesmo tamanho em ordem lexicográfica da coordenada 1
        for b in range(q - 1):
            if t0[b] == t0[b + 1]:
                if [p[w] for w in bl[b]] > [p[w] for w in bl[b + 1]]:
                    return False
        return True

    rec(0)
    return out


def registros_incoerentes(regs, q, n, R, M):
    """Registros cujo campo `tipos` não é a instância `inst` da lista do codificador (na ordem gravada), ou cujos
    parâmetros não são os da célula. O `fecha_perfis` confia em `tipos`; esta checagem fecha a lacuna."""
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "fibras"))
    import fib_encode as enc
    smin = enc.fibra_minima(q, n, R, M)
    listas = {o: enc.instancias(q, n, M, n, smin, ordem=o)[1] for o in ("min", "max")}
    return [r for r in regs
            if ["".join(map(str, t)) for t in listas[r.get("ordem", "min")][r["inst"]]] != r["tipos"]
            or (r["q"], r["n"], r.get("R"), r["M"], r["k"], r["smin"]) != (q, n, R, M, n, smin)]


def verificar(arq, q, n, R, M, imprimir=True):
    """Devolve estatísticas e levanta AssertionError se faltar/sobrar perfil ou se faltar cubo."""
    pr = print if imprimir else (lambda *a, **k: None)
    smin = s_min(q, n, R, M)
    T = tipos(q, M, smin)
    perfis = {tuple(sorted("".join(map(str, T[i])) for i in c)) for c in itertools.combinations_with_replacement(range(len(T)), n)}
    pr(f"K_{q}({n},{R}) M={M}: s_min={smin}, tipos={len(T)}, perfis={len(perfis)} (esperado C(T+n-1,n)={math.comb(len(T)+n-1, n)})")
    regs = [json.loads(l) for l in lzma.open(arq, "rt")]
    inteiros = Counter(tuple(sorted(r["tipos"])) for r in regs if not r.get("L") and r["resultado"] == "UNSAT")
    cubos = defaultdict(list)
    for r in regs:
        if r.get("L"):
            cubos[(tuple(sorted(r["tipos"])), r["ordem"], r["inst"], r["L"])].append(r)
    todos = set(inteiros) | {k[0] for k in cubos}
    pr(f"registros {len(regs)}: perfis inteiros {len(inteiros)}, perfis em cubos {len(cubos)}")
    pr("faltando:", len(perfis - todos), "sobrando:", len(todos - perfis),
          "duplicados (inteiro repetido):", sum(1 for v in inteiros.values() if v > 1),
          "inteiro E cubo:", len(set(inteiros) & {k[0] for k in cubos}))
    assert not (perfis - todos) and not (todos - perfis)
    for (perfil, ordem, inst, L), rs in sorted(cubos.items()):
        t = [tuple(int(c) for c in s) for s in rs[0]["tipos"]]
        assert all([tuple(int(c) for c in s) for s in r["tipos"]] == t for r in rs)
        assert all(sum(x) == M for x in t) and len(t) == n
        # a ordem dos tipos no registro é a da instância: t0 = coordenada 0
        validas = coord1_validas(q, M, t[0], t[1])
        pref = sorted({v[:L] for v in validas})
        gravados = sorted(tuple(int(c) for c in r["cubo"]) for r in rs)
        dup = len(gravados) - len(set(gravados))
        faltam = set(pref) - set(gravados)
        sobram = set(gravados) - set(pref)
        idx_ok = sorted(r["cubo_idx"] for r in rs) == list(range(len(rs)))
        pr(f"  cubos {ordem} inst {inst} L={L} perfil {' '.join(perfil)[:60]}...: válidas={len(validas)} "
              f"prefixos={len(pref)} gravados={len(gravados)} faltam={len(faltam)} sobram={len(sobram)} dup={dup} idx={idx_ok}")
        assert not faltam, "cubo faltando: o certificado NÃO cobre toda a coordenada 1"
        assert not dup and idx_ok
    return {"smin": smin, "tipos": len(T), "perfis": len(perfis), "inteiros": len(inteiros), "perfis_em_cubos": len(cubos),
            "cubos": sum(len(v) for v in cubos.values())}


def main():
    arq, q, n, R, M = sys.argv[1], *map(int, sys.argv[2:6])
    verificar(arq, q, n, R, M)


if __name__ == "__main__":
    main()
