#!/usr/bin/env python3
"""Gera o MAPA PÚBLICO DA FRONTEIRA (site estático) a partir do ledger.

Lê ledger/cells.json e ledger/targets.py (o ranqueamento NÃO é reimplementado
aqui) e escreve site/out/: página inicial, mapa q×n em SVG, tabela filtrável,
ranking de alvos e uma página por célula. Sem dependência, sem requisição de
rede, sem data/hora do relógio: o rodapé usa o sha e a data do COMMIT, então
duas execuções no mesmo commit geram bytes idênticos.

Uso:
    python3 scripts/site/build.py                 # escreve site/out/
    python3 scripts/site/build.py --saida DIR --commit SHA --data AAAA-MM-DD
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import shutil
import subprocess
import sys
from html import escape
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
REPO = "https://github.com/thiagopatzdorf/Matematica"

# estado exibido de cada célula (exclusivo); a ordem é a da legenda
CURTO = {"nosso": "Nossa", "melhorada": "Melhorada", "virgem": "Ninguém atacou",
         "atacada": "Atacada", "fechada": "Fechada"}
ESTADOS = [
    ("nosso", "Nossa cota, verificada no Lean"),
    ("melhorada", "Melhorada desde 2011 por outros"),
    ("virgem", "Aberta, ninguém atacou desde 2011"),
    ("atacada", "Aberta, atacada sem melhora"),
    ("fechada", "Fechada (cotas iguais)"),
]
ROTULO = dict(ESTADOS)
ROTULO_FONTE = {
    "keri_2011": "Kéri 2011",
    "gijswijt_polak_2025": "Gijswijt–Polak 2025",
    "marosi_2026": "Marosi 2026",
    "florath_lean": "Florath (Lean)",
    "literatura_pos_keri": "literatura pós-Kéri",
}
ORDEM_FONTES = list(ROTULO_FONTE)


def carregar_targets():
    spec = importlib.util.spec_from_file_location("ledger_targets", RAIZ / "ledger" / "targets.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


TARGETS = carregar_targets()


# ---------------------------------------------------------------- modelo

def slug(c: dict) -> str:
    return f"K{c['q']}-{c['n']}-{c['R']}"


def melhor_ub(c: dict) -> int:
    return TARGETS.melhor_ub(c)


def lb(c: dict) -> int:
    return c["published"]["lb"]["value"]


def aberta(c: dict) -> bool:
    return lb(c) < melhor_ub(c)


def estado(c: dict) -> str:
    if c.get("ours_lean") or c.get("ours_computational"):
        return "nosso"
    if not aberta(c):
        return "fechada"
    return {2: "melhorada", 1: "atacada", 0: "virgem"}[TARGETS.camada(c)]


def resumo(cells: list[dict]) -> dict:
    """Todos os números exibidos na página inicial. O teste os recalcula do JSON cru."""
    est = {k: 0 for k, _ in ESTADOS}
    for c in cells:
        est[estado(c)] += 1
    return {
        "n_cells": len(cells),
        "n_lean": sum(1 for c in cells if c.get("ours_lean")),
        "n_beats": sum(1 for c in cells if c.get("best") and c["best"]["beats_published"]),
        "n_virgem": est["virgem"],
        "n_melhoradas": sum(1 for c in cells if c.get("ub_improved_since_2011")),
        "n_abertas": sum(1 for c in cells if aberta(c)),
        "n_exatas": sum(1 for c in cells if c["published"].get("exact")),
        "estados": est,
    }


def git_info(commit: str | None, data: str | None) -> tuple[str, str]:
    if commit and data:
        return commit, data
    try:
        out = subprocess.run(["git", "-C", str(RAIZ), "log", "-1", "--format=%H%n%cI"],
                             capture_output=True, text=True, check=True).stdout.split()
        return commit or out[0], data or out[1][:10]
    except (OSError, subprocess.CalledProcessError, IndexError):
        return commit or "desconhecido", data or "desconhecida"


def arquivo_lean(decl: str) -> str | None:
    """Onde mora o teorema: procura `theorem <nome>` em CoveringLean/ (nada de caminho chutado)."""
    curto = decl.split(".")[-1]
    for f in sorted((RAIZ / "CoveringLean").glob("*.lean")):
        txt = f.read_text(encoding="utf-8", errors="replace")
        if f"theorem {curto}" in txt:
            return f"CoveringLean/{f.name}"
    return None


# ---------------------------------------------------------------- html

def kh(c: dict) -> str:
    return f"K<sub>{c['q']}</sub>({c['n']},{c['R']})"


def blob(caminho: str) -> str:
    return f"{REPO}/blob/main/{caminho}"


def chip(est: str) -> str:
    return f'<span class="chip s-{est}"><i></i>{escape(ROTULO[est])}</span>'


NAV = [("index.html", "Início"), ("mapa.html", "Mapa"), ("celulas.html", "Células"),
       ("alvos.html", "Alvos")]


def pagina(titulo: str, corpo: str, raiz: str, atual: str, rodape: str, desc: str = "",
           js: bool = False) -> str:
    cur = ' aria-current="page"'
    nav = "".join(f'<li><a href="{raiz}{h}"{cur if h == atual else ""}>{t}</a></li>'
                  for h, t in NAV)
    script = f'<script src="{raiz}assets/app.js" defer></script>' if js else ""
    return f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{escape(titulo)} · Mapa da fronteira</title>
<meta name="description" content="{escape(desc)}">
<link rel="stylesheet" href="{raiz}assets/style.css">
</head>
<body>
<a class="skip" href="#conteudo">Pular para o conteúdo</a>
<header class="top"><div class="wrap"><b>Mapa da fronteira</b><nav aria-label="Principal"><ul>{nav}</ul></nav></div></header>
<main id="conteudo"><div class="wrap">
{corpo}
</div></main>
<footer><div class="wrap">{rodape}</div></footer>
{script}
</body>
</html>
"""


