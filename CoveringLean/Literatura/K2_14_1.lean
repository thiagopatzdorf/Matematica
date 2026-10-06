import CoveringLean.Regras
import CoveringLean.Syn_K2_13_1_704

/-!
# K_2(14,1) ≤ 1408

Do código de 704 palavras de Östergård–Weakley (Designs, Codes and Cryptography 16 (1999) 65–73,
DOI 10.1023/A:1008326409439, Teorema 1; certificado por síndromes `Syn.K2_13_1_le_704_syn`) e
da regra `K(n+1, R) ≤ 2 K(n, R)` (`UB.lengthen_dummy`), como no Comentário 1 do artigo.
-/

namespace CoveringLit
open CoveringUB

theorem ub_K2_13_1 : UB 2 13 1 704 := UB.of_exists Syn.K2_13_1_le_704_syn

theorem K2_13_1_le_704 : K 2 13 1 ≤ 704 := K_le ub_K2_13_1

theorem ub_K2_14_1 : UB 2 14 1 1408 := by
  simpa using UB.lengthen_dummy (q := 2) 1 ub_K2_13_1

theorem K2_14_1_le_1408 : K 2 14 1 ≤ 1408 := K_le ub_K2_14_1

end CoveringLit

#print axioms CoveringLit.K2_14_1_le_1408
