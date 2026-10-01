import Mathlib

/-!
# A4: formas fechadas e controles da teoria de códigos de cobertura

Espaço `Fin n → ZMod q` (`[NeZero q]`), distância de Hamming de Mathlib.

* (1) `R ≥ n` : uma palavra cobre (`K = 1`), e zero palavras nunca cobrem.
* (2) `K_q(n, n-1) = q` para `n ≥ 1`.
* (3) Controles: monotonia em `R`; `K_q(n+1, R+1) ≤ K_q(n, R)`.
* (4) Estresse: casos pequenos checados no kernel (`decide +kernel`), para mostrar que os
  enunciados acima não são vácuos nem têm erro de um.
-/

namespace CoveringA4

/-- Cobertura: toda palavra está a distância `≤ R` de alguma palavra de `C`. -/
def Covers {q : ℕ} (n R : ℕ) (C : Finset (Fin n → ZMod q)) : Prop :=
  ∀ x : Fin n → ZMod q, ∃ c ∈ C, hammingDist x c ≤ R

/-- Existe código de cobertura de raio `R` com no máximo `m` palavras. -/
def Kle (n q R m : ℕ) : Prop :=
  ∃ C : Finset (Fin n → ZMod q), Covers n R C ∧ C.card ≤ m

instance {q n R : ℕ} [NeZero q] (C : Finset (Fin n → ZMod q)) : Decidable (Covers n R C) := by
  unfold Covers; infer_instance

variable {q : ℕ} [NeZero q]

/-! ## (1) raio ≥ n -/

/-- Código vazio nunca cobre: o espaço é não vazio. -/
theorem not_covers_empty (n R : ℕ) : ¬ Covers (q := q) n R ∅ := by
  intro h
  obtain ⟨c, hc, _⟩ := h 0
  simp at hc

/-- Nenhum código com 0 palavras cobre (K ≥ 1). -/
theorem not_Kle_zero (n R : ℕ) : ¬ Kle n q R 0 := by
  rintro ⟨C, hC, hcard⟩
  have : C = ∅ := Finset.card_eq_zero.mp (Nat.le_zero.mp hcard)
  subst this
  exact not_covers_empty n R hC

/-- Com `R ≥ n`, uma única palavra (a nula) cobre tudo. -/
theorem covers_singleton_of_le {n R : ℕ} (h : n ≤ R) :
    Covers (q := q) n R {0} := by
  intro x
  refine ⟨0, Finset.mem_singleton_self _, ?_⟩
  exact (hammingDist_le_card_fintype).trans (by simpa using h)

/-- (1) `K = 1` quando `R ≥ n`: uma palavra basta e zero não bastam. -/
theorem K_eq_one_of_le {n R : ℕ} (h : n ≤ R) :
    Kle n q R 1 ∧ ∀ m, Kle n q R m → 1 ≤ m := by
  refine ⟨⟨{0}, covers_singleton_of_le h, by simp⟩, ?_⟩
  intro m hm
  by_contra hlt
  have : m = 0 := by omega
  subst this
  exact not_Kle_zero n R hm

/-! ## (2) K_q(n, n-1) = q -/

/-- Se `x` e `c` coincidem em alguma coordenada, a distância é `≤ n - 1`. -/
theorem hammingDist_le_pred_of_agree {n : ℕ} {x c : Fin n → ZMod q} {i : Fin n}
    (h : x i = c i) : hammingDist x c ≤ n - 1 := by
  have hlt : hammingDist x c < n := by
    unfold hammingDist
    have hss : (Finset.univ.filter fun j => x j ≠ c j) ⊂ (Finset.univ : Finset (Fin n)) := by
      refine Finset.ssubset_iff_subset_ne.mpr ⟨Finset.filter_subset _ _, ?_⟩
      intro heq
      have : i ∈ (Finset.univ.filter fun j => x j ≠ c j) := by rw [heq]; exact Finset.mem_univ _
      simp [h] at this
    simpa using Finset.card_lt_card hss
  omega

/-- Se `x` difere de `c` em todas as coordenadas, a distância é exatamente `n`. -/
theorem hammingDist_eq_of_all_ne {n : ℕ} {x c : Fin n → ZMod q}
    (h : ∀ i, x i ≠ c i) : hammingDist x c = n := by
  unfold hammingDist
  rw [Finset.filter_true_of_mem (fun i _ => h i)]
  simp

