#!/usr/bin/env python3
"""Autópsia das instâncias da fatia mínima de K_3(6,2), M = 15 (gaps2): por que algumas são duras.

Tudo parte do OPB que `tools/exatos/gaps2/fatia_pb.py` escreve. Medidas (cada uma é um comando):

  opb      regera o OPB, confere o sha256 contra o registro (só as fáceis têm sha registrado)
  reduzir  fórmula efetiva: fatia 0 substituída (243 variáveis fixas), cobertura já satisfeita por K
           removida; sobram 486 variáveis livres e restrições de cardinalidade
  cnf      CNF equivalente da fórmula efetiva (totalizador do pysat para as cardinalidades)
  up       propagação unitária na raiz e literais falhos (sondagem) na fórmula efetiva
  estab    estabilizador de K em S_3 wr S_5 (combinatório) e grupo da fórmula pelo nauty (dreadnaut)
  grafo    modularidade (Louvain) do grafo de incidência e largura de árvore heurística do primal
  sa       recozimento: menor número de pontos descobertos respeitando a instância
  gama/nu/tau  cobertura, empacotamento e LP do lema da fatia 0 (U em bolas de raio 1)
  lex      restrições lex-leader (PB) para os geradores do grupo, para anexar ao OPB

  python3 autopsia.py --instancias i15.json --idx 11927 medir --saida m.json
"""
import argparse
import hashlib
import itertools
import json
import os
import subprocess
import sys
from collections import Counter

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, "..", "..", "gaps2"))
import fatia  # noqa: E402
import fatia_pb  # noqa: E402

Q, N, R, M = 3, 6, 2, 15
PTS = list(itertools.product(range(Q), repeat=N))
VAR = {c: i + 1 for i, c in enumerate(PTS)}


def instancia(lista, idx):
    s, K, t = lista[idx]
    return s, tuple(tuple(k) for k in K), tuple(t)


_FIXAS = []


def opb(inst):
    """Mesmo texto de `fatia_pb.opb` (conferido no teste), mas as 730 primeiras restrições
    (cobertura e tamanho), que não dependem da instância, saem de um cache: o censo regera
    milhares de OPBs e o original custa ~0,5 s cada."""
    s, K, t = inst
    if not _FIXAS:
        _FIXAS.extend(fatia_pb.opb(Q, N, R, M, inst)[0].splitlines()[1:731])
    fixos = {(0,) + tuple(k) for k in K}
    ls = list(_FIXAS)
    ls += [f"+1 x{VAR[c]} = {int(c in fixos)} ;" for c in PTS if c[0] == 0]
    ls += [" ".join(f"+1 x{VAR[c]}" for c in PTS if c[0] == b) + f" = {tb} ;"
           for b, tb in enumerate(t, start=1)]
    if s > 0:
        ls += [" ".join(f"+1 x{VAR[c]}" for c in PTS if c[j] == a) + f" >= {s} ;"
               for j in range(1, N) for a in range(Q)]
    neq = sum(" = " in ln for ln in ls)
    txt = f"* #variable= {len(PTS)} #constraint= {len(ls)} #equal= {neq} intsize= 8\n" + \
        "\n".join(ls) + "\n"
    return txt, hashlib.sha256(txt.encode()).hexdigest()


def reduzir(inst):
    """Fórmula efetiva: lista de (vars, op, rhs) só sobre os pontos com c_0 != 0."""
    s, K, t = inst
    fix = {(0,) + k: 1 for k in K}
    for c in PTS:
        if c[0] == 0:
            fix.setdefault(c, 0)
    livres = [c for c in PTS if c[0] != 0]
    cons = []
    for x in PTS:
        if any(fatia.dist(c, x) <= R for c in fix if fix[c]):
            continue
        cons.append(([VAR[c] for c in livres if fatia.dist(c, x) <= R], ">=", 1, "cob"))
    for b, tb in enumerate(t, start=1):
        cons.append(([VAR[c] for c in livres if c[0] == b], "=", tb, "bloco"))
    for j in range(1, N):
        for a in range(Q):
            r = s - sum(1 for k in K if k[j - 1] == a)
            if r > 0:
                cons.append(([VAR[c] for c in livres if c[j] == a], ">=", r, "fibra"))
    return [VAR[c] for c in livres], cons


