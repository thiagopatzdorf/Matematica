# Formato estruturado de código de cobertura (`covering-code/v1`) e verificador oficial

Um código de cobertura `C ⊆ Z_q^n` com raio `R` e `|C| = M` mora em dois lugares:

* `data/codes/q<q>_n<n>_R<R>_M<M>.txt`: a lista plana, uma palavra por linha. É o que os
  teoremas Lean (`C1_Data_*.lean`) decodificam.
* `data/structured/q<q>_n<n>_R<R>_M<M>.json`: a mesma lista descrita pela estrutura dela
  (cosets de um código linear, cosets de subcódigos, palavras soltas) e com a proveniência.

A ligação entre os dois é o **sha256 canônico**, conferido por teste: `expand(json)` tem de dar
exatamente o sha256 canônico do `.txt`.

## Convenções

**Dígitos.** Uma palavra é um texto `s = s[0] s[1] … s[n-1]` com um caractere `'0'..'9'` por
coordenada (q ≤ 10). Como inteiro, `w = Σ_k s[k]·q^k` (little-endian): o dígito `k` é
`(w // q^k) % q`. É a codificação das listas `C1_Data_*.lean`.

**Forma canônica.** As palavras como texto, ordenadas por byte, unidas por LF, com LF final.
Para comprimento fixo, a ordem por byte é a ordem do inteiro lido com `s[0]` como dígito **mais**
significativo (não é a ordem de `w`). `canonical_sha256` é o sha256 desses bytes; não depende da
ordem nem da quebra de linha do `.txt`, por isso os `.txt` não precisam estar ordenados.

**Grupo.** Por padrão a soma é coordenada a coordenada mod `q` (`"group": "Zq"`; para `q` primo é
`GF(q)^n`). Para `q = 2^m`, `"group": "xor"` lê cada dígito como vetor de `m` bits e soma por
ou-exclusivo (a soma de `GF(2^m)`); é o caso do `K_4(10,4) ≤ 192`, que não tem estrutura em `Z_4`.

## Esquema

```json
{
 "format": "covering-code/v1",
 "q": 7, "n": 9, "R": 4, "M": 1285,
 "digit_convention": "word text s[0]..s[n-1]; integer w = sum_k s[k]*q^k; digit k = (w // q^k) % q",
 "group": "Zq",                                   // opcional; "Zq" (padrão) ou "xor"
 "linear_base": {                                 // opcional; só q primo e group Zq
  "k": 3,
  "generator":    ["165653100", "242340010", "551665001"],   // G, k linhas, sistemática
  "info_columns": [6, 7, 8],                                  // G restrita a elas = identidade
  "parity_check": ["100000652", "010000132", "001000256",
                   "000100141", "000010231", "000001402"],    // H, n-k linhas, H G^T = 0
  "check_columns": [0, 1, 2, 3, 4, 5],                        // H restrita a elas = identidade
  "coset_syndromes": ["000000", "363122", "414655"],          // síndromes s = H x (texto, n-k dígitos)
  "coset_reps": []                                            // opcional: representantes explícitos
 },
 "subcode_cosets": [                              // zero ou mais blocos
  {"generators": ["165653100"], "reps": ["002113056", "003023345", "..."]}
 ],
 "patch_words": ["065405511", "110541111", "126162510", "421333411"],
 "provenance": {"generator": "...", "commit": null, "seed": null, "command": "...",
                "date": "2026-10-02", "agent": "James.V1", "repo_commit": null, "notes": "..."},
 "canonical_sha256": "aa388cc9642bc064527a0237b60522ba558491291a2adf02ab1e4d8d3f756c1f"
}
```

### Semântica (o que `scripts/codes/expand.py` faz)

1. `linear_base`: `L = {u·G : u ∈ GF(q)^k}`. Para cada síndrome `s`, o representante é o vetor
   `r` com `r[check_columns[i]] = s[i]` e zero no resto (então `H r = s`, porque `H` é identidade
   nas colunas de checagem); o bloco é `r + L`. Cada `coset_reps[j]` também dá `coset_reps[j] + L`.
2. Cada bloco de `subcode_cosets`: `S = ` subgrupo gerado por `generators` (para `q` primo, o
   subespaço gerado); para cada `rep`, o bloco é `rep + S`. Os geradores não precisam estar em `L`.
3. `patch_words`: palavras literais.
4. A união tem de ser **disjunta** (palavra gerada duas vezes é erro) e ter exatamente `M`
   palavras. `expand` confere ainda `H G^T = 0`, as identidades em `info_columns`/`check_columns`
   e `rank G = k`, e por fim o `canonical_sha256`.

Com pivôs escolhidos da direita para a esquerda, `H` sai na forma `[I_{n-k} | A]` sempre que as
últimas `k` colunas são um conjunto de informação. É o caso de todos os nossos códigos, e é a
mesma `A` do gerador do 1285 (`scripts/search/gen.py`, `"A": "652 132 256 141 231 402"`).

### Para o certificado Lean por síndromes

