-- gerado por scripts/syndrome/gen_syn.py; não editar à mão
import CoveringLean.SynBridge
import CoveringLean.SynLeaf_K1351_0
import CoveringLean.SynLeaf_K1351_1
import CoveringLean.SynLeaf_K1351_2
import CoveringLean.SynLeaf_K1351_3
import CoveringLean.SynLeaf_K1351_4
import CoveringLean.SynLeaf_K1351_5
import CoveringLean.SynLeaf_K1351_6
import CoveringLean.SynLeaf_K1351_7
import CoveringLean.SynLeaf_K1351_8
import CoveringLean.SynLeaf_K1351_9
import CoveringLean.SynLeaf_K1351_10
import CoveringLean.SynLeaf_K1351_11
import CoveringLean.SynLeaf_K1351_12
import CoveringLean.SynLeaf_K1351_13
import CoveringLean.SynLeaf_K1351_14

/-! # K_7(9,4) ≤ 1351 pelo certificado por síndromes

Código: `Syn.LK1351` (sha256 canônico 54dbdade1337432303847d2fd0d1c13b506de08ba518e1694c5fb37ed0e81162), união de 3 cosets completos de um
`[9,3]_7` (bloco de informação [0,3)) com 322 palavras de remendo;
27 síndromes órfãs (9261 pontos checados um a um).
-/

namespace Syn

set_option maxRecDepth 100000

theorem hTK1351 : ∀ t < 117649, ∃ w, okT PK1351 t w = true :=
  all_of_chunks (fun t => ∃ w, okT PK1351 t w = true) 4096 29 117649 (by norm_num) (by
    intro c hc
    match c, hc with
    | 0, _ => exact fun i _ hlt => chkT_sound PK1351 _ _ _ _ TK1351_0 i (by omega)
    | 1, _ => exact fun i _ hlt => chkT_sound PK1351 _ _ _ _ TK1351_1 i (by omega)
    | 2, _ => exact fun i _ hlt => chkT_sound PK1351 _ _ _ _ TK1351_2 i (by omega)
    | 3, _ => exact fun i _ hlt => chkT_sound PK1351 _ _ _ _ TK1351_3 i (by omega)
    | 4, _ => exact fun i _ hlt => chkT_sound PK1351 _ _ _ _ TK1351_4 i (by omega)
    | 5, _ => exact fun i _ hlt => chkT_sound PK1351 _ _ _ _ TK1351_5 i (by omega)
    | 6, _ => exact fun i _ hlt => chkT_sound PK1351 _ _ _ _ TK1351_6 i (by omega)
    | 7, _ => exact fun i _ hlt => chkT_sound PK1351 _ _ _ _ TK1351_7 i (by omega)
    | 8, _ => exact fun i _ hlt => chkT_sound PK1351 _ _ _ _ TK1351_8 i (by omega)
    | 9, _ => exact fun i _ hlt => chkT_sound PK1351 _ _ _ _ TK1351_9 i (by omega)
    | 10, _ => exact fun i _ hlt => chkT_sound PK1351 _ _ _ _ TK1351_10 i (by omega)
    | 11, _ => exact fun i _ hlt => chkT_sound PK1351 _ _ _ _ TK1351_11 i (by omega)
    | 12, _ => exact fun i _ hlt => chkT_sound PK1351 _ _ _ _ TK1351_12 i (by omega)
    | 13, _ => exact fun i _ hlt => chkT_sound PK1351 _ _ _ _ TK1351_13 i (by omega)
    | 14, _ => exact fun i _ hlt => chkT_sound PK1351 _ _ _ _ TK1351_14 i (by omega)
    | 15, _ => exact fun i _ hlt => chkT_sound PK1351 _ _ _ _ TK1351_15 i (by omega)
    | 16, _ => exact fun i _ hlt => chkT_sound PK1351 _ _ _ _ TK1351_16 i (by omega)
    | 17, _ => exact fun i _ hlt => chkT_sound PK1351 _ _ _ _ TK1351_17 i (by omega)
    | 18, _ => exact fun i _ hlt => chkT_sound PK1351 _ _ _ _ TK1351_18 i (by omega)
    | 19, _ => exact fun i _ hlt => chkT_sound PK1351 _ _ _ _ TK1351_19 i (by omega)
    | 20, _ => exact fun i _ hlt => chkT_sound PK1351 _ _ _ _ TK1351_20 i (by omega)
    | 21, _ => exact fun i _ hlt => chkT_sound PK1351 _ _ _ _ TK1351_21 i (by omega)
    | 22, _ => exact fun i _ hlt => chkT_sound PK1351 _ _ _ _ TK1351_22 i (by omega)
    | 23, _ => exact fun i _ hlt => chkT_sound PK1351 _ _ _ _ TK1351_23 i (by omega)
    | 24, _ => exact fun i _ hlt => chkT_sound PK1351 _ _ _ _ TK1351_24 i (by omega)
    | 25, _ => exact fun i _ hlt => chkT_sound PK1351 _ _ _ _ TK1351_25 i (by omega)
    | 26, _ => exact fun i _ hlt => chkT_sound PK1351 _ _ _ _ TK1351_26 i (by omega)
    | 27, _ => exact fun i _ hlt => chkT_sound PK1351 _ _ _ _ TK1351_27 i (by omega)
    | 28, _ => exact fun i _ hlt => chkT_sound PK1351 _ _ _ _ TK1351_28 i (by omega)
    | c + 29, h => exact absurd h (by omega))

