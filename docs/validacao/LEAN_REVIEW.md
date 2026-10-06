# Revisão e recompilação de `Syn.K7_9_4_le_1137_syn`

- **Data:** 2026-10-02 (UTC), das 20:32 às 21:06
- **Repositório:** https://github.com/thiagopatzdorf/Matematica, clone novo, separado do checkout de trabalho
- **Commit:** `fcf0984d1b66e70bb6d3e2ad79cf22e077d5e89c`, que é o HEAD de `origin/main` no momento do clone ("audit: certificado computacional da varredura de bases de K_7(9,4) (#9)", 2026-10-02 12:39:50 -0300). A árvore de trabalho estava limpa. Única adição local: `tmpcheck/Axioms.lean`, não rastreado.
- **Resultado:** o build do zero passou, o teorema depende só de `[propext, Classical.choice, Quot.sound]` e a lista de palavras bate com o sha256 canônico. A seção 6 lista os pontos de atenção.

## 1. Respostas a–e

### a. Enunciado exato

`CoveringLean/Syn_K1137.lean:84-87`:

```lean
theorem K7_9_4_le_1137_syn :
    ∃ C : Finset (Fin 9 → ZMod 7), C.card = 1137 ∧ CoveringA2.Covers 4 C :=
  syn_cert PK1137 LK1137 rfl rfl rfl ⟨rfl, by decide⟩ VK1137 hTK1137 hOK1137 hBK1137
    (by decide +kernel) (by decide +kernel) (by decide +kernel)
```

O `#check` (logs/05_print_axioms.log) imprime `Syn.K7_9_4_le_1137_syn : ∃ C, C.card = 1137 ∧ CoveringA2.Covers 4 C`. O namespace `Syn` está declarado em `Syn_K1137.lean:21`.

O enunciado é existencial: existe um código de cardinalidade **exatamente** 1137 que cobre `(ZMod 7)^9` com raio 4. Isso implica K_7(9,4) ≤ 1137. Não há no Lean uma definição de `K_q(n,R)` como mínimo; a cota é a existência.

### b. Onde estão as 1137 palavras, em que formato, e como chegam ao `Finset`

O arquivo é `CoveringLean/SynData_K1137.lean`, e as palavras aparecem duas vezes:

- `def LK1137 : List Nat := [0, 4191, 7708, …]` (`SynData_K1137.lean:23`): 1137 naturais em ordem estritamente crescente.
- O campo `PN` da estrutura `PK1137 : Spec` (`:10-21`, com `PN` na linha 19): a mesma lista empacotada num único inteiro, com `b := 26` bits por entrada (`:20`) e `cnt := 1137` (`:21`). Os parâmetros do certificado estão em `:11-18`: `q=7, n=9, k=3, o=0, R=4`, o gerador `Gs` (`:16`), os representantes de coset `reps` (`:17`) e as síndromes órfãs `orphs` (`:18`).

**Codificação de uma palavra:** inteiro `w = Σ_i w_i·7^i`, com coordenada `i` igual ao dígito `i` em base 7 (little-endian). Isso foi confirmado no código em três pontos:

- `Syn.D q w i = w / q^i % q` (`SynCheck.lean:21`)
- `CoveringCerts.dig` (`C1_CoverCheck.lean:38-40`, `m % q :: dig q k (m / q)`)
- `CoveringCerts.word` (`C1_CoverCheck.lean:189-190`), que converte o índice `m` na função `Fin n → ZMod q` pelos dígitos `dig q n m`. `K3_Bridge.lean:19-35` (`getElem_dig`, `word_eq_wdf`) prova que as duas convenções coincidem.

**Ligação com o `Finset` do enunciado.** A ligação passa por `Syn.syn_cert` (`SynBridge.lean:339-354`):

