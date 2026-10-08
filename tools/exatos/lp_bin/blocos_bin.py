#!/usr/bin/env python3
"""Roda `certificar_bin.py` em blocos com checkpoint, para listas que não cabem numa rodada só.

Por que existe: `certificar_bin.py` grava a saída só no fim. Em `K_2(14,5)` (341 547 instâncias,
~12 h de raiz) numa VM spot, uma preempção no meio perderia tudo. Aqui a lista é cortada em
blocos de tamanho fixo; cada bloco vira `bloco_<k>.jsonl.gz`, escrito num temporário e renomeado
só quando o processo termina (rename é atômico). Ao retomar, bloco que já existe é pulado, então
uma preempção custa no máximo o bloco em andamento.

`juntar` concatena os blocos, em ordem, num gzip de vários membros (o `gzip` do Python lê os
membros em sequência): o arquivo resultante é idêntico, para `verificar_bin.py`, a uma rodada
única. `juntar` recusa se faltar bloco. A prova continua sendo só `verificar_bin.py` sobre o
arquivo juntado e a lista com sha256; este script não decide nada.

  python3 tools/exatos/lp_bin/blocos_bin.py rodar --n 14 --R 5 --M 10 --instancias i.json \\
      --dir raiz --bloco 5000 -j 8 --sem-ramos
  python3 tools/exatos/lp_bin/blocos_bin.py rodar ... --dir ramos --refazer-dir raiz --orcamento 2000
  python3 tools/exatos/lp_bin/blocos_bin.py resumo --dir raiz --vivas vivas.json
  python3 tools/exatos/lp_bin/blocos_bin.py remendar ... --vivas vivas.json --dir rem \\
      --parte 0 --partes 3 -j 8 --orcamento 2000          # uma máquina por parte
  python3 tools/exatos/lp_bin/blocos_bin.py juntar --dir raiz --remendos rem \\
      --total 341547 --bloco 5000 --saida c.jsonl.gz
"""
import argparse
import gzip
import json
import os
import subprocess
import sys
import time
from pathlib import Path

AQUI = Path(__file__).resolve().parent


def nome_bloco(k):
    return f"bloco_{k:05d}.jsonl.gz"


def blocos(total, tam):
    """[(k, início, fim)] com fim exclusivo; o último bloco pode ser menor."""
    return [(k, i, min(i + tam, total)) for k, i in enumerate(range(0, total, tam))]


def rodar(a):
    total = len(json.load(open(a.instancias)))
    d = Path(a.dir)
    d.mkdir(parents=True, exist_ok=True)
    meus = [b for b in blocos(total, a.bloco) if a.de <= b[0] < (a.ate if a.ate >= 0 else 1 << 30)]
    for k, ini, fim in meus:
        alvo = d / nome_bloco(k)
        if alvo.exists():
            continue
        tmp = d / (nome_bloco(k) + ".tmp")
        cmd = [sys.executable, str(AQUI / "certificar_bin.py"), "--n", str(a.n), "--R", str(a.R),
               "--M", str(a.M), "--instancias", a.instancias, "--saida", str(tmp),
               "--so", f"{ini}-{fim - 1}", "-j", str(a.j), "--orcamento", str(a.orcamento)]
        if a.sem_ramos:
            cmd.append("--sem-ramos")
        if a.refazer_dir:
            cmd += ["--refazer", str(Path(a.refazer_dir) / nome_bloco(k))]
        t0 = time.time()
        with open(d / f"bloco_{k:05d}.log", "w") as log:
            rc = subprocess.call(cmd, stdout=log, stderr=subprocess.STDOUT)
        # certificar_bin sai com 1 quando sobra instância sem certificado: o bloco está completo
        if rc not in (0, 1) or not tmp.exists():
            sys.exit(f"bloco {k} falhou (código {rc}); nada renomeado")
        os.replace(tmp, alvo)
        print(f"bloco {k} [{ini}, {fim}) rc={rc} {time.time() - t0:.0f} s", flush=True)


def remendar(a):
    """Ramifica só as vivas, em grupos pequenos espalhados entre máquinas (`--parte`/`--partes`).

    As vivas da raiz se concentram nos primeiros blocos (s* <= 4), então dividir por bloco deixaria
    uma máquina com quase todo o trabalho. Cada grupo vira `remendo_<k>.jsonl.gz`, também atômico."""
    vivas = json.load(open(a.vivas))
    d = Path(a.dir)
    d.mkdir(parents=True, exist_ok=True)
    grupos = [vivas[i:i + a.grupo] for i in range(0, len(vivas), a.grupo)]
    for k, g in enumerate(grupos):
        if k % a.partes != a.parte:
            continue
        alvo = d / f"remendo_{k:05d}.jsonl.gz"
        if alvo.exists():
            continue
        tmp = d / f"remendo_{k:05d}.jsonl.gz.tmp"
        cmd = [sys.executable, str(AQUI / "certificar_bin.py"), "--n", str(a.n), "--R", str(a.R),
               "--M", str(a.M), "--instancias", a.instancias, "--saida", str(tmp),
               "--so", ",".join(str(i) for i in g), "-j", str(a.j), "--orcamento", str(a.orcamento)]
        t0 = time.time()
        with open(d / f"remendo_{k:05d}.log", "w") as log:
            rc = subprocess.call(cmd, stdout=log, stderr=subprocess.STDOUT)
        if rc not in (0, 1) or not tmp.exists():
            sys.exit(f"remendo {k} falhou (código {rc}); nada renomeado")
        os.replace(tmp, alvo)
        print(f"remendo {k} ({len(g)} vivas) rc={rc} {time.time() - t0:.0f} s", flush=True)


