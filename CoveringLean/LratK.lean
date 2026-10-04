
/-!
# LratK: verificador de refutações LRAT (só RUP) executado pelo kernel

Um verificador LRAT escrito para ser **reduzido pelo kernel** (`decide +kernel`), com prova de
correção. Nenhum `native_decide`, nenhum `ofReduceBool`.

Por que não `Mathlib.Tactic.Sat.FromLRAT` (o que o Florath usou para K_8(4,2) = 23): ele monta
um termo de prova passo a passo no elaborador, e o custo de memória cresce rápido demais.
Medido aqui (2026-10-04): LRAT de 1,1 MB (`K_8(8,5)` do Florath) = 122 s e 5,6 GB de RSS; LRAT
aparado de 5 MB de um perfil de K_7(4,2) = morto por falta de memória acima de 12 GB. As provas
de K_7(4,2) ≥ 19 somam 1,67 GB depois de aparadas (`lrat-trim`), então é preciso outro caminho.

## Ideia

* Literal codificado como `Nat`: `2v` é `x_v`, `2v+1` é `¬x_v`.
* O banco de cláusulas é **dado estático**: uma árvore binária (`Tree`) com as cláusulas
  originais nas chaves `1..n` e as cláusulas derivadas nas chaves `n+1, n+2, …` (a prova é
  renumerada fora do Lean, o que não precisa de confiança: tudo é conferido aqui). Assim o
  kernel só **lê** a árvore, nunca a reconstrói passo a passo.
* `checkF` confere que as chaves `1..n` guardam exatamente as cláusulas da fórmula.
* `checkRange` confere, em ordem, que cada cláusula derivada da chave `k` é RUP a partir das
  dicas, todas com chave em `[1, k)`. Pode ser chamado em blocos consecutivos (um teorema por
  bloco), o que limita a memória de cada `decide +kernel`.
* A atribuição parcial da propagação unitária é um `Nat` usado como conjunto de bits (o bit `l`
  aceso = literal `l` verdadeiro); o kernel faz `|||`, `>>>`, `%` com GMP. O literal oposto é
  `flip l = l + 1 − 2 (l % 2)`.
* As funções que o kernel executa são escritas com recursores (`List.rec`, `Tree.rec`,
  `Option.rec`) em vez de `match`/recursão estrutural: o `brecOn` deixava a redução ~2× mais
  lenta (medido).

## Correção

`unsat_of_good` (e `LratK.unsat_of_chain`, em `LratKData`): se `checkF db F = true`, cada bloco
de `checkRange` dá `true` e a chave final guarda a cláusula vazia, então nenhuma valoração
satisfaz `F`. Só Lean core (sem Mathlib): a memória de base de quem importa este arquivo fica
pequena, o que importa nas refutações grandes.
-/

namespace LratK

/-! ## Semântica -/

/-- Valor de um literal codificado. -/
def litVal (v : Nat → Bool) (l : Nat) : Bool := if l % 2 = 0 then v (l / 2) else !v (l / 2)

/-- A cláusula tem um literal verdadeiro. -/
def ClauseSat (v : Nat → Bool) (c : List Nat) : Prop := ∃ l ∈ c, litVal v l = true

/-- Nenhuma valoração satisfaz todas as cláusulas. -/
def Unsat (F : List (List Nat)) : Prop := ∀ v : Nat → Bool, ∃ c ∈ F, ¬ ClauseSat v c

/-! ## O banco de cláusulas -/

inductive Tree where
  | leaf
  | node (l : Tree) (v : Option (List Nat)) (r : Tree)

/-- Busca pela chave `k`, bit menos significativo primeiro. -/
noncomputable def Tree.get (t : Tree) (k : Nat) : Option (List Nat) :=
  Tree.rec (motive := fun _ => Nat → Option (List Nat)) (fun _ => none)
    (fun _ v _ ihl ihr k =>
      bif Nat.beq k 0 then v else bif Nat.beq (k % 2) 0 then ihl (k / 2) else ihr (k / 2)) t k

