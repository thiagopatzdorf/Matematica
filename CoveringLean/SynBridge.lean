import Mathlib
import CoveringLean.SynCheck
import CoveringLean.K3_Bridge

/-!
# SynBridge: correção do certificado por síndromes (tamanho fixo, genérico em `q, n, k, o`)

`Syn.syn_cert` transforma as checagens booleanas de `SynCheck.lean` (rodadas pelo kernel nas
folhas `SynLeaf_*`) em

    ∃ C : Finset (Fin n → ZMod q), C.card = M ∧ CoveringA2.Covers R C

com `C = codeOf q n L`, a lista ordenada do código (a mesma cujo sha256 canônico está no
cabeçalho do arquivo de dados).  O argumento:

1. `x = y + c` com `c = a·G` (`a` = dígitos de `x` no bloco `[o, o+k)`, porque `G` é a
   identidade ali — `chkPiv`) e `y` nulo no bloco, isto é, `y = y_t` para um `t < q^(n-k)`;
2. se `t` tem testemunha `(s, m)`, então `x` está a distância `≤ R` de `rₛ + (m + a)·G`, que
   é palavra de `L` (`chkB` checa os `q^k` membros de cada coset);
3. se `t` é órfão, `x = y_t + a·G` é um dos pontos checados um a um por `chkO`.

Sem `sorry`, sem `native_decide`, sem axioma novo.
-/

namespace Syn

open CoveringKernel CoveringCerts

/-! ### Normalização: as checagens usam `Nat.add`/`Nat.beq`… (rápidos no kernel); as provas, `+`/`=`. -/

