import CoveringLean.SearchSound
import CoveringLean.A2_Sphere

/-!
# Ponte para o formato de `A2_Sphere` (`Fin n → ZMod 2`, `CoveringA2.Covers`)

`ZMod 2` reduz a `Fin 2`, então `CoveringA2.Covers 1 C` e `CoveringA6.Covers 1 C` são o mesmo
enunciado; a conversão é por `Iff.rfl`-ish (`exact`).
-/

namespace SC

theorem K_2_6_1_ge12_A2_of (h : Ref 6 (root 6 10)) :
    ∀ C : Finset (Fin 6 → ZMod 2), C.card < 12 → ¬ CoveringA2.Covers 1 C := by
  intro C hC hcov
  exact K_2_6_1_ge12_of h C hC hcov

end SC

#print axioms SC.K_2_6_1_ge12_A2_of
