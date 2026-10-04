# K_7(4,2) = 19 no Lean 4 (2026-10-04)

Lean 4.34.1 + Mathlib v4.34.1. Regras: checado pelo kernel, sem `sorry`, sem `native_decide`,
sem `ofReduceBool`/`implemented_by`; todo `#print axioms` dá no máximo
`[propext, Classical.choice, Quot.sound]`. Contexto: `docs/exatos/FASE1_B_K742.md` (o
resultado computacional), `tools/exatos/k742/README.md` (a prova escrita) e
`docs/exatos/REDTEAM_K742.md`.

## Resumo: o que é teorema e o que ainda é computação

| afirmação | estado | declaração |
|---|---|---|
| K_7(4,2) ≤ 19 | **teorema** | `K742.K_7_4_2_le_19` |
| Lema 0 (caixas de comprimento 3), `K_6(3,1) ≥ 18` e `K_7(3,1) ≥ 21` na forma de caixa | **teorema** | `K742.box_fiber_bound`, `K742.box_card_ge_18`, `K742.box_card_ge_21` |
| Lema 1: com M ≤ 18, toda fibra tem ≥ 2 palavras | **teorema** | `K742.fiber_card_ge_two` |
| redução código → perfil (cada coordenada tem um dos 5 tipos; o multiconjunto é um dos 70 perfis) | **teorema** | `K742.fiberType_mem_types18`, `K742.profile_mem_profiles18`, `K742.profiles18_card`, `K742.perfis18_complete` |
| a CNF de cada perfil, igual à de `encode.py` | **definição** no Lean (`K742Cnf.cnf`), conferida contra o DIMACS **pelo kernel** a cada refutação | `K742Cnf.cnf`, `K742Cnf.cnfSemQuebra` |
| verificador LRAT executado pelo kernel, com prova de correção | **teorema** | `LratK.unsat_of_good`, `LratK.good_of_checkRange`, `LratK.rup_sound`; comando `lratk_refute` |
| K_7(4,2) = 19 **a partir de** `Ponte18 G` e `Refut18 G` | **teorema** (condicional) | `K742.K_7_4_2_eq_19_of` |
| `Refut18`: as 70 CNFs de M = 18 são insatisfatíveis | **1 de 70 no kernel** (perfil 64, o menor); os outros 69 têm prova LRAT conferida fora do Lean | `K742Sat.refut18_p64` (lib `CoveringK742Sat`, fora do alvo padrão) |
| `Ponte18`: todo código de 18 palavras satisfaz a CNF de algum perfil | **não formalizado** (forma normal do `canonizar.py`; argumento no README, testado por máquina) | — |
| teste de ponta a ponta do verificador: as 5 CNFs de K_4(4,2), M = 6 | **teorema**, no alvo padrão | `LratK_K4.refut6` |

Ou seja: K_7(4,2) = 19 **ainda não é teorema do Lean**. É teorema condicionado a duas
proposições fechadas, cada uma enunciada no Lean sobre objetos do Lean; uma delas
(`Refut18`) é pura computação, já com o caminho de execução pronto e medido.

## Arquivos

| arquivo | conteúdo | alvo |
|---|---|---|
| `CoveringLean/K742_Upper.lean` | código da partição 1+3+3 (19 palavras), cobertura por `decide +kernel` nos 2401 pontos | padrão |
| `CoveringLean/K742_Fibras.lean` | Lema 0, Lema 1, tipos e perfis | padrão |
| `CoveringLean/K742_Cnf.lean` | `encode.py` reescrito no Lean (`cnf`, `cnfSemQuebra`) e a lista `perfis18` | padrão |
| `CoveringLean/K742_Final.lean` | `Ponte18`, `Refut18`, `K_7_4_2_eq_19_of`, `perfis18_complete` | padrão |
| `CoveringLean/LratK.lean` | o verificador LRAT e a prova de correção (só Lean core, sem Mathlib) | padrão |
| `CoveringLean/LratKData.lean` | `lratk_refute`: lê CNF + LRAT, monta dados e teoremas por bloco | padrão |
| `CoveringLean/LratK_K4.lean` + `LratK_K4/` | as 5 refutações de K_4(4,2), M = 6 (dados no git, 270 KB) | padrão |
| `CoveringLean/K742Sat/P64.lean` | perfil 64 de K_7(4,2), M = 18 (dados fora do git) | `CoveringK742Sat` |
| `tools/exatos/k742/lean/gerar_dados.py` | gera CNF + LRAT aparado de um perfil e confere o sha256 com `manifesto.json` | — |
| `tools/exatos/k742/lean/aparo_M18*.jsonl` | medições do aparo das 70 provas (com e sem (d)–(f)) | — |
| `tests/test_lean_k742.py` | `perfis18`/`perfis6` do Lean = `encode.perfis`, sha256 dos dados, nada de atalho fora do kernel | pytest |

