-- gerado por scripts/syndrome/gen_syn.py; não editar à mão
import CoveringLean.SynBridge
import CoveringLean.SynLeaf_K1285_0
import CoveringLean.SynLeaf_K1285_1
import CoveringLean.SynLeaf_K1285_2
import CoveringLean.SynLeaf_K1285_3
import CoveringLean.SynLeaf_K1285_4
import CoveringLean.SynLeaf_K1285_5
import CoveringLean.SynLeaf_K1285_6
import CoveringLean.SynLeaf_K1285_7
import CoveringLean.SynLeaf_K1285_8
import CoveringLean.SynLeaf_K1285_9
import CoveringLean.SynLeaf_K1285_10
import CoveringLean.SynLeaf_K1285_11
import CoveringLean.SynLeaf_K1285_12
import CoveringLean.SynLeaf_K1285_13
import CoveringLean.SynLeaf_K1285_14

/-! # K_7(9,4) ≤ 1285 pelo certificado por síndromes

Código: `Syn.LK1285` (sha256 canônico aa388cc9642bc064527a0237b60522ba558491291a2adf02ab1e4d8d3f756c1f), união de 3 cosets completos de um
`[9,3]_7` (bloco de informação [0,3)) com 256 palavras de remendo;
24 síndromes órfãs (8232 pontos checados um a um).
-/

namespace Syn

set_option maxRecDepth 100000

theorem hTK1285 : ∀ t < 117649, ∃ w, okT PK1285 t w = true :=
  all_of_chunks (fun t => ∃ w, okT PK1285 t w = true) 4096 29 117649 (by norm_num) (by
    intro c hc
    match c, hc with
    | 0, _ => exact fun i _ hlt => chkT_sound PK1285 _ _ _ _ TK1285_0 i (by omega)
    | 1, _ => exact fun i _ hlt => chkT_sound PK1285 _ _ _ _ TK1285_1 i (by omega)
    | 2, _ => exact fun i _ hlt => chkT_sound PK1285 _ _ _ _ TK1285_2 i (by omega)
    | 3, _ => exact fun i _ hlt => chkT_sound PK1285 _ _ _ _ TK1285_3 i (by omega)
    | 4, _ => exact fun i _ hlt => chkT_sound PK1285 _ _ _ _ TK1285_4 i (by omega)
    | 5, _ => exact fun i _ hlt => chkT_sound PK1285 _ _ _ _ TK1285_5 i (by omega)
    | 6, _ => exact fun i _ hlt => chkT_sound PK1285 _ _ _ _ TK1285_6 i (by omega)
    | 7, _ => exact fun i _ hlt => chkT_sound PK1285 _ _ _ _ TK1285_7 i (by omega)
    | 8, _ => exact fun i _ hlt => chkT_sound PK1285 _ _ _ _ TK1285_8 i (by omega)
    | 9, _ => exact fun i _ hlt => chkT_sound PK1285 _ _ _ _ TK1285_9 i (by omega)
    | 10, _ => exact fun i _ hlt => chkT_sound PK1285 _ _ _ _ TK1285_10 i (by omega)
    | 11, _ => exact fun i _ hlt => chkT_sound PK1285 _ _ _ _ TK1285_11 i (by omega)
    | 12, _ => exact fun i _ hlt => chkT_sound PK1285 _ _ _ _ TK1285_12 i (by omega)
    | 13, _ => exact fun i _ hlt => chkT_sound PK1285 _ _ _ _ TK1285_13 i (by omega)
    | 14, _ => exact fun i _ hlt => chkT_sound PK1285 _ _ _ _ TK1285_14 i (by omega)
    | 15, _ => exact fun i _ hlt => chkT_sound PK1285 _ _ _ _ TK1285_15 i (by omega)
    | 16, _ => exact fun i _ hlt => chkT_sound PK1285 _ _ _ _ TK1285_16 i (by omega)
    | 17, _ => exact fun i _ hlt => chkT_sound PK1285 _ _ _ _ TK1285_17 i (by omega)
    | 18, _ => exact fun i _ hlt => chkT_sound PK1285 _ _ _ _ TK1285_18 i (by omega)
    | 19, _ => exact fun i _ hlt => chkT_sound PK1285 _ _ _ _ TK1285_19 i (by omega)
    | 20, _ => exact fun i _ hlt => chkT_sound PK1285 _ _ _ _ TK1285_20 i (by omega)
    | 21, _ => exact fun i _ hlt => chkT_sound PK1285 _ _ _ _ TK1285_21 i (by omega)
    | 22, _ => exact fun i _ hlt => chkT_sound PK1285 _ _ _ _ TK1285_22 i (by omega)
    | 23, _ => exact fun i _ hlt => chkT_sound PK1285 _ _ _ _ TK1285_23 i (by omega)
    | 24, _ => exact fun i _ hlt => chkT_sound PK1285 _ _ _ _ TK1285_24 i (by omega)
    | 25, _ => exact fun i _ hlt => chkT_sound PK1285 _ _ _ _ TK1285_25 i (by omega)
    | 26, _ => exact fun i _ hlt => chkT_sound PK1285 _ _ _ _ TK1285_26 i (by omega)
    | 27, _ => exact fun i _ hlt => chkT_sound PK1285 _ _ _ _ TK1285_27 i (by omega)
    | 28, _ => exact fun i _ hlt => chkT_sound PK1285 _ _ _ _ TK1285_28 i (by omega)
    | c + 29, h => exact absurd h (by omega))

