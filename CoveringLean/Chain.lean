import Mathlib
import CoveringLean.A1_Weight
import CoveringLean.A2_Sphere
import CoveringLean.A3_Numeric

/-!
# Chain: liga A1 (volume) + A2 (cota de esfera) + A3 (aritmética) nas 8 claims `SPH.*.lb`

Cada teorema final diz: todo código `C ⊆ (ℤ/q)^n` que cobre com raio `R` tem `|C| ≥ cota`.
-/

open Finset

namespace CoveringChain

variable {q n : ℕ} [NeZero q]

/-- O volume da bola de A2 (`hammingDist x 0 ≤ R`) é a fórmula fechada de A3. -/
theorem ball_zero_eq_V (R : ℕ) :
    (CoveringA2.ball R (0 : Fin n → ZMod q)).card = CoveringA3.V q n R := by
  have h : CoveringA2.ball R (0 : Fin n → ZMod q)
      = univ.filter fun z : Fin n → ZMod q => hammingNorm z ≤ R := by
    ext z
    simp [CoveringA2.mem_ball, hammingDist_zero_right]
  rw [h, CoveringA1.ball_zero_card]
  rfl

/-- Cota de esfera com o volume na forma fechada. -/
theorem sphere_covering_formula {R : ℕ} {C : Finset (Fin n → ZMod q)}
    (hC : CoveringA2.Covers R C) : q ^ n ≤ C.card * CoveringA3.V q n R :=
  CoveringA2.sphere_covering_V hC (ball_zero_eq_V R)

theorem SPH_K5_7_2_lb (C : Finset (Fin 7 → ZMod 5)) (hC : CoveringA2.Covers 2 C) :
    215 ≤ C.card := CoveringA3.lb_5_7_2 _ (sphere_covering_formula hC)

theorem SPH_K4_10_4_lb (C : Finset (Fin 10 → ZMod 4)) (hC : CoveringA2.Covers 4 C) :
    51 ≤ C.card := CoveringA3.lb_4_10_4 _ (sphere_covering_formula hC)

theorem SPH_K5_9_3_lb (C : Finset (Fin 9 → ZMod 5)) (hC : CoveringA2.Covers 3 C) :
    327 ≤ C.card := CoveringA3.lb_5_9_3 _ (sphere_covering_formula hC)

theorem SPH_K5_10_4_lb (C : Finset (Fin 10 → ZMod 5)) (hC : CoveringA2.Covers 4 C) :
    158 ≤ C.card := CoveringA3.lb_5_10_4 _ (sphere_covering_formula hC)

theorem SPH_K5_9_5_lb (C : Finset (Fin 9 → ZMod 5)) (hC : CoveringA2.Covers 5 C) :
    12 ≤ C.card := CoveringA3.lb_5_9_5 _ (sphere_covering_formula hC)

theorem SPH_K5_9_4_lb (C : Finset (Fin 9 → ZMod 5)) (hC : CoveringA2.Covers 4 C) :
    52 ≤ C.card := CoveringA3.lb_5_9_4 _ (sphere_covering_formula hC)

theorem SPH_K7_8_3_lb (C : Finset (Fin 8 → ZMod 7)) (hC : CoveringA2.Covers 3 C) :
    439 ≤ C.card := CoveringA3.lb_7_8_3 _ (sphere_covering_formula hC)

theorem SPH_K7_9_4_lb (C : Finset (Fin 9 → ZMod 7)) (hC : CoveringA2.Covers 4 C) :
    221 ≤ C.card := CoveringA3.lb_7_9_4 _ (sphere_covering_formula hC)

end CoveringChain

#print axioms CoveringChain.sphere_covering_formula
#print axioms CoveringChain.SPH_K5_7_2_lb
#print axioms CoveringChain.SPH_K4_10_4_lb
#print axioms CoveringChain.SPH_K5_9_3_lb
#print axioms CoveringChain.SPH_K5_10_4_lb
#print axioms CoveringChain.SPH_K5_9_5_lb
#print axioms CoveringChain.SPH_K5_9_4_lb
#print axioms CoveringChain.SPH_K7_9_4_lb
#print axioms CoveringChain.SPH_K7_8_3_lb