- O código é `codeOf 7 9 LK1137 = (LK1137.map (word 7 9)).toFinset` (`C1_CoverCheck.lean:193`, usado em `SynBridge.lean:354`).
- **Cardinalidade exata:** `card_codeOf` (`C1_CoverCheck.lean:250-255`) exige que todo `m ∈ L` satisfaça `m < q^n` e que `L` seja `Pairwise (<)`. Daí sai `Nodup` da lista mapeada, via `word_inj` (`:243-248`), e `card = L.length`. A hipótese `hlen : L.length = M` dá 1137.
- **Sem duplicatas:** garantido pela ordem estritamente crescente. `strictlyInc` (`C1_CoverCheck.lean:262-264`) é checado por kernel e convertido em `Pairwise` por `pairwise_of_strictlyInc` (`:266-276`).
- **Os três `decide +kernel` finais** (`Syn_K1137.lean:87`) são as hipóteses `hU`, `hlen` e `hchk` de `syn_cert` (`SynBridge.lean:346-347`):
  - `hU`: `unpack 26 1137 PN = LK1137`, ou seja, a lista empacotada é idêntica à lista literal;
  - `hlen`: `LK1137.length = 1137`;
  - `hchk`: `LK1137.all (· < 7^9) && strictlyInc LK1137`.

### c. O Lean verifica cada palavra? Como `Covers` é definido?

**Definição.** `CoveringA2.Covers` está em `CoveringLean/A2_Sphere.lean:29-30` (a bola, `ball`, em `:25-26`):

```lean
def Covers (R : ℕ) (C : Finset (Fin n → ZMod q)) : Prop :=
  ∀ x : Fin n → ZMod q, ∃ c ∈ C, hammingDist x c ≤ R
```

A distância é `hammingDist` do Mathlib, o raio é `≤ R` com `R = 4`, e o espaço é `Fin 9 → ZMod 7` com `q = 7`, `n = 9` (`[NeZero q]`, `A2_Sphere.lean:22`). O `#print CoveringA2.Covers` no log 05 confirma a forma elaborada.

O kernel não percorre os 7^9 pontos. A cobertura é provada por um certificado de síndromes (`SynCheck.lean:1-16`, `SynBridge.lean:5-23`). O código tem a forma `C = ⋃_s (r_s + C0) ∪ P`, onde `C0 = {m·G}` é um `[9,3]_7` com `G` igual à identidade no bloco `[0,3)`. O kernel checa:

1. **`VK1137`** (`SynLeaf_K1137_9.lean:10`, `chkPiv PK1137 343`): `G` é a identidade no bloco de informação, para todo `a < 7^3`.
2. **`hTK1137`** (`Syn_K1137.lean:25-58`, folhas `TK1137_0…28`): cada um dos `7^6 = 117649` pontos `y_t` do transversal (zero no bloco) tem uma testemunha. A testemunha é uma palavra `r_s + m·G` a distância ≤ 4, com distância calculada coordenada a coordenada por `Syn.dist`, ou então `t` aparece em `orphs` (`okT`, `SynCheck.lean:75-80`). Os blocos têm 4096 pontos e são 29 (`29·4096 ≥ 117649`); a montagem é feita por `all_of_chunks` (`SynBridge.lean:324-335`).
3. **`hOK1137`** (`:60-69`): para cada um dos 6 órfãos e cada `a < 343`, o ponto `y_t + a·G` está a distância ≤ 4 de alguma palavra `L[j]` com `j < 1137` (2058 pontos, `okO`).
4. **`hBK1137`** (`:71-77`): para cada um dos 3 cosets e cada `m < 343`, a palavra `r_s + m·G` é igual a algum `L[j]` (`okB`), ou seja, os 3·343 = 1029 membros dos cosets estão em `L`.

`syn_cert` (`SynBridge.lean:339-432`) prova, dentro do Lean e com o Mathlib, que essas checagens implicam `Covers R (codeOf q n L)`. A prova escreve `x = y + c` com `c = a·G`, e então:

- se `t` tem testemunha `(s, m)`, `x` está a distância ≤ R de `r_s + (m ⊕ a)·G ∈ L`, usando `S_dsum` e a invariância por translação `hammingDist_sub_right`;
- se `t` é órfão, `x` é um dos pontos checados um a um.

A ponte entre a distância booleana e `hammingDist` é `hd_wdf` (`SynBridge.lean:317-319`), apoiada em `CoveringKernel.hd_eq` (`K2_Core.lean:40-60`).

Portanto, cada palavra de `L` é verificada quanto a intervalo e unicidade. A cobertura é provada para **todos** os `x` por um argumento formal que usa o certificado. A lista `L` é amarrada aos cosets e aos remendos pelas checagens `okB` e `okO`.

### d. Como a prova é fechada, e o grep por construções inseguras

Reflexão booleana com **`decide +kernel`**:

