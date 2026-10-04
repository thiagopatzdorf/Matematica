#!/usr/bin/env python3
"""Roda um comando com teto de memória (soma do RSS da árvore de processos) e registra o pico.

    python3 vigia.py --teto-gb 10 -- lake build Alvo

Mata a árvore inteira (só a sessão criada para o comando) se o RSS somado passar do teto.
Imprime no stderr, ao fim: tempo de parede, pico de RSS e código de saída.
"""
import argparse
import os
import signal
import subprocess
import sys
import time


def filhos(sid):
    """Processos da sessão `sid` (o comando roda numa sessão nova; lake cria filhos em threads
    diferentes, então `/proc/<pid>/task/<pid>/children` não basta)."""
    out = []
    for d in os.listdir("/proc"):
        if not d.isdigit() or int(d) == sid:
            continue
        try:
            with open(f"/proc/{d}/stat") as f:
                campos = f.read().rsplit(")", 1)[1].split()
            if int(campos[3]) == sid:
                out.append(int(d))
        except (OSError, IndexError, ValueError):
            pass
    return out


def rss(pid):
    try:
        with open(f"/proc/{pid}/statm") as f:
            return int(f.read().split()[1]) * os.sysconf("SC_PAGE_SIZE")
    except OSError:
        return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--teto-gb", type=float, required=True)
    ap.add_argument("cmd", nargs=argparse.REMAINDER)
    a = ap.parse_args()
    cmd = a.cmd[1:] if a.cmd and a.cmd[0] == "--" else a.cmd
    t0 = time.time()
    p = subprocess.Popen(cmd, start_new_session=True)
    pico = 0
    morto = False
    while p.poll() is None:
        tot = rss(p.pid) + sum(rss(c) for c in filhos(p.pid))
        pico = max(pico, tot)
        if tot > a.teto_gb * 2**30:
            os.killpg(p.pid, signal.SIGKILL)
            morto = True
            break
        time.sleep(1)
    rc = p.wait()
    print(f"[vigia] parede {time.time() - t0:.0f} s, pico RSS {pico / 2**30:.2f} GB, rc {rc}"
          + (" (MORTO PELO TETO)" if morto else ""), file=sys.stderr)
    sys.exit(rc if not morto else 137)


if __name__ == "__main__":
    main()
