-- GERADO por tools/certificar/gerar.py (lineares.py); não edite à mão. Código linear de K5_6_2.
import CoveringLean.SynLinear
import CoveringLean.Regras

/-! `K_5(6,2) ≤ 125` por código linear (`Syn.lin_cert`); gerado, não edite à mão. -/

namespace CoveringLedger.Lin
open CoveringUB Syn

/-- [6,3]_5, G = [I_3 | P] (linha j = Σ dígito_i · 5^i), raio 2. -/
def P_K5_6_2 : Syn.Spec where
  q := 5
  n := 6
  k := 3
  o := 0
  R := 2
  Gs := [3251, 7005, 11150]
  reps := [0]
  orphs := []
  PN := 0
  b := 0
  cnt := 0

/-- Testemunhas dos pontos 0..124 do transversal, na base 126. -/
theorem T_K5_6_2_0 : chkT P_K5_6_2 126 125 0
    1229538736116176999744340639797125770700256896806281719857395219526194640993278912307833753145156027854264918054886375679347604481518018475863372936025373894501726083975951582137789948957869916902947100032382585896470610156230647694303364224803264608827794816960 = true := by
  decide +kernel

set_option maxRecDepth 100000 in
theorem hT_K5_6_2 : ∀ t < 125, ∃ w, okT P_K5_6_2 t w = true :=
  all_of_chunks (fun t => ∃ w, okT P_K5_6_2 t w = true) 1024 1 125 (by norm_num) (by
    intro c hc
    match c, hc with
    | 0, _ => exact fun i _ hlt => chkT_sound P_K5_6_2 _ _ _ _ T_K5_6_2_0 i (by omega)
    | c + 1, h => exact absurd h (by omega))

set_option maxRecDepth 100000 in
theorem l_K5_6_2 : UB 5 6 2 125 :=
  UB.of_exists (Syn.lin_cert P_K5_6_2 rfl rfl rfl (by decide +kernel) ⟨rfl, by decide⟩
    (by decide +kernel) rfl rfl hT_K5_6_2)

end CoveringLedger.Lin
