import Mathlib
import CoveringLean.A6b_Hamming

namespace CoveringA6

open Finset

/-! ## (5) H2: `K_2(6,1) ≥ 11` by a kernel-checked exhaustive search

`K_2(6,1) = 12` (C oracle); the sphere bound only gives `⌈64/7⌉ = 10`.  We prove `≥ 11`, which
is enough: the additive gap `K - ⌈S⌉` is `≥ 1` at `(2,6,1)` but `0` at `(2,7,1)`
(`K_2(7,1) = 16 = 128/8`), so H2 ("the gap is nondecreasing in n") is false.

The search is a depth-first branch on the highest uncovered word `u` (some codeword must lie
in the ball of `u`: 7 choices), with the counting prune "uncovered > left · V".  Sets of words
are `Nat` bitmasks, so `lor`/`xor`/`log2` run on GMP in the kernel.  `refuted_sound` is the
(generic) proof that `refuted … = true` really rules out every list of `≤ l` centres. -/

/-- `refuted N V bm nbr l cov = true`: no `≤ l` further balls (masks `bm c`, `c ∈ nbr u` for the
branching word `u`) complete the covered-set `cov` to all `N` words. -/
def refuted (N V : ℕ) (bm : ℕ → ℕ) (nbr : ℕ → List ℕ) : ℕ → ℕ → Bool
  | 0, cov => cov != 2 ^ N - 1
  | l + 1, cov =>
      cov != 2 ^ N - 1 &&
      (decide ((l + 1) * V < (List.range N).countP fun i => !(cov.testBit i)) ||
        (nbr (Nat.log2 ((2 ^ N - 1) ^^^ cov))).all fun c => refuted N V bm nbr l (cov ||| bm c))

section Checker

variable {N V : ℕ} {bm : ℕ → ℕ} {nbr : ℕ → List ℕ}

theorem exists_clear {cov : ℕ} (hc : cov < 2 ^ N) (hne : cov ≠ 2 ^ N - 1) :
    ∃ i, i < N ∧ cov.testBit i = false := by
  by_contra h
  push_neg at h
  apply hne
  apply Nat.eq_of_testBit_eq
  intro i
  rw [Nat.testBit_two_pow_sub_one]
  by_cases hi : i < N
  · have := h i hi
    simp only [hi, decide_true]
    simpa using this
  · have hlt : cov < 2 ^ i := lt_of_lt_of_le hc (Nat.pow_le_pow_right (by norm_num) (by omega))
    rw [Nat.testBit_lt_two_pow hlt]
    simp [hi]

theorem countP_range_eq (N : ℕ) (p : ℕ → Bool) :
    (List.range N).countP p = ((Finset.range N).filter fun i => p i = true).card := by
  rw [List.countP_eq_length_filter]
  simp [Finset.card, Finset.filter_val, Finset.range_val, Multiset.range]

