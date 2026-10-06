-- GERADO por tools/literatura/gerar_lean.py; não edite à mão.
import CoveringLean.Surjetivo
import CoveringLean.Literatura.Surj_t2_n10_v1_N1
import CoveringLean.Literatura.Surj_t2_n10_v2_N6
import CoveringLean.Literatura.Surj_t2_n4_v4_N16
import CoveringLean.Literatura.Surj_t2_n4_v5_N25
import CoveringLean.Literatura.Surj_t2_n4_v6_N37
import CoveringLean.Literatura.Surj_t2_n4_v7_N49
import CoveringLean.Literatura.Surj_t2_n5_v2_N6
import CoveringLean.Literatura.Surj_t2_n5_v3_N11
import CoveringLean.Literatura.Surj_t2_n5_v4_N16
import CoveringLean.Literatura.Surj_t2_n5_v5_N25
import CoveringLean.Literatura.Surj_t2_n5_v6_N39
import CoveringLean.Literatura.Surj_t2_n6_v1_N1
import CoveringLean.Literatura.Surj_t2_n6_v2_N6
import CoveringLean.Literatura.Surj_t2_n6_v3_N12
import CoveringLean.Literatura.Surj_t2_n6_v5_N25
import CoveringLean.Literatura.Surj_t2_n7_v1_N1
import CoveringLean.Literatura.Surj_t2_n7_v2_N6
import CoveringLean.Literatura.Surj_t2_n7_v3_N12
import CoveringLean.Literatura.Surj_t2_n7_v4_N21
import CoveringLean.Literatura.Surj_t2_n7_v5_N29
import CoveringLean.Literatura.Surj_t2_n8_v1_N1
import CoveringLean.Literatura.Surj_t2_n8_v2_N6
import CoveringLean.Literatura.Surj_t2_n8_v3_N13
import CoveringLean.Literatura.Surj_t2_n9_v1_N1
import CoveringLean.Literatura.Surj_t2_n9_v2_N6
import CoveringLean.Literatura.Surj_t3_n5_v3_N33
import CoveringLean.Literatura.Surj_t3_n5_v4_N64
import CoveringLean.Literatura.Surj_t3_n5_v5_N125
import CoveringLean.Literatura.Surj_t3_n5_v7_N343
import CoveringLean.Literatura.Surj_t3_n5_v8_N512
import CoveringLean.Literatura.Surj_t3_n5_v9_N729
import CoveringLean.Literatura.Surj_t3_n7_v2_N12
import CoveringLean.Literatura.Surj_t3_n7_v3_N40
import CoveringLean.Literatura.Surj_t3_n7_v7_N343
import CoveringLean.Literatura.Surj_t3_n9_v1_N1
import CoveringLean.Literatura.Surj_t3_n9_v2_N12
import CoveringLean.Literatura.Surj_t4_n10_v2_N24
import CoveringLean.Literatura.Surj_t4_n7_v11_N14641
import CoveringLean.Literatura.Surj_t4_n7_v7_N2401
import CoveringLean.Literatura.Surj_t4_n7_v8_N4096
import CoveringLean.Literatura.Surj_t4_n7_v9_N6561

/-! # Cotas da chave `n` (Corolário 3 de Kéri–Östergård 2005)

Gerzson Kéri, Patric R. J. Östergård, *Bounds for covering codes over large alphabets*, Designs, Codes and Cryptography 37 (2005) 45-60, DOI 10.1007/s10623-004-3804-8, Teorema 2 e Corolário 3 (pp. 54–55). Uma célula por teorema: a partição do alfabeto
e os ingredientes estão em `data/literatura/keri_ostergard_2005.json`; o código é
`CoveringSurj.codigo` e o raio vem de `CoveringSurj.cobre` (pombal). Reconferido fora do Lean por
`tools/literatura/codigos_papers.py` (exaustão dos ingredientes e força bruta onde q^n ≤ 3·10^6).
-/

namespace CoveringLit
open CoveringUB

/-- K_6(5,2) ≤ 66: blocos [3, 3]. -/
theorem ub_K6_5_2 : UB 6 5 2 66 :=
  CoveringSurj.ub (n := 5) (r := 3) [⟨0, 3, L_t3_n5_v3_N33, S_t3_n5_v3_N33⟩, ⟨3, 3, L_t3_n5_v3_N33, S_t3_n5_v3_N33⟩]
    (by decide) (by decide +kernel) (by decide) (by decide +kernel)

theorem K6_5_2_le_66 : K 6 5 2 ≤ 66 := K_le ub_K6_5_2

/-- K_6(6,4) ≤ 10: blocos [2, 1, 1, 1, 1]. -/
theorem ub_K6_6_4 : UB 6 6 4 10 :=
  CoveringSurj.ub (n := 6) (r := 2) [⟨0, 2, L_t2_n6_v2_N6, S_t2_n6_v2_N6⟩, ⟨2, 1, L_t2_n6_v1_N1, S_t2_n6_v1_N1⟩, ⟨3, 1, L_t2_n6_v1_N1, S_t2_n6_v1_N1⟩, ⟨4, 1, L_t2_n6_v1_N1, S_t2_n6_v1_N1⟩, ⟨5, 1, L_t2_n6_v1_N1, S_t2_n6_v1_N1⟩]
    (by decide) (by decide +kernel) (by decide) (by decide +kernel)

theorem K6_6_4_le_10 : K 6 6 4 ≤ 10 := K_le ub_K6_6_4

/-- K_6(7,4) ≤ 36: blocos [2, 2, 2]. -/
theorem ub_K6_7_4 : UB 6 7 4 36 :=
  CoveringSurj.ub (n := 7) (r := 3) [⟨0, 2, L_t3_n7_v2_N12, S_t3_n7_v2_N12⟩, ⟨2, 2, L_t3_n7_v2_N12, S_t3_n7_v2_N12⟩, ⟨4, 2, L_t3_n7_v2_N12, S_t3_n7_v2_N12⟩]
    (by decide) (by decide +kernel) (by decide) (by decide +kernel)

theorem K6_7_4_le_36 : K 6 7 4 ≤ 36 := K_le ub_K6_7_4

/-- K_6(10,6) ≤ 72: blocos [2, 2, 2]. -/
theorem ub_K6_10_6 : UB 6 10 6 72 :=
  CoveringSurj.ub (n := 10) (r := 4) [⟨0, 2, L_t4_n10_v2_N24, S_t4_n10_v2_N24⟩, ⟨2, 2, L_t4_n10_v2_N24, S_t4_n10_v2_N24⟩, ⟨4, 2, L_t4_n10_v2_N24, S_t4_n10_v2_N24⟩]
    (by decide) (by decide +kernel) (by decide) (by decide +kernel)

theorem K6_10_6_le_72 : K 6 10 6 ≤ 72 := K_le ub_K6_10_6

/-- K_7(5,2) ≤ 97: blocos [4, 3]. -/
theorem ub_K7_5_2 : UB 7 5 2 97 :=
  CoveringSurj.ub (n := 5) (r := 3) [⟨0, 4, L_t3_n5_v4_N64, S_t3_n5_v4_N64⟩, ⟨4, 3, L_t3_n5_v3_N33, S_t3_n5_v3_N33⟩]
    (by decide) (by decide +kernel) (by decide) (by decide +kernel)

theorem K7_5_2_le_97 : K 7 5 2 ≤ 97 := K_le ub_K7_5_2

/-- K_7(7,5) ≤ 11: blocos [2, 1, 1, 1, 1, 1]. -/
theorem ub_K7_7_5 : UB 7 7 5 11 :=
  CoveringSurj.ub (n := 7) (r := 2) [⟨0, 2, L_t2_n7_v2_N6, S_t2_n7_v2_N6⟩, ⟨2, 1, L_t2_n7_v1_N1, S_t2_n7_v1_N1⟩, ⟨3, 1, L_t2_n7_v1_N1, S_t2_n7_v1_N1⟩, ⟨4, 1, L_t2_n7_v1_N1, S_t2_n7_v1_N1⟩, ⟨5, 1, L_t2_n7_v1_N1, S_t2_n7_v1_N1⟩, ⟨6, 1, L_t2_n7_v1_N1, S_t2_n7_v1_N1⟩]
    (by decide) (by decide +kernel) (by decide) (by decide +kernel)

theorem K7_7_5_le_11 : K 7 7 5 ≤ 11 := K_le ub_K7_7_5

/-- K_7(9,6) ≤ 37: blocos [2, 2, 2, 1]. -/
theorem ub_K7_9_6 : UB 7 9 6 37 :=
  CoveringSurj.ub (n := 9) (r := 3) [⟨0, 2, L_t3_n9_v2_N12, S_t3_n9_v2_N12⟩, ⟨2, 2, L_t3_n9_v2_N12, S_t3_n9_v2_N12⟩, ⟨4, 2, L_t3_n9_v2_N12, S_t3_n9_v2_N12⟩, ⟨6, 1, L_t3_n9_v1_N1, S_t3_n9_v1_N1⟩]
    (by decide) (by decide +kernel) (by decide) (by decide +kernel)

theorem K7_9_6_le_37 : K 7 9 6 ≤ 37 := K_le ub_K7_9_6

/-- K_8(5,2) ≤ 128: blocos [4, 4]. -/
theorem ub_K8_5_2 : UB 8 5 2 128 :=
  CoveringSurj.ub (n := 5) (r := 3) [⟨0, 4, L_t3_n5_v4_N64, S_t3_n5_v4_N64⟩, ⟨4, 4, L_t3_n5_v4_N64, S_t3_n5_v4_N64⟩]
    (by decide) (by decide +kernel) (by decide) (by decide +kernel)

