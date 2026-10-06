#!/usr/bin/env python3
"""Gera a identidade visual do repositório em docs/assets/.

Duas famílias de peça:

* Diagramas e marca em SVG (logo, colapso, escada de estados, cubo, torres): precisam ser nítidos e legíveis
  em qualquer tela. O texto vira contorno (path), porque SVG dentro de <img> no GitHub não carrega webfont;
  cada glifo é definido uma vez em <defs> e reaproveitado com <use>, o que mantém cada arquivo < 60 KB.
* Banner (claro e escuro) e social preview em PNG: uma cena WebGL (three.js) em cena/historia.html, com o
  caos do espaço Z_q^n condensando em quatro esferas de Hamming tangentes, com profundidade, luz e névoa,
  retratada no Chromium headless. O PNG é quantizado para 256 cores (fica < 1 MB sem perda visível).

Fonte: Cormorant Garamond (SIL Open Font License 1.1, Christian Thalmann), do pacote
@fontsource/cormorant-garamond; three.js (MIT) do pacote npm `three`. Os dois são baixados num cache
temporário, fixados por versão; nenhum entra no repositório. Converter glifos em contorno é uso permitido
pela OFL.

Uso (precisa de rede na primeira vez):

    pip install fonttools uharfbuzz cairosvg playwright pillow
    python3 docs/assets/gerar_identidade.py              # escreve todas as peças de SAIDAS
    python3 docs/assets/gerar_identidade.py --so-svg     # só os SVG (sem navegador)
    python3 docs/assets/gerar_identidade.py --previa D   # também renderiza PNG de cada SVG em D

O navegador é o Chromium do Playwright; se a versão instalada do Playwright não casar com a do navegador
baixado, aponte o executável em CHROMIUM_PATH.

Inversa: os arquivos gerados são só os listados em SAIDAS; apagar é `git rm` deles.
"""

from __future__ import annotations

import argparse
import math
import os
import random
import tempfile
import urllib.request
from pathlib import Path

AQUI = Path(__file__).resolve().parent
VERSAO_FONTE = "5.3.0"
URL_FONTE = ("https://cdn.jsdelivr.net/npm/@fontsource/cormorant-garamond@{v}/files/"
             "cormorant-garamond-latin-{peso}-{estilo}.woff")
PESOS = {"r": ("400", "normal"), "m": ("500", "normal"), "sb": ("600", "normal"),
         "i": ("400", "italic"), "mi": ("500", "italic")}
SAIDAS = ("logo.svg", "colapso.svg", "escada-de-estados.svg", "cubo-cobertura.svg", "torres.svg",
          "banner-claro.png", "banner-escuro.png", "social-preview.png")
VERSAO_THREE = "0.170.0"
ARQUIVOS_THREE = ["build/three.module.js"] + [f"examples/jsm/postprocessing/{n}.js" for n in (
    "EffectComposer", "RenderPass", "UnrealBloomPass", "OutputPass", "Pass", "ShaderPass", "MaskPass")] + [
    f"examples/jsm/shaders/{n}.js" for n in ("CopyShader", "LuminosityHighPassShader", "OutputShader")]

# Os contornos são gravados em múltiplos de QUANTUM unidades da fonte (1000 por em), o que encurta
# cada número. Títulos (peso m) usam 3 unidades: 0,4 px no maior (132 px, só no PNG). Texto (r, i) nunca
# passa de ~40 px e usa 6 unidades: 0,24 px nesse tamanho, invisível.
QUANTUM = {"r": 6, "i": 6, "m": 3, "mi": 3, "sb": 3}

# Paleta alinhada com a página (site/matematica): marfim #F6F1E7, grafite #141414, ouro #B8975A.
# "ouro" é o fio fino (traços e esferas); "ourotx" é o mesmo ouro escurecido/clareado para texto pequeno,
# porque #B8975A sobre marfim dá só ~2,4:1 de contraste e legenda precisa de >= 4,5:1.
TEMAS = {
    "claro": {"fundo": "#F6F1E7", "tinta": "#141414", "suave": "#5C564C", "fraco": "#E0D7C4",
              "ouro": "#B8975A", "ouro2": "#B8975A", "ourotx": "#7A5F2F"},
    "escuro": {"fundo": "#141414", "tinta": "#F6F1E7", "suave": "#A9A193", "fraco": "#2B2926",
               "ouro": "#B8975A", "ouro2": "#B8975A", "ourotx": "#C9AB72"},
}

# --------------------------------------------------------------------------------------------
# Tipografia: texto -> contornos reaproveitáveis
# --------------------------------------------------------------------------------------------

def _cache_fontes() -> Path:
    d = Path(os.environ.get("MATEMATICA_CACHE_FONTES", Path(tempfile.gettempdir()) / "matematica-fontes"))
    d.mkdir(parents=True, exist_ok=True)
    return d


def _baixar(peso: str, estilo: str) -> Path:
    destino = _cache_fontes() / f"cg-{VERSAO_FONTE}-{peso}-{estilo}.woff"
    if not destino.exists():
        url = URL_FONTE.format(v=VERSAO_FONTE, peso=peso, estilo=estilo)
        with urllib.request.urlopen(url, timeout=60) as r:  # noqa: S310 (URL fixa)
            destino.write_bytes(r.read())
    return destino


