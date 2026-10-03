-- gerado por scripts/syndrome/gen_syn.py; não editar à mão
import CoveringLean.SynBridge
import CoveringLean.SynLeaf_K5616_0
import CoveringLean.SynLeaf_K5616_1
import CoveringLean.SynLeaf_K5616_2
import CoveringLean.SynLeaf_K5616_3
import CoveringLean.SynLeaf_K5616_4
import CoveringLean.SynLeaf_K5616_5
import CoveringLean.SynLeaf_K5616_6
import CoveringLean.SynLeaf_K5616_7
import CoveringLean.SynLeaf_K5616_8
import CoveringLean.SynLeaf_K5616_9
import CoveringLean.SynLeaf_K5616_10
import CoveringLean.SynLeaf_K5616_11
import CoveringLean.SynLeaf_K5616_12
import CoveringLean.SynLeaf_K5616_13
import CoveringLean.SynLeaf_K5616_14
import CoveringLean.SynLeaf_K5616_15
import CoveringLean.SynLeaf_K5616_16
import CoveringLean.SynLeaf_K5616_17
import CoveringLean.SynLeaf_K5616_18
import CoveringLean.SynLeaf_K5616_19
import CoveringLean.SynLeaf_K5616_20
import CoveringLean.SynLeaf_K5616_21
import CoveringLean.SynLeaf_K5616_22
import CoveringLean.SynLeaf_K5616_23
import CoveringLean.SynLeaf_K5616_24
import CoveringLean.SynLeaf_K5616_25
import CoveringLean.SynLeaf_K5616_26
import CoveringLean.SynLeaf_K5616_27
import CoveringLean.SynLeaf_K5616_28
import CoveringLean.SynLeaf_K5616_29
import CoveringLean.SynLeaf_K5616_30
import CoveringLean.SynLeaf_K5616_31
import CoveringLean.SynLeaf_K5616_32
import CoveringLean.SynLeaf_K5616_33
import CoveringLean.SynLeaf_K5616_34
import CoveringLean.SynLeaf_K5616_35
import CoveringLean.SynLeaf_K5616_36
import CoveringLean.SynLeaf_K5616_37
import CoveringLean.SynLeaf_K5616_38
import CoveringLean.SynLeaf_K5616_39
import CoveringLean.SynLeaf_K5616_40
import CoveringLean.SynLeaf_K5616_41
import CoveringLean.SynLeaf_K5616_42
import CoveringLean.SynLeaf_K5616_43
import CoveringLean.SynLeaf_K5616_44
import CoveringLean.SynLeaf_K5616_45
import CoveringLean.SynLeaf_K5616_46
import CoveringLean.SynLeaf_K5616_47
import CoveringLean.SynLeaf_K5616_48
import CoveringLean.SynLeaf_K5616_49
import CoveringLean.SynLeaf_K5616_50
import CoveringLean.SynLeaf_K5616_51
import CoveringLean.SynLeaf_K5616_52
import CoveringLean.SynLeaf_K5616_53
import CoveringLean.SynLeaf_K5616_54
import CoveringLean.SynLeaf_K5616_55

/-! # K_7(10,4) ≤ 5616 pelo certificado por síndromes

Código: `Syn.LK5616` (sha256 canônico 750cae3ba3ded64eef208548f6e3c8fe0356c0b599ab3f605aac6fd175a78a5e), união de 16 cosets completos de um
`[10,3]_7` (bloco de informação [0,3)) com 128 palavras de remendo;
3 síndromes órfãs (1029 pontos checados um a um).
-/

namespace Syn

set_option maxRecDepth 100000

