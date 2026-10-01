import Mathlib
import CoveringLean.A5_Frontier

/-! # A5b: estresses exaustivos (pesados) da fronteira. Opcional; fora da biblioteca raiz. -/

open Finset

namespace CoveringA5

variable {q n : ℕ} [NeZero q]

/-- q=2, n=3, R=1: para cada `M` em `1..8` o minimo exato e `ceil(M/4) = (M+3)/4`:
existe codigo com esse tamanho e nenhum codigo menor cobre `M` palavras. Cota justa em todo M
(porque `{000,111}` e perfeito). Verificado exaustivamente sobre os 256 codigos. -/
theorem stress_n3 :
    ∀ M ∈ Finset.Icc 1 8,
      (∃ C : Finset (Fin 3 → ZMod 2), C.card = (M + 3) / 4 ∧ M ≤ (coveredSet 1 C).card) ∧
      (∀ C : Finset (Fin 3 → ZMod 2), M ≤ (coveredSet 1 C).card → (M + 3) / 4 ≤ C.card) := by
  decide +kernel

/-- q=2, n=4, R=1 (`V = 5`), `M = 15`: a cota de esfera da `ceil(15/5) = 3`, mas nenhum codigo
de 3 palavras cobre 15 (exaustivo sobre os `C(16,3) = 560` codigos; `<= 2` palavras ja cai na
dupla contagem `2*5 = 10`). Minimo real: 4. Cota frouxa por 1. -/
theorem stress_n4_M15 :
    (∀ C ∈ (univ : Finset (Fin 4 → ZMod 2)).powersetCard 3, (coveredSet 1 C).card < 15) := by
  decide +kernel

theorem stress_n4_M15_lower (C : Finset (Fin 4 → ZMod 2)) (h : 15 ≤ (coveredSet 1 C).card) :
    4 ≤ C.card := by
  by_contra hlt
  push_neg at hlt
  have hle := card_coveredSet_le 1 5 V_n4 C
  by_cases h3 : C.card = 3
  · have : C ∈ (univ : Finset (Fin 4 → ZMod 2)).powersetCard 3 := by
      simp [mem_powersetCard, h3]
    have := stress_n4_M15 C this
    omega
  · omega

/-- Existe codigo de 4 palavras que cobre as 16: minimo para `M=15` e `M=16` e 4. -/
theorem stress_n4_exists4 :
    ∃ C ∈ (univ : Finset (Fin 4 → ZMod 2)).powersetCard 4, 16 ≤ (coveredSet 1 C).card := by
  decide +kernel

/-- `M = 16`: cota `ceil(16/5) = 4` e justa (`= K_2(4,1) = 4`). -/
theorem stress_n4_M16 (C : Finset (Fin 4 → ZMod 2)) (h : 16 ≤ (coveredSet 1 C).card) :
    4 ≤ C.card ∧ ⌈((16 : ℕ) : ℚ) / 5⌉₊ = 4 := by
  refine ⟨?_, ?_⟩
  · have := (frontier_bound_nat 1 5 V_n4 16 C h).1
    omega
  · rw [Nat.ceil_eq_iff (by norm_num)]
    norm_num

end CoveringA5

#print axioms CoveringA5.stress_n3
#print axioms CoveringA5.stress_n4_M15
#print axioms CoveringA5.stress_n4_M15_lower
#print axioms CoveringA5.stress_n4_exists4
#print axioms CoveringA5.stress_n4_M16
