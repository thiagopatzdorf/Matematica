#!/usr/bin/env python3
"""Contabilidade ponta a ponta da campanha de compressão: a razão só vale se somar TODAS as fases.

    python3 tools/fatoracao/contabilidade.py tetos            # teto de ganho de cada fase do recorde RSA-896
    python3 tools/fatoracao/contabilidade.py razao base.json novo.json

Regras que isto impõe (cada uma nasceu de um jeito fácil de se enganar):

* **Razão de compressão** = compute do melhor baseline reproduzível / compute do método novo, somando as fases
  `polyselect`, `crivo`, `filtragem`, `algebra_linear`, `raiz` e o custo das tentativas que falharam. Fase omitida no
  método novo é erro, não zero: "ganho" que esconde a álgebra linear não é ponta a ponta.
* **Lei de Amdahl:** ganhar `k` numa fase que pesa `s` do total rende `1 / (1 - s + s/k)`. Um 100× em 1% do custo vale 1,0100× (1 / 0,9901).
* **Degrau da escada** (1×, 2×, 5×, 10×, 100×, 1000×) é decidido pelo **limite inferior** do intervalo de confiança
  de 95% da razão, nunca pela estimativa pontual.
"""
import json
import random
import sys
from pathlib import Path

FASES = ("polyselect", "crivo", "filtragem", "algebra_linear", "raiz")

# Participação de cada fase no relógio do RSA-896 (post de Weis, 2026-09-19; relógio, não compute: o número de nós por fase muda).
# filtragem 21,9 h; algebra_linear = Krylov 58,8 + lingen e checagem 40,2 + mksol 7,4; raiz = caracteres e raiz quadrada 5,3.
# O test sieve (2,2 h) fica fora: é custo de lançamento, não de uma fase do método.
RSA896_HORAS = {"polyselect": 14.9, "crivo": 90.9, "filtragem": 21.9, "algebra_linear": 106.4, "raiz": 5.3}

DEGRAUS = ((1000.0, "1000×: investigar mudança de regime"), (100.0, "100×: possível nova abordagem algorítmica"),
           (10.0, "10×: resultado forte"), (5.0, "5×: engenharia significativa"), (2.0, "2×: melhoria confirmada"),
           (1.0, "1×: baseline reproduzido"))


def participacoes(horas):
    total = sum(horas.values())
    return {k: v / total for k, v in horas.items()}


def razao_fim_a_fim(base, novo):
    """Soma das fases do baseline / soma das fases do método novo. As duas têm de ter exatamente as mesmas fases."""
    if set(base) != set(novo):
        raise ValueError(f"fases diferentes: só no baseline {sorted(set(base) - set(novo))}, só no novo {sorted(set(novo) - set(base))}")
    if any(v < 0 for v in list(base.values()) + list(novo.values())):
        raise ValueError("custo negativo")
    soma_base, soma_novo = sum(base.values()), sum(novo.values())
    if soma_base <= 0 or soma_novo <= 0:
        raise ValueError("custo total tem de ser positivo")
    return soma_base / soma_novo


def ganho_amdahl(shares, speedups):
    """Ganho ponta a ponta quando a fase i fica `speedups[i]` vezes mais rápida (as que faltam ficam em 1)."""
    if abs(sum(shares.values()) - 1.0) > 1e-9:
        raise ValueError(f"as participações somam {sum(shares.values())}, não 1")
    if any(k <= 0 for k in speedups.values()):
        raise ValueError("speedup tem de ser positivo")
    return 1.0 / sum(s / speedups.get(fase, 1.0) for fase, s in shares.items())


def teto_por_fase(shares):
    """Se a fase custasse zero, o ganho máximo ponta a ponta seria 1 / (1 - s)."""
    return {fase: 1.0 / (1.0 - s) for fase, s in shares.items()}


def degrau(razao_limite_inferior):
    for minimo, nome in DEGRAUS:
        if razao_limite_inferior >= minimo:
            return nome
    return "abaixo de 1×: pior que o baseline"


def ic_razao(totais_base, totais_novo, rodadas=10000, semente=0, nivel=0.95):
    """Bootstrap da razão das médias dos custos ponta a ponta (um total por réplica). Devolve (estimativa, inferior, superior)."""
    if len(totais_base) < 2 or len(totais_novo) < 2:
        raise ValueError("precisa de pelo menos 2 réplicas de cada lado para ter intervalo")
    rng = random.Random(semente)
    media = lambda xs: sum(xs) / len(xs)
    razoes = sorted(media(rng.choices(totais_base, k=len(totais_base))) / media(rng.choices(totais_novo, k=len(totais_novo)))
                    for _ in range(rodadas))
    cauda = (1 - nivel) / 2
    return media(totais_base) / media(totais_novo), razoes[int(cauda * rodadas)], razoes[int((1 - cauda) * rodadas) - 1]


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if argv[:1] == ["tetos"]:
        sh = participacoes(RSA896_HORAS)
        for fase, teto in teto_por_fase(sh).items():
            print(f"{fase:<15} {100 * sh[fase]:5.1f}% do relógio   teto se custasse 0: {teto:.2f}×")
        return 0
    if argv[:1] == ["razao"] and len(argv) == 3:
        base, novo = (json.loads(Path(p).read_text(encoding="utf-8")) for p in argv[1:])
        print(f"{razao_fim_a_fim(base, novo):.4f}")
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
