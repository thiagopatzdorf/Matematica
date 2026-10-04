import Mathlib
import CoveringLean.A2_Sphere
import CoveringLean.C1_CoverCheck
import CoveringLean.K742_Upper

/-!
# Cotas superiores genéricas: `K_q(n,R) ≤ |C|` e regras de construção

Espaço `Fin n → ZMod q` e cobertura `CoveringA2.Covers` (os mesmos de todos os certificados do
repositório). Aqui fica o que serve para **qualquer** célula, de modo que uma cota vinda de
construção vire "célula base certificada + regra", e não uma prova artesanal:

* `UB q n R M`: existe código de raio `R` em `Z_q^n` com no máximo `M` palavras;
  `K q n R := sInf {M | UB q n R M}` e `K_le_card`: `Covers R C → K q n R ≤ C.card`.
* `UB.of_exists`: ponte para a forma `∃ C, C.card = M ∧ Covers R C` dos certificados existentes
  (`CoveringCerts.cert_of_check`, `Syn.*`, `K742.K_7_4_2_le_19`).
* regras: `UB.mono`, `UB.radius_mono`, `UB.univ` (o espaço todo), `UB.large_radius`
  (`n ≤ R ⇒ 1`), `UB.constant_symbol` (palavras constantes, `q(n−R−1) < n ⇒ q`),
  `UB.direct_sum` (`K(n₁+n₂, R₁+R₂) ≤ K(n₁,R₁)·K(n₂,R₂)`), `UB.lengthen_free`
  (`K(n+t, R+t) ≤ K(n,R)`), `UB.lengthen_dummy` (`K(n+t, R) ≤ q^t·K(n,R)`), `UB.puncture`
  (`K(n,R) ≤ K(n+t,R)`) e `UB.project` (projeção de alfabeto, `K_a(n,R) ≤ K_q(n,R)` para
  `a ≤ q`).
* `UB.weaken`: ajusta `n`, `R` e `M` por igualdade/desigualdade numérica, para que um gerador
  encadeie regras só com `by decide` nas condições.

As regras são as clássicas (Cohen–Honkala–Litsyn–Lobstein, *Covering Codes*, cap. 3; mesmas que o
banco Lean do Florath, `florath/covering-codes-lean`, BSD-3, usa com outros tipos); as provas
abaixo foram escritas aqui para estes tipos. Sem `sorry`, sem `native_decide`; axiomas no fim.
-/

open Finset CoveringA2

namespace CoveringUB

/-- Existe código de raio `R` em `Z_q^n` com no máximo `M` palavras: `K_q(n,R) ≤ M`. -/
def UB (q n R M : ℕ) : Prop :=
  ∃ C : Finset (Fin n → ZMod q), C.card ≤ M ∧ Covers R C

/-- O número de cobertura `K_q(n,R)`. -/
noncomputable def K (q n R : ℕ) : ℕ := sInf {M | UB q n R M}

theorem K_le {q n R M : ℕ} (h : UB q n R M) : K q n R ≤ M := Nat.sInf_le h

/-- **Teorema genérico**: todo código que cobre dá `K_q(n,R) ≤ |C|`. -/
theorem K_le_card {q n R : ℕ} {C : Finset (Fin n → ZMod q)} (hC : Covers R C) :
    K q n R ≤ C.card :=
  K_le ⟨C, le_rfl, hC⟩

/-- Ponte com a forma dos certificados existentes. -/
theorem UB.of_exists {q n R M : ℕ} (h : ∃ C : Finset (Fin n → ZMod q), C.card = M ∧ Covers R C) :
    UB q n R M := by
  obtain ⟨C, hc, hC⟩ := h
  exact ⟨C, hc.le, hC⟩

theorem UB.mono {q n R M M' : ℕ} (h : UB q n R M) (hM : M ≤ M') : UB q n R M' := by
  obtain ⟨C, hc, hC⟩ := h
  exact ⟨C, hc.trans hM, hC⟩

theorem UB.radius_mono {q n R R' M : ℕ} (h : UB q n R M) (hR : R ≤ R') : UB q n R' M := by
  obtain ⟨C, hc, hC⟩ := h
  exact ⟨C, hc, fun x => (hC x).imp fun c ⟨hc, hd⟩ => ⟨hc, hd.trans hR⟩⟩