- as folhas `TK1137_*`, `OK1137_*`, `BK1137_*` e `VK1137` (`SynLeaf_K1137_*.lean`, 39 teoremas, todos `:= by decide +kernel`);
- os três `decide +kernel` de `Syn_K1137.lean:87`;
- um `decide` comum para `o + k ≤ n` (`:86`).

Os verificadores (`SynCheck.lean`) usam só `Nat.add/mul/div/mod/pow/beq/ble/blt/shiftRight`, que o kernel acelera com GMP. **Não há `native_decide`.** `Syn_K1137.lean:81` traz um teste de não-vacuidade: `okT PK1137 0 59 = false`.

O grep cobriu todos os `*.lean` do repositório, fora `.lake`:

| padrão | ocorrências em código |
|---|---|
| `sorry` | 0 (3 em comentários de doc: `A6_Finite.lean:7`, `SynBridge.lean:22`, `A5_Frontier.lean:28`) |
| `admit` | 0 |
| `axiom` | 0 |
| `unsafe` | 0 |
| `implemented_by` | 0 |
| `extern` | 0 |
| `@[csimp]` | 0 |
| `native_decide` | 0 (7 em comentários dizendo "sem native_decide") |
| `ofReduceBool`, `trustCompiler`, `debug.skipKernelTC`, `opaque` | 0 |
| `elab`/`macro`/`syntax`/`run_cmd`/`#eval`/`initialize`/`notation` | 0 |

Também foram conferidos:

- **`instance`:** 3 ocorrências, todas instâncias `Decidable` fora do cone desta prova (`A6_Finite.lean:32,37`, `A4_Closed.lean:25`).
- **`set_option`:** só `maxRecDepth 100000`, 5 vezes, uma em cada `Syn_K*.lean`.
- **Cone de importação** (só o que está no projeto): `A2_Sphere`, `K2_Loop`, `K2_Core`, `C1_CoverCheck`, `K3_Bridge`, `SynCheck`, `SynBridge`, `SynData_K1137`, `SynLeaf_K1137_0..9` e `Syn_K1137`, além do `Mathlib`.

### e. `#print axioms`

Arquivo `tmpcheck/Axioms.lean`, rodado com `lake env lean` (logs/05_print_axioms.log):

```
'Syn.K7_9_4_le_1137_syn' depends on axioms: [propext, Classical.choice, Quot.sound]
```

O `#print axioms` que fica no próprio arquivo (`Syn_K1137.lean:91`) imprimiu o mesmo durante o build (log 04). Esses são os três axiomas padrão do Lean/Mathlib, sem `Lean.ofReduceBool`, `sorryAx` ou axioma novo.

**Extra:** uma repetição independente pelo kernel (`leanchecker`, do toolchain) dos `.olean` dos 19 módulos do cone local terminou com exit 0 em todos. As folhas pesadas levaram de 81 a 172 s cada, o que é coerente com o kernel recomputando os `decide`. Log: `logs/06_leanchecker.log`. O Mathlib não foi repetido.

## 2. Build do zero

`/usr/bin/time` não existe na máquina. A medição foi feita por `scripts/measure.py`, que registra:

- tempo de parede;
- CPU via `getrusage(RUSAGE_CHILDREN)`;
- RSS máximo de um processo;
- soma de RSS da árvore de processos, amostrada a cada 1 s em `/proc`;
- número máximo de processos `lean` simultâneos.

O Lake 5.0.0 não tem flag `-j` e paraleliza pelo número de threads de hardware (4).

| passo | parede | CPU user/sys | RSS máx. de 1 processo | `lean` simultâneos | exit |
|---|---|---|---|---|---|
| `lake exe cache get` (1ª vez) | 6 min 47 s (clone do Mathlib + exe do cache) | n/d | n/d | n/d | 0 |
| `lake exe cache get` (de novo, ver 6.1) | 123 s | 104/93 s | 949 MB | 4 | 0 |
| `lake clean CoveringLean` | 1,6 s | n/d | n/d | 0 | 0 |
| `nice -n 10 lake build` (padrão, 8944 jobs; 20 módulos `CoveringLean` compilados, Mathlib do cache) | **285,5 s** | 318/125 s | **10,1 GB** | 4 | **0** |
| `nice -n 10 lake build CoveringLean.Syn_K1137` (8942 jobs; 12 módulos Syn compilados agora, 6 reaproveitados do passo anterior) | **318,0 s** | 486/175 s | **6,8 GB** | 4 | **0** |
| `lake env lean tmpcheck/Axioms.lean` | 10 s | n/d | 6,7 GB | 1 | 0 |
| `leanchecker` (19 módulos, `xargs -P 4`) | 5 min 13 s | n/d | n/d | 4 | 0 em todos |

