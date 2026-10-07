-- GERADO por tools/certificar/gerar.py (lineares.py); não edite à mão. Código linear de K6_7_2.
import CoveringLean.SynLinear
import CoveringLean.Regras

/-! `K_6(7,2) ≤ 1296` por código linear (`Syn.lin_cert`); gerado, não edite à mão. -/

namespace CoveringLedger.Lin
open CoveringUB Syn

/-- [7,4]_6, G = [I_4 | P] (linha j = Σ dígito_i · 6^i), raio 2. -/
def P_K6_7_2 : Syn.Spec where
  q := 6
  n := 7
  k := 4
  o := 0
  R := 2
  Gs := [84241, 231990, 154260, 67608]
  reps := [0]
  orphs := []
  PN := 0
  b := 0
  cnt := 0

/-- Testemunhas dos pontos 0..215 do transversal, na base 1297. -/
theorem T_K6_7_2_0 : chkT P_K6_7_2 1297 216 0
    11522053418774817174056137693830910393068539580999553115879947654466782005658050747405561360011937285442583444560494484104611908348799226199421644778743301128934683189558990049484416770622827612176589155163150196082352287037916409152537252239568484469924142846495078687591826589403604798667314926259946180901398861362295789431122339435718557615933679454699222989466334041689569624186346782406134090427676389443108322357909335199056540637481962303717786973746272576955497328074589714443973163319302882627254429140445574891840739513347216173059260513265425179917333244756939508084672777231479803824152740897801352056757067093037002747562586159731627465860889183564201102442 = true := by
  decide +kernel

set_option maxRecDepth 100000 in
theorem hT_K6_7_2 : ∀ t < 216, ∃ w, okT P_K6_7_2 t w = true :=
  all_of_chunks (fun t => ∃ w, okT P_K6_7_2 t w = true) 1024 1 216 (by norm_num) (by
    intro c hc
    match c, hc with
    | 0, _ => exact fun i _ hlt => chkT_sound P_K6_7_2 _ _ _ _ T_K6_7_2_0 i (by omega)
    | c + 1, h => exact absurd h (by omega))

set_option maxRecDepth 100000 in
theorem l_K6_7_2 : UB 6 7 2 1296 :=
  UB.of_exists (Syn.lin_cert P_K6_7_2 rfl rfl rfl (by decide +kernel) ⟨rfl, by decide⟩
    (by decide +kernel) rfl rfl hT_K6_7_2)

end CoveringLedger.Lin
