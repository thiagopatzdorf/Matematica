import Mathlib
import CoveringLean.A6c_Search

/-!
# A6e: `K_2(6,1) ≥ 11` sem busca e sem hipótese (argumento de excesso)

Substitui a hipótese `refuted 64 7 bm6 nbr6 10 0 = true` de `A6c_Search` por uma contagem dupla.

Para `a ≠ c`, `|B(a) ∩ B(c)| ∈ {0, 2}` (par).  Seja `cnt y = #{c ∈ C | y ∈ B(c)}`.
Para `x ∉ C`, `S x = ∑_{y ∈ B x} cnt y = ∑_{c ∈ C} |B x ∩ B c|` é par e `≥ 7`, logo `≥ 8`;
para `x ∈ C`, `S x ≥ 7`.  Como `∑_x S x = 49 |C|`, vem `49 K + K ≥ 8 · 64`, isto é `K ≥ 11`.

O único fato finito verificado no kernel é a paridade das interseções `B(0) ∩ B(d)`
(64 casos, depois de transladar `a` para `0`) e o volume `7` das bolas.
-/

namespace CoveringA6

open Finset

section Abstract

variable {α : Type*} [Fintype α] [DecidableEq α]

/-- Núcleo da contagem dupla, para qualquer família de "bolas" simétricas de tamanho 7 cujas
interseções entre centros distintos têm cardinal par: `8 · |α| ≤ 50 · |C|`. -/
theorem excess_bound (B : α → Finset α)
    (hcard : ∀ x, (B x).card = 7)
    (hsymm : ∀ x y, y ∈ B x ↔ x ∈ B y)
    (heven : ∀ a c, a ≠ c → Even (B a ∩ B c).card)
    (C : Finset α) (hcov : ∀ x, ∃ c ∈ C, x ∈ B c) :
    8 * Fintype.card α ≤ 50 * C.card := by
  classical
  -- quantas bolas de `C` contêm `y`
  set cnt : α → ℕ := fun y => (C.filter fun c => y ∈ B c).card with hcnt
  have cnt_pos : ∀ y, 1 ≤ cnt y := by
    intro y
    obtain ⟨c, hc, hyc⟩ := hcov y
    exact Finset.card_pos.2 ⟨c, Finset.mem_filter.2 ⟨hc, hyc⟩⟩
  -- `S x = ∑_{y ∈ B x} cnt y = ∑_{c ∈ C} |B x ∩ B c|`
  have hS : ∀ x, ∑ y ∈ B x, cnt y = ∑ c ∈ C, (B x ∩ B c).card := by
    intro x
    simp only [hcnt, Finset.card_filter]
    rw [Finset.sum_comm]
    refine Finset.sum_congr rfl fun c _ => ?_
    rw [← Finset.card_filter, Finset.filter_mem_eq_inter]
  have hS7 : ∀ x, 7 ≤ ∑ y ∈ B x, cnt y := by
    intro x
    calc 7 = ∑ _y ∈ B x, 1 := by simp [hcard x]
      _ ≤ ∑ y ∈ B x, cnt y := Finset.sum_le_sum fun y _ => cnt_pos y
  have hS8 : ∀ x, x ∉ C → 8 ≤ ∑ y ∈ B x, cnt y := by
    intro x hx
    have hev : Even (∑ y ∈ B x, cnt y) := by
      rw [hS x]
      refine Finset.even_sum _ fun c hc => heven x c ?_
      rintro rfl; exact hx hc
    have h7 := hS7 x
    obtain ⟨k, hk⟩ := hev
    omega
  -- `∑_y cnt y = 7 |C|`
  have hsumcnt : ∑ y, cnt y = 7 * C.card := by
    simp only [hcnt, Finset.card_filter]
    rw [Finset.sum_comm]
    calc ∑ c ∈ C, ∑ y, (if y ∈ B c then 1 else 0)
        = ∑ c ∈ C, (B c).card := by
          refine Finset.sum_congr rfl fun c _ => ?_
          rw [← Finset.card_filter, Finset.filter_mem_eq_inter, Finset.univ_inter]
      _ = 7 * C.card := by simp [hcard, mul_comm]
  -- `∑_x S x = 49 |C|`
  have htot : ∑ x, ∑ y ∈ B x, cnt y = 49 * C.card := by
    rw [Finset.sum_comm' (t' := Finset.univ) (s' := fun y => B y)
      (fun x y => by simp [hsymm x y])]
    calc ∑ y, ∑ _x ∈ B y, cnt y = ∑ y, 7 * cnt y := by simp [hcard]
      _ = 7 * ∑ y, cnt y := by rw [Finset.mul_sum]
      _ = 49 * C.card := by rw [hsumcnt]; ring
  -- cada ponto: `S x + [x ∈ C] ≥ 8`
  have hpt : ∀ x, 8 ≤ ∑ y ∈ B x, cnt y + (if x ∈ C then 1 else 0) := by
    intro x
    by_cases hx : x ∈ C
    · have := hS7 x; simp [hx]; omega
    · have := hS8 x hx; simp [hx, this]
  have hsum := Finset.sum_le_sum (s := (Finset.univ : Finset α)) fun x _ => hpt x
  rw [Finset.sum_add_distrib, htot] at hsum
  have hC : ∑ x : α, (if x ∈ C then 1 else 0) = C.card := by
    rw [← Finset.card_filter]; simp
  rw [hC] at hsum
  simp only [Finset.sum_const, Finset.card_univ, smul_eq_mul] at hsum
  omega