## 1. Cota superior

`code19` = `0000` + tetracódigo `(a, b, a+b, a+2b)` sobre {1,2,3} e sobre {4,5,6}.
`code19_card` e `code19_covers_vec` saem por `decide +kernel` direto (2401 pontos × 19
palavras, ~50 s de CPU); `code19_covers` passa do vetor `![a,b,c,d]` para `Fin 4 → ZMod 7`.
O espaço é pequeno o bastante para não precisar do certificado por prefixos/síndromes.

## 2. Lemas 0 e 1 e os perfis

* **Lema 0, forma geral** (`box_fiber_bound`): `D` cobre com raio 1 a caixa
  `S 0 × S 1 × S 2` (as palavras de `D` podem estar fora dela), `|S i| ≥ v`; para `a ∈ S 0`
  com `s = |{d : d 0 = a}|`, vale `(v − s)² + s ≤ |D|`. Daí `box_card_ge_18` (`v ≥ 6`) e
  `box_card_ge_21` (`v ≥ 7`): toda fibra tem ≥ 3 e as `v` fibras somam ≥ 3v.
* **Lema 1** (`shorten_covers` + `fiber_card_ge_two`): a fibra `F(j,a)` com `s` palavras deixa
  uma caixa de lado `≥ 7 − s` nas outras três coordenadas, coberta com raio 1 pelas projeções das
  `|C| − s` palavras de fora. `s = 0` contradiz `≥ 21`; `s = 1` contradiz `≥ 18`.
  Diferença do README: não é preciso trocar símbolos de fora da caixa por um símbolo fixo,
  porque o Lema 0 já vale para palavras fora da caixa.
* **Perfis**: `multiset_mem_types18` (7 naturais ≥ 2 somando 18 formam um dos 5 tipos, por
  contagem de multiplicidades), `fiberType_mem_types18`, `profile_mem_profiles18` (o perfil do
  código está em `profiles18 = types18.sym 4`), `profiles18_card = 70` e `perfis18_complete`
  (toda entrada de `profiles18` aparece em `perfis18`, a lista na ordem do `encode.py`).

## 3. Inexistência para M = 18

### 3.1 Como o Florath checou K_8(4,2) = 23

Em `florath/covering-codes-lean@bbed9a6`, `OctonaryFourTwoBlockLRAT.lean` lê CNF + LRAT com
`include_str` e chama `Mathlib.Tactic.Sat.FromLRAT` (`buildProof`), que monta no elaborador um
termo de prova de `Sat.Fmla.proof F []`, conferido pelo kernel. **Não usa `native_decide` nem
`bv_decide`** nos arquivos de K_8(4,2) (o repositório usa `native_decide` em outros arquivos,
p. ex. `TernaryGolay.lean`, `KnownBounds/K_7_6_2.lean`, que não interessam aqui). Os quatro LRAT
dele são de classificadores pequenos de grafos de perfil, não de 1001 perfis.

Medido aqui com o mesmo mecanismo:

| LRAT | tempo | RSS de pico |
|---|---|---|
| K_4(4,2) M = 6, perfil 0 (43 KB) | ~4 s | — |
| `data/K_8_8_5/cover.lrat` do Florath (1,1 MB) | 122 s | 5,6 GB |
| K_7(4,2) M = 18, perfil 64, aparado (5 MB) | — | **morto por falta de memória acima de 12 GB** |

As 70 provas de M = 18 somam 1,67 GB aparadas. Por isso escrevi outro verificador.

### 3.2 O verificador `LratK`