/-- (2a) `q` palavras (as constantes) cobrem com raio `n - 1`, `n ≥ 1`. -/
theorem Kle_pred_q {n : ℕ} (hn : 1 ≤ n) : Kle n q (n - 1) q := by
  refine ⟨Finset.univ.image (fun a : ZMod q => fun _ : Fin n => a), ?_, ?_⟩
  · intro x
    refine ⟨fun _ => x ⟨0, hn⟩, Finset.mem_image.mpr ⟨_, Finset.mem_univ _, rfl⟩, ?_⟩
    exact hammingDist_le_pred_of_agree (i := ⟨0, hn⟩) rfl
  · calc _ ≤ (Finset.univ : Finset (ZMod q)).card := Finset.card_image_le
      _ = q := by simp [Finset.card_univ, ZMod.card]

/-- (2b) Pombo: com menos de `q` palavras sobra uma palavra a distância `n` de todas. -/
theorem exists_far_word {n : ℕ} (C : Finset (Fin n → ZMod q)) (hC : C.card < q) :
    ∃ x : Fin n → ZMod q, ∀ c ∈ C, hammingDist x c = n := by
  have key : ∀ i : Fin n, ∃ v : ZMod q, ∀ c ∈ C, v ≠ c i := by
    intro i
    by_contra hcon
    push_neg at hcon
    have hsub : (Finset.univ : Finset (ZMod q)) ⊆ C.image (fun c => c i) := by
      intro v _
      obtain ⟨c, hc, hv⟩ := hcon v
      exact Finset.mem_image.mpr ⟨c, hc, hv.symm⟩
    have h1 := Finset.card_le_card hsub
    have h2 : (C.image (fun c => c i)).card ≤ C.card := Finset.card_image_le
    have h3 : (Finset.univ : Finset (ZMod q)).card = q := by simp [Finset.card_univ, ZMod.card]
    omega
  choose v hv using key
  exact ⟨v, fun c hc => hammingDist_eq_of_all_ne (fun i => hv i c hc)⟩

/-- (2b) Todo código de raio `n - 1` (com `n ≥ 1`) tem pelo menos `q` palavras. -/
theorem q_le_of_Kle_pred {n : ℕ} (hn : 1 ≤ n) {m : ℕ} (h : Kle n q (n - 1) m) : q ≤ m := by
  obtain ⟨C, hC, hcard⟩ := h
  by_contra hlt
  push_neg at hlt
  obtain ⟨x, hx⟩ := exists_far_word C (lt_of_le_of_lt hcard hlt)
  obtain ⟨c, hc, hd⟩ := hC x
  rw [hx c hc] at hd
  omega

/-- (2) `K_q(n, n-1) = q` para `n ≥ 1`: o mínimo é atingido e é `q`. -/
theorem K_pred_eq_q {n : ℕ} (hn : 1 ≤ n) :
    Kle n q (n - 1) q ∧ ∀ m, Kle n q (n - 1) m → q ≤ m :=
  ⟨Kle_pred_q hn, fun _ h => q_le_of_Kle_pred hn h⟩

/-! ## (3) Controles -/

/-- Monotonia em `R`. -/
theorem Kle_mono_R {n R m : ℕ} (h : Kle n q R m) : Kle n q (R + 1) m := by
  obtain ⟨C, hC, hcard⟩ := h
  exact ⟨C, fun x => by obtain ⟨c, hc, hd⟩ := hC x; exact ⟨c, hc, hd.trans (Nat.le_succ _)⟩, hcard⟩

/-- `hammingDist` na primeira coordenada: `Fin.cons` separa a coordenada 0 do resto. -/
theorem hammingDist_cons_le {n : ℕ} (a b : ZMod q) (x y : Fin n → ZMod q) :
    hammingDist (Fin.cons a x : Fin (n + 1) → ZMod q) (Fin.cons b y) ≤ hammingDist x y + 1 := by
  unfold hammingDist
  rw [Finset.card_filter, Finset.card_filter, Fin.sum_univ_succ]
  simp only [Fin.cons_zero, Fin.cons_succ]
  have : (if a ≠ b then 1 else 0) ≤ 1 := by split_ifs <;> omega
  omega

