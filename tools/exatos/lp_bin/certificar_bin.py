#!/usr/bin/env python3
"""Certificados de Farkas inteiros para as instâncias binárias da fatia mínima.

Instância (s*, K, t) de `fatia_bin.py`: o sistema 0-1 de `tools/exatos/k362/contagem/
certificar_lp.py` com q = 2 (cobertura, fibras >= s*, tamanho M, bloco t_1, fatia 0 fixa).

**LP reduzido por simetria.** Seja H o grupo das permutações de coordenadas 1..n−1 que trocam
entre si colunas idênticas de K. H fixa a coordenada 0 e fixa K ponto a ponto, então preserva o
sistema (permuta linhas de cobertura, permuta fibras dentro do tipo, mantém as igualdades e a
fatia fixa). Se z é solução 0-1, a média de z sobre H é solução fracionária constante nas
órbitas de H. Logo basta o LP sobre um peso w_B por órbita B da fatia 1. A órbita de um ponto é
dada por x_0 e pelo número de uns em cada tipo de coluna.

**Certificado no espaço inteiro.** O dual do LP reduzido (ỹ_A por órbita de linha de cobertura,
ỹ por tipo de fibra, μ̃) se levanta ao sistema completo: y_x = ỹ_A·L/|A| para cada x em A,
a linha reduzida de fibra do tipo v é a soma das m_v linhas de coordenada, e cada uma leva ỹ·L;
μ = (0, μ̃·L), com L o mmc dos |A| usados. Então g_c = g̃_B·L/|B| e a folga do certificado completo é L vezes a do reduzido. O
arquivo gravado traz o certificado **completo** (sem nada desta simetria). Folhas sem ramos
estão no formato de `tools/exatos/k362/contagem/verificar.py`; todas passam em `verificar_bin.py`.

Quando o LP reduzido é viável, ramifica sem sair do espaço reduzido: na soma inteira
N_B = Σ_{c∈B} z_c da órbita B mais fracionária (N_B <= k / N_B >= k + 1, restrições invariantes
por H), e, quando todos os N_B são inteiros, em z_c = 1 / z_c = 0 de um ponto c de uma órbita
parcialmente cheia (c passa a refinar o agrupamento das colunas, e o grupo encolhe para o
estabilizador de c). Cada decisão vai para a folha como linha Σ_{c∈S} z_c >= r ou <= r, com o
conjunto S explícito, e é conferida por `verificar_bin.py` (escrito do zero, só stdlib).

  python3 tools/exatos/lp_bin/certificar_bin.py --n 10 --R 3 --M 11 --instancias i.json --saida c.jsonl.gz
"""
import argparse
import gzip
import json
import sys
import time
from math import gcd

import numpy as np
from scipy.optimize import linprog
from scipy.sparse import csr_matrix, hstack, identity, vstack

REGRA = ['fracionaria']  # escolha da órbita para ramificar
MOTIVO = []  # por que a última ramificação desistiu (diagnóstico)
ESCALAS = (1, 2, 3, 4, 6, 8, 12, 24, 60, 120, 1000, 10**4, 10**5, 10**6, 10**8)


def _popcount(n):
    return np.array([bin(i).count("1") for i in range(1 << n)], dtype=np.int16)


class Espaco:
    def __init__(self, n, R):
        self.n, self.R, self.N = n, R, 1 << n
        self.idx = np.arange(self.N)
        self.POP = _popcount(n)
        self.bits = (self.idx[:, None] >> (n - 1 - np.arange(n))) & 1


def ponto(k, n):
    """Índice de (0, k): coordenada 0 é o bit mais alto (ordem de itertools.product)."""
    v = 0
    for b in k:
        v = (v << 1) | int(b)
    return v


