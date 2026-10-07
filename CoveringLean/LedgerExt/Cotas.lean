import CoveringLean.Ledger.Cotas
import CoveringLean.Literatura.Binarios
import CoveringLean.Literatura.KO05
import CoveringLean.Syn_K2_15_2_384
import CoveringLean.Syn_K2_18_3_512
import CoveringLean.Syn_K2_19_4_256
import CoveringLean.Syn_K2_19_6_32
import CoveringLean.Syn_K2_24_5_1024

/-!
# Cotas superiores do ledger a partir de teoremas de fora do lote (GERADO)

Gerado por `tools/certificar/gerar.py`; não edite à mão. Cada célula aqui é uma regra sobre pelo
menos um teorema do kernel que não sai do lote (`ledger/ours.json`: síndromes, Corolário 3 de
Kéri–Östergård, witnesses dos artigos...). Fica fora do `CoveringLedger` porque importa os
módulos dessas bases: `lake build CoveringLedgerExt`.
-/

namespace CoveringLedgerExt
open CoveringUB

-- teorema do kernel fora do lote (Syn.K2_15_2_le_384_syn)
theorem e3150 : UB 2 15 2 384 :=
  UB.of_exists Syn.K2_15_2_le_384_syn
-- teorema do kernel fora do lote (CoveringLit.K2_15_4_le_32)
theorem e3151 : UB 2 15 4 32 :=
  K_le_iff.mp CoveringLit.K2_15_4_le_32
-- teorema do kernel fora do lote (Syn.K2_18_3_le_512_syn)
theorem e3155 : UB 2 18 3 512 :=
  UB.of_exists Syn.K2_18_3_le_512_syn
-- teorema do kernel fora do lote (Syn.K2_19_4_le_256_syn)
theorem e3156 : UB 2 19 4 256 :=
  UB.of_exists Syn.K2_19_4_le_256_syn
-- teorema do kernel fora do lote (Syn.K2_19_6_le_32_syn)
theorem e3157 : UB 2 19 6 32 :=
  UB.of_exists Syn.K2_19_6_le_32_syn
-- teorema do kernel fora do lote (Syn.K2_24_5_le_1024_syn)
theorem e3160 : UB 2 24 5 1024 :=
  UB.of_exists Syn.K2_24_5_le_1024_syn
-- teorema do kernel fora do lote (CoveringLit.K8_5_2_le_128)
theorem e3175 : UB 8 5 2 128 :=
  K_le_iff.mp CoveringLit.K8_5_2_le_128
-- teorema do kernel fora do lote (CoveringLit.K9_5_2_le_189)
theorem e3180 : UB 9 5 2 189 :=
  K_le_iff.mp CoveringLit.K9_5_2_le_189
-- teorema do kernel fora do lote (CoveringLit.K9_7_4_le_120)
theorem e3181 : UB 9 7 4 120 :=
  K_le_iff.mp CoveringLit.K9_7_4_le_120
-- teorema do kernel fora do lote (CoveringLit.K10_5_2_le_250)
theorem e3185 : UB 10 5 2 250 :=
  K_le_iff.mp CoveringLit.K10_5_2_le_250
-- teorema do kernel fora do lote (CoveringLit.K13_4_2_le_57)
theorem e3195 : UB 13 4 2 57 :=
  K_le_iff.mp CoveringLit.K13_4_2_le_57
-- teorema do kernel fora do lote (CoveringLit.K14_4_2_le_66)
theorem e3198 : UB 14 4 2 66 :=
  K_le_iff.mp CoveringLit.K14_4_2_le_66
-- teorema do kernel fora do lote (CoveringLit.K15_4_2_le_75)
theorem e3204 : UB 15 4 2 75 :=
  K_le_iff.mp CoveringLit.K15_4_2_le_75
-- teorema do kernel fora do lote (CoveringLit.K16_4_2_le_87)
theorem e3210 : UB 16 4 2 87 :=
  K_le_iff.mp CoveringLit.K16_4_2_le_87
-- teorema do kernel fora do lote (CoveringLit.K16_5_3_le_64)
theorem e3212 : UB 16 5 3 64 :=
  K_le_iff.mp CoveringLit.K16_5_3_le_64
-- teorema do kernel fora do lote (CoveringLit.K17_4_2_le_99)
theorem e3216 : UB 17 4 2 99 :=
  K_le_iff.mp CoveringLit.K17_4_2_le_99
