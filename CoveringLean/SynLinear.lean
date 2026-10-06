import Mathlib
import CoveringLean.SynBridge

/-!
# SynLinear: cota superior por código linear em forma sistemática, sem a lista do código

`Syn.lin_cert` é o caso linear puro do certificado por síndromes de `SynBridge.lean`: o código é
`C₀ = {m·G : m < q^k}`, com `G` (as `k` linhas de `P.Gs`) igual à identidade no bloco
`[o, o+k)`. Não há lista `L` nem remendo:

* `|C₀| = q^k`, porque o bloco de informação devolve a mensagem (`m ↦ m·G` é injetiva);
* `C₀` cobre com raio `R` se cada ponto `y_t` do transversal (nulo no bloco, `q^(n-k)` pontos)
  tem uma testemunha `m` com `d(m·G, y_t) ≤ R` (`okT` com um único coset, o nulo).

É o que basta para as cotas que as tabelas do Kéri marcam como "código linear", "código de
Hamming" ou "código perfeito" (Golay): o kernel confere `q^(n-k)` pontos e `k²` dígitos, nunca
os `q^n · q^k` pares que um witness explícito exigiria.

Funciona sobre `ZMod q` com `q` qualquer (anel, não precisa ser corpo): a prova só usa que o
código é imagem de uma aplicação aditiva com bloco identidade.

Sem `sorry`, sem `native_decide`, sem axioma novo.
-/

namespace Syn

open CoveringKernel CoveringCerts

/-- Se toda linha tem dígito `0` na coordenada `i`, `S` é `0` ali. -/
theorem S_zero (q i : ℕ) : ∀ (Gs : List ℕ) (m : ℕ),
    (∀ j < Gs.length, D q (Gs.getD j 0) i = 0) → S q Gs m i = 0 := by
  intro Gs
  induction Gs with
  | nil => intro _ _; rfl
  | cons g gs ih =>
    intro m h
    have h0 : D q g i = 0 := by simpa using h 0 (by simp)
    rw [S_cons, h0, ih (m / q) (fun j hj => by
      simpa using h (j + 1) (by simp; omega))]
    simp

/-- Coluna unitária: se a coordenada `i` de `G` é o vetor unitário `l`, então `(m·G)ᵢ` é o
dígito `l` de `m` (por que importa: é o que deixa ler a mensagem no bloco de informação). -/
theorem S_unit {q : ℕ} (i : ℕ) : ∀ (Gs : List ℕ) (m l : ℕ), l < Gs.length →
    (∀ j < Gs.length, D q (Gs.getD j 0) i = if j = l then 1 else 0) → S q Gs m i = D q m l := by
  intro Gs
  induction Gs with
  | nil => intro _ l hl; simp at hl
  | cons g gs ih =>
    intro m l hl h
    rw [S_cons]
    cases l with
    | zero =>
      have h0 : D q g i = 1 := by simpa using h 0 (by simp)
      rw [h0, S_zero q i gs (m / q) (fun j hj => by simpa using h (j + 1) (by simp; omega)),
        D_zero]
      ring
    | succ l =>
      have h0 : D q g i = 0 := by simpa using h 0 (by simp)
      rw [h0, ih (m / q) l (by simpa using hl) (fun j hj => by
        simpa using h (j + 1) (by simp; omega)), D_succ]
      ring

theorem enc_congr (q : ℕ) : ∀ (n : ℕ) (f g : ℕ → ℕ), (∀ i < n, f i = g i) → enc q f n = enc q g n := by
  intro n
  induction n with
  | zero => intro _ _ _; rfl
  | succ n ih =>
    intro f g h
    rw [enc_succ, enc_succ, h 0 (by omega), ih _ _ (fun i hi => h (i + 1) (by omega))]

/-- Um número `< q^k` é a codificação dos seus `k` dígitos. -/
theorem enc_D {q : ℕ} (hq : 0 < q) : ∀ (k m : ℕ), m < q ^ k → enc q (D q m) k = m := by
  intro k
  induction k with
  | zero => intro m hm; simp at hm; simp [enc, hm]
  | succ k ih =>
    intro m hm
    rw [enc_succ, enc_congr q k (fun i => D q m (i + 1)) (D q (m / q)) (fun i _ => D_succ q m i),
      ih (m / q) (by rw [Nat.div_lt_iff_lt_mul hq]; rw [pow_succ] at hm; exact hm), D_zero]
    exact Nat.mod_add_div m q

