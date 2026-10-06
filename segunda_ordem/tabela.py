"""Monta e confere a tabela de K^(2)_q(n,r) a partir das testemunhas e dos certificados.

Uso (da raiz do repositório):

    python3 -m segunda_ordem.tabela conferir     # reconfere testemunhas e cotas, imprime a tabela
    python3 -m segunda_ordem.tabela gerar        # reescreve dados/tabela.json a partir do resto
    python3 -m segunda_ordem.tabela readme       # reescreve a tabela do README.md a partir do resto
    python3 -m segunda_ordem.tabela veripb Q N R   # RoundingSat + VeriPB: ótimo da célula
    python3 -m segunda_ordem.tabela drat Q N R [M] # CaDiCaL + drat-trim: nada com menos de M palavras
                                                   # (sem M: M = tamanho da testemunha)
    python3 -m segunda_ordem.tabela cubos Q N R M K  # o mesmo em 2^K cubos (disco de uma prova só)

Cada célula 1 ≤ r < n tem:
* cota inferior = máximo de: q (teorema das q palavras, r < n), K_q(n,r) do ledger,
  ⌈√K_{q²}(n,r)⌉ do ledger, cota da esfera, e o valor certificado (VeriPB ou DRAT) quando existe;
* cota superior = tamanho da menor testemunha, reconferida pelos dois verificadores de ``raio2``;
* estado "exato" só quando as duas cotas coincidem.

O ledger (``ledger/cells.json``) é só lido. As cotas dele são, na maioria, da literatura (estado
CLAIMED no próprio ledger); a tabela registra qual célula do ledger foi usada.
"""
from __future__ import annotations

import gzip
import hashlib
import json
import os
import shutil
import subprocess
import sys
from math import ceil
from pathlib import Path

from .codificacao import Codificacao
from .raio2 import cota_esfera, r2_bruto, r2_rapido, raiz_teto

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
DADOS = AQUI / "dados"
TESTEMUNHAS = DADOS / "testemunhas.json"
CERTIFICADOS = DADOS / "certificados.json"
TABELA = DADOS / "tabela.json"
PROVAS = DADOS / "provas"
LEDGER = RAIZ / "ledger" / "cells.json"

# Faixa da tabela: q=2 com n ≤ 7 e q=3 com n ≤ 5, todo 1 ≤ r < n.
FAIXA = {2: range(2, 8), 3: range(2, 6)}
LIMITE_BRUTO = 2_000_000  # q^{2n}·|C|^2 até aqui: confere também com o verificador ingênuo


def celulas():
    for q, ns in FAIXA.items():
        for n in ns:
            for r in range(1, n):
                yield q, n, r


def chave(q: int, n: int, r: int) -> str:
    return f"{q},{n},{r}"


def limiar_trivial(q: int, n: int) -> int:
    """Menor r com K^(2)_q(n,r) = q: r = n − ⌈n/q²⌉ (ver README, teorema das q palavras)."""
    return n - ceil(n / (q * q))


def _ledger_lb() -> dict[str, int]:
    dados = json.loads(LEDGER.read_text(encoding="utf-8"))["cells"]
    return {c["id"]: c["certification"]["lb"]["value"] for c in dados}


def cotas_livres(q: int, n: int, r: int, ledger: dict[str, int] | None = None) -> dict:
    """Cotas inferiores que não pedem busca nenhuma, com a origem de cada uma."""
    ledger = _ledger_lb() if ledger is None else ledger
    out = {"q_palavras": q, "esfera": cota_esfera(q, n, r)}
    k1 = ledger.get(f"K{q}({n},{r})")
    if k1 is not None:
        out["K_q"] = k1
    k2 = ledger.get(f"K{q * q}({n},{r})")
    if k2 is not None:
        out["raiz_K_q2"] = raiz_teto(k2)
        out["K_q2_lb"] = k2
    return out


def carregar(caminho: Path) -> dict:
    if not caminho.exists():
        return {}
    return json.loads(caminho.read_text(encoding="utf-8"))


def palavras_de(texto: list[str]) -> list[tuple[int, ...]]:
    return [tuple(int(ch) for ch in w) for w in texto]


