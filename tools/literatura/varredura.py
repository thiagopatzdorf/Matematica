#!/usr/bin/env python3
"""Varredura reprodutível de literatura sobre códigos de cobertura.

Etapas (cada uma idempotente, com cache em disco; rodar de novo só busca o que falta):

  sementes   resolve DOIs, ids arXiv e títulos-chave no OpenAlex
  buscas     consultas no OpenAlex, arXiv e zbMATH Open
  expandir   citações (quem a obra cita e quem a cita), 1-2 níveis, com corte por relevância
  arxivmeta  filtra o dump público de metadados do arXiv (Kaggle, gs://arxiv-dataset) por streaming
  tabelas    espelha as tabelas do Kéri (site + Wayback Machine) e outras tabelas públicas
  baixar     baixa PDFs de acesso aberto (arXiv, links OA do OpenAlex)
  extrair    texto dos PDFs (pdftotext se houver; senão pypdf)
  mencoes    procura as células-alvo nos textos (e nas resenhas do zbMATH)
  subir      envia tudo ao bucket GCS (JSON API, token em memória)
  tudo       todas as etapas acima, nesta ordem

Diretório de dados: $LIT_DIR (padrão: ./literatura-dados). Nada aqui conhece caminho
de máquina; o token do GCP vem de `gcp_credencial.token()` cujo diretório é
$GCP_CREDENCIAL_DIR (o `apps/factory/bin` da Factory).
"""
from __future__ import annotations

import argparse
import datetime as dt
import difflib
import gzip
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

AQUI = Path(__file__).resolve().parent
SEMENTES = AQUI / "sementes.json"
MAILTO = os.environ.get("LIT_MAILTO", "noreply@factory.mybagcenter.com")
UA = f"matematica-literatura/1.0 (mailto:{MAILTO})"
BUCKET = os.environ.get("LIT_BUCKET", "factory-literatura-matematica")
HOJE = dt.date.today().isoformat()

# Intervalos mínimos entre chamadas por host: o arXiv pede 1 req / 3 s; os outros
# são educados por regra da casa (polite pool do OpenAlex aguenta 10/s, usamos ~5/s).
INTERVALO = {"export.arxiv.org": 3.1, "arxiv.org": 3.1, "api.openalex.org": 0.2,
             "api.zbmath.org": 1.0, "web.archive.org": 1.5, "api.crossref.org": 0.25,
             "api.opencitations.net": 0.5, "api.unpaywall.org": 0.2}
_ultimo: dict[str, float] = {}
# O OpenAlex passou a cobrar por orçamento diário (US$ 0,10/dia por IP sem chave;
# busca custa 10 créditos). Medido em 2026-10-03: ~100 buscas esgotam o dia e tudo
# passa a devolver 429 até a meia-noite UTC. Ao primeiro 429 do OpenAlex a rodada
# para de chamá-lo e usa Crossref/OpenCitations/Unpaywall no lugar.
SEM_OPENALEX = {"esgotado": False}
OPENALEX_KEY = os.environ.get("OPENALEX_API_KEY", "")


# ---------------------------------------------------------------- infraestrutura
def dados() -> Path:
    d = Path(os.environ.get("LIT_DIR", "literatura-dados")).resolve()
    for sub in ("meta", "pdf", "txt", "tabelas", "cache", f"buscas/{HOJE}", "relatorios"):
        (d / sub).mkdir(parents=True, exist_ok=True)
    return d


def log(msg: str) -> None:
    linha = f"{dt.datetime.now().isoformat(timespec='seconds')} {msg}"
    print(linha, flush=True)
    with open(dados() / "buscas" / HOJE / "log.txt", "a", encoding="utf-8") as f:
        f.write(linha + "\n")


_trava = threading.Lock()


def _espera(url: str) -> None:
    """Reserva o próximo horário livre do host (seguro entre threads) e dorme até ele."""
    host = urllib.parse.urlparse(url).netloc
    dt_min = INTERVALO.get(host, 0.5)
    with _trava:
        agora = time.time()
        vez = max(agora, _ultimo.get(host, 0) + dt_min)
        _ultimo[host] = vez
    if vez > agora:
        time.sleep(vez - agora)


def baixar_bytes(url: str, *, tentativas: int = 3, tempo: int = 60, limite: int = 60_000_000) -> tuple[int, bytes]:
    """GET com espera por host e retentativa em 429/5xx. Devolve (status, corpo)."""
    for i in range(tentativas):
        _espera(url)
        req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
        try:
            with urllib.request.urlopen(req, timeout=tempo) as r:
                return r.status, r.read(limite)
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 504) and i + 1 < tentativas:
                time.sleep(5 * (i + 1))
                continue
            return e.code, b""
        except Exception as e:  # noqa: BLE001 - rede: registra e segue
            if i + 1 < tentativas:
                time.sleep(3 * (i + 1))
                continue
            log(f"erro de rede {url[:120]}: {type(e).__name__}")
            return 0, b""
    return 0, b""


def json_cache(url: str) -> dict | None:
    """GET JSON com cache em disco (chave = sha1 da URL). É o que torna o script reexecutável."""
    chave = hashlib.sha1(url.encode()).hexdigest()
    arq = dados() / "cache" / f"{chave}.json.gz"
    if arq.exists():
        with gzip.open(arq, "rt", encoding="utf-8") as f:
            return json.load(f)
    openalex = "api.openalex.org" in url
    if openalex and SEM_OPENALEX["esgotado"]:
        return None
    pedido = url + (f"&api_key={OPENALEX_KEY}" if openalex and OPENALEX_KEY else "")
    st, corpo = baixar_bytes(pedido, tentativas=1 if openalex else 3)
    if st != 200:
        if openalex and st == 429:
            SEM_OPENALEX["esgotado"] = True
            log("OpenAlex: orçamento diário esgotado (429); seguindo sem OpenAlex nesta rodada")
        log(f"HTTP {st} {url[:160]}")
        return None
    try:
        obj = json.loads(corpo)
    except ValueError:
        return None
    with gzip.open(arq, "wt", encoding="utf-8") as f:
        json.dump(obj, f)
    return obj


def texto_cache(url: str) -> str | None:
    chave = hashlib.sha1(url.encode()).hexdigest()
    arq = dados() / "cache" / f"{chave}.txt.gz"
    if arq.exists():
        with gzip.open(arq, "rt", encoding="utf-8") as f:
            return f.read()
    st, corpo = baixar_bytes(url)
    if st != 200:
        log(f"HTTP {st} {url[:160]}")
        return None
    t = corpo.decode("utf-8", "replace")
    with gzip.open(arq, "wt", encoding="utf-8") as f:
        f.write(t)
    return t


def cfg() -> dict:
    return json.loads(SEMENTES.read_text(encoding="utf-8"))


