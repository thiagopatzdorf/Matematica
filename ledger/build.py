#!/usr/bin/env python3
"""Gera ledger/cells.json: uma entrada por célula K_q(n,R).

Para cada célula das tabelas do Kéri (1145 células, via cov/bounds.json do
repositório público do Marosi, Mapika/coldcase) junta:

* as melhores cotas inferior e superior PUBLICADAS, com a fonte de cada uma:
  Kéri 2011, Gijswijt–Polak 2025 (arXiv:2504.01932, só inferiores, q <= 5),
  Marosi 2026 (arXiv:2608.19872, superiores e inferiores SDP) e o banco Lean
  do Florath (arXiv:2606.09600);
* se o Marosi atacou a célula (registro, alvo de varredura ou cerco);
* o NOSSO estado (ledger/ours.json): ours_computational e ours_lean.

As fontes ficam fixadas por commit em ledger/sources.json, e o sha256 de cada
arquivo lido vai para o meta do cells.json: o mesmo commit tem de dar o mesmo
ledger, byte a byte.

Uso:
    python3 ledger/build.py                      # baixa as fontes (commits fixos)
    python3 ledger/build.py --fonte DIR          # lê de DIR/coldcase/... e DIR/florath/...
    python3 ledger/build.py --saida /tmp/c.json

Sem dependências além da biblioteca padrão.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import sys
import urllib.request
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent

# Ordem de desempate quando duas fontes dão o mesmo valor: a mais antiga leva
# o crédito (quem publicou primeiro).
# A compilação pós-Kéri repete valores das fontes primárias; fica por último
# para só levar o crédito quando for estritamente melhor (ex.: Wu–Chen 2024).
PRIORIDADE = {"keri_2011": 0, "gijswijt_polak_2025": 1, "marosi_2026": 2,
              "florath_lean": 3, "literatura_pos_keri": 4}
ROTULO = {
    "keri_2011": "Kéri 2011 (tabelas, http://old.sztaki.hu/~keri/codes/)",
    "gijswijt_polak_2025": "Gijswijt–Polak, arXiv:2504.01932",
    "marosi_2026": "Marosi, arXiv:2608.19872 (Mapika/coldcase)",
    "florath_lean": "Florath, banco Lean, arXiv:2606.09600",
    "literatura_pos_keri": "literatura pós-Kéri compilada por Florath (reference-data/post-keri)",
}


# As tabelas do Kéri são quatro PDFs, e cada um tem a sua legenda: a mesma letra quer dizer
# coisas diferentes em q = 2, q = 3, q = 4–5 e q ≥ 6 (o `f` é "van Wee, 1988" em q = 2 e
# "direct sum" em q ≥ 6). Sem dizer a tabela, "chave 'f'" não identifica a fonte.
TABELAS_KERI = {"keri_2_tables.pdf": "q=2", "keri_3_tables.pdf": "q=3",
                "keri_4-5_tables.pdf": "q=4–5", "keri_6-21_tables.pdf": "q≥6"}
# A transcrição do coldcase (bounds.json, `keys`) traz as legendas de q = 3, q = 4–5 e q ≥ 6, mas
# deixa vazia a de q = 2. Transcrita aqui do keri_2_tables.pdf, pp. 4–5 ("Key to the tables for
# K(n, R), lower bounds" e "... upper bounds"), lido em 2026-10-06.
LEGENDA_KERI_Q2 = {
    "lower": {
        "unmarked": "trivial", "b": "(Taussky–Todd, 1948)", "c": "(Stanton–Kalbfleisch, 1968 and 1969)",
        "d": "(Bhandari–Chanduka–Lal, 1998)", "f": "(van Wee, 1988)", "g": "(Cohen–Lobstein–Sloane, 1986)",
        "h": "perfect code", "i": "(Bertolo–Östergård–Weakly, 2004)", "j": "(Östergård, 2005)",
        "l": "(Habsieger, 1997)", "m": "(Honkala, 1991)", "n": "(Li–Chen, 1994)",
        "o": "(Östergård–Blass, 2001)", "p": "(Östergård–Weakly, 2000)", "q": "(Kéri–Östergård, 2003–2006)",
        "r": "(Habsieger–Plagne, 2000)", "s": "(Zhang, 1991)", "t": "(Zhang–Lo, 1992)", "u": "(Kéri, 2006)",
        "v": "(Plagne, 2008)", "w": "(Kéri, 2009)", "x": "(Lang–Quistorff–Schneider, 2006)",
        "y": "(Haas, 2007–2008)", "z": "(Blass–Litsyn, 1998 and 1999)"},
    "upper": {
        "unmarked": "trivial", "b": "(Taussky–Todd, 1948)", "c": "(Stanton–Kalbfleisch, 1968)",
        "d": "(Etzion–Greenberg, 1993)", "f": "(van Wee, 1988)", "g": "(Cohen–Lobstein–Sloane, 1986)",
        "h": "perfect code", "j": "(Wille, 1990 and 1996)", "k": "(Brualdi–Pless, 1990)",
        "l": "(Cohen–Honkala–Litsyn–Lobstein, 1997)", "m": "(Honkala, 1991)", "n": "(Li–Chen, 1994)",
        "o": "(Östergård, 1994)", "p": "(Östergård–Weakly, 1999)",
        "s": "(Hämäläinen–Honkala–Kaikkonen–Litsyn, 1993)", "t": "(Hämäläinen–Honkala–Litsyn–Östergård, 1995)",
        "u": "(Mollard, 1981)", "v": "(Östergård–Kaikkonen, 1998)", "w": "(Hämäläinen–Rankinen, 1991)",
        "x": "(Honkala–Hämäläinen, 1988)", "y": "(Graham–Sloane, 1985)",
        "z": "(Bertolo–Di Pasquale–Santisi, 2006)"},
}


def tabela_keri(q: int) -> str:
    return "q=2" if q == 2 else "q=3" if q == 3 else "q=4–5" if q <= 5 else "q≥6"


def legendas_keri(bounds: dict) -> dict:
    """{tabela: {"lower"|"upper": {letra: texto}}}: q = 2 daqui, o resto do bounds.json."""
    out = {"q=2": LEGENDA_KERI_Q2}
    for k in bounds.get("keys") or []:
        t = TABELAS_KERI.get(k.get("src"))
        if t and t != "q=2" and (k.get("lower") or k.get("upper")):
            out[t] = {"lower": k.get("lower") or {}, "upper": k.get("upper") or {}}
    return out


def ref_keri(q: int, lado: str, letra, legendas: dict) -> str:
    """"chave 'f' da tabela do Kéri para q≥6 (direct sum)"; sem letra é a entrada "trivial"."""
    t = tabela_keri(q)
    texto = (legendas.get(t) or {}).get("upper" if lado == "ub" else "lower", {}).get(letra or "unmarked")
    base = f"chave {letra!r} da tabela do Kéri para {t}" if letra else f"sem chave na tabela do Kéri para {t}"
    if not texto:
        return base
    return f"{base} {texto}" if texto.startswith("(") else f"{base} ({texto})"


def chave(q: int, n: int, R: int) -> str:
    return f"{q},{n},{R}"


def nome(q: int, n: int, R: int) -> str:
    return f"K{q}({n},{R})"


def volume(q: int, n: int, R: int) -> int:
    """Tamanho da bola de Hamming de raio R em Z_q^n."""
    from math import comb

    return sum(comb(n, i) * (q - 1) ** i for i in range(R + 1))


def cota_esfera(q: int, n: int, R: int) -> int:
    V = volume(q, n, R)
    return -(-(q**n) // V)


# ---------------------------------------------------------------- leitura


def _baixar(url: str) -> bytes:
    # urllib respeita HTTPS_PROXY e SSL_CERT_FILE do ambiente.
    with urllib.request.urlopen(url, timeout=120) as r:
        return r.read()


def ler_fontes(fonte: Path | None, sources: dict, cache: Path | None = None) -> dict:
    """Devolve {nome: (bytes, sha256, origem)} para cada arquivo de sources.json.

    Com `fonte`, lê de fonte/<repo>/<caminho>; sem, baixa do GitHub no commit
    fixado (e guarda em `cache`, se dado)."""
    out = {}
    for repo, spec in sources.items():
        if not isinstance(spec, dict) or "arquivos" not in spec:
            continue
        base = spec["repo"].replace("https://github.com/", "https://raw.githubusercontent.com/")
        for nome_arq, caminho in spec["arquivos"].items():
            if fonte is not None:
                p = fonte / repo / caminho
                dados = p.read_bytes() if p.exists() else None
                origem = str(p)
            else:
                c = cache / repo / spec["commit"] / caminho if cache else None
                if c is not None and c.exists():
                    dados = c.read_bytes()
                else:
                    dados = _baixar(f"{base}/{spec['commit']}/{caminho}")
                    if c is not None:
                        c.parent.mkdir(parents=True, exist_ok=True)
                        c.write_bytes(dados)
                origem = f"{spec['repo']}/blob/{spec['commit']}/{caminho}"
            sha = hashlib.sha256(dados).hexdigest() if dados is not None else None
            out[nome_arq] = (dados, sha, origem)
    return out


def _json(fontes: dict, nome_arq: str, padrao):
    dados = fontes.get(nome_arq, (None,))[0]
    return json.loads(dados) if dados is not None else padrao


# ---------------------------------------------------------------- montagem


def evidencias_marosi(fontes: dict) -> dict:
    """{chave: {"ub": [motivos], "lb": [motivos]}} do que o Marosi tocou."""
    ev: dict[str, dict[str, list]] = {}

    def marca(q, n, R, lado, motivo):
        d = ev.setdefault(chave(q, n, R), {"ub": [], "lb": []})
        if motivo not in d[lado]:
            d[lado].append(motivo)

    for e in _json(fontes, "marosi_ub", []):
        marca(e["q"], e["n"], e["R"], "ub", "record:final_records.json")
    for arq in ("attack_records", "attack_records2", "attack_sieges"):
        for e in _json(fontes, arq, []):
            marca(e["q"], e["n"], e["R"], "ub", f"attack:{arq}.json")
    for e in _json(fontes, "sweep_targets", []):
        marca(e["q"], e["n"], e["R"], "ub", "sweep:sweep_targets.json")
    for k in _json(fontes, "sweep_state", {}):
        q, n, R = (int(x) for x in k.split(","))
        marca(q, n, R, "ub", "sweep:cov_sweep_state.json")
    for e in _json(fontes, "marosi_lb", []):
        marca(e["q"], e["n"], e["R"], "lb", "sdp:lb_master.json")
    return ev


def tabela_florath(fontes: dict, arquivo: str = "lean_table") -> dict:
    dados = fontes.get(arquivo, (None,))[0]
    if dados is None:
        return {}
    out = {}
    for row in csv.DictReader(io.StringIO(dados.decode("utf-8"))):
        try:
            q, n, r = int(row["q"]), int(row["n"]), int(row["r"])
        except (KeyError, ValueError):
            continue
        out[chave(q, n, r)] = {
            "lb": int(row["lower_bound"]) if row.get("lower_bound") else None,
            "ub": int(row["upper_bound"]) if row.get("upper_bound") else None,
            "lb_ref": row.get("lower_bound_reference") or None,
            "ub_ref": row.get("upper_bound_reference") or None,
        }
    return out


def _melhor(candidatos: list[tuple[int, str]], maior: bool):
    cs = [c for c in candidatos if c[0] is not None]
    if not cs:
        return None
    alvo = max(v for v, _ in cs) if maior else min(v for v, _ in cs)
    fonte = min((f for v, f in cs if v == alvo), key=lambda f: PRIORIDADE[f])
    return {"value": alvo, "source": fonte, "ref": ROTULO[fonte]}


def montar_celula(e: dict, gp: int | None, mub: dict | None, mlb: dict | None,
                  flo: dict | None, ev: dict | None, lit: dict | None = None,
                  legendas: dict | None = None) -> dict:
    q, n, R = e["q"], e["n"], e["R"]
    legendas = legendas if legendas is not None else {"q=2": LEGENDA_KERI_Q2}
    pub = {
        "keri_2011": {"lb": e["lb"], "ub": e["ub"], "lb_key": e.get("lb_key"),
                      "ub_key": e.get("ub_key"), "n_optimal": e.get("n_optimal"),
                      "src": e.get("src"), "page": e.get("page"),
                      "lb_ref": ref_keri(q, "lb", e.get("lb_key"), legendas),
                      "ub_ref": ref_keri(q, "ub", e.get("ub_key"), legendas)},
        "gijswijt_polak_2025": {"lb": gp} if gp is not None else None,
        "marosi_2026": None,
        "florath_lean": flo,
        "literatura_pos_keri": lit,
    }
    if mub or mlb:
        pub["marosi_2026"] = {"ub": mub["ours"] if mub else None,
                              "code_file": mub["code_file"] if mub else None,
                              "lb": mlb["K_lower_bound"] if mlb else None,
                              "lb_certificate": f"cov/lb/certs_all/{mlb['cert']}" if mlb else None}
    lbs = [(e["lb"], "keri_2011"), (gp, "gijswijt_polak_2025")]
    ubs = [(e["ub"], "keri_2011")]
    if pub["marosi_2026"]:
        lbs.append((pub["marosi_2026"]["lb"], "marosi_2026"))
        ubs.append((pub["marosi_2026"]["ub"], "marosi_2026"))
    if flo:
        lbs.append((flo["lb"], "florath_lean"))
        ubs.append((flo["ub"], "florath_lean"))
    if lit:
        lbs.append((lit["lb"], "literatura_pos_keri"))
        ubs.append((lit["ub"], "literatura_pos_keri"))
    ev = ev or {"ub": [], "lb": []}
    best_lb = _melhor(lbs, maior=True)
    best_ub = _melhor(ubs, maior=False)
    return {
        "id": nome(q, n, R),
        "q": q, "n": n, "R": R,
        "space": q**n,
        "sphere_bound": cota_esfera(q, n, R),
        "published": {
            "lb": best_lb,
            "ub": best_ub,
            "exact": best_lb is not None and best_ub is not None and best_lb["value"] == best_ub["value"],
            "sources": pub,
        },
        "marosi_attacked": {"ub": bool(ev["ub"]), "lb": bool(ev["lb"]), "evidence": ev["ub"] + ev["lb"]},
        # Superior melhorada por alguém depois de 2011 (Marosi ou Florath).
        "ub_improved_since_2011": best_ub is not None and best_ub["value"] < e["ub"],
        "ours_computational": None,
        "ours_lean": None,
        "best": None,
    }


def aplicar_nosso(cel: dict, nosso: dict | None) -> dict:
    """Escreve ours_* e recalcula `best` (melhor cota superior conhecida,
    contando a nossa) e `status`."""
    nosso = nosso or {}
    cel["ours_computational"] = nosso.get("ours_computational")
    cel["ours_lean"] = nosso.get("ours_lean")
    pub_ub = cel["published"]["ub"]["value"] if cel["published"]["ub"] else None
    cands = []
    if pub_ub is not None:
        cands.append((pub_ub, 2, "published"))
    if cel["ours_lean"]:
        cands.append((cel["ours_lean"]["M"], 0, "ours_lean"))
    if cel["ours_computational"]:
        cands.append((cel["ours_computational"]["M"], 1, "ours_computational"))
    if cands:
        v, _, quem = min(cands)
        cel["best"] = {"ub": v, "holder": quem,
                       "beats_published": pub_ub is not None and v < pub_ub}
    if cel["ours_lean"]:
        cel["status"] = "ours_lean"
    elif cel["ours_computational"]:
        cel["status"] = "ours_computational"
    else:
        cel["status"] = "published"
    return cel


# ---------------------------------------------------------------- certificação

# Escada de estado de uma cota (cumulativa: cada degrau supõe o anterior).
#   CLAIMED                  publicada numa fonte de versão congelada; nada conferido aqui.
#   WITNESS_CHECKED          o certificado (código explícito, ou prova LRAT de inexistência) foi
#                            conferido por um verificador exato fora do Lean.
#   CERTIFICATE_VERIFIED     só cota INFERIOR: a inexistência inteira está coberta por certificados
#                            (LRAT, VeriPB ou Farkas) fixados por sha256, conferidos por verificador
#                            que não é o gerador, e a prova sobreviveu a um red team em PR próprio.
#                            Não há Lean. (A superior pula o degrau: o código explícito já é o
#                            certificado inteiro, e WITNESS_CHECKED o confere sem redução nenhuma.)
#   FORMALIZED               há teorema do Lean, checado pelo kernel, com exatamente esta cota.
#   INDEPENDENTLY_REPRODUCED formalizada E conferida por um segundo verificador independente,
#                            executado (hoje: o código de data/codes/ passa no tools/verify em C).
ESTADOS = ("CLAIMED", "WITNESS_CHECKED", "CERTIFICATE_VERIFIED", "FORMALIZED", "INDEPENDENTLY_REPRODUCED")
# Sistemas de prova aceitos em CERTIFICATE_VERIFIED: resolução (LRAT), planos de corte (VeriPB) e
# inviabilidade de LP com multiplicadores inteiros (Farkas). Outro tipo exige decidir antes se o
# verificador dele é exato; por isso a lista é fechada e o build aborta fora dela.
TIPOS_CERTIFICADO = ("LRAT", "VeriPB", "Farkas")
CAMPOS_PROVENIENCIA = ("fonte", "versao", "witness", "sha256", "verificador_independente", "lean")
# fonte -> arquivo de sources.json (repo:nome) de onde a cota foi lida.
VERSAO_FONTE = {"keri_2011": "coldcase:bounds", "gijswijt_polak_2025": "coldcase:bounds",
                "marosi_2026": {"ub": "coldcase:marosi_ub", "lb": "coldcase:marosi_lb"},
                "florath_lean": "florath:lean_table", "literatura_pos_keri": "florath:post_keri_table"}
VERIFICADOR_PY = "avaliador Python de tools/certificar/buscar.py, rodado em tests/test_certificar.py"
VERIFICADOR_C = "tools/verify/verify (C; tools/verify/check_all.sh confere todo data/codes/)"


def _versao(fonte: str, lado: str) -> str:
    v = VERSAO_FONTE[fonte]
    return v[lado] if isinstance(v, dict) else v


def _ref_fonte(cel: dict, fonte: str, lado: str):
    """A referência dentro da fonte: chave do Kéri, arquivo do Marosi, regra do Florath..."""
    s = cel["published"]["sources"].get(fonte) or {}
    if fonte == "keri_2011":
        return s.get(lado + "_ref") or ref_keri(cel["q"], lado, s.get(lado + "_key"), {"q=2": LEGENDA_KERI_Q2})
    if fonte == "marosi_2026":
        return s.get("code_file") if lado == "ub" else s.get("lb_certificate")
    if fonte == "gijswijt_polak_2025":
        return "arXiv:2504.01932"
    return s.get(lado + "_ref")


def _prov(fonte, versao, witness=None, sha256=None, verificador=None, lean=None, lacuna=None):
    p = dict(zip(CAMPOS_PROVENIENCIA, (fonte, versao, witness, sha256, verificador, lean)))
    if lacuna:
        p["lacuna"] = lacuna
    return p


def _fonte_publicada(cel: dict, lado: str, valor: int):
    """Fonte original e versão da tabela, se alguma fonte publicada traz exatamente `valor`."""
    b = cel["published"][lado]
    if b is None or b["value"] != valor:
        return None, None
    return {"source": b["source"], "ref": _ref_fonte(cel, b["source"], lado)}, _versao(b["source"], lado)


def _externa(cel: dict, lado: str, valor: int):
    """Prova Lean de terceiros (Florath) da mesma cota: registrada, mas não sobe o estado,
    porque não foi reconstruída aqui."""
    f = cel["published"]["sources"].get("florath_lean")
    if f and f.get(lado) == valor:
        return {"source": "florath_lean", "ref": f.get(lado + "_ref"), "versao": "florath:lean_table"}
    return None


def certificar_ub(cel: dict, formal: dict | None = None) -> dict:
    v = cel["best"]["ub"]
    lean, comp = cel["ours_lean"], cel["ours_computational"]
    fonte, versao = _fonte_publicada(cel, "ub", v)
    if lean and lean["M"] == v:
        arq = lean.get("file") or lean.get("witness_lean")
        if fonte is None:
            fonte, versao = {"source": "nosso", "ref": lean.get("provenance")}, f"git tag {lean.get('tag')}"
        estado = "INDEPENDENTLY_REPRODUCED" if lean.get("file") else "FORMALIZED"
        prov = _prov(fonte, versao, arq, lean.get("sha256") or lean.get("witness_sha256"),
                     VERIFICADOR_C if lean.get("file") else None,
                     {"declaration": lean["declaration"], "tag": lean.get("tag")},
                     None if arq else "o código está dentro da prova Lean; não há arquivo em data/codes/")
    elif formal and formal["M"] == v:
        # Certificado em lote (tools/certificar/gerar.py): célula base + regra, teorema gerado.
        if fonte is None:
            fonte, versao = {"source": "nosso", "ref": formal["construcao"]}, None
        wit = formal.get("witness")
        # Witness explícito: além do kernel, o avaliador Python (tools/certificar/buscar.py) reconfere
        # o código em todo pytest (tests/test_certificar.py); regra pura não tem segundo verificador.
        estado = "INDEPENDENTLY_REPRODUCED" if wit else "FORMALIZED"
        prov = _prov(fonte, versao, wit or formal["arquivo"],
                     formal.get("sha256") if wit else formal["sha256_arquivo"],
                     formal.get("verificador", VERIFICADOR_PY) if wit else None,
                     {"declaration": formal["declaration"], "lib": formal.get("lib", "CoveringLedger")})
        prov["construcao"] = formal["construcao"]
    elif comp and comp["M"] == v:
        if fonte is None:
            fonte, versao = {"source": "nosso", "ref": comp.get("provenance")}, None
        estado = "WITNESS_CHECKED"
        prov = _prov(fonte, versao, comp["file"], comp["sha256"], VERIFICADOR_C)
    else:
        estado = "CLAIMED"
        prov = _prov(fonte, versao, lacuna="cota herdada da literatura; nenhum certificado conferido aqui")
    ext = _externa(cel, "ub", v)
    if ext:
        prov["formalizacao_externa"] = ext
    return {"value": v, "state": estado, "provenance": prov}


def validar_certificado(cid: str, registro: dict) -> None:
    """Aborta o build se um registro CERTIFICATE_VERIFIED não traz a proveniência que o degrau exige.

    Sem isto, o estado viraria rótulo: qualquer registro poderia se dizer verificado sem apontar
    qual certificado, qual verificador e qual red team sustentam a cota."""
    c = registro.get("certificado") or {}
    erros = []
    tipos = c.get("tipo") or []
    if not tipos or any(t not in TIPOS_CERTIFICADO for t in tipos):
        erros.append(f"certificado.tipo deve ser lista não vazia de {TIPOS_CERTIFICADO}, veio {tipos!r}")
    arqs = c.get("arquivos") or {}
    if not arqs or any(not isinstance(h, str) or len(h) != 64 for h in arqs.values()):
        erros.append("certificado.arquivos deve mapear cada certificado (ou manifesto) ao seu sha256")
    if not c.get("verificadores"):
        erros.append("certificado.verificadores vazio")
    if not c.get("pr"):
        erros.append("certificado.pr vazio")
    rt = c.get("red_team") or {}
    if not (rt.get("pr") and rt.get("doc")):
        erros.append("certificado.red_team precisa de pr e doc")
    if registro.get("lean"):
        erros.append("com teorema Lean a cota é FORMALIZED, não CERTIFICATE_VERIFIED")
    if erros:
        raise SystemExit(f"{cid}: CERTIFICATE_VERIFIED sem proveniência completa: " + "; ".join(erros))


def certificar_lb(cel: dict, registro: dict | None) -> dict | None:
    pub = cel["published"]["lb"]
    lean = cel["ours_lean"]
    if lean and lean.get("exact"):
        v = lean["M"]
        fonte, versao = _fonte_publicada(cel, "lb", v)
        estado = "FORMALIZED"
        prov = _prov(fonte or {"source": "nosso", "ref": lean["declaration"]}, versao,
                     lean.get("witness_lean"), None, None,
                     {"declaration": lean["declaration"], "tag": lean.get("tag")},
                     "inexistência provada no kernel; não há certificado fora do Lean")
    elif registro:
        v, estado = registro["value"], registro["estado"]
        if estado in ESTADOS and ESTADOS.index(estado) >= ESTADOS.index("FORMALIZED") \
                and (registro.get("lean") or {}).get("condicional"):
            raise SystemExit(f"{cel['id']}: teorema Lean condicional não é FORMALIZED")
        if estado == "CERTIFICATE_VERIFIED":
            validar_certificado(cel["id"], registro)
        fonte, versao = _fonte_publicada(cel, "lb", v)
        prov = _prov(fonte or {"source": "nosso", "ref": registro.get("docs")}, versao or registro.get("data"),
                     registro.get("witness"), registro.get("sha256"),
                     registro.get("verificador_independente"), registro.get("lean"))
        for k in ("formalizacao_parcial", "formalizacao_completa", "reproducao_independente",
                  "certificado", "dependencias"):
            if registro.get(k):
                prov[k] = registro[k]
    elif pub is not None:
        v, estado = pub["value"], "CLAIMED"
        fonte, versao = _fonte_publicada(cel, "lb", v)
        prov = _prov(fonte, versao, lacuna="cota herdada da literatura; nenhum certificado conferido aqui")
    else:
        return None
    if estado not in ESTADOS:
        raise SystemExit(f"{cel['id']}: estado desconhecido {estado!r}")
    if pub is not None and v < pub["value"]:
        raise SystemExit(f"{cel['id']}: cota inferior nossa {v} abaixo da publicada {pub['value']}")
    if v > cel["best"]["ub"]:
        raise SystemExit(f"{cel['id']}: cota inferior {v} > superior {cel['best']['ub']}")
    ext = _externa(cel, "lb", v)
    if ext:
        prov["formalizacao_externa"] = ext
    return {"value": v, "state": estado, "provenance": prov}


def certificar(cel: dict, nosso: dict | None, formal: dict | None = None) -> dict:
    ub = certificar_ub(cel, formal)
    lb = certificar_lb(cel, (nosso or {}).get("lb"))
    cel["certification"] = {"ub": ub, "lb": lb, "exact": lb is not None and lb["value"] == ub["value"]}
    return cel


# A transcrição do coldcase (bounds.json, commit 56a8cce) perde o expoente de "4^79" etc. nas
# tabelas do Kéri: n_optimal chega truncado ao primeiro dígito (K4(4,3) vem 7, não 79). Valores da
# tabela do Kéri, recontados por classificação exaustiva em tools/exatos/motor (--classificar).
N_OPTIMAL_CORRIGIDO = {
    (4, 3, 2): 21, (4, 4, 3): 79, (4, 5, 4): 269, (4, 6, 5): 839,
    (5, 3, 2): 54, (5, 4, 3): 471,
}


def corrigir_n_optimal(e: dict) -> dict:
    alvo = N_OPTIMAL_CORRIGIDO.get((e["q"], e["n"], e["R"]))
    if alvo is None or e.get("n_optimal") == alvo:
        return e
    if e.get("n_optimal") != int(str(alvo)[0]):
        raise SystemExit(f"n_optimal inesperado em K{e['q']}({e['n']},{e['R']}): {e.get('n_optimal')}")
    return {**e, "n_optimal": alvo}


def versoes(sources: dict, fontes: dict) -> dict:
    out = {}
    for repo, spec in sources.items():
        if not isinstance(spec, dict) or "arquivos" not in spec:
            continue
        for nome_arq, caminho in spec["arquivos"].items():
            out[f"{repo}:{nome_arq}"] = {"repo": spec["repo"], "commit": spec["commit"], "arquivo": caminho,
                                         "lido_em": spec.get("lido_em"),
                                         "sha256": fontes.get(nome_arq, (None, None))[1]}
    return out


def carregar_formal(caminho: Path = AQUI / "formal_ub.json") -> dict:
    """Cotas superiores certificadas em lote (gerado por tools/certificar/gerar.py)."""
    return json.loads(caminho.read_text(encoding="utf-8"))["cells"] if caminho.exists() else {}


def construir(fontes: dict, ours: dict, sources: dict, formal: dict | None = None) -> dict:
    bounds = _json(fontes, "bounds", None)
    if bounds is None:
        raise SystemExit("bounds.json do coldcase não encontrado")
    mub = {chave(e["q"], e["n"], e["R"]): e for e in _json(fontes, "marosi_ub", [])}
    mlb = {chave(e["q"], e["n"], e["R"]): e for e in _json(fontes, "marosi_lb", [])
           if e.get("improves_best_known")}
    flo = tabela_florath(fontes)
    lit = tabela_florath(fontes, "post_keri_table")
    ev = evidencias_marosi(fontes)
    legendas = legendas_keri(bounds)
    nossos = ours.get("cells", {})
    formal = carregar_formal() if formal is None else formal
    cells = []
    vistos = set()
    for e in bounds["entries"]:
        e = corrigir_n_optimal(e)
        k = chave(e["q"], e["n"], e["R"])
        vistos.add(k)
        c = montar_celula(e, e.get("lb_updated"), mub.get(k), mlb.get(k), flo.get(k), ev.get(k), lit.get(k),
                          legendas)
        cells.append(certificar(aplicar_nosso(c, nossos.get(k)), nossos.get(k), formal.get(k)))
    faltando = sorted(set(nossos) - vistos)
    if faltando:
        raise SystemExit(f"células nossas fora da tabela do Kéri: {faltando}")
    cells.sort(key=lambda c: (c["q"], c["n"], c["R"]))
    return {
        "meta": {
            "descricao": "Ledger de células K_q(n,R): melhores cotas publicadas, fonte, e o nosso estado. Gerado por ledger/build.py; não edite à mão (edite ledger/ours.json).",
            "gerado_por": "ledger/build.py",
            "fontes": {k: {"repo": v["repo"], "commit": v["commit"]}
                       for k, v in sources.items() if isinstance(v, dict) and "repo" in v},
            "sha256_fontes": {nome_arq: sha for nome_arq, (_, sha, _) in sorted(fontes.items())},
            # Versão congelada de cada tabela, citada em certification.*.provenance.versao.
            "versoes": versoes(sources, fontes),
            "estados": list(ESTADOS),
            "ours_atualizado": ours.get("atualizado"),
            "n_cells": len(cells),
        },
        "cells": cells,
    }


def escrever(ledger: dict, saida: Path) -> None:
    # Uma célula por linha: diff legível e arquivo pequeno.
    linhas = ['{"meta": ' + json.dumps(ledger["meta"], ensure_ascii=False, sort_keys=True) + ',',
              ' "cells": [']
    cs = ledger["cells"]
    for i, c in enumerate(cs):
        linhas.append("  " + json.dumps(c, ensure_ascii=False, sort_keys=True) + ("," if i < len(cs) - 1 else ""))
    linhas.append(" ]}")
    saida.write_text("\n".join(linhas) + "\n", encoding="utf-8")


def carregar(caminho: Path = AQUI / "cells.json") -> dict:
    return json.loads(caminho.read_text(encoding="utf-8"))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--fonte", type=Path, help="diretório local com coldcase/ e florath/ (sem rede)")
    ap.add_argument("--sources", type=Path, default=AQUI / "sources.json")
    ap.add_argument("--ours", type=Path, default=AQUI / "ours.json")
    ap.add_argument("--saida", type=Path, default=AQUI / "cells.json")
    ap.add_argument("--cache", type=Path, default=AQUI / ".cache")
    a = ap.parse_args(argv)
    sources = json.loads(a.sources.read_text(encoding="utf-8"))
    ours = json.loads(a.ours.read_text(encoding="utf-8"))
    fontes = ler_fontes(a.fonte, sources, None if a.fonte else a.cache)
    ledger = construir(fontes, ours, sources)
    escrever(ledger, a.saida)
    st = {}
    for c in ledger["cells"]:
        st[c["status"]] = st.get(c["status"], 0) + 1
    print(f"{a.saida}: {ledger['meta']['n_cells']} células; status {st}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
