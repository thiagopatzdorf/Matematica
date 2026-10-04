import CoveringLean.LratK

/-!
# A CNF de um perfil de K_q(4,2), no Lean

Reimplementa `tools/exatos/k742/encode.py` (`codificar(q, M, perfil, quebra=True)`) **cláusula a
cláusula e variável a variável**: mesma numeração (a ordem em que o Python chama `cnf.var()`) e
mesma ordem de cláusulas. Os literais saem já no formato de `LratK` (`2v` positivo, `2v+1`
negativo).

A igualdade com o DIMACS do Python não precisa de confiança: `LratK.checkF` confere, no kernel,
que o banco montado a partir do arquivo guarda exatamente estas cláusulas.

Perfil: `t : List (List Nat)`, os 4 tipos (vetores de fibra decrescentes, um por coordenada).
-/

namespace K742Cnf

/-- Literal positivo e negativo no formato de `LratK`. -/
def pos (v : Nat) : Nat := 2 * v
def neg (v : Nat) : Nat := 2 * v + 1

/-- Pares de coordenadas `(i, j)`, `i < j`, na ordem de `itertools.combinations(range(4), 2)`. -/
def pares : List (Nat × Nat) := [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]

/-- Pares `a < b` de `range q`, na ordem de `itertools.combinations`. -/
def combos2 (q : Nat) : List (Nat × Nat) :=
  (List.range q).flatMap fun a => ((List.range q).filter (a < ·)).map fun b => (a, b)

/-- Variável `x[k][i][a]` (palavra `k`, coordenada `i = 1..3`, símbolo `a`). -/
def xv (q k i a : Nat) : Nat := 1 + k * (3 * q) + (i - 1) * q + a

/-- Cláusulas "exatamente um símbolo" de cada palavra e coordenada. -/
def exactlyOne (q M : Nat) : List (List Nat) :=
  (List.range M).flatMap fun k => [1, 2, 3].flatMap fun i =>
    ((List.range q).map fun a => pos (xv q k i a)) ::
      (combos2 q).map fun (a, b) => [neg (xv q k i a), neg (xv q k i b)]

/-- Contador sequencial `exatamente(xs, k)` com variáveis a partir de `base`
(`r[i][j] = base + i*(k+1) + j`). Devolve as cláusulas; usa `xs.length * (k+1)` variáveis. -/
def exatamente (xs : List Nat) (k base : Nat) : List (List Nat) :=
  let n := xs.length
  let r := fun i j => base + i * (k + 1) + j
  let x := fun i => xs.getD i 0
  if k > n then [[]] else
  ((List.range n).flatMap fun i => (List.range (k + 1)).flatMap fun j =>
    let v := r i j
    if i = 0 then
      (if j = 0 then [[neg v, pos (x 0)], [pos v, neg (x 0)]] else [[neg v]])
    else
      let prev := r (i - 1) j
      [neg prev, pos v] ::
      (if j = 0 then [[neg (x i), pos v], [neg v, pos prev, pos (x i)]]
       else
         let pj := r (i - 1) (j - 1)
         [[neg pj, neg (x i), pos v], [neg v, pos prev, pos (x i)], [neg v, pos prev, pos pj]])) ++
  (if k > 0 then [[pos (r (n - 1) (k - 1))]] else []) ++ [[neg (r (n - 1) k)]]

/-- Lista de (coordenada, símbolo) na ordem dos contadores: `i = 1..3`, `a = 0..q-1`. -/
def counterKeys (q : Nat) : List (Nat × Nat) := [1, 2, 3].flatMap fun i => (List.range q).map (i, ·)

/-- Tamanho de fibra `t[i][a]`. -/
def tv (t : List (List Nat)) (i a : Nat) : Nat := (t.getD i []).getD a 0

/-- Primeira variável do contador da posição `idx` de `counterKeys`. -/
def counterBase (q M : Nat) (t : List (List Nat)) (idx : Nat) : Nat :=
  1 + M * (3 * q) +
    (((counterKeys q).take idx).map fun (i, a) => M * (tv t i a + 1)).sum