/-- Inserção (só no elaborador, para montar o dado; o kernel nunca a executa). -/
def Tree.ins : Nat → Tree → Nat → List Nat → Tree
  | 0, t, _, _ => t
  | f + 1, .leaf, k, c =>
    if k = 0 then .node .leaf (some c) .leaf
    else if k % 2 = 0 then .node (Tree.ins f .leaf (k / 2) c) none .leaf
    else .node .leaf none (Tree.ins f .leaf (k / 2) c)
  | f + 1, .node l v r, k, c =>
    if k = 0 then .node l (some c) r
    else if k % 2 = 0 then .node (Tree.ins f l (k / 2) c) v r
    else .node l v (Tree.ins f r (k / 2) c)

/-! ## O verificador -/

/-- O literal oposto: `2v ↔ 2v+1` (só aritmética, para a prova não depender de lemas de `^^^`). -/
def flip (l : Nat) : Nat := l + 1 - 2 * (l % 2)

/-- O bit `l` de `a` está aceso. -/
def isSet (a l : Nat) : Bool := Nat.beq ((a >>> l) % 2) 1

inductive Res where
  | conflict
  | unit (l : Nat)
  | skip
  | bad

/-- Avalia uma cláusula sob a atribuição parcial `a`: todos os literais falsos (`conflict`),
um só livre (`unit`), algum verdadeiro (`skip`) ou dois livres (`bad`). -/
noncomputable def scan (a : Nat) (D : List Nat) : Option Nat → Res :=
  List.rec (motive := fun _ => Option Nat → Res)
    (fun acc => Option.rec Res.conflict (fun u => Res.unit u) acc)
    (fun l _ ih acc =>
      bif isSet a l then Res.skip
      else bif isSet a (flip l) then ih acc
      else Option.rec (ih (some l)) (fun _ => Res.bad) acc) D

/-- Propagação unitária pelas dicas (chaves em `[1, k)`), até achar um conflito. -/
noncomputable def rup (db : Tree) (k : Nat) (hs : List Nat) : Nat → Bool :=
  List.rec (motive := fun _ => Nat → Bool) (fun _ => false)
    (fun h _ ih a =>
      bif Nat.blt h k && Nat.blt 0 h then
        Option.rec false
          (fun D => Res.rec true (fun u => ih (a ||| (1 <<< u))) (ih a) false (scan a D none))
          (db.get h)
      else false) hs

/-- Atribuição inicial: a negação de cada literal da cláusula. -/
noncomputable def negs (c : List Nat) : Nat → Nat :=
  List.rec (motive := fun _ => Nat → Nat) (fun a => a)
    (fun l _ ih a => ih (a ||| (1 <<< flip l))) c

/-- Igualdade booleana de listas de naturais (sem passar por instâncias). -/
noncomputable def listBeq (xs : List Nat) : List Nat → Bool :=
  List.rec (motive := fun _ => List Nat → Bool)
    (fun ys => List.rec (motive := fun _ => Bool) true (fun _ _ _ => false) ys)
    (fun x _ ih ys => List.rec (motive := fun _ => Bool) false
      (fun y ys' _ => Nat.beq x y && ih ys') ys) xs

/-- As chaves `k, k+1, …` guardam as cláusulas de `F`, em ordem. -/
noncomputable def checkF (db : Tree) (F : List (List Nat)) : Nat → Bool :=
  List.rec (motive := fun _ => Nat → Bool) (fun _ => true)
    (fun c _ ih k => Option.rec false (fun d => listBeq c d) (db.get k) && ih (k + 1)) F

/-- Cada cláusula derivada das chaves `k, k+1, …` é RUP a partir das suas dicas. -/
noncomputable def checkRange (db : Tree) (hs : List (List Nat)) : Nat → Bool :=
  List.rec (motive := fun _ => Nat → Bool) (fun _ => true)
    (fun h _ ih k => Option.rec false (fun c => rup db k h (negs c 0)) (db.get k) && ih (k + 1))
    hs

/-! ## Lemas de bits -/

theorem isSet_iff (a l : Nat) : isSet a l = true ↔ a.testBit l = true := by
  rw [isSet, Nat.testBit_eq_decide_div_mod_eq, Nat.shiftRight_eq_div_pow]
  simp [Nat.beq_eq]

theorem testBit_or_shift (a u l : Nat) :
    (a ||| (1 <<< u)).testBit l = true ↔ a.testBit l = true ∨ l = u := by
  rw [Nat.testBit_or, Nat.one_shiftLeft, Nat.testBit_two_pow, Bool.or_eq_true,
    decide_eq_true_iff]
  exact or_congr_right ⟨Eq.symm, Eq.symm⟩

