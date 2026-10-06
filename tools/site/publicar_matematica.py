#!/usr/bin/env python3
"""Publica (e despublica) site/matematica/ em https://genesisinnovation.io/matematica.

Como a raiz é servida (medido em 2026-10-06): genesisinnovation.io é um domínio
customizado do Worker Cloudflare `mybagcenter-static-legado-proxy` (fonte em
thiagopatzdorf/fabrica-de-sites, infra/static-legado/worker.js), que lê do
bucket GCS público `mybagcenter-static-legado`, prefixo `genesis/`. Cada página
é um objeto sem extensão: /matematica -> objeto `genesis/matematica`;
/matematica/x.css -> `genesis/matematica/x.css`; objeto ausente -> 404 de
verdade. Por isso publicar aqui NÃO mexe na Cloudflare: nenhum Worker, rota ou
DNS novo, nada que dispute a cota grátis da loja. É só subir objetos no bucket.

O index.html vira o objeto `genesis/matematica` com <base href="/matematica/">
injetado (sem isso, `estilo.css` relativo resolveria na raiz do site), e os
links de âncora `href="#x"` viram `href="/matematica#x"` (com o <base>, `#x`
apontaria para /matematica/#x e recarregaria a página).

Templo: antes de sobrescrever ou apagar, cada objeto atual é copiado para
gs://factory-cauteloso-telemetria/matematica-site-backup/<carimbo>/ e
`restaurar --carimbo` devolve exatamente aquele estado.

Credencial: token OAuth em $GCS_TOKEN (nunca impresso); sem ele, tenta
`gcloud auth print-access-token`. Na factory-01, ver docs/infra/PAGINA_MATEMATICA.md.

Uso (seco por padrão; só escreve com --confirmar):
    python3 tools/site/publicar_matematica.py publicar   [--pasta site/matematica] [--confirmar]
    python3 tools/site/publicar_matematica.py despublicar [--confirmar]
    python3 tools/site/publicar_matematica.py restaurar --carimbo 20261006T010203Z [--confirmar]
    python3 tools/site/publicar_matematica.py listar
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
BUCKET = "mybagcenter-static-legado"
PREFIXO = "genesis/matematica"          # o objeto da página; o resto vai em PREFIXO + "/"
CAMINHO = "/matematica"
SITE = "https://genesisinnovation.io" + CAMINHO
BACKUP_BUCKET = "factory-cauteloso-telemetria"
BACKUP_PREFIXO = "matematica-site-backup"
API = "https://storage.googleapis.com/storage/v1/b"
UPLOAD = "https://storage.googleapis.com/upload/storage/v1/b"
# 60 s: sem cacheControl o GCS aplica 1 h de cache público (medido na casa).
CACHE = "public, max-age=60"
# A Cloudflare da zona responde 403 ao User-Agent padrão "Python-urllib" (medido em
# 2026-10-06); a conferência se identifica com um nome honesto, não finge navegador.
UA = "matematica-publicador/1 (+https://github.com/thiagopatzdorf/Matematica)"
TIPOS = {
    ".html": "text/html; charset=utf-8", ".css": "text/css; charset=utf-8",
    ".js": "application/javascript; charset=utf-8", ".mjs": "application/javascript; charset=utf-8",
    ".json": "application/json; charset=utf-8", ".svg": "image/svg+xml", ".png": "image/png",
    ".jpg": "image/jpeg", ".webp": "image/webp", ".ico": "image/x-icon", ".woff2": "font/woff2",
    ".txt": "text/plain; charset=utf-8", ".pdf": "application/pdf",
}
IGNORAR = {".md", ".py"}                # README e ferramental ficam no repo
TETO = 5 * 1024 * 1024                  # mesmo teto por arquivo dos testes de higiene


class Recusa(ValueError):
    """O conteúdo não pode subir como está (sem index, extensão sem tipo, arquivo grande)."""


def html_entrada(texto: str) -> str:
    sem_coment = re.sub(r"<!--.*?-->", "", texto, flags=re.S)
    if "<base " in sem_coment:
        raise Recusa("index.html já tem <base>; o publicador injeta o dele")
    m = re.search(r"<head(\s[^>]*)?>", texto, flags=re.I)
    if not m:
        raise Recusa("index.html sem <head>")
    texto = texto[:m.end()] + f'<base href="{CAMINHO}/">' + texto[m.end():]
    return re.sub(r'href=(["\'])#', lambda g: f"href={g.group(1)}{CAMINHO}#", texto)


def plano(pasta: Path) -> list[tuple[str, str, bytes]]:
    """(objeto, content-type, bytes) para cada arquivo publicável da pasta, ordenado."""
    if not (pasta / "index.html").is_file():
        raise Recusa(f"{pasta}/index.html não existe")
    itens = []
    for p in sorted(pasta.rglob("*")):
        if not p.is_file() or p.name.startswith("."):
            continue
        rel = p.relative_to(pasta).as_posix()
        ext = p.suffix.lower()
        if ext in IGNORAR:
            continue
        if ext not in TIPOS:
            raise Recusa(f"{rel}: extensão sem content-type conhecido")
        if p.stat().st_size > TETO:
            raise Recusa(f"{rel}: {p.stat().st_size} bytes acima do teto de {TETO}")
        if rel == "index.html":
            itens.append((PREFIXO, TIPOS[ext], html_entrada(p.read_text(encoding="utf-8")).encode()))
        else:
            itens.append((f"{PREFIXO}/{rel}", TIPOS[ext], p.read_bytes()))
    return itens


# ---------------------------------------------------------------- GCS (stdlib)
def token() -> str:
    t = os.environ.get("GCS_TOKEN", "").strip()
    if t:
        return t
    try:
        return subprocess.run(["gcloud", "auth", "print-access-token"], capture_output=True,
                              text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        sys.exit("sem credencial: exporte GCS_TOKEN (ver docs/infra/PAGINA_MATEMATICA.md)")


def q(s: str) -> str:
    return urllib.parse.quote(s, safe="")


def chamar(metodo: str, url: str, tok: str, corpo: bytes | None = None,
           tipo: str = "application/json") -> tuple[int, bytes]:
    req = urllib.request.Request(url, data=corpo, method=metodo,
                                 headers={"Authorization": f"Bearer {tok}", "Content-Type": tipo})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()


def listar(tok: str) -> list[str]:
    nomes, pagina = [], None
    while True:
        url = f"{API}/{BUCKET}/o?prefix={q(PREFIXO)}&fields=items(name),nextPageToken"
        if pagina:
            url += f"&pageToken={q(pagina)}"
        st, b = chamar("GET", url, tok)
        if st != 200:
            raise RuntimeError(f"listar: HTTP {st} {b[:200]!r}")
        d = json.loads(b or b"{}")
        # prefix casa também genesis/matematica-outra-coisa: só a página e o que está abaixo dela
        nomes += [i["name"] for i in d.get("items", [])
                  if i["name"] == PREFIXO or i["name"].startswith(PREFIXO + "/")]
        pagina = d.get("nextPageToken")
        if not pagina:
            return sorted(nomes)


def copiar(tok: str, b_orig: str, orig: str, b_dest: str, dest: str) -> bool:
    url = f"{API}/{b_orig}/o/{q(orig)}/rewriteTo/b/{b_dest}/o/{q(dest)}"
    st, b = chamar("POST", url, tok, b"{}")
    if st == 404:
        return False
    while True:
        if st != 200:
            raise RuntimeError(f"copiar {orig}: HTTP {st} {b[:200]!r}")
        d = json.loads(b)
        if d.get("done"):
            return True
        st, b = chamar("POST", url + f"?rewriteToken={q(d['rewriteToken'])}", tok, b"{}")


def guardar(tok: str, nomes: list[str], carimbo: str) -> int:
    n = 0
    for nome in nomes:
        n += copiar(tok, BUCKET, nome, BACKUP_BUCKET, f"{BACKUP_PREFIXO}/{carimbo}/{nome}")
    return n


def subir(tok: str, nome: str, tipo: str, dados: bytes) -> None:
    b = "matematica7f3a"
    meta = json.dumps({"name": nome, "contentType": tipo, "cacheControl": CACHE}).encode()
    corpo = (f"--{b}\r\nContent-Type: application/json; charset=UTF-8\r\n\r\n".encode() + meta
             + f"\r\n--{b}\r\nContent-Type: {tipo}\r\n\r\n".encode() + dados + f"\r\n--{b}--".encode())
    st, r = chamar("POST", f"{UPLOAD}/{BUCKET}/o?uploadType=multipart", tok, corpo,
                   f"multipart/related; boundary={b}")
    if st != 200:
        raise RuntimeError(f"subir {nome}: HTTP {st} {r[:200]!r}")


def apagar(tok: str, nome: str) -> None:
    st, r = chamar("DELETE", f"{API}/{BUCKET}/o/{q(nome)}", tok)
    if st not in (204, 404):
        raise RuntimeError(f"apagar {nome}: HTTP {st} {r[:200]!r}")


# A borda da Cloudflare injeta o beacon do Web Analytics no HTML de algumas
# respostas (medido em 2026-10-06 a partir da factory-01, não daqui): a
# conferência descarta só essa tag antes de comparar os bytes.
BEACON = re.compile(rb'<script[^>]*static\.cloudflareinsights\.com[^>]*>\s*</script>\s*')


def sem_beacon(corpo: bytes) -> bytes:
    return BEACON.sub(b"", corpo)


def conferir_no_ar(itens: list[tuple[str, str, bytes]]) -> list[str]:
    """Baixa cada arquivo pela URL pública e compara os bytes: 'enviado' não é 'entregue'."""
    erros = []
    for nome, _, dados in itens:
        url = "https://genesisinnovation.io/" + nome[len("genesis/"):]
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"Cache-Control": "no-cache", "User-Agent": UA}),
                                        timeout=60) as r:
                if r.status != 200 or sem_beacon(r.read()) != dados:
                    erros.append(f"{url}: conteúdo no ar difere do enviado")
        except urllib.error.HTTPError as e:
            erros.append(f"{url}: HTTP {e.code}")
    return erros


def carimbo_agora() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("acao", choices=["publicar", "despublicar", "restaurar", "listar"])
    ap.add_argument("--pasta", type=Path, default=RAIZ / "site" / "matematica")
    ap.add_argument("--carimbo", help="restaurar: carimbo do backup (AAAAMMDDTHHMMSSZ)")
    ap.add_argument("--confirmar", action="store_true", help="sem isto, só mostra o que faria")
    a = ap.parse_args(argv)

    if a.acao == "publicar":
        itens = plano(a.pasta)
        for nome, tipo, dados in itens:
            print(f"{'subir' if a.confirmar else 'subiria'} gs://{BUCKET}/{nome} ({tipo}, {len(dados)} B)")
        if not a.confirmar:
            return 0
        tok, carimbo = token(), carimbo_agora()
        atuais = listar(tok)
        print(f"backup de {guardar(tok, atuais, carimbo)} objeto(s) em "
              f"gs://{BACKUP_BUCKET}/{BACKUP_PREFIXO}/{carimbo}/")
        for nome, tipo, dados in itens:
            subir(tok, nome, tipo, dados)
        # Objeto que saiu da pasta sai do ar também (senão um arquivo renomeado fica servido para sempre).
        novos = {n for n, _, _ in itens}
        for nome in atuais:
            if nome not in novos:
                apagar(tok, nome)
                print(f"apagado {nome} (não está mais na pasta)")
        erros = conferir_no_ar(itens)
        for e in erros:
            print("ERRO:", e, file=sys.stderr)
        print(f"{'FALHOU' if erros else 'ok'}: {SITE} ({len(itens)} arquivos; "
              f"volta: restaurar --carimbo {carimbo})")
        return 1 if erros else 0

    tok = token()
    if a.acao == "listar":
        for nome in listar(tok):
            print(nome)
        return 0

    if a.acao == "despublicar":
        atuais = listar(tok)
        for nome in atuais:
            print(f"{'apagar' if a.confirmar else 'apagaria'} gs://{BUCKET}/{nome}")
        if not a.confirmar or not atuais:
            return 0
        carimbo = carimbo_agora()
        if guardar(tok, atuais, carimbo) != len(atuais):
            print("ERRO: backup incompleto; nada foi apagado", file=sys.stderr)
            return 1
        for nome in atuais:
            apagar(tok, nome)
        print(f"despublicado; volta: restaurar --carimbo {carimbo} --confirmar")
        return 0

    # restaurar
    if not a.carimbo or not re.fullmatch(r"\d{8}T\d{6}Z", a.carimbo):
        print("ERRO: restaurar exige --carimbo AAAAMMDDTHHMMSSZ", file=sys.stderr)
        return 2
    base = f"{BACKUP_PREFIXO}/{a.carimbo}/"
    st, b = chamar("GET", f"{API}/{BACKUP_BUCKET}/o?prefix={q(base + PREFIXO)}&fields=items(name)", tok)
    if st != 200:
        print(f"ERRO: listar backup: HTTP {st}", file=sys.stderr)
        return 1
    nomes = [i["name"][len(base):] for i in json.loads(b or b"{}").get("items", [])]
    if not nomes:
        print(f"ERRO: backup {a.carimbo} vazio ou inexistente", file=sys.stderr)
        return 1
    for nome in nomes:
        print(f"{'restaurar' if a.confirmar else 'restauraria'} {nome}")
    if a.confirmar:
        guardar(tok, listar(tok), carimbo_agora())   # o estado atual também ganha volta
        for nome in nomes:
            copiar(tok, BACKUP_BUCKET, base + nome, BUCKET, nome)
        for nome in set(listar(tok)) - set(nomes):
            apagar(tok, nome)
        print("restaurado")
    return 0


if __name__ == "__main__":
    sys.exit(main())
