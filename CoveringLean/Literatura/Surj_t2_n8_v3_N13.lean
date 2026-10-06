-- GERADO por tools/literatura/gerar_lean.py; não edite à mão.
import CoveringLean.Surjetivo

/-! Ingrediente 2-sobrejetivo sobre `Z_3^8` com 13 palavras (data/literatura/surjetivos/ca_t2_n8_v3_N13.txt). -/

namespace CoveringLit

def L_t2_n8_v3_N13 : List Nat := [1766, 3760, 3537, 2650, 1887, 607, 3614, 4545, 6404, 759, 5473, 3418, 4454]

theorem S_t2_n8_v3_N13 : CoveringSurj.Surj 3 8 2 L_t2_n8_v3_N13 :=
  CoveringSurj.surj_of_check (by decide) (by decide +kernel)

end CoveringLit
