-- GERADO por tools/literatura/gerar_lean.py; não edite à mão.
import CoveringLean.Surjetivo

/-! Ingrediente 2-sobrejetivo sobre `Z_4^4` com 16 palavras (Reed–Solomon estendido sobre GF(4)). -/

namespace CoveringLit

def L_t2_n4_v4_N16 : List Nat := [0, 100, 184, 220, 21, 113, 173, 201, 42, 78, 146, 246, 63, 91, 135, 227]

theorem S_t2_n4_v4_N16 : CoveringSurj.Surj 4 4 2 L_t2_n4_v4_N16 :=
  CoveringSurj.surj_of_check (by decide) (by decide +kernel)

end CoveringLit