Tempos por módulo de `Syn_K1137` (log 04):

| módulo | tempo |
|---|---|
| `SynLeaf_K1137_0` a `_6` | 127–156 s cada |
| `SynLeaf_K1137_7` | 23 s |
| `SynLeaf_K1137_8` | 6 s |
| `SynLeaf_K1137_9` | 4,5 s |
| `SynData` | 2 s |
| `Syn_K1137` | 23 s |

A soma de RSS da árvore chegou a 28,8 GB no build padrão, acima dos 15 GB físicos. Isso é sobrecontagem: cada processo `lean` mapeia em memória os mesmos `.olean` do Mathlib. Use o RSS de um processo como teto real por processo. Os builds só emitiram avisos de linter de estilo (linha longa, cabeçalho, `show`); nenhum erro.

**Logs** (resumo e versões em `verification/lean/`; logs completos não versionados):

- `build_summary.txt`: resumo da tentativa válida;
- `01_cache_get.log` e `01b_cache_get_again.log`;
- `02_lake_clean_root.log`;
- `03_lake_build_default.log`;
- `04_lake_build_syn1137.log`;
- `05_print_axioms.log`;
- `06_leanchecker.log`;
- `*.stats`: medições de cada passo;
- da primeira tentativa abortada: `02_lake_clean_ALLPKGS_mistake.log*`, `03_ABORTED_mathlib_rebuild.log` e `build_summary_attempt1.txt`.

**Scripts:** `verification/lean/` (o `decode_synData.py`; os demais eram auxiliares de build e não foram versionados):

- `run_build.sh`
- `measure.py`
- `run_leanchecker.sh`
- `decode_synData.py`
- `compare_toolchain.py`

## 3. Versões

Arquivo completo: `logs/versions.txt`.

- **Lean:** `Lean (version 4.34.1, x86_64-unknown-linux-gnu, commit 5045d0056413266e57c625dcd7c365b10e377c52, Release)`
- **Lake:** `Lake version 5.0.0-src+5045d00 (Lean version 4.34.1)`
- **elan:** 4.1.2 (58e8d545e 2025-05-26); `lean-toolchain` = `leanprover/lean4:v4.34.1`
- **Mathlib:** `d13f23b723b8a846827a245b89c10fc7d3f11612`, `inputRev v4.34.1`, conforme `lake-manifest.json`. O checkout em `.lake/packages/mathlib` está no mesmo commit.
- **SO:** `Linux vm 6.18.44-fc-v51 #1 SMP PREEMPT_DYNAMIC x86_64 GNU/Linux`, Ubuntu 24.04.4 LTS (noble); 4 núcleos, 16 GB, sem swap.
- **Repo:** `fcf0984d1b66e70bb6d3e2ad79cf22e077d5e89c`.

**Toolchain conferido bit a bit.** `~/.elan/toolchains/leanprover--lean4---v4.34.1` é um **symlink** para um diretório temporário da sessão, um diretório de scratchpad compartilhado. Por isso o pacote oficial `lean-4.34.1-linux.tar.zst` foi baixado do release do GitHub e comparado:

- sha256 `47bf4bbd78f70c2e9670598ab7124d92b6efb7330ff33e5fbb4030f6fd72e4e4`, idêntico ao tarball que estava em uso;
- os **17738 arquivos** instalados batem com o tarball, com 0 diferentes e 0 faltando (`logs/toolchain_sha.txt`).

## 4. Conferência da lista contra `data/codes/q7_n9_R4_M1137.txt`

O script `scripts/decode_synData.py` foi escrito do zero e não reusa `scripts/syndrome/*`. Ele lê o `.lean`, extrai `LK1137` e o `PN` e desempacota o `PN` com 26 bits por entrada, como `pget`/`unpack`. Depois gera as strings `w_0…w_8` (`dígito i = w // 7^i % 7`), ordena, junta com `\n` e calcula o sha256. Saída (`logs/04_decode.log`):

