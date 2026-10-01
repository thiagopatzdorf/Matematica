/-!
# SearchCore: núcleo de busca verificável para códigos de cobertura binários de raio 1

Só o core do Lean (sem Mathlib), para que os pedaços gerados (`Chunk_k.lean`) compilem leve.
Palavras de `{0,1}^n` são `Nat < 2^n`; conjuntos de palavras são bitmasks `Nat` (bit `w` = palavra
`w`).  Todas as operações por nó são `Nat.land/lor/xor/shiftLeft/shiftRight/log2/beq/blt`, que o
kernel calcula com GMP.

A semântica exata (ordem dos filhos, poda, fronteira) está em `INTERFACE.md`; o gerador Python
tem de espelhá-la bit a bit.  A prova de que `chk = true` implica refutação está em
`SearchSound.lean`.
-/

namespace SC

/-- Estado de busca: `l` = quantos centros ainda podem ser escolhidos, `cov` = bitmask das
palavras já cobertas, `forb` = bitmask dos centros proibidos. -/
structure St where
  l : Nat
  cov : Nat
  forb : Nat

/-- Igualdade booleana de estados (comparação com a fronteira). -/
def stBeq (a b : St) : Bool := a.l.beq b.l && (a.cov.beq b.cov && a.forb.beq b.forb)

/-- `bmA c k` = bitmask de `{c} ∪ {c xor 2^j : j < k}`. -/
def bmA (c : Nat) : Nat → Nat
  | 0 => 1 <<< c
  | k + 1 => bmA c k ||| 1 <<< (c ^^^ (1 <<< k))

/-- Bola de Hamming de raio 1 do centro `c` em `{0,1}^n`, como bitmask (`n+1` bits). -/
def bm (n c : Nat) : Nat := bmA c n

/-- `nbrT u k m` = `[u xor 2^k, u xor 2^(k+1), …]` (`m` termos). -/
def nbrT (u : Nat) : Nat → Nat → List Nat
  | _, 0 => []
  | k, m + 1 => (u ^^^ (1 <<< k)) :: nbrT u (k + 1) m

/-- Os `n+1` centros cuja bola contém `u`, NESTA ordem: `u, u^1, u^2, u^4, …, u^2^(n-1)`. -/
def nbr (n u : Nat) : List Nat := u :: nbrT u 0 n

/-- Máscara cheia: as `2^n` palavras. -/
def full (n : Nat) : Nat := (1 <<< (1 <<< n)) - 1

/-- Máscara das palavras descobertas. -/
def unc (n cov : Nat) : Nat := full n ^^^ (cov &&& full n)

/-- Índice do bit menos significativo ligado de `x` (para `x ≠ 0`); o resultado é conferido em
tempo de execução (`testBit`), então a prova não depende desta fórmula. -/
def low (x : Nat) : Nat := Nat.log2 (x ^^^ (x &&& (x - 1)))

/-- Contagem de bits: `popc k m` = número de bits ligados de `m` entre as posições `0..k-1`. -/
def popc : Nat → Nat → Nat
  | 0, _ => 0
  | k + 1, m => m % 2 + popc k (m / 2)

/-- Quantas palavras da lista estão ligadas em `x`. -/
def cntIn (x : Nat) : List Nat → Nat
  | [] => 0
  | w :: ws => cond (x.testBit w) (cntIn x ws + 1) (cntIn x ws)

/-- Laço dos filhos.  `f` é a chamada recursiva; `l'` já é `l - 1`; `x` = descobertas do pai;
`ucnt` = cota inferior do número de descobertas do pai.  Cada centro livre `c` vira um filho com
`cov ∪ bola c` e `forb ∪ {centros já tentados, inclusive c}`. -/
def kids (n : Nat) (f : St → Nat → List St → Option (List St)) (l' cov x ucnt : Nat) :
    Nat → List Nat → List St → Option (List St)
  | _, [], S => some S
  | forb, c :: cs, S =>
    cond (forb.testBit c) (kids n f l' cov x ucnt forb cs S)
      (match f ⟨l', cov ||| bm n c, forb ||| 1 <<< c⟩ (ucnt - cntIn x (nbr n c)) S with
        | none => none
        | some S' => kids n f l' cov x ucnt (forb ||| 1 <<< c) cs S')

/-- Um nó.  `rec = none` significa profundidade esgotada (fronteira: o estado tem de ser a cabeça
de `S`, que é consumida); `rec = some f` expande. -/
def node (n : Nat) (rec : Option (St → Nat → List St → Option (List St))) (s : St) (ucnt : Nat)
    (S : List St) : Option (List St) :=
  let x := unc n s.cov
  cond (x.beq 0) none <|
  cond (Nat.blt (s.l * (n + 1)) ucnt) (some S) <|
  match rec with
  | none =>
    match S with
    | [] => none
    | t :: S' => cond (stBeq t s) (some S') none
  | some f =>
    let u := low x
    cond (x.testBit u) (kids n f (s.l - 1) s.cov x ucnt s.forb (nbr n u) S) none

/-- Busca com profundidade `d`, consumindo a lista de fronteira `S` em ordem DFS. -/
def go (n : Nat) : Nat → St → Nat → List St → Option (List St)
  | 0 => node n none
  | d + 1 => node n (some (go n d))

/-- `chkN n S d s = true`: toda tentativa de completar `s` com `≤ s.l` centros falha, desde que
todo estado de `S` (a fronteira na profundidade `d`, em ordem DFS) também seja refutado. -/
def chkN (n : Nat) (S : List St) (d : Nat) (s : St) : Bool :=
  match go n d s (popc (1 <<< n) (unc n s.cov)) S with
  | some [] => true
  | _ => false

/-- Instância `n = 6` (64 palavras). -/
def chk (S : List St) (d : Nat) (s : St) : Bool := chkN 6 S d s

/-- Raiz da busca `K_2(n,1) ≥ m+2`: o centro `2^n-1` está no código (translação), sobram `m`. -/
def root (n m : Nat) : St := ⟨m, bm n ((1 <<< n) - 1), 1 <<< ((1 <<< n) - 1)⟩

end SC
