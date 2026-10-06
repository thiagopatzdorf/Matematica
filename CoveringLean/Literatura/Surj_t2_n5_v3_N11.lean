-- GERADO por tools/literatura/gerar_lean.py; não edite à mão.
import CoveringLean.Surjetivo

/-! Ingrediente 2-sobrejetivo sobre `Z_3^5` com 11 palavras (data/literatura/surjetivos/ca_t2_n5_v3_N11.txt). -/

namespace CoveringLit

def L_t2_n5_v3_N11 : List Nat := [11, 235, 197, 69, 140, 108, 174, 124, 105, 50, 4]

theorem S_t2_n5_v3_N11 : CoveringSurj.Surj 3 5 2 L_t2_n5_v3_N11 :=
  CoveringSurj.surj_of_check (by decide) (by decide +kernel)

end CoveringLit
