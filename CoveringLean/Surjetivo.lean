import CoveringLean.Regras
import CoveringLean.SynCheck

/-!
# Corolário 3 de Kéri–Östergård (2005): união de códigos sobrejetivos em sub-alfabetos

G. Kéri e P. R. J. Östergård, *Bounds for covering codes over large alphabets*, Designs, Codes
and Cryptography 37 (2005) 45–60, DOI 10.1007/s10623-004-3804-8, Teorema 2 e Corolário 3
(pp. 54–55). É a chave `n` das tabelas do Kéri para `q ≥ 6`.

**Enunciado.** Seja `n = k(r-1) + 1` e parta o alfabeto `Z_q` em `k` blocos de `v₁, …, v_k`
símbolos consecutivos. Se `Lᵢ` é um código `r`-sobrejetivo sobre `Z_{vᵢ}^n` (toda escolha de
`r` coordenadas vê todas as `vᵢ^r` tuplas), a união dos `Lᵢ`, com o bloco `i` deslocado para os
seus símbolos, tem raio de cobertura `n - r`. Logo `K_q(n, n-r) ≤ Σ |Lᵢ|`.

**Prova (pombal).** Dada `x`, cada coordenada cai em algum bloco; como `k(r-1) < n`, algum bloco
recebe `≥ r` coordenadas. Escolha `r` delas: a sobrejetividade dá uma palavra do bloco que
concorda com `x` nessas `r`, logo a distância é `≤ n - r`.

Aqui a sobrejetividade de cada ingrediente é conferida pelo kernel com um verificador booleano
barato (`checkSurj`): para cada lista crescente de `r` coordenadas, o mapa de bits das projeções
(um `Nat` com o bit `proj c` ligado para cada palavra `c`, operações que o kernel acelera com
GMP) tem de ser `2^(v^r) - 1`. O custo é `C(n,r) · |L|`, sem passar pelos `q^n` pontos do espaço.
Sem `sorry`, sem `native_decide`; axiomas no fim.
-/

open Finset CoveringA2 CoveringUB

namespace CoveringSurj

/-- Dígito `j` de `w` em base `v` (coordenada `j` da palavra de índice `w`). -/
def dg (v w j : ℕ) : ℕ := Nat.mod (Nat.div w (Nat.pow v j)) v

/-- `L` (índices de palavras de `Z_v^n`) é `r`-sobrejetivo: em quaisquer `r` coordenadas,
toda tupla de símbolos `< v` aparece em alguma palavra. -/
def Surj (v n r : ℕ) (L : List ℕ) : Prop :=
  ∀ S : Finset (Fin n), S.card = r → ∀ t : Fin n → ℕ, (∀ j ∈ S, t j < v) →
    ∃ c ∈ L, ∀ j ∈ S, dg v c j = t j

/-- Um bloco do alfabeto: símbolos `off, …, off + v - 1`, com o seu código sobrejetivo. -/
structure Parte (n r : ℕ) where
  off : ℕ
  v : ℕ
  L : List ℕ
  surj : Surj v n r L

/-- A palavra de `Z_q^n` que a palavra `c` do bloco `(off, v)` representa. -/
def palavra (q n off v c : ℕ) : Fin n → ZMod q := fun j => ((off + dg v c j : ℕ) : ZMod q)

/-- O código do Corolário 3: a união dos blocos. -/
def codigo (q n r : ℕ) (P : List (Parte n r)) : Finset (Fin n → ZMod q) :=
  (P.flatMap fun p => p.L.map (palavra q n p.off p.v)).toFinset

/-- `Σ |Lᵢ|`. -/
def tamanho {n r : ℕ} (P : List (Parte n r)) : ℕ := (P.map fun p => p.L.length).sum

theorem card_codigo (q n r : ℕ) (P : List (Parte n r)) : (codigo q n r P).card ≤ tamanho P := by
  unfold codigo tamanho
  refine (List.toFinset_card_le _).trans (le_of_eq ?_)
  simp [List.length_flatMap]

