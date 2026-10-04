#!/usr/bin/env python3
"""Valida Cartões de Problema (problems/SPEC.md) em stdlib pura.

    python3 tools/problems/validate.py problems/cartoes/algum.json
    python3 tools/problems/validate.py --all [--json]

Código de saída 0 só se todo cartão é válido. Confere: campos e tipos, enums, slug (e que o
nome do arquivo é `<id>.json`, para o id não divergir), unicidade de ids, coerência do
histórico com o ciclo de vida (lifecycle.py) e regras entre campos (ex.: `certificado` exige
prova Lean em `nosso`).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lifecycle  # noqa: E402

RAIZ = Path(__file__).resolve().parents[2]
PASTA = RAIZ / "problems" / "cartoes"
TIPOS = ("cota_superior", "cota_inferior", "valor_exato", "construcao", "formalizacao")
NOSSO_ESTADOS = ("nenhum", "computacional", "lrat", "lean")
CAMPOS = {"formato", "id", "titulo", "dominio", "tipo", "enunciado", "enunciado_formal", "estado",
          "melhor_conhecido", "nosso", "avaliador", "celula_ledger", "historico"}
OBRIGATORIOS = CAMPOS - {"enunciado_formal", "celula_ledger"}
SLUG = re.compile(r"^[a-z0-9][a-z0-9-]{2,63}$")
CELULA = re.compile(r"^K[0-9]+\([0-9]+,[0-9]+\)$")
# estados em que `nosso` já tem de carregar um valor (há candidato em pé)
COM_VALOR = {"candidato", "verificado", "certificado", "publicado"}


def _num(x) -> bool:
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def _obj(c: dict, chave: str, obrig: set[str], opc: set[str], erros: list[str]) -> dict:
    o = c.get(chave)
    if not isinstance(o, dict):
        erros.append(f"{chave}: deve ser objeto")
        return {}
    for k in sorted(obrig - set(o)):
        erros.append(f"{chave}.{k}: campo obrigatório ausente")
    for k in sorted(set(o) - obrig - opc):
        erros.append(f"{chave}.{k}: campo desconhecido")
    return o


def validar_cartao(c) -> list[str]:
    """Lista de erros do cartão (vazia = válido)."""
    if not isinstance(c, dict):
        return ["o cartão deve ser um objeto JSON"]
    erros: list[str] = []
    for k in sorted(OBRIGATORIOS - set(c)):
        erros.append(f"{k}: campo obrigatório ausente")
    for k in sorted(set(c) - CAMPOS):
        erros.append(f"{k}: campo desconhecido")
    if c.get("formato") != "cartao-problema/v1":
        erros.append('formato: deve ser "cartao-problema/v1"')
    if not isinstance(c.get("id"), str) or not SLUG.match(c["id"]):
        erros.append("id: slug minúsculo [a-z0-9-], 3 a 64 caracteres")
    for k, minimo in (("titulo", 3), ("enunciado", 10), ("dominio", 1)):
        if not isinstance(c.get(k), str) or len(c[k].strip()) < minimo:
            erros.append(f"{k}: texto obrigatório (mín. {minimo} caracteres)")
    if c.get("tipo") not in TIPOS:
        erros.append(f"tipo: um de {', '.join(TIPOS)}")
    if c.get("estado") not in lifecycle.ESTADOS:
        erros.append(f"estado: um de {', '.join(lifecycle.ESTADOS)}")
    ef = c.get("enunciado_formal")
    if ef is not None and not (isinstance(ef, str) and ef.strip()):
        erros.append("enunciado_formal: nome de declaração Lean ou null")
    cl = c.get("celula_ledger")
    if cl is not None and not (isinstance(cl, str) and CELULA.match(cl)):
        erros.append("celula_ledger: formato K<q>(<n>,<R>) ou null")

    mk = _obj(c, "melhor_conhecido", {"valor", "fonte", "ref"}, {"intervalo"}, erros)
    if mk:
        if mk.get("valor") is not None and not _num(mk["valor"]):
            erros.append("melhor_conhecido.valor: número ou null")
        for k in ("fonte", "ref"):
            if k in mk and not (isinstance(mk[k], str) and mk[k].strip()):
                erros.append(f"melhor_conhecido.{k}: texto obrigatório")
        iv = mk.get("intervalo")
        if iv is not None and not (isinstance(iv, dict) and set(iv) == {"lb", "ub"}
                                   and _num(iv["lb"]) and _num(iv["ub"]) and iv["lb"] <= iv["ub"]):
            erros.append("melhor_conhecido.intervalo: {lb, ub} numéricos com lb <= ub")
    no = _obj(c, "nosso", {"valor", "estado", "prova"}, set(), erros)
    if no:
        if "valor" in no and no["valor"] is not None and not _num(no["valor"]):
            erros.append("nosso.valor: número ou null")
        if no.get("estado") not in NOSSO_ESTADOS:
            erros.append(f"nosso.estado: um de {', '.join(NOSSO_ESTADOS)}")
        if "prova" in no and no["prova"] is not None and not (isinstance(no["prova"], str) and no["prova"].strip()):
            erros.append("nosso.prova: texto ou null")
        if (no.get("estado") == "nenhum") != (no.get("valor") is None):
            erros.append('nosso: `valor` é null se e só se `estado` é "nenhum"')
        if no.get("estado") not in (None, "nenhum") and not no.get("prova"):
            erros.append("nosso.prova: obrigatória quando há resultado nosso")
        if c.get("estado") in COM_VALOR and no.get("valor") is None:
            erros.append(f"nosso.valor: obrigatório no estado {c.get('estado')}")
        if c.get("estado") in ("certificado", "publicado") and no.get("estado") != "lean":
            erros.append('nosso.estado: "certificado"/"publicado" exigem kernel do Lean ("lean")')
    av = _obj(c, "avaliador", {"id", "como_rodar", "custo_estimado_usd"}, set(), erros)
    if av:
        for k in ("id", "como_rodar"):
            if k in av and not (isinstance(av[k], str) and av[k].strip()):
                erros.append(f"avaliador.{k}: texto obrigatório")
        if "custo_estimado_usd" in av and not (_num(av["custo_estimado_usd"]) and av["custo_estimado_usd"] >= 0):
            erros.append("avaliador.custo_estimado_usd: número >= 0")
    if not isinstance(c.get("historico"), list):
        erros.append("historico: deve ser lista")
    else:
        erros += ["historico: " + e for e in lifecycle.verificar_historico(c)]
    return erros


def validar_pasta(pasta: Path) -> dict[str, list[str]]:
    """{arquivo: erros} para todo *.json da pasta, mais a unicidade de ids."""
    res: dict[str, list[str]] = {}
    ids: dict[str, str] = {}
    for f in sorted(pasta.glob("*.json")):
        res[f.name] = validar_arquivo(f)
        try:
            i = json.loads(f.read_text(encoding="utf-8")).get("id")
        except (ValueError, AttributeError):
            continue
        if i in ids:
            res[f.name].append(f"id {i!r} repetido em {ids[i]}")
        ids.setdefault(i, f.name)
    return res


def validar_arquivo(f: Path) -> list[str]:
    try:
        c = json.loads(f.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        return [f"JSON ilegível: {e}"]
    erros = validar_cartao(c)
    if isinstance(c, dict) and isinstance(c.get("id"), str) and f.stem != c["id"]:
        erros.append(f"arquivo deve se chamar {c['id']}.json (o id é estável, o nome segue o id)")
    return erros


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("arquivos", nargs="*", type=Path)
    ap.add_argument("--all", action="store_true", help="todos os cartões de problems/cartoes/")
    ap.add_argument("--json", action="store_true", help="saída em JSON")
    a = ap.parse_args(argv)
    if a.all == bool(a.arquivos):
        ap.error("informe arquivos OU --all")
    if a.all:
        res = validar_pasta(PASTA)
    else:
        res = {str(f): validar_arquivo(f) for f in a.arquivos}
    invalidos = {k: v for k, v in res.items() if v}
    if a.json:
        print(json.dumps({"total": len(res), "invalidos": len(invalidos), "cartoes": res},
                         ensure_ascii=False, indent=2, sort_keys=True))
    else:
        for k, v in res.items():
            print(("INVÁLIDO " if v else "ok       ") + k)
            for e in v:
                print("    - " + e)
        print(f"{len(res) - len(invalidos)}/{len(res)} cartões válidos")
    return 1 if invalidos or not res else 0


if __name__ == "__main__":
    sys.exit(main())
