-- GERADO por tools/literatura/gerar_lean.py; não edite à mão.
import CoveringLean.Surjetivo

/-! Ingrediente 2-sobrejetivo sobre `Z_7^4` com 49 palavras (Reed–Solomon estendido sobre GF(7)). -/

namespace CoveringLit

def L_t2_n4_v7_N49 : List Nat := [0, 448, 896, 1344, 1449, 1897, 2345, 57, 505, 953, 1058, 1506, 1954, 2353, 114, 562, 1010, 1115, 1563, 1962, 2067, 171, 619, 724, 1172, 1571, 2019, 2124, 228, 676, 781, 1180, 1628, 1733, 2181, 285, 390, 789, 1237, 1685, 1790, 2238, 342, 398, 846, 1294, 1399, 1847, 2295]

theorem S_t2_n4_v7_N49 : CoveringSurj.Surj 7 4 2 L_t2_n4_v7_N49 :=
  CoveringSurj.surj_of_check (by decide) (by decide +kernel)

end CoveringLit
