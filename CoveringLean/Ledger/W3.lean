-- GERADO por tools/certificar/gerar.py; não edite à mão. Witnesses de W3.
import CoveringLean.Regras

namespace CoveringLedger.Data
open CoveringUB

/-- tools/certificar/witnesses/K2_5_1_M7.txt, 7 palavras (índice = Σ dígito_k · q^k). -/
def K2_5_1 : List Nat := [0, 7, 9, 10, 19, 23, 28]

set_option maxRecDepth 100000 in
theorem w_K2_5_1 : UB 2 5 1 7 :=
  UB.of_go (L := K2_5_1) (by decide +kernel) (by decide +kernel)

/-- tools/certificar/witnesses/K2_6_1_M12.txt, 12 palavras (índice = Σ dígito_k · q^k). -/
def K2_6_1 : List Nat := [0, 7, 13, 18, 24, 31, 42, 43, 46, 49, 52, 53]

set_option maxRecDepth 100000 in
theorem w_K2_6_1 : UB 2 6 1 12 :=
  UB.of_go (L := K2_6_1) (by decide +kernel) (by decide +kernel)

/-- tools/certificar/witnesses/K2_6_2_M4.txt, 4 palavras (índice = Σ dígito_k · q^k). -/
def K2_6_2 : List Nat := [0, 1, 62, 63]

set_option maxRecDepth 100000 in
theorem w_K2_6_2 : UB 2 6 2 4 :=
  UB.of_go (L := K2_6_2) (by decide +kernel) (by decide +kernel)

/-- tools/certificar/witnesses/K2_7_1_M16.txt, 16 palavras (índice = Σ dígito_k · q^k). -/
def K2_7_1 : List Nat := [0, 7, 25, 30, 42, 45, 51, 52, 75, 76, 82, 85, 97, 102, 120, 127]

set_option maxRecDepth 100000 in
theorem w_K2_7_1 : UB 2 7 1 16 :=
  UB.of_go (L := K2_7_1) (by decide +kernel) (by decide +kernel)

/-- tools/certificar/witnesses/K2_7_2_M7.txt, 7 palavras (índice = Σ dígito_k · q^k). -/
def K2_7_2 : List Nat := [0, 21, 52, 53, 78, 90, 107]

set_option maxRecDepth 100000 in
theorem w_K2_7_2 : UB 2 7 2 7 :=
  UB.of_go (L := K2_7_2) (by decide +kernel) (by decide +kernel)

/-- tools/certificar/witnesses/K2_8_1_M32.txt, 32 palavras (índice = Σ dígito_k · q^k). -/
def K2_8_1 : List Nat := [1, 14, 23, 24, 37, 43, 48, 62, 68, 75, 82, 93, 98, 108, 119, 121, 130, 141, 148, 155, 166, 168, 179, 189, 199, 200, 209, 222, 225, 239, 244, 250]

set_option maxRecDepth 100000 in
theorem w_K2_8_1 : UB 2 8 1 32 :=
  UB.of_go (L := K2_8_1) (by decide +kernel) (by decide +kernel)

/-- tools/certificar/witnesses/K2_8_2_M12.txt, 12 palavras (índice = Σ dígito_k · q^k). -/
def K2_8_2 : List Nat := [0, 47, 51, 82, 90, 124, 143, 157, 168, 197, 233, 246]

set_option maxRecDepth 100000 in
theorem w_K2_8_2 : UB 2 8 2 12 :=
  UB.of_go (L := K2_8_2) (by decide +kernel) (by decide +kernel)

/-- tools/certificar/witnesses/K2_9_2_M16.txt, 16 palavras (índice = Σ dígito_k · q^k). -/
def K2_9_2 : List Nat := [22, 75, 109, 120, 145, 162, 183, 204, 256, 277, 294, 379, 417, 463, 474, 508]

set_option maxRecDepth 100000 in
theorem w_K2_9_2 : UB 2 9 2 16 :=
  UB.of_go (L := K2_9_2) (by decide +kernel) (by decide +kernel)

/-- tools/certificar/witnesses/K2_9_3_M7.txt, 7 palavras (índice = Σ dígito_k · q^k). -/
def K2_9_3 : List Nat := [0, 120, 239, 279, 360, 402, 405]

set_option maxRecDepth 100000 in
theorem w_K2_9_3 : UB 2 9 3 7 :=
  UB.of_go (L := K2_9_3) (by decide +kernel) (by decide +kernel)

/-- tools/certificar/witnesses/K2_10_3_M12.txt, 12 palavras (índice = Σ dígito_k · q^k). -/
def K2_10_3 : List Nat := [118, 143, 160, 349, 433, 455, 458, 530, 617, 732, 804, 955]

set_option maxRecDepth 100000 in
theorem w_K2_10_3 : UB 2 10 3 12 :=
  UB.of_go (L := K2_10_3) (by decide +kernel) (by decide +kernel)

