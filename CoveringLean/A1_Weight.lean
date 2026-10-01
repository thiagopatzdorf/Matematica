import Mathlib

/-!
# A1: distribuição do peso de Hamming em `Fin n → ZMod q`

* `weight_genfun`  : `∑ z, X ^ ‖z‖₀ = (1 + (q-1) X) ^ n` em `ℕ[X]`
* `count_weight`   : `#{z | ‖z‖₀ = i} = C(n,i) (q-1)^i`
* `ball_zero_card` : `#{z | ‖z‖₀ ≤ R} = ∑_{i ≤ R} C(n,i) (q-1)^i`
-/

open Finset Polynomial

namespace CoveringA1

variable {q : ℕ} [NeZero q]

/-- `X ^ peso` é um produto coordenada a coordenada (cada entrada não nula contribui com um `X`). -/
lemma pow_hammingNorm_eq_prod {n : ℕ} (z : Fin n → ZMod q) :
    (X : ℕ[X]) ^ hammingNorm z = ∏ i, (if z i = 0 then (1 : ℕ[X]) else X) := by
  rw [hammingNorm, ← Finset.prod_const, Finset.prod_filter]
  refine Finset.prod_congr rfl fun i _ => ?_
  by_cases h : z i = 0 <;> simp [h]

/-- Soma por coordenada: o zero contribui com `1`, os `q-1` não nulos com `X`. -/
lemma sum_coord :
    ∑ a : ZMod q, (if a = 0 then (1 : ℕ[X]) else X) = 1 + C (q - 1 : ℕ) * X := by
  rw [← Finset.add_sum_erase _ _ (Finset.mem_univ (0 : ZMod q))]
  have h : ∑ a ∈ (Finset.univ : Finset (ZMod q)).erase 0, (if a = 0 then (1 : ℕ[X]) else X)
      = ∑ a ∈ (Finset.univ : Finset (ZMod q)).erase 0, (X : ℕ[X]) := by
    refine Finset.sum_congr rfl fun a ha => ?_
    rw [if_neg (Finset.ne_of_mem_erase ha)]
  have hC : (C (q - 1 : ℕ) : ℕ[X]) = ((q - 1 : ℕ) : ℕ[X]) := C_eq_natCast (R := ℕ) (q - 1)
  rw [h, Finset.sum_const, Finset.card_erase_of_mem (Finset.mem_univ _), Finset.card_univ,
    ZMod.card, nsmul_eq_mul, hC, if_pos rfl]

/-- (1) Função geradora do peso de Hamming. -/
theorem weight_genfun (n : ℕ) :
    ∑ z : Fin n → ZMod q, (X : ℕ[X]) ^ hammingNorm z
      = (1 + C (q - 1 : ℕ) * X) ^ n := by
  calc ∑ z : Fin n → ZMod q, (X : ℕ[X]) ^ hammingNorm z
      = ∑ z : Fin n → ZMod q, ∏ i, (if z i = 0 then (1 : ℕ[X]) else X) :=
        Finset.sum_congr rfl fun z _ => pow_hammingNorm_eq_prod z
    _ = ∏ _i : Fin n, ∑ a : ZMod q, (if a = 0 then (1 : ℕ[X]) else X) := by
        rw [Finset.prod_univ_sum, Fintype.piFinset_univ]
    _ = (1 + C (q - 1 : ℕ) * X) ^ n := by
        rw [Finset.prod_const, Finset.card_univ, Fintype.card_fin, sum_coord]

/-- (2) Número de palavras de peso exatamente `i`. -/
theorem count_weight (n i : ℕ) :
    (Finset.univ.filter fun z : Fin n → ZMod q => hammingNorm z = i).card
      = n.choose i * (q - 1) ^ i := by
  have h := congrArg (fun p : ℕ[X] => p.coeff i) (weight_genfun (q := q) n)
  simp only [finsetSum_coeff, coeff_X_pow] at h
  -- lado esquerdo: soma de indicadores = cardinal do filtro
  have hL : (∑ z : Fin n → ZMod q, if i = hammingNorm z then (1 : ℕ) else 0)
      = (Finset.univ.filter fun z : Fin n → ZMod q => hammingNorm z = i).card := by
    rw [Finset.card_filter]
    exact Finset.sum_congr rfl fun z _ => by
      by_cases hz : hammingNorm z = i
      · simp [hz]
      · simp [hz, Ne.symm hz]
  -- lado direito: teorema binomial
  have hR : ((1 + C (q - 1 : ℕ) * X : ℕ[X]) ^ n).coeff i = n.choose i * (q - 1) ^ i := by
    rw [show (1 + C (q - 1 : ℕ) * X : ℕ[X]) = C (q - 1 : ℕ) * X + 1 from add_comm _ _,
      add_pow, finsetSum_coeff]
    have hterm : ∀ m : ℕ, (((C (q - 1 : ℕ) * X) ^ m * 1 ^ (n - m) * (n.choose m : ℕ[X])) :
        ℕ[X]).coeff i = if i = m then (q - 1) ^ m * n.choose m else 0 := by
      intro m
      have hc : ((n.choose m : ℕ) : ℕ[X]) = C (n.choose m) := (C_eq_natCast (R := ℕ) _).symm
      have hform : (C (q - 1 : ℕ) * X) ^ m * 1 ^ (n - m) * (n.choose m : ℕ[X])
          = C ((q - 1) ^ m * n.choose m) * X ^ m := by
        rw [one_pow, mul_one, mul_pow, ← C_pow, hc, C_mul]
        ring
      rw [hform, coeff_C_mul_X_pow]
    simp only [hterm]
    rw [Finset.sum_ite_eq]
    split_ifs with h
    · ring
    · have h' : ¬ i < n + 1 := fun hh => h (Finset.mem_range.mpr hh)
      have hlt : n < i := by omega
      rw [Nat.choose_eq_zero_of_lt hlt]
      simp
  rw [← hL, h, hR]

/-- (3) Volume da bola de raio `R` em torno de `0` (e, por translação, de qualquer centro). -/
theorem ball_zero_card (n R : ℕ) :
    (Finset.univ.filter fun z : Fin n → ZMod q => hammingNorm z ≤ R).card
      = ∑ i ∈ range (R + 1), n.choose i * (q - 1) ^ i := by
  rw [Finset.card_eq_sum_card_fiberwise (f := fun z : Fin n → ZMod q => hammingNorm z)
    (t := range (R + 1))]
  · refine Finset.sum_congr rfl fun i hi => ?_
    rw [← count_weight (q := q) n i]
    congr 1
    ext z
    simp only [Finset.mem_filter, Finset.mem_univ, true_and]
    constructor
    · exact fun h => h.2
    · intro h
      exact ⟨by have := Finset.mem_range.mp hi; omega, h⟩
  · intro z hz
    simp only [Finset.coe_filter, Finset.mem_univ, true_and, Set.mem_setOf_eq] at hz
    simpa [Finset.mem_range, Nat.lt_succ_iff] using hz

end CoveringA1

#print axioms CoveringA1.weight_genfun
#print axioms CoveringA1.count_weight
#print axioms CoveringA1.ball_zero_card