class Tipografo:
    """Converte texto em <use> de glifos definidos uma vez por documento."""

    def __init__(self) -> None:
        import uharfbuzz as hb
        from fontTools.ttLib import TTFont

        self.hb = hb
        self.fontes = {}
        for chave, (peso, estilo) in PESOS.items():
            caminho = _baixar(peso, estilo)
            tt = TTFont(str(caminho))
            tt.flavor = None
            import io
            buf = io.BytesIO()
            tt.save(buf)
            dados = buf.getvalue()
            face = hb.Face(dados)
            fonte = hb.Font(face)
            self.fontes[chave] = (tt, fonte, tt.getGlyphSet(), tt["head"].unitsPerEm, tt.getGlyphOrder())
        self.usados: dict[str, str] = {}
        self.ids: dict[tuple[str, int], str] = {}

    def _gid(self, chave: str, gid: int) -> str:
        from fontTools.pens.recordingPen import DecomposingRecordingPen

        chave_glifo = (chave, gid)
        if chave_glifo in self.ids:
            return self.ids[chave_glifo]
        # id curto (a, b, ..., Z, aa, ab...): cada glifo é referido centenas de vezes por arquivo
        nome = _id_curto(len(self.ids))
        self.ids[chave_glifo] = nome
        if nome not in self.usados:
            tt, _f, gs, _u, ordem = self.fontes[chave]
            pen = DecomposingRecordingPen(gs)
            gs[ordem[gid]].draw(pen)
            self.usados[nome] = _caminho_compacto(pen.value, QUANTUM[chave])
        return nome

    def _shape(self, texto: str, chave: str, tracking: float = 0.0):
        _tt, fonte, _gs, upem, _o = self.fontes[chave]
        buf = self.hb.Buffer()
        buf.add_str(texto)
        buf.guess_segment_properties()
        self.hb.shape(fonte, buf, {"kern": True, "liga": True, "lnum": True})
        glifos, x = [], 0.0
        for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
            glifos.append((info.codepoint, x + pos.x_offset))
            x += pos.x_advance + tracking * upem
        if glifos and tracking:
            x -= tracking * upem
        return glifos, x, upem

    def largura(self, texto: str, tamanho: float, chave: str = "r", tracking: float = 0.0) -> float:
        partes = self._partes(texto, chave)
        total = 0.0
        for t, k in partes:
            _g, x, upem = self._shape(t, k, tracking)
            total += x * tamanho / upem
        return total

    @staticmethod
    def _partes(texto: str, chave: str):
        """`*itálico*` dentro do texto troca para a versão itálica do peso."""
        ital = {"r": "i", "m": "mi", "sb": "mi", "i": "r", "mi": "m"}[chave]
        partes, atual, em = [], "", False
        for c in texto:
            if c == "*":
                if atual:
                    partes.append((atual, ital if em else chave))
                atual, em = "", not em
            else:
                atual += c
        if atual:
            partes.append((atual, ital if em else chave))
        return partes

    def texto(self, texto: str, x: float, y: float, tamanho: float, chave: str = "r",
              cor: str = "currentColor", ancora: str = "start", tracking: float = 0.0,
              opacidade: float | None = None, extra: str = "") -> str:
        w = self.largura(texto, tamanho, chave, tracking)
        if ancora == "middle":
            x -= w / 2
        elif ancora == "end":
            x -= w
        # um grupo por trecho (redondo / itálico): cada fonte tem o seu QUANTUM e, portanto, a sua escala
        grupos, cursor = [], 0.0
        for t, k in self._partes(texto, chave):
            glifos, avanco, upem = self._shape(t, k, tracking)
            q = QUANTUM[k]
            usos = [f'<use href="#{self._gid(k, gid)}" x="{round(gx / q)}"/>'.replace(' x="0"', '')
                    for gid, gx in glifos if self.fontes[k][4][gid] not in ("space", "uni00A0", ".notdef")]
            if usos:
                s = tamanho / upem * q
                gx0 = x + cursor * tamanho / upem
                grupos.append(f'<g transform="translate({gx0:.1f} {y:.1f}) scale({s:.4f} {-s:.4f})">'
                              + "".join(usos) + "</g>")
            cursor += avanco
        if not grupos:
            return ""
        op = f' opacity="{opacidade:g}"' if opacidade is not None else ""
        return f'<g fill="{cor}"{op}{extra}>' + "".join(grupos) + "</g>"

    def paragrafo(self, texto: str, x: float, y: float, largura_max: float, tamanho: float,
                  entrelinha: float, **kw) -> tuple[str, float]:
        """Quebra por largura medida (não por número de caracteres) e devolve (svg, y_final)."""
        palavras, linhas, atual = texto.split(), [], ""
        chave = kw.get("chave", "r")
        for p in palavras:
            cand = f"{atual} {p}".strip()
            # o asterisco é marcação; medir com ele aberto/fechado dá a largura certa por parte
            if self.largura(_fecha(cand), tamanho, chave) <= largura_max or not atual:
                atual = cand
            else:
                linhas.append(atual)
                atual = p
        if atual:
            linhas.append(atual)
        # reabre itálico que atravessa a quebra de linha
        out, aberto = [], False
        for linha in linhas:
            if aberto:
                linha = "*" + linha
            aberto = linha.count("*") % 2 == 1
            out.append(_fecha(linha))
        svg = "".join(self.texto(linha, x, y + i * entrelinha, tamanho, **kw) for i, linha in enumerate(out))
        return svg, y + (len(out) - 1) * entrelinha

    def defs(self) -> str:
        return "".join(f'<path id="{k}" d="{d}"/>' for k, d in sorted(self.usados.items()))

    def reiniciar(self) -> None:
        self.usados, self.ids = {}, {}


