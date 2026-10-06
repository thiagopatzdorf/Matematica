-- gerado por scripts/syndrome/gen_syn.py; não editar à mão
import CoveringLean.SynBridge
import CoveringLean.SynLeaf_K2_15_2_384_0
import CoveringLean.SynLeaf_K2_15_2_384_1
import CoveringLean.SynLeaf_K2_15_2_384_2
import CoveringLean.SynLeaf_K2_15_2_384_3
import CoveringLean.SynLeaf_K2_15_2_384_4
import CoveringLean.SynLeaf_K2_15_2_384_5
import CoveringLean.SynLeaf_K2_15_2_384_6
import CoveringLean.SynLeaf_K2_15_2_384_7
import CoveringLean.SynLeaf_K2_15_2_384_8
import CoveringLean.SynLeaf_K2_15_2_384_9
import CoveringLean.SynLeaf_K2_15_2_384_10
import CoveringLean.SynLeaf_K2_15_2_384_11
import CoveringLean.SynLeaf_K2_15_2_384_12
import CoveringLean.SynLeaf_K2_15_2_384_13
import CoveringLean.SynLeaf_K2_15_2_384_14
import CoveringLean.SynLeaf_K2_15_2_384_15
import CoveringLean.SynLeaf_K2_15_2_384_16
import CoveringLean.SynLeaf_K2_15_2_384_17
import CoveringLean.SynLeaf_K2_15_2_384_18
import CoveringLean.SynLeaf_K2_15_2_384_19
import CoveringLean.SynLeaf_K2_15_2_384_20
import CoveringLean.SynLeaf_K2_15_2_384_21
import CoveringLean.SynLeaf_K2_15_2_384_22
import CoveringLean.SynLeaf_K2_15_2_384_23
import CoveringLean.SynLeaf_K2_15_2_384_24
import CoveringLean.SynLeaf_K2_15_2_384_25
import CoveringLean.SynLeaf_K2_15_2_384_26
import CoveringLean.SynLeaf_K2_15_2_384_27
import CoveringLean.SynLeaf_K2_15_2_384_28
import CoveringLean.SynLeaf_K2_15_2_384_29
import CoveringLean.SynLeaf_K2_15_2_384_30
import CoveringLean.SynLeaf_K2_15_2_384_31
import CoveringLean.SynLeaf_K2_15_2_384_32
import CoveringLean.SynLeaf_K2_15_2_384_33
import CoveringLean.SynLeaf_K2_15_2_384_34
import CoveringLean.SynLeaf_K2_15_2_384_35
import CoveringLean.SynLeaf_K2_15_2_384_36
import CoveringLean.SynLeaf_K2_15_2_384_37
import CoveringLean.SynLeaf_K2_15_2_384_38
import CoveringLean.SynLeaf_K2_15_2_384_39
import CoveringLean.SynLeaf_K2_15_2_384_40
import CoveringLean.SynLeaf_K2_15_2_384_41
import CoveringLean.SynLeaf_K2_15_2_384_42
import CoveringLean.SynLeaf_K2_15_2_384_43
import CoveringLean.SynLeaf_K2_15_2_384_44
import CoveringLean.SynLeaf_K2_15_2_384_45
import CoveringLean.SynLeaf_K2_15_2_384_46
import CoveringLean.SynLeaf_K2_15_2_384_47
import CoveringLean.SynLeaf_K2_15_2_384_48
import CoveringLean.SynLeaf_K2_15_2_384_49

/-! # K_2(15,2) ≤ 384 pelo certificado por síndromes

Código: `Syn.LK2_15_2_384` (sha256 canônico 57c2d0bc2c6d52fee4d6f3adf3de604a4827627d257cb666559d35cb695d0fc0), união de 192 cosets completos de um
`[15,1]_2` (bloco de informação [0,1)) com 0 palavras de remendo;
0 síndromes órfãs (0 pontos checados um a um).
-/

namespace Syn

set_option maxRecDepth 100000

theorem hTK2_15_2_384 : ∀ t < 16384, ∃ w, okT PK2_15_2_384 t w = true :=
  all_of_chunks (fun t => ∃ w, okT PK2_15_2_384 t w = true) 4096 4 16384 (by norm_num) (by
    intro c hc
    match c, hc with
    | 0, _ => exact fun i _ hlt => chkT_sound PK2_15_2_384 _ _ _ _ TK2_15_2_384_0 i (by omega)
    | 1, _ => exact fun i _ hlt => chkT_sound PK2_15_2_384 _ _ _ _ TK2_15_2_384_1 i (by omega)
    | 2, _ => exact fun i _ hlt => chkT_sound PK2_15_2_384 _ _ _ _ TK2_15_2_384_2 i (by omega)
    | 3, _ => exact fun i _ hlt => chkT_sound PK2_15_2_384 _ _ _ _ TK2_15_2_384_3 i (by omega)
    | c + 4, h => exact absurd h (by omega))

theorem hOK2_15_2_384 : ∀ i < PK2_15_2_384.orphs.length, ∀ a < 2, ∃ j, okO PK2_15_2_384 (PK2_15_2_384.orphs.getD i 0) a j = true := by
  intro i hi
  match i, hi with
  | i + 0, h => exact absurd h (by have : PK2_15_2_384.orphs.length = 0 := rfl; omega)

