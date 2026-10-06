-- GERADO por tools/literatura/gerar_lean.py; não edite à mão.
import CoveringLean.Surjetivo

/-! Ingrediente 3-sobrejetivo sobre `Z_3^7` com 40 palavras (data/literatura/surjetivos/ca_t3_n7_v3_N40.txt). -/

namespace CoveringLit

def L_t3_n7_v3_N40 : List Nat := [520, 952, 2095, 1083, 371, 1352, 1282, 2125, 1484, 774, 87, 251, 2004, 2138, 1685, 211, 854, 391, 1428, 1171, 1914, 1041, 603, 59, 1867, 1211, 2048, 1078, 459, 1614, 1567, 1774, 1791, 903, 507, 665, 1217, 10, 1742, 728]

theorem S_t3_n7_v3_N40 : CoveringSurj.Surj 3 7 3 L_t3_n7_v3_N40 :=
  CoveringSurj.surj_of_check (by decide) (by decide +kernel)

end CoveringLit