def cnf(livres, cons):
    """Cláusulas equivalentes (variáveis auxiliares acima de 729)."""
    from pysat.card import CardEnc, EncType
    top, cls = len(PTS), []
    for vs, op, r, _ in cons:
        if op == ">=" and r == 1:
            cls.append(list(vs))
            continue
        f = CardEnc.equals if op == "=" else CardEnc.atleast
        e = f(lits=vs, bound=r, top_id=top, encoding=EncType.totalizer)
        top = max(top, e.nv)
        cls += e.clauses
    return top, cls


def propagar(cons, a):
    """Propagação de cardinalidade (coeficientes 1). a: dict var->0/1, alterado. False = conflito."""
    mudou = True
    while mudou:
        mudou = False
        for vs, op, r, _ in cons:
            um = sum(1 for v in vs if a.get(v) == 1)
            liv = [v for v in vs if v not in a]
            if um > r and op == "=" or um + len(liv) < r:
                return False
            if liv and um + len(liv) == r:
                for v in liv:
                    a[v] = 1
                mudou = True
            elif liv and op == "=" and um == r:
                for v in liv:
                    a[v] = 0
                mudou = True
    return True


def up(livres, cons):
    raiz = {}
    ok = propagar(cons, raiz)
    falhos = 0
    for v in livres:
        if v in raiz:
            continue
        for val in (0, 1):
            a = dict(raiz)
            a[v] = val
            falhos += not propagar(cons, a)
    return {"up_conflito_raiz": not ok, "up_fixas_raiz": len(raiz), "literais_falhos": falhos}


def estabilizador(K):
    """Elementos de S_3 wr S_5 (permutação de coordenadas + símbolos por coordenada) com g(K) = K."""
    import numpy as np
    sig = list(itertools.permutations(range(3)))
    alvo = sorted(sum(v * 3 ** i for i, v in enumerate(k)) for k in K)
    Kn = np.array(K)
    gs = []
    for pi in itertools.permutations(range(5)):
        P = Kn[:, list(pi)]
        for ss in itertools.product(range(6), repeat=5):
            cod = sorted(sum(sig[ss[i]][P[p, i]] * 3 ** i for i in range(5)) for p in range(len(K)))
            if cod == alvo:
                gs.append((pi, ss))
    return gs


def nauty(livres, cons):
    """Grupo de automorfismos da fórmula efetiva: vértice por variável e por restrição, cores por
    (tipo, rhs). Devolve (ordem do grupo, geradores restritos às variáveis)."""
    idx = {v: i for i, v in enumerate(livres)}
    nv = len(livres)
    cores = {}
    for vs, op, r, tipo in cons:
        cores.setdefault((tipo, op, r), []).append(None)
    ordem = sorted(cores)
    cid, viz = {}, {}
    for k, (vs, op, r, tipo) in enumerate(cons):
        viz[nv + k] = [idx[v] for v in vs]
        cid.setdefault((tipo, op, r), []).append(nv + k)
    part = "[" + "|".join([",".join(map(str, range(nv)))] +
                          [",".join(map(str, cid[c])) for c in ordem]) + "]"
    linhas = [f"n={nv + len(cons)} g"]
    for u in range(nv + len(cons)):
        linhas.append(" ".join(map(str, viz.get(u, []))) + (";" if u < nv + len(cons) - 1 else "."))
    entrada = "\n".join(linhas) + f"\nf={part} x\n"
    out = subprocess.run(["dreadnaut"], input="At +a -m\n" + entrada + "q\n",
                         capture_output=True, text=True).stdout
    grp = [ln for ln in out.splitlines() if "grpsize" in ln]
    tam = grp[0].split("grpsize=")[1].split(";")[0].strip() if grp else "?"
    gens, cur = [], ""
    for ln in out.splitlines():  # gerador começa com "(" e continua em linhas "   (..."
        if ln.startswith("(") or ln.startswith("Gen"):
            gens.append(cur) if cur else None
            cur = ln.split(":", 1)[-1].strip()
        elif cur and ln.startswith("   ("):
            cur += " " + ln.strip()
        elif cur:
            gens.append(cur)
            cur = ""
    perms = []
    for g in gens:
        p = {}
        for ciclo in g.replace(")", "").split("(")[1:]:
            el = [int(x) for x in ciclo.split()]
            for a, b in zip(el, el[1:] + el[:1]):
                if a < nv:
                    p[livres[a]] = livres[b]
        if p:
            perms.append(p)
    return tam, perms


