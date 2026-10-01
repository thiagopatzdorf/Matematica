import Mathlib

/-!
# A2: cota de esfera (sphere-covering) para códigos de cobertura

Espaço `Fin n → ZMod q`, distância `hammingDist` de Mathlib.  Self-contained: não depende de
`Basic.lean` nem do fórmula do volume da bola (essa é do agente A1); aqui o volume é `(ball 0 R).card`
ou qualquer `V` com `hV : (ball 0 R).card = V`.

Teoremas principais:
* `ball_card_indep`      : toda bola tem o mesmo cardinal que a bola em 0
* `sphere_covering`      : `Covers C → q^n ≤ C.card * (ball 0 R).card`
* `sphere_covering_V`    : idem com `V` abstrato
* `no_perfect`           : `¬ V ∣ q^n → q^n < C.card * V`, e a forma com teto `ceil_bound`
* `equality_iff_perfect` : igualdade + cobertura ⇒ bolas dos centros disjuntas
-/

open Finset

namespace CoveringA2

variable {q : ℕ} [NeZero q] {n : ℕ}

/-- Bola de Hamming de centro `c` e raio `R`. -/
def ball (R : ℕ) (c : Fin n → ZMod q) : Finset (Fin n → ZMod q) :=
  univ.filter fun x => hammingDist x c ≤ R

/-- `C` cobre com raio `R`: todo ponto está a distância `≤ R` de alguma palavra de `C`. -/
def Covers (R : ℕ) (C : Finset (Fin n → ZMod q)) : Prop :=
  ∀ x : Fin n → ZMod q, ∃ c ∈ C, hammingDist x c ≤ R

theorem mem_ball {R : ℕ} {c x : Fin n → ZMod q} : x ∈ ball R c ↔ hammingDist x c ≤ R := by
  simp [ball]

/-- Translação preserva a distância de Hamming (por que: é o que faz toda bola ser "a mesma"). -/
theorem hammingDist_sub_right (x y c : Fin n → ZMod q) :
    hammingDist (x - c) (y - c) = hammingDist x y := by
  simp [hammingDist]

/-- Cardinal do espaço: `q ^ n`. -/
theorem card_space : Fintype.card (Fin n → ZMod q) = q ^ n := by
  simp [Fintype.card_fun, ZMod.card]

/-- (1) Toda bola tem o mesmo cardinal que a bola de centro 0. -/
theorem ball_card_indep (R : ℕ) (c : Fin n → ZMod q) :
    (ball R c).card = (ball R (0 : Fin n → ZMod q)).card := by
  refine Finset.card_nbij' (fun x => x - c) (fun y => y + c) ?_ ?_ ?_ ?_
  · intro x hx
    have hx' : hammingDist x c ≤ R := mem_ball.mp (by simpa using hx)
    have : hammingDist (x - c) 0 = hammingDist x c := by
      simpa using hammingDist_sub_right x c c
    simpa [mem_ball, this] using hx'
  · intro y hy
    have hy' : hammingDist y 0 ≤ R := mem_ball.mp (by simpa using hy)
    have : hammingDist (y + c) c = hammingDist y 0 := by
      simpa using (hammingDist_sub_right (y + c) c c).symm
    simpa [mem_ball, this] using hy'
  · intro x _; simp
  · intro y _; simp

/-- A bola contém seu centro, logo `V > 0`. -/
theorem ball_card_pos (R : ℕ) (c : Fin n → ZMod q) : 0 < (ball R c).card :=
  Finset.card_pos.mpr ⟨c, mem_ball.mpr (by simp)⟩

/-- Cota de esfera com `V` abstrato (compõe com a fórmula do volume). -/
theorem sphere_covering_V {R V : ℕ} {C : Finset (Fin n → ZMod q)} (hC : Covers R C)
    (hV : (ball R (0 : Fin n → ZMod q)).card = V) : q ^ n ≤ C.card * V := by
  have hsub : (univ : Finset (Fin n → ZMod q)) ⊆ C.biUnion (fun c => ball R c) := by
    intro x _
    obtain ⟨c, hc, hd⟩ := hC x
    exact Finset.mem_biUnion.mpr ⟨c, hc, mem_ball.mpr hd⟩
  calc q ^ n = (univ : Finset (Fin n → ZMod q)).card := by
        rw [Finset.card_univ, card_space]
    _ ≤ (C.biUnion (fun c => ball R c)).card := Finset.card_le_card hsub
    _ ≤ ∑ c ∈ C, (ball R c).card := Finset.card_biUnion_le
    _ = ∑ _c ∈ C, V := Finset.sum_congr rfl fun c _ => by rw [ball_card_indep, hV]
    _ = C.card * V := by simp