def pagina_inicial(cells: list[dict], r: dict, meta: dict) -> str:
    def num(k, v):
        return f'<span data-num="{k}">{v}</span>'

    est_li = "".join(
        f'<li>{chip(k)} <a href="celulas.html?estado={k}">{num("estado_" + k, r["estados"][k])}</a></li>'
        for k, _ in ESTADOS)
    return f"""<h1>Onde termina o que se sabe sobre códigos de cobertura</h1>
<p class="lead">Para cada célula <code>K<sub>q</sub>(n,R)</code> das tabelas do Kéri (o menor número de palavras de um código <i>q</i>-ário de comprimento <i>n</i> que cobre todo o espaço com raio <i>R</i>), este mapa mostra a melhor cota conhecida, de quem ela é, e o que já fizemos, com verificação formal no Lean. Cada número vem do <a href="{blob('ledger/cells.json')}">ledger</a> do repositório.</p>
<ul class="cards" aria-label="Números do ledger">
<li class="card"><strong class="big">{num("n_cells", r["n_cells"])}</strong><span class="lab">células no ledger</span><small>{num("n_abertas", r["n_abertas"])} abertas (cota inferior publicada &lt; melhor superior conhecida); {num("n_exatas", r["n_exatas"])} exatas na literatura.</small></li>
<li class="card"><strong class="big">{num("n_lean", r["n_lean"])}</strong><span class="lab">com cota superior nossa verificada no Lean</span><small>Teorema aceito pelo kernel, com o código explícito como certificado.</small></li>
<li class="card"><strong class="big">{num("n_beats", r["n_beats"])}</strong><span class="lab">melhoram a literatura</span><small>A melhor cota superior conhecida passa a ser a nossa (a décima segunda célula, K<sub>2</sub>(6,1), é exata e só confirma o valor).</small></li>
<li class="card"><strong class="big">{num("n_virgem", r["n_virgem"])}</strong><span class="lab">abertas que ninguém atacou desde 2011</span><small>Nas fontes lidas: nem o Marosi, nem nós. É onde ainda não olhou ninguém.</small></li>
<li class="card"><strong class="big">{num("n_melhoradas", r["n_melhoradas"])}</strong><span class="lab">cotas superiores melhoradas desde 2011</span><small>Pelo Marosi (2026), contando as que depois melhoramos de novo.</small></li>
</ul>
<div class="btns"><a class="btn pri" href="mapa.html">Ver o mapa da fronteira</a><a class="btn" href="alvos.html">Ranking de alvos</a><a class="btn" href="celulas.html">Todas as células</a><a class="btn" href="{REPO}">Repositório</a></div>
<h2>Como as células se dividem</h2>
<ul class="legend">{est_li}</ul>
<p>Cada célula tem um único estado, o mais forte: nossa cota verificada, depois fechada, depois o resto das abertas pela atenção que já recebeu.</p>
<h2>Participe: pessoas e agentes</h2>
<p>Dá para contribuir sem pedir licença. Escolha uma célula (o <a href="alvos.html">ranking</a> sugere por onde começar), ache um código menor que a melhor cota conhecida e confira com o verificador oficial; a aceitação não depende de quem achou, depende de o código cobrir.</p>
<pre>git clone {REPO}.git &amp;&amp; cd Matematica
python3 ledger/targets.py --top 15          # alvos ranqueados
cc -O2 -std=c99 -o tools/verify/verify tools/verify/verify.c
tools/verify/verify -q 7 -n 9 -r 4 meu_codigo.txt   # só vale se cobre, sem palavra repetida
python3 scripts/loop/record_loop.py --celula "K7(9,4)"   # seco; --executar grava no ledger</pre>
<p>Cada célula tem uma página com o comando certo para ela. Um código que cobre vira cota nova; o teorema no Lean vem depois, a partir do código.</p>
<h2>O que este mapa não diz</h2>
<p class="note">Literatura posterior a 2011 fora das fontes lidas (Kéri 2011, Gijswijt–Polak 2025 para <i>q</i> ≤ 5, Marosi 2026, Florath e uma compilação pós-Kéri, lidas em 2026-10-02), em especial a binária e a ternária, <b>não foi auditada</b>. “Ninguém atacou” quer dizer: ninguém nessas fontes. Cota nossa só aparece como recorde quando o ledger a marca como melhor que a publicada.</p>
"""


