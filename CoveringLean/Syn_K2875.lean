-- gerado por scripts/syndrome/gen_syn.py; não editar à mão
import CoveringLean.SynBridge
import CoveringLean.SynLeaf_K2875_0
import CoveringLean.SynLeaf_K2875_1
import CoveringLean.SynLeaf_K2875_2
import CoveringLean.SynLeaf_K2875_3
import CoveringLean.SynLeaf_K2875_4
import CoveringLean.SynLeaf_K2875_5
import CoveringLean.SynLeaf_K2875_6
import CoveringLean.SynLeaf_K2875_7
import CoveringLean.SynLeaf_K2875_8
import CoveringLean.SynLeaf_K2875_9
import CoveringLean.SynLeaf_K2875_10
import CoveringLean.SynLeaf_K2875_11
import CoveringLean.SynLeaf_K2875_12
import CoveringLean.SynLeaf_K2875_13
import CoveringLean.SynLeaf_K2875_14
import CoveringLean.SynLeaf_K2875_15
import CoveringLean.SynLeaf_K2875_16
import CoveringLean.SynLeaf_K2875_17
import CoveringLean.SynLeaf_K2875_18
import CoveringLean.SynLeaf_K2875_19
import CoveringLean.SynLeaf_K2875_20
import CoveringLean.SynLeaf_K2875_21
import CoveringLean.SynLeaf_K2875_22
import CoveringLean.SynLeaf_K2875_23
import CoveringLean.SynLeaf_K2875_24
import CoveringLean.SynLeaf_K2875_25
import CoveringLean.SynLeaf_K2875_26
import CoveringLean.SynLeaf_K2875_27
import CoveringLean.SynLeaf_K2875_28
import CoveringLean.SynLeaf_K2875_29

/-! # K_5(11,4) ≤ 2875 pelo certificado por síndromes

Código: `Syn.LK2875` (sha256 canônico 2a700e2f928a8d893e8863ee100c9514a8ffd65a480776682c7560c96029dc9b), união de 23 cosets completos de um
`[11,3]_5` (bloco de informação [0,3)) com 0 palavras de remendo;
0 síndromes órfãs (0 pontos checados um a um).
-/

namespace Syn

set_option maxRecDepth 100000

