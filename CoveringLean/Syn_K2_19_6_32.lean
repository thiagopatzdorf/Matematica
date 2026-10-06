-- gerado por scripts/syndrome/gen_syn.py; não editar à mão
import CoveringLean.SynBridge
import CoveringLean.SynLeaf_K2_19_6_32_0
import CoveringLean.SynLeaf_K2_19_6_32_1
import CoveringLean.SynLeaf_K2_19_6_32_2
import CoveringLean.SynLeaf_K2_19_6_32_3
import CoveringLean.SynLeaf_K2_19_6_32_4
import CoveringLean.SynLeaf_K2_19_6_32_5
import CoveringLean.SynLeaf_K2_19_6_32_6
import CoveringLean.SynLeaf_K2_19_6_32_7
import CoveringLean.SynLeaf_K2_19_6_32_8
import CoveringLean.SynLeaf_K2_19_6_32_9
import CoveringLean.SynLeaf_K2_19_6_32_10

/-! # K_2(19,6) ≤ 32 pelo certificado por síndromes

Código: `Syn.LK2_19_6_32` (sha256 canônico d466fc9751eb37cba1240b575fec2a4f1dc2af1fe02cd9f656214158cee249e1), união de 8 cosets completos de um
`[19,2]_2` (bloco de informação [7,9)) com 0 palavras de remendo;
0 síndromes órfãs (0 pontos checados um a um).
-/

namespace Syn

set_option maxRecDepth 100000

theorem hTK2_19_6_32 : ∀ t < 131072, ∃ w, okT PK2_19_6_32 t w = true :=
  all_of_chunks (fun t => ∃ w, okT PK2_19_6_32 t w = true) 4096 32 131072 (by norm_num) (by
    intro c hc
    match c, hc with
    | 0, _ => exact fun i _ hlt => chkT_sound PK2_19_6_32 _ _ _ _ TK2_19_6_32_0 i (by omega)
    | 1, _ => exact fun i _ hlt => chkT_sound PK2_19_6_32 _ _ _ _ TK2_19_6_32_1 i (by omega)
    | 2, _ => exact fun i _ hlt => chkT_sound PK2_19_6_32 _ _ _ _ TK2_19_6_32_2 i (by omega)
    | 3, _ => exact fun i _ hlt => chkT_sound PK2_19_6_32 _ _ _ _ TK2_19_6_32_3 i (by omega)
    | 4, _ => exact fun i _ hlt => chkT_sound PK2_19_6_32 _ _ _ _ TK2_19_6_32_4 i (by omega)
    | 5, _ => exact fun i _ hlt => chkT_sound PK2_19_6_32 _ _ _ _ TK2_19_6_32_5 i (by omega)
    | 6, _ => exact fun i _ hlt => chkT_sound PK2_19_6_32 _ _ _ _ TK2_19_6_32_6 i (by omega)
    | 7, _ => exact fun i _ hlt => chkT_sound PK2_19_6_32 _ _ _ _ TK2_19_6_32_7 i (by omega)
    | 8, _ => exact fun i _ hlt => chkT_sound PK2_19_6_32 _ _ _ _ TK2_19_6_32_8 i (by omega)
    | 9, _ => exact fun i _ hlt => chkT_sound PK2_19_6_32 _ _ _ _ TK2_19_6_32_9 i (by omega)
    | 10, _ => exact fun i _ hlt => chkT_sound PK2_19_6_32 _ _ _ _ TK2_19_6_32_10 i (by omega)
    | 11, _ => exact fun i _ hlt => chkT_sound PK2_19_6_32 _ _ _ _ TK2_19_6_32_11 i (by omega)
    | 12, _ => exact fun i _ hlt => chkT_sound PK2_19_6_32 _ _ _ _ TK2_19_6_32_12 i (by omega)
    | 13, _ => exact fun i _ hlt => chkT_sound PK2_19_6_32 _ _ _ _ TK2_19_6_32_13 i (by omega)
    | 14, _ => exact fun i _ hlt => chkT_sound PK2_19_6_32 _ _ _ _ TK2_19_6_32_14 i (by omega)
    | 15, _ => exact fun i _ hlt => chkT_sound PK2_19_6_32 _ _ _ _ TK2_19_6_32_15 i (by omega)
    | 16, _ => exact fun i _ hlt => chkT_sound PK2_19_6_32 _ _ _ _ TK2_19_6_32_16 i (by omega)
    | 17, _ => exact fun i _ hlt => chkT_sound PK2_19_6_32 _ _ _ _ TK2_19_6_32_17 i (by omega)
    | 18, _ => exact fun i _ hlt => chkT_sound PK2_19_6_32 _ _ _ _ TK2_19_6_32_18 i (by omega)
    | 19, _ => exact fun i _ hlt => chkT_sound PK2_19_6_32 _ _ _ _ TK2_19_6_32_19 i (by omega)
    | 20, _ => exact fun i _ hlt => chkT_sound PK2_19_6_32 _ _ _ _ TK2_19_6_32_20 i (by omega)
    | 21, _ => exact fun i _ hlt => chkT_sound PK2_19_6_32 _ _ _ _ TK2_19_6_32_21 i (by omega)
    | 22, _ => exact fun i _ hlt => chkT_sound PK2_19_6_32 _ _ _ _ TK2_19_6_32_22 i (by omega)
    | 23, _ => exact fun i _ hlt => chkT_sound PK2_19_6_32 _ _ _ _ TK2_19_6_32_23 i (by omega)
    | 24, _ => exact fun i _ hlt => chkT_sound PK2_19_6_32 _ _ _ _ TK2_19_6_32_24 i (by omega)
    | 25, _ => exact fun i _ hlt => chkT_sound PK2_19_6_32 _ _ _ _ TK2_19_6_32_25 i (by omega)
    | 26, _ => exact fun i _ hlt => chkT_sound PK2_19_6_32 _ _ _ _ TK2_19_6_32_26 i (by omega)
    | 27, _ => exact fun i _ hlt => chkT_sound PK2_19_6_32 _ _ _ _ TK2_19_6_32_27 i (by omega)
    | 28, _ => exact fun i _ hlt => chkT_sound PK2_19_6_32 _ _ _ _ TK2_19_6_32_28 i (by omega)
    | 29, _ => exact fun i _ hlt => chkT_sound PK2_19_6_32 _ _ _ _ TK2_19_6_32_29 i (by omega)
    | 30, _ => exact fun i _ hlt => chkT_sound PK2_19_6_32 _ _ _ _ TK2_19_6_32_30 i (by omega)
    | 31, _ => exact fun i _ hlt => chkT_sound PK2_19_6_32 _ _ _ _ TK2_19_6_32_31 i (by omega)
    | c + 32, h => exact absurd h (by omega))

