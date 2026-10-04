"""Módulo papers: arXiv, OpenAlex, Semantic Scholar, Zenodo e a biblioteca no bucket.

Cada busca é guardada em `buscas/<fonte>/<sha>.json` no bucket de literatura: a mesma pergunta
feita por outra pessoa volta do cache e não bate de novo na fonte (descoberta cara vira
verificação barata). O que o módulo devolve é sempre o registro da fonte, com o link: ele
nunca resume um paper de memória.

`paper_guardar` só baixa de hosts da allowlist (sem isso o servidor viraria um proxy aberto para
a rede interna) e recusa passar de 30 MB. Nada aqui gasta crédito: são APIs abertas.
"""
from __future__ import annotations

import hashlib
import json
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from typing import Callable

NOME = "papers"
FONTES = ("arxiv", "openalex", "semanticscholar", "zenodo")
HOSTS_PDF = ("arxiv.org", "zenodo.org", "www.biorxiv.org", "openreview.net", "hal.science", "eprint.iacr.org")
PDF_MAX = 30_000_000
UA = "infinito-mcp/1 (pesquisa de matematica; contato: thiagosleman@gmail.com)"
_ATOM = {"a": "http://www.w3.org/2005/Atom"}

Buscador = Callable[[str, int], list[dict]]


def _get(url: str, timeout: int = 30) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read(PDF_MAX + 1)


def buscar_arxiv(consulta: str, limite: int, get=_get) -> list[dict]:
    q = urllib.parse.urlencode({"search_query": f"all:{consulta}", "start": 0, "max_results": limite,
                                "sortBy": "relevance"})
    raiz = ET.fromstring(get(f"https://export.arxiv.org/api/query?{q}"))
    saida = []
    for e in raiz.findall("a:entry", _ATOM):
        link = e.findtext("a:id", "", _ATOM)
        saida.append({"fonte": "arxiv", "id": link.rsplit("/abs/", 1)[-1], "titulo": " ".join(e.findtext("a:title", "", _ATOM).split()),
                      "autores": [a.findtext("a:name", "", _ATOM) for a in e.findall("a:author", _ATOM)],
                      "data": e.findtext("a:published", "", _ATOM)[:10], "resumo": " ".join(e.findtext("a:summary", "", _ATOM).split())[:1200],
                      "url": link, "pdf": link.replace("/abs/", "/pdf/")})
    return saida


def buscar_openalex(consulta: str, limite: int, get=_get) -> list[dict]:
    q = urllib.parse.urlencode({"search": consulta, "per-page": limite})
    d = json.loads(get(f"https://api.openalex.org/works?{q}"))
    return [{"fonte": "openalex", "id": w["id"], "titulo": w.get("display_name"), "data": w.get("publication_date"),
             "doi": w.get("doi"), "citacoes": w.get("cited_by_count"),
             "autores": [a["author"]["display_name"] for a in w.get("authorships", [])[:8]],
             "url": w.get("doi") or w["id"], "pdf": ((w.get("best_oa_location") or {}).get("pdf_url"))}
            for w in d.get("results", [])]


def buscar_semanticscholar(consulta: str, limite: int, get=_get) -> list[dict]:
    q = urllib.parse.urlencode({"query": consulta, "limit": limite,
                                "fields": "title,year,authors,abstract,externalIds,openAccessPdf,citationCount,url"})
    d = json.loads(get(f"https://api.semanticscholar.org/graph/v1/paper/search?{q}"))
    return [{"fonte": "semanticscholar", "id": p["paperId"], "titulo": p.get("title"), "data": p.get("year"),
             "autores": [a.get("name") for a in p.get("authors", [])[:8]], "resumo": (p.get("abstract") or "")[:1200],
             "citacoes": p.get("citationCount"), "doi": (p.get("externalIds") or {}).get("DOI"),
             "url": p.get("url"), "pdf": (p.get("openAccessPdf") or {}).get("url")} for p in d.get("data", [])]


def buscar_zenodo(consulta: str, limite: int, get=_get) -> list[dict]:
    q = urllib.parse.urlencode({"q": consulta, "size": limite, "sort": "bestmatch"})
    d = json.loads(get(f"https://zenodo.org/api/records?{q}"))
    return [{"fonte": "zenodo", "id": str(h["id"]), "titulo": h["metadata"].get("title"), "data": h["metadata"].get("publication_date"),
             "doi": h.get("doi"), "autores": [c.get("name") for c in h["metadata"].get("creators", [])[:8]],
             "url": h["links"].get("self_html"), "pdf": next((f["links"]["self"] for f in h.get("files", [])
                                                              if f.get("key", "").lower().endswith(".pdf")), None)}
            for h in d.get("hits", {}).get("hits", [])]


BUSCADORES: dict[str, Buscador] = {"arxiv": buscar_arxiv, "openalex": buscar_openalex,
                                   "semanticscholar": buscar_semanticscholar, "zenodo": buscar_zenodo}


def _ano(r: dict) -> int:
    d = str(r.get("data") or "")
    return int(d[:4]) if d[:4].isdigit() else 0