theorem K8_5_2_le_128 : K 8 5 2 ≤ 128 := K_le ub_K8_5_2

/-- K_8(7,4) ≤ 92: blocos [3, 3, 2]. -/
theorem ub_K8_7_4 : UB 8 7 4 92 :=
  CoveringSurj.ub (n := 7) (r := 3) [⟨0, 3, L_t3_n7_v3_N40, S_t3_n7_v3_N40⟩, ⟨3, 3, L_t3_n7_v3_N40, S_t3_n7_v3_N40⟩, ⟨6, 2, L_t3_n7_v2_N12, S_t3_n7_v2_N12⟩]
    (by decide) (by decide +kernel) (by decide) (by decide +kernel)

theorem K8_7_4_le_92 : K 8 7 4 ≤ 92 := K_le ub_K8_7_4

/-- K_8(7,5) ≤ 16: blocos [2, 2, 1, 1, 1, 1]. -/
theorem ub_K8_7_5 : UB 8 7 5 16 :=
  CoveringSurj.ub (n := 7) (r := 2) [⟨0, 2, L_t2_n7_v2_N6, S_t2_n7_v2_N6⟩, ⟨2, 2, L_t2_n7_v2_N6, S_t2_n7_v2_N6⟩, ⟨4, 1, L_t2_n7_v1_N1, S_t2_n7_v1_N1⟩, ⟨5, 1, L_t2_n7_v1_N1, S_t2_n7_v1_N1⟩, ⟨6, 1, L_t2_n7_v1_N1, S_t2_n7_v1_N1⟩, ⟨7, 1, L_t2_n7_v1_N1, S_t2_n7_v1_N1⟩]
    (by decide) (by decide +kernel) (by decide) (by decide +kernel)

theorem K8_7_5_le_16 : K 8 7 5 ≤ 16 := K_le ub_K8_7_5

/-- K_8(8,6) ≤ 12: blocos [2, 1, 1, 1, 1, 1, 1]. -/
theorem ub_K8_8_6 : UB 8 8 6 12 :=
  CoveringSurj.ub (n := 8) (r := 2) [⟨0, 2, L_t2_n8_v2_N6, S_t2_n8_v2_N6⟩, ⟨2, 1, L_t2_n8_v1_N1, S_t2_n8_v1_N1⟩, ⟨3, 1, L_t2_n8_v1_N1, S_t2_n8_v1_N1⟩, ⟨4, 1, L_t2_n8_v1_N1, S_t2_n8_v1_N1⟩, ⟨5, 1, L_t2_n8_v1_N1, S_t2_n8_v1_N1⟩, ⟨6, 1, L_t2_n8_v1_N1, S_t2_n8_v1_N1⟩, ⟨7, 1, L_t2_n8_v1_N1, S_t2_n8_v1_N1⟩]
    (by decide) (by decide +kernel) (by decide) (by decide +kernel)

theorem K8_8_6_le_12 : K 8 8 6 ≤ 12 := K_le ub_K8_8_6

/-- K_8(9,6) ≤ 48: blocos [2, 2, 2, 2]. -/
theorem ub_K8_9_6 : UB 8 9 6 48 :=
  CoveringSurj.ub (n := 9) (r := 3) [⟨0, 2, L_t3_n9_v2_N12, S_t3_n9_v2_N12⟩, ⟨2, 2, L_t3_n9_v2_N12, S_t3_n9_v2_N12⟩, ⟨4, 2, L_t3_n9_v2_N12, S_t3_n9_v2_N12⟩, ⟨6, 2, L_t3_n9_v2_N12, S_t3_n9_v2_N12⟩]
    (by decide) (by decide +kernel) (by decide) (by decide +kernel)

theorem K8_9_6_le_48 : K 8 9 6 ≤ 48 := K_le ub_K8_9_6

/-- K_9(5,2) ≤ 189: blocos [5, 4]. -/
theorem ub_K9_5_2 : UB 9 5 2 189 :=
  CoveringSurj.ub (n := 5) (r := 3) [⟨0, 5, L_t3_n5_v5_N125, S_t3_n5_v5_N125⟩, ⟨5, 4, L_t3_n5_v4_N64, S_t3_n5_v4_N64⟩]
    (by decide) (by decide +kernel) (by decide) (by decide +kernel)

theorem K9_5_2_le_189 : K 9 5 2 ≤ 189 := K_le ub_K9_5_2

/-- K_9(7,4) ≤ 120: blocos [3, 3, 3]. -/
theorem ub_K9_7_4 : UB 9 7 4 120 :=
  CoveringSurj.ub (n := 7) (r := 3) [⟨0, 3, L_t3_n7_v3_N40, S_t3_n7_v3_N40⟩, ⟨3, 3, L_t3_n7_v3_N40, S_t3_n7_v3_N40⟩, ⟨6, 3, L_t3_n7_v3_N40, S_t3_n7_v3_N40⟩]
    (by decide) (by decide +kernel) (by decide) (by decide +kernel)

theorem K9_7_4_le_120 : K 9 7 4 ≤ 120 := K_le ub_K9_7_4

/-- K_9(7,5) ≤ 21: blocos [2, 2, 2, 1, 1, 1]. -/
theorem ub_K9_7_5 : UB 9 7 5 21 :=
  CoveringSurj.ub (n := 7) (r := 2) [⟨0, 2, L_t2_n7_v2_N6, S_t2_n7_v2_N6⟩, ⟨2, 2, L_t2_n7_v2_N6, S_t2_n7_v2_N6⟩, ⟨4, 2, L_t2_n7_v2_N6, S_t2_n7_v2_N6⟩, ⟨6, 1, L_t2_n7_v1_N1, S_t2_n7_v1_N1⟩, ⟨7, 1, L_t2_n7_v1_N1, S_t2_n7_v1_N1⟩, ⟨8, 1, L_t2_n7_v1_N1, S_t2_n7_v1_N1⟩]
    (by decide) (by decide +kernel) (by decide) (by decide +kernel)

theorem K9_7_5_le_21 : K 9 7 5 ≤ 21 := K_le ub_K9_7_5

/-- K_9(8,6) ≤ 17: blocos [2, 2, 1, 1, 1, 1, 1]. -/
theorem ub_K9_8_6 : UB 9 8 6 17 :=
  CoveringSurj.ub (n := 8) (r := 2) [⟨0, 2, L_t2_n8_v2_N6, S_t2_n8_v2_N6⟩, ⟨2, 2, L_t2_n8_v2_N6, S_t2_n8_v2_N6⟩, ⟨4, 1, L_t2_n8_v1_N1, S_t2_n8_v1_N1⟩, ⟨5, 1, L_t2_n8_v1_N1, S_t2_n8_v1_N1⟩, ⟨6, 1, L_t2_n8_v1_N1, S_t2_n8_v1_N1⟩, ⟨7, 1, L_t2_n8_v1_N1, S_t2_n8_v1_N1⟩, ⟨8, 1, L_t2_n8_v1_N1, S_t2_n8_v1_N1⟩]
    (by decide) (by decide +kernel) (by decide) (by decide +kernel)

theorem K9_8_6_le_17 : K 9 8 6 ≤ 17 := K_le ub_K9_8_6

/-- K_9(9,7) ≤ 13: blocos [2, 1, 1, 1, 1, 1, 1, 1]. -/
theorem ub_K9_9_7 : UB 9 9 7 13 :=
  CoveringSurj.ub (n := 9) (r := 2) [⟨0, 2, L_t2_n9_v2_N6, S_t2_n9_v2_N6⟩, ⟨2, 1, L_t2_n9_v1_N1, S_t2_n9_v1_N1⟩, ⟨3, 1, L_t2_n9_v1_N1, S_t2_n9_v1_N1⟩, ⟨4, 1, L_t2_n9_v1_N1, S_t2_n9_v1_N1⟩, ⟨5, 1, L_t2_n9_v1_N1, S_t2_n9_v1_N1⟩, ⟨6, 1, L_t2_n9_v1_N1, S_t2_n9_v1_N1⟩, ⟨7, 1, L_t2_n9_v1_N1, S_t2_n9_v1_N1⟩, ⟨8, 1, L_t2_n9_v1_N1, S_t2_n9_v1_N1⟩]
    (by decide) (by decide +kernel) (by decide) (by decide +kernel)

theorem K9_9_7_le_13 : K 9 9 7 ≤ 13 := K_le ub_K9_9_7

/-- K_10(5,2) ≤ 250: blocos [5, 5]. -/
theorem ub_K10_5_2 : UB 10 5 2 250 :=
  CoveringSurj.ub (n := 5) (r := 3) [⟨0, 5, L_t3_n5_v5_N125, S_t3_n5_v5_N125⟩, ⟨5, 5, L_t3_n5_v5_N125, S_t3_n5_v5_N125⟩]
    (by decide) (by decide +kernel) (by decide) (by decide +kernel)

theorem K10_5_2_le_250 : K 10 5 2 ≤ 250 := K_le ub_K10_5_2