theorem hBK2_15_2_384 : ∀ s < PK2_15_2_384.reps.length, ∀ m < 2, ∃ j, okB PK2_15_2_384 s m j = true := by
  intro s hs
  match s, hs with
  | 0, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_0
  | 1, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_1
  | 2, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_2
  | 3, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_3
  | 4, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_4
  | 5, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_5
  | 6, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_6
  | 7, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_7
  | 8, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_8
  | 9, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_9
  | 10, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_10
  | 11, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_11
  | 12, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_12
  | 13, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_13
  | 14, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_14
  | 15, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_15
  | 16, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_16
  | 17, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_17
  | 18, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_18
  | 19, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_19
  | 20, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_20
  | 21, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_21
  | 22, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_22
  | 23, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_23
  | 24, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_24
  | 25, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_25
  | 26, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_26
  | 27, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_27
  | 28, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_28
  | 29, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_29
  | 30, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_30
  | 31, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_31
  | 32, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_32
  | 33, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_33
  | 34, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_34
  | 35, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_35
  | 36, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_36
  | 37, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_37
  | 38, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_38
  | 39, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_39
  | 40, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_40
  | 41, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_41
  | 42, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_42
  | 43, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_43
  | 44, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_44
  | 45, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_45
  | 46, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_46
  | 47, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_47
  | 48, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_48
  | 49, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_49
  | 50, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_50
  | 51, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_51
  | 52, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_52
  | 53, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_53
  | 54, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_54
  | 55, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_55
  | 56, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_56
  | 57, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_57
  | 58, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_58
  | 59, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_59
  | 60, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_60
  | 61, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_61
  | 62, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_62
  | 63, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_63
  | 64, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_64
  | 65, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_65
  | 66, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_66
  | 67, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_67
  | 68, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_68
  | 69, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_69
  | 70, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_70
  | 71, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_71
  | 72, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_72
  | 73, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_73
  | 74, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_74
  | 75, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_75
  | 76, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_76
  | 77, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_77
  | 78, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_78
  | 79, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_79
  | 80, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_80
  | 81, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_81
  | 82, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_82
  | 83, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_83
  | 84, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_84
  | 85, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_85
  | 86, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_86
  | 87, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_87
  | 88, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_88
  | 89, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_89
  | 90, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_90
  | 91, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_91
  | 92, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_92
  | 93, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_93
  | 94, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_94
  | 95, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_95
  | 96, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_96
  | 97, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_97
  | 98, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_98
  | 99, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_99
  | 100, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_100
  | 101, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_101
  | 102, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_102
  | 103, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_103
  | 104, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_104
  | 105, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_105
  | 106, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_106
  | 107, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_107
  | 108, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_108
  | 109, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_109
  | 110, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_110
  | 111, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_111
  | 112, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_112
  | 113, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_113
  | 114, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_114
  | 115, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_115
  | 116, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_116
  | 117, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_117
  | 118, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_118
  | 119, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_119
  | 120, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_120
  | 121, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_121
  | 122, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_122
  | 123, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_123
  | 124, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_124
  | 125, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_125
  | 126, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_126
  | 127, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_127
  | 128, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_128
  | 129, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_129
  | 130, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_130
  | 131, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_131
  | 132, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_132
  | 133, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_133
  | 134, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_134
  | 135, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_135
  | 136, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_136
  | 137, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_137
  | 138, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_138
  | 139, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_139
  | 140, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_140
  | 141, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_141
  | 142, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_142
  | 143, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_143
  | 144, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_144
  | 145, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_145
  | 146, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_146
  | 147, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_147
  | 148, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_148
  | 149, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_149
  | 150, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_150
  | 151, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_151
  | 152, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_152
  | 153, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_153
  | 154, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_154
  | 155, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_155
  | 156, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_156
  | 157, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_157
  | 158, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_158
  | 159, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_159
  | 160, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_160
  | 161, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_161
  | 162, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_162
  | 163, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_163
  | 164, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_164
  | 165, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_165
  | 166, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_166
  | 167, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_167
  | 168, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_168
  | 169, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_169
  | 170, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_170
  | 171, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_171
  | 172, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_172
  | 173, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_173
  | 174, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_174
  | 175, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_175
  | 176, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_176
  | 177, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_177
  | 178, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_178
  | 179, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_179
  | 180, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_180
  | 181, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_181
  | 182, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_182
  | 183, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_183
  | 184, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_184
  | 185, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_185
  | 186, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_186
  | 187, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_187
  | 188, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_188
  | 189, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_189
  | 190, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_190
  | 191, _ => exact chkB_sound PK2_15_2_384 _ _ _ _ BK2_15_2_384_191
  | s + 192, h => exact absurd h (by have : PK2_15_2_384.reps.length = 192 := rfl; omega)

/-- Não-vacuidade: o verificador recusa uma testemunha errada (ponto `t = 0`, palavra
`71` a distância 14 > 2). -/
example : okT PK2_15_2_384 0 71 = false := by decide +kernel

/-- `K_2(15,2) ≤ 384`: o código `LK2_15_2_384` tem 384 palavras e cobre com raio 2. -/
theorem K2_15_2_le_384_syn :
    ∃ C : Finset (Fin 15 → ZMod 2), C.card = 384 ∧ CoveringA2.Covers 2 C :=
  syn_cert PK2_15_2_384 LK2_15_2_384 rfl rfl rfl ⟨rfl, by decide⟩ VK2_15_2_384 hTK2_15_2_384 hOK2_15_2_384 hBK2_15_2_384
    (by decide +kernel) (by decide +kernel) (by decide +kernel)

end Syn

#print axioms Syn.K2_15_2_le_384_syn
