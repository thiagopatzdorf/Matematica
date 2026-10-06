#!/usr/bin/env python3
"""Gera o bloco "Resultados" do README a partir do ledger (só biblioteca padrão).

Por que existe: o README da raiz repetia à mão números do ledger e divergia dele (dizia 520 exatas e
13 células com teorema próprio quando `ledger/cells.json` já tinha 523 e 14). Aqui o bloco é derivado,
e um teste (`tests/test_gerar_resultados.py`) falha se o README commitado não bater com o gerado.

Fontes: `ledger/cells.json` (contado por `ledger/cobertura.py`, a mesma função que gera o
`ledger/COBERTURA.md`), `data/codes/` (sha256 conferido contra o ledger) e `CITATION.cff` (versão e DOI).
Determinístico: mesma entrada, mesmos bytes (sem data de geração, ordem fixa).

    python3 tools/site/gerar_resultados.py [--lingua en|pt-BR|fr]   # imprime o bloco
    python3 tools/site/gerar_resultados.py --escrever          # README.md, README.pt-BR.md, README.fr.md
    python3 tools/site/gerar_resultados.py --checar            # sai 1 se algum estiver desatualizado
    python3 tools/site/gerar_resultados.py --badges docs/badges
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "ledger"))
# Reuso: a contagem por estado é a do COBERTURA.md; duas contagens da mesma coisa divergem.
from cobertura import contar  # noqa: E402
from build import ESTADOS  # noqa: E402

INICIO = "<!-- RESULTADOS:INICIO -->"
FIM = "<!-- RESULTADOS:FIM -->"
FRASE_LEDGER = "A machine-checked ledger of covering-code upper bounds, with formally certified exact entries."
KERNEL = ("FORMALIZED", "INDEPENDENTLY_REPRODUCED")  # estados em que a cota é teorema do kernel do Lean
# A busca bibliográfica da v0.9 não vive no ledger; o doc é a fonte da frase "potencialmente novo".
DOC_NOVIDADE = "docs/exatos/NOVIDADE_V09.md"


class SemMarcas(Exception):
    """O arquivo alvo não tem o par de marcas RESULTADOS."""


# ---------------------------------------------------------------- leitura


def ler_ledger(raiz: Path = RAIZ) -> dict:
    return json.loads((raiz / "ledger" / "cells.json").read_text(encoding="utf-8"))


def ler_citacao(raiz: Path = RAIZ) -> dict:
    """version e doi do CITATION.cff (chaves de topo, uma por linha; não precisa de YAML)."""
    out = {}
    for linha in (raiz / "CITATION.cff").read_text(encoding="utf-8").splitlines():
        m = re.match(r"^(version|doi):\s*['\"]?([^'\"\s]+)", linha)
        if m:
            out[m.group(1)] = m.group(2)
    return out


def conferir_codigos(cells: list[dict], raiz: Path = RAIZ) -> dict:
    """Arquivos de data/codes e quantos são a testemunha atual de uma cota do ledger (sha256 recalculado)."""
    shas = {c["ours_lean"]["sha256"] for c in cells if c["ours_lean"] and c["ours_lean"].get("sha256")}
    arquivos = sorted((raiz / "data" / "codes").glob("*.txt"))
    no_ledger = sum(hashlib.sha256(p.read_bytes()).hexdigest() in shas for p in arquivos)
    return {"arquivos": len(arquivos), "testemunhas_do_ledger": no_ledger}


# ---------------------------------------------------------------- números


def numeros(ledger: dict, raiz: Path = RAIZ) -> dict:
    cells = ledger["cells"]
    total = sum(contar(cells).values(), Counter())
    ub = {e: total[f"ub:{e}"] for e in ESTADOS}
    lb = {e: total[f"lb:{e}"] for e in ESTADOS}
    novas = [c for c in cells if c["certification"]["exact"] and not c["published"]["exact"]]
    proprias = [c for c in cells if c["ours_lean"]]
    qs = sorted({c["q"] for c in cells})
    return {
        "celulas": total["celulas"],
        "q_min": qs[0],
        "q_max": qs[-1],
        "exatas": total["exatas"],
        "abertas": total["celulas"] - total["exatas"],
        "superiores_por_estado": ub,
        "inferiores_por_estado": lb,
        "kernel": sum(ub[e] for e in KERNEL),
        "exatas_novas": len(novas),
        "exatas_novas_certificado": sum(c["certification"]["lb"]["state"] == "CERTIFICATE_VERIFIED" for c in novas),
        "exatas_novas_kernel": sum(all(c["certification"][s]["state"] in KERNEL for s in ("lb", "ub")) for c in novas),
        "teorema_proprio": len(proprias),
        "abaixo_do_publicado": sum(c["best"]["beats_published"] for c in proprias),
        "codigos": conferir_codigos(cells, raiz),
        "atualizado": ledger["meta"].get("ours_atualizado"),
    }


# ---------------------------------------------------------------- destaques


def _intervalo(lb, ub) -> str:
    return f"= {ub}" if lb == ub else f"{lb}–{ub}"


def _pct(x: float, decimal: str = ",", sep: str = " ") -> str:
    """Percentual com uma casa; separador decimal e espaço antes do % seguem a língua (o número não muda)."""
    return f"{x * 100:.1f}".replace(".", decimal) + sep + "%"


def _nome(c: dict) -> str:
    return f"`K_{c['q']}({c['n']},{c['R']})`"


def _eh_caminho(ref, raiz: Path) -> bool:
    return isinstance(ref, str) and "/" in ref and (raiz / ref).is_file()


def _prova(c: dict, raiz: Path, rotulo_codigo: str = "código") -> str:
    """Onde está a prova: doc da cota inferior própria, declaração Lean e arquivo do código, se existirem."""
    cert = c["certification"]
    partes, vistas = [], set()
    lb_p, ub_p = cert["lb"]["provenance"], cert["ub"]["provenance"]
    if cert["lb"]["state"] != "CLAIMED" and lb_p.get("fonte", {}).get("source") == "nosso":
        ref = lb_p["fonte"].get("ref")
        if _eh_caminho(ref, raiz):
            partes.append(f"[{Path(ref).stem}]({ref})")
    for lado in (ub_p, lb_p):
        decl = (lado.get("lean") or {}).get("declaration")
        if decl and decl not in vistas:
            vistas.add(decl)
            partes.append(f"`{decl}`")
    w = ub_p.get("witness")
    if cert["ub"]["state"] != "CLAIMED" and _eh_caminho(w, raiz) and w.startswith("data/codes/"):
        partes.append(f"[{rotulo_codigo}]({w})")
    return " · ".join(partes) or "—"


def destaques(cells: list[dict], raiz: Path = RAIZ) -> list[dict]:
    """Células com resultado próprio: teorema Lean nosso ou cota inferior por certificado verificado.

    Ordem: exatas novas primeiro (maior intervalo fechado relativo), depois maior ganho relativo na cota
    superior; empate por (q, n, R), para a saída não depender da ordem do ledger.
    """
    linhas = []
    for c in cells:
        cert, pub = c["certification"], c["published"]
        if not (c["ours_lean"] or cert["lb"]["state"] == "CERTIFICATE_VERIFIED"):
            continue
        p_lb = pub["lb"]["value"] if pub["lb"] else None
        p_ub = pub["ub"]["value"]
        nova = cert["exact"] and not pub["exact"]
        ganho = (p_ub - cert["ub"]["value"]) / p_ub
        fechado = (p_ub - p_lb) / p_ub if nova and p_lb is not None else 0.0
        linhas.append({
            "celula": c["id"], "q": c["q"], "n": c["n"], "R": c["R"],
            "antes_lb": p_lb, "antes_ub": p_ub,
            "agora_lb": cert["lb"]["value"], "agora_ub": cert["ub"]["value"],
            "estado_lb": cert["lb"]["state"], "estado_ub": cert["ub"]["state"],
            "exata_nova": nova, "ganho": ganho, "fechado": fechado,
            "_nome": _nome(c), "_cell": c,
        })
    linhas.sort(key=lambda d: (not d["exata_nova"], -(d["fechado"] if d["exata_nova"] else d["ganho"]),
                               d["q"], d["n"], d["R"]))
    return linhas


def _agora(d: dict, t: dict) -> str:
    if d["agora_lb"] == d["agora_ub"]:
        return f"**= {d['agora_ub']}**"
    lb = f"**{d['agora_lb']}**" if d["agora_lb"] != d["antes_lb"] else str(d["agora_lb"])
    ub = f"**{d['agora_ub']}**" if d["agora_ub"] != d["antes_ub"] else str(d["agora_ub"])
    sufixo = f" (−{_pct(d['ganho'], t['decimal'], t['sep_pct'])})" if d["ganho"] > 0 else ""
    return f"{lb}–{ub}{sufixo}"


# ---------------------------------------------------------------- textos por língua
# Só rótulos mudam entre as línguas; os números vêm de numeros()/destaques() uma vez e são os mesmos.
# A frase do ledger e os nomes dos estados ficam em inglês em todas: são o nome da coisa.

LINGUAS = ("en", "pt-BR", "fr")
ARQUIVOS = {"en": "README.md", "pt-BR": "README.pt-BR.md", "fr": "README.fr.md"}

TEXTOS = {
    "pt-BR": {
        "decimal": ",", "sep_pct": " ", "pv": "; ",
        "aviso": "Gerado por tools/site/gerar_resultados.py a partir de ledger/cells.json; não edite à mão.",
        "cab": "| o quê | valor |",
        "celulas": "células `K_q(n,R)` no ledger (q de {q_min} a {q_max})",
        "exatas": "exatas (cota inferior = superior)",
        "abertas": "abertas",
        "kernel": "cotas superiores que são teorema do kernel do Lean (FORMALIZED + INDEPENDENTLY_REPRODUCED)",
        "de": "de",
        "inferiores": "cotas inferiores por estado (quase todas herdadas da literatura)",
        "novas": "exatas fechadas aqui (o intervalo publicado estava aberto)",
        "novas_det": "{k} com as duas cotas no kernel; {v} com a inferior por certificado verificado fora do Lean",
        "proprias": "células com teorema Lean próprio",
        "proprias_det": "{b} abaixo da melhor cota superior publicada que achamos",
        "codigos": "códigos explícitos em `data/codes/`",
        "codigos_det": "todos passam no verificador C oficial, `tools/verify/check_all.sh`, no CI",
        "codigos_led": "{t} são a testemunha atual de uma cota do ledger, sha256 conferido",
        "versao": "Versão", "atualizado": "ledger atualizado em",
        "lb_aviso": "As cotas inferiores **não** estão, em geral, no Lean: só {f} delas são teorema do kernel.",
        "destaques": "### Destaques",
        "destaques_txt": "Células com resultado próprio: teorema Lean nosso ou cota inferior por certificado "
                         "verificado. Exatas novas primeiro; depois, maior ganho relativo na cota superior.",
        "tabela": "| célula | antes (publicado) | agora | estado inferior | estado superior | prova |",
        "codigo": "código",
        "pot_novas": "Potencialmente novas (não encontradas na literatura que pesquisamos{ver}): {cels}.",
        "ver": ", ver {link}",
        "lacunas": "Lacunas declaradas: ",
        "lac_lb": "a cota inferior de {cels} é certificado computacional verificado, não teorema do Lean",
        "lac_ub": "a cota superior de {cels} é só a anunciada na literatura (CLAIMED), não conferida aqui",
    },
    "en": {
        "decimal": ".", "sep_pct": "", "pv": "; ",
        "aviso": "Generated by tools/site/gerar_resultados.py from ledger/cells.json; do not edit by hand.",
        "cab": "| what | value |",
        "celulas": "`K_q(n,R)` cells in the ledger (q from {q_min} to {q_max})",
        "exatas": "exact (lower bound = upper bound)",
        "abertas": "open",
        "kernel": "upper bounds that are Lean kernel theorems (FORMALIZED + INDEPENDENTLY_REPRODUCED)",
        "de": "of",
        "inferiores": "lower bounds by state (almost all inherited from the literature)",
        "novas": "exact values closed here (the published interval was open)",
        "novas_det": "{k} with both bounds in the kernel; {v} with the lower bound by a verified certificate "
                     "outside Lean",
        "proprias": "cells with our own Lean theorem",
        "proprias_det": "{b} below the best published upper bound we found",
        "codigos": "explicit codes in `data/codes/`",
        "codigos_det": "all pass the official C verifier, `tools/verify/check_all.sh`, in CI",
        "codigos_led": "{t} are the current witness of a ledger bound, sha256 checked",
        "versao": "Version", "atualizado": "ledger updated on",
        "lb_aviso": "Lower bounds are, in general, **not** in Lean: only {f} of them are kernel theorems.",
        "destaques": "### Highlights",
        "destaques_txt": "Cells with a result of our own: our Lean theorem or a lower bound by verified "
                         "certificate. New exact values first; then largest relative gain in the upper bound.",
        "tabela": "| cell | before (published) | now | lower-bound state | upper-bound state | proof |",
        "codigo": "code",
        "pot_novas": "Potentially new (not found in the literature we searched{ver}): {cels}.",
        "ver": ", see {link}",
        "lacunas": "Declared gaps: ",
        "lac_lb": "the lower bound of {cels} is a verified computational certificate, not a Lean theorem",
        "lac_ub": "the upper bound of {cels} is only the one announced in the literature (CLAIMED), "
                  "not checked here",
    },
    "fr": {
        "decimal": ",", "sep_pct": "\u00a0", "pv": " ; ",
        "aviso": "Généré par tools/site/gerar_resultados.py à partir de ledger/cells.json ; ne pas modifier "
                 "à la main.",
        "cab": "| quoi | valeur |",
        "celulas": "cellules `K_q(n,R)` dans le registre (q de {q_min} à {q_max})",
        "exatas": "exactes (borne inférieure = borne supérieure)",
        "abertas": "ouvertes",
        "kernel": "bornes supérieures qui sont des théorèmes du noyau de Lean (FORMALIZED + "
                  "INDEPENDENTLY_REPRODUCED)",
        "de": "sur",
        "inferiores": "bornes inférieures par état (presque toutes héritées de la littérature)",
        "novas": "valeurs exactes établies ici (l'intervalle publié était ouvert)",
        "novas_det": "{k} avec les deux bornes dans le noyau ; {v} avec la borne inférieure par certificat "
                     "vérifié hors de Lean",
        "proprias": "cellules avec un théorème Lean à nous",
        "proprias_det": "{b} sous la meilleure borne supérieure publiée que nous avons trouvée",
        "codigos": "codes explicites dans `data/codes/`",
        "codigos_det": "tous passent le vérificateur C officiel, `tools/verify/check_all.sh`, en CI",
        "codigos_led": "{t} sont le témoin actuel d'une borne du registre, sha256 vérifié",
        "versao": "Version", "atualizado": "registre mis à jour le",
        "lb_aviso": "Les bornes inférieures ne sont **pas**, en général, dans Lean : seules {f} d'entre elles "
                    "sont des théorèmes du noyau.",
        "destaques": "### Faits marquants",
        "destaques_txt": "Cellules avec un résultat à nous : théorème Lean ou borne inférieure par certificat "
                         "vérifié. Nouvelles valeurs exactes d'abord ; ensuite, plus grand gain relatif sur la "
                         "borne supérieure.",
        "tabela": "| cellule | avant (publié) | maintenant | état inférieur | état supérieur | preuve |",
        "codigo": "code",
        "pot_novas": "Potentiellement nouvelles (introuvables dans la littérature consultée{ver}) : {cels}.",
        "ver": ", voir {link}",
        "lacunas": "Lacunes déclarées : ",
        "lac_lb": "la borne inférieure de {cels} est un certificat calculatoire vérifié, pas un théorème Lean",
        "lac_ub": "la borne supérieure de {cels} est seulement celle annoncée dans la littérature (CLAIMED), "
                  "non vérifiée ici",
    },
}


def lingua_do_arquivo(caminho) -> str:
    """README.md → en, README.pt-BR.md → pt-BR, README.fr.md → fr; outro nome é erro (não adivinhamos)."""
    nome = Path(caminho).name
    for lingua, arq in ARQUIVOS.items():
        if nome == arq:
            return lingua
    raise ValueError(f"não sei a língua de {nome}: use um de {', '.join(ARQUIVOS.values())} ou --lingua")


# ---------------------------------------------------------------- bloco


def bloco(ledger: dict | None = None, raiz: Path = RAIZ, lingua: str = "pt-BR") -> str:
    t = TEXTOS[lingua]
    ledger = ledger if ledger is not None else ler_ledger(raiz)
    n = numeros(ledger, raiz)
    cit = ler_citacao(raiz)
    ub, lb = n["superiores_por_estado"], n["inferiores_por_estado"]
    lb_txt = " · ".join(f"{e} {lb[e]}" for e in ESTADOS if lb[e])
    cod = n["codigos"]
    ds = destaques(ledger["cells"], raiz)
    doi = cit.get("doi", "?")
    L = [
        f"<!-- {t['aviso']} -->",
        "",
        f"> {FRASE_LEDGER}",
        "",
        t["cab"],
        "|---|---:|",
        f"| {t['celulas'].format(**n)} | **{n['celulas']}** |",
        f"| {t['exatas']} | **{n['exatas']}** |",
        f"| {t['abertas']} | **{n['abertas']}** |",
        f"| {t['kernel']} | **{n['kernel']}** {t['de']} {n['celulas']} "
        f"({ub['FORMALIZED']} + {ub['INDEPENDENTLY_REPRODUCED']}) |",
        f"| {t['inferiores']} | {lb_txt} |",
        f"| {t['novas']} | **{n['exatas_novas']}** "
        f"({t['novas_det'].format(k=n['exatas_novas_kernel'], v=n['exatas_novas_certificado'])}) |",
        f"| {t['proprias']} | **{n['teorema_proprio']}** ({t['proprias_det'].format(b=n['abaixo_do_publicado'])}) |",
        f"| {t['codigos']} | **{cod['arquivos']}** ({t['codigos_det']}){t['pv']}"
        f"{t['codigos_led'].format(t=cod['testemunhas_do_ledger'])} |",
        "",
        f"{t['versao']} {cit.get('version', '?')} · DOI [{doi}](https://doi.org/{doi}) · "
        f"{t['atualizado']} {n['atualizado']}. "
        + t["lb_aviso"].format(f=lb["FORMALIZED"] + lb["INDEPENDENTLY_REPRODUCED"]),
        "",
        t["destaques"],
        "",
        t["destaques_txt"],
        "",
        t["tabela"],
        "|---|---:|---:|---|---|---|",
    ]
    for d in ds:
        L.append(f"| {d['_nome']} | {_intervalo(d['antes_lb'], d['antes_ub'])} | {_agora(d, t)} | "
                 f"{d['estado_lb']} | {d['estado_ub']} | {_prova(d['_cell'], raiz, t['codigo'])} |")
    cert_lb = [d["_nome"] for d in ds if d["exata_nova"] and d["estado_lb"] == "CERTIFICATE_VERIFIED"]
    ub_claimed = [d["_nome"] for d in ds if d["estado_ub"] == "CLAIMED"]
    L.append("")
    if cert_lb:
        ver = ""
        if (raiz / DOC_NOVIDADE).is_file():
            ver = t["ver"].format(link=f"[{Path(DOC_NOVIDADE).stem}]({DOC_NOVIDADE})")
        L += [t["pot_novas"].format(ver=ver, cels=", ".join(cert_lb)), ""]
    lacunas = []
    if cert_lb:
        lacunas.append(t["lac_lb"].format(cels=", ".join(cert_lb)))
    if ub_claimed:
        lacunas.append(t["lac_ub"].format(cels=", ".join(ub_claimed)))
    if lacunas:
        L += [t["lacunas"] + t["pv"].join(lacunas) + ".", ""]
    return "\n".join(L).rstrip("\n") + "\n"


# ---------------------------------------------------------------- badges (shields.io endpoint)


def badges(ledger: dict | None = None, raiz: Path = RAIZ) -> dict[str, str]:
    ledger = ledger if ledger is not None else ler_ledger(raiz)
    n = numeros(ledger, raiz)

    def js(label, message, color):
        return json.dumps({"schemaVersion": 1, "label": label, "message": message, "color": color},
                          ensure_ascii=False, sort_keys=True) + "\n"

    return {
        "kernel.json": js("cotas superiores no kernel", f"{n['kernel']}/{n['celulas']}", "blue"),
        "exatas-fechadas.json": js("exatas fechadas aqui", str(n["exatas_novas"]), "brightgreen"),
        "potencialmente-novas.json": js("exatas potencialmente novas", str(n["exatas_novas_certificado"]),
                                        "brightgreen"),
        "exatas.json": js("exatas", f"{n['exatas']}/{n['celulas']}", "informational"),
    }


# ---------------------------------------------------------------- README


def substituir(texto: str, novo_bloco: str) -> str:
    """Troca só o trecho entre as marcas; falha se elas não existirem (uma vez cada, na ordem)."""
    if texto.count(INICIO) != 1 or texto.count(FIM) != 1 or texto.index(INICIO) > texto.index(FIM):
        raise SemMarcas(f"faltam as marcas {INICIO} e {FIM} (uma de cada, nessa ordem). Crie-as vazias "
                        "no lugar onde o bloco deve ficar e rode de novo.")
    antes, resto = texto.split(INICIO, 1)
    _, depois = resto.split(FIM, 1)
    return f"{antes}{INICIO}\n{novo_bloco}{FIM}{depois}"


def _aplicar(caminho: Path, checar: bool) -> int:
    """0 = ok/escrito; 1 = desatualizado (só em --checar); 2 = arquivo ou marcas ausentes."""
    try:
        lingua = lingua_do_arquivo(caminho)
    except ValueError as e:
        print(e, file=sys.stderr)
        return 2
    if not caminho.is_file():
        print(f"{caminho}: não existe (o README de {lingua} vem com as marcas RESULTADOS)", file=sys.stderr)
        return 2
    atual = caminho.read_text(encoding="utf-8")
    try:
        gerado = substituir(atual, bloco(lingua=lingua))
    except SemMarcas as e:
        print(f"{caminho}: {e}", file=sys.stderr)
        return 2
    if checar:
        if gerado != atual:
            print(f"{caminho}: o bloco RESULTADOS diverge do ledger; rode "
                  f"`python3 tools/site/gerar_resultados.py --escrever {caminho}`", file=sys.stderr)
            return 1
        return 0
    if gerado != atual:
        caminho.write_text(gerado, encoding="utf-8")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--escrever", metavar="ARQ", nargs="*",
                   help="substitui o trecho entre as marcas RESULTADOS (sem ARQ: os três READMEs da raiz)")
    g.add_argument("--checar", metavar="ARQ", nargs="*",
                   help="sai 1 se algum trecho diverge do gerado (sem ARQ: os três READMEs da raiz)")
    g.add_argument("--badges", metavar="DIR", help="escreve os JSON de endpoint do shields.io em DIR")
    ap.add_argument("--lingua", choices=LINGUAS, default="pt-BR", help="língua do bloco impresso (padrão pt-BR)")
    a = ap.parse_args(argv)
    if a.badges:
        d = Path(a.badges)
        d.mkdir(parents=True, exist_ok=True)
        for nome, conteudo in badges().items():
            (d / nome).write_text(conteudo, encoding="utf-8")
        return 0
    alvos = a.escrever if a.escrever is not None else a.checar
    if alvos is None:
        sys.stdout.write(bloco(lingua=a.lingua))
        return 0
    caminhos = [Path(x) for x in alvos] or [RAIZ / ARQUIVOS[lg] for lg in LINGUAS]
    # Todos os arquivos são processados mesmo se um falhar: o relatório mostra todos os defeitos de uma vez.
    return max(_aplicar(p, checar=a.checar is not None) for p in caminhos)


if __name__ == "__main__":
    sys.exit(main())
