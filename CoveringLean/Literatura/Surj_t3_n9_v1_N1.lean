-- GERADO por tools/literatura/gerar_lean.py; não edite à mão.
import CoveringLean.Surjetivo

/-! Ingrediente 3-sobrejetivo sobre `Z_1^9` com 1 palavras (trivial (uma palavra)). -/

namespace CoveringLit

def L_t3_n9_v1_N1 : List Nat := [0]

theorem S_t3_n9_v1_N1 : CoveringSurj.Surj 1 9 3 L_t3_n9_v1_N1 :=
  CoveringSurj.surj_of_check (by decide) (by decide +kernel)

end CoveringLit