theorem litVal_flip (v : Nat → Bool) (l : Nat) : litVal v (flip l) = !litVal v l := by
  unfold litVal flip
  rcases Nat.mod_two_eq_zero_or_one l with h | h
  · have h1 : (l + 1 - 2 * (l % 2)) % 2 = 1 := by omega
    have h2 : (l + 1 - 2 * (l % 2)) / 2 = l / 2 := by omega
    rw [h1, h2, h]; simp
  · have h1 : (l + 1 - 2 * (l % 2)) % 2 = 0 := by omega
    have h2 : (l + 1 - 2 * (l % 2)) / 2 = l / 2 := by omega
    rw [h1, h2, h]; simp

/-! ## Invariantes -/

/-- A atribuição parcial `a` é consistente com `v`: todo bit aceso é um literal verdadeiro. -/
def Cons (v : Nat → Bool) (a : Nat) : Prop := ∀ l, isSet a l = true → litVal v l = true

theorem Cons.set {v : Nat → Bool} {a u : Nat} (h : Cons v a) (hu : litVal v u = true) :
    Cons v (a ||| (1 <<< u)) := by
  intro l hl
  rw [isSet_iff, testBit_or_shift, ← isSet_iff] at hl
  rcases hl with hl | rfl
  · exact h l hl
  · exact hu

/-- As cláusulas das chaves `[1, k)` são verdadeiras em `v`. -/
def Good (db : Tree) (v : Nat → Bool) (k : Nat) : Prop :=
  ∀ i c, 0 < i → i < k → db.get i = some c → ClauseSat v c

theorem Good.mono {db : Tree} {v : Nat → Bool} {k k' : Nat} (h : Good db v k) (hk : k' ≤ k) :
    Good db v k' := fun i c h0 hi hc => h i c h0 (Nat.lt_of_lt_of_le hi hk) hc

/-- Correção de `scan`: sob `Cons v a`, uma cláusula verdadeira não dá `conflict`, e se dá
`unit u` então `u` é verdadeiro. -/
theorem scan_sound {v : Nat → Bool} {a : Nat} (ha : Cons v a) :
    ∀ (D : List Nat) (acc : Option Nat),
      (∀ u, acc = some u → (∃ l ∈ D, litVal v l = true) ∨ litVal v u = true) →
      (∃ l ∈ D, litVal v l = true) ∨ (∃ u, acc = some u ∧ litVal v u = true) →
      (scan a D acc ≠ .conflict) ∧ (∀ u, scan a D acc = .unit u → litVal v u = true) := by
  intro D
  induction D with
  | nil =>
    intro acc _ hsat
    rcases hsat with ⟨l, hl, _⟩ | ⟨u, rfl, hu⟩
    · simp at hl
    · refine ⟨fun h => ?_, fun u' h => ?_⟩
      · cases h
      · change Res.unit u = Res.unit u' at h
        cases h; exact hu
  | cons l ls ih =>
    intro acc hacc hsat
    have hscan : scan a (l :: ls) acc =
        (bif isSet a l then Res.skip
         else bif isSet a (flip l) then scan a ls acc
         else Option.rec (scan a ls (some l)) (fun _ => Res.bad) acc) := rfl
    rw [hscan]
    cases h1 : isSet a l
    · cases h2 : isSet a (flip l)
      · -- `l` livre
        cases acc with
        | none =>
          simp only [Bool.cond_false]
          apply ih (some l)
          · intro u hu
            cases hu
            by_cases hl : litVal v l = true
            · exact Or.inr hl
            · rcases hsat with ⟨l', hl', hv⟩ | ⟨u, hu, _⟩
              · rcases List.mem_cons.1 hl' with rfl | hl'
                · exact absurd hv hl
                · exact Or.inl ⟨l', hl', hv⟩
              · cases hu
          · by_cases hl : litVal v l = true
            · exact Or.inr ⟨l, rfl, hl⟩
            · rcases hsat with ⟨l', hl', hv⟩ | ⟨u, hu, _⟩
              · rcases List.mem_cons.1 hl' with rfl | hl'
                · exact absurd hv hl
                · exact Or.inl ⟨l', hl', hv⟩
              · cases hu
        | some u =>
          simp only [Bool.cond_false]
          exact ⟨fun h => Res.noConfusion h, fun u' h => Res.noConfusion h⟩
      · -- `l` falso
        simp only [Bool.cond_false, Bool.cond_true]
        have hlf : litVal v l = false := by
          have := ha _ h2
          rw [litVal_flip] at this
          simpa using this
        have hsat' : (∃ l ∈ ls, litVal v l = true) ∨ (∃ u, acc = some u ∧ litVal v u = true) := by
          rcases hsat with ⟨l', hl', hv⟩ | h
          · rcases List.mem_cons.1 hl' with rfl | hl'
            · rw [hlf] at hv; cases hv
            · exact Or.inl ⟨l', hl', hv⟩
          · exact Or.inr h
        apply ih acc _ hsat'
        intro u hu
        rcases hacc u hu with ⟨l', hl', hv⟩ | h
        · rcases List.mem_cons.1 hl' with rfl | hl'
          · rw [hlf] at hv; cases hv
          · exact Or.inl ⟨l', hl', hv⟩
        · exact Or.inr h
    · simp only [Bool.cond_true]
      exact ⟨fun h => Res.noConfusion h, fun u h => Res.noConfusion h⟩

