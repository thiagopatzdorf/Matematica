import Mathlib
import CoveringLean.A2_Sphere

/-!
# C1: a computable covering checker with a Lean soundness proof

A code is given as a list `L : List ℕ` of *indices*: the codeword `w₀ … w_{n-1}` (digits `< q`) is the
number `∑ wᵢ qⁱ` (little-endian).  `check q n R L` returns `true` only if

* every index is `< q ^ n`                                     (so decoding is injective),
* `L` is strictly increasing                                   (so the `|L|` words are pairwise distinct),
* every word of `(ℤ/q)ⁿ` is within Hamming distance `R` of some listed word.

The covering test is a depth-first search over the *suffix tree* of the space (`cov`).  A node is a prefix
`u` of the word `x` being covered; it carries the candidate codewords whose prefix is within distance `R`
of `u` (with their partial distance and the unread rest).  Pruning that is proved sound:

* a candidate whose partial distance already exceeds `R` is dropped;
* if some candidate has `partial + (remaining coordinates) ≤ R`, the whole subtree is covered.

Main results (`CoveringCerts.sound`, `CoveringCerts.cert_of_check`):

    check q n R L = true →
      (codeOf q n L).card = L.length  ∧  CoveringA2.Covers R (codeOf q n L)

What this does NOT show: that the list `L` is the code of some data file / certificate.  That link is only
the sha256 embedded by `scripts/gen_lean_cover.py` and `tests/test_lean_cover.py`.  The theorems about the
8 real cells live in `C1_Certs.lean` (native tier) / `C1_Kernel.lean` (pure kernel tier).
-/

open Finset

namespace CoveringCerts

/-! ### Index ↔ digits -/

/-- The `k` low digits of `m` in base `q`, little-endian (coordinate `i` = `i`-th element). -/
def dig (q : ℕ) : ℕ → ℕ → List ℕ
  | 0, _ => []
  | k + 1, m => m % q :: dig q k (m / q)

/-- Inverse of `dig` on `m < q ^ k`. -/
def undig (q : ℕ) : List ℕ → ℕ
  | [] => 0
  | d :: ds => d + q * undig q ds

@[simp] theorem length_dig (q k m : ℕ) : (dig q k m).length = k := by
  induction k generalizing m with
  | zero => rfl
  | succ k ih => simp [dig, ih]

theorem dig_lt {q : ℕ} (hq : 0 < q) (k m : ℕ) : ∀ d ∈ dig q k m, d < q := by
  induction k generalizing m with
  | zero => simp [dig]
  | succ k ih =>
    intro d hd
    simp only [dig, List.mem_cons] at hd
    rcases hd with rfl | hd
    · exact Nat.mod_lt _ hq
    · exact ih _ d hd

