#!/usr/bin/env python3
"""Gera site/matematica/dados.json: os números que a página pública mostra.

Toda contagem sai do repositório, nunca de texto escrito à mão:

* ledger/cells.json   -> células, exatas, abertas, estados por lado, destaques;
* ledger/COBERTURA.md -> conferência cruzada: se a tabela gerada por
  ledger/cobertura.py divergir das contagens de cells.json, o script falha
  (a página não pode mostrar um número que o ledger não sustenta);
* data/codes/*.txt    -> códigos explícitos conferidos pelo verificador oficial
  (tools/verify/check_all.sh roda sobre todos eles no CI);
* .zenodo.json e CITATION.cff -> versão (as duas têm de concordar);
* git rev-parse HEAD  -> commit.

Determinístico: com --commit e --gerado-em fixos, duas execuções dão bytes
idênticos. Só stdlib.

Uso:
    python3 tools/site/gerar_dados_site.py                 # escreve site/matematica/dados.json
    python3 tools/site/gerar_dados_site.py --verificar     # falha se o versionado estiver velho
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
SAIDA = RAIZ / "site" / "matematica" / "dados.json"
ESTADOS = ["CLAIMED", "WITNESS_CHECKED", "CERTIFICATE_VERIFIED", "FORMALIZED",
           "INDEPENDENTLY_REPRODUCED"]
# DOIs do Zenodo. O de conceito está no CITATION.cff e é conferido lá; o da
# versão 0.9.0 é o registro dessa versão específica (resolve sempre para ela).
DOI_VERSAO = {"0.9.0": "10.5281/zenodo.23172276"}
DOI_CONCEITO = "10.5281/zenodo.23085769"
NOME_CODIGO = re.compile(r"^q\d+_n\d+_R\d+_M\d+\.txt$")
# Campos que mudam a cada execução; --verificar os ignora.
VOLATEIS = ("gerado_em", "commit")


class Divergencia(ValueError):
    """Duas fontes do repositório discordam; publicar seria mostrar um número sem lastro."""


def _intervalo(lb: int | None, ub: int | None) -> str:
    if lb is not None and lb == ub:
        return f"K = {ub}"
    if lb is None:
        return f"K ≤ {ub}"
    return f"{lb} ≤ K ≤ {ub}"


def _fonte(c: dict) -> str:
    lean = c.get("ours_lean")
    if lean and lean.get("declaration"):
        return f"Lean: {lean['declaration']}"
    prov = c["certification"]["lb"].get("provenance") or {}
    red = (prov.get("certificado") or {}).get("red_team") or {}
    if red.get("doc"):
        return red["doc"]
    return "ledger/cells.json"


def _e_destaque(c: dict) -> bool:
    """Célula em que este repositório mudou algo: cota superior abaixo da
    publicada, ou cota inferior certificada aqui (acima de CLAIMED)."""
    return bool(c["best"].get("beats_published")) or c["certification"]["lb"]["state"] != "CLAIMED"


def destaques(cells: list[dict]) -> list[dict]:
    out = []
    for c in cells:
        if not _e_destaque(c):
            continue
        pub, cert = c["published"], c["certification"]
        out.append({
            "celula": c["id"],
            "antes": _intervalo(pub["lb"]["value"] if pub["lb"] else None,
                                pub["ub"]["value"] if pub["ub"] else None),
            "agora": _intervalo(cert["lb"]["value"], cert["ub"]["value"]),
            "estado_lb": cert["lb"]["state"],
            "estado_ub": cert["ub"]["state"],
            "fonte": _fonte(c),
        })
    return sorted(out, key=lambda d: _chave_celula(d["celula"]))


def _chave_celula(cid: str) -> tuple[int, int, int]:
    q, n, r = re.match(r"K(\d+)\((\d+),(\d+)\)", cid).groups()
    return int(q), int(n), int(r)


def contar_estados(cells: list[dict], lado: str) -> dict[str, int]:
    conta = {e: 0 for e in ESTADOS}
    for c in cells:
        estado = c["certification"][lado]["state"]
        if estado not in conta:
            raise Divergencia(f"{c['id']}: estado {estado!r} fora da escada {ESTADOS}")
        conta[estado] += 1
    return conta


def ler_cobertura(texto: str) -> dict:
    """Extrai de ledger/COBERTURA.md o total, as exatas e a tabela por lado."""
    m = re.search(r"Total: (\d+) células; exatas \(inferior = superior\): (\d+)", texto)
    if not m:
        raise Divergencia("COBERTURA.md sem a linha 'Total: N células; exatas ...: M'")
    lados = {}
    for lado in ("ub", "lb"):
        linha = re.search(rf"^\| {lado} \|((?: *\d+ *\|){{{len(ESTADOS)}}})\s*$", texto, re.M)
        if not linha:
            raise Divergencia(f"COBERTURA.md sem a linha da tabela de estados para {lado}")
        nums = [int(x) for x in linha.group(1).split("|") if x.strip()]
        lados[lado] = dict(zip(ESTADOS, nums))
    return {"total": int(m.group(1)), "exatas": int(m.group(2)), **lados}


def versao_do_repo(raiz: Path) -> str:
    zen = json.loads((raiz / ".zenodo.json").read_text(encoding="utf-8"))["version"]
    cff = (raiz / "CITATION.cff").read_text(encoding="utf-8")
    m = re.search(r"^version:\s*['\"]?([^'\"\s]+)", cff, re.M)
    if not m or m.group(1) != zen:
        raise Divergencia(f"versão do .zenodo.json ({zen}) != CITATION.cff ({m and m.group(1)})")
    d = re.search(r"^doi:\s*(\S+)", cff, re.M)
    if not d or d.group(1) != DOI_CONCEITO:
        raise Divergencia(f"DOI de conceito do CITATION.cff ({d and d.group(1)}) != {DOI_CONCEITO}")
    return zen


def contar_codigos(raiz: Path) -> int:
    return sum(1 for p in (raiz / "data" / "codes").iterdir() if NOME_CODIGO.match(p.name))


def gerar(raiz: Path = RAIZ, *, commit: str | None = None, gerado_em: str | None = None) -> dict:
    cells = json.loads((raiz / "ledger" / "cells.json").read_text(encoding="utf-8"))["cells"]
    total = len(cells)
    exatas = sum(1 for c in cells if c["certification"]["exact"])
    sup, inf = contar_estados(cells, "ub"), contar_estados(cells, "lb")

    cob = ler_cobertura((raiz / "ledger" / "COBERTURA.md").read_text(encoding="utf-8"))
    esperado = {"total": total, "exatas": exatas, "ub": sup, "lb": inf}
    if cob != esperado:
        raise Divergencia(f"ledger/COBERTURA.md {cob} diverge de ledger/cells.json {esperado}; "
                          "rode python3 ledger/cobertura.py")

    versao = versao_do_repo(raiz)
    if versao not in DOI_VERSAO:
        raise Divergencia(f"versão {versao} sem DOI de versão registrado em DOI_VERSAO")
    if commit is None:
        commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=raiz, capture_output=True,
                                text=True, check=True).stdout.strip()
    if gerado_em is None:
        gerado_em = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()
    return {
        "gerado_em": gerado_em,
        "commit": commit,
        "versao": versao,
        "doi": DOI_VERSAO[versao],
        "doi_conceito": DOI_CONCEITO,
        "frase_ledger": ("A machine-checked ledger of covering-code upper bounds, "
                         "with formally certified exact entries."),
        "celulas_total": total,
        "exatas": exatas,
        "abertas": total - exatas,
        "superiores_por_estado": sup,
        "inferiores_por_estado": inf,
        "destaques": destaques(cells),
        "codigos_verificados": contar_codigos(raiz),
    }


def serializar(dados: dict) -> str:
    return json.dumps(dados, ensure_ascii=False, indent=2) + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--saida", type=Path, default=SAIDA)
    ap.add_argument("--commit")
    ap.add_argument("--gerado-em")
    ap.add_argument("--verificar", action="store_true",
                    help="não escreve; falha se o arquivo versionado diverge (fora gerado_em/commit)")
    a = ap.parse_args(argv)
    try:
        dados = gerar(commit=a.commit, gerado_em=a.gerado_em)
    except Divergencia as e:
        print(f"ERRO: {e}", file=sys.stderr)
        return 1
    if a.verificar:
        atual = json.loads(a.saida.read_text(encoding="utf-8")) if a.saida.exists() else {}
        limpo = lambda d: {k: v for k, v in d.items() if k not in VOLATEIS}  # noqa: E731
        if limpo(atual) != limpo(dados):
            print(f"ERRO: {a.saida} está velho; rode python3 tools/site/gerar_dados_site.py",
                  file=sys.stderr)
            return 1
        print(f"ok: {a.saida} confere com o repositório")
        return 0
    a.saida.parent.mkdir(parents=True, exist_ok=True)
    a.saida.write_text(serializar(dados), encoding="utf-8")
    print(f"escrito {a.saida} ({dados['celulas_total']} células, {len(dados['destaques'])} destaques)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
