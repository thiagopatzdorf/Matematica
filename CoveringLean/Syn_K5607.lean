-- gerado por scripts/syndrome/gen_syn.py; não editar à mão
import CoveringLean.SynBridge
import CoveringLean.SynLeaf_K5607_0
import CoveringLean.SynLeaf_K5607_1
import CoveringLean.SynLeaf_K5607_2
import CoveringLean.SynLeaf_K5607_3
import CoveringLean.SynLeaf_K5607_4
import CoveringLean.SynLeaf_K5607_5
import CoveringLean.SynLeaf_K5607_6
import CoveringLean.SynLeaf_K5607_7
import CoveringLean.SynLeaf_K5607_8
import CoveringLean.SynLeaf_K5607_9
import CoveringLean.SynLeaf_K5607_10
import CoveringLean.SynLeaf_K5607_11
import CoveringLean.SynLeaf_K5607_12
import CoveringLean.SynLeaf_K5607_13
import CoveringLean.SynLeaf_K5607_14
import CoveringLean.SynLeaf_K5607_15
import CoveringLean.SynLeaf_K5607_16
import CoveringLean.SynLeaf_K5607_17
import CoveringLean.SynLeaf_K5607_18
import CoveringLean.SynLeaf_K5607_19
import CoveringLean.SynLeaf_K5607_20
import CoveringLean.SynLeaf_K5607_21
import CoveringLean.SynLeaf_K5607_22
import CoveringLean.SynLeaf_K5607_23
import CoveringLean.SynLeaf_K5607_24
import CoveringLean.SynLeaf_K5607_25
import CoveringLean.SynLeaf_K5607_26
import CoveringLean.SynLeaf_K5607_27
import CoveringLean.SynLeaf_K5607_28
import CoveringLean.SynLeaf_K5607_29
import CoveringLean.SynLeaf_K5607_30
import CoveringLean.SynLeaf_K5607_31
import CoveringLean.SynLeaf_K5607_32
import CoveringLean.SynLeaf_K5607_33
import CoveringLean.SynLeaf_K5607_34
import CoveringLean.SynLeaf_K5607_35
import CoveringLean.SynLeaf_K5607_36
import CoveringLean.SynLeaf_K5607_37
import CoveringLean.SynLeaf_K5607_38
import CoveringLean.SynLeaf_K5607_39
import CoveringLean.SynLeaf_K5607_40
import CoveringLean.SynLeaf_K5607_41
import CoveringLean.SynLeaf_K5607_42
import CoveringLean.SynLeaf_K5607_43
import CoveringLean.SynLeaf_K5607_44
import CoveringLean.SynLeaf_K5607_45
import CoveringLean.SynLeaf_K5607_46
import CoveringLean.SynLeaf_K5607_47
import CoveringLean.SynLeaf_K5607_48
import CoveringLean.SynLeaf_K5607_49
import CoveringLean.SynLeaf_K5607_50
import CoveringLean.SynLeaf_K5607_51
import CoveringLean.SynLeaf_K5607_52
import CoveringLean.SynLeaf_K5607_53
import CoveringLean.SynLeaf_K5607_54
import CoveringLean.SynLeaf_K5607_55

/-! # K_7(10,4) ≤ 5607 pelo certificado por síndromes

Código: `Syn.LK5607` (sha256 canônico 7670a7bd3560fb6ba1ea6a68d7c6a6ec8853ab2d0406370cd2c80c0f12402fa5), união de 16 cosets completos de um
`[10,3]_7` (bloco de informação [0,3)) com 119 palavras de remendo;
3 síndromes órfãs (1029 pontos checados um a um).
-/

namespace Syn

set_option maxRecDepth 100000

