import Mathlib
import CoveringLean.SearchCore
import CoveringLean.A6c_Search

/-!
# SearchSound: `chkN … = true` implica refutação (prova de correção do núcleo de busca)

* `Ref n s`: nenhuma lista de `≤ s.l` centros `< 2^n` fora de `s.forb` completa `s.cov`.
* `chk_sound`: `chkN n S d s = true → (∀ t ∈ S, Ref n t) → Ref n s`.
* `no_cover_nat`: translação (WLOG `2^n-1 ∈ C`): `Ref n (root n m)` ⇒ nenhuma lista de `≤ m+1`
  centros cobre `{0,1}^n`.
* `no_cover_W`: a mesma coisa no formato do repositório (`CoveringA6.Covers` sobre `W 2 n`).
-/

namespace SC

open Finset

/-! ## Primitivas de bits -/

theorem testBit_one_shl (c i : ℕ) : (1 <<< c).testBit i = decide (i = c) := by
  rw [Nat.one_shiftLeft, Nat.testBit_two_pow]
  exact decide_eq_decide.2 eq_comm

theorem testBit_pow2 (c i : ℕ) : (2 ^ c).testBit i = true ↔ i = c := by
  rw [Nat.testBit_two_pow, decide_eq_true_eq]; exact eq_comm

theorem xor_xor_cancel (x a : ℕ) : x ^^^ a ^^^ a = x := by
  rw [Nat.xor_assoc, Nat.xor_self, Nat.xor_zero]

theorem xor_right_comm' (c t a : ℕ) : c ^^^ t ^^^ a = c ^^^ a ^^^ t := by
  rw [Nat.xor_assoc, Nat.xor_comm t a, ← Nat.xor_assoc]

theorem mem_nbrT (u : ℕ) : ∀ (m k i : ℕ),
    i ∈ nbrT u k m ↔ ∃ j, k ≤ j ∧ j < k + m ∧ i = u ^^^ 2 ^ j := by
  intro m
  induction m with
  | zero =>
    intro k i
    simp only [nbrT, List.not_mem_nil, false_iff, not_exists, not_and]
    intro j h1 h2; omega
  | succ m ih =>
    intro k i
    simp only [nbrT, List.mem_cons, ih, Nat.one_shiftLeft]
    constructor
    · rintro (h | ⟨j, h1, h2, h3⟩)
      · exact ⟨k, le_refl _, by omega, h⟩
      · exact ⟨j, by omega, by omega, h3⟩
    · rintro ⟨j, h1, h2, h3⟩
      rcases Nat.eq_or_lt_of_le h1 with h | h
      · left; subst h; exact h3
      · right; exact ⟨j, by omega, by omega, h3⟩

theorem mem_nbr (n u i : ℕ) : i ∈ nbr n u ↔ i = u ∨ ∃ j < n, i = u ^^^ 2 ^ j := by
  simp only [nbr, List.mem_cons, mem_nbrT]
  constructor
  · rintro (h | ⟨j, -, h2, h3⟩)
    · exact Or.inl h
    · exact Or.inr ⟨j, by omega, h3⟩
  · rintro (h | ⟨j, h2, h3⟩)
    · exact Or.inl h
    · exact Or.inr ⟨j, by omega, by omega, h3⟩

theorem length_nbrT (u : ℕ) : ∀ m k, (nbrT u k m).length = m := by
  intro m; induction m with
  | zero => intro k; simp [nbrT]
  | succ m ih => intro k; simp [nbrT, ih]

theorem length_nbr (n u : ℕ) : (nbr n u).length = n + 1 := by
  simp [nbr, length_nbrT]

theorem testBit_bmA (c : ℕ) : ∀ k i, (bmA c k).testBit i = true ↔ i = c ∨ ∃ j < k, i = c ^^^ 2 ^ j := by
  intro k
  induction k with
  | zero => intro i; simp only [bmA, Nat.one_shiftLeft, testBit_pow2]; simp
  | succ k ih =>
    intro i
    simp only [bmA, Nat.one_shiftLeft, Nat.testBit_or, Bool.or_eq_true, ih, testBit_pow2]
    constructor
    · rintro ((h | ⟨j, hj, h⟩) | h)
      · exact Or.inl h
      · exact Or.inr ⟨j, by omega, h⟩
      · exact Or.inr ⟨k, by omega, h⟩
    · rintro (h | ⟨j, hj, h⟩)
      · exact Or.inl (Or.inl h)
      · rcases Nat.lt_succ_iff_lt_or_eq.1 hj with hj | hj
        · exact Or.inl (Or.inr ⟨j, hj, h⟩)
        · subst hj; exact Or.inr h

