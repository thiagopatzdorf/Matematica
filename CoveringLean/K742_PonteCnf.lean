import CoveringLean.K742_Cnf

/-!
# A ponte, metade CNF: uma lista de 18 palavras "normalizadas" satisfaz `cnfSemQuebra 7 18 t`

Dadas 18 palavras `w k : ℕ → ℕ` (coordenadas `0..3`, símbolos `< 7`) tais que

* (cobertura) todo `x ∈ {0..6}^4` concorda com alguma palavra num dos 6 pares de coordenadas;
* (contadores) para `i = 1, 2, 3`, o símbolo `a` aparece `tv t i a` vezes na coordenada `i`;
* (blocos) a palavra `k` está no bloco do seu símbolo da coordenada 0 (`k ∈ block t (w k 0)`),

a valoração `val t w` satisfaz toda cláusula de `K742Cnf.cnfSemQuebra 7 18 t`
(`cnfSemQuebra_sat`). As variáveis do gerador formam segmentos consecutivos (as `x`, os 21
contadores, os 6 pares); `val` decodifica o número da variável pelo segmento (`segVal`).

Só Lean core: nada aqui depende de Mathlib.
-/

namespace K742Ponte

open K742Cnf LratK

/-! ## Literais -/

theorem litVal_pos (v : Nat → Bool) (n : Nat) : litVal v (pos n) = v n := by
  unfold litVal pos
  have h1 : 2 * n % 2 = 0 := by omega
  have h2 : 2 * n / 2 = n := by omega
  simp [h1, h2]

theorem litVal_neg (v : Nat → Bool) (n : Nat) : litVal v (neg n) = !v n := by
  unfold litVal neg
  have h1 : (2 * n + 1) % 2 = 1 := by omega
  have h2 : (2 * n + 1) / 2 = n := by omega
  simp [h1, h2]

theorem clauseSat_iff (v : Nat → Bool) (c : List Nat) :
    ClauseSat v c ↔ ∃ l ∈ c, litVal v l = true := Iff.rfl

/-! ## Segmentos de variáveis -/

/-- Valor da posição `n` numa sequência de segmentos `(comprimento, valor)`. -/
def segVal : List (Nat × (Nat → Bool)) → Nat → Bool
  | [], _ => false
  | s :: rest, n => if n < s.1 then s.2 n else segVal rest (n - s.1)

/-- Comprimento total. -/
def slen (L : List (Nat × (Nat → Bool))) : Nat := (L.map Prod.fst).sum

theorem segVal_append (A B : List (Nat × (Nat → Bool))) (m : Nat) :
    segVal (A ++ B) (slen A + m) = segVal B m := by
  induction A with
  | nil => simp [slen]
  | cons a A ih =>
    simp only [List.cons_append, segVal, slen, List.map_cons, List.sum_cons]
    rw [if_neg (by omega)]
    have : a.1 + (A.map Prod.fst).sum + m - a.1 = slen A + m := by simp [slen]; omega
    rw [this, ih]

theorem segVal_head (s : Nat × (Nat → Bool)) (B : List (Nat × (Nat → Bool))) (o : Nat)
    (ho : o < s.1) : segVal (s :: B) o = s.2 o := by
  simp [segVal, ho]

theorem segVal_mid (A : List (Nat × (Nat → Bool))) (s : Nat × (Nat → Bool))
    (B : List (Nat × (Nat → Bool))) (o : Nat) (ho : o < s.1) :
    segVal (A ++ s :: B) (slen A + o) = s.2 o := by
  rw [segVal_append, segVal_head _ _ _ ho]

/-- Posição `o` dentro do segmento de índice `i` de `L`, seguido de `B`. -/
theorem segVal_idx (L B : List (Nat × (Nat → Bool))) (i : Nat) (hi : i < L.length) (o : Nat)
    (ho : o < L[i].1) :
    segVal (L ++ B) (slen (L.take i) + o) = L[i].2 o := by
  have hL : L ++ B = L.take i ++ L[i] :: (L.drop (i + 1) ++ B) := by
    have h := List.take_append_drop i L
    rw [List.drop_eq_getElem_cons hi] at h
    rw [← List.cons_append, ← List.append_assoc, h]
  rw [hL, segVal_mid _ _ _ _ ho]

/-! ## Contagem de prefixos -/

