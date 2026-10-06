#!/usr/bin/env python3
"""Gera, em lote, certificados Lean das cotas superiores do ledger: célula base + regra.

Para cada célula K_q(n,R) do ledger escolhe o certificado mais barato que atinge a melhor cota
superior conhecida (`best.ub`):

* base genérica, sem witness: espaço inteiro (`UB.univ`), raio grande (`UB.large_radius`),
  palavras constantes (`UB.constant_symbol`);
* witness explícito pequeno de tools/certificar/witnesses/ (conferido pelo kernel com
  `CoveringKernel.go`, via `UB.of_go`), ou um teorema já existente (K_7(4,2) ≤ 19);
* código linear sistemático de tools/certificar/lineares/ (Hamming, Golay, "linear code" do Kéri),
  conferido pelo kernel pelas síndromes, sem lista de palavras (`Syn.lin_cert`, lineares.py);
* regra a partir de outras células: soma direta, alongamento livre, coordenada muda, punção,
  monotonia do raio, projeção de alfabeto (CoveringLean/Regras.lean).

O fecho é uma relaxação até ponto fixo sobre todas as (q, n, R) com n até o maior n do ledger
para aquele q. Cada melhora vira um nó novo (as dependências são sempre nós anteriores, então a
ordem de criação é topológica e não há ciclo). Só os nós alcançáveis a partir das células cuja
cota bate com `best.ub` vão para o Lean.

Saídas (regeneradas por inteiro; não edite à mão):
* CoveringLean/Ledger/W<k>.lean: as listas de índices dos witnesses;
* CoveringLean/Ledger/Lin_K<q>_<n>_<R>.lean: os códigos lineares e as testemunhas do transversal;
* CoveringLean/Ledger/Cotas.lean: um teorema `CoveringLedger.K<q>_<n>_<R>_le_<M> : K q n R ≤ M`
  por célula certificada;
* ledger/formal_ub.json: o que o ledger/build.py lê para marcar a cota FORMALIZED.

    python3 tools/certificar/gerar.py            # gera
    python3 tools/certificar/gerar.py --resumo   # só conta, sem escrever
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import lineares  # noqa: E402
WIT = RAIZ / "tools" / "certificar" / "witnesses"
SAIDA_LEAN = RAIZ / "CoveringLean" / "Ledger"
SAIDA_JSON = RAIZ / "ledger" / "formal_ub.json"
# Teto de q^n · M por witness: o kernel confere ~10^4 unidades/s e a família da partição K_q(4,2)
# com q ≥ 13 (≥ 1,2·10^6) passou de 30 min e de 4 GB por arquivo neste container (q = 17 morreu por
# memória). Acima do teto o witness fica versionado mas fora do lote: ver --custo-max.
CUSTO_MAX = 1_200_000
CUSTO_POR_ARQUIVO = 2_000_000  # soma de q^n · M por arquivo W<k>.lean (o lake confere os arquivos em paralelo)
# Teoremas já existentes no alvo padrão que servem de célula base.
EXISTENTES = {(7, 4, 2): (19, "UB.of_exists K742.K_7_4_2_le_19", "CoveringLean.K742_Upper")}


def ler_witnesses() -> dict:
    """{(q,n,R): (M, caminho, [índices little-endian ordenados])}."""
    out = {}
    for p in sorted(WIT.glob("K*_M*.txt")):
        q, n, R, M = (int(x) for x in p.stem[1:].replace("_M", "_").split("_"))
        idx = []
        for linha in p.read_text().splitlines():
            if linha.strip():
                ds = [int(x) for x in (linha.split() if q > 10 else linha.strip())]
                idx.append(sum(d * q**k for k, d in enumerate(ds)))
        assert len(idx) == M and len(set(idx)) == M, p
        if (q, n, R) not in out or M < out[(q, n, R)][0]:
            out[(q, n, R)] = (M, p, sorted(idx))
    return out


def fechar(cells: list[dict], wits: dict, lins: dict | None = None):
    """Relaxação até ponto fixo. Devolve (valor por estado, nó atual por estado, nós).

    `lins` ({(q,n,R): (M, caminho, G, construcao)}, de lineares.ler_lineares) entra como base,
    como os witnesses."""
    nmax: dict[int, int] = {}
    for c in cells:
        nmax[c["q"]] = max(nmax.get(c["q"], 0), c["n"])
    nos: list[tuple] = []  # (estado, valor, regra, args)
    atual: dict[tuple, int] = {}
    V: dict[tuple, int] = {}

    def novo(s, v, regra, *args):
        nos.append((s, v, regra, args))
        atual[s], V[s] = len(nos) - 1, v

    estados = [(q, n, R) for q in sorted(nmax) for n in range(1, nmax[q] + 1) for R in range(n + 1)]
    for s in estados:
        q, n, R = s
        novo(s, q**n, "univ")
        if n <= R:
            novo(s, 1, "large")
        elif q * (n - R - 1) < n and q < V[s]:
            novo(s, q, "const")
    for s, (M, _p, _i) in wits.items():
        if s in V and M < V[s]:
            novo(s, M, "wit")
    for s, (M, _p, _G, construcao) in (lins or {}).items():
        if s in V and M < V[s]:
            novo(s, M, "lin", construcao)
    for s, (M, _d, _m) in EXISTENTES.items():
        if M < V[s]:
            novo(s, M, "existente")
    mudou = True
    while mudou:
        mudou = False
        for s in estados:
            q, n, R = s
            melhor = (V[s], None)

            def cand(v, *regra):
                nonlocal melhor
                if v < melhor[0]:
                    melhor = (v, regra)

            for t in range(1, n):
                if R - t >= 0:
                    cand(V[(q, n - t, R - t)], "free", atual[(q, n - t, R - t)], t)
                if R <= n - t:
                    cand(q**t * V[(q, n - t, R)], "dummy", atual[(q, n - t, R)], t)
            for t in range(1, nmax[q] - n + 1):
                cand(V[(q, n + t, R)], "punct", atual[(q, n + t, R)], t)
            for Rp in range(R):
                cand(V[(q, n, Rp)], "radius", atual[(q, n, Rp)])
            for qp in nmax:
                if qp > q and n <= nmax[qp]:
                    cand(V[(qp, n, R)], "proj", atual[(qp, n, R)])
            for n1 in range(1, n):
                n2 = n - n1
                for R1 in range(min(R, n1) + 1):
                    R2 = min(R - R1, n2)
                    cand(V[(q, n1, R1)] * V[(q, n2, R2)], "sum", atual[(q, n1, R1)], atual[(q, n2, R2)])
            if melhor[1] is not None:
                novo(s, melhor[0], *melhor[1])
                mudou = True
    return V, atual, nos


def deps(no) -> list[int]:
    """Nós de que um nó depende (os inteiros de `args` que são nós, não o `t` das regras)."""
    _s, _v, regra, args = no
    if regra == "sum":
        return list(args)
    return [args[0]] if regra in ("radius", "proj", "free", "dummy", "punct") else []


def _nome(s, v):
    return f"K{s[0]}_{s[1]}_{s[2]}_le_{v}"


def descrever(nos, k) -> str:
    s, v, regra, args = nos[k]
    cel = lambda j: f"K{nos[j][0][0]}({nos[j][0][1]},{nos[j][0][2]}) ≤ {nos[j][1]}"  # noqa: E731
    fixas = {"univ": "espaço inteiro", "large": "raio ≥ n: uma palavra",
             "const": "palavras constantes (pombal)", "wit": "witness explícito", "existente": "teorema existente"}
    if regra in fixas:
        return fixas[regra]
    if regra == "lin":
        return args[0]
    if regra == "sum":
        return f"soma direta de {cel(args[0])} e {cel(args[1])}"
    nome = {"free": "alongamento livre", "dummy": "coordenada muda", "punct": "punção",
            "radius": "monotonia do raio", "proj": "projeção de alfabeto"}[regra]
    t = f" (t = {args[1]})" if len(args) > 1 else ""
    return f"{nome}{t} de {cel(args[0])}"


def _ident(s) -> str:
    return f"K{s[0]}_{s[1]}_{s[2]}"


def prova(nos, k, wits, wmod) -> str:
    (q, n, R), v, regra, args = nos[k]
    w = "(by decide) (by decide) (by decide)"
    if regra == "univ":
        return f"UB.univ {q} {n} {R}"
    if regra == "large":
        return f"UB.large_radius (q := {q}) (n := {n}) (R := {R}) (by decide)"
    if regra == "const":
        return f"UB.constant_symbol (q := {q}) (n := {n}) (R := {R}) (by decide)"
    if regra == "wit":
        return wmod[(q, n, R)]
    if regra == "existente":
        return EXISTENTES[(q, n, R)][1]
    if regra == "lin":
        return f"Lin.l_{_ident((q, n, R))}"
    u = [f"u{j}" for j in deps(nos[k])]
    if regra == "free":
        return f"(UB.lengthen_free {args[1]} {u[0]}).weaken {w}"
    if regra == "dummy":
        return f"(UB.lengthen_dummy {args[1]} {u[0]}).weaken {w}"
    if regra == "punct":
        return f"UB.puncture (n := {n}) {args[1]} ({u[0]}.weaken (by decide) le_rfl le_rfl)"
    if regra == "radius":
        return f"{u[0]}.weaken rfl (by decide) le_rfl"
    if regra == "proj":
        return f"UB.project (a := {q}) (by decide) {u[0]}"
    if regra == "sum":
        return f"(UB.direct_sum {u[0]} {u[1]}).weaken {w}"
    raise ValueError(regra)


def gerar(cells: list[dict], escrever: bool = True, custo_max: int = CUSTO_MAX) -> dict:
    wits = {s: w for s, w in ler_witnesses().items() if s[0] ** s[1] * w[0] <= custo_max}
    lins = lineares.ler_lineares()
    V, atual, nos = fechar(cells, wits, lins)
    alvo = {(c["q"], c["n"], c["R"]): c["best"]["ub"] for c in cells}
    menor = [s for s, b in alvo.items() if V[s] < b]
    if menor:
        raise SystemExit(f"regras deram cota abaixo da melhor conhecida (confira!): {menor[:5]}")
    certos = sorted(s for s, b in alvo.items() if V[s] == b)
    # Fecho das dependências a partir das células certificadas.
    usados, pilha = set(), [atual[s] for s in certos]
    while pilha:
        k = pilha.pop()
        if k in usados:
            continue
        usados.add(k)
        pilha += deps(nos[k])
    wit_usados = sorted({nos[k][0] for k in usados if nos[k][2] == "wit"},
                        key=lambda s: -(s[0] ** s[1]) * wits[s][0])
    # Um arquivo por lote de custo parecido (q^n · M), para o lake conferir em paralelo.
    lotes: list[list] = []
    for s in wit_usados:
        custo = s[0] ** s[1] * wits[s][0]
        if lotes and lotes[-1][0] + custo <= CUSTO_POR_ARQUIVO:
            lotes[-1][0] += custo
            lotes[-1][1].append(s)
        else:
            lotes.append([custo, [s]])
    wmod, arquivos_w = {}, []
    for i, (_c, grupo) in enumerate(lotes):
        nome = f"W{i}"
        linhas = [f"-- GERADO por tools/certificar/gerar.py; não edite à mão. Witnesses de {nome}.",
                  "import CoveringLean.Regras", "", "namespace CoveringLedger.Data", "open CoveringUB", ""]
        for s in sorted(grupo):
            M, p, idx = wits[s]
            ident = f"K{s[0]}_{s[1]}_{s[2]}"
            wmod[s] = f"Data.w_{ident}"
            linhas.append(f"/-- {p.relative_to(RAIZ)}, {M} palavras (índice = Σ dígito_k · q^k). -/")
            linhas.append(f"def {ident} : List Nat := {idx}")
            linhas.append("")
            linhas.append("set_option maxRecDepth 100000 in")
            linhas.append(f"theorem w_{ident} : UB {s[0]} {s[1]} {s[2]} {M} :=")
            linhas.append(f"  UB.of_go (L := {ident}) (by decide +kernel) (by decide +kernel)")
            linhas.append("")
        linhas.append("end CoveringLedger.Data")
        arquivos_w.append((nome, "\n".join(linhas) + "\n"))
    lin_usados = sorted({nos[k][0] for k in usados if nos[k][2] == "lin"})
    for s in lin_usados:
        _M, _p, G, _c = lins[s]
        arquivos_w.append(lineares.lean(_ident(s), s[0], s[1], s[2], G))
    imports = ["import CoveringLean.Regras"] + [f"import {m}" for m in sorted({e[2] for e in EXISTENTES.values()})]
    imports += [f"import CoveringLean.Ledger.{nome}" for nome, _ in arquivos_w]
    corpo = imports + ["", "/-!", "# Cotas superiores do ledger, célula base + regra (GERADO)", "",
                       "Gerado por `tools/certificar/gerar.py` a partir de `ledger/cells.json`; não edite à mão.",
                       "Cada `K<q>_<n>_<R>_le_<M>` é a melhor cota superior conhecida da célula.", "-/", "",
                       "namespace CoveringLedger", "open CoveringUB", ""]
    for k in sorted(usados):
        s, v, _r, _a = nos[k]
        corpo.append(f"-- {descrever(nos, k)}")
        corpo.append(f"theorem u{k} : UB {s[0]} {s[1]} {s[2]} {v} :=\n  {prova(nos, k, wits, wmod)}")
    corpo.append("")
    formal = {}
    for s in certos:
        k = atual[s]
        nm = _nome(s, V[s])
        corpo.append(f"theorem {nm} : K {s[0]} {s[1]} {s[2]} ≤ {V[s]} := K_le u{k}")
        formal[f"{s[0]},{s[1]},{s[2]}"] = {
            "M": V[s], "declaration": f"CoveringLedger.{nm}", "construcao": descrever(nos, k),
            "witness": str(wits[s][1].relative_to(RAIZ)) if nos[k][2] == "wit" else None}
        if nos[k][2] == "lin":
            # O código linear também tem segundo verificador: as síndromes em Python
            # (lineares.cobre_por_sindromes), rodadas em tests/test_certificar.py.
            formal[f"{s[0]},{s[1]},{s[2]}"]["witness"] = str(lins[s][1].relative_to(RAIZ))
            formal[f"{s[0]},{s[1]},{s[2]}"]["verificador"] = lineares.VERIFICADOR
    # Uma conjunção de todas: um único `#print axioms` cobre o lote inteiro.
    conj = " ∧\n    ".join(f"K {s[0]} {s[1]} {s[2]} ≤ {V[s]}" for s in certos)
    corpo += ["", "set_option maxRecDepth 100000 in", f"theorem todas_as_cotas :\n    {conj} :=", "  ⟨" + ",\n   ".join(
        "CoveringLedger." + _nome(s, V[s]) for s in certos) + "⟩",
        "", "end CoveringLedger", "", "#print axioms CoveringLedger.todas_as_cotas", ""]
    cotas = "\n".join(corpo)
    if escrever:
        SAIDA_LEAN.mkdir(parents=True, exist_ok=True)
        for p in SAIDA_LEAN.glob("*.lean"):
            p.unlink()
        for nome, txt in arquivos_w:
            (SAIDA_LEAN / f"{nome}.lean").write_text(txt)
        (SAIDA_LEAN / "Cotas.lean").write_text(cotas)
        sha = hashlib.sha256(cotas.encode()).hexdigest()
        for e in formal.values():
            e["arquivo"] = "CoveringLean/Ledger/Cotas.lean"
            e["sha256_arquivo"] = sha
            if e["witness"]:
                e["sha256"] = hashlib.sha256((RAIZ / e["witness"]).read_bytes()).hexdigest()
        doc = {"descricao": "GERADO por tools/certificar/gerar.py: células cuja melhor cota superior tem "
                            "teorema em CoveringLean/Ledger/Cotas.lean (lake build CoveringLedger). Não edite à mão.",
               "cells": formal}
        SAIDA_JSON.write_text(json.dumps(doc, ensure_ascii=False, indent=1, sort_keys=True) + "\n")
    return {"certificadas": len(certos), "teoremas": len(usados), "witnesses": len(wit_usados),
            "lineares": len(lin_usados),
            "por_regra": _contar(nos, [atual[s] for s in certos])}


def _contar(nos, ks):
    out: dict[str, int] = {}
    for k in ks:
        out[nos[k][2]] = out.get(nos[k][2], 0) + 1
    return dict(sorted(out.items()))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--resumo", action="store_true", help="só conta, não escreve")
    ap.add_argument("--custo-max", type=int, default=CUSTO_MAX, help="teto de q^n · M por witness")
    a = ap.parse_args(argv)
    cells = json.loads((RAIZ / "ledger" / "cells.json").read_text())["cells"]
    r = gerar(cells, escrever=not a.resumo, custo_max=a.custo_max)
    print(json.dumps(r, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