/-- K_10(7,5) ≤ 26: blocos [2, 2, 2, 2, 1, 1]. -/
theorem ub_K10_7_5 : UB 10 7 5 26 :=
  CoveringSurj.ub (n := 7) (r := 2) [⟨0, 2, L_t2_n7_v2_N6, S_t2_n7_v2_N6⟩, ⟨2, 2, L_t2_n7_v2_N6, S_t2_n7_v2_N6⟩, ⟨4, 2, L_t2_n7_v2_N6, S_t2_n7_v2_N6⟩, ⟨6, 2, L_t2_n7_v2_N6, S_t2_n7_v2_N6⟩, ⟨8, 1, L_t2_n7_v1_N1, S_t2_n7_v1_N1⟩, ⟨9, 1, L_t2_n7_v1_N1, S_t2_n7_v1_N1⟩]
    (by decide) (by decide +kernel) (by decide) (by decide +kernel)

theorem K10_7_5_le_26 : K 10 7 5 ≤ 26 := K_le ub_K10_7_5

/-- K_10(8,6) ≤ 22: blocos [2, 2, 2, 1, 1, 1, 1]. -/
theorem ub_K10_8_6 : UB 10 8 6 22 :=
  CoveringSurj.ub (n := 8) (r := 2) [⟨0, 2, L_t2_n8_v2_N6, S_t2_n8_v2_N6⟩, ⟨2, 2, L_t2_n8_v2_N6, S_t2_n8_v2_N6⟩, ⟨4, 2, L_t2_n8_v2_N6, S_t2_n8_v2_N6⟩, ⟨6, 1, L_t2_n8_v1_N1, S_t2_n8_v1_N1⟩, ⟨7, 1, L_t2_n8_v1_N1, S_t2_n8_v1_N1⟩, ⟨8, 1, L_t2_n8_v1_N1, S_t2_n8_v1_N1⟩, ⟨9, 1, L_t2_n8_v1_N1, S_t2_n8_v1_N1⟩]
    (by decide) (by decide +kernel) (by decide) (by decide +kernel)

theorem K10_8_6_le_22 : K 10 8 6 ≤ 22 := K_le ub_K10_8_6

/-- K_10(9,7) ≤ 18: blocos [2, 2, 1, 1, 1, 1, 1, 1]. -/
theorem ub_K10_9_7 : UB 10 9 7 18 :=
  CoveringSurj.ub (n := 9) (r := 2) [⟨0, 2, L_t2_n9_v2_N6, S_t2_n9_v2_N6⟩, ⟨2, 2, L_t2_n9_v2_N6, S_t2_n9_v2_N6⟩, ⟨4, 1, L_t2_n9_v1_N1, S_t2_n9_v1_N1⟩, ⟨5, 1, L_t2_n9_v1_N1, S_t2_n9_v1_N1⟩, ⟨6, 1, L_t2_n9_v1_N1, S_t2_n9_v1_N1⟩, ⟨7, 1, L_t2_n9_v1_N1, S_t2_n9_v1_N1⟩, ⟨8, 1, L_t2_n9_v1_N1, S_t2_n9_v1_N1⟩, ⟨9, 1, L_t2_n9_v1_N1, S_t2_n9_v1_N1⟩]
    (by decide) (by decide +kernel) (by decide) (by decide +kernel)

theorem K10_9_7_le_18 : K 10 9 7 ≤ 18 := K_le ub_K10_9_7

/-- K_10(10,8) ≤ 14: blocos [2, 1, 1, 1, 1, 1, 1, 1, 1]. -/
theorem ub_K10_10_8 : UB 10 10 8 14 :=
  CoveringSurj.ub (n := 10) (r := 2) [⟨0, 2, L_t2_n10_v2_N6, S_t2_n10_v2_N6⟩, ⟨2, 1, L_t2_n10_v1_N1, S_t2_n10_v1_N1⟩, ⟨3, 1, L_t2_n10_v1_N1, S_t2_n10_v1_N1⟩, ⟨4, 1, L_t2_n10_v1_N1, S_t2_n10_v1_N1⟩, ⟨5, 1, L_t2_n10_v1_N1, S_t2_n10_v1_N1⟩, ⟨6, 1, L_t2_n10_v1_N1, S_t2_n10_v1_N1⟩, ⟨7, 1, L_t2_n10_v1_N1, S_t2_n10_v1_N1⟩, ⟨8, 1, L_t2_n10_v1_N1, S_t2_n10_v1_N1⟩, ⟨9, 1, L_t2_n10_v1_N1, S_t2_n10_v1_N1⟩]
    (by decide) (by decide +kernel) (by decide) (by decide +kernel)

theorem K10_10_8_le_14 : K 10 10 8 ≤ 14 := K_le ub_K10_10_8

/-- K_11(7,5) ≤ 31: blocos [2, 2, 2, 2, 2, 1]. -/
theorem ub_K11_7_5 : UB 11 7 5 31 :=
  CoveringSurj.ub (n := 7) (r := 2) [⟨0, 2, L_t2_n7_v2_N6, S_t2_n7_v2_N6⟩, ⟨2, 2, L_t2_n7_v2_N6, S_t2_n7_v2_N6⟩, ⟨4, 2, L_t2_n7_v2_N6, S_t2_n7_v2_N6⟩, ⟨6, 2, L_t2_n7_v2_N6, S_t2_n7_v2_N6⟩, ⟨8, 2, L_t2_n7_v2_N6, S_t2_n7_v2_N6⟩, ⟨10, 1, L_t2_n7_v1_N1, S_t2_n7_v1_N1⟩]
    (by decide) (by decide +kernel) (by decide) (by decide +kernel)

theorem K11_7_5_le_31 : K 11 7 5 ≤ 31 := K_le ub_K11_7_5

/-- K_11(8,6) ≤ 27: blocos [2, 2, 2, 2, 1, 1, 1]. -/
theorem ub_K11_8_6 : UB 11 8 6 27 :=
  CoveringSurj.ub (n := 8) (r := 2) [⟨0, 2, L_t2_n8_v2_N6, S_t2_n8_v2_N6⟩, ⟨2, 2, L_t2_n8_v2_N6, S_t2_n8_v2_N6⟩, ⟨4, 2, L_t2_n8_v2_N6, S_t2_n8_v2_N6⟩, ⟨6, 2, L_t2_n8_v2_N6, S_t2_n8_v2_N6⟩, ⟨8, 1, L_t2_n8_v1_N1, S_t2_n8_v1_N1⟩, ⟨9, 1, L_t2_n8_v1_N1, S_t2_n8_v1_N1⟩, ⟨10, 1, L_t2_n8_v1_N1, S_t2_n8_v1_N1⟩]
    (by decide) (by decide +kernel) (by decide) (by decide +kernel)

theorem K11_8_6_le_27 : K 11 8 6 ≤ 27 := K_le ub_K11_8_6

/-- K_12(5,2) ≤ 468: blocos [7, 5]. -/
theorem ub_K12_5_2 : UB 12 5 2 468 :=
  CoveringSurj.ub (n := 5) (r := 3) [⟨0, 7, L_t3_n5_v7_N343, S_t3_n5_v7_N343⟩, ⟨7, 5, L_t3_n5_v5_N125, S_t3_n5_v5_N125⟩]
    (by decide) (by decide +kernel) (by decide) (by decide +kernel)

theorem K12_5_2_le_468 : K 12 5 2 ≤ 468 := K_le ub_K12_5_2

/-- K_12(7,5) ≤ 36: blocos [2, 2, 2, 2, 2, 2]. -/
theorem ub_K12_7_5 : UB 12 7 5 36 :=
  CoveringSurj.ub (n := 7) (r := 2) [⟨0, 2, L_t2_n7_v2_N6, S_t2_n7_v2_N6⟩, ⟨2, 2, L_t2_n7_v2_N6, S_t2_n7_v2_N6⟩, ⟨4, 2, L_t2_n7_v2_N6, S_t2_n7_v2_N6⟩, ⟨6, 2, L_t2_n7_v2_N6, S_t2_n7_v2_N6⟩, ⟨8, 2, L_t2_n7_v2_N6, S_t2_n7_v2_N6⟩, ⟨10, 2, L_t2_n7_v2_N6, S_t2_n7_v2_N6⟩]
    (by decide) (by decide +kernel) (by decide) (by decide +kernel)

theorem K12_7_5_le_36 : K 12 7 5 ≤ 36 := K_le ub_K12_7_5

/-- K_12(8,6) ≤ 32: blocos [2, 2, 2, 2, 2, 1, 1]. -/
theorem ub_K12_8_6 : UB 12 8 6 32 :=
  CoveringSurj.ub (n := 8) (r := 2) [⟨0, 2, L_t2_n8_v2_N6, S_t2_n8_v2_N6⟩, ⟨2, 2, L_t2_n8_v2_N6, S_t2_n8_v2_N6⟩, ⟨4, 2, L_t2_n8_v2_N6, S_t2_n8_v2_N6⟩, ⟨6, 2, L_t2_n8_v2_N6, S_t2_n8_v2_N6⟩, ⟨8, 2, L_t2_n8_v2_N6, S_t2_n8_v2_N6⟩, ⟨10, 1, L_t2_n8_v1_N1, S_t2_n8_v1_N1⟩, ⟨11, 1, L_t2_n8_v1_N1, S_t2_n8_v1_N1⟩]
    (by decide) (by decide +kernel) (by decide) (by decide +kernel)

theorem K12_8_6_le_32 : K 12 8 6 ≤ 32 := K_le ub_K12_8_6

/-- K_13(4,2) ≤ 57: blocos [5, 4, 4]. -/
theorem ub_K13_4_2 : UB 13 4 2 57 :=
  CoveringSurj.ub (n := 4) (r := 2) [⟨0, 5, L_t2_n4_v5_N25, S_t2_n4_v5_N25⟩, ⟨5, 4, L_t2_n4_v4_N16, S_t2_n4_v4_N16⟩, ⟨9, 4, L_t2_n4_v4_N16, S_t2_n4_v4_N16⟩]
    (by decide) (by decide +kernel) (by decide) (by decide +kernel)

