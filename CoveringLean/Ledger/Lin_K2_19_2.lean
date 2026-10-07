-- GERADO por tools/certificar/gerar.py (lineares.py); não edite à mão. Código linear de K2_19_2.
import CoveringLean.SynLinear
import CoveringLean.Regras

/-! `K_2(19,2) ≤ 4096` por código linear (`Syn.lin_cert`); gerado, não edite à mão. -/

namespace CoveringLedger.Lin
open CoveringUB Syn

/-- [19,12]_2, G = [I_12 | P] (linha j = Σ dígito_i · 2^i), raio 2. -/
def P_K2_19_2 : Syn.Spec where
  q := 2
  n := 19
  k := 12
  o := 0
  R := 2
  Gs := [217089, 180226, 430084, 245768, 61456, 94240, 467008, 118912, 147712, 373248, 13312, 43008]
  reps := [0]
  orphs := []
  PN := 0
  b := 0
  cnt := 0

/-- Testemunhas dos pontos 0..127 do transversal, na base 4097. -/
theorem T_K2_19_2_0 : chkT P_K2_19_2 4097 128 0
    466169240285937124654135297565218718643132361919982921274194865875485438250478985428170201662727989762613859593732308081381545088842410000015404172586280739147714120890405472489956771629057605505628303630146864704964814793696152585568816387115538765016778734151368433728496219387076958383685723176518746167875407931695168089965420516054569584133591483769892801765659726090392450033215150526087063220728359056904469094490963434468520483576316410649249210551070577 = true := by
  decide +kernel

set_option maxRecDepth 100000 in
theorem hT_K2_19_2 : ∀ t < 128, ∃ w, okT P_K2_19_2 t w = true :=
  all_of_chunks (fun t => ∃ w, okT P_K2_19_2 t w = true) 1024 1 128 (by norm_num) (by
    intro c hc
    match c, hc with
    | 0, _ => exact fun i _ hlt => chkT_sound P_K2_19_2 _ _ _ _ T_K2_19_2_0 i (by omega)
    | c + 1, h => exact absurd h (by omega))

set_option maxRecDepth 100000 in
theorem l_K2_19_2 : UB 2 19 2 4096 :=
  UB.of_exists (Syn.lin_cert P_K2_19_2 rfl rfl rfl (by decide +kernel) ⟨rfl, by decide⟩
    (by decide +kernel) rfl rfl hT_K2_19_2)

end CoveringLedger.Lin
