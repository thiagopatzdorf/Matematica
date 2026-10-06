-- GERADO por tools/literatura/gerar_lean.py; não edite à mão.
import CoveringLean.Surjetivo

/-! Ingrediente 3-sobrejetivo sobre `Z_2^7` com 12 palavras (data/literatura/surjetivos/ca_t3_n7_v2_N12.txt). -/

namespace CoveringLit

def L_t3_n7_v2_N12 : List Nat := [85, 48, 66, 126, 61, 100, 39, 19, 88, 14, 9, 107]

theorem S_t3_n7_v2_N12 : CoveringSurj.Surj 2 7 3 L_t3_n7_v2_N12 :=
  CoveringSurj.surj_of_check (by decide) (by decide +kernel)

end CoveringLit