theorem K13_4_2_le_57 : K 13 4 2 ≤ 57 := K_le ub_K13_4_2

/-- K_13(7,5) ≤ 42: blocos [3, 2, 2, 2, 2, 2]. -/
theorem ub_K13_7_5 : UB 13 7 5 42 :=
  CoveringSurj.ub (n := 7) (r := 2) [⟨0, 3, L_t2_n7_v3_N12, S_t2_n7_v3_N12⟩, ⟨3, 2, L_t2_n7_v2_N6, S_t2_n7_v2_N6⟩, ⟨5, 2, L_t2_n7_v2_N6, S_t2_n7_v2_N6⟩, ⟨7, 2, L_t2_n7_v2_N6, S_t2_n7_v2_N6⟩, ⟨9, 2, L_t2_n7_v2_N6, S_t2_n7_v2_N6⟩, ⟨11, 2, L_t2_n7_v2_N6, S_t2_n7_v2_N6⟩]
    (by decide) (by decide +kernel) (by decide) (by decide +kernel)

theorem K13_7_5_le_42 : K 13 7 5 ≤ 42 := K_le ub_K13_7_5

/-- K_13(8,6) ≤ 37: blocos [2, 2, 2, 2, 2, 2, 1]. -/
theorem ub_K13_8_6 : UB 13 8 6 37 :=
  CoveringSurj.ub (n := 8) (r := 2) [⟨0, 2, L_t2_n8_v2_N6, S_t2_n8_v2_N6⟩, ⟨2, 2, L_t2_n8_v2_N6, S_t2_n8_v2_N6⟩, ⟨4, 2, L_t2_n8_v2_N6, S_t2_n8_v2_N6⟩, ⟨6, 2, L_t2_n8_v2_N6, S_t2_n8_v2_N6⟩, ⟨8, 2, L_t2_n8_v2_N6, S_t2_n8_v2_N6⟩, ⟨10, 2, L_t2_n8_v2_N6, S_t2_n8_v2_N6⟩, ⟨12, 1, L_t2_n8_v1_N1, S_t2_n8_v1_N1⟩]
    (by decide) (by decide +kernel) (by decide) (by decide +kernel)

theorem K13_8_6_le_37 : K 13 8 6 ≤ 37 := K_le ub_K13_8_6

/-- K_14(4,2) ≤ 66: blocos [5, 5, 4]. -/
theorem ub_K14_4_2 : UB 14 4 2 66 :=
  CoveringSurj.ub (n := 4) (r := 2) [⟨0, 5, L_t2_n4_v5_N25, S_t2_n4_v5_N25⟩, ⟨5, 5, L_t2_n4_v5_N25, S_t2_n4_v5_N25⟩, ⟨10, 4, L_t2_n4_v4_N16, S_t2_n4_v4_N16⟩]
    (by decide) (by decide +kernel) (by decide) (by decide +kernel)

theorem K14_4_2_le_66 : K 14 4 2 ≤ 66 := K_le ub_K14_4_2

/-- K_14(5,2) ≤ 686: blocos [7, 7]. -/
theorem ub_K14_5_2 : UB 14 5 2 686 :=
  CoveringSurj.ub (n := 5) (r := 3) [⟨0, 7, L_t3_n5_v7_N343, S_t3_n5_v7_N343⟩, ⟨7, 7, L_t3_n5_v7_N343, S_t3_n5_v7_N343⟩]
    (by decide) (by decide +kernel) (by decide) (by decide +kernel)

theorem K14_5_2_le_686 : K 14 5 2 ≤ 686 := K_le ub_K14_5_2

/-- K_14(5,3) ≤ 54: blocos [4, 4, 4, 2]. -/
theorem ub_K14_5_3 : UB 14 5 3 54 :=
  CoveringSurj.ub (n := 5) (r := 2) [⟨0, 4, L_t2_n5_v4_N16, S_t2_n5_v4_N16⟩, ⟨4, 4, L_t2_n5_v4_N16, S_t2_n5_v4_N16⟩, ⟨8, 4, L_t2_n5_v4_N16, S_t2_n5_v4_N16⟩, ⟨12, 2, L_t2_n5_v2_N6, S_t2_n5_v2_N6⟩]
    (by decide) (by decide +kernel) (by decide) (by decide +kernel)

theorem K14_5_3_le_54 : K 14 5 3 ≤ 54 := K_le ub_K14_5_3

/-- K_14(7,3) ≤ 4802: blocos [7, 7]. -/
theorem ub_K14_7_3 : UB 14 7 3 4802 :=
  CoveringSurj.ub (n := 7) (r := 4) [⟨0, 7, L_t4_n7_v7_N2401, S_t4_n7_v7_N2401⟩, ⟨7, 7, L_t4_n7_v7_N2401, S_t4_n7_v7_N2401⟩]
    (by decide) (by decide +kernel) (by decide) (by decide +kernel)

theorem K14_7_3_le_4802 : K 14 7 3 ≤ 4802 := K_le ub_K14_7_3

/-- K_14(7,5) ≤ 48: blocos [3, 3, 2, 2, 2, 2]. -/
theorem ub_K14_7_5 : UB 14 7 5 48 :=
  CoveringSurj.ub (n := 7) (r := 2) [⟨0, 3, L_t2_n7_v3_N12, S_t2_n7_v3_N12⟩, ⟨3, 3, L_t2_n7_v3_N12, S_t2_n7_v3_N12⟩, ⟨6, 2, L_t2_n7_v2_N6, S_t2_n7_v2_N6⟩, ⟨8, 2, L_t2_n7_v2_N6, S_t2_n7_v2_N6⟩, ⟨10, 2, L_t2_n7_v2_N6, S_t2_n7_v2_N6⟩, ⟨12, 2, L_t2_n7_v2_N6, S_t2_n7_v2_N6⟩]
    (by decide) (by decide +kernel) (by decide) (by decide +kernel)

theorem K14_7_5_le_48 : K 14 7 5 ≤ 48 := K_le ub_K14_7_5

/-- K_14(8,6) ≤ 42: blocos [2, 2, 2, 2, 2, 2, 2]. -/
theorem ub_K14_8_6 : UB 14 8 6 42 :=
  CoveringSurj.ub (n := 8) (r := 2) [⟨0, 2, L_t2_n8_v2_N6, S_t2_n8_v2_N6⟩, ⟨2, 2, L_t2_n8_v2_N6, S_t2_n8_v2_N6⟩, ⟨4, 2, L_t2_n8_v2_N6, S_t2_n8_v2_N6⟩, ⟨6, 2, L_t2_n8_v2_N6, S_t2_n8_v2_N6⟩, ⟨8, 2, L_t2_n8_v2_N6, S_t2_n8_v2_N6⟩, ⟨10, 2, L_t2_n8_v2_N6, S_t2_n8_v2_N6⟩, ⟨12, 2, L_t2_n8_v2_N6, S_t2_n8_v2_N6⟩]
    (by decide) (by decide +kernel) (by decide) (by decide +kernel)

theorem K14_8_6_le_42 : K 14 8 6 ≤ 42 := K_le ub_K14_8_6

/-- K_15(4,2) ≤ 75: blocos [5, 5, 5]. -/
theorem ub_K15_4_2 : UB 15 4 2 75 :=
  CoveringSurj.ub (n := 4) (r := 2) [⟨0, 5, L_t2_n4_v5_N25, S_t2_n4_v5_N25⟩, ⟨5, 5, L_t2_n4_v5_N25, S_t2_n4_v5_N25⟩, ⟨10, 5, L_t2_n4_v5_N25, S_t2_n4_v5_N25⟩]
    (by decide) (by decide +kernel) (by decide) (by decide +kernel)

theorem K15_4_2_le_75 : K 15 4 2 ≤ 75 := K_le ub_K15_4_2

/-- K_15(5,2) ≤ 855: blocos [8, 7]. -/
theorem ub_K15_5_2 : UB 15 5 2 855 :=
  CoveringSurj.ub (n := 5) (r := 3) [⟨0, 8, L_t3_n5_v8_N512, S_t3_n5_v8_N512⟩, ⟨8, 7, L_t3_n5_v7_N343, S_t3_n5_v7_N343⟩]
    (by decide) (by decide +kernel) (by decide) (by decide +kernel)

theorem K15_5_2_le_855 : K 15 5 2 ≤ 855 := K_le ub_K15_5_2

/-- K_15(5,3) ≤ 59: blocos [4, 4, 4, 3]. -/
theorem ub_K15_5_3 : UB 15 5 3 59 :=
  CoveringSurj.ub (n := 5) (r := 2) [⟨0, 4, L_t2_n5_v4_N16, S_t2_n5_v4_N16⟩, ⟨4, 4, L_t2_n5_v4_N16, S_t2_n5_v4_N16⟩, ⟨8, 4, L_t2_n5_v4_N16, S_t2_n5_v4_N16⟩, ⟨12, 3, L_t2_n5_v3_N11, S_t2_n5_v3_N11⟩]
    (by decide) (by decide +kernel) (by decide) (by decide +kernel)

theorem K15_5_3_le_59 : K 15 5 3 ≤ 59 := K_le ub_K15_5_3