def counters (q M : Nat) (t : List (List Nat)) : List (List Nat) :=
  ((counterKeys q).zipIdx).flatMap fun ((i, a), idx) =>
    exatamente ((List.range M).map fun k => xv q k i a) (tv t i a)
      (counterBase q M t idx)

/-- Início do bloco do símbolo `a` na coordenada 0. -/
def blockStart (t : List (List Nat)) (a : Nat) : Nat := ((t.getD 0 []).take a).sum

/-- Índices das palavras do bloco `a`. -/
def block (t : List (List Nat)) (a : Nat) : List Nat :=
  (List.range (tv t 0 a)).map (blockStart t a + ·)

/-- Variáveis por par de coordenadas: `q*q` projeções, cada uma com `M` auxiliares `y` quando
`i ≥ 1`. -/
def pairSize (q M : Nat) (ij : Nat × Nat) : Nat := if ij.1 = 0 then q * q else q * q * (M + 1)

/-- Primeira variável das projeções. -/
def projBase (q M : Nat) (t : List (List Nat)) : Nat := counterBase q M t (3 * q)

def pairBase (q M : Nat) (t : List (List Nat)) (p : Nat) : Nat :=
  projBase q M t + ((pares.take p).map (pairSize q M)).sum

/-- Variável `P[i,j,a,b]` do par de índice `p`. -/
def pv (q M : Nat) (t : List (List Nat)) (p a b : Nat) : Nat :=
  let ij := pares.getD p (0, 0)
  if ij.1 = 0 then pairBase q M t p + a * q + b
  else pairBase q M t p + (a * q + b) * (M + 1)

def projections (q M : Nat) (t : List (List Nat)) : List (List Nat) :=
  (pares.zipIdx).flatMap fun ((i, j), p) => (List.range q).flatMap fun a =>
    (List.range q).flatMap fun b =>
      let P := pv q M t p a b
      if i = 0 then
        let lits := (block t a).map fun k => pos (xv q k j b)
        (neg P :: lits) :: lits.map fun l => [l + 1, pos P]
      else
        ((List.range M).flatMap fun k =>
          let y := P + 1 + k
          [[neg y, pos (xv q k i a)], [neg y, pos (xv q k j b)],
           [pos y, neg (xv q k i a), neg (xv q k j b)], [neg y, pos P]]) ++
        [neg P :: (List.range M).map fun k => pos (P + 1 + k)]

/-- Uma cláusula por ponto de `Z_q^4` (ordem lexicográfica de `itertools.product`). -/
def coverage (q M : Nat) (t : List (List Nat)) : List (List Nat) :=
  (List.range q).flatMap fun w0 => (List.range q).flatMap fun w1 =>
    (List.range q).flatMap fun w2 => (List.range q).map fun w3 =>
      let w := [w0, w1, w2, w3]
      (pares.zipIdx).map fun ((i, j), p) => pos (pv q M t p (w.getD i 0) (w.getD j 0))

/-- (d): dentro de cada bloco, coordenada 1 não decrescente. -/
def symD (q : Nat) (t : List (List Nat)) : List (List Nat) :=
  (List.range q).flatMap fun B => ((block t B).dropLast).flatMap fun k =>
    (List.range q).flatMap fun a => (List.range a).map fun b =>
      [neg (xv q k 1 a), neg (xv q (k + 1) 1 b)]

/-- (e): coordenada 1, precedência por bloco entre símbolos de mesma fibra. -/
def symE (q : Nat) (t : List (List Nat)) : List (List Nat) :=
  (List.range (q - 1)).flatMap fun a =>
    if tv t 1 a ≠ tv t 1 (a + 1) then [] else
    (List.range q).flatMap fun bi =>
      let antes := ((List.range (bi + 1)).flatMap (block t)).map fun kk => pos (xv q kk 1 a)
      (block t bi).map fun k => neg (xv q k 1 (a + 1)) :: antes

/-- (f): coordenadas 2 e 3, precedência por palavra entre símbolos de mesma fibra. -/
def symF (q M : Nat) (t : List (List Nat)) : List (List Nat) :=
  [2, 3].flatMap fun i => (List.range (q - 1)).flatMap fun a =>
    if tv t i a ≠ tv t i (a + 1) then [] else
    (List.range M).map fun k =>
      neg (xv q k i (a + 1)) :: (List.range k).map fun kk => pos (xv q kk i a)

