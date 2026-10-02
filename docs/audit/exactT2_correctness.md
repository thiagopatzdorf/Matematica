# exactT2: por que ele devolve exatamente os mesmos trios que exactT

Escopo: `scripts/search/base_search.c`, modos `exactT` (referência) e `exactT2` (otimizado), para
bases formadas por 3 classes laterais `{0, s1, s2}` de um código `[n,k]_q`, `H = [I_r | A]`. No caso
estudado, q = 7, n = 9, k = 3 e r = 6.

## Definições

- `V = F_q^r`, `N = q^r`; `B = { H e : wt(e) <= R }`; `Bc = V \ B`.
- `orf(a,b,c) = |(Bc+a) ∩ (Bc+b) ∩ (Bc+c)|`, para um trio de pontos distintos `{a,b,c}` de `V`.
- **Saída a comparar:** o conjunto das órbitas de trios com `orf <= T` sob o grupo `G = {x ↦ λx + v}`
  (λ ∈ F_q*, v ∈ V), cada órbita com o seu valor de `orf`. Para comparar, cada trio é escrito na forma
  canônica: a menor tripla ordenada `{λ(p − b)}` entre os 3 pontos-base b e os q−1 escalares λ.
  Isso é feito por `canon.py` e, de forma independente, por `scripts/audit/verify_trios.c`.

**Lema 0 (invariância).** `orf` é constante nas órbitas de G.

Translação por v: `x ↦ x + v` leva `∩(Bc + p)` em `∩(Bc + p + v)`.

Escala por λ: `λB = B`, porque `wt(λe) = wt(e)`; logo `λBc = Bc` e `λ(Bc + p) = Bc + λp`. A bijeção
`x ↦ λx` leva um conjunto no outro. ∎

## Referência: exactT

O exactT percorre `s1 ∈ C`, onde C tem um representante por classe escalar de `V \ {0}` (o primeiro
dígito não nulo vale 1), e `s2 ∈ V \ {0, s1}`. Avalia o trio `{0, s1, s2}`.

**Completude.** Dada uma órbita, tome um representante `{a,b,c}`. Transladando por −a, ele vira
`{0, d, e}` com `d = b − a ≠ 0`. Existe um único λ com `λd ∈ C`; escalando, o trio vira `{0, s1, s2}`
com `s1 = λd ∈ C` e `s2 = λe ∉ {0, s1}`. Toda órbita, portanto, é visitada.

**Poda por amostra.** Seja `X(s1) = Bc ∩ (Bc + s1)` e Y ⊂ X qualquer. Para todo s2,
`orf(0,s1,s2) = |X ∩ (Bc+s2)| >= |Y ∩ (Bc+s2)| = cnt_Y(s2)`. Se `cnt_Y(s2) > T`, o trio está fora.
Caso contrário, a contagem continua sobre `X \ Y`, com saída antecipada só quando o valor passa de T.
O conjunto de pares (s1, s2) com `orf <= T` é obtido **exatamente**, qualquer que seja Y.

## As cinco transformações do exactT2

### 1. Amostra adaptativa (`m = ceil(mu·N/|Bc|)`, com teto 250)

- **Operação original:** amostra Y de tamanho fixo `m = 200`.
- **Transformação:** o tamanho passa a depender de `|Bc|`.
- **Invariante:** Y ⊂ X(s1).
- **Equivalência:** a poda acima é correta para **qualquer** Y ⊂ X, inclusive Y vazio; m só muda o
  tempo. O teto 250 garante que `cnt_Y <= |Y| <= 250` cabe no contador `uint8_t`, sem estouro.
- **Teste:** diferencial exactT × exactT2 (seção "Testes").

### 2. Contagem em blocos de L1

- **Operação original:** `cnt[y − b]++` para todo y ∈ Y e b ∈ Bc, num vetor de N posições.
- **Transformação:** a síndrome s se escreve `(lo(s), hi(s))`, com 3 dígitos em cada metade, e lo e
  hi são homomorfismos de grupo (a soma é dígito a dígito). Os valores `−b` são agrupados por
  `hi(−b)`. Para cada bloco H, `blk[l]` recebe as contribuições dos pares com
  `hi(y) + hi(−b) = H`, ou seja, com `hi(−b) = H − hi(y)`; a metade baixa vai para
  `lo(y) + lo(−b)`.