/-- K_15(7,3) ≤ 6497: blocos [8, 7]. -/
theorem ub_K15_7_3 : UB 15 7 3 6497 :=
  CoveringSurj.ub (n := 7) (r := 4) [⟨0, 8, L_t4_n7_v8_N4096, S_t4_n7_v8_N4096⟩, ⟨8, 7, L_t4_n7_v7_N2401, S_t4_n7_v7_N2401⟩]
    (by decide) (by decide +kernel) (by decide) (by decide +kernel)

theorem K15_7_3_le_6497 : K 15 7 3 ≤ 6497 := K_le ub_K15_7_3

/-- K_15(7,5) ≤ 54: blocos [3, 3, 3, 2, 2, 2]. -/
theorem ub_K15_7_5 : UB 15 7 5 54 :=
  CoveringSurj.ub (n := 7) (r := 2) [⟨0, 3, L_t2_n7_v3_N12, S_t2_n7_v3_N12⟩, ⟨3, 3, L_t2_n7_v3_N12, S_t2_n7_v3_N12⟩, ⟨6, 3, L_t2_n7_v3_N12, S_t2_n7_v3_N12⟩, ⟨9, 2, L_t2_n7_v2_N6, S_t2_n7_v2_N6⟩, ⟨11, 2, L_t2_n7_v2_N6, S_t2_n7_v2_N6⟩, ⟨13, 2, L_t2_n7_v2_N6, S_t2_n7_v2_N6⟩]
    (by decide) (by decide +kernel) (by decide) (by decide +kernel)

theorem K15_7_5_le_54 : K 15 7 5 ≤ 54 := K_le ub_K15_7_5

/-- K_15(8,6) ≤ 49: blocos [3, 2, 2, 2, 2, 2, 2]. -/
theorem ub_K15_8_6 : UB 15 8 6 49 :=
  CoveringSurj.ub (n := 8) (r := 2) [⟨0, 3, L_t2_n8_v3_N13, S_t2_n8_v3_N13⟩, ⟨3, 2, L_t2_n8_v2_N6, S_t2_n8_v2_N6⟩, ⟨5, 2, L_t2_n8_v2_N6, S_t2_n8_v2_N6⟩, ⟨7, 2, L_t2_n8_v2_N6, S_t2_n8_v2_N6⟩, ⟨9, 2, L_t2_n8_v2_N6, S_t2_n8_v2_N6⟩, ⟨11, 2, L_t2_n8_v2_N6, S_t2_n8_v2_N6⟩, ⟨13, 2, L_t2_n8_v2_N6, S_t2_n8_v2_N6⟩]
    (by decide) (by decide +kernel) (by decide) (by decide +kernel)

theorem K15_8_6_le_49 : K 15 8 6 ≤ 49 := K_le ub_K15_8_6

/-- K_16(4,2) ≤ 87: blocos [6, 5, 5]. -/
theorem ub_K16_4_2 : UB 16 4 2 87 :=
  CoveringSurj.ub (n := 4) (r := 2) [⟨0, 6, L_t2_n4_v6_N37, S_t2_n4_v6_N37⟩, ⟨6, 5, L_t2_n4_v5_N25, S_t2_n4_v5_N25⟩, ⟨11, 5, L_t2_n4_v5_N25, S_t2_n4_v5_N25⟩]
    (by decide) (by decide +kernel) (by decide) (by decide +kernel)

theorem K16_4_2_le_87 : K 16 4 2 ≤ 87 := K_le ub_K16_4_2

/-- K_16(5,2) ≤ 1024: blocos [8, 8]. -/
theorem ub_K16_5_2 : UB 16 5 2 1024 :=
  CoveringSurj.ub (n := 5) (r := 3) [⟨0, 8, L_t3_n5_v8_N512, S_t3_n5_v8_N512⟩, ⟨8, 8, L_t3_n5_v8_N512, S_t3_n5_v8_N512⟩]
    (by decide) (by decide +kernel) (by decide) (by decide +kernel)

theorem K16_5_2_le_1024 : K 16 5 2 ≤ 1024 := K_le ub_K16_5_2

/-- K_16(5,3) ≤ 64: blocos [4, 4, 4, 4]. -/
theorem ub_K16_5_3 : UB 16 5 3 64 :=
  CoveringSurj.ub (n := 5) (r := 2) [⟨0, 4, L_t2_n5_v4_N16, S_t2_n5_v4_N16⟩, ⟨4, 4, L_t2_n5_v4_N16, S_t2_n5_v4_N16⟩, ⟨8, 4, L_t2_n5_v4_N16, S_t2_n5_v4_N16⟩, ⟨12, 4, L_t2_n5_v4_N16, S_t2_n5_v4_N16⟩]
    (by decide) (by decide +kernel) (by decide) (by decide +kernel)

theorem K16_5_3_le_64 : K 16 5 3 ≤ 64 := K_le ub_K16_5_3

/-- K_16(7,3) ≤ 8192: blocos [8, 8]. -/
theorem ub_K16_7_3 : UB 16 7 3 8192 :=
  CoveringSurj.ub (n := 7) (r := 4) [⟨0, 8, L_t4_n7_v8_N4096, S_t4_n7_v8_N4096⟩, ⟨8, 8, L_t4_n7_v8_N4096, S_t4_n7_v8_N4096⟩]
    (by decide) (by decide +kernel) (by decide) (by decide +kernel)

theorem K16_7_3_le_8192 : K 16 7 3 ≤ 8192 := K_le ub_K16_7_3

/-- K_16(7,5) ≤ 60: blocos [3, 3, 3, 3, 2, 2]. -/
theorem ub_K16_7_5 : UB 16 7 5 60 :=
  CoveringSurj.ub (n := 7) (r := 2) [⟨0, 3, L_t2_n7_v3_N12, S_t2_n7_v3_N12⟩, ⟨3, 3, L_t2_n7_v3_N12, S_t2_n7_v3_N12⟩, ⟨6, 3, L_t2_n7_v3_N12, S_t2_n7_v3_N12⟩, ⟨9, 3, L_t2_n7_v3_N12, S_t2_n7_v3_N12⟩, ⟨12, 2, L_t2_n7_v2_N6, S_t2_n7_v2_N6⟩, ⟨14, 2, L_t2_n7_v2_N6, S_t2_n7_v2_N6⟩]
    (by decide) (by decide +kernel) (by decide) (by decide +kernel)

theorem K16_7_5_le_60 : K 16 7 5 ≤ 60 := K_le ub_K16_7_5

/-- K_16(8,6) ≤ 56: blocos [3, 3, 2, 2, 2, 2, 2]. -/
theorem ub_K16_8_6 : UB 16 8 6 56 :=
  CoveringSurj.ub (n := 8) (r := 2) [⟨0, 3, L_t2_n8_v3_N13, S_t2_n8_v3_N13⟩, ⟨3, 3, L_t2_n8_v3_N13, S_t2_n8_v3_N13⟩, ⟨6, 2, L_t2_n8_v2_N6, S_t2_n8_v2_N6⟩, ⟨8, 2, L_t2_n8_v2_N6, S_t2_n8_v2_N6⟩, ⟨10, 2, L_t2_n8_v2_N6, S_t2_n8_v2_N6⟩, ⟨12, 2, L_t2_n8_v2_N6, S_t2_n8_v2_N6⟩, ⟨14, 2, L_t2_n8_v2_N6, S_t2_n8_v2_N6⟩]
    (by decide) (by decide +kernel) (by decide) (by decide +kernel)

theorem K16_8_6_le_56 : K 16 8 6 ≤ 56 := K_le ub_K16_8_6

/-- K_17(4,2) ≤ 99: blocos [7, 5, 5]. -/
theorem ub_K17_4_2 : UB 17 4 2 99 :=
  CoveringSurj.ub (n := 4) (r := 2) [⟨0, 7, L_t2_n4_v7_N49, S_t2_n4_v7_N49⟩, ⟨7, 5, L_t2_n4_v5_N25, S_t2_n4_v5_N25⟩, ⟨12, 5, L_t2_n4_v5_N25, S_t2_n4_v5_N25⟩]
    (by decide) (by decide +kernel) (by decide) (by decide +kernel)

theorem K17_4_2_le_99 : K 17 4 2 ≤ 99 := K_le ub_K17_4_2

/-- K_17(5,2) ≤ 1241: blocos [9, 8]. -/
theorem ub_K17_5_2 : UB 17 5 2 1241 :=
  CoveringSurj.ub (n := 5) (r := 3) [⟨0, 9, L_t3_n5_v9_N729, S_t3_n5_v9_N729⟩, ⟨9, 8, L_t3_n5_v8_N512, S_t3_n5_v8_N512⟩]
    (by decide) (by decide +kernel) (by decide) (by decide +kernel)

theorem K17_5_2_le_1241 : K 17 5 2 ≤ 1241 := K_le ub_K17_5_2

/-- K_17(5,3) ≤ 73: blocos [5, 4, 4, 4]. -/
theorem ub_K17_5_3 : UB 17 5 3 73 :=
  CoveringSurj.ub (n := 5) (r := 2) [⟨0, 5, L_t2_n5_v5_N25, S_t2_n5_v5_N25⟩, ⟨5, 4, L_t2_n5_v4_N16, S_t2_n5_v4_N16⟩, ⟨9, 4, L_t2_n5_v4_N16, S_t2_n5_v4_N16⟩, ⟨13, 4, L_t2_n5_v4_N16, S_t2_n5_v4_N16⟩]
    (by decide) (by decide +kernel) (by decide) (by decide +kernel)

theorem K17_5_3_le_73 : K 17 5 3 ≤ 73 := K_le ub_K17_5_3

