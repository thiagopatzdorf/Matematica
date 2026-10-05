#!/usr/bin/env python3
"""Propagador de cotas sobre as células K_q(n,R) do ledger, até ponto fixo.

Aplica só desigualdades que são teoremas:

* as regras de cota SUPERIOR provadas em CoveringLean/Regras.lean (soma direta,
  alongamento livre, coordenada muda, punção, monotonia do raio, projeção de
  alfabeto, raio grande, palavras constantes);
* as mesmas desigualdades lidas ao contrário, que dão cota INFERIOR: se
  K(A) <= f(K(B)) vale para os números verdadeiros, então lb(B) sai de lb(A).
  Não há regra nova aqui, só contrapositiva (ver docs/PROPAGACAO_COTAS.md);
* a cota da esfera (empacotamento de bolas), clássica, como base das células
  fora da tabela.

Domínio: para cada q do ledger, todo (n,R) com 1 <= n <= N_q e 0 <= R <= n,
onde N_q é o maior n da tabela para aquele q. As células fora da tabela entram
só como passo intermediário (R = 0, R = n, R acima do teto da tabela) e não são
reportadas.

Cada cota guarda a regra e as premissas que a produziram, para reconstruir a
cadeia de dedução. Nada aqui escreve no ledger.

Uso:
    python3 tools/propagar/propagar.py                     # cenário (a) e (b), relatório em texto
    python3 tools/propagar/propagar.py --json saida.json   # também em JSON
"""
from __future__ import annotations

import argparse
import json
import sys
from math import comb
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]

# Resultados novos ainda em PR (2026-10-05): (q, n, R) -> {"lb": v, "ub": v}.
# K7(4,2) = 19 já está no ledger; fica aqui para o cenário (b) ser explícito.
NOVOS = {
    (3, 6, 2): {"lb": 17, "ub": 17, "ref": "K3(6,2) = 17 (PR em aberto)"},
    (7, 6, 4): {"lb": 14, "ub": 14, "ref": "K7(6,4) = 14, código de 14 (PR em aberto)"},
    (7, 5, 3): {"lb": 16, "ref": "K7(5,3) >= 16 (PR em aberto)"},
    (7, 4, 2): {"lb": 19, "ub": 19, "ref": "K7(4,2) = 19 (publicado, v0.8)"},
}

# Regra -> onde está provada (Lean) ou de onde vem.
REGRAS = {
    "ledger": "valor do ledger (best.ub / certification.lb)",
    "novo": "resultado novo do cenário (b)",
    "esfera": "cota da esfera: K >= q^n / V_q(n,R) (clássica)",
    "trivial": "K_q(n,R) <= q^n (o espaço todo)",
    "raio_grande": "UB.large_radius: n <= R => K = 1",
    "constantes": "UB.constant_symbol: q(n-R-1) < n => K <= q",
    "raio": "UB.radius_mono: K(n,R+1) <= K(n,R)",
    "alongamento": "UB.lengthen_free: K(n+1,R+1) <= K(n,R)",
    "muda": "UB.lengthen_dummy: K(n+1,R) <= q K(n,R)",
    "puncao": "UB.puncture: K(n,R) <= K(n+1,R)",
    "projecao": "UB.project: K_a(n,R) <= K_q(n,R) para a <= q",
    "soma": "UB.direct_sum: K(n1+n2,R1+R2) <= K(n1,R1) K(n2,R2)",
}


def volume(q: int, n: int, R: int) -> int:
    return sum(comb(n, i) * (q - 1) ** i for i in range(min(R, n) + 1))


