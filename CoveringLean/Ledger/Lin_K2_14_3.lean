-- GERADO por tools/certificar/gerar.py (lineares.py); não edite à mão. Código linear de K2_14_3.
import CoveringLean.SynLinear
import CoveringLean.Regras

/-! `K_2(14,3) ≤ 64` por código linear (`Syn.lin_cert`); gerado, não edite à mão. -/

namespace CoveringLedger.Lin
open CoveringUB Syn

/-- [14,6]_2, G = [I_6 | P] (linha j = Σ dígito_i · 2^i), raio 3. -/
def P_K2_14_3 : Syn.Spec where
  q := 2
  n := 14
  k := 6
  o := 0
  R := 3
  Gs := [1921, 16194, 5572, 2888, 15248, 9952]
  reps := [0]
  orphs := []
  PN := 0
  b := 0
  cnt := 0

/-- Testemunhas dos pontos 0..255 do transversal, na base 65. -/
theorem T_K2_14_3_0 : chkT P_K2_14_3 65 256 0
    4409997991343463996369690861961444956822180535739039391231652476593449446026573190480809562247490531216111367338979150130713623540875612507891367630344182969358460192365410241573849760582908015593866519993992807753809111410008567270970764350075997786619985837392246442287700539235770990262460618010731625863538085675135383853618595697342939594938444626717864875035861330799714333972782974164246709023806656762888332769799024975655006320136376039925779815649843750 = true := by
  decide +kernel

set_option maxRecDepth 100000 in
theorem hT_K2_14_3 : ∀ t < 256, ∃ w, okT P_K2_14_3 t w = true :=
  all_of_chunks (fun t => ∃ w, okT P_K2_14_3 t w = true) 1024 1 256 (by norm_num) (by
    intro c hc
    match c, hc with
    | 0, _ => exact fun i _ hlt => chkT_sound P_K2_14_3 _ _ _ _ T_K2_14_3_0 i (by omega)
    | c + 1, h => exact absurd h (by omega))

set_option maxRecDepth 100000 in
theorem l_K2_14_3 : UB 2 14 3 64 :=
  UB.of_exists (Syn.lin_cert P_K2_14_3 rfl rfl rfl (by decide +kernel) ⟨rfl, by decide⟩
    (by decide +kernel) rfl rfl hT_K2_14_3)

end CoveringLedger.Lin