# glifos redundantes à cor: cada estado também se distingue sem enxergar cores
def glifo(est: str, x: float, y: float, s: int) -> str:
    cx, cy = x + s / 2, y + s / 2
    if est == "nosso":
        return f'<path class="gf" d="M{cx} {y + 3}L{x + s - 3} {cy}L{cx} {y + s - 3}L{x + 3} {cy}Z"/>'
    if est == "melhorada":
        return f'<path class="g" d="M{x + 3} {y + s - 3}L{x + s - 3} {y + 3}"/>'
    if est == "atacada":
        return f'<circle class="gf" cx="{cx}" cy="{cy}" r="2"/>'
    return ""


def painel_q(q: int, cells: list[dict]) -> tuple[str, int]:
    S, P, ML, MT = 16, 18, 26, 22
    ns = sorted({c["n"] for c in cells})
    rs = sorted({c["R"] for c in cells})
    n0, n1, r1 = ns[0], ns[-1], rs[-1]
    cols, rows = n1 - n0 + 1, r1
    W, H = ML + cols * P + 4, MT + rows * P + 4
    por = {(c["n"], c["R"]): c for c in cells}
    out = [f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="t{q}">',
           f'<title id="t{q}">Células de q = {q}, n de {n0} a {n1}, R de 1 a {r1}</title>']
    for n in range(n0, n1 + 1):
        if (n - n0) % 2 == 0 or cols < 14:
            out.append(f'<text x="{ML + (n - n0) * P + S / 2}" y="{MT - 8}" text-anchor="middle">{n}</text>')
    for R in range(1, r1 + 1):
        out.append(f'<text x="{ML - 6}" y="{MT + (R - 1) * P + S / 2 + 4}" text-anchor="end">{R}</text>')
    for (n, R), c in sorted(por.items()):
        x, y = ML + (n - n0) * P, MT + (R - 1) * P
        e = estado(c)
        tip = (f"{c['id']}: {ROTULO[e]}; cota inferior {lb(c)}, melhor superior {melhor_ub(c)}")
        out.append(f'<g class="cell c-{e}"><a href="celula/{slug(c)}.html" aria-label="{escape(tip)}">'
                   f'<title>{escape(tip)}</title><rect x="{x}" y="{y}" width="{S}" height="{S}" rx="3"/>'
                   f'{glifo(e, x, y, S)}</a></g>')
    out.append("</svg>")
    return "".join(out), cols * P + ML