-- teorema do kernel fora do lote (CoveringLit.K17_5_2_le_1241)
theorem e3217 : UB 17 5 2 1241 :=
  K_le_iff.mp CoveringLit.K17_5_2_le_1241
-- teorema do kernel fora do lote (CoveringLit.K17_5_3_le_73)
theorem e3218 : UB 17 5 3 73 :=
  K_le_iff.mp CoveringLit.K17_5_3_le_73
-- teorema do kernel fora do lote (CoveringLit.K18_4_2_le_111)
theorem e3222 : UB 18 4 2 111 :=
  K_le_iff.mp CoveringLit.K18_4_2_le_111
-- teorema do kernel fora do lote (CoveringLit.K19_4_2_le_123)
theorem e3229 : UB 19 4 2 123 :=
  K_le_iff.mp CoveringLit.K19_4_2_le_123
-- teorema do kernel fora do lote (CoveringLit.K20_4_2_le_135)
theorem e3235 : UB 20 4 2 135 :=
  K_le_iff.mp CoveringLit.K20_4_2_le_135
-- teorema do kernel fora do lote (CoveringLit.K21_7_4_le_1029)
theorem e3244 : UB 21 7 4 1029 :=
  K_le_iff.mp CoveringLit.K21_7_4_le_1029
-- coordenada muda (t = 1) de K2(15,2) ≤ 384
theorem e3247 : UB 2 16 2 768 :=
  (UB.lengthen_dummy 1 e3150).weaken (by decide) (by decide) (by decide)
-- coordenada muda (t = 1) de K2(15,4) ≤ 32
theorem e3248 : UB 2 16 4 64 :=
  (UB.lengthen_dummy 1 e3151).weaken (by decide) (by decide) (by decide)
-- coordenada muda (t = 1) de K2(16,2) ≤ 768
theorem e3249 : UB 2 17 2 1536 :=
  (UB.lengthen_dummy 1 e3247).weaken (by decide) (by decide) (by decide)
-- coordenada muda (t = 1) de K2(18,3) ≤ 512
theorem e3250 : UB 2 19 3 1024 :=
  (UB.lengthen_dummy 1 e3155).weaken (by decide) (by decide) (by decide)
-- coordenada muda (t = 1) de K2(19,4) ≤ 256
theorem e3251 : UB 2 20 4 512 :=
  (UB.lengthen_dummy 1 e3156).weaken (by decide) (by decide) (by decide)
-- soma direta de K2(3,1) ≤ 2 e K2(19,6) ≤ 32
theorem e3253 : UB 2 22 7 64 :=
  (UB.direct_sum CoveringLedger.u10 e3157).weaken (by decide) (by decide) (by decide)
-- soma direta de K2(5,2) ≤ 2 e K2(19,6) ≤ 32
theorem e3255 : UB 2 24 8 64 :=
  (UB.direct_sum CoveringLedger.u26 e3157).weaken (by decide) (by decide) (by decide)
-- coordenada muda (t = 1) de K2(24,5) ≤ 1024
theorem e3256 : UB 2 25 5 2048 :=
  (UB.lengthen_dummy 1 e3160).weaken (by decide) (by decide) (by decide)
-- coordenada muda (t = 1) de K2(25,5) ≤ 2048
theorem e3258 : UB 2 26 5 4096 :=
  (UB.lengthen_dummy 1 e3256).weaken (by decide) (by decide) (by decide)
-- soma direta de K8(4,2) ≤ 23 e K8(5,2) ≤ 128
theorem e3287 : UB 8 9 4 2944 :=
  (UB.direct_sum CoveringLedger.u2418 e3175).weaken (by decide) (by decide) (by decide)
-- alongamento livre (t = 1) de K9(7,4) ≤ 120
theorem e3293 : UB 9 8 5 120 :=
  (UB.lengthen_free 1 e3181).weaken (by decide) (by decide) (by decide)
-- soma direta de K9(4,2) ≤ 27 e K9(5,2) ≤ 189
theorem e3294 : UB 9 9 4 5103 :=
  (UB.direct_sum CoveringLedger.u2420 e3180).weaken (by decide) (by decide) (by decide)
-- soma direta de K10(4,2) ≤ 34 e K10(5,2) ≤ 250
theorem e3303 : UB 10 9 4 8500 :=
  (UB.direct_sum CoveringLedger.u2380 e3185).weaken (by decide) (by decide) (by decide)