def conferir_testemunha(q: int, n: int, r: int, palavras: list[str]) -> int:
    """Raio R_2 da testemunha pelos verificadores; levanta erro se eles divergem."""
    codigo = palavras_de(palavras)
    if len(set(codigo)) != len(codigo) or any(len(w) != n or max(w) >= q for w in codigo):
        raise ValueError(f"testemunha malformada em {chave(q, n, r)}")
    rap = r2_rapido(codigo, q, n)
    if q ** (2 * n) * len(codigo) ** 2 <= LIMITE_BRUTO:
        bru = r2_bruto(codigo, q, n)
        if bru != rap:
            raise AssertionError(f"verificadores divergem em {chave(q, n, r)}: {bru} != {rap}")
    return rap


def montar() -> dict:
    ledger = _ledger_lb()
    test = carregar(TESTEMUNHAS)
    cert = carregar(CERTIFICADOS)
    linhas = {}
    for q, n, r in celulas():
        k = chave(q, n, r)
        livres = cotas_livres(q, n, r, ledger)
        lb = max(v for kk, v in livres.items() if kk != "K_q2_lb")
        origem_lb = sorted(kk for kk, v in livres.items() if kk != "K_q2_lb" and v == lb)
        if r >= limiar_trivial(q, n):
            origem_lb = ["teorema_q_palavras"]
        c = cert.get(k)
        if c and c.get("verificado") and c["lb"] > lb:
            lb, origem_lb = c["lb"], [c["metodo"]]
        elif c and c.get("verificado") and c["lb"] == lb:
            origem_lb = origem_lb + [c["metodo"]]
        t = test.get(k)
        ub = len(t["palavras"]) if t else q ** (n - r)
        linhas[k] = {
            "q": q, "n": n, "r": r, "lb": lb, "ub": ub,
            "exato": lb == ub, "origem_lb": origem_lb,
            "origem_ub": "testemunha" if t else "construcao_q^(n-r)",
            "cotas_livres": livres,
        }
    return {"descricao": "K^(2)_q(n,r) = min |C| com R_2(C) <= r; gerado por segunda_ordem/tabela.py",
            "celulas": linhas}


def tabela_markdown(tab: dict) -> str:
    out = []
    for q in FAIXA:
        ns = list(FAIXA[q])
        out.append(f"\n**q = {q}**\n")
        out.append("| n \\ r | " + " | ".join(str(r) for r in range(1, ns[-1])) + " |")
        out.append("|---" * ns[-1] + "|")
        for n in ns:
            cel = []
            for r in range(1, ns[-1]):
                if r >= n:
                    cel.append("")
                    continue
                c = tab["celulas"][chave(q, n, r)]
                cel.append(str(c["ub"]) if c["exato"] else f"{c['lb']}–{c['ub']}")
            out.append(f"| {n} | " + " | ".join(cel) + " |")
    return "\n".join(out)


ROTULO_LB = {
    "teorema_q_palavras": "teorema das q palavras",
    "veripb": "VeriPB (ótimo)",
    "drat": "DRAT",
    "raiz_K_q2": "raiz de K_{q²} (ledger)",
    "K_q": "K_q (ledger)",
    "esfera": "esfera",
    "q_palavras": "q palavras",
}
INICIO, FIM = "<!-- tabela:inicio (gerado por tabela.py readme) -->", "<!-- tabela:fim -->"
README = AQUI / "README.md"


def estado_markdown(tab: dict) -> str:
    """Uma linha por célula: valor ou intervalo, e a origem de cada cota."""
    out = ["| q | n | r | K^(2) | estado | cota inferior | cota superior |", "|---|---|---|---|---|---|---|"]
    for c in tab["celulas"].values():
        valor = str(c["ub"]) if c["exato"] else f"{c['lb']}–{c['ub']}"
        estado = "exato" if c["exato"] else "intervalo"
        lb = f"{c['lb']}: " + ", ".join(ROTULO_LB[o] for o in c["origem_lb"])
        ub = f"{c['ub']}: " + ("testemunha" if c["origem_ub"] == "testemunha" else "q^(n−r)")
        out.append(f"| {c['q']} | {c['n']} | {c['r']} | {valor} | {estado} | {lb} | {ub} |")
    return "\n".join(out)