def pagina_mapa(cells: list[dict]) -> str:
    por_q: dict[int, list[dict]] = {}
    for c in cells:
        por_q.setdefault(c["q"], []).append(c)
    legenda = "".join(f"<li>{chip(k)}</li>" for k, _ in ESTADOS)
    paineis, linhas = [], []
    for q in sorted(por_q):
        svg, largura = painel_q(q, por_q[q])
        cont = {k: 0 for k, _ in ESTADOS}
        for c in por_q[q]:
            cont[estado(c)] += 1
        paineis.append(
            f'<section class="panel" aria-labelledby="h{q}"><h3 id="h{q}">q = {q} <span class="chip" style="font-weight:400">{len(por_q[q])} células</span></h3>'
            f'<div class="scroll" tabindex="0" role="region" aria-label="Mapa de q = {q}"><div style="min-width:{largura}px">{svg}</div></div></section>')
        celulas = "".join(f'<td class="n">{cont[k]}</td>' for k, _ in ESTADOS)
        linhas.append(f'<tr><th scope="row"><a href="celulas.html?q={q}">{q}</a></th><td class="n">{len(por_q[q])}</td>{celulas}</tr>')
    cab = "".join(f'<th scope="col" class="n" title="{escape(t)}">{CURTO[k]}</th>' for k, t in ESTADOS)
    return f"""<h1>Mapa da fronteira</h1>
<p class="lead">Um painel por alfabeto <i>q</i>. Em cada um, as colunas são o comprimento <i>n</i> e as linhas o raio <i>R</i>; cada quadrado é uma célula e leva à sua página. Procure o verde (aberta, ninguém atacou desde 2011) e o laranja (já temos cota verificada).</p>
<ul class="legend" aria-label="Legenda">{legenda}</ul>
<p>Forma além da cor: losango = nossa cota; traço diagonal = melhorada por outros; ponto = atacada sem melhora; liso verde = ninguém atacou; cinza claro = fechada.</p>
{"".join(paineis)}
<h2>Os mesmos números, em tabela</h2>
<div class="scroll"><table><caption>Células por alfabeto q e por estado</caption>
<thead><tr><th scope="col">q</th><th scope="col" class="n">Células</th>{cab}</tr></thead><tbody>{"".join(linhas)}</tbody></table></div>
"""


def pagina_celulas(cells: list[dict]) -> str:
    qs = sorted({c["q"] for c in cells})
    opt_q = "".join(f'<option value="{q}">{q}</option>' for q in qs)
    opt_e = "".join(f'<option value="{k}">{escape(t)}</option>' for k, t in ESTADOS)
    linhas = []
    for i, c in enumerate(cells):
        e, ub = estado(c), melhor_ub(c)
        pub_ub = c["published"]["ub"]
        ours = c.get("ours_lean") or c.get("ours_computational")
        nosso = ours["M"] if ours else ""
        linhas.append(
            f'<tr data-id="{escape(c["id"])}" data-q="{c["q"]}" data-estado="{e}" data-aberta="{int(aberta(c))}" data-ord="{i}">'
            f'<th scope="row" data-v="{escape(c["id"])}"><a href="celula/{slug(c)}.html">{kh(c)}</a></th>'
            f'<td class="n" data-v="{c["q"]}">{c["q"]}</td><td class="n" data-v="{c["n"]}">{c["n"]}</td><td class="n" data-v="{c["R"]}">{c["R"]}</td>'
            f'<td class="n" data-v="{lb(c)}">{lb(c)}</td>'
            f'<td class="n" data-v="{pub_ub["value"]}">{pub_ub["value"]}</td>'
            f'<td class="n" data-v="{ub}">{ub}</td>'
            f'<td class="n" data-v="{nosso if nosso != "" else 0}">{nosso}</td>'
            f'<td data-v="{e}">{chip(e)}</td></tr>')

    def th(rot, tipo, cls=""):
        return f'<th scope="col" class="{cls}" data-tipo="{tipo}"><button type="button">{rot}</button></th>'

    cab = (th("Célula", "t") + th("q", "n", "n") + th("n", "n", "n") + th("R", "n", "n")
           + th("Inferior publicada", "n", "n") + th("Superior publicada", "n", "n")
           + th("Melhor superior", "n", "n") + th("Nossa", "n", "n") + th("Estado", "t"))
    return f"""<h1>Todas as células</h1>
<p class="lead">Ordene pelos cabeçalhos e filtre pelos controles. Sem JavaScript a tabela aparece inteira, na ordem do ledger.</p>
<div class="tools js-only" role="search">
<label>q<select id="f-q"><option value="">todos</option>{opt_q}</select></label>
<label>Estado<select id="f-estado"><option value="">todos</option>{opt_e}</select></label>
<label>Buscar<input type="search" id="f-busca" placeholder="K7(9,4)"></label>
<label style="flex-direction:row;align-items:center;gap:6px"><input type="checkbox" id="f-abertas"> só abertas</label>
<span id="contagem" aria-live="polite"></span></div>
<div class="scroll"><table id="tabela"><caption>{len(cells)} células K<sub>q</sub>(n,R): cotas publicadas, melhor superior conhecida e nossa cota</caption>
<thead><tr>{cab}</tr></thead><tbody>{"".join(linhas)}</tbody></table></div>
"""


