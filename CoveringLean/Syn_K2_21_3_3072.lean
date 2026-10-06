-- gerado por scripts/syndrome/gen_syn.py; não editar à mão
import CoveringLean.SynBridge
import CoveringLean.SynLeaf_K2_21_3_3072_0
import CoveringLean.SynLeaf_K2_21_3_3072_1
import CoveringLean.SynLeaf_K2_21_3_3072_2
import CoveringLean.SynLeaf_K2_21_3_3072_3
import CoveringLean.SynLeaf_K2_21_3_3072_4
import CoveringLean.SynLeaf_K2_21_3_3072_5
import CoveringLean.SynLeaf_K2_21_3_3072_6
import CoveringLean.SynLeaf_K2_21_3_3072_7
import CoveringLean.SynLeaf_K2_21_3_3072_8
import CoveringLean.SynLeaf_K2_21_3_3072_9
import CoveringLean.SynLeaf_K2_21_3_3072_10
import CoveringLean.SynLeaf_K2_21_3_3072_11
import CoveringLean.SynLeaf_K2_21_3_3072_12
import CoveringLean.SynLeaf_K2_21_3_3072_13
import CoveringLean.SynLeaf_K2_21_3_3072_14
import CoveringLean.SynLeaf_K2_21_3_3072_15
import CoveringLean.SynLeaf_K2_21_3_3072_16
import CoveringLean.SynLeaf_K2_21_3_3072_17
import CoveringLean.SynLeaf_K2_21_3_3072_18
import CoveringLean.SynLeaf_K2_21_3_3072_19
import CoveringLean.SynLeaf_K2_21_3_3072_20
import CoveringLean.SynLeaf_K2_21_3_3072_21
import CoveringLean.SynLeaf_K2_21_3_3072_22
import CoveringLean.SynLeaf_K2_21_3_3072_23
import CoveringLean.SynLeaf_K2_21_3_3072_24
import CoveringLean.SynLeaf_K2_21_3_3072_25
import CoveringLean.SynLeaf_K2_21_3_3072_26
import CoveringLean.SynLeaf_K2_21_3_3072_27
import CoveringLean.SynLeaf_K2_21_3_3072_28

/-! # K_2(21,3) ≤ 3072 pelo certificado por síndromes

Código: `Syn.LK2_21_3_3072` (sha256 canônico 820ee32ecae2f28c71d8daca7539a849aa91540eb8dde75d91a9b9f5dca6d877), união de 96 cosets completos de um
`[21,5]_2` (bloco de informação [13,18)) com 0 palavras de remendo;
0 síndromes órfãs (0 pontos checados um a um).
-/

namespace Syn

set_option maxRecDepth 100000

theorem hTK2_21_3_3072 : ∀ t < 65536, ∃ w, okT PK2_21_3_3072 t w = true :=
  all_of_chunks (fun t => ∃ w, okT PK2_21_3_3072 t w = true) 4096 16 65536 (by norm_num) (by
    intro c hc
    match c, hc with
    | 0, _ => exact fun i _ hlt => chkT_sound PK2_21_3_3072 _ _ _ _ TK2_21_3_3072_0 i (by omega)
    | 1, _ => exact fun i _ hlt => chkT_sound PK2_21_3_3072 _ _ _ _ TK2_21_3_3072_1 i (by omega)
    | 2, _ => exact fun i _ hlt => chkT_sound PK2_21_3_3072 _ _ _ _ TK2_21_3_3072_2 i (by omega)
    | 3, _ => exact fun i _ hlt => chkT_sound PK2_21_3_3072 _ _ _ _ TK2_21_3_3072_3 i (by omega)
    | 4, _ => exact fun i _ hlt => chkT_sound PK2_21_3_3072 _ _ _ _ TK2_21_3_3072_4 i (by omega)
    | 5, _ => exact fun i _ hlt => chkT_sound PK2_21_3_3072 _ _ _ _ TK2_21_3_3072_5 i (by omega)
    | 6, _ => exact fun i _ hlt => chkT_sound PK2_21_3_3072 _ _ _ _ TK2_21_3_3072_6 i (by omega)
    | 7, _ => exact fun i _ hlt => chkT_sound PK2_21_3_3072 _ _ _ _ TK2_21_3_3072_7 i (by omega)
    | 8, _ => exact fun i _ hlt => chkT_sound PK2_21_3_3072 _ _ _ _ TK2_21_3_3072_8 i (by omega)
    | 9, _ => exact fun i _ hlt => chkT_sound PK2_21_3_3072 _ _ _ _ TK2_21_3_3072_9 i (by omega)
    | 10, _ => exact fun i _ hlt => chkT_sound PK2_21_3_3072 _ _ _ _ TK2_21_3_3072_10 i (by omega)
    | 11, _ => exact fun i _ hlt => chkT_sound PK2_21_3_3072 _ _ _ _ TK2_21_3_3072_11 i (by omega)
    | 12, _ => exact fun i _ hlt => chkT_sound PK2_21_3_3072 _ _ _ _ TK2_21_3_3072_12 i (by omega)
    | 13, _ => exact fun i _ hlt => chkT_sound PK2_21_3_3072 _ _ _ _ TK2_21_3_3072_13 i (by omega)
    | 14, _ => exact fun i _ hlt => chkT_sound PK2_21_3_3072 _ _ _ _ TK2_21_3_3072_14 i (by omega)
    | 15, _ => exact fun i _ hlt => chkT_sound PK2_21_3_3072 _ _ _ _ TK2_21_3_3072_15 i (by omega)
    | c + 16, h => exact absurd h (by omega))

