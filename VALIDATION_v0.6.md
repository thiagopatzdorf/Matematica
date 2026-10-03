# Validação v0.6: K_7(9,4) ≤ 1134, K_5(10,5) ≤ 162, K_5(11,4) ≤ 2875, K_7(10,4) ≤ 5616

Data: 2026-10-03. Branch `feat/v0.6`, que junta `feat/k794-1134`, `origin/feat/ataque-celulas-2011` e
`origin/main` (merges sem rebase e sem conflito). Toolchain: Lean 4.34.1 e Mathlib `v4.34.1`, os
mesmos do `lake-manifest.json`. Máquina: contêiner com 4 vCPU (Xeon 2,1 GHz) e 15 GB de RAM.

O padrão é o da v0.5 (`VALIDATION.md` e `LEAN_RED_TEAM.md`, feitos para o 1137): um teorema Lean
por célula, verificadores independentes sobre todo o espaço e mutações que **têm de falhar**.
O red team da v0.6 está em `LEAN_RED_TEAM.md`, seção "v0.6".

## Teoremas

| célula | declaração | enunciado (conferido por `example … := teorema`) | código (`data/codes/`) |
|---|---|---|---|
| K7(9,4) | `Syn.K7_9_4_le_1134_syn` | `∃ C : Finset (Fin 9 → ZMod 7), C.card = 1134 ∧ CoveringA2.Covers 4 C` | `q7_n9_R4_M1134.txt` |
| K5(10,5) | `Syn.K5_10_5_le_162_syn` | `∃ C : Finset (Fin 10 → ZMod 5), C.card = 162 ∧ CoveringA2.Covers 5 C` | `q5_n10_R5_M162.txt` |
| K5(11,4) | `Syn.K5_11_4_le_2875_syn` | `∃ C : Finset (Fin 11 → ZMod 5), C.card = 2875 ∧ CoveringA2.Covers 4 C` | `q5_n11_R4_M2875.txt` |
| K7(10,4) | `Syn.K7_10_4_le_5616_syn` | `∃ C : Finset (Fin 10 → ZMod 7), C.card = 5616 ∧ CoveringA2.Covers 4 C` | `q7_n10_R4_M5616.txt` |

`CoveringA2.Covers R C` é, por definição (`A2_Sphere.lean:29`), `∀ x : Fin n → ZMod q, ∃ c ∈ C,
hammingDist x c ≤ R`, com o `hammingDist` do Mathlib. O arquivo de checagem
(`verification/outputs/v0.6/Stmt.lean.txt`) prova isso por `Iff.rfl` e prova cada enunciado
acima com o tipo escrito por extenso. A saída dele está em `verification/outputs/v0.6/lean_statements.txt`.

Axiomas dos quatro teoremas (`#print axioms`): `[propext, Classical.choice, Quot.sound]`. Nos
arquivos do certificado e em `SynCheck`/`SynBridge` não aparece nenhum `sorry`, `admit`,
`native_decide`, `axiom`, `implemented_by`, `extern`, `unsafe`, `ofReduceBool`, `#eval`,
`run_cmd` ou `include_str` (os únicos casos estão num comentário de `SynBridge.lean:22`). Os únicos
`set_option` são `maxRecDepth 100000`, um limite do elaborador que não afrouxa o kernel.

## Certificados (gerados por `scripts/syndrome/gen_syn.py`)

Mesmo gerador e mesma ponte (`SynBridge.syn_cert`) do 1137. Comando:
`python3 scripts/syndrome/gen_syn.py data/structured/<json> <TAG>`. O gerador confere sozinho o
`canonical_sha256` do JSON.

| TAG | base `C0` | classes laterais | remendo | síndromes órfãs | folhas / arquivos | tamanho dos .lean |
|---|---|---|---|---|---|---|
| K1134 | [9,3]_7 | 3 | 105 | 6 (2058 pontos) | 39 / 10 | 0,43 MB |
| K162 | [10,3]_5 | 1 | 37 | 8 (1000 pontos) | 30 / 8 | 0,18 MB |
| K2875 | [11,3]_5 | 23 | 0 | 0 | 120 / 30 | 1,5 MB |
| K5616 | [10,3]_7 | 16 | 128 | 3 (1029 pontos) | 222 / 56 | 3,4 MB |

O gerador não assumia q = 7 nem n = 9. Só faltava uma coisa, achada no primeiro build do K2875: o
literal `LK2875` (2875 elementos) estoura o `maxRecDepth` padrão na elaboração de `SynData`. O
gerador agora emite `set_option maxRecDepth 100000 in` antes da lista quando M > 2048. Abaixo desse
limiar nada muda, e os certificados antigos continuam saindo byte a byte iguais (conferido no K1134:
os 12 arquivos regenerados são idênticos aos commitados). Os testes estão em `tests/test_gen_syn.py`:
reprodução byte a byte do K162 (q = 5, n = 10), lista de 2080 palavras com o `set_option`, e K1887
sem ele.

