/-!
# Duas cotas superiores de segunda ordem conferidas pelo kernel

K^(2)_q(n,r) é o menor |C|, C ⊆ Z_q^n, com R_2(C) ≤ r, onde

  R_2(C) = max_{(u1,u2)} min_{(c1,c2) ∈ C×C} |supp(u1−c1) ∪ supp(u2−c2)|

(Elimelech–Schwartz, arXiv:2210.00531). Uma palavra de Z_q^n é representada pelo seu índice
x < q^n na base q, little-endian: a coordenada i é `x / q^i % q` (a mesma convenção de
`segunda_ordem/raio2.py`; em `segunda_ordem/dados/testemunhas.json` a coordenada 0 é o primeiro
caractere). Isso é uma bijeção entre `{x // x < q^n}` e Z_q^n, então os enunciados abaixo dizem
exatamente "R_2(C) ≤ r".

Só Lean core (sem Mathlib), só `decide +kernel`. Não entra no alvo padrão do `lake build`;
confira com

    lean -j1 segunda_ordem/lean/SegundaOrdemUB.lean

(o `lean` da versão de `lean-toolchain`; ~1 min). Saída medida em 2026-10-06: os dois teoremas
"do not depend on any axioms" (nem os três padrão). A testemunha K^(2)_3(4,2) ≤ 9 também foi
tentada e estourou a memória da máquina (81² pares × 81 pares de palavras no kernel); fica fora.
-/

namespace SegundaOrdem

/-- Coordenada `i` da palavra de índice `x` em Z_q^n. -/
def coord (q x i : Nat) : Nat := x / q ^ i % q

/-- |supp(u1−c1) ∪ supp(u2−c2)|: colunas em que (u1;u2) e (c1;c2) diferem. -/
def dist2 (q n u1 u2 c1 c2 : Nat) : Nat :=
  ((List.range n).filter fun i => coord q u1 i != coord q c1 i || coord q u2 i != coord q c2 i).length

/-- "R_2(C) ≤ r" para C dado por índices (cada índice < q^n). -/
def R2Le (q n r : Nat) (C : List Nat) : Prop :=
  ∀ u1, u1 < q ^ n → ∀ u2, u2 < q ^ n → ∃ c1 ∈ C, ∃ c2 ∈ C, dist2 q n u1 u2 c1 c2 ≤ r

instance (q n r : Nat) (C : List Nat) : Decidable (R2Le q n r C) := by
  unfold R2Le; exact inferInstance

/-- Testemunha de K^(2)_2(5,2) ≤ 6: palavras 00010, 00110, 01101, 10001, 11100, 11111. -/
def C_2_5_2 : List Nat := [8, 12, 22, 17, 7, 31]

theorem k2_2_5_2_le_6 : C_2_5_2.length = 6 ∧ (∀ c ∈ C_2_5_2, c < 2 ^ 5) ∧ R2Le 2 5 2 C_2_5_2 := by
  decide +kernel

/-- Testemunha de K^(2)_3(3,1) ≤ 9: 001, 011, 021, 100, 111, 121, 201, 212, 220. -/
def C_3_3_1 : List Nat := [9, 12, 15, 1, 13, 16, 11, 23, 8]

theorem k2_3_3_1_le_9 : C_3_3_1.length = 9 ∧ (∀ c ∈ C_3_3_1, c < 3 ^ 3) ∧ R2Le 3 3 1 C_3_3_1 := by
  decide +kernel

end SegundaOrdem

#print axioms SegundaOrdem.k2_2_5_2_le_6
#print axioms SegundaOrdem.k2_3_3_1_le_9