theorem hTK5607 : ∀ t < 823543, ∃ w, okT PK5607 t w = true :=
  all_of_chunks (fun t => ∃ w, okT PK5607 t w = true) 4096 202 823543 (by norm_num) (by
    intro c hc
    match c, hc with
    | 0, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_0 i (by omega)
    | 1, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_1 i (by omega)
    | 2, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_2 i (by omega)
    | 3, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_3 i (by omega)
    | 4, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_4 i (by omega)
    | 5, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_5 i (by omega)
    | 6, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_6 i (by omega)
    | 7, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_7 i (by omega)
    | 8, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_8 i (by omega)
    | 9, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_9 i (by omega)
    | 10, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_10 i (by omega)
    | 11, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_11 i (by omega)
    | 12, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_12 i (by omega)
    | 13, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_13 i (by omega)
    | 14, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_14 i (by omega)
    | 15, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_15 i (by omega)
    | 16, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_16 i (by omega)
    | 17, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_17 i (by omega)
    | 18, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_18 i (by omega)
    | 19, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_19 i (by omega)
    | 20, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_20 i (by omega)
    | 21, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_21 i (by omega)
    | 22, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_22 i (by omega)
    | 23, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_23 i (by omega)
    | 24, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_24 i (by omega)
    | 25, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_25 i (by omega)
    | 26, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_26 i (by omega)
    | 27, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_27 i (by omega)
    | 28, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_28 i (by omega)
    | 29, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_29 i (by omega)
    | 30, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_30 i (by omega)
    | 31, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_31 i (by omega)
    | 32, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_32 i (by omega)
    | 33, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_33 i (by omega)
    | 34, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_34 i (by omega)
    | 35, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_35 i (by omega)
    | 36, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_36 i (by omega)
    | 37, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_37 i (by omega)
    | 38, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_38 i (by omega)
    | 39, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_39 i (by omega)
    | 40, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_40 i (by omega)
    | 41, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_41 i (by omega)
    | 42, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_42 i (by omega)
    | 43, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_43 i (by omega)
    | 44, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_44 i (by omega)
    | 45, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_45 i (by omega)
    | 46, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_46 i (by omega)
    | 47, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_47 i (by omega)
    | 48, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_48 i (by omega)
    | 49, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_49 i (by omega)
    | 50, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_50 i (by omega)
    | 51, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_51 i (by omega)
    | 52, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_52 i (by omega)
    | 53, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_53 i (by omega)
    | 54, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_54 i (by omega)
    | 55, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_55 i (by omega)
    | 56, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_56 i (by omega)
    | 57, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_57 i (by omega)
    | 58, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_58 i (by omega)
    | 59, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_59 i (by omega)
    | 60, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_60 i (by omega)
    | 61, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_61 i (by omega)
    | 62, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_62 i (by omega)
    | 63, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_63 i (by omega)
    | 64, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_64 i (by omega)
    | 65, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_65 i (by omega)
    | 66, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_66 i (by omega)
    | 67, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_67 i (by omega)
    | 68, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_68 i (by omega)
    | 69, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_69 i (by omega)
    | 70, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_70 i (by omega)
    | 71, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_71 i (by omega)
    | 72, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_72 i (by omega)
    | 73, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_73 i (by omega)
    | 74, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_74 i (by omega)
    | 75, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_75 i (by omega)
    | 76, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_76 i (by omega)
    | 77, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_77 i (by omega)
    | 78, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_78 i (by omega)
    | 79, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_79 i (by omega)
    | 80, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_80 i (by omega)
    | 81, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_81 i (by omega)
    | 82, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_82 i (by omega)
    | 83, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_83 i (by omega)
    | 84, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_84 i (by omega)
    | 85, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_85 i (by omega)
    | 86, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_86 i (by omega)
    | 87, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_87 i (by omega)
    | 88, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_88 i (by omega)
    | 89, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_89 i (by omega)
    | 90, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_90 i (by omega)
    | 91, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_91 i (by omega)
    | 92, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_92 i (by omega)
    | 93, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_93 i (by omega)
    | 94, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_94 i (by omega)
    | 95, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_95 i (by omega)
    | 96, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_96 i (by omega)
    | 97, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_97 i (by omega)
    | 98, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_98 i (by omega)
    | 99, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_99 i (by omega)
    | 100, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_100 i (by omega)
    | 101, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_101 i (by omega)
    | 102, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_102 i (by omega)
    | 103, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_103 i (by omega)
    | 104, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_104 i (by omega)
    | 105, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_105 i (by omega)
    | 106, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_106 i (by omega)
    | 107, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_107 i (by omega)
    | 108, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_108 i (by omega)
    | 109, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_109 i (by omega)
    | 110, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_110 i (by omega)
    | 111, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_111 i (by omega)
    | 112, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_112 i (by omega)
    | 113, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_113 i (by omega)
    | 114, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_114 i (by omega)
    | 115, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_115 i (by omega)
    | 116, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_116 i (by omega)
    | 117, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_117 i (by omega)
    | 118, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_118 i (by omega)
    | 119, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_119 i (by omega)
    | 120, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_120 i (by omega)
    | 121, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_121 i (by omega)
    | 122, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_122 i (by omega)
    | 123, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_123 i (by omega)
    | 124, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_124 i (by omega)
    | 125, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_125 i (by omega)
    | 126, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_126 i (by omega)
    | 127, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_127 i (by omega)
    | 128, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_128 i (by omega)
    | 129, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_129 i (by omega)
    | 130, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_130 i (by omega)
    | 131, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_131 i (by omega)
    | 132, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_132 i (by omega)
    | 133, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_133 i (by omega)
    | 134, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_134 i (by omega)
    | 135, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_135 i (by omega)
    | 136, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_136 i (by omega)
    | 137, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_137 i (by omega)
    | 138, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_138 i (by omega)
    | 139, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_139 i (by omega)
    | 140, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_140 i (by omega)
    | 141, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_141 i (by omega)
    | 142, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_142 i (by omega)
    | 143, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_143 i (by omega)
    | 144, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_144 i (by omega)
    | 145, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_145 i (by omega)
    | 146, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_146 i (by omega)
    | 147, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_147 i (by omega)
    | 148, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_148 i (by omega)
    | 149, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_149 i (by omega)
    | 150, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_150 i (by omega)
    | 151, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_151 i (by omega)
    | 152, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_152 i (by omega)
    | 153, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_153 i (by omega)
    | 154, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_154 i (by omega)
    | 155, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_155 i (by omega)
    | 156, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_156 i (by omega)
    | 157, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_157 i (by omega)
    | 158, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_158 i (by omega)
    | 159, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_159 i (by omega)
    | 160, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_160 i (by omega)
    | 161, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_161 i (by omega)
    | 162, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_162 i (by omega)
    | 163, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_163 i (by omega)
    | 164, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_164 i (by omega)
    | 165, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_165 i (by omega)
    | 166, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_166 i (by omega)
    | 167, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_167 i (by omega)
    | 168, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_168 i (by omega)
    | 169, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_169 i (by omega)
    | 170, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_170 i (by omega)
    | 171, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_171 i (by omega)
    | 172, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_172 i (by omega)
    | 173, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_173 i (by omega)
    | 174, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_174 i (by omega)
    | 175, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_175 i (by omega)
    | 176, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_176 i (by omega)
    | 177, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_177 i (by omega)
    | 178, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_178 i (by omega)
    | 179, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_179 i (by omega)
    | 180, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_180 i (by omega)
    | 181, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_181 i (by omega)
    | 182, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_182 i (by omega)
    | 183, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_183 i (by omega)
    | 184, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_184 i (by omega)
    | 185, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_185 i (by omega)
    | 186, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_186 i (by omega)
    | 187, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_187 i (by omega)
    | 188, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_188 i (by omega)
    | 189, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_189 i (by omega)
    | 190, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_190 i (by omega)
    | 191, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_191 i (by omega)
    | 192, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_192 i (by omega)
    | 193, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_193 i (by omega)
    | 194, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_194 i (by omega)
    | 195, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_195 i (by omega)
    | 196, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_196 i (by omega)
    | 197, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_197 i (by omega)
    | 198, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_198 i (by omega)
    | 199, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_199 i (by omega)
    | 200, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_200 i (by omega)
    | 201, _ => exact fun i _ hlt => chkT_sound PK5607 _ _ _ _ TK5607_201 i (by omega)
    | c + 202, h => exact absurd h (by omega))

