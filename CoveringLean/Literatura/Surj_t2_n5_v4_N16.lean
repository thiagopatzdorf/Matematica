-- GERADO por tools/literatura/gerar_lean.py; não edite à mão.
import CoveringLean.Surjetivo

/-! Ingrediente 2-sobrejetivo sobre `Z_4^5` com 16 palavras (Reed–Solomon estendido sobre GF(4)). -/

namespace CoveringLit

def L_t2_n5_v4_N16 : List Nat := [0, 484, 632, 924, 85, 433, 557, 969, 170, 334, 722, 822, 255, 283, 647, 867]

theorem S_t2_n5_v4_N16 : CoveringSurj.Surj 4 5 2 L_t2_n5_v4_N16 :=
  CoveringSurj.surj_of_check (by decide) (by decide +kernel)

end CoveringLit
