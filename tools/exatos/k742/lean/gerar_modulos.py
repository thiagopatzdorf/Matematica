#!/usr/bin/env python3
"""Escreve os módulos Lean das refutações sem quebra (lib `CoveringK742Sat`).

    python3 tools/exatos/k742/lean/gerar_modulos.py [--perfis 55,65]

Lê `tools/exatos/k742/lean/semquebra_M18.jsonl` (uma linha por perfil, a saída de
`preparar_semquebra.py`) e escreve, para cada perfil `p`:

* `CoveringLean/K742Sat/S<p>/Data.lean`  (`lratk_data`),
* `CoveringLean/K742Sat/S<p>/B<m>.lean`  (`lratk_steps`, um por arquivo `h<m>.txt`),
* `CoveringLean/K742Sat/S<p>/Final.lean` (`lratk_final … for K742Cnf.cnfSemQuebra 7 18 t`),

e `CoveringLean/K742Sat/Refut.lean`, que junta os 70 em `K742Sat.refut18 :
K742.Refut18 (K742Cnf.cnfSemQuebra 7 18)`.
"""
import argparse
import json
import os

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.abspath(os.path.join(AQUI, "..", "..", "..", ".."))
SAT = os.path.join(RAIZ, "CoveringLean", "K742Sat")


def tipos_lean(tipos):
    return "[" + ", ".join("[" + ",".join(c for c in t) + "]" for t in tipos) + "]"


def escrever(caminho, texto):
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    with open(caminho, "w") as f:
        f.write(texto)


def modulos_perfil(e):
    p = e["perfil"]
    d = os.path.join(SAT, f"S{p}")
    dados = f"../dados/s{p:04d}"
    ns = f"s{p}"
    cab = (f"/-! K_7(4,2), M = 18, perfil {p} (`{' | '.join(e['tipos'])}`), CNF sem a quebra (d)–(f).\n"
           f"Gerado por `tools/exatos/k742/lean/gerar_modulos.py`; dados por `preparar_semquebra.py`\n"
           f"(sha256 em `tools/exatos/k742/lean/semquebra_M18.jsonl`). -/\n")
    escrever(os.path.join(d, "Data.lean"),
             f"import CoveringLean.LratKData\n\n{cab}\nnamespace K742Sat\n\n"
             f"lratk_data {ns} \"{dados}\"\n\nend K742Sat\n")
    for m in e["modulos"]:
        escrever(os.path.join(d, f"B{m['modulo']}.lean"),
                 f"import CoveringLean.K742Sat.S{p}.Data\n\n{cab}\nnamespace K742Sat\n\n"
                 f"lratk_steps {ns} \"{dados}/h{m['modulo']}.txt\"\n\nend K742Sat\n")
    imps = "".join(f"import CoveringLean.K742Sat.S{p}.B{m['modulo']}\n" for m in e["modulos"])
    escrever(os.path.join(d, "Final.lean"),
             f"{imps}import CoveringLean.K742_Cnf\n\n{cab}\nnamespace K742Sat\n\n"
             f"lratk_final {ns} \"{dados}\"\n  for K742Cnf.cnfSemQuebra 7 18 {tipos_lean(e['tipos'])}\n\n"
             f"end K742Sat\n\n#print axioms K742Sat.{ns}.unsatFor\n")


def refut(perfis):
    imps = "".join(f"import CoveringLean.K742Sat.S{p}.Final\n" for p in perfis)
    casos = "\n".join(f"  · exact K742Sat.s{p}.unsatFor" for p in perfis)
    texto = f"""{imps}import CoveringLean.K742_Final

/-!
# `Refut18` para a CNF sem quebra: as 70 refutações, no kernel

Cada `K742Sat.s<p>.unsatFor : LratK.Unsat (K742Cnf.cnfSemQuebra 7 18 t_p)` vem de um verificador
LRAT provado correto (`LratK`), executado pelo kernel. Gerado por
`tools/exatos/k742/lean/gerar_modulos.py`.
-/

namespace K742Sat

set_option maxRecDepth 100000 in
/-- **As 70 CNFs sem quebra de `M = 18` são insatisfatíveis.** -/
theorem refut18 : K742.Refut18 (K742Cnf.cnfSemQuebra 7 18) := by
  intro t ht
  simp only [K742.perfis18, List.mem_cons, List.not_mem_nil, or_false] at ht
  rcases ht with {" | ".join("rfl" for _ in perfis)}
{casos}

end K742Sat

#print axioms K742Sat.refut18
"""
    escrever(os.path.join(SAT, "Refut.lean"), texto)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--perfis", default="")
    ap.add_argument("--refut", action="store_true", help="escreve também Refut.lean (precisa dos 70)")
    a = ap.parse_args()
    reg = {}
    with open(os.path.join(AQUI, "semquebra_M18.jsonl")) as f:
        for ln in f:
            e = json.loads(ln)
            reg[e["perfil"]] = e
    perfis = [int(x) for x in a.perfis.split(",")] if a.perfis else sorted(reg)
    for p in perfis:
        modulos_perfil(reg[p])
    if a.refut:
        assert sorted(reg) == list(range(70)), "faltam perfis"
        refut(list(range(70)))


if __name__ == "__main__":
    main()
