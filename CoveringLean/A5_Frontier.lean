import Mathlib

/-!
# A5 -- fronteira C(eps) dos covering codes: cota de esfera parcial

## Veredito sobre PRICE_OF_IMPOSSIBILITY.md (secoes 3.3, 4)

Doc: `Pi_eps = min{|C| : C cobre >= (1-eps) q^n}` e `Pi_eps >= ceil((1-eps) S)`, `S = q^n / V`;
`P(theta) = inf { eps : C_theta(eps) < oo }`.

* A cota e EXATAMENTE o que foi provado aqui (`frontier_bound_rat`): `ceil((1-eps)*S) <= |C|`
  para todo codigo `C` que cobre `>= (1-eps) q^n` palavras. Sem folga de teto ou de
  desigualdade estrita. "Cobre >= (1-eps) q^n" (real) e "cobre >= ceil((1-eps) q^n)" (inteiro)
  sao a mesma condicao (`cover_real_iff_nat`), e `ceil(ceil(x)/V) = ceil(x/V)`
  (`ceil_ceil_div`), entao formular com M inteiro ou com real da o mesmo numero.
* Nao precisa de `eps in [0,1]` para a desigualdade (para eps > 1 o lado esquerdo e 0). O
  intervalo `[0,1]` so importa para a fronteira ser bem definida (conjunto nao vazio):
  eps > 1 pede cobrir mais que `q^n` palavras (vazio) -- `exists_least_of_eps`.
  eps = 1: M = 0, `C(1) = 0` (codigo vazio) e a cota 0 e justa (`eps_one_least`).
* `P(theta) = inf { eps : C_theta(eps) < oo }` esta correto, com `D x <= eps` NAO estrito
  (`P_eq_feasibility_threshold`), supondo Cost finito em todo ponto viavel. Em covering codes
  P = 0 (o proprio `C(0) = K` e finito) -- o doc ja diz isso (linha "Pi = 0").
* Nao ha erro numerico no doc. A cota e justa em alguns M e frouxa em outros:
  q=2,n=3,R=1 (V=4, codigo perfeito de repeticao): justa para TODO M em 1..8 (`stress_n3`, em A5b_Stress.lean: decide no kernel sobre 256 codigos e pesado).
  q=2,n=4,R=1 (V=5): frouxa em M=15 (cota ceil(15/5)=3, minimo real 4, `stress_n4_M15`),
  justa em M=16 (cota 4 = K) (`stress_n4_M16`). Fica um "salto" que a cota de esfera nao ve.

Sem lacunas (nenhum "sorry"), sem `native_decide`, sem axiomas novos (ver `#print axioms`).
-/

open Finset

namespace CoveringA5

variable {q n : ℕ} [NeZero q]

/-- Bola de Hamming de raio `R` centrada em `c`. -/
def hball (R : ℕ) (c : Fin n → ZMod q) : Finset (Fin n → ZMod q) :=
  univ.filter fun x => hammingDist x c ≤ R

/-- Palavras cobertas por `C` (a distancia `<= R` de algum codigo). -/
def coveredSet (R : ℕ) (C : Finset (Fin n → ZMod q)) : Finset (Fin n → ZMod q) :=
  univ.filter fun x => ∃ c ∈ C, hammingDist x c ≤ R

/-- Defeito impedido: sem isto a bola em `c` nao teria o mesmo tamanho que a bola em `0`. -/
theorem hammingDist_sub_right (x c : Fin n → ZMod q) :
    hammingDist x c = hammingDist (x - c) 0 := by
  simp [hammingDist, sub_eq_zero]

/-- Toda bola tem o mesmo tamanho (translacao `x ↦ x - c`). -/
theorem card_hball (R : ℕ) (c : Fin n → ZMod q) :
    (hball R c).card = (hball R (0 : Fin n → ZMod q)).card := by
  apply Finset.card_bij (fun x _ => x - c)
  · intro x hx
    simp only [hball, mem_filter, mem_univ, true_and] at hx ⊢
    rwa [← hammingDist_sub_right]
  · intro a _ b _ h
    simpa using h
  · intro y hy
    refine ⟨y + c, ?_, by simp⟩
    simp only [hball, mem_filter, mem_univ, true_and] at hy ⊢
    rw [hammingDist_sub_right]
    simpa using hy

theorem card_hball_pos (R : ℕ) : 0 < (hball R (0 : Fin n → ZMod q)).card :=
  Finset.card_pos.2 ⟨0, by rw [hball, mem_filter]; exact ⟨mem_univ _, by simp⟩⟩

/-! ### (1) Dupla contagem -/

