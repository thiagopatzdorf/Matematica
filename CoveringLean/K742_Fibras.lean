import Mathlib
import CoveringLean.A2_Sphere

/-!
# K_7(4,2): Lema 0 (caixas de comprimento 3), Lema 1 (fibras) e a redução a perfis

Formalização de `tools/exatos/k742/README.md`, seções "Lema 0", "Lema 1" e "Perfis".

* `box_fiber_bound` (Lema 0, forma geral): se `D` cobre com raio 1 a caixa `S 0 × S 1 × S 2`
  (as palavras de `D` podem estar fora da caixa) e `|S i| ≥ v`, então para todo `a ∈ S 0`, com
  `s = |{d ∈ D : d 0 = a}|`, vale `(v − s)² + s ≤ |D|`.
* `box_card_ge_18` / `box_card_ge_21`: com `v ≥ 6` toda cobertura tem `≥ 18` palavras; com
  `v ≥ 7`, `≥ 21` (são `K_6(3,1) ≥ 18` e `K_7(3,1) ≥ 21`, na forma de caixa).
* `fiber_card_ge_two` (Lema 1): num código de raio 2 em `Z_7^4` com no máximo 18 palavras,
  toda fibra `{c : c j = a}` tem pelo menos 2 palavras.
* `fiberType_mem_types18` e `profile_mem_profiles18`: com 18 palavras, o vetor de tamanhos de
  fibra de cada coordenada é um dos 5 tipos, e o multiconjunto dos 4 tipos é um dos
  `profiles18.card = 70` perfis (completude da lista de perfis de `encode.py`).

Diferença em relação ao README: no Lema 1 não é preciso trocar os símbolos de fora da caixa por
um símbolo fixo; o Lema 0 já é provado para palavras quaisquer cobrindo a caixa, o que encurta a
formalização sem mudar o argumento.
-/

open Finset

namespace K742

/-! ## Distância de Hamming em coordenadas -/

theorem hammingDist_eq_sum {α : Type*} [DecidableEq α] {n : ℕ} (x y : Fin n → α) :
    hammingDist x y = ∑ i, if x i ≠ y i then 1 else 0 := by
  simp [hammingDist, Finset.card_filter]

theorem hammingDist_fin3 {α : Type*} [DecidableEq α] (x y : Fin 3 → α) :
    hammingDist x y = (if x 0 ≠ y 0 then 1 else 0) + (if x 1 ≠ y 1 then 1 else 0) +
      (if x 2 ≠ y 2 then 1 else 0) := by
  rw [hammingDist_eq_sum, Fin.sum_univ_three]

/-- Separar uma coordenada `j`: a distância é a da coordenada `j` mais a das outras três. -/
theorem hammingDist_succAbove {α : Type*} [DecidableEq α] {n : ℕ} (j : Fin (n + 1))
    (x y : Fin (n + 1) → α) :
    hammingDist x y = (if x j ≠ y j then 1 else 0) +
      hammingDist (x ∘ j.succAbove) (y ∘ j.succAbove) := by
  rw [hammingDist_eq_sum, hammingDist_eq_sum, Fin.sum_univ_succAbove _ j]
  rfl

/-! ## Lema 0: caixas de comprimento 3 -/

section Box

variable {α : Type*} [DecidableEq α]