/-- (2) Cota de esfera: `q^n ≤ |C| · |B(0,R)|`. -/
theorem sphere_covering {R : ℕ} {C : Finset (Fin n → ZMod q)} (hC : Covers R C) :
    q ^ n ≤ C.card * (ball R (0 : Fin n → ZMod q)).card :=
  sphere_covering_V hC rfl

/-- (4) Se `V ∤ q^n`, a cota é estrita. -/
theorem no_perfect {R V : ℕ} {C : Finset (Fin n → ZMod q)} (hC : Covers R C)
    (hV : (ball R (0 : Fin n → ZMod q)).card = V) (hnd : ¬ V ∣ q ^ n) :
    q ^ n < C.card * V := by
  refine lt_of_le_of_ne (sphere_covering_V hC hV) fun h => hnd ?_
  exact ⟨C.card, by rw [h, mul_comm]⟩

/-- `V > 0` quando `V` é o volume. -/
theorem V_pos {R V : ℕ} (hV : (ball R (0 : Fin n → ZMod q)).card = V) : 0 < V :=
  hV ▸ ball_card_pos R 0

/-- (4, forma com teto) `⌈q^n / V⌉ ≤ |C|`, com o teto em divisão natural. -/
theorem ceil_bound {R V : ℕ} {C : Finset (Fin n → ZMod q)} (hC : Covers R C)
    (hV : (ball R (0 : Fin n → ZMod q)).card = V) :
    (q ^ n + V - 1) / V ≤ C.card := by
  have hpos := V_pos hV
  have h := sphere_covering_V hC hV
  have h2 : (C.card + 1) * V = C.card * V + V := by ring
  have : (q ^ n + V - 1) / V < C.card + 1 := by
    rw [Nat.div_lt_iff_lt_mul hpos, h2]
    generalize C.card * V = m at *
    omega
  omega

/-- Número de centros de `C` cuja bola contém `x`. -/
private def cnt (R : ℕ) (C : Finset (Fin n → ZMod q)) (x : Fin n → ZMod q) : ℕ :=
  ∑ c ∈ C, if hammingDist x c ≤ R then 1 else 0

private theorem card_ball_eq_sum (R : ℕ) (c : Fin n → ZMod q) :
    (ball R c).card = ∑ x : Fin n → ZMod q, if hammingDist x c ≤ R then 1 else 0 := by
  unfold ball
  rw [Finset.card_filter]

/-- (5) Igualdade `|C|·V = q^n` + cobertura ⇒ as bolas `B(c,R)`, `c ∈ C`, são disjuntas
(código perfeito). -/
theorem equality_iff_perfect {R V : ℕ} {C : Finset (Fin n → ZMod q)} (hC : Covers R C)
    (hV : (ball R (0 : Fin n → ZMod q)).card = V) (heq : C.card * V = q ^ n) :
    (C : Set (Fin n → ZMod q)).PairwiseDisjoint (fun c => ball R c) := by
  intro c₁ h₁ c₂ h₂ hne
  rw [Function.onFun, Finset.disjoint_left]
  intro x hx₁ hx₂
  have hx₁' := mem_ball.mp hx₁
  have hx₂' := mem_ball.mp hx₂
  -- cada ponto tem contagem ≥ 1 (cobertura) e x tem contagem ≥ 2
  have hge : ∀ y, 1 ≤ cnt R C y := by
    intro y
    obtain ⟨c, hc, hd⟩ := hC y
    calc 1 = (if hammingDist y c ≤ R then 1 else 0) := by simp [hd]
      _ ≤ cnt R C y :=
        Finset.single_le_sum (f := fun c => if hammingDist y c ≤ R then 1 else 0)
          (fun _ _ => Nat.zero_le _) hc
  have hx2 : 2 ≤ cnt R C x := by
    have hsub : ({c₁, c₂} : Finset (Fin n → ZMod q)) ⊆ C := by
      intro a ha
      rcases Finset.mem_insert.mp ha with rfl | ha
      · exact Finset.mem_coe.mp h₁
      · rw [Finset.mem_singleton.mp ha]; exact Finset.mem_coe.mp h₂
    calc 2 = ∑ c ∈ ({c₁, c₂} : Finset _), (if hammingDist x c ≤ R then 1 else 0) := by
          rw [Finset.sum_pair hne]; simp [hx₁', hx₂']
      _ ≤ cnt R C x :=
        Finset.sum_le_sum_of_subset_of_nonneg hsub fun _ _ _ => Nat.zero_le _
  -- dupla contagem: ∑ x, cnt x = ∑ c, |ball c| = |C|·V = q^n
  have hdouble : ∑ y : Fin n → ZMod q, cnt R C y = q ^ n := by
    unfold cnt
    rw [Finset.sum_comm]
    calc ∑ c ∈ C, ∑ y : Fin n → ZMod q, (if hammingDist y c ≤ R then 1 else 0)
        = ∑ c ∈ C, (ball R c).card :=
          Finset.sum_congr rfl fun c _ => (card_ball_eq_sum R c).symm
      _ = ∑ _c ∈ C, V := Finset.sum_congr rfl fun c _ => by rw [ball_card_indep, hV]
      _ = q ^ n := by rw [← heq]; simp
  have hlt : ∑ _y : Fin n → ZMod q, 1 < ∑ y : Fin n → ZMod q, cnt R C y :=
    Finset.sum_lt_sum (fun y _ => hge y) ⟨x, mem_univ _, by omega⟩
  rw [hdouble] at hlt
  simp [card_space] at hlt

