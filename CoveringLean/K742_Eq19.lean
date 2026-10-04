import CoveringLean.K742_Ponte
import CoveringLean.K742Sat.Refut
import CoveringLean.A6_Finite

/-!
# K_7(4,2) = 19, incondicional

As duas hipóteses de `K742.K_7_4_2_eq_19_of`, para a CNF sem a quebra de simetria (d)–(f):

* `K742Ponte.ponte18 : K742.Ponte18 (K742Cnf.cnfSemQuebra 7 18)` (alvo padrão);
* `K742Sat.refut18 : K742.Refut18 (K742Cnf.cnfSemQuebra 7 18)`: as 70 refutações LRAT
  conferidas pelo kernel com o verificador `LratK` (lib `CoveringK742Sat`, pesada: os dados
  vêm de `tools/exatos/k742/lean/preparar_semquebra.py`; ver `docs/exatos/LEAN_K742.md`).
-/

namespace K742

/-- **K_7(4,2) = 19**: existe código de raio 2 em `Z_7^4` com 19 palavras, e nenhum com menos. -/
theorem K_7_4_2_eq_19 :
    (∃ C : Finset (Fin 4 → ZMod 7), C.card = 19 ∧ CoveringA2.Covers 2 C) ∧
      ∀ C : Finset (Fin 4 → ZMod 7), C.card < 19 → ¬ CoveringA2.Covers 2 C :=
  K_7_4_2_eq_19_of K742Ponte.ponte18 K742Sat.refut18

/-- A mesma igualdade na forma `CoveringA6.IsK` (palavras em `Fin 4 → Fin 7`). -/
theorem K_7_4_2_isK : CoveringA6.IsK 7 4 2 19 := K_7_4_2_eq_19

end K742

#print axioms K742.K_7_4_2_eq_19
#print axioms K742.K_7_4_2_isK