_LETRAS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"


def _id_curto(n: int) -> str:
    if n < len(_LETRAS):
        return _LETRAS[n]
    return _id_curto(n // len(_LETRAS) - 1) + _LETRAS[n % len(_LETRAS)]


def _num(v: float) -> str:
    return str(round(v))


def _par(dx: float, dy: float) -> str:
    a, b = _num(dx), _num(dy)
    return a + ("" if b.startswith("-") else " ") + b


def _caminho_compacto(cmds, q: int) -> str:
    """Serializa os contornos em comandos relativos e inteiros: ~40% menor que o SVGPathPen absoluto.

    Quadráticas encadeadas do TrueType (vários pontos fora da curva) viram uma sequência de q com o ponto
    médio implícito explicitado, que é o que a especificação do formato define.
    """
    out, cx, cy, sx, sy = [], 0, 0, 0, 0
    for op, pts in cmds:
        # arredonda no absoluto antes de diferenciar: assim o erro não se acumula ao longo do contorno
        pts = tuple(None if p is None else (round(p[0] / q), round(p[1] / q)) for p in pts)
        if op == "moveTo":
            (x, y), = pts
            out.append("m" + _par(x - cx, y - cy))
            cx, cy, sx, sy = x, y, x, y
        elif op == "lineTo":
            (x, y), = pts
            out.append("l" + _par(x - cx, y - cy))
            cx, cy = x, y
        elif op == "qCurveTo":
            pts = list(pts)
            if pts[-1] is None:  # contorno só de pontos fora da curva
                pts = pts[:-1]
                pts.append((round((pts[-1][0] + pts[0][0]) / 2), round((pts[-1][1] + pts[0][1]) / 2)))
            controles, fim = pts[:-1], pts[-1]
            for k, c in enumerate(controles):
                if k + 1 < len(controles):
                    n = controles[k + 1]
                    e = (round((c[0] + n[0]) / 2), round((c[1] + n[1]) / 2))
                else:
                    e = fim
                out.append("q" + _par(c[0] - cx, c[1] - cy) + " " + _par(e[0] - cx, e[1] - cy))
                cx, cy = e
        elif op == "curveTo":
            c1, c2, e = pts
            out.append("c" + " ".join(_par(p[0] - cx, p[1] - cy) for p in (c1, c2, e)))
            cx, cy = e
        elif op in ("closePath", "endPath"):
            out.append("z")
            cx, cy = sx, sy
    return "".join(out).replace(" -", "-")


def _fecha(s: str) -> str:
    return s + "*" if s.count("*") % 2 else s


def documento(tip: Tipografo, w: int, h: int, titulo: str, desc: str, corpo: str, defs: str = "") -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="titulo descricao">'
            f'<title id="titulo">{titulo}</title><desc id="descricao">{desc}</desc>'
            f'<defs>{tip.defs()}{defs}</defs>{corpo}</svg>\n')


# --------------------------------------------------------------------------------------------
# Motivo: os pontos dispersos de Z_q^n colapsam em poucas esferas de Hamming tangentes
# --------------------------------------------------------------------------------------------

def _ordem(cx: float, cy: float, r: float, linhas: int = 2, colunas: int = 2):
    """Esferas tangentes (centros a 2r) e, em cada uma, a grade 3x3 de palavras que ela cobre.

    O passo da grade é r/sqrt(2): as quatro palavras dos cantos ficam exatamente sobre a esfera
    (distância = raio), as outras dentro. Devolve (centros, palavras).
    """
    d = r / math.sqrt(2)
    centros = [(cx + (i - (colunas - 1) / 2) * 2 * r, cy + (j - (linhas - 1) / 2) * 2 * r)
               for j in range(linhas) for i in range(colunas)]
    palavras = [(x + a * d, y + b * d) for x, y in centros for a in (-1, 0, 1) for b in (-1, 0, 1)]
    return centros, palavras


