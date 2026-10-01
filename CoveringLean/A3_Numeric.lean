import Mathlib

/-!
# A3: lado NUMERICO da cota de esfera

Autocontido (nao importa os outros arquivos).  O teorema abstrato `q^n ≤ |C| * V` e provado
por outros; aqui entram:

1. lema generico `lb_of_sphere` (divisao com teto) e versao estrita;
2. os 8 valores `V` e `ceil(q^n/V)` das celulas PROVEN `SPH.<cell>.lb`, com a prova de que a
   cota e justa COMO COTA (`m = ceil - 1` nao satisfaz `q^n ≤ m*V`);
3. a parte racional: `S = q^n/V`, `S < ceil S`, `ceil S - S ∈ (0,1)` quando `V ∤ q^n`;
4. estresse: `V 7 8 3 = 13153`, e `13161` (numero lembrado errado) e REFUTADO.

Valores recalculados em Python a partir de `src/impossibility/covering.py` (inteiros exatos)
antes de escrever este arquivo; nada aqui foi copiado de memoria.
-/

namespace CoveringA3

/-- Volume da esfera de Hamming: `∑_{i ≤ R} C(n,i) (q-1)^i`. -/
def V (q n R : ℕ) : ℕ := ∑ i ∈ Finset.range (R + 1), n.choose i * (q - 1) ^ i

/-! ## (1) Lemas genericos -/

/-- Propriedades da divisao com teto `c = (N+v-1)/v`: `N ≤ c*v < N+v`. -/
theorem ceil_spec (N v : ℕ) (hv : 0 < v) :
    N ≤ ((N + v - 1) / v) * v ∧ ((N + v - 1) / v) * v < N + v := by
  have h1 := Nat.div_add_mod (N + v - 1) v
  have h2 := Nat.mod_lt (N + v - 1) hv
  have h3 : ((N + v - 1) / v) * v = v * ((N + v - 1) / v) := Nat.mul_comm _ _
  constructor <;> omega

/-- Cota de esfera, forma aritmetica: `q^n ≤ m*V` implica `ceil(q^n/V) ≤ m`. -/
theorem lb_of_sphere (q n V m : ℕ) (hV : 0 < V) (h : q ^ n ≤ m * V) :
    (q ^ n + V - 1) / V ≤ m := by
  obtain ⟨_, h2⟩ := ceil_spec (q ^ n) V hV
  have h3 : ((q ^ n + V - 1) / V) * V < (m + 1) * V := by
    have : (m + 1) * V = m * V + V := by ring
    omega
  have := Nat.lt_of_mul_lt_mul_right h3
  omega

/-- Se `V ∤ q^n`, a desigualdade de esfera e ESTRITA: `q^n < m*V`. -/
theorem lt_of_sphere (q n V m : ℕ) (h : q ^ n ≤ m * V) (hnd : ¬ V ∣ q ^ n) :
    q ^ n < m * V := by
  rcases Nat.lt_or_ge (q ^ n) (m * V) with hlt | hge
  · exact hlt
  · exfalso
    have heq : q ^ n = m * V := le_antisymm h hge
    exact hnd ⟨m, by rw [heq, Nat.mul_comm]⟩

/-- Justeza como cota: com `c = ceil`, `m = c-1` NAO satisfaz `N ≤ m*v`. -/
theorem pred_not_sphere (N v : ℕ) (hv : 0 < v) (hN : 0 < N) :
    ¬ N ≤ ((N + v - 1) / v - 1) * v := by
  obtain ⟨h1, h2⟩ := ceil_spec N v hv
  have h3 : ((N + v - 1) / v - 1) * v = ((N + v - 1) / v) * v - v := by
    rw [Nat.sub_mul, Nat.one_mul]
  rw [h3]
  generalize ((N + v - 1) / v) * v = m at *
  omega

/-! ## (3) Parte racional -/

