-- GERADO por tools/literatura/gerar_lean.py; não edite à mão.
import CoveringLean.Surjetivo

/-! Ingrediente 2-sobrejetivo sobre `Z_5^6` com 25 palavras (Reed–Solomon estendido sobre GF(5)). -/

namespace CoveringLit

def L_t2_n6_v5_N25 : List Nat := [0, 6055, 8360, 11165, 13470, 781, 3711, 9016, 11321, 14226, 1562, 3867, 6672, 12077, 14882, 2343, 4523, 7428, 9733, 15038, 3124, 5279, 7584, 10389, 12694]

theorem S_t2_n6_v5_N25 : CoveringSurj.Surj 5 6 2 L_t2_n6_v5_N25 :=
  CoveringSurj.surj_of_check (by decide) (by decide +kernel)

end CoveringLit
