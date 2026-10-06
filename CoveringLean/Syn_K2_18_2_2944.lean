-- gerado por scripts/syndrome/gen_syn.py; não editar à mão
import CoveringLean.SynBridge
import CoveringLean.SynLeaf_K2_18_2_2944_0
import CoveringLean.SynLeaf_K2_18_2_2944_1
import CoveringLean.SynLeaf_K2_18_2_2944_2
import CoveringLean.SynLeaf_K2_18_2_2944_3
import CoveringLean.SynLeaf_K2_18_2_2944_4
import CoveringLean.SynLeaf_K2_18_2_2944_5
import CoveringLean.SynLeaf_K2_18_2_2944_6
import CoveringLean.SynLeaf_K2_18_2_2944_7
import CoveringLean.SynLeaf_K2_18_2_2944_8
import CoveringLean.SynLeaf_K2_18_2_2944_9
import CoveringLean.SynLeaf_K2_18_2_2944_10
import CoveringLean.SynLeaf_K2_18_2_2944_11

/-! # K_2(18,2) ≤ 2944 pelo certificado por síndromes

Código: `Syn.LK2_18_2_2944` (sha256 canônico bde9af6646dba5afe06ae1f2374b9423589bff6963a43433e20ccfa2dc3055ff), união de 46 cosets completos de um
`[18,6]_2` (bloco de informação [0,6)) com 0 palavras de remendo;
0 síndromes órfãs (0 pontos checados um a um).
-/

namespace Syn

set_option maxRecDepth 100000

theorem hTK2_18_2_2944 : ∀ t < 4096, ∃ w, okT PK2_18_2_2944 t w = true :=
  all_of_chunks (fun t => ∃ w, okT PK2_18_2_2944 t w = true) 4096 1 4096 (by norm_num) (by
    intro c hc
    match c, hc with
    | 0, _ => exact fun i _ hlt => chkT_sound PK2_18_2_2944 _ _ _ _ TK2_18_2_2944_0 i (by omega)
    | c + 1, h => exact absurd h (by omega))

theorem hOK2_18_2_2944 : ∀ i < PK2_18_2_2944.orphs.length, ∀ a < 64, ∃ j, okO PK2_18_2_2944 (PK2_18_2_2944.orphs.getD i 0) a j = true := by
  intro i hi
  match i, hi with
  | i + 0, h => exact absurd h (by have : PK2_18_2_2944.orphs.length = 0 := rfl; omega)

