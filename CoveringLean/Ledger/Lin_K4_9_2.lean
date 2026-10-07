-- GERADO por tools/certificar/gerar.py (lineares.py); não edite à mão. Código linear de K4_9_2.
import CoveringLean.SynLinear
import CoveringLean.Regras

/-! `K_4(9,2) ≤ 1024` por código linear (`Syn.lin_cert`); gerado, não edite à mão. -/

namespace CoveringLedger.Lin
open CoveringUB Syn

/-- [9,5]_4, G = [I_5 | P] (linha j = Σ dígito_i · 4^i), raio 2. -/
def P_K4_9_2 : Syn.Spec where
  q := 4
  n := 9
  k := 5
  o := 0
  R := 2
  Gs := [18433, 152580, 244752, 123968, 94464]
  reps := [0]
  orphs := []
  PN := 0
  b := 0
  cnt := 0

/-- Testemunhas dos pontos 0..255 do transversal, na base 1025. -/
theorem T_K4_9_2_0 : chkT P_K4_9_2 1025 256 0
    6716122915067404563947987349713323087362472741231463998853215281508284281152699363082486293043734672757081671802179507157976181155157749609126584604645005655021865883521010728562624343577570685172425187874568879577461472675151478274737860085929504960374044056343382002265350849496491640237133249805575302478710090284222395704310933207511137798854303056449038582643055305097452788758154391880621356744608263814526622449269576682555014119004172697331650875869636621458586583303107441255995788477887251907899087340014120933040380609382349187391406135139175115868802270468458748925630099385976680724050440295007721827940933644211207390111711658166201855562907245056731476345586690621675052626645531369548573286963683384325814270708117551605675975146595012451171875000000000 = true := by
  decide +kernel

set_option maxRecDepth 100000 in
theorem hT_K4_9_2 : ∀ t < 256, ∃ w, okT P_K4_9_2 t w = true :=
  all_of_chunks (fun t => ∃ w, okT P_K4_9_2 t w = true) 1024 1 256 (by norm_num) (by
    intro c hc
    match c, hc with
    | 0, _ => exact fun i _ hlt => chkT_sound P_K4_9_2 _ _ _ _ T_K4_9_2_0 i (by omega)
    | c + 1, h => exact absurd h (by omega))

set_option maxRecDepth 100000 in
theorem l_K4_9_2 : UB 4 9 2 1024 :=
  UB.of_exists (Syn.lin_cert P_K4_9_2 rfl rfl rfl (by decide +kernel) ⟨rfl, by decide⟩
    (by decide +kernel) rfl rfl hT_K4_9_2)

end CoveringLedger.Lin
