-- gerado por scripts/syndrome/gen_syn.py; não editar à mão
import CoveringLean.SynBridge
import CoveringLean.SynLeaf_K1134_0
import CoveringLean.SynLeaf_K1134_1
import CoveringLean.SynLeaf_K1134_2
import CoveringLean.SynLeaf_K1134_3
import CoveringLean.SynLeaf_K1134_4
import CoveringLean.SynLeaf_K1134_5
import CoveringLean.SynLeaf_K1134_6
import CoveringLean.SynLeaf_K1134_7
import CoveringLean.SynLeaf_K1134_8
import CoveringLean.SynLeaf_K1134_9

/-! # K_7(9,4) ≤ 1134 pelo certificado por síndromes

Código: `Syn.LK1134` (sha256 canônico a48e3a42922616b3466a5fafbfaa0e4098a77f675841df3129ac96bbcb8b7b41), união de 3 cosets completos de um
`[9,3]_7` (bloco de informação [0,3)) com 105 palavras de remendo;
6 síndromes órfãs (2058 pontos checados um a um).
-/

namespace Syn

set_option maxRecDepth 100000

theorem hTK1134 : ∀ t < 117649, ∃ w, okT PK1134 t w = true :=
  all_of_chunks (fun t => ∃ w, okT PK1134 t w = true) 4096 29 117649 (by norm_num) (by
    intro c hc
    match c, hc with
    | 0, _ => exact fun i _ hlt => chkT_sound PK1134 _ _ _ _ TK1134_0 i (by omega)
    | 1, _ => exact fun i _ hlt => chkT_sound PK1134 _ _ _ _ TK1134_1 i (by omega)
    | 2, _ => exact fun i _ hlt => chkT_sound PK1134 _ _ _ _ TK1134_2 i (by omega)
    | 3, _ => exact fun i _ hlt => chkT_sound PK1134 _ _ _ _ TK1134_3 i (by omega)
    | 4, _ => exact fun i _ hlt => chkT_sound PK1134 _ _ _ _ TK1134_4 i (by omega)
    | 5, _ => exact fun i _ hlt => chkT_sound PK1134 _ _ _ _ TK1134_5 i (by omega)
    | 6, _ => exact fun i _ hlt => chkT_sound PK1134 _ _ _ _ TK1134_6 i (by omega)
    | 7, _ => exact fun i _ hlt => chkT_sound PK1134 _ _ _ _ TK1134_7 i (by omega)
    | 8, _ => exact fun i _ hlt => chkT_sound PK1134 _ _ _ _ TK1134_8 i (by omega)
    | 9, _ => exact fun i _ hlt => chkT_sound PK1134 _ _ _ _ TK1134_9 i (by omega)
    | 10, _ => exact fun i _ hlt => chkT_sound PK1134 _ _ _ _ TK1134_10 i (by omega)
    | 11, _ => exact fun i _ hlt => chkT_sound PK1134 _ _ _ _ TK1134_11 i (by omega)
    | 12, _ => exact fun i _ hlt => chkT_sound PK1134 _ _ _ _ TK1134_12 i (by omega)
    | 13, _ => exact fun i _ hlt => chkT_sound PK1134 _ _ _ _ TK1134_13 i (by omega)
    | 14, _ => exact fun i _ hlt => chkT_sound PK1134 _ _ _ _ TK1134_14 i (by omega)
    | 15, _ => exact fun i _ hlt => chkT_sound PK1134 _ _ _ _ TK1134_15 i (by omega)
    | 16, _ => exact fun i _ hlt => chkT_sound PK1134 _ _ _ _ TK1134_16 i (by omega)
    | 17, _ => exact fun i _ hlt => chkT_sound PK1134 _ _ _ _ TK1134_17 i (by omega)
    | 18, _ => exact fun i _ hlt => chkT_sound PK1134 _ _ _ _ TK1134_18 i (by omega)
    | 19, _ => exact fun i _ hlt => chkT_sound PK1134 _ _ _ _ TK1134_19 i (by omega)
    | 20, _ => exact fun i _ hlt => chkT_sound PK1134 _ _ _ _ TK1134_20 i (by omega)
    | 21, _ => exact fun i _ hlt => chkT_sound PK1134 _ _ _ _ TK1134_21 i (by omega)
    | 22, _ => exact fun i _ hlt => chkT_sound PK1134 _ _ _ _ TK1134_22 i (by omega)
    | 23, _ => exact fun i _ hlt => chkT_sound PK1134 _ _ _ _ TK1134_23 i (by omega)
    | 24, _ => exact fun i _ hlt => chkT_sound PK1134 _ _ _ _ TK1134_24 i (by omega)
    | 25, _ => exact fun i _ hlt => chkT_sound PK1134 _ _ _ _ TK1134_25 i (by omega)
    | 26, _ => exact fun i _ hlt => chkT_sound PK1134 _ _ _ _ TK1134_26 i (by omega)
    | 27, _ => exact fun i _ hlt => chkT_sound PK1134 _ _ _ _ TK1134_27 i (by omega)
    | 28, _ => exact fun i _ hlt => chkT_sound PK1134 _ _ _ _ TK1134_28 i (by omega)
    | c + 29, h => exact absurd h (by omega))

theorem hOK1134 : ∀ i < PK1134.orphs.length, ∀ a < 343, ∃ j, okO PK1134 (PK1134.orphs.getD i 0) a j = true := by
  intro i hi
  match i, hi with
  | 0, _ => exact chkO_sound PK1134 _ _ _ _ OK1134_0
  | 1, _ => exact chkO_sound PK1134 _ _ _ _ OK1134_1
  | 2, _ => exact chkO_sound PK1134 _ _ _ _ OK1134_2
  | 3, _ => exact chkO_sound PK1134 _ _ _ _ OK1134_3
  | 4, _ => exact chkO_sound PK1134 _ _ _ _ OK1134_4
  | 5, _ => exact chkO_sound PK1134 _ _ _ _ OK1134_5
  | i + 6, h => exact absurd h (by have : PK1134.orphs.length = 6 := rfl; omega)

theorem hBK1134 : ∀ s < PK1134.reps.length, ∀ m < 343, ∃ j, okB PK1134 s m j = true := by
  intro s hs
  match s, hs with
  | 0, _ => exact chkB_sound PK1134 _ _ _ _ BK1134_0
  | 1, _ => exact chkB_sound PK1134 _ _ _ _ BK1134_1
  | 2, _ => exact chkB_sound PK1134 _ _ _ _ BK1134_2
  | s + 3, h => exact absurd h (by have : PK1134.reps.length = 3 := rfl; omega)

/-- Não-vacuidade: o verificador recusa uma testemunha errada (ponto `t = 0`, palavra
`59` a distância 9 > 4). -/
example : okT PK1134 0 59 = false := by decide +kernel

/-- `K_7(9,4) ≤ 1134`: o código `LK1134` tem 1134 palavras e cobre com raio 4. -/
theorem K7_9_4_le_1134_syn :
    ∃ C : Finset (Fin 9 → ZMod 7), C.card = 1134 ∧ CoveringA2.Covers 4 C :=
  syn_cert PK1134 LK1134 rfl rfl rfl ⟨rfl, by decide⟩ VK1134 hTK1134 hOK1134 hBK1134
    (by decide +kernel) (by decide +kernel) (by decide +kernel)

end Syn

#print axioms Syn.K7_9_4_le_1134_syn