theorem hTK2875 : ∀ t < 390625, ∃ w, okT PK2875 t w = true :=
  all_of_chunks (fun t => ∃ w, okT PK2875 t w = true) 4096 96 390625 (by norm_num) (by
    intro c hc
    match c, hc with
    | 0, _ => exact fun i _ hlt => chkT_sound PK2875 _ _ _ _ TK2875_0 i (by omega)
    | 1, _ => exact fun i _ hlt => chkT_sound PK2875 _ _ _ _ TK2875_1 i (by omega)
    | 2, _ => exact fun i _ hlt => chkT_sound PK2875 _ _ _ _ TK2875_2 i (by omega)
    | 3, _ => exact fun i _ hlt => chkT_sound PK2875 _ _ _ _ TK2875_3 i (by omega)
    | 4, _ => exact fun i _ hlt => chkT_sound PK2875 _ _ _ _ TK2875_4 i (by omega)
    | 5, _ => exact fun i _ hlt => chkT_sound PK2875 _ _ _ _ TK2875_5 i (by omega)
    | 6, _ => exact fun i _ hlt => chkT_sound PK2875 _ _ _ _ TK2875_6 i (by omega)
    | 7, _ => exact fun i _ hlt => chkT_sound PK2875 _ _ _ _ TK2875_7 i (by omega)
    | 8, _ => exact fun i _ hlt => chkT_sound PK2875 _ _ _ _ TK2875_8 i (by omega)
    | 9, _ => exact fun i _ hlt => chkT_sound PK2875 _ _ _ _ TK2875_9 i (by omega)
    | 10, _ => exact fun i _ hlt => chkT_sound PK2875 _ _ _ _ TK2875_10 i (by omega)
    | 11, _ => exact fun i _ hlt => chkT_sound PK2875 _ _ _ _ TK2875_11 i (by omega)
    | 12, _ => exact fun i _ hlt => chkT_sound PK2875 _ _ _ _ TK2875_12 i (by omega)
    | 13, _ => exact fun i _ hlt => chkT_sound PK2875 _ _ _ _ TK2875_13 i (by omega)
    | 14, _ => exact fun i _ hlt => chkT_sound PK2875 _ _ _ _ TK2875_14 i (by omega)
    | 15, _ => exact fun i _ hlt => chkT_sound PK2875 _ _ _ _ TK2875_15 i (by omega)
    | 16, _ => exact fun i _ hlt => chkT_sound PK2875 _ _ _ _ TK2875_16 i (by omega)
    | 17, _ => exact fun i _ hlt => chkT_sound PK2875 _ _ _ _ TK2875_17 i (by omega)
    | 18, _ => exact fun i _ hlt => chkT_sound PK2875 _ _ _ _ TK2875_18 i (by omega)
    | 19, _ => exact fun i _ hlt => chkT_sound PK2875 _ _ _ _ TK2875_19 i (by omega)
    | 20, _ => exact fun i _ hlt => chkT_sound PK2875 _ _ _ _ TK2875_20 i (by omega)
    | 21, _ => exact fun i _ hlt => chkT_sound PK2875 _ _ _ _ TK2875_21 i (by omega)
    | 22, _ => exact fun i _ hlt => chkT_sound PK2875 _ _ _ _ TK2875_22 i (by omega)
    | 23, _ => exact fun i _ hlt => chkT_sound PK2875 _ _ _ _ TK2875_23 i (by omega)
    | 24, _ => exact fun i _ hlt => chkT_sound PK2875 _ _ _ _ TK2875_24 i (by omega)
    | 25, _ => exact fun i _ hlt => chkT_sound PK2875 _ _ _ _ TK2875_25 i (by omega)
    | 26, _ => exact fun i _ hlt => chkT_sound PK2875 _ _ _ _ TK2875_26 i (by omega)
    | 27, _ => exact fun i _ hlt => chkT_sound PK2875 _ _ _ _ TK2875_27 i (by omega)
    | 28, _ => exact fun i _ hlt => chkT_sound PK2875 _ _ _ _ TK2875_28 i (by omega)
    | 29, _ => exact fun i _ hlt => chkT_sound PK2875 _ _ _ _ TK2875_29 i (by omega)
    | 30, _ => exact fun i _ hlt => chkT_sound PK2875 _ _ _ _ TK2875_30 i (by omega)
    | 31, _ => exact fun i _ hlt => chkT_sound PK2875 _ _ _ _ TK2875_31 i (by omega)
    | 32, _ => exact fun i _ hlt => chkT_sound PK2875 _ _ _ _ TK2875_32 i (by omega)
    | 33, _ => exact fun i _ hlt => chkT_sound PK2875 _ _ _ _ TK2875_33 i (by omega)
    | 34, _ => exact fun i _ hlt => chkT_sound PK2875 _ _ _ _ TK2875_34 i (by omega)
    | 35, _ => exact fun i _ hlt => chkT_sound PK2875 _ _ _ _ TK2875_35 i (by omega)
    | 36, _ => exact fun i _ hlt => chkT_sound PK2875 _ _ _ _ TK2875_36 i (by omega)
    | 37, _ => exact fun i _ hlt => chkT_sound PK2875 _ _ _ _ TK2875_37 i (by omega)
    | 38, _ => exact fun i _ hlt => chkT_sound PK2875 _ _ _ _ TK2875_38 i (by omega)
    | 39, _ => exact fun i _ hlt => chkT_sound PK2875 _ _ _ _ TK2875_39 i (by omega)
    | 40, _ => exact fun i _ hlt => chkT_sound PK2875 _ _ _ _ TK2875_40 i (by omega)
    | 41, _ => exact fun i _ hlt => chkT_sound PK2875 _ _ _ _ TK2875_41 i (by omega)
    | 42, _ => exact fun i _ hlt => chkT_sound PK2875 _ _ _ _ TK2875_42 i (by omega)
    | 43, _ => exact fun i _ hlt => chkT_sound PK2875 _ _ _ _ TK2875_43 i (by omega)
    | 44, _ => exact fun i _ hlt => chkT_sound PK2875 _ _ _ _ TK2875_44 i (by omega)
    | 45, _ => exact fun i _ hlt => chkT_sound PK2875 _ _ _ _ TK2875_45 i (by omega)
    | 46, _ => exact fun i _ hlt => chkT_sound PK2875 _ _ _ _ TK2875_46 i (by omega)
    | 47, _ => exact fun i _ hlt => chkT_sound PK2875 _ _ _ _ TK2875_47 i (by omega)
    | 48, _ => exact fun i _ hlt => chkT_sound PK2875 _ _ _ _ TK2875_48 i (by omega)
    | 49, _ => exact fun i _ hlt => chkT_sound PK2875 _ _ _ _ TK2875_49 i (by omega)
    | 50, _ => exact fun i _ hlt => chkT_sound PK2875 _ _ _ _ TK2875_50 i (by omega)
    | 51, _ => exact fun i _ hlt => chkT_sound PK2875 _ _ _ _ TK2875_51 i (by omega)
    | 52, _ => exact fun i _ hlt => chkT_sound PK2875 _ _ _ _ TK2875_52 i (by omega)
    | 53, _ => exact fun i _ hlt => chkT_sound PK2875 _ _ _ _ TK2875_53 i (by omega)
    | 54, _ => exact fun i _ hlt => chkT_sound PK2875 _ _ _ _ TK2875_54 i (by omega)
    | 55, _ => exact fun i _ hlt => chkT_sound PK2875 _ _ _ _ TK2875_55 i (by omega)
    | 56, _ => exact fun i _ hlt => chkT_sound PK2875 _ _ _ _ TK2875_56 i (by omega)
    | 57, _ => exact fun i _ hlt => chkT_sound PK2875 _ _ _ _ TK2875_57 i (by omega)
    | 58, _ => exact fun i _ hlt => chkT_sound PK2875 _ _ _ _ TK2875_58 i (by omega)
    | 59, _ => exact fun i _ hlt => chkT_sound PK2875 _ _ _ _ TK2875_59 i (by omega)
    | 60, _ => exact fun i _ hlt => chkT_sound PK2875 _ _ _ _ TK2875_60 i (by omega)
    | 61, _ => exact fun i _ hlt => chkT_sound PK2875 _ _ _ _ TK2875_61 i (by omega)
    | 62, _ => exact fun i _ hlt => chkT_sound PK2875 _ _ _ _ TK2875_62 i (by omega)
    | 63, _ => exact fun i _ hlt => chkT_sound PK2875 _ _ _ _ TK2875_63 i (by omega)
    | 64, _ => exact fun i _ hlt => chkT_sound PK2875 _ _ _ _ TK2875_64 i (by omega)
    | 65, _ => exact fun i _ hlt => chkT_sound PK2875 _ _ _ _ TK2875_65 i (by omega)
    | 66, _ => exact fun i _ hlt => chkT_sound PK2875 _ _ _ _ TK2875_66 i (by omega)
    | 67, _ => exact fun i _ hlt => chkT_sound PK2875 _ _ _ _ TK2875_67 i (by omega)
    | 68, _ => exact fun i _ hlt => chkT_sound PK2875 _ _ _ _ TK2875_68 i (by omega)
    | 69, _ => exact fun i _ hlt => chkT_sound PK2875 _ _ _ _ TK2875_69 i (by omega)
    | 70, _ => exact fun i _ hlt => chkT_sound PK2875 _ _ _ _ TK2875_70 i (by omega)
    | 71, _ => exact fun i _ hlt => chkT_sound PK2875 _ _ _ _ TK2875_71 i (by omega)
    | 72, _ => exact fun i _ hlt => chkT_sound PK2875 _ _ _ _ TK2875_72 i (by omega)
    | 73, _ => exact fun i _ hlt => chkT_sound PK2875 _ _ _ _ TK2875_73 i (by omega)
    | 74, _ => exact fun i _ hlt => chkT_sound PK2875 _ _ _ _ TK2875_74 i (by omega)
    | 75, _ => exact fun i _ hlt => chkT_sound PK2875 _ _ _ _ TK2875_75 i (by omega)
    | 76, _ => exact fun i _ hlt => chkT_sound PK2875 _ _ _ _ TK2875_76 i (by omega)
    | 77, _ => exact fun i _ hlt => chkT_sound PK2875 _ _ _ _ TK2875_77 i (by omega)
    | 78, _ => exact fun i _ hlt => chkT_sound PK2875 _ _ _ _ TK2875_78 i (by omega)
    | 79, _ => exact fun i _ hlt => chkT_sound PK2875 _ _ _ _ TK2875_79 i (by omega)
    | 80, _ => exact fun i _ hlt => chkT_sound PK2875 _ _ _ _ TK2875_80 i (by omega)
    | 81, _ => exact fun i _ hlt => chkT_sound PK2875 _ _ _ _ TK2875_81 i (by omega)
    | 82, _ => exact fun i _ hlt => chkT_sound PK2875 _ _ _ _ TK2875_82 i (by omega)
    | 83, _ => exact fun i _ hlt => chkT_sound PK2875 _ _ _ _ TK2875_83 i (by omega)
    | 84, _ => exact fun i _ hlt => chkT_sound PK2875 _ _ _ _ TK2875_84 i (by omega)
    | 85, _ => exact fun i _ hlt => chkT_sound PK2875 _ _ _ _ TK2875_85 i (by omega)
    | 86, _ => exact fun i _ hlt => chkT_sound PK2875 _ _ _ _ TK2875_86 i (by omega)
    | 87, _ => exact fun i _ hlt => chkT_sound PK2875 _ _ _ _ TK2875_87 i (by omega)
    | 88, _ => exact fun i _ hlt => chkT_sound PK2875 _ _ _ _ TK2875_88 i (by omega)
    | 89, _ => exact fun i _ hlt => chkT_sound PK2875 _ _ _ _ TK2875_89 i (by omega)
    | 90, _ => exact fun i _ hlt => chkT_sound PK2875 _ _ _ _ TK2875_90 i (by omega)
    | 91, _ => exact fun i _ hlt => chkT_sound PK2875 _ _ _ _ TK2875_91 i (by omega)
    | 92, _ => exact fun i _ hlt => chkT_sound PK2875 _ _ _ _ TK2875_92 i (by omega)
    | 93, _ => exact fun i _ hlt => chkT_sound PK2875 _ _ _ _ TK2875_93 i (by omega)
    | 94, _ => exact fun i _ hlt => chkT_sound PK2875 _ _ _ _ TK2875_94 i (by omega)
    | 95, _ => exact fun i _ hlt => chkT_sound PK2875 _ _ _ _ TK2875_95 i (by omega)
    | c + 96, h => exact absurd h (by omega))