/-- `S := N/v` satisfaz `S < ceil S` quando `v ∤ N`, e `ceil S - S ∈ (0,1)`. -/
theorem rat_ceil_gap (N v : ℕ) (hv : 0 < v) (hnd : ¬ v ∣ N) :
    ((N : ℚ) / v < ((N + v - 1) / v : ℕ)) ∧
    (0 < (((N + v - 1) / v : ℕ) : ℚ) - (N : ℚ) / v) ∧
    ((((N + v - 1) / v : ℕ) : ℚ) - (N : ℚ) / v < 1) := by
  obtain ⟨h1, h2⟩ := ceil_spec N v hv
  set c := (N + v - 1) / v with hc
  have hne : N ≠ c * v := fun h => hnd ⟨c, by rw [h, Nat.mul_comm]⟩
  have hlt : N < c * v := lt_of_le_of_ne h1 hne
  have hvq : (0 : ℚ) < v := by exact_mod_cast hv
  have hltq : (N : ℚ) < c * v := by exact_mod_cast hlt
  have hltq2 : (c : ℚ) * v < N + v := by exact_mod_cast h2
  refine ⟨?_, ?_, ?_⟩
  · rw [div_lt_iff₀ hvq]; exact hltq
  · have : (N : ℚ) / v < c := by rw [div_lt_iff₀ hvq]; exact hltq
    linarith
  · have : (c : ℚ) - N / v < 1 := by
      have : (c : ℚ) * v - N < v := by linarith
      have h4 : ((c : ℚ) * v - N) / v < 1 := by rw [div_lt_one hvq]; exact this
      have h5 : ((c : ℚ) * v - N) / v = c - N / v := by field_simp
      linarith
    exact this

/-- Para qualquer `m ≥ ceil`, a folga aditiva `m - ceil` e `≥ 0` (em ℚ e em ℕ). -/
theorem additive_gap_nonneg (c m : ℕ) (h : c ≤ m) :
    (0 : ℚ) ≤ (m : ℚ) - c ∧ 0 ≤ m - c := by
  refine ⟨?_, Nat.zero_le _⟩
  have : (c : ℚ) ≤ m := by exact_mod_cast h
  linarith

/-- E, se `m ≥ ceil`, `m - S ≥ ceil - S > 0`: a folga real sobre a razao e positiva. -/
theorem gap_over_ratio_pos (N v m : ℕ) (hv : 0 < v) (hnd : ¬ v ∣ N)
    (h : (N + v - 1) / v ≤ m) : (0 : ℚ) < (m : ℚ) - (N : ℚ) / v := by
  obtain ⟨_, hpos, _⟩ := rat_ceil_gap N v hv hnd
  have : (((N + v - 1) / v : ℕ) : ℚ) ≤ m := by exact_mod_cast h
  linarith

/-- O teto coincide com `Nat.ceil` da razao racional. -/
theorem ceil_eq_natCeil (N v : ℕ) (hv : 0 < v) :
    (N + v - 1) / v = ⌈(N : ℚ) / v⌉₊ := by
  apply le_antisymm
  · -- c ≤ ⌈S⌉₊ : pois N ≤ ⌈S⌉₊ * v
    have hvq : (0 : ℚ) < v := by exact_mod_cast hv
    have h1 : (N : ℚ) / v ≤ ⌈(N : ℚ) / v⌉₊ := Nat.le_ceil _
    rw [div_le_iff₀ hvq] at h1
    have h2 : N ≤ ⌈(N : ℚ) / v⌉₊ * v := by exact_mod_cast h1
    simpa using lb_of_sphere N 1 v ⌈(N : ℚ) / v⌉₊ hv (by simpa using h2)
  · apply Nat.ceil_le.mpr
    obtain ⟨h1, _⟩ := ceil_spec N v hv
    have hvq : (0 : ℚ) < v := by exact_mod_cast hv
    rw [div_le_iff₀ hvq]
    exact_mod_cast h1

/-! ## (2) As 8 celulas -/

/-- Pacote de fatos numericos de uma celula `(q,n,R)` com `V = v` e `ceil = c`. -/
def CellFacts (q n R v c : ℕ) : Prop :=
  V q n R = v ∧ 0 < v ∧ ¬ v ∣ q ^ n ∧ (q ^ n + v - 1) / v = c ∧
  (∀ m : ℕ, q ^ n ≤ m * V q n R → c ≤ m) ∧
  (∀ m : ℕ, q ^ n ≤ m * V q n R → q ^ n < m * V q n R) ∧
  ¬ q ^ n ≤ (c - 1) * V q n R ∧
  ((q ^ n : ℕ) : ℚ) / v < c ∧
  0 < (c : ℚ) - ((q ^ n : ℕ) : ℚ) / v ∧ (c : ℚ) - ((q ^ n : ℕ) : ℚ) / v < 1