end Abstract

/-! ## Instância `W 2 6`, raio 1 -/

/-- Translação preserva a distância de Hamming. -/
theorem hammingDist_sub_right' (x y z : W 2 6) :
    hammingDist (x - z) (y - z) = hammingDist x y := by
  simp [hammingDist]

/-- Translação leva `B(a) ∩ B(c)` em `B(0) ∩ B(c - a)`. -/
theorem inter_card_translate (a c : W 2 6) :
    (ball 1 a ∩ ball 1 c).card = (ball 1 0 ∩ ball 1 (c - a)).card := by
  refine Finset.card_nbij' (fun x => x - a) (fun y => y + a) ?_ ?_ ?_ ?_
  · intro x hx
    simp only [Finset.coe_inter, Set.mem_inter_iff, Finset.mem_coe, ball, Finset.mem_filter,
      Finset.mem_univ, true_and] at hx ⊢
    rw [show (0 : W 2 6) = a - a from (sub_self a).symm, hammingDist_sub_right',
      hammingDist_sub_right']
    exact hx
  · intro y hy
    simp only [Finset.coe_inter, Set.mem_inter_iff, Finset.mem_coe, ball, Finset.mem_filter,
      Finset.mem_univ, true_and] at hy ⊢
    rw [← hammingDist_sub_right' (y + a) a a, ← hammingDist_sub_right' (y + a) c a]
    simpa using hy
  · intro x _; simp
  · intro y _; simp

/-- Fato finito (64 casos): `|B(0) ∩ B(d)|` é par para `d ≠ 0`. -/
theorem even_inter_zero : ∀ d : W 2 6, d ≠ 0 → Even (ball 1 0 ∩ ball 1 d).card := by
  decide +kernel

theorem vol_2_6_1 : HasVol 2 6 1 7 := by decide +kernel

theorem even_inter (a c : W 2 6) (h : a ≠ c) : Even (ball 1 a ∩ ball 1 c).card := by
  rw [inter_card_translate]
  exact even_inter_zero _ fun h0 => h (sub_eq_zero.1 h0).symm

/-- `K_2(6,1) ≥ 11`, incondicional: nenhum código de tamanho `≤ 10` cobre `Fin 6 → Fin 2`
com raio 1.  Mesmo enunciado de `no_cover_2_6_1_le10`, sem a hipótese `refuted … = true`. -/
theorem no_cover_2_6_1_le10_uncond :
    ∀ C : Finset (W 2 6), C.card ≤ 10 → ¬ Covers 1 C := by
  intro C hC hcov
  have h := excess_bound (ball 1)
    (fun x => vol_2_6_1 x)
    (fun x y => by simp [ball, hammingDist_comm])
    even_inter C
    (fun x => by
      obtain ⟨c, hc, hd⟩ := hcov x
      exact ⟨c, hc, by simp [ball, hd]⟩)
  have h64 : Fintype.card (W 2 6) = 64 := by simp
  rw [h64] at h
  omega

/-- Forma "cota inferior": todo código que cobre tem `≥ 11` palavras. -/
theorem K_2_6_1_ge_11 (C : Finset (W 2 6)) (hC : Covers 1 C) : 11 ≤ C.card := by
  by_contra h
  exact no_cover_2_6_1_le10_uncond C (by omega) hC

/-- H2 refutada, agora sem hipótese: gap `K - ⌈S⌉ ≥ 1` em `(2,6,1)` e `= 0` em `(2,7,1)`. -/
theorem H2_counterexample_uncond :
    (∀ C : Finset (W 2 6), C.card < 11 → ¬ Covers 1 C) ∧
    (∃ C : Finset (W 2 6), C.card = 12 ∧ Covers 1 C) ∧
    IsK 2 7 1 16 ∧ HasVol 2 6 1 7 ∧ (2 ^ 6 + 7 - 1) / 7 = 10 ∧ (2 ^ 7 + 8 - 1) / 8 = 16 :=
  ⟨fun C hC => no_cover_2_6_1_le10_uncond C (by omega), ⟨code12, code12_card, code12_covers⟩,
    K_2_7_1, vol_2_6_1, by norm_num, by norm_num⟩

end CoveringA6

#print axioms CoveringA6.excess_bound
#print axioms CoveringA6.no_cover_2_6_1_le10_uncond
#print axioms CoveringA6.K_2_6_1_ge_11
#print axioms CoveringA6.H2_counterexample_uncond
