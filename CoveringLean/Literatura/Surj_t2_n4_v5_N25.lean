-- GERADO por tools/literatura/gerar_lean.py; não edite à mão.
import CoveringLean.Surjetivo

/-! Ingrediente 2-sobrejetivo sobre `Z_5^4` com 25 palavras (Reed–Solomon estendido sobre GF(5)). -/

namespace CoveringLit

def L_t2_n4_v5_N25 : List Nat := [0, 180, 360, 415, 595, 31, 211, 266, 446, 601, 62, 242, 297, 452, 507, 93, 148, 303, 483, 538, 124, 154, 334, 389, 569]

theorem S_t2_n4_v5_N25 : CoveringSurj.Surj 5 4 2 L_t2_n4_v5_N25 :=
  CoveringSurj.surj_of_check (by decide) (by decide +kernel)

end CoveringLit