def reduzido(E, M, s, K, t, ramos=(), marcados=()):
    """ramos: [(pontos S, 'ge'|'le', r)] = Σ_{c ∈ S} z_c >= r ou <= r (S união de órbitas).
    marcados: [(c, v)] pontos da fatia 1 já decididos por um ramo; só refinam o agrupamento das
    colunas (o grupo encolhe para o estabilizador deles, e cada um vira órbita unitária). A
    decisão em si está em `ramos`, como linha Σ_{c} z_c >= 1 ou <= 0."""
    n, R, N, bits, POP, idx = E.n, E.R, E.N, E.bits, E.POP, E.idx
    m = n - 1
    cols = [tuple(k[j] for k in K) + tuple(int(bits[c, j + 1]) for c, _ in marcados) for j in range(m)]
    tipos = {}
    for j, cvec in enumerate(cols):
        tipos.setdefault(cvec, []).append(j + 1)
    tipos = list(tipos.items())
    mult = [len(js) + 1 for _, js in tipos]
    pesos = [int(np.prod(mult[i + 1:])) for i in range(len(tipos))]
    a = np.stack([bits[:, js].sum(1) for _, js in tipos], 1)
    nor_meia = int(np.prod(mult))
    oid = bits[:, 0] * nor_meia + a @ np.array(pesos)
    tam = np.bincount(oid, minlength=2 * nor_meia)
    rep = np.full(2 * nor_meia, -1)
    rep[oid[::-1]] = idx[::-1]
    Kp = np.array([ponto(k, n) for k in K], dtype=np.int64)
    um = np.arange(nor_meia, 2 * nor_meia)
    vivas = um[tam[um] > 0]
    col = {o: i for i, o in enumerate(vivas)}
    linhas, rhs, rot = [], [], []
    for o in range(2 * nor_meia):
        x = rep[o]
        if x < 0 or (len(Kp) and (POP[Kp ^ x] <= R).any()):
            continue
        perto = np.nonzero(POP[idx ^ x] <= R)[0]
        perto = perto[bits[perto, 0] == 1]
        row = np.zeros(len(vivas), dtype=np.int64)
        for oo, c in zip(*np.unique(oid[perto], return_counts=True)):
            row[col[oo]] = c
        linhas.append(row); rhs.append(1); rot.append(("cob", o))
    if s > 0:
        tb = tam[vivas]
        for i, (cvec, js) in enumerate(tipos):
            bv = ((vivas - nor_meia) // pesos[i]) % mult[i]
            uns = sum(cvec[:len(K)])
            mv = len(js)
            # linha da fibra (uma coordenada do tipo) vezes m_v, para ficar inteira
            linhas.append(tb * bv); rhs.append(mv * (s - uns)); rot.append(("fib", i, 1))
            linhas.append(tb * (mv - bv)); rhs.append(mv * (s - (s - uns))); rot.append(("fib", i, 0))
    for i, (pts, sent, r) in enumerate(ramos):
        cnt = np.bincount(oid[np.array(pts)], minlength=2 * nor_meia)[vivas].astype(np.int64)
        linhas.append(cnt if sent == "ge" else -cnt); rhs.append(r if sent == "ge" else -r)
        rot.append(("ramo", i, sent, r))
    lb, ub = np.zeros(len(vivas), dtype=np.int64), np.ones(len(vivas), dtype=np.int64)
    return dict(G=np.array(linhas, dtype=np.int64), h=np.array(rhs, dtype=np.int64), rot=rot,
                tam=tam, rep=rep, oid=oid, vivas=vivas, tipos=tipos, eq=tam[vivas], e=M - s,
                lb=lb, ub=ub, ramos=list(ramos), marcados=list(marcados))


def dual(G, h, Eq, e, lb, ub):
    """max y.h + mu.e − Σ u, u >= g ub, u >= g lb, Σ y <= 1 (G pode ser esparsa)."""
    ng, nv = G.shape
    Eq = np.atleast_2d(Eq)
    ne = Eq.shape[0]
    GT = hstack([csr_matrix(G).T, csr_matrix(Eq).T]).tocsr()
    I = identity(nv, format="csr")
    A = vstack([hstack([GT.multiply(ub[:, None]), -I]), hstack([GT.multiply(lb[:, None]), -I]),
                csr_matrix(np.r_[np.ones(ng), np.zeros(ne + nv)][None])]).tocsr()
    c = -np.r_[h, e, -np.ones(nv)]
    r = linprog(c, A_ub=A, b_ub=np.r_[np.zeros(2 * nv), 1.0],
                bounds=[(0, None)] * ng + [(None, None)] * (ne + nv), method="highs")
    if r.status != 0:
        return -1.0, None, None
    return -r.fun, r.x[:ng], r.x[ng:ng + ne]


def folga(G, h, Eq, e, lb, ub, y, mu):
    """Folga exata em inteiros Python (> 0 = inviável). lb/ub inteiros 0/1."""
    y = [int(v) for v in y]
    mu = [int(v) for v in mu]
    if any(v < 0 for v in y):
        return -1
    Eq = np.atleast_2d(Eq)
    nz = [i for i, v in enumerate(y) if v]
    g = [0] * G.shape[1]
    for i in nz:
        row = G[i]
        if hasattr(row, "indices"):
            for j, v in zip(row.indices, row.data):
                g[j] += y[i] * int(v)
        else:
            for j in np.nonzero(row)[0]:
                g[j] += y[i] * int(row[j])
    for k, mk in enumerate(mu):
        if mk:
            for j in np.nonzero(Eq[k])[0]:
                g[j] += mk * int(Eq[k][j])
    lhs = sum(y[i] * int(h[i]) for i in nz) + sum(mk * int(ek) for mk, ek in zip(mu, np.atleast_1d(e)))
    rhs = sum(max(gj * int(lb[j]), gj * int(ub[j])) for j, gj in enumerate(g))
    return lhs - rhs


def inteirar(G, h, Eq, e, lb, ub, y, mu):
    for esc in ESCALAS:
        yi = np.maximum(np.floor(y * esc + 1e-9), 0).astype(np.int64)
        mi = np.round(np.atleast_1d(mu) * esc).astype(np.int64)
        if folga(G, h, Eq, e, lb, ub, yi, mi) > 0:
            return yi, mi
    return None


def levantar(E, S, y, mu):
    """Certificado do sistema completo (formato de verificar.py) a partir do reduzido."""
    n, N = E.n, E.N
    L = 1
    for i in np.nonzero(y)[0]:
        r = S["rot"][i]
        if r[0] == "cob":
            d = int(S["tam"][r[1]])
            L = L * d // gcd(L, d)
    yf = {}
    for i in np.nonzero(y)[0]:
        r = S["rot"][i]
        if r[0] == "ramo":
            continue
        if r[0] == "cob":
            o = r[1]
            v = int(y[i]) * L // int(S["tam"][o])
            for x in np.nonzero(S["oid"] == o)[0]:
                yf[int(x)] = yf.get(int(x), 0) + v
        else:
            _, ti, a = r
            js = S["tipos"][ti][1]
            # linha reduzida = m_v × (linha de uma coordenada): cada coordenada leva y·L
            for j in js:
                k = N + (j - 1) * 2 + a
                yf[k] = yf.get(k, 0) + int(y[i]) * L
    ramos, yr = [], []
    for i, r in enumerate(S["rot"]):
        if r[0] == "ramo":
            ramos.append([[int(x) for x in S["ramos"][r[1]][0]], r[2], int(r[3])])
            yr.append(int(y[i]) * L)
    # a igualdade reduzida é o bloco b = 1 (Σ_{c_0=1} z_c = M − s)
    return {"fixos": [], "ramos": ramos, "yr": yr, "y": {str(k): v for k, v in sorted(yf.items())},
            "mu": [0, int(mu[0]) * L]}


def _raiz_reduzida(E, M, s, K, t, ramos, marcados):
    S = reduzido(E, M, s, K, t, ramos, marcados)
    nv = len(S["vivas"])
    lb, ub = S["lb"], S["ub"]
    v, y, mu = dual(S["G"].astype(float), S["h"].astype(float), S["eq"][None].astype(float),
                    np.array([float(S["e"])]), lb.astype(float), ub.astype(float))
    if v > 1e-9:
        r = inteirar(S["G"], S["h"], S["eq"][None], np.array([S["e"]]), lb, ub, y, mu)
        if r:
            return S, levantar(E, S, r[0], r[1]), None
    p = linprog(np.zeros(nv), A_ub=-S["G"], b_ub=-S["h"], A_eq=S["eq"][None], b_eq=[S["e"]],
                bounds=list(zip(lb, ub)), method="highs")
    return S, None, (p.x if p.status == 0 else None)


def agregado(E, M, s, K, t, ramos=(), marcados=(), prof=0, prof_max=150, orc=None):
    """Ramifica em N_B = Σ_{c ∈ B} z_c (inteiro) pela órbita B mais fracionária: N_B <= k ou
    N_B >= k + 1. As restrições são invariantes por H, então cada filho segue reduzível."""
    orc = orc if orc is not None else [400]
    orc[0] -= 1
    S, folha, x = _raiz_reduzida(E, M, s, K, t, list(ramos), list(marcados))
    if folha:
        return [folha]
    if x is None or prof >= prof_max or orc[0] <= 0:
        if x is None:
            MOTIVO.append("lp_inviavel_sem_certificado")
        else:
            MOTIVO.append("profundidade" if prof >= prof_max else "orcamento")
        return None
    N = x * S["tam"][S["vivas"]]
    fr = np.abs(N - np.floor(N) - 0.5)
    j = int(np.argmin(fr))
    if REGRA[0] == "maior" and fr[j] <= 0.5 - 1e-6:
        cand = np.nonzero(fr <= 0.5 - 1e-6)[0]
        j = int(cand[np.argmax(S["tam"][S["vivas"]][cand])])
    elif REGRA[0] == "mais_cheia" and fr[j] <= 0.5 - 1e-6:
        cand = np.nonzero(fr <= 0.5 - 1e-6)[0]
        j = int(cand[np.argmax(N[cand])])
    folhas = []
    if fr[j] > 0.5 - 1e-6:
        # todos os N_B inteiros: fixa um ponto de uma órbita parcialmente cheia (quebra simetria)
        parc = np.nonzero((x > 1e-6) & (x < 1 - 1e-6))[0]
        if not len(parc):
            MOTIVO.append("solucao_01")
            return None  # solução 0-1: seria um código
        c = int(S["rep"][S["vivas"][parc[np.argmax(S["tam"][S["vivas"][parc]])]]])
        for v in (1, 0):
            dec = ((c,), "ge", 1) if v else ((c,), "le", 0)  # z_c = v como linha, na ordem do caminho
            sub = agregado(E, M, s, K, t, tuple(ramos) + (dec,), tuple(marcados) + ((c, v),),
                           prof + 1, prof_max, orc)
            if sub is None:
                return None
            folhas += sub
        return folhas
    o, k = int(S["vivas"][j]), int(np.floor(N[j]))
    pts = tuple(int(p) for p in np.nonzero(S["oid"] == o)[0])
    for sent, r in (("le", k), ("ge", k + 1)):
        sub = agregado(E, M, s, K, t, tuple(ramos) + ((pts, sent, r),), marcados, prof + 1, prof_max, orc)
        if sub is None:
            return None
        folhas += sub
    return folhas


def certificar(E, M, s, K, t, ramos=True, orc=4000):
    """(folhas, modo) com modo 'reduzido', 'completo' ou None (sem certificado)."""
    S = reduzido(E, M, s, K, t)
    nv = len(S["vivas"])
    lb, ub = S["lb"], S["ub"]
    v, y, mu = dual(S["G"].astype(float), S["h"].astype(float), S["eq"][None].astype(float),
                    np.array([float(S["e"])]), lb.astype(float), ub.astype(float))
    if v > 1e-9:
        r = inteirar(S["G"], S["h"], S["eq"][None], np.array([S["e"]]), lb, ub, y, mu)
        if r:
            return [levantar(E, S, r[0], r[1])], "reduzido"
    if not ramos:
        return None, None
    f = agregado(E, M, s, K, t, orc=[orc])
    return (f, "agregado") if f else (None, None)


_E = None


def _trabalho(args):
    global _E
    n, R, M, i, (s, K, t), ramos, orc = args
    if _E is None:
        _E = Espaco(n, R)
    ti = time.time()
    folhas, modo = certificar(_E, M, s, [tuple(k) for k in K], t, ramos=ramos, orc=orc)
    return {"inst": i, "s": s, "K": K, "t": t, "modo": modo, "tempo_s": round(time.time() - ti, 3),
            "folhas": folhas}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    for k in ("n", "R", "M"):
        ap.add_argument("--" + k, type=int, required=True)
    ap.add_argument("--instancias", required=True)
    ap.add_argument("--saida", required=True)
    ap.add_argument("--sem-ramos", action="store_true", help="só o LP reduzido na raiz (medição)")
    ap.add_argument("--so", default="", help="índices, ex.: 0-99,150 (medição; a prova exige todos)")
    ap.add_argument("--refazer", help="certificados anteriores: refaz só as instâncias sem certificado")
    ap.add_argument("--orcamento", type=int, default=4000, help="nós da ramificação agregada por instância")
    ap.add_argument("-j", type=int, default=1)
    a = ap.parse_args()
    ins = json.load(open(a.instancias))
    idxs = list(range(len(ins)))
    if a.so:
        idxs = [i for p in a.so.split(",") for i in range(int(p.partition("-")[0]),
                                                          int(p.partition("-")[2] or p.partition("-")[0]) + 1)]
    antigos = {}
    if a.refazer:
        for linha in gzip.open(a.refazer, "rt"):
            r = json.loads(linha)
            if r["folhas"]:
                antigos[r["inst"]] = r
    tarefas = [(a.n, a.R, a.M, i, ins[i], not a.sem_ramos, a.orcamento) for i in idxs if i not in antigos]
    cont, ruins, t0 = {}, [], time.time()
    novos = {}
    from concurrent.futures import ProcessPoolExecutor
    with ProcessPoolExecutor(a.j) as ex:
        for reg in ex.map(_trabalho, tarefas, chunksize=1):
            novos[reg["inst"]] = reg
            print(reg["inst"], reg["modo"], reg["tempo_s"], flush=True)
    with gzip.open(a.saida, "wt") as f:
        for i in idxs:
            reg = antigos.get(i) or novos[i]
            f.write(json.dumps(reg, separators=(",", ":")) + "\n")
            cont[(reg["s"], reg["modo"])] = cont.get((reg["s"], reg["modo"]), 0) + 1
            if reg["folhas"] is None:
                ruins.append(i)
    print(f"K_2({a.n},{a.R}) M={a.M}: {len(idxs)} instâncias ({len(tarefas)} rodadas agora) em "
          f"{time.time() - t0:.1f} s; (s*, modo): {sorted(cont.items(), key=str)}; "
          f"sem certificado: {len(ruins)} {ruins[:30]}")
    sys.exit(1 if ruins else 0)


if __name__ == "__main__":
    main()