theorem hTK5616 : ∀ t < 823543, ∃ w, okT PK5616 t w = true :=
  all_of_chunks (fun t => ∃ w, okT PK5616 t w = true) 4096 202 823543 (by norm_num) (by
    intro c hc
    match c, hc with
    | 0, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_0 i (by omega)
    | 1, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_1 i (by omega)
    | 2, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_2 i (by omega)
    | 3, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_3 i (by omega)
    | 4, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_4 i (by omega)
    | 5, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_5 i (by omega)
    | 6, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_6 i (by omega)
    | 7, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_7 i (by omega)
    | 8, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_8 i (by omega)
    | 9, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_9 i (by omega)
    | 10, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_10 i (by omega)
    | 11, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_11 i (by omega)
    | 12, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_12 i (by omega)
    | 13, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_13 i (by omega)
    | 14, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_14 i (by omega)
    | 15, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_15 i (by omega)
    | 16, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_16 i (by omega)
    | 17, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_17 i (by omega)
    | 18, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_18 i (by omega)
    | 19, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_19 i (by omega)
    | 20, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_20 i (by omega)
    | 21, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_21 i (by omega)
    | 22, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_22 i (by omega)
    | 23, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_23 i (by omega)
    | 24, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_24 i (by omega)
    | 25, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_25 i (by omega)
    | 26, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_26 i (by omega)
    | 27, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_27 i (by omega)
    | 28, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_28 i (by omega)
    | 29, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_29 i (by omega)
    | 30, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_30 i (by omega)
    | 31, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_31 i (by omega)
    | 32, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_32 i (by omega)
    | 33, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_33 i (by omega)
    | 34, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_34 i (by omega)
    | 35, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_35 i (by omega)
    | 36, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_36 i (by omega)
    | 37, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_37 i (by omega)
    | 38, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_38 i (by omega)
    | 39, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_39 i (by omega)
    | 40, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_40 i (by omega)
    | 41, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_41 i (by omega)
    | 42, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_42 i (by omega)
    | 43, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_43 i (by omega)
    | 44, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_44 i (by omega)
    | 45, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_45 i (by omega)
    | 46, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_46 i (by omega)
    | 47, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_47 i (by omega)
    | 48, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_48 i (by omega)
    | 49, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_49 i (by omega)
    | 50, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_50 i (by omega)
    | 51, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_51 i (by omega)
    | 52, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_52 i (by omega)
    | 53, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_53 i (by omega)
    | 54, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_54 i (by omega)
    | 55, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_55 i (by omega)
    | 56, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_56 i (by omega)
    | 57, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_57 i (by omega)
    | 58, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_58 i (by omega)
    | 59, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_59 i (by omega)
    | 60, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_60 i (by omega)
    | 61, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_61 i (by omega)
    | 62, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_62 i (by omega)
    | 63, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_63 i (by omega)
    | 64, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_64 i (by omega)
    | 65, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_65 i (by omega)
    | 66, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_66 i (by omega)
    | 67, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_67 i (by omega)
    | 68, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_68 i (by omega)
    | 69, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_69 i (by omega)
    | 70, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_70 i (by omega)
    | 71, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_71 i (by omega)
    | 72, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_72 i (by omega)
    | 73, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_73 i (by omega)
    | 74, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_74 i (by omega)
    | 75, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_75 i (by omega)
    | 76, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_76 i (by omega)
    | 77, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_77 i (by omega)
    | 78, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_78 i (by omega)
    | 79, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_79 i (by omega)
    | 80, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_80 i (by omega)
    | 81, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_81 i (by omega)
    | 82, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_82 i (by omega)
    | 83, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_83 i (by omega)
    | 84, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_84 i (by omega)
    | 85, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_85 i (by omega)
    | 86, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_86 i (by omega)
    | 87, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_87 i (by omega)
    | 88, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_88 i (by omega)
    | 89, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_89 i (by omega)
    | 90, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_90 i (by omega)
    | 91, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_91 i (by omega)
    | 92, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_92 i (by omega)
    | 93, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_93 i (by omega)
    | 94, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_94 i (by omega)
    | 95, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_95 i (by omega)
    | 96, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_96 i (by omega)
    | 97, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_97 i (by omega)
    | 98, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_98 i (by omega)
    | 99, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_99 i (by omega)
    | 100, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_100 i (by omega)
    | 101, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_101 i (by omega)
    | 102, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_102 i (by omega)
    | 103, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_103 i (by omega)
    | 104, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_104 i (by omega)
    | 105, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_105 i (by omega)
    | 106, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_106 i (by omega)
    | 107, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_107 i (by omega)
    | 108, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_108 i (by omega)
    | 109, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_109 i (by omega)
    | 110, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_110 i (by omega)
    | 111, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_111 i (by omega)
    | 112, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_112 i (by omega)
    | 113, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_113 i (by omega)
    | 114, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_114 i (by omega)
    | 115, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_115 i (by omega)
    | 116, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_116 i (by omega)
    | 117, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_117 i (by omega)
    | 118, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_118 i (by omega)
    | 119, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_119 i (by omega)
    | 120, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_120 i (by omega)
    | 121, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_121 i (by omega)
    | 122, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_122 i (by omega)
    | 123, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_123 i (by omega)
    | 124, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_124 i (by omega)
    | 125, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_125 i (by omega)
    | 126, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_126 i (by omega)
    | 127, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_127 i (by omega)
    | 128, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_128 i (by omega)
    | 129, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_129 i (by omega)
    | 130, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_130 i (by omega)
    | 131, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_131 i (by omega)
    | 132, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_132 i (by omega)
    | 133, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_133 i (by omega)
    | 134, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_134 i (by omega)
    | 135, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_135 i (by omega)
    | 136, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_136 i (by omega)
    | 137, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_137 i (by omega)
    | 138, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_138 i (by omega)
    | 139, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_139 i (by omega)
    | 140, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_140 i (by omega)
    | 141, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_141 i (by omega)
    | 142, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_142 i (by omega)
    | 143, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_143 i (by omega)
    | 144, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_144 i (by omega)
    | 145, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_145 i (by omega)
    | 146, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_146 i (by omega)
    | 147, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_147 i (by omega)
    | 148, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_148 i (by omega)
    | 149, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_149 i (by omega)
    | 150, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_150 i (by omega)
    | 151, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_151 i (by omega)
    | 152, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_152 i (by omega)
    | 153, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_153 i (by omega)
    | 154, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_154 i (by omega)
    | 155, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_155 i (by omega)
    | 156, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_156 i (by omega)
    | 157, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_157 i (by omega)
    | 158, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_158 i (by omega)
    | 159, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_159 i (by omega)
    | 160, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_160 i (by omega)
    | 161, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_161 i (by omega)
    | 162, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_162 i (by omega)
    | 163, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_163 i (by omega)
    | 164, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_164 i (by omega)
    | 165, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_165 i (by omega)
    | 166, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_166 i (by omega)
    | 167, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_167 i (by omega)
    | 168, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_168 i (by omega)
    | 169, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_169 i (by omega)
    | 170, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_170 i (by omega)
    | 171, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_171 i (by omega)
    | 172, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_172 i (by omega)
    | 173, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_173 i (by omega)
    | 174, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_174 i (by omega)
    | 175, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_175 i (by omega)
    | 176, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_176 i (by omega)
    | 177, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_177 i (by omega)
    | 178, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_178 i (by omega)
    | 179, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_179 i (by omega)
    | 180, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_180 i (by omega)
    | 181, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_181 i (by omega)
    | 182, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_182 i (by omega)
    | 183, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_183 i (by omega)
    | 184, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_184 i (by omega)
    | 185, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_185 i (by omega)
    | 186, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_186 i (by omega)
    | 187, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_187 i (by omega)
    | 188, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_188 i (by omega)
    | 189, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_189 i (by omega)
    | 190, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_190 i (by omega)
    | 191, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_191 i (by omega)
    | 192, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_192 i (by omega)
    | 193, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_193 i (by omega)
    | 194, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_194 i (by omega)
    | 195, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_195 i (by omega)
    | 196, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_196 i (by omega)
    | 197, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_197 i (by omega)
    | 198, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_198 i (by omega)
    | 199, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_199 i (by omega)
    | 200, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_200 i (by omega)
    | 201, _ => exact fun i _ hlt => chkT_sound PK5616 _ _ _ _ TK5616_201 i (by omega)
    | c + 202, h => exact absurd h (by omega))