def grafo(livres, cons):
    import networkx as nx
    from networkx.algorithms import approximation as ap
    from networkx.algorithms import community as cm
    G = nx.Graph()
    for k, (vs, *_) in enumerate(cons):
        G.add_edges_from((("c", k), v) for v in vs)
    comm = cm.louvain_communities(G, seed=1)
    P = nx.Graph()
    P.add_nodes_from(livres)
    for vs, op, r, tipo in cons:
        if tipo == "cob":  # cardinalidades grandes (243/162 variáveis) viram clique: só a cobertura
            P.add_edges_from(itertools.combinations(vs, 2))
    tw, _ = ap.treewidth_min_fill_in(P)
    return {"modularidade": round(cm.modularity(G, comm), 4), "comunidades": len(comm),
            "tw_primal_cobertura": tw, "arestas_primal": P.number_of_edges()}



def sa(inst, passos=400000, semente=1, fibras=True):
    """Recozimento: K fixo, 5+5 palavras nos blocos 1 e 2, troca uma palavra por outra do mesmo
    bloco. Custo = descobertos + 3 * déficit de fibra. Devolve o menor número de descobertos
    entre os estados sem déficit (cota SUPERIOR do mínimo; o CP-SAT dá a inferior)."""
    import math
    import random
    import numpy as np
    rng = random.Random(semente)
    s, K, t = inst
    P = np.array(PTS)
    bola = [np.flatnonzero((P != np.array(c)).sum(1) <= R) for c in PTS]
    blocos = [[i for i, c in enumerate(PTS) if c[0] == b] for b in (1, 2)]
    cnt = np.zeros(len(PTS), int)
    fib = np.zeros((N, Q), int)
    for k in K:
        i = VAR[(0,) + k] - 1
        cnt[bola[i]] += 1
        fib[np.arange(N), P[i]] += 1
    cur = [rng.sample(b, tb) for b, tb in zip(blocos, t)]
    for b in cur:
        for i in b:
            cnt[bola[i]] += 1
            fib[np.arange(N), P[i]] += 1

    def custo():
        d = np.maximum(s - fib[1:], 0).sum() if fibras else 0
        return int((cnt == 0).sum()), int(d)
    u, d = custo()
    melhor = u if d == 0 else 10 ** 9
    T0 = 2.0
    for it in range(passos):
        T = T0 * (1 - it / passos) + 0.05
        bi = rng.randrange(2)
        j = rng.randrange(len(cur[bi]))
        old, new = cur[bi][j], rng.choice(blocos[bi])
        if new in cur[bi]:
            continue
        cnt[bola[old]] -= 1
        fib[np.arange(N), P[old]] -= 1
        cnt[bola[new]] += 1
        fib[np.arange(N), P[new]] += 1
        u2, d2 = custo()
        delta = (u2 + 3 * d2) - (u + 3 * d)
        if delta <= 0 or rng.random() < math.exp(-delta / T):
            cur[bi][j], u, d = new, u2, d2
            if d == 0 and u < melhor:
                melhor = u
        else:
            cnt[bola[new]] -= 1
            fib[np.arange(N), P[new]] -= 1
            cnt[bola[old]] += 1
            fib[np.arange(N), P[old]] += 1
    return melhor