theorem refuted_sound
    (hbm : ∀ c, c < N → bm c < 2 ^ N)
    (hV : ∀ c, c < N → ((List.range N).countP fun i => (bm c).testBit i) ≤ V)
    (hnbr : ∀ u, u < N → ∀ c, c < N → (bm c).testBit u = true → c ∈ nbr u) :
    ∀ (l cov : ℕ), cov < 2 ^ N → refuted N V bm nbr l cov = true →
      ∀ L : List ℕ, L.length ≤ l → (∀ c ∈ L, c < N) →
        ¬ ∀ i, i < N → (cov.testBit i = true ∨ ∃ c ∈ L, (bm c).testBit i = true) := by
  intro l
  induction l with
  | zero =>
    intro cov hcov href L hL hLN hcover
    have hne : cov ≠ 2 ^ N - 1 := by simpa [refuted] using href
    obtain ⟨i, hi, hfalse⟩ := exists_clear hcov hne
    have L0 : L = [] := List.length_eq_zero_iff.1 (by omega)
    subst L0
    rcases hcover i hi with h | ⟨c, hc, _⟩
    · simp [hfalse] at h
    · simp at hc
  | succ l ih =>
    intro cov hcov href L hL hLN hcover
    simp only [refuted, Bool.and_eq_true, bne_iff_ne, ne_eq, Bool.or_eq_true,
      decide_eq_true_eq, List.all_eq_true] at href
    obtain ⟨hne, hprune | hrec⟩ := href
    · -- counting prune: the uncovered words fit in `|L|` balls of size `≤ V`
      rw [countP_range_eq] at hprune
      have hsub : ((Finset.range N).filter fun i => (!(cov.testBit i)) = true) ⊆
          L.toFinset.biUnion fun c => (Finset.range N).filter fun i => (bm c).testBit i = true := by
        intro i hi
        simp only [Finset.mem_filter, Finset.mem_range, Bool.not_eq_true'] at hi
        obtain ⟨hiN, hic⟩ := hi
        rcases hcover i hiN with h | ⟨c, hc, hb⟩
        · simp [hic] at h
        · exact Finset.mem_biUnion.2 ⟨c, List.mem_toFinset.2 hc, by simp [hiN, hb]⟩
      have h1 := Finset.card_le_card hsub
      have h2 := Finset.card_biUnion_le (s := L.toFinset)
        (t := fun c => (Finset.range N).filter fun i => (bm c).testBit i = true)
      have h3 : ∑ c ∈ L.toFinset, ((Finset.range N).filter fun i => (bm c).testBit i = true).card
          ≤ L.toFinset.card * V := by
        have := Finset.sum_le_card_nsmul L.toFinset
          (fun c => ((Finset.range N).filter fun i => (bm c).testBit i = true).card) V
          (fun c hc => by
            rw [← countP_range_eq]; exact hV c (hLN c (List.mem_toFinset.1 hc)))
        simpa using this
      have h4 : L.toFinset.card ≤ L.length := List.toFinset_card_le L
      have h5 : L.toFinset.card * V ≤ (l + 1) * V := Nat.mul_le_mul_right V (by omega)
      omega
    · obtain ⟨u0, hu0, hfalse⟩ := exists_clear hcov hne
      have hlt : (2 ^ N - 1) ^^^ cov < 2 ^ N :=
        Nat.xor_lt_two_pow (by have := Nat.one_le_two_pow (n := N); omega) hcov
      have hunc : (2 ^ N - 1) ^^^ cov ≠ 0 := by
        intro h0
        have : ((2 ^ N - 1) ^^^ cov).testBit u0 = true := by
          simp [Nat.testBit_xor, hu0, hfalse]
        rw [h0] at this
        simp at this
      have hu_bit := Nat.testBit_log2 hunc
      generalize hu : Nat.log2 ((2 ^ N - 1) ^^^ cov) = u at hrec hu_bit
      have huN : u < N := by
        by_contra hge
        push_neg at hge
        have := Nat.testBit_lt_two_pow
          (lt_of_lt_of_le hlt (Nat.pow_le_pow_right (by norm_num) hge))
        rw [this] at hu_bit
        exact absurd hu_bit (by simp)
      have hcov_u : cov.testBit u = false := by
        simp [Nat.testBit_xor, huN] at hu_bit
        simpa using hu_bit
      rcases hcover u huN with h | ⟨c, hc, hbc⟩
      · simp [hcov_u] at h
      · have hcN := hLN c hc
        have hr := hrec c (hnbr u huN c hcN hbc)
        have hcov' : cov ||| bm c < 2 ^ N := Nat.or_lt_two_pow hcov (hbm c hcN)
        refine ih (cov ||| bm c) hcov' hr (L.erase c) ?_ ?_ ?_
        · rw [List.length_erase_of_mem hc]; omega
        · intro c' hc'; exact hLN c' (List.mem_of_mem_erase hc')
        · intro i hi
          rcases hcover i hi with h | ⟨c', hc', hb⟩
          · left; simp [h]
          · by_cases hcc : c' = c
            · left; subst hcc; simp [hb]
            · right; exact ⟨c', (List.mem_erase_of_ne hcc).2 hc', hb⟩

end Checker

/-- Words of `Fin 6 → Fin 2` as numbers `0..63`. -/
def enc (x : W 2 6) : ℕ := ∑ i : Fin 6, (x i).val * 2 ^ i.val

def dec (k : ℕ) : W 2 6 := fun i => ⟨(k / 2 ^ i.val) % 2, Nat.mod_lt _ (by norm_num)⟩

