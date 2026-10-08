#!/usr/bin/env python3
"""Captura compacta e reproduzível das relações de uma execução do CADO-NFS (formato próprio, sem caminho de máquina).

    python3 tools/fatoracao/captura_relacoes.py <pasta de trabalho do CADO> <nome, por exemplo c60> <destino>

Por que existe: o executor apagava a pasta de trabalho no sucesso, e sem as relações não dá para estudar quanta informação
nova cada uma traz. A captura guarda, de forma que outra pessoa reproduza:

* `relacoes.tsv.gz`: TODAS as relações brutas consumidas pelo filtro, na ordem canônica do próprio `filelist` do CADO
  (a verdade sobre o que entrou na filtragem, não um glob: a pasta de upload tem blocos que chegaram depois do fim da coleta);
* `arquivos.json`: por bloco, relações, special-q processados e CPU (a unidade de trabalho independente de hardware);
* `livres.tsv.gz`, `poly.txt`, `purgadas.tsv.gz`, `index.gz`, `purge.json`: o que o filtro fez com elas;
* `manifest.json`: contagens por estágio, sementes, commits e `sha256` de cada arquivo.

A ordem canônica é a do `filelist` e, dentro do bloco, a do arquivo: nunca tempo de relógio.
"""
import gzip
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

FORMATO = "relacoes-cado/v1"
CABECALHO_SQ = re.compile(r"# Sieving side-(\d) q=(\d+); rho=(\d+);")
TOTAL_REPORTS = re.compile(r"# Total (\d+) reports \[[\d.e+-]+s/r, ([\d.]+)r/sq\]")
CPU_TOTAL = re.compile(r"# Total cpu time ([\d.]+)s")
COMMIT_CADO = re.compile(r"^# \(([0-9a-f]{7,40})\)")


def sha256_arquivo(caminho):
    return hashlib.sha256(Path(caminho).read_bytes()).hexdigest()


def arquivos_consumidos(pasta, nome):
    """Os blocos que o CADO realmente mandou para a dedup, na ordem dele, somando TODAS as rodadas de filtragem.

    A 1ª rodada usa `<nome>.dup1.filelist.*` (ou, com poucos blocos como no c30, os arquivos na linha de comando); cada rodada
    seguinte (quando faltou relação, caso do c80) passa só os blocos novos na linha do `dup1`, registrada no log. Ler só a
    filelist devolve a 1ª rodada e uma matriz sem excesso: foi o erro que invalidou as primeiras capturas c80.
    """
    pasta = Path(pasta)
    nomes = []
    for lista in sorted(pasta.glob(f"{nome}.dup1.filelist.*")):
        nomes += [Path(x.strip()).name for x in lista.read_text(encoding="utf-8").splitlines() if x.strip()]
    if (pasta / f"{nome}.log").is_file():
        for linha in (pasta / f"{nome}.log").read_text(encoding="utf-8", errors="replace").splitlines():
            if "Command:" in linha and "/filter/dup1 " in linha:
                nomes += [Path(t).name for t in linha.split("Command:", 1)[1].split()[1:] if t.endswith(".gz")]
    if not nomes:
        raise FileNotFoundError(f"sem filelist nem comando do dup1 no log de {nome}: não dá para saber o que o filtro consumiu")
    nomes = list(dict.fromkeys(nomes))
    faltando = [n for n in nomes if not (pasta / f"{nome}.upload" / n).is_file()]
    if faltando:
        raise FileNotFoundError(f"blocos consumidos ausentes em {nome}.upload: {faltando[:3]}")
    return nomes


def ler_bloco(caminho):
    """(relacoes, estatisticas) de um bloco: cada relação é (q, rho, a, b, primos0, primos1) com primos em texto hexadecimal."""
    relacoes, q, rho, n_sq, cpu, commit = [], None, None, None, None, None
    with gzip.open(caminho, "rt", encoding="utf-8") as fh:
        for linha in fh:
            if linha.startswith("#"):
                m = CABECALHO_SQ.match(linha)
                if m:
                    q, rho = int(m.group(2)), int(m.group(3))
                m = TOTAL_REPORTS.match(linha)
                if m:
                    n_sq = round(int(m.group(1)) / float(m.group(2)))
                m = CPU_TOTAL.match(linha)
                if m:
                    cpu = float(m.group(1))
                m = COMMIT_CADO.match(linha)
                if m and commit is None:
                    commit = m.group(1)
                continue
            ab, p0, p1 = linha.strip().split(":")
            a, b = ab.split(",")
            relacoes.append((q, rho, int(a), int(b), p0, p1))
    return relacoes, {"n_sq": n_sq, "cpu_s": cpu, "commit_cado": commit}