theorem hOK5616 : ∀ i < PK5616.orphs.length, ∀ a < 343, ∃ j, okO PK5616 (PK5616.orphs.getD i 0) a j = true := by
  intro i hi
  match i, hi with
  | 0, _ => exact chkO_sound PK5616 _ _ _ _ OK5616_0
  | 1, _ => exact chkO_sound PK5616 _ _ _ _ OK5616_1
  | 2, _ => exact chkO_sound PK5616 _ _ _ _ OK5616_2
  | i + 3, h => exact absurd h (by have : PK5616.orphs.length = 3 := rfl; omega)

theorem hBK5616 : ∀ s < PK5616.reps.length, ∀ m < 343, ∃ j, okB PK5616 s m j = true := by
  intro s hs
  match s, hs with
  | 0, _ => exact chkB_sound PK5616 _ _ _ _ BK5616_0
  | 1, _ => exact chkB_sound PK5616 _ _ _ _ BK5616_1
  | 2, _ => exact chkB_sound PK5616 _ _ _ _ BK5616_2
  | 3, _ => exact chkB_sound PK5616 _ _ _ _ BK5616_3
  | 4, _ => exact chkB_sound PK5616 _ _ _ _ BK5616_4
  | 5, _ => exact chkB_sound PK5616 _ _ _ _ BK5616_5
  | 6, _ => exact chkB_sound PK5616 _ _ _ _ BK5616_6
  | 7, _ => exact chkB_sound PK5616 _ _ _ _ BK5616_7
  | 8, _ => exact chkB_sound PK5616 _ _ _ _ BK5616_8
  | 9, _ => exact chkB_sound PK5616 _ _ _ _ BK5616_9
  | 10, _ => exact chkB_sound PK5616 _ _ _ _ BK5616_10
  | 11, _ => exact chkB_sound PK5616 _ _ _ _ BK5616_11
  | 12, _ => exact chkB_sound PK5616 _ _ _ _ BK5616_12
  | 13, _ => exact chkB_sound PK5616 _ _ _ _ BK5616_13
  | 14, _ => exact chkB_sound PK5616 _ _ _ _ BK5616_14
  | 15, _ => exact chkB_sound PK5616 _ _ _ _ BK5616_15
  | s + 16, h => exact absurd h (by have : PK5616.reps.length = 16 := rfl; omega)

/-- Não-vacuidade: o verificador recusa uma testemunha errada (ponto `t = 0`, palavra
`400` a distância 10 > 4). -/
example : okT PK5616 0 400 = false := by decide +kernel

/-- `K_7(10,4) ≤ 5616`: o código `LK5616` tem 5616 palavras e cobre com raio 4. -/
theorem K7_10_4_le_5616_syn :
    ∃ C : Finset (Fin 10 → ZMod 7), C.card = 5616 ∧ CoveringA2.Covers 4 C :=
  syn_cert PK5616 LK5616 rfl rfl rfl ⟨rfl, by decide⟩ VK5616 hTK5616 hOK5616 hBK5616
    (by decide +kernel) (by decide +kernel) (by decide +kernel)

end Syn

#print axioms Syn.K7_10_4_le_5616_syn
