-- GERADO por tools/literatura/gerar_lean.py; não edite à mão.
import CoveringLean.Surjetivo

/-! Ingrediente 2-sobrejetivo sobre `Z_2^6` com 6 palavras (Kleitman–Spencer (6 linhas)). -/

namespace CoveringLit

def L_t2_n6_v2_N6 : List Nat := [0, 63, 7, 25, 42, 52]

theorem S_t2_n6_v2_N6 : CoveringSurj.Surj 2 6 2 L_t2_n6_v2_N6 :=
  CoveringSurj.surj_of_check (by decide) (by decide +kernel)

end CoveringLit