def _pos(resultados: list[dict], desde: int, ordem: str, limite: int) -> list[dict]:
    """Corte por ano e ordenação por data, depois da fonte (o cache guarda o bruto, então o mesmo cache serve a todos)."""
    saida = [r for r in resultados if not desde or _ano(r) >= desde]
    if ordem == "data":
        saida = sorted(saida, key=lambda r: str(r.get("data") or ""), reverse=True)
    return saida[:limite]


def host_permitido(url: str) -> bool:
    p = urllib.parse.urlparse(url)
    return p.scheme == "https" and (p.hostname or "") in HOSTS_PDF


def registrar(ctx, buscadores: dict[str, Buscador] | None = None, baixar: Callable[[str], bytes] = _get) -> None:
    tool, lit = ctx.tool, ctx.literatura
    fontes = buscadores or BUSCADORES

    @tool
    def papers_buscar(consulta: str, fonte: str = "arxiv", limite: int = 10, desde: int = 0, ordem: str = "relevancia") -> dict:
        """Busca papers. fonte: arxiv, openalex, semanticscholar ou zenodo. Devolve título, autores, data,
        link e (quando aberto) o PDF. A mesma busca repetida volta do cache do bucket.
        `desde`: ano mínimo (ex.: 2025) — a fonte não filtra, então buscamos até 3× `limite` e cortamos aqui.
        `ordem`: "relevancia" (padrão) ou "data" (mais novos primeiro, entre os que a fonte devolveu)."""
        if fonte not in fontes:
            return {"ok": False, "erro": f"fonte inválida; use uma de: {', '.join(FONTES)}"}
        if ordem not in ("relevancia", "data"):
            return {"ok": False, "erro": 'ordem inválida; use "relevancia" ou "data"'}
        limite = max(1, min(limite, 50))
        busca = min(50, limite * 3) if desde else limite           # sobra margem para o corte por ano
        chave = hashlib.sha256(f"{fonte}|{busca}|{consulta.strip().lower()}".encode()).hexdigest()[:20]
        nome = f"buscas/{fonte}/{chave}.json"
        em_cache = lit.ler(nome)
        if em_cache:
            return {"ok": True, "cache": True, "fonte": fonte,
                    "resultados": _pos(json.loads(em_cache)["resultados"], desde, ordem, limite)}
        try:
            resultados = fontes[fonte](consulta, busca)
        except Exception as e:  # noqa: BLE001 - fonte fora do ar é resposta, não queda do servidor
            return {"ok": False, "erro": f"{fonte} não respondeu ({type(e).__name__}); tente outra fonte"}
        lit.por(nome, json.dumps({"consulta": consulta, "fonte": fonte, "resultados": resultados},
                                 ensure_ascii=False).encode(), "application/json", publico=False)
        return {"ok": True, "cache": False, "fonte": fonte, "resultados": _pos(resultados, desde, ordem, limite)}

    @tool
    def paper_guardar(url_pdf: str, titulo: str, doi: str = "", confirmar: bool = False) -> dict:
        """Baixa um PDF aberto para a biblioteca (`pdf/<sha>.pdf` + `meta/<sha>.json`) para todos usarem.
        Só hosts: arxiv.org, zenodo.org, biorxiv, openreview, hal.science, eprint.iacr.org. Máximo 30 MB.
        Sem confirmar=true só confere e diz o que faria."""
        if not host_permitido(url_pdf):
            return {"ok": False, "erro": f"host não permitido; use https em: {', '.join(HOSTS_PDF)}"}
        if not titulo.strip():
            return {"ok": False, "erro": "titulo é obrigatório"}
        if not confirmar:
            return {"ok": True, "seco": True, "faria": f"baixar {url_pdf} e guardar como '{titulo.strip()}'"}
        try:
            dados = baixar(url_pdf)
        except Exception as e:  # noqa: BLE001
            return {"ok": False, "erro": f"download falhou ({type(e).__name__})"}
        if len(dados) > PDF_MAX:
            return {"ok": False, "erro": "PDF passa de 30 MB"}
        if not dados.startswith(b"%PDF"):
            return {"ok": False, "erro": "o arquivo baixado não é PDF"}
        sha = hashlib.sha256(dados).hexdigest()
        if lit.ler(f"meta/{sha}.json"):
            return {"ok": True, "ja_existia": True, "sha256": sha}
        lit.por(f"pdf/{sha}.pdf", dados, "application/pdf", publico=False)
        meta = {"sha256": sha, "titulo": titulo.strip(), "doi": doi.strip(), "origem": url_pdf, "por": ctx.quem(), "bytes": len(dados)}
        lit.por(f"meta/{sha}.json", json.dumps(meta, ensure_ascii=False).encode(), "application/json", publico=False)
        return {"ok": True, "ja_existia": False, "sha256": sha, "bytes": len(dados)}

    @tool
    def biblioteca_buscar(texto: str = "", limite: int = 30) -> dict:
        """Procura na biblioteca do bucket (título, DOI ou origem contém o texto). Sem texto, lista as mais recentes."""
        achados = []
        for nome in lit.listar("meta/"):
            m = json.loads(lit.ler(nome))
            if not texto or texto.lower() in " ".join(str(m.get(k, "")) for k in ("titulo", "doi", "origem")).lower():
                achados.append(m)
        return {"ok": True, "total": len(achados), "itens": achados[: max(1, min(limite, 200))]}