theorem hOK1351 : ∀ i < PK1351.orphs.length, ∀ a < 343, ∃ j, okO PK1351 (PK1351.orphs.getD i 0) a j = true := by
  intro i hi
  match i, hi with
  | 0, _ => exact chkO_sound PK1351 _ _ _ _ OK1351_0
  | 1, _ => exact chkO_sound PK1351 _ _ _ _ OK1351_1
  | 2, _ => exact chkO_sound PK1351 _ _ _ _ OK1351_2
  | 3, _ => exact chkO_sound PK1351 _ _ _ _ OK1351_3
  | 4, _ => exact chkO_sound PK1351 _ _ _ _ OK1351_4
  | 5, _ => exact chkO_sound PK1351 _ _ _ _ OK1351_5
  | 6, _ => exact chkO_sound PK1351 _ _ _ _ OK1351_6
  | 7, _ => exact chkO_sound PK1351 _ _ _ _ OK1351_7
  | 8, _ => exact chkO_sound PK1351 _ _ _ _ OK1351_8
  | 9, _ => exact chkO_sound PK1351 _ _ _ _ OK1351_9
  | 10, _ => exact chkO_sound PK1351 _ _ _ _ OK1351_10
  | 11, _ => exact chkO_sound PK1351 _ _ _ _ OK1351_11
  | 12, _ => exact chkO_sound PK1351 _ _ _ _ OK1351_12
  | 13, _ => exact chkO_sound PK1351 _ _ _ _ OK1351_13
  | 14, _ => exact chkO_sound PK1351 _ _ _ _ OK1351_14
  | 15, _ => exact chkO_sound PK1351 _ _ _ _ OK1351_15
  | 16, _ => exact chkO_sound PK1351 _ _ _ _ OK1351_16
  | 17, _ => exact chkO_sound PK1351 _ _ _ _ OK1351_17
  | 18, _ => exact chkO_sound PK1351 _ _ _ _ OK1351_18
  | 19, _ => exact chkO_sound PK1351 _ _ _ _ OK1351_19
  | 20, _ => exact chkO_sound PK1351 _ _ _ _ OK1351_20
  | 21, _ => exact chkO_sound PK1351 _ _ _ _ OK1351_21
  | 22, _ => exact chkO_sound PK1351 _ _ _ _ OK1351_22
  | 23, _ => exact chkO_sound PK1351 _ _ _ _ OK1351_23
  | 24, _ => exact chkO_sound PK1351 _ _ _ _ OK1351_24
  | 25, _ => exact chkO_sound PK1351 _ _ _ _ OK1351_25
  | 26, _ => exact chkO_sound PK1351 _ _ _ _ OK1351_26
  | i + 27, h => exact absurd h (by have : PK1351.orphs.length = 27 := rfl; omega)

theorem hBK1351 : ∀ s < PK1351.reps.length, ∀ m < 343, ∃ j, okB PK1351 s m j = true := by
  intro s hs
  match s, hs with
  | 0, _ => exact chkB_sound PK1351 _ _ _ _ BK1351_0
  | 1, _ => exact chkB_sound PK1351 _ _ _ _ BK1351_1
  | 2, _ => exact chkB_sound PK1351 _ _ _ _ BK1351_2
  | s + 3, h => exact absurd h (by have : PK1351.reps.length = 3 := rfl; omega)

/-- Não-vacuidade: o verificador recusa uma testemunha errada (ponto `t = 0`, palavra
`57` a distância 9 > 4). -/
example : okT PK1351 0 57 = false := by decide +kernel

/-- `K_7(9,4) ≤ 1351`: o código `LK1351` tem 1351 palavras e cobre com raio 4. -/
theorem K7_9_4_le_1351_syn :
    ∃ C : Finset (Fin 9 → ZMod 7), C.card = 1351 ∧ CoveringA2.Covers 4 C :=
  syn_cert PK1351 LK1351 rfl rfl rfl ⟨rfl, by decide⟩ VK1351 hTK1351 hOK1351 hBK1351
    (by decide +kernel) (by decide +kernel) (by decide +kernel)

end Syn

#print axioms Syn.K7_9_4_le_1351_syn
