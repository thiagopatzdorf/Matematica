import Mathlib

/-!
# A6: finite facts behind the refutations of H1, H2, H3, H5 (kernel-checked)

Space: `W q n := Fin n → Fin q` with Mathlib's `hammingDist`.
No `native_decide`, no `sorry`, no new axioms (see the `#print axioms` at the end).

Conventions
* `ball R c`  = Hamming ball of radius `R`.
* `Covers R C` = every word is within `R` of some word of `C`.
* `IsK q n R k` = `k = K_q(n,R)`: some code of size `k` covers, no code of size `< k` does.
* `HasVol q n R V` = every ball has exactly `V` words.

The sphere-covering bound itself (`sphere_bound`) is proved here for any `q n R` given the
ball size; the instances use it so that only the genuinely non-counting lower bound
(`K_3(3,2) ≥ 3`) needs an exhaustive check.
-/

namespace CoveringA6

open Finset

abbrev W (q n : ℕ) := Fin n → Fin q

def ball {q n : ℕ} (R : ℕ) (c : W q n) : Finset (W q n) :=
  univ.filter fun x => hammingDist x c ≤ R

def Covers {q n : ℕ} (R : ℕ) (C : Finset (W q n)) : Prop :=
  ∀ x : W q n, ∃ c ∈ C, hammingDist x c ≤ R

instance {q n : ℕ} (R : ℕ) (C : Finset (W q n)) : Decidable (Covers R C) := by
  unfold Covers; infer_instance

def HasVol (q n R V : ℕ) : Prop := ∀ c : W q n, (ball R c).card = V

instance (q n R V : ℕ) : Decidable (HasVol q n R V) := by
  unfold HasVol; infer_instance

/-- `k = K_q(n,R)`. -/
def IsK (q n R k : ℕ) : Prop :=
  (∃ C : Finset (W q n), C.card = k ∧ Covers R C) ∧
    ∀ C : Finset (W q n), C.card < k → ¬ Covers R C

/-- The sphere-covering bound, from a bound on the size of every ball. -/
theorem sphere_bound {q n R V : ℕ} (hV : ∀ c : W q n, (ball R c).card ≤ V)
    {C : Finset (W q n)} (hC : Covers R C) : q ^ n ≤ C.card * V := by
  have hsub : (univ : Finset (W q n)) ⊆ C.biUnion (ball R) := by
    intro x _
    obtain ⟨c, hc, hd⟩ := hC x
    exact mem_biUnion.2 ⟨c, hc, by simp [ball, hd]⟩
  calc q ^ n = (univ : Finset (W q n)).card := by simp
    _ ≤ (C.biUnion (ball R)).card := card_le_card hsub
    _ ≤ ∑ c ∈ C, (ball R c).card := card_biUnion_le
    _ ≤ C.card * V := by
        have := Finset.sum_le_card_nsmul C (fun c => (ball R c).card) V (fun c _ => hV c)
        simpa using this

/-- Lower bound by counting: if `q^n > m * V` then no code of size `m` covers. -/
theorem not_covers_of_count {q n R V m : ℕ} (hV : ∀ c : W q n, (ball R c).card ≤ V)
    (h : m * V < q ^ n) {C : Finset (W q n)} (hm : C.card ≤ m) : ¬ Covers R C := fun hC =>
  absurd (sphere_bound hV hC) (not_le.2 (lt_of_le_of_lt (Nat.mul_le_mul_right V hm) h))

/-! ## (1) H5: `K_2(2,1) = 2`, `V = 3`, `3 ∤ 4` -/

theorem vol_2_2_1 : HasVol 2 2 1 3 := by decide +kernel

theorem K_2_2_1 : IsK 2 2 1 2 := by
  refine ⟨⟨{![0, 0], ![1, 1]}, by decide +kernel, by decide +kernel⟩, fun C hC => ?_⟩
  exact not_covers_of_count (m := 1) (V := 3) (fun c => (vol_2_2_1 c).le) (by decide)
    (by omega)

