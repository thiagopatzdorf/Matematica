-- GERADO por tools/certificar/gerar.py (lineares.py); não edite à mão. Código linear de K5_6_1.
import CoveringLean.SynLinear
import CoveringLean.Regras

/-! `K_5(6,1) ≤ 625` por código linear (`Syn.lin_cert`); gerado, não edite à mão. -/

namespace CoveringLedger.Lin
open CoveringUB Syn

/-- [6,4]_5, G = [I_4 | P] (linha j = Σ dígito_i · 5^i), raio 1. -/
def P_K5_6_1 : Syn.Spec where
  q := 5
  n := 6
  k := 4
  o := 0
  R := 1
  Gs := [15001, 11880, 8775, 5750]
  reps := [0]
  orphs := []
  PN := 0
  b := 0
  cnt := 0

/-- Testemunhas dos pontos 0..24 do transversal, na base 626. -/
theorem T_K5_6_1_0 : chkT P_K5_6_1 626 25 0
    14163564782132617567407586584726814947916619744821363602861359826560 = true := by
  decide +kernel

set_option maxRecDepth 100000 in
theorem hT_K5_6_1 : ∀ t < 25, ∃ w, okT P_K5_6_1 t w = true :=
  all_of_chunks (fun t => ∃ w, okT P_K5_6_1 t w = true) 1024 1 25 (by norm_num) (by
    intro c hc
    match c, hc with
    | 0, _ => exact fun i _ hlt => chkT_sound P_K5_6_1 _ _ _ _ T_K5_6_1_0 i (by omega)
    | c + 1, h => exact absurd h (by omega))

set_option maxRecDepth 100000 in
theorem l_K5_6_1 : UB 5 6 1 625 :=
  UB.of_exists (Syn.lin_cert P_K5_6_1 rfl rfl rfl (by decide +kernel) ⟨rfl, by decide⟩
    (by decide +kernel) rfl rfl hT_K5_6_1)

end CoveringLedger.Lin