def gama(K):
    """gamma_1(U): menor número de bolas de raio 1 em Z_3^5 que cobrem U (os pontos da fatia 0
    a distância > 2 de K). Cada palavra fora da fatia 0 cobre, na fatia 0, a bola de raio 1 da
    sua projeção; logo gamma_1(U) > M - s* = 10 já torna a instância inviável (lema da fatia
    refinado: a contagem |U| <= 10 * 11 é o caso em que as bolas não se sobrepõem)."""
    import numpy as np
    from scipy.optimize import LinearConstraint, milp
    U = fatia.descobertos(Q, N - 1, R, K)
    if not U:
        return 0
    C = list(itertools.product(range(Q), repeat=N - 1))
    A = np.array([[int(fatia.dist(u, c) <= 1) for c in C] for u in U])
    r = milp(np.ones(len(C)), constraints=LinearConstraint(A, lb=1), integrality=np.ones(len(C)),
             bounds=(0, 1))
    return int(round(r.fun))



def nu(K):
    """nu(U): maior subconjunto de U com distâncias duas a duas >= 3. Nenhuma bola de raio 1
    contém dois desses pontos, então gamma_1(U) >= nu(U) (dualidade fraca, o lema de
    empacotamento): nu(U) > M - s* é uma prova de inviabilidade que cabe numa linha."""
    import numpy as np
    from scipy.optimize import LinearConstraint, milp
    U = fatia.descobertos(Q, N - 1, R, K)
    if not U:
        return 0
    pares = [(i, j) for i in range(len(U)) for j in range(i + 1, len(U))
             if fatia.dist(U[i], U[j]) <= 2]
    A = np.zeros((max(len(pares), 1), len(U)))
    for k, (i, j) in enumerate(pares):
        A[k, i] = A[k, j] = 1
    r = milp(-np.ones(len(U)), constraints=LinearConstraint(A, ub=1), integrality=np.ones(len(U)),
             bounds=(0, 1))
    return int(round(-r.fun))


def tau(K):
    """Cota do LP (cobertura fracionária) para gamma_1(U)."""
    import numpy as np
    from scipy.optimize import linprog
    U = fatia.descobertos(Q, N - 1, R, K)
    C = list(itertools.product(range(Q), repeat=N - 1))
    A = np.array([[int(fatia.dist(u, c) <= 1) for c in C] for u in U])
    return linprog(np.ones(len(C)), A_ub=-A, b_ub=-np.ones(len(U)), bounds=(0, 1)).fun


def nucleo_prova(opb_txt, prova):
    """Linhas do OPB (0 = primeira restrição) alcançadas, de trás para frente, a partir da
    contradição final da prova do RoundingSat (hints dos `rup` e operandos dos `p`). Uma
    igualdade vira duas restrições no VeriPB. É um núcleo da prova, não um núcleo mínimo: a
    conferência é rodar de novo só com ele (ver `opb_subconjunto`)."""
    dono = {}
    cid = 0
    for k, ln in enumerate(opb_txt.splitlines()[1:]):
        for _ in range(2 if " = " in ln else 1):
            cid += 1
            dono[cid] = k
    deps, fim = {}, None
    with open(prova) as f:
        for ln in f:
            if ln.startswith("rup"):
                cid += 1
                deps[cid] = [int(x) for x in ln.split(";", 1)[1].split()]
            elif ln.startswith("p "):
                cid += 1
                deps[cid] = [int(x) for x in ln.split()[1:] if x.isdigit()]
            elif ln.startswith("conclusion"):
                fim = int(ln.split(":")[1])
    usados, pilha, visto = set(), [fim], set()
    while pilha:
        c = pilha.pop()
        if c in visto:
            continue
        visto.add(c)
        if c in dono:
            usados.add(dono[c])
        else:
            pilha += deps.get(c, [])
    return usados


