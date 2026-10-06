#!/usr/bin/env python3
"""Cria a release do GitHub de uma versão já publicada no Zenodo.

Existe porque a v0.8.0 e a v0.9.0 ganharam tag e DOI, mas ninguém criou a
página de release: o GitHub continuou mostrando a v0.7.0 como "Latest" por
dois dias. Agora `zenodo_newversion.py --publicar --release-github` chama
este módulo logo depois do DOI ser cunhado, e o passo deixa de depender de
alguém lembrar.

As notas saem do próprio `.zenodo.json`: o trecho "New in version <versão>:"
da descrição, mais a frase obrigatória do ledger e os dois DOIs. Sem esse
trecho a release não é criada (é sinal de que a descrição não foi
atualizada para a versão).

SECO É O PADRÃO: mostra título e notas. `--criar` roda `gh release create`
com a autenticação que o `gh` já tem; nenhum token passa por aqui.

Uso:
    python3 scripts/publish/github_release.py --zenodo-json .zenodo.json \\
        --doi 10.5281/zenodo.23178159 --pdf paper/main.pdf          # seco
    python3 scripts/publish/github_release.py ... --criar
"""
from __future__ import annotations

import argparse
import html
import json
import re
import subprocess
import sys
from pathlib import Path

REPO = "thiagopatzdorf/Matematica"
DOI_CONCEITO = "10.5281/zenodo.23085769"
FRASE_LEDGER = ("A machine-checked ledger of covering-code upper bounds, "
                "with formally certified exact entries.")


class ErroRelease(RuntimeError):
    pass


def _texto(descricao: str) -> str:
    sem_tags = re.sub(r"<[^>]+>", " ", descricao)
    return re.sub(r"\s+", " ", html.unescape(sem_tags)).strip()


def novidades(descricao: str, versao: str) -> str:
    """Trecho "New in version <versao>: ..." até a próxima versão ou o fim."""
    texto = _texto(descricao)
    marca = f"New in version {versao}:"
    i = texto.find(marca)
    if i < 0:
        raise ErroRelease(f"a descrição do .zenodo.json não tem '{marca}'")
    resto = texto[i + len(marca):]
    prox = re.search(r"New in version \d+\.\d+\.\d+:", resto)
    return resto[:prox.start() if prox else None].strip()


def montar(z: dict, doi: str, titulo: str | None = None) -> tuple[str, str, str]:
    """Devolve (tag, título, notas em markdown)."""
    versao = z.get("version")
    if not versao:
        raise ErroRelease(".zenodo.json sem 'version'")
    if not re.fullmatch(r"10\.5281/zenodo\.\d+", doi or ""):
        raise ErroRelease(f"DOI do Zenodo inválido: {doi!r}")
    tag = f"v{versao}"
    notas = (f"New in {tag}: {novidades(z['description'], versao)}\n\n"
             f"{FRASE_LEDGER}\n\n"
             f"Zenodo: https://doi.org/{doi} · concept DOI (always the latest): "
             f"https://doi.org/{DOI_CONCEITO}\n")
    return tag, titulo or tag, notas


def criar(tag: str, titulo: str, notas: str, pdf: Path | None, rodar=subprocess.run) -> None:
    cmd = ["gh", "release", "create", tag, "-R", REPO, "--title", titulo,
           "--notes-file", "-", "--latest", "--verify-tag"]
    if pdf is not None:
        cmd.append(str(pdf))
    r = rodar(cmd, input=notas, text=True, capture_output=True)
    if r.returncode != 0:
        raise ErroRelease(f"gh release create falhou ({r.returncode}): {r.stderr.strip()}")
    print(f"RELEASE {r.stdout.strip()}")


def main(argv=None, rodar=subprocess.run) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    ap.add_argument("--zenodo-json", type=Path, required=True)
    ap.add_argument("--doi", required=True, help="DOI da versão (não o conceito)")
    ap.add_argument("--titulo", help="título da release (padrão: v<versão>)")
    ap.add_argument("--pdf", type=Path, help="PDF anexado à release")
    ap.add_argument("--criar", action="store_true", help="cria de verdade (padrão: seco)")
    a = ap.parse_args(argv)
    try:
        z = json.loads(a.zenodo_json.read_text(encoding="utf-8"))
        tag, titulo, notas = montar(z, a.doi, a.titulo)
        if a.pdf is not None and not a.pdf.is_file():
            raise ErroRelease(f"PDF não encontrado: {a.pdf}")
        print(f"tag {tag}; título: {titulo}\n---\n{notas}---")
        if not a.criar:
            print("SECO: criaria a release no GitHub. Use --criar.")
            return 0
        criar(tag, titulo, notas, a.pdf, rodar)
        return 0
    except ErroRelease as e:
        print(f"ERRO: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
