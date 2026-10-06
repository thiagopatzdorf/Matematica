#!/usr/bin/env python3
"""Gera os certificados Lean das cotas que vêm dos artigos de data/literatura/ (GERADO; não edite
os .lean à mão).

* Corolário 3 de Kéri–Östergård 2005 (chave `n`): um arquivo por ingrediente r-sobrejetivo,
  `CoveringLean/Literatura/Surj_t<t>_n<n>_v<v>_N<N>.lean` (a sobrejetividade conferida pelo kernel
  com `CoveringSurj.checkSurj`), e `CoveringLean/Literatura/KO05.lean` com um teorema
  `CoveringLit.K<q>_<n>_<R>_le_<M> : K q n R ≤ M` por célula (`CoveringSurj.ub`).
* Binários pequenos (q^n · M ≤ CUSTO_GO): `CoveringLean/Literatura/Binarios.lean`, witness explícito
  pelo verificador por prefixos `CoveringKernel.go` (`UB.of_go`), o caminho de K753_Upper.lean.
* Binários uniões de cosets: as especificações `data/literatura/syn/<tag>.json` para
  scripts/syndrome/gen_syn.py (certificado por síndromes, lib `CoveringSyn`).

Só entram células cuja cota publicada é igual à do código (as outras ficam no relatório).

    python3 tools/literatura/gerar_lean.py            # escreve
    python3 tools/literatura/gerar_lean.py --resumo   # só lista
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.set_int_max_str_digits(0)
sys.path.insert(0, str(Path(__file__).resolve().parent))
import codigos_papers as cp  # noqa: E402

RAIZ = cp.RAIZ
OUT = RAIZ / "CoveringLean" / "Literatura"
SYN = RAIZ / "data" / "literatura" / "syn"
CUSTO_GO = 1_200_000  # o mesmo teto de tools/certificar/gerar.py (q^n · M)
MAX_TRANSVERSAL = 1 << 17  # pontos do transversal do certificado por síndromes
HDR = "-- GERADO por tools/literatura/gerar_lean.py; não edite à mão.\n"
CHAVES_BIN = ("ostergard_kaikkonen_1998", "ostergard_weakley_1999",
              "hamalainen_honkala_kaikkonen_litsyn_1993")


def enc(w, v):
    return sum(x * v ** j for j, x in enumerate(w))


def defs_lista(nome, idx):
    """`def nome : List Nat`. Lista longa vira concatenação de literais de até 500 itens: um
    literal grande estoura o maxRecDepth da elaboração, e empacotar num Nat (Syn.unpack) custou
    12 GB no kernel para 14 641 palavras (cada passo do unpack é um Nat de 30 KB guardado em cache)."""
    if len(idx) <= 500:
        return f"def {nome} : List Nat := {idx}\n"
    partes = [idx[i:i + 500] for i in range(0, len(idx), 500)]
    out = "".join(f"def {nome}_{i} : List Nat := {c}\n" for i, c in enumerate(partes))
    return out + f"def {nome} : List Nat :=\n  " + " ++ ".join(f"{nome}_{i}" for i in range(len(partes))) + "\n"


QUEBRA = 5000  # N · C(n,t) acima disso: um teorema por lista de coordenadas (memória do kernel)


def prova_surj(nm, v, n, t, N):
    import itertools
    import math
    if N * math.comb(n, t) <= QUEBRA:
        return (f"theorem S_{nm} : CoveringSurj.Surj {v} {n} {t} L_{nm} :=\n"
                "  CoveringSurj.surj_of_check (by decide) (by decide +kernel)\n\n")
    Ls = [list(c) for c in itertools.combinations(range(n), t)]
    out = "".join(f"theorem M_{nm}_{i} : CoveringSurj.mapa {v} {ls} L_{nm} = 2 ^ {v} ^ {t} - 1 := by\n"
                  "  decide +kernel\n\n" for i, ls in enumerate(Ls))
    cadeia = "".join(f"List.forall_mem_cons.2 ⟨M_{nm}_{i}, " for i in range(len(Ls)))
    cadeia += "fun _ h => absurd h List.not_mem_nil" + "⟩" * len(Ls)
    # A cadeia de C(n,t) List.forall_mem_cons aninhados passa do maxRecDepth padrão para C(10,4) = 210.
    profundidade = "set_option maxRecDepth 20000 in\n" if len(Ls) > 100 else ""
    return out + profundidade + (f"theorem S_{nm} : CoveringSurj.Surj {v} {n} {t} L_{nm} :=\n"
                  f"  CoveringSurj.surj_of_mapas (by decide) {Ls} (by decide +kernel)\n    ({cadeia})\n\n")


def nome_ing(v, n, t, N):
    return f"t{t}_n{n}_v{v}_N{N}"


def citar(J):
    c = J["citacao"]
    return f"{', '.join(c['autores'])}, *{c['titulo']}*, {c['veiculo']} {c['volume']} ({c['ano']}) {c['paginas']}, DOI {c['doi']}"


def celulas_publicadas():
    return cp.celulas()


def alvo(c, M):
    """A célula entra se a publicada é M e a cota ainda não tem Lean, ou se o Lean já é deste gerador
    (regerar não pode derrubar o que ele mesmo certificou)."""
    if c is None or c["published"]["ub"]["value"] != M:
        return False
    ub = c["certification"]["ub"]
    if ub["state"] in ("CLAIMED", "WITNESS_CHECKED"):
        return True
    dec = ((ub.get("provenance") or {}).get("lean") or {}).get("declaration") or ""
    return dec.startswith(("CoveringLit.", "Syn.K2_"))


def ko05(escrever: bool):
    J = cp.carregar("keri_ostergard_2005")
    cells = celulas_publicadas()
    ings: dict = {}
    teoremas = []
    for it in J["itens"]:
        if it["tipo"] != "corolario3":
            continue
        q, n, R = it["q"], it["n"], it["R"]
        if not alvo(cells.get((q, n, R)), it["M"]):
            continue
        cod = cp.corolario3(q, n, R)
        assert cod and cod["M"] == it["M"] and cod["partes"] == it["partes"], it["id"]
        partes = []
        for g in cod["ingredientes"]:
            nm = nome_ing(g["v"], n, cod["t"], g["N"])
            ings[nm] = (g["v"], n, cod["t"], g["N"], g["palavras"], g["origem"])
            partes.append((g["off"], g["v"], nm))
        teoremas.append((q, n, R, cod["t"], it["M"], partes))
    if escrever:
        OUT.mkdir(parents=True, exist_ok=True)
        for nm, (v, n, t, N, ws, origem) in sorted(ings.items()):
            idx = [enc(w, v) for w in ws]
            assert cp.e_surjetivo(ws, v, n, t), nm
            (OUT / f"Surj_{nm}.lean").write_text(
                HDR + "import CoveringLean.Surjetivo\n\n"
                f"/-! Ingrediente {t}-sobrejetivo sobre `Z_{v}^{n}` com {N} palavras ({origem}). -/\n\n"
                "namespace CoveringLit\n\n"
                + defs_lista(f"L_{nm}", idx) + "\n" + prova_surj(nm, v, n, t, len(idx))
                + "end CoveringLit\n")
        linhas = [HDR + "import CoveringLean.Surjetivo\n"]
        linhas += [f"import CoveringLean.Literatura.Surj_{nm}\n" for nm in sorted(ings)]
        linhas.append(f"""