/-- Troca `n` por um igual e afrouxa `R` e `M`: a cola entre regras num certificado gerado. -/
theorem UB.weaken {q n n' R R' M M' : ℕ} (h : UB q n R M) (hn : n = n') (hR : R ≤ R')
    (hM : M ≤ M') : UB q n' R' M' := by
  subst hn
  exact (h.radius_mono hR).mono hM

/-- Witness explícito pequeno: a lista de índices passa no verificador do kernel
(`CoveringCerts.check`, `C1_CoverCheck.lean`). -/
theorem UB.of_check {q n R M : ℕ} [NeZero q] {L : List ℕ} (h : CoveringCerts.check q n R L = true)
    (hM : L.length ≤ M) : UB q n R M :=
  (UB.of_exists (CoveringCerts.cert_of_check rfl h)).mono hM

/-! ## Células base sem witness explícito -/

/-- O espaço inteiro cobre com raio 0. -/
theorem UB.univ (q n R : ℕ) [NeZero q] : UB q n R (q ^ n) :=
  ⟨Finset.univ, by rw [Finset.card_univ, card_space], fun x => ⟨x, Finset.mem_univ _, by simp⟩⟩

/-- `K` é atingido: para `q > 0` o espaço todo cobre, então o ínfimo é um mínimo. -/
theorem UB.K_spec (q n R : ℕ) [NeZero q] : UB q n R (K q n R) :=
  Nat.sInf_mem (s := {M | UB q n R M}) ⟨q ^ n, UB.univ q n R⟩

theorem K_le_iff {q n R M : ℕ} [NeZero q] : K q n R ≤ M ↔ UB q n R M :=
  ⟨fun h => (UB.K_spec q n R).mono h, K_le⟩

/-- Raio grande: com `n ≤ R`, uma palavra cobre tudo. -/
theorem UB.large_radius {q n R : ℕ} (h : n ≤ R) : UB q n R 1 :=
  ⟨{0}, by simp, fun x => ⟨0, Finset.mem_singleton_self _,
    (hammingDist_le_card_fintype.trans (by simp)).trans h⟩⟩

/-- Palavras constantes: se `q(n−R−1) < n`, algum símbolo aparece em mais de `n−R−1`
coordenadas de `x` (pombal), e a palavra constante desse símbolo fica a distância `≤ R`. -/
theorem UB.constant_symbol {q n R : ℕ} [NeZero q] (h : q * (n - R - 1) < n) : UB q n R q := by
  refine ⟨Finset.univ.image fun a : ZMod q => fun _ : Fin n => a, ?_, fun x => ?_⟩
  · exact Finset.card_image_le.trans (by simp [ZMod.card])
  · obtain ⟨a, -, ha⟩ := Finset.exists_lt_card_fiber_of_mul_lt_card_of_maps_to
      (s := (Finset.univ : Finset (Fin n))) (t := (Finset.univ : Finset (ZMod q))) (f := x)
      (n := n - R - 1) (fun _ _ => Finset.mem_univ _) (by simpa [ZMod.card] using h)
    refine ⟨fun _ => a, Finset.mem_image_of_mem _ (Finset.mem_univ _), ?_⟩
    have hsplit := Finset.card_filter_add_card_filter_not
      (s := (Finset.univ : Finset (Fin n))) (fun i => x i = a)
    simp only [Finset.card_univ, Fintype.card_fin] at hsplit
    have : hammingDist x (fun _ => a) = (Finset.univ.filter fun i => ¬ x i = a).card := rfl
    omega

/-! ## Regras -/

theorem hammingDist_append {q n₁ n₂ : ℕ} (a c : Fin n₁ → ZMod q) (b d : Fin n₂ → ZMod q) :
    hammingDist (Fin.append a b) (Fin.append c d) = hammingDist a c + hammingDist b d := by
  simp only [hammingDist, Finset.card_filter]
  rw [Fin.sum_univ_add]
  simp [Fin.append_left, Fin.append_right]

/-- **Soma direta**: `K_q(n₁+n₂, R₁+R₂) ≤ K_q(n₁,R₁) · K_q(n₂,R₂)`. -/
theorem UB.direct_sum {q n₁ n₂ R₁ R₂ M₁ M₂ : ℕ} (h₁ : UB q n₁ R₁ M₁) (h₂ : UB q n₂ R₂ M₂) :
    UB q (n₁ + n₂) (R₁ + R₂) (M₁ * M₂) := by
  obtain ⟨C₁, hc₁, hC₁⟩ := h₁
  obtain ⟨C₂, hc₂, hC₂⟩ := h₂
  refine ⟨(C₁ ×ˢ C₂).image fun p => Fin.append p.1 p.2, ?_, fun x => ?_⟩
  · exact Finset.card_image_le.trans (by rw [Finset.card_product]; exact Nat.mul_le_mul hc₁ hc₂)
  · obtain ⟨c₁, hm₁, hd₁⟩ := hC₁ fun i => x (Fin.castAdd n₂ i)
    obtain ⟨c₂, hm₂, hd₂⟩ := hC₂ fun i => x (Fin.natAdd n₁ i)
    refine ⟨Fin.append c₁ c₂, Finset.mem_image.2 ⟨(c₁, c₂), Finset.mem_product.2 ⟨hm₁, hm₂⟩, rfl⟩, ?_⟩
    rw [← Fin.append_castAdd_natAdd (f := x), hammingDist_append]
    exact Nat.add_le_add hd₁ hd₂

/-- **Alongamento livre**: `K_q(n+t, R+t) ≤ K_q(n,R)`. -/
theorem UB.lengthen_free {q n R M : ℕ} (t : ℕ) (h : UB q n R M) : UB q (n + t) (R + t) M := by
  simpa using h.direct_sum (UB.large_radius (q := q) (n := t) (R := t) le_rfl)

/-- **Coordenada muda**: `K_q(n+t, R) ≤ q^t · K_q(n,R)`. -/
theorem UB.lengthen_dummy {q n R M : ℕ} [NeZero q] (t : ℕ) (h : UB q n R M) :
    UB q (n + t) R (M * q ^ t) := by
  simpa using h.direct_sum (UB.univ q t 0)

/-- **Punção**: apagar `t` coordenadas não aumenta o raio, `K_q(n,R) ≤ K_q(n+t,R)`. -/
theorem UB.puncture {q n R M : ℕ} (t : ℕ) (h : UB q (n + t) R M) : UB q n R M := by
  obtain ⟨C, hc, hC⟩ := h
  refine ⟨C.image fun c i => c (Fin.castAdd t i), Finset.card_image_le.trans hc, fun x => ?_⟩
  obtain ⟨c, hm, hd⟩ := hC (Fin.append x 0)
  refine ⟨fun i => c (Fin.castAdd t i), Finset.mem_image_of_mem _ hm, ?_⟩
  rw [← Fin.append_castAdd_natAdd (f := c), hammingDist_append] at hd
  exact le_trans (Nat.le_add_right _ _) hd

/-- **Projeção de alfabeto**: para `a ≤ q`, `K_a(n,R) ≤ K_q(n,R)` (símbolos `≥ a` viram `a−1`). -/
theorem UB.project {a q n R M : ℕ} [NeZero a] (ha : a ≤ q) (h : UB q n R M) : UB a n R M := by
  obtain ⟨C, hc, hC⟩ := h
  let φ : ZMod q → ZMod a := fun s => ((min s.val (a - 1) : ℕ) : ZMod a)
  have hφ : ∀ y : ZMod a, φ ((y.val : ℕ) : ZMod q) = y := by
    intro y
    have hy : y.val < a := ZMod.val_lt y
    have hq : NeZero q := ⟨by have := NeZero.ne a; omega⟩
    simp only [φ, ZMod.val_cast_of_lt (hy.trans_le ha), min_eq_left (Nat.le_sub_one_of_lt hy),
      ZMod.natCast_zmod_val]
  refine ⟨C.image fun c i => φ (c i), Finset.card_image_le.trans hc, fun x => ?_⟩
  obtain ⟨c, hm, hd⟩ := hC fun i => ((x i).val : ZMod q)
  refine ⟨fun i => φ (c i), Finset.mem_image_of_mem _ hm, ?_⟩
  have := hammingDist_comp_le_hammingDist (fun _ => φ) (x := fun i => ((x i).val : ZMod q)) (y := c)
  simp only [hφ] at this
  exact this.trans hd

/-! ## Não vacuidade: as regras compõem e batem com valores conhecidos -/

/-- `K_2(3,1) ≤ 2` pelas palavras constantes (`2·1 < 3`). -/
example : UB 2 3 1 2 := UB.constant_symbol (by decide)

/-- `K_3(5,4) ≤ 3`: alongamento livre (`t = 3`) de `K_3(2,1) ≤ 3` (constantes, `3·0 < 2`). -/
example : UB 3 5 4 3 := (UB.constant_symbol (q := 3) (n := 2) (R := 1) (by decide)).lengthen_free 3

/-- A cola numérica: soma direta de `K_2(3,1) ≤ 2` consigo mesma dá `K_2(6,2) ≤ 4`. -/
example : UB 2 6 2 4 :=
  (UB.direct_sum (UB.constant_symbol (q := 2) (n := 3) (R := 1) (by decide))
    (UB.constant_symbol (q := 2) (n := 3) (R := 1) (by decide))).weaken (by decide) le_rfl le_rfl

example : K 2 6 2 ≤ 4 :=
  K_le (UB.direct_sum (UB.constant_symbol (q := 2) (n := 3) (R := 1) (by decide))
    (UB.constant_symbol (q := 2) (n := 3) (R := 1) (by decide)))

/-- Witness explícito pelo verificador do kernel: `{00, 11, 22}` dá `K_3(2,1) ≤ 3`. -/
example : UB 3 2 1 3 := UB.of_check (L := [0, 4, 8]) (by decide +kernel) le_rfl

/-- O certificado existente de `K_7(4,2) ≤ 19` entra pela ponte. -/
theorem K_7_4_2_le_19 : K 7 4 2 ≤ 19 := K_le (UB.of_exists K742.K_7_4_2_le_19)

end CoveringUB

#print axioms CoveringUB.K_le_card
#print axioms CoveringUB.K_le_iff
#print axioms CoveringUB.UB.of_check
#print axioms CoveringUB.K_7_4_2_le_19
#print axioms CoveringUB.UB.of_exists
#print axioms CoveringUB.UB.univ
#print axioms CoveringUB.UB.large_radius
#print axioms CoveringUB.UB.constant_symbol
#print axioms CoveringUB.UB.direct_sum
#print axioms CoveringUB.UB.lengthen_free
#print axioms CoveringUB.UB.lengthen_dummy
#print axioms CoveringUB.UB.puncture
#print axioms CoveringUB.UB.project
