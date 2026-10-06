import CoveringLean.Regras

/-!
# K_7(5,3) ≤ 17 no kernel

O código de 17 palavras é `data/codes/q7_n5_R3_M17.txt` (achado por recozimento simulado,
`tools/exatos/busca_local/sa.c`, e conferido fora do Lean por `tools/verify/verify`: 0 pontos
descobertos nos 7^5 = 16 807). Aqui a cobertura de raio 3 é conferida pelo kernel com o
verificador por prefixos `CoveringKernel.go` (`K2_Loop.lean`), via `UB.of_go` (`Regras.lean`), o
mesmo caminho de `K764_Upper.lean`: só `decide +kernel`, nenhum axioma além dos três padrão.

Só a cota superior: a inferior K_7(5,3) ≥ 17 é uma refutação LRAT fora do Lean (PR #56/#67).
Antes deste arquivo a superior 17 era só anunciada nas tabelas do Kéri (Rivas Soriano).
-/

namespace CoveringK753
open CoveringUB

/-- As 17 palavras de `data/codes/q7_n5_R3_M17.txt`, como índices little-endian
(índice = Σ dígito_k · 7^k, dígito 0 = primeiro caractere da linha). -/
def code17 : List Nat :=
  [608, 1336, 1770, 3041, 3496, 4371, 4992, 6906, 8710, 8804, 10003, 10878, 11627, 12027, 14235,
   15223, 15325]

/-- Existe código de raio 3 em `Z_7^5` com no máximo 17 palavras. -/
theorem ub_7_5_3_17 : UB 7 5 3 17 :=
  UB.of_go (L := code17) (by decide +kernel) (by decide +kernel)

/-- **K_7(5,3) ≤ 17.** -/
theorem K_7_5_3_le_17 : K 7 5 3 ≤ 17 := K_le ub_7_5_3_17

end CoveringK753

#print axioms CoveringK753.K_7_5_3_le_17