/-- K_17(7,3) ≤ 10657: blocos [9, 8]. -/
theorem ub_K17_7_3 : UB 17 7 3 10657 :=
  CoveringSurj.ub (n := 7) (r := 4) [⟨0, 9, L_t4_n7_v9_N6561, S_t4_n7_v9_N6561⟩, ⟨9, 8, L_t4_n7_v8_N4096, S_t4_n7_v8_N4096⟩]
    (by decide) (by decide +kernel) (by decide) (by decide +kernel)

theorem K17_7_3_le_10657 : K 17 7 3 ≤ 10657 := K_le ub_K17_7_3

/-- K_17(7,5) ≤ 66: blocos [3, 3, 3, 3, 3, 2]. -/
theorem ub_K17_7_5 : UB 17 7 5 66 :=
  CoveringSurj.ub (n := 7) (r := 2) [⟨0, 3, L_t2_n7_v3_N12, S_t2_n7_v3_N12⟩, ⟨3, 3, L_t2_n7_v3_N12, S_t2_n7_v3_N12⟩, ⟨6, 3, L_t2_n7_v3_N12, S_t2_n7_v3_N12⟩, ⟨9, 3, L_t2_n7_v3_N12, S_t2_n7_v3_N12⟩, ⟨12, 3, L_t2_n7_v3_N12, S_t2_n7_v3_N12⟩, ⟨15, 2, L_t2_n7_v2_N6, S_t2_n7_v2_N6⟩]
    (by decide) (by decide +kernel) (by decide) (by decide +kernel)

theorem K17_7_5_le_66 : K 17 7 5 ≤ 66 := K_le ub_K17_7_5

/-- K_17(8,6) ≤ 63: blocos [3, 3, 3, 2, 2, 2, 2]. -/
theorem ub_K17_8_6 : UB 17 8 6 63 :=
  CoveringSurj.ub (n := 8) (r := 2) [⟨0, 3, L_t2_n8_v3_N13, S_t2_n8_v3_N13⟩, ⟨3, 3, L_t2_n8_v3_N13, S_t2_n8_v3_N13⟩, ⟨6, 3, L_t2_n8_v3_N13, S_t2_n8_v3_N13⟩, ⟨9, 2, L_t2_n8_v2_N6, S_t2_n8_v2_N6⟩, ⟨11, 2, L_t2_n8_v2_N6, S_t2_n8_v2_N6⟩, ⟨13, 2, L_t2_n8_v2_N6, S_t2_n8_v2_N6⟩, ⟨15, 2, L_t2_n8_v2_N6, S_t2_n8_v2_N6⟩]
    (by decide) (by decide +kernel) (by decide) (by decide +kernel)

theorem K17_8_6_le_63 : K 17 8 6 ≤ 63 := K_le ub_K17_8_6

/-- K_18(4,2) ≤ 111: blocos [7, 6, 5]. -/
theorem ub_K18_4_2 : UB 18 4 2 111 :=
  CoveringSurj.ub (n := 4) (r := 2) [⟨0, 7, L_t2_n4_v7_N49, S_t2_n4_v7_N49⟩, ⟨7, 6, L_t2_n4_v6_N37, S_t2_n4_v6_N37⟩, ⟨13, 5, L_t2_n4_v5_N25, S_t2_n4_v5_N25⟩]
    (by decide) (by decide +kernel) (by decide) (by decide +kernel)

theorem K18_4_2_le_111 : K 18 4 2 ≤ 111 := K_le ub_K18_4_2

/-- K_18(5,2) ≤ 1458: blocos [9, 9]. -/
theorem ub_K18_5_2 : UB 18 5 2 1458 :=
  CoveringSurj.ub (n := 5) (r := 3) [⟨0, 9, L_t3_n5_v9_N729, S_t3_n5_v9_N729⟩, ⟨9, 9, L_t3_n5_v9_N729, S_t3_n5_v9_N729⟩]
    (by decide) (by decide +kernel) (by decide) (by decide +kernel)

theorem K18_5_2_le_1458 : K 18 5 2 ≤ 1458 := K_le ub_K18_5_2

/-- K_18(5,3) ≤ 82: blocos [5, 5, 4, 4]. -/
theorem ub_K18_5_3 : UB 18 5 3 82 :=
  CoveringSurj.ub (n := 5) (r := 2) [⟨0, 5, L_t2_n5_v5_N25, S_t2_n5_v5_N25⟩, ⟨5, 5, L_t2_n5_v5_N25, S_t2_n5_v5_N25⟩, ⟨10, 4, L_t2_n5_v4_N16, S_t2_n5_v4_N16⟩, ⟨14, 4, L_t2_n5_v4_N16, S_t2_n5_v4_N16⟩]
    (by decide) (by decide +kernel) (by decide) (by decide +kernel)

theorem K18_5_3_le_82 : K 18 5 3 ≤ 82 := K_le ub_K18_5_3

/-- K_18(6,4) ≤ 80: blocos [5, 5, 3, 3, 2]. -/
theorem ub_K18_6_4 : UB 18 6 4 80 :=
  CoveringSurj.ub (n := 6) (r := 2) [⟨0, 5, L_t2_n6_v5_N25, S_t2_n6_v5_N25⟩, ⟨5, 5, L_t2_n6_v5_N25, S_t2_n6_v5_N25⟩, ⟨10, 3, L_t2_n6_v3_N12, S_t2_n6_v3_N12⟩, ⟨13, 3, L_t2_n6_v3_N12, S_t2_n6_v3_N12⟩, ⟨16, 2, L_t2_n6_v2_N6, S_t2_n6_v2_N6⟩]
    (by decide) (by decide +kernel) (by decide) (by decide +kernel)

theorem K18_6_4_le_80 : K 18 6 4 ≤ 80 := K_le ub_K18_6_4

/-- K_18(7,3) ≤ 13122: blocos [9, 9]. -/
theorem ub_K18_7_3 : UB 18 7 3 13122 :=
  CoveringSurj.ub (n := 7) (r := 4) [⟨0, 9, L_t4_n7_v9_N6561, S_t4_n7_v9_N6561⟩, ⟨9, 9, L_t4_n7_v9_N6561, S_t4_n7_v9_N6561⟩]
    (by decide) (by decide +kernel) (by decide) (by decide +kernel)

theorem K18_7_3_le_13122 : K 18 7 3 ≤ 13122 := K_le ub_K18_7_3

/-- K_18(7,5) ≤ 72: blocos [3, 3, 3, 3, 3, 3]. -/
theorem ub_K18_7_5 : UB 18 7 5 72 :=
  CoveringSurj.ub (n := 7) (r := 2) [⟨0, 3, L_t2_n7_v3_N12, S_t2_n7_v3_N12⟩, ⟨3, 3, L_t2_n7_v3_N12, S_t2_n7_v3_N12⟩, ⟨6, 3, L_t2_n7_v3_N12, S_t2_n7_v3_N12⟩, ⟨9, 3, L_t2_n7_v3_N12, S_t2_n7_v3_N12⟩, ⟨12, 3, L_t2_n7_v3_N12, S_t2_n7_v3_N12⟩, ⟨15, 3, L_t2_n7_v3_N12, S_t2_n7_v3_N12⟩]
    (by decide) (by decide +kernel) (by decide) (by decide +kernel)

theorem K18_7_5_le_72 : K 18 7 5 ≤ 72 := K_le ub_K18_7_5

/-- K_18(8,6) ≤ 70: blocos [3, 3, 3, 3, 2, 2, 2]. -/
theorem ub_K18_8_6 : UB 18 8 6 70 :=
  CoveringSurj.ub (n := 8) (r := 2) [⟨0, 3, L_t2_n8_v3_N13, S_t2_n8_v3_N13⟩, ⟨3, 3, L_t2_n8_v3_N13, S_t2_n8_v3_N13⟩, ⟨6, 3, L_t2_n8_v3_N13, S_t2_n8_v3_N13⟩, ⟨9, 3, L_t2_n8_v3_N13, S_t2_n8_v3_N13⟩, ⟨12, 2, L_t2_n8_v2_N6, S_t2_n8_v2_N6⟩, ⟨14, 2, L_t2_n8_v2_N6, S_t2_n8_v2_N6⟩, ⟨16, 2, L_t2_n8_v2_N6, S_t2_n8_v2_N6⟩]
    (by decide) (by decide +kernel) (by decide) (by decide +kernel)

theorem K18_8_6_le_70 : K 18 8 6 ≤ 70 := K_le ub_K18_8_6

/-- K_19(4,2) ≤ 123: blocos [7, 7, 5]. -/
theorem ub_K19_4_2 : UB 19 4 2 123 :=
  CoveringSurj.ub (n := 4) (r := 2) [⟨0, 7, L_t2_n4_v7_N49, S_t2_n4_v7_N49⟩, ⟨7, 7, L_t2_n4_v7_N49, S_t2_n4_v7_N49⟩, ⟨14, 5, L_t2_n4_v5_N25, S_t2_n4_v5_N25⟩]
    (by decide) (by decide +kernel) (by decide) (by decide +kernel)

theorem K19_4_2_le_123 : K 19 4 2 ≤ 123 := K_le ub_K19_4_2

/-- K_19(5,3) ≤ 91: blocos [5, 5, 5, 4]. -/
theorem ub_K19_5_3 : UB 19 5 3 91 :=
  CoveringSurj.ub (n := 5) (r := 2) [⟨0, 5, L_t2_n5_v5_N25, S_t2_n5_v5_N25⟩, ⟨5, 5, L_t2_n5_v5_N25, S_t2_n5_v5_N25⟩, ⟨10, 5, L_t2_n5_v5_N25, S_t2_n5_v5_N25⟩, ⟨15, 4, L_t2_n5_v4_N16, S_t2_n5_v4_N16⟩]
    (by decide) (by decide +kernel) (by decide) (by decide +kernel)