* Literal `2v` / `2v+1`; a fórmula é `List (List ℕ)`.
* **Banco estático**: as cláusulas originais nas chaves `1..n` e as derivadas renumeradas em
  `n+1, n+2, …`, numa árvore binária que é **dado** (o kernel só lê; não reconstrói o banco a
  cada passo — a primeira versão, que inseria no kernel, era ~3× mais lenta).
* `checkF` confere as chaves `1..n` contra a fórmula; `checkRange` confere cada passo RUP
  (dicas com chave em `[1, k)`, atribuição parcial num `ℕ` usado como conjunto de bits).
* Funções reduzidas pelo kernel escritas com recursores (`List.rec`, `Tree.rec`, `Option.rec`):
  medido, o `brecOn` da recursão estrutural deixava a redução ~2× mais lenta.
* Correção: `rup_sound` (passo aceito ⇒ cláusula verdadeira em toda valoração que satisfaz as
  dicas), `good_of_checkRange` (blocos encadeiam), `unsat_of_good`. Tudo em Lean core.
* `lratk_refute ns "f.cnf" "f.lrat" bloco for G` declara os dados (em pedaços, para o kernel não
  estourar a pilha com listas de 20 mil elementos), um teorema `of_decide_eq_true (Eq.refl true)`
  por bloco de passos, `ns.unsat : Unsat F` e, com `for G`, `ns.eqF` (o DIMACS lido é igual a
  `G`, conferido no kernel) e `ns.unsatFor : Unsat G`. Nada no elaborador precisa de confiança.
* Teste de mutação: trocar um literal de uma cláusula derivada no LRAT de K_4 faz o kernel
  recusar o bloco (`application type mismatch … of_decide_eq_true`).
* Tentativa descartada: cláusulas como pares de máscaras de bits e dicas empacotadas num natural
  (menos nós no termo, unidade por `U &&& (U − 1) = 0`). Ficou ~2× **mais lenta** no K_4
  (29 s contra 14 s, mesma máquina carregada), então não entrou.

### 3.3 Números das provas (CaDiCaL 3.0.1 `c607304`, `lrat-trim` 0.2.0 `b30f400`)

| | LRAT original | aparado (texto, com deleções) | passos | dicas (resoluções) | CaDiCaL |
|---|---|---|---|---|---|
| M = 18 com (d)–(f) (a dos certificados) | 3,00 GB | 1,67 GB | 4,69 M | **205 M** | 499 s |
| M = 18 sem (d)–(f) (`--sem-quebra`) | 5,33 GB | 1,95 GB | 5,60 M | **227 M** | 3570 s |

70/70 conferidos pelo `lrat-trim` nos dois casos (`aparo_M18.jsonl`, `aparo_M18_semquebra.jsonl`;
o tamanho do LRAT original de cada perfil com (d)–(f) bate byte a byte com o JSONL da fase 1).
**Achado**: sem a quebra de simetria (d)–(f), o solver leva 7× mais tempo, mas depois do aparo a
prova só cresce 11% em dicas. Isso decide o plano da ponte (abaixo).

### 3.4 O que já roda no kernel

| caso | passos | dicas | tempo de parede | RSS de pico |
|---|---|---|---|---|
| K_4(4,2) M = 6, 5 perfis (`LratK_K4`, alvo padrão) | 1 366 | ~15 mil | ~1,5 min (o arquivo todo) | < 1 GB |
| K_7(4,2) M = 18, perfil 64 (`K742Sat.P64`), sem `for G` | 17 797 | 595 825 | 650 s (1,1 ms por dica) | 8,6 GB, dos quais ~6,9 GB eram só o `import Mathlib` da versão de então |
| idem, versão final (sem Mathlib, com `for G`: `eqF` + `unsatFor`) | 17 797 | 595 825 | 829 s (máquina mais carregada) | 4,9 GB |

Tempos em container de 4 núcleos dividido com outros trabalhos: são ordem de grandeza.

### 3.5 O que falta e quanto custa