theorem hOK1285 : ∀ i < PK1285.orphs.length, ∀ a < 343, ∃ j, okO PK1285 (PK1285.orphs.getD i 0) a j = true := by
  intro i hi
  match i, hi with
  | 0, _ => exact chkO_sound PK1285 _ _ _ _ OK1285_0
  | 1, _ => exact chkO_sound PK1285 _ _ _ _ OK1285_1
  | 2, _ => exact chkO_sound PK1285 _ _ _ _ OK1285_2
  | 3, _ => exact chkO_sound PK1285 _ _ _ _ OK1285_3
  | 4, _ => exact chkO_sound PK1285 _ _ _ _ OK1285_4
  | 5, _ => exact chkO_sound PK1285 _ _ _ _ OK1285_5
  | 6, _ => exact chkO_sound PK1285 _ _ _ _ OK1285_6
  | 7, _ => exact chkO_sound PK1285 _ _ _ _ OK1285_7
  | 8, _ => exact chkO_sound PK1285 _ _ _ _ OK1285_8
  | 9, _ => exact chkO_sound PK1285 _ _ _ _ OK1285_9
  | 10, _ => exact chkO_sound PK1285 _ _ _ _ OK1285_10
  | 11, _ => exact chkO_sound PK1285 _ _ _ _ OK1285_11
  | 12, _ => exact chkO_sound PK1285 _ _ _ _ OK1285_12
  | 13, _ => exact chkO_sound PK1285 _ _ _ _ OK1285_13
  | 14, _ => exact chkO_sound PK1285 _ _ _ _ OK1285_14
  | 15, _ => exact chkO_sound PK1285 _ _ _ _ OK1285_15
  | 16, _ => exact chkO_sound PK1285 _ _ _ _ OK1285_16
  | 17, _ => exact chkO_sound PK1285 _ _ _ _ OK1285_17
  | 18, _ => exact chkO_sound PK1285 _ _ _ _ OK1285_18
  | 19, _ => exact chkO_sound PK1285 _ _ _ _ OK1285_19
  | 20, _ => exact chkO_sound PK1285 _ _ _ _ OK1285_20
  | 21, _ => exact chkO_sound PK1285 _ _ _ _ OK1285_21
  | 22, _ => exact chkO_sound PK1285 _ _ _ _ OK1285_22
  | 23, _ => exact chkO_sound PK1285 _ _ _ _ OK1285_23
  | i + 24, h => exact absurd h (by have : PK1285.orphs.length = 24 := rfl; omega)

theorem hBK1285 : ∀ s < PK1285.reps.length, ∀ m < 343, ∃ j, okB PK1285 s m j = true := by
  intro s hs
  match s, hs with
  | 0, _ => exact chkB_sound PK1285 _ _ _ _ BK1285_0
  | 1, _ => exact chkB_sound PK1285 _ _ _ _ BK1285_1
  | 2, _ => exact chkB_sound PK1285 _ _ _ _ BK1285_2
  | s + 3, h => exact absurd h (by have : PK1285.reps.length = 3 := rfl; omega)

/-- Não-vacuidade: o verificador recusa uma testemunha errada (ponto `t = 0`, palavra
`57` a distância 9 > 4). -/
example : okT PK1285 0 57 = false := by decide +kernel

/-- `K_7(9,4) ≤ 1285`: o código `LK1285` tem 1285 palavras e cobre com raio 4. -/
theorem K7_9_4_le_1285_syn :
    ∃ C : Finset (Fin 9 → ZMod 7), C.card = 1285 ∧ CoveringA2.Covers 4 C :=
  syn_cert PK1285 LK1285 rfl rfl rfl ⟨rfl, by decide⟩ VK1285 hTK1285 hOK1285 hBK1285
    (by decide +kernel) (by decide +kernel) (by decide +kernel)

end Syn

#print axioms Syn.K7_9_4_le_1285_syn
