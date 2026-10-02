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
                  flo: dict | None, ev: dict | None, lit: dict | None = None) -> dict:
    q, n, R = e["q"], e["n"], e["R"]
    pub = {
        "keri_2011": {"lb": e["lb"], "ub": e["ub"], "lb_key": e.get("lb_key"),
                      "ub_key": e.get("ub_key"), "n_optimal": e.get("n_optimal"),
                      "src": e.get("src"), "page": e.get("page")},
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


def construir(fontes: dict, ours: dict, sources: dict) -> dict:
    bounds = _json(fontes, "bounds", None)
    if bounds is None:
        raise SystemExit("bounds.json do coldcase não encontrado")
    mub = {chave(e["q"], e["n"], e["R"]): e for e in _json(fontes, "marosi_ub", [])}
    mlb = {chave(e["q"], e["n"], e["R"]): e for e in _json(fontes, "marosi_lb", [])
           if e.get("improves_best_known")}
    flo = tabela_florath(fontes)
    lit = tabela_florath(fontes, "post_keri_table")
    ev = evidencias_marosi(fontes)
    nossos = ours.get("cells", {})
    cells = []
    vistos = set()
    for e in bounds["entries"]:
        k = chave(e["q"], e["n"], e["R"])
        vistos.add(k)
        c = montar_celula(e, e.get("lb_updated"), mub.get(k), mlb.get(k), flo.get(k), ev.get(k), lit.get(k))
        cells.append(aplicar_nosso(c, nossos.get(k)))
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