O bloco `linear_base` foi desenhado para isso: um certificado pode provar `H G^T = 0` uma vez e
então representar os `c` cosets por `c` síndromes de `n-k` dígitos, em vez de `c·q^k` palavras.
Os campos que o certificado precisa são `parity_check`, `check_columns` e `coset_syndromes`; o
resto (`subcode_cosets`, `patch_words`) é lista explícita ou subespaço pequeno.

## Os códigos de `data/codes`

| célula | estrutura (gerada por `structure.py`) | sha256 canônico |
|---|---|---|
| `K_7(9,4) ≤ 1351` | 3 cosets de `[9,3]_7` + 46 cosets de uma reta `[9,1]_7` | `54dbdade…` |
| `K_7(9,4) ≤ 1285` | 3 cosets de outro `[9,3]_7` + 36 cosets de uma reta + 4 palavras | `aa388cc9…` |
| `K_7(8,3) ≤ 1887` | 5 cosets de `[8,3]_7` + 172 palavras | `98531afb…` |
| `K_7(8,3) ≤ 1893` | os mesmos 5 cosets de `[8,3]_7` + 178 palavras | `7c276cf1…` |
| `K_5(10,4) ≤ 625` | 1 coset (o próprio código linear `[10,4]_5`) | `9e686671…` |
| `K_5(9,3) ≤ 1250` | 2 cosets de `[9,4]_5` | `ee623546…` |
| `K_5(7,2) ≤ 500` | 4 cosets de `[7,3]_5` | `5bebf8d2…` |
| `K_5(9,4) ≤ 250` | 2 cosets de `[9,3]_5` | `b818a971…` |
| `K_5(9,5) ≤ 50` | 2 cosets de `[9,2]_5` | `6125e06c…` |
| `K_4(10,4) ≤ 192` | `group: xor`: 1 coset de um subgrupo de ordem `2^7` + 1 de ordem `2^6` | `907b0f19…` |

Achado ao estruturar: as 322 palavras de "remendo guloso" do 1351, cuja origem não ficou
registrada, são 46 cosets de uma reta — o código inteiro é união de cosets de `<111111111>`.

O 1285 também se descreve como "3 cosets de `[9,3]` + 3 cosets de um `[9,2]` + 15 retas + 4"
(é o que `structure.py` acha sozinho, maior dimensão primeiro). O JSON versionado usa
`--dims 3,1`, que reproduz a descrição do gerador (36 retas). As duas expandem para o mesmo código.

## Ferramentas

| comando | o que faz |
|---|---|
| `python3 scripts/codes/expand.py X.json [-o X.txt]` | JSON → forma canônica; falha se o sha256 não bater |
| `python3 scripts/codes/structure.py X.txt [--dims 3,1] [--provenance p.json]` | lista → JSON (detecta cosets) |
| `python3 scripts/codes/build_structured.py [--check]` | regenera (ou confere) todo `data/structured/` com a proveniência registrada nele |
| `tools/verify/check_all.sh` | verificador oficial em todo `data/codes` e em todo JSON expandido |
| `python3 -m unittest discover -s tests -v` | testes do formato e do verificador |

Só biblioteca padrão do Python 3 e um compilador C.

## Verificador oficial (`tools/verify/verify.c`)

C99, sem dependências (usa `__builtin_popcountll`/`__builtin_ctzll`, presentes em gcc e clang).

```
cc -O2 -std=c99 -o tools/verify/verify tools/verify/verify.c
tools/verify/verify data/codes/q7_n9_R4_M1351.txt
python3 scripts/codes/expand.py data/structured/q7_n9_R4_M1351.json | tools/verify/verify -q 7 -n 9 -r 4 -m 1351 -
```

Confere dígito `< q`, comprimento `n`, ausência de duplicata e `|C| = M`; marca num bitset de
`q^n` bits a bola de raio `R` de cada palavra (busca em profundidade com a tabela
`delta[p][a][v] = ((a+v) mod q − a)·q^p` pré-computada) e conta os descobertos. Imprime
`q= n= R= M= points= uncovered= sha256=` (e `first_uncovered=` se houver). Saída: `0` cobre,
`1` há ponto descoberto, `2` entrada inválida.

Tempo medido (2026-10-02, container de 4 vCPU, `-O2`): `K_7(9,4)`, 40 353 607 pontos e
1351 × 182 791 marcações, **1,1 s de CPU** (2,6 s de relógio numa máquina compartilhada);
`check_all.sh` inteiro, 10 códigos + 10 JSON: 6,4 s de CPU.

## CI

`.github/workflows/verify-codes.yml` roda em todo push/PR que toque `data/`, `tools/`,
`scripts/codes/`, `scripts/search/`, `tests/` ou a biblioteca Lean:

* job `verify`: compila o verificador com `-Werror`, roda `check_all.sh` e os testes;
* job `lean`: `leanprover/lean-action` com o cache do Mathlib (`lake exe cache get`) e
  `lake build` do alvo padrão (`CoveringLean`; na VM, 32 s e 7,7 GB de pico). `CoveringHeavy`
  (~12 h de CPU) fica fora. Este job não foi rodado neste container (não há Lean aqui); a primeira
  execução no GitHub é a medida. Se estourar memória ou tempo no runner hospedado, a saída é
  tirar o job e deixar só o verificador, registrando aqui o número que estourou.
