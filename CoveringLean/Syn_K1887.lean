-- gerado por scripts/syndrome/gen_syn.py; não editar à mão
import CoveringLean.SynBridge
import CoveringLean.SynLeaf_K1887_0
import CoveringLean.SynLeaf_K1887_1
import CoveringLean.SynLeaf_K1887_2
import CoveringLean.SynLeaf_K1887_3

/-! # K_7(8,3) ≤ 1887 pelo certificado por síndromes

Código: `Syn.LK1887` (sha256 canônico 98531afbd8afbcec54ec01d441836ce706f8702ece4df594447789af6732643b), união de 5 cosets completos de um
`[8,3]_7` (bloco de informação [0,3)) com 172 palavras de remendo;
2 síndromes órfãs (686 pontos checados um a um).
-/

namespace Syn

set_option maxRecDepth 100000

theorem hTK1887 : ∀ t < 16807, ∃ w, okT PK1887 t w = true :=
  all_of_chunks (fun t => ∃ w, okT PK1887 t w = true) 4096 5 16807 (by norm_num) (by
    intro c hc
    match c, hc with
    | 0, _ => exact fun i _ hlt => chkT_sound PK1887 _ _ _ _ TK1887_0 i (by omega)
    | 1, _ => exact fun i _ hlt => chkT_sound PK1887 _ _ _ _ TK1887_1 i (by omega)
    | 2, _ => exact fun i _ hlt => chkT_sound PK1887 _ _ _ _ TK1887_2 i (by omega)
    | 3, _ => exact fun i _ hlt => chkT_sound PK1887 _ _ _ _ TK1887_3 i (by omega)
    | 4, _ => exact fun i _ hlt => chkT_sound PK1887 _ _ _ _ TK1887_4 i (by omega)
    | c + 5, h => exact absurd h (by omega))

theorem hOK1887 : ∀ i < PK1887.orphs.length, ∀ a < 343, ∃ j, okO PK1887 (PK1887.orphs.getD i 0) a j = true := by
  intro i hi
  match i, hi with
  | 0, _ => exact chkO_sound PK1887 _ _ _ _ OK1887_0
  | 1, _ => exact chkO_sound PK1887 _ _ _ _ OK1887_1
  | i + 2, h => exact absurd h (by have : PK1887.orphs.length = 2 := rfl; omega)

theorem hBK1887 : ∀ s < PK1887.reps.length, ∀ m < 343, ∃ j, okB PK1887 s m j = true := by
  intro s hs
  match s, hs with
  | 0, _ => exact chkB_sound PK1887 _ _ _ _ BK1887_0
  | 1, _ => exact chkB_sound PK1887 _ _ _ _ BK1887_1
  | 2, _ => exact chkB_sound PK1887 _ _ _ _ BK1887_2
  | 3, _ => exact chkB_sound PK1887 _ _ _ _ BK1887_3
  | 4, _ => exact chkB_sound PK1887 _ _ _ _ BK1887_4
  | s + 5, h => exact absurd h (by have : PK1887.reps.length = 5 := rfl; omega)

/-- Não-vacuidade: o verificador recusa uma testemunha errada (ponto `t = 0`, palavra
`58` a distância 8 > 3). -/
example : okT PK1887 0 58 = false := by decide +kernel

/-- `K_7(8,3) ≤ 1887`: o código `LK1887` tem 1887 palavras e cobre com raio 3. -/
theorem K7_8_3_le_1887_syn :
    ∃ C : Finset (Fin 8 → ZMod 7), C.card = 1887 ∧ CoveringA2.Covers 3 C :=
  syn_cert PK1887 LK1887 rfl rfl rfl ⟨rfl, by decide⟩ VK1887 hTK1887 hOK1887 hBK1887
    (by decide +kernel) (by decide +kernel) (by decide +kernel)

end Syn

#print axioms Syn.K7_8_3_le_1887_syn