def _gravar_gz(caminho, linhas):
    """gzip sem nome nem data no cabeçalho: o mesmo conteúdo dá sempre o mesmo `sha256`."""
    with open(caminho, "wb") as bruto, gzip.GzipFile(filename="", mode="wb", fileobj=bruto, mtime=0) as fh:
        for l in linhas:
            fh.write((l + "\n").encode("utf-8"))


def _rodada_do_purge(texto):
    ini = re.search(r"Sing\. rem\.: begin with: nrows=(\d+) ncols=(\d+) excess=(-?\d+)", texto)
    blocos = texto.split("Step 1 of")[0]
    fim = re.findall(r"nrows=(\d+) ncols=(\d+) excess=(-?\d+)", blocos)[-1]
    return ({"inicio": dict(zip(("nrows", "ncols", "excess"), map(int, ini.groups()))),
             "apos_singletons": dict(zip(("nrows", "ncols", "excess"), map(int, fim)))},
            len(re.findall(r"Step \d+ of \d+: target excess", texto)))


def _purge(pasta, nome):
    """Contagens do `purge` do CADO. `inicio`/`apos_singletons`/`final` são da ÚLTIMA rodada (a que gerou o `purged.gz`);
    `rodadas` traz todas, porque rodada com excesso negativo é a medida de quanto faltou de relação."""
    arqs = sorted(Path(pasta).glob(f"{nome}.purge.stdout.*"), key=lambda f: int(f.name.rsplit(".", 1)[1]))
    rodadas = [_rodada_do_purge(f.read_text(encoding="utf-8", errors="replace")) for f in arqs]
    ultima, cliques = rodadas[-1]
    primeira = open_gz_primeira_linha(Path(pasta) / f"{nome}.purged.gz")
    nrows, nprimos, ncols = (int(x) for x in primeira.lstrip("# ").split())
    return {**ultima, "final": {"nrows": nrows, "ncols": ncols, "excess": nrows - ncols}, "tamanho_renumber": nprimos,
            "etapas_de_cliques": cliques, "rodadas": [r for r, _ in rodadas]}


def open_gz_primeira_linha(caminho):
    with gzip.open(caminho, "rt", encoding="utf-8") as fh:
        return fh.readline()


def _params(pasta, nome):
    snap = Path(pasta) / f"{nome}.parameters_snapshot.0"
    if not snap.is_file():
        return {}
    saida = {}
    for l in snap.read_text(encoding="utf-8", errors="replace").splitlines():
        if "=" in l and "/" not in l and not l.lstrip().startswith("#"):
            k, v = l.split("=", 1)
            saida[k.strip()] = v.strip()
    return saida


def acrescentar_arquivo(destino, nome, texto):
    """Grava `nome` numa captura já feita e refaz `sha256`/`bytes` do manifesto.

    Usado para `badideais.txt` (o `badidealinfo` do CADO) e `inercias.txt` (saída de `cado/inercia.cpp`). Sem eles, ideal ruim
    vira uma coluna só e a matriz difere da do CADO em 1-2 colunas.
    """
    destino = Path(destino)
    (destino / nome).write_text(texto, encoding="utf-8")
    manifesto = json.loads((destino / "manifest.json").read_text(encoding="utf-8"))
    manifesto["sha256"][nome] = sha256_arquivo(destino / nome)
    manifesto["bytes"] = sum((destino / f).stat().st_size for f in manifesto["sha256"])
    (destino / "manifest.json").write_text(json.dumps(manifesto, indent=1, sort_keys=True), encoding="utf-8")


def inercias_do_poly(poly, binario):
    """Roda `cado/inercia.cpp` compilado (`binario`) sobre o `.poly` e devolve o texto: um ideal com inércia != 1 por linha."""
    r = subprocess.run([str(binario), str(poly)], capture_output=True, text=True, check=True)
    return r.stdout


def badideais_do_poly(poly, ferramenta):
    """`badidealinfo` do polinômio, gerado por `numbertheory_tool` do CADO (a pasta de trabalho não o guarda).

    A ferramenta sai com código 1 ("Ramified ell not supported") mesmo com `ell` primo grande, mas grava os arquivos: vale o arquivo.
    """
    import tempfile
    with tempfile.TemporaryDirectory() as t:
        subprocess.run([str(ferramenta), "-poly", str(poly), "-badideals", f"{t}/b", "-badidealinfo", f"{t}/i", "-ell", "1000003"],
                       capture_output=True, text=True)
        arq = Path(t) / "i"
        if not arq.is_file():
            raise RuntimeError(f"numbertheory_tool não gerou o badidealinfo de {poly}")
        return arq.read_text(encoding="utf-8")