theorem hOK5607 : ∀ i < PK5607.orphs.length, ∀ a < 343, ∃ j, okO PK5607 (PK5607.orphs.getD i 0) a j = true := by
  intro i hi
  match i, hi with
  | 0, _ => exact chkO_sound PK5607 _ _ _ _ OK5607_0
  | 1, _ => exact chkO_sound PK5607 _ _ _ _ OK5607_1
  | 2, _ => exact chkO_sound PK5607 _ _ _ _ OK5607_2
  | i + 3, h => exact absurd h (by have : PK5607.orphs.length = 3 := rfl; omega)

theorem hBK5607 : ∀ s < PK5607.reps.length, ∀ m < 343, ∃ j, okB PK5607 s m j = true := by
  intro s hs
  match s, hs with
  | 0, _ => exact chkB_sound PK5607 _ _ _ _ BK5607_0
  | 1, _ => exact chkB_sound PK5607 _ _ _ _ BK5607_1
  | 2, _ => exact chkB_sound PK5607 _ _ _ _ BK5607_2
  | 3, _ => exact chkB_sound PK5607 _ _ _ _ BK5607_3
  | 4, _ => exact chkB_sound PK5607 _ _ _ _ BK5607_4
  | 5, _ => exact chkB_sound PK5607 _ _ _ _ BK5607_5
  | 6, _ => exact chkB_sound PK5607 _ _ _ _ BK5607_6
  | 7, _ => exact chkB_sound PK5607 _ _ _ _ BK5607_7
  | 8, _ => exact chkB_sound PK5607 _ _ _ _ BK5607_8
  | 9, _ => exact chkB_sound PK5607 _ _ _ _ BK5607_9
  | 10, _ => exact chkB_sound PK5607 _ _ _ _ BK5607_10
  | 11, _ => exact chkB_sound PK5607 _ _ _ _ BK5607_11
  | 12, _ => exact chkB_sound PK5607 _ _ _ _ BK5607_12
  | 13, _ => exact chkB_sound PK5607 _ _ _ _ BK5607_13
  | 14, _ => exact chkB_sound PK5607 _ _ _ _ BK5607_14
  | 15, _ => exact chkB_sound PK5607 _ _ _ _ BK5607_15
  | s + 16, h => exact absurd h (by have : PK5607.reps.length = 16 := rfl; omega)

/-- Não-vacuidade: o verificador recusa uma testemunha errada (ponto `t = 0`, palavra
`400` a distância 10 > 4). -/
example : okT PK5607 0 400 = false := by decide +kernel

/-- `K_7(10,4) ≤ 5607`: o código `LK5607` tem 5607 palavras e cobre com raio 4. -/
theorem K7_10_4_le_5607_syn :
    ∃ C : Finset (Fin 10 → ZMod 7), C.card = 5607 ∧ CoveringA2.Covers 4 C :=
  syn_cert PK5607 LK5607 rfl rfl rfl ⟨rfl, by decide⟩ VK5607 hTK5607 hOK5607 hBK5607
    (by decide +kernel) (by decide +kernel) (by decide +kernel)

end Syn

#print axioms Syn.K7_10_4_le_5607_syn