theorem K19_5_3_le_91 : K 19 5 3 ≤ 91 := K_le ub_K19_5_3

/-- K_19(6,4) ≤ 86: blocos [5, 5, 3, 3, 3]. -/
theorem ub_K19_6_4 : UB 19 6 4 86 :=
  CoveringSurj.ub (n := 6) (r := 2) [⟨0, 5, L_t2_n6_v5_N25, S_t2_n6_v5_N25⟩, ⟨5, 5, L_t2_n6_v5_N25, S_t2_n6_v5_N25⟩, ⟨10, 3, L_t2_n6_v3_N12, S_t2_n6_v3_N12⟩, ⟨13, 3, L_t2_n6_v3_N12, S_t2_n6_v3_N12⟩, ⟨16, 3, L_t2_n6_v3_N12, S_t2_n6_v3_N12⟩]
    (by decide) (by decide +kernel) (by decide) (by decide +kernel)

theorem K19_6_4_le_86 : K 19 6 4 ≤ 86 := K_le ub_K19_6_4

/-- K_19(7,3) ≤ 18737: blocos [11, 8]. -/
theorem ub_K19_7_3 : UB 19 7 3 18737 :=
  CoveringSurj.ub (n := 7) (r := 4) [⟨0, 11, L_t4_n7_v11_N14641, S_t4_n7_v11_N14641⟩, ⟨11, 8, L_t4_n7_v8_N4096, S_t4_n7_v8_N4096⟩]
    (by decide) (by decide +kernel) (by decide) (by decide +kernel)

theorem K19_7_3_le_18737 : K 19 7 3 ≤ 18737 := K_le ub_K19_7_3

/-- K_19(7,5) ≤ 81: blocos [4, 3, 3, 3, 3, 3]. -/
theorem ub_K19_7_5 : UB 19 7 5 81 :=
  CoveringSurj.ub (n := 7) (r := 2) [⟨0, 4, L_t2_n7_v4_N21, S_t2_n7_v4_N21⟩, ⟨4, 3, L_t2_n7_v3_N12, S_t2_n7_v3_N12⟩, ⟨7, 3, L_t2_n7_v3_N12, S_t2_n7_v3_N12⟩, ⟨10, 3, L_t2_n7_v3_N12, S_t2_n7_v3_N12⟩, ⟨13, 3, L_t2_n7_v3_N12, S_t2_n7_v3_N12⟩, ⟨16, 3, L_t2_n7_v3_N12, S_t2_n7_v3_N12⟩]
    (by decide) (by decide +kernel) (by decide) (by decide +kernel)

theorem K19_7_5_le_81 : K 19 7 5 ≤ 81 := K_le ub_K19_7_5

/-- K_19(8,6) ≤ 77: blocos [3, 3, 3, 3, 3, 2, 2]. -/
theorem ub_K19_8_6 : UB 19 8 6 77 :=
  CoveringSurj.ub (n := 8) (r := 2) [⟨0, 3, L_t2_n8_v3_N13, S_t2_n8_v3_N13⟩, ⟨3, 3, L_t2_n8_v3_N13, S_t2_n8_v3_N13⟩, ⟨6, 3, L_t2_n8_v3_N13, S_t2_n8_v3_N13⟩, ⟨9, 3, L_t2_n8_v3_N13, S_t2_n8_v3_N13⟩, ⟨12, 3, L_t2_n8_v3_N13, S_t2_n8_v3_N13⟩, ⟨15, 2, L_t2_n8_v2_N6, S_t2_n8_v2_N6⟩, ⟨17, 2, L_t2_n8_v2_N6, S_t2_n8_v2_N6⟩]
    (by decide) (by decide +kernel) (by decide) (by decide +kernel)

theorem K19_8_6_le_77 : K 19 8 6 ≤ 77 := K_le ub_K19_8_6

/-- K_20(4,2) ≤ 135: blocos [7, 7, 6]. -/
theorem ub_K20_4_2 : UB 20 4 2 135 :=
  CoveringSurj.ub (n := 4) (r := 2) [⟨0, 7, L_t2_n4_v7_N49, S_t2_n4_v7_N49⟩, ⟨7, 7, L_t2_n4_v7_N49, S_t2_n4_v7_N49⟩, ⟨14, 6, L_t2_n4_v6_N37, S_t2_n4_v6_N37⟩]
    (by decide) (by decide +kernel) (by decide) (by decide +kernel)

theorem K20_4_2_le_135 : K 20 4 2 ≤ 135 := K_le ub_K20_4_2

/-- K_20(5,3) ≤ 100: blocos [5, 5, 5, 5]. -/
theorem ub_K20_5_3 : UB 20 5 3 100 :=
  CoveringSurj.ub (n := 5) (r := 2) [⟨0, 5, L_t2_n5_v5_N25, S_t2_n5_v5_N25⟩, ⟨5, 5, L_t2_n5_v5_N25, S_t2_n5_v5_N25⟩, ⟨10, 5, L_t2_n5_v5_N25, S_t2_n5_v5_N25⟩, ⟨15, 5, L_t2_n5_v5_N25, S_t2_n5_v5_N25⟩]
    (by decide) (by decide +kernel) (by decide) (by decide +kernel)

theorem K20_5_3_le_100 : K 20 5 3 ≤ 100 := K_le ub_K20_5_3

/-- K_20(6,4) ≤ 93: blocos [5, 5, 5, 3, 2]. -/
theorem ub_K20_6_4 : UB 20 6 4 93 :=
  CoveringSurj.ub (n := 6) (r := 2) [⟨0, 5, L_t2_n6_v5_N25, S_t2_n6_v5_N25⟩, ⟨5, 5, L_t2_n6_v5_N25, S_t2_n6_v5_N25⟩, ⟨10, 5, L_t2_n6_v5_N25, S_t2_n6_v5_N25⟩, ⟨15, 3, L_t2_n6_v3_N12, S_t2_n6_v3_N12⟩, ⟨18, 2, L_t2_n6_v2_N6, S_t2_n6_v2_N6⟩]
    (by decide) (by decide +kernel) (by decide) (by decide +kernel)

theorem K20_6_4_le_93 : K 20 6 4 ≤ 93 := K_le ub_K20_6_4

/-- K_20(7,3) ≤ 21202: blocos [11, 9]. -/
theorem ub_K20_7_3 : UB 20 7 3 21202 :=
  CoveringSurj.ub (n := 7) (r := 4) [⟨0, 11, L_t4_n7_v11_N14641, S_t4_n7_v11_N14641⟩, ⟨11, 9, L_t4_n7_v9_N6561, S_t4_n7_v9_N6561⟩]
    (by decide) (by decide +kernel) (by decide) (by decide +kernel)

theorem K20_7_3_le_21202 : K 20 7 3 ≤ 21202 := K_le ub_K20_7_3

/-- K_20(7,5) ≤ 89: blocos [5, 3, 3, 3, 3, 3]. -/
theorem ub_K20_7_5 : UB 20 7 5 89 :=
  CoveringSurj.ub (n := 7) (r := 2) [⟨0, 5, L_t2_n7_v5_N29, S_t2_n7_v5_N29⟩, ⟨5, 3, L_t2_n7_v3_N12, S_t2_n7_v3_N12⟩, ⟨8, 3, L_t2_n7_v3_N12, S_t2_n7_v3_N12⟩, ⟨11, 3, L_t2_n7_v3_N12, S_t2_n7_v3_N12⟩, ⟨14, 3, L_t2_n7_v3_N12, S_t2_n7_v3_N12⟩, ⟨17, 3, L_t2_n7_v3_N12, S_t2_n7_v3_N12⟩]
    (by decide) (by decide +kernel) (by decide) (by decide +kernel)

theorem K20_7_5_le_89 : K 20 7 5 ≤ 89 := K_le ub_K20_7_5

/-- K_20(8,6) ≤ 84: blocos [3, 3, 3, 3, 3, 3, 2]. -/
theorem ub_K20_8_6 : UB 20 8 6 84 :=
  CoveringSurj.ub (n := 8) (r := 2) [⟨0, 3, L_t2_n8_v3_N13, S_t2_n8_v3_N13⟩, ⟨3, 3, L_t2_n8_v3_N13, S_t2_n8_v3_N13⟩, ⟨6, 3, L_t2_n8_v3_N13, S_t2_n8_v3_N13⟩, ⟨9, 3, L_t2_n8_v3_N13, S_t2_n8_v3_N13⟩, ⟨12, 3, L_t2_n8_v3_N13, S_t2_n8_v3_N13⟩, ⟨15, 3, L_t2_n8_v3_N13, S_t2_n8_v3_N13⟩, ⟨18, 2, L_t2_n8_v2_N6, S_t2_n8_v2_N6⟩]
    (by decide) (by decide +kernel) (by decide) (by decide +kernel)

theorem K20_8_6_le_84 : K 20 8 6 ≤ 84 := K_le ub_K20_8_6

