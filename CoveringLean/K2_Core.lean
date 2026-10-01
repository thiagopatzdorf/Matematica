import Mathlib
import CoveringLean.A2_Sphere
import CoveringLean.K2_Loop

/-!
# K2_Core: from a checked word list to `Covers` (kernel tier, no `native_decide`)

Words are packed little-endian into natural numbers (`dg q w k = w / q^k % q`).  `cover_simple`
turns a successful run of `go` (K2_Loop) over all `n` positions, with one radius-`R` item per word,
into `∃ C : Finset (Fin n → ZMod q), C.card ≤ W.length ∧ Covers R C`.
-/

open CoveringA2

namespace CoveringKernel

/-- Hamming distance of two digit functions on the first `m` positions. -/
def distI (a b : ℕ → ℕ) : ℕ → ℕ
  | 0 => 0
  | m + 1 => distI a b m + (if a m = b m then 0 else 1)

theorem distI_eq (a b : ℕ → ℕ) (m : ℕ) :
    distI a b m = ∑ k ∈ Finset.range m, (if a k = b k then 0 else 1) := by
  induction m with
  | zero => simp [distI]
  | succ m ih => rw [distI, ih, Finset.sum_range_succ]

/-- digits of a word -/
def xval {q n : ℕ} (x : Fin n → ZMod q) (k : ℕ) : ℕ := if h : k < n then (x ⟨k, h⟩).val else 0

/-- word with digit function `c` -/
def wdf (q n : ℕ) (c : ℕ → ℕ) : Fin n → ZMod q := fun i => ((c i.val : ℕ) : ZMod q)

theorem xval_lt {q n : ℕ} [NeZero q] (x : Fin n → ZMod q) (k : ℕ) : xval x k < q := by
  unfold xval
  split_ifs with h
  · exact ZMod.val_lt _
  · exact Nat.pos_of_ne_zero (NeZero.ne q)

theorem hd_eq {q n : ℕ} [NeZero q] (x : Fin n → ZMod q) (c : ℕ → ℕ) (hc : ∀ k < n, c k < q) :
    hammingDist x (wdf q n c) = distI c (xval x) n := by
  unfold hammingDist
  rw [Finset.card_filter, distI_eq,
    ← Fin.sum_univ_eq_sum_range (fun k => if c k = xval x k then 0 else 1) n]
  apply Finset.sum_congr rfl
  intro i _
  have hxv : xval x i.val = (x i).val := by simp [xval]
  have key : x i = ((c i.val : ℕ) : ZMod q) ↔ c i.val = xval x i.val := by
    rw [hxv]
    constructor
    · intro h
      rw [h, ZMod.val_natCast_of_lt (hc i.val i.2)]
    · intro h
      rw [h, ZMod.natCast_zmod_val]
  by_cases h : c i.val = xval x i.val
  · have := key.mpr h
    simp [wdf, this, h]
  · have : ¬ x i = ((c i.val : ℕ) : ZMod q) := fun h' => h (key.mp h')
    simp [wdf, this, h]

def wordItems (R : ℕ) (W : List ℕ) : List Item := W.map (fun w => ⟨w, 0, R⟩)

theorem cover_simple (q n R : ℕ) [NeZero q] (W : List ℕ)
    (hgo : go q n (wordItems R W) = true) :
    ∃ C : Finset (Fin n → ZMod q), C.card ≤ W.length ∧ Covers R C := by
  classical
  refine ⟨(W.map (fun w => wdf q n (dg q w))).toFinset, ?_, ?_⟩
  · exact le_trans (List.toFinset_card_le _) (by rw [List.length_map])
  · intro x
    obtain ⟨it, hit, hd⟩ := go_sound q n _ hgo (xval x) (fun k _ => xval_lt x k)
    simp only [wordItems, List.mem_map] at hit
    obtain ⟨w, hw, rfl⟩ := hit
    refine ⟨wdf q n (dg q w), List.mem_toFinset.mpr (List.mem_map.mpr ⟨w, hw, rfl⟩), ?_⟩
    rw [hd_eq x (dg q w) (fun k _ => Nat.mod_lt _ (Nat.pos_of_ne_zero (NeZero.ne q))), distI_eq]
    simpa using hd

end CoveringKernel
