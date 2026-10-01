import Mathlib
import CoveringLean.K2_Core
import CoveringLean.C1_CoverCheck

/-!
# K3_Bridge: kernel-tier `go` run  →  `∃ C, C.card = M ∧ Covers R C` (exact cardinality)

`K2_Core.cover_simple` only gives `C.card ≤ W.length`.  Here the code is C1's `codeOf q n L`
(digits by `CoveringCerts.dig`), whose exact cardinality is `CoveringCerts.card_codeOf`
(indices `< q^n` and strictly increasing, checked by `decide +kernel`).  The two digit
conventions agree: `(dig q k m)[i] = m / q^i % q = dg q m i` (`getElem_dig`).
No `native_decide`, no new axiom.
-/

namespace CoveringKernel

open CoveringCerts

theorem getElem_dig (q : ℕ) : ∀ (k m i : ℕ) (h : i < (dig q k m).length),
    (dig q k m)[i] = m / q ^ i % q := by
  intro k
  induction k with
  | zero => intro m i h; simp at h
  | succ k ih =>
    intro m i h
    cases i with
    | zero => simp [dig]
    | succ i =>
      simp only [dig, List.getElem_cons_succ]
      rw [ih, Nat.div_div_eq_div_mul, pow_succ']

theorem word_eq_wdf {q n : ℕ} [NeZero q] (m : ℕ) : word q n m = wdf q n (dg q m) := by
  funext i
  simp only [word, wdf, dg]
  rw [getElem_dig]

theorem covers_of_go {q n R : ℕ} [NeZero q] (W : List ℕ)
    (hgo : go q n (wordItems R W) = true) : CoveringA2.Covers R (codeOf q n W) := by
  classical
  intro x
  obtain ⟨it, hit, hd⟩ := go_sound q n _ hgo (xval x) (fun k _ => xval_lt x k)
  simp only [wordItems, List.mem_map] at hit
  obtain ⟨w, hw, rfl⟩ := hit
  refine ⟨word q n w, ?_, ?_⟩
  · simp only [codeOf, List.mem_toFinset, List.mem_map]
    exact ⟨w, hw, rfl⟩
  · rw [word_eq_wdf, hd_eq x (dg q w) (fun k _ => Nat.mod_lt _ (Nat.pos_of_ne_zero (NeZero.ne q))),
      distI_eq]
    simpa using hd

/-- Exact-cardinality certificate from a kernel-checked `go` run. -/
theorem cert_of_go {q n R M : ℕ} [NeZero q] {L : List ℕ} (hlen : L.length = M)
    (hchk : (L.all (fun m => decide (m < q ^ n)) && strictlyInc L) = true)
    (hgo : go q n (wordItems R L) = true) :
    ∃ C : Finset (Fin n → ZMod q), C.card = M ∧ CoveringA2.Covers R C := by
  simp only [Bool.and_eq_true, List.all_eq_true, decide_eq_true_eq] at hchk
  exact ⟨codeOf q n L, (card_codeOf hchk.1 (pairwise_of_strictlyInc L hchk.2)).trans hlen,
    covers_of_go L hgo⟩

/-! Non-vacuity: the binary Hamming [7,4] code (C1's `hamming74`) through this route. -/
example : ∃ C : Finset (Fin 7 → ZMod 2), C.card = 16 ∧ CoveringA2.Covers 1 C :=
  cert_of_go (L := hamming74) (by decide +kernel) (by decide +kernel) (by decide +kernel)

/-- and a wrong code is rejected by `go` (word 127 replaced by 126). -/
example : go 2 7 (wordItems 1 [0, 7, 25, 30, 42, 45, 51, 52, 75, 76, 82, 85, 97, 102, 120, 126])
    = false := by decide +kernel

end CoveringKernel

#print axioms CoveringKernel.cert_of_go
