-- GERADO por tools/certificar/gerar.py (lineares.py); não edite à mão. Código linear de K2_20_2.
import CoveringLean.SynLinear
import CoveringLean.Regras

/-! `K_2(20,2) ≤ 8192` por código linear (`Syn.lin_cert`); gerado, não edite à mão. -/

namespace CoveringLedger.Lin
open CoveringUB Syn

/-- [20,13]_2, G = [I_13 | P] (linha j = Σ dígito_i · 2^i), raio 2. -/
def P_K2_20_2 : Syn.Spec where
  q := 2
  n := 20
  k := 13
  o := 0
  R := 2
  Gs := [360449, 688130, 172036, 794632, 860176, 720928, 696384, 49280, 368896, 836096, 1041408, 223232, 757760]
  reps := [0]
  orphs := []
  PN := 0
  b := 0
  cnt := 0

/-- Testemunhas dos pontos 0..127 do transversal, na base 8193. -/
theorem T_K2_20_2_0 : chkT P_K2_20_2 8193 128 0
    104137763101481204611194039928289952446116177735727393737907087982073038566148021230231649556957694891720311313595677628313030358498531319455723735112925765878726377166658984878407050872788365907992552586422539534072133791079852678744059051529358737126555931268850454991312460690812282219909295204039394327823389859766496643386719333366008999482258695633282686033740905624795905584552193866369693233670639890498749713359177142484732147891803081294402697575751399247187123947218892415823895582530480708 = true := by
  decide +kernel

set_option maxRecDepth 100000 in
theorem hT_K2_20_2 : ∀ t < 128, ∃ w, okT P_K2_20_2 t w = true :=
  all_of_chunks (fun t => ∃ w, okT P_K2_20_2 t w = true) 1024 1 128 (by norm_num) (by
    intro c hc
    match c, hc with
    | 0, _ => exact fun i _ hlt => chkT_sound P_K2_20_2 _ _ _ _ T_K2_20_2_0 i (by omega)
    | c + 1, h => exact absurd h (by omega))

set_option maxRecDepth 100000 in
theorem l_K2_20_2 : UB 2 20 2 8192 :=
  UB.of_exists (Syn.lin_cert P_K2_20_2 rfl rfl rfl (by decide +kernel) ⟨rfl, by decide⟩
    (by decide +kernel) rfl rfl hT_K2_20_2)

end CoveringLedger.Lin