theorem hOK2875 : ∀ i < PK2875.orphs.length, ∀ a < 125, ∃ j, okO PK2875 (PK2875.orphs.getD i 0) a j = true := by
  intro i hi
  match i, hi with
  | i + 0, h => exact absurd h (by have : PK2875.orphs.length = 0 := rfl; omega)

theorem hBK2875 : ∀ s < PK2875.reps.length, ∀ m < 125, ∃ j, okB PK2875 s m j = true := by
  intro s hs
  match s, hs with
  | 0, _ => exact chkB_sound PK2875 _ _ _ _ BK2875_0
  | 1, _ => exact chkB_sound PK2875 _ _ _ _ BK2875_1
  | 2, _ => exact chkB_sound PK2875 _ _ _ _ BK2875_2
  | 3, _ => exact chkB_sound PK2875 _ _ _ _ BK2875_3
  | 4, _ => exact chkB_sound PK2875 _ _ _ _ BK2875_4
  | 5, _ => exact chkB_sound PK2875 _ _ _ _ BK2875_5
  | 6, _ => exact chkB_sound PK2875 _ _ _ _ BK2875_6
  | 7, _ => exact chkB_sound PK2875 _ _ _ _ BK2875_7
  | 8, _ => exact chkB_sound PK2875 _ _ _ _ BK2875_8
  | 9, _ => exact chkB_sound PK2875 _ _ _ _ BK2875_9
  | 10, _ => exact chkB_sound PK2875 _ _ _ _ BK2875_10
  | 11, _ => exact chkB_sound PK2875 _ _ _ _ BK2875_11
  | 12, _ => exact chkB_sound PK2875 _ _ _ _ BK2875_12
  | 13, _ => exact chkB_sound PK2875 _ _ _ _ BK2875_13
  | 14, _ => exact chkB_sound PK2875 _ _ _ _ BK2875_14
  | 15, _ => exact chkB_sound PK2875 _ _ _ _ BK2875_15
  | 16, _ => exact chkB_sound PK2875 _ _ _ _ BK2875_16
  | 17, _ => exact chkB_sound PK2875 _ _ _ _ BK2875_17
  | 18, _ => exact chkB_sound PK2875 _ _ _ _ BK2875_18
  | 19, _ => exact chkB_sound PK2875 _ _ _ _ BK2875_19
  | 20, _ => exact chkB_sound PK2875 _ _ _ _ BK2875_20
  | 21, _ => exact chkB_sound PK2875 _ _ _ _ BK2875_21
  | 22, _ => exact chkB_sound PK2875 _ _ _ _ BK2875_22
  | s + 23, h => exact absurd h (by have : PK2875.reps.length = 23 := rfl; omega)

/-- Não-vacuidade: o verificador recusa uma testemunha errada (ponto `t = 0`, palavra
`33` a distância 11 > 4). -/
example : okT PK2875 0 33 = false := by decide +kernel

/-- `K_5(11,4) ≤ 2875`: o código `LK2875` tem 2875 palavras e cobre com raio 4. -/
theorem K5_11_4_le_2875_syn :
    ∃ C : Finset (Fin 11 → ZMod 5), C.card = 2875 ∧ CoveringA2.Covers 4 C :=
  syn_cert PK2875 LK2875 rfl rfl rfl ⟨rfl, by decide⟩ VK2875 hTK2875 hOK2875 hBK2875
    (by decide +kernel) (by decide +kernel) (by decide +kernel)

end Syn

#print axioms Syn.K5_11_4_le_2875_syn
