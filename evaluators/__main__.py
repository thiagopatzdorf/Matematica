"""CLI:  python3 -m evaluators <id> [alvo] [--json] [--opt chave=valor ...]

Saída: 0 se `ok`; 1 se reprovou; 2 se não deu para avaliar (sem compilador, alvo ausente, uso errado).
"""
from __future__ import annotations

import argparse
import sys

from . import base


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python3 -m evaluators", description=__doc__.splitlines()[0])
    ap.add_argument("avaliador", nargs="?", help="id do avaliador (sem ele, lista os disponíveis)")
    ap.add_argument("alvo", nargs="?", help="o que avaliar (cada avaliador tem um alvo padrão, se houver)")
    ap.add_argument("--json", action="store_true", help="imprime o Resultado inteiro em JSON")
    ap.add_argument("--opt", action="append", default=[], metavar="CHAVE=VALOR", help="opção do avaliador")
    a = ap.parse_args(argv)
    if not a.avaliador:
        for i in base.ids():
            print(f"{i}\t{base.obter(i).descricao}")
        return 0
    try:
        av = base.obter(a.avaliador)
    except KeyError as e:
        print(e.args[0], file=sys.stderr)
        return 2
    opcoes = {}
    for kv in a.opt:
        k, _, v = kv.partition("=")
        opcoes[k] = v
    if a.alvo is None and av.alvo_padrao is None:
        print(f"o avaliador {av.id} precisa de um alvo", file=sys.stderr)
        return 2
    r = av.executar(a.alvo, **opcoes)
    if a.json:
        print(r.to_json(indent=2))
    else:
        print(f"{'OK  ' if r.ok else 'FALHA'} {r.avaliador}: {r.veredito}")
        print(f"  sha256_arquivo={r.sha256_arquivo}  sha256_canonico={r.sha256_canonico}  tempo={r.tempo_s}s")
        print(f"  reproduzir: {r.comando_reproducao}")
    if r.ok:
        return 0
    return 2 if r.erro_de_ambiente else 1


if __name__ == "__main__":
    sys.exit(main())
