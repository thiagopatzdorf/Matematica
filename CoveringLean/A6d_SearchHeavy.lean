import Mathlib
import CoveringLean.A6c_Search

/-!
# A6d: a busca exaustiva de `K_2(6,1) >= 11` NO KERNEL (OPCIONAL, pesada, fora da biblioteca)

NAO FAZ PARTE de `CoveringLean.lean` e **nao foi compilada com sucesso**: `decide +kernel` sobre
`refuted` (195112 nos, medidos em Python) estourou >24 GB de RAM em ~2.5 min numa VM de 32 GB
(1/7 da arvore ja passa de 17 GB em 1m37). O custo e por no: cada no varre 64 bits em `List.range`.
Enquanto isto nao compila, `no_cover_2_6_1_le10` e `H2_counterexample` em `A6c_Search.lean` so valem
**condicionais** a `refuted 64 7 bm6 nbr6 10 0 = true`; o valor `K_2(6,1) >= 11` segue como
COMPUTATIONALLY_VERIFIED (oraculo C), nao PROVEN_FORMAL.
-/

namespace CoveringA6

/-- A busca exaustiva: nenhum conjunto de 10 bolas completa o conjunto coberto vazio. -/
theorem search_6_1_10 : refuted 64 7 bm6 nbr6 10 0 = true := by decide +kernel

theorem H2_unconditional :
    (∀ C : Finset (W 2 6), C.card < 11 → ¬ Covers 1 C) ∧
    (∃ C : Finset (W 2 6), C.card = 12 ∧ Covers 1 C) ∧
    IsK 2 7 1 16 ∧ HasVol 2 6 1 7 ∧ (2 ^ 6 + 7 - 1) / 7 = 10 ∧ (2 ^ 7 + 8 - 1) / 8 = 16 :=
  H2_counterexample search_6_1_10

end CoveringA6

#print axioms CoveringA6.H2_unconditional