/-! # Cotas da chave `n` (Corolário 3 de Kéri–Östergård 2005)

{citar(J)}, Teorema 2 e Corolário 3 (pp. 54–55). Uma célula por teorema: a partição do alfabeto
e os ingredientes estão em `data/literatura/keri_ostergard_2005.json`; o código é
`CoveringSurj.codigo` e o raio vem de `CoveringSurj.cobre` (pombal). Reconferido fora do Lean por
`tools/literatura/codigos_papers.py` (exaustão dos ingredientes e força bruta onde q^n ≤ 3·10^6).
-/

namespace CoveringLit
open CoveringUB

""")
        for q, n, R, t, M, partes in teoremas:
            ps = ", ".join(f"⟨{o}, {v}, L_{nm}, S_{nm}⟩" for o, v, nm in partes)
            linhas.append(
                f"/-- K_{q}({n},{R}) ≤ {M}: blocos {[v for _, v, _ in partes]}. -/\n"
                f"theorem ub_K{q}_{n}_{R} : UB {q} {n} {R} {M} :=\n"
                f"  CoveringSurj.ub (n := {n}) (r := {t}) [{ps}]\n"
                "    (by decide) (by decide +kernel) (by decide) (by decide +kernel)\n\n"
                f"theorem K{q}_{n}_{R}_le_{M} : K {q} {n} {R} ≤ {M} := K_le ub_K{q}_{n}_{R}\n\n")
        linhas.append("end CoveringLit\n\n")
        for q, n, R, t, M, _p in teoremas:
            linhas.append(f"#print axioms CoveringLit.K{q}_{n}_{R}_le_{M}\n")
        (OUT / "KO05.lean").write_text("".join(linhas))
    return teoremas, ings


def binarios(escrever: bool):
    """Códigos binários dos artigos cuja cota é igual à publicada numa célula CLAIMED."""
    cells = celulas_publicadas()
    go, syn, fora = [], [], []
    vistos = set()
    for chave in CHAVES_BIN:
        J = cp.carregar(chave)
        for r in cp.reconstruir_binarios(chave):
            n, R, M = r["n"], r["R"], r["M"]
            c = cells.get((2, n, R))
            if not alvo(c, M):
                continue
            if (n, R) in vistos:
                continue
            assert cp.raio_ok_binario(r["palavras"], n, R) == 0, r["id"]
            vistos.add((n, R))
            reg = dict(r, citacao=citar(J), local=r["item"]["local"])
            if (1 << n) * M <= CUSTO_GO:
                go.append(reg)
                continue
            spec, dim = spec_syn(r["palavras"], n, R)
            if (1 << (n - dim)) <= MAX_TRANSVERSAL:
                syn.append((reg, spec, dim))
            else:
                fora.append((reg, dim))
    if escrever:
        OUT.mkdir(parents=True, exist_ok=True)
        ls = [HDR + "import CoveringLean.Regras\n\n/-! # Cotas binárias dos artigos, witness explícito pelo kernel\n\n"
              "Cada lista é o código reconstruído por `tools/literatura/codigos_papers.py` a partir de\n"
              "`data/literatura/<chave>.json` (índices little-endian: coordenada j = bit j).\n-/\n\n"
              "namespace CoveringLit\nopen CoveringUB\n\n"]
        for g in go:
            n, R, M = g["n"], g["R"], g["M"]
            ls.append(f"/-- {g['id']}: {g['local']}. {g['citacao']}. -/\n"
                      f"def W2_{n}_{R} : List Nat := {sorted(g['palavras'])}\n\n"
                      f"theorem ub_K2_{n}_{R} : UB 2 {n} {R} {M} :=\n"
                      f"  UB.of_go (L := W2_{n}_{R}) (by decide +kernel) (by decide +kernel)\n\n"
                      f"theorem K2_{n}_{R}_le_{M} : K 2 {n} {R} ≤ {M} := K_le ub_K2_{n}_{R}\n\n")
        ls.append("end CoveringLit\n\n")
        ls += [f"#print axioms CoveringLit.K2_{g['n']}_{g['R']}_le_{g['M']}\n" for g in go]
        (OUT / "Binarios.lean").write_text("".join(ls))
        SYN.mkdir(parents=True, exist_ok=True)
        for reg, spec, _d in syn:
            tag = tag_syn(reg)
            spec["origem"] = f"{reg['id']}: {reg['local']}. {reg['citacao']}."
            (SYN / f"{tag}.json").write_text(json.dumps(spec, ensure_ascii=False, indent=1) + "\n")
            subprocess.run([sys.executable, str(RAIZ / "scripts" / "syndrome" / "gen_syn.py"),
                            str(SYN / f"{tag}.json"), tag], check=True, capture_output=True)
    return go, syn, fora


def tag_syn(reg):
    return f"K2_{reg['n']}_{reg['R']}_{reg['M']}"


def bloco_contiguo(base, n):
    """Existe o tal que as colunas o..o+k-1 da geradora formam matriz invertível sobre GF(2)."""
    k = len(base)
    for o in range(n - k + 1):
        rows = [(b >> o) & ((1 << k) - 1) for b in base]
        posto = 0
        for bit in range(k):
            piv = next((i for i in range(posto, k) if rows[i] >> bit & 1), None)
            if piv is None:
                break
            rows[posto], rows[piv] = rows[piv], rows[posto]
            for i in range(k):
                if i != posto and rows[i] >> bit & 1:
                    rows[i] ^= rows[posto]
            posto += 1
        if posto == k:
            return True
    return False


def spec_syn(C, n, R):
    """Maior grupo de translações que fixa C (um código linear C0) e um representante por coset."""
    C = sorted(set(C))
    S = set(C)
    c0 = C[0]
    G = [g for g in (c ^ c0 for c in C) if all((c ^ g) in S for c in C)]
    base, piv = [], []
    for g in G:
        x = g
        for b, p in zip(base, piv):
            if x >> p & 1:
                x ^= b
        if x:
            base.append(x)
            piv.append(x.bit_length() - 1)
    while base and not bloco_contiguo(base, n):
        base.pop()  # gen_syn.py exige um bloco de informação contíguo; um subcódigo menor serve
    span = {0}
    for b in base:
        span |= {s ^ b for s in span}
    reps, vistos = [], set()
    for c in C:
        if c not in vistos:
            reps.append(c)
            vistos |= {c ^ s for s in span}
    assert len(reps) * len(span) == len(C)
    return ({"q": 2, "n": n, "R": R, "generator": [cp.i2s(b, n) for b in base],
             "coset_reps": [cp.i2s(r, n) for r in reps], "patch_words": []}, len(base))


def registrar(teoremas, go, syn, extras=()):
    """`ours_lean` em ledger/ours.json para cada célula certificada aqui (rode depois do lake build).
    Com código em data/codes/ a cota fica INDEPENDENTLY_REPRODUCED (verify.c + kernel); sem, FORMALIZED."""
    import hashlib
    ours_p = RAIZ / "ledger" / "ours.json"
    ours = json.loads(ours_p.read_text())
    regs = []
    for q, n, R, _t, M, _p in teoremas:
        regs.append((q, n, R, M, f"CoveringLit.K{q}_{n}_{R}_le_{M}", "CoveringLiteratura"))
    for g in go:
        regs.append((2, g["n"], g["R"], g["M"], f"CoveringLit.K2_{g['n']}_{g['R']}_le_{g['M']}", "CoveringLiteratura"))
    for reg, _s, _d in syn:
        regs.append((2, reg["n"], reg["R"], reg["M"], f"Syn.K2_{reg['n']}_{reg['R']}_le_{reg['M']}_syn", "CoveringSyn"))
    regs.extend(extras)
    for q, n, R, M, dec, lib in regs:
        chave = f"{q},{n},{R}"
        e = ours["cells"].setdefault(chave, {"ours_computational": None, "ours_lean": None})
        lean = {"M": M, "declaration": dec, "lib": lib, "tag": None}
        comp = e.get("ours_computational")
        arq = RAIZ / "data" / "codes" / f"q{q}_n{n}_R{R}_M{M}.txt"
        if comp and comp.get("file") == str(arq.relative_to(RAIZ)) and arq.exists():
            assert hashlib.sha256(arq.read_bytes()).hexdigest() == comp["sha256"], arq
            lean.update(file=comp["file"], sha256=comp["sha256"], provenance=comp["provenance"])
        e["ours_lean"] = lean
    ours_p.write_text(json.dumps(ours, ensure_ascii=False, indent=2) + "\n")
    return len(regs)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--resumo", action="store_true")
    ap.add_argument("--registrar", action="store_true",
                    help="registra em ledger/ours.json os teoremas (só depois do lake build verde)")
    a = ap.parse_args()
    t, ings = ko05(not a.resumo)
    go, syn, fora = binarios(not a.resumo)
    if a.registrar:
        extra = [(2, 14, 1, 1408, "CoveringLit.K2_14_1_le_1408", "CoveringLiteratura")]
        print("registradas:", registrar(t, go, syn, extra))
    print(f"KO05: {len(t)} células, {len(ings)} ingredientes")
    print("binários kernel:", [f"K2({g['n']},{g['R']})" for g in go])
    print("binários síndromes:", [f"K2({r['n']},{r['R']}) 2^{r['n'] - d}" for r, _s, d in syn])
    print("binários fora (transversal grande):", [f"K2({r['n']},{r['R']}) 2^{r['n'] - d}" for r, d in fora])


if __name__ == "__main__":
    main()