/-- Quantos de `b 0, …, b i` são verdadeiros. -/
def cnt (b : Nat → Bool) (i : Nat) : Nat := ((List.range (i + 1)).filter b).length

theorem cnt_zero (b : Nat → Bool) : cnt b 0 = if b 0 = true then 1 else 0 := by
  unfold cnt
  cases h : b 0 <;> simp [List.range_succ, h]

theorem cnt_succ (b : Nat → Bool) (i : Nat) :
    cnt b (i + 1) = cnt b i + if b (i + 1) = true then 1 else 0 := by
  unfold cnt
  rw [List.range_succ (n := i + 1)]
  cases h : b (i + 1) <;> simp [List.filter_append, h]

theorem cnt_le (b : Nat → Bool) (i : Nat) : cnt b i ≤ i + 1 := by
  unfold cnt
  have := List.length_filter_le b (List.range (i + 1))
  simpa using this

/-! ## O contador sequencial -/

/-- Toda cláusula de `exatamente xs k base` vale quando as variáveis de `xs` valem `b`, a
variável `r[i][j]` vale "pelo menos `j+1` dos `b 0..b i`" e exatamente `k` dos `b` valem. -/
theorem exatamente_sat (v : Nat → Bool) (xs : List Nat) (k base : Nat) (b : Nat → Bool)
    (hn : 0 < xs.length) (hk : k ≤ xs.length)
    (hx : ∀ i < xs.length, v (xs.getD i 0) = b i)
    (hr : ∀ i < xs.length, ∀ j ≤ k, v (base + i * (k + 1) + j) = decide (j + 1 ≤ cnt b i))
    (hc : cnt b (xs.length - 1) = k) :
    ∀ c ∈ exatamente xs k base, ClauseSat v c := by
  intro c hc'
  unfold exatamente at hc'
  simp only [show ¬ (k > xs.length) from by omega, if_false] at hc'
  simp only [List.mem_append, List.mem_flatMap, List.mem_range] at hc'
  rcases hc' with (⟨i, hi, j, hj, hcm⟩ | hcm) | hcm
  · by_cases hi0 : i = 0
    · subst hi0
      simp only [if_true] at hcm
      by_cases hj0 : j = 0
      · subst hj0
        simp only [if_true, List.mem_cons, List.not_mem_nil, or_false] at hcm
        have h1 := hr 0 hn 0 (Nat.zero_le _)
        have h2 := hx 0 hn
        simp only [Nat.zero_mul, Nat.add_zero] at h1
        have h1' : v base = b 0 := by rw [h1, cnt_zero]; cases b 0 <;> rfl
        rcases hcm with rfl | rfl <;>
          simp only [clauseSat_iff, List.mem_cons, List.not_mem_nil, or_false,
            exists_eq_or_imp, exists_eq_left, litVal_pos, litVal_neg, Nat.zero_mul,
            Nat.add_zero, h1', h2] <;>
          cases hb : b 0 <;> simp
      · simp only [hj0, if_false, List.mem_cons, List.not_mem_nil, or_false] at hcm
        subst hcm
        have h1 := hr 0 hn j (by omega)
        simp only [Nat.zero_mul, Nat.add_zero] at h1
        have := cnt_le b 0
        simp only [clauseSat_iff, List.mem_cons, List.not_mem_nil, or_false, exists_eq_left,
          litVal_neg, Nat.zero_mul, Nat.add_zero, h1]
        simp; omega
    · simp only [hi0, if_false] at hcm
      obtain ⟨i', rfl⟩ : ∃ i', i = i' + 1 := ⟨i - 1, by omega⟩
      simp only [Nat.add_sub_cancel] at hcm
      have hcs := cnt_succ b i'
      have hxi := hx (i' + 1) hi
      have hrr : ∀ j' ≤ k, v (base + (i' + 1) * (k + 1) + j') =
          decide (j' + 1 ≤ cnt b (i' + 1)) := hr (i' + 1) hi
      have hrp : ∀ j' ≤ k, v (base + i' * (k + 1) + j') = decide (j' + 1 ≤ cnt b i') :=
        hr i' (by omega)
      rcases List.mem_cons.1 hcm with rfl | hcm
      · simp only [clauseSat_iff, List.mem_cons, List.not_mem_nil, or_false, exists_eq_or_imp,
          exists_eq_left, litVal_pos, litVal_neg, hrr j (by omega), hrp j (by omega)]
        simp only [Bool.not_eq_true', decide_eq_false_iff_not, decide_eq_true_eq]
        omega
      · by_cases hj0 : j = 0
        · subst hj0
          simp only [if_true, List.mem_cons, List.not_mem_nil, or_false] at hcm
          rcases hcm with rfl | rfl <;>
            simp only [clauseSat_iff, List.mem_cons, List.not_mem_nil, or_false,
              exists_eq_or_imp, exists_eq_left, litVal_pos, litVal_neg, hxi,
              hrr 0 (by omega), hrp 0 (by omega)] <;>
            cases hb : b (i' + 1) <;> simp [hb] at hcs ⊢ <;> omega
        · simp only [hj0, if_false, List.mem_cons, List.not_mem_nil, or_false] at hcm
          have hjm : j - 1 + 1 = j := by omega
          have e1 := hrp (j - 1) (by omega)
          rw [hjm] at e1
          rcases hcm with rfl | rfl | rfl <;>
            simp only [clauseSat_iff, List.mem_cons, List.not_mem_nil, or_false,
              exists_eq_or_imp, exists_eq_left, litVal_pos, litVal_neg, hxi,
              hrr j (by omega), hrp j (by omega), e1] <;>
            cases hb : b (i' + 1) <;> simp [hb] at hcs ⊢ <;> omega
  · by_cases hk0 : k > 0
    · simp only [hk0, if_true, List.mem_cons, List.not_mem_nil, or_false] at hcm
      subst hcm
      have h1 := hr (xs.length - 1) (by omega) (k - 1) (by omega)
      have hkm : k - 1 + 1 = k := by omega
      rw [hkm, hc] at h1
      simp [clauseSat_iff, litVal_pos, h1]
    · simp [hk0] at hcm
  · simp only [List.mem_cons, List.not_mem_nil, or_false] at hcm
    subst hcm
    have h1 := hr (xs.length - 1) (by omega) k (Nat.le_refl _)
    rw [hc] at h1
    simp [clauseSat_iff, litVal_neg, h1]

/-! ## A valoração -/

section Val

variable (t : List (List Nat)) (w : Nat → Nat → Nat)

/-- As variáveis `x[k][i][a]`: `378 = 18 · 3 · 7` posições. -/
def xSeg : Nat × (Nat → Bool) := (378, fun o => decide (w (o / 21) (o % 21 / 7 + 1) = o % 7))

/-- O contador de `(i, a)`: `r[l][j]` = "pelo menos `j+1` das palavras `0..l` têm `a` em `i`". -/
def cSeg (ia : Nat × Nat) : Nat × (Nat → Bool) :=
  (18 * (tv t ia.1 ia.2 + 1), fun o =>
    decide (o % (tv t ia.1 ia.2 + 1) + 1 ≤
      cnt (fun l => decide (w l ia.1 = ia.2)) (o / (tv t ia.1 ia.2 + 1))))

/-- O par de coordenadas `(i, j)`: as projeções `P[a,b]` e, para `i ≥ 1`, os auxiliares `y`. -/
def pSeg (ij : Nat × Nat) : Nat × (Nat → Bool) :=
  if ij.1 = 0 then (49, fun o => (block t (o / 7)).any fun k => decide (w k ij.2 = o % 7))
  else (49 * 19, fun o =>
    if o % 19 = 0 then
      (List.range 18).any fun k => decide (w k ij.1 = o / 19 / 7 ∧ w k ij.2 = o / 19 % 7)
    else decide (w (o % 19 - 1) ij.1 = o / 19 / 7 ∧ w (o % 19 - 1) ij.2 = o / 19 % 7))

def cSegs : List (Nat × (Nat → Bool)) := (counterKeys 7).map (cSeg t w)
def pSegs : List (Nat × (Nat → Bool)) := pares.map (pSeg t w)

/-- A valoração: a variável `n ≥ 1` é a posição `n − 1` dos segmentos. -/
def val (n : Nat) : Bool := segVal (xSeg w :: (cSegs t w ++ pSegs t w)) (n - 1)

theorem val_x {k i a : Nat} (hk : k < 18) (hi1 : 1 ≤ i) (hi3 : i ≤ 3) (ha : a < 7) :
    val t w (xv 7 k i a) = decide (w k i = a) := by
  unfold val xv
  rw [segVal_head _ _ _ (by simp only [xSeg]; omega)]
  simp only [xSeg]
  have e1 : (1 + k * (3 * 7) + (i - 1) * 7 + a - 1) / 21 = k := by omega
  have e2 : (1 + k * (3 * 7) + (i - 1) * 7 + a - 1) % 21 / 7 + 1 = i := by omega
  have e3 : (1 + k * (3 * 7) + (i - 1) * 7 + a - 1) % 7 = a := by omega
  rw [e1, e2, e3]

theorem counterKeys_length : (counterKeys 7).length = 21 := by decide

theorem slen_cSegs_take (idx : Nat) :
    slen ((cSegs t w).take idx) =
      (((counterKeys 7).take idx).map fun (i, a) => 18 * (tv t i a + 1)).sum := by
  unfold slen cSegs
  rw [← List.map_take, List.map_map]
  rfl

theorem div_mod_aux (i j m : Nat) (hj : j < m) : (i * m + j) / m = i ∧ (i * m + j) % m = j := by
  have hm : 0 < m := by omega
  constructor
  · rw [Nat.add_comm, Nat.add_mul_div_right _ _ hm, Nat.div_eq_of_lt hj, Nat.zero_add]
  · rw [Nat.add_comm, Nat.add_mul_mod_self_right, Nat.mod_eq_of_lt hj]

theorem val_c {idx : Nat} (hidx : idx < 21) {i' j : Nat} (hi' : i' < 18)
    (hj : j ≤ tv t ((counterKeys 7)[idx]'(by rw [counterKeys_length]; exact hidx)).1
      ((counterKeys 7)[idx]'(by rw [counterKeys_length]; exact hidx)).2) :
    val t w (counterBase 7 18 t idx +
        i' * (tv t ((counterKeys 7)[idx]'(by rw [counterKeys_length]; exact hidx)).1
          ((counterKeys 7)[idx]'(by rw [counterKeys_length]; exact hidx)).2 + 1) + j) =
      decide (j + 1 ≤ cnt (fun l => decide
        (w l ((counterKeys 7)[idx]'(by rw [counterKeys_length]; exact hidx)).1 =
          ((counterKeys 7)[idx]'(by rw [counterKeys_length]; exact hidx)).2)) i') := by
  generalize hia : (counterKeys 7)[idx]'(by rw [counterKeys_length]; exact hidx) = ia at *
  have hlen : idx < (cSegs t w).length := by simp [cSegs, counterKeys_length, hidx]
  have hget : (cSegs t w)[idx] = cSeg t w ia := by simp [cSegs, hia]
  unfold val counterBase
  have hpos : 1 + 18 * (3 * 7) + (((counterKeys 7).take idx).map
      fun (ia : Nat × Nat) => 18 * (tv t ia.1 ia.2 + 1)).sum +
      i' * (tv t ia.1 ia.2 + 1) + j - 1 =
      (xSeg w).1 + (slen ((cSegs t w).take idx) + (i' * (tv t ia.1 ia.2 + 1) + j)) := by
    rw [slen_cSegs_take]
    simp only [xSeg]
    omega
  have hpos' := hpos
  simp only [show (fun (ia : Nat × Nat) => 18 * (tv t ia.1 ia.2 + 1)) =
    (fun x => match x with | (i, a) => 18 * (tv t i a + 1)) from rfl] at hpos'
  rw [hpos', segVal]
  rw [if_neg (by omega), Nat.add_sub_cancel_left]
  have hlt : i' * (tv t ia.1 ia.2 + 1) + j < ((cSegs t w)[idx]).1 := by
    rw [hget]; simp only [cSeg]
    have : i' * (tv t ia.1 ia.2 + 1) + j < (i' + 1) * (tv t ia.1 ia.2 + 1) := by
      rw [Nat.succ_mul]; omega
    have h2 : (i' + 1) * (tv t ia.1 ia.2 + 1) ≤ 18 * (tv t ia.1 ia.2 + 1) :=
      Nat.mul_le_mul_right _ (by omega)
    omega
  rw [segVal_idx _ _ _ hlen _ hlt, hget]
  simp only [cSeg]
  obtain ⟨d1, d2⟩ := div_mod_aux i' j (tv t ia.1 ia.2 + 1) (by omega)
  rw [d1, d2]

theorem val_c' {idx i a : Nat} (h : (counterKeys 7)[idx]? = some (i, a)) {i' j : Nat}
    (hi' : i' < 18) (hj : j ≤ tv t i a) :
    val t w (counterBase 7 18 t idx + i' * (tv t i a + 1) + j) =
      decide (j + 1 ≤ cnt (fun l => decide (w l i = a)) i') := by
  obtain ⟨hlt, heq⟩ := List.getElem?_eq_some_iff.1 h
  have hidx : idx < 21 := by rw [counterKeys_length] at hlt; exact hlt
  have := val_c t w hidx hi' (j := j) (by simp only [heq]; exact hj)
  simpa only [heq] using this

theorem pares_length : pares.length = 6 := rfl

theorem slen_pSegs_take (p : Nat) :
    slen ((pSegs t w).take p) = ((pares.take p).map (pairSize 7 18)).sum := by
  unfold slen pSegs
  rw [← List.map_take, List.map_map]
  congr 2
  funext ij
  simp only [Function.comp, pSeg, pairSize]
  split <;> rfl

theorem counterBase_eq (idx : Nat) :
    counterBase 7 18 t idx = 1 + (xSeg w).1 + slen ((cSegs t w).take idx) := by
  unfold counterBase slen cSegs
  rw [← List.map_take, List.map_map]
  rfl

theorem projBase_eq : projBase 7 18 t - 1 = (xSeg w).1 + slen (cSegs t w) := by
  unfold projBase
  rw [counterBase_eq t w]
  have h2 : (cSegs t w).take (3 * 7) = cSegs t w :=
    List.take_of_length_le (by simp [cSegs, counterKeys_length])
  rw [h2]
  omega

theorem val_p {p : Nat} (hp : p < 6) {o : Nat}
    (ho : o < (pSeg t w (pares[p]'(by rw [pares_length]; exact hp))).1) :
    val t w (pairBase 7 18 t p + o) = (pSeg t w (pares[p]'(by rw [pares_length]; exact hp))).2 o := by
  have hpb : pairBase 7 18 t p + o - 1 =
      (xSeg w).1 + (slen (cSegs t w) + (slen ((pSegs t w).take p) + o)) := by
    unfold pairBase
    have := projBase_eq t w
    have h1 : 1 ≤ projBase 7 18 t := by unfold projBase counterBase; omega
    rw [slen_pSegs_take]
    omega
  unfold val
  rw [hpb, segVal, if_neg (by omega), Nat.add_sub_cancel_left, segVal_append]
  have hlen : p < (pSegs t w).length := by simp [pSegs, pares_length, hp]
  have hget : (pSegs t w)[p] = pSeg t w (pares[p]'(by rw [pares_length]; exact hp)) := by
    simp [pSegs]
  have := segVal_idx (pSegs t w) [] p hlen o (by rw [hget]; exact ho)
  rw [List.append_nil, hget] at this
  exact this

theorem pv_eq {p i j : Nat} (h : pares[p]? = some (i, j)) (a b : Nat) :
    pv 7 18 t p a b = if i = 0 then pairBase 7 18 t p + (a * 7 + b)
      else pairBase 7 18 t p + (a * 7 + b) * 19 := by
  have hg : pares.getD p (0, 0) = (i, j) := by rw [List.getD_eq_getElem?_getD, h]; rfl
  unfold pv
  simp only [hg]
  split <;> omega

theorem val_P0 {p j a b : Nat} (h : pares[p]? = some (0, j)) (ha : a < 7) (hb : b < 7) :
    val t w (pv 7 18 t p a b) = (block t a).any fun k => decide (w k j = b) := by
  obtain ⟨hlt, heq⟩ := List.getElem?_eq_some_iff.1 h
  rw [pv_eq t h, if_pos rfl]
  have hp : p < 6 := hlt
  rw [val_p t w hp (by rw [heq]; unfold pSeg; rw [if_pos rfl]; omega)]
  rw [heq]; unfold pSeg; rw [if_pos rfl]; dsimp only
  have e1 : (a * 7 + b) / 7 = a := by omega
  have e2 : (a * 7 + b) % 7 = b := by omega
  rw [e1, e2]

theorem val_P1 {p i j a b : Nat} (h : pares[p]? = some (i, j)) (hi : i ≠ 0) (ha : a < 7)
    (hb : b < 7) :
    val t w (pv 7 18 t p a b) =
      (List.range 18).any fun k => decide (w k i = a ∧ w k j = b) := by
  obtain ⟨hlt, heq⟩ := List.getElem?_eq_some_iff.1 h
  rw [pv_eq t h, if_neg hi]
  have hp : p < 6 := hlt
  rw [val_p t w hp (by rw [heq]; unfold pSeg; rw [if_neg hi]; dsimp only; omega)]
  rw [heq]; unfold pSeg; rw [if_neg hi]; dsimp only
  have e0 : (a * 7 + b) * 19 % 19 = 0 := by omega
  have e1 : (a * 7 + b) * 19 / 19 / 7 = a := by omega
  have e2 : (a * 7 + b) * 19 / 19 % 7 = b := by omega
  rw [if_pos e0, e1, e2]

theorem val_Y {p i j a b k : Nat} (h : pares[p]? = some (i, j)) (hi : i ≠ 0) (ha : a < 7)
    (hb : b < 7) (hk : k < 18) :
    val t w (pv 7 18 t p a b + 1 + k) = decide (w k i = a ∧ w k j = b) := by
  obtain ⟨hlt, heq⟩ := List.getElem?_eq_some_iff.1 h
  rw [pv_eq t h, if_neg hi]
  have hp : p < 6 := hlt
  rw [Nat.add_assoc, Nat.add_assoc,
    val_p t w hp (o := (a * 7 + b) * 19 + (1 + k)) (by rw [heq]; unfold pSeg; rw [if_neg hi]; dsimp only; omega)]
  rw [heq]; unfold pSeg; rw [if_neg hi]; dsimp only
  have e0 : ((a * 7 + b) * 19 + (1 + k)) % 19 = k + 1 := by omega
  have e1 : ((a * 7 + b) * 19 + (1 + k)) / 19 / 7 = a := by omega
  have e2 : ((a * 7 + b) * 19 + (1 + k)) / 19 % 7 = b := by omega
  rw [if_neg (by omega), e0, e1, e2, Nat.add_sub_cancel]

end Val

/-! ## As quatro famílias de cláusulas -/

section Sat

variable (t : List (List Nat)) (w : Nat → Nat → Nat)

/-- As hipóteses sobre as 18 palavras normalizadas. -/
structure Normal : Prop where
  sym : ∀ k < 18, ∀ i < 4, w k i < 7
  cover : ∀ x : Nat → Nat, (∀ i < 4, x i < 7) →
    ∃ k < 18, ∃ ij ∈ pares, w k ij.1 = x ij.1 ∧ w k ij.2 = x ij.2
  count : ∀ i, 1 ≤ i → i ≤ 3 → ∀ a < 7, cnt (fun l => decide (w l i = a)) 17 = tv t i a
  blk : ∀ k < 18, k ∈ block t (w k 0)
  blk18 : ∀ a < 7, ∀ k ∈ block t a, k < 18

theorem mem_counterKeys {i a : Nat} (h : (i, a) ∈ counterKeys 7) :
    1 ≤ i ∧ i ≤ 3 ∧ a < 7 := by
  simp only [counterKeys, List.mem_flatMap, List.mem_map, List.mem_range, List.mem_cons,
    List.not_mem_nil, or_false, Prod.mk.injEq] at h
  obtain ⟨i', hi', a', ha', rfl, rfl⟩ := h
  omega

theorem mem_pares {i j : Nat} (h : (i, j) ∈ pares) : i < j ∧ j < 4 := by
  simp only [pares, List.mem_cons, List.not_mem_nil, or_false, Prod.mk.injEq] at h
  omega

theorem exactlyOne_sat (hN : Normal t w) : ∀ c ∈ exactlyOne 7 18, ClauseSat (val t w) c := by
  intro c hc
  simp only [exactlyOne, List.mem_flatMap, List.mem_range, List.mem_cons, List.not_mem_nil,
    or_false, List.mem_map] at hc
  obtain ⟨k, hk, i, hi, hc⟩ := hc
  have hi' : 1 ≤ i ∧ i ≤ 3 := by omega
  rcases hc with rfl | ⟨⟨a, b⟩, hab, rfl⟩
  · refine ⟨pos (xv 7 k i (w k i)), List.mem_map.2 ⟨w k i, ?_, rfl⟩, ?_⟩
    · exact List.mem_range.2 (hN.sym k hk i (by omega))
    · rw [litVal_pos, val_x t w hk hi'.1 hi'.2 (hN.sym k hk i (by omega))]
      simp
  · simp only [combos2, List.mem_flatMap, List.mem_map, List.mem_filter, List.mem_range,
      decide_eq_true_eq, Prod.mk.injEq] at hab
    obtain ⟨a', ha', b', ⟨hb', hab'⟩, rfl, rfl⟩ := hab
    by_cases hwa : w k i = a'
    · refine ⟨neg (xv 7 k i b'), by simp, ?_⟩
      rw [litVal_neg, val_x t w hk hi'.1 hi'.2 hb']
      simp; omega
    · refine ⟨neg (xv 7 k i a'), by simp, ?_⟩
      rw [litVal_neg, val_x t w hk hi'.1 hi'.2 ha']
      simp [hwa]

theorem counters_sat (hN : Normal t w) : ∀ c ∈ counters 7 18 t, ClauseSat (val t w) c := by
  intro c hc
  simp only [counters, List.mem_flatMap] at hc
  obtain ⟨⟨⟨i, a⟩, idx⟩, hmem, hc⟩ := hc
  have hget : (counterKeys 7)[idx]? = some (i, a) := List.mem_zipIdx_iff_getElem?.1 hmem
  obtain ⟨hi1, hi3, ha⟩ := mem_counterKeys (List.mem_of_getElem? hget)
  have hcnt := hN.count i hi1 hi3 a ha
  refine exatamente_sat (val t w) _ _ _ (fun l => decide (w l i = a)) (by simp) ?_ ?_ ?_ ?_ c hc
  · have := cnt_le (fun l => decide (w l i = a)) 17
    simp; omega
  · intro l hl
    simp only [List.length_map, List.length_range] at hl
    simp only [List.getD_eq_getElem?_getD, List.getElem?_map, List.getElem?_range hl,
      Option.map_some, Option.getD_some]
    exact val_x t w hl hi1 hi3 ha
  · intro l hl j hj
    simp only [List.length_map, List.length_range] at hl
    exact val_c' t w hget hl hj
  · simpa using hcnt

theorem projections_sat (hN : Normal t w) :
    ∀ c ∈ projections 7 18 t, ClauseSat (val t w) c := by
  intro c hc
  simp only [projections, List.mem_flatMap, List.mem_range] at hc
  obtain ⟨⟨⟨i, j⟩, p⟩, hmem, a, ha, b, hb, hc⟩ := hc
  have hget : pares[p]? = some (i, j) := List.mem_zipIdx_iff_getElem?.1 hmem
  obtain ⟨hij, hj4⟩ := mem_pares (List.mem_of_getElem? hget)
  by_cases hi0 : i = 0
  · subst hi0
    have hP := val_P0 t w hget ha hb
    dsimp only at hc
    rw [if_pos rfl] at hc
    rcases List.mem_cons.1 hc with rfl | hc
    · cases hv : (block t a).any fun k => decide (w k j = b)
      · exact ⟨neg (pv 7 18 t p a b), by simp, by rw [litVal_neg, hP, hv]; rfl⟩
      · obtain ⟨k, hk, hkb⟩ := List.any_eq_true.1 hv
        have hk18 := hN.blk18 a ha k hk
        refine ⟨pos (xv 7 k j b), by simp; exact Or.inr ⟨k, hk, rfl⟩, ?_⟩
        rw [litVal_pos, val_x t w hk18 (by omega) (by omega) hb]
        exact hkb
    · obtain ⟨l, hl, rfl⟩ := List.mem_map.1 hc
      obtain ⟨k, hk, rfl⟩ := List.mem_map.1 hl
      have hk18 := hN.blk18 a ha k hk
      by_cases hkb : w k j = b
      · refine ⟨pos (pv 7 18 t p a b), by simp, ?_⟩
        rw [litVal_pos, hP]
        exact List.any_eq_true.2 ⟨k, hk, by simp [hkb]⟩
      · refine ⟨pos (xv 7 k j b) + 1, by simp, ?_⟩
        rw [show pos (xv 7 k j b) + 1 = neg (xv 7 k j b) from rfl, litVal_neg,
          val_x t w hk18 (by omega) (by omega) hb]
        simp [hkb]
  · dsimp only at hc
    simp only [if_neg hi0, List.mem_append, List.mem_flatMap, List.mem_range, List.mem_cons,
      List.not_mem_nil, or_false] at hc
    have hP := val_P1 t w hget hi0 ha hb
    rcases hc with ⟨k, hk, hc⟩ | rfl
    · have hY := val_Y t w hget hi0 ha hb hk
      have hxa := val_x t w hk (by omega) (by omega) ha (i := i) (a := a)
      have hxb := val_x t w hk (by omega) (by omega) hb (i := j) (a := b)
      rcases hc with rfl | rfl | rfl | rfl <;>
        simp only [clauseSat_iff, List.mem_cons, List.not_mem_nil, or_false, exists_eq_or_imp,
          exists_eq_left, litVal_pos, litVal_neg, hY, hxa, hxb, hP]
      · by_cases h1 : w k i = a <;> simp [h1]
      · by_cases h1 : w k j = b <;> simp [h1]
      · by_cases h1 : w k i = a <;> by_cases h2 : w k j = b <;> simp [h1, h2]
      · by_cases h1 : w k i = a ∧ w k j = b
        · right; exact List.any_eq_true.2 ⟨k, List.mem_range.2 hk, by simp [h1]⟩
        · left; simp [h1]
    · cases hv : (List.range 18).any fun k => decide (w k i = a ∧ w k j = b)
      · exact ⟨neg (pv 7 18 t p a b), by simp, by rw [litVal_neg, hP, hv]; rfl⟩
      · obtain ⟨k, hk, hkb⟩ := List.any_eq_true.1 hv
        have hk' := List.mem_range.1 hk
        refine ⟨pos (pv 7 18 t p a b + 1 + k), by simp; exact Or.inr ⟨k, hk', rfl⟩, ?_⟩
        rw [litVal_pos, val_Y t w hget hi0 ha hb hk']
        exact hkb

theorem coverage_sat (hN : Normal t w) : ∀ c ∈ coverage 7 18 t, ClauseSat (val t w) c := by
  intro c hc
  simp only [coverage, List.mem_flatMap, List.mem_range, List.mem_map] at hc
  obtain ⟨w0, h0, w1, h1, w2, h2, w3, h3, rfl⟩ := hc
  let x : Nat → Nat := fun i => [w0, w1, w2, w3].getD i 0
  have hx : ∀ i < 4, x i < 7 := by
    intro i hi
    obtain rfl | rfl | rfl | rfl : i = 0 ∨ i = 1 ∨ i = 2 ∨ i = 3 := by omega
    all_goals simpa [x]
  obtain ⟨k, hk, ⟨i, j⟩, hij, hwi, hwj⟩ := hN.cover x hx
  obtain ⟨p, hp⟩ := List.mem_iff_getElem?.1 hij
  obtain ⟨hlt, hj4⟩ := mem_pares hij
  refine ⟨pos (pv 7 18 t p (x i) (x j)), ?_, ?_⟩
  · exact List.mem_map.2 ⟨((i, j), p), List.mem_zipIdx_iff_getElem?.2 hp, rfl⟩
  · rw [litVal_pos]
    by_cases hi0 : i = 0
    · subst hi0
      rw [val_P0 t w hp (hx 0 (by omega)) (hx j hj4)]
      refine List.any_eq_true.2 ⟨k, ?_, by simp [hwj]⟩
      rw [← hwi]; exact hN.blk k hk
    · rw [val_P1 t w hp hi0 (hx i (by omega)) (hx j hj4)]
      exact List.any_eq_true.2 ⟨k, List.mem_range.2 hk, by simp [hwi, hwj]⟩

/-- **A metade CNF da ponte**: palavras normalizadas satisfazem a CNF sem quebra. -/
theorem cnfSemQuebra_sat (hN : Normal t w) :
    ∀ c ∈ cnfSemQuebra 7 18 t, ClauseSat (val t w) c := by
  intro c hc
  simp only [cnfSemQuebra, List.mem_append] at hc
  rcases hc with ((h | h) | h) | h
  · exact exactlyOne_sat t w hN c h
  · exact counters_sat t w hN c h
  · exact projections_sat t w hN c h
  · exact coverage_sat t w hN c h

end Sat

end K742Ponte

#print axioms K742Ponte.cnfSemQuebra_sat