def _desenha_ordem(centros, palavras, r: float, c: dict, ponto: float, traco: float) -> str:
    out = [f'<g fill="none" stroke="{c["ouro"]}" stroke-width="{traco}">']
    out += [f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}"/>' for x, y in centros]
    out.append(f'</g><g fill="{c["tinta"]}">')
    out += [f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{ponto:.1f}"/>' for x, y in palavras if (x, y) not in centros]
    out.append(f'</g><g fill="{c["ouro"]}">')
    out += [f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{ponto * 1.5:.1f}"/>' for x, y in centros]
    out.append("</g>")
    return "".join(out)


# --------------------------------------------------------------------------------------------
# Peças em SVG
# --------------------------------------------------------------------------------------------

def logo(tip: Tipografo) -> str:
    tip.reiniciar()
    c = TEMAS["escuro"]
    centros, palavras = _ordem(256, 256, 92)
    corpo = (f'<rect width="512" height="512" rx="112" fill="{c["fundo"]}"/>'
             + _desenha_ordem(centros, palavras, 92, c, 7, 3.2))
    return documento(tip, 512, 512, "Matemática — marca",
                     "Quatro esferas de Hamming tangentes, em fio de ouro, cobrindo uma grade de 36 palavras: "
                     "toda palavra está a distância no máximo R de um centro. Fundo quase-preto.", corpo)


def _cartao(W: int, H: int, c: dict) -> str:
    return (f'<rect width="{W}" height="{H}" rx="20" fill="{c["fundo"]}"/>'
            f'<rect x="12.5" y="12.5" width="{W - 25}" height="{H - 25}" rx="12" fill="none" '
            f'stroke="{c["fraco"]}"/>')


def _icone_descoberta(cx, cy, c):
    """Caos: pontos dispersos e o rastro tracejado de uma busca que tateia até achar."""
    rnd = random.Random(3)
    out = [f'<g fill="{c["tinta"]}">']
    for _ in range(70):
        a, r = rnd.uniform(0, 2 * math.pi), 52 * math.sqrt(rnd.random())
        out.append(f'<circle cx="{cx + r * math.cos(a):.1f}" cy="{cy + r * math.sin(a):.1f}" '
                   f'r="{rnd.uniform(0.7, 2.0):.1f}" opacity="{rnd.uniform(.3, .9):.2f}"/>')
    out.append("</g>")
    pts = [(cx - 46, cy + 26), (cx - 18, cy - 4), (cx - 32, cy - 34), (cx + 4, cy - 18), (cx + 0, cy + 16),
           (cx + 30, cy + 4), (cx + 24, cy - 26)]
    d = "M" + " L".join(f"{x:.0f} {y:.0f}" for x, y in pts)
    out.append(f'<path d="{d}" fill="none" stroke="{c["ouro"]}" stroke-width="1" stroke-dasharray="2 4"/>')
    out.append(f'<circle cx="{pts[-1][0]}" cy="{pts[-1][1]}" r="3.5" fill="{c["ouro"]}"/>')
    return "".join(out)


def _icone_certificado(cx, cy, c):
    """Certificado: o objeto achado, quatro esferas tangentes sobre as suas palavras."""
    centros, palavras = _ordem(cx, cy, 27)
    return _desenha_ordem(centros, palavras, 27, c, 1.8, 1)


def _icone_verificacao(cx, cy, c):
    """Verificação: cada palavra ligada ao seu centro por um fio; conferir é medir cada fio."""
    centros, palavras = _ordem(cx, cy, 27)
    out = [f'<g stroke="{c["ouro"]}" stroke-width=".8">']
    for k, (x, y) in enumerate(palavras):
        ox, oy = centros[k // 9]
        if (x, y) != (ox, oy):
            out.append(f'<line x1="{ox:.1f}" y1="{oy:.1f}" x2="{x:.1f}" y2="{y:.1f}"/>')
    out.append("</g>")
    out.append(_desenha_ordem(centros, palavras, 27, {**c, "ouro": c["fraco"]}, 1.8, 1))
    return "".join(out)


def _icone_ledger(cx, cy, c):
    """Ledger: a escada de cinco degraus, o último em ouro."""
    pw, ph, x0, y0 = 18, 18, cx - 45, cy + 45
    d = f"M{x0} {y0}" + "".join(f" V{y0 - (k + 1) * ph} H{x0 + (k + 1) * pw}" for k in range(5)) + f" V{y0} Z"
    return (f'<path d="{d}" fill="{c["fraco"]}" opacity=".6" stroke="{c["tinta"]}" stroke-width="1.2"/>'
            f'<path d="M{x0 + 4 * pw} {y0 - 5 * ph} H{x0 + 5 * pw}" stroke="{c["ouro"]}" stroke-width="3"/>')


def colapso(tip: Tipografo) -> str:
    tip.reiniciar()
    c = TEMAS["claro"]
    W, H = 1280, 600
    t = [_cartao(W, H, c)]
    t.append(tip.texto("O MÉTODO", 72, 82, 14, "m", c["ourotx"], tracking=0.24))
    t.append(tip.texto("Descoberta cara, verificação barata", 72, 128, 44, "r", c["tinta"]))
    etapas = [
        ("I", "Descoberta", _icone_descoberta,
         "Busca local, SAT, LP e programação inteira. Cara e heurística: acha, mas não garante."),
        ("II", "Certificado", _icone_certificado,
         "O que a busca devolve vira objeto conferível: código explícito, refutação LRAT, VeriPB ou Farkas, "
         "fixado por sha256."),
        ("III", "Verificação", _icone_verificacao,
         "Um juiz exato e barato confere o certificado: o verificador em C de tools/verify e o kernel do Lean 4."),
        ("IV", "Ledger", _icone_ledger,
         "Cada cota sobe de estado só com a evidência que a confere, em ledger/cells.json. Nada sobe à mão."),
    ]
    col_w, x0, gap = 262, 72, 30
    for k, (num, nome, icone, texto) in enumerate(etapas):
        x = x0 + k * (col_w + gap)
        cx = x + col_w / 2
        t.append(tip.texto(num, cx, 196, 20, "m", c["ourotx"], ancora="middle", tracking=0.1))
        t.append(icone(cx, 278, c))
        t.append(tip.texto(nome, cx, 376, 30, "r", c["tinta"], ancora="middle"))
        par, _ = tip.paragrafo(texto, x + 8, 408, col_w - 16, 17.5, 24, chave="r", cor=c["suave"])
        t.append(par)
        if k < 3:
            ax = x + col_w + gap / 2
            t.append(f'<path d="M{ax - 9} 278 h18 m-6 -5 l6 5 l-6 5" fill="none" stroke="{c["ouro"]}" '
                     f'stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/>')
    # cunha de custo: larga na descoberta, fio na verificação
    y = 520
    xa, xb = x0 + 20, x0 + 3 * (col_w + gap) - gap - 20
    t.append(f'<path d="M{xa} {y - 5} L{xb} {y - 0.5} L{xb} {y + 0.5} L{xa} {y + 5} Z" fill="{c["ouro2"]}" '
             f'opacity=".7"/>')
    t.append(tip.texto("CUSTO DE ACHAR", xa, y - 20, 12, "m", c["suave"], tracking=0.2))
    t.append(tip.texto("CUSTO DE CONFERIR", xb, y - 20, 12, "m", c["suave"], ancora="end", tracking=0.2))
    t.append(tip.texto("Achar é caro; conferir é exato e barato. É o P = NP como norte de engenharia, "
                       "não como teorema.", W / 2, 566, 18, "r", c["tinta"], ancora="middle", opacidade=0.85))
    desc = ("Diagrama do método em quatro etapas, da esquerda para a direita. I. Descoberta: busca local, SAT, LP "
            "e programação inteira, cara e heurística. II. Certificado: código explícito, refutação LRAT, VeriPB "
            "ou Farkas, fixado por sha256. III. Verificação: o verificador exato em C de tools/verify e o kernel "
            "do Lean 4. IV. Ledger: cada cota sobe de estado só com a evidência que a confere, em "
            "ledger/cells.json. Uma cunha de ouro afina da descoberta à verificação: achar é caro, conferir é "
            "barato.")
    return documento(tip, W, H, "O método: descoberta cara, verificação barata", desc, "".join(t))


# Uma linha por degrau, conferida contra a tabela de ledger/README.md e o comentário de ledger/build.py.
ESTADOS = [
    ("CLAIMED", "Está numa fonte publicada de versão congelada; nada foi conferido aqui."),
    ("WITNESS_CHECKED", "Certificado conferido por verificador exato fora do Lean: código explícito "
                        "(tools/verify) ou refutação LRAT de inexistência."),
    ("CERTIFICATE_VERIFIED", "Inexistência inteira coberta por certificados LRAT, VeriPB ou Farkas fixados por "
                             "sha256, conferidos por verificador que não é o gerador, após red team. Sem Lean."),
    ("FORMALIZED", "Teorema do Lean checado pelo kernel, com exatamente esta cota e sem hipótese pendente."),
    ("INDEPENDENTLY_REPRODUCED", "Formalizada e conferida por um segundo verificador independente, executado: "
                                 "o código de data/codes/ passa no tools/verify em C."),
]


def escada(tip: Tipografo) -> str:
    tip.reiniciar()
    c = TEMAS["claro"]
    W, H = 1280, 740
    t = [_cartao(W, H, c)]
    t.append(tip.texto("O LEDGER, COTA POR COTA", 72, 82, 14, "m", c["ourotx"], tracking=0.24))
    t.append(tip.texto("A escada de estados", 72, 128, 44, "r", c["tinta"]))
    t.append(tip.texto("Cumulativa: cada degrau exige o anterior. Calculada por ledger/build.py, nunca à mão.",
                       72, 162, 18, "r", c["suave"]))
    base, ph, pw, x0, xt = 652, 92, 62, 72, 468
    # silhueta da escada, preenchida de leve
    pts = [f"{x0} {base}"]
    for k in range(5):
        pts += [f"{x0 + k * pw} {base - (k + 1) * ph}", f"{x0 + (k + 1) * pw} {base - (k + 1) * ph}"]
    pts.append(f"{x0 + 5 * pw} {base}")
    t.append(f'<polygon points="{" ".join(pts)}" fill="{c["fraco"]}" opacity=".35"/>')
    for k, (nome, texto) in enumerate(ESTADOS):
        y_topo = base - (k + 1) * ph
        x = x0 + k * pw
        lateral = nome == "CERTIFICATE_VERIFIED"
        # o degrau de CERTIFICATE_VERIFIED é tracejado: só existe para a cota inferior
        dash = ' stroke-dasharray="5 5"' if lateral else ""
        cor = c["ouro"] if k == 4 else c["tinta"]
        t.append(f'<path d="M{x} {y_topo + ph} V{y_topo} H{x + pw}" fill="none" stroke="{cor}" '
                 f'stroke-width="1.8"{dash}/>')
        t.append(tip.texto(["I", "II", "III", "IV", "V"][k], x + pw / 2, y_topo + 30, 17, "m", c["ourotx"],
                           ancora="middle"))
        ty = y_topo + 30
        t.append(f'<line x1="{x + pw + 10}" y1="{ty - 6}" x2="{xt - 20}" y2="{ty - 6}" stroke="{c["fraco"]}" '
                 f'stroke-width="1"{dash}/>')
        t.append(f'<circle cx="{xt - 20}" cy="{ty - 6}" r="2.2" fill="{cor}"/>')
        t.append(tip.texto(nome, xt, ty, 19, "m", c["ourotx"] if k == 4 else cor, tracking=0.12))
        if lateral:
            wn = tip.largura(nome, 19, "m", 0.12)
            t.append(tip.texto("SÓ COTA INFERIOR", xt + wn + 18, ty - 1, 12, "m", c["ourotx"], tracking=0.2))
        par, _ = tip.paragrafo(texto, xt, ty + 25, W - xt - 72, 17, 22, chave="r", cor=c["suave"])
        t.append(par)
    t.append(f'<line x1="{x0}" y1="{base}" x2="{W - 72}" y2="{base}" stroke="{c["tinta"]}" stroke-width="1"/>')
    t.append(tip.texto("A machine-checked ledger of covering-code upper bounds, with formally certified exact "
                       "entries.", 72, 690, 17, "r", c["tinta"]))
    t.append(tip.texto("As cotas inferiores são, quase todas, herdadas da literatura (CLAIMED).",
                       72, 714, 15, "r", c["suave"]))
    desc = ("Escada de cinco degraus, de baixo para cima. " + " ".join(
        f"{i + 1}. {n}: {tx}" for i, (n, tx) in enumerate(ESTADOS))
        + " O degrau CERTIFICATE_VERIFIED vale só para a cota inferior. A escada é cumulativa. A machine-checked "
          "ledger of covering-code upper bounds, with formally certified exact entries; as cotas inferiores são, "
          "quase todas, herdadas da literatura.")
    return documento(tip, W, H, "A escada de estados do ledger", desc, "".join(t))


# --------------------------------------------------------------------------------------------
# Para leigos: o cubo Q3 e a analogia das torres
# --------------------------------------------------------------------------------------------

ARDOSIA = "#3F6878"   # segunda cor das esferas: ardósia, distinta do ouro também para daltonismo


def _k_indice(tip: Tipografo, x: float, y: float, tam: float, q: str, resto: str, cor: str, chave: str = "r") -> str:
    """Escreve K com índice q rebaixado, seguido de `resto` (a fonte não tem os dígitos subscritos)."""
    wk = tip.largura("K", tam, chave)
    wq = tip.largura(q, tam * 0.62, chave)
    return (tip.texto("K", x, y, tam, chave, cor) + tip.texto(q, x + wk + 1, y + tam * 0.22, tam * 0.62, chave, cor)
            + tip.texto(resto, x + wk + wq + 3, y, tam, chave, cor))


ROTULOS_CUBO = {"000": (-26, 44, "end"), "100": (0, 52, "middle"), "010": (-30, -18, "end"),
                "110": (-22, -24, "end"), "001": (24, -16, "start"), "011": (-26, -22, "end"),
                "111": (28, -22, "start"), "101": (28, 44, "start")}


def cubo(tip: Tipografo) -> str:
    tip.reiniciar()
    c = TEMAS["claro"]
    W, H = 1280, 640
    t = [_cartao(W, H, c)]
    # projeção oblíqua do cubo: bit 1 -> direita, bit 2 -> cima, bit 3 -> profundidade
    S, ox, oy = 230, 150, 500

    def pos(v: str) -> tuple[float, float]:
        a, b, cc = (int(ch) for ch in v)
        return ox + a * S + cc * S * 0.52, oy - b * S - cc * S * 0.36

    vertices = [f"{i:03b}" for i in range(8)]
    viz = lambda u, v: sum(x != y for x, y in zip(u, v)) == 1  # noqa: E731
    esferas = {"000": c["ouro"], "111": ARDOSIA}
    dono = {v: ("000" if v.count("1") <= 1 else "111") for v in vertices}
    # arestas: as que saem de um centro tomam a cor dele; as outras ficam em traço fino
    for i, u in enumerate(vertices):
        for v in vertices[i + 1:]:
            if not viz(u, v):
                continue
            (x1, y1), (x2, y2) = pos(u), pos(v)
            centro = u if u in esferas else v if v in esferas else None
            if centro:
                t.append(f'<line x1="{x1:.0f}" y1="{y1:.0f}" x2="{x2:.0f}" y2="{y2:.0f}" '
                         f'stroke="{esferas[centro]}" stroke-width="3.2" stroke-linecap="round"/>')
            else:
                t.append(f'<line x1="{x1:.0f}" y1="{y1:.0f}" x2="{x2:.0f}" y2="{y2:.0f}" '
                         f'stroke="{c["suave"]}" stroke-width="1.2" stroke-dasharray="4 5" opacity=".7"/>')
    for v in vertices:
        x, y = pos(v)
        cor = esferas[dono[v]]
        t.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="30" fill="{cor}" opacity=".16"/>')
        if v in esferas:
            t.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="13" fill="{cor}"/>'
                     f'<circle cx="{x:.0f}" cy="{y:.0f}" r="19" fill="none" stroke="{cor}" stroke-width="1.5"/>')
        else:
            t.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="8" fill="{c["fundo"]}" stroke="{cor}" stroke-width="3"/>')
        # rótulo em posição escolhida à mão para não cruzar nenhuma aresta
        dx, dy, anc = ROTULOS_CUBO[v]
        t.append(tip.texto(v, x + dx, y + dy, 24, "m", c["tinta"], ancora=anc, tracking=0.06))
    # texto à direita
    xt = 720
    t.append(tip.texto("PARA QUEM CHEGA AGORA", xt, 112, 14, "m", c["ourotx"], tracking=0.24))
    t.append(tip.texto("Cobrir o cubo com duas esferas", xt, 160, 40, "r", c["tinta"]))
    par, yf = tip.paragrafo("Cada vértice do cubo é uma palavra de 3 bits. Duas palavras são vizinhas quando "
                            "diferem em um só bit: estão a distância de Hamming 1. A esfera de raio 1 de um centro "
                            "é ele mais os seus três vizinhos.", xt, 204, W - xt - 72, 19, 27, chave="r",
                            cor=c["suave"])
    t.append(par)
    y = yf + 56
    for centro, membros in (("000", "000, 001, 010, 100"), ("111", "111, 110, 101, 011")):
        t.append(f'<circle cx="{xt + 10}" cy="{y - 6}" r="9" fill="{esferas[centro]}"/>')
        t.append(tip.texto(f"centro {centro} cobre {membros}", xt + 32, y, 19, "r", c["tinta"]))
        y += 36
    t.append(f'<line x1="{xt}" y1="{y + 4}" x2="{xt + 72}" y2="{y + 4}" stroke="{c["ouro"]}" stroke-width="1.5"/>')
    t.append(_k_indice(tip, xt, y + 54, 34, "2", "(3,1) = 2", c["tinta"], "m"))
    t.append(tip.texto("duas palavras cobrem todas as oito", xt, y + 90, 22, "r", c["tinta"]))
    t.append(tip.texto("Uma só não basta: cada esfera cobre 4 das 8 palavras.", xt, y + 122, 17, "r", c["suave"]))
    desc = ("O cubo de três dimensões com as oito palavras binárias de 3 bits nos vértices. A esfera de Hamming "
            "de raio 1 com centro 000, em ouro, cobre 000, 001, 010 e 100. A esfera com centro 111, em ardósia, "
            "cobre 111, 110, 101 e 011. As arestas que saem de cada centro estão na cor da sua esfera. Legenda: "
            "K₂(3,1) = 2: duas palavras cobrem todas as oito; uma só não basta, pois cada esfera cobre 4 das 8.")
    return documento(tip, W, H, "K₂(3,1) = 2: duas palavras cobrem todas as oito", desc, "".join(t))


def torres(tip: Tipografo) -> str:
    tip.reiniciar()
    c = TEMAS["claro"]
    W, H = 1280, 640
    t = [_cartao(W, H, c)]
    # vila: grade 8 x 6 de casas; quatro torres cujo alcance (mesmo raio) cobre todas
    gx0, gy0, esp, cols, lins = 700, 155, 66, 8, 6
    casas = [(gx0 + i * esp, gy0 + j * esp) for j in range(lins) for i in range(cols)]
    # torres entre duas casas da linha do meio de cada quadrante (sem encostar em casa nenhuma)
    torres_pos = [(gx0 + 1.5 * esp, gy0 + 1.0 * esp - 3), (gx0 + 5.5 * esp, gy0 + 1.0 * esp + 4),
                  (gx0 + 1.5 * esp, gy0 + 4.0 * esp + 3), (gx0 + 5.5 * esp, gy0 + 4.0 * esp - 4)]
    raio = max(min(math.dist(h, tp) for tp in torres_pos) for h in casas) + 10
    # a figura só sai se a cobertura for verdadeira: toda casa dentro do alcance de alguma torre
    assert all(any(math.dist(h, tp) <= raio for tp in torres_pos) for h in casas)
    for tx, ty in torres_pos:
        t.append(f'<circle cx="{tx:.0f}" cy="{ty:.0f}" r="{raio:.0f}" fill="{c["ouro2"]}" opacity=".07"/>'
                 f'<circle cx="{tx:.0f}" cy="{ty:.0f}" r="{raio:.0f}" fill="none" stroke="{c["ouro"]}" '
                 f'stroke-width="1.3" stroke-dasharray="6 5"/>')
    for hx, hy in casas:
        t.append(f'<use href="#casa" x="{hx:.0f}" y="{hy:.0f}" fill="{c["tinta"]}"/>')
    for tx, ty in torres_pos:
        t.append(f'<use href="#torre" x="{tx:.0f}" y="{ty:.0f}" fill="{c["ourotx"]}"/>')
    defs = ('<path id="casa" d="M-11 8V-3L0-12L11-3V8zM-3 8V2h6v6z" fill-rule="evenodd"/>'
            '<path id="torre" d="M-8 20L-5-9h10L8 20zM-10-9h20v-5h-4v-5h-4v5h-4v-5h-4v5h-4zM-2 8h4v9h-4z" '
            'fill-rule="evenodd"/>')
    xt = 72
    t.append(tip.texto("A MESMA IDEIA, SEM FÓRMULA", xt, 112, 14, "m", c["ourotx"], tracking=0.24))
    t.append(tip.texto("Casas e torres", xt, 166, 48, "r", c["tinta"]))
    par, yf = tip.paragrafo("Toda casa da vila precisa estar ao alcance de alguma torre. Quantas torres bastam? "
                            "Nesta vila, quatro dão conta, e qualquer pessoa confere: basta olhar casa por casa.",
                            xt, 214, 480, 19, 27, chave="r", cor=c["suave"])
    t.append(par)
    par2, yf = tip.paragrafo("Nos códigos de cobertura, as casas são todas as palavras, as torres são as palavras "
                             "do código e o alcance é o raio R, medido na distância de Hamming.", xt, yf + 44, 480, 19, 27,
                             chave="r", cor=c["suave"])
    t.append(par2)
    t.append(f'<line x1="{xt}" y1="{yf + 44}" x2="{xt + 72}" y2="{yf + 44}" stroke="{c["ouro"]}" '
             f'stroke-width="1.5"/>')
    t.append(tip.texto("Achar torres é fácil de conferir;", xt, yf + 92, 26, "r", c["tinta"]))
    t.append(tip.texto("provar que não dá com menos é o difícil.", xt, yf + 128, 26, "r", c["tinta"]))
    desc = ("Analogia ilustrada. Uma vila de 48 casas em grade de 8 por 6 e quatro torres de ouro; o alcance de "
            "cada torre é um círculo tracejado, e juntos os quatro círculos cobrem todas as casas. Texto: toda casa "
            "precisa estar ao alcance de alguma torre; conferir uma solução é fácil, casa por casa. Nos códigos de "
            "cobertura, as casas são as palavras, as torres são as palavras do código e o alcance é a distância "
            "de Hamming R. Legenda: achar torres é fácil de conferir; provar que não dá com menos é o difícil.")
    return documento(tip, W, H, "Casas e torres: a ideia da cobertura sem fórmula", desc, "".join(t), defs)


# --------------------------------------------------------------------------------------------
# Peças em PNG: a cena WebGL retratada no Chromium headless
# --------------------------------------------------------------------------------------------

def _preparar_cena(destino: Path) -> None:
    """Monta o diretório servido: a cena, o three.js e as duas fontes que o título usa."""
    import shutil

    shutil.copy(AQUI / "cena" / "historia.html", destino / "historia.html")
    cache = _cache_fontes() / f"three-{VERSAO_THREE}"
    for rel in ARQUIVOS_THREE:
        alvo = cache / rel
        if not alvo.exists():
            alvo.parent.mkdir(parents=True, exist_ok=True)
            url = f"https://cdn.jsdelivr.net/npm/three@{VERSAO_THREE}/{rel}"
            with urllib.request.urlopen(url, timeout=60) as r:  # noqa: S310 (URL fixa)
                alvo.write_bytes(r.read())
        (destino / "three" / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(alvo, destino / "three" / rel)
    (destino / "fontes").mkdir()
    for peso, estilo in (("500", "normal"), ("400", "italic")):
        shutil.copy(_baixar(peso, estilo), destino / "fontes" / f"cg-{peso}-{estilo}.woff")


def renderizar_cena() -> dict[str, bytes]:
    import functools
    import http.server
    import io
    import threading

    from PIL import Image
    from playwright.sync_api import sync_playwright

    pecas = {"banner-claro.png": ("claro", "banner", 1280, 400, 2),
             "banner-escuro.png": ("escuro", "banner", 1280, 400, 2),
             "social-preview.png": ("escuro", "social", 1280, 640, 1)}
    saida = {}
    with tempfile.TemporaryDirectory() as tmp:
        _preparar_cena(Path(tmp))
        class Silencioso(http.server.SimpleHTTPRequestHandler):
            def log_message(self, *a, **k) -> None:  # o log de cada GET só esconde o que importa
                pass

        handler = functools.partial(Silencioso, directory=tmp)
        srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        try:
            with sync_playwright() as p:
                exe = os.environ.get("CHROMIUM_PATH") or None
                nav = p.chromium.launch(executable_path=exe,
                                        args=["--use-angle=swiftshader", "--enable-unsafe-swiftshader"])
                for nome, (tema, peca, w, h, escala) in pecas.items():
                    pg = nav.new_page(viewport={"width": w, "height": h}, device_scale_factor=escala)
                    erros: list[str] = []
                    pg.on("pageerror", lambda e, erros=erros: erros.append(str(e)))
                    pg.goto(f"http://127.0.0.1:{srv.server_port}/historia.html?tema={tema}&peca={peca}")
                    pg.wait_for_function("document.title === 'pronto'", timeout=120_000)
                    if erros:
                        raise SystemExit(f"{nome}: erro na cena: {erros}")
                    bruto = pg.screenshot()
                    pg.close()
                    # 256 cores com difusão: a cena é quase monocromática + ouro, e cai de ~1 MB para ~300 KB
                    im = Image.open(io.BytesIO(bruto)).convert("RGB").quantize(
                        colors=256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.FLOYDSTEINBERG)
                    buf = io.BytesIO()
                    im.save(buf, format="PNG", optimize=True)
                    saida[nome] = buf.getvalue()
                nav.close()
        finally:
            srv.shutdown()
    return saida


# --------------------------------------------------------------------------------------------

def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--previa", type=Path, help="diretório onde renderizar PNG de cada SVG para conferência")
    ap.add_argument("--so-svg", action="store_true", help="não abre o navegador: gera só os SVG")
    a = ap.parse_args()

    tip = Tipografo()
    pecas = {"logo.svg": logo(tip), "colapso.svg": colapso(tip), "escada-de-estados.svg": escada(tip),
             "cubo-cobertura.svg": cubo(tip), "torres.svg": torres(tip)}
    for nome, svg in pecas.items():
        (AQUI / nome).write_text(svg, encoding="utf-8")
        print(f"{nome}: {len(svg.encode()) / 1000:.1f} KB")
    if not a.so_svg:
        for nome, png in renderizar_cena().items():
            (AQUI / nome).write_bytes(png)
            print(f"{nome}: {len(png) / 1000:.1f} KB")
    if a.previa:
        import cairosvg

        a.previa.mkdir(parents=True, exist_ok=True)
        for nome, svg in pecas.items():
            cairosvg.svg2png(bytestring=svg.encode(), write_to=str(a.previa / nome.replace(".svg", ".png")))


if __name__ == "__main__":
    main()