/-- Os bits da bola são exatamente a lista `nbr`. -/
theorem testBit_bm (n c i : ℕ) : (bm n c).testBit i = true ↔ i ∈ nbr n c := by
  rw [bm, testBit_bmA, mem_nbr]

theorem mem_nbr_comm (n c i : ℕ) : i ∈ nbr n c ↔ c ∈ nbr n i := by
  rw [mem_nbr, mem_nbr]
  constructor
  · rintro (h | ⟨j, hj, h⟩)
    · exact Or.inl h.symm
    · exact Or.inr ⟨j, hj, by rw [h, xor_xor_cancel]⟩
  · rintro (h | ⟨j, hj, h⟩)
    · exact Or.inl h.symm
    · exact Or.inr ⟨j, hj, by rw [h, xor_xor_cancel]⟩

/-- Translação: `x ↦ x xor a` leva bola em bola. -/
theorem mem_nbr_xor (n c i a : ℕ) : i ∈ nbr n c → (i ^^^ a) ∈ nbr n (c ^^^ a) := by
  rw [mem_nbr, mem_nbr]
  rintro (h | ⟨j, hj, h⟩)
  · exact Or.inl (by rw [h])
  · exact Or.inr ⟨j, hj, by rw [h, xor_right_comm']⟩

theorem testBit_full (n i : ℕ) : (full n).testBit i = decide (i < 2 ^ n) := by
  rw [full, Nat.one_shiftLeft, Nat.one_shiftLeft, Nat.testBit_two_pow_sub_one]

theorem testBit_unc (n cov i : ℕ) :
    (unc n cov).testBit i = (decide (i < 2 ^ n) && !cov.testBit i) := by
  rw [unc, Nat.testBit_xor, Nat.testBit_and, testBit_full]
  cases decide (i < 2 ^ n) <;> cases cov.testBit i <;> rfl

/-! ## Contagens -/

/-- Palavras descobertas. -/
def Ufs (n cov : ℕ) : Finset ℕ := (range (2 ^ n)).filter fun i => cov.testBit i = false

theorem popc_eq : ∀ k m, popc k m = ((range k).filter fun i => m.testBit i = true).card := by
  intro k
  induction k with
  | zero => intro m; simp [popc]
  | succ k ih =>
    intro m
    rw [popc, ih, Finset.card_filter, Finset.card_filter, Finset.sum_range_succ']
    have h0 : (if m.testBit 0 = true then 1 else 0) = m % 2 := by
      rw [Nat.testBit_zero]
      rcases Nat.mod_two_eq_zero_or_one m with h | h <;> simp [h]
    rw [h0, add_comm]
    congr 1
    apply Finset.sum_congr rfl
    intro i _
    rw [Nat.testBit_succ]

theorem popc_unc (n cov : ℕ) : popc (1 <<< n) (unc n cov) = (Ufs n cov).card := by
  rw [popc_eq, Nat.one_shiftLeft, Ufs]
  congr 1
  apply Finset.filter_congr
  intro i hi
  rw [Finset.mem_range] at hi
  rw [testBit_unc]
  simp [hi]

theorem cntIn_eq (x : ℕ) : ∀ L : List ℕ, cntIn x L = L.countP fun w => x.testBit w := by
  intro L
  induction L with
  | nil => rfl
  | cons w ws ih =>
    rw [cntIn, List.countP_cons, ih]
    cases x.testBit w <;> rfl

/-- Se todo elemento de `A` está ligado em `x`, `|A ∩ L| ≤ cntIn x L`. -/
theorem card_inter_le_cntIn (x : ℕ) (A : Finset ℕ) (hA : ∀ i ∈ A, x.testBit i = true)
    (L : List ℕ) : (A ∩ L.toFinset).card ≤ cntIn x L := by
  have hsub : A ∩ L.toFinset ⊆ (L.filter fun w => x.testBit w).toFinset := by
    intro i hi
    rw [Finset.mem_inter, List.mem_toFinset] at hi
    rw [List.mem_toFinset, List.mem_filter]
    exact ⟨hi.2, hA i hi.1⟩
  calc (A ∩ L.toFinset).card ≤ (L.filter fun w => x.testBit w).toFinset.card :=
        Finset.card_le_card hsub
    _ ≤ (L.filter fun w => x.testBit w).length := List.toFinset_card_le _
    _ = cntIn x L := by rw [cntIn_eq, List.countP_eq_length_filter]

/-! ## A propriedade refutada -/

/-- `L` completa `cov`: toda palavra `< 2^n` está em `cov` ou na bola de algum `c ∈ L`. -/
def Covd (n cov : ℕ) (L : List ℕ) : Prop :=
  ∀ i, i < 2 ^ n → cov.testBit i = true ∨ ∃ c ∈ L, (bm n c).testBit i = true

/-- `Ref n s`: nenhuma lista de `≤ s.l` centros `< 2^n`, fora de `s.forb`, completa `s.cov`. -/
def Ref (n : ℕ) (s : St) : Prop :=
  ∀ L : List ℕ, L.length ≤ s.l → (∀ c ∈ L, c < 2 ^ n) → (∀ c ∈ L, s.forb.testBit c = false) →
    ¬ Covd n s.cov L

/-- Poda por contagem: `|U| ≤ |L|·(n+1)`. -/
theorem card_Ufs_le (n cov : ℕ) (L : List ℕ) (h : Covd n cov L) :
    (Ufs n cov).card ≤ L.length * (n + 1) := by
  have hsub : Ufs n cov ⊆ L.toFinset.biUnion fun c => (nbr n c).toFinset := by
    intro i hi
    simp only [Ufs, Finset.mem_filter, Finset.mem_range] at hi
    rcases h i hi.1 with h1 | ⟨c, hc, hb⟩
    · rw [hi.2] at h1; exact absurd h1 (by simp)
    · exact Finset.mem_biUnion.2
        ⟨c, List.mem_toFinset.2 hc, List.mem_toFinset.2 ((testBit_bm n c i).1 hb)⟩
  calc (Ufs n cov).card ≤ (L.toFinset.biUnion fun c => (nbr n c).toFinset).card :=
        Finset.card_le_card hsub
    _ ≤ ∑ c ∈ L.toFinset, (nbr n c).toFinset.card := Finset.card_biUnion_le
    _ ≤ ∑ _c ∈ L.toFinset, (n + 1) :=
        Finset.sum_le_sum fun c _ => (List.toFinset_card_le _).trans (length_nbr n c).le
    _ = L.toFinset.card * (n + 1) := by simp
    _ ≤ L.length * (n + 1) := Nat.mul_le_mul_right _ (List.toFinset_card_le L)

/-- A cota inferior incremental continua válida no filho. -/
theorem card_Ufs_step (n cov c : ℕ) :
    (Ufs n cov).card ≤ (Ufs n (cov ||| bm n c)).card + cntIn (unc n cov) (nbr n c) := by
  have hsub : Ufs n cov ⊆ Ufs n (cov ||| bm n c) ∪ (Ufs n cov ∩ (nbr n c).toFinset) := by
    intro i hi
    have hi' := hi
    simp only [Ufs, Finset.mem_filter, Finset.mem_range] at hi'
    by_cases hb : (bm n c).testBit i = true
    · exact Finset.mem_union_right _
        (Finset.mem_inter.2 ⟨hi, List.mem_toFinset.2 ((testBit_bm n c i).1 hb)⟩)
    · apply Finset.mem_union_left
      simp only [Ufs, Finset.mem_filter, Finset.mem_range, Nat.testBit_or, hi'.2, Bool.false_or]
      exact ⟨hi'.1, by simpa using hb⟩
  have hA : ∀ i ∈ Ufs n cov, (unc n cov).testBit i = true := by
    intro i hi
    simp only [Ufs, Finset.mem_filter, Finset.mem_range] at hi
    simp [testBit_unc, hi.1, hi.2]
  calc (Ufs n cov).card ≤ (Ufs n (cov ||| bm n c) ∪ (Ufs n cov ∩ (nbr n c).toFinset)).card :=
        Finset.card_le_card hsub
    _ ≤ (Ufs n (cov ||| bm n c)).card + (Ufs n cov ∩ (nbr n c).toFinset).card :=
        Finset.card_union_le _ _
    _ ≤ _ := Nat.add_le_add_left (card_inter_le_cntIn _ _ hA _) _

theorem stBeq_eq {a b : St} (h : stBeq a b = true) : a = b := by
  cases a; cases b
  simp only [stBeq, Bool.and_eq_true, Nat.beq_eq] at h
  obtain ⟨h1, h2, h3⟩ := h
  subst h1 h2 h3; rfl

/-- Conclusão de um laço de filhos / de um nó: o que foi consumido de `S` é um prefixo `P`. -/
def Res (n : ℕ) (S S' : List St) (Q : Prop) : Prop :=
  ∃ P, S = P ++ S' ∧ ((∀ t ∈ P, Ref n t) → Q)

/-- Laço dos filhos (exclusão de irmãos: se `c ∈ L`, o filho de `c` refuta). -/
theorem kids_sound (n : ℕ) (f : St → ℕ → List St → Option (List St)) (l' cov ucnt : ℕ)
    (hf : ∀ s u S S', f s u S = some S' → u ≤ (Ufs n s.cov).card → Res n S S' (Ref n s))
    (hu : ucnt ≤ (Ufs n cov).card) :
    ∀ (cs : List ℕ) (forb : ℕ) (S S' : List St),
      kids n f l' cov (unc n cov) ucnt forb cs S = some S' →
      Res n S S' (∀ c ∈ cs, forb.testBit c = false → ∀ L : List ℕ, L.length ≤ l' + 1 →
          (∀ c ∈ L, c < 2 ^ n) → (∀ c ∈ L, forb.testBit c = false) → c ∈ L → ¬ Covd n cov L) := by
  intro cs
  induction cs with
  | nil =>
    intro forb S S' h
    simp only [kids, Option.some.injEq] at h
    exact ⟨[], by simp [h], fun _ c hc => by simp at hc⟩
  | cons c cs ih =>
    intro forb S S' h
    cases hfc : forb.testBit c with
    | true =>
      simp only [kids, hfc, cond_true] at h
      obtain ⟨P, hP, hR⟩ := ih forb S S' h
      refine ⟨P, hP, fun hPR c0 hc0 hf0 => ?_⟩
      rcases List.mem_cons.1 hc0 with h0 | hc0
      · subst h0; rw [hfc] at hf0; exact absurd hf0 (by simp)
      · exact hR hPR c0 hc0 hf0
    | false =>
      simp only [kids, hfc, cond_false] at h
      cases hch : f ⟨l', cov ||| bm n c, forb ||| 1 <<< c⟩ (ucnt - cntIn (unc n cov) (nbr n c)) S
        with
      | none => rw [hch] at h; exact absurd h (by simp)
      | some S1 =>
        rw [hch] at h
        simp only at h
        have hu' : ucnt - cntIn (unc n cov) (nbr n c) ≤ (Ufs n (cov ||| bm n c)).card := by
          have := card_Ufs_step n cov c; omega
        obtain ⟨P1, hP1, hR1⟩ := hf _ _ _ _ hch hu'
        obtain ⟨P2, hP2, hR2⟩ := ih _ S1 S' h
        refine ⟨P1 ++ P2, by rw [hP1, hP2, List.append_assoc], fun hPR => ?_⟩
        have hchild : Ref n ⟨l', cov ||| bm n c, forb ||| 1 <<< c⟩ :=
          hR1 fun t ht => hPR t (List.mem_append_left _ ht)
        have hrest := hR2 fun t ht => hPR t (List.mem_append_right _ ht)
        have hc : ∀ L : List ℕ, L.length ≤ l' + 1 → (∀ c ∈ L, c < 2 ^ n) →
            (∀ c ∈ L, forb.testBit c = false) → c ∈ L → ¬ Covd n cov L := by
          intro L hlen hlt hfb hcL hcov
          refine hchild (L.filter fun x => x != c) ?_ ?_ ?_ ?_
          · have : (L.filter fun x => x != c).length < L.length :=
              List.length_filter_lt_length_iff_exists.2 ⟨c, hcL, by simp⟩
            change _ ≤ l'
            omega
          · intro x hx; exact hlt x (List.mem_filter.1 hx).1
          · intro x hx
            obtain ⟨hxL, hxc⟩ := List.mem_filter.1 hx
            change (forb ||| 1 <<< c).testBit x = false
            rw [Nat.testBit_or, testBit_one_shl, hfb x hxL]
            simpa using hxc
          · intro i hi
            change (cov ||| bm n c).testBit i = true ∨ _
            rw [Nat.testBit_or]
            rcases hcov i hi with h1 | ⟨x, hxL, hxb⟩
            · left; simp [h1]
            · by_cases hxc : x = c
              · left; subst hxc; simp [hxb]
              · right; exact ⟨x, List.mem_filter.2 ⟨hxL, by simpa using hxc⟩, hxb⟩
        intro c0 hc0 hf0 L hlen hlt hfb hc0L
        rcases List.mem_cons.1 hc0 with h0 | hc0
        · subst h0; exact hc L hlen hlt hfb hc0L
        · by_cases hcL : c ∈ L
          · exact hc L hlen hlt hfb hcL
          · have hne : c0 ≠ c := fun h => hcL (h ▸ hc0L)
            have hf0' : (forb ||| 1 <<< c).testBit c0 = false := by
              rw [Nat.testBit_or, testBit_one_shl, hf0]; simpa using hne
            refine hrest c0 hc0 hf0' L hlen hlt ?_ hc0L
            intro x hx
            have hxc : x ≠ c := fun h => hcL (h ▸ hx)
            rw [Nat.testBit_or, testBit_one_shl, hfb x hx]; simpa using hxc

/-- Um nó é correto se a chamada recursiva (quando há) é correta. -/
theorem node_sound (n : ℕ) (rec : Option (St → ℕ → List St → Option (List St)))
    (hrec : ∀ f, rec = some f →
      ∀ s u S S', f s u S = some S' → u ≤ (Ufs n s.cov).card → Res n S S' (Ref n s)) :
    ∀ s ucnt S S', node n rec s ucnt S = some S' → ucnt ≤ (Ufs n s.cov).card →
      Res n S S' (Ref n s) := by
  intro s ucnt S S' h hu
  unfold node at h
  dsimp only at h
  cases hx : (unc n s.cov).beq 0 with
  | true => rw [hx] at h; simp at h
  | false =>
    rw [hx, cond_false] at h
    cases hp : Nat.blt (s.l * (n + 1)) ucnt with
    | true =>
      rw [hp, cond_true, Option.some.injEq] at h
      subst h
      refine ⟨[], by simp, fun _ L hlen _ _ hcov => ?_⟩
      have h1 := card_Ufs_le n s.cov L hcov
      have h2 : s.l * (n + 1) < ucnt := by simpa [Nat.blt_eq] using hp
      have h3 : L.length * (n + 1) ≤ s.l * (n + 1) := Nat.mul_le_mul_right _ hlen
      omega
    | false =>
      rw [hp, cond_false] at h
      cases rec with
      | none =>
        simp only at h
        cases S with
        | nil => simp at h
        | cons t S0 =>
          simp only at h
          cases ht : stBeq t s with
          | false => rw [ht] at h; simp at h
          | true =>
            rw [ht, cond_true, Option.some.injEq] at h
            subst h
            have hts : t = s := stBeq_eq ht
            exact ⟨[t], rfl, fun hP => hts ▸ hP t (by simp)⟩
      | some f =>
        simp only at h
        cases hb : (unc n s.cov).testBit (low (unc n s.cov)) with
        | false => rw [hb] at h; simp at h
        | true =>
          rw [hb, cond_true] at h
          obtain ⟨P, hP, hR⟩ :=
            kids_sound n f (s.l - 1) s.cov ucnt (hrec f rfl) hu _ _ _ _ h
          refine ⟨P, hP, fun hPR L hlen hlt hfb hcov => ?_⟩
          obtain ⟨hu1, hu2⟩ : low (unc n s.cov) < 2 ^ n ∧
              s.cov.testBit (low (unc n s.cov)) = false := by
            rw [testBit_unc] at hb; simpa using hb
          rcases hcov _ hu1 with h1 | ⟨c, hcL, hcb⟩
          · rw [hu2] at h1; exact absurd h1 (by simp)
          · have hcn : c ∈ nbr n (low (unc n s.cov)) :=
              (mem_nbr_comm n c _).1 ((testBit_bm n c _).1 hcb)
            exact hR hPR c hcn (hfb c hcL) L (by omega) hlt hfb hcL hcov

theorem go_sound (n : ℕ) : ∀ d s ucnt S S', go n d s ucnt S = some S' →
    ucnt ≤ (Ufs n s.cov).card → Res n S S' (Ref n s) := by
  intro d
  induction d with
  | zero =>
    intro s ucnt S S' h hu
    rw [go] at h
    exact node_sound n none (fun f hf => by cases hf) s ucnt S S' h hu
  | succ d ih =>
    intro s ucnt S S' h hu
    rw [go] at h
    exact node_sound n (some (go n d)) (fun f hf => by cases hf; exact ih) s ucnt S S' h hu

/-- **Correção do núcleo**: `chkN n S d s = true` e a fronteira `S` refutada ⇒ `s` refutado. -/
theorem chkN_sound (n : ℕ) (S : List St) (d : ℕ) (s : St) (h : chkN n S d s = true)
    (hS : ∀ t ∈ S, Ref n t) : Ref n s := by
  cases hg : go n d s (popc (1 <<< n) (unc n s.cov)) S with
  | none => simp [chkN, hg] at h
  | some S' =>
    cases S' with
    | cons t S'' => simp [chkN, hg] at h
    | nil =>
      obtain ⟨P, hP, hR⟩ := go_sound n d s _ S [] hg (popc_unc n s.cov).le
      rw [List.append_nil] at hP
      subst hP
      exact hR hS

theorem chk_sound (S : List St) (d : ℕ) (s : St) (h : chk S d s = true)
    (hS : ∀ t ∈ S, Ref 6 t) : Ref 6 s :=
  chkN_sound 6 S d s h hS

/-! ## Translação: WLOG `2^n - 1 ∈ C` -/

theorem no_cover_nat (n m : ℕ) (hR : Ref n (root n m)) (L : List ℕ) (hL : ∀ c ∈ L, c < 2 ^ n)
    (hlen : L.length ≤ m + 1) : ¬ Covd n 0 L := by
  intro hcov
  have htop : (1 <<< n) - 1 < 2 ^ n := by
    rw [Nat.one_shiftLeft]; have := Nat.one_le_two_pow (n := n); omega
  obtain ⟨b, hbL, -⟩ : ∃ b ∈ L, (bm n b).testBit 0 = true := by
    rcases hcov 0 (Nat.two_pow_pos n) with h | h
    · simp at h
    · exact h
  have ha : b ^^^ ((1 <<< n) - 1) < 2 ^ n := Nat.xor_lt_two_pow (hL b hbL) htop
  have htopL1 : (1 <<< n) - 1 ∈ L.map fun x => x ^^^ (b ^^^ ((1 <<< n) - 1)) :=
    List.mem_map.2 ⟨b, hbL, by rw [← Nat.xor_assoc, Nat.xor_self, Nat.zero_xor]⟩
  refine hR ((L.map fun x => x ^^^ (b ^^^ ((1 <<< n) - 1))).filter fun x => x != (1 <<< n) - 1)
    ?_ ?_ ?_ ?_
  · have h1 : ((L.map fun x => x ^^^ (b ^^^ ((1 <<< n) - 1))).filter
        fun x => x != (1 <<< n) - 1).length < (L.map fun x => x ^^^ (b ^^^ ((1 <<< n) - 1))).length :=
      List.length_filter_lt_length_iff_exists.2 ⟨(1 <<< n) - 1, htopL1, by simp⟩
    rw [List.length_map] at h1
    change _ ≤ m
    omega
  · intro x hx
    obtain ⟨y, hy, rfl⟩ := List.mem_map.1 (List.mem_filter.1 hx).1
    exact Nat.xor_lt_two_pow (hL y hy) ha
  · intro x hx
    have := (List.mem_filter.1 hx).2
    change (1 <<< ((1 <<< n) - 1)).testBit x = false
    rw [testBit_one_shl]; simpa using this
  · intro i hi
    change (bm n ((1 <<< n) - 1)).testBit i = true ∨ _
    have hi' : i ^^^ (b ^^^ ((1 <<< n) - 1)) < 2 ^ n := Nat.xor_lt_two_pow hi ha
    rcases hcov _ hi' with h | ⟨c, hcL, hcb⟩
    · simp at h
    · have hmem : i ∈ nbr n (c ^^^ (b ^^^ ((1 <<< n) - 1))) := by
        have := mem_nbr_xor n c _ (b ^^^ ((1 <<< n) - 1)) ((testBit_bm n c _).1 hcb)
        rwa [xor_xor_cancel] at this
      by_cases hct : c ^^^ (b ^^^ ((1 <<< n) - 1)) = (1 <<< n) - 1
      · left; rw [← hct]; exact (testBit_bm n _ _).2 hmem
      · right
        exact ⟨_, List.mem_filter.2 ⟨List.mem_map.2 ⟨c, hcL, rfl⟩, by simpa using hct⟩,
          (testBit_bm n _ _).2 hmem⟩

/-! ## Ponte para o formato do repositório (`CoveringA6.Covers` sobre `W 2 n`) -/

open CoveringA6 in
theorem no_cover_W {n m : ℕ} (enc : W 2 n → ℕ) (dec : ℕ → W 2 n)
    (henc : ∀ x, enc x < 2 ^ n) (hed : ∀ k, k < 2 ^ n → enc (dec k) = k)
    (hspec : ∀ x c : W 2 n, hammingDist x c ≤ 1 → (bm n (enc c)).testBit (enc x) = true)
    (hR : Ref n (root n m)) (C : Finset (W 2 n)) (hC : C.card ≤ m + 1) : ¬ Covers 1 C := by
  intro hcov
  refine no_cover_nat n m hR (C.toList.map enc) ?_ (by simpa using hC) ?_
  · intro c hc; obtain ⟨x, -, rfl⟩ := List.mem_map.1 hc; exact henc x
  · intro i hi
    right
    obtain ⟨c, hc, hd⟩ := hcov (dec i)
    refine ⟨enc c, List.mem_map.2 ⟨c, Finset.mem_toList.2 hc, rfl⟩, ?_⟩
    have := hspec (dec i) c hd
    rwa [hed i hi] at this

/-- Codificação `W 2 n → ℕ` (little-endian), como em `A6c_Search.enc`. -/
def encN (n : ℕ) (x : CoveringA6.W 2 n) : ℕ := ∑ i : Fin n, (x i).val * 2 ^ i.val

def decN (n k : ℕ) : CoveringA6.W 2 n := fun i => ⟨(k / 2 ^ i.val) % 2, Nat.mod_lt _ (by norm_num)⟩

theorem enc6_lt : ∀ x : CoveringA6.W 2 6, encN 6 x < 2 ^ 6 := by decide +kernel
theorem enc6_dec : ∀ k, k < 2 ^ 6 → encN 6 (decN 6 k) = k := by decide +kernel
theorem spec6 : ∀ x c : CoveringA6.W 2 6, hammingDist x c ≤ 1 →
    (bm 6 (encN 6 c)).testBit (encN 6 x) = true := by decide +kernel

open CoveringA6 in
/-- `Ref 6 (root 6 10)` ⇒ nenhum código de `≤ 11` palavras cobre `{0,1}^6` com raio 1. -/
theorem K_2_6_1_ge12_of (h : Ref 6 (root 6 10)) :
    ∀ C : Finset (W 2 6), C.card < 12 → ¬ Covers 1 C :=
  fun C hC => no_cover_W (encN 6) (decN 6) enc6_lt enc6_dec spec6 h C (by omega)

open CoveringA6 in
/-- `Ref 6 (root 6 10)` ⇒ `K_2(6,1) = 12` (a cota superior é `code12` de `A6c_Search`). -/
theorem K_2_6_1_eq12_of (h : Ref 6 (root 6 10)) : IsK 2 6 1 12 :=
  ⟨⟨code12, code12_card, code12_covers⟩, K_2_6_1_ge12_of h⟩

open CoveringA6 in
theorem K_2_6_1_ge11_of (h : Ref 6 (root 6 9)) :
    ∀ C : Finset (W 2 6), C.card < 11 → ¬ Covers 1 C :=
  fun C hC => no_cover_W (encN 6) (decN 6) enc6_lt enc6_dec spec6 h C (by omega)

end SC

#print axioms SC.chkN_sound
#print axioms SC.chk_sound
#print axioms SC.no_cover_W
#print axioms SC.K_2_6_1_eq12_of