def pagina_alvos(alvos: list[dict], por_id: dict) -> str:
    linhas = []
    for t in alvos:
        c = por_id[t["id"]]
        linhas.append(
            f'<tr><td class="n">{t["rank"]}</td><th scope="row"><a href="celula/{slug(c)}.html">{kh(c)}</a></th>'
            f'<td class="n">{t["lb"]}</td><td class="n">{t["ub"]}</td><td class="n">{t["ratio"]:.2f}</td>'
            f'<td class="n">{c["q"]}^{c["n"]} = {c["space"]}</td><td>{chip(estado(c))}</td></tr>')
    return f"""<h1>Ranking de alvos</h1>
<p class="lead">Onde há mais chance de avançar: células abertas com espaço <i>q</i><sup><i>n</i></sup> ≤ 10<sup>9</sup> (verificação barata), na ordem de <code>ledger/targets.py</code>: primeiro as que ninguém atacou desde 2011, depois as que o Marosi atacou sem melhorar, depois as já melhoradas; dentro de cada grupo, maior razão superior/inferior e, no empate, espaço menor. Os {len(alvos)} primeiros:</p>
<div class="scroll"><table><caption>Alvos ranqueados</caption>
<thead><tr><th scope="col" class="n">#</th><th scope="col">Célula</th><th scope="col" class="n">Inferior</th><th scope="col" class="n">Superior</th><th scope="col" class="n">Razão</th><th scope="col" class="n">Espaço</th><th scope="col">Estado</th></tr></thead>
<tbody>{"".join(linhas)}</tbody></table></div>
<p>Razão grande não promete recorde: a cota inferior pode estar frouxa em vez da superior. É um critério para escolher por onde começar, e o ranking é regenerado a cada build.</p>
"""


def fonte_txt(b: dict | None) -> str:
    if not b:
        return "—"
    return f'{b["value"]} <small>({escape(ROTULO_FONTE.get(b["source"], b["source"]))})</small>'


def bloco_nosso(c: dict, titulo: str, chave: str) -> str:
    o = c.get(chave)
    if not o:
        return ""
    itens = [f"<dt>Tamanho</dt><dd>{o['M']} palavras</dd>"]
    if o.get("declaration"):
        arq = arquivo_lean(o["declaration"])
        link = f' (<a href="{blob(arq)}">{escape(arq)}</a>)' if arq else ""
        itens.append(f"<dt>Declaração Lean</dt><dd><code>{escape(o['declaration'])}</code>{link}</dd>")
    if o.get("tag"):
        itens.append(f"<dt>Tag</dt><dd>{escape(o['tag'])}</dd>")
    elif chave == "ours_lean":
        itens.append("<dt>Tag</dt><dd>ainda sem tag</dd>")
    if o.get("file"):
        itens.append(f'<dt>Código</dt><dd><a href="{blob(o["file"])}">{escape(o["file"])}</a></dd>')
        estr = "data/structured/" + Path(o["file"]).stem + ".json"
        if (RAIZ / estr).exists():
            itens.append(f'<dt>Formato estruturado</dt><dd><a href="{blob(estr)}">{escape(estr)}</a></dd>')
    if o.get("sha256"):
        itens.append(f"<dt>sha256</dt><dd><code>{escape(o['sha256'])}</code></dd>")
    if o.get("provenance"):
        itens.append(f'<dt>Proveniência</dt><dd>registro <code>{escape(o["provenance"])}</code> em <a href="{blob("ledger/provenance.json")}">ledger/provenance.json</a></dd>')
    return f'<h2>{titulo}</h2><dl class="kv">{"".join(itens)}</dl>'


