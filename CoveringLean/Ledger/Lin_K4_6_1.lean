-- GERADO por tools/certificar/gerar.py (lineares.py); não edite à mão. Código linear de K4_6_1.
import CoveringLean.SynLinear
import CoveringLean.Regras

/-! `K_4(6,1) ≤ 256` por código linear (`Syn.lin_cert`); gerado, não edite à mão. -/

namespace CoveringLedger.Lin
open CoveringUB Syn

/-- [6,4]_4, G = [I_4 | P] (linha j = Σ dígito_i · 4^i), raio 1. -/
def P_K4_6_1 : Syn.Spec where
  q := 4
  n := 6
  k := 4
  o := 0
  R := 1
  Gs := [1793, 2820, 1296, 3648]
  reps := [0]
  orphs := []
  PN := 0
  b := 0
  cnt := 0

/-- Testemunhas dos pontos 0..15 do transversal, na base 257. -/
theorem T_K4_6_1_0 : chkT P_K4_6_1 257 16 0
    67996384438628706882675851778486766558 = true := by
  decide +kernel

set_option maxRecDepth 100000 in
theorem hT_K4_6_1 : ∀ t < 16, ∃ w, okT P_K4_6_1 t w = true :=
  all_of_chunks (fun t => ∃ w, okT P_K4_6_1 t w = true) 1024 1 16 (by norm_num) (by
    intro c hc
    match c, hc with
    | 0, _ => exact fun i _ hlt => chkT_sound P_K4_6_1 _ _ _ _ T_K4_6_1_0 i (by omega)
    | c + 1, h => exact absurd h (by omega))

set_option maxRecDepth 100000 in
theorem l_K4_6_1 : UB 4 6 1 256 :=
  UB.of_exists (Syn.lin_cert P_K4_6_1 rfl rfl rfl (by decide +kernel) ⟨rfl, by decide⟩
    (by decide +kernel) rfl rfl hT_K4_6_1)

end CoveringLedger.Lin
