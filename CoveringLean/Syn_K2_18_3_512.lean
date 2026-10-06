-- gerado por scripts/syndrome/gen_syn.py; não editar à mão
import CoveringLean.SynBridge
import CoveringLean.SynLeaf_K2_18_3_512_0

/-! # K_2(18,3) ≤ 512 pelo certificado por síndromes

Código: `Syn.LK2_18_3_512` (sha256 canônico 604e3f670290cf2c7f3fa02a1321374554c5df163ccde15021eca2ac6bb093c5), união de 1 cosets completos de um
`[18,9]_2` (bloco de informação [8,17)) com 0 palavras de remendo;
0 síndromes órfãs (0 pontos checados um a um).
-/

namespace Syn

set_option maxRecDepth 100000

theorem hTK2_18_3_512 : ∀ t < 512, ∃ w, okT PK2_18_3_512 t w = true :=
  all_of_chunks (fun t => ∃ w, okT PK2_18_3_512 t w = true) 4096 1 512 (by norm_num) (by
    intro c hc
    match c, hc with
    | 0, _ => exact fun i _ hlt => chkT_sound PK2_18_3_512 _ _ _ _ TK2_18_3_512_0 i (by omega)
    | c + 1, h => exact absurd h (by omega))

theorem hOK2_18_3_512 : ∀ i < PK2_18_3_512.orphs.length, ∀ a < 512, ∃ j, okO PK2_18_3_512 (PK2_18_3_512.orphs.getD i 0) a j = true := by
  intro i hi
  match i, hi with
  | i + 0, h => exact absurd h (by have : PK2_18_3_512.orphs.length = 0 := rfl; omega)

theorem hBK2_18_3_512 : ∀ s < PK2_18_3_512.reps.length, ∀ m < 512, ∃ j, okB PK2_18_3_512 s m j = true := by
  intro s hs
  match s, hs with
  | 0, _ => exact chkB_sound PK2_18_3_512 _ _ _ _ BK2_18_3_512_0
  | s + 1, h => exact absurd h (by have : PK2_18_3_512.reps.length = 1 := rfl; omega)

/-- Não-vacuidade: o verificador recusa uma testemunha errada (ponto `t = 0`, palavra
`511` a distância 16 > 3). -/
example : okT PK2_18_3_512 0 511 = false := by decide +kernel

/-- `K_2(18,3) ≤ 512`: o código `LK2_18_3_512` tem 512 palavras e cobre com raio 3. -/
theorem K2_18_3_le_512_syn :
    ∃ C : Finset (Fin 18 → ZMod 2), C.card = 512 ∧ CoveringA2.Covers 3 C :=
  syn_cert PK2_18_3_512 LK2_18_3_512 rfl rfl rfl ⟨rfl, by decide⟩ VK2_18_3_512 hTK2_18_3_512 hOK2_18_3_512 hBK2_18_3_512
    (by decide +kernel) (by decide +kernel) (by decide +kernel)

end Syn

#print axioms Syn.K2_18_3_le_512_syn
