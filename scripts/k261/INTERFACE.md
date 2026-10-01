# INTERFACE — núcleo de busca verificável (frente 4a) ↔ gerador de pedaços (frente 4b)

Fonte da verdade: `CoveringLean/SearchCore.lean` (só core do Lean, sem Mathlib).
Se este texto e o código divergirem, **vale o código**; avise 4a.

## Objetos

```lean
namespace SC
structure St where  l : Nat; cov : Nat; forb : Nat   -- escrever como  ⟨l, cov, forb⟩
def chkN (n : Nat) (S : List St) (d : Nat) (s : St) : Bool
def chk  (S : List St) (d : Nat) (s : St) : Bool := chkN 6 S d s
def root (n m : Nat) : St := ⟨m, bm n (2^n-1), 1 <<< (2^n-1)⟩
```

* palavras = `Nat` em `[0, 2^n)`; conjuntos = bitmask `Nat` (bit `w` ligado ⇔ palavra `w` no conjunto).
* `l` = centros que ainda podem ser escolhidos; `cov` = palavras cobertas; `forb` = centros proibidos.
* `bm n c` = bola de raio 1 de `c`: bits `c, c^1, c^2, c^4, …, c^2^(n-1)`.
* `nbr n u` = lista `[u, u^1, u^2, u^4, …, u^2^(n-1)]` — **ordem fixa**, é a ordem dos filhos.

## Teorema que a prova dá (SearchSound.lean)

`chkN n S d s = true → (∀ t ∈ S, Ref n t) → Ref n s`, onde
`Ref n s` = não existe lista `L` de centros `< 2^n`, todos fora de `s.forb`, com `|L| ≤ s.l`,
tal que `s.cov ∪ ⋃_{c∈L} bm n c` = todas as `2^n` palavras.

Objetivo final: `Ref 6 (root 6 10)` ⇒ `K_2(6,1) ≥ 12`.  (`Ref 6 (root 6 9)` ⇒ `≥ 11`.)

## Semântica exata de um nó (o Python tem de espelhar bit a bit)

Entrada: estado `s = ⟨l, cov, forb⟩`, profundidade restante `d`, lista de fronteira `S` (consumida
da esquerda para a direita).  Seja `U` = palavras `< 2^n` fora de `cov`, `|U|` = popcount.

1. Se `U = ∅` → **FALHA** (achou cobertura; a busca inteira devolve `false`).
2. Se `l * (n+1) < |U|` → **PODA** (refutado, não consome nada de `S`).  Isto inclui `l = 0`.
3. Se `d = 0` → **FRONTEIRA**: o estado tem de ser exatamente a cabeça de `S` (igualdade dos três
   `Nat`); a cabeça é consumida.  Se `S` vazia ou cabeça diferente → FALHA.
4. Senão (`d > 0`): `u` = **menor** palavra de `U`.  Para cada `c` em `nbr n u`, na ordem acima,
   mantendo um `F` que começa em `forb`:
   * se `c ∈ F` → pula `c`;
   * senão → filho `⟨l-1, cov ||| bm n c, F ||| (1<<<c)⟩` com profundidade `d-1`; depois
     `F := F ||| (1<<<c)` (o próprio `c` entra em `F`, junto com os irmãos anteriores).
   Todos os filhos têm de passar.  Se nenhum `c` está livre, o nó passa (refutado).

`chkN n S d s = true` ⇔ a raiz passa **e** `S` foi consumida inteira.

Observações para o gerador:
* A contagem da poda é o popcount **exato** de `U` (internamente o Lean carrega uma cota inferior
  incremental que coincide com o exato; para o Python basta o popcount).
* A ordem DFS de `S`: pré-ordem, filhos na ordem de `nbr n u`.  Só entram em `S` os nós de
  profundidade exatamente `d` que **não** caíram nos casos 1–2.
* Um pedaço refuta seu estado sozinho com `S = []` e `d` maior que a altura da subárvore
  (`d = s.l + 1` sempre basta, pois cada nível gasta um centro e `l = 0` poda).
* Hierarquia é permitida: um arquivo intermediário prova `chk S_j d_j s_j = true` e o de cima usa
  `s_j` na sua própria fronteira.

## Formato de um pedaço

```lean
import CoveringLean.SearchCore
open SC
theorem chunk_k : chk [] 11 ⟨l, cov, forb⟩ = true := by decide +kernel
```
e a raiz (montagem, 4a): `theorem top : chk [s_1, …, s_m] d (root 6 10) = true := by decide +kernel`.

Proibido: `native_decide`, `decide` puro, `rfl`/`reduceBool`, `sorry`, axioma novo.

## Medições (lean-build2, Lean 4.34.1, `decide +kernel`) — 4a, 2026-10-01

| busca | nós (sc_ref.py) | tempo | RSS máx |
|---|---|---|---|
| `chkN 5 [] 6 (root 5 5)` (K_2(5,1) ≥ 7) | 785 | ~1,4 s | <1 GB |
| `chk [] 10 (root 6 9)` (≥ 11, arquivo único) | 25 827 | 99 s | 7,1 GB |
| pedaço de `root 6 10` com 11 171 nós | 11 171 | 76 s | 3,3 GB |

Regra prática: ~3–7 ms e ~0,3 MB por nó; mantenha pedaços ≤ ~25 000 nós para caber em 8 GB.
GMP no kernel confirmado para `&&& ||| ^^^ >>> <<<` e `Nat.log2` (números de 300 000 bits).

## Referência executável (espelho exato, 4a)

* `~/h/sc_ref.py n m [d]` — espelho Python de `chkN` (conta nós, devolve a fronteira).
  `root 6 10`: 436 727 nós; `root 6 9`: 25 827; `root 5 5`: 785.
* `~/h/gen_demo.py n m d outdir PREFIX` — gera `PREFIX_Chunk_k.lean` + `PREFIX_Top.lean`
  (montagem com `chkN_sound`). Em d=2, `root 6 10` dá 38 pedaços, o maior com 21 207 nós.
* `~/h/build_chunks.sh PREFIX [P]` — compila com ≤ P builds simultâneos, resumo em `~/h/logs/PREFIX.sum`.

Ensaio completo já passou: `G69_*` + `SearchK6ge11.lean` provam `K_2(6,1) ≥ 11` sem hipótese.
4a está compilando `G610_*` (o mesmo para `≥ 12`); 4b: se o seu gerador cobrir o mesmo, compare
a fronteira com `sc_ref.py 6 10 2` (tem de ser idêntica, na mesma ordem).
