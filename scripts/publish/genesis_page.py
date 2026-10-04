#!/usr/bin/env python3
"""Gera a página /provas/cobertura da Genesis a partir do ledger.

Lê ledger/cells.json (cotas publicadas + nosso estado), ledger/provenance.json
e o .zenodo.json, e escreve UM arquivo HTML autocontido, no molde da página
publicada da v0.3 (mesmo CSS, metas citation_* para o Google Scholar). Não
sobe nada: subir é outra decisão, de outra ferramenta.

Uso:
    python3 scripts/publish/genesis_page.py --doi 10.5281/zenodo.23092580 \\
        --tag v0.3.0 --data 2026-10-02 --saida build/provas/cobertura.html
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from html import escape
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
REPO = "https://github.com/thiagopatzdorf/Matematica"
SITE = "https://genesisinnovation.io/provas/cobertura"

ROTULO_FONTE = {
    "keri_2011": "Kéri 2011",
    "gijswijt_polak_2025": "Gijswijt–Polak 2025",
    "marosi_2026": "Marosi 2026",
    "florath_lean": "Florath (Lean)",
    "literatura_pos_keri": "post-Kéri literature",
}

CSS = """:root{--bg:#05060A;--ink:#F6FDFF;--mut:rgba(246,253,255,.64);--dim:rgba(246,253,255,.42);--line:rgba(246,253,255,.10);--card:rgba(246,253,255,.035);--brand:#35C6F4;color-scheme:dark}
*{box-sizing:border-box}html,body{margin:0;background:var(--bg);color:var(--ink)}body{font-family:Manrope,system-ui,sans-serif;font-size:17px;line-height:1.7}a{color:var(--brand);text-decoration:none}
.bar{border-bottom:1px solid var(--line);background:rgba(5,7,12,.66);position:sticky;top:0}.bar-in{max-width:820px;margin:0 auto;padding:14px 20px;display:flex;justify-content:space-between}.bar-in b{letter-spacing:.14em;font-size:13px}.bar-in a{color:var(--mut);margin-left:16px;font-size:14px}
main{max-width:820px;margin:0 auto;padding:48px 20px 80px}
.tag{font-family:ui-monospace,monospace;letter-spacing:.16em;text-transform:uppercase;font-size:11px;color:var(--brand)}
h1{font-size:clamp(28px,4vw,40px);line-height:1.15;margin:12px 0}
.meta{color:var(--dim);font-size:14px;margin:0 0 28px}
.cta{display:flex;gap:12px;flex-wrap:wrap;margin:0 0 36px}.cta a{border:1px solid var(--line);border-radius:12px;padding:12px 16px;color:var(--ink);font-weight:600}.cta a.pri{background:var(--brand);color:#05060A;border-color:transparent}
h2{font-size:22px;margin:36px 0 10px}.abs{border-left:3px solid var(--brand);padding-left:16px}
.wrap{overflow-x:auto}table{border-collapse:collapse;width:100%;font-size:15px}th,td{border-bottom:1px solid var(--line);padding:8px 10px;text-align:left;vertical-align:top}td.n{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}
.ok{color:#7CE3A1}.cp{color:#F5C46B}
pre{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px;overflow-x:auto;font-size:13.5px;line-height:1.5}code{font-family:ui-monospace,monospace;font-size:.92em}
footer{border-top:1px solid var(--line);color:var(--dim);font-size:13px;max-width:820px;margin:0 auto;padding:24px 20px}"""


def k_html(c: dict) -> str:
    return f"K<sub>{c['q']}</sub>({c['n']},{c['R']})"


def k_txt(c: dict) -> str:
    return f"K_{c['q']}({c['n']},{c['R']})"


def fonte(b: dict | None) -> str:
    if not b:
        return "—"
    return f"{b['value']} <span class=\"meta\">({escape(ROTULO_FONTE.get(b['source'], b['source']))})</span>"


def linhas_tabela(cells: list[dict], tag: str) -> list[str]:
    out = []
    for c in cells:
        pub = c["published"]
        lean, comp = c.get("ours_lean"), c.get("ours_computational")
        if lean:
            lb_lean = _inferior_no_kernel(c)
            rel = "=" if lean.get("exact") or lb_lean else "≤"
            onde = f"<code>{escape(lean['declaration'])}</code>"
            onde += f" ({escape(lean['tag'])})" if lean.get("tag") else \
                f" (next release{', ' + escape(lean['tag_pendente']) if lean.get('tag_pendente') else ''})"
            if lb_lean:
                onde += f"; exact value <code>{escape(lb_lean['declaration'])}</code>"
                onde += f" ({escape(lb_lean['tag'])})" if lb_lean.get("tag") else ""
            cod = _link_codigo(lean.get("file"), tag)
            out.append(f"<tr><td>{k_html(c)}</td><td class=\"n\">{fonte(pub['lb'])}</td>"
                       f"<td class=\"n\">{fonte(pub['ub'])}</td><td class=\"n\"><b>{rel} {lean['M']}</b></td>"
                       f"<td><span class=\"ok\">Lean kernel</span>: {onde}</td><td>{cod}</td></tr>")
        if comp and (not lean or comp["M"] < lean["M"]):
            out.append(f"<tr><td>{k_html(c)}</td><td class=\"n\">{fonte(pub['lb'])}</td>"
                       f"<td class=\"n\">{fonte(pub['ub'])}</td><td class=\"n\"><b>≤ {comp['M']}</b></td>"
                       f"<td><span class=\"cp\">computer only</span> (not yet a Lean theorem)</td>"
                       f"<td>{_link_codigo(comp.get('file'), tag)}</td></tr>")
    return out


def _inferior_no_kernel(c: dict) -> dict | None:
    """Declaração Lean da cota inferior quando ela é teorema sem hipótese e fecha a célula (= superior).

    Sem isso a página mostraria "≤ 19" para K_7(4,2), cuja igualdade é teorema do kernel desde a v0.8.
    """
    cert = c.get("certification") or {}
    lb, lean = cert.get("lb") or {}, c.get("ours_lean") or {}
    decl = (lb.get("provenance") or {}).get("lean")
    if (not cert.get("exact") or lb.get("state") not in ("FORMALIZED", "INDEPENDENTLY_REPRODUCED")
            or not isinstance(decl, dict) or not decl.get("declaration") or decl.get("condicional")
            or lb.get("value") != lean.get("M") or decl["declaration"] == lean.get("declaration")):
        return None
    return decl


def _link_codigo(arquivo: str | None, tag: str) -> str:
    if not arquivo:
        return "—"
    return f"<a href=\"{REPO}/blob/main/{escape(arquivo)}\">{escape(Path(arquivo).name)}</a>"


def gerar(ledger: dict, zen: dict, prov: dict, doi: str, doi_conceito: str | None,
          tag: str, data: str) -> str:
    nossos = [c for c in ledger["cells"] if c.get("ours_lean") or c.get("ours_computational")]
    nossos.sort(key=lambda c: (c["q"], c["n"], c["R"]))
    lean = [c for c in nossos if c.get("ours_lean")]
    so_comp = [c for c in nossos if c.get("ours_computational")
               and (not c.get("ours_lean") or c["ours_computational"]["M"] < c["ours_lean"]["M"])]
    batem = [c for c in nossos if c.get("best", {}) and c["best"].get("beats_published")]
    titulo = zen["title"]
    versao = zen.get("version", "")
    data_barra = data.replace("-", "/")
    d = dt.date.fromisoformat(data)
    data_longa = f"{d.day} {d.strftime('%B')} {d.year}"
    # 'gap' é o texto em inglês para a página; 'lacuna' (pt) é o fallback.
    lacunas = [f"<li><code>{escape(r.get('codigo', k))}</code>: {escape(r.get('gap') or r['lacuna'])}</li>"
               for k, r in prov.get("registros", {}).items() if r.get("gap") or r.get("lacuna")]
    decl = "\n".join(f"theorem {c['ours_lean']['declaration']}  -- {k_txt(c)} "
                     f"{'=' if c['ours_lean'].get('exact') else '≤'} {c['ours_lean']['M']}"
                     for c in lean)
    decl += "".join(f"\ntheorem {lb_d['declaration']}  -- {k_txt(c)} = {c['ours_lean']['M']}"
                    for c in lean if (lb_d := _inferior_no_kernel(c)))
    fontes = ledger["meta"].get("fontes", {})
    fontes_txt = "; ".join(f"{escape(k)} <code>{escape(v['commit'][:7])}</code>" for k, v in sorted(fontes.items()))
    autores = zen.get("creators", [{}])
    autor = autores[0].get("name", "")
    afil = autores[0].get("affiliation", "")
    descricao = (f"{len(lean)} covering-code bounds proved in Lean 4 and checked by the kernel; "
                 f"{len(batem)} cells below the best published upper bound.")
    linhas = "\n".join(linhas_tabela(nossos, tag))
    conceito = (f" · concept DOI <a href=\"https://doi.org/{escape(doi_conceito)}\">{escape(doi_conceito)}</a>"
                if doi_conceito else "")
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{escape(titulo)} · Genesis</title>
<meta name="description" content="{escape(descricao)}">
<meta name="citation_title" content="{escape(titulo)}">
<meta name="citation_author" content="{escape(autor)}">
<meta name="citation_author_institution" content="{escape(afil)}">
<meta name="citation_publication_date" content="{data_barra}">
<meta name="citation_online_date" content="{data_barra}">
<meta name="citation_language" content="en">
<meta name="citation_doi" content="{escape(doi)}">
<meta name="citation_pdf_url" content="{SITE}.pdf">
<meta name="citation_abstract_html_url" content="{SITE}">
<meta name="citation_keywords" content="{escape('; '.join(zen.get('keywords', [])))}">
<link rel="canonical" href="{SITE}">
<meta property="og:title" content="{escape(titulo)}">
<meta property="og:description" content="{escape(descricao)}">
<meta property="og:url" content="{SITE}">
<meta property="og:type" content="article">
<style>
{CSS}
</style>
</head>
<body>
<div class="bar"><div class="bar-in"><a href="/"><b>GENESIS</b></a><nav><a href="/provas/paper">Sphere bound</a><a href="{REPO}">Code</a></nav></div></div>
<main>
<p class="tag">Paper · v{escape(versao)} · {escape(data_longa)}</p>
<h1>{escape(titulo)}</h1>
<p class="meta">{escape(autor)} · {escape(afil)} · <a href="https://doi.org/{escape(doi)}">doi:{escape(doi)}</a>{conceito}</p>
<div class="cta"><a class="pri" href="/provas/cobertura.pdf">PDF</a><a href="https://doi.org/{escape(doi)}">Zenodo</a><a href="{REPO}/tree/{escape(tag)}">Lean source</a><a href="{REPO}/blob/main/ledger/cells.json">Ledger (all cells)</a></div>

<p class="abs">{escape(zen.get('description', ''))}</p>

<h2>Bounds</h2>
<p>Every row is one of our results next to the best bounds published before it. <span class="ok">Lean kernel</span> means a theorem checked by the Lean 4 kernel, with no <code>sorry</code> and no <code>native_decide</code>; <span class="cp">computer only</span> means the code passed independent checkers outside Lean but is not yet a theorem.</p>
<div class="wrap"><table>
<tr><th>Cell</th><th>Best lower bound</th><th>Best published upper bound</th><th>Ours</th><th>Status</th><th>Code</th></tr>
{linhas}
</table></div>

<h2>The theorems</h2>
<pre>{escape(decl)}</pre>
<p>For an upper bound <code>K_q(n,R) ≤ M</code> the statement is <code>∃ C : Finset (Fin n → ZMod q), C.card = M ∧ CoveringA2.Covers R C</code>: every word is within Hamming distance <code>R</code> (Mathlib's <code>hammingDist</code>) of some word of <code>C</code>.</p>

<h2>Sources and provenance</h2>
<p>Published bounds are read by <code>ledger/build.py</code> from pinned commits ({fontes_txt}): Kéri's 2011 tables, Gijswijt–Polak (<a href="https://arxiv.org/abs/2504.01932">arXiv:2504.01932</a>), Marosi (<a href="https://arxiv.org/abs/2608.19872">arXiv:2608.19872</a>) and Florath's Lean database (<a href="https://arxiv.org/abs/2606.09600">arXiv:2606.09600</a>). Novelty is our reading of these sources, not something Lean checks. Corrections are welcome.</p>
<p>A Lean theorem does not depend on how its code was found, but a search should be reproducible. Known gaps:</p>
<ul>
{chr(10).join(lacunas)}
</ul>
{'<p>' + str(len(so_comp)) + ' cell(s) currently have a computer-verified code better than the Lean theorem.</p>' if so_comp else ''}
</main>
<footer>Genesis · Cite as: {escape(autor)}, <i>{escape(titulo)}</i>, Zenodo, {d.year}, doi:{escape(doi)}</footer>
</body>
</html>
"""


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--ledger", type=Path, default=RAIZ / "ledger" / "cells.json")
    ap.add_argument("--provenance", type=Path, default=RAIZ / "ledger" / "provenance.json")
    ap.add_argument("--zenodo-json", type=Path, default=RAIZ / ".zenodo.json")
    ap.add_argument("--doi", required=True, help="DOI da versão (ex.: 10.5281/zenodo.23092580)")
    ap.add_argument("--doi-conceito", default="10.5281/zenodo.23085769")
    ap.add_argument("--tag", required=True, help="tag git do código Lean (ex.: v0.3.0)")
    ap.add_argument("--data", default=dt.date.today().isoformat())
    ap.add_argument("--saida", type=Path, default=RAIZ / "build" / "provas" / "cobertura.html")
    a = ap.parse_args(argv)
    html = gerar(json.loads(a.ledger.read_text(encoding="utf-8")),
                 json.loads(a.zenodo_json.read_text(encoding="utf-8")),
                 json.loads(a.provenance.read_text(encoding="utf-8")),
                 a.doi, a.doi_conceito, a.tag, a.data)
    a.saida.parent.mkdir(parents=True, exist_ok=True)
    a.saida.write_text(html, encoding="utf-8")
    print(f"{a.saida}: {len(html)} bytes (não publicado)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