theorem cellFacts_intro (q n R v c : ℕ) (hV : V q n R = v) (hv : 0 < v)
    (hnd : ¬ v ∣ q ^ n) (hc : (q ^ n + v - 1) / v = c) : CellFacts q n R v c := by
  subst hV hc
  refine ⟨rfl, hv, hnd, rfl, ?_, ?_, ?_, ?_⟩
  · intro m h; exact lb_of_sphere q n _ m hv h
  · intro m h; exact lt_of_sphere q n _ m h hnd
  · exact pred_not_sphere _ _ hv
      (Nat.pos_of_ne_zero fun h => hnd (by rw [h]; exact dvd_zero _))
  · obtain ⟨a, b, c⟩ := rat_ceil_gap (q ^ n) (V q n R) hv hnd
    exact ⟨a, b, c⟩

/-- `(5,7,2)`: `V = 365`, `ceil = 215`. -/
theorem cell_5_7_2 : CellFacts 5 7 2 365 215 :=
  cellFacts_intro _ _ _ _ _ (by decide +kernel) (by norm_num) (by decide +kernel)
    (by decide +kernel)

/-- `(4,10,4)`: `V = 20686`, `ceil = 51`. -/
theorem cell_4_10_4 : CellFacts 4 10 4 20686 51 :=
  cellFacts_intro _ _ _ _ _ (by decide +kernel) (by norm_num) (by decide +kernel)
    (by decide +kernel)

/-- `(5,9,3)`: `V = 5989`, `ceil = 327`. -/
theorem cell_5_9_3 : CellFacts 5 9 3 5989 327 :=
  cellFacts_intro _ _ _ _ _ (by decide +kernel) (by norm_num) (by decide +kernel)
    (by decide +kernel)

/-- `(5,10,4)`: `V = 62201`, `ceil = 158`. -/
theorem cell_5_10_4 : CellFacts 5 10 4 62201 158 :=
  cellFacts_intro _ _ _ _ _ (by decide +kernel) (by norm_num) (by decide +kernel)
    (by decide +kernel)

/-- `(5,9,5)`: `V = 167269`, `ceil = 12`. -/
theorem cell_5_9_5 : CellFacts 5 9 5 167269 12 :=
  cellFacts_intro _ _ _ _ _ (by decide +kernel) (by norm_num) (by decide +kernel)
    (by decide +kernel)

/-- `(5,9,4)`: `V = 38245`, `ceil = 52`. -/
theorem cell_5_9_4 : CellFacts 5 9 4 38245 52 :=
  cellFacts_intro _ _ _ _ _ (by decide +kernel) (by norm_num) (by decide +kernel)
    (by decide +kernel)

/-- `(7,8,3)`: `V = 13153`, `ceil = 439`. -/
theorem cell_7_8_3 : CellFacts 7 8 3 13153 439 :=
  cellFacts_intro _ _ _ _ _ (by decide +kernel) (by norm_num) (by decide +kernel)
    (by decide +kernel)

/-- `(7,9,4)`: `V = 182791`, `ceil = 221`. -/
theorem cell_7_9_4 : CellFacts 7 9 4 182791 221 :=
  cellFacts_intro _ _ _ _ _ (by decide +kernel) (by norm_num) (by decide +kernel)
    (by decide +kernel)

/-! Formas diretas, uma por celula, no formato pedido: `q^n ≤ m * V → c ≤ m`. -/

theorem lb_5_7_2 (m : ℕ) (h : 5 ^ 7 ≤ m * V 5 7 2) : 215 ≤ m := cell_5_7_2.2.2.2.2.1 m h
theorem lb_4_10_4 (m : ℕ) (h : 4 ^ 10 ≤ m * V 4 10 4) : 51 ≤ m := cell_4_10_4.2.2.2.2.1 m h
theorem lb_5_9_3 (m : ℕ) (h : 5 ^ 9 ≤ m * V 5 9 3) : 327 ≤ m := cell_5_9_3.2.2.2.2.1 m h
theorem lb_5_10_4 (m : ℕ) (h : 5 ^ 10 ≤ m * V 5 10 4) : 158 ≤ m := cell_5_10_4.2.2.2.2.1 m h
theorem lb_5_9_5 (m : ℕ) (h : 5 ^ 9 ≤ m * V 5 9 5) : 12 ≤ m := cell_5_9_5.2.2.2.2.1 m h
theorem lb_5_9_4 (m : ℕ) (h : 5 ^ 9 ≤ m * V 5 9 4) : 52 ≤ m := cell_5_9_4.2.2.2.2.1 m h
theorem lb_7_8_3 (m : ℕ) (h : 7 ^ 8 ≤ m * V 7 8 3) : 439 ≤ m := cell_7_8_3.2.2.2.2.1 m h
theorem lb_7_9_4 (m : ℕ) (h : 7 ^ 9 ≤ m * V 7 9 4) : 221 ≤ m := cell_7_9_4.2.2.2.2.1 m h

