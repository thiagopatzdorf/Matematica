-- GERADO por tools/certificar/gerar.py (lineares.py); não edite à mão. Código linear de K7_8_1.
import CoveringLean.SynLinear
import CoveringLean.Regras

/-! `K_7(8,1) ≤ 117649` por código linear (`Syn.lin_cert`); gerado, não edite à mão. -/

namespace CoveringLedger.Lin
open CoveringUB Syn

/-- [8,6]_7, G = [I_6 | P] (linha j = Σ dígito_i · 7^i), raio 1. -/
def P_K7_8_1 : Syn.Spec where
  q := 7
  n := 8
  k := 6
  o := 0
  R := 1
  Gs := [5647153, 4823616, 4000115, 3176866, 2355381, 1546244]
  reps := [0]
  orphs := []
  PN := 0
  b := 0
  cnt := 0

/-- Testemunhas dos pontos 0..48 do transversal, na base 117650. -/
theorem T_K7_8_1_0 : chkT P_K7_8_1 117650 49 0
    2460015768483765477871459896041208332804157668450217927094245111377614911170982469133532475894797351494601773734194390248287309148000846189424167301624461409374021649912331484891545560967652862494603205928461907464472238670484285781250000000000 = true := by
  decide +kernel

set_option maxRecDepth 100000 in
theorem hT_K7_8_1 : ∀ t < 49, ∃ w, okT P_K7_8_1 t w = true :=
  all_of_chunks (fun t => ∃ w, okT P_K7_8_1 t w = true) 1024 1 49 (by norm_num) (by
    intro c hc
    match c, hc with
    | 0, _ => exact fun i _ hlt => chkT_sound P_K7_8_1 _ _ _ _ T_K7_8_1_0 i (by omega)
    | c + 1, h => exact absurd h (by omega))

set_option maxRecDepth 100000 in
theorem l_K7_8_1 : UB 7 8 1 117649 :=
  UB.of_exists (Syn.lin_cert P_K7_8_1 rfl rfl rfl (by decide +kernel) ⟨rfl, by decide⟩
    (by decide +kernel) rfl rfl hT_K7_8_1)

end CoveringLedger.Lin