def como_atacar(c: dict, e: str) -> str:
    ub = melhor_ub(c)
    cid = c["id"]
    if e == "fechada":
        return ("<h2>Como atacar esta célula</h2><p>A célula está fechada (cota inferior = superior): "
                "não há cota superior a melhorar. Resta, no máximo, conferir a fonte.</p>")
    barato = c["space"] <= 1e9
    peso = ("" if barato else
            f"<p class=\"note\">O espaço tem {c['space']} pontos (acima de 10<sup>9</sup>): a verificação é pesada; "
            "use o verificador em C e conte com minutos a horas.</p>")
    return f"""<h2>Como atacar esta célula</h2>
<p>Para entrar como novidade, um código precisa ter <b>menos de {ub} palavras</b> (a melhor cota superior conhecida) e cobrir todo o espaço com raio {c['R']}. Os comandos abaixo existem no repositório; rode da raiz.</p>
<pre>python3 ledger/targets.py --top 30          # onde esta célula está no ranking
cc -O2 -std=c99 -o tools/verify/verify tools/verify/verify.c
tools/verify/verify -q {c['q']} -n {c['n']} -r {c['R']} meu_codigo.txt
python3 scripts/loop/record_loop.py --celula "{cid}"          # plano, sem rodar nada
python3 scripts/loop/record_loop.py --celula "{cid}" \\
    --gerador "./meu_gerador {{q}} {{n}} {{R}} {{saida}}" \\
    --verificador "tools/verify/verify -q {{q}} -n {{n}} -r {{R}} {{arquivo}}" --executar</pre>
{peso}
<p>Ferramentas de busca (cosets de códigos lineares, remendo por ILP): <a href="{blob('scripts/search/README.md')}">scripts/search/README.md</a>. Formato de arquivo: <a href="{blob('docs/code-format.md')}">docs/code-format.md</a>.</p>"""


def pagina_celula(c: dict) -> str:
    e = estado(c)
    pub = c["published"]
    linhas = []
    for k in ORDEM_FONTES:
        s = pub["sources"].get(k)
        if not s:
            continue
        ref_lb = s.get("lb_ref") or ""
        ref_ub = s.get("ub_ref") or ""
        ref = escape("; ".join(x for x in (f"inf.: {ref_lb}" if ref_lb else "", f"sup.: {ref_ub}" if ref_ub else "") if x))
        linhas.append(f'<tr><th scope="row">{escape(ROTULO_FONTE[k])}</th><td class="n">{s.get("lb") if s.get("lb") is not None else "—"}</td>'
                      f'<td class="n">{s.get("ub") if s.get("ub") is not None else "—"}</td><td>{ref}</td></tr>')
    ataque = c["marosi_attacked"]
    ev = ", ".join(escape(x) for x in ataque["evidence"]) or "nenhuma"
    best = c["best"]
    holder = {"published": "publicada", "ours_lean": "nossa, Lean", "ours_computational": "nossa, computacional"}.get(best["holder"], best["holder"])
    return f"""<p><a href="../celulas.html">← todas as células</a></p>
<h1>{kh(c)}</h1>
<p>{chip(e)} &nbsp; q = {c['q']}, n = {c['n']}, R = {c['R']}; espaço {c['q']}<sup>{c['n']}</sup> = {c['space']}; cota de esfera {c['sphere_bound']}.</p>
<h2>Cotas publicadas</h2>
<dl class="kv"><dt>Inferior</dt><dd>{fonte_txt(pub['lb'])}<br><small>{escape(pub['lb'].get('ref', ''))}</small></dd>
<dt>Superior</dt><dd>{fonte_txt(pub['ub'])}<br><small>{escape(pub['ub'].get('ref', ''))}</small></dd>
<dt>Exata</dt><dd>{'sim' if pub.get('exact') else 'não'}</dd>
<dt>Melhor superior conhecida</dt><dd>{best['ub']} ({holder}){'; melhor que a publicada' if best['beats_published'] else ''}</dd></dl>
<div class="scroll"><table><caption>Cada fonte lida, com a cota que ela traz</caption>
<thead><tr><th scope="col">Fonte</th><th scope="col" class="n">Inferior</th><th scope="col" class="n">Superior</th><th scope="col">Referência</th></tr></thead>
<tbody>{"".join(linhas)}</tbody></table></div>
<h2>Quem já atacou</h2>
<dl class="kv"><dt>Marosi, cota superior</dt><dd>{'atacou' if ataque['ub'] else 'sem registro'}</dd><dt>Marosi, cota inferior</dt><dd>{'atacou' if ataque['lb'] else 'sem registro'}</dd><dt>Evidência</dt><dd>{ev}</dd>
<dt>Melhorada desde 2011</dt><dd>{'sim' if c['ub_improved_since_2011'] else 'não'}</dd></dl>
{bloco_nosso(c, 'Nosso estado: Lean', 'ours_lean')}{bloco_nosso(c, 'Nosso estado: computacional', 'ours_computational')}
{'' if (c.get('ours_lean') or c.get('ours_computational')) else '<h2>Nosso estado</h2><p>Nada nosso nesta célula ainda.</p>'}
{como_atacar(c, e)}
"""


