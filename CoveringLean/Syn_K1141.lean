-- gerado por scripts/syndrome/gen_syn.py; não editar à mão
import CoveringLean.SynBridge
import CoveringLean.SynLeaf_K1141_0
import CoveringLean.SynLeaf_K1141_1
import CoveringLean.SynLeaf_K1141_2
import CoveringLean.SynLeaf_K1141_3
import CoveringLean.SynLeaf_K1141_4
import CoveringLean.SynLeaf_K1141_5
import CoveringLean.SynLeaf_K1141_6
import CoveringLean.SynLeaf_K1141_7
import CoveringLean.SynLeaf_K1141_8
import CoveringLean.SynLeaf_K1141_9

/-! # K_7(9,4) ≤ 1141 pelo certificado por síndromes

Código: `Syn.LK1141` (sha256 canônico bcb05960410d3f32ccd0de46720606a6df3d0402cb56c67e93766f12e41f5259), união de 3 cosets completos de um
`[9,3]_7` (bloco de informação [0,3)) com 112 palavras de remendo;
6 síndromes órfãs (2058 pontos checados um a um).
-/

namespace Syn

set_option maxRecDepth 100000

theorem hTK1141 : ∀ t < 117649, ∃ w, okT PK1141 t w = true :=
  all_of_chunks (fun t => ∃ w, okT PK1141 t w = true) 4096 29 117649 (by norm_num) (by
    intro c hc
    match c, hc with
    | 0, _ => exact fun i _ hlt => chkT_sound PK1141 _ _ _ _ TK1141_0 i (by omega)
    | 1, _ => exact fun i _ hlt => chkT_sound PK1141 _ _ _ _ TK1141_1 i (by omega)
    | 2, _ => exact fun i _ hlt => chkT_sound PK1141 _ _ _ _ TK1141_2 i (by omega)
    | 3, _ => exact fun i _ hlt => chkT_sound PK1141 _ _ _ _ TK1141_3 i (by omega)
    | 4, _ => exact fun i _ hlt => chkT_sound PK1141 _ _ _ _ TK1141_4 i (by omega)
    | 5, _ => exact fun i _ hlt => chkT_sound PK1141 _ _ _ _ TK1141_5 i (by omega)
    | 6, _ => exact fun i _ hlt => chkT_sound PK1141 _ _ _ _ TK1141_6 i (by omega)
    | 7, _ => exact fun i _ hlt => chkT_sound PK1141 _ _ _ _ TK1141_7 i (by omega)
    | 8, _ => exact fun i _ hlt => chkT_sound PK1141 _ _ _ _ TK1141_8 i (by omega)
    | 9, _ => exact fun i _ hlt => chkT_sound PK1141 _ _ _ _ TK1141_9 i (by omega)
    | 10, _ => exact fun i _ hlt => chkT_sound PK1141 _ _ _ _ TK1141_10 i (by omega)
    | 11, _ => exact fun i _ hlt => chkT_sound PK1141 _ _ _ _ TK1141_11 i (by omega)
    | 12, _ => exact fun i _ hlt => chkT_sound PK1141 _ _ _ _ TK1141_12 i (by omega)
    | 13, _ => exact fun i _ hlt => chkT_sound PK1141 _ _ _ _ TK1141_13 i (by omega)
    | 14, _ => exact fun i _ hlt => chkT_sound PK1141 _ _ _ _ TK1141_14 i (by omega)
    | 15, _ => exact fun i _ hlt => chkT_sound PK1141 _ _ _ _ TK1141_15 i (by omega)
    | 16, _ => exact fun i _ hlt => chkT_sound PK1141 _ _ _ _ TK1141_16 i (by omega)
    | 17, _ => exact fun i _ hlt => chkT_sound PK1141 _ _ _ _ TK1141_17 i (by omega)
    | 18, _ => exact fun i _ hlt => chkT_sound PK1141 _ _ _ _ TK1141_18 i (by omega)
    | 19, _ => exact fun i _ hlt => chkT_sound PK1141 _ _ _ _ TK1141_19 i (by omega)
    | 20, _ => exact fun i _ hlt => chkT_sound PK1141 _ _ _ _ TK1141_20 i (by omega)
    | 21, _ => exact fun i _ hlt => chkT_sound PK1141 _ _ _ _ TK1141_21 i (by omega)
    | 22, _ => exact fun i _ hlt => chkT_sound PK1141 _ _ _ _ TK1141_22 i (by omega)
    | 23, _ => exact fun i _ hlt => chkT_sound PK1141 _ _ _ _ TK1141_23 i (by omega)
    | 24, _ => exact fun i _ hlt => chkT_sound PK1141 _ _ _ _ TK1141_24 i (by omega)
    | 25, _ => exact fun i _ hlt => chkT_sound PK1141 _ _ _ _ TK1141_25 i (by omega)
    | 26, _ => exact fun i _ hlt => chkT_sound PK1141 _ _ _ _ TK1141_26 i (by omega)
    | 27, _ => exact fun i _ hlt => chkT_sound PK1141 _ _ _ _ TK1141_27 i (by omega)
    | 28, _ => exact fun i _ hlt => chkT_sound PK1141 _ _ _ _ TK1141_28 i (by omega)
    | c + 29, h => exact absurd h (by omega))

theorem hOK1141 : ∀ i < PK1141.orphs.length, ∀ a < 343, ∃ j, okO PK1141 (PK1141.orphs.getD i 0) a j = true := by
  intro i hi
  match i, hi with
  | 0, _ => exact chkO_sound PK1141 _ _ _ _ OK1141_0
  | 1, _ => exact chkO_sound PK1141 _ _ _ _ OK1141_1
  | 2, _ => exact chkO_sound PK1141 _ _ _ _ OK1141_2
  | 3, _ => exact chkO_sound PK1141 _ _ _ _ OK1141_3
  | 4, _ => exact chkO_sound PK1141 _ _ _ _ OK1141_4
  | 5, _ => exact chkO_sound PK1141 _ _ _ _ OK1141_5
  | i + 6, h => exact absurd h (by have : PK1141.orphs.length = 6 := rfl; omega)

theorem hBK1141 : ∀ s < PK1141.reps.length, ∀ m < 343, ∃ j, okB PK1141 s m j = true := by
  intro s hs
  match s, hs with
  | 0, _ => exact chkB_sound PK1141 _ _ _ _ BK1141_0
  | 1, _ => exact chkB_sound PK1141 _ _ _ _ BK1141_1
  | 2, _ => exact chkB_sound PK1141 _ _ _ _ BK1141_2
  | s + 3, h => exact absurd h (by have : PK1141.reps.length = 3 := rfl; omega)

/-- Não-vacuidade: o verificador recusa uma testemunha errada (ponto `t = 0`, palavra
`59` a distância 9 > 4). -/
example : okT PK1141 0 59 = false := by decide +kernel

/-- `K_7(9,4) ≤ 1141`: o código `LK1141` tem 1141 palavras e cobre com raio 4. -/
theorem K7_9_4_le_1141_syn :
    ∃ C : Finset (Fin 9 → ZMod 7), C.card = 1141 ∧ CoveringA2.Covers 4 C :=
  syn_cert PK1141 LK1141 rfl rfl rfl ⟨rfl, by decide⟩ VK1141 hTK1141 hOK1141 hBK1141
    (by decide +kernel) (by decide +kernel) (by decide +kernel)

end Syn

#print axioms Syn.K7_9_4_le_1141_syn