theorem nmod (a b : ℕ) : Nat.mod a b = a % b := rfl
theorem ndiv (a b : ℕ) : Nat.div a b = a / b := rfl
theorem nadd (a b : ℕ) : Nat.add a b = a + b := rfl
theorem nmul (a b : ℕ) : Nat.mul a b = a * b := rfl
theorem npow (a b : ℕ) : Nat.pow a b = a ^ b := rfl
theorem nsub (a b : ℕ) : Nat.sub a b = a - b := rfl
theorem nshr (a b : ℕ) : Nat.shiftRight a b = a >>> b := rfl
theorem beq_true {a b : ℕ} (h : a = b) : Nat.beq a b = true := by subst h; exact Nat.beq_refl a
theorem beq_false {a b : ℕ} (h : a ≠ b) : Nat.beq a b = false := by
  cases h' : Nat.beq a b
  · rfl
  · exact absurd (Nat.eq_of_beq_eq_true h') h
theorem beq_iff {a b : ℕ} : Nat.beq a b = true ↔ a = b := ⟨Nat.eq_of_beq_eq_true, beq_true⟩
theorem ble_iff {a b : ℕ} : Nat.ble a b = true ↔ a ≤ b := ⟨Nat.le_of_ble_eq_true, Nat.ble_eq_true_of_le⟩
theorem blt_iff {a b : ℕ} : Nat.blt a b = true ↔ a < b := ⟨Nat.le_of_ble_eq_true, Nat.ble_eq_true_of_le⟩

attribute [local simp] nmod ndiv nadd nmul npow nsub nshr beq_iff ble_iff blt_iff

/-! ### Fatos de `Nat` sobre dígitos e codificação -/

theorem D_eq (q w i : ℕ) : D q w i = w / q ^ i % q := rfl

theorem D_lt {q : ℕ} (hq : 0 < q) (w i : ℕ) : D q w i < q := Nat.mod_lt _ hq

theorem D_zero (q w : ℕ) : D q w 0 = w % q := by simp [D_eq]

theorem D_succ (q w i : ℕ) : D q w (i + 1) = D q (w / q) i := by
  simp only [D_eq, pow_succ', Nat.div_div_eq_div_mul]

theorem enc_succ (q : ℕ) (f : ℕ → ℕ) (n : ℕ) :
    enc q f (n + 1) = f 0 + q * enc q (fun i => f (i + 1)) n := rfl

theorem D_enc {q : ℕ} (hq : 0 < q) : ∀ (n : ℕ) (f : ℕ → ℕ), (∀ i < n, f i < q) →
    ∀ i < n, D q (enc q f n) i = f i := by
  intro n
  induction n with
  | zero => intro f _ i hi; omega
  | succ n ih =>
    intro f hf i hi
    have h0 := hf 0 (by omega)
    cases i with
    | zero =>
      rw [D_zero, enc_succ, Nat.add_mul_mod_self_left, Nat.mod_eq_of_lt h0]
    | succ i =>
      rw [D_succ, enc_succ, Nat.add_mul_div_left _ _ hq, Nat.div_eq_of_lt h0, zero_add]
      exact ih (fun i => f (i + 1)) (fun j hj => hf (j + 1) (by omega)) i (by omega)

theorem enc_lt {q : ℕ} (hq : 0 < q) : ∀ (n : ℕ) (f : ℕ → ℕ), (∀ i < n, f i < q) →
    enc q f n < q ^ n := by
  intro n
  induction n with
  | zero => intro f _; simp [enc]
  | succ n ih =>
    intro f hf
    have h0 := hf 0 (by omega)
    have h1 := ih (fun i => f (i + 1)) (fun j hj => hf (j + 1) (by omega))
    rw [enc_succ, pow_succ']
    nlinarith

/-- Soma dígito a dígito (mod `q`) de duas mensagens de `K` dígitos. -/
def dsum (q : ℕ) : ℕ → ℕ → ℕ → ℕ
  | 0, _, _ => 0
  | K + 1, m, a => (m % q + a % q) % q + q * dsum q K (m / q) (a / q)

theorem dsum_lt {q : ℕ} (hq : 0 < q) : ∀ (K m a : ℕ), dsum q K m a < q ^ K := by
  intro K
  induction K with
  | zero => intro m a; simp [dsum]
  | succ K ih =>
    intro m a
    have h0 : (m % q + a % q) % q < q := Nat.mod_lt _ hq
    have h1 := ih (m / q) (a / q)
    simp only [dsum, pow_succ']
    nlinarith

theorem S_cons (q g : ℕ) (gs : List ℕ) (m i : ℕ) :
    S q (g :: gs) m i = m % q * D q g i + S q gs (m / q) i := rfl

theorem S_dsum {q : ℕ} (hq : 0 < q) : ∀ (Gs : List ℕ) (m a i : ℕ),
    ((S q Gs (dsum q Gs.length m a) i : ℕ) : ZMod q) = (S q Gs m i : ZMod q) + S q Gs a i := by
  intro Gs
  induction Gs with
  | nil => intro m a i; simp [S]
  | cons g gs ih =>
    intro m a i
    have h0 : (m % q + a % q) % q < q := Nat.mod_lt _ hq
    have hmod : dsum q (gs.length + 1) m a % q = (m % q + a % q) % q := by
      simp only [dsum]; rw [Nat.add_mul_mod_self_left, Nat.mod_eq_of_lt h0]
    have hdiv : dsum q (gs.length + 1) m a / q = dsum q gs.length (m / q) (a / q) := by
      simp only [dsum]; rw [Nat.add_mul_div_left _ _ hq, Nat.div_eq_of_lt h0, zero_add]
    rw [List.length_cons, S_cons, S_cons, S_cons, hmod, hdiv]
    simp only [Nat.cast_add, Nat.cast_mul, ZMod.natCast_mod, ih]
    ring

/-! ### Funções booleanas → proposições -/

theorem dist_eq (a b : ℕ → ℕ) : ∀ m, dist a b m = distI a b m := by
  intro m
  induction m with
  | zero => rfl
  | succ m ih =>
    show dist a b m + cond (Nat.beq (a m) (b m)) 0 1 = distI a b m + (if a m = b m then 0 else 1)
    rw [ih]
    by_cases h : a m = b m
    · simp [h]
    · simp [h, beq_false h]

theorem distI_congr (a b b' : ℕ → ℕ) : ∀ m, (∀ i < m, b i = b' i) → distI a b m = distI a b' m := by
  intro m
  induction m with
  | zero => intro _; rfl
  | succ m ih =>
    intro h
    simp only [distI]
    rw [ih (fun i hi => h i (by omega)), h m (by omega)]

theorem memN_sound (x : ℕ) : ∀ l : List ℕ, memN x l = true → x ∈ l := by
  intro l
  induction l with
  | nil => intro h; simp [memN] at h
  | cons y ys ih =>
    intro h
    by_cases hxy : x = y
    · simp [hxy]
    · simp only [memN, beq_false hxy, Bool.cond_false] at h
      exact List.mem_cons_of_mem _ (ih h)

theorem pget_mem (b : ℕ) : ∀ (c PN j : ℕ), j < c → pget PN b j ∈ unpack b c PN := by
  intro c
  induction c with
  | zero => intro _ j hj; omega
  | succ c ih =>
    intro PN j hj
    cases j with
    | zero => simp [pget, unpack]
    | succ j =>
      have : pget PN b (j + 1) = pget (PN >>> b) b j := by
        simp only [pget, nmod, nmul, nshr, npow]
        rw [show b * (j + 1) = b + b * j by ring, Nat.shiftRight_add]
      rw [this]
      exact List.mem_cons_of_mem _ (ih _ j (by omega))

theorem chkT_sound (P : Spec) (B : ℕ) : ∀ (c t N : ℕ), chkT P B c t N = true →
    ∀ i < c, ∃ w, okT P (t + i) w = true := by
  intro c
  induction c with
  | zero => intro _ _ _ i hi; omega
  | succ c ih =>
    intro t N h i hi
    simp only [chkT, Bool.and_eq_true] at h
    cases i with
    | zero => exact ⟨_, h.1⟩
    | succ i =>
      obtain ⟨w, hw⟩ := ih (Nat.add t 1) (N / B) h.2 i (by omega)
      exact ⟨w, by rw [show t + (i + 1) = Nat.add t 1 + i by simp [Nat.add_eq]; omega]; exact hw⟩

theorem chkO_sound' (P : Spec) (B t : ℕ) : ∀ (c a N : ℕ), chkO P B t c a N = true →
    ∀ i < c, ∃ j, okO P t (a + i) j = true := by
  intro c
  induction c with
  | zero => intro _ _ _ i hi; omega
  | succ c ih =>
    intro a N h i hi
    simp only [chkO, Bool.and_eq_true] at h
    cases i with
    | zero => exact ⟨_, h.1⟩
    | succ i =>
      obtain ⟨w, hw⟩ := ih (Nat.add a 1) (N / B) h.2 i (by omega)
      exact ⟨w, by rw [show a + (i + 1) = Nat.add a 1 + i by simp [Nat.add_eq]; omega]; exact hw⟩

theorem chkO_sound (P : Spec) (B t c N : ℕ) (h : chkO P B t c 0 N = true) :
    ∀ a < c, ∃ j, okO P t a j = true := by
  intro a ha
  simpa using chkO_sound' P B t c 0 N h a ha

theorem chkB_sound' (P : Spec) (B s : ℕ) : ∀ (c m N : ℕ), chkB P B s c m N = true →
    ∀ i < c, ∃ j, okB P s (m + i) j = true := by
  intro c
  induction c with
  | zero => intro _ _ _ i hi; omega
  | succ c ih =>
    intro m N h i hi
    simp only [chkB, Bool.and_eq_true] at h
    cases i with
    | zero => exact ⟨_, h.1⟩
    | succ i =>
      obtain ⟨w, hw⟩ := ih (Nat.add m 1) (N / B) h.2 i (by omega)
      exact ⟨w, by rw [show m + (i + 1) = Nat.add m 1 + i by simp [Nat.add_eq]; omega]; exact hw⟩

theorem chkB_sound (P : Spec) (B s c N : ℕ) (h : chkB P B s c 0 N = true) :
    ∀ m < c, ∃ j, okB P s m j = true := by
  intro m hm
  simpa using chkB_sound' P B s c 0 N h m hm

theorem chkPivA_sound (P : Spec) (a : ℕ) : ∀ K, chkPivA P a K = true →
    ∀ l < K, S P.q P.Gs a (P.o + l) % P.q = D P.q a l := by
  intro K
  induction K with
  | zero => intro _ l hl; omega
  | succ K ih =>
    intro h l hl
    simp only [chkPivA, Bool.and_eq_true] at h
    rcases Nat.lt_succ_iff_lt_or_eq.mp hl with hl | rfl
    · exact ih h.2 l hl
    · simpa using h.1

theorem chkPiv_sound (P : Spec) : ∀ N, chkPiv P N = true →
    ∀ a < N, ∀ l < P.k, S P.q P.Gs a (P.o + l) % P.q = D P.q a l := by
  intro N
  induction N with
  | zero => intro _ a ha; omega
  | succ N ih =>
    intro h a ha
    simp only [chkPiv, Bool.and_eq_true] at h
    rcases Nat.lt_succ_iff_lt_or_eq.mp ha with ha | rfl
    · exact ih h.2 a ha
    · exact chkPivA_sound P a P.k h.1

theorem okT_spec (P : Spec) (hq : 0 < P.q) (t w : ℕ) (h : okT P t w = true) :
    t ∈ P.orphs ∨ ∃ s < P.reps.length, ∃ m < P.q ^ P.k,
      dist (cwF P.q P.Gs (D P.q (P.reps.getD s 0)) m) (ydig P.q P.o P.k t) P.n ≤ P.R := by
  unfold okT at h
  by_cases hw : w = P.reps.length * P.q ^ P.k
  · have : Nat.beq w (Nat.mul P.reps.length (Nat.pow P.q P.k)) = true := beq_true hw
    rw [this] at h
    exact Or.inl (memN_sound _ _ h)
  · have : Nat.beq w (Nat.mul P.reps.length (Nat.pow P.q P.k)) = false := beq_false hw
    rw [this, Bool.cond_false, Bool.and_eq_true] at h
    refine Or.inr ⟨w / P.q ^ P.k, by simpa using h.1, w % P.q ^ P.k,
      Nat.mod_lt _ (Nat.pow_pos hq), by simpa using h.2⟩

theorem okO_spec (P : Spec) (t a j : ℕ) (h : okO P t a j = true) :
    j < P.cnt ∧ dist (D P.q (pget P.PN P.b j)) (cwF P.q P.Gs (ydig P.q P.o P.k t) a) P.n ≤ P.R := by
  simp only [okO, Bool.and_eq_true] at h
  exact ⟨by simpa using h.1, by simpa using h.2⟩

theorem okB_spec (P : Spec) (s m j : ℕ) (h : okB P s m j = true) :
    j < P.cnt ∧ pget P.PN P.b j = enc P.q (cwF P.q P.Gs (D P.q (P.reps.getD s 0)) m) P.n := by
  simp only [okB, Bool.and_eq_true] at h
  exact ⟨by simpa using h.1, by simpa using h.2⟩

theorem ydig_eq (q o k t i : ℕ) :
    ydig q o k t i = if i < o then D q t i else if i < o + k then 0 else D q t (i - k) := by
  unfold ydig
  by_cases h1 : i < o
  · have : Nat.blt i o = true := blt_iff.mpr h1
    simp [this, h1]
  · have : Nat.blt i o = false := by
      cases h : Nat.blt i o
      · rfl
      · exact absurd (blt_iff.mp h) h1
    by_cases h2 : i < o + k
    · have h2' : Nat.blt i (Nat.add o k) = true := blt_iff.mpr h2
      simp [this, h1, h2, h2']
    · have h2' : Nat.blt i (Nat.add o k) = false := by
        cases h : Nat.blt i (Nat.add o k)
        · rfl
        · exact absurd (blt_iff.mp h) h2
      simp [this, h1, h2, h2']

/-! ### Vetores -/

section Vec

variable {q n : ℕ} [NeZero q]

theorem xval_wdf (f : ℕ → ℕ) (hf : ∀ i < n, f i < q) : ∀ i < n, xval (wdf q n f) i = f i := by
  intro i hi
  simp [xval, wdf, hi, ZMod.val_natCast, Nat.mod_eq_of_lt (hf i hi)]

theorem wdf_xval (x : Fin n → ZMod q) : wdf q n (xval x) = x := by
  funext i
  simp [wdf, xval, i.2]

theorem wdf_congr (f g : ℕ → ℕ) (h : ∀ i < n, f i = g i) : wdf q n f = wdf q n g := by
  funext i
  simp [wdf, h i.1 i.2]

theorem wdf_cwF (Gs : List ℕ) (rd : ℕ → ℕ) (m : ℕ) :
    wdf q n (cwF q Gs rd m) = wdf q n rd + wdf q n (S q Gs m) := by
  funext i
  show (((rd i.1 + S q Gs m i.1) % q : ℕ) : ZMod q) = _
  simp [wdf, ZMod.natCast_mod]

theorem word_eq_D (w : ℕ) : word q n w = wdf q n (D q w) := word_eq_wdf w

theorem hd_wdf (x : Fin n → ZMod q) (c : ℕ → ℕ) (hc : ∀ k < n, c k < q) :
    hammingDist x (wdf q n c) = dist c (xval x) n := by
  rw [hd_eq x c hc, dist_eq]

end Vec

/-- Montagem das folhas do transversal (blocos de `C` pontos). -/
theorem all_of_chunks (Q : ℕ → Prop) (C nch total : ℕ) (hc : total ≤ C * nch)
    (h : ∀ c < nch, ∀ i < C, C * c + i < total → Q (C * c + i)) : ∀ t < total, Q t := by
  intro t ht
  have hC : 0 < C := by
    rcases Nat.eq_zero_or_pos C with h0 | h0
    · simp [h0] at hc; omega
    · exact h0
  have h1 := Nat.div_add_mod t C
  have h2 : t / C < nch := by
    rw [Nat.div_lt_iff_lt_mul hC]; nlinarith
  have := h (t / C) h2 (t % C) (Nat.mod_lt _ hC) (by rw [h1]; exact ht)
  rwa [h1] at this

/-! ### O teorema -/

theorem syn_cert {q n R M : ℕ} [NeZero q] (P : Spec) (L : List ℕ)
    (hq : P.q = q) (hn : P.n = n) (hR : P.R = R)
    (hdim : P.Gs.length = P.k ∧ P.o + P.k ≤ P.n)
    (hpiv : chkPiv P (P.q ^ P.k) = true)
    (hT : ∀ t < P.q ^ (P.n - P.k), ∃ w, okT P t w = true)
    (hO : ∀ i < P.orphs.length, ∀ a < P.q ^ P.k, ∃ j, okO P (P.orphs.getD i 0) a j = true)
    (hB : ∀ s < P.reps.length, ∀ m < P.q ^ P.k, ∃ j, okB P s m j = true)
    (hU : unpack P.b P.cnt P.PN = L) (hlen : L.length = M)
    (hchk : (L.all (fun m => decide (m < q ^ n)) && strictlyInc L) = true) :
    ∃ C : Finset (Fin n → ZMod q), C.card = M ∧ CoveringA2.Covers R C := by
  classical
  subst hq hn hR
  obtain ⟨hk, hon⟩ := hdim
  have hq0 : 0 < P.q := Nat.pos_of_ne_zero (NeZero.ne _)
  simp only [Bool.and_eq_true, List.all_eq_true, decide_eq_true_eq] at hchk
  refine ⟨codeOf P.q P.n L, (card_codeOf hchk.1 (pairwise_of_strictlyInc L hchk.2)).trans hlen, ?_⟩
  -- palavras de `L` vindas de `pget`
  have hmemL : ∀ j < P.cnt, word P.q P.n (pget P.PN P.b j) ∈ codeOf P.q P.n L := by
    intro j hj
    simp only [codeOf, List.mem_toFinset, List.mem_map]
    exact ⟨_, hU ▸ pget_mem P.b P.cnt P.PN j hj, rfl⟩
  have hDlt : ∀ w i, D P.q w i < P.q := fun w i => D_lt hq0 w i
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
    have h1 := chkPiv_sound P _ hpiv a ha l hl
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
  have hxyc : x = y + c := by simp [hy_def]
  obtain ⟨w, hw⟩ := hT t ht
  rcases okT_spec P hq0 t w hw with horph | ⟨s, hs, m, hm, hd⟩
  · -- 3. órfão: x = y_t + a·G é checado diretamente
    obtain ⟨i, hi, hti⟩ := List.mem_iff_getElem.mp horph
    obtain ⟨j, hj⟩ := hO i hi a ha
    rw [List.getD_eq_getElem _ _ hi, hti] at hj
    obtain ⟨hjc, hjd⟩ := okO_spec P t a j hj
    have hx : x = wdf P.q P.n (cwF P.q P.Gs (ydig P.q P.o P.k t) a) := by
      rw [wdf_cwF, hxyc, ← wdf_xval y, wdf_congr _ _ hyt]
    refine ⟨_, hmemL j hjc, ?_⟩
    rw [word_eq_D, hd_wdf x _ (fun k _ => hDlt _ k), dist_eq,
      distI_congr _ _ (cwF P.q P.Gs (ydig P.q P.o P.k t) a) _ (fun i hi => by
        rw [hx]; exact xval_wdf _ (fun k _ => hcw _ _ k) i hi), ← dist_eq]
    exact hjd
  · -- 2'. testemunha (s, m): x está perto de rₛ + (m ⊕ a)·G
    set r := P.reps.getD s 0
    set f := cwF P.q P.Gs (D P.q r) m with hf_def
    have hdy : hammingDist y (wdf P.q P.n f) ≤ P.R := by
      rw [hd_wdf y f (fun k _ => hcw _ _ k), dist_eq, distI_congr _ _ _ _ hyt, ← dist_eq]
      exact hd
    set m' := dsum P.q P.Gs.length m a
    have hm' : m' < P.q ^ P.k := hk ▸ dsum_lt hq0 _ _ _
    obtain ⟨j, hj⟩ := hB s hs m' hm'
    obtain ⟨hjc, hje⟩ := okB_spec P s m' j hj
    have hword : word P.q P.n (pget P.PN P.b j) = wdf P.q P.n f + c := by
      rw [word_eq_D, hje]
      rw [wdf_congr _ (cwF P.q P.Gs (D P.q r) m')
        (fun i hi => D_enc hq0 _ _ (fun k _ => hcw _ _ k) i hi)]
      rw [wdf_cwF, hf_def, wdf_cwF, hc_def, add_assoc]
      congr 1
      funext i
      simp only [wdf, Pi.add_apply]
      exact S_dsum hq0 P.Gs m a i.1
    refine ⟨_, hmemL j hjc, ?_⟩
    rw [hword, ← CoveringA2.hammingDist_sub_right x (wdf P.q P.n f + c) c, add_sub_cancel_right]
    exact hdy

end Syn
