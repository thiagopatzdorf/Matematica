-- GERADO por tools/literatura/gerar_lean.py; não edite à mão.
import CoveringLean.Surjetivo

/-! Ingrediente 2-sobrejetivo sobre `Z_4^7` com 21 palavras (data/literatura/surjetivos/ca_t2_n7_v4_N21.txt). -/

namespace CoveringLit

def L_t2_n7_v4_N21 : List Nat := [11573, 12662, 15271, 5747, 8029, 8841, 1253, 8671, 16108, 10336, 13336, 3474, 4131, 3147, 5508, 6634, 2582, 9998, 1016, 2238, 15297]

theorem S_t2_n7_v4_N21 : CoveringSurj.Surj 4 7 2 L_t2_n7_v4_N21 :=
  CoveringSurj.surj_of_check (by decide) (by decide +kernel)

end CoveringLit