def rodape(sha: str, data: str, meta: dict) -> str:
    return (f'Gerado do commit <a href="{REPO}/commit/{escape(sha)}"><code>{escape(sha[:7])}</code></a> em {escape(data)}; '
            f'nosso estado no ledger: {escape(str(meta.get("ours_atualizado", "?")))}. '
            f'Sem rastreadores, sem requisições externas. Código e dados: <a href="{REPO}">{REPO.split("//")[1]}</a>.')


# ---------------------------------------------------------------- montagem

def construir(cells: list[dict], meta: dict, sha: str, data: str) -> dict[str, str]:
    cells = sorted(cells, key=lambda c: (c["q"], c["n"], c["R"]))
    por_id = {c["id"]: c for c in cells}
    r = resumo(cells)
    alvos = TARGETS.ranquear(cells)[:30]
    rod = rodape(sha, data, meta)
    arqs = {
        "index.html": pagina("Início", pagina_inicial(cells, r, meta), "", "index.html", rod,
                             "Estado do conhecimento sobre cotas de códigos de cobertura e onde contribuir."),
        "mapa.html": pagina("Mapa", pagina_mapa(cells), "", "mapa.html", rod, "Mapa q × n × R das células de cobertura."),
        "celulas.html": pagina("Células", pagina_celulas(cells), "", "celulas.html", rod, "Tabela de todas as células.", js=True),
        "alvos.html": pagina("Alvos", pagina_alvos(alvos, por_id), "", "alvos.html", rod, "Células-alvo ranqueadas."),
    }
    for c in cells:
        arqs[f"celula/{slug(c)}.html"] = pagina(
            c["id"], pagina_celula(c), "../", "", rod, f"Cotas e estado de {c['id']}.")
    return arqs


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--ledger", type=Path, default=RAIZ / "ledger" / "cells.json")
    ap.add_argument("--saida", type=Path, default=RAIZ / "site" / "out")
    ap.add_argument("--commit")
    ap.add_argument("--data")
    a = ap.parse_args(argv)
    led = json.loads(a.ledger.read_text(encoding="utf-8"))
    sha, data = git_info(a.commit, a.data)
    arqs = construir(led["cells"], led["meta"], sha, data)
    if a.saida.exists():
        shutil.rmtree(a.saida)  # saída é descartável: reconstruir é o inverso de apagar
    for rel, txt in arqs.items():
        f = a.saida / rel
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(txt, encoding="utf-8", newline="\n")
    (a.saida / "assets").mkdir(exist_ok=True)
    for nome in ("style.css", "app.js"):
        shutil.copyfile(RAIZ / "site" / "templates" / nome, a.saida / "assets" / nome)
    print(f"{len(arqs)} páginas em {a.saida} (commit {sha[:7]}, {data})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