/-- Justeza como cota: `m = c-1` falha em cada celula (ex.: `214 * 365 < 5^7`). -/
theorem tight_5_7_2 : ¬ 5 ^ 7 ≤ 214 * V 5 7 2 := cell_5_7_2.2.2.2.2.2.2.1
theorem tight_4_10_4 : ¬ 4 ^ 10 ≤ 50 * V 4 10 4 := cell_4_10_4.2.2.2.2.2.2.1
theorem tight_5_9_3 : ¬ 5 ^ 9 ≤ 326 * V 5 9 3 := cell_5_9_3.2.2.2.2.2.2.1
theorem tight_5_10_4 : ¬ 5 ^ 10 ≤ 157 * V 5 10 4 := cell_5_10_4.2.2.2.2.2.2.1
theorem tight_5_9_5 : ¬ 5 ^ 9 ≤ 11 * V 5 9 5 := cell_5_9_5.2.2.2.2.2.2.1
theorem tight_5_9_4 : ¬ 5 ^ 9 ≤ 51 * V 5 9 4 := cell_5_9_4.2.2.2.2.2.2.1
theorem tight_7_8_3 : ¬ 7 ^ 8 ≤ 438 * V 7 8 3 := cell_7_8_3.2.2.2.2.2.2.1
theorem tight_7_9_4 : ¬ 7 ^ 9 ≤ 220 * V 7 9 4 := cell_7_9_4.2.2.2.2.2.2.1

/-! ## (4) Estresse: numero lembrado de memoria vs numero calculado -/

/-- O valor correto. -/
theorem V_7_8_3 : V 7 8 3 = 13153 := by decide +kernel

/-- `13161` (valor lembrado errado) e refutado: este exemplo FALHARIA se o numero errado
fosse usado no lugar do correto. -/
example : V 7 8 3 ≠ 13161 := by decide +kernel

example : ¬ (V 7 8 3 = 13161) := by rw [V_7_8_3]; norm_num

/-- Honestidade do estresse: o `V` errado (13161) NAO mudaria o teto publicado; ambos dao 439.
O erro de memoria era no valor de `V` (e em `S`), nao na cota inteira. -/
example : (7 ^ 8 + 13161 - 1) / 13161 = 439 := by norm_num
example : (7 ^ 8 + 13153 - 1) / 13153 = 439 := by norm_num

/-- E `438` nao e cota valida: `438 * 13153 < 7^8` (a justeza usa o `V` certo). -/
example : 438 * 13153 < 7 ^ 8 := by norm_num

end CoveringA3

#print axioms CoveringA3.lb_of_sphere
#print axioms CoveringA3.lt_of_sphere
#print axioms CoveringA3.pred_not_sphere
#print axioms CoveringA3.rat_ceil_gap
#print axioms CoveringA3.additive_gap_nonneg
#print axioms CoveringA3.gap_over_ratio_pos
#print axioms CoveringA3.ceil_eq_natCeil
#print axioms CoveringA3.cellFacts_intro
#print axioms CoveringA3.cell_5_7_2
#print axioms CoveringA3.cell_4_10_4
#print axioms CoveringA3.cell_5_9_3
#print axioms CoveringA3.cell_5_10_4
#print axioms CoveringA3.cell_5_9_5
#print axioms CoveringA3.cell_5_9_4
#print axioms CoveringA3.cell_7_8_3
#print axioms CoveringA3.cell_7_9_4
#print axioms CoveringA3.lb_5_7_2
#print axioms CoveringA3.tight_5_7_2
#print axioms CoveringA3.tight_7_8_3
#print axioms CoveringA3.V_7_8_3