theorem hBK2_18_2_2944 : ∀ s < PK2_18_2_2944.reps.length, ∀ m < 64, ∃ j, okB PK2_18_2_2944 s m j = true := by
  intro s hs
  match s, hs with
  | 0, _ => exact chkB_sound PK2_18_2_2944 _ _ _ _ BK2_18_2_2944_0
  | 1, _ => exact chkB_sound PK2_18_2_2944 _ _ _ _ BK2_18_2_2944_1
  | 2, _ => exact chkB_sound PK2_18_2_2944 _ _ _ _ BK2_18_2_2944_2
  | 3, _ => exact chkB_sound PK2_18_2_2944 _ _ _ _ BK2_18_2_2944_3
  | 4, _ => exact chkB_sound PK2_18_2_2944 _ _ _ _ BK2_18_2_2944_4
  | 5, _ => exact chkB_sound PK2_18_2_2944 _ _ _ _ BK2_18_2_2944_5
  | 6, _ => exact chkB_sound PK2_18_2_2944 _ _ _ _ BK2_18_2_2944_6
  | 7, _ => exact chkB_sound PK2_18_2_2944 _ _ _ _ BK2_18_2_2944_7
  | 8, _ => exact chkB_sound PK2_18_2_2944 _ _ _ _ BK2_18_2_2944_8
  | 9, _ => exact chkB_sound PK2_18_2_2944 _ _ _ _ BK2_18_2_2944_9
  | 10, _ => exact chkB_sound PK2_18_2_2944 _ _ _ _ BK2_18_2_2944_10
  | 11, _ => exact chkB_sound PK2_18_2_2944 _ _ _ _ BK2_18_2_2944_11
  | 12, _ => exact chkB_sound PK2_18_2_2944 _ _ _ _ BK2_18_2_2944_12
  | 13, _ => exact chkB_sound PK2_18_2_2944 _ _ _ _ BK2_18_2_2944_13
  | 14, _ => exact chkB_sound PK2_18_2_2944 _ _ _ _ BK2_18_2_2944_14
  | 15, _ => exact chkB_sound PK2_18_2_2944 _ _ _ _ BK2_18_2_2944_15
  | 16, _ => exact chkB_sound PK2_18_2_2944 _ _ _ _ BK2_18_2_2944_16
  | 17, _ => exact chkB_sound PK2_18_2_2944 _ _ _ _ BK2_18_2_2944_17
  | 18, _ => exact chkB_sound PK2_18_2_2944 _ _ _ _ BK2_18_2_2944_18
  | 19, _ => exact chkB_sound PK2_18_2_2944 _ _ _ _ BK2_18_2_2944_19
  | 20, _ => exact chkB_sound PK2_18_2_2944 _ _ _ _ BK2_18_2_2944_20
  | 21, _ => exact chkB_sound PK2_18_2_2944 _ _ _ _ BK2_18_2_2944_21
  | 22, _ => exact chkB_sound PK2_18_2_2944 _ _ _ _ BK2_18_2_2944_22
  | 23, _ => exact chkB_sound PK2_18_2_2944 _ _ _ _ BK2_18_2_2944_23
  | 24, _ => exact chkB_sound PK2_18_2_2944 _ _ _ _ BK2_18_2_2944_24
  | 25, _ => exact chkB_sound PK2_18_2_2944 _ _ _ _ BK2_18_2_2944_25
  | 26, _ => exact chkB_sound PK2_18_2_2944 _ _ _ _ BK2_18_2_2944_26
  | 27, _ => exact chkB_sound PK2_18_2_2944 _ _ _ _ BK2_18_2_2944_27
  | 28, _ => exact chkB_sound PK2_18_2_2944 _ _ _ _ BK2_18_2_2944_28
  | 29, _ => exact chkB_sound PK2_18_2_2944 _ _ _ _ BK2_18_2_2944_29
  | 30, _ => exact chkB_sound PK2_18_2_2944 _ _ _ _ BK2_18_2_2944_30
  | 31, _ => exact chkB_sound PK2_18_2_2944 _ _ _ _ BK2_18_2_2944_31
  | 32, _ => exact chkB_sound PK2_18_2_2944 _ _ _ _ BK2_18_2_2944_32
  | 33, _ => exact chkB_sound PK2_18_2_2944 _ _ _ _ BK2_18_2_2944_33
  | 34, _ => exact chkB_sound PK2_18_2_2944 _ _ _ _ BK2_18_2_2944_34
  | 35, _ => exact chkB_sound PK2_18_2_2944 _ _ _ _ BK2_18_2_2944_35
  | 36, _ => exact chkB_sound PK2_18_2_2944 _ _ _ _ BK2_18_2_2944_36
  | 37, _ => exact chkB_sound PK2_18_2_2944 _ _ _ _ BK2_18_2_2944_37
  | 38, _ => exact chkB_sound PK2_18_2_2944 _ _ _ _ BK2_18_2_2944_38
  | 39, _ => exact chkB_sound PK2_18_2_2944 _ _ _ _ BK2_18_2_2944_39
  | 40, _ => exact chkB_sound PK2_18_2_2944 _ _ _ _ BK2_18_2_2944_40
  | 41, _ => exact chkB_sound PK2_18_2_2944 _ _ _ _ BK2_18_2_2944_41
  | 42, _ => exact chkB_sound PK2_18_2_2944 _ _ _ _ BK2_18_2_2944_42
  | 43, _ => exact chkB_sound PK2_18_2_2944 _ _ _ _ BK2_18_2_2944_43
  | 44, _ => exact chkB_sound PK2_18_2_2944 _ _ _ _ BK2_18_2_2944_44
  | 45, _ => exact chkB_sound PK2_18_2_2944 _ _ _ _ BK2_18_2_2944_45
  | s + 46, h => exact absurd h (by have : PK2_18_2_2944.reps.length = 46 := rfl; omega)

/-- Não-vacuidade: o verificador recusa uma testemunha errada (ponto `t = 0`, palavra
`63` a distância 16 > 2). -/
example : okT PK2_18_2_2944 0 63 = false := by decide +kernel

/-- `K_2(18,2) ≤ 2944`: o código `LK2_18_2_2944` tem 2944 palavras e cobre com raio 2. -/
theorem K2_18_2_le_2944_syn :
    ∃ C : Finset (Fin 18 → ZMod 2), C.card = 2944 ∧ CoveringA2.Covers 2 C :=
  syn_cert PK2_18_2_2944 LK2_18_2_2944 rfl rfl rfl ⟨rfl, by decide⟩ VK2_18_2_2944 hTK2_18_2_2944 hOK2_18_2_2944 hBK2_18_2_2944
    (by decide +kernel) (by decide +kernel) (by decide +kernel)

end Syn

#print axioms Syn.K2_18_2_le_2944_syn
