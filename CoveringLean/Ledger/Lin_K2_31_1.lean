-- GERADO por tools/certificar/gerar.py (lineares.py); não edite à mão. Código linear de K2_31_1.
import CoveringLean.SynLinear
import CoveringLean.Regras

/-! `K_2(31,1) ≤ 67108864` por código linear (`Syn.lin_cert`); gerado, não edite à mão. -/

namespace CoveringLedger.Lin
open CoveringUB Syn

/-- [31,26]_2, G = [I_26 | P] (linha j = Σ dígito_i · 2^i), raio 1. -/
def P_K2_31_1 : Syn.Spec where
  q := 2
  n := 31
  k := 26
  o := 0
  R := 1
  Gs := [1610612737, 1342177282, 805306372, 1879048200, 1207959568, 671088672, 1744830528, 402653312, 1476395264, 939524608, 2013266944, 1140852736, 603983872, 1677729792, 335560704, 1409318912, 872480768, 1946288128, 201588736, 1275592704, 739246080, 1814036480, 473956352, 1551892480, 1023410176, 2113929216]
  reps := [0]
  orphs := []
  PN := 0
  b := 0
  cnt := 0

/-- Testemunhas dos pontos 0..31 do transversal, na base 67108865. -/
theorem T_K2_31_1_0 : chkT P_K2_31_1 67108865 32 0
    14319458573915788261443192097010993000264825825750018217785340258962165907403920392569479198958333911169541276908821856763613731912674943434964433362125698955257427550243748320464294882028137669305201256909897731840044640349687467267477237888372965375 = true := by
  decide +kernel

set_option maxRecDepth 100000 in
theorem hT_K2_31_1 : ∀ t < 32, ∃ w, okT P_K2_31_1 t w = true :=
  all_of_chunks (fun t => ∃ w, okT P_K2_31_1 t w = true) 1024 1 32 (by norm_num) (by
    intro c hc
    match c, hc with
    | 0, _ => exact fun i _ hlt => chkT_sound P_K2_31_1 _ _ _ _ T_K2_31_1_0 i (by omega)
    | c + 1, h => exact absurd h (by omega))

set_option maxRecDepth 100000 in
theorem l_K2_31_1 : UB 2 31 1 67108864 :=
  UB.of_exists (Syn.lin_cert P_K2_31_1 rfl rfl rfl (by decide +kernel) ⟨rfl, by decide⟩
    (by decide +kernel) rfl rfl hT_K2_31_1)

end CoveringLedger.Lin
