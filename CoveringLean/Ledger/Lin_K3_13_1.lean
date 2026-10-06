-- GERADO por tools/certificar/gerar.py (lineares.py); não edite à mão. Código linear de K3_13_1.
import CoveringLean.SynLinear
import CoveringLean.Regras

/-! `K_3(13,1) ≤ 59049` por código linear (`Syn.lin_cert`); gerado, não edite à mão. -/

namespace CoveringLedger.Lin
open CoveringUB Syn

/-- [13,10]_3, G = [I_10 | P] (linha j = Σ dígito_i · 3^i), raio 1. -/
def P_K3_13_1 : Syn.Spec where
  q := 3
  n := 13
  k := 10
  o := 0
  R := 1
  Gs := [1417177, 885738, 1180989, 649566, 472473, 1535517, 1004562, 297432, 1364688, 846369]
  reps := [0]
  orphs := []
  PN := 0
  b := 0
  cnt := 0

/-- Testemunhas dos pontos 0..26 do transversal, na base 59050. -/
theorem T_K3_13_1_0 : chkT P_K3_13_1 59050 27 0
    2744817998264557935269254874270595408678981186511128005088387013996472791415352486361900219880237561057807282268941924700000000 = true := by
  decide +kernel

set_option maxRecDepth 100000 in
theorem hT_K3_13_1 : ∀ t < 27, ∃ w, okT P_K3_13_1 t w = true :=
  all_of_chunks (fun t => ∃ w, okT P_K3_13_1 t w = true) 1024 1 27 (by norm_num) (by
    intro c hc
    match c, hc with
    | 0, _ => exact fun i _ hlt => chkT_sound P_K3_13_1 _ _ _ _ T_K3_13_1_0 i (by omega)
    | c + 1, h => exact absurd h (by omega))

set_option maxRecDepth 100000 in
theorem l_K3_13_1 : UB 3 13 1 59049 :=
  UB.of_exists (Syn.lin_cert P_K3_13_1 rfl rfl rfl (by decide +kernel) ⟨rfl, by decide⟩
    (by decide +kernel) rfl rfl hT_K3_13_1)

end CoveringLedger.Lin