/-! ### Não-vacuidade: instâncias minúsculas, checadas pelo kernel (sem `native_decide`) -/

section Stress

/-- Códigos constantes em `(ZMod 3)^2`. -/
def constCode : Finset (Fin 2 → ZMod 3) :=
  (univ : Finset (ZMod 3)).image fun a _ => a

/-- As 3 palavras constantes cobrem `(ZMod 3)^2` com raio 1 (hipótese de `sphere_covering` é
satisfazível). -/
theorem constCode_covers : Covers 1 constCode := by
  unfold Covers constCode
  decide +kernel

theorem constCode_card : constCode.card = 3 := by
  unfold constCode
  decide +kernel

/-- Aqui `V = 1 + 2·2 = 5`, calculado pelo kernel, não de memória. -/
theorem ball_card_3_2_1 : (ball 1 (0 : Fin 2 → ZMod 3)).card = 5 := by
  unfold ball
  decide +kernel

/-- A cota dá `9 ≤ 3·5`; instância concreta de `sphere_covering`. -/
example : 3 ^ 2 ≤ constCode.card * (ball 1 (0 : Fin 2 → ZMod 3)).card :=
  sphere_covering constCode_covers

/-- Instância de `no_perfect`: `5 ∤ 9`, logo `9 < 3·5`. -/
example : 3 ^ 2 < constCode.card * 5 :=
  no_perfect constCode_covers ball_card_3_2_1 (by decide)

/-- Caso de igualdade (Hamming binário `n=3`, `R=1`): `C = {000, 111}`, `V = 4`, `|C|·V = 8 = 2³`.
Mostra que a hipótese de `equality_iff_perfect` é satisfazível. -/
def rep3 : Finset (Fin 3 → ZMod 2) :=
  (univ : Finset (ZMod 2)).image fun a _ => a

theorem rep3_covers : Covers 1 rep3 := by
  unfold Covers rep3
  decide +kernel

theorem rep3_card : rep3.card = 2 := by
  unfold rep3
  decide +kernel

theorem ball_card_2_3_1 : (ball 1 (0 : Fin 3 → ZMod 2)).card = 4 := by
  unfold ball
  decide +kernel

example : (rep3 : Set (Fin 3 → ZMod 2)).PairwiseDisjoint (fun c => ball 1 c) :=
  equality_iff_perfect rep3_covers ball_card_2_3_1 (by rw [rep3_card]; decide)

end Stress

end CoveringA2

#print axioms CoveringA2.ball_card_indep
#print axioms CoveringA2.sphere_covering
#print axioms CoveringA2.sphere_covering_V
#print axioms CoveringA2.no_perfect
#print axioms CoveringA2.ceil_bound
#print axioms CoveringA2.equality_iff_perfect
#print axioms CoveringA2.constCode_covers
#print axioms CoveringA2.rep3_covers
