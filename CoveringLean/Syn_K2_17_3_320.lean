-- gerado por scripts/syndrome/gen_syn.py; não editar à mão
import CoveringLean.SynBridge
import CoveringLean.SynLeaf_K2_17_3_320_0
import CoveringLean.SynLeaf_K2_17_3_320_1

/-! # K_2(17,3) ≤ 320 pelo certificado por síndromes

Código: `Syn.LK2_17_3_320` (sha256 canônico 400fef9e67d92cdfeef54940e246c049c323810cf57d79512844393b053656d5), união de 5 cosets completos de um
`[17,6]_2` (bloco de informação [0,6)) com 0 palavras de remendo;
0 síndromes órfãs (0 pontos checados um a um).
-/

namespace Syn

set_option maxRecDepth 100000

theorem hTK2_17_3_320 : ∀ t < 2048, ∃ w, okT PK2_17_3_320 t w = true :=
  all_of_chunks (fun t => ∃ w, okT PK2_17_3_320 t w = true) 4096 1 2048 (by norm_num) (by
    intro c hc
    match c, hc with
    | 0, _ => exact fun i _ hlt => chkT_sound PK2_17_3_320 _ _ _ _ TK2_17_3_320_0 i (by omega)
    | c + 1, h => exact absurd h (by omega))

theorem hOK2_17_3_320 : ∀ i < PK2_17_3_320.orphs.length, ∀ a < 64, ∃ j, okO PK2_17_3_320 (PK2_17_3_320.orphs.getD i 0) a j = true := by
  intro i hi
  match i, hi with
  | i + 0, h => exact absurd h (by have : PK2_17_3_320.orphs.length = 0 := rfl; omega)

theorem hBK2_17_3_320 : ∀ s < PK2_17_3_320.reps.length, ∀ m < 64, ∃ j, okB PK2_17_3_320 s m j = true := by
  intro s hs
  match s, hs with
  | 0, _ => exact chkB_sound PK2_17_3_320 _ _ _ _ BK2_17_3_320_0
  | 1, _ => exact chkB_sound PK2_17_3_320 _ _ _ _ BK2_17_3_320_1
  | 2, _ => exact chkB_sound PK2_17_3_320 _ _ _ _ BK2_17_3_320_2
  | 3, _ => exact chkB_sound PK2_17_3_320 _ _ _ _ BK2_17_3_320_3
  | 4, _ => exact chkB_sound PK2_17_3_320 _ _ _ _ BK2_17_3_320_4
  | s + 5, h => exact absurd h (by have : PK2_17_3_320.reps.length = 5 := rfl; omega)

/-- Não-vacuidade: o verificador recusa uma testemunha errada (ponto `t = 0`, palavra
`255` a distância 16 > 3). -/
example : okT PK2_17_3_320 0 255 = false := by decide +kernel

/-- `K_2(17,3) ≤ 320`: o código `LK2_17_3_320` tem 320 palavras e cobre com raio 3. -/
theorem K2_17_3_le_320_syn :
    ∃ C : Finset (Fin 17 → ZMod 2), C.card = 320 ∧ CoveringA2.Covers 3 C :=
  syn_cert PK2_17_3_320 LK2_17_3_320 rfl rfl rfl ⟨rfl, by decide⟩ VK2_17_3_320 hTK2_17_3_320 hOK2_17_3_320 hBK2_17_3_320
    (by decide +kernel) (by decide +kernel) (by decide +kernel)

end Syn

#print axioms Syn.K2_17_3_le_320_syn