- **Invariante:** `blk[l]` do bloco H é igual a `cnt[l + LO·H]`.
- **Equivalência:** cada par (y, b) cai em **exatamente um** bloco, o de
  `H = hi(y − b) = hi(y) + hi(−b)`, e na posição baixa `lo(y − b)`. A união das contagens por
  bloco é a contagem completa.
- **Teste:** exactT2 com `sym=0` reproduz o exactT (classe 1, T=8: mesmos trios, mínimo 6).

### 3. Simetria do trio (`sym=1`): processar cada órbita pela sua diferença "mínima"

**Definição.** Para `v ≠ 0`, `pc(hi(v)) ∈ {0, …, 56}` é o índice da classe projetiva de `hi(v)` em
`F_7^3`. Se `hi(v) = 0`, define-se `pc = 57`, a maior chave. Valem duas propriedades:

- **P1:** `pc(hi(λv)) = pc(hi(v))`, porque hi é linear e a classe projetiva é invariante por escalar.
  Isso inclui λ = −1.
- **P2:** `hi(a − b) = hi(a) − hi(b)`.

**Regra.** Ao processar s1, com `j1 = pc(hi(s1))`, o bloco H só é pulado se
`pc(H) < j1` ou `pc(H − hi(s1)) < j1`.

**Invariante da órbita.** O multiconjunto `P = { pc(hi(d)) : d ∈ {b−a, c−a, c−b} }`. Ele não muda
por translação, porque as diferenças não mudam. Também não muda por escala nem por troca de sinal,
pela P1. Seja `j* = min P`.

**Afirmações:**

1. **Todo trio válido aparece.** Escolha uma diferença d com `pc(hi(d)) = j*` e rotule a órbita de
   modo que `d = b − a`. Transladando por −a e escalando por λ com `λd ∈ C`, obtém-se
   `{0, s1, s2}` com `s1 = λd`, logo `j1 = j*` pela P1. As outras duas diferenças são
   `s2 = λ(c − a)` e `s2 − s1 = λ(c − b)`, e as duas têm pc ≥ j*. O bloco de s2 é `H = hi(s2)`:
   - `pc(H) = pc(hi(s2)) ≥ j*`;
   - `pc(H − hi(s1)) = pc(hi(s2 − s1)) ≥ j*`, pela P2.

   O bloco **não** é pulado, e dentro dele s2 é avaliado com a mesma poda exata do exactT.
2. **Nenhum trio válido é eliminado.** Um par (s1, s2) só é pulado se uma das outras duas
   diferenças tem pc < `pc(hi(s1))`. Então `j* < pc(hi(s1))`, e a órbita é encontrada pela
   diferença mínima, como em (1). O que se descarta é uma **representação** da órbita, nunca a
   órbita.
3. **Duplicatas são só removidas.** O exactT2 ainda pode devolver mais de um par (s1, s2) da mesma
   órbita, nos empates em j*. A forma canônica as junta. A comparação é feita entre conjuntos de
   órbitas, com o valor de `orf` de cada uma; um valor divergente para a mesma órbita é tratado
   como erro.
4. **Empates e casos degenerados:**
   - **Empate no mínimo:** qualquer diferença com pc = j* serve, porque a regra exige só ≥.
   - **Trio colinear** (`c − a = μ(b − a)`): as três diferenças estão na mesma classe escalar, os
     três pc são iguais e (1) vale.
   - **Todas as diferenças com `hi = 0`:** `j* = 57`, o bloco é `H = 0`, `pc(0) = 57` e
     `H − hi(s1) = 0`, então o bloco não é pulado.
   - **`s2 ∈ {0, s1}`:** excluído, como no exactT, porque não forma trio.
   - **`q = 7` e `hi_d = 3` fixos:** `build_pcH` usa `hi_d` e q do Kit, e nada além.

- **Teste:**
  - classe 1 com T=30, exactT × exactT2(`sym=1`): **1992 = 1992 órbitas**, idênticas, com órfãs de
    6 a 30;
  - classe 1 com T=10 e T=8: idênticas;
  - teste diferencial estratificado (abaixo).