### Build (`lake build CoveringLean.Syn_<TAG>`)

Os módulos próprios de cada certificado (`SynData`, folhas, montagem) foram compilados do zero, com
os `.olean`/`.ir` apagados antes. Os módulos comuns (Mathlib, `SynCheck`, `SynBridge`) vieram do
cache. Os quatro somam ~20 min de parede (1224 s).

| TAG | exit | tempo de parede (4 núcleos) | folha mais lenta | observação |
|---|---|---|---|---|
| K1134 | 0 | 105 s | | os artefatos do K1134 (96 arquivos em `.lake/build`) apagados antes e recompilados |
| K162 | 0 | 101 s | ~55 s | recompilação limpa com a máquina ociosa. A 1ª compilação levou 460 s, 211 s deles na montagem (carga fria da Mathlib, 1º build após o merge) |
| K2875 | 0 | 364 s | 64 s | 1ª tentativa: exit 1 em `SynData_K2875` (maxRecDepth), corrigida no gerador. O build que valeu foi o primeiro das folhas, nenhuma tinha sido compilada antes |
| K5616 | 0 | 654 s | 53 s | recompilação limpa com a máquina ociosa. A 1ª compilação levou 887 s, concorrendo com as mutações (`nice 19`); folha mais lenta 76 s |

Disco: `.lake/build` do projeto ficou em ~80 MB. O disco livre não saiu de 16 GB e nenhum build
chegou perto do teto de 10 GB. Memória: não medi o pico por processo. Uma leitura de `free -g` no
meio do build do K5616, com 4 folhas em paralelo, deu 4 GB usados de 15.

## Verificação independente (todo o espaço)

Cada código passou por cinco programas, mais o `check_all.sh`. As saídas estão em
`verification/outputs/v0.6/` e o resumo em `verifiers_summary.txt`.

| programa | método | K1134 | K162 | K2875 | K5616 |
|---|---|---|---|---|---|
| `tools/verify/verify` (C, oficial) | bitset das bolas | 0 descob., 0,4 s | 0, 0,1 s | 0, 0,5 s | 0, 4,4 s |
| `scripts/loop/verify_cover.py` | dilatação de Hamming (numpy) | ok, 4,0 s | ok, 0,9 s | ok, 4,6 s | ok, 48 s |
| `scripts/search/verify.py` | R dilatações por `np.roll` | VALID | VALID | VALID | VALID |
| `scripts/attack/verify_bfs.c` | BFS multifonte | COBRE | COBRE | COBRE | COBRE |
| `verification/verify_bfs/main.rs` (verificador C da v0.5) | BFS multifonte | PASS | PASS | PASS | PASS |
| `verification/lean/decode_synData.py --tag T --cover` | lista do `.lean` = arquivo; bolas por `itertools` | OK | OK | OK | OK |
| `tools/verify/check_all.sh` | os 16 códigos + expand dos JSON | 16 códigos, 0 descobertos | | | |

O `main.rs` tem q = 7, n = 9 e R = 4 fixos no código. Para as outras células ele foi compilado em
cópia, com as constantes trocadas por `sed`: `Q`, `N`, `SPACE`, a faixa de dígitos e, no K162,
`skip(6)`/`maxd <= 5`/`R = 5`. O arquivo do repositório não foi alterado. O `decode_synData.py`
foi generalizado com `--tag`; sem a opção, o comportamento é o da v0.5 (K1137).

Distribuição de distâncias. Os dois BFS dão números idênticos:

| | N_0 | N_1 | N_2 | N_3 | N_4 | N_5 | total |
|---|---|---|---|---|---|---|---|
| K1134 | 1 134 | 61 040 | 1 417 073 | 15 311 828 | 23 562 532 | | 40 353 607 = 7^9 |
| K162 | 162 | 6 480 | 116 454 | 1 187 157 | 5 570 563 | 2 884 809 | 9 765 625 = 5^10 |
| K2875 | 2 875 | 126 500 | 2 506 750 | 23 621 625 | 22 570 375 | | 48 828 125 = 5^11 |
| K5616 | 5 616 | 336 958 | 9 036 210 | 119 779 085 | 153 317 380 | | 282 475 249 = 7^10 |

### sha256

| célula | sha256 canônico (palavras ordenadas, LF) | sha256 dos bytes do `.txt` |
|---|---|---|
| K7(9,4) ≤ 1134 | `a48e3a42922616b3466a5fafbfaa0e4098a77f675841df3129ac96bbcb8b7b41` | igual (o arquivo já está em forma canônica) |
| K5(10,5) ≤ 162 | `74176af64936119ce0d199e487127dff999888f93c7bde0b8386ba03ece12ce5` | `6f8d8baa3b47d1998e2d13ad6d87188aaf6cc4bb3eb361fdea9f162718c3cd38` |
| K5(11,4) ≤ 2875 | `2a700e2f928a8d893e8863ee100c9514a8ffd65a480776682c7560c96029dc9b` | `e8ff1f41662ffc314686ea40241dbafcaac022acdb953f3d9e4ffc0b394cabe9` |
| K7(10,4) ≤ 5616 | `750cae3ba3ded64eef208548f6e3c8fe0356c0b599ab3f605aac6fd175a78a5e` | `bfa4f489c610aedaa9208736a5bb3cdf5a17b116d4fd83c516835493f4f4f0a7` |

