"""Página pública site/matematica/ (genesisinnovation.io/matematica).

Cada teste descreve a falha que impede: número da página divergindo do ledger, código do prólogo
diferente do arquivo verificado, Problema do Milênio com status errado, tradução faltando, recurso
externo fora da lista, página pesada demais, ou <base> que o publicador recusa.
"""
import json
import re
import sys
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
PAGINA = RAIZ / "site" / "matematica"
HTML = (PAGINA / "index.html").read_text(encoding="utf-8")
JS = (PAGINA / "app.js").read_text(encoding="utf-8")
CELLS = json.loads((RAIZ / "ledger" / "cells.json").read_text(encoding="utf-8"))["cells"]
sys.path.insert(0, str(RAIZ / "tools" / "site"))
from gerar_dados_site import DOI_VERSAO  # noqa: E402

FRASE_LEDGER = "A machine-checked ledger of covering-code upper bounds, with formally certified exact entries."
ESTADOS = ["CLAIMED", "WITNESS_CHECKED", "CERTIFICATE_VERIFIED", "FORMALIZED", "INDEPENDENTLY_REPRODUCED"]
HOSTS_PERMITIDOS = ("https://fonts.googleapis.com", "https://fonts.gstatic.com")


class Coleta(HTMLParser):
    VAZIOS = {"meta", "link", "br", "img", "input", "hr", "path", "rect", "circle", "source", "line"}

    def __init__(self):
        super().__init__()
        self.pilha, self.tags, self.erros = [], [], []

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))
        if tag not in self.VAZIOS:
            self.pilha.append(tag)

    def handle_startendtag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))

    def handle_endtag(self, tag):
        if tag in self.VAZIOS:
            return
        if self.pilha and self.pilha[-1] == tag:
            self.pilha.pop()
        else:
            self.erros.append(f"</{tag}> com pilha {self.pilha[-3:]}")


def _coleta() -> Coleta:
    c = Coleta()
    c.feed(HTML)
    return c


def _objeto_js(nome: str) -> str:
    """Texto do literal `var NOME = {...};` ou `[...]` em app.js (casando chaves)."""
    i = JS.index(f"var {nome} = ") + len(f"var {nome} = ")
    abre = JS[i]
    fecha = {"{": "}", "[": "]"}[abre]
    nivel = 0
    for j in range(i, len(JS)):
        if JS[j] == abre:
            nivel += 1
        elif JS[j] == fecha:
            nivel -= 1
            if nivel == 0:
                return JS[i:j + 1]
    raise AssertionError(f"literal {nome} sem fechamento")


def test_html_bem_formado_com_marcos_de_acessibilidade():
    c = _coleta()
    assert not c.erros and not c.pilha, (c.erros, c.pilha)
    nomes = [t for t, _ in c.tags]
    for marco in ("header", "main", "footer", "nav", "h1"):
        assert marco in nomes, f"falta <{marco}>"
    assert nomes.count("h1") == 1
    assert re.search(r'<html lang="pt-BR">', HTML)


def test_secoes_do_brief_existem():
    for sec in ("prologo", "entenda", "manifesto", "principios", "keri", "numeros", "james",
                "horizonte", "metodo", "lacunas", "citar"):
        assert f'id="{sec}"' in HTML, f"seção {sec} sumiu"


def test_sem_base_porque_o_publicador_injeta_a_sua():
    assert "<base" not in HTML.lower()


def test_hreflang_nas_tres_linguas():
    for lang in ("pt", "en", "fr"):
        assert f'href="https://genesisinnovation.io/matematica?lang={lang}"' in HTML
    assert 'hreflang="x-default"' in HTML


def test_recursos_externos_so_do_google_fonts_e_locais_existem():
    for tag, a in _coleta().tags:
        alvo = None
        if tag == "script":
            alvo = a.get("src")
        elif tag == "link" and a.get("rel") in ("stylesheet", "icon", "preload"):
            alvo = a.get("href")
        elif tag in ("img", "source"):
            alvo = a.get("src")
        if not alvo or alvo.startswith("data:"):
            continue
        if alvo.startswith("http"):
            assert alvo.startswith(HOSTS_PERMITIDOS), f"recurso externo fora da lista: {alvo}"
        else:
            assert not alvo.startswith("/"), f"caminho absoluto quebra em /matematica: {alvo}"
            assert (PAGINA / alvo).is_file(), f"recurso local não existe: {alvo}"
    for srcset in re.findall(r'srcset="([^"]+)"', HTML):
        for parte in srcset.split(","):
            caminho = parte.strip().split()[0]
            assert (PAGINA / caminho).is_file(), f"srcset aponta para arquivo inexistente: {caminho}"