-- soma direta de K13(4,2) ≤ 57 e K13(4,2) ≤ 57
theorem e3318 : UB 13 8 4 3249 :=
  (UB.direct_sum e3195 e3195).weaken (by decide) (by decide) (by decide)
-- soma direta de K14(4,2) ≤ 66 e K14(4,2) ≤ 66
theorem e3324 : UB 14 8 4 4356 :=
  (UB.direct_sum e3198 e3198).weaken (by decide) (by decide) (by decide)
-- soma direta de K15(4,2) ≤ 75 e K15(4,2) ≤ 75
theorem e3330 : UB 15 8 4 5625 :=
  (UB.direct_sum e3204 e3204).weaken (by decide) (by decide) (by decide)
-- alongamento livre (t = 1) de K16(5,3) ≤ 64
theorem e3333 : UB 16 6 4 64 :=
  (UB.lengthen_free 1 e3212).weaken (by decide) (by decide) (by decide)
-- soma direta de K16(4,2) ≤ 87 e K16(4,2) ≤ 87
theorem e3336 : UB 16 8 4 7569 :=
  (UB.direct_sum e3210 e3210).weaken (by decide) (by decide) (by decide)
-- alongamento livre (t = 1) de K17(5,2) ≤ 1241
theorem e3338 : UB 17 6 3 1241 :=
  (UB.lengthen_free 1 e3217).weaken (by decide) (by decide) (by decide)
-- alongamento livre (t = 1) de K17(5,3) ≤ 73
theorem e3339 : UB 17 6 4 73 :=
  (UB.lengthen_free 1 e3218).weaken (by decide) (by decide) (by decide)
-- soma direta de K17(4,2) ≤ 99 e K17(4,2) ≤ 99
theorem e3342 : UB 17 8 4 9801 :=
  (UB.direct_sum e3216 e3216).weaken (by decide) (by decide) (by decide)
-- soma direta de K18(4,2) ≤ 111 e K18(4,2) ≤ 111
theorem e3347 : UB 18 8 4 12321 :=
  (UB.direct_sum e3222 e3222).weaken (by decide) (by decide) (by decide)
-- soma direta de K19(4,2) ≤ 123 e K19(4,2) ≤ 123
theorem e3356 : UB 19 8 4 15129 :=
  (UB.direct_sum e3229 e3229).weaken (by decide) (by decide) (by decide)
-- soma direta de K20(4,2) ≤ 135 e K20(4,2) ≤ 135
theorem e3365 : UB 20 8 4 18225 :=
  (UB.direct_sum e3235 e3235).weaken (by decide) (by decide) (by decide)
-- coordenada muda (t = 1) de K21(7,4) ≤ 1029
theorem e3374 : UB 21 8 4 21609 :=
  (UB.lengthen_dummy 1 e3244).weaken (by decide) (by decide) (by decide)
-- alongamento livre (t = 1) de K21(7,4) ≤ 1029
theorem e3375 : UB 21 8 5 1029 :=
  (UB.lengthen_free 1 e3244).weaken (by decide) (by decide) (by decide)

theorem K2_16_2_le_768 : K 2 16 2 ≤ 768 := K_le e3247
theorem K2_16_4_le_64 : K 2 16 4 ≤ 64 := K_le e3248
theorem K2_17_2_le_1536 : K 2 17 2 ≤ 1536 := K_le e3249
theorem K2_19_3_le_1024 : K 2 19 3 ≤ 1024 := K_le e3250
theorem K2_20_4_le_512 : K 2 20 4 ≤ 512 := K_le e3251
theorem K2_22_7_le_64 : K 2 22 7 ≤ 64 := K_le e3253
theorem K2_24_8_le_64 : K 2 24 8 ≤ 64 := K_le e3255
theorem K2_25_5_le_2048 : K 2 25 5 ≤ 2048 := K_le e3256
theorem K2_26_5_le_4096 : K 2 26 5 ≤ 4096 := K_le e3258
theorem K8_9_4_le_2944 : K 8 9 4 ≤ 2944 := K_le e3287
theorem K9_8_5_le_120 : K 9 8 5 ≤ 120 := K_le e3293
theorem K9_9_4_le_5103 : K 9 9 4 ≤ 5103 := K_le e3294
theorem K10_9_4_le_8500 : K 10 9 4 ≤ 8500 := K_le e3303
theorem K13_8_4_le_3249 : K 13 8 4 ≤ 3249 := K_le e3318
theorem K14_8_4_le_4356 : K 14 8 4 ≤ 4356 := K_le e3324
theorem K15_8_4_le_5625 : K 15 8 4 ≤ 5625 := K_le e3330
theorem K16_6_4_le_64 : K 16 6 4 ≤ 64 := K_le e3333
theorem K16_8_4_le_7569 : K 16 8 4 ≤ 7569 := K_le e3336
theorem K17_6_3_le_1241 : K 17 6 3 ≤ 1241 := K_le e3338
theorem K17_6_4_le_73 : K 17 6 4 ≤ 73 := K_le e3339
theorem K17_8_4_le_9801 : K 17 8 4 ≤ 9801 := K_le e3342
theorem K18_8_4_le_12321 : K 18 8 4 ≤ 12321 := K_le e3347
theorem K19_8_4_le_15129 : K 19 8 4 ≤ 15129 := K_le e3356
theorem K20_8_4_le_18225 : K 20 8 4 ≤ 18225 := K_le e3365
theorem K21_8_4_le_21609 : K 21 8 4 ≤ 21609 := K_le e3374
theorem K21_8_5_le_1029 : K 21 8 5 ≤ 1029 := K_le e3375