/-- K_21(4,2) ≤ 147: blocos [7, 7, 7]. -/
theorem ub_K21_4_2 : UB 21 4 2 147 :=
  CoveringSurj.ub (n := 4) (r := 2) [⟨0, 7, L_t2_n4_v7_N49, S_t2_n4_v7_N49⟩, ⟨7, 7, L_t2_n4_v7_N49, S_t2_n4_v7_N49⟩, ⟨14, 7, L_t2_n4_v7_N49, S_t2_n4_v7_N49⟩]
    (by decide) (by decide +kernel) (by decide) (by decide +kernel)

theorem K21_4_2_le_147 : K 21 4 2 ≤ 147 := K_le ub_K21_4_2

/-- K_21(5,3) ≤ 114: blocos [6, 5, 5, 5]. -/
theorem ub_K21_5_3 : UB 21 5 3 114 :=
  CoveringSurj.ub (n := 5) (r := 2) [⟨0, 6, L_t2_n5_v6_N39, S_t2_n5_v6_N39⟩, ⟨6, 5, L_t2_n5_v5_N25, S_t2_n5_v5_N25⟩, ⟨11, 5, L_t2_n5_v5_N25, S_t2_n5_v5_N25⟩, ⟨16, 5, L_t2_n5_v5_N25, S_t2_n5_v5_N25⟩]
    (by decide) (by decide +kernel) (by decide) (by decide +kernel)

theorem K21_5_3_le_114 : K 21 5 3 ≤ 114 := K_le ub_K21_5_3

/-- K_21(6,4) ≤ 99: blocos [5, 5, 5, 3, 3]. -/
theorem ub_K21_6_4 : UB 21 6 4 99 :=
  CoveringSurj.ub (n := 6) (r := 2) [⟨0, 5, L_t2_n6_v5_N25, S_t2_n6_v5_N25⟩, ⟨5, 5, L_t2_n6_v5_N25, S_t2_n6_v5_N25⟩, ⟨10, 5, L_t2_n6_v5_N25, S_t2_n6_v5_N25⟩, ⟨15, 3, L_t2_n6_v3_N12, S_t2_n6_v3_N12⟩, ⟨18, 3, L_t2_n6_v3_N12, S_t2_n6_v3_N12⟩]
    (by decide) (by decide +kernel) (by decide) (by decide +kernel)

theorem K21_6_4_le_99 : K 21 6 4 ≤ 99 := K_le ub_K21_6_4

/-- K_21(7,4) ≤ 1029: blocos [7, 7, 7]. -/
theorem ub_K21_7_4 : UB 21 7 4 1029 :=
  CoveringSurj.ub (n := 7) (r := 3) [⟨0, 7, L_t3_n7_v7_N343, S_t3_n7_v7_N343⟩, ⟨7, 7, L_t3_n7_v7_N343, S_t3_n7_v7_N343⟩, ⟨14, 7, L_t3_n7_v7_N343, S_t3_n7_v7_N343⟩]
    (by decide) (by decide +kernel) (by decide) (by decide +kernel)

theorem K21_7_4_le_1029 : K 21 7 4 ≤ 1029 := K_le ub_K21_7_4

/-- K_21(7,5) ≤ 98: blocos [5, 4, 3, 3, 3, 3]. -/
theorem ub_K21_7_5 : UB 21 7 5 98 :=
  CoveringSurj.ub (n := 7) (r := 2) [⟨0, 5, L_t2_n7_v5_N29, S_t2_n7_v5_N29⟩, ⟨5, 4, L_t2_n7_v4_N21, S_t2_n7_v4_N21⟩, ⟨9, 3, L_t2_n7_v3_N12, S_t2_n7_v3_N12⟩, ⟨12, 3, L_t2_n7_v3_N12, S_t2_n7_v3_N12⟩, ⟨15, 3, L_t2_n7_v3_N12, S_t2_n7_v3_N12⟩, ⟨18, 3, L_t2_n7_v3_N12, S_t2_n7_v3_N12⟩]
    (by decide) (by decide +kernel) (by decide) (by decide +kernel)

theorem K21_7_5_le_98 : K 21 7 5 ≤ 98 := K_le ub_K21_7_5

/-- K_21(8,6) ≤ 91: blocos [3, 3, 3, 3, 3, 3, 3]. -/
theorem ub_K21_8_6 : UB 21 8 6 91 :=
  CoveringSurj.ub (n := 8) (r := 2) [⟨0, 3, L_t2_n8_v3_N13, S_t2_n8_v3_N13⟩, ⟨3, 3, L_t2_n8_v3_N13, S_t2_n8_v3_N13⟩, ⟨6, 3, L_t2_n8_v3_N13, S_t2_n8_v3_N13⟩, ⟨9, 3, L_t2_n8_v3_N13, S_t2_n8_v3_N13⟩, ⟨12, 3, L_t2_n8_v3_N13, S_t2_n8_v3_N13⟩, ⟨15, 3, L_t2_n8_v3_N13, S_t2_n8_v3_N13⟩, ⟨18, 3, L_t2_n8_v3_N13, S_t2_n8_v3_N13⟩]
    (by decide) (by decide +kernel) (by decide) (by decide +kernel)

theorem K21_8_6_le_91 : K 21 8 6 ≤ 91 := K_le ub_K21_8_6

end CoveringLit

#print axioms CoveringLit.K6_5_2_le_66
#print axioms CoveringLit.K6_6_4_le_10
#print axioms CoveringLit.K6_7_4_le_36
#print axioms CoveringLit.K6_10_6_le_72
#print axioms CoveringLit.K7_5_2_le_97
#print axioms CoveringLit.K7_7_5_le_11
#print axioms CoveringLit.K7_9_6_le_37
#print axioms CoveringLit.K8_5_2_le_128
#print axioms CoveringLit.K8_7_4_le_92
#print axioms CoveringLit.K8_7_5_le_16
#print axioms CoveringLit.K8_8_6_le_12
#print axioms CoveringLit.K8_9_6_le_48
#print axioms CoveringLit.K9_5_2_le_189
#print axioms CoveringLit.K9_7_4_le_120
#print axioms CoveringLit.K9_7_5_le_21
#print axioms CoveringLit.K9_8_6_le_17
#print axioms CoveringLit.K9_9_7_le_13
#print axioms CoveringLit.K10_5_2_le_250
#print axioms CoveringLit.K10_7_5_le_26
#print axioms CoveringLit.K10_8_6_le_22
#print axioms CoveringLit.K10_9_7_le_18
#print axioms CoveringLit.K10_10_8_le_14
#print axioms CoveringLit.K11_7_5_le_31
#print axioms CoveringLit.K11_8_6_le_27
#print axioms CoveringLit.K12_5_2_le_468
#print axioms CoveringLit.K12_7_5_le_36
#print axioms CoveringLit.K12_8_6_le_32
#print axioms CoveringLit.K13_4_2_le_57
#print axioms CoveringLit.K13_7_5_le_42
#print axioms CoveringLit.K13_8_6_le_37
#print axioms CoveringLit.K14_4_2_le_66
#print axioms CoveringLit.K14_5_2_le_686
#print axioms CoveringLit.K14_5_3_le_54
#print axioms CoveringLit.K14_7_3_le_4802
#print axioms CoveringLit.K14_7_5_le_48
#print axioms CoveringLit.K14_8_6_le_42
#print axioms CoveringLit.K15_4_2_le_75
#print axioms CoveringLit.K15_5_2_le_855
#print axioms CoveringLit.K15_5_3_le_59
#print axioms CoveringLit.K15_7_3_le_6497
#print axioms CoveringLit.K15_7_5_le_54
#print axioms CoveringLit.K15_8_6_le_49
#print axioms CoveringLit.K16_4_2_le_87
#print axioms CoveringLit.K16_5_2_le_1024
#print axioms CoveringLit.K16_5_3_le_64
#print axioms CoveringLit.K16_7_3_le_8192
#print axioms CoveringLit.K16_7_5_le_60
#print axioms CoveringLit.K16_8_6_le_56
#print axioms CoveringLit.K17_4_2_le_99
#print axioms CoveringLit.K17_5_2_le_1241
#print axioms CoveringLit.K17_5_3_le_73
#print axioms CoveringLit.K17_7_3_le_10657
#print axioms CoveringLit.K17_7_5_le_66
#print axioms CoveringLit.K17_8_6_le_63
#print axioms CoveringLit.K18_4_2_le_111
#print axioms CoveringLit.K18_5_2_le_1458
#print axioms CoveringLit.K18_5_3_le_82
#print axioms CoveringLit.K18_6_4_le_80
#print axioms CoveringLit.K18_7_3_le_13122
#print axioms CoveringLit.K18_7_5_le_72
#print axioms CoveringLit.K18_8_6_le_70
#print axioms CoveringLit.K19_4_2_le_123
#print axioms CoveringLit.K19_5_3_le_91
#print axioms CoveringLit.K19_6_4_le_86
#print axioms CoveringLit.K19_7_3_le_18737
#print axioms CoveringLit.K19_7_5_le_81
#print axioms CoveringLit.K19_8_6_le_77
#print axioms CoveringLit.K20_4_2_le_135
#print axioms CoveringLit.K20_5_3_le_100
#print axioms CoveringLit.K20_6_4_le_93
#print axioms CoveringLit.K20_7_3_le_21202
#print axioms CoveringLit.K20_7_5_le_89
#print axioms CoveringLit.K20_8_6_le_84
#print axioms CoveringLit.K21_4_2_le_147
#print axioms CoveringLit.K21_5_3_le_114
#print axioms CoveringLit.K21_6_4_le_99
#print axioms CoveringLit.K21_7_4_le_1029
#print axioms CoveringLit.K21_7_5_le_98
#print axioms CoveringLit.K21_8_6_le_91
