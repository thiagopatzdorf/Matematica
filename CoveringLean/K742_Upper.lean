import Mathlib
import CoveringLean.A2_Sphere

/-!
# K_7(4,2) ≤ 19 no kernel

O código é a construção por partição 1 + 3 + 3 (`tools/exatos/particao_q42.py`,
`tools/exatos/k742/redteam/cod19.py`): a palavra `0000`, o tetracódigo `[4,2,3]_3`
`(a, b, a+b, a+2b)` sobre os símbolos {1,2,3} e o mesmo sobre {4,5,6}.

O espaço tem só 7^4 = 2401 pontos, então a cobertura é conferida por `decide +kernel` direto,
ponto a ponto, sem certificado intermediário. Sem `native_decide`.
-/

namespace K742

/-- Código da partição 1 + 3 + 3 em `Z_7^4`, 19 palavras. -/
def code19 : Finset (Fin 4 → ZMod 7) :=
  {![0,0,0,0], ![1,1,1,1], ![1,2,2,3], ![1,3,3,2], ![2,1,2,2], ![2,2,3,1], ![2,3,1,3],
   ![3,1,3,3], ![3,2,1,2], ![3,3,2,1], ![4,4,4,4], ![4,5,5,6], ![4,6,6,5], ![5,4,5,5],
   ![5,5,6,4], ![5,6,4,6], ![6,4,6,6], ![6,5,4,5], ![6,6,5,4]}

/-- As 19 palavras são distintas. -/
theorem code19_card : code19.card = 19 := by decide +kernel

/-- A cobertura de raio 2, ponto a ponto (2401 casos, conferidos pelo kernel). -/
theorem code19_covers_vec :
    ∀ a b c d : ZMod 7, ∃ w ∈ code19, hammingDist ![a, b, c, d] w ≤ 2 := by
  decide +kernel

theorem code19_covers : CoveringA2.Covers 2 code19 := by
  intro x
  have hx : x = ![x 0, x 1, x 2, x 3] := by
    ext i; fin_cases i <;> rfl
  rw [hx]
  exact code19_covers_vec _ _ _ _

/-- **K_7(4,2) ≤ 19.** -/
theorem K_7_4_2_le_19 :
    ∃ C : Finset (Fin 4 → ZMod 7), C.card = 19 ∧ CoveringA2.Covers 2 C :=
  ⟨code19, code19_card, code19_covers⟩

end K742

#print axioms K742.code19_card
#print axioms K742.code19_covers
#print axioms K742.K_7_4_2_le_19
