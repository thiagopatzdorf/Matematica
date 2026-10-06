-- GERADO por tools/certificar/gerar.py (lineares.py); não edite à mão. Código linear de K2_15_1.
import CoveringLean.SynLinear
import CoveringLean.Regras

/-! `K_2(15,1) ≤ 2048` por código linear (`Syn.lin_cert`); gerado, não edite à mão. -/

namespace CoveringLedger.Lin
open CoveringUB Syn

/-- [15,11]_2, G = [I_11 | P] (linha j = Σ dígito_i · 2^i), raio 1. -/
def P_K2_15_1 : Syn.Spec where
  q := 2
  n := 15
  k := 11
  o := 0
  R := 1
  Gs := [24577, 20482, 12292, 28680, 18448, 10272, 26688, 6272, 22784, 14848, 31744]
  reps := [0]
  orphs := []
  PN := 0
  b := 0
  cnt := 0

/-- Testemunhas dos pontos 0..15 do transversal, na base 2049. -/
theorem T_K2_15_1_0 : chkT P_K2_15_1 2049 16 0
    48242632132200860311147561735496669903529736591427583 = true := by
  decide +kernel

set_option maxRecDepth 100000 in
theorem hT_K2_15_1 : ∀ t < 16, ∃ w, okT P_K2_15_1 t w = true :=
  all_of_chunks (fun t => ∃ w, okT P_K2_15_1 t w = true) 1024 1 16 (by norm_num) (by
    intro c hc
    match c, hc with
    | 0, _ => exact fun i _ hlt => chkT_sound P_K2_15_1 _ _ _ _ T_K2_15_1_0 i (by omega)
    | c + 1, h => exact absurd h (by omega))

set_option maxRecDepth 100000 in
theorem l_K2_15_1 : UB 2 15 1 2048 :=
  UB.of_exists (Syn.lin_cert P_K2_15_1 rfl rfl rfl (by decide +kernel) ⟨rfl, by decide⟩
    (by decide +kernel) rfl rfl hT_K2_15_1)

end CoveringLedger.Lin