/-- **Corolário 3 (Kéri–Östergård 2005).** -/
theorem cobre (q n r : ℕ) [NeZero q] (P : List (Parte n r))
    (hn : P.length * (r - 1) < n)
    (hcov : ∀ a, a < q → ∃ p ∈ P, p.off ≤ a ∧ a < p.off + p.v) :
    Covers (n - r) (codigo q n r P) := by
  classical
  intro x
  have hc : ∀ j : Fin n, ∃ i : Fin P.length,
      P[i].off ≤ (x j).val ∧ (x j).val < P[i].off + P[i].v := by
    intro j
    obtain ⟨p, hp, h1, h2⟩ := hcov (x j).val (ZMod.val_lt (x j))
    obtain ⟨i, hi, rfl⟩ := List.getElem_of_mem hp
    exact ⟨⟨i, hi⟩, h1, h2⟩
  choose f hf using hc
  obtain ⟨i, -, hi⟩ := Finset.exists_lt_card_fiber_of_mul_lt_card_of_maps_to
    (s := (univ : Finset (Fin n))) (t := (univ : Finset (Fin P.length))) (f := f) (n := r - 1)
    (fun _ _ => mem_univ _) (by simpa using hn)
  have hr : r ≤ (univ.filter fun j => f j = i).card := by omega
  obtain ⟨S, hSF, hS⟩ := Finset.exists_subset_card_eq hr
  have hSi : ∀ j ∈ S, f j = i := fun j hj => (Finset.mem_filter.1 (hSF hj)).2
  obtain ⟨c, hcL, hcS⟩ := P[i].surj S hS (fun j => (x j).val - P[i].off) (by
    intro j hj
    have := hf j
    rw [hSi j hj] at this
    omega)
  refine ⟨palavra q n P[i].off P[i].v c, ?_, ?_⟩
  · simp only [codigo, List.mem_toFinset, List.mem_flatMap, List.mem_map]
    exact ⟨P[i], List.getElem_mem _, c, hcL, rfl⟩
  · have hig : ∀ j ∈ S, x j = palavra q n P[i].off P[i].v c j := by
      intro j hj
      have := hf j
      rw [hSi j hj] at this
      simp only [palavra]
      rw [hcS j hj, Nat.add_sub_cancel' this.1, ZMod.natCast_zmod_val]
    have hsub : (univ.filter fun j => x j ≠ palavra q n P[i].off P[i].v c j) ⊆ Sᶜ := by
      intro j hj
      rw [Finset.mem_compl]
      intro hjS
      exact (Finset.mem_filter.1 hj).2 (hig j hjS)
    have := Finset.card_le_card hsub
    rw [Finset.card_compl, Fintype.card_fin, hS] at this
    exact this

/-! ## O verificador booleano da sobrejetividade -/

/-- Todas as listas de comprimento `r` com entradas `< n`. -/
def tuplas : ℕ → ℕ → List (List ℕ)
  | _, 0 => [[]]
  | n, r + 1 => (List.range n).flatMap fun a => (tuplas n r).map (a :: ·)

/-- A lista é estritamente crescente. -/
def crescente : List ℕ → Bool
  | a :: b :: t => decide (a < b) && crescente (b :: t)
  | _ => true

/-- Projeção da palavra `c` nas coordenadas `ls`, lida em base `v`. -/
def proj (v c : ℕ) : List ℕ → ℕ
  | [] => 0
  | j :: ls => Nat.add (dg v c j) (Nat.mul v (proj v c ls))

/-- Mapa de bits das projeções: bit `proj c` ligado para cada `c ∈ L`. -/
def mapa (v : ℕ) (ls : List ℕ) : List ℕ → ℕ
  | [] => 0
  | c :: L => Nat.lor (mapa v ls L) (Nat.shiftLeft 1 (proj v c ls))

/-- Para cada lista crescente de `r` coordenadas, todas as `v^r` projeções aparecem. -/
def checkSurj (v n r : ℕ) (L : List ℕ) : Bool :=
  (tuplas n r).all fun ls => !crescente ls || Nat.beq (mapa v ls L) (Nat.sub (Nat.pow 2 (Nat.pow v r)) 1)

theorem mem_tuplas : ∀ (r n : ℕ) (ls : List ℕ), ls.length = r → (∀ a ∈ ls, a < n) →
    ls ∈ tuplas n r
  | 0, n, ls, h, _ => by simp_all [tuplas]
  | r + 1, n, [], h, _ => by simp at h
  | r + 1, n, a :: ls, h, ha => by
    simp only [tuplas, List.mem_flatMap, List.mem_range, List.mem_map]
    exact ⟨a, ha a (by simp), ls, mem_tuplas r n ls (by simpa using h)
      (fun b hb => ha b (by simp [hb])), rfl⟩

theorem crescente_of_pairwise : ∀ ls : List ℕ, ls.Pairwise (· < ·) → crescente ls = true
  | [], _ => rfl
  | [_], _ => rfl
  | a :: b :: t, h => by
    simp only [crescente, Bool.and_eq_true, decide_eq_true_eq]
    exact ⟨List.rel_of_pairwise_cons h (by simp), crescente_of_pairwise _ h.of_cons⟩

theorem testBit_mapa (v : ℕ) (ls : List ℕ) :
    ∀ (L : List ℕ) (m : ℕ), (mapa v ls L).testBit m = true → ∃ c ∈ L, proj v c ls = m
  | [], m, h => by simp [mapa] at h
  | c :: L, m, h => by
    have e : mapa v ls (c :: L) = mapa v ls L ||| (1 <<< proj v c ls) := rfl
    rw [e, Nat.testBit_or, Bool.or_eq_true] at h
    rcases h with h | h
    · obtain ⟨c', hc', e⟩ := testBit_mapa v ls L m h
      exact ⟨c', List.mem_cons_of_mem _ hc', e⟩
    · rw [Nat.one_shiftLeft, Nat.testBit_two_pow] at h
      exact ⟨c, List.mem_cons_self, by simpa using h⟩

/-- Leitura em base `v` de uma função ao longo de `ls`. -/
def leitura (v : ℕ) (g : ℕ → ℕ) : List ℕ → ℕ
  | [] => 0
  | j :: ls => g j + v * leitura v g ls

theorem proj_eq_leitura (v c : ℕ) : ∀ ls, proj v c ls = leitura v (dg v c) ls
  | [] => rfl
  | j :: ls => by simp [proj, leitura, proj_eq_leitura v c ls]

theorem leitura_lt (v : ℕ) (g : ℕ → ℕ) : ∀ ls : List ℕ, (∀ a ∈ ls, g a < v) →
    leitura v g ls < v ^ ls.length
  | [], _ => by simp [leitura]
  | j :: ls, h => by
    have h1 := h j (by simp)
    have h2 := leitura_lt v g ls (fun a ha => h a (by simp [ha]))
    simp only [leitura, List.length_cons, pow_succ]
    nlinarith

theorem leitura_inj (v : ℕ) (f g : ℕ → ℕ) : ∀ ls : List ℕ, (∀ a ∈ ls, f a < v) →
    (∀ a ∈ ls, g a < v) → leitura v f ls = leitura v g ls → ∀ a ∈ ls, f a = g a
  | [], _, _, _ => by simp
  | j :: ls, hf, hg, h => by
    simp only [leitura] at h
    have hfj := hf j (by simp)
    have hgj := hg j (by simp)
    have hv : 0 < v := by omega
    have e1 : f j = g j := by
      have := congrArg (· % v) h
      simp only [Nat.add_mul_mod_self_left, Nat.mod_eq_of_lt hfj, Nat.mod_eq_of_lt hgj] at this
      exact this
    have e2 : leitura v f ls = leitura v g ls := by
      rw [e1] at h
      exact Nat.eq_of_mul_eq_mul_left hv (by omega)
    intro a ha
    rcases List.mem_cons.1 ha with rfl | ha
    · exact e1
    · exact leitura_inj v f g ls (fun b hb => hf b (by simp [hb])) (fun b hb => hg b (by simp [hb]))
        e2 a ha

theorem dg_lt {v : ℕ} (hv : 0 < v) (c j : ℕ) : dg v c j < v := Nat.mod_lt _ hv

/-- **Correção do verificador**: `checkSurj = true` dá a sobrejetividade. -/
theorem surj_of_check {v n r : ℕ} {L : List ℕ} (hv : 0 < v) (h : checkSurj v n r L = true) :
    Surj v n r L := by
  classical
  intro S hS t ht
  set T : Finset ℕ := S.image Fin.val
  set ls := T.sort (· ≤ ·)
  have hT : T.card = r := by
    rw [Finset.card_image_of_injective _ Fin.val_injective, hS]
  have hlen : ls.length = r := by rw [Finset.length_sort, hT]
  have hmem : ∀ a, a ∈ ls ↔ ∃ j ∈ S, (j : ℕ) = a := by
    intro a
    rw [Finset.mem_sort, Finset.mem_image]
  have hlt : ∀ a ∈ ls, a < n := by
    intro a ha
    obtain ⟨j, -, rfl⟩ := (hmem a).1 ha
    exact j.isLt
  have hcres : crescente ls = true := crescente_of_pairwise _ (Finset.sortedLT_sort T).pairwise
  have hall := List.all_eq_true.1 h ls (mem_tuplas r n ls hlen hlt)
  simp only [hcres, Bool.not_true, Bool.false_or, Nat.beq_eq, Nat.pow_eq, Nat.sub_eq] at hall
  let g : ℕ → ℕ := fun a => if hx : a < n then t ⟨a, hx⟩ else 0
  have hg : ∀ a ∈ ls, g a < v := by
    intro a ha
    obtain ⟨j, hj, rfl⟩ := (hmem a).1 ha
    simp only [g, j.isLt, ↓reduceDIte]
    exact ht j hj
  have hm : leitura v g ls < v ^ r := hlen ▸ leitura_lt v g ls hg
  have hbit : (mapa v ls L).testBit (leitura v g ls) = true := by
    rw [hall, Nat.testBit_two_pow_sub_one]
    exact decide_eq_true hm
  obtain ⟨c, hcL, hc⟩ := testBit_mapa v ls L _ hbit
  refine ⟨c, hcL, fun j hj => ?_⟩
  rw [proj_eq_leitura] at hc
  have := leitura_inj v (dg v c) g ls (fun a _ => dg_lt hv c a) hg hc j ((hmem j).2 ⟨j, hj, rfl⟩)
  simpa [g, j.isLt] using this

/-- A mesma conferência quebrada em uma afirmação por lista de coordenadas: cada
`mapa v ls L = 2^(v^r) - 1` vira um teorema próprio (o cache do kernel é por declaração; numa
declaração só, 14 641 palavras × 35 listas passaram de 12 GB). `Ls` lista as crescentes. -/
theorem surj_of_mapas {v n r : ℕ} {L : List ℕ} (hv : 0 < v) (Ls : List (List ℕ))
    (hcob : (tuplas n r).all (fun ls => !crescente ls || Ls.contains ls) = true)
    (hall : ∀ ls ∈ Ls, mapa v ls L = 2 ^ v ^ r - 1) : Surj v n r L := by
  refine surj_of_check hv (List.all_eq_true.2 fun ls hls => ?_)
  have h := List.all_eq_true.1 hcob ls hls
  cases hc : crescente ls
  · rfl
  · simp only [hc, Bool.not_true, Bool.false_or, List.contains_iff_mem] at h
    simp only [Bool.not_true, Bool.false_or, Nat.beq_eq, Nat.pow_eq, Nat.sub_eq]
    exact hall ls h

/-- Cobertura dos símbolos pelos blocos, em forma booleana. -/
def cobreAlfabeto {n r : ℕ} (q : ℕ) (P : List (Parte n r)) : Bool :=
  (List.range q).all fun a => P.any fun p => decide (p.off ≤ a) && decide (a < p.off + p.v)

/-- **Cota pronta para os certificados gerados**: `K_q(n, R) ≤ M` a partir dos blocos. -/
theorem ub {q n r R M : ℕ} [NeZero q] (P : List (Parte n r)) (hn : P.length * (r - 1) < n)
    (hcov : cobreAlfabeto q P = true) (hR : n - r = R) (hM : tamanho P = M) : UB q n R M := by
  refine ⟨codigo q n r P, (card_codigo q n r P).trans hM.le, hR ▸ cobre q n r P hn ?_⟩
  intro a ha
  have := List.all_eq_true.1 hcov a (List.mem_range.2 ha)
  simp only [List.any_eq_true, Bool.and_eq_true, decide_eq_true_eq] at this
  exact this

end CoveringSurj

#print axioms CoveringSurj.cobre
#print axioms CoveringSurj.surj_of_check
#print axioms CoveringSurj.ub
#print axioms CoveringSurj.surj_of_mapas
