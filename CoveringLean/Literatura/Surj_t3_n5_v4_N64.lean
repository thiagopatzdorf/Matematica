-- GERADO por tools/literatura/gerar_lean.py; não edite à mão.
import CoveringLean.Surjetivo

/-! Ingrediente 3-sobrejetivo sobre `Z_4^5` com 64 palavras (Reed–Solomon estendido sobre GF(4)). -/

namespace CoveringLit

def L_t3_n5_v4_N64 : List Nat := [0, 436, 728, 876, 228, 336, 572, 904, 120, 460, 672, 788, 156, 296, 580, 1008, 85, 481, 653, 825, 177, 261, 617, 989, 45, 409, 757, 833, 201, 381, 529, 933, 170, 286, 626, 966, 78, 506, 662, 802, 210, 358, 522, 958, 54, 386, 750, 858, 255, 331, 551, 915, 27, 431, 707, 887, 135, 307, 607, 1003, 99, 471, 699, 783]

theorem S_t3_n5_v4_N64 : CoveringSurj.Surj 4 5 3 L_t3_n5_v4_N64 :=
  CoveringSurj.surj_of_check (by decide) (by decide +kernel)

end CoveringLit