theorem H5_counterexample :
    IsK 2 2 1 2 ∧ HasVol 2 2 1 3 ∧ 2 = (2 ^ 2 + 3 - 1) / 3 ∧ ¬ (3 ∣ 2 ^ 2) :=
  ⟨K_2_2_1, vol_2_2_1, by decide, by decide⟩

/-! ## (2) H1: `α(2,3,1) = 1`, `α(2,4,1) = 5/4` -/

theorem vol_2_3_1 : HasVol 2 3 1 4 := by decide +kernel

theorem K_2_3_1 : IsK 2 3 1 2 := by
  refine ⟨⟨{![0, 0, 0], ![1, 1, 1]}, by decide +kernel, by decide +kernel⟩, fun C hC => ?_⟩
  exact not_covers_of_count (m := 1) (V := 4) (fun c => (vol_2_3_1 c).le) (by decide)
    (by omega)

theorem vol_2_4_1 : HasVol 2 4 1 5 := by decide +kernel

/-- NOTE: `K_2(4,1) = 4` (not 5): the lower bound `⌈16/5⌉ = 4` is attained. -/
theorem K_2_4_1 : IsK 2 4 1 4 := by
  refine ⟨⟨{![0, 0, 0, 0], ![0, 0, 0, 1], ![1, 1, 1, 0], ![1, 1, 1, 1]},
    by decide +kernel, by decide +kernel⟩, fun C hC => ?_⟩
  exact not_covers_of_count (m := 3) (V := 5) (fun c => (vol_2_4_1 c).le) (by decide)
    (by omega)

/-- `α(q,n,R) = K · V / q^n`. H1 says `α` is nonincreasing in `n`; here it goes `1 → 5/4`. -/
theorem H1_counterexample :
    IsK 2 3 1 2 ∧ HasVol 2 3 1 4 ∧ IsK 2 4 1 4 ∧ HasVol 2 4 1 5 ∧
      ((2 : ℚ) * 4 / 2 ^ 3 = 1) ∧ ((4 : ℚ) * 5 / 2 ^ 4 = 5 / 4) ∧
      ((2 : ℚ) * 4 / 2 ^ 3 < (4 : ℚ) * 5 / 2 ^ 4) :=
  ⟨K_2_3_1, vol_2_3_1, K_2_4_1, vol_2_4_1, by norm_num, by norm_num, by norm_num⟩

/-! ## (3) H3: `K_3(3,2) = 3`, `V = 19`, `α = 19/9 > 2` -/

theorem vol_3_3_2 : HasVol 3 3 2 19 := by decide +kernel

/-- No 2-word code covers `Fin 3 → Fin 3` at radius 2 (351 unordered pairs; checked as 729
ordered pairs including the degenerate ones). -/
theorem no_pair_3_3_2 : ∀ a b : W 3 3, ¬ Covers 2 ({a, b} : Finset (W 3 3)) := by
  decide +kernel

theorem K_3_3_2 : IsK 3 3 2 3 := by
  refine ⟨⟨{![0, 0, 0], ![0, 0, 1], ![0, 0, 2]}, by decide +kernel, by decide +kernel⟩,
    fun C hC => ?_⟩
  have h2 : C.card ≤ 2 := by omega
  -- sizes 0 and 1 by counting (19 < 27), size 2 exhaustively.
  rcases Nat.lt_or_ge C.card 2 with h | h
  · exact not_covers_of_count (m := 1) (V := 19) (fun c => (vol_3_3_2 c).le) (by decide)
      (by omega)
  · obtain ⟨a, b, -, rfl⟩ := Finset.card_eq_two.1 (by omega : C.card = 2)
    exact no_pair_3_3_2 a b

theorem H3_counterexample :
    IsK 3 3 2 3 ∧ HasVol 3 3 2 19 ∧ ((3 : ℚ) * 19 / 3 ^ 3 = 19 / 9) ∧ ((2 : ℚ) < 3 * 19 / 3 ^ 3) :=
  ⟨K_3_3_2, vol_3_3_2, by norm_num, by norm_num⟩


#print axioms H5_counterexample
#print axioms H1_counterexample
#print axioms H3_counterexample

end CoveringA6