/-- (1) Se `C` cobre todo ponto de `T` com raio `R`, entao `|T| <= |C| * |ball 0 R|`. -/
theorem partial_cover_bound (R : ℕ) (T C : Finset (Fin n → ZMod q))
    (h : ∀ x ∈ T, ∃ c ∈ C, hammingDist x c ≤ R) :
    T.card ≤ C.card * (hball R (0 : Fin n → ZMod q)).card := by
  have hsub : T ⊆ C.biUnion (fun c => hball R c) := by
    intro x hx
    obtain ⟨c, hc, hd⟩ := h x hx
    exact mem_biUnion.2 ⟨c, hc, by simp [hball, hd]⟩
  calc T.card ≤ (C.biUnion (fun c => hball R c)).card := card_le_card hsub
    _ ≤ ∑ c ∈ C, (hball R c).card := card_biUnion_le
    _ = C.card * (hball R (0 : Fin n → ZMod q)).card := by
        simp [card_hball]

/-- (1) com volume abstrato `V`. -/
theorem partial_cover_bound_V (R V : ℕ) (hV : (hball R (0 : Fin n → ZMod q)).card = V)
    (T C : Finset (Fin n → ZMod q)) (h : ∀ x ∈ T, ∃ c ∈ C, hammingDist x c ≤ R) :
    T.card ≤ C.card * V := hV ▸ partial_cover_bound R T C h

theorem card_coveredSet_le (R V : ℕ) (hV : (hball R (0 : Fin n → ZMod q)).card = V)
    (C : Finset (Fin n → ZMod q)) : (coveredSet R C).card ≤ C.card * V :=
  partial_cover_bound_V R V hV _ C (fun x hx => by simpa [coveredSet] using hx)

/-! ### (2) Forma de fronteira -/

/-- `C` cobre pelo menos `M` palavras. -/
def Achieves (R M : ℕ) (C : Finset (Fin n → ZMod q)) : Prop := M ≤ (coveredSet R C).card

/-- (2a) Se `C` cobre `>= M` palavras, entao `M <= |C| * V`, logo `|C| >= ceil(M/V)`. -/
theorem frontier_bound_nat (R V : ℕ) (hV : (hball R (0 : Fin n → ZMod q)).card = V)
    (M : ℕ) (C : Finset (Fin n → ZMod q)) (h : Achieves R M C) :
    M ≤ C.card * V ∧ ⌈(M : ℚ) / V⌉₊ ≤ C.card := by
  have hVpos : 0 < V := hV ▸ card_hball_pos R
  have h1 : M ≤ C.card * V := h.trans (card_coveredSet_le R V hV C)
  refine ⟨h1, Nat.ceil_le.2 ?_⟩
  rw [div_le_iff₀ (by exact_mod_cast hVpos)]
  exact_mod_cast h1

/-- Cobrir `>= x` palavras (real) equivale a cobrir `>= ceil x` (inteiro): a contagem e inteira. -/
theorem cover_real_iff_nat (R : ℕ) (C : Finset (Fin n → ZMod q)) (x : ℚ) :
    x ≤ ((coveredSet R C).card : ℚ) ↔ Achieves R ⌈x⌉₊ C := by
  unfold Achieves
  exact (Nat.ceil_le).symm

/-- `ceil(ceil(x)/V) = ceil(x/V)` para `V >= 1`: usar `M` inteiro nao muda a cota. -/
theorem ceil_ceil_div (x : ℚ) (V : ℕ) (hV : 0 < V) : ⌈(⌈x⌉₊ : ℚ) / V⌉₊ = ⌈x / V⌉₊ := by
  have hVq : (0 : ℚ) < V := by exact_mod_cast hV
  refine eq_of_forall_ge_iff fun k => ?_
  rw [Nat.ceil_le, Nat.ceil_le, div_le_iff₀ hVq, div_le_iff₀ hVq]
  have : (⌈x⌉₊ : ℚ) ≤ (k : ℚ) * V ↔ ⌈x⌉₊ ≤ k * V := by exact_mod_cast Iff.rfl
  rw [this, Nat.ceil_le]
  push_cast
  rfl