theorem hOK2_21_3_3072 : ∀ i < PK2_21_3_3072.orphs.length, ∀ a < 32, ∃ j, okO PK2_21_3_3072 (PK2_21_3_3072.orphs.getD i 0) a j = true := by
  intro i hi
  match i, hi with
  | i + 0, h => exact absurd h (by have : PK2_21_3_3072.orphs.length = 0 := rfl; omega)

theorem hBK2_21_3_3072 : ∀ s < PK2_21_3_3072.reps.length, ∀ m < 32, ∃ j, okB PK2_21_3_3072 s m j = true := by
  intro s hs
  match s, hs with
  | 0, _ => exact chkB_sound PK2_21_3_3072 _ _ _ _ BK2_21_3_3072_0
  | 1, _ => exact chkB_sound PK2_21_3_3072 _ _ _ _ BK2_21_3_3072_1
  | 2, _ => exact chkB_sound PK2_21_3_3072 _ _ _ _ BK2_21_3_3072_2
  | 3, _ => exact chkB_sound PK2_21_3_3072 _ _ _ _ BK2_21_3_3072_3
  | 4, _ => exact chkB_sound PK2_21_3_3072 _ _ _ _ BK2_21_3_3072_4
  | 5, _ => exact chkB_sound PK2_21_3_3072 _ _ _ _ BK2_21_3_3072_5
  | 6, _ => exact chkB_sound PK2_21_3_3072 _ _ _ _ BK2_21_3_3072_6
  | 7, _ => exact chkB_sound PK2_21_3_3072 _ _ _ _ BK2_21_3_3072_7
  | 8, _ => exact chkB_sound PK2_21_3_3072 _ _ _ _ BK2_21_3_3072_8
  | 9, _ => exact chkB_sound PK2_21_3_3072 _ _ _ _ BK2_21_3_3072_9
  | 10, _ => exact chkB_sound PK2_21_3_3072 _ _ _ _ BK2_21_3_3072_10
  | 11, _ => exact chkB_sound PK2_21_3_3072 _ _ _ _ BK2_21_3_3072_11
  | 12, _ => exact chkB_sound PK2_21_3_3072 _ _ _ _ BK2_21_3_3072_12
  | 13, _ => exact chkB_sound PK2_21_3_3072 _ _ _ _ BK2_21_3_3072_13
  | 14, _ => exact chkB_sound PK2_21_3_3072 _ _ _ _ BK2_21_3_3072_14
  | 15, _ => exact chkB_sound PK2_21_3_3072 _ _ _ _ BK2_21_3_3072_15
  | 16, _ => exact chkB_sound PK2_21_3_3072 _ _ _ _ BK2_21_3_3072_16
  | 17, _ => exact chkB_sound PK2_21_3_3072 _ _ _ _ BK2_21_3_3072_17
  | 18, _ => exact chkB_sound PK2_21_3_3072 _ _ _ _ BK2_21_3_3072_18
  | 19, _ => exact chkB_sound PK2_21_3_3072 _ _ _ _ BK2_21_3_3072_19
  | 20, _ => exact chkB_sound PK2_21_3_3072 _ _ _ _ BK2_21_3_3072_20
  | 21, _ => exact chkB_sound PK2_21_3_3072 _ _ _ _ BK2_21_3_3072_21
  | 22, _ => exact chkB_sound PK2_21_3_3072 _ _ _ _ BK2_21_3_3072_22
  | 23, _ => exact chkB_sound PK2_21_3_3072 _ _ _ _ BK2_21_3_3072_23
  | 24, _ => exact chkB_sound PK2_21_3_3072 _ _ _ _ BK2_21_3_3072_24
  | 25, _ => exact chkB_sound PK2_21_3_3072 _ _ _ _ BK2_21_3_3072_25
  | 26, _ => exact chkB_sound PK2_21_3_3072 _ _ _ _ BK2_21_3_3072_26
  | 27, _ => exact chkB_sound PK2_21_3_3072 _ _ _ _ BK2_21_3_3072_27
  | 28, _ => exact chkB_sound PK2_21_3_3072 _ _ _ _ BK2_21_3_3072_28
  | 29, _ => exact chkB_sound PK2_21_3_3072 _ _ _ _ BK2_21_3_3072_29
  | 30, _ => exact chkB_sound PK2_21_3_3072 _ _ _ _ BK2_21_3_3072_30
  | 31, _ => exact chkB_sound PK2_21_3_3072 _ _ _ _ BK2_21_3_3072_31
  | 32, _ => exact chkB_sound PK2_21_3_3072 _ _ _ _ BK2_21_3_3072_32
  | 33, _ => exact chkB_sound PK2_21_3_3072 _ _ _ _ BK2_21_3_3072_33
  | 34, _ => exact chkB_sound PK2_21_3_3072 _ _ _ _ BK2_21_3_3072_34
  | 35, _ => exact chkB_sound PK2_21_3_3072 _ _ _ _ BK2_21_3_3072_35
  | 36, _ => exact chkB_sound PK2_21_3_3072 _ _ _ _ BK2_21_3_3072_36
  | 37, _ => exact chkB_sound PK2_21_3_3072 _ _ _ _ BK2_21_3_3072_37
  | 38, _ => exact chkB_sound PK2_21_3_3072 _ _ _ _ BK2_21_3_3072_38
  | 39, _ => exact chkB_sound PK2_21_3_3072 _ _ _ _ BK2_21_3_3072_39
  | 40, _ => exact chkB_sound PK2_21_3_3072 _ _ _ _ BK2_21_3_3072_40
  | 41, _ => exact chkB_sound PK2_21_3_3072 _ _ _ _ BK2_21_3_3072_41
  | 42, _ => exact chkB_sound PK2_21_3_3072 _ _ _ _ BK2_21_3_3072_42
  | 43, _ => exact chkB_sound PK2_21_3_3072 _ _ _ _ BK2_21_3_3072_43
  | 44, _ => exact chkB_sound PK2_21_3_3072 _ _ _ _ BK2_21_3_3072_44
  | 45, _ => exact chkB_sound PK2_21_3_3072 _ _ _ _ BK2_21_3_3072_45
  | 46, _ => exact chkB_sound PK2_21_3_3072 _ _ _ _ BK2_21_3_3072_46
  | 47, _ => exact chkB_sound PK2_21_3_3072 _ _ _ _ BK2_21_3_3072_47
  | 48, _ => exact chkB_sound PK2_21_3_3072 _ _ _ _ BK2_21_3_3072_48
  | 49, _ => exact chkB_sound PK2_21_3_3072 _ _ _ _ BK2_21_3_3072_49
  | 50, _ => exact chkB_sound PK2_21_3_3072 _ _ _ _ BK2_21_3_3072_50
  | 51, _ => exact chkB_sound PK2_21_3_3072 _ _ _ _ BK2_21_3_3072_51
  | 52, _ => exact chkB_sound PK2_21_3_3072 _ _ _ _ BK2_21_3_3072_52
  | 53, _ => exact chkB_sound PK2_21_3_3072 _ _ _ _ BK2_21_3_3072_53
  | 54, _ => exact chkB_sound PK2_21_3_3072 _ _ _ _ BK2_21_3_3072_54
  | 55, _ => exact chkB_sound PK2_21_3_3072 _ _ _ _ BK2_21_3_3072_55
  | 56, _ => exact chkB_sound PK2_21_3_3072 _ _ _ _ BK2_21_3_3072_56
  | 57, _ => exact chkB_sound PK2_21_3_3072 _ _ _ _ BK2_21_3_3072_57
  | 58, _ => exact chkB_sound PK2_21_3_3072 _ _ _ _ BK2_21_3_3072_58
  | 59, _ => exact chkB_sound PK2_21_3_3072 _ _ _ _ BK2_21_3_3072_59
  | 60, _ => exact chkB_sound PK2_21_3_3072 _ _ _ _ BK2_21_3_3072_60
  | 61, _ => exact chkB_sound PK2_21_3_3072 _ _ _ _ BK2_21_3_3072_61
  | 62, _ => exact chkB_sound PK2_21_3_3072 _ _ _ _ BK2_21_3_3072_62
  | 63, _ => exact chkB_sound PK2_21_3_3072 _ _ _ _ BK2_21_3_3072_63
  | 64, _ => exact chkB_sound PK2_21_3_3072 _ _ _ _ BK2_21_3_3072_64
  | 65, _ => exact chkB_sound PK2_21_3_3072 _ _ _ _ BK2_21_3_3072_65
  | 66, _ => exact chkB_sound PK2_21_3_3072 _ _ _ _ BK2_21_3_3072_66
  | 67, _ => exact chkB_sound PK2_21_3_3072 _ _ _ _ BK2_21_3_3072_67
  | 68, _ => exact chkB_sound PK2_21_3_3072 _ _ _ _ BK2_21_3_3072_68
  | 69, _ => exact chkB_sound PK2_21_3_3072 _ _ _ _ BK2_21_3_3072_69
  | 70, _ => exact chkB_sound PK2_21_3_3072 _ _ _ _ BK2_21_3_3072_70
  | 71, _ => exact chkB_sound PK2_21_3_3072 _ _ _ _ BK2_21_3_3072_71
  | 72, _ => exact chkB_sound PK2_21_3_3072 _ _ _ _ BK2_21_3_3072_72
  | 73, _ => exact chkB_sound PK2_21_3_3072 _ _ _ _ BK2_21_3_3072_73
  | 74, _ => exact chkB_sound PK2_21_3_3072 _ _ _ _ BK2_21_3_3072_74
  | 75, _ => exact chkB_sound PK2_21_3_3072 _ _ _ _ BK2_21_3_3072_75
  | 76, _ => exact chkB_sound PK2_21_3_3072 _ _ _ _ BK2_21_3_3072_76
  | 77, _ => exact chkB_sound PK2_21_3_3072 _ _ _ _ BK2_21_3_3072_77
  | 78, _ => exact chkB_sound PK2_21_3_3072 _ _ _ _ BK2_21_3_3072_78
  | 79, _ => exact chkB_sound PK2_21_3_3072 _ _ _ _ BK2_21_3_3072_79
  | 80, _ => exact chkB_sound PK2_21_3_3072 _ _ _ _ BK2_21_3_3072_80
  | 81, _ => exact chkB_sound PK2_21_3_3072 _ _ _ _ BK2_21_3_3072_81
  | 82, _ => exact chkB_sound PK2_21_3_3072 _ _ _ _ BK2_21_3_3072_82
  | 83, _ => exact chkB_sound PK2_21_3_3072 _ _ _ _ BK2_21_3_3072_83
  | 84, _ => exact chkB_sound PK2_21_3_3072 _ _ _ _ BK2_21_3_3072_84
  | 85, _ => exact chkB_sound PK2_21_3_3072 _ _ _ _ BK2_21_3_3072_85
  | 86, _ => exact chkB_sound PK2_21_3_3072 _ _ _ _ BK2_21_3_3072_86
  | 87, _ => exact chkB_sound PK2_21_3_3072 _ _ _ _ BK2_21_3_3072_87
  | 88, _ => exact chkB_sound PK2_21_3_3072 _ _ _ _ BK2_21_3_3072_88
  | 89, _ => exact chkB_sound PK2_21_3_3072 _ _ _ _ BK2_21_3_3072_89
  | 90, _ => exact chkB_sound PK2_21_3_3072 _ _ _ _ BK2_21_3_3072_90
  | 91, _ => exact chkB_sound PK2_21_3_3072 _ _ _ _ BK2_21_3_3072_91
  | 92, _ => exact chkB_sound PK2_21_3_3072 _ _ _ _ BK2_21_3_3072_92
  | 93, _ => exact chkB_sound PK2_21_3_3072 _ _ _ _ BK2_21_3_3072_93
  | 94, _ => exact chkB_sound PK2_21_3_3072 _ _ _ _ BK2_21_3_3072_94
  | 95, _ => exact chkB_sound PK2_21_3_3072 _ _ _ _ BK2_21_3_3072_95
  | s + 96, h => exact absurd h (by have : PK2_21_3_3072.reps.length = 96 := rfl; omega)

/-- Não-vacuidade: o verificador recusa uma testemunha errada (ponto `t = 0`, palavra
`511` a distância 20 > 3). -/
example : okT PK2_21_3_3072 0 511 = false := by decide +kernel

/-- `K_2(21,3) ≤ 3072`: o código `LK2_21_3_3072` tem 3072 palavras e cobre com raio 3. -/
theorem K2_21_3_le_3072_syn :
    ∃ C : Finset (Fin 21 → ZMod 2), C.card = 3072 ∧ CoveringA2.Covers 3 C :=
  syn_cert PK2_21_3_3072 LK2_21_3_3072 rfl rfl rfl ⟨rfl, by decide⟩ VK2_21_3_3072 hTK2_21_3_3072 hOK2_21_3_3072 hBK2_21_3_3072
    (by decide +kernel) (by decide +kernel) (by decide +kernel)

end Syn

#print axioms Syn.K2_21_3_le_3072_syn