/-- Núcleo do Lema 0: os pontos `(a, u, w)` com `u, w` fora das projeções da fibra `F(0,a)` só
são cobertos por palavras com `d 0 ≠ a` que concordam em `u` e `w`; logo cada uma cobre no
máximo um deles. -/
theorem box_fiber_core {D : Finset (Fin 3 → α)} {S : Fin 3 → Finset α}
    (hcov : ∀ y : Fin 3 → α, (∀ i, y i ∈ S i) → ∃ d ∈ D, hammingDist y d ≤ 1)
    {a : α} (ha : a ∈ S 0) :
    (S 1 \ (D.filter (fun d => d 0 = a)).image (· 1)) ×ˢ
        (S 2 \ (D.filter (fun d => d 0 = a)).image (· 2)) ⊆
      (D.filter (fun d => ¬ d 0 = a)).image (fun d => (d 1, d 2)) := by
  rintro ⟨u, w⟩ hp
  simp only [mem_product, mem_sdiff, mem_image, mem_filter, not_exists, not_and] at hp
  obtain ⟨⟨hu, hu'⟩, hw, hw'⟩ := hp
  obtain ⟨d, hd, hdist⟩ := hcov ![a, u, w] (by
    intro i; fin_cases i
    · exact ha
    · exact hu
    · exact hw)
  rw [hammingDist_fin3] at hdist
  simp only [Fin.isValue, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.cons_val_two,
    Matrix.head_cons, Matrix.tail_cons] at hdist
  by_cases h0 : d 0 = a
  · have h1 : d 1 ≠ u := fun h => hu' d ⟨hd, h0⟩ h
    have h2 : d 2 ≠ w := fun h => hw' d ⟨hd, h0⟩ h
    have : u ≠ d 1 := fun h => h1 h.symm
    have : w ≠ d 2 := fun h => h2 h.symm
    simp_all
  · have ha0 : a ≠ d 0 := fun h => h0 h.symm
    simp only [ne_eq, ha0, not_false_eq_true, ite_true] at hdist
    have h1 : u = d 1 := by by_contra h; simp [h] at hdist; omega
    have h2 : w = d 2 := by by_contra h; simp [h] at hdist
    exact mem_image.2 ⟨d, mem_filter.2 ⟨hd, h0⟩, by rw [h1, h2]⟩

/-- **Lema 0**, forma geral: `(v − s)² + s ≤ |D|`. -/
theorem box_fiber_bound {D : Finset (Fin 3 → α)} {S : Fin 3 → Finset α} {v : ℕ}
    (hS : ∀ i, v ≤ (S i).card)
    (hcov : ∀ y : Fin 3 → α, (∀ i, y i ∈ S i) → ∃ d ∈ D, hammingDist y d ≤ 1)
    {a : α} (ha : a ∈ S 0) :
    (v - (D.filter (fun d => d 0 = a)).card) * (v - (D.filter (fun d => d 0 = a)).card) +
      (D.filter (fun d => d 0 = a)).card ≤ D.card := by
  have hsub := card_le_card (box_fiber_core hcov ha)
  rw [card_product] at hsub
  have himg := (card_image_le (s := D.filter (fun d => ¬ d 0 = a)) (f := fun d => (d 1, d 2)))
  have hsplit := card_filter_add_card_filter_not (s := D) (fun d : Fin 3 → α => d 0 = a)
  set F := D.filter (fun d => d 0 = a) with hF
  have hT : ∀ i : Fin 3, v - F.card ≤ (S i \ F.image (· i)).card := by
    intro i
    have h1 := le_card_sdiff (F.image (· i)) (S i)
    have h2 : (F.image (· i)).card ≤ F.card := card_image_le
    have := hS i
    omega
  have := Nat.mul_le_mul (hT 1) (hT 2)
  omega

/-- As fibras de uma coordenada são disjuntas: a soma dos seus tamanhos não passa de `|D|`. -/
theorem sum_fiber_le {β : Type*} {D : Finset β} (f : β → α) (T : Finset α) :
    ∑ a ∈ T, (D.filter (fun d => f d = a)).card ≤ D.card := by
  have h := card_eq_sum_card_fiberwise (s := D.filter (fun d => f d ∈ T)) (t := T) (f := f)
    (fun x hx => (mem_filter.1 hx).2)
  have h2 : ∀ a ∈ T, (D.filter (fun d => f d ∈ T)).filter (fun d => f d = a) =
      D.filter (fun d => f d = a) := by
    intro a ha
    ext d; simp only [mem_filter]
    constructor
    · rintro ⟨⟨h1, _⟩, h3⟩; exact ⟨h1, h3⟩
    · rintro ⟨h1, h3⟩; exact ⟨⟨h1, h3 ▸ ha⟩, h3⟩
  rw [Finset.sum_congr rfl (fun a ha => congrArg Finset.card (h2 a ha))] at h
  rw [← h]
  exact card_filter_le _ _

