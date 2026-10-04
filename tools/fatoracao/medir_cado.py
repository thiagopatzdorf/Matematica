#!/usr/bin/env python3
"""Linha de base do CADO-NFS: roda semiprimos balanceados e grava UMA linha por TENTATIVA.

    python3 tools/fatoracao/medir_cado.py gerar 60,65,70 3 conjunto.json
    python3 tools/fatoracao/medir_cado.py medir conjunto.json resultados.jsonl --cado <pasta do cado-nfs> --trabalho <pasta>
    python3 tools/fatoracao/medir_cado.py estatistica resultados.jsonl

Por que existe: o bloco Wiedemann do CADO às vezes falha com `nlucky=0` ("Could not find the required set of
solutions"). O README do bwc diz que o programa `prep` não é determinístico, e que fixar `seed` serve para repetir.
Um lote que trata essa falha como sucesso, ou que descarta a rodada, enviesa a curva de custo, que é justamente o que o
programa "bater o GNFS" mede. Aqui, a falha:

* é classificada pelo texto do log, e `exit 0` com fatores errados também é falha;
* repete com a semente seguinte (1, 2, 3), sempre a mesma ordem, e cada tentativa é uma linha;
* guarda a pasta de trabalho da tentativa que falhou, e o `sha256` do log, do polinômio e da saída;
* entra na estatística: taxa de falha na primeira tentativa e custo até o sucesso incluindo as tentativas perdidas.
"""
import argparse
import hashlib
import json
import random
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

SEMENTES_BWC = (1, 2, 3)
MARCA_NLUCKY0 = "Could not find the required set of solutions"
PRIMOS_PEQUENOS = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)