def cota_esfera(q: int, n: int, R: int) -> int:
    return -(-(q**n) // volume(q, n, R))


def cdiv(a: int, b: int) -> int:
    return -(-a // b)


def nome(c) -> str:
    q, n, R = c
    return f"K{q}({n},{R})"


class Estado:
    """lb/ub por célula, com a justificativa de cada valor."""

    def __init__(self):
        self.lb: dict = {}
        self.ub: dict = {}
        self.por: dict = {}  # (lado, célula) -> (regra, [(lado, célula), ...])
        self.tabela: set = set()
        self.N: dict = {}

    def melhora(self, lado, c, v, regra, prem) -> bool:
        d = self.lb if lado == "lb" else self.ub
        if c not in d:
            return False
        if (lado == "lb" and v > d[c]) or (lado == "ub" and v < d[c]):
            d[c] = v
            self.por[(lado, c)] = (regra, prem)
            return True
        return False

    def copia(self) -> "Estado":
        e = Estado()
        e.lb, e.ub, e.por = dict(self.lb), dict(self.ub), dict(self.por)
        e.tabela, e.N = set(self.tabela), dict(self.N)
        return e


def carregar(cells: list) -> Estado:
    e = Estado()
    for x in cells:
        q, n = x["q"], x["n"]
        e.N[q] = max(e.N.get(q, 0), n)
    for q, N in e.N.items():
        for n in range(1, N + 1):
            for R in range(0, n + 1):
                c = (q, n, R)
                if R >= n:
                    e.lb[c], e.ub[c] = 1, 1
                    e.por[("lb", c)] = e.por[("ub", c)] = ("raio_grande", [])
                    continue
                e.lb[c] = cota_esfera(q, n, R)
                e.por[("lb", c)] = ("esfera", [])
                e.ub[c] = q**n
                e.por[("ub", c)] = ("trivial", [])
                if q * (n - R - 1) < n and q < e.ub[c]:
                    e.ub[c] = q
                    e.por[("ub", c)] = ("constantes", [])
    for x in cells:
        c = (x["q"], x["n"], x["R"])
        e.tabela.add(c)
        lb, ub = x["certification"]["lb"]["value"], x["best"]["ub"]
        # O valor do ledger manda, mesmo que seja pior que a base: assim uma
        # base mais forte que o ledger aparece como "melhoria", não some.
        e.lb[c], e.ub[c] = lb, ub
        e.por[("lb", c)] = e.por[("ub", c)] = ("ledger", [])
    return e


def aplicar_novos(e: Estado, novos: dict = NOVOS) -> Estado:
    e = e.copia()
    for c, v in novos.items():
        for lado in ("lb", "ub"):
            if lado in v:
                e.melhora(lado, c, v[lado], "novo", [])
    return e


def _passo(e: Estado) -> bool:
    mudou = False
    lb, ub = e.lb, e.ub
    qs = sorted(e.N)
    for c in list(lb):
        q, n, R = c
        # Monotonia do raio: K(n,R+1) <= K(n,R).
        d = (q, n, R + 1)
        if d in ub:
            mudou |= e.melhora("ub", d, ub[c], "raio", [("ub", c)])
            mudou |= e.melhora("lb", c, lb[d], "raio", [("lb", d)])
        # Alongamento livre: K(n+1,R+1) <= K(n,R).
        d = (q, n + 1, R + 1)
        if d in ub:
            mudou |= e.melhora("ub", d, ub[c], "alongamento", [("ub", c)])
            mudou |= e.melhora("lb", c, lb[d], "alongamento", [("lb", d)])
        # Coordenada muda: K(n+1,R) <= q K(n,R); e punção: K(n,R) <= K(n+1,R).
        d = (q, n + 1, R)
        if d in ub:
            mudou |= e.melhora("ub", d, q * ub[c], "muda", [("ub", c)])
            mudou |= e.melhora("lb", c, cdiv(lb[d], q), "muda", [("lb", d)])
            mudou |= e.melhora("ub", c, ub[d], "puncao", [("ub", d)])
            mudou |= e.melhora("lb", d, lb[c], "puncao", [("lb", c)])
        # Projeção de alfabeto: K_a(n,R) <= K_b(n,R), a < b.
        for b in qs:
            if b <= q:
                continue
            d = (b, n, R)
            if d in ub:
                mudou |= e.melhora("ub", c, ub[d], "projecao", [("ub", d)])
                mudou |= e.melhora("lb", d, lb[c], "projecao", [("lb", c)])
    # Soma direta: K(n1+n2, R1+R2) <= K(n1,R1) K(n2,R2), e contrapositiva
    # lb(n1,R1) >= ceil(lb(n1+n2,R1+R2) / ub(n2,R2)).
    porq: dict = {}
    for c in lb:
        porq.setdefault(c[0], []).append(c)
    for q, cs in porq.items():
        N = e.N[q]
        for a in cs:
            _, n1, R1 = a
            for b in cs:
                _, n2, R2 = b
                if n1 + n2 > N or (n2, R2) < (n1, R1):
                    continue
                s = (q, n1 + n2, R1 + R2)
                if s not in ub:
                    continue
                mudou |= e.melhora("ub", s, ub[a] * ub[b], "soma", [("ub", a), ("ub", b)])
                mudou |= e.melhora("lb", a, cdiv(lb[s], ub[b]), "soma", [("lb", s), ("ub", b)])
                mudou |= e.melhora("lb", b, cdiv(lb[s], ub[a]), "soma", [("lb", s), ("ub", a)])
    return mudou


def propagar(e: Estado, max_passos: int = 200) -> Estado:
    e = e.copia()
    for _ in range(max_passos):
        if not _passo(e):
            return e
    raise RuntimeError("sem ponto fixo em max_passos")


def cadeia(e: Estado, lado: str, c) -> list:
    """Passos (em ordem de dedução) que levam ao valor de `lado` em `c`."""
    vistos, passos = set(), []

    def visita(no):
        if no in vistos:
            return
        vistos.add(no)
        regra, prem = e.por[no]
        for p in prem:
            visita(p)
        ld, cel = no
        val = e.lb[cel] if ld == "lb" else e.ub[cel]
        sinal = ">=" if ld == "lb" else "<="
        txt = f"{nome(cel)} {sinal} {val}  [{regra}"
        if prem:
            txt += ": " + ", ".join(f"{p[0]} {nome(p[1])}" for p in prem)
        passos.append(txt + "]")

    visita((lado, c))
    return passos


def inconsistencias(e: Estado) -> list:
    return sorted(c for c in e.lb if e.lb[c] > e.ub[c])


def diferencas(antes: Estado, depois: Estado, so_tabela: bool = True) -> list:
    out = []
    for c in sorted(depois.lb):
        if so_tabela and c not in depois.tabela:
            continue
        dl = depois.lb[c] > antes.lb[c]
        du = depois.ub[c] < antes.ub[c]
        if dl or du:
            out.append({"celula": nome(c), "q": c[0], "n": c[1], "R": c[2],
                        "lb": [antes.lb[c], depois.lb[c]], "ub": [antes.ub[c], depois.ub[c]],
                        "exata_agora": depois.lb[c] == depois.ub[c] and antes.lb[c] != antes.ub[c],
                        "cadeia_lb": cadeia(depois, "lb", c) if dl else [],
                        "cadeia_ub": cadeia(depois, "ub", c) if du else []})
    return out


def implicacoes(e: Estado, c) -> list:
    """Consequências de UM passo a partir de `c`, com a folga contra o valor atual.

    Serve para explicar por que um resultado novo não propaga: cada linha diz o
    que a regra entrega no vizinho e o que o vizinho já tem.
    """
    q, n, R = c
    out = []

    def add(regra, lado, d, v):
        if d in e.lb:
            atual = e.lb[d] if lado == "lb" else e.ub[d]
            melhor = v > atual if lado == "lb" else v < atual
            out.append({"regra": regra, "vizinho": nome(d), "lado": lado, "implica": v,
                        "atual": atual, "melhora": melhor})

    add("raio", "ub", (q, n, R + 1), e.ub[c])
    add("raio", "lb", (q, n, R - 1), e.lb[c])
    add("alongamento", "ub", (q, n + 1, R + 1), e.ub[c])
    add("alongamento", "lb", (q, n - 1, R - 1), e.lb[c])
    add("muda", "ub", (q, n + 1, R), q * e.ub[c])
    add("muda", "lb", (q, n - 1, R), cdiv(e.lb[c], q))
    add("puncao", "ub", (q, n - 1, R), e.ub[c])
    add("puncao", "lb", (q, n + 1, R), e.lb[c])
    # Só o alfabeto vizinho: q-2, q+2... ficam dominados por transitividade.
    add("projecao", "ub", (q - 1, n, R), e.ub[c])
    add("projecao", "lb", (q + 1, n, R), e.lb[c])
    return out


def ler_novos(textos: list) -> dict:
    """'7,6,4:lb=14,ub=14' -> {(7,6,4): {'lb': 14, 'ub': 14}}."""
    out = {}
    for t in textos:
        cel, _, vals = t.partition(":")
        c = tuple(int(x) for x in cel.split(","))
        d = {"ref": t}
        for kv in vals.split(","):
            k, _, v = kv.partition("=")
            if k.strip() not in ("lb", "ub"):
                raise ValueError(f"lado inválido em {t!r}")
            d[k.strip()] = int(v)
        out[c] = d
    return out


def relatorio(cells: list, novos: dict = NOVOS) -> dict:
    base = carregar(cells)
    a = propagar(base)
    b = propagar(aplicar_novos(a, novos))
    return {
        "regras": REGRAS,
        "novos": {nome(c): v for c, v in novos.items()},
        "a_inconsistencias": [{"celula": nome(c), "lb": a.lb[c], "ub": a.ub[c],
                               "cadeia_lb": cadeia(a, "lb", c), "cadeia_ub": cadeia(a, "ub", c)}
                              for c in inconsistencias(a)],
        "a_melhorias_sobre_ledger": diferencas(base, a),
        "b_inconsistencias": [{"celula": nome(c), "lb": b.lb[c], "ub": b.ub[c],
                               "cadeia_lb": cadeia(b, "lb", c), "cadeia_ub": cadeia(b, "ub", c)}
                              for c in inconsistencias(b)],
        # Fora as próprias células novas, quando ficam só com o valor dado.
        "b_melhorias_por_consequencia": [
            d for d in diferencas(a, b)
            if (d["q"], d["n"], d["R"]) not in novos
            or d["lb"][1] > novos[(d["q"], d["n"], d["R"])].get("lb", 0)
            or d["ub"][1] < novos[(d["q"], d["n"], d["R"])].get("ub", float("inf"))],
        "b_exatas": [nome(c) for c in sorted(b.tabela) if b.lb[c] == b.ub[c] and a.lb[c] != a.ub[c]],
        "b_implicacoes": {nome(c): implicacoes(b, c) for c in novos if c in b.lb},
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--cells", default=str(RAIZ / "ledger" / "cells.json"))
    ap.add_argument("--json", help="grava o relatório completo em JSON")
    ap.add_argument("--novo", action="append", default=[],
                    help="resultado do cenário (b), ex. '7,6,4:lb=14,ub=14'; repetível; "
                         "sem ele, usa NOVOS")
    args = ap.parse_args(argv)
    cells = json.loads(Path(args.cells).read_text())["cells"]
    rel = relatorio(cells, ler_novos(args.novo) if args.novo else NOVOS)
    for chave in ("a_inconsistencias", "a_melhorias_sobre_ledger", "b_inconsistencias",
                  "b_melhorias_por_consequencia"):
        print(f"\n== {chave}: {len(rel[chave])}")
        for d in rel[chave]:
            extra = " EXATA" if d.get("exata_agora") else ""
            print(f"  {d['celula']}: lb {d['lb']} ub {d['ub']}{extra}")
            for p in d.get("cadeia_lb", []) + d.get("cadeia_ub", []):
                print(f"      {p}")
    print(f"\n== b_exatas: {rel['b_exatas']}")
    print("\n== b_implicacoes (um passo; folga = o vizinho já tem)")
    for cel, imps in rel["b_implicacoes"].items():
        for i in imps:
            marca = "MELHORA" if i["melhora"] else "folga"
            print(f"  {cel} -[{i['regra']}]-> {i['vizinho']} {i['lado']} {i['implica']}"
                  f" (atual {i['atual']}, {marca})")
    if args.json:
        Path(args.json).write_text(json.dumps(rel, ensure_ascii=False, indent=1) + "\n")
    return 1 if rel["a_inconsistencias"] or rel["b_inconsistencias"] else 0


if __name__ == "__main__":
    sys.exit(main())