set_option maxRecDepth 100000 in
theorem todas_as_cotas :
    K 2 16 2 ≤ 768 ∧
    K 2 16 4 ≤ 64 ∧
    K 2 17 2 ≤ 1536 ∧
    K 2 19 3 ≤ 1024 ∧
    K 2 20 4 ≤ 512 ∧
    K 2 22 7 ≤ 64 ∧
    K 2 24 8 ≤ 64 ∧
    K 2 25 5 ≤ 2048 ∧
    K 2 26 5 ≤ 4096 ∧
    K 8 9 4 ≤ 2944 ∧
    K 9 8 5 ≤ 120 ∧
    K 9 9 4 ≤ 5103 ∧
    K 10 9 4 ≤ 8500 ∧
    K 13 8 4 ≤ 3249 ∧
    K 14 8 4 ≤ 4356 ∧
    K 15 8 4 ≤ 5625 ∧
    K 16 6 4 ≤ 64 ∧
    K 16 8 4 ≤ 7569 ∧
    K 17 6 3 ≤ 1241 ∧
    K 17 6 4 ≤ 73 ∧
    K 17 8 4 ≤ 9801 ∧
    K 18 8 4 ≤ 12321 ∧
    K 19 8 4 ≤ 15129 ∧
    K 20 8 4 ≤ 18225 ∧
    K 21 8 4 ≤ 21609 ∧
    K 21 8 5 ≤ 1029 :=
  ⟨CoveringLedgerExt.K2_16_2_le_768,
   CoveringLedgerExt.K2_16_4_le_64,
   CoveringLedgerExt.K2_17_2_le_1536,
   CoveringLedgerExt.K2_19_3_le_1024,
   CoveringLedgerExt.K2_20_4_le_512,
   CoveringLedgerExt.K2_22_7_le_64,
   CoveringLedgerExt.K2_24_8_le_64,
   CoveringLedgerExt.K2_25_5_le_2048,
   CoveringLedgerExt.K2_26_5_le_4096,
   CoveringLedgerExt.K8_9_4_le_2944,
   CoveringLedgerExt.K9_8_5_le_120,
   CoveringLedgerExt.K9_9_4_le_5103,
   CoveringLedgerExt.K10_9_4_le_8500,
   CoveringLedgerExt.K13_8_4_le_3249,
   CoveringLedgerExt.K14_8_4_le_4356,
   CoveringLedgerExt.K15_8_4_le_5625,
   CoveringLedgerExt.K16_6_4_le_64,
   CoveringLedgerExt.K16_8_4_le_7569,
   CoveringLedgerExt.K17_6_3_le_1241,
   CoveringLedgerExt.K17_6_4_le_73,
   CoveringLedgerExt.K17_8_4_le_9801,
   CoveringLedgerExt.K18_8_4_le_12321,
   CoveringLedgerExt.K19_8_4_le_15129,
   CoveringLedgerExt.K20_8_4_le_18225,
   CoveringLedgerExt.K21_8_4_le_21609,
   CoveringLedgerExt.K21_8_5_le_1029⟩

end CoveringLedgerExt

#print axioms CoveringLedgerExt.todas_as_cotas
