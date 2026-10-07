-- GERADO por tools/certificar/gerar.py (lineares.py); não edite à mão. Código linear de K2_13_2.
import CoveringLean.SynLinear
import CoveringLean.Regras

/-! `K_2(13,2) ≤ 128` por código linear (`Syn.lin_cert`); gerado, não edite à mão. -/

namespace CoveringLedger.Lin
open CoveringUB Syn

/-- [13,7]_2, G = [I_7 | P] (linha j = Σ dígito_i · 2^i), raio 2. -/
def P_K2_13_2 : Syn.Spec where
  q := 2
  n := 13
  k := 7
  o := 0
  R := 2
  Gs := [2305, 5250, 1924, 3976, 6800, 5664, 3136]
  reps := [0]
  orphs := []
  PN := 0
  b := 0
  cnt := 0

/-- Testemunhas dos pontos 0..63 do transversal, na base 129. -/
theorem T_K2_13_2_0 : chkT P_K2_13_2 129 64 0
    76553139553963160202190662703084804635413786123928200649453246051943098876701573985702769684160391786745873686472299533026256621954109 = true := by
  decide +kernel

set_option maxRecDepth 100000 in
theorem hT_K2_13_2 : ∀ t < 64, ∃ w, okT P_K2_13_2 t w = true :=
  all_of_chunks (fun t => ∃ w, okT P_K2_13_2 t w = true) 1024 1 64 (by norm_num) (by
    intro c hc
    match c, hc with
    | 0, _ => exact fun i _ hlt => chkT_sound P_K2_13_2 _ _ _ _ T_K2_13_2_0 i (by omega)
    | c + 1, h => exact absurd h (by omega))

set_option maxRecDepth 100000 in
theorem l_K2_13_2 : UB 2 13 2 128 :=
  UB.of_exists (Syn.lin_cert P_K2_13_2 rfl rfl rfl (by decide +kernel) ⟨rfl, by decide⟩
    (by decide +kernel) rfl rfl hT_K2_13_2)

end CoveringLedger.Lin