def empacotar(pasta, nome, destino, meta=None, inercia=None, numbertheory=None):
    """Lê a pasta de trabalho do CADO e grava a captura em `destino`. Devolve o manifesto.

    `numbertheory`: caminho do `numbertheory_tool` (ou `CADO_NUMBERTHEORY_TOOL`), que gera os ideais ruins.
    `inercia`: caminho do binário de `tools/fatoracao/cado/inercia.cpp` (ou a variável de ambiente `CADO_INERCIA`). Sem ele a
    captura sai sem `inercias.txt` e `relacoes.carregar` avisa que a reprodução exata do purge não está garantida.
    """
    pasta, destino = Path(pasta), Path(destino)
    destino.mkdir(parents=True, exist_ok=True)
    blocos, linhas, arquivos, commit = arquivos_consumidos(pasta, nome), [], [], None
    idx = 0
    for k, bloco in enumerate(blocos):
        rels, est = ler_bloco(pasta / f"{nome}.upload" / bloco)
        commit = commit or est["commit_cado"]
        arquivos.append({"nome": bloco, "n_relacoes": len(rels), "n_sq": est["n_sq"], "cpu_s": est["cpu_s"]})
        for q, rho, a, b, p0, p1 in rels:
            linhas.append(f"{idx}\t{k}\t{q}\t{rho}\t{a}\t{b}\t{p0}\t{p1}")
            idx += 1
    _gravar_gz(destino / "relacoes.tsv.gz", ["#ordem\tbloco\tq\trho\ta\tb\tprimos_lado0\tprimos_lado1"] + linhas)
    (destino / "arquivos.json").write_text(json.dumps(arquivos, indent=1), encoding="utf-8")
    livres = []
    with gzip.open(pasta / f"{nome}.freerel.gz", "rt", encoding="utf-8") as fh:
        for l in fh:
            if not l.startswith("#"):
                cab, resto = l.strip().split(":")
                livres.append(f"{int(cab.split(',')[0], 16)}\t{len(resto.split(','))}")
    _gravar_gz(destino / "livres.tsv.gz", ["#p\tn_indices"] + livres)
    (destino / "poly.txt").write_text((pasta / f"{nome}.poly").read_text(encoding="utf-8"), encoding="utf-8")
    purgadas = []
    with gzip.open(pasta / f"{nome}.purged.gz", "rt", encoding="utf-8") as fh:
        for l in fh:
            if not l.startswith("#"):
                a, b = l.split(":", 1)[0].split(",")
                purgadas.append(f"{int(a, 16)}\t{int(b, 16)}")  # o purged.gz é sempre em hexadecimal
    _gravar_gz(destino / "purgadas.tsv.gz", ["#a\tb"] + purgadas)
    (destino / "index.gz").write_bytes((pasta / f"{nome}.index.gz").read_bytes())
    ruins = pasta / f"{nome}.badidealinfo"
    numbertheory = numbertheory or os.environ.get("CADO_NUMBERTHEORY_TOOL")
    if ruins.is_file():
        (destino / "badideais.txt").write_text(ruins.read_text(encoding="utf-8"), encoding="utf-8")
    elif numbertheory:
        (destino / "badideais.txt").write_text(badideais_do_poly(destino / "poly.txt", numbertheory), encoding="utf-8")
    inercia = inercia or os.environ.get("CADO_INERCIA")
    if inercia:
        (destino / "inercias.txt").write_text(inercias_do_poly(destino / "poly.txt", inercia), encoding="utf-8")
    purge = _purge(pasta, nome)
    (destino / "purge.json").write_text(json.dumps(purge, indent=1), encoding="utf-8")
    manifesto = {"formato": FORMATO, "nome": nome, "commit_cado": commit, "n_brutas": len(linhas), "n_blocos": len(blocos),
                 "n_livres": len(livres), "n_purgadas": len(purgadas), "purge": purge, "parametros": _params(pasta, nome),
                 "meta": meta or {}}
    manifesto["sha256"] = {f: sha256_arquivo(destino / f) for f in sorted(
        ("relacoes.tsv.gz", "arquivos.json", "livres.tsv.gz", "poly.txt", "purgadas.tsv.gz", "index.gz", "purge.json")
        + tuple(x for x in ("badideais.txt", "inercias.txt") if (destino / x).is_file()))}
    manifesto["bytes"] = sum((destino / f).stat().st_size for f in manifesto["sha256"])
    (destino / "manifest.json").write_text(json.dumps(manifesto, indent=1, sort_keys=True), encoding="utf-8")
    return manifesto


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 3:
        print(__doc__)
        return 2
    m = empacotar(*argv)
    print(json.dumps({k: m[k] for k in ("n_brutas", "n_blocos", "n_livres", "n_purgadas", "bytes")}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
