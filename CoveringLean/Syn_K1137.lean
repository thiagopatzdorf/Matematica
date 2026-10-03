-- gerado por scripts/syndrome/gen_syn.py; não editar à mão
import CoveringLean.SynBridge
import CoveringLean.SynLeaf_K1137_0
import CoveringLean.SynLeaf_K1137_1
import CoveringLean.SynLeaf_K1137_2
import CoveringLean.SynLeaf_K1137_3
import CoveringLean.SynLeaf_K1137_4
import CoveringLean.SynLeaf_K1137_5
import CoveringLean.SynLeaf_K1137_6
import CoveringLean.SynLeaf_K1137_7
import CoveringLean.SynLeaf_K1137_8
import CoveringLean.SynLeaf_K1137_9

/-! # K_7(9,4) ≤ 1137 pelo certificado por síndromes

Código: `Syn.LK1137` (sha256 canônico df3e8d527bc393a9680fe4b2b39e7bde088ab6a02f2f94ee26019a5efc05a102), união de 3 cosets completos de um
`[9,3]_7` (bloco de informação [0,3)) com 108 palavras de remendo;
6 síndromes órfãs (2058 pontos checados um a um).
-/

namespace Syn

set_option maxRecDepth 100000

theorem hTK1137 : ∀ t < 117649, ∃ w, okT PK1137 t w = true :=
  all_of_chunks (fun t => ∃ w, okT PK1137 t w = true) 4096 29 117649 (by norm_num) (by
    intro c hc
    match c, hc with
    | 0, _ => exact fun i _ hlt => chkT_sound PK1137 _ _ _ _ TK1137_0 i (by omega)
    | 1, _ => exact fun i _ hlt => chkT_sound PK1137 _ _ _ _ TK1137_1 i (by omega)
    | 2, _ => exact fun i _ hlt => chkT_sound PK1137 _ _ _ _ TK1137_2 i (by omega)
    | 3, _ => exact fun i _ hlt => chkT_sound PK1137 _ _ _ _ TK1137_3 i (by omega)
    | 4, _ => exact fun i _ hlt => chkT_sound PK1137 _ _ _ _ TK1137_4 i (by omega)
    | 5, _ => exact fun i _ hlt => chkT_sound PK1137 _ _ _ _ TK1137_5 i (by omega)
    | 6, _ => exact fun i _ hlt => chkT_sound PK1137 _ _ _ _ TK1137_6 i (by omega)
    | 7, _ => exact fun i _ hlt => chkT_sound PK1137 _ _ _ _ TK1137_7 i (by omega)
    | 8, _ => exact fun i _ hlt => chkT_sound PK1137 _ _ _ _ TK1137_8 i (by omega)
    | 9, _ => exact fun i _ hlt => chkT_sound PK1137 _ _ _ _ TK1137_9 i (by omega)
    | 10, _ => exact fun i _ hlt => chkT_sound PK1137 _ _ _ _ TK1137_10 i (by omega)
    | 11, _ => exact fun i _ hlt => chkT_sound PK1137 _ _ _ _ TK1137_11 i (by omega)
    | 12, _ => exact fun i _ hlt => chkT_sound PK1137 _ _ _ _ TK1137_12 i (by omega)
    | 13, _ => exact fun i _ hlt => chkT_sound PK1137 _ _ _ _ TK1137_13 i (by omega)
    | 14, _ => exact fun i _ hlt => chkT_sound PK1137 _ _ _ _ TK1137_14 i (by omega)
    | 15, _ => exact fun i _ hlt => chkT_sound PK1137 _ _ _ _ TK1137_15 i (by omega)
    | 16, _ => exact fun i _ hlt => chkT_sound PK1137 _ _ _ _ TK1137_16 i (by omega)
    | 17, _ => exact fun i _ hlt => chkT_sound PK1137 _ _ _ _ TK1137_17 i (by omega)
    | 18, _ => exact fun i _ hlt => chkT_sound PK1137 _ _ _ _ TK1137_18 i (by omega)
    | 19, _ => exact fun i _ hlt => chkT_sound PK1137 _ _ _ _ TK1137_19 i (by omega)
    | 20, _ => exact fun i _ hlt => chkT_sound PK1137 _ _ _ _ TK1137_20 i (by omega)
    | 21, _ => exact fun i _ hlt => chkT_sound PK1137 _ _ _ _ TK1137_21 i (by omega)
    | 22, _ => exact fun i _ hlt => chkT_sound PK1137 _ _ _ _ TK1137_22 i (by omega)
    | 23, _ => exact fun i _ hlt => chkT_sound PK1137 _ _ _ _ TK1137_23 i (by omega)
    | 24, _ => exact fun i _ hlt => chkT_sound PK1137 _ _ _ _ TK1137_24 i (by omega)
    | 25, _ => exact fun i _ hlt => chkT_sound PK1137 _ _ _ _ TK1137_25 i (by omega)
    | 26, _ => exact fun i _ hlt => chkT_sound PK1137 _ _ _ _ TK1137_26 i (by omega)
    | 27, _ => exact fun i _ hlt => chkT_sound PK1137 _ _ _ _ TK1137_27 i (by omega)
    | 28, _ => exact fun i _ hlt => chkT_sound PK1137 _ _ _ _ TK1137_28 i (by omega)
    | c + 29, h => exact absurd h (by omega))

theorem hOK1137 : ∀ i < PK1137.orphs.length, ∀ a < 343, ∃ j, okO PK1137 (PK1137.orphs.getD i 0) a j = true := by
  intro i hi
  match i, hi with
  | 0, _ => exact chkO_sound PK1137 _ _ _ _ OK1137_0
  | 1, _ => exact chkO_sound PK1137 _ _ _ _ OK1137_1
  | 2, _ => exact chkO_sound PK1137 _ _ _ _ OK1137_2
  | 3, _ => exact chkO_sound PK1137 _ _ _ _ OK1137_3
  | 4, _ => exact chkO_sound PK1137 _ _ _ _ OK1137_4
  | 5, _ => exact chkO_sound PK1137 _ _ _ _ OK1137_5
  | i + 6, h => exact absurd h (by have : PK1137.orphs.length = 6 := rfl; omega)

theorem hBK1137 : ∀ s < PK1137.reps.length, ∀ m < 343, ∃ j, okB PK1137 s m j = true := by
  intro s hs
  match s, hs with
  | 0, _ => exact chkB_sound PK1137 _ _ _ _ BK1137_0
  | 1, _ => exact chkB_sound PK1137 _ _ _ _ BK1137_1
  | 2, _ => exact chkB_sound PK1137 _ _ _ _ BK1137_2
  | s + 3, h => exact absurd h (by have : PK1137.reps.length = 3 := rfl; omega)

/-- Não-vacuidade: o verificador recusa uma testemunha errada (ponto `t = 0`, palavra
`59` a distância 9 > 4). -/
example : okT PK1137 0 59 = false := by decide +kernel

/-- `K_7(9,4) ≤ 1137`: o código `LK1137` tem 1137 palavras e cobre com raio 4. -/
theorem K7_9_4_le_1137_syn :
    ∃ C : Finset (Fin 9 → ZMod 7), C.card = 1137 ∧ CoveringA2.Covers 4 C :=
  syn_cert PK1137 LK1137 rfl rfl rfl ⟨rfl, by decide⟩ VK1137 hTK1137 hOK1137 hBK1137
    (by decide +kernel) (by decide +kernel) (by decide +kernel)

end Syn

#print axioms Syn.K7_9_4_le_1137_syn
