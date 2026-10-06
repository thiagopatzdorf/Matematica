#!/usr/bin/env python3
"""Reconstrói e confere os códigos explícitos transcritos de artigos (data/literatura/*.json).

Cada JSON de data/literatura/ traz a citação completa (autores, título, veículo, DOI) e os dados
explícitos do artigo (listas de palavras, matrizes do método matricial, matrizes de verificação,
grupos de automorfismos com representantes de órbita) ou uma construção explícita a partir de
outros itens (soma direta amalgamada, soma direta em blocos, repetição de coordenada, Corolário 3
de Kéri–Östergård 2005). O PDF nunca é versionado: só os fatos matemáticos e o lugar exato.

Este módulo é o avaliador exato, independente do Lean e do tools/verify/verify.c:

* binário (n ≤ 30): bitset de 2^n bits; R rodadas de "vizinhos" e contagem de pontos descobertos;
* q-ário pelo Corolário 3 (KO05): cada ingrediente é conferido r-sobrejetivo por exaustão (toda
  escolha de r coordenadas vê todas as v^r tuplas); a cobertura vem do pombal do corolário e,
  quando q^n ≤ FORCA_BRUTA, também é conferida ponto a ponto.

    python3 tools/literatura/codigos_papers.py              # reconstrói, confere, compara ao ledger
    python3 tools/literatura/codigos_papers.py --escrever   # grava data/codes/ (só os elegíveis)

Um código cujo raio medido difere do anunciado é um ACHADO: aparece como FALHA no relatório e
o teste tests/test_literatura_codigos.py fixa o resultado (não se corrige a transcrição para o
número bater; a transcrição é conferida contra a imagem da página).
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import sys
from functools import lru_cache
from pathlib import Path

import numpy as np

RAIZ = Path(__file__).resolve().parents[2]
LIT = RAIZ / "data" / "literatura"
SURJ = LIT / "surjetivos"
CODES = RAIZ / "data" / "codes"
# Teto do verificador oficial em C (tools/verify/verify.c: MAXN 20, MAXQ 10) e do custo que o
# check_all do CI aguenta (M · |bola| marcações): acima disso o código não vai para data/codes/.
MAXN_C, MAXQ_C, CUSTO_C = 20, 10, 50_000_000
FORCA_BRUTA = 3_000_000  # q^n até onde a cobertura q-ária é conferida ponto a ponto


# ----------------------------------------------------------------------------- binário

def hexs(xs):
    return [int(x, 16) for x in xs]


def s2i(s: str) -> int:
    """Palavra '0101...' do artigo (coordenada 1 à esquerda) -> inteiro (coordenada j = bit j-1)."""
    return sum(1 << j for j, ch in enumerate(s) if ch == "1")


def i2s(x: int, n: int) -> str:
    return "".join("1" if x >> j & 1 else "0" for j in range(n))


def matriz(n: int, k: int, colunas, S):
    """Método matricial: A = [I_k M] (k × n), C = {x : A x ∈ S}; |C| = |S| · 2^(n-k)."""
    m = n - k
    assert len(colunas) == m, (n, k, len(colunas))
    out = []
    for y in range(1 << m):
        my = 0
        for j in range(m):
            if y >> j & 1:
                my ^= colunas[j]
        out.extend((s ^ my) | (y << k) for s in S)
    return out


def automorfismo(n: int, ciclos, barras):
    """chi = sigma tau_S: complementa as coordenadas de S (barras) e leva a coordenada i a sigma(i)."""
    sig = list(range(n))
    for c in ciclos:
        for a, b in zip(c, c[1:] + c[:1]):
            sig[a - 1] = b - 1
    S = sum(1 << (i - 1) for i in barras)

    def f(x):
        x ^= S
        return sum(1 << sig[j] for j in range(n) if x >> j & 1)
    return f


def orbitas(n, geradores, reps, complementos):
    gens = [automorfismo(n, g["ciclos"], g.get("barras", [])) for g in geradores]
    out = set()
    for w in reps:
        pilha = [s2i(w)]
        vistos = set(pilha)
        while pilha:
            x = pilha.pop()
            for g in gens:
                y = g(x)
                if y not in vistos:
                    vistos.add(y)
                    pilha.append(y)
        out |= vistos
    if complementos:
        cheio = (1 << n) - 1
        out |= {cheio ^ x for x in out}
    return sorted(out)


def mover_para_fim(x, n, i):
    bits = [x >> j & 1 for j in range(n)]
    b = bits.pop(i)
    bits.append(b)
    return sum(v << j for j, v in enumerate(bits))


def ads(A, nA, iA, B, nB, iB):
    """Soma direta amalgamada (Cohen–Lobstein–Sloane): A normal na coordenada iA (levada ao fim),
    B na coordenada iB (que some): C = A_0 ⊕ B_0' ∪ A_1 ⊕ B_1'. Comprimento nA + nB - 1."""
    As = [mover_para_fim(a, nA, iA) for a in A]
    Bd = []
    for b in B:
        bits = [b >> j & 1 for j in range(nB)]
        t = bits.pop(iB)
        Bd.append((t, sum(v << j for j, v in enumerate(bits))))
    return sorted({a | (bp << nA) for a in As for t, bp in Bd if t == (a >> (nA - 1) & 1)})


def raio_ok_binario(code, n: int, R: int) -> int:
    """Pontos de F_2^n a distância > R do código (0 = cobre). Bitset de 2^n bits, exato."""
    W = max(1, (1 << n) // 64)
    cur = np.zeros(W, dtype=np.uint64)
    idx = np.array(sorted(set(code)), dtype=np.uint64)
    np.bitwise_or.at(cur, (idx >> np.uint64(6)).astype(np.int64),
                     np.left_shift(np.uint64(1), idx & np.uint64(63)))
    mk = [0x5555555555555555, 0x3333333333333333, 0x0F0F0F0F0F0F0F0F,
          0x00FF00FF00FF00FF, 0x0000FFFF0000FFFF, 0x00000000FFFFFFFF]
    for _ in range(R):
        nx = cur.copy()
        for j in range(n):
            if j < 6:
                s, m = np.uint64(1 << j), np.uint64(mk[j])
                nx |= ((cur & m) << s) | ((cur >> s) & m)
            else:
                s = 1 << (j - 6)
                nx |= cur.reshape(-1, 2, s)[:, ::-1, :].reshape(-1)
        cur = nx
    total = 1 << n
    cobertos = int(sum(bin(int(w)).count("1") for w in cur)) if W < 64 else \
        int(np.unpackbits(cur.view(np.uint8)).sum())
    if n < 6:
        cobertos = bin(int(cur[0]) & ((1 << total) - 1)).count("1")
    return total - cobertos


# ----------------------------------------------------------------------------- itens dos JSON

def carregar(chave: str) -> dict:
    return json.loads((LIT / f"{chave}.json").read_text(encoding="utf-8"))


def construir_binario(item: dict, ctx: dict):
    t = item["tipo"]
    n = item["n"]
    if t == "matriz":
        return matriz(n, item["k"], hexs(item["colunas_M"]), hexs(item["S"]))
    if t == "linear":
        k = n - int(round(np.log2(item["M"])))  # número de linhas de H = [I M]
        return matriz(n, k, hexs(item["colunas_M"]), [0])
    if t == "lista_hex":
        return sorted({w for p in item["partes"] for w in hexs(p)})
    if t == "lista":
        return sorted({s2i(w) for w in item["palavras"]})
    if t == "orbitas":
        return orbitas(n, item["geradores"], item["representantes"], item.get("complementos", False))
    if t == "repetir":  # ADS com [3,1]1 aplicada m vezes: a coordenada i aparece 2m+1 vezes
        base = ctx[item["base"]]
        nb, i, e = base["n"], item["coordenada"] - 1, item["copias"]
        return sorted({a | sum(((a >> i) & 1) << (nb + c) for c in range(e)) for a in base["palavras"]})
    if t == "ads":
        A, B = ctx[item["A"]], ctx[item["B"]]
        return ads(A["palavras"], A["n"], item["iA"] - 1, B["palavras"], B["n"], item["iB"] - 1)
    if t == "bds":  # soma direta em blocos: ∪ A_i ⊕ B_i, A primeiro
        Ap = [[s2i(w) for w in p] for p in item["A_partes"]]
        Bp = [hexs(p) for p in ctx[item["B"]]["item"]["partes"]]
        nA = len(item["A_partes"][0][0])
        return sorted({a | (b << nA) for P, Q in zip(Ap, Bp) for a in P for b in Q})
    raise ValueError(f"tipo desconhecido {t!r} em {item['id']}")


def reconstruir_binarios(chave: str) -> list[dict]:
    """Reconstrói os itens binários do JSON, na ordem (construções usam itens anteriores)."""
    J = carregar(chave)
    ctx: dict = {}
    out = []
    for item in J["itens"]:
        if item.get("q", 2) != 2 or item["tipo"] in ("nao_reproduzido", "corolario3", "surjetivo"):
            continue
        if item["n"] > 30:  # fora do bitset de 2^n bits (o [37,25]3 não tem célula na tabela)
            continue
        pal = construir_binario(item, ctx)
        r = {"id": item["id"], "n": item["n"], "R": item["R"], "M": item["M"], "palavras": pal,
             "item": item, "chave": chave}
        ctx[item["id"]] = r
        out.append(r)
    return out


# ----------------------------------------------------------------------------- q-ário: Corolário 3

def _irred(p, m):
    # x^2+x+1, x^3+x+1, x^4+x+1, x^2+1 (irredutíveis)
    return {(2, 2): [1, 1, 1], (2, 3): [1, 1, 0, 1], (2, 4): [1, 1, 0, 0, 1], (3, 2): [1, 0, 1]}[(p, m)]


@lru_cache(None)
def corpo(v: int):
    """Tabelas (soma, produto) de GF(v), elementos 0..v-1 (coeficientes em base p)."""
    for p in (2, 3, 5, 7, 11, 13, 17, 19):
        m = 1
        while p ** m < v:
            m += 1
        if p ** m == v:
            break
    else:
        raise ValueError(f"{v} não é potência de primo")
    if m == 1:
        return ([[(a + b) % v for b in range(v)] for a in range(v)],
                [[(a * b) % v for b in range(v)] for a in range(v)])
    f = _irred(p, m)  # coeficientes do grau 0 ao m

    def dig(a):
        return [(a // p ** i) % p for i in range(m)]

    def und(d):
        return sum(x * p ** i for i, x in enumerate(d))

    def mul(a, b):
        da, db = dig(a), dig(b)
        prod = [0] * (2 * m - 1)
        for i, x in enumerate(da):
            for j, y in enumerate(db):
                prod[i + j] = (prod[i + j] + x * y) % p
        for g in range(2 * m - 2, m - 1, -1):
            c = prod[g]
            if c:
                for i in range(m + 1):
                    prod[g - m + i] = (prod[g - m + i] - c * f[i]) % p
        return und(prod[:m])
    soma = [[und([(x + y) % p for x, y in zip(dig(a), dig(b))]) for b in range(v)] for a in range(v)]
    return soma, [[mul(a, b) for b in range(v)] for a in range(v)]


def surjetivo_mds(v: int, n: int, t: int):
    """Reed–Solomon estendido sobre GF(v): v^t palavras, t-sobrejetivo para n ≤ v + 1."""
    assert n <= v + 1
    soma, prod = corpo(v)
    out = []
    for msg in itertools.product(range(v), repeat=t):
        w = []
        for a in range(n - 1):  # avalia f(x) = sum msg_i x^i nos pontos 0..n-2
            acc, pw = 0, 1
            for c in msg:
                acc = soma[acc][prod[c][pw]]
                pw = prod[pw][a]
            w.append(acc)
        w.append(msg[-1])  # ponto no infinito: coeficiente líder
        out.append(tuple(w))
    return out


def surjetivo_ks(n: int):
    """Kleitman–Spencer: 6 linhas binárias 2-sobrejetivas para n ≤ 10 (colunas = 3-subconjuntos de
    {1..5} com a linha 0 nula; dois 3-subconjuntos distintos de 5 se cortam e não se contêm)."""
    cols = [c for c in itertools.combinations(range(1, 6), 3)][:n]
    assert len(cols) == n
    return [tuple(1 if r in c else 0 for c in cols) for r in range(6)]


def ler_surjetivo(v: int, n: int, t: int, N: int):
    p = SURJ / f"ca_t{t}_n{n}_v{v}_N{N}.txt"
    return [tuple(int(x) for x in linha.split()) for linha in p.read_text().splitlines() if linha.strip()]


def ingrediente(v: int, n: int, t: int):
    """(N, palavras, origem) do menor ingrediente t-sobrejetivo disponível para (v, n)."""
    if v == 1:
        return 1, [tuple([0] * n)], "trivial (uma palavra)"
    cand = []
    for p in SURJ.glob(f"ca_t{t}_n{n}_v{v}_N*.txt"):
        N = int(p.stem.split("_N")[1])
        cand.append((N, ler_surjetivo(v, n, t, N), f"data/literatura/surjetivos/{p.name}"))
    try:
        corpo(v)
        if n <= v + 1:
            cand.append((v ** t, surjetivo_mds(v, n, t), f"Reed–Solomon estendido sobre GF({v})"))
    except ValueError:
        pass
    if v == 2 and t == 2 and 5 <= n <= 10:
        cand.append((6, surjetivo_ks(n), "Kleitman–Spencer (6 linhas)"))
    if not cand:
        return None
    return min(cand, key=lambda c: c[0])


def e_surjetivo(pal, v: int, n: int, t: int) -> bool:
    for S in itertools.combinations(range(n), t):
        vistos = {tuple(w[j] for j in S) for w in pal}
        if len(vistos) != v ** t or any(x >= v for w in pal for x in w):
            return False
    return True


def melhor_particao(q: int, n: int, t: int, k: int):
    """Partição q = v_1 + … + v_k que minimiza a soma dos ingredientes disponíveis."""
    custo = {v: (ingrediente(v, n, t) or (None,))[0] for v in range(1, q + 1)}

    @lru_cache(None)
    def f(resto, partes, mx):
        if partes == 0:
            return (0, ()) if resto == 0 else (10 ** 18, ())
        melhor = (10 ** 18, ())
        for v in range(min(resto, mx), 0, -1):
            if custo[v] is None:
                continue
            c, ps = f(resto - v, partes - 1, v)
            if c + custo[v] < melhor[0]:
                melhor = (c + custo[v], (v,) + ps)
        return melhor
    return f(q, k, q)


def corolario3(q: int, n: int, R: int):
    """Código do Corolário 3 de KO05 para K_q(n, R), n = k(r-1)+1, r = n - R: união dos
    ingredientes r-sobrejetivos sobre os sub-alfabetos disjuntos {off, …, off+v-1}."""
    t = n - R
    if t < 2 or (n - 1) % (t - 1):
        return None
    k = (n - 1) // (t - 1)
    total, partes = melhor_particao(q, n, t, k)
    if total >= 10 ** 18:
        return None
    off, pal, ings = 0, [], []
    for v in partes:
        N, ws, origem = ingrediente(v, n, t)
        ings.append({"v": v, "off": off, "N": N, "origem": origem, "palavras": ws})
        pal.extend(tuple(off + x for x in w) for w in ws)
        off += v
    return {"q": q, "n": n, "R": R, "t": t, "k": k, "partes": list(partes), "M": len(pal),
            "ingredientes": ings, "palavras": pal}


def cobre_forca_bruta(pal, q: int, n: int, R: int) -> bool:
    C = np.array(pal, dtype=np.int16)
    tot = q ** n
    for i in range(0, tot, 20000):
        ids = np.arange(i, min(tot, i + 20000), dtype=np.int64)
        bloco = np.stack([(ids // q ** j) % q for j in range(n)], axis=1).astype(np.int16)
        d = (bloco[:, None, :] != C[None, :, :]).sum(axis=2).min(axis=1)
        if (d > R).any():
            return False
    return True


# ----------------------------------------------------------------------------- ledger e saída

def celulas():
    return {(c["q"], c["n"], c["R"]): c for c in json.loads((RAIZ / "ledger" / "cells.json").read_text())["cells"]}


def texto_palavra(w, q):
    return (" " if q > 10 else "").join(str(x) for x in w)


def palavras_binarias_como_tuplas(pal, n):
    return [tuple(x >> j & 1 for j in range(n)) for x in pal]


def elegivel_data_codes(q, n, R, M):
    if q > MAXQ_C or n > MAXN_C:
        return False
    bola = sum(__import__("math").comb(n, i) * (q - 1) ** i for i in range(R + 1))
    return M * bola <= CUSTO_C


def sha_arquivo(linhas):
    return hashlib.sha256(("\n".join(linhas) + "\n").encode()).hexdigest()


def relatorio(escrever=False, nmax_bin=30, conferir_ko=True):
    cells = celulas()
    linhas = []
    for chave in ("ostergard_kaikkonen_1998", "ostergard_weakley_1999",
                  "hamalainen_honkala_kaikkonen_litsyn_1993"):
        for r in reconstruir_binarios(chave):
            n, R, M = r["n"], r["R"], r["M"]
            if n > nmax_bin:
                continue
            unc = raio_ok_binario(r["palavras"], n, R) if n <= 30 else None
            ok = len(r["palavras"]) == M and unc == 0
            c = cells.get((2, n, R))
            linhas.append({"chave": chave, "id": r["id"], "q": 2, "n": n, "R": R, "M": M,
                           "medido_M": len(r["palavras"]), "descobertos": unc, "ok": ok,
                           "ub_publicada": c["published"]["ub"]["value"] if c else None,
                           "estado": c["certification"]["ub"]["state"] if c else None,
                           "tuplas": palavras_binarias_como_tuplas(r["palavras"], n)})
    ko = carregar("keri_ostergard_2005")
    for it in ko["itens"]:
        if it["tipo"] != "corolario3":
            continue
        q, n, R = it["q"], it["n"], it["R"]
        cod = corolario3(q, n, R)
        okp = cod is not None and cod["M"] == it["M"] and cod["partes"] == it["partes"]
        if conferir_ko:
            okp = okp and all(e_surjetivo(g["palavras"], g["v"], n, cod["t"]) for g in cod["ingredientes"])
        forca = conferir_ko and okp and q ** n <= FORCA_BRUTA
        if forca:
            okp = cobre_forca_bruta(cod["palavras"], q, n, R)
        c = cells.get((q, n, R))
        linhas.append({"chave": "keri_ostergard_2005", "id": it["id"], "q": q, "n": n, "R": R,
                       "M": it["M"], "medido_M": cod["M"] if cod else None,
                       "descobertos": (0 if okp else None) if forca else "pombal",
                       "ok": okp, "ub_publicada": c["published"]["ub"]["value"] if c else None,
                       "estado": c["certification"]["ub"]["state"] if c else None,
                       "tuplas": cod["palavras"] if cod else []})
    if escrever:
        for L in linhas:
            if L["ok"] and L["ub_publicada"] == L["M"] and L["estado"] == "CLAIMED" \
                    and elegivel_data_codes(L["q"], L["n"], L["R"], L["M"]):
                txt = sorted(texto_palavra(w, L["q"]) for w in L["tuplas"])
                p = CODES / f"q{L['q']}_n{L['n']}_R{L['R']}_M{L['M']}.txt"
                if not p.exists():
                    p.write_text("\n".join(txt) + "\n")
    return linhas


HOJE = "2026-10-06"


def registrar(linhas):
    """Para cada código gravado em data/codes/ que iguala a cota publicada de uma célula CLAIMED:
    `ours_computational` em ledger/ours.json e o registro de proveniência (seis campos)."""
    ours_p, prov_p = RAIZ / "ledger" / "ours.json", RAIZ / "ledger" / "provenance.json"
    ours, prov = json.loads(ours_p.read_text()), json.loads(prov_p.read_text())
    cells = celulas()
    feitos = []
    for L in linhas:
        q, n, R, M = L["q"], L["n"], L["R"], L["M"]
        arq = CODES / f"q{q}_n{n}_R{R}_M{M}.txt"
        c = cells.get((q, n, R))
        if not (L["ok"] and arq.exists() and c and c["published"]["ub"]["value"] == M
                and c["certification"]["ub"]["state"] == "CLAIMED"):
            continue
        chave = f"{q},{n},{R}"
        if chave in ours["cells"]:
            continue
        pid = f"P-lit-{q}-{n}-{R}-{M}"
        J = carregar(L["chave"])
        cit = J["citacao"]
        sha = hashlib.sha256(arq.read_bytes()).hexdigest()
        rel = str(arq.relative_to(RAIZ))
        ours["cells"][chave] = {"ours_computational": {"M": M, "file": rel, "sha256": sha, "provenance": pid},
                                "ours_lean": None}
        prov["registros"][pid] = {
            "codigo": rel,
            "gerador": f"tools/literatura/codigos_papers.py a partir de data/literatura/{L['chave']}.json "
                       f"(item {L['id']}); fonte: {', '.join(cit['autores'])}, {cit['titulo']}, "
                       f"{cit['veiculo']} {cit['volume']} ({cit['ano']}), DOI {cit['doi']}",
            "commit": None,
            "seed": None,
            "comando": "python3 tools/literatura/codigos_papers.py --escrever",
            "data": HOJE,
            "agente": "James.V1",
            "lacuna": "Reconstrução determinística da transcrição (sem semente); o gerador entra no mesmo "
                      "commit do código. Construção e dependências descritas no item do JSON.",
            "gap": "deterministic reconstruction from the transcription (no seed); the generator lands in "
                   "the same commit as the code. Construction and dependencies are described in the JSON item."}
        feitos.append(chave)
    ours["atualizado"] = HOJE
    ours_p.write_text(json.dumps(ours, ensure_ascii=False, indent=2) + "\n")
    prov_p.write_text(json.dumps(prov, ensure_ascii=False, indent=2) + "\n")
    return feitos


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--escrever", action="store_true", help="grava data/codes/ para os elegíveis")
    ap.add_argument("--registrar", action="store_true",
                    help="com --escrever: registra em ledger/ours.json e ledger/provenance.json")
    a = ap.parse_args()
    linhas = relatorio(a.escrever)
    if a.registrar:
        print("registradas:", registrar(linhas))
    for L in linhas:
        marca = "ok   " if L["ok"] else "FALHA"
        cmp = "" if L["ub_publicada"] is None else (
            "= publicada" if L["M"] == L["ub_publicada"] else
            ("< publicada" if L["M"] < L["ub_publicada"] else f"> publicada ({L['ub_publicada']})"))
        print(f"{marca} {L['id']:<22} K{L['q']}({L['n']},{L['R']}) <= {L['M']:<6} "
              f"descobertos={L['descobertos']} {cmp} [{L['estado']}]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