/-- Toda fibra de uma cobertura de caixa com `|D|` pequeno tem `≥ 3` palavras. -/
theorem box_fiber_ge_three {D : Finset (Fin 3 → α)} {S : Fin 3 → Finset α} {v : ℕ}
    (hS : ∀ i, v ≤ (S i).card)
    (hcov : ∀ y : Fin 3 → α, (∀ i, y i ∈ S i) → ∃ d ∈ D, hammingDist y d ≤ 1)
    (hv : (6 ≤ v ∧ D.card ≤ 17) ∨ (7 ≤ v ∧ D.card ≤ 20))
    {a : α} (ha : a ∈ S 0) : 3 ≤ (D.filter (fun d => d 0 = a)).card := by
  have hb := box_fiber_bound hS hcov ha
  set s := (D.filter (fun d => d 0 = a)).card
  by_contra hlt
  push Not at hlt
  rcases hv with ⟨hv, hD⟩ | ⟨hv, hD⟩
  · have h6 : 6 - s ≤ v - s := Nat.sub_le_sub_right hv s
    have := Nat.mul_le_mul h6 h6
    interval_cases s <;> omega
  · have h7 : 7 - s ≤ v - s := Nat.sub_le_sub_right hv s
    have := Nat.mul_le_mul h7 h7
    interval_cases s <;> omega

/-- `K_6(3,1) ≥ 18` na forma de caixa: cobrir uma caixa de lado `≥ 6` com raio 1 exige
18 palavras. -/
theorem box_card_ge_18 {D : Finset (Fin 3 → α)} {S : Fin 3 → Finset α} {v : ℕ}
    (hv : 6 ≤ v) (hS : ∀ i, v ≤ (S i).card)
    (hcov : ∀ y : Fin 3 → α, (∀ i, y i ∈ S i) → ∃ d ∈ D, hammingDist y d ≤ 1) :
    18 ≤ D.card := by
  by_contra hlt
  push Not at hlt
  have h3 : ∀ a ∈ S 0, 3 ≤ (D.filter (fun d => d 0 = a)).card :=
    fun a ha => box_fiber_ge_three hS hcov (Or.inl ⟨hv, by omega⟩) ha
  have hsum := sum_fiber_le (D := D) (fun d => d 0) (S 0)
  have hge : (S 0).card * 3 ≤ ∑ a ∈ S 0, (D.filter (fun d => d 0 = a)).card := by
    rw [← smul_eq_mul, ← sum_const]; exact sum_le_sum h3
  have := hS 0
  omega

/-- `K_7(3,1) ≥ 21` na forma de caixa. -/
theorem box_card_ge_21 {D : Finset (Fin 3 → α)} {S : Fin 3 → Finset α} {v : ℕ}
    (hv : 7 ≤ v) (hS : ∀ i, v ≤ (S i).card)
    (hcov : ∀ y : Fin 3 → α, (∀ i, y i ∈ S i) → ∃ d ∈ D, hammingDist y d ≤ 1) :
    21 ≤ D.card := by
  by_contra hlt
  push Not at hlt
  have h3 : ∀ a ∈ S 0, 3 ≤ (D.filter (fun d => d 0 = a)).card :=
    fun a ha => box_fiber_ge_three hS hcov (Or.inr ⟨hv, by omega⟩) ha
  have hsum := sum_fiber_le (D := D) (fun d => d 0) (S 0)
  have hge : (S 0).card * 3 ≤ ∑ a ∈ S 0, (D.filter (fun d => d 0 = a)).card := by
    rw [← smul_eq_mul, ← sum_const]; exact sum_le_sum h3
  have := hS 0
  omega