theorem hOK2_19_6_32 : ∀ i < PK2_19_6_32.orphs.length, ∀ a < 4, ∃ j, okO PK2_19_6_32 (PK2_19_6_32.orphs.getD i 0) a j = true := by
  intro i hi
  match i, hi with
  | i + 0, h => exact absurd h (by have : PK2_19_6_32.orphs.length = 0 := rfl; omega)

theorem hBK2_19_6_32 : ∀ s < PK2_19_6_32.reps.length, ∀ m < 4, ∃ j, okB PK2_19_6_32 s m j = true := by
  intro s hs
  match s, hs with
  | 0, _ => exact chkB_sound PK2_19_6_32 _ _ _ _ BK2_19_6_32_0
  | 1, _ => exact chkB_sound PK2_19_6_32 _ _ _ _ BK2_19_6_32_1
  | 2, _ => exact chkB_sound PK2_19_6_32 _ _ _ _ BK2_19_6_32_2
  | 3, _ => exact chkB_sound PK2_19_6_32 _ _ _ _ BK2_19_6_32_3
  | 4, _ => exact chkB_sound PK2_19_6_32 _ _ _ _ BK2_19_6_32_4
  | 5, _ => exact chkB_sound PK2_19_6_32 _ _ _ _ BK2_19_6_32_5
  | 6, _ => exact chkB_sound PK2_19_6_32 _ _ _ _ BK2_19_6_32_6
  | 7, _ => exact chkB_sound PK2_19_6_32 _ _ _ _ BK2_19_6_32_7
  | s + 8, h => exact absurd h (by have : PK2_19_6_32.reps.length = 8 := rfl; omega)

/-- Não-vacuidade: o verificador recusa uma testemunha errada (ponto `t = 0`, palavra
`3` a distância 19 > 6). -/
example : okT PK2_19_6_32 0 3 = false := by decide +kernel

/-- `K_2(19,6) ≤ 32`: o código `LK2_19_6_32` tem 32 palavras e cobre com raio 6. -/
theorem K2_19_6_le_32_syn :
    ∃ C : Finset (Fin 19 → ZMod 2), C.card = 32 ∧ CoveringA2.Covers 6 C :=
  syn_cert PK2_19_6_32 LK2_19_6_32 rfl rfl rfl ⟨rfl, by decide⟩ VK2_19_6_32 hTK2_19_6_32 hOK2_19_6_32 hBK2_19_6_32
    (by decide +kernel) (by decide +kernel) (by decide +kernel)

end Syn

#print axioms Syn.K2_19_6_le_32_syn