**(a) `Refut18`, os outros 69 perfis — computação, sem matemática nova.** Pelo ritmo medido
(1,1 ms por dica): 205 M dicas ≈ **63 h de CPU** (sem (d)–(f): 227 M ≈ 69 h). Paralelizável por
perfil e, dentro do perfil, por bloco (módulos separados que importam o módulo de dados). A
memória por processo deve crescer com o tamanho do banco do perfil (só medida no menor: 4,9 GB;
é hipótese, não medida, para os grandes), então o alvo
natural é uma `e2-highmem-8` spot (8 vCPU / 64 GB, US$ 0,133/h na tabela do `lote-gcp.py`):
6–8 processos ≈ 8–11 h de parede, **≈ US$ 1,5** (com disco e folga, < US$ 3). O maior perfil
(55: 22,9 M dicas) sozinho dá ~7 h num núcleo e tem o maior banco, então precisa ser dividido em
módulos (dados num, blocos de passos em vários) para caber na mesma janela e na memória.
Os `.olean` resultantes (vários GB) não vão para o git; o que vai é o `.lean` gerado e o registro da execução. Não
rodei agora porque, sem a ponte, o resultado seria só uma lista de 70 teoremas `Unsat` que
teria de ser recompilada de qualquer jeito quando a ponte existir (os `.olean` morrem com a VM).

**(b) `Ponte18` — formalização.** Recomendação: usar `cnfSemQuebra` (só +11% de dicas) e
formalizar só (a)–(c), que são "sem perda de generalidade" simples:

1. invariância de `Covers` e dos tamanhos de fibra por permutação de coordenadas e de símbolos
   (isometrias de Hamming);
2. existência de permutações que ordenam o vetor de fibras de cada coordenada e põem as
   coordenadas na ordem do perfil (`perfis18_complete` + `profile_mem_profiles18` já dão o perfil);
3. enumerar as 18 palavras ordenadas pela coordenada 0 (blocos de tamanhos `t[0]`);
4. a valoração: `x[k][i][a] := (w_k i = a)`, contadores `r[i][j] := #{k ≤ i : …} ≥ j+1`,
   projeções `P` e auxiliares `y`; provar cada família de cláusulas de `cnfSemQuebra`
   (exatamente-um, contador sequencial, projeções, cobertura a partir de `Covers`).

Estimativa: 800–1500 linhas de Lean, a parte mais longa sendo o contador sequencial e a
numeração das variáveis (o gerador usa fórmulas fechadas para os índices, o que ajuda). Com
(d)–(f) seria preciso formalizar também os passos 4–5 do `canonizar.py` (forma normal por
primeira aparição), mais do que dobrando o trabalho, para economizar 10% de CPU.

## Reproduzir

    lake build                         # alvo padrão: tudo menos o perfil 64
    python3 tools/exatos/k742/lean/gerar_dados.py --q 7 --M 18 --perfil 64 \
        --saida CoveringLean/K742Sat/dados      # precisa de CADICAL e LRAT_TRIM
    lake build CoveringK742Sat         # ~11–14 min, ~5 GB de RAM
    python3 -m pytest -q tests/test_lean_k742.py

## Decisões tomadas sozinho

* Escrevi um verificador LRAT próprio em vez de reaproveitar o `FromLRAT` do Florath: medido, o
  dele não cabe nem no menor perfil de K_7(4,2).
* A CNF do Lean é a do `encode.py` reescrita (não lida de arquivo) e o kernel confere a
  igualdade com o DIMACS a cada refutação; fora do Lean conferi os 90 perfis (70 de M = 18, 15 de
  M = 17, 5 de K_4) byte a byte, e 3 perfis da versão sem quebra.
* Deixei o enunciado final condicional (`K_7_4_2_eq_19_of`) em vez de não entregar nada da
  inexistência: as duas lacunas viram proposições do Lean, não frases.
* Não rodei os 69 perfis restantes na nuvem (ver 3.5 (a)); custo de nuvem desta tarefa: zero.
* O verificador e o gerador não importam Mathlib (só Lean core), o que derrubou a memória de base
  de ~6,9 GB para ~0,5 GB.

## Falhas

* A primeira medição do `FromLRAT` no perfil 64 estourou a memória do container; o OOM killer
  matou também um processo de outro trabalho que rodava em paralelo
  (`tools/exatos/k742/redteam/indep.py 7 18 2 perfil`, a segunda opinião independente de M = 18).
  Ele precisa ser reiniciado por quem o lançou. Depois disso passei a rodar Lean com um vigia de
  memória que mata o processo antes do limite.
* Uma rodada do perfil 64 com `for G` foi morta pelo meu vigia a 10 GB; a causa era o
  `import Mathlib` (6,9 GB de base), não o verificador.