def test_pagina_leve_e_imagens_otimizadas():
    codigo = sum((PAGINA / n).stat().st_size for n in ("index.html", "estilo.css", "app.js"))
    assert codigo < 200_000, f"HTML+CSS+JS com {codigo} bytes (teto 200 KB, sem fontes)"
    for img in (PAGINA / "img").glob("*"):
        assert img.stat().st_size < 300_000, f"{img.name} passa de 300 KB"


def test_frase_do_ledger_e_sem_afirmar_tabela_inteira_formalizada():
    assert FRASE_LEDGER in HTML
    assert FRASE_LEDGER in JS  # também nas versões EN/FR do texto fixo
    proibido = re.compile(r"tabela inteira (foi|está|é) (formalmente )?verificada|whole table (is|was|has been) "
                          r"(formally )?verified|entire table (is|was|has been) (formally )?verified", re.I)
    for texto in (HTML, JS):
        assert not proibido.search(texto)


def test_numeros_embutidos_batem_com_o_ledger():
    # Se o ledger mudar, a página embutida (fallback sem dados.json) não pode mentir: regenere os números.
    emb = _objeto_js("DADOS_EMBUTIDOS")
    sup = Counter(c["certification"]["ub"]["state"] for c in CELLS)
    inf = Counter(c["certification"]["lb"]["state"] for c in CELLS)
    exatas = sum(1 for c in CELLS if c["certification"].get("exact"))
    assert f"celulas_total: {len(CELLS)}," in emb
    assert f"exatas: {exatas}," in emb
    assert f"abertas: {len(CELLS) - exatas}," in emb
    for lado, contagem in (("superiores_por_estado", sup), ("inferiores_por_estado", inf)):
        trecho = re.search(lado + r": \{([^}]*)\}", emb).group(1)
        for e in ESTADOS:
            assert f"{e}: {contagem.get(e, 0)}" in trecho, f"{lado}.{e} diverge do ledger"
    assert f'data-d="celulas_total">{len(CELLS)}<' in HTML
    assert f'data-d="exatas">{exatas}<' in HTML


def test_versao_e_doi_embutidos_ou_do_html_ficam_para_tras_do_zenodo_e_do_ledger():
    # A 0.10.0 foi cunhada no Zenodo; página embutida com versão ou DOI da anterior cita o artefato errado,
    # e o "no kernel" do HTML estático tem de ser FORMALIZED + INDEPENDENTLY_REPRODUCED do ledger.
    zen = json.loads((RAIZ / ".zenodo.json").read_text(encoding="utf-8"))["version"]
    doi = DOI_VERSAO[zen]
    emb = _objeto_js("DADOS_EMBUTIDOS")
    assert f'versao: "{zen}"' in emb and f'doi: "{doi}"' in emb
    assert f"version = {{{zen}}}" in HTML and f"doi     = {{{doi}}}" in HTML
    assert f"v{zen})." in HTML  # carimbo "Números embutidos na página"
    sup = Counter(c["certification"]["ub"]["state"] for c in CELLS)
    assert f'data-d="no_lean">{sup["FORMALIZED"] + sup["INDEPENDENTLY_REPRODUCED"]}<' in HTML


def test_destaques_embutidos_batem_com_os_estados_do_ledger():
    por_id = {c["id"]: c for c in CELLS}
    emb = _objeto_js("DADOS_EMBUTIDOS")
    for celula, lb, ub in re.findall(r'celula: "([^"]+)".*?estado_lb: "(\w+)", estado_ub: "(\w+)"', emb):
        cert = por_id[celula]["certification"]
        assert (cert["lb"]["state"], cert["ub"]["state"]) == (lb, ub), f"estados de {celula} divergem"


def test_potencialmente_novo_sao_exatamente_as_tres_celulas():
    novo = _objeto_js("POTENCIALMENTE_NOVO")
    assert sorted(re.findall(r'"(K\d\(\d,\d\))"', novo)) == ["K3(6,2)", "K7(5,3)", "K7(6,4)"]
    marcadas = re.findall(r'<li class="destaque novo"><span class="celula">K<sub>(\d)</sub>\((\d,\d)\)', HTML)
    assert sorted(f"K{q}({nr})" for q, nr in marcadas) == ["K3(6,2)", "K7(5,3)", "K7(6,4)"]


def test_codigo_do_prologo_e_o_arquivo_verificado():
    arquivo = [linha.strip() for linha in (RAIZ / "data/codes/q7_n6_R4_M14.txt").read_text().splitlines() if linha.strip()]
    no_js = re.findall(r'"(\d{6})"', _objeto_js("CODIGO_K764"))
    assert no_js == arquivo


