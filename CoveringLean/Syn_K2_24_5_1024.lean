-- gerado por scripts/syndrome/gen_syn.py; não editar à mão
import CoveringLean.SynBridge
import CoveringLean.SynLeaf_K2_24_5_1024_0
import CoveringLean.SynLeaf_K2_24_5_1024_1

/-! # K_2(24,5) ≤ 1024 pelo certificado por síndromes

Código: `Syn.LK2_24_5_1024` (sha256 canônico 1640b5f9d9d78a3b2a542b9923871199feba90a768298620a87bba9194c3d24e), união de 1 cosets completos de um
`[24,10]_2` (bloco de informação [10,20)) com 0 palavras de remendo;
0 síndromes órfãs (0 pontos checados um a um).
-/

namespace Syn

set_option maxRecDepth 100000

theorem hTK2_24_5_1024 : ∀ t < 16384, ∃ w, okT PK2_24_5_1024 t w = true :=
  all_of_chunks (fun t => ∃ w, okT PK2_24_5_1024 t w = true) 4096 4 16384 (by norm_num) (by
    intro c hc
    match c, hc with
    | 0, _ => exact fun i _ hlt => chkT_sound PK2_24_5_1024 _ _ _ _ TK2_24_5_1024_0 i (by omega)
    | 1, _ => exact fun i _ hlt => chkT_sound PK2_24_5_1024 _ _ _ _ TK2_24_5_1024_1 i (by omega)
    | 2, _ => exact fun i _ hlt => chkT_sound PK2_24_5_1024 _ _ _ _ TK2_24_5_1024_2 i (by omega)
    | 3, _ => exact fun i _ hlt => chkT_sound PK2_24_5_1024 _ _ _ _ TK2_24_5_1024_3 i (by omega)
    | c + 4, h => exact absurd h (by omega))

theorem hOK2_24_5_1024 : ∀ i < PK2_24_5_1024.orphs.length, ∀ a < 1024, ∃ j, okO PK2_24_5_1024 (PK2_24_5_1024.orphs.getD i 0) a j = true := by
  intro i hi
  match i, hi with
  | i + 0, h => exact absurd h (by have : PK2_24_5_1024.orphs.length = 0 := rfl; omega)

theorem hBK2_24_5_1024 : ∀ s < PK2_24_5_1024.reps.length, ∀ m < 1024, ∃ j, okB PK2_24_5_1024 s m j = true := by
  intro s hs
  match s, hs with
  | 0, _ => exact chkB_sound PK2_24_5_1024 _ _ _ _ BK2_24_5_1024_0
  | s + 1, h => exact absurd h (by have : PK2_24_5_1024.reps.length = 1 := rfl; omega)

/-- Não-vacuidade: o verificador recusa uma testemunha errada (ponto `t = 0`, palavra
`895` a distância 23 > 5). -/
example : okT PK2_24_5_1024 0 895 = false := by decide +kernel

/-- `K_2(24,5) ≤ 1024`: o código `LK2_24_5_1024` tem 1024 palavras e cobre com raio 5. -/
theorem K2_24_5_le_1024_syn :
    ∃ C : Finset (Fin 24 → ZMod 2), C.card = 1024 ∧ CoveringA2.Covers 5 C :=
  syn_cert PK2_24_5_1024 LK2_24_5_1024 rfl rfl rfl ⟨rfl, by decide⟩ VK2_24_5_1024 hTK2_24_5_1024 hOK2_24_5_1024 hBK2_24_5_1024
    (by decide +kernel) (by decide +kernel) (by decide +kernel)

end Syn

#print axioms Syn.K2_24_5_le_1024_syn
