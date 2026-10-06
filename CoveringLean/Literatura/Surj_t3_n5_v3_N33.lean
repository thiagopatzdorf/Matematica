-- GERADO por tools/literatura/gerar_lean.py; não edite à mão.
import CoveringLean.Surjetivo

/-! Ingrediente 3-sobrejetivo sobre `Z_3^5` com 33 palavras (data/literatura/surjetivos/ca_t3_n5_v3_N33.txt). -/

namespace CoveringLit

def L_t3_n5_v3_N33 : List Nat := [163, 104, 25, 189, 64, 223, 57, 85, 213, 87, 34, 38, 42, 18, 159, 238, 137, 13, 149, 179, 120, 236, 2, 151, 80, 90, 202, 225, 50, 194, 116, 127, 183]

theorem S_t3_n5_v3_N33 : CoveringSurj.Surj 3 5 3 L_t3_n5_v3_N33 :=
  CoveringSurj.surj_of_check (by decide) (by decide +kernel)

end CoveringLit
