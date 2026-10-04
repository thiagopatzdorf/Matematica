-- gerado por scripts/syndrome/gen_syn.py; não editar à mão
import CoveringLean.SynBridge
import CoveringLean.SynLeaf_K162_0
import CoveringLean.SynLeaf_K162_1
import CoveringLean.SynLeaf_K162_2
import CoveringLean.SynLeaf_K162_3
import CoveringLean.SynLeaf_K162_4
import CoveringLean.SynLeaf_K162_5
import CoveringLean.SynLeaf_K162_6
import CoveringLean.SynLeaf_K162_7

/-! # K_5(10,5) ≤ 162 pelo certificado por síndromes

Código: `Syn.LK162` (sha256 canônico 74176af64936119ce0d199e487127dff999888f93c7bde0b8386ba03ece12ce5), união de 1 cosets completos de um
`[10,3]_5` (bloco de informação [0,3)) com 37 palavras de remendo;
8 síndromes órfãs (1000 pontos checados um a um).
-/

namespace Syn

set_option maxRecDepth 100000

theorem hTK162 : ∀ t < 78125, ∃ w, okT PK162 t w = true :=
  all_of_chunks (fun t => ∃ w, okT PK162 t w = true) 4096 20 78125 (by norm_num) (by
    intro c hc
    match c, hc with
    | 0, _ => exact fun i _ hlt => chkT_sound PK162 _ _ _ _ TK162_0 i (by omega)
    | 1, _ => exact fun i _ hlt => chkT_sound PK162 _ _ _ _ TK162_1 i (by omega)
    | 2, _ => exact fun i _ hlt => chkT_sound PK162 _ _ _ _ TK162_2 i (by omega)
    | 3, _ => exact fun i _ hlt => chkT_sound PK162 _ _ _ _ TK162_3 i (by omega)
    | 4, _ => exact fun i _ hlt => chkT_sound PK162 _ _ _ _ TK162_4 i (by omega)
    | 5, _ => exact fun i _ hlt => chkT_sound PK162 _ _ _ _ TK162_5 i (by omega)
    | 6, _ => exact fun i _ hlt => chkT_sound PK162 _ _ _ _ TK162_6 i (by omega)
    | 7, _ => exact fun i _ hlt => chkT_sound PK162 _ _ _ _ TK162_7 i (by omega)
    | 8, _ => exact fun i _ hlt => chkT_sound PK162 _ _ _ _ TK162_8 i (by omega)
    | 9, _ => exact fun i _ hlt => chkT_sound PK162 _ _ _ _ TK162_9 i (by omega)
    | 10, _ => exact fun i _ hlt => chkT_sound PK162 _ _ _ _ TK162_10 i (by omega)
    | 11, _ => exact fun i _ hlt => chkT_sound PK162 _ _ _ _ TK162_11 i (by omega)
    | 12, _ => exact fun i _ hlt => chkT_sound PK162 _ _ _ _ TK162_12 i (by omega)
    | 13, _ => exact fun i _ hlt => chkT_sound PK162 _ _ _ _ TK162_13 i (by omega)
    | 14, _ => exact fun i _ hlt => chkT_sound PK162 _ _ _ _ TK162_14 i (by omega)
    | 15, _ => exact fun i _ hlt => chkT_sound PK162 _ _ _ _ TK162_15 i (by omega)
    | 16, _ => exact fun i _ hlt => chkT_sound PK162 _ _ _ _ TK162_16 i (by omega)
    | 17, _ => exact fun i _ hlt => chkT_sound PK162 _ _ _ _ TK162_17 i (by omega)
    | 18, _ => exact fun i _ hlt => chkT_sound PK162 _ _ _ _ TK162_18 i (by omega)
    | 19, _ => exact fun i _ hlt => chkT_sound PK162 _ _ _ _ TK162_19 i (by omega)
    | c + 20, h => exact absurd h (by omega))

theorem hOK162 : ∀ i < PK162.orphs.length, ∀ a < 125, ∃ j, okO PK162 (PK162.orphs.getD i 0) a j = true := by
  intro i hi
  match i, hi with
  | 0, _ => exact chkO_sound PK162 _ _ _ _ OK162_0
  | 1, _ => exact chkO_sound PK162 _ _ _ _ OK162_1
  | 2, _ => exact chkO_sound PK162 _ _ _ _ OK162_2
  | 3, _ => exact chkO_sound PK162 _ _ _ _ OK162_3
  | 4, _ => exact chkO_sound PK162 _ _ _ _ OK162_4
  | 5, _ => exact chkO_sound PK162 _ _ _ _ OK162_5
  | 6, _ => exact chkO_sound PK162 _ _ _ _ OK162_6
  | 7, _ => exact chkO_sound PK162 _ _ _ _ OK162_7
  | i + 8, h => exact absurd h (by have : PK162.orphs.length = 8 := rfl; omega)

theorem hBK162 : ∀ s < PK162.reps.length, ∀ m < 125, ∃ j, okB PK162 s m j = true := by
  intro s hs
  match s, hs with
  | 0, _ => exact chkB_sound PK162 _ _ _ _ BK162_0
  | s + 1, h => exact absurd h (by have : PK162.reps.length = 1 := rfl; omega)

/-- Não-vacuidade: o verificador recusa uma testemunha errada (ponto `t = 0`, palavra
`37` a distância 10 > 5). -/
example : okT PK162 0 37 = false := by decide +kernel

/-- `K_5(10,5) ≤ 162`: o código `LK162` tem 162 palavras e cobre com raio 5. -/
theorem K5_10_5_le_162_syn :
    ∃ C : Finset (Fin 10 → ZMod 5), C.card = 162 ∧ CoveringA2.Covers 5 C :=
  syn_cert PK162 LK162 rfl rfl rfl ⟨rfl, by decide⟩ VK162 hTK162 hOK162 hBK162
    (by decide +kernel) (by decide +kernel) (by decide +kernel)

end Syn

#print axioms Syn.K5_10_5_le_162_syn