/-- Colar o símbolo `0` na frente de cada palavra é injetivo. -/
theorem cons_zero_injective (n : ℕ) :
    Function.Injective (fun c : Fin n → ZMod q => (Fin.cons 0 c : Fin (n + 1) → ZMod q)) := by
  intro c d h
  funext i
  have := congrFun h i.succ
  simpa using this

/-- `K_q(n+1, R+1) ≤ K_q(n, R)`: cola-se um símbolo fixo; a coordenada nova custa 1. -/
theorem Kle_succ_succ {n R m : ℕ} (h : Kle n q R m) : Kle (n + 1) q (R + 1) m := by
  obtain ⟨C, hC, hcard⟩ := h
  refine ⟨C.map ⟨fun c => (Fin.cons 0 c : Fin (n + 1) → ZMod q), cons_zero_injective n⟩, ?_, ?_⟩
  · intro x
    obtain ⟨c, hc, hd⟩ := hC (Fin.tail x)
    refine ⟨Fin.cons 0 c, Finset.mem_map.mpr ⟨c, hc, rfl⟩, ?_⟩
    have hx : x = Fin.cons (x 0) (Fin.tail x) := (Fin.cons_self_tail x).symm
    rw [hx]
    exact (hammingDist_cons_le _ _ _ _).trans (by omega)
  · simpa using hcard

/-! ## (4) Estresse: os enunciados não são vácuos nem têm erro de um -/

/-- n=2, q=3, R=1: 3 palavras bastam (instância de `Kle_pred_q`, sem o teorema geral). -/
theorem stress_3_words : Kle 2 3 1 3 := by
  refine ⟨{![0, 0], ![1, 1], ![2, 2]}, ?_, by decide +kernel⟩
  decide +kernel

/-- n=2, q=3, R=1: 2 palavras NÃO bastam, checado por enumeração no kernel
(todos os `Finset` de `(ZMod 3)^2` com ≤ 2 elementos). -/
theorem stress_2_words_fail : ¬ Kle 2 3 1 2 := by
  rintro ⟨C, hC, hcard⟩
  have : ∀ C : Finset (Fin 2 → ZMod 3), C.card ≤ 2 → ¬ Covers 2 1 C := by decide +kernel
  exact this C hcard hC

/-- Mesmo resultado pelo teorema geral: K_3(2,1) = 3. -/
theorem stress_general : Kle 2 3 1 3 ∧ ¬ Kle 2 3 1 2 :=
  ⟨stress_3_words, stress_2_words_fail⟩

/-- Sem erro de um em `R`: com `R = n - 2 = 0` (n = 2) são necessárias 9 palavras, não 3. -/
theorem stress_radius_off_by_one : ¬ Kle 2 3 0 3 := by
  rintro ⟨C, hC, hcard⟩
  have : ∀ C : Finset (Fin 2 → ZMod 3), C.card ≤ 3 → ¬ Covers 2 0 C := by decide +kernel
  exact this C hcard hC

/-- Sem erro de um em `R` do outro lado: com `R = n = 2` uma palavra basta (e 0 não). -/
theorem stress_R_eq_n : Kle 2 3 2 1 ∧ ¬ Kle 2 3 2 0 :=
  ⟨(K_eq_one_of_le (q := 3) (le_refl 2)).1, not_Kle_zero 2 2⟩

/-- Em `R = n - 1 = 1` (n = 2) uma palavra NÃO basta: separa `R ≥ n` de `R = n - 1`. -/
theorem stress_R_eq_pred_n_needs_more : ¬ Kle 2 3 1 1 := by
  intro h
  have := q_le_of_Kle_pred (q := 3) (n := 2) (by norm_num) (m := 1) h
  omega

end CoveringA4

#print axioms CoveringA4.K_eq_one_of_le
#print axioms CoveringA4.K_pred_eq_q
#print axioms CoveringA4.Kle_mono_R
#print axioms CoveringA4.Kle_succ_succ
#print axioms CoveringA4.stress_general
#print axioms CoveringA4.stress_radius_off_by_one