/-- (2b) A cota do doc: `C` cobre `>= (1-eps) q^n` palavras `⇒ |C| >= ceil((1-eps) * S)`,
`S = q^n / V`. Vale para qualquer `eps : ℚ` (sem hipotese de intervalo). -/
theorem frontier_bound_rat (R V : ℕ) (hV : (hball R (0 : Fin n → ZMod q)).card = V)
    (ε : ℚ) (C : Finset (Fin n → ZMod q))
    (h : (1 - ε) * (q : ℚ) ^ n ≤ ((coveredSet R C).card : ℚ)) :
    ⌈(1 - ε) * ((q : ℚ) ^ n / V)⌉₊ ≤ C.card := by
  have hVpos : 0 < V := hV ▸ card_hball_pos R
  have hVq : (0 : ℚ) < V := by exact_mod_cast hVpos
  have h1 : (coveredSet R C).card ≤ C.card * V := card_coveredSet_le R V hV C
  refine Nat.ceil_le.2 ?_
  have h2 : (1 - ε) * (q : ℚ) ^ n ≤ (C.card : ℚ) * V := by
    refine h.trans ?_
    exact_mod_cast h1
  rw [← mul_div_assoc, div_le_iff₀ hVq]
  exact h2

/-- (2b') Idem na forma `M = ceil((1-eps) q^n)`: `|C| >= ceil(M/V)` e `= ceil((1-eps)S)`. -/
theorem frontier_bound_M (R V : ℕ) (hV : (hball R (0 : Fin n → ZMod q)).card = V)
    (ε : ℚ) (C : Finset (Fin n → ZMod q))
    (h : Achieves R ⌈(1 - ε) * (q : ℚ) ^ n⌉₊ C) :
    ⌈(⌈(1 - ε) * (q : ℚ) ^ n⌉₊ : ℚ) / V⌉₊ = ⌈(1 - ε) * ((q : ℚ) ^ n / V)⌉₊ ∧
    ⌈(1 - ε) * ((q : ℚ) ^ n / V)⌉₊ ≤ C.card := by
  have hVpos : 0 < V := hV ▸ card_hball_pos R
  refine ⟨?_, frontier_bound_rat R V hV ε C ((cover_real_iff_nat R C _).2 h)⟩
  rw [ceil_ceil_div _ V hVpos, mul_div_assoc]

/-! ### (3) Monotonicidade da fronteira -/

/-- (3a) Cobrir `>= M` palavras implica cobrir `>= M'` para `M' <= M`. -/
theorem achieves_anti {R M M' : ℕ} {C : Finset (Fin n → ZMod q)} (hM : M' ≤ M)
    (h : Achieves R M C) : Achieves R M' C := hM.trans h

/-- (3b) O tamanho minimo e nao crescente em `M`: se `k` e minimo para `M` e `k'` minimo para
`M' <= M`, entao `k' <= k`. -/
theorem least_size_antitone {R M M' k k' : ℕ} (hM : M' ≤ M)
    (hk : IsLeast {k : ℕ | ∃ C : Finset (Fin n → ZMod q), C.card = k ∧ Achieves R M C} k)
    (hk' : IsLeast {k : ℕ | ∃ C : Finset (Fin n → ZMod q), C.card = k ∧ Achieves R M' C} k') :
    k' ≤ k := by
  obtain ⟨C, hCk, hC⟩ := hk.1
  exact hk'.2 ⟨C, hCk, achieves_anti hM hC⟩

/-- Fronteira em `eps`: existe codigo de tamanho `k` cobrindo `>= (1-eps) q^n` palavras. -/
def AchievesEps (R : ℕ) (ε : ℚ) (k : ℕ) : Prop :=
  ∃ C : Finset (Fin n → ZMod q), C.card = k ∧
    (1 - ε) * (q : ℚ) ^ n ≤ ((coveredSet R C).card : ℚ)

/-- (3c) Monotonicidade em `eps` (estrutural): afrouxar `eps` nao encarece. -/
theorem achievesEps_mono {R : ℕ} {ε ε' : ℚ} {k : ℕ} (hε : ε ≤ ε')
    (h : AchievesEps (q := q) (n := n) R ε k) : AchievesEps (q := q) (n := n) R ε' k := by
  obtain ⟨C, hC, hcov⟩ := h
  refine ⟨C, hC, le_trans ?_ hcov⟩
  have : (0 : ℚ) ≤ (q : ℚ) ^ n := by positivity
  nlinarith

/-- (3d) Forma limpa: `C(eps)` (minimo) e nao crescente em `eps`. -/
theorem least_eps_antitone {R : ℕ} {ε ε' : ℚ} {k k' : ℕ} (hε : ε ≤ ε')
    (hk : IsLeast {k | AchievesEps (q := q) (n := n) R ε k} k)
    (hk' : IsLeast {k | AchievesEps (q := q) (n := n) R ε' k} k') : k' ≤ k :=
  hk'.2 (achievesEps_mono hε hk.1)

/-- Para `eps in [0,1]` o conjunto e nao vazio (o codigo cheio cobre tudo), logo o minimo
existe. Para `eps > 1` o conjunto e vazio ou trivial, por isso o intervalo no enunciado. -/
theorem exists_least_of_eps (R : ℕ) (ε : ℚ) (h0 : 0 ≤ ε) :
    ∃ k, IsLeast {k | AchievesEps (q := q) (n := n) R ε k} k := by
  have hne : {k | AchievesEps (q := q) (n := n) R ε k}.Nonempty := by
    refine ⟨(univ : Finset (Fin n → ZMod q)).card, univ, rfl, ?_⟩
    have hall : coveredSet R (univ : Finset (Fin n → ZMod q)) = univ := by
      ext x
      simp only [coveredSet, mem_filter, mem_univ, true_and, iff_true]
      exact ⟨x, by simp⟩
    rw [hall, card_univ]
    have : (Fintype.card (Fin n → ZMod q) : ℚ) = (q : ℚ) ^ n := by
      simp [Fintype.card_fun, ZMod.card]
    rw [this]
    have : (0 : ℚ) ≤ (q : ℚ) ^ n := by positivity
    nlinarith
  exact ⟨sInf _, Nat.sInf_mem hne, fun k hk => Nat.sInf_le hk⟩

/-- `eps = 1`: o minimo e `0` (codigo vazio), e a cota `ceil(0 * S) = 0` e justa. -/
theorem eps_one_least (R : ℕ) :
    IsLeast {k | AchievesEps (q := q) (n := n) R 1 k} 0 := by
  refine ⟨⟨∅, rfl, ?_⟩, fun k _ => Nat.zero_le k⟩
  simp

/-! ### Limiar de factibilidade: `P(theta) = inf { eps : C_theta(eps) < oo }` -/

/-- `inf_x D x = inf { eps | ∃ x, D x <= eps }` (nao estrito). Com `Cost` finito, `C(eps) < oo`
equivale a `∃ x, D x <= eps`, e e isso que o doc afirma. -/
theorem P_eq_feasibility_threshold {F : Type*} [Nonempty F] (D : F → ℝ)
    (hb : BddBelow (Set.range D)) :
    sInf (Set.range D) = sInf {ε : ℝ | ∃ x, D x ≤ ε} := by
  have hbS : BddBelow {ε : ℝ | ∃ x, D x ≤ ε} := by
    obtain ⟨b, hb'⟩ := hb
    exact ⟨b, fun ε ⟨x, hx⟩ => (hb' ⟨x, rfl⟩).trans hx⟩
  have hne : (Set.range D).Nonempty := Set.range_nonempty D
  apply le_antisymm
  · refine le_csInf ⟨D (Classical.arbitrary F), _, le_rfl⟩ ?_
    rintro ε ⟨x, hx⟩
    exact (csInf_le hb ⟨x, rfl⟩).trans hx
  · exact csInf_le_csInf hbS hne (fun y ⟨x, hx⟩ => ⟨x, hx.le⟩)

/-! ### Estresse: q=2, n=3, R=1 (codigo perfeito) e q=2, n=4, R=1 -/

theorem V_n3 : (hball 1 (0 : Fin 3 → ZMod 2)).card = 4 := by decide +kernel
theorem V_n4 : (hball 1 (0 : Fin 4 → ZMod 2)).card = 5 := by decide +kernel

/-- `(M+3)/4` e mesmo `ceil(M/V)` com `V = 4`. -/
theorem div_eq_ceil (M : ℕ) : (M + 3) / 4 = ⌈(M : ℚ) / 4⌉₊ := by
  refine eq_of_forall_ge_iff fun k => ?_
  rw [Nat.ceil_le, div_le_iff₀ (by norm_num)]
  have : (M : ℚ) ≤ (k : ℚ) * 4 ↔ M ≤ k * 4 := by exact_mod_cast Iff.rfl
  rw [this]
  omega


end CoveringA5

#print axioms CoveringA5.partial_cover_bound
#print axioms CoveringA5.partial_cover_bound_V
#print axioms CoveringA5.frontier_bound_nat
#print axioms CoveringA5.frontier_bound_rat
#print axioms CoveringA5.frontier_bound_M
#print axioms CoveringA5.cover_real_iff_nat
#print axioms CoveringA5.ceil_ceil_div
#print axioms CoveringA5.least_size_antitone
#print axioms CoveringA5.least_eps_antitone
#print axioms CoveringA5.exists_least_of_eps
#print axioms CoveringA5.eps_one_least
#print axioms CoveringA5.P_eq_feasibility_threshold
#print axioms CoveringA5.div_eq_ceil