theorem undig_dig {q : ℕ} (hq : 0 < q) (k : ℕ) : ∀ m, m < q ^ k → undig q (dig q k m) = m := by
  induction k with
  | zero => intro m hm; simp at hm; simp [dig, undig, hm]
  | succ k ih =>
    intro m hm
    have h1 : m / q < q ^ k := by
      apply Nat.div_lt_of_lt_mul
      rw [pow_succ'] at hm
      exact hm
    simp only [dig, undig, ih _ h1]
    exact Nat.mod_add_div m q

/-- Decoding is injective below `q ^ k` (why the strictly-increasing check gives `M` distinct words). -/
theorem dig_inj {q : ℕ} (hq : 0 < q) (k : ℕ) {m m' : ℕ} (hm : m < q ^ k) (hm' : m' < q ^ k)
    (h : dig q k m = dig q k m') : m = m' :=
  calc m = undig q (dig q k m) := (undig_dig hq k m hm).symm
    _ = undig q (dig q k m') := by rw [h]
    _ = m' := undig_dig hq k m' hm'

/-! ### Hamming distance on digit lists -/

/-- Number of positions where the two lists differ (stops at the shorter list). -/
def hd : List ℕ → List ℕ → ℕ
  | a :: as, b :: bs => (if a = b then 0 else 1) + hd as bs
  | _, _ => 0

theorem hd_nil_right (u : List ℕ) : hd u [] = 0 := by cases u <;> rfl

theorem hd_le (u v : List ℕ) : hd u v ≤ u.length := by
  induction u generalizing v with
  | nil => cases v <;> simp [hd]
  | cons a as ih =>
    cases v with
    | nil => simp [hd]
    | cons b bs =>
      have := ih bs
      by_cases h : a = b <;> simp [hd, h] <;> omega

/-! ### The suffix-tree search -/

/-- Read one more coordinate `a` of `x`: keep candidates whose partial distance stays `≤ R`. -/
def advance (R a : ℕ) (cands : List (ℕ × List ℕ)) : List (ℕ × List ℕ) :=
  cands.filterMap fun p =>
    match p.2 with
    | b :: w =>
      if p.1 + (if b = a then 0 else 1) ≤ R then some (p.1 + (if b = a then 0 else 1), w) else none
    | [] => none

/-- `cov q R k cands`: every length-`k` suffix over digits `< q` is within `R` of some candidate
(`d + hd rest y ≤ R`). -/
def cov (q R : ℕ) : ℕ → List (ℕ × List ℕ) → Bool
  | 0, cands => cands.any fun p => decide (p.1 ≤ R)
  | k + 1, cands =>
    cands.any (fun p => decide (p.1 + (k + 1) ≤ R)) ||
      (List.range q).all fun a => cov q R k (advance R a cands)

theorem mem_advance {R a : ℕ} {cands : List (ℕ × List ℕ)} {p' : ℕ × List ℕ}
    (h : p' ∈ advance R a cands) :
    ∃ p ∈ cands, ∃ b, p.2 = b :: p'.2 ∧ p'.1 = p.1 + (if b = a then 0 else 1) ∧ p'.1 ≤ R := by
  unfold advance at h
  rw [List.mem_filterMap] at h
  obtain ⟨⟨d, w⟩, hp, hf⟩ := h
  cases w with
  | nil => simp at hf
  | cons b w =>
    simp only at hf
    generalize he : (if b = a then 0 else 1) = e at hf
    by_cases hle : d + e ≤ R
    · rw [if_pos hle] at hf
      have := Option.some.inj hf
      subst this
      exact ⟨(d, b :: w), hp, b, rfl, by show d + e = d + _; rw [he], hle⟩
    · rw [if_neg hle] at hf
      simp at hf

theorem cov_sound (q R : ℕ) : ∀ (k : ℕ) (cands : List (ℕ × List ℕ)),
    (∀ p ∈ cands, p.2.length = k) → cov q R k cands = true →
    ∀ y : List ℕ, y.length = k → (∀ a ∈ y, a < q) → ∃ p ∈ cands, p.1 + hd p.2 y ≤ R := by
  intro k
  induction k with
  | zero =>
    intro cands _ h y hy _
    have hy0 : y = [] := List.length_eq_zero_iff.mp hy
    subst hy0
    simp only [cov, List.any_eq_true, decide_eq_true_eq] at h
    obtain ⟨p, hp, hpR⟩ := h
    exact ⟨p, hp, by rw [hd_nil_right]; omega⟩
  | succ k ih =>
    intro cands hlen h y hy hyq
    cases y with
    | nil => simp at hy
    | cons a y' =>
      have hy' : y'.length = k := by simpa using hy
      simp only [cov, Bool.or_eq_true, List.any_eq_true, decide_eq_true_eq,
        List.all_eq_true] at h
      rcases h with ⟨p, hp, hpR⟩ | h
      · -- shortcut: even if every remaining coordinate is wrong, the candidate still covers
        refine ⟨p, hp, ?_⟩
        have := hd_le p.2 (a :: y')
        rw [hlen p hp] at this
        omega
      · have ha : a ∈ List.range q := List.mem_range.mpr (hyq a (by simp))
        have hcov := h a ha
        have hlen' : ∀ p ∈ advance R a cands, p.2.length = k := by
          intro p' hp'
          obtain ⟨p, hp, b, hb, _, _⟩ := mem_advance hp'
          have := hlen p hp
          rw [hb] at this
          simpa using this
        obtain ⟨p', hp', hle⟩ :=
          ih (advance R a cands) hlen' hcov y' hy' (fun c hc => hyq c (by simp [hc]))
        obtain ⟨p, hp, b, hb, hd1, _⟩ := mem_advance hp'
        refine ⟨p, hp, ?_⟩
        rw [hb]
        simp only [hd]
        rw [hd1] at hle
        by_cases hba : b = a <;> simp_all <;> omega

/-! ### From digit lists to functions `Fin n → ZMod q` -/

section Bridge

variable {q n : ℕ} [NeZero q]

theorem hq_pos : 0 < q := Nat.pos_of_ne_zero (NeZero.ne q)

/-- Codeword with index `m`, as a function on coordinates. -/
def word (q n m : ℕ) : Fin n → ZMod q :=
  fun i => (((dig q n m)[i.1]'(by rw [length_dig]; exact i.2) : ℕ) : ZMod q)

/-- The (finite) code with indices `L`. -/
def codeOf (q n : ℕ) (L : List ℕ) : Finset (Fin n → ZMod q) := (L.map (word q n)).toFinset

theorem ofFn_word (m : ℕ) : List.ofFn (fun i => (word q n m i).val) = dig q n m := by
  refine List.ext_getElem (by simp) fun i h1 h2 => ?_
  have hlt : (dig q n m)[i] < q := dig_lt hq_pos n m _ (List.getElem_mem _)
  simp [word, ZMod.val_natCast, Nat.mod_eq_of_lt hlt]

theorem hd_ofFn : ∀ (k : ℕ) (f g : Fin k → ℕ),
    hd (List.ofFn f) (List.ofFn g) = ∑ i, if f i = g i then 0 else 1
  | 0, f, g => by simp [hd]
  | k + 1, f, g => by
    rw [List.ofFn_succ, List.ofFn_succ, Fin.sum_univ_succ]
    simp only [hd]
    rw [hd_ofFn k (fun i => f i.succ) (fun i => g i.succ)]

theorem hammingDist_eq_sum (x c : Fin n → ZMod q) :
    hammingDist x c = ∑ i, if x i = c i then 0 else 1 := by
  simp only [hammingDist, Finset.card_filter]
  refine Finset.sum_congr rfl fun i _ => ?_
  by_cases h : x i = c i <;> simp [h]

/-- `hammingDist` on `Fin n → ZMod q` is `hd` on the digit lists (by injectivity of `ZMod.val`). -/
theorem hd_val (x c : Fin n → ZMod q) :
    hd (List.ofFn fun i => (c i).val) (List.ofFn fun i => (x i).val) = hammingDist x c := by
  rw [hd_ofFn, hammingDist_eq_sum]
  refine Finset.sum_congr rfl fun i _ => ?_
  have : ((c i).val = (x i).val) ↔ x i = c i :=
    ⟨fun h => (ZMod.val_injective q h).symm, fun h => by rw [h]⟩
  simp only [this]

theorem covers_of_cov {R : ℕ} {L : List ℕ}
    (h : cov q R n (L.map fun m => (0, dig q n m)) = true) :
    CoveringA2.Covers R (codeOf q n L) := by
  intro x
  obtain ⟨p, hp, hpR⟩ := cov_sound q R n _
    (by intro p hp; simp only [List.mem_map] at hp; obtain ⟨m, _, rfl⟩ := hp; simp) h
    (List.ofFn fun i => (x i).val) (by simp)
    (by
      intro a ha
      rw [List.mem_ofFn] at ha
      obtain ⟨i, rfl⟩ := ha
      exact ZMod.val_lt _)
  simp only [List.mem_map] at hp
  obtain ⟨m, hm, rfl⟩ := hp
  refine ⟨word q n m, ?_, ?_⟩
  · simp only [codeOf, List.mem_toFinset, List.mem_map]
    exact ⟨m, hm, rfl⟩
  · rw [← hd_val x (word q n m), ofFn_word]
    simpa using hpR

theorem word_inj {m m' : ℕ} (hm : m < q ^ n) (hm' : m' < q ^ n)
    (h : word q n m = word q n m') : m = m' := by
  apply dig_inj hq_pos n hm hm'
  calc dig q n m = List.ofFn (fun i => (word q n m i).val) := (ofFn_word m).symm
    _ = List.ofFn (fun i => (word q n m' i).val) := by rw [h]
    _ = dig q n m' := ofFn_word m'

theorem card_codeOf {L : List ℕ} (hlt : ∀ m ∈ L, m < q ^ n) (hP : L.Pairwise (· < ·)) :
    (codeOf q n L).card = L.length := by
  unfold codeOf
  rw [List.toFinset_card_of_nodup, List.length_map]
  exact List.Nodup.map_on (fun a ha b hb h => word_inj (hlt a ha) (hlt b hb) h)
    (List.Pairwise.imp (fun h => Nat.ne_of_lt h) hP)

end Bridge

/-! ### The checker -/

/-- `true` iff the list is strictly increasing. -/
def strictlyInc : List ℕ → Bool
  | a :: b :: t => decide (a < b) && strictlyInc (b :: t)
  | _ => true

theorem pairwise_of_strictlyInc : ∀ L : List ℕ, strictlyInc L = true → L.Pairwise (· < ·)
  | [], _ => List.Pairwise.nil
  | [a], _ => by simp
  | a :: b :: t, h => by
    simp only [strictlyInc, Bool.and_eq_true, decide_eq_true_eq] at h
    have ih := pairwise_of_strictlyInc (b :: t) h.2
    refine List.Pairwise.cons ?_ ih
    intro c hc
    rcases List.mem_cons.mp hc with rfl | hc
    · exact h.1
    · exact lt_trans h.1 ((List.pairwise_cons.mp ih).1 c hc)

/-- The checker: indices in range, strictly increasing, and covering with radius `R`. -/
def check (q n R : ℕ) (L : List ℕ) : Bool :=
  L.all (fun m => decide (m < q ^ n)) && strictlyInc L &&
    cov q R n (L.map fun m => (0, dig q n m))

/-- **Soundness.** -/
theorem sound {q n R : ℕ} [NeZero q] {L : List ℕ} (h : check q n R L = true) :
    (codeOf q n L).card = L.length ∧ CoveringA2.Covers R (codeOf q n L) := by
  simp only [check, Bool.and_eq_true, List.all_eq_true, decide_eq_true_eq] at h
  obtain ⟨⟨hlt, hinc⟩, hcov⟩ := h
  exact ⟨card_codeOf hlt (pairwise_of_strictlyInc L hinc), covers_of_cov hcov⟩

/-- Shape of the 8 final theorems: `∃ C, C.card = M ∧ Covers R C`. -/
theorem cert_of_check {q n R M : ℕ} [NeZero q] {L : List ℕ} (hlen : L.length = M)
    (h : check q n R L = true) :
    ∃ C : Finset (Fin n → ZMod q), C.card = M ∧ CoveringA2.Covers R C :=
  ⟨codeOf q n L, hlen ▸ (sound h).1, (sound h).2⟩

/-! ### Non-vacuity on tiny instances (pure kernel, no `native_decide`) -/

section Tiny

/-- `{00, 11, 22}`: indices `0`, `1+3`, `2+6`. -/
def const3 : List ℕ := [0, 4, 8]

/-- the checker accepts the 3 constant words as a radius-1 covering of `(ℤ/3)²` … -/
example : check 3 2 1 const3 = true := by decide +kernel

/-- … and the decoded code IS A2's `constCode` (so the index convention is the intended one). -/
example : (codeOf 3 2 const3 : Finset (Fin 2 → ZMod 3)) = CoveringA2.constCode := by
  decide +kernel

/-- a deliberately wrong code (one word dropped) must be REJECTED. -/
example : check 3 2 1 [0, 4] = false := by decide +kernel
/-- another wrong code: `(2,2)` is at distance 2 from `(0,0)`, `(1,0)` and `(0,1)`. -/
example : check 3 2 1 [0, 1, 3] = false := by decide +kernel
/-- not strictly increasing (duplicate) must be rejected even if covering. -/
example : check 3 2 1 [0, 4, 4, 8] = false := by decide +kernel
/-- out-of-range index (`9 ≥ 3²`) must be rejected. -/
example : check 3 2 1 [0, 4, 8, 9] = false := by decide +kernel
/-- unsorted must be rejected. -/
example : check 3 2 1 [4, 0, 8] = false := by decide +kernel

/-- radius 0 forces the whole space: all of `(ℤ/2)³` accepted, 7 words rejected. -/
example : check 2 3 0 [0, 1, 2, 3, 4, 5, 6, 7] = true := by decide +kernel
example : check 2 3 0 [0, 1, 2, 3, 4, 5, 6] = false := by decide +kernel

/-- binary Hamming code [7,4]: 16 words, radius 1 (perfect).  Indices computed (python, not by hand)
from the parity checks of A6b: `∑ bit_b(i+1) xᵢ ≡ 0`, `b < 3`, coordinate `i` = bit `i` of the index. -/
def hamming74 : List ℕ :=
  [0, 7, 25, 30, 42, 45, 51, 52, 75, 76, 82, 85, 97, 102, 120, 127]

example : check 2 7 1 hamming74 = true := by decide +kernel
/-- same code with its last word replaced by `126` (not a codeword): must be REJECTED. -/
example : check 2 7 1 [0, 7, 25, 30, 42, 45, 51, 52, 75, 76, 82, 85, 97, 102, 120, 126] = false := by
  decide +kernel
/-- same code minus one word: must be REJECTED. -/
example : check 2 7 1 [0, 7, 25, 30, 42, 45, 51, 52, 75, 76, 82, 85, 97, 102, 120] = false := by
  decide +kernel
example : ∃ C : Finset (Fin 7 → ZMod 2), C.card = 16 ∧ CoveringA2.Covers 1 C :=
  cert_of_check (L := hamming74) (by decide) (by decide +kernel)

/-- Perfect code `{000, 111}` in `(ℤ/2)³`, radius 1: accepted; with the wrong word `110` rejected. -/
example : check 2 3 1 [0, 7] = true := by decide +kernel
example : check 2 3 1 [0, 6] = false := by decide +kernel

/-- Soundness theorem instantiated: exact card and covering for the constant code. -/
example : ∃ C : Finset (Fin 2 → ZMod 3), C.card = 3 ∧ CoveringA2.Covers 1 C :=
  cert_of_check (L := const3) (by decide) (by decide +kernel)

end Tiny

end CoveringCerts

#print axioms CoveringCerts.dig_inj
#print axioms CoveringCerts.cov_sound
#print axioms CoveringCerts.sound
#print axioms CoveringCerts.cert_of_check