/-- Ball of radius 1 around `c`, as a bitmask. -/
def bm6 (c : ℕ) : ℕ :=
  (1 <<< c) ||| (1 <<< (c ^^^ 1)) ||| (1 <<< (c ^^^ 2)) ||| (1 <<< (c ^^^ 4)) |||
    (1 <<< (c ^^^ 8)) ||| (1 <<< (c ^^^ 16)) ||| (1 <<< (c ^^^ 32))

/-- The 7 centres whose ball contains `u`. -/
def nbr6 (u : ℕ) : List ℕ := [u, u ^^^ 1, u ^^^ 2, u ^^^ 4, u ^^^ 8, u ^^^ 16, u ^^^ 32]

theorem enc_lt : ∀ x : W 2 6, enc x < 64 := by decide +kernel
theorem enc_dec : ∀ k, k < 64 → enc (dec k) = k := by decide +kernel
/-- The bitmask ball is Hamming's ball. -/
theorem bm6_spec : ∀ x c : W 2 6, hammingDist x c ≤ 1 ↔ (bm6 (enc c)).testBit (enc x) = true := by
  decide +kernel
theorem bm6_lt : ∀ c, c < 64 → bm6 c < 2 ^ 64 := by decide +kernel
theorem bm6_card : ∀ c, c < 64 → ((List.range 64).countP fun i => (bm6 c).testBit i) ≤ 7 := by
  decide +kernel
theorem nbr6_spec : ∀ u, u < 64 → ∀ c, c < 64 → (bm6 c).testBit u = true → c ∈ nbr6 u := by
  decide +kernel

/-- No code of size `≤ 10` covers `Fin 6 → Fin 2` at radius 1. -/
theorem no_cover_2_6_1_le10 (hsearch : refuted 64 7 bm6 nbr6 10 0 = true) :
    ∀ C : Finset (W 2 6), C.card ≤ 10 → ¬ Covers 1 C := by
  intro C hC hcov
  refine refuted_sound (N := 64) (V := 7) (bm := bm6) (nbr := nbr6) bm6_lt bm6_card nbr6_spec
    10 0 (by norm_num) hsearch (C.toList.map enc) (by simpa using hC)
    (by intro c hc; obtain ⟨c0, -, rfl⟩ := List.mem_map.1 hc; exact enc_lt c0) ?_
  intro i hi
  right
  obtain ⟨c, hc, hd⟩ := hcov (dec i)
  refine ⟨enc c, List.mem_map.2 ⟨c, Finset.mem_toList.2 hc, rfl⟩, ?_⟩
  have := (bm6_spec (dec i) c).1 hd
  rwa [enc_dec i hi] at this

/-- A 12-word cover of `Fin 6 → Fin 2` at radius 1 (so `11 ≤ K_2(6,1) ≤ 12`; the value 12
itself is only certified by the C oracle). -/
def code12 : Finset (W 2 6) :=
  (([0, 1, 2, 15, 28, 23, 57, 58, 59, 39, 44, 52] : List ℕ).map dec).toFinset

theorem code12_card : code12.card = 12 := by decide +kernel
theorem code12_covers : Covers 1 code12 := by decide +kernel

/-- H2 refuted: gap `K - ⌈S⌉` is `≥ 11 - 10 = 1` at `(2,6,1)` and `16 - 16 = 0` at `(2,7,1)`. -/
theorem H2_counterexample (hsearch : refuted 64 7 bm6 nbr6 10 0 = true) :
    (∀ C : Finset (W 2 6), C.card < 11 → ¬ Covers 1 C) ∧
    (∃ C : Finset (W 2 6), C.card = 12 ∧ Covers 1 C) ∧
    IsK 2 7 1 16 ∧ HasVol 2 6 1 7 ∧ (2 ^ 6 + 7 - 1) / 7 = 10 ∧ (2 ^ 7 + 8 - 1) / 8 = 16 :=
  ⟨fun C hC => no_cover_2_6_1_le10 hsearch C (by omega), ⟨code12, code12_card, code12_covers⟩, K_2_7_1,
    by decide +kernel, by norm_num, by norm_num⟩


#print axioms refuted_sound
#print axioms no_cover_2_6_1_le10
#print axioms H2_counterexample

end CoveringA6
