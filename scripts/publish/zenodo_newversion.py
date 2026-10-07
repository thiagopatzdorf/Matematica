#!/usr/bin/env python3
"""Publica uma NOVA VERSÃO de um registro do Zenodo (PDF + metadados do .zenodo.json).

Generaliza o script que publicou a v0.3.0 (registro 23085770, DOI conceitual
10.5281/zenodo.23085769). Passos com --publicar:

  0.  confere que o paper (.tex ao lado do PDF) e o .zenodo.json dizem a contagem de cotas no
      kernel do ledger (ledger/cells.json); se diverge, recusa antes de abrir rede
  1. POST  /deposit/depositions/<record>/actions/newversion
  2. GET   rascunho (links.latest_draft); apaga os arquivos herdados
  3. PUT   o PDF no bucket do rascunho
  4. PUT   metadados montados do .zenodo.json
  5. POST  /actions/publish

SECO É O PADRÃO: confere o PDF e o .zenodo.json localmente e mostra o plano,
sem rede. `--conferir` (ainda seco) faz só o GET do registro atual.

O token vem SÓ da variável de ambiente ZENODO_TOKEN e nunca é impresso:
toda mensagem passa por `redigir`. No repositório não há segredo nenhum.

Uso:
    python3 scripts/publish/zenodo_newversion.py --record 23085770 \\
        --pdf paper/main.pdf --zenodo-json .zenodo.json            # seco
    ZENODO_TOKEN=... python3 scripts/publish/zenodo_newversion.py ... --publicar
    ZENODO_TOKEN=... python3 scripts/publish/zenodo_newversion.py ... --publicar --release-github
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools" / "paper"))
import github_release  # noqa: E402
import numeros as paper_numeros  # noqa: E402

API = {"zenodo": "https://zenodo.org/api/deposit/depositions",
       "sandbox": "https://sandbox.zenodo.org/api/deposit/depositions"}
CAMPOS_OBRIGATORIOS = ("title", "description", "creators", "version", "keywords")


class ErroZenodo(RuntimeError):
    pass


RAIZ = Path(__file__).resolve().parents[2]


def ler_tex(caminho: Path) -> str:
    """O .tex com as macros do numeros.tex ao lado já expandidas: as contagens do ledger moram lá, não no texto."""
    tex = caminho.read_text(encoding="utf-8")
    numeros = caminho.with_name("numeros.tex")
    return paper_numeros.expandir(tex, numeros.read_text(encoding="utf-8")) if numeros.is_file() else tex


def contagem_do_kernel(cells_json: Path) -> tuple[int, int, int]:
    """(cotas superiores no kernel, CLAIMED, total) do ledger: FORMALIZED + INDEPENDENTLY_REPRODUCED."""
    cells = json.loads(cells_json.read_text(encoding="utf-8"))["cells"]
    est = [c["certification"]["ub"]["state"] for c in cells]
    return (est.count("FORMALIZED") + est.count("INDEPENDENTLY_REPRODUCED"), est.count("CLAIMED"), len(cells))


def conferir_contagem(tex: str, z: dict, cells_json: Path) -> None:
    """Na hora de publicar, o paper e o .zenodo.json dizem exatamente o que o ledger tem.

    Entre lançamentos o paper pode ficar atrás do ledger da main (tests/test_publish.py aceita);
    a igualdade é exigida aqui, no único passo que publica (v0.9.0 saiu dizendo 659 com 658)."""
    import re
    kernel, claimed, total = contagem_do_kernel(cells_json)
    tex = tex.replace(r"\allowbreak ", "")
    erros = []
    if tex.count(f"${kernel}$ of the ${total}$ upper bounds") != 2:
        erros.append(f"paper não diz ${kernel}$ of the ${total}$ upper bounds (resumo e seção do ledger)")
    if f"The other ${claimed}$ upper bounds are only claimed" not in tex:
        erros.append(f"paper não diz The other ${claimed}$ upper bounds are only claimed")
    if f"{kernel} of the {total} upper bounds are theorems of the Lean kernel" not in z.get("description", ""):
        erros.append(f".zenodo.json não diz {kernel} of the {total} upper bounds")
    ditos = re.findall(r"\$(\d+)\$ of the \$(\d+)\$ upper bounds", tex)
    if erros:
        raise ErroZenodo(f"contagem diverge do ledger ({kernel} no kernel, {claimed} CLAIMED, {total} células; "
                         f"o paper diz {ditos}): " + "; ".join(erros))


def redigir(texto: str, token: str | None) -> str:
    """Tira o token de qualquer texto antes de ir para a tela ou exceção."""
    texto = str(texto)
    if token:
        texto = texto.replace(token, "***")
    return texto


def montar_metadados(z: dict, data_publicacao: str) -> dict:
    faltando = [c for c in CAMPOS_OBRIGATORIOS if not z.get(c)]
    if faltando:
        raise ErroZenodo(f".zenodo.json sem {faltando}")
    desc = z["description"]
    if not desc.lstrip().startswith("<"):
        desc = "<p>" + desc + "</p>"
    return {
        "title": z["title"],
        "upload_type": z.get("upload_type", "publication"),
        "publication_type": z.get("publication_type", "preprint"),
        "description": desc,
        "creators": z["creators"],
        "access_right": z.get("access_right", "open"),
        "license": z.get("license", "cc-by-4.0"),
        "language": z.get("language", "eng"),
        "version": z["version"],
        "keywords": z["keywords"],
        "related_identifiers": z.get("related_identifiers", []),
        "publication_date": data_publicacao,
    }


class Cliente:
    """HTTP mínimo. `abrir` é injetável para teste (padrão: urllib)."""

    def __init__(self, token: str, base: str, abrir=None):
        self.token = token
        self.base = base
        self.abrir = abrir or (lambda req, timeout: urllib.request.urlopen(req, timeout=timeout))

    def req(self, metodo: str, url: str, dados: bytes | None = None, ct: str | None = None):
        h = {"Authorization": f"Bearer {self.token}"}
        if ct:
            h["Content-Type"] = ct
        r = urllib.request.Request(url, data=dados, headers=h, method=metodo)
        try:
            with self.abrir(r, timeout=180) as x:
                b = x.read()
                return x.status, (json.loads(b) if b else {})
        except urllib.error.HTTPError as e:
            corpo = e.read()[:400].decode("utf-8", "replace")
            return e.code, redigir(corpo, self.token)

    def exigir(self, etapa: str, res):
        s, corpo = res
        if s >= 300:
            raise ErroZenodo(redigir(f"{etapa}: HTTP {s} {corpo}", self.token))
        return corpo


def publicar(cli: Cliente, record: str, pdf: Path, nome_arquivo: str, meta: dict, log=print) -> dict:
    nv = cli.exigir("newversion", cli.req("POST", f"{cli.base}/{record}/actions/newversion"))
    draft = cli.exigir("rascunho", cli.req("GET", nv["links"]["latest_draft"]))
    did = draft["id"]
    for f in draft.get("files", []):
        s, _ = cli.req("DELETE", f"{cli.base}/{did}/files/{f['id']}")
        log(f"apagou arquivo herdado do rascunho: HTTP {s}")
    up = cli.exigir("upload", cli.req("PUT", draft["links"]["bucket"] + "/" + nome_arquivo,
                                      pdf.read_bytes(), "application/octet-stream"))
    log(f"pdf enviado: checksum {up.get('checksum')}")
    cli.exigir("metadados", cli.req("PUT", f"{cli.base}/{did}",
                                    json.dumps({"metadata": meta}).encode(), "application/json"))
    pub = cli.exigir("publish", cli.req("POST", f"{cli.base}/{did}/actions/publish"))
    log(f"PUBLICADO {pub.get('doi')} {pub.get('links', {}).get('record_html')} conceito {pub.get('conceptdoi')}")
    return pub


def main(argv=None, abrir=None, ambiente=None, rodar=subprocess.run) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    ap.add_argument("--record", required=True, help="id de qualquer versão do registro (ex.: 23085770)")
    ap.add_argument("--pdf", type=Path, required=True)
    ap.add_argument("--zenodo-json", type=Path, required=True)
    ap.add_argument("--nome-arquivo", help="nome do PDF no Zenodo (padrão: covering-codes-lean-kernel-v<versão>.pdf)")
    ap.add_argument("--data-publicacao", default=dt.date.today().isoformat())
    ap.add_argument("--sandbox", action="store_true", help="usa sandbox.zenodo.org")
    ap.add_argument("--conferir", action="store_true", help="seco, mas faz o GET do registro atual")
    ap.add_argument("--publicar", action="store_true", help="publica de verdade (padrão: seco)")
    ap.add_argument("--release-github", action="store_true",
                    help="depois de publicar, cria a release do GitHub com o DOI cunhado (github_release.py)")
    ap.add_argument("--titulo-release", help="título da release do GitHub (padrão: v<versão>)")
    ap.add_argument("--tex", type=Path, help="fonte do paper (padrão: o .tex ao lado do --pdf)")
    ap.add_argument("--ledger", type=Path, default=RAIZ / "ledger" / "cells.json",
                    help="ledger cuja contagem o paper e o .zenodo.json têm de repetir ao publicar")
    a = ap.parse_args(argv)
    env = os.environ if ambiente is None else ambiente
    token = env.get("ZENODO_TOKEN", "").strip() or None

    try:
        if not a.pdf.is_file():
            raise ErroZenodo(f"PDF não encontrado: {a.pdf}")
        z = json.loads(a.zenodo_json.read_text(encoding="utf-8"))
        meta = montar_metadados(z, a.data_publicacao)
        nome = a.nome_arquivo or f"covering-codes-lean-kernel-v{meta['version']}.pdf"
        pdf_b = a.pdf.read_bytes()
        print(f"registro {a.record} ({'sandbox' if a.sandbox else 'zenodo'}); versão {meta['version']}; "
              f"data {a.data_publicacao}")
        print(f"pdf {a.pdf}: {len(pdf_b)} bytes, sha256 {hashlib.sha256(pdf_b).hexdigest()} -> {nome}")
        print(f"título: {meta['title']}")
        print(f"ZENODO_TOKEN: {'presente, ' + str(len(token)) + ' caracteres' if token else 'ausente'}")
        base = API["sandbox" if a.sandbox else "zenodo"]
        if not a.publicar:
            if a.conferir:
                if not token:
                    raise ErroZenodo("--conferir precisa de ZENODO_TOKEN")
                cli = Cliente(token, base, abrir)
                dep = cli.exigir("registro atual", cli.req("GET", f"{base}/{a.record}"))
                print(f"registro atual: doi {dep.get('doi')} versão {dep.get('metadata', {}).get('version')}")
            print("SECO: faria newversion, trocaria o PDF, gravaria os metadados e publicaria. Use --publicar.")
            return 0
        if not token:
            raise ErroZenodo("ZENODO_TOKEN ausente no ambiente")
        tex = ler_tex(a.tex or a.pdf.with_suffix(".tex"))
        conferir_contagem(tex, z, a.ledger)
        pub = publicar(Cliente(token, base, abrir), a.record, a.pdf, nome, meta)
        if a.release_github:
            # A release do GitHub nasce no mesmo passo que o DOI: v0.8.0 e v0.9.0 ficaram
            # dois dias sem página de release porque esse passo dependia de lembrar.
            tag, titulo, notas = github_release.montar(z, pub.get("doi", ""), a.titulo_release)
            github_release.criar(tag, titulo, notas, a.pdf, rodar)
        return 0
    except github_release.ErroRelease as e:
        print("ERRO (Zenodo já publicado; release do GitHub não criada): " + redigir(e, token), file=sys.stderr)
        return 3
    except ErroZenodo as e:
        print("ERRO: " + redigir(e, token), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
