-- gerado por scripts/syndrome/gen_syn.py; não editar à mão
import CoveringLean.SynBridge
import CoveringLean.SynLeaf_K2_23_4_2048_0

/-! # K_2(23,4) ≤ 2048 pelo certificado por síndromes

Código: `Syn.LK2_23_4_2048` (sha256 canônico 6286a852e24e8aac999d9c10b8bfc0cf6bfa7eb418efbaa59209f3ae722df3cf), união de 1 cosets completos de um
`[23,11]_2` (bloco de informação [0,11)) com 0 palavras de remendo;
0 síndromes órfãs (0 pontos checados um a um).
-/

namespace Syn

set_option maxRecDepth 100000

theorem hTK2_23_4_2048 : ∀ t < 4096, ∃ w, okT PK2_23_4_2048 t w = true :=
  all_of_chunks (fun t => ∃ w, okT PK2_23_4_2048 t w = true) 4096 1 4096 (by norm_num) (by
    intro c hc
    match c, hc with
    | 0, _ => exact fun i _ hlt => chkT_sound PK2_23_4_2048 _ _ _ _ TK2_23_4_2048_0 i (by omega)
    | c + 1, h => exact absurd h (by omega))

theorem hOK2_23_4_2048 : ∀ i < PK2_23_4_2048.orphs.length, ∀ a < 2048, ∃ j, okO PK2_23_4_2048 (PK2_23_4_2048.orphs.getD i 0) a j = true := by
  intro i hi
  match i, hi with
  | i + 0, h => exact absurd h (by have : PK2_23_4_2048.orphs.length = 0 := rfl; omega)

theorem hBK2_23_4_2048 : ∀ s < PK2_23_4_2048.reps.length, ∀ m < 2048, ∃ j, okB PK2_23_4_2048 s m j = true := by
  intro s hs
  match s, hs with
  | 0, _ => exact chkB_sound PK2_23_4_2048 _ _ _ _ BK2_23_4_2048_0
  | s + 1, h => exact absurd h (by have : PK2_23_4_2048.reps.length = 1 := rfl; omega)

/-- Não-vacuidade: o verificador recusa uma testemunha errada (ponto `t = 0`, palavra
`2031` a distância 20 > 4). -/
example : okT PK2_23_4_2048 0 2031 = false := by decide +kernel

/-- `K_2(23,4) ≤ 2048`: o código `LK2_23_4_2048` tem 2048 palavras e cobre com raio 4. -/
theorem K2_23_4_le_2048_syn :
    ∃ C : Finset (Fin 23 → ZMod 2), C.card = 2048 ∧ CoveringA2.Covers 4 C :=
  syn_cert PK2_23_4_2048 LK2_23_4_2048 rfl rfl rfl ⟨rfl, by decide⟩ VK2_23_4_2048 hTK2_23_4_2048 hOK2_23_4_2048 hBK2_23_4_2048
    (by decide +kernel) (by decide +kernel) (by decide +kernel)

end Syn

#print axioms Syn.K2_23_4_le_2048_syn