/-- A CNF sem a quebra de simetria (d)–(f) (`encode.py --sem-quebra`): só (a)–(c), que vêm de
graça da ordem dos tipos, dos símbolos e dos blocos. A ponte código → CNF é bem mais curta
para esta versão (não precisa da forma normal do `canonizar.py`, passos 4–5). -/
def cnfSemQuebra (q M : Nat) (t : List (List Nat)) : List (List Nat) :=
  exactlyOne q M ++ counters q M t ++ projections q M t ++ coverage q M t

/-- A CNF do perfil `t` (com a quebra de simetria (d)–(f)), igual à de `encode.py`. -/
def cnf (q M : Nat) (t : List (List Nat)) : List (List Nat) :=
  cnfSemQuebra q M t ++ symD q t ++ symE q t ++ symF q M t

end K742Cnf

namespace K742

/-- Os 70 perfis de `M = 18`, na ordem de `encode.py --q 7 --M 18 --listar`. -/
def perfis18 : List (List (List Nat)) :=
  [[[4,3,3,2,2,2,2], [4,3,3,2,2,2,2], [4,3,3,2,2,2,2], [4,3,3,2,2,2,2]],
   [[4,3,3,2,2,2,2], [4,3,3,2,2,2,2], [4,3,3,2,2,2,2], [5,3,2,2,2,2,2]],
   [[4,3,3,2,2,2,2], [4,3,3,2,2,2,2], [4,3,3,2,2,2,2], [3,3,3,3,2,2,2]],
   [[4,3,3,2,2,2,2], [4,3,3,2,2,2,2], [4,3,3,2,2,2,2], [4,4,2,2,2,2,2]],
   [[4,3,3,2,2,2,2], [4,3,3,2,2,2,2], [4,3,3,2,2,2,2], [6,2,2,2,2,2,2]],
   [[4,3,3,2,2,2,2], [4,3,3,2,2,2,2], [5,3,2,2,2,2,2], [5,3,2,2,2,2,2]],
   [[4,3,3,2,2,2,2], [4,3,3,2,2,2,2], [5,3,2,2,2,2,2], [3,3,3,3,2,2,2]],
   [[4,3,3,2,2,2,2], [4,3,3,2,2,2,2], [5,3,2,2,2,2,2], [4,4,2,2,2,2,2]],
   [[4,3,3,2,2,2,2], [4,3,3,2,2,2,2], [5,3,2,2,2,2,2], [6,2,2,2,2,2,2]],
   [[4,3,3,2,2,2,2], [4,3,3,2,2,2,2], [3,3,3,3,2,2,2], [3,3,3,3,2,2,2]],
   [[4,3,3,2,2,2,2], [4,3,3,2,2,2,2], [3,3,3,3,2,2,2], [4,4,2,2,2,2,2]],
   [[4,3,3,2,2,2,2], [4,3,3,2,2,2,2], [3,3,3,3,2,2,2], [6,2,2,2,2,2,2]],
   [[4,3,3,2,2,2,2], [4,3,3,2,2,2,2], [4,4,2,2,2,2,2], [4,4,2,2,2,2,2]],
   [[4,3,3,2,2,2,2], [4,3,3,2,2,2,2], [4,4,2,2,2,2,2], [6,2,2,2,2,2,2]],
   [[4,3,3,2,2,2,2], [4,3,3,2,2,2,2], [6,2,2,2,2,2,2], [6,2,2,2,2,2,2]],
   [[4,3,3,2,2,2,2], [5,3,2,2,2,2,2], [5,3,2,2,2,2,2], [5,3,2,2,2,2,2]],
   [[4,3,3,2,2,2,2], [5,3,2,2,2,2,2], [5,3,2,2,2,2,2], [3,3,3,3,2,2,2]],
   [[4,3,3,2,2,2,2], [5,3,2,2,2,2,2], [5,3,2,2,2,2,2], [4,4,2,2,2,2,2]],
   [[4,3,3,2,2,2,2], [5,3,2,2,2,2,2], [5,3,2,2,2,2,2], [6,2,2,2,2,2,2]],
   [[4,3,3,2,2,2,2], [5,3,2,2,2,2,2], [3,3,3,3,2,2,2], [3,3,3,3,2,2,2]],
   [[4,3,3,2,2,2,2], [5,3,2,2,2,2,2], [3,3,3,3,2,2,2], [4,4,2,2,2,2,2]],
   [[4,3,3,2,2,2,2], [5,3,2,2,2,2,2], [3,3,3,3,2,2,2], [6,2,2,2,2,2,2]],
   [[4,3,3,2,2,2,2], [5,3,2,2,2,2,2], [4,4,2,2,2,2,2], [4,4,2,2,2,2,2]],
   [[4,3,3,2,2,2,2], [5,3,2,2,2,2,2], [4,4,2,2,2,2,2], [6,2,2,2,2,2,2]],
   [[4,3,3,2,2,2,2], [5,3,2,2,2,2,2], [6,2,2,2,2,2,2], [6,2,2,2,2,2,2]],
   [[4,3,3,2,2,2,2], [3,3,3,3,2,2,2], [3,3,3,3,2,2,2], [3,3,3,3,2,2,2]],
   [[4,3,3,2,2,2,2], [3,3,3,3,2,2,2], [3,3,3,3,2,2,2], [4,4,2,2,2,2,2]],
   [[4,3,3,2,2,2,2], [3,3,3,3,2,2,2], [3,3,3,3,2,2,2], [6,2,2,2,2,2,2]],
   [[4,3,3,2,2,2,2], [3,3,3,3,2,2,2], [4,4,2,2,2,2,2], [4,4,2,2,2,2,2]],
   [[4,3,3,2,2,2,2], [3,3,3,3,2,2,2], [4,4,2,2,2,2,2], [6,2,2,2,2,2,2]],
   [[4,3,3,2,2,2,2], [3,3,3,3,2,2,2], [6,2,2,2,2,2,2], [6,2,2,2,2,2,2]],
   [[4,3,3,2,2,2,2], [4,4,2,2,2,2,2], [4,4,2,2,2,2,2], [4,4,2,2,2,2,2]],
   [[4,3,3,2,2,2,2], [4,4,2,2,2,2,2], [4,4,2,2,2,2,2], [6,2,2,2,2,2,2]],
   [[4,3,3,2,2,2,2], [4,4,2,2,2,2,2], [6,2,2,2,2,2,2], [6,2,2,2,2,2,2]],
   [[4,3,3,2,2,2,2], [6,2,2,2,2,2,2], [6,2,2,2,2,2,2], [6,2,2,2,2,2,2]],
   [[5,3,2,2,2,2,2], [5,3,2,2,2,2,2], [5,3,2,2,2,2,2], [5,3,2,2,2,2,2]],
   [[5,3,2,2,2,2,2], [5,3,2,2,2,2,2], [5,3,2,2,2,2,2], [3,3,3,3,2,2,2]],
   [[5,3,2,2,2,2,2], [5,3,2,2,2,2,2], [5,3,2,2,2,2,2], [4,4,2,2,2,2,2]],
   [[5,3,2,2,2,2,2], [5,3,2,2,2,2,2], [5,3,2,2,2,2,2], [6,2,2,2,2,2,2]],
   [[5,3,2,2,2,2,2], [5,3,2,2,2,2,2], [3,3,3,3,2,2,2], [3,3,3,3,2,2,2]],
   [[5,3,2,2,2,2,2], [5,3,2,2,2,2,2], [3,3,3,3,2,2,2], [4,4,2,2,2,2,2]],
   [[5,3,2,2,2,2,2], [5,3,2,2,2,2,2], [3,3,3,3,2,2,2], [6,2,2,2,2,2,2]],
   [[5,3,2,2,2,2,2], [5,3,2,2,2,2,2], [4,4,2,2,2,2,2], [4,4,2,2,2,2,2]],
   [[5,3,2,2,2,2,2], [5,3,2,2,2,2,2], [4,4,2,2,2,2,2], [6,2,2,2,2,2,2]],
   [[5,3,2,2,2,2,2], [5,3,2,2,2,2,2], [6,2,2,2,2,2,2], [6,2,2,2,2,2,2]],
   [[5,3,2,2,2,2,2], [3,3,3,3,2,2,2], [3,3,3,3,2,2,2], [3,3,3,3,2,2,2]],
   [[5,3,2,2,2,2,2], [3,3,3,3,2,2,2], [3,3,3,3,2,2,2], [4,4,2,2,2,2,2]],
   [[5,3,2,2,2,2,2], [3,3,3,3,2,2,2], [3,3,3,3,2,2,2], [6,2,2,2,2,2,2]],
   [[5,3,2,2,2,2,2], [3,3,3,3,2,2,2], [4,4,2,2,2,2,2], [4,4,2,2,2,2,2]],
   [[5,3,2,2,2,2,2], [3,3,3,3,2,2,2], [4,4,2,2,2,2,2], [6,2,2,2,2,2,2]],
   [[5,3,2,2,2,2,2], [3,3,3,3,2,2,2], [6,2,2,2,2,2,2], [6,2,2,2,2,2,2]],
   [[5,3,2,2,2,2,2], [4,4,2,2,2,2,2], [4,4,2,2,2,2,2], [4,4,2,2,2,2,2]],
   [[5,3,2,2,2,2,2], [4,4,2,2,2,2,2], [4,4,2,2,2,2,2], [6,2,2,2,2,2,2]],
   [[5,3,2,2,2,2,2], [4,4,2,2,2,2,2], [6,2,2,2,2,2,2], [6,2,2,2,2,2,2]],
   [[5,3,2,2,2,2,2], [6,2,2,2,2,2,2], [6,2,2,2,2,2,2], [6,2,2,2,2,2,2]],
   [[3,3,3,3,2,2,2], [3,3,3,3,2,2,2], [3,3,3,3,2,2,2], [3,3,3,3,2,2,2]],
   [[3,3,3,3,2,2,2], [3,3,3,3,2,2,2], [3,3,3,3,2,2,2], [4,4,2,2,2,2,2]],
   [[3,3,3,3,2,2,2], [3,3,3,3,2,2,2], [3,3,3,3,2,2,2], [6,2,2,2,2,2,2]],
   [[3,3,3,3,2,2,2], [3,3,3,3,2,2,2], [4,4,2,2,2,2,2], [4,4,2,2,2,2,2]],
   [[3,3,3,3,2,2,2], [3,3,3,3,2,2,2], [4,4,2,2,2,2,2], [6,2,2,2,2,2,2]],
   [[3,3,3,3,2,2,2], [3,3,3,3,2,2,2], [6,2,2,2,2,2,2], [6,2,2,2,2,2,2]],
   [[3,3,3,3,2,2,2], [4,4,2,2,2,2,2], [4,4,2,2,2,2,2], [4,4,2,2,2,2,2]],
   [[3,3,3,3,2,2,2], [4,4,2,2,2,2,2], [4,4,2,2,2,2,2], [6,2,2,2,2,2,2]],
   [[3,3,3,3,2,2,2], [4,4,2,2,2,2,2], [6,2,2,2,2,2,2], [6,2,2,2,2,2,2]],
   [[3,3,3,3,2,2,2], [6,2,2,2,2,2,2], [6,2,2,2,2,2,2], [6,2,2,2,2,2,2]],
   [[4,4,2,2,2,2,2], [4,4,2,2,2,2,2], [4,4,2,2,2,2,2], [4,4,2,2,2,2,2]],
   [[4,4,2,2,2,2,2], [4,4,2,2,2,2,2], [4,4,2,2,2,2,2], [6,2,2,2,2,2,2]],
   [[4,4,2,2,2,2,2], [4,4,2,2,2,2,2], [6,2,2,2,2,2,2], [6,2,2,2,2,2,2]],
   [[4,4,2,2,2,2,2], [6,2,2,2,2,2,2], [6,2,2,2,2,2,2], [6,2,2,2,2,2,2]],
   [[6,2,2,2,2,2,2], [6,2,2,2,2,2,2], [6,2,2,2,2,2,2], [6,2,2,2,2,2,2]]]

theorem perfis18_length : perfis18.length = 70 := by decide

end K742

#print axioms K742.perfis18_length
