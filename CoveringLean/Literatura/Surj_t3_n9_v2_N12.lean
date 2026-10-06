-- GERADO por tools/literatura/gerar_lean.py; não edite à mão.
import CoveringLean.Surjetivo

/-! Ingrediente 3-sobrejetivo sobre `Z_2^9` com 12 palavras (data/literatura/surjetivos/ca_t3_n9_v2_N12.txt). -/

namespace CoveringLit

def L_t3_n9_v2_N12 : List Nat := [17, 99, 395, 376, 434, 301, 30, 255, 200, 326, 469, 164]

theorem S_t3_n9_v2_N12 : CoveringSurj.Surj 2 9 3 L_t3_n9_v2_N12 :=
  CoveringSurj.surj_of_check (by decide) (by decide +kernel)

end CoveringLit