end Box

/-! ## Lema 1: fibras de um código de raio 2 em `Z_7^4` -/

/-- Fibra `F(j,a)` de um código. -/
def fiber (C : Finset (Fin 4 → ZMod 7)) (j : Fin 4) (a : ZMod 7) : Finset (Fin 4 → ZMod 7) :=
  C.filter (fun c => c j = a)

/-- Encurtamento: a fibra `F(j,a)` com `s` palavras deixa uma caixa de lado `≥ 7 − s`, nas três
outras coordenadas, coberta com raio 1 pelas projeções das `|C| − s` palavras de fora da
fibra. -/
theorem shorten_covers {C : Finset (Fin 4 → ZMod 7)} (hC : CoveringA2.Covers 2 C)
    (j : Fin 4) (a : ZMod 7) :
    let F := fiber C j a
    let S : Fin 3 → Finset (ZMod 7) := fun i => univ \ F.image (· (j.succAbove i))
    let D := (C.filter (fun c => ¬ c j = a)).image (fun c => c ∘ j.succAbove)
    (∀ i, 7 - F.card ≤ (S i).card) ∧ D.card + F.card ≤ C.card ∧
      ∀ y : Fin 3 → ZMod 7, (∀ i, y i ∈ S i) → ∃ d ∈ D, hammingDist y d ≤ 1 := by
  intro F S D
  refine ⟨?_, ?_, ?_⟩
  · intro i
    have h1 := le_card_sdiff (F.image (· (j.succAbove i))) (univ : Finset (ZMod 7))
    have h2 : (F.image (· (j.succAbove i))).card ≤ F.card := card_image_le
    have h3 : (univ : Finset (ZMod 7)).card = 7 := by simp
    simp only [S]
    omega
  · have h1 : D.card ≤ (C.filter (fun c => ¬ c j = a)).card := card_image_le
    have h2 := card_filter_add_card_filter_not (s := C) (fun c : Fin 4 → ZMod 7 => c j = a)
    simp only [F, fiber]
    omega
  · intro y hy
    obtain ⟨c, hc, hdist⟩ := hC (Fin.insertNth j a y)
    rw [hammingDist_succAbove j] at hdist
    have hxj : Fin.insertNth (α := fun _ => ZMod 7) j a y j = a := by simp
    have hxs : (Fin.insertNth j a y) ∘ j.succAbove = y := by
      ext i; simp [Fin.insertNth_apply_succAbove]
    rw [hxj, hxs] at hdist
    by_cases hcj : c j = a
    · -- `c` está na fibra: difere de `y` nas três coordenadas
      exfalso
      have hcF : c ∈ F := mem_filter.2 ⟨hc, hcj⟩
      have hne : ∀ i, y i ≠ c (j.succAbove i) := by
        intro i h
        have := hy i
        simp only [S, mem_sdiff, mem_univ, true_and, mem_image, not_exists, not_and] at this
        exact this c hcF h.symm
      rw [hammingDist_fin3] at hdist
      simp only [Function.comp_apply, ne_eq, hne 0, hne 1, hne 2, not_false_eq_true,
        ite_true] at hdist
      omega
    · refine ⟨c ∘ j.succAbove, mem_image.2 ⟨c, mem_filter.2 ⟨hc, hcj⟩, rfl⟩, ?_⟩
      have : a ≠ c j := fun h => hcj h.symm
      simp only [ne_eq, this, not_false_eq_true, ite_true] at hdist
      omega

