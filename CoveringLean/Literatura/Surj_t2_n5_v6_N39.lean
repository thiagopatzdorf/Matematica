-- GERADO por tools/literatura/gerar_lean.py; não edite à mão.
import CoveringLean.Surjetivo

/-! Ingrediente 2-sobrejetivo sobre `Z_6^5` com 39 palavras (data/literatura/surjetivos/ca_t2_n5_v6_N39.txt). -/

namespace CoveringLit

def L_t2_n5_v6_N39 : List Nat := [4892, 1152, 561, 6328, 3555, 2543, 5924, 3933, 4187, 5831, 2930, 7000, 4770, 1716, 6751, 3781, 2278, 1766, 3174, 250, 5547, 7526, 6205, 4345, 3306, 2794, 5304, 6272, 4684, 1959, 5163, 917, 7265, 170, 835, 1399, 6486, 2597, 7737]

theorem S_t2_n5_v6_N39 : CoveringSurj.Surj 6 5 2 L_t2_n5_v6_N39 :=
  CoveringSurj.surj_of_check (by decide) (by decide +kernel)

end CoveringLit
