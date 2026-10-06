-- GERADO por tools/literatura/gerar_lean.py; não edite à mão.
import CoveringLean.Surjetivo

/-! Ingrediente 2-sobrejetivo sobre `Z_3^7` com 12 palavras (data/literatura/surjetivos/ca_t2_n7_v3_N12.txt). -/

namespace CoveringLit

def L_t2_n7_v3_N12 : List Nat := [1367, 1760, 84, 1576, 1977, 724, 371, 1378, 1173, 259, 801, 1646]

theorem S_t2_n7_v3_N12 : CoveringSurj.Surj 3 7 2 L_t2_n7_v3_N12 :=
  CoveringSurj.surj_of_check (by decide) (by decide +kernel)

end CoveringLit