/-- Código linear sistemático `[n, k]_q` com raio de cobertura `R`, sem lista: `q^k` palavras. -/
theorem lin_cert {q n R M : ℕ} [NeZero q] (P : Spec)
    (hq : P.q = q) (hn : P.n = n) (hR : P.R = R) (hM : q ^ P.k = M)
    (hdim : P.Gs.length = P.k ∧ P.o + P.k ≤ P.n)
    (hunit : ∀ j < P.k, ∀ l < P.k, D P.q (P.Gs.getD j 0) (P.o + l) = if j = l then 1 else 0)
    (hreps : P.reps = [0]) (horph : P.orphs = [])
    (hT : ∀ t < P.q ^ (P.n - P.k), ∃ w, okT P t w = true) :
    ∃ C : Finset (Fin n → ZMod q), C.card = M ∧ CoveringA2.Covers R C := by
  classical
  subst hq hn hR hM
  obtain ⟨hk, hon⟩ := hdim
  have hq0 : 0 < P.q := Nat.pos_of_ne_zero (NeZero.ne _)
  -- o bloco de informação devolve a mensagem
  have hpiv : ∀ a, ∀ l < P.k, S P.q P.Gs a (P.o + l) % P.q = D P.q a l := by
    intro a l hl
    rw [S_unit (P.o + l) P.Gs a l (hk ▸ hl) (fun j hj => hunit j (hk ▸ hj) l hl)]
    exact Nat.mod_eq_of_lt (D_lt hq0 _ _)
  refine ⟨(Finset.range (P.q ^ P.k)).image (fun m => wdf P.q P.n (S P.q P.Gs m)), ?_, ?_⟩
  · rw [Finset.card_image_of_injOn, Finset.card_range]
    intro m hm m' hm' heq
    have hm : m < P.q ^ P.k := by simpa using hm
    have hm' : m' < P.q ^ P.k := by simpa using hm'
    have hdig : ∀ l < P.k, D P.q m l = D P.q m' l := by
      intro l hl
      have h1 := congrArg ZMod.val (congrFun heq ⟨P.o + l, by omega⟩)
      simp only [wdf, ZMod.val_natCast] at h1
      rw [← hpiv m l hl, ← hpiv m' l hl, h1]
    rw [← enc_D hq0 P.k m hm, ← enc_D hq0 P.k m' hm', enc_congr P.q P.k _ _ hdig]
  have hcw : ∀ rd m i, cwF P.q P.Gs rd m i < P.q := fun _ _ _ => Nat.mod_lt _ hq0
  intro x
  -- 1. a = dígitos de x no bloco, c = a·G
  set a := enc P.q (fun l => xval x (P.o + l)) P.k with ha_def
  have ha : a < P.q ^ P.k := enc_lt hq0 _ _ (fun i _ => xval_lt x _)
  have hDa : ∀ l < P.k, D P.q a l = xval x (P.o + l) :=
    D_enc hq0 _ _ (fun i _ => xval_lt x _)
  set c : Fin P.n → ZMod P.q := wdf P.q P.n (S P.q P.Gs a) with hc_def
  set y := x - c with hy_def
  have hyblk : ∀ l < P.k, xval y (P.o + l) = 0 := by
    intro l hl
    have hlt : P.o + l < P.n := by omega
    have h1 := hpiv a l hl
    simp only [xval, hlt, dite_true, hy_def, hc_def, Pi.sub_apply, wdf]
    have : ((S P.q P.Gs a (P.o + l) : ℕ) : ZMod P.q) = x ⟨P.o + l, hlt⟩ := by
      rw [← ZMod.natCast_mod, h1, hDa l hl]
      simp [xval, hlt]
    rw [this, sub_self, ZMod.val_zero]
  -- 2. t = índice de y no transversal
  set t := enc P.q (fun j => xval y (if j < P.o then j else j + P.k)) (P.n - P.k) with ht_def
  have ht : t < P.q ^ (P.n - P.k) := enc_lt hq0 _ _ (fun i _ => xval_lt y _)
  have hDt : ∀ j < P.n - P.k, D P.q t j = xval y (if j < P.o then j else j + P.k) :=
    D_enc hq0 _ _ (fun i _ => xval_lt y _)
  have hyt : ∀ i < P.n, xval y i = ydig P.q P.o P.k t i := by
    intro i hi
    rw [ydig_eq]
    by_cases h1 : i < P.o
    · rw [if_pos h1, hDt i (by omega), if_pos h1]
    · rw [if_neg h1]
      by_cases h2 : i < P.o + P.k
      · rw [if_pos h2]
        have := hyblk (i - P.o) (by omega)
        rwa [show P.o + (i - P.o) = i by omega] at this
      · rw [if_neg h2, hDt (i - P.k) (by omega), if_neg (by omega),
          show i - P.k + P.k = i by omega]
  obtain ⟨w, hw⟩ := hT t ht
  rcases okT_spec P hq0 t w hw with horph' | ⟨s, hs, m, hm, hd⟩
  · rw [horph] at horph'
    simp at horph'
  -- 3. testemunha m: x está perto de (m ⊕ a)·G, que é palavra do código
  have hs0 : s = 0 := by rw [hreps] at hs; simpa using hs
  subst hs0
  have hr : P.reps.getD 0 0 = 0 := by rw [hreps]; rfl
  rw [hr] at hd
  set f := cwF P.q P.Gs (D P.q 0) m with hf_def
  have hdy : hammingDist y (wdf P.q P.n f) ≤ P.R := by
    rw [hd_wdf y f (fun k _ => hcw _ _ k), dist_eq, distI_congr _ _ _ _ hyt, ← dist_eq]
    exact hd
  set m' := dsum P.q P.Gs.length m a
  have hm' : m' < P.q ^ P.k := hk ▸ dsum_lt hq0 _ _ _
  have hword : wdf P.q P.n (S P.q P.Gs m') = wdf P.q P.n f + c := by
    rw [hf_def, wdf_cwF, hc_def]
    have h0 : wdf P.q P.n (D P.q 0) = 0 := by
      funext i
      simp [wdf, D_eq]
    rw [h0, zero_add]
    funext i
    simp only [wdf, Pi.add_apply]
    exact S_dsum hq0 P.Gs m a i.1
  refine ⟨_, Finset.mem_image.mpr ⟨m', Finset.mem_range.mpr hm', rfl⟩, ?_⟩
  rw [hword, ← CoveringA2.hammingDist_sub_right x (wdf P.q P.n f + c) c, add_sub_cancel_right]
  exact hdy

end Syn

#print axioms Syn.lin_cert
