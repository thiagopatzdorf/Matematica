-- GERADO por tools/certificar/gerar.py (lineares.py); não edite à mão. Código linear de K3_11_2.
import CoveringLean.SynLinear
import CoveringLean.Regras

/-! `K_3(11,2) ≤ 729` por código linear (`Syn.lin_cert`); gerado, não edite à mão. -/

namespace CoveringLedger.Lin
open CoveringUB Syn

/-- [11,6]_3, G = [I_6 | P] (linha j = Σ dígito_i · 3^i), raio 2. -/
def P_K3_11_2 : Syn.Spec where
  q := 3
  n := 11
  k := 6
  o := 0
  R := 2
  Gs := [106435, 116643, 68535, 160407, 56214, 168642]
  reps := [0]
  orphs := []
  PN := 0
  b := 0
  cnt := 0

/-- Testemunhas dos pontos 0..242 do transversal, na base 730. -/
theorem T_K3_11_2_0 : chkT P_K3_11_2 730 243 0
    15118712250180849679909436639310451882425910512200398263527027236611094043838350504307673817552475357217140711773519800224641822371974240246269319989101314243827321859312523431798918231748719676949020170916683715912768660827296423487941599811722738417436151466009380206901029718011600360721265809994545753378604973301270280928594212081040005918718760052347799949525217408418436292798610141929042839895862998119502819283283415698146388499142250626734846369034451585655773007309437770608252057672939078515058875685851843213342938826320369838420472538248294355853155869978558491940279698901556560779486729513419755118485104591273112243282811738427208852946026831402157125803791953660270000000000000 = true := by
  decide +kernel

set_option maxRecDepth 100000 in
theorem hT_K3_11_2 : ∀ t < 243, ∃ w, okT P_K3_11_2 t w = true :=
  all_of_chunks (fun t => ∃ w, okT P_K3_11_2 t w = true) 1024 1 243 (by norm_num) (by
    intro c hc
    match c, hc with
    | 0, _ => exact fun i _ hlt => chkT_sound P_K3_11_2 _ _ _ _ T_K3_11_2_0 i (by omega)
    | c + 1, h => exact absurd h (by omega))

set_option maxRecDepth 100000 in
theorem l_K3_11_2 : UB 3 11 2 729 :=
  UB.of_exists (Syn.lin_cert P_K3_11_2 rfl rfl rfl (by decide +kernel) ⟨rfl, by decide⟩
    (by decide +kernel) rfl rfl hT_K3_11_2)

end CoveringLedger.Lin
