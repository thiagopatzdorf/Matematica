import CoveringLean.K742_Upper
import CoveringLean.K742_Fibras
import CoveringLean.K742_Cnf

/-!
# K_7(4,2) = 19 reduzido a duas proposições nomeadas

`K_7_4_2_eq_19_of` prova a igualdade **a partir de** duas hipóteses, cada uma uma proposição
fechada sobre objetos definidos no Lean:

* `Ponte18 G`: todo código de raio 2 em `Z_7^4` com 18 palavras satisfaz a CNF `G t` de algum
  dos 70 perfis (`G = K742Cnf.cnf 7 18`, o mesmo texto de `encode.py`, ou a versão sem a quebra
  de simetria (d)–(f), `K742Cnf.cnfSemQuebra 7 18`). É a forma normal do
  `canonizar.py`; a parte "o perfil está na lista" já é teorema (`perfis18_complete` com
  `profile_mem_profiles18`).
* `Refut18 G`: as 70 CNFs são insatisfatíveis. Cada uma é um teorema `LratK.Unsat` que o kernel
  confere pelo verificador LRAT verificado de `LratK` (`lratk_refute`); ver
  `docs/exatos/LEAN_K742.md` para o que já está feito e o custo do resto.

O resto (cota superior, completar um código menor até 18 palavras) é teorema aqui.
-/

open Finset

namespace K742

/-- A ponte código → CNF (ainda não formalizada), para uma família de CNFs `G t`: com
`G = K742Cnf.cnf 7 18` (a dos certificados, com (d)–(f)) ou `G = K742Cnf.cnfSemQuebra 7 18`. -/
def Ponte18 (G : List (List ℕ) → List (List ℕ)) : Prop :=
  ∀ C : Finset (Fin 4 → ZMod 7), C.card = 18 → CoveringA2.Covers 2 C →
    ∃ t ∈ perfis18, ∃ v : ℕ → Bool, ∀ c ∈ G t, LratK.ClauseSat v c

/-- A parte computacional: as 70 CNFs são insatisfatíveis. -/
def Refut18 (G : List (List ℕ) → List (List ℕ)) : Prop := ∀ t ∈ perfis18, LratK.Unsat (G t)

theorem covers_mono {C D : Finset (Fin 4 → ZMod 7)} (h : C ⊆ D) (hC : CoveringA2.Covers 2 C) :
    CoveringA2.Covers 2 D := fun x => by
  obtain ⟨c, hc, hd⟩ := hC x
  exact ⟨c, h hc, hd⟩

/-- Sem 18 palavras, nenhum código menor cobre: completa-se até 18 palavras distintas. -/
theorem no_cover_le_18 {G : List (List ℕ) → List (List ℕ)} (hp : Ponte18 G) (hr : Refut18 G)
    {C : Finset (Fin 4 → ZMod 7)} (hC : C.card ≤ 18) : ¬ CoveringA2.Covers 2 C := by
  intro hcov
  have huniv : (univ : Finset (Fin 4 → ZMod 7)).card = 2401 := by
    rw [card_univ, CoveringA2.card_space]; norm_num
  obtain ⟨D, hCD, -, hD⟩ := exists_subsuperset_card_eq (subset_univ C) hC (by omega)
  obtain ⟨t, ht, v, hv⟩ := hp D hD (covers_mono hCD hcov)
  obtain ⟨c, hc, hn⟩ := hr t ht v
  exact hn (hv c hc)

/-- **K_7(4,2) = 19**, condicionado a `Ponte18` e `Refut18`. -/
theorem K_7_4_2_eq_19_of {G : List (List ℕ) → List (List ℕ)} (hp : Ponte18 G)
    (hr : Refut18 G) :
    (∃ C : Finset (Fin 4 → ZMod 7), C.card = 19 ∧ CoveringA2.Covers 2 C) ∧
      ∀ C : Finset (Fin 4 → ZMod 7), C.card < 19 → ¬ CoveringA2.Covers 2 C :=
  ⟨K_7_4_2_le_19, fun _ hC => no_cover_le_18 hp hr (by omega)⟩

set_option maxRecDepth 100000 in
/-- A lista `perfis18` cobre todo multiconjunto de 4 tipos (`profiles18`): a parte "perfil"
da ponte já está provada (`profile_mem_profiles18`). -/
theorem perfis18_complete :
    ∀ P ∈ profiles18, ∃ t ∈ perfis18,
      ((t.map (fun l => (l : Multiset ℕ)) : List (Multiset ℕ)) : Multiset (Multiset ℕ)) =
        (P : Multiset (Multiset ℕ)) := by
  decide +kernel

end K742

#print axioms K742.no_cover_le_18
#print axioms K742.K_7_4_2_eq_19_of
#print axioms K742.perfis18_complete