def eh_primo(n):
    """Miller-Rabin com as 12 primeiras bases: determinístico até 3,3e24, e erro desprezível acima disso."""
    if n < 2:
        return False
    for p in PRIMOS_PEQUENOS:
        if n % p == 0:
            return n == p
    d, s = n - 1, 0
    while d % 2 == 0:
        d //= 2
        s += 1
    for a in PRIMOS_PEQUENOS:
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(s - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False
    return True


def proximo_primo(n):
    n += 1 if n % 2 == 0 else 2
    while not eh_primo(n):
        n += 2
    return n


def semiprimo(digitos, rng):
    """(n, p, q) com `n` de exatamente `digitos` dígitos e fatores de tamanho igual (balanceado)."""
    lo, hi = 10 ** ((digitos - 1) // 2), 10 ** ((digitos + 1) // 2)
    while True:
        p = proximo_primo(rng.randrange(lo * 3, hi))
        q = proximo_primo(rng.randrange(lo * 3, hi))
        if p != q and len(str(p * q)) == digitos:
            return p * q, min(p, q), max(p, q)


def gerar(tamanhos, por_tamanho, prefixo="gnfs-base"):
    """Mesma entrada, mesmos números: a semente é o texto `<prefixo>-<dígitos>`.

    Prefixos diferentes dão conjuntos diferentes (`dev` para desenvolver, `teste` para avaliar, selado até o commit do método).
    """
    saida = []
    for d in tamanhos:
        rng = random.Random(f"{prefixo}-{d}")
        for i in range(por_tamanho):
            n, p, q = semiprimo(d, rng)
            saida.append({"digitos": d, "i": i, "n": str(n), "p": str(p), "q": str(q)})
    return saida


def conferir_fatores(item, saida):
    """A saída do CADO termina com os dois fatores; só vale se forem exatamente os gerados e multiplicarem em N."""
    tokens = saida.split()
    if len(tokens) < 2 or not all(t.isdigit() for t in tokens[-2:]):
        return False
    a, b = int(tokens[-2]), int(tokens[-1])
    return sorted((a, b)) == sorted((int(item["p"]), int(item["q"]))) and a * b == int(item["n"])


def classificar(returncode, stderr, fatores_ok):
    if returncode == 0:
        return "ok" if fatores_ok else "fatores_errados"
    return "bwc_nlucky0" if MARCA_NLUCKY0 in stderr else "outra_falha"


def semente(tentativa):
    return SEMENTES_BWC[tentativa - 1]


def deve_repetir(classe, tentativa):
    """Só `nlucky=0` repete: é a falha que o CADO documenta como estocástica. As outras ficam registradas e param."""
    return classe == "bwc_nlucky0" and tentativa < len(SEMENTES_BWC)


def _numero(rx, texto, tipo=float):
    achados = re.findall(rx, texto)
    return tipo(achados[-1]) if achados else None


def metricas(err):
    return {
        "rels_total": _numero(r"Total number of relations: (\d+)", err, int),
        "rels_unicas": _numero(r"(\d+) unique relations remain in total", err, int),
        "rels_pos_purge": _numero(r"After purge, (\d+) relations", err, int),
        "matriz_linhas": _numero(r"Merged matrix has (\d+) rows", err, int),
        "matriz_peso": _numero(r"Merged matrix has \d+ rows and total weight (\d+)", err, int),
        "polyselect_s": round((_numero(r"Polynomial Selection \(size optimized\): Total time: ([\d.]+)", err) or 0)
                              + (_numero(r"Polynomial Selection \(root optimized\): Total time: ([\d.]+)", err) or 0), 2),
        "crivo_s_soma_wu": _numero(r"Lattice Sieving: Total time: ([\d.]+)s", err),
        "bwc_cpu_s": _numero(r"Total cpu/real time for bwc: ([\d.]+)/", err),
        "sqrt_cpu_s": _numero(r"Total cpu/real time for sqrt: ([\d.]+)/", err),
        "merge_cpu_s": _numero(r"Total cpu/real time for merge: ([\d.]+)/", err),
        "qmax_crivo": max([int(b) for _, b in re.findall(r"\.(\d+)-(\d+)\.gz", err)] or [0]),
    }


def sha256_arquivo(caminho):
    caminho = Path(caminho)
    return hashlib.sha256(caminho.read_bytes()).hexdigest() if caminho.is_file() else None


def sha256_texto(texto):
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()


def rodar_tentativa(cado_py, item, tentativa, trabalho, threads=4):
    """Uma execução completa do CADO com a semente da tentativa. Devolve a linha do registro."""
    d, i = item["digitos"], item["i"]
    pasta = Path(trabalho) / f"c{d}_{i}_t{tentativa}"
    shutil.rmtree(pasta, ignore_errors=True)
    t0 = time.time()
    r = subprocess.run([sys.executable, str(cado_py), item["n"], f"tasks.linalg.bwc.seed={semente(tentativa)}",
                        "--workdir", str(pasta), "-t", str(threads)], capture_output=True, text=True)
    real = round(time.time() - t0, 1)
    ok_fatores = r.returncode == 0 and conferir_fatores(item, r.stdout)
    classe = classificar(r.returncode, r.stderr, ok_fatores)
    logs = Path(trabalho) / "logs"
    logs.mkdir(parents=True, exist_ok=True)
    log = logs / f"c{d}_{i}_t{tentativa}.log"
    log.write_text(r.stderr, encoding="utf-8")
    linha = {"digitos": d, "i": i, "tentativa": tentativa, "semente_bwc": semente(tentativa), "threads": threads,
             "exit": r.returncode, "classe": classe, "real_s": real, "log": log.name,
             "sha256_log": sha256_arquivo(log), "sha256_poly": sha256_arquivo(pasta / f"c{d}.poly"),
             "sha256_saida": sha256_texto(r.stdout), "pasta": None if classe == "ok" else pasta.name,
             **metricas(r.stderr)}
    if classe == "ok":
        shutil.rmtree(pasta, ignore_errors=True)
    return linha


def pendente(linhas_do_item):
    """Falta rodar? Sim se não há linha, ou se a última falhou de um jeito que repete e ainda há semente."""
    if not linhas_do_item:
        return True
    ultima = max(linhas_do_item, key=lambda x: x["tentativa"])
    return deve_repetir(ultima["classe"], ultima["tentativa"])


def ler_registro(caminho):
    caminho = Path(caminho)
    return [json.loads(x) for x in caminho.read_text(encoding="utf-8").splitlines()] if caminho.exists() else []


def medir(conjunto, registro, cado_py, trabalho, threads=4, rodar=rodar_tentativa):
    for item in conjunto:
        while True:
            feitas = [x for x in ler_registro(registro) if (x["digitos"], x["i"]) == (item["digitos"], item["i"])]
            if not pendente(feitas):
                break
            tentativa = max([x["tentativa"] for x in feitas] or [0]) + 1
            linha = rodar(cado_py, item, tentativa, trabalho, threads)
            with open(registro, "a", encoding="utf-8") as f:
                f.write(json.dumps(linha) + "\n")
            print(linha["digitos"], linha["i"], f"t{tentativa}", linha["real_s"], linha["classe"], flush=True)


def estatistica(linhas):
    """Por tamanho: quantos números, quantas falhas na 1ª tentativa, quantos nunca fecharam, custo até o sucesso."""
    por_numero = {}
    for x in linhas:
        por_numero.setdefault((x["digitos"], x["i"]), []).append(x)
    por_tamanho = {}
    for (d, _), tent in por_numero.items():
        tent = sorted(tent, key=lambda x: x["tentativa"])
        s = por_tamanho.setdefault(d, {"numeros": 0, "falhas_1a_tentativa": 0, "sem_sucesso": 0, "custo_s": []})
        s["numeros"] += 1
        s["falhas_1a_tentativa"] += tent[0]["classe"] != "ok"
        s["sem_sucesso"] += not any(x["classe"] == "ok" for x in tent)
        s["custo_s"].append(sum(x["real_s"] for x in tent))
    for s in por_tamanho.values():
        s["taxa_falha_1a_tentativa"] = round(s["falhas_1a_tentativa"] / s["numeros"], 3)
        s["custo_medio_s"] = round(sum(s["custo_s"]) / len(s["custo_s"]), 1)
    return dict(sorted(por_tamanho.items()))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("gerar")
    g.add_argument("tamanhos", help="dígitos separados por vírgula, por exemplo 60,65,70")
    g.add_argument("por_tamanho", type=int)
    g.add_argument("saida")
    g.add_argument("--prefixo", default="gnfs-base", help="prefixo da semente: dev, teste ou o padrão")
    m = sub.add_parser("medir")
    m.add_argument("conjunto")
    m.add_argument("registro")
    m.add_argument("--cado", required=True, help="pasta do cado-nfs (onde está cado-nfs.py)")
    m.add_argument("--trabalho", required=True)
    m.add_argument("--threads", type=int, default=4)
    e = sub.add_parser("estatistica")
    e.add_argument("registro")
    a = ap.parse_args(argv)
    if a.cmd == "gerar":
        dados = gerar([int(x) for x in a.tamanhos.split(",")], a.por_tamanho, a.prefixo)
        Path(a.saida).write_text(json.dumps(dados, indent=1), encoding="utf-8")
        print(len(dados), "semiprimos ->", a.saida)
    elif a.cmd == "medir":
        medir(json.loads(Path(a.conjunto).read_text(encoding="utf-8")), a.registro,
              Path(a.cado) / "cado-nfs.py", a.trabalho, a.threads)
    else:
        print(json.dumps(estatistica(ler_registro(a.registro)), indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