/-- Correção de `rup`: com as dicas verdadeiras (`Good`) e `Cons v a`, a propagação nunca chega
a um conflito; logo `rup … = true` é impossível. -/
theorem rup_false {db : Tree} {v : Nat → Bool} {k : Nat} (hg : Good db v k) :
    ∀ (hs : List Nat) (a : Nat), Cons v a → rup db k hs a = false := by
  intro hs
  induction hs with
  | nil => intro a _; rfl
  | cons h hs ih =>
    intro a ha
    have hrup : rup db k (h :: hs) a =
        (bif Nat.blt h k && Nat.blt 0 h then
          Option.rec false
            (fun D => Res.rec true (fun u => rup db k hs (a ||| (1 <<< u))) (rup db k hs a) false
              (scan a D none))
            (db.get h)
        else false) := rfl
    rw [hrup]
    cases hb : (Nat.blt h k && Nat.blt 0 h)
    · rfl
    · simp only [Bool.cond_true]
      rw [Bool.and_eq_true, Nat.blt_eq, Nat.blt_eq] at hb
      cases hD : db.get h with
      | none => rfl
      | some D =>
        have hsat := hg h D hb.2 hb.1 hD
        obtain ⟨hnc, hunit⟩ := scan_sound ha D none (fun u hu => by cases hu) (Or.inl hsat)
        change Res.rec true (fun u => rup db k hs (a ||| (1 <<< u))) (rup db k hs a) false
          (scan a D none) = false
        cases hs' : scan a D none with
        | conflict => exact absurd hs' hnc
        | unit u => exact ih _ (ha.set (hunit u hs'))
        | skip => exact ih a ha
        | bad => rfl

theorem negs_cons {v : Nat → Bool} {c : List Nat} (hc : ∀ l ∈ c, litVal v l = false) :
    ∀ (c' : List Nat) (a : Nat), (∀ l ∈ c', l ∈ c) → Cons v a → Cons v (negs c' a) := by
  intro c'
  induction c' with
  | nil => intro a _ ha; exact ha
  | cons l ls ih =>
    intro a hsub ha
    change Cons v (negs ls (a ||| (1 <<< flip l)))
    apply ih _ (fun x hx => hsub x (List.mem_cons_of_mem _ hx))
    apply ha.set
    rw [litVal_flip, hc l (hsub l List.mem_cons_self)]
    rfl

theorem cons_zero (v : Nat → Bool) : Cons v 0 := by
  intro l hl
  rw [isSet_iff, Nat.zero_testBit] at hl
  cases hl

/-- Um passo RUP aceito produz uma cláusula verdadeira em toda valoração que satisfaz as dicas. -/
theorem rup_sound {db : Tree} {v : Nat → Bool} {k : Nat} (hg : Good db v k) {c hs : List Nat}
    (h : rup db k hs (negs c 0) = true) : ClauseSat v c := by
  refine Classical.byContradiction fun hn => ?_
  have hc : ∀ l ∈ c, litVal v l = false := by
    intro l hl
    cases h' : litVal v l
    · rfl
    · exact absurd ⟨l, hl, h'⟩ hn
  have := rup_false hg hs (negs c 0) (negs_cons hc c 0 (fun _ h => h) (cons_zero v))
  rw [this] at h
  cases h

theorem listBeq_eq : ∀ (xs ys : List Nat), listBeq xs ys = true → xs = ys := by
  intro xs
  induction xs with
  | nil =>
    intro ys h
    cases ys with
    | nil => rfl
    | cons y ys => cases h
  | cons x xs ih =>
    intro ys h
    cases ys with
    | nil => cases h
    | cons y ys =>
      change (Nat.beq x y && listBeq xs ys) = true at h
      rw [Bool.and_eq_true, Nat.beq_eq] at h
      rw [h.1, ih ys h.2]

theorem checkF_sound {db : Tree} {v : Nat → Bool} :
    ∀ (F : List (List Nat)) (k : Nat), checkF db F k = true → (∀ c ∈ F, ClauseSat v c) →
      ∀ i c, k ≤ i → i < k + F.length → db.get i = some c → ClauseSat v c := by
  intro F
  induction F with
  | nil => intro k _ _ i c h1 h2; simp at h2; omega
  | cons d F ih =>
    intro k hchk hF i c h1 h2 hc
    change (Option.rec false (fun d' => listBeq d d') (db.get k) && checkF db F (k + 1)) = true
      at hchk
    rw [Bool.and_eq_true] at hchk
    rcases Nat.eq_or_lt_of_le h1 with rfl | h1
    · rw [hc] at hchk
      have := listBeq_eq d c hchk.1
      subst this
      exact hF d List.mem_cons_self
    · exact ih (k + 1) hchk.2 (fun c' hc' => hF c' (List.mem_cons_of_mem _ hc')) i c h1
        (by simp at h2; omega) hc

/-- As cláusulas originais nas chaves `1..n` dão `Good` até `n + 1`. -/
theorem good_of_checkF {db : Tree} {v : Nat → Bool} {F : List (List Nat)}
    (hchk : checkF db F 1 = true) (hF : ∀ c ∈ F, ClauseSat v c) : Good db v (F.length + 1) :=
  fun i c h0 hi hc => checkF_sound F 1 hchk hF i c h0 (by omega) hc

/-- Um bloco de passos conferido estende `Good`. -/
theorem good_of_checkRange {db : Tree} {v : Nat → Bool} :
    ∀ (hs : List (List Nat)) (k : Nat), Good db v k → checkRange db hs k = true →
      Good db v (k + hs.length) := by
  intro hs
  induction hs with
  | nil => intro k hg _; simpa using hg
  | cons h hs ih =>
    intro k hg hchk
    change (Option.rec false (fun c => rup db k h (negs c 0)) (db.get k) &&
      checkRange db hs (k + 1)) = true at hchk
    rw [Bool.and_eq_true] at hchk
    have hg' : Good db v (k + 1) := by
      intro i c h0 hi hc
      rcases Nat.lt_succ_iff_lt_or_eq.1 hi with hi | rfl
      · exact hg i c h0 hi hc
      · rw [hc] at hchk
        exact rup_sound hg hchk.1
    have := ih (k + 1) hg' hchk.2
    simpa [Nat.add_assoc, Nat.add_comm 1] using this

/-- **Correção do verificador.** Se as chaves `1..n` guardam `F`, os passos das chaves
`n+1 … K` conferem (em qualquer divisão em blocos, ver `good_of_checkRange`) e a chave `K`
guarda a cláusula vazia, então `F` é insatisfatível. -/
theorem unsat_of_good {db : Tree} {F : List (List Nat)} {K : Nat}
    (hchk : checkF db F 1 = true)
    (hsteps : ∀ v : Nat → Bool, Good db v (F.length + 1) → Good db v (K + 1))
    (hK : 0 < K) (hempty : db.get K = some []) : Unsat F := by
  intro v
  refine Classical.byContradiction fun hn => ?_
  have hn' : ∀ c ∈ F, ClauseSat v c := fun c hc =>
    Classical.byContradiction fun h => hn ⟨c, hc, h⟩
  have hg := hsteps v (good_of_checkF hchk hn')
  obtain ⟨l, hl, _⟩ := hg K [] hK (Nat.lt_succ_self K) hempty
  simp at hl

end LratK

#print axioms LratK.rup_sound
#print axioms LratK.good_of_checkRange
#print axioms LratK.unsat_of_good