/-- tools/certificar/witnesses/K2_11_3_M16.txt, 16 palavras (índice = Σ dígito_k · q^k). -/
def K2_11_3 : List Nat := [87, 233, 298, 400, 549, 600, 927, 998, 1155, 1278, 1341, 1348, 1586, 1676, 1867, 2033]

set_option maxRecDepth 100000 in
theorem w_K2_11_3 : UB 2 11 3 16 :=
  UB.of_go (L := K2_11_3) (by decide +kernel) (by decide +kernel)

/-- tools/certificar/witnesses/K3_3_1_M5.txt, 5 palavras (índice = Σ dígito_k · q^k). -/
def K3_3_1 : List Nat := [0, 4, 10, 12, 26]

set_option maxRecDepth 100000 in
theorem w_K3_3_1 : UB 3 3 1 5 :=
  UB.of_go (L := K3_3_1) (by decide +kernel) (by decide +kernel)

/-- tools/certificar/witnesses/K3_4_1_M9.txt, 9 palavras (índice = Σ dígito_k · q^k). -/
def K3_4_1 : List Nat := [0, 17, 22, 34, 39, 47, 59, 64, 78]

set_option maxRecDepth 100000 in
theorem w_K3_4_1 : UB 3 4 1 9 :=
  UB.of_go (L := K3_4_1) (by decide +kernel) (by decide +kernel)

/-- tools/certificar/witnesses/K3_5_2_M8.txt, 8 palavras (índice = Σ dígito_k · q^k). -/
def K3_5_2 : List Nat := [0, 29, 70, 123, 142, 145, 185, 210]

set_option maxRecDepth 100000 in
theorem w_K3_5_2 : UB 3 5 2 8 :=
  UB.of_go (L := K3_5_2) (by decide +kernel) (by decide +kernel)

/-- tools/certificar/witnesses/K3_6_2_M17.txt, 17 palavras (índice = Σ dígito_k · q^k). -/
def K3_6_2 : List Nat := [25, 36, 110, 174, 235, 253, 318, 374, 384, 440, 472, 537, 545, 598, 638, 666, 691]

set_option maxRecDepth 100000 in
theorem w_K3_6_2 : UB 3 6 2 17 :=
  UB.of_go (L := K3_6_2) (by decide +kernel) (by decide +kernel)

/-- tools/certificar/witnesses/K3_6_3_M6.txt, 6 palavras (índice = Σ dígito_k · q^k). -/
def K3_6_3 : List Nat := [0, 196, 199, 258, 401, 644]

set_option maxRecDepth 100000 in
theorem w_K3_6_3 : UB 3 6 3 6 :=
  UB.of_go (L := K3_6_3) (by decide +kernel) (by decide +kernel)

/-- tools/certificar/witnesses/K4_3_1_M8.txt, 8 palavras (índice = Σ dígito_k · q^k). -/
def K4_3_1 : List Nat := [0, 11, 21, 30, 35, 40, 54, 61]

set_option maxRecDepth 100000 in
theorem w_K4_3_1 : UB 4 3 1 8 :=
  UB.of_go (L := K4_3_1) (by decide +kernel) (by decide +kernel)

/-- tools/certificar/witnesses/K4_4_1_M24.txt, 24 palavras (índice = Σ dígito_k · q^k). -/
def K4_4_1 : List Nat := [0, 4, 30, 31, 41, 57, 77, 88, 99, 102, 114, 119, 138, 139, 145, 149, 172, 188, 205, 216, 226, 231, 243, 246]

set_option maxRecDepth 100000 in
theorem w_K4_4_1 : UB 4 4 1 24 :=
  UB.of_go (L := K4_4_1) (by decide +kernel) (by decide +kernel)

/-- tools/certificar/witnesses/K4_4_2_M7.txt, 7 palavras (índice = Σ dígito_k · q^k). -/
def K4_4_2 : List Nat := [0, 85, 170, 191, 239, 251, 254]

set_option maxRecDepth 100000 in
theorem w_K4_4_2 : UB 4 4 2 7 :=
  UB.of_go (L := K4_4_2) (by decide +kernel) (by decide +kernel)

/-- tools/certificar/witnesses/K5_3_1_M13.txt, 13 palavras (índice = Σ dígito_k · q^k). -/
def K5_3_1 : List Nat := [0, 11, 19, 26, 39, 40, 54, 60, 66, 83, 97, 107, 123]

set_option maxRecDepth 100000 in
theorem w_K5_3_1 : UB 5 3 1 13 :=
  UB.of_go (L := K5_3_1) (by decide +kernel) (by decide +kernel)

/-- tools/certificar/witnesses/K5_4_2_M11.txt, 11 palavras (índice = Σ dígito_k · q^k). -/
def K5_4_2 : List Nat := [0, 156, 312, 349, 368, 444, 463, 497, 573, 592, 614]

set_option maxRecDepth 100000 in
theorem w_K5_4_2 : UB 5 4 2 11 :=
  UB.of_go (L := K5_4_2) (by decide +kernel) (by decide +kernel)

