import Mathlib

/-!
# K2_Loop: kernel-checkable pruned enumeration (pure Nat/List, raw `Nat` primitives)

An *item* is a word packed into one natural number `row` (digit `k` of the original word is
`row / q^k % q`) with a running Hamming distance `d` and a radius `rad`.  `go q m items` enumerates
digit assignments for the next `m` positions; each step shifts every item's `row` by one digit
(`row / q`), so the digit to compare is always `row % q` (no powers; GMP-accelerated `Nat` ops only).
It answers `true` iff on every branch some item ends within its radius.
Pruning (sound, speed only): an item with `d > rad` is dropped; if some item satisfies
`d + remaining ≤ rad` the whole subtree is accepted.
The raw `Nat.add/div/mod/beq/ble` and `cond` are used on purpose: they avoid instance unfolding in
the kernel, which is the dominant cost of `decide +kernel`.
-/

namespace CoveringKernel

structure Item where
  row : ℕ
  d : ℕ
  rad : ℕ

/-- digit `k` of the packed word `w` -/
def dg (q w k : ℕ) : ℕ := w / q ^ k % q

def alive (it : Item) : Bool := Nat.ble it.d it.rad

/-- advance one position with digit `v`; drop items whose distance exceeds their radius -/
def stepAll (q v : ℕ) : List Item → List Item
  | [] => []
  | it :: r =>
    bif Nat.ble (Nat.add it.d (cond (Nat.beq (Nat.mod it.row q) v) 0 1)) it.rad then
      ⟨Nat.div it.row q, Nat.add it.d (cond (Nat.beq (Nat.mod it.row q) v) 0 1), it.rad⟩
        :: stepAll q v r
    else stepAll q v r

def go (q : ℕ) : ℕ → List Item → Bool
  | 0, items => items.any alive
  | m + 1, items =>
    bif items.any (fun it => Nat.ble (Nat.add it.d (m + 1)) it.rad) then true
    else (List.range q).all (fun v => go q m (stepAll q v items))

/-- Splitting the first branching level into separate theorems (to bound kernel memory). -/
theorem go_split (q m : ℕ) (items : List Item)
    (h : ∀ v < q, go q m (stepAll q v items) = true) : go q (m + 1) items = true := by
  simp only [go]
  cases hc : items.any (fun it => Nat.ble (Nat.add it.d (m + 1)) it.rad)
  · simp only [Bool.cond_false]
    exact List.all_eq_true.mpr (fun v hv => h v (List.mem_range.mp hv))
  · rfl

theorem cb_eq (a v : ℕ) : cond (Nat.beq a v) 0 1 = if a = v then 0 else 1 := by
  by_cases h : a = v
  · subst h; simp
  · have : Nat.beq a v = false := by
      cases hb : Nat.beq a v
      · rfl
      · exact absurd (Nat.eq_of_beq_eq_true hb) h
    simp [this, h]

theorem mem_stepAll (q v : ℕ) (it' : Item) :
    ∀ items : List Item, it' ∈ stepAll q v items →
      ∃ it ∈ items, it' = ⟨it.row / q, it.d + (if it.row % q = v then 0 else 1), it.rad⟩ ∧
        it'.d ≤ it'.rad := by
  intro items
  induction items with
  | nil => simp [stepAll]
  | cons it r ih =>
    intro h
    simp only [stepAll] at h
    cases hle : Nat.ble (Nat.add it.d (cond (Nat.beq (Nat.mod it.row q) v) 0 1)) it.rad
    · rw [hle] at h
      simp only [Bool.cond_false] at h
      obtain ⟨it2, h2, e, hh⟩ := ih h
      exact ⟨it2, List.mem_cons_of_mem _ h2, e, hh⟩
    · rw [hle] at h
      simp only [Bool.cond_true] at h
      rcases List.mem_cons.mp h with rfl | h
      · refine ⟨it, List.mem_cons_self, ?_, Nat.le_of_ble_eq_true hle⟩
        rw [cb_eq]
        rfl
      · obtain ⟨it2, h2, e, hh⟩ := ih h
        exact ⟨it2, List.mem_cons_of_mem _ h2, e, hh⟩

/-- Semantic meaning: every assignment of digits `< q` on the next `m` positions is served by an item. -/
def Sound (q m : ℕ) (items : List Item) : Prop :=
  ∀ a : ℕ → ℕ, (∀ k < m, a k < q) →
    ∃ it ∈ items, it.d + ∑ k ∈ Finset.range m, (if dg q it.row k = a k then 0 else 1) ≤ it.rad

theorem dg_succ (q w k : ℕ) : dg q (w / q) k = dg q w (k + 1) := by
  unfold dg
  rw [Nat.div_div_eq_div_mul, pow_succ']

theorem go_sound (q : ℕ) :
    ∀ (m : ℕ) (items : List Item), go q m items = true → Sound q m items := by
  intro m
  induction m with
  | zero =>
    intro items h a _
    simp only [go, List.any_eq_true] at h
    obtain ⟨it, hit, hd⟩ := h
    refine ⟨it, hit, ?_⟩
    simpa [alive, Nat.ble_eq] using hd
  | succ m ih =>
    intro items h a ha
    simp only [go] at h
    cases hc : items.any (fun it => Nat.ble (Nat.add it.d (m + 1)) it.rad)
    · rw [hc] at h
      simp only [Bool.cond_false] at h
      have hv : a 0 < q := ha 0 (by omega)
      have h2 := List.all_eq_true.mp h (a 0) (List.mem_range.mpr hv)
      obtain ⟨it', hit', hd'⟩ := ih _ h2 (fun k => a (k + 1)) (fun k hk => ha (k + 1) (by omega))
      obtain ⟨it, hit, e, _⟩ := mem_stepAll q (a 0) it' _ hit'
      refine ⟨it, hit, ?_⟩
      subst e
      rw [Finset.sum_range_succ']
      simp only [dg_succ] at hd'
      have h0 : dg q it.row 0 = it.row % q := by simp [dg]
      rw [h0]
      omega
    · rw [hc] at h
      simp only [List.any_eq_true, Nat.ble_eq] at hc
      obtain ⟨it, hit, hd⟩ := hc
      refine ⟨it, hit, le_trans ?_ hd⟩
      have h1 : ∑ k ∈ Finset.range (m + 1), (if dg q it.row k = a k then 0 else 1) ≤
          ∑ k ∈ Finset.range (m + 1), 1 :=
        Finset.sum_le_sum (fun k _ => by split_ifs <;> simp)
      simp only [Finset.sum_const, Finset.card_range, smul_eq_mul, mul_one] at h1
      show it.d + _ ≤ it.d + (m + 1)
      omega

end CoveringKernel
