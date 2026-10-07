-- GERADO por tools/certificar/gerar.py (lineares.py); não edite à mão. Código linear de K2_13_4.
import CoveringLean.SynLinear
import CoveringLean.Regras

/-! `K_2(13,4) ≤ 16` por código linear (`Syn.lin_cert`); gerado, não edite à mão. -/

namespace CoveringLedger.Lin
open CoveringUB Syn

/-- [13,4]_2, G = [I_4 | P] (linha j = Σ dígito_i · 2^i), raio 4. -/
def P_K2_13_4 : Syn.Spec where
  q := 2
  n := 13
  k := 4
  o := 0
  R := 4
  Gs := [7665, 7842, 5876, 8088]
  reps := [0]
  orphs := []
  PN := 0
  b := 0
  cnt := 0

/-- Testemunhas dos pontos 0..511 do transversal, na base 17. -/
theorem T_K2_13_4_0 : chkT P_K2_13_4 17 512 0
    62534537827786803130941706571403865517526395485626736239426959121359342741055344331513029548851580407425920037293623282008951102237818201839955576783487098005195709040824258541327589825768442027656677541459100136794078892233807029528053334156326210173256771372745969260323520148441257727208461849919238715689158119088206140796777875706235320370405405964722426258719584108498693829156246113655600702728359303205643052334360613973667922134569307118900131546652368534539205797939722364070787939020112811204244542997102338793844920162562639509683074256731740050311590869801567409847814827034903400246707646355047031672759236858324559 = true := by
  decide +kernel

set_option maxRecDepth 100000 in
theorem hT_K2_13_4 : ∀ t < 512, ∃ w, okT P_K2_13_4 t w = true :=
  all_of_chunks (fun t => ∃ w, okT P_K2_13_4 t w = true) 1024 1 512 (by norm_num) (by
    intro c hc
    match c, hc with
    | 0, _ => exact fun i _ hlt => chkT_sound P_K2_13_4 _ _ _ _ T_K2_13_4_0 i (by omega)
    | c + 1, h => exact absurd h (by omega))

set_option maxRecDepth 100000 in
theorem l_K2_13_4 : UB 2 13 4 16 :=
  UB.of_exists (Syn.lin_cert P_K2_13_4 rfl rfl rfl (by decide +kernel) ⟨rfl, by decide⟩
    (by decide +kernel) rfl rfl hT_K2_13_4)

end CoveringLedger.Lin