def bloco_readme(tab: dict) -> str:
    exatas = sum(c["exato"] for c in tab["celulas"].values())
    return "\n".join([
        INICIO,
        tabela_markdown(tab).lstrip("\n"),
        "",
        f"{exatas} de {len(tab['celulas'])} células exatas. Estado de cada uma:",
        "",
        estado_markdown(tab),
        FIM,
    ])


def conferir() -> dict:
    test = carregar(TESTEMUNHAS)
    for k, t in test.items():
        q, n, r = map(int, k.split(","))
        raio = conferir_testemunha(q, n, r, t["palavras"])
        if raio > r:
            raise AssertionError(f"testemunha de {k} tem R_2 = {raio} > {r}")
    tab = montar()
    for k, c in tab["celulas"].items():
        if c["lb"] > c["ub"]:
            raise AssertionError(f"cota inferior acima da superior em {k}: {c}")
    return tab


def _sha(caminho: Path) -> str:
    h = hashlib.sha256()
    with open(caminho, "rb") as f:
        for bloco in iter(lambda: f.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()


def _registrar(k: str, reg: dict, prova: Path) -> dict:
    velho = carregar(CERTIFICADOS).get(k, {}).get("prova_gz")
    if velho and (AQUI / velho).exists():
        (AQUI / velho).unlink()  # prova de uma cota substituída não fica órfã no repositório
    if prova.stat().st_size <= 4_000_000:
        PROVAS.mkdir(parents=True, exist_ok=True)
        destino = PROVAS / (prova.name + ".gz")
        with open(prova, "rb") as f, gzip.GzipFile(destino, "wb", mtime=0) as g:
            shutil.copyfileobj(f, g)
        if destino.stat().st_size > 1_500_000:
            destino.unlink()
        else:
            reg["prova_gz"] = f"dados/provas/{destino.name}"
    cert = carregar(CERTIFICADOS)
    cert[k] = reg
    CERTIFICADOS.write_text(json.dumps(cert, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return reg


def _binario(nome: str) -> str:
    caminho = os.environ.get(nome.upper().replace("-", "_")) or shutil.which(nome)
    if not caminho:
        raise SystemExit(f"defina {nome.upper().replace('-', '_')} (caminho do binário {nome})")
    return caminho


def certificar_veripb(q: int, n: int, r: int, trabalho: Path, tempo: int = 3600) -> dict:
    """RoundingSat minimiza |C| com log de prova; VeriPB confere o ótimo. Sem quebra de simetria
    além de 0 ∈ C. Binários: ROUNDINGSAT e VERIPB no ambiente (ou no PATH)."""
    rs, vp = _binario("roundingsat"), _binario("veripb")
    trabalho.mkdir(parents=True, exist_ok=True)
    base = trabalho / f"k2_q{q}_n{n}_r{r}"
    opb, prova = base.with_suffix(".opb"), base.with_suffix(".pbp")
    opb.write_text(Codificacao(q, n, r, fixar_zero=True).opb(), encoding="utf-8")
    saida = subprocess.run([rs, f"--proof-log={prova}", str(opb)], capture_output=True, text=True,
                           timeout=tempo).stdout
    otimo = [int(x.split()[1]) for x in saida.splitlines() if x.startswith("o ")]
    if "OPTIMUM FOUND" not in saida or not otimo:
        raise SystemExit(f"RoundingSat não fechou {chave(q, n, r)}")
    v = subprocess.run([vp, str(opb), str(prova)], capture_output=True, text=True, timeout=tempo).stdout
    reg = {
        "metodo": "veripb", "lb": otimo[-1],
        "verificado": f"VERIFIED BOUNDS {otimo[-1]} <= obj <= {otimo[-1]}" in v,
        "simetria": "só 0 ∈ C",
        "formula": "Codificacao(q, n, r, fixar_zero=True).opb()",
        "formula_sha256": _sha(opb), "prova_sha256": _sha(prova), "prova_bytes": prova.stat().st_size,
    }
    return _registrar(chave(q, n, r), reg, prova)


def certificar_drat(q: int, n: int, r: int, M: int, trabalho: Path, tempo: int | None = None) -> dict:
    # Só substitui um registro anterior se a cota nova for maior (rodar com M pequeno não apaga
    # um certificado melhor).
    """CaDiCaL prova que não existe código com |C| ≤ M−1 (com quebra de simetria lex-leader) e
    drat-trim confere a prova DRAT. Binários: CADICAL e DRAT_TRIM no ambiente (ou no PATH)."""
    cad, dt = _binario("cadical"), _binario("drat-trim")
    tempo = tempo or int(os.environ.get("SEGUNDA_ORDEM_TEMPO", "7200"))
    trabalho.mkdir(parents=True, exist_ok=True)
    base = trabalho / f"k2_q{q}_n{n}_r{r}_ate{M - 1}"
    cnf, prova = base.with_suffix(".cnf"), base.with_suffix(".drat")
    cod = Codificacao(q, n, r, fixar_zero=True)
    cod.quebrar_simetria()
    cnf.write_text(cod.dimacs(M - 1), encoding="utf-8")
    s = subprocess.run([cad, "-q", str(cnf), str(prova)], capture_output=True, text=True,
                       timeout=tempo).stdout
    if "s UNSATISFIABLE" not in s:
        raise SystemExit(f"CaDiCaL não refutou |C| <= {M - 1} em {chave(q, n, r)}")
    v = subprocess.run([dt, str(cnf), str(prova), "-t", str(tempo)], capture_output=True, text=True,
                       timeout=tempo + 60).stdout
    reg = {
        "metodo": "drat", "lb": M, "unsat_ate": M - 1,
        "verificado": any(linha.strip() == "s VERIFIED" for linha in v.splitlines()),
        "simetria": "0 ∈ C e x ≥lex g(x) para transposições de coordenadas e de símbolos",
        "formula": f"Codificacao(q, n, r, fixar_zero=True) + quebrar_simetria() + dimacs({M - 1})",
        "formula_sha256": _sha(cnf), "prova_sha256": _sha(prova), "prova_bytes": prova.stat().st_size,
    }
    anterior = carregar(CERTIFICADOS).get(chave(q, n, r))
    if anterior and anterior.get("verificado") and anterior["lb"] >= M:
        return anterior
    return _registrar(chave(q, n, r), reg, prova)


def certificar_drat_cubos(q: int, n: int, r: int, M: int, k: int, trabalho: Path,
                          tempo: int | None = None) -> dict:
    """Como ``certificar_drat``, mas dividido em 2^k cubos: os cubos fixam x_1..x_k (as palavras de
    índice 1..k) em todas as 2^k combinações, então juntos esgotam todas as atribuições. Cada cubo
    é a mesma fórmula mais k cláusulas unitárias; CaDiCaL refuta, drat-trim confere, e a prova é
    apagada antes do próximo cubo (o disco usado fica no tamanho de uma prova só). Retomável: o
    progresso fica em ``trabalho/<base>.progresso.json``."""
    cad, dt = _binario("cadical"), _binario("drat-trim")
    tempo = tempo or int(os.environ.get("SEGUNDA_ORDEM_TEMPO", "7200"))
    trabalho.mkdir(parents=True, exist_ok=True)
    base = trabalho / f"k2_q{q}_n{n}_r{r}_ate{M - 1}_cubos{k}"
    progresso_arq = base.with_suffix(".progresso.json")
    progresso = carregar(progresso_arq)
    cod = Codificacao(q, n, r, fixar_zero=True)
    cod.quebrar_simetria()
    texto = cod.dimacs(M - 1)
    cab, corpo = texto.split("\n", 1)
    nv, ncl = map(int, cab.split()[2:4])
    h_base = hashlib.sha256(texto.encode()).hexdigest()
    for i in range(2**k):
        chave_cubo = str(i)
        if progresso.get(chave_cubo, {}).get("verificado"):
            continue
        unidades = [(c + 1) if (i >> (c - 1)) & 1 else -(c + 1) for c in range(1, k + 1)]
        cnf, prova = base.with_suffix(f".c{i}.cnf"), base.with_suffix(f".c{i}.drat")
        cnf.write_text(f"p cnf {nv} {ncl + k}\n" + corpo + "".join(f"{u} 0\n" for u in unidades),
                       encoding="utf-8")
        s = subprocess.run([cad, "-q", str(cnf), str(prova)], capture_output=True, text=True,
                           timeout=tempo).stdout
        if "s UNSATISFIABLE" not in s:
            raise SystemExit(f"cubo {i} não refutado em {chave(q, n, r)}")
        v = subprocess.run([dt, str(cnf), str(prova), "-t", str(tempo)], capture_output=True,
                           text=True, timeout=tempo + 60).stdout
        progresso[chave_cubo] = {
            "unidades": unidades,
            "verificado": any(linha.strip() == "s VERIFIED" for linha in v.splitlines()),
            "cnf_sha256": _sha(cnf), "prova_sha256": _sha(prova), "prova_bytes": prova.stat().st_size,
        }
        prova.unlink()
        cnf.unlink()
        progresso_arq.write_text(json.dumps(progresso, indent=1, sort_keys=True) + "\n", encoding="utf-8")
        if not progresso[chave_cubo]["verificado"]:
            raise SystemExit(f"drat-trim recusou o cubo {i} em {chave(q, n, r)}")
    reg = {
        "metodo": "drat", "lb": M, "unsat_ate": M - 1,
        "verificado": all(progresso[str(i)]["verificado"] for i in range(2**k)),
        "simetria": "0 ∈ C e x ≥lex g(x) para transposições de coordenadas e de símbolos",
        "formula": f"Codificacao(q, n, r, fixar_zero=True) + quebrar_simetria() + dimacs({M - 1})",
        "formula_sha256": h_base,
        "cubos": {"k": k, "variaveis": list(range(2, k + 2)),
                  "nota": "2^k cubos sobre x_1..x_k (variáveis DIMACS 2..k+1); cada um com prova DRAT conferida",
                  "provas_sha256": [progresso[str(i)]["prova_sha256"] for i in range(2**k)],
                  "provas_bytes": sum(progresso[str(i)]["prova_bytes"] for i in range(2**k))},
    }
    anterior = carregar(CERTIFICADOS).get(chave(q, n, r))
    if anterior and anterior.get("verificado") and anterior["lb"] >= M:
        return anterior
    cert = carregar(CERTIFICADOS)
    cert[chave(q, n, r)] = reg
    CERTIFICADOS.write_text(json.dumps(cert, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return reg


def main(argv: list[str]) -> int:
    if not argv or argv[0] == "conferir":
        tab = conferir()
        print(tabela_markdown(tab))
        exatas = sum(c["exato"] for c in tab["celulas"].values())
        print(f"\n{exatas} de {len(tab['celulas'])} células exatas; testemunhas reconferidas.")
        return 0
    if argv[0] == "gerar":
        tab = conferir()
        TABELA.write_text(json.dumps(tab, indent=1, sort_keys=True, ensure_ascii=False) + "\n",
                          encoding="utf-8")
        print(f"gravado {TABELA.relative_to(RAIZ)}")
        return 0
    if argv[0] == "readme":
        texto = README.read_text(encoding="utf-8")
        antes, resto = texto.split(INICIO, 1)
        depois = resto.split(FIM, 1)[1]
        README.write_text(antes + bloco_readme(conferir()) + depois, encoding="utf-8")
        print(f"atualizado {README.relative_to(RAIZ)}")
        return 0
    if argv[0] == "cubos":
        q, n, r, M, k = map(int, argv[1:6])
        trabalho = Path(os.environ.get("SEGUNDA_ORDEM_TRABALHO", "segunda_ordem_trabalho"))
        print(json.dumps(certificar_drat_cubos(q, n, r, M, k, trabalho), indent=1, ensure_ascii=False))
        return 0
    if argv[0] in ("veripb", "drat"):
        q, n, r = map(int, argv[1:4])
        trabalho = Path(os.environ.get("SEGUNDA_ORDEM_TRABALHO", "segunda_ordem_trabalho"))
        if argv[0] == "veripb":
            reg = certificar_veripb(q, n, r, trabalho)
        else:
            # sem M: refuta logo abaixo da testemunha (prova o valor exato); com M: só "≥ M"
            M = int(argv[4]) if len(argv) > 4 else len(carregar(TESTEMUNHAS)[chave(q, n, r)]["palavras"])
            reg = certificar_drat(q, n, r, M, trabalho)
        print(json.dumps(reg, indent=1, ensure_ascii=False))
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))


__all__ = ["celulas", "cotas_livres", "conferir", "conferir_testemunha", "montar"]