def opb_subconjunto(opb_txt, linhas):
    cab, *res = opb_txt.splitlines()
    sel = [ln for k, ln in enumerate(res) if k in linhas]
    neq = sum(" = " in ln for ln in sel)
    return f"* #variable= {len(PTS)} #constraint= {len(sel)} #equal= {neq} intsize= 8\n" + \
        "\n".join(sel) + "\n"


def lex(livres, perms, prefixo=40):
    """Lex-leader truncado (x <=_lex g(x) nos primeiros `prefixo` pontos movidos), em PB linear:
    sum_k 2^(p-k) (x_{g(i_k)} - x_{i_k}) >= 0 sobre o prefixo (coeficientes cabem em 64 bits)."""
    out = []
    for g in perms:
        sup = [v for v in livres if g.get(v, v) != v][:prefixo]
        termos = []
        for k, v in enumerate(sup):
            w = 2 ** (len(sup) - 1 - k)
            termos += [f"+{w} x{g[v]}", f"-{w} x{v}"]
        if termos:
            out.append(" ".join(termos) + " >= 0 ;")
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--instancias", required=True)
    ap.add_argument("--idx", type=int, required=True)
    ap.add_argument("cmd", choices=["opb", "cnf", "medir", "lex"])
    ap.add_argument("--saida")
    a = ap.parse_args()
    inst = instancia(json.load(open(a.instancias)), a.idx)
    livres, cons = reduzir(inst)
    if a.cmd == "opb":
        txt, h = opb(inst)
        open(a.saida, "w").write(txt)
        print(h)
    elif a.cmd == "cnf":
        nv, cls = cnf(livres, cons)
        with open(a.saida, "w") as f:
            f.write(f"p cnf {nv} {len(cls)}\n")
            f.writelines(" ".join(map(str, c)) + " 0\n" for c in cls)
        print(nv, len(cls))
    elif a.cmd == "lex":
        txt, _ = opb(inst)
        _, perms = nauty(livres, cons)
        ex = lex(livres, perms)
        cab, resto = txt.split("\n", 1)
        nc = int(cab.split("#constraint=")[1].split()[0])
        cab = cab.replace(f"#constraint= {nc}", f"#constraint= {nc + len(ex)}")
        open(a.saida, "w").write(cab + "\n" + resto + "\n".join(ex) + "\n")
        print(len(ex), "restrições lex")
    else:
        nv, cls = cnf(livres, cons)
        gs = estabilizador(inst[1])
        tam, perms = nauty(livres, cons)
        r = {"idx": a.idx, "s": inst[0], "blocos": list(inst[2]),
             "config": ["".join(map(str, k)) for k in inst[1]],
             "sha256_opb": opb(inst)[1], "livres": len(livres), "restricoes": len(cons),
             "por_tipo": dict(Counter(c[3] for c in cons)),
             "cob_tam_min": min(len(c[0]) for c in cons if c[3] == "cob"),
             "U_fatia0": len(fatia.descobertos(Q, N - 1, R, inst[1])),
             "cnf_vars": nv, "cnf_clausulas": len(cls),
             "estab_K": len(gs), "aut_formula": tam, "geradores": len(perms)}
        r.update(up(livres, cons))
        r.update(grafo(livres, cons))
        r["sa_descobertos"] = min(sa(inst, 200000, sem) for sem in (1, 2))
        r["sa_descobertos_sem_fibras"] = sa(inst, 200000, 1, False)
        r["gama1_U"], r["tau_U"] = gama(inst[1]), round(tau(inst[1]), 3)
        txt = json.dumps(r)
        print(txt)
        if a.saida:
            open(a.saida, "w").write(txt + "\n")


if __name__ == "__main__":
    main()
