-- GERADO por tools/literatura/gerar_lean.py; não edite à mão.
import CoveringLean.Surjetivo

/-! Ingrediente 2-sobrejetivo sobre `Z_5^5` com 25 palavras (Reed–Solomon estendido sobre GF(5)). -/

namespace CoveringLit

def L_t2_n5_v5_N25 : List Nat := [0, 1055, 1485, 2415, 2845, 156, 1211, 1516, 1946, 2976, 312, 742, 1672, 2077, 3007, 468, 773, 1803, 2233, 2538, 624, 904, 1334, 2264, 2694]

theorem S_t2_n5_v5_N25 : CoveringSurj.Surj 5 5 2 L_t2_n5_v5_N25 :=
  CoveringSurj.surj_of_check (by decide) (by decide +kernel)

end CoveringLit
