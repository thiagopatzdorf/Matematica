-- GERADO por tools/literatura/gerar_lean.py; não edite à mão.
import CoveringLean.Regras

/-! # Cotas binárias dos artigos, witness explícito pelo kernel

Cada lista é o código reconstruído por `tools/literatura/codigos_papers.py` a partir de
`data/literatura/<chave>.json` (índices little-endian: coordenada j = bit j).
-/

namespace CoveringLit
open CoveringUB

/-- OK98-Ex11: Exemplo 11, p. 174. Patric R. J. Östergård, Markku K. Kaikkonen, *New upper bounds for binary covering codes*, Discrete Mathematics 178 (1998) 165-179, DOI 10.1016/S0012-365X(97)81825-0. -/
def W2_15_4 : List Nat := [0, 255, 2921, 2966, 5678, 5841, 7451, 7652, 10055, 10168, 11356, 11427, 12658, 12685, 14901, 15050, 17717, 17866, 20082, 20109, 21340, 21411, 22599, 22712, 25115, 25316, 26926, 27089, 29801, 29846, 32512, 32767]

theorem ub_K2_15_4 : UB 2 15 4 32 :=
  UB.of_go (L := W2_15_4) (by decide +kernel) (by decide +kernel)

theorem K2_15_4_le_32 : K 2 15 4 ≤ 32 := K_le ub_K2_15_4

/-- OK98-Ex13: Exemplo 13 (G. Exoo), p. 174. Patric R. J. Östergård, Markku K. Kaikkonen, *New upper bounds for binary covering codes*, Discrete Mathematics 178 (1998) 165-179, DOI 10.1016/S0012-365X(97)81825-0. -/
def W2_12_3 : List Nat := [0, 3, 124, 127, 469, 690, 813, 970, 1166, 1378, 1465, 1625, 1765, 1814, 2281, 2330, 2470, 2630, 2717, 2929, 3125, 3282, 3405, 3626, 3968, 3971, 4092, 4095]

theorem ub_K2_12_3 : UB 2 12 3 28 :=
  UB.of_go (L := W2_12_3) (by decide +kernel) (by decide +kernel)

theorem K2_12_3_le_28 : K 2 12 3 ≤ 28 := K_le ub_K2_12_3

/-- OK98-Ex13-ADS1: Tabela 3, chave a1 (ADS com [3,1]1) sobre o Exemplo 13. Patric R. J. Östergård, Markku K. Kaikkonen, *New upper bounds for binary covering codes*, Discrete Mathematics 178 (1998) 165-179, DOI 10.1016/S0012-365X(97)81825-0. -/
def W2_14_4 : List Nat := [0, 124, 690, 970, 1166, 1378, 1814, 2330, 2470, 2630, 3282, 3626, 3968, 4092, 12291, 12415, 12757, 13101, 13753, 13913, 14053, 14569, 15005, 15217, 15413, 15693, 16259, 16383]

theorem ub_K2_14_4 : UB 2 14 4 28 :=
  UB.of_go (L := W2_14_4) (by decide +kernel) (by decide +kernel)

theorem K2_14_4_le_28 : K 2 14 4 ≤ 28 := K_le ub_K2_14_4

/-- HHKL93-T1-13-42: Tabela 1 (mu = 1), pp. 264-265. Heikki O. Hämäläinen, Iiro S. Honkala, Markku K. Kaikkonen, Simon N. Litsyn, *Bounds for binary multiple covering codes*, Designs, Codes and Cryptography 3 (1993) 251-275, DOI 10.1007/BF01388486. -/
def W2_13_3 : List Nat := [0, 63, 902, 953, 1216, 1239, 1262, 1882, 1893, 1997, 2034, 2519, 2536, 2630, 2681, 3345, 3374, 3612, 3619, 3723, 3764, 4427, 4468, 4572, 4579, 4817, 4846, 5510, 5561, 5655, 5672, 6157, 6194, 6298, 6309, 6912, 6935, 6958, 7238, 7289, 8128, 8191]

theorem ub_K2_13_3 : UB 2 13 3 42 :=
  UB.of_go (L := W2_13_3) (by decide +kernel) (by decide +kernel)

theorem K2_13_3_le_42 : K 2 13 3 ≤ 42 := K_le ub_K2_13_3

end CoveringLit

#print axioms CoveringLit.K2_15_4_le_32
#print axioms CoveringLit.K2_12_3_le_28
#print axioms CoveringLit.K2_14_4_le_28
#print axioms CoveringLit.K2_13_3_le_42