/-- tools/certificar/witnesses/K6_3_1_M18.txt, 18 palavras (índice = Σ dígito_k · q^k). -/
def K6_3_1 : List Nat := [0, 7, 17, 58, 62, 69, 93, 100, 104, 113, 114, 121, 145, 155, 156, 200, 207, 214]

set_option maxRecDepth 100000 in
theorem w_K6_3_1 : UB 6 3 1 18 :=
  UB.of_go (L := K6_3_1) (by decide +kernel) (by decide +kernel)

/-- tools/certificar/witnesses/K6_4_2_M15.txt, 15 palavras (índice = Σ dígito_k · q^k). -/
def K6_4_2 : List Nat := [0, 259, 302, 482, 512, 517, 777, 827, 856, 1001, 1030, 1077, 1222, 1251, 1283]

set_option maxRecDepth 100000 in
theorem w_K6_4_2 : UB 6 4 2 15 :=
  UB.of_go (L := K6_4_2) (by decide +kernel) (by decide +kernel)

/-- tools/certificar/witnesses/K7_3_1_M25.txt, 25 palavras (índice = Σ dígito_k · q^k). -/
def K7_3_1 : List Nat := [0, 18, 40, 62, 72, 78, 94, 106, 122, 132, 142, 152, 161, 186, 205, 218, 227, 244, 255, 272, 275, 288, 298, 313, 329]

set_option maxRecDepth 100000 in
theorem w_K7_3_1 : UB 7 3 1 25 :=
  UB.of_go (L := K7_3_1) (by decide +kernel) (by decide +kernel)

/-- tools/certificar/witnesses/K7_4_2_M19.txt, 19 palavras (índice = Σ dígito_k · q^k). -/
def K7_4_2 : List Nat := [0, 400, 465, 506, 752, 793, 855, 1101, 1142, 1186, 1600, 1665, 1706, 1952, 1993, 2055, 2301, 2342, 2386]

set_option maxRecDepth 100000 in
theorem w_K7_4_2 : UB 7 4 2 19 :=
  UB.of_go (L := K7_4_2) (by decide +kernel) (by decide +kernel)

/-- tools/certificar/witnesses/K8_3_1_M32.txt, 32 palavras (índice = Σ dígito_k · q^k). -/
def K8_3_1 : List Nat := [0, 10, 19, 30, 103, 108, 113, 125, 165, 169, 183, 188, 195, 200, 214, 218, 262, 267, 274, 280, 356, 367, 373, 377, 386, 398, 400, 411, 481, 493, 500, 511]

set_option maxRecDepth 100000 in
theorem w_K8_3_1 : UB 8 3 1 32 :=
  UB.of_go (L := K8_3_1) (by decide +kernel) (by decide +kernel)

/-- tools/certificar/witnesses/K9_3_1_M41.txt, 41 palavras (índice = Σ dígito_k · q^k). -/
def K9_3_1 : List Nat := [0, 12, 32, 74, 86, 92, 108, 156, 184, 204, 208, 224, 232, 262, 286, 294, 301, 314, 348, 361, 377, 385, 391, 430, 449, 454, 465, 469, 488, 495, 516, 563, 593, 607, 619, 622, 636, 651, 662, 677, 720]

set_option maxRecDepth 100000 in
theorem w_K9_3_1 : UB 9 3 1 41 :=
  UB.of_go (L := K9_3_1) (by decide +kernel) (by decide +kernel)

/-- tools/certificar/witnesses/K10_3_1_M50.txt, 50 palavras (índice = Σ dígito_k · q^k). -/
def K10_3_1 : List Nat := [0, 11, 22, 33, 44, 104, 110, 121, 132, 143, 203, 214, 220, 231, 242, 302, 313, 324, 330, 341, 401, 412, 423, 434, 440, 555, 566, 577, 588, 599, 659, 665, 676, 687, 698, 758, 769, 775, 786, 797, 857, 868, 879, 885, 896, 956, 967, 978, 989, 995]

set_option maxRecDepth 100000 in
theorem w_K10_3_1 : UB 10 3 1 50 :=
  UB.of_go (L := K10_3_1) (by decide +kernel) (by decide +kernel)

/-- tools/certificar/witnesses/K11_3_1_M61.txt, 61 palavras (índice = Σ dígito_k · q^k). -/
def K11_3_1 : List Nat := [0, 12, 24, 36, 48, 125, 132, 144, 156, 168, 245, 257, 264, 276, 288, 365, 377, 389, 396, 408, 485, 497, 509, 521, 528, 665, 677, 689, 701, 713, 725, 791, 797, 809, 821, 833, 845, 911, 923, 929, 941, 953, 965, 1031, 1043, 1055, 1061, 1073, 1085, 1151, 1163, 1175, 1187, 1193, 1205, 1271, 1283, 1295, 1307, 1319, 1325]

set_option maxRecDepth 100000 in
theorem w_K11_3_1 : UB 11 3 1 61 :=
  UB.of_go (L := K11_3_1) (by decide +kernel) (by decide +kernel)

end CoveringLedger.Data