def test_codigo_do_prologo_cobre_tudo_com_raio_4():
    # A página diz ao visitante que o navegador conferiu; o teste confere a mesma coisa aqui.
    codigo = [tuple(int(ch) for ch in w) for w in re.findall(r'"(\d{6})"', _objeto_js("CODIGO_K764"))]
    pior = 0
    for w in range(7 ** 6):
        dig = tuple((w // 7 ** k) % 7 for k in range(6))
        pior = max(pior, min(sum(a != b for a, b in zip(dig, c)) for c in codigo))
        if pior > 4:
            break
    assert pior == 4


def test_milenio_so_poincare_resolvido_e_aviso_presente():
    assert HTML.count('class="status resolvido"') == 1
    bloco = HTML[HTML.index('id="milenio"'):HTML.index("</ul>", HTML.index('id="milenio"'))]
    itens = re.findall(r'<li class="problema"><h3>([^<]+)</h3>.*?<span class="status( resolvido)?">', bloco, re.S)
    assert len(itens) == 7
    assert [n for n, r in itens if r] == ["Conjectura de Poincaré"]
    assert "Não resolvemos nem atacamos nenhum destes problemas" in HTML
    assert "https://www.claymath.org/millennium-problems/" in HTML
    for nome in ("conteudo.exemplo.json", "conteudo.exemplo.en.json", "conteudo.exemplo.fr.json"):
        mil = json.loads((PAGINA / nome).read_text(encoding="utf-8"))["milenio"]
        assert len(mil) == 7
        resolvidos = [m["problema"] for m in mil if re.match(r"\s*(resolvid|solved|résolu)", m["status"], re.I)]
        assert len(resolvidos) == 1 and "Poincaré" in resolvidos[0], nome
        assert all("claymath.org" in m["fonte"] for m in mil)


def test_exemplos_seguem_o_contrato_dos_schemas():
    chaves_c = {"titulo", "subtitulo", "manifesto", "principios", "metodo", "milenio", "james", "keri",
                "lacunas", "links", "explicando", "glossario"}
    for nome in ("conteudo.exemplo.json", "conteudo.exemplo.en.json", "conteudo.exemplo.fr.json"):
        c = json.loads((PAGINA / nome).read_text(encoding="utf-8"))
        assert chaves_c <= set(c), (nome, chaves_c - set(c))
        assert {"resumo", "teoremas"} <= set(c["james"])
        assert {"resumo", "porque_importa"} <= set(c["keri"])
        for k in c["explicando"]["camadas"]:
            assert {"nivel", "titulo", "texto", "analogia", "exemplo"} <= set(k)
    d = json.loads((PAGINA / "dados.exemplo.json").read_text(encoding="utf-8"))
    for k in ("gerado_em", "commit", "versao", "doi", "celulas_total", "exatas", "abertas",
              "superiores_por_estado", "inferiores_por_estado", "destaques"):
        assert k in d, k
    for h in d["destaques"]:
        assert {"celula", "antes", "agora", "estado_lb", "estado_ub", "fonte"} <= set(h)
        assert h["estado_lb"] in ESTADOS and h["estado_ub"] in ESTADOS


def test_todo_rotulo_fixo_tem_traducao_em_ingles_e_frances():
    usados = set(re.findall(r'data-i="([\w.]+)"', HTML)) | set(re.findall(r'data-i-aria="([\w.]+)"', HTML))
    ui = _objeto_js("UI")
    blocos = {lang: ui[ui.index(f"{lang}: {{"):] for lang in ("en", "fr")}
    blocos["en"] = blocos["en"][:blocos["en"].index("\n    fr: {")]
    for lang, bloco in blocos.items():
        definidos = set(re.findall(r'"([\w.]+)":', bloco))
        faltam = sorted(usados - definidos)
        assert not faltam, f"rótulos sem tradução em {lang}: {faltam}"


def test_frases_do_js_existem_nas_tres_linguas():
    s = _objeto_js("S")
    chaves = {}
    for lang in ("pt", "en", "fr"):
        i = s.index(f"{lang}: {{")
        j = s.index("\n    }", i)
        chaves[lang] = set(re.findall(r"\n      (\w+):", s[i:j]))
    assert chaves["pt"] == chaves["en"] == chaves["fr"], {k: chaves["pt"] ^ v for k, v in chaves.items()}


def test_creditos_das_fotografias_no_rodape():
    fotos = sorted(p.name.split("-")[0].split(".")[0] for p in (PAGINA / "img").glob("*.webp") if p.stem != "colapso")
    assert fotos, "sem fotografias"
    assert "Unsplash" in HTML
    assert len(re.findall(r'href="https://unsplash.com/photos/', HTML)) == len(set(fotos))


def test_sem_caminho_de_maquina_na_pagina():
    for f in PAGINA.rglob("*"):
        if f.suffix in (".html", ".css", ".js", ".json"):
            assert not re.search(r"/home/[A-Za-z_]|/Users/[A-Za-z_]", f.read_text(encoding="utf-8")), f
