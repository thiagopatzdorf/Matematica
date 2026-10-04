#!/usr/bin/env python3
"""Gera os cartões semeados de problems/cartoes/ a partir de dados reais do repositório.

    python3 tools/problems/seed_from_ledger.py                 # grava problems/cartoes/*.json
    python3 tools/problems/seed_from_ledger.py --saida DIR     # grava em outra pasta
    python3 tools/problems/seed_from_ledger.py --reverificar   # roda o verificador e refaz problems/evidencias/

Determinístico: nenhum relógio, nenhum acaso; as datas vêm do ledger (`ours_atualizado`) e do
documento citado. Duas execuções dão bytes idênticos (o teste confere).

Fontes de cada valor, todas lidas aqui e nunca digitadas:
  * K7(9,4), K7(10,4), K7(8,3), K5(10,4): `ledger/cells.json` (cota publicada, nosso código e
    declaração Lean) e a saída do verificador oficial guardada em `problems/evidencias/`;
  * K_7(4,2): `docs/exatos/FASE1_B_K742.md` (resultado) e os registros
    `tools/exatos/k742/certificados/K7_4_2_M{17,18}.jsonl` (cada perfil UNSAT com LRAT conferido).
    O ledger ainda diz 17..19; o cartão diz isso em `melhor_conhecido` e o 19 em `nosso`.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lifecycle  # noqa: E402

RAIZ = Path(__file__).resolve().parents[2]
CELULAS = ("K7(9,4)", "K7(10,4)", "K7(8,3)", "K5(10,4)")
IMPORTADOR = "tools/problems/seed_from_ledger.py"
DOC_K742 = "docs/exatos/FASE1_B_K742.md"
CERTS_K742 = ("tools/exatos/k742/certificados/K7_4_2_M17.jsonl", "tools/exatos/k742/certificados/K7_4_2_M18.jsonl")


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def slug_celula(c: dict) -> str:
    return f"cobertura-k{c['q']}-{c['n']}-{c['R']}-ub"


def evidencia_verificador(c: dict, reverificar: bool, raiz: Path) -> dict:
    """Saída do verificador oficial (scripts/loop/verify_cover.py) para o código nosso."""
    nosso = c["ours_lean"]
    arq = raiz / "problems" / "evidencias" / f"{slug_celula(c)}.verificador.json"
    if reverificar:
        r = subprocess.run([sys.executable, str(raiz / "scripts/loop/verify_cover.py"), str(raiz / nosso["file"]),
                            str(c["q"]), str(c["n"]), str(c["R"])], capture_output=True, text=True, check=False)
        saida = json.loads(r.stdout.strip().splitlines()[-1])
        if r.returncode != 0 or not saida.get("ok"):
            raise SystemExit(f"verificador reprovou {c['id']}: {r.stdout}{r.stderr}")
        arq.parent.mkdir(parents=True, exist_ok=True)
        arq.write_text(json.dumps(saida, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    if not arq.exists():
        raise SystemExit(f"falta {arq.relative_to(raiz)}; rode com --reverificar")
    return json.loads(arq.read_text(encoding="utf-8"))


def cartao_cobertura(c: dict, ours_data: str, saida_verif: dict) -> dict:
    q, n, R = c["q"], c["n"], c["R"]
    nosso, pub = c["ours_lean"], c["published"]["ub"]
    sid = slug_celula(c)
    como = f"python3 scripts/loop/verify_cover.py {nosso['file']} {q} {n} {R}"
    cart = {
        "formato": "cartao-problema/v1", "id": sid,
        "titulo": f"K_{q}({n},{R}): cota superior",
        "dominio": "codigos-de-cobertura", "tipo": "cota_superior",
        "enunciado": (f"Exibir um código C ⊆ Z_{q}^{n} tal que toda palavra de Z_{q}^{n} está a distância de "
                      f"Hamming ≤ {R} de alguma palavra de C, com |C| = M o menor possível. "
                      f"K_{q}({n},{R}) é o mínimo desse M; uma cota superior é um código concreto."),
        "enunciado_formal": nosso["declaration"],
        "estado": "certificado",
        "melhor_conhecido": {"valor": pub["value"], "fonte": pub["source"], "ref": pub["ref"]},
        "nosso": {"valor": nosso["M"], "estado": "lean", "prova": nosso["declaration"]},
        "avaliador": {"id": "verify_cover", "como_rodar": como, "custo_estimado_usd": 0},
        "celula_ledger": c["id"],
        "historico": [],
    }
    base = {"quem": IMPORTADOR, "origem": "importacao", "quando": ours_data}
    passos = [
        ("proposto", "qualquer", {}),
        ("aceito", "mantenedor", {}),
        ("aberto", "mantenedor", {}),
        ("candidato", "qualquer", {"artefato": nosso["file"], "sha256": nosso["sha256"]}),
        ("verificado", "avaliador", {"avaliador": "verify_cover", "veredito": "ok",
                                      "saida": json.dumps(saida_verif, sort_keys=True, ensure_ascii=False),
                                      "como_rodar": como}),
        ("certificado", "avaliador", {"kernel": "lean", "declaracao": nosso["declaration"],
                                       "tag": nosso.get("tag"), "fonte": "ledger/cells.json (ours_lean)"}),
    ]
    return _aplicar(cart, passos, base)


def cartao_k742(c: dict, raiz: Path) -> dict:
    doc = (raiz / DOC_K742).read_text(encoding="utf-8")
    m_res = re.search(r"\*\*Resultado: K_7\(4,2\) = (\d+)\.\*\*", doc)
    m_ant = re.search(r"Antes: (\d+) ≤ K ≤ (\d+)", doc)
    m_data = re.search(r"\((\d{4}-\d{2}-\d{2})\)", doc.splitlines()[0])
    m_custo = re.search(r"\| exb-1 \|[^|]*\|[^|]*\|[^|]*\| ~US\$ ([0-9,]+) \|", doc)
    if not (m_res and m_ant and m_data and m_custo):
        raise SystemExit(f"{DOC_K742} mudou de forma; ajuste os regex de seed_from_ledger.py")
    exato, lb, ub = int(m_res[1]), int(m_ant[1]), int(m_ant[2])
    resumo = {}
    for rel in CERTS_K742:
        linhas = [json.loads(x) for x in (raiz / rel).read_text(encoding="utf-8").splitlines()]
        assert all(x["resultado"] == "UNSAT" and x["lrat_check"] == "VERIFIED" for x in linhas), rel
        resumo[f"M={linhas[0]['M']}"] = f"{len(linhas)}/{len(linhas)} perfis UNSAT, lrat-check VERIFIED"
    como = "python3 tools/exatos/k742/rodar.py --q 7 --M 18 --dir saida --prova"
    pub = c["published"]
    cart = {
        "formato": "cartao-problema/v1", "id": "cobertura-k7-4-2-exato",
        "titulo": "K_7(4,2): valor exato",
        "dominio": "codigos-de-cobertura", "tipo": "valor_exato",
        "enunciado": ("Determinar o menor número de palavras de um código C ⊆ Z_7^4 tal que toda palavra de "
                      "Z_7^4 está a distância de Hamming ≤ 2 de C. Fechar o valor exato exige uma cota "
                      "superior (código) e uma inferior (inexistência de código menor)."),
        "enunciado_formal": None,
        "estado": "verificado",
        "melhor_conhecido": {"valor": None, "fonte": pub["lb"]["source"], "ref": pub["lb"]["ref"],
                             "intervalo": {"lb": pub["lb"]["value"], "ub": pub["ub"]["value"]}},
        "nosso": {"valor": exato, "estado": "lrat",
                  "prova": f"{DOC_K742}; " + "; ".join(CERTS_K742)},
        "avaliador": {"id": "k742-lrat", "como_rodar": como, "custo_estimado_usd": float(m_custo[1].replace(",", "."))},
        "celula_ledger": c["id"],
        "historico": [],
    }
    assert (pub["lb"]["value"], pub["ub"]["value"]) == (lb, ub), "ledger e doc divergem no intervalo anterior"
    base = {"quem": IMPORTADOR, "origem": "importacao", "quando": m_data[1]}
    passos = [
        ("proposto", "qualquer", {}),
        ("aceito", "mantenedor", {}),
        ("aberto", "mantenedor", {}),
        ("candidato", "qualquer", {"artefato": CERTS_K742[1], "sha256": sha256(raiz / CERTS_K742[1]),
                                   "sha256_m17": sha256(raiz / CERTS_K742[0])}),
        ("verificado", "avaliador", {"avaliador": "k742-lrat", "veredito": "ok",
                                      "saida": json.dumps(resumo, sort_keys=True, ensure_ascii=False),
                                      "ref": DOC_K742, "como_rodar": como,
                                      "nota": "computacional com certificado LRAT; não é teorema no Lean, por isso não está certificado"}),
    ]
    return _aplicar(cart, passos, base)


def _aplicar(cart: dict, passos: list, base: dict) -> dict:
    estado = None
    hist = []
    for para, papel, ev in passos:
        e = {"quem": base["quem"], "papel": papel, "quando": base["quando"], "de": estado, "para": para,
             "evidencia": ev, "origem": "importacao"}
        lifecycle.checar({"avaliador": cart["avaliador"], "historico": hist}, estado, para, e["quem"], papel,
                         e["quando"], ev, importacao=True)
        hist.append(e)
        estado = para
    cart["historico"] = hist
    assert cart["estado"] == estado
    return cart


def gerar(raiz: Path = RAIZ, reverificar: bool = False) -> dict[str, dict]:
    ledger = json.loads((raiz / "ledger/cells.json").read_text(encoding="utf-8"))
    cells = {c["id"]: c for c in ledger["cells"]}
    data = ledger["meta"]["ours_atualizado"]
    out = {}
    for cid in CELULAS:
        c = cells[cid]
        cart = cartao_cobertura(c, data, evidencia_verificador(c, reverificar, raiz))
        out[cart["id"]] = cart
    k = cartao_k742(cells["K7(4,2)"], raiz)
    out[k["id"]] = k
    return out


def serializar(c: dict) -> str:
    return json.dumps(c, ensure_ascii=False, indent=2, sort_keys=False) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--saida", type=Path, default=RAIZ / "problems" / "cartoes")
    ap.add_argument("--reverificar", action="store_true", help="roda scripts/loop/verify_cover.py (~1 min)")
    a = ap.parse_args(argv)
    a.saida.mkdir(parents=True, exist_ok=True)
    for sid, cart in gerar(RAIZ, a.reverificar).items():
        (a.saida / f"{sid}.json").write_text(serializar(cart), encoding="utf-8")
        print(f"{sid}: {cart['estado']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
