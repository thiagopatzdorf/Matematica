#!/usr/bin/env python3
"""Gera o bloco "Resultados" do README a partir do ledger (só biblioteca padrão).

Por que existe: o README da raiz repetia à mão números do ledger e divergia dele (dizia 520 exatas e
13 células com teorema próprio quando `ledger/cells.json` já tinha 523 e 14). Aqui o bloco é derivado,
e um teste (`tests/test_gerar_resultados.py`) falha se o README commitado não bater com o gerado.

Fontes: `ledger/cells.json` (contado por `ledger/cobertura.py`, a mesma função que gera o
`ledger/COBERTURA.md`), `data/codes/` (sha256 conferido contra o ledger) e `CITATION.cff` (versão e DOI).
Determinístico: mesma entrada, mesmos bytes (sem data de geração, ordem fixa).

    python3 tools/site/gerar_resultados.py                    # imprime o bloco
    python3 tools/site/gerar_resultados.py --escrever README.md
    python3 tools/site/gerar_resultados.py --checar README.md # sai 1 se o README estiver desatualizado
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


def _pct(x: float) -> str:
    return f"{x * 100:.1f}".replace(".", ",") + " %"


def _nome(c: dict) -> str:
    return f"`K_{c['q']}({c['n']},{c['R']})`"


def _eh_caminho(ref, raiz: Path) -> bool:
    return isinstance(ref, str) and "/" in ref and (raiz / ref).is_file()


def _prova(c: dict, raiz: Path) -> str:
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
        partes.append(f"[código]({w})")
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
            "_nome": _nome(c), "_prova": _prova(c, raiz),
        })
    linhas.sort(key=lambda d: (not d["exata_nova"], -(d["fechado"] if d["exata_nova"] else d["ganho"]),
                               d["q"], d["n"], d["R"]))
    return linhas


def _agora(d: dict) -> str:
    if d["agora_lb"] == d["agora_ub"]:
        return f"**= {d['agora_ub']}**"
    lb = f"**{d['agora_lb']}**" if d["agora_lb"] != d["antes_lb"] else str(d["agora_lb"])
    ub = f"**{d['agora_ub']}**" if d["agora_ub"] != d["antes_ub"] else str(d["agora_ub"])
    sufixo = f" (−{_pct(d['ganho'])})" if d["ganho"] > 0 else ""
    return f"{lb}–{ub}{sufixo}"


# ---------------------------------------------------------------- bloco


def bloco(ledger: dict | None = None, raiz: Path = RAIZ) -> str:
    ledger = ledger if ledger is not None else ler_ledger(raiz)
    n = numeros(ledger, raiz)
    cit = ler_citacao(raiz)
    ub, lb = n["superiores_por_estado"], n["inferiores_por_estado"]
    lb_txt = " · ".join(f"{e} {lb[e]}" for e in ESTADOS if lb[e])
    cod = n["codigos"]
    ds = destaques(ledger["cells"], raiz)
    L = [
        "<!-- Gerado por tools/site/gerar_resultados.py a partir de ledger/cells.json; não edite à mão. -->",
        "",
        f"> {FRASE_LEDGER}",
        "",
        "| o quê | valor |",
        "|---|---:|",
        f"| células `K_q(n,R)` no ledger (q de {n['q_min']} a {n['q_max']}) | **{n['celulas']}** |",
        f"| exatas (cota inferior = superior) | **{n['exatas']}** |",
        f"| abertas | **{n['abertas']}** |",
        f"| cotas superiores que são teorema do kernel do Lean (FORMALIZED + INDEPENDENTLY_REPRODUCED) | "
        f"**{n['kernel']}** de {n['celulas']} ({ub['FORMALIZED']} + {ub['INDEPENDENTLY_REPRODUCED']}) |",
        f"| cotas inferiores por estado (quase todas herdadas da literatura) | {lb_txt} |",
        f"| exatas fechadas aqui (o intervalo publicado estava aberto) | **{n['exatas_novas']}** "
        f"({n['exatas_novas_kernel']} com as duas cotas no kernel; {n['exatas_novas_certificado']} com a "
        f"inferior por certificado verificado fora do Lean) |",
        f"| células com teorema Lean próprio | **{n['teorema_proprio']}** ({n['abaixo_do_publicado']} abaixo "
        f"da melhor cota superior publicada que achamos) |",
        f"| códigos explícitos em `data/codes/` | **{cod['arquivos']}** (todos passam no verificador C oficial, "
        f"`tools/verify/check_all.sh`, no CI); {cod['testemunhas_do_ledger']} são a testemunha atual de uma "
        f"cota do ledger, sha256 conferido |",
        "",
        f"Versão {cit.get('version', '?')} · DOI [{cit.get('doi', '?')}](https://doi.org/{cit.get('doi', '')}) · "
        f"ledger atualizado em {n['atualizado']}. As cotas inferiores **não** estão, em geral, no Lean: só "
        f"{lb['FORMALIZED'] + lb['INDEPENDENTLY_REPRODUCED']} delas são teorema do kernel.",
        "",
        "### Destaques",
        "",
        "Células com resultado próprio: teorema Lean nosso ou cota inferior por certificado verificado. "
        "Exatas novas primeiro; depois, maior ganho relativo na cota superior.",
        "",
        "| célula | antes (publicado) | agora | estado inferior | estado superior | prova |",
        "|---|---:|---:|---|---|---|",
    ]
    for d in ds:
        L.append(f"| {d['_nome']} | {_intervalo(d['antes_lb'], d['antes_ub'])} | {_agora(d)} | "
                 f"{d['estado_lb']} | {d['estado_ub']} | {d['_prova']} |")
    cert_lb = [d["_nome"] for d in ds if d["exata_nova"] and d["estado_lb"] == "CERTIFICATE_VERIFIED"]
    ub_claimed = [d["_nome"] for d in ds if d["estado_ub"] == "CLAIMED"]
    L.append("")
    if cert_lb:
        novidade = f"[{Path(DOC_NOVIDADE).stem}]({DOC_NOVIDADE})" if (raiz / DOC_NOVIDADE).is_file() else ""
        L.append(f"Potencialmente novas (não encontradas na literatura que pesquisamos{', ver ' + novidade if novidade else ''}): "
                 f"{', '.join(cert_lb)}.")
        L.append("")
    lacunas = []
    if cert_lb:
        lacunas.append(f"a cota inferior de {', '.join(cert_lb)} é certificado computacional verificado, "
                       "não teorema do Lean")
    if ub_claimed:
        lacunas.append(f"a cota superior de {', '.join(ub_claimed)} é só a anunciada na literatura (CLAIMED), "
                       "não conferida aqui")
    if lacunas:
        L.append("Lacunas declaradas: " + "; ".join(lacunas) + ".")
        L.append("")
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


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--escrever", metavar="ARQ", help="substitui o trecho entre as marcas RESULTADOS em ARQ")
    g.add_argument("--checar", metavar="ARQ", help="sai 1 se o trecho de ARQ diverge do gerado")
    g.add_argument("--badges", metavar="DIR", help="escreve os JSON de endpoint do shields.io em DIR")
    a = ap.parse_args(argv)
    novo = bloco()
    if a.badges:
        d = Path(a.badges)
        d.mkdir(parents=True, exist_ok=True)
        for nome, conteudo in badges().items():
            (d / nome).write_text(conteudo, encoding="utf-8")
        return 0
    alvo = a.escrever or a.checar
    if not alvo:
        sys.stdout.write(novo)
        return 0
    p = Path(alvo)
    atual = p.read_text(encoding="utf-8")
    try:
        gerado = substituir(atual, novo)
    except SemMarcas as e:
        print(f"{p}: {e}", file=sys.stderr)
        return 2
    if a.checar:
        if gerado != atual:
            print(f"{p}: o bloco RESULTADOS diverge do ledger; rode "
                  f"`python3 tools/site/gerar_resultados.py --escrever {alvo}`", file=sys.stderr)
            return 1
        return 0
    p.write_text(gerado, encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
