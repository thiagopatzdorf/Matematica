import CoveringLean.K742_Final
import CoveringLean.K742_PonteCnf

/-!
# A ponte código → CNF sem quebra: `Ponte18 (K742Cnf.cnfSemQuebra 7 18)`

Todo código `C ⊆ Z_7^4` de raio 2 com 18 palavras satisfaz a CNF sem quebra de algum dos 70
perfis. Passos, todos "sem perda de generalidade":

1. o perfil de `C` está na lista (`profile_mem_profiles18`, `perfis18_complete`): um `t`;
2. uma permutação `π` das coordenadas leva o tipo da coordenada `π i` em `t[i]`, e em cada
   coordenada uma permutação `σ i` dos símbolos ordena as fibras como em `t[i]`
   (`exists_perm_of_map_eq`); as palavras renomeadas são `φ i (c (π i))`;
3. as 18 palavras são enumeradas por blocos da coordenada 0 (`finSigmaFinEquiv`);
4. as palavras assim obtidas cumprem `K742Ponte.Normal`, e `K742Ponte.cnfSemQuebra_sat` dá a
   valoração.

Não há (d)–(f): a CNF sem quebra só usa a ordem dos tipos, dos símbolos e dos blocos.
-/

open Finset

namespace K742Ponte

/-- Duas funções de um tipo finito com o mesmo multiconjunto de valores diferem por uma
permutação do domínio. -/
theorem exists_perm_of_map_eq {α β : Type*} [Fintype α] [DecidableEq β] (f g : α → β)
    (h : (univ : Finset α).val.map f = (univ : Finset α).val.map g) :
    ∃ σ : Equiv.Perm α, ∀ x, f (σ x) = g x := by
  have hc : ∀ b, Fintype.card { x // g x = b } = Fintype.card { x // f x = b } := by
    intro b
    rw [Fintype.card_subtype, Fintype.card_subtype]
    have h1 := Multiset.count_map f (univ : Finset α).val b
    have h2 := Multiset.count_map g (univ : Finset α).val b
    rw [h, h2] at h1
    have e : ∀ (p : α → Prop) [DecidablePred p],
        Multiset.card ((univ : Finset α).val.filter p) = (univ.filter p).card := fun _ _ => rfl
    rw [← e, ← e]
    simp only [eq_comm (a := b)] at h1
    exact h1
  refine ⟨((Equiv.sigmaFiberEquiv g).symm.trans
    (Equiv.sigmaCongrRight fun b => Fintype.equivOfCardEq (hc b))).trans
    (Equiv.sigmaFiberEquiv f), fun x => ?_⟩
  simp only [Equiv.trans_apply, Equiv.sigmaCongrRight_apply, Equiv.sigmaFiberEquiv_apply]
  exact (Fintype.equivOfCardEq (hc (g x)) _).2

/-- Num espaço de comprimento 4, distância `≤ 2` dá duas coordenadas distintas de acordo. -/
theorem agree_two {α : Type*} [DecidableEq α] (X c : Fin 4 → α) (h : hammingDist X c ≤ 2) :
    ∃ j1 j2 : Fin 4, j1 ≠ j2 ∧ X j1 = c j1 ∧ X j2 = c j2 := by
  rw [K742.hammingDist_eq_sum, Fin.sum_univ_four] at h
  by_cases h0 : X 0 = c 0 <;> by_cases h1 : X 1 = c 1 <;> by_cases h2 : X 2 = c 2 <;>
    by_cases h3 : X 3 = c 3 <;> simp only [h0, h1, h2, h3, ne_eq, not_true_eq_false,
      not_false_eq_true, if_true, if_false] at h <;>
    first
    | omega
    | exact ⟨0, 1, by decide, h0, h1⟩
    | exact ⟨0, 2, by decide, h0, h2⟩
    | exact ⟨0, 3, by decide, h0, h3⟩
    | exact ⟨1, 2, by decide, h1, h2⟩
    | exact ⟨1, 3, by decide, h1, h3⟩
    | exact ⟨2, 3, by decide, h2, h3⟩

/-- Soma de prefixo de uma lista como soma sobre `Fin a`. -/
theorem sum_fin_getD (l : List ℕ) (a : ℕ) :
    ∑ i : Fin a, l.getD i 0 = (l.take a).sum := by
  induction a with
  | zero => simp
  | succ a ih =>
    rw [Fin.sum_univ_castSucc]
    simp only [Fin.coe_castSucc, Fin.val_last, ih]
    rcases Nat.lt_or_ge a l.length with h | h
    · rw [List.take_succ, List.sum_append, List.getD_eq_getElem?_getD,
        List.getElem?_eq_getElem h]
      simp
    · rw [List.take_of_length_le h, List.take_of_length_le (by omega),
        List.getD_eq_getElem?_getD, List.getElem?_eq_none h]
      simp

/-- Fatos decididos sobre os 70 perfis. -/
theorem perfis18_shape : ∀ t ∈ K742.perfis18, t.length = 4 ∧
    (∀ i < 4, (t.getD i []).length = 7) ∧ (t.getD 0 []).sum = 18 ∧
    ∀ a < 7, ∀ k ∈ K742Cnf.block t a, k < 18 := by
  decide +kernel

open K742Cnf

theorem mem_pares_of_lt {i j : ℕ} (hij : i < j) (hj : j < 4) : (i, j) ∈ pares := by
  obtain rfl | rfl | rfl : j = 1 ∨ j = 2 ∨ j = 3 := by omega
  all_goals (obtain rfl | rfl | rfl : i = 0 ∨ i = 1 ∨ i = 2 := by omega)
  all_goals first | omega | decide

theorem filter_range_length (n : ℕ) (p : ℕ → Prop) [DecidablePred p] :
    ((List.range n).filter fun k => decide (p k)).length = ((Finset.range n).filter p).card := by
  simp [Finset.card, Finset.filter_val, Finset.range_val, Multiset.range, Multiset.filter_coe]

theorem ofFn_getD_eq {α : Type*} (l : List α) (d : α) (n : ℕ) (h : l.length = n) :
    List.ofFn (fun i : Fin n => l.getD i d) = l := by
  subst h
  apply List.ext_getElem (by simp)
  intro i h1 h2
  simp [List.getD_eq_getElem?_getD, List.getElem?_eq_getElem h2]

/-- Enumeração das palavras de `C` por blocos de uma chave `κ : C → Fin 7`, com `n a` palavras
de chave `a`: a palavra `k` tem chave `a` e `k = n 0 + … + n (a−1) + j`, `j < n a`. -/
theorem exists_block_enum {C : Finset (Fin 4 → ZMod 7)} (κ : {c // c ∈ C} → Fin 7)
    (n : Fin 7 → ℕ) (hn : ∑ a, n a = 18)
    (hcard : ∀ a, Fintype.card {c : {c // c ∈ C} // κ c = a} = n a) :
    ∃ E : Fin 18 ≃ {c // c ∈ C}, ∀ k : Fin 18, ∃ j : ℕ, j < n (κ (E k)) ∧
      (k : ℕ) = ∑ i : Fin (κ (E k)), n (Fin.castLE (κ (E k)).2.le i) + j := by
  let e : ∀ a, Fin (n a) ≃ {c : {c // c ∈ C} // κ c = a} :=
    fun a => (Fintype.equivFinOfCardEq (hcard a)).symm
  refine ⟨((finCongr hn.symm).trans finSigmaFinEquiv.symm).trans
    ((Equiv.sigmaCongrRight e).trans (Equiv.sigmaFiberEquiv κ)), fun k => ?_⟩
  set s := (finSigmaFinEquiv (n := n)).symm (finCongr hn.symm k) with hs
  have hk : (((finCongr hn.symm).trans finSigmaFinEquiv.symm).trans
      ((Equiv.sigmaCongrRight e).trans (Equiv.sigmaFiberEquiv κ))) k = ((e s.1) s.2).1 := rfl
  have hκ : κ ((e s.1) s.2).1 = s.1 := ((e s.1) s.2).2
  rw [hk, hκ]
  refine ⟨s.2, s.2.2, ?_⟩
  have h1 : ((finCongr hn.symm k : Fin (∑ a, n a)) : ℕ) = k := rfl
  have h2 : finSigmaFinEquiv s = finCongr hn.symm k := by rw [hs]; simp
  rw [← h1, ← h2, finSigmaFinEquiv_apply]

/-- **A ponte**, versão sem quebra: todo código de raio 2 com 18 palavras satisfaz a CNF sem
quebra de algum dos 70 perfis. -/
theorem ponte18 : K742.Ponte18 (K742Cnf.cnfSemQuebra 7 18) := by
  intro C hC hcov
  obtain ⟨P, hP, hPC⟩ := K742.profile_mem_profiles18 hcov hC
  obtain ⟨t, ht, htP⟩ := K742.perfis18_complete P hP
  obtain ⟨hlen, hlen7, hsum0, hblk18⟩ := perfis18_shape t ht
  -- 1. permutação das coordenadas
  simp at htP
  have hfm : ∀ l : List (List ℕ), List.flatMap (fun a : List ℕ => [Multiset.ofList a]) l =
      List.map (fun a : List ℕ => Multiset.ofList a) l := by
    intro l; induction l with
    | nil => rfl
    | cons a l ih => simp only [List.flatMap_cons, List.map_cons, List.singleton_append, ih]
  rw [hfm] at htP
  let g : Fin 4 → Multiset ℕ := fun i => ((t.getD (i : ℕ) [] : List ℕ) : Multiset ℕ)
  have hg : (univ : Finset (Fin 4)).val.map (K742.fiberType C) = (univ : Finset (Fin 4)).val.map g := by
    rw [Fin.univ_val_map g]
    have : List.ofFn g = List.map (fun l : List ℕ => Multiset.ofList l) t := by
      rw [← ofFn_getD_eq (List.map (fun l : List ℕ => Multiset.ofList l) t) 0 4 (by simp [hlen])]
      congr 1; funext i
      simp only [g, List.getD_eq_getElem?_getD, List.getElem?_map]
      cases t[(i : ℕ)]? <;> rfl
    rw [this, htP, hPC]
    rfl
  obtain ⟨π, hπ⟩ := exists_perm_of_map_eq _ _ hg
  -- 2. permutação dos símbolos em cada coordenada
  have hZ : (univ : Finset (ZMod 7)).val.map ZMod.val = Multiset.range 7 := by decide
  have hσ : ∀ i : Fin 4, ∃ σ : Equiv.Perm (ZMod 7), ∀ a : ZMod 7,
      (K742.fiber C (π i) (σ a)).card = (t.getD (i : ℕ) []).getD (ZMod.val a) 0 := by
    intro i
    refine exists_perm_of_map_eq (fun a => (K742.fiber C (π i) a).card)
      (fun a : ZMod 7 => (t.getD (i : ℕ) []).getD (ZMod.val a) 0) ?_
    have e1 : (univ : Finset (ZMod 7)).val.map (fun a => (K742.fiber C (π i) a).card) =
        ((t.getD (i : ℕ) [] : List ℕ) : Multiset ℕ) := hπ i
    rw [e1]
    have e2 : (univ : Finset (ZMod 7)).val.map (fun a : ZMod 7 => (t.getD (i : ℕ) []).getD
        (ZMod.val a) 0) = (Multiset.range 7).map (fun m => (t.getD (i : ℕ) []).getD m 0) := by
      rw [← hZ, Multiset.map_map]; rfl
    rw [e2, ← Multiset.coe_range, Multiset.map_coe]
    congr 1
    apply List.ext_getElem (by simp only [List.length_map, List.length_range]; exact hlen7 i i.2)
    intro m h1 h2
    simp only [List.getElem_map, List.getElem_range]
    rw [List.getD_eq_getElem?_getD (l := t.getD (i : ℕ) []), List.getElem?_eq_getElem h1]
    rfl
  choose σ hσ using hσ
  -- a chave de bloco: o símbolo renomeado da coordenada 0
  let κ : {c // c ∈ C} → Fin 7 := fun c => ⟨((σ 0).symm (c.1 (π 0))).val, ZMod.val_lt _⟩
  have hκ : ∀ c a, κ c = a ↔ c.1 (π 0) = σ 0 ((a : ℕ) : ZMod 7) := by
    intro c a
    rw [← Equiv.symm_apply_eq, Fin.ext_iff]
    constructor
    · intro h; rw [← h]; simp [κ]
    · intro h; simp [κ, h, ZMod.val_natCast, Nat.mod_eq_of_lt a.2]
  let n : Fin 7 → ℕ := fun a => (t.getD 0 []).getD a 0
  have hn : ∑ a, n a = 18 := by
    simp only [n]
    rw [sum_fin_getD, List.take_of_length_le (by rw [hlen7 0 (by omega)]), hsum0]
  have hcard : ∀ a, Fintype.card {c : {c // c ∈ C} // κ c = a} = n a := by
    intro a
    have h := hσ 0 ((a : ℕ) : ZMod 7)
    rw [ZMod.val_natCast, Nat.mod_eq_of_lt a.2] at h
    rw [Fintype.card_subtype, show n a = (t.getD ((0 : Fin 4) : ℕ) []).getD a 0 from rfl, ← h]
    apply Finset.card_bij (fun c _ => c.1)
    · intro c hc
      simp only [mem_filter, mem_univ, true_and] at hc
      simp only [K742.fiber, mem_filter]
      exact ⟨c.2, (hκ c a).1 hc⟩
    · intro c1 _ c2 _ h; exact Subtype.ext h
    · intro b hb
      simp only [K742.fiber, mem_filter] at hb
      refine ⟨⟨b, hb.1⟩, ?_, rfl⟩
      simp only [mem_filter, mem_univ, true_and]
      exact (hκ _ a).2 hb.2
  obtain ⟨E, hE⟩ := exists_block_enum κ n hn hcard
  -- 3. as palavras normalizadas
  let W : Fin 18 → Fin 4 → ℕ := fun k i => ((σ i).symm ((E k).1 (π i))).val
  let w : ℕ → ℕ → ℕ := fun k i =>
    if hk : k < 18 then if hi : i < 4 then W ⟨k, hk⟩ ⟨i, hi⟩ else 0 else 0
  have hw : ∀ k (hk : k < 18) i (hi : i < 4), w k i = W ⟨k, hk⟩ ⟨i, hi⟩ := by
    intro k hk i hi; simp [w, hk, hi]
  have hWeq : ∀ (k : Fin 18) (i : Fin 4) (a : ℕ), a < 7 →
      (W k i = a ↔ (E k).1 (π i) = σ i (a : ZMod 7)) := by
    intro k i a ha
    rw [← Equiv.symm_apply_eq]
    constructor
    · intro h; rw [← h]; simp [W]
    · intro h; simp [W, h, ZMod.val_natCast, Nat.mod_eq_of_lt ha]
  have hN : Normal t w := by
    refine ⟨?_, ?_, ?_, ?_, ?_⟩
    · intro k hk i hi
      rw [hw k hk i hi]
      exact ZMod.val_lt _
    · intro x hx
      let X : Fin 4 → ZMod 7 := fun j => σ (π.symm j) ((x (π.symm j) : ℕ) : ZMod 7)
      obtain ⟨c, hc, hd⟩ := hcov X
      obtain ⟨j1, j2, hne, h1, h2⟩ := agree_two X c hd
      set k := E.symm ⟨c, hc⟩ with hkdef
      have hEk : (E k).1 = c := by rw [hkdef]; simp
      have hval : ∀ j : Fin 4, X j = c j → w k (π.symm j) = x (π.symm j) := by
        intro j hj
        rw [hw k k.2 _ (π.symm j).2, Fin.eta]
        refine (hWeq k _ _ (hx _ (π.symm j).2)).2 ?_
        rw [hEk]
        simp only [Fin.eta, Equiv.apply_symm_apply]
        exact hj.symm
      have hne' : (π.symm j1 : ℕ) ≠ π.symm j2 := by
        intro h; exact hne (π.symm.injective (Fin.ext h))
      rcases Nat.lt_or_gt_of_ne hne' with hlt | hlt
      · exact ⟨k, k.2, (π.symm j1, π.symm j2), mem_pares_of_lt hlt (π.symm j2).2,
          hval j1 h1, hval j2 h2⟩
      · exact ⟨k, k.2, (π.symm j2, π.symm j1), mem_pares_of_lt hlt (π.symm j1).2,
          hval j2 h2, hval j1 h1⟩
    · intro i hi1 hi3 a ha
      have h := hσ ⟨i, by omega⟩ ((a : ℕ) : ZMod 7)
      rw [ZMod.val_natCast, Nat.mod_eq_of_lt ha] at h
      unfold cnt
      rw [filter_range_length, show tv t i a = (t.getD ((⟨i, by omega⟩ : Fin 4) : ℕ) []).getD
        a 0 from rfl, ← h]
      apply Finset.card_bij (fun k hk => ((E ⟨k, by simp at hk; exact hk.1⟩).1))
      · intro k hk
        simp only [mem_filter, Finset.mem_range] at hk
        simp only [K742.fiber, mem_filter]
        refine ⟨(E _).2, ?_⟩
        have := hk.2
        rw [hw k hk.1 i (by omega)] at this
        exact (hWeq _ _ a ha).1 this
      · intro k1 hk1 k2 hk2 h
        have := E.injective (Subtype.ext h)
        simpa using congrArg Fin.val this
      · intro c hc
        simp only [K742.fiber, mem_filter] at hc
        refine ⟨E.symm ⟨c, hc.1⟩, ?_, by simp⟩
        simp only [mem_filter, Finset.mem_range, Fin.is_lt, true_and]
        rw [hw _ (E.symm ⟨c, hc.1⟩).2 i (by omega), Fin.eta]
        refine (hWeq _ _ a ha).2 ?_
        simp [hc.2]
    · intro k hk
      obtain ⟨j, hj, hkj⟩ := hE ⟨k, hk⟩
      have hw0 : w k 0 = (κ (E ⟨k, hk⟩) : ℕ) := by
        rw [hw k hk 0 (by omega)]; rfl
      rw [hw0]
      simp only [block, List.mem_map, List.mem_range]
      refine ⟨j, hj, ?_⟩
      have hs := sum_fin_getD (t.getD 0 []) (κ (E ⟨k, hk⟩))
      have hs' : ∑ i : Fin (κ (E ⟨k, hk⟩)), n (Fin.castLE (κ (E ⟨k, hk⟩)).2.le i) =
          ∑ i : Fin (κ (E ⟨k, hk⟩)), (t.getD 0 []).getD (i : ℕ) 0 := rfl
      simp only [Fin.val_mk] at hkj
      rw [blockStart]
      omega
    · exact hblk18
  exact ⟨t, ht, val t w, cnfSemQuebra_sat t w hN⟩

end K742Ponte

#print axioms K742Ponte.ponte18