/-- **Lema 1** para `q = 7`: num código de raio 2 em `Z_7^4` com no máximo 18 palavras, toda
fibra tem pelo menos 2 palavras. `s = 0` daria uma caixa de lado 7 coberta por `≤ 18 < 21`
palavras; `s = 1`, uma de lado 6 coberta por `≤ 17 < 18`. -/
theorem fiber_card_ge_two {C : Finset (Fin 4 → ZMod 7)} (hC : CoveringA2.Covers 2 C)
    (hM : C.card ≤ 18) (j : Fin 4) (a : ZMod 7) : 2 ≤ (fiber C j a).card := by
  obtain ⟨hS, hD, hcov⟩ := shorten_covers hC j a
  by_contra hlt
  push Not at hlt
  interval_cases h : (fiber C j a).card
  · have := box_card_ge_21 (v := 7) le_rfl (by simpa [h] using hS) hcov
    omega
  · have := box_card_ge_18 (v := 6) le_rfl (by simpa [h] using hS) hcov
    omega

/-! ## Perfis: a redução código → multiconjunto de tipos -/

/-- Tipo de fibra da coordenada `j`: o multiconjunto dos 7 tamanhos de fibra. -/
def fiberType (C : Finset (Fin 4 → ZMod 7)) (j : Fin 4) : Multiset ℕ :=
  (univ : Finset (ZMod 7)).val.map (fun a => (fiber C j a).card)

/-- Perfil: o multiconjunto dos tipos das 4 coordenadas. -/
def profile (C : Finset (Fin 4 → ZMod 7)) : Multiset (Multiset ℕ) :=
  (univ : Finset (Fin 4)).val.map (fiberType C)

/-- Os 5 tipos de `M = 18` (partições de 18 em 7 partes `≥ 2`), na notação de `encode.py`:
6222222, 5322222, 4422222, 4332222, 3333222. -/
def types18 : Finset (Multiset ℕ) :=
  {{6, 2, 2, 2, 2, 2, 2}, {5, 3, 2, 2, 2, 2, 2}, {4, 4, 2, 2, 2, 2, 2}, {4, 3, 3, 2, 2, 2, 2},
   {3, 3, 3, 3, 2, 2, 2}}

theorem types18_card : types18.card = 5 := by decide

/-- Os perfis de `M = 18`: multiconjuntos de 4 tipos. -/
def profiles18 : Finset (Sym (Multiset ℕ) 4) := types18.sym 4

set_option maxRecDepth 100000 in
/-- São 70, como em `encode.py --listar` e no red team (`perfis_indep.py`). -/
theorem profiles18_card : profiles18.card = 70 := by
  decide +kernel

/-- Combinatória pura: 7 naturais `≥ 2` somando 18 formam um dos 5 tipos. -/
theorem multiset_mem_types18 (m : Multiset ℕ) (hcard : Multiset.card m = 7)
    (hsum : m.sum = 18) (hge : ∀ x ∈ m, 2 ≤ x) : m ∈ types18 := by
  -- todo elemento é ≤ 6: os outros 6 somam ≥ 12
  have hle : ∀ x ∈ m, x ≤ 6 := by
    intro x hx
    obtain ⟨t, rfl⟩ := Multiset.exists_cons_of_mem hx
    have hc : Multiset.card t = 6 := by simpa using hcard
    have ht : Multiset.card t * 2 ≤ t.sum := by
      have := Multiset.card_nsmul_le_sum (s := t) (a := 2)
        (fun y hy => hge y (Multiset.mem_cons_of_mem hy))
      simpa [mul_comm] using this
    simp only [Multiset.sum_cons] at hsum
    omega
  have hsub : m.toFinset ⊆ range 7 := by
    intro x hx
    have := hle x (Multiset.mem_toFinset.1 hx)
    simp; omega
  -- reescrever cardinal, soma e o próprio multiconjunto pelas contagens
  have hcnt : ∑ v ∈ range 7, m.count v = 7 := by
    have h := Multiset.toFinset_sum_count_eq m
    rw [hcard] at h
    exact (sum_subset hsub (fun x _ hx => Multiset.count_eq_zero.2
      (fun h => hx (Multiset.mem_toFinset.2 h)))).symm.trans h
  have hsm : ∑ v ∈ range 7, m.count v * v = 18 := by
    rw [← hsum, Finset.sum_multiset_count]
    simp only [smul_eq_mul]
    exact (sum_subset hsub (fun x _ hx => by
      rw [Multiset.count_eq_zero.2 (fun h => hx (Multiset.mem_toFinset.2 h)), zero_mul])).symm
  have hm : m = ∑ v ∈ range 7, m.count v • ({v} : Multiset ℕ) := by
    conv_lhs => rw [← Multiset.toFinset_sum_count_nsmul_eq m]
    exact sum_subset hsub (fun x _ hx => by
      rw [Multiset.count_eq_zero.2 (fun h => hx (Multiset.mem_toFinset.2 h)), zero_nsmul])
  have h0 : m.count 0 = 0 := Multiset.count_eq_zero.2 (fun h => by have := hge 0 h; omega)
  have h1 : m.count 1 = 0 := Multiset.count_eq_zero.2 (fun h => by have := hge 1 h; omega)
  simp only [sum_range_succ, sum_range_zero, h0, h1] at hcnt hsm hm
  rw [hm]
  have b6 : m.count 6 ≤ 1 := by omega
  have b5 : m.count 5 ≤ 1 := by omega
  have b4 : m.count 4 ≤ 2 := by omega
  have b3 : m.count 3 ≤ 4 := by omega
  have b2 : m.count 2 ≤ 7 := by omega
  generalize m.count 2 = n2 at *
  generalize m.count 3 = n3 at *
  generalize m.count 4 = n4 at *
  generalize m.count 5 = n5 at *
  generalize m.count 6 = n6 at *
  interval_cases n6 <;> interval_cases n5 <;> interval_cases n4 <;> interval_cases n3 <;>
    interval_cases n2 <;> first | omega | decide