```
len(LK1137) = 1137
unpack(PN) == LK1137: True
sha256(canonical from .lean) = df3e8d527bc393a9680fe4b2b39e7bde088ab6a02f2f94ee26019a5efc05a102
sha256(data/codes/q7_n9_R4_M1137.txt) = df3e8d527bc393a9680fe4b2b39e7bde088ab6a02f2f94ee26019a5efc05a102
canonical == file bytes: True
matches expected: True
ball size = 182791
points covered: 40353607 of 40353607
OK
```

Além disso, o script confere:

- `LK1137` está em ordem estritamente crescente, não tem duplicatas e tem todos os valores `< 7^9`;
- `PN` não tem bits além das 1137 entradas.

A forma canônica gerada a partir do `.lean` é **byte a byte igual** ao arquivo de dados, e os dois têm o sha256 esperado. A codificação foi confirmada no código (item b). Exemplos: a linha `000000056` do arquivo corresponde a `w = 5·7^7 + 6·7^8 = 38706521`, que está em `LK1137`; o segundo elemento de `LK1137`, `4191`, corresponde à string `531510000`, que é a linha 891 do arquivo. A ordem do arquivo é a das strings, não a dos inteiros.

**Extra (`--cover`):** uma checagem de cobertura por força bruta, independente do Lean, foi feita com numpy. Ela marca as bolas de raio 4 (182791 pontos cada) das 1137 palavras e confirma que todos os **40353607 = 7^9** pontos ficam cobertos.

## 5. Conclusão

- **Enunciado:** `∃ C : Finset (Fin 9 → ZMod 7), C.card = 1137 ∧ CoveringA2.Covers 4 C`, com `Covers R C := ∀ x, ∃ c ∈ C, hammingDist x c ≤ R`.
- **Axiomas:** `[propext, Classical.choice, Quot.sound]`.
- **Build do zero:** passou. Projeto compilado do zero sobre o cache do Mathlib, `lake build` em 285 s e `lake build CoveringLean.Syn_K1137` em 318 s, exit 0. Pico de 10,1 GB num processo no build padrão e 6,8 GB no alvo Syn; 4 jobs.
- **Repetição pelo `leanchecker`:** ok.
- **Lista:** decodifica exatamente para `q7_n9_R4_M1137.txt`, sha256 `df3e8d52…a102`. A cobertura de raio 4 também foi confirmada por força bruta fora do Lean.

## 6. Pontos de atenção

1. **`lake clean` sem argumento apaga o build de todos os pacotes, inclusive o Mathlib** (`lake help clean`). Seguir a receita literal ("cache get, depois lake clean, depois lake build") recompila o Mathlib inteiro do fonte, o que levaria horas em 4 núcleos. Isso aconteceu na primeira tentativa, que foi abortada e está registrada em `build_summary_attempt1.txt`. A forma correta é `lake exe cache get && lake clean CoveringLean`, que limpa só o pacote raiz.
2. **`Syn_K1137` não está no alvo padrão.** Ele pertence à lib `CoveringSyn` (`lakefile.toml`), então `lake build` sozinho **não** verifica este teorema. É preciso `lake build CoveringLean.Syn_K1137` ou `lake build CoveringSyn`. Isso está documentado no `lakefile`, mas convém deixar explícito em qualquer texto que diga "compila com `lake build`".
3. **O toolchain do elan aponta para um diretório de scratchpad compartilhado**, não para uma instalação do elan. Ele foi conferido contra o release oficial e é idêntico, mas é frágil: se o scratchpad for limpo, o toolchain some.
4. **O cache do Mathlib já existia em `~/.cache/mathlib`.** O `cache get` não baixou nada; só descompactou 8907 arquivos, que o próprio cache confere por hash. Num ambiente realmente limpo, ele baixaria.
5. **Havia outros jobs rodando na máquina durante o build:** outra sessão compilando `SynLeaf_K1137_*` num diretório temporário, além de `verify_balls.py` e `run_mutations.py`. Os tempos são, portanto, um teto pessimista e têm ruído.
6. **Nada de suspeito na prova.** O teorema é existencial (não há definição formal de `K_q(n,R)`), mas é exatamente o que "K_7(9,4) ≤ 1137" significa. O código tem cardinalidade exata, e não apenas `≤`. A confiança está no kernel do Lean, incluindo a aceleração GMP de operações de `Nat`, que faz parte do kernel padrão, e no Mathlib.
