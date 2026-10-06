-- GERADO por tools/literatura/gerar_lean.py; não edite à mão.
import CoveringLean.Surjetivo

/-! Ingrediente 2-sobrejetivo sobre `Z_1^7` com 1 palavras (trivial (uma palavra)). -/

namespace CoveringLit

def L_t2_n7_v1_N1 : List Nat := [0]

theorem S_t2_n7_v1_N1 : CoveringSurj.Surj 1 7 2 L_t2_n7_v1_N1 :=
  CoveringSurj.surj_of_check (by decide) (by decide +kernel)

end CoveringLit