/-- O vetor de fibras de cada coordenada soma `|C|`. -/
theorem fiberType_sum (C : Finset (Fin 4 → ZMod 7)) (j : Fin 4) :
    (fiberType C j).sum = C.card := by
  rw [fiberType, Finset.sum_map_val]
  exact (card_eq_sum_card_fiberwise (s := C) (t := univ) (f := fun c => c j)
    (fun _ _ => mem_univ _)).symm

/-- **Redução código → tipo**: num código de raio 2 em `Z_7^4` com 18 palavras, o vetor de
tamanhos de fibra de cada coordenada é um dos 5 tipos de `types18`. -/
theorem fiberType_mem_types18 {C : Finset (Fin 4 → ZMod 7)} (hC : CoveringA2.Covers 2 C)
    (hM : C.card = 18) (j : Fin 4) : fiberType C j ∈ types18 := by
  apply multiset_mem_types18
  · simp [fiberType]
  · rw [fiberType_sum, hM]
  · intro x hx
    obtain ⟨a, -, rfl⟩ := Multiset.mem_map.1 hx
    exact fiber_card_ge_two hC hM.le j a

/-- **Completude da lista de perfis**: o perfil de qualquer código de raio 2 em `Z_7^4` com 18
palavras é um dos 70 perfis de `profiles18`. -/
theorem profile_mem_profiles18 {C : Finset (Fin 4 → ZMod 7)} (hC : CoveringA2.Covers 2 C)
    (hM : C.card = 18) :
    ∃ P ∈ profiles18, (P : Multiset (Multiset ℕ)) = profile C := by
  refine ⟨⟨profile C, by simp [profile]⟩, ?_, rfl⟩
  refine Finset.mem_sym_iff.2 (fun t ht => ?_)
  obtain ⟨j, -, rfl⟩ := Multiset.mem_map.1 (show t ∈ profile C from ht)
  exact fiberType_mem_types18 hC hM j

end K742

#print axioms K742.box_fiber_bound
#print axioms K742.box_card_ge_18
#print axioms K742.box_card_ge_21
#print axioms K742.shorten_covers
#print axioms K742.fiber_card_ge_two
#print axioms K742.multiset_mem_types18
#print axioms K742.fiberType_mem_types18
#print axioms K742.profiles18_card
#print axioms K742.profile_mem_profiles18