# ---------------------------------------------------------------- base de obras
class Base:
    """meta/works.jsonl: um registro por obra, deduplicado por DOI, arXiv e OpenAlex."""

    def __init__(self) -> None:
        self.arq = dados() / "meta" / "works.jsonl"
        self.obras: dict[str, dict] = {}
        self.por_doi: dict[str, str] = {}
        self.por_arxiv: dict[str, str] = {}
        self.por_oa: dict[str, str] = {}
        if self.arq.exists():
            for linha in self.arq.read_text(encoding="utf-8").splitlines():
                if linha.strip():
                    self._indexa(json.loads(linha))

    def _indexa(self, w: dict) -> None:
        self.obras[w["id"]] = w
        if w.get("doi"):
            self.por_doi[w["doi"]] = w["id"]
        if w.get("arxiv"):
            self.por_arxiv[w["arxiv"]] = w["id"]
        if w.get("openalex"):
            self.por_oa[w["openalex"]] = w["id"]

    def acha(self, w: dict) -> str | None:
        return ((w.get("doi") and self.por_doi.get(w["doi"]))
                or (w.get("arxiv") and self.por_arxiv.get(w["arxiv"]))
                or (w.get("openalex") and self.por_oa.get(w["openalex"])) or None)

    def poe(self, w: dict, motivo: str) -> dict:
        """Insere ou funde. Campos vazios do registro antigo são preenchidos; motivos acumulam."""
        velho_id = self.acha(w)
        if velho_id:
            v = self.obras[velho_id]
            for k, val in w.items():
                if k in ("motivos", "fontes", "id"):
                    continue
                if val and not v.get(k):
                    v[k] = val
            v["fontes"] = sorted(set(v.get("fontes", [])) | set(w.get("fontes", [])))
            if motivo not in v.setdefault("motivos", []):
                v["motivos"].append(motivo)
            v["score"] = max(v.get("score", 0), w.get("score", 0))
            self._indexa(v)
            return v
        w["motivos"] = [motivo]
        self._indexa(w)
        return w

    def salva(self) -> None:
        tmp = self.arq.with_suffix(".tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            for w in sorted(self.obras.values(), key=lambda x: (-x.get("score", 0), x["id"])):
                f.write(json.dumps(w, ensure_ascii=False) + "\n")
        tmp.replace(self.arq)


def norm_doi(d: str | None) -> str | None:
    if not d:
        return None
    d = d.strip().lower()
    d = re.sub(r"^https?://(dx\.)?doi\.org/", "", d)
    return d or None


def norm_arxiv(a: str | None) -> str | None:
    if not a:
        return None
    a = a.strip()
    a = re.sub(r"^https?://arxiv\.org/(abs|pdf)/", "", a)
    a = re.sub(r"^arxiv:", "", a, flags=re.I)
    a = re.sub(r"v\d+$", "", a.replace(".pdf", ""))
    return a or None


def score(texto: str) -> int:
    t = (texto or "").lower()
    return sum(p for k, p in cfg()["palavras_relevancia"].items() if k in t)


def id_seguro(w: dict) -> str:
    """Nome de arquivo estável para pdf/<id>.pdf e txt/<id>.txt."""
    return re.sub(r"[^A-Za-z0-9._-]", "_", w["id"])


# ---------------------------------------------------------------- OpenAlex
OA = "https://api.openalex.org"
OA_SEL = ("id,doi,title,display_name,publication_year,authorships,primary_location,best_oa_location,"
          "open_access,locations,ids,cited_by_count,referenced_works,abstract_inverted_index,type")


def oa_url(caminho: str, **params) -> str:
    params.setdefault("mailto", MAILTO)
    return f"{OA}{caminho}?{urllib.parse.urlencode(params)}"


def resumo_oa(inv: dict | None) -> str:
    if not inv:
        return ""
    pos = {}
    for palavra, ps in inv.items():
        for p in ps:
            pos[p] = palavra
    return " ".join(pos[i] for i in sorted(pos))


def de_openalex(o: dict, fonte: str) -> dict:
    ids = o.get("ids") or {}
    arx = None
    for loc in o.get("locations") or []:
        src = ((loc or {}).get("source") or {}).get("display_name") or ""
        lp = (loc or {}).get("landing_page_url") or ""
        if "arxiv" in src.lower() or "arxiv.org" in lp:
            arx = norm_arxiv(lp.split("arxiv.org/abs/")[-1]) if "arxiv.org/abs/" in lp else arx
    doi = norm_doi(o.get("doi"))
    if not arx and doi and doi.startswith("10.48550/arxiv."):
        arx = doi.split("arxiv.")[-1]
    pdfs = []
    best = o.get("best_oa_location") or {}
    if best.get("pdf_url"):
        pdfs.append(best["pdf_url"])
    for loc in o.get("locations") or []:
        if loc and loc.get("pdf_url") and loc["pdf_url"] not in pdfs:
            pdfs.append(loc["pdf_url"])
    if (o.get("open_access") or {}).get("oa_url") and o["open_access"]["oa_url"] not in pdfs:
        pdfs.append(o["open_access"]["oa_url"])
    titulo = o.get("title") or o.get("display_name") or ""
    resumo = resumo_oa(o.get("abstract_inverted_index"))
    venue = ((o.get("primary_location") or {}).get("source") or {}).get("display_name")
    oaid = (o.get("id") or "").rsplit("/", 1)[-1] or None
    return {
        "id": oaid or (f"arxiv_{arx}" if arx else f"doi_{doi}"),
        "openalex": oaid, "doi": doi, "arxiv": arx, "zbmath": None,
        "titulo": titulo, "autores": [a.get("author", {}).get("display_name") for a in o.get("authorships") or []],
        "ano": o.get("publication_year"), "venue": venue, "tipo": o.get("type"),
        "citado_por": o.get("cited_by_count"), "oa_url": pdfs[0] if pdfs else None, "pdf_candidatos": pdfs,
        "is_oa": bool((o.get("open_access") or {}).get("is_oa")),
        "referencias": [r.rsplit("/", 1)[-1] for r in o.get("referenced_works") or []],
        "resumo": resumo[:3000], "fontes": [fonte], "score": score(titulo + " " + resumo),
    }


def oa_obra(chave: str) -> dict | None:
    return json_cache(oa_url(f"/works/{urllib.parse.quote(chave, safe=':/')}", select=OA_SEL))


def oa_pesquisa(params: dict, paginas: int) -> list[dict]:
    """Paginação por cursor (o OpenAlex limita page*per_page a 10 000)."""
    saida, cursor = [], "*"
    for _ in range(paginas):
        r = json_cache(oa_url("/works", **params, select=OA_SEL, cursor=cursor, **{"per-page": 200}))
        if not r:
            break
        saida += r.get("results") or []
        cursor = (r.get("meta") or {}).get("next_cursor")
        if not cursor or not r.get("results"):
            break
    return saida


# ---------------------------------------------------------------- Crossref / OpenCitations / Unpaywall
CR = "https://api.crossref.org"


def de_crossref(it: dict, fonte: str = "crossref") -> dict:
    doi = norm_doi(it.get("DOI"))
    titulo = " ".join(" ".join(it.get("title") or [""]).split())
    resumo = re.sub(r"<[^>]+>", " ", it.get("abstract") or "")
    resumo = " ".join(resumo.split())
    ano = None
    for k in ("published-print", "published-online", "issued", "created"):
        partes = ((it.get(k) or {}).get("date-parts") or [[None]])[0]
        if partes and partes[0]:
            ano = partes[0]
            break
    pdfs = [ln["URL"] for ln in it.get("link") or [] if "pdf" in (ln.get("content-type") or "")
            and (ln.get("intended-application") in ("text-mining", "similarity-checking", None))]
    arx = doi.split("arxiv.")[-1] if doi and doi.startswith("10.48550/arxiv.") else None
    return {
        "id": f"arxiv_{arx}" if arx else f"doi_{doi}", "openalex": None, "doi": doi, "arxiv": arx, "zbmath": None,
        "titulo": titulo, "autores": [" ".join(x for x in (a.get("given"), a.get("family")) if x) for a in it.get("author") or []],
        "ano": ano, "venue": " ".join(it.get("container-title") or []) or None, "tipo": it.get("type"),
        "citado_por": it.get("is-referenced-by-count"), "oa_url": None, "pdf_candidatos": pdfs[:2], "is_oa": False,
        "referencias": [], "referencias_doi": [norm_doi(r.get("DOI")) for r in it.get("reference") or [] if r.get("DOI")],
        "resumo": resumo[:3000], "fontes": [fonte], "score": score(titulo + " " + resumo),
    }


def cr_url(caminho: str, **params) -> str:
    params.setdefault("mailto", MAILTO)
    return f"{CR}{caminho}?{urllib.parse.urlencode(params)}"


def cr_pesquisa(q: str, maximo: int = 1000) -> list[dict]:
    # offset, não cursor: com cursor o Crossref ignora a ordem de relevância e devolve
    # lixo (medido em 2026-10-03: "saturating sets ..." → ressonância magnética).
    saida = []
    for offset in range(0, maximo, 200):
        r = json_cache(cr_url("/works", **{"query.bibliographic": q}, rows=200, offset=offset, sort="relevance",
                              select="DOI,title,author,issued,container-title,type,abstract,is-referenced-by-count,link"))
        itens = ((r or {}).get("message") or {}).get("items") or []
        saida += itens
        if len(itens) < 200:
            break
    return saida


def cr_por_dois(dois: list[str]) -> list[dict]:
    """Metadados de muitos DOIs em lotes de 40 (filtro doi:A,doi:B,... é um OU no Crossref)."""
    saida = []
    for i in range(0, len(dois), 40):
        lote = ",".join(f"doi:{d}" for d in dois[i:i + 40])
        r = json_cache(cr_url("/works", filter=lote, rows=40,
                              select="DOI,title,author,issued,container-title,type,abstract,is-referenced-by-count,link"))
        saida += ((r or {}).get("message") or {}).get("items") or []
    return saida


def opencitations(doi: str, tipo: str) -> list[str]:
    """tipo = 'references' (o que a obra cita) ou 'citations' (quem cita a obra). Devolve DOIs."""
    r = json_cache(f"https://api.opencitations.net/index/v2/{tipo}/doi:{urllib.parse.quote(doi, safe='/')}")
    campo = "cited" if tipo == "references" else "citing"
    saida = []
    for x in r or []:
        for tok in (x.get(campo) or "").split():
            if tok.startswith("doi:"):
                saida.append(norm_doi(tok[4:]))
    return [d for d in saida if d]


def unpaywall_pdf(doi: str) -> list[str]:
    r = json_cache(f"https://api.unpaywall.org/v2/{urllib.parse.quote(doi, safe='/')}?email={MAILTO}")
    if not r:
        return []
    urls = []
    for loc in [r.get("best_oa_location")] + (r.get("oa_locations") or []):
        if loc and loc.get("url_for_pdf") and loc["url_for_pdf"] not in urls:
            urls.append(loc["url_for_pdf"])
    return urls


# ---------------------------------------------------------------- arXiv
ATOM = {"a": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}


def arxiv_consulta(q: str, inicio: int = 0, n: int = 200) -> list[dict]:
    params = ({"id_list": q[len("id_list:"):]} if q.startswith("id_list:")
              else {"search_query": q, "start": inicio, "max_results": n, "sortBy": "relevance"})
    url = "http://export.arxiv.org/api/query?" + urllib.parse.urlencode(params)
    t = texto_cache(url)
    if not t:
        return []
    try:
        raiz = ET.fromstring(t)
    except ET.ParseError:
        return []
    saida = []
    for e in raiz.findall("a:entry", ATOM):
        aid = norm_arxiv((e.findtext("a:id", "", ATOM) or "").split("/abs/")[-1])
        titulo = " ".join((e.findtext("a:title", "", ATOM) or "").split())
        resumo = " ".join((e.findtext("a:summary", "", ATOM) or "").split())
        doi = norm_doi(e.findtext("arxiv:doi", None, ATOM))
        ano = (e.findtext("a:published", "", ATOM) or "")[:4]
        saida.append({
            "id": f"arxiv_{aid}", "openalex": None, "doi": doi, "arxiv": aid, "zbmath": None,
            "titulo": titulo, "autores": [a.findtext("a:name", "", ATOM) for a in e.findall("a:author", ATOM)],
            "ano": int(ano) if ano.isdigit() else None, "venue": "arXiv", "tipo": "preprint",
            "oa_url": f"https://arxiv.org/pdf/{aid}", "pdf_candidatos": [f"https://arxiv.org/pdf/{aid}"],
            "is_oa": True, "referencias": [], "resumo": resumo[:3000], "fontes": ["arxiv"],
            "score": score(titulo + " " + resumo),
        })
    return saida


# ---------------------------------------------------------------- zbMATH Open
def zb_consulta(q: str, paginas: int) -> list[dict]:
    saida = []
    for p in range(paginas):
        url = "https://api.zbmath.org/v1/document/_search?" + urllib.parse.urlencode(
            {"search_string": q, "page": p, "results_per_page": 100})
        r = json_cache(url)
        res = (r or {}).get("result") or []
        for z in res:
            tit = z.get("title") or {}
            titulo = tit.get("title") if isinstance(tit, dict) else str(tit)
            doi = arx = None
            for ln in z.get("links") or []:
                if ln.get("type") == "doi":
                    doi = norm_doi(ln.get("identifier"))
                if ln.get("type") == "arxiv":
                    arx = norm_arxiv(ln.get("identifier"))
            resenha = " ".join(c.get("text") or "" for c in z.get("editorial_contributions") or [])
            src = z.get("source") or {}
            serie = (src.get("series") or [{}])[0] if src.get("series") else {}
            ano = None
            for s in src.get("series") or []:
                ano = ano or s.get("year")
            ano = ano or z.get("year")
            saida.append({
                "id": f"zb_{z.get('identifier') or z.get('id')}", "openalex": None, "doi": doi, "arxiv": arx,
                "zbmath": z.get("identifier"), "titulo": titulo or "",
                "autores": [a.get("name") for a in (z.get("contributors") or {}).get("authors") or []],
                "ano": int(ano) if str(ano or "").isdigit() else None,
                "venue": serie.get("short_title") or serie.get("title"), "tipo": (z.get("document_type") or {}).get("description"),
                "msc": [m.get("code") for m in z.get("msc") or []],
                "oa_url": f"https://arxiv.org/pdf/{arx}" if arx else None,
                "pdf_candidatos": [f"https://arxiv.org/pdf/{arx}"] if arx else [],
                "is_oa": bool(arx), "referencias": [], "resenha_zbmath": resenha[:6000], "resumo": "",
                "fontes": ["zbmath"], "score": score((titulo or "") + " " + resenha) + (3 if "94B75" in str(z.get("msc")) else 0),
            })
        total = ((r or {}).get("status") or {}).get("nr_total_results") or 0
        if len(res) < 100 or (p + 1) * 100 >= total:
            break
    return saida


# ---------------------------------------------------------------- etapas
def etapa_sementes(b: Base) -> None:
    c = cfg()
    falhas = []
    for d in c["dois"]:
        o = oa_obra(f"doi:{d}")
        (b.poe(de_openalex(o, "openalex"), "semente:doi") if o else falhas.append(f"doi {d}"))
    for a in c["arxiv"]:
        ws = arxiv_consulta(f"id_list:{a}") or []
        o = oa_obra(f"doi:10.48550/arxiv.{a}")
        if o:
            w = de_openalex(o, "openalex")
            w["arxiv"] = a
            b.poe(w, "semente:arxiv")
        for w in ws:
            b.poe(w, "semente:arxiv")
        if not ws and not o:
            falhas.append(f"arxiv {a}")
    for t in c["titulos"]:
        res = json_cache(oa_url("/works", search=t, select=OA_SEL, **{"per-page": 5})) or {}
        melhor, r_max = None, 0.0
        for o in res.get("results") or []:
            r = difflib.SequenceMatcher(None, t.lower(), (o.get("title") or "").lower()).ratio()
            if r > r_max:
                melhor, r_max = o, r
        w = de_openalex(melhor, "openalex") if melhor and r_max >= 0.6 else None
        if w is None:
            # Sem OpenAlex (orçamento) ou sem casamento: tenta o Crossref pelo título.
            r = json_cache(cr_url("/works", **{"query.bibliographic": t}, rows=5,
                                  select="DOI,title,author,issued,container-title,type,abstract,is-referenced-by-count,link")) or {}
            for it in (r.get("message") or {}).get("items") or []:
                rr = difflib.SequenceMatcher(None, t.lower(), " ".join(it.get("title") or [""]).lower()).ratio()
                if rr > r_max:
                    w, r_max = de_crossref(it), rr
            if r_max < 0.6:
                w = None
        if w is not None:
            w["score"] = max(w["score"], c["limiar_expansao"])  # semente sempre expande
            b.poe(w, f"semente:titulo ({r_max:.2f})")
        else:
            falhas.append(f"titulo {t!r} (melhor {r_max:.2f})")
    b.salva()
    (dados() / "buscas" / HOJE / "sementes_nao_resolvidas.txt").write_text("\n".join(falhas) + "\n", encoding="utf-8")
    log(f"sementes: {len(b.obras)} obras na base; {len(falhas)} sementes não resolvidas")


def etapa_buscas(b: Base) -> None:
    c = cfg()
    contagem = {}
    for q in c["consultas_openalex"]:
        res = oa_pesquisa({"search": q}, c["max_paginas_por_consulta"])
        aceitas = 0
        for o in res:
            w = de_openalex(o, "openalex")
            if w["score"] >= c["limiar_inclusao"]:
                b.poe(w, f"busca:openalex:{q}")
                aceitas += 1
        contagem[f"openalex:{q}"] = {"retornadas": len(res), "aceitas": aceitas}
        log(f"openalex {q!r}: {len(res)} → {aceitas}")
    for q in c["consultas_openalex"]:
        # Crossref sempre (é grátis e cobre periódicos que o arXiv não tem); o mesmo
        # texto de consulta do OpenAlex, com o mesmo corte de relevância.
        res = cr_pesquisa(q, 600)
        aceitas = 0
        for it in res:
            w = de_crossref(it)
            if w["score"] >= c["limiar_inclusao"]:
                b.poe(w, f"busca:crossref:{q}")
                aceitas += 1
        contagem[f"crossref:{q}"] = {"retornadas": len(res), "aceitas": aceitas}
        log(f"crossref {q!r}: {len(res)} → {aceitas}")
    b.salva()
    for q in c["consultas_arxiv"]:
        res = []
        for ini in range(0, 1000, 200):
            lote = arxiv_consulta(q, ini, 200)
            res += lote
            if len(lote) < 200:
                break
        aceitas = 0
        for w in res:
            if w["score"] >= c["limiar_inclusao"]:
                b.poe(w, f"busca:arxiv:{q}")
                aceitas += 1
        contagem[f"arxiv:{q}"] = {"retornadas": len(res), "aceitas": aceitas}
        log(f"arxiv {q!r}: {len(res)} → {aceitas}")
    for q in c["consultas_zbmath"]:
        res = zb_consulta(q, 30 if q.startswith("cc:") else 5)
        aceitas = 0
        for w in res:
            # MSC 94B75 é "covering radius" por definição: entra sem filtro de palavra.
            if w["score"] >= c["limiar_inclusao"] or q.startswith("cc:"):
                b.poe(w, f"busca:zbmath:{q}")
                aceitas += 1
        contagem[f"zbmath:{q}"] = {"retornadas": len(res), "aceitas": aceitas}
        log(f"zbmath {q!r}: {len(res)} → {aceitas}")
    b.salva()
    (dados() / "buscas" / HOJE / "consultas.json").write_text(json.dumps(contagem, ensure_ascii=False, indent=1), encoding="utf-8")


def expandir_por_doi(b: Base, niveis: int) -> None:
    """Expansão sem OpenAlex: OpenCitations dá as arestas (DOI→DOI), Crossref dá título e
    resumo para o corte de relevância."""
    c = cfg()
    feitos_arq = dados() / "meta" / "expandidas_doi.json"
    feitos = set(json.loads(feitos_arq.read_text())) if feitos_arq.exists() else set()
    for nivel in range(1, niveis + 1):
        fila = [w for w in list(b.obras.values())
                if w.get("doi") and w["doi"] not in feitos and w.get("score", 0) >= c["limiar_expansao"]
                and not w["doi"].startswith("10.48550/")]
        log(f"expandir (OpenCitations) nível {nivel}: {len(fila)} obras-semente")
        novos = 0
        for k, w in enumerate(fila):
            vizinhos = {}
            for d in opencitations(w["doi"], "references") + list(w.get("referencias_doi") or []):
                vizinhos.setdefault(d, f"citado_por:{w['doi']}")
            cit = opencitations(w["doi"], "citations")
            for d in cit[: c["max_citantes_por_obra"]]:
                vizinhos.setdefault(d, f"cita:{w['doi']}")
            desconhecidos = [d for d in vizinhos if d not in b.por_doi]
            for it in cr_por_dois(desconhecidos):
                x = de_crossref(it, "crossref")
                if x["score"] >= c["limiar_inclusao"]:
                    b.poe(x, vizinhos.get(x["doi"], "vizinho"))
                    novos += 1
            for d in vizinhos:
                if d in b.por_doi:
                    v = b.obras[b.por_doi[d]]
                    if vizinhos[d] not in v.setdefault("motivos", []) and len(v["motivos"]) < 30:
                        v["motivos"].append(vizinhos[d])
            feitos.add(w["doi"])
            if k % 25 == 24:
                b.salva()
                feitos_arq.write_text(json.dumps(sorted(feitos)))
                log(f"  {k + 1}/{len(fila)}; {novos} novas; base {len(b.obras)}")
        b.salva()
        feitos_arq.write_text(json.dumps(sorted(feitos)))
        log(f"expandir (OpenCitations) nível {nivel}: {novos} obras novas; base com {len(b.obras)}")


def etapa_expandir(b: Base, niveis: int = 2) -> None:
    expandir_por_doi(b, niveis)
    if SEM_OPENALEX["esgotado"]:
        log("expandir: OpenAlex sem orçamento; ficou só a expansão por OpenCitations")
        return
    c = cfg()
    feitos_arq = dados() / "meta" / "expandidas.json"
    feitos = set(json.loads(feitos_arq.read_text())) if feitos_arq.exists() else set()
    for nivel in range(1, niveis + 1):
        # Nível 1 expande a partir das obras muito relevantes; nível 2 só a partir das
        # que entraram no nível 1 e também são relevantes: o corte segura a explosão.
        fila = [w for w in list(b.obras.values())
                if w.get("openalex") and w["openalex"] not in feitos and w.get("score", 0) >= c["limiar_expansao"]]
        log(f"expandir nível {nivel}: {len(fila)} obras-semente")
        novos = 0
        for w in fila:
            oaid = w["openalex"]
            if not w.get("referencias"):
                o = oa_obra(oaid)
                if o:
                    w["referencias"] = [r.rsplit("/", 1)[-1] for r in o.get("referenced_works") or []]
            refs = w.get("referencias") or []
            for i in range(0, len(refs), 50):
                lote = "|".join(refs[i:i + 50])
                r = json_cache(oa_url("/works", filter=f"openalex:{lote}", select=OA_SEL, **{"per-page": 50})) or {}
                for o in r.get("results") or []:
                    x = de_openalex(o, "openalex")
                    if x["score"] >= c["limiar_inclusao"] and not b.acha(x):
                        novos += 1
                    if x["score"] >= c["limiar_inclusao"]:
                        b.poe(x, f"citado_por:{oaid}")
            paginas = max(1, c["max_citantes_por_obra"] // 200)
            for o in oa_pesquisa({"filter": f"cites:{oaid}"}, paginas):
                x = de_openalex(o, "openalex")
                if x["score"] >= c["limiar_inclusao"]:
                    if not b.acha(x):
                        novos += 1
                    b.poe(x, f"cita:{oaid}")
            feitos.add(oaid)
            if len(feitos) % 25 == 0:
                b.salva()
                feitos_arq.write_text(json.dumps(sorted(feitos)))
        b.salva()
        feitos_arq.write_text(json.dumps(sorted(feitos)))
        log(f"expandir nível {nivel}: {novos} obras novas; base com {len(b.obras)}")


RX_ARXIV_META = re.compile(r"covering (code|radius)|football pool|saturating set|covering design|"
                           r"orbital branching|orbitope|isomorph rejection", re.I)


def etapa_arxivmeta(b: Base) -> None:
    """Lê o dump de 4,5 GB do Kaggle em streaming; não grava o dump, só as linhas que casam."""
    saida = dados() / "meta" / "arxiv_meta_filtrado.jsonl"
    if saida.exists() and saida.stat().st_size > 0:
        log("arxivmeta: já filtrado (apague o arquivo para refazer)")
    else:
        url = "https://storage.googleapis.com/arxiv-dataset/metadata-v5/arxiv-metadata-oai.json"
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        n = k = 0
        with urllib.request.urlopen(req, timeout=120) as r, open(saida.with_suffix(".tmp"), "w", encoding="utf-8") as f:
            for linha in r:
                n += 1
                if RX_ARXIV_META.search(linha.decode("utf-8", "replace")):
                    f.write(linha.decode("utf-8", "replace"))
                    k += 1
                if n % 500_000 == 0:
                    log(f"arxivmeta: {n} linhas lidas, {k} casaram")
        saida.with_suffix(".tmp").replace(saida)
        log(f"arxivmeta: {n} linhas, {k} casaram")
    c = cfg()
    aceitas = 0
    for linha in saida.read_text(encoding="utf-8").splitlines():
        m = json.loads(linha)
        titulo = " ".join((m.get("title") or "").split())
        resumo = " ".join((m.get("abstract") or "").split())
        s = score(titulo + " " + resumo)
        if s < c["limiar_inclusao"]:
            continue
        aid = m["id"]
        # metadata-v5 não traz data nem authors_parsed (versions é ['v1', ...]):
        # o ano sai do próprio id novo (AAMM.nnnnn) ou do antigo (arquivo/AAMMnnn).
        mm = re.match(r"(\d{2})(\d{2})\.", aid) or re.match(r"[a-z.-]+/(\d{2})(\d{2})", aid)
        ano = str((2000 if int(mm.group(1)) < 91 else 1900) + int(mm.group(1))) if mm else None
        b.poe({"id": f"arxiv_{aid}", "openalex": None, "doi": norm_doi(m.get("doi")), "arxiv": aid, "zbmath": None,
               "titulo": titulo, "autores": [x.strip() for x in re.split(r",| and ", m.get("authors") or "") if x.strip()],
               "ano": int(ano) if ano and ano.isdigit() else None, "venue": "arXiv", "tipo": "preprint",
               "oa_url": f"https://arxiv.org/pdf/{aid}", "pdf_candidatos": [f"https://arxiv.org/pdf/{aid}"],
               "is_oa": True, "referencias": [], "resumo": resumo[:3000], "categorias": m.get("categories"),
               "fontes": ["arxiv-kaggle"], "score": s}, "arxiv-kaggle:filtro")
        aceitas += 1
    b.salva()
    log(f"arxivmeta: {aceitas} obras aceitas pelo limiar")


KERI_BASE = "https://old.sztaki.hu/~keri/codes/"
TABELAS_EXTRA = {
    "lobstein_bib-a-jour.pdf": "https://www.lri.fr/~lobstein/bib-a-jour.pdf",
    "coldcase_bounds.json": "https://raw.githubusercontent.com/Mapika/coldcase/56a8cce68ec3f6f406c845f5cc3e51711e5b8294/cov/bounds.json",
    "coldcase_final_records.json": "https://raw.githubusercontent.com/Mapika/coldcase/56a8cce68ec3f6f406c845f5cc3e51711e5b8294/cov/results/final_records.json",
    "coldcase_lb_master.json": "https://raw.githubusercontent.com/Mapika/coldcase/56a8cce68ec3f6f406c845f5cc3e51711e5b8294/cov/lb/results/lb_master.json",
    "florath_non_mixed_covering_codes.csv": "https://raw.githubusercontent.com/florath/covering-codes-lean/bbed9a690e6c54f8bba423031d4d516f70d267b9/reference-data/lean/non_mixed_covering_codes.csv",
    "florath_post_keri_non_mixed.csv": "https://raw.githubusercontent.com/florath/covering-codes-lean/bbed9a690e6c54f8bba423031d4d516f70d267b9/reference-data/post-keri/non_mixed_covering_codes.csv",
}


def etapa_tabelas() -> None:
    d = dados() / "tabelas"
    manifesto = []
    # 1) site vivo do Kéri: índice + todos os arquivos listados.
    keri = d / "keri"
    keri.mkdir(exist_ok=True)
    idx = texto_cache(KERI_BASE) or ""
    nomes = sorted(set(re.findall(r'href="([^"?/][^"]*)"', idx)))
    for nome in nomes:
        alvo = keri / nome
        if not alvo.exists():
            st, corpo = baixar_bytes(KERI_BASE + nome)
            if st == 200 and corpo:
                alvo.write_bytes(corpo)
        if alvo.exists():
            manifesto.append({"arquivo": f"keri/{nome}", "url": KERI_BASE + nome,
                              "sha256": hashlib.sha256(alvo.read_bytes()).hexdigest(), "bytes": alvo.stat().st_size})
    (keri / "index_listing.html").write_text(idx, encoding="utf-8")
    # 2) Wayback: versões arquivadas de cada arquivo do Kéri (hosts antigo e novo). Guarda
    #    a cópia mais antiga e a mais nova de cada nome com digest distinto do vivo.
    wb = d / "keri_wayback"
    wb.mkdir(exist_ok=True)
    cdx_todos = []
    for host in ("old.sztaki.hu/~keri/*", "www.sztaki.hu/~keri/*", "sztaki.hu/~keri/*", "www.sztaki.hu/~keri/codes/*"):
        r = json_cache("http://web.archive.org/cdx/search/cdx?" + urllib.parse.urlencode(
            {"url": host, "output": "json", "filter": "statuscode:200", "collapse": "digest", "limit": 5000}))
        if r and len(r) > 1:
            cab = r[0]
            cdx_todos += [dict(zip(cab, x)) for x in r[1:]]
    (wb / "cdx.json").write_text(json.dumps(cdx_todos, indent=0), encoding="utf-8")
    vivos = {m["sha256"] for m in manifesto}
    por_nome: dict[str, list] = {}
    for x in cdx_todos:
        partes = x["original"].split("?")[0].rstrip("/").split("/")
        nome = "_".join(partes[-2:]) if len(partes) > 3 else (partes[-1] or "index")
        if re.search(r"(tables|biblio|survey|normality|gamma|index|codes)", nome, re.I):
            por_nome.setdefault(nome, []).append(x)
    for nome, lst in por_nome.items():
        lst.sort(key=lambda x: x["timestamp"])
        for x in {lst[0]["timestamp"]: lst[0], lst[-1]["timestamp"]: lst[-1]}.values():
            alvo = wb / f"{x['timestamp']}_{re.sub(r'[^A-Za-z0-9._-]', '_', nome)}"
            if not alvo.exists():
                st, corpo = baixar_bytes(f"http://web.archive.org/web/{x['timestamp']}id_/{x['original']}")
                if st == 200 and corpo:
                    alvo.write_bytes(corpo)
            if alvo.exists():
                h = hashlib.sha256(alvo.read_bytes()).hexdigest()
                manifesto.append({"arquivo": f"keri_wayback/{alvo.name}", "url": x["original"], "timestamp": x["timestamp"],
                                  "sha256": h, "bytes": alvo.stat().st_size, "igual_ao_vivo": h in vivos})
    # 3) outras tabelas públicas fixadas por commit.
    for nome, url in TABELAS_EXTRA.items():
        alvo = d / nome
        if not alvo.exists():
            st, corpo = baixar_bytes(url)
            if st == 200 and corpo:
                alvo.write_bytes(corpo)
            else:
                log(f"tabela extra indisponível ({st}): {url}")
        if alvo.exists():
            manifesto.append({"arquivo": nome, "url": url, "sha256": hashlib.sha256(alvo.read_bytes()).hexdigest(),
                              "bytes": alvo.stat().st_size})
    (d / "MANIFESTO.json").write_text(json.dumps(manifesto, ensure_ascii=False, indent=1), encoding="utf-8")
    # 4) texto das tabelas em PDF para o grep.
    for pdf in list(keri.glob("*.pdf")) + list(wb.glob("*.pdf")) + list(d.glob("*.pdf")):
        txt = pdf.with_suffix(".txt")
        if not txt.exists():
            t = extrair_texto(pdf)
            if t:
                txt.write_text(t, encoding="utf-8")
    log(f"tabelas: {len(manifesto)} arquivos no manifesto")


def _baixar_uma(w: dict, alvo: Path) -> dict:
    """Tenta os candidatos de uma obra. Roda em thread: não mexe na Base, só devolve o resultado."""
    cands = list(w.get("pdf_candidatos") or [])
    if w.get("arxiv") and f"https://arxiv.org/pdf/{w['arxiv']}" not in cands:
        cands.insert(0, f"https://arxiv.org/pdf/{w['arxiv']}")
    if w.get("doi") and not w.get("arxiv") and not w.get("unpaywall_visto"):
        for u in unpaywall_pdf(w["doi"]):
            if u not in cands:
                cands.append(u)
    if not cands:
        return {"pdf_status": "sem_oa", "unpaywall_visto": True}
    for u in cands[:4]:
        # Uma tentativa e 30 s: editora que não serve o PDF costuma pendurar a conexão,
        # e com 2 x 90 s a rodada levava horas (medido em 2026-10-03: 3 PDFs em 2 min).
        st, corpo = baixar_bytes(u, tentativas=1, tempo=30)
        if st == 200 and corpo[:5] == b"%PDF-":
            tmp = alvo.with_suffix(".tmp")
            tmp.write_bytes(corpo)
            tmp.replace(alvo)
            return {"pdf_status": "ok", "pdf_url_usada": u, "pdf_sha256": hashlib.sha256(corpo).hexdigest(),
                    "unpaywall_visto": True}
    return {"pdf_status": "falhou", "unpaywall_visto": True, "_candidatos": cands[:4]}


def etapa_baixar(b: Base, limite_gb: float = 6.0, threads: int = 8) -> None:
    from concurrent.futures import ThreadPoolExecutor, as_completed

    pdfdir = dados() / "pdf"
    falhas, fila = [], []
    for w in sorted(b.obras.values(), key=lambda w: -w.get("score", 0)):
        alvo = pdfdir / f"{id_seguro(w)}.pdf"
        if alvo.exists():
            # PDF que chegou por outro caminho (rodada anterior, pré-carga do arXiv):
            # registra em vez de baixar de novo.
            if w.get("pdf_status") != "ok":
                w["pdf_status"] = "ok"
                w["pdf_sha256"] = hashlib.sha256(alvo.read_bytes()).hexdigest()
            continue
        if w.get("pdf_status") in ("sem_oa", "falhou") or w.get("score", 0) < cfg()["limiar_inclusao"]:
            continue
        fila.append((w, alvo))
    usado = sum(p.stat().st_size for p in pdfdir.glob("*.pdf")) / 1e9
    log(f"baixar: {len(fila)} obras na fila; {usado:.2f} GB já no disco")
    feitos = 0
    with ThreadPoolExecutor(threads) as ex:
        futuros = {ex.submit(_baixar_uma, w, alvo): w for w, alvo in fila}
        for fut in as_completed(futuros):
            w = futuros[fut]
            try:
                res = fut.result()
            except Exception as e:  # noqa: BLE001 - uma obra ruim não derruba a rodada
                res = {"pdf_status": "falhou", "_erro": type(e).__name__}
            cands = res.pop("_candidatos", None)
            w.update(res)
            if res["pdf_status"] == "falhou":
                falhas.append({"id": w["id"], "titulo": w.get("titulo"), "candidatos": cands})
            feitos += 1
            if feitos % 50 == 0:
                b.salva()
                log(f"  baixar: {feitos}/{len(fila)}")
                if sum(p.stat().st_size for p in pdfdir.glob("*.pdf")) / 1e9 > limite_gb:
                    log(f"baixar: limite local de {limite_gb} GB atingido; cancelando o resto")
                    for f in futuros:
                        f.cancel()
                    break
    b.salva()
    (dados() / "buscas" / HOJE / "pdf_falhas.json").write_text(json.dumps(falhas, ensure_ascii=False, indent=0), encoding="utf-8")
    log(f"baixar: {len(list(pdfdir.glob('*.pdf')))} PDFs locais; {len(falhas)} falhas nesta rodada")


def extrair_texto(pdf: Path, tempo: int = 120) -> str:
    if shutil.which("pdftotext"):
        try:
            r = subprocess.run(["pdftotext", "-layout", str(pdf), "-"], capture_output=True, timeout=tempo)
            if r.returncode == 0:
                return r.stdout.decode("utf-8", "replace")
        except subprocess.TimeoutExpired:
            return ""
    # Em subprocesso: alguns PDFs travam o parser e o timeout precisa matar. PyMuPDF
    # primeiro (medido em 2026-10-03: pypdf levava ~5 s por PDF, 45 min para 543 PDFs).
    codigos = [
        "import sys,pymupdf\nd=pymupdf.open(sys.argv[1])\nsys.stdout.write('\\f'.join(p.get_text() for p in d))",
        "import sys,pypdf\nr=pypdf.PdfReader(sys.argv[1])\n"
        "sys.stdout.write('\\f'.join((p.extract_text() or '') for p in r.pages))",
    ]
    for codigo in codigos:
        try:
            r = subprocess.run([sys.executable, "-c", codigo, str(pdf)], capture_output=True, timeout=tempo)
        except subprocess.TimeoutExpired:
            continue
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout.decode("utf-8", "replace")
    return ""


def etapa_extrair(b: Base) -> None:
    from concurrent.futures import ThreadPoolExecutor

    def um(pdf: Path) -> None:
        (dados() / "txt" / f"{pdf.stem}.txt").write_text(extrair_texto(pdf), encoding="utf-8")

    fila = [p for p in sorted((dados() / "pdf").glob("*.pdf")) if not (dados() / "txt" / f"{p.stem}.txt").exists()]
    with ThreadPoolExecutor(3) as ex:
        list(ex.map(um, fila))
    n = len(fila)
    # Resenhas do zbMATH também são texto pesquisável (citam cotas com frequência).
    for w in b.obras.values():
        if w.get("resenha_zbmath"):
            arq = dados() / "txt" / f"{id_seguro(w)}.zbmath.txt"
            if not arq.exists():
                arq.write_text(w.get("titulo", "") + "\n\n" + w["resenha_zbmath"], encoding="utf-8")
    vazios = sum(1 for t in (dados() / "txt").glob("*.txt") if t.stat().st_size < 200)
    log(f"extrair: {n} textos novos; {vazios} textos quase vazios (PDF escaneado ou protegido)")


# ---------------------------------------------------------------- menções das células
def padroes_celula(q: int, n: int, R: int) -> list[re.Pattern]:
    """Formas de escrever K_q(n,R) em texto extraído de PDF: K7(9,4), K_7(9,4), K_{7}(9, 4),
    'K 7 (9, 4)' (o pdftotext separa subscritos) e K(9,4) com q=7 dito por perto."""
    sp = r"\s*"
    return [
        re.compile(rf"K{sp}_?{sp}\{{?{sp}{q}{sp}\}}?{sp}\({sp}{n}{sp},{sp}{R}{sp}\)"),
        re.compile(rf"K{sp}\({sp}{n}{sp},{sp}{R}{sp}\)"),  # forma sem q; validar q no contexto
    ]


def procurar_mencoes(texto: str, cel: dict, janela: int = 250) -> list[dict]:
    q, n, R = cel["q"], cel["n"], cel["R"]
    achados = []
    p_full, p_sem_q = padroes_celula(q, n, R)
    for m in p_full.finditer(texto):
        a, z = max(0, m.start() - janela), m.end() + janela
        achados.append({"tipo": "celula", "pos": m.start(), "trecho": " ".join(texto[a:z].split())})
    for m in p_sem_q.finditer(texto):
        a, z = max(0, m.start() - janela), m.end() + janela
        ctx = texto[a:z]
        if re.search(rf"q\s*=\s*{q}\b|{q}-ary|{['', '', 'binary', 'ternary', 'quaternary', 'quinary', 'senary', 'septenary'][q] if q < 8 else 'x'}", ctx, re.I):
            achados.append({"tipo": "celula_sem_q", "pos": m.start(), "trecho": " ".join(ctx.split())})
    for num in cel.get("numeros_alvo") or []:
        for m in re.finditer(rf"(?<![\d.]){num}(?![\d.])", texto):
            a, z = max(0, m.start() - janela), m.end() + janela
            ctx = texto[a:z]
            if re.search(r"cover", ctx, re.I) and re.search(rf"(?<!\d){n}(?!\d)", ctx) and re.search(rf"(?<!\d){R}(?!\d)", ctx):
                achados.append({"tipo": f"numero:{num}", "pos": m.start(), "trecho": " ".join(ctx.split())})
    return achados


def etapa_mencoes(b: Base) -> None:
    c = cfg()
    saida = dados() / "buscas" / HOJE / "mencoes.jsonl"
    resumo = {cel["id"]: {"arquivos": 0, "achados": 0} for cel in c["celulas"]}
    textos = sorted((dados() / "txt").glob("*.txt")) + sorted((dados() / "tabelas").rglob("*.txt"))
    with open(saida, "w", encoding="utf-8") as f:
        for t in textos:
            texto = t.read_text(encoding="utf-8", errors="replace")
            if not texto.strip():
                continue
            wid = t.name.split(".")[0]
            for cel in c["celulas"]:
                ach = procurar_mencoes(texto, cel)
                if ach:
                    resumo[cel["id"]]["arquivos"] += 1
                    resumo[cel["id"]]["achados"] += len(ach)
                    for a in ach:
                        f.write(json.dumps({"celula": cel["id"], "arquivo": str(t.relative_to(dados())), "obra": wid,
                                            "titulo": (b.obras.get(wid) or {}).get("titulo"), **a}, ensure_ascii=False) + "\n")
    (dados() / "buscas" / HOJE / "mencoes_resumo.json").write_text(json.dumps(resumo, indent=1), encoding="utf-8")
    log(f"mencoes: {len(textos)} textos lidos; {json.dumps(resumo)}")


# ---------------------------------------------------------------- bucket
def _token() -> str:
    d = os.environ.get("GCP_CREDENCIAL_DIR")
    if d:
        sys.path.insert(0, d)
    import gcp_credencial  # noqa: WPS433 - só quem sobe ao bucket precisa

    return gcp_credencial.token()


def etapa_subir() -> None:
    raiz = dados()
    estado_arq = raiz / "meta" / ".subidos.json"  # local: nome -> sha256 já enviado
    estado = json.loads(estado_arq.read_text()) if estado_arq.exists() else {}
    tok = _token()
    enviados = pulados = erros = 0
    for p in sorted(raiz.rglob("*")):
        if not p.is_file() or p.name.startswith(".") or "cache" in p.relative_to(raiz).parts or p.suffix == ".tmp":
            continue
        nome = str(p.relative_to(raiz))
        h = hashlib.sha256(p.read_bytes()).hexdigest()
        if estado.get(nome) == h:
            pulados += 1
            continue
        tipo = {".pdf": "application/pdf", ".json": "application/json", ".jsonl": "application/x-ndjson",
                ".md": "text/markdown", ".txt": "text/plain", ".csv": "text/csv", ".html": "text/html",
                ".htm": "text/html", ".ps": "application/postscript"}.get(p.suffix, "application/octet-stream")
        url = (f"https://storage.googleapis.com/upload/storage/v1/b/{BUCKET}/o?uploadType=media&name="
               + urllib.parse.quote(nome, safe=""))
        req = urllib.request.Request(url, data=p.read_bytes(), method="POST",
                                     headers={"Authorization": "Bearer " + tok, "Content-Type": tipo})
        try:
            with urllib.request.urlopen(req, timeout=300) as r:
                if r.status == 200:
                    estado[nome] = h
                    enviados += 1
        except urllib.error.HTTPError as e:
            erros += 1
            log(f"subir: HTTP {e.code} em {nome}")
            if e.code == 401:
                tok = _token()
        if enviados and enviados % 100 == 0:
            estado_arq.write_text(json.dumps(estado))
    estado_arq.write_text(json.dumps(estado))
    log(f"subir: {enviados} enviados, {pulados} já estavam, {erros} erros")


def etapa_relatorio(b: Base) -> None:
    """Contagens para o relatório: quantas obras, PDFs, textos, OA x não OA."""
    obras = list(b.obras.values())
    rel = {
        "data": HOJE, "obras": len(obras),
        "por_fonte": {f: sum(1 for w in obras if f in w.get("fontes", [])) for f in ("openalex", "crossref", "arxiv", "zbmath", "arxiv-kaggle")},
        "com_doi": sum(1 for w in obras if w.get("doi")), "com_arxiv": sum(1 for w in obras if w.get("arxiv")),
        "pdf_ok": sum(1 for w in obras if w.get("pdf_status") == "ok"),
        "pdf_falhou": sum(1 for w in obras if w.get("pdf_status") == "falhou"),
        "sem_oa": sum(1 for w in obras if w.get("pdf_status") == "sem_oa"),
        "pdfs_no_disco": len(list((dados() / "pdf").glob("*.pdf"))),
        "txts": len(list((dados() / "txt").glob("*.txt"))),
        "score>=6": sum(1 for w in obras if w.get("score", 0) >= 6),
    }
    (dados() / "relatorios" / f"contagens_{HOJE}.json").write_text(json.dumps(rel, indent=1), encoding="utf-8")
    nao_oa = [{"id": w["id"], "doi": w.get("doi"), "titulo": w.get("titulo"), "ano": w.get("ano"), "score": w.get("score")}
              for w in obras if w.get("pdf_status") in ("sem_oa", "falhou") and w.get("score", 0) >= 6]
    (dados() / "relatorios" / f"nao_acessiveis_{HOJE}.json").write_text(json.dumps(nao_oa, ensure_ascii=False, indent=0), encoding="utf-8")
    log(f"relatorio: {json.dumps(rel)}")


ETAPAS = ["sementes", "buscas", "expandir", "arxivmeta", "tabelas", "baixar", "extrair", "mencoes", "relatorio", "subir"]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("etapas", nargs="+", choices=ETAPAS + ["tudo"])
    ap.add_argument("--niveis", type=int, default=2, help="níveis de expansão por citação (padrão 2)")
    ap.add_argument("--limite-gb", type=float, default=6.0, help="teto local de PDFs em GB")
    a = ap.parse_args(argv)
    etapas = ETAPAS if "tudo" in a.etapas else a.etapas
    b = Base()
    for e in etapas:
        log(f"== etapa {e}")
        if e == "sementes":
            etapa_sementes(b)
        elif e == "buscas":
            etapa_buscas(b)
        elif e == "expandir":
            etapa_expandir(b, a.niveis)
        elif e == "arxivmeta":
            etapa_arxivmeta(b)
        elif e == "tabelas":
            etapa_tabelas()
        elif e == "baixar":
            etapa_baixar(b, a.limite_gb)
        elif e == "extrair":
            etapa_extrair(b)
        elif e == "mencoes":
            etapa_mencoes(b)
        elif e == "relatorio":
            etapa_relatorio(b)
        elif e == "subir":
            etapa_subir()
    return 0


if __name__ == "__main__":
    sys.exit(main())