### 4. Subtração SWAR com bitset de 32 KB (q ≤ 7, r = 6)

- **Operação original:** `inB[kit_sub(x, s)]`.
- **Transformação:** cada dígito ocupa um byte; `c = a + q − b`; `c ← c − q·[c ≥ q]`. O resultado é
  compactado em 18 bits (3 por dígito) por deslocamentos e máscaras, que indexam um bitset de B.
- **Invariante:** cada byte de c fica em `[1, 2q−1] ⊂ [1, 13]` (sem empréstimo, porque a + q > b) e
  `c + (128 − q) ≤ 134 < 256` (sem vai-um). O bit 7 de cada byte vale 1 exatamente quando `c ≥ q`.
  Depois da correção, cada byte fica em `[0, q−1]`. Os dígitos são tratados de forma independente.
- **Equivalência:** dígito a dígito é `(a_i − b_i) mod q`. `idx18` é uma bijeção de `Z_7^6` em
  inteiros de 18 bits, e o bitset é montado a partir de `inB` em todo V; logo `INBP(c) = inB[c]`.
- **Teste:** `scripts/audit/test_swar.c`: **10.058.800 comparações com `kit_sub`, 0 divergências**
  (todos os 7×7 pares por posição de dígito, mais 10^7 pares aleatórios); `idx18` com **0
  colisões** nos 117.649 elementos.

### 5. Tabelas `uint16` e laço desenrolado

- **Equivalência:** `add16[i] = addlo[i] < 343` cabe em 16 bits, e o desenrolamento de 4 em 4 com
  resto faz a mesma sequência de incrementos.
- **Teste:** classes 1 e 3000, versões com e sem a mudança, mesma saída.

## Testes diferenciais

Três implementações: `exactT` (referência), `exactT2` (`sym=1`, SWAR) e
`scripts/audit/verify_trios.c`. Esta última **não** usa kit.h, blocos, simetria do trio nem SWAR:
tem bola, aritmética e canonização próprias.

- **Classe 1, T=10:** as três dão as mesmas 3 órbitas, todas com orf = 6.
- **Classe 1, T=30:** exactT = exactT2 nas mesmas 1992 órbitas.
- **Amostra estratificada com T=8:** 14 classes (|Bc| mínimo, posições 2, 3, 5, 10 e 50, Q25, mediana,
  Q75, máximo e 4 sorteadas com semente 20261002) → `docs/audit/differential.md`.
- **Conjuntos completos com T=30:** classe 1 feita (1992 órbitas iguais); as classes 2, 3 e 5 estão em andamento → `docs/audit/differential.md`.

## Proveniência da varredura (que binário avaliou cada classe)

| período (UTC) | onde | modo | código |
|---|---|---|---|
| 11:52–13:03 | VMs e2 (fz-01..03) | exactT, m=200, T=8 | `be52cc2` (o binário foi compilado no 1º lançamento de cada VM; uma VM lançada depois de 12:40 pode ter compilado `a44bed6`, mas o modo **exactT** é idêntico nos dois commits: o `a44bed6` só acrescenta o exactT2) |
| 13:03–13:35 | VMs e2 | exactT2, sym=1 | `75a844b` |
| 13:05–13:11 | contêiner local, 62 classes (L = 5363–5424) | exactT2, sym=1 | árvore em `75a844b` |
| 13:37– | VMs t2d (fz-01..03) | exactT2, sym=1, SWAR | `3c4ed99` |

Todas as variantes têm, pelas seções acima, a mesma saída. O registro por classe (`ledger`) traz o
período de cada arquivo. **Limite (red team):** a versão é deduzida pelo horário do arquivo; os `c_L.out` não trazem commit, mu, sym nem m. O `base_search.c` atual da factory-01 é idêntico ao `3c4ed99`, e o motor não mudou desde então. As cópias da VM para a factory-01 foram feitas com `rsync -a`, que preserva
o horário; os 62 arquivos locais estão listados à parte. A recontagem independente completa é o
passo de certificado proposto no relatório.
