"""Testes do mapa público (scripts/site/build.py): determinismo, fidelidade ao ledger, sem rede."""
import hashlib
import importlib.util
import json
import re
from html.parser import HTMLParser
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
CELLS = json.loads((RAIZ / "ledger" / "cells.json").read_text(encoding="utf-8"))["cells"]


def _carregar():
    spec = importlib.util.spec_from_file_location("site_build", RAIZ / "scripts" / "site" / "build.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def build():
    return _carregar()


@pytest.fixture(scope="module")
def saida(build, tmp_path_factory):
    d = tmp_path_factory.mktemp("out")
    assert build.main(["--saida", str(d), "--commit", "a" * 40, "--data", "2026-01-01"]) == 0
    return d


def _hashes(d: Path) -> dict:
    return {str(f.relative_to(d)): hashlib.sha256(f.read_bytes()).hexdigest()
            for f in sorted(d.rglob("*")) if f.is_file()}


class Coleta(HTMLParser):
    def __init__(self):
        super().__init__()
        self.pilha, self.attrs, self.erros = [], [], []

    VAZIOS = {"meta", "link", "br", "img", "input", "hr", "path", "rect", "circle"}

    def handle_starttag(self, tag, attrs):
        self.attrs.append((tag, dict(attrs)))
        if tag not in self.VAZIOS:
            self.pilha.append(tag)

    def handle_startendtag(self, tag, attrs):
        self.attrs.append((tag, dict(attrs)))

    def handle_endtag(self, tag):
        if tag in self.VAZIOS:
            return
        if not self.pilha or self.pilha[-1] != tag:
            self.erros.append(f"</{tag}> com pilha {self.pilha[-3:]}")
        else:
            self.pilha.pop()


def _parse(f: Path) -> Coleta:
    p = Coleta()
    p.feed(f.read_text(encoding="utf-8"))
    if p.pilha:
        p.erros.append(f"tags abertas no fim: {p.pilha}")
    return p


def test_build_duas_vezes_gera_os_mesmos_bytes(build, saida, tmp_path):
    build.main(["--saida", str(tmp_path), "--commit", "a" * 40, "--data", "2026-01-01"])
    assert _hashes(tmp_path) == _hashes(saida)


def test_numeros_da_pagina_inicial_batem_com_o_ledger_cru(saida):
    html = (saida / "index.html").read_text(encoding="utf-8")
    achados = {k: int(v) for k, v in re.findall(r'data-num="(\w+)">(\d+)<', html)}
    # recalculado do JSON cru, sem usar o código do gerador
    abertas = [c for c in CELLS if c["published"]["lb"]["value"] < c["best"]["ub"]]
    assert achados["n_cells"] == len(CELLS)
    assert achados["n_lean"] == sum(1 for c in CELLS if c["ours_lean"])
    assert achados["n_beats"] == sum(1 for c in CELLS if c["best"]["beats_published"])
    assert achados["n_melhoradas"] == sum(1 for c in CELLS if c["ub_improved_since_2011"])
    assert achados["n_exatas"] == sum(1 for c in CELLS if c["published"]["exact"])
    assert achados["n_abertas"] == len(abertas)
    virgens = [c for c in abertas if not c["marosi_attacked"]["ub"] and not c["ub_improved_since_2011"]
               and not c["ours_lean"] and not c["ours_computational"]]
    assert achados["n_virgem"] == len(virgens)
    assert sum(v for k, v in achados.items() if k.startswith("estado_")) == len(CELLS)


@pytest.mark.parametrize("cid", ["K7(9,4)", "K2(6,1)", "K5(10,5)", "K2(2,1)", "K21(8,1)"])
def test_pagina_de_celula_traz_as_cotas_do_ledger(build, saida, cid):
    c = next((x for x in CELLS if x["id"] == cid), None)
    if c is None:
        pytest.skip("célula fora do ledger")
    html = (saida / "celula" / f"{build.slug(c)}.html").read_text(encoding="utf-8")
    texto = re.sub(r"<[^>]+>", " ", html)
    assert f"{c['published']['lb']['value']}" in texto
    assert f"{c['published']['ub']['value']}" in texto
    assert f"{c['best']['ub']}" in texto
    if c["ours_lean"]:
        assert c["ours_lean"]["declaration"] in html
        if c["ours_lean"].get("sha256"):
            assert c["ours_lean"]["sha256"] in html


def test_k7_9_4_mostra_nossa_cota_1134_e_nao_afirma_recorde_sem_fonte(saida):
    html = (saida / "celula" / "K7-9-4.html").read_text(encoding="utf-8")
    assert "1134" in html and "Syn.K7_9_4_le_1134_syn" in html
    assert "1475" in html and "Marosi" in html  # a cota publicada e a fonte aparecem junto


def test_nenhuma_requisicao_externa_nos_arquivos_gerados(saida):
    for f in saida.rglob("*"):
        if not f.is_file():
            continue
        txt = f.read_text(encoding="utf-8")
        if f.suffix == ".html":
            for tag, a in _parse(f).attrs:
                if tag == "script":
                    assert not (a.get("src") or "").startswith(("http", "//")), f
                if tag == "link":
                    assert not (a.get("href") or "").startswith(("http", "//")), f
        else:
            assert not re.search(r"https?://|@import|url\(", txt), f"{f} faz requisição externa"
    # no HTML, URL absoluta só em <a href>
    for f in saida.rglob("*.html"):
        sem_links = re.sub(r'<a [^>]*href="https?://[^"]*"[^>]*>', "<a>", f.read_text(encoding="utf-8"))
        sem_links = re.sub(r"<title>.*?</title>", "", sem_links, flags=re.S)
        assert not re.search(r'(src|href|action)="https?://', sem_links), f


def test_html_bem_formado_e_links_internos_resolvem(saida):
    ids_ruins = []
    for f in saida.rglob("*.html"):
        p = _parse(f)
        assert not p.erros, (f, p.erros[:3])
        for tag, a in p.attrs:
            for k in ("href", "src"):
                v = a.get(k)
                if not v or v.startswith(("http://", "https://", "#", "mailto:")):
                    continue
                alvo = (f.parent / v.split("#")[0].split("?")[0]).resolve()
                if not alvo.is_file():
                    ids_ruins.append((str(f.relative_to(saida)), v))
    assert not ids_ruins[:5], ids_ruins[:5]


def test_toda_celula_do_ledger_tem_pagina_e_aparece_no_mapa_e_na_tabela(build, saida):
    mapa = (saida / "mapa.html").read_text(encoding="utf-8")
    tabela = (saida / "celulas.html").read_text(encoding="utf-8")
    for c in CELLS:
        nome = f"celula/{build.slug(c)}.html"
        assert (saida / nome).is_file()
        assert nome in mapa and nome in tabela


def test_acessibilidade_basica_tabela_caption_scope_e_grafico_com_texto(saida):
    for nome in ("celulas.html", "alvos.html", "mapa.html"):
        html = (saida / nome).read_text(encoding="utf-8")
        assert "<caption>" in html and 'scope="col"' in html
    mapa = (saida / "mapa.html").read_text(encoding="utf-8")
    assert 'role="img"' in mapa and "<title id=" in mapa
    assert "Os mesmos números, em tabela" in mapa  # equivalente textual do gráfico
    assert 'lang="pt-BR"' in mapa and 'name="viewport"' in mapa


def test_rodape_usa_sha_do_commit_e_nao_a_hora_do_build(saida):
    html = (saida / "index.html").read_text(encoding="utf-8")
    assert "aaaaaaa" in html and "2026-01-01" in html


def test_ranking_de_alvos_usa_o_targets_do_ledger(build, saida):
    import sys
    sys.path.insert(0, str(RAIZ / "ledger"))
    import targets
    esperado = [t["id"] for t in targets.ranquear(CELLS)[:30]]
    html = (saida / "alvos.html").read_text(encoding="utf-8")
    achados = re.findall(r'<a href="celula/(K[\d-]+)\.html"', html)
    assert achados == [build.slug(next(c for c in CELLS if c["id"] == i)) for i in esperado]
