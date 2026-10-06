-- gerado por scripts/syndrome/gen_syn.py; não editar à mão
import CoveringLean.SynBridge
import CoveringLean.SynLeaf_K2_17_5_32_0
import CoveringLean.SynLeaf_K2_17_5_32_1
import CoveringLean.SynLeaf_K2_17_5_32_2
import CoveringLean.SynLeaf_K2_17_5_32_3
import CoveringLean.SynLeaf_K2_17_5_32_4

/-! # K_2(17,5) ≤ 32 pelo certificado por síndromes

Código: `Syn.LK2_17_5_32` (sha256 canônico 3846acf19c6f319254936c157743657d4d83e828cbc1e5ee0c278a29f58ad4c3), união de 8 cosets completos de um
`[17,2]_2` (bloco de informação [7,9)) com 0 palavras de remendo;
0 síndromes órfãs (0 pontos checados um a um).
-/

namespace Syn

set_option maxRecDepth 100000

theorem hTK2_17_5_32 : ∀ t < 32768, ∃ w, okT PK2_17_5_32 t w = true :=
  all_of_chunks (fun t => ∃ w, okT PK2_17_5_32 t w = true) 4096 8 32768 (by norm_num) (by
    intro c hc
    match c, hc with
    | 0, _ => exact fun i _ hlt => chkT_sound PK2_17_5_32 _ _ _ _ TK2_17_5_32_0 i (by omega)
    | 1, _ => exact fun i _ hlt => chkT_sound PK2_17_5_32 _ _ _ _ TK2_17_5_32_1 i (by omega)
    | 2, _ => exact fun i _ hlt => chkT_sound PK2_17_5_32 _ _ _ _ TK2_17_5_32_2 i (by omega)
    | 3, _ => exact fun i _ hlt => chkT_sound PK2_17_5_32 _ _ _ _ TK2_17_5_32_3 i (by omega)
    | 4, _ => exact fun i _ hlt => chkT_sound PK2_17_5_32 _ _ _ _ TK2_17_5_32_4 i (by omega)
    | 5, _ => exact fun i _ hlt => chkT_sound PK2_17_5_32 _ _ _ _ TK2_17_5_32_5 i (by omega)
    | 6, _ => exact fun i _ hlt => chkT_sound PK2_17_5_32 _ _ _ _ TK2_17_5_32_6 i (by omega)
    | 7, _ => exact fun i _ hlt => chkT_sound PK2_17_5_32 _ _ _ _ TK2_17_5_32_7 i (by omega)
    | c + 8, h => exact absurd h (by omega))

theorem hOK2_17_5_32 : ∀ i < PK2_17_5_32.orphs.length, ∀ a < 4, ∃ j, okO PK2_17_5_32 (PK2_17_5_32.orphs.getD i 0) a j = true := by
  intro i hi
  match i, hi with
  | i + 0, h => exact absurd h (by have : PK2_17_5_32.orphs.length = 0 := rfl; omega)

theorem hBK2_17_5_32 : ∀ s < PK2_17_5_32.reps.length, ∀ m < 4, ∃ j, okB PK2_17_5_32 s m j = true := by
  intro s hs
  match s, hs with
  | 0, _ => exact chkB_sound PK2_17_5_32 _ _ _ _ BK2_17_5_32_0
  | 1, _ => exact chkB_sound PK2_17_5_32 _ _ _ _ BK2_17_5_32_1
  | 2, _ => exact chkB_sound PK2_17_5_32 _ _ _ _ BK2_17_5_32_2
  | 3, _ => exact chkB_sound PK2_17_5_32 _ _ _ _ BK2_17_5_32_3
  | 4, _ => exact chkB_sound PK2_17_5_32 _ _ _ _ BK2_17_5_32_4
  | 5, _ => exact chkB_sound PK2_17_5_32 _ _ _ _ BK2_17_5_32_5
  | 6, _ => exact chkB_sound PK2_17_5_32 _ _ _ _ BK2_17_5_32_6
  | 7, _ => exact chkB_sound PK2_17_5_32 _ _ _ _ BK2_17_5_32_7
  | s + 8, h => exact absurd h (by have : PK2_17_5_32.reps.length = 8 := rfl; omega)

/-- Não-vacuidade: o verificador recusa uma testemunha errada (ponto `t = 0`, palavra
`3` a distância 17 > 5). -/
example : okT PK2_17_5_32 0 3 = false := by decide +kernel

/-- `K_2(17,5) ≤ 32`: o código `LK2_17_5_32` tem 32 palavras e cobre com raio 5. -/
theorem K2_17_5_le_32_syn :
    ∃ C : Finset (Fin 17 → ZMod 2), C.card = 32 ∧ CoveringA2.Covers 5 C :=
  syn_cert PK2_17_5_32 LK2_17_5_32 rfl rfl rfl ⟨rfl, by decide⟩ VK2_17_5_32 hTK2_17_5_32 hOK2_17_5_32 hBK2_17_5_32
    (by decide +kernel) (by decide +kernel) (by decide +kernel)

end Syn

#print axioms Syn.K2_17_5_le_32_syn
