import Mathlib
import CoveringLean.A6_Finite

namespace CoveringA6

open Finset

/-! ## (4) Tightness: binary Hamming code `[7,4]` meets the sphere bound with equality -/

/-- Parity check `b` (`b < 3`): `∑ᵢ bit_b(i+1) · xᵢ ≡ 0 (mod 2)`; columns of `H` are `1..7`. -/
def parity (b : ℕ) (x : W 2 7) : ℕ := (∑ i : Fin 7, (((i.val + 1) >>> b) % 2) * (x i).val) % 2

/-- The Hamming code: words with zero syndrome. -/
def hamming : Finset (W 2 7) :=
  univ.filter fun x => parity 0 x = 0 ∧ parity 1 x = 0 ∧ parity 2 x = 0

theorem hamming_card : hamming.card = 16 := by decide +kernel

theorem vol_2_7_1 : HasVol 2 7 1 8 := by decide +kernel

theorem hamming_covers : Covers 1 hamming := by decide +kernel

/-- Equality in the sphere bound: `|C| · V = q^n`, with `C` covering. -/
theorem hamming_tight :
    Covers 1 hamming ∧ HasVol 2 7 1 8 ∧ hamming.card * 8 = 2 ^ 7 :=
  ⟨hamming_covers, vol_2_7_1, by rw [hamming_card]; norm_num⟩

/-- Perfect: the balls around codewords are pairwise disjoint. -/
theorem hamming_perfect :
    ∀ a ∈ hamming, ∀ b ∈ hamming, a ≠ b → Disjoint (ball 1 a) (ball 1 b) := by
  decide +kernel

theorem K_2_7_1 : IsK 2 7 1 16 := by
  refine ⟨⟨hamming, hamming_card, hamming_covers⟩, fun C hC => ?_⟩
  exact not_covers_of_count (m := 15) (V := 8) (fun c => (vol_2_7_1 c).le) (by decide)
    (by omega)


#print axioms hamming_tight
#print axioms hamming_perfect
#print axioms K_2_7_1

end CoveringA6
