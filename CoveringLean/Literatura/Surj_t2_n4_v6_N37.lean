-- GERADO por tools/literatura/gerar_lean.py; não edite à mão.
import CoveringLean.Surjetivo

/-! Ingrediente 2-sobrejetivo sobre `Z_6^4` com 37 palavras (data/literatura/surjetivos/ca_t2_n4_v6_N37.txt). -/

namespace CoveringLit

def L_t2_n4_v6_N37 : List Nat := [948, 210, 1183, 311, 747, 165, 1282, 258, 1238, 125, 1015, 792, 506, 325, 231, 61, 1197, 1104, 625, 700, 422, 839, 667, 80, 558, 920, 1000, 899, 514, 788, 605, 440, 1121, 1047, 501, 394, 4]

theorem S_t2_n4_v6_N37 : CoveringSurj.Surj 6 4 2 L_t2_n4_v6_N37 :=
  CoveringSurj.surj_of_check (by decide) (by decide +kernel)

end CoveringLit
