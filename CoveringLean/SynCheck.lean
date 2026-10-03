/-!
# SynCheck: o verificador booleano do certificado por síndromes (só núcleo, sem Mathlib)

Formato de código coberto aqui: `C = ⋃ₛ (rₛ + C₀) ∪ P`, com `C₀ = {m·G}` um código linear
`[n,k]_q` cujo gerador `G` é a identidade num bloco contíguo de coordenadas `o, …, o+k-1`
(as linhas de `G` são palavras codificadas como `Nat`, dígito `i` = `w / q^i % q`).

Por que o bloco de informação: toda palavra `x` se escreve `x = y + c` com `c ∈ C₀` e `y`
nulo no bloco; como a união de cosets é invariante por `C₀`, basta checar os `q^(n-k)` pontos
`y` (o "transversal", indexado por `t`), e não os `q^n` pontos do espaço.  Um `t` cuja bola não
encontra nenhum coset é "órfão": aí os `q^k` pontos `y_t + m·G` são checados contra a lista.

Este arquivo só define as funções booleanas (rápidas no kernel: só operações de `Nat` que o
kernel acelera com GMP).  A ponte de correção está em `SynBridge.lean`.  As folhas importam só
este arquivo, para elaborar sem carregar a Mathlib.
-/

namespace Syn

/-- Dígito `i` de `w` em base `q` (mesma convenção de `CoveringCerts.dig`). -/
def D (q w i : Nat) : Nat := Nat.mod (Nat.div w (Nat.pow q i)) q

/-- `S q Gs m i = ∑ⱼ (dígito j de m) · (dígito i de Gs[j])` (sem redução mod q). -/
def S (q : Nat) : List Nat → Nat → Nat → Nat
  | [], _, _ => 0
  | g :: gs, m, i => Nat.add (Nat.mul (Nat.mod m q) (D q g i)) (S q gs (Nat.div m q) i)

/-- Coordenada `i` da palavra `rd + m·G` (dígitos de `rd` dados como função). -/
def cwF (q : Nat) (Gs : List Nat) (rd : Nat → Nat) (m i : Nat) : Nat :=
  Nat.mod (Nat.add (rd i) (S q Gs m i)) q

/-- Ponto `y_t` do transversal: zero no bloco `[o, o+k)`, dígitos de `t` fora dele. -/
def ydig (q o k t i : Nat) : Nat :=
  cond (Nat.blt i o) (D q t i) (cond (Nat.blt i (Nat.add o k)) 0 (D q t (Nat.sub i k)))

/-- Distância de Hamming entre duas funções-dígito nas primeiras `m` coordenadas. -/
def dist (a b : Nat → Nat) : Nat → Nat
  | 0 => 0
  | m + 1 => Nat.add (dist a b m) (cond (Nat.beq (a m) (b m)) 0 1)

/-- Entrada `j` (de `b` bits) do inteiro empacotado `PN`. -/
def pget (PN b j : Nat) : Nat := Nat.mod (Nat.shiftRight PN (Nat.mul b j)) (Nat.pow 2 b)

/-- Desempacota `c` entradas de `b` bits. -/
def unpack (b : Nat) : Nat → Nat → List Nat
  | 0, _ => []
  | c + 1, PN => Nat.mod PN (Nat.pow 2 b) :: unpack b c (Nat.shiftRight PN b)

def memN (x : Nat) : List Nat → Bool
  | [] => false
  | y :: ys => cond (Nat.beq x y) true (memN x ys)

/-- Codificação little-endian dos `n` primeiros valores de `f`. -/
def enc (q : Nat) : (Nat → Nat) → Nat → Nat
  | _, 0 => 0
  | f, n + 1 => Nat.add (f 0) (Nat.mul q (enc q (fun i => f (Nat.add i 1)) n))

/-- Os parâmetros de um certificado. `L` (a lista ordenada do código) está empacotada em `PN`
com `b` bits por palavra e `cnt = |L|` entradas. -/
structure Spec where
  q : Nat
  n : Nat
  k : Nat
  o : Nat
  R : Nat
  Gs : List Nat
  reps : List Nat
  orphs : List Nat
  PN : Nat
  b : Nat
  cnt : Nat

/-- Testemunha de um ponto do transversal: `w = s·q^k + m` (coset `s`, mensagem `m`) a
distância `≤ R`, ou `w = |reps|·q^k`, que marca `t` como órfão (então `t ∈ orphs`). -/
def okT (P : Spec) (t w : Nat) : Bool :=
  cond (Nat.beq w (Nat.mul P.reps.length (Nat.pow P.q P.k)))
    (memN t P.orphs)
    (Nat.blt (Nat.div w (Nat.pow P.q P.k)) P.reps.length &&
      Nat.ble (dist (cwF P.q P.Gs (D P.q (P.reps.getD (Nat.div w (Nat.pow P.q P.k)) 0))
        (Nat.mod w (Nat.pow P.q P.k))) (ydig P.q P.o P.k t) P.n) P.R)

/-- `c` pontos consecutivos do transversal a partir de `t`; testemunhas de `B` em `B` no fluxo `N`. -/
def chkT (P : Spec) (B : Nat) : Nat → Nat → Nat → Bool
  | 0, _, _ => true
  | c + 1, t, N => okT P t (Nat.mod N B) && chkT P B c (Nat.add t 1) (Nat.div N B)

/-- Ponto `y_t + a·G` de um órfão coberto pela palavra `L[j]`. -/
def okO (P : Spec) (t a j : Nat) : Bool :=
  Nat.blt j P.cnt && Nat.ble (dist (D P.q (pget P.PN P.b j)) (cwF P.q P.Gs (ydig P.q P.o P.k t) a) P.n) P.R

def chkO (P : Spec) (B t : Nat) : Nat → Nat → Nat → Bool
  | 0, _, _ => true
  | c + 1, a, N => okO P t a (Nat.mod N B) && chkO P B t c (Nat.add a 1) (Nat.div N B)

/-- A palavra `rₛ + m·G` é `L[j]`. -/
def okB (P : Spec) (s m j : Nat) : Bool :=
  Nat.blt j P.cnt &&
    Nat.beq (pget P.PN P.b j) (enc P.q (cwF P.q P.Gs (D P.q (P.reps.getD s 0)) m) P.n)

def chkB (P : Spec) (B s : Nat) : Nat → Nat → Nat → Bool
  | 0, _, _ => true
  | c + 1, m, N => okB P s m (Nat.mod N B) && chkB P B s c (Nat.add m 1) (Nat.div N B)

/-- O gerador é a identidade no bloco: para todo `a < q^k` e `l < k`, `(a·G)_{o+l} = aₗ`. -/
def chkPivA (P : Spec) (a : Nat) : Nat → Bool
  | 0 => true
  | l + 1 => Nat.beq (Nat.mod (S P.q P.Gs a (Nat.add P.o l)) P.q) (D P.q a l) && chkPivA P a l

def chkPiv (P : Spec) : Nat → Bool
  | 0 => true
  | a + 1 => chkPivA P a P.k && chkPiv P a

end Syn
