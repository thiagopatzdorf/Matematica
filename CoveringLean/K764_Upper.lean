import CoveringLean.Regras

/-!
# K_7(6,4) ≤ 14 no kernel

O código de 14 palavras é `data/codes/q7_n6_R4_M14.txt` (conferido fora do Lean por
`tools/verify/verify`: 0 pontos descobertos nos 7^6 = 117 649). Aqui a cobertura de raio 4 é
conferida pelo kernel com o verificador por prefixos `CoveringKernel.go` (`K2_Loop.lean`),
via `UB.of_go` (`Regras.lean`), o mesmo caminho do lote `CoveringLedger`. A poda do `go` aceita a
subárvore assim que alguma palavra ainda cabe no raio, então a árvore é pequena e `decide +kernel`
basta, só com redução no kernel (nenhum axioma além dos três padrão).

Só a cota superior: a inferior K_7(6,4) ≥ 14 é uma refutação LRAT fora do Lean.
-/

namespace CoveringK764
open CoveringUB

/-- As 14 palavras de `data/codes/q7_n6_R4_M14.txt`, como índices little-endian
(índice = Σ dígito_k · 7^k, dígito 0 = primeiro caractere da linha). -/
def code14 : List Nat :=
  [0, 799, 19209, 19607, 38824, 39209, 58824, 62375, 76431, 78382, 97633, 100834, 114904, 116505]

/-- Existe código de raio 4 em `Z_7^6` com no máximo 14 palavras. -/
theorem ub_7_6_4_14 : UB 7 6 4 14 :=
  UB.of_go (L := code14) (by decide +kernel) (by decide +kernel)

/-- **K_7(6,4) ≤ 14.** -/
theorem K_7_6_4_le_14 : K 7 6 4 ≤ 14 := K_le ub_7_6_4_14

end CoveringK764

#print axioms CoveringK764.K_7_6_4_le_14
