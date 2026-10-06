-- GERADO por tools/literatura/gerar_lean.py; não edite à mão.
import CoveringLean.Surjetivo

/-! Ingrediente 2-sobrejetivo sobre `Z_5^7` com 29 palavras (data/literatura/surjetivos/ca_t2_n7_v5_N29.txt). -/

namespace CoveringLit

def L_t2_n7_v5_N29 : List Nat := [21753, 8238, 26835, 4942, 9533, 17556, 36605, 57198, 56082, 74741, 11629, 50094, 32968, 22640, 2545, 67722, 38021, 47137, 23424, 28622, 61790, 41277, 13451, 66661, 69175, 46439, 48351, 76258, 63734]

theorem S_t2_n7_v5_N29 : CoveringSurj.Surj 5 7 2 L_t2_n7_v5_N29 :=
  CoveringSurj.surj_of_check (by decide) (by decide +kernel)

end CoveringLit
