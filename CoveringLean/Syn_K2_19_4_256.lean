-- gerado por scripts/syndrome/gen_syn.py; não editar à mão
import CoveringLean.SynBridge
import CoveringLean.SynLeaf_K2_19_4_256_0

/-! # K_2(19,4) ≤ 256 pelo certificado por síndromes

Código: `Syn.LK2_19_4_256` (sha256 canônico 4c8464f205928c4b63f4bb494939f4324820c92e96bfea992caf91f574c39cc8), união de 1 cosets completos de um
`[19,8]_2` (bloco de informação [0,8)) com 0 palavras de remendo;
0 síndromes órfãs (0 pontos checados um a um).
-/

namespace Syn

set_option maxRecDepth 100000

theorem hTK2_19_4_256 : ∀ t < 2048, ∃ w, okT PK2_19_4_256 t w = true :=
  all_of_chunks (fun t => ∃ w, okT PK2_19_4_256 t w = true) 4096 1 2048 (by norm_num) (by
    intro c hc
    match c, hc with
    | 0, _ => exact fun i _ hlt => chkT_sound PK2_19_4_256 _ _ _ _ TK2_19_4_256_0 i (by omega)
    | c + 1, h => exact absurd h (by omega))

theorem hOK2_19_4_256 : ∀ i < PK2_19_4_256.orphs.length, ∀ a < 256, ∃ j, okO PK2_19_4_256 (PK2_19_4_256.orphs.getD i 0) a j = true := by
  intro i hi
  match i, hi with
  | i + 0, h => exact absurd h (by have : PK2_19_4_256.orphs.length = 0 := rfl; omega)

theorem hBK2_19_4_256 : ∀ s < PK2_19_4_256.reps.length, ∀ m < 256, ∃ j, okB PK2_19_4_256 s m j = true := by
  intro s hs
  match s, hs with
  | 0, _ => exact chkB_sound PK2_19_4_256 _ _ _ _ BK2_19_4_256_0
  | s + 1, h => exact absurd h (by have : PK2_19_4_256.reps.length = 1 := rfl; omega)

/-- Não-vacuidade: o verificador recusa uma testemunha errada (ponto `t = 0`, palavra
`183` a distância 17 > 4). -/
example : okT PK2_19_4_256 0 183 = false := by decide +kernel

/-- `K_2(19,4) ≤ 256`: o código `LK2_19_4_256` tem 256 palavras e cobre com raio 4. -/
theorem K2_19_4_le_256_syn :
    ∃ C : Finset (Fin 19 → ZMod 2), C.card = 256 ∧ CoveringA2.Covers 4 C :=
  syn_cert PK2_19_4_256 LK2_19_4_256 rfl rfl rfl ⟨rfl, by decide⟩ VK2_19_4_256 hTK2_19_4_256 hOK2_19_4_256 hBK2_19_4_256
    (by decide +kernel) (by decide +kernel) (by decide +kernel)

end Syn

#print axioms Syn.K2_19_4_le_256_syn
