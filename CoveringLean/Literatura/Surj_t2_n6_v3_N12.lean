-- GERADO por tools/literatura/gerar_lean.py; não edite à mão.
import CoveringLean.Surjetivo

/-! Ingrediente 2-sobrejetivo sobre `Z_3^6` com 12 palavras (data/literatura/surjetivos/ca_t2_n6_v3_N12.txt). -/

namespace CoveringLit

def L_t2_n6_v3_N12 : List Nat := [671, 233, 129, 25, 29, 405, 359, 582, 685, 397, 309, 544]

theorem S_t2_n6_v3_N12 : CoveringSurj.Surj 3 6 2 L_t2_n6_v3_N12 :=
  CoveringSurj.surj_of_check (by decide) (by decide +kernel)

end CoveringLit