def ler_bloco(caminho):
    with gzip.open(caminho, "rt") as f:
        return [json.loads(ln) for ln in f]


def resumo(a):
    modos, vivas, n = {}, [], 0
    arquivos = [Path(a.arquivo)] if a.arquivo else sorted(Path(a.dir).glob("bloco_*.jsonl.gz"))
    for p in arquivos:
        for r in ler_bloco(p):
            n += 1
            modos[r["modo"]] = modos.get(r["modo"], 0) + 1
            if not r["folhas"]:
                vivas.append(r["inst"])
    print(json.dumps({"instancias": n, "modos": {str(k): v for k, v in modos.items()},
                      "vivas": len(vivas), "vivas_primeiras": vivas[:50]}, ensure_ascii=False))
    if a.vivas:
        Path(a.vivas).write_text(json.dumps(vivas))


def juntar(a):
    d = Path(a.dir)
    faltam = [k for k, _, _ in blocos(a.total, a.bloco) if not (d / nome_bloco(k)).exists()]
    if faltam:
        sys.exit(f"faltam {len(faltam)} blocos: {faltam[:20]}")
    # remendo só substitui o registro da raiz quando traz certificado; um posterior vence um anterior
    novos = {}
    for rd in a.remendos or []:
        for p in sorted(Path(rd).glob("remendo_*.jsonl.gz")):
            for r in ler_bloco(p):
                if r["folhas"]:
                    novos[r["inst"]] = r
    with open(a.saida, "wb") as out:
        for k, _, _ in blocos(a.total, a.bloco):
            if not novos:
                out.write((d / nome_bloco(k)).read_bytes())
                continue
            with gzip.open(out, "wt") as g:
                for r in ler_bloco(d / nome_bloco(k)):
                    g.write(json.dumps(novos.get(r["inst"], r), separators=(",", ":")) + "\n")
    print(f"{a.saida}: {a.total} instâncias em {len(blocos(a.total, a.bloco))} blocos, "
          f"{len(novos)} registros vindos de remendos")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("rodar")
    for k in ("n", "R", "M"):
        r.add_argument("--" + k, type=int, required=True)
    r.add_argument("--instancias", required=True)
    r.add_argument("--dir", required=True)
    r.add_argument("--bloco", type=int, default=5000)
    r.add_argument("--de", type=int, default=0, help="primeiro bloco desta máquina")
    r.add_argument("--ate", type=int, default=-1, help="bloco final exclusivo (-1 = até o fim)")
    r.add_argument("-j", type=int, default=1)
    r.add_argument("--sem-ramos", action="store_true")
    r.add_argument("--refazer-dir", help="blocos anteriores (mesmo --bloco): refaz só as sem certificado")
    r.add_argument("--orcamento", type=int, default=4000)
    m = sub.add_parser("remendar")
    for k in ("n", "R", "M"):
        m.add_argument("--" + k, type=int, required=True)
    m.add_argument("--instancias", required=True)
    m.add_argument("--vivas", required=True, help="JSON com os índices sem certificado")
    m.add_argument("--dir", required=True)
    m.add_argument("--grupo", type=int, default=40)
    m.add_argument("--parte", type=int, default=0)
    m.add_argument("--partes", type=int, default=1)
    m.add_argument("-j", type=int, default=1)
    m.add_argument("--orcamento", type=int, default=4000)
    s = sub.add_parser("resumo")
    s.add_argument("--dir")
    s.add_argument("--arquivo", help="um gzip juntado, em vez dos blocos de --dir")
    s.add_argument("--vivas", help="grava a lista de índices sem certificado (JSON)")
    j = sub.add_parser("juntar")
    j.add_argument("--dir", required=True)
    j.add_argument("--total", type=int, required=True)
    j.add_argument("--bloco", type=int, required=True)
    j.add_argument("--saida", required=True)
    j.add_argument("--remendos", nargs="*", help="pastas de `remendar`, aplicadas em ordem")
    a = ap.parse_args(argv)
    {"rodar": rodar, "remendar": remendar, "resumo": resumo, "juntar": juntar}[a.cmd](a)


if __name__ == "__main__":
    main()