Os três `.txt` do ataque não estão em ordem canônica. O sha canônico é o do `canonical_sha256` do
JSON, o do `verify` e o do comentário do `SynData`, e é o que o `decode_synData.py` compara. O
ledger guarda o sha dos bytes do arquivo, como nas entradas antigas; o teste do ledger confere esse.

## Mutações destrutivas (Lean)

Script: `verification/lean/run_mutations_syn.sh TAG DIR [--full]`. Ele gera as mutações com
`mutate_syn.py`, em cópias com tag nova numa pasta à parte, e compila cada módulo adulterado com
`lake env lean --root=DIR`. O `lakefile.toml` e o `CoveringLean/` não são tocados. Antes de
tudo, um **controle positivo** (a folha 0 original com outro nome) tem de compilar. Só conta como
rejeição um erro do Lean com posição no arquivo adulterado.

Esse cuidado veio de um erro real desta rodada. A primeira versão do script contava qualquer falha
como rejeição, e um `lake: command not found` saiu como "8/8 mutações rejeitadas". Uma segunda
versão quebrou a resolução de módulos, e só o controle positivo pegou.

| mutação | o que muda | K1134 | K162 (`--full`) | K2875 | K5616 |
|---|---|---|---|---|---|
| M1 troca | `L[0]` → palavra nova (L continua crescente, `PN` coerente), que deixa N pontos descobertos | N = 378; rejeitada em `BK1134M1_0` | N = 160; rejeitada em `BK162M1_0` (as 7 folhas anteriores passam) | N = 55; rejeitada em `BK2875M1_5` | N = 111; rejeitada em `BK5616M1_0` |
| M2a remoção, card | tira `L[0]`; o teorema ainda diz M | `decide (L.length = 1134)`: kernel type mismatch | idem (162) | idem (2875) | idem (5616) |
| M2b remoção, cobertura | tira `L[0]`, enunciado com M−1 | rejeitada em `OK1134M2_0` | rejeitada em `OK162M2_0` | rejeitada em `BK2875M2_0` | rejeitada em `OK5616M2_0` |
| M3 tabela | testemunha do ponto t = 0 na folha `T…_0` → `negW` (distância > R) | rejeitada em `TK1134M3_0` | `TK162M3_0` | `TK2875M3_0` | `TK5616M3_0` |
| controle | folha 0 original, renomeada | compila | compila | compila | compila |

Em todas as rejeições de folha, a mensagem é "Tactic `decide` proved that the proposition … is
false". A da M2a é "(kernel) application type mismatch". As saídas completas estão em
`verification/outputs/v0.6/mutations_<TAG>.txt` e os planos (índice, palavra velha e nova, pontos
descobertos) em `mutations_<TAG>_plan.json`. Os pontos descobertos de cada mutação foram contados
pelo `tools/verify/verify`. No K162 o certificado adulterado inteiro foi montado (`--full`). Nos
outros só as folhas atingidas foram compiladas, porque a montagem importa todas as folhas e não
compila sem a que falhou.

## Testes do repositório

`python3 -m pytest -q tests`: **63 passed**. Foi preciso consertar o seguinte por causa dos dados
novos, sem afrouxar nenhum teste:

- `build_structured.py --check` acusava `DIFERE` no JSON do 1134, um defeito que já vinha da branch
  `feat/k794-1134`. O JSON commitado guardava o remendo fora de ordem e sem registro de proveniência
  no `build_structured.py`. Entrou o registro (com `dims: [3]`, que mantém as 105 palavras soltas) e
  o JSON foi regenerado. As palavras e o sha canônico são os mesmos, e o certificado Lean regenerado
  dele sai byte a byte igual.
- A fixture das fontes (`tests/fixtures/fontes`) ganhou K5(10,5) e K5(11,4). O `recortar_fontes.py`
  foi rodado de novo a partir do cache do `build.py` nos commits fixados, e o diff só tem acréscimos.
- `test_ledger`: 9 → 12 células nossas; o melhor de K7(9,4) passa a 1134. O exemplo de célula
  "que ninguém atacou desde 2011" era K7(10,4), que agora é nossa. Passou a ser K6(9,3), e o teste
  ganhou a asserção de que K7(10,4) é camada 2.
- `test_publish`: a página mostra 12 cotas Lean, com as três declarações novas e ≤ 5616.

## NÃO provado

- Otimalidade de qualquer uma das quatro cotas e cota inferior nova.
- Que o remendo de 105 palavras (1134), o de 37 (162) ou o de 128 (5616) seja mínimo.
- O CI continua sem compilar `CoveringSyn` (achado de processo da v0.5, ainda aberto): os quatro
  teoremas dependem de build manual.
