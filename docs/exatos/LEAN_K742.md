# K_7(4,2) = 19 no Lean 4 (2026-10-04)

Lean 4.34.1 + Mathlib v4.34.1. Regras: checado pelo kernel, sem `sorry`, sem `native_decide`,
sem `ofReduceBool`/`implemented_by`; todo `#print axioms` dá no máximo
`[propext, Classical.choice, Quot.sound]`. Contexto: `docs/exatos/FASE1_B_K742.md` (o
resultado computacional), `tools/exatos/k742/README.md` (a prova escrita) e
`docs/exatos/REDTEAM_K742.md`.

## Resumo: K_7(4,2) = 19 é teorema do Lean

| afirmação | estado | declaração |
|---|---|---|
| **K_7(4,2) = 19** | **teorema** (lib `CoveringK742Sat`) | `K742.K_7_4_2_eq_19`, `K742.K_7_4_2_isK : CoveringA6.IsK 7 4 2 19` |
| K_7(4,2) ≤ 19 | **teorema** | `K742.K_7_4_2_le_19` |
| Lema 0 (caixas de comprimento 3), `K_6(3,1) ≥ 18` e `K_7(3,1) ≥ 21` na forma de caixa | **teorema** | `K742.box_fiber_bound`, `K742.box_card_ge_18`, `K742.box_card_ge_21` |
| Lema 1: com M ≤ 18, toda fibra tem ≥ 2 palavras | **teorema** | `K742.fiber_card_ge_two` |
| redução código → perfil (cada coordenada tem um dos 5 tipos; o multiconjunto é um dos 70 perfis) | **teorema** | `K742.fiberType_mem_types18`, `K742.profile_mem_profiles18`, `K742.profiles18_card`, `K742.perfis18_complete` |
| a CNF de cada perfil, igual à de `encode.py` | **definição** no Lean (`K742Cnf.cnf`, `K742Cnf.cnfSemQuebra`), conferida contra o DIMACS **pelo kernel** a cada refutação | `K742Cnf.cnf`, `K742Cnf.cnfSemQuebra` |
| verificador LRAT executado pelo kernel, com prova de correção | **teorema** | `LratK.unsat_of_good`, `LratK.good_of_checkRange`, `LratK.rup_sound`; comandos `lratk_refute`, `lratk_data`/`lratk_steps`/`lratk_final` |
| **`Ponte18 cnfSemQuebra`**: todo código de 18 palavras satisfaz a CNF sem quebra de algum perfil | **teorema** (alvo padrão) | `K742Ponte.ponte18`, `K742Ponte.cnfSemQuebra_sat` |
| **`Refut18 cnfSemQuebra`**: as 70 CNFs sem quebra de M = 18 são insatisfatíveis | **teorema** (lib `CoveringK742Sat`, 70 refutações no kernel) | `K742Sat.refut18`, `K742Sat.s<p>.unsatFor` (p = 0..69) |
| K_7(4,2) = 19 **a partir de** `Ponte18 G` e `Refut18 G` | **teorema** (condicional, para qualquer família `G`) | `K742.K_7_4_2_eq_19_of` |
| perfil 64 **com** a quebra (d)–(f) | teorema (registro histórico, não usado no final) | `K742Sat.refut18_p64` |
| teste de ponta a ponta do verificador: as 5 CNFs de K_4(4,2), M = 6 | **teorema**, no alvo padrão | `LratK_K4.refut6` |

Todos os `#print axioms` dão `[propext, Classical.choice, Quot.sound]` (ou menos); nada de
`sorry`, `native_decide`, `ofReduceBool` ou `implemented_by`. Ver a seção 4 para o que foi
compilado, onde, quanto custou e como reproduzir.

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
| `CoveringLean/K742Sat/P64.lean` | perfil 64 de K_7(4,2), M = 18, **com** quebra (dados fora do git) | `CoveringK742Sat` |
| `CoveringLean/LratKFinal.lean` | `lratk_final_seg`: fecho da refutação dividida, com a cadeia em segmentos | padrão |
| `CoveringLean/K742_PonteCnf.lean` | metade CNF da ponte: palavras normalizadas satisfazem `cnfSemQuebra` (só Lean core) | padrão |
| `CoveringLean/K742_Ponte.lean` | `K742Ponte.ponte18`: normalização por isometrias e enumeração por blocos | padrão |
| `CoveringLean/K742Sat/S<p>/{Data,B<m>,Final}.lean` | as 70 refutações sem quebra, divididas em módulos (gerados) | `CoveringK742Sat` |
| `CoveringLean/K742Sat/Refut.lean` | `K742Sat.refut18 : Refut18 (cnfSemQuebra 7 18)` (gerado) | `CoveringK742Sat` |
| `CoveringLean/K742_Eq19.lean` | `K742.K_7_4_2_eq_19`, `K742.K_7_4_2_isK` | `CoveringK742Sat` |
| `tools/exatos/k742/lean/preparar_semquebra.py` | CNF sem quebra + CaDiCaL + `lrat-trim` + renumeração e divisão em módulos | — |
| `tools/exatos/k742/lean/gerar_modulos.py` | escreve os módulos `S<p>/` e `Refut.lean` a partir de `semquebra_M18.jsonl` | — |
| `tools/exatos/k742/lean/semquebra_M18.jsonl` | por perfil: `n`, `K`, passos, dicas, módulos, sha256 da CNF, do LRAT aparado e de cada arquivo de dados | — |
| `tools/exatos/k742/lean/vm/` | `rodar.sh` (VM de lote), `agendar.py` (compila os módulos com `lean`, com registro), `lakefile.toml` mínimo (sem Mathlib) | — |
| `tools/exatos/k742/lean/execucao/` | registro da execução nas VMs: `modulos*.jsonl` (tempo, CPU, RSS, rc por módulo), `axiomas.txt`, `preparo*.jsonl` | — |
| `tools/exatos/k742/lean/vigia.py` | roda um comando com teto de RSS (usado nos builds locais) | — |
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

### 3.5 A ponte código → CNF sem quebra (`K742Ponte.ponte18`)

Feita para `cnfSemQuebra` (só (a)–(c)), como recomendado: a CNF com (d)–(f) exigiria formalizar a
forma normal do `canonizar.py`, e o aparo mostrou que a prova sem quebra só tem 11% mais dicas.
847 linhas em dois arquivos.

* **`K742_PonteCnf.lean` (só Lean core).** `Normal t w` diz que 18 palavras `w k : ℕ → ℕ` têm
  símbolos `< 7`, cobrem (todo `x ∈ {0..6}^4` concorda com alguma palavra num dos 6 pares de
  coordenadas), têm `tv t i a` ocorrências de `a` na coordenada `i = 1..3` e que a palavra `k` está
  no bloco do seu símbolo da coordenada 0. `val t w` é a valoração: as variáveis do gerador formam
  segmentos consecutivos (as `x`, os 21 contadores, os 6 pares) e `segVal` decodifica o número da
  variável pelo segmento (`segVal_idx`, `counterBase_eq`, `projBase_eq`). `exatamente_sat` prova o
  contador sequencial de uma vez (`r[i][j]` = "pelo menos `j+1` dos `b 0..b i`"); as outras três
  famílias (`exactlyOne_sat`, `projections_sat`, `coverage_sat`) saem das fórmulas fechadas dos
  índices (`val_x`, `val_c'`, `val_P0`, `val_P1`, `val_Y`). Resultado: `cnfSemQuebra_sat`.
* **`K742_Ponte.lean`.** Dado `C`, `profile_mem_profiles18` + `perfis18_complete` dão `t`;
  `exists_perm_of_map_eq` (duas funções de um tipo finito com o mesmo multiconjunto de valores
  diferem por uma permutação) dá a permutação `π` das coordenadas e, em cada coordenada, a
  permutação `σ i` dos símbolos que põe as fibras na ordem de `t[i]`; as palavras renomeadas são
  `(σ i)⁻¹ (c (π i))`. A enumeração por blocos sai de `finSigmaFinEquiv`
  (`Σ a, Fin (n a) ≃ Fin (∑ n)`, com o índice `n 0 + … + n (a−1) + j`), composto com as bijeções
  de cada fibra (`exists_block_enum`). A cobertura usa `agree_two` (distância ≤ 2 em comprimento 4
  ⇒ duas coordenadas de acordo). Fatos dos 70 perfis (comprimentos, soma 18, blocos dentro de
  `0..17`) por `decide +kernel` (`perfis18_shape`).

## 4. As 70 refutações sem quebra no kernel (`K742Sat.refut18`)

### 4.1 Como foi dividido

`lratk_refute` (um módulo por refutação) não serve para os perfis grandes: o perfil 55 sem
quebra tem 853 545 passos e 39,0 M dicas (~5 h de CPU num módulo só). Os dados passam a vir
renumerados e já cortados por `preparar_semquebra.py`, e cada perfil `p` vira:

* `S<p>/Data.lean` — `lratk_data`: a árvore `db` (CNF nas chaves `1..n`, derivadas em `n+1..K`),
  `F` em pedaços, `fGood`, `hK`, `hempty`;
* `S<p>/B<m>.lean` — `lratk_steps`: blocos de 100 passos (`H<j>`, `ok<j>`), até ~2 M dicas por
  módulo (o perfil 55 tem 20 módulos B); importam só o `Data` do perfil, então compilam em paralelo;
* `S<p>/Final.lean` — `lratk_final_seg` (`LratKFinal.lean`): encadeia `fGood` e os `ok<j>` em
  teoremas `seg<s>` de até 200 blocos, depois `unsat`, `eqF` (a fórmula lida é
  `cnfSemQuebra 7 18 t`, no kernel) e `unsatFor`.

Medido antes de rodar: blocos de 100 passos em vez de 400 baixam o pico de RSS de um módulo de
~3,8 GB para ~2,8 GB (o kernel guarda os bits da atribuição parcial de cada bloco) sem custo de
tempo; e um termo com 12 001 `good_of_checkRange` aninhados faz o kernel parar com "deep recursion
detected" (o perfil 55 tem 8 536 blocos), daí os segmentos.

### 4.2 Execução (2026-10-04, duas VMs spot em southamerica-east1-a)

| | exg-1 (`t2d-standard-8`, 8 núcleos físicos, 32 GB) | exg-2 (`c2d-highmem-8`, 4 núcleos com SMT, 64 GB) |
|---|---|---|
| ligada | 17:58 → 21:37 UTC (3,65 h) | 19:38 → 21:58 UTC (2,3 h) |
| perfis | os 8 maiores (55, 25, 9, 0, 2, 39, 47, 45) | os outros 62 |
| módulos com rc 0 | 150 | 196 |
| CPU | 23,0 h | 14,7 h |
| paralelismo | 7 `lean` | 8 `lean` |

* Preparo (CNF + CaDiCaL + `lrat-trim` + divisão): ~2 min para os 70 perfis em cada VM (CaDiCaL
  `c607304` e `lrat-trim` `b30f400` compilados na VM). Os 62 perfis preparados nas duas VMs deram
  JSON idênticos (sha256 de cada arquivo de dados), o que confere o determinismo em duas CPUs
  diferentes.
* Módulos: **284** (70 `Data`, 144 `B`, 70 `Final`), todos com rc 0. CPU total **37,8 h**, dos
  quais 36,3 h nos blocos B: **0,58 ms de CPU por dica** (226,9 M dicas). Pico de RSS: 9,2 GB
  (`S55.Data`, a árvore de 873 mil cláusulas), 4,2 GB num `B`, 5,2 GB num `Final`. Parede do
  primeiro ao último módulo: 3,7 h.
* Perfis mais caros (CPU): 55 = 6,8 h, 25 = 5,0 h, 9 = 3,1 h, 0 = 2,9 h, 2 = 2,4 h.
* Depois das 70 refutações, na exg-2: `Refut.lean` (6,5 s) e `K742_Eq19.lean` (4,3 s), com
  Mathlib do cache e os `.olean` da exg-1 copiados para lá; os `#print axioms` de
  `K742Sat.refut18`, `K742.K_7_4_2_eq_19` e `K742.K_7_4_2_isK` dão
  `[propext, Classical.choice, Quot.sound]`.
* **Custo de nuvem: ≈ US$ 1,0** (exg-1 3,65 h × US$ 0,177 + exg-2 2,3 h × US$ 0,145 + disco
  pd-standard de 60 GB por poucas horas). As duas VMs foram destruídas no fim.

O registro está em `tools/exatos/k742/lean/execucao/`: `modulos_exg1.jsonl` e
`modulos_exg2.jsonl` (uma linha por módulo: parede, CPU, pico de RSS por `wait4`, rc),
`axiomas.txt` (os 73 `#print axioms`), `saida_modulos.txt` (a saída de cada `lean`),
`final_exg2.{jsonl,log}` (caminhos absolutos das VMs trocados por `<raiz>`/`<home>`). `resumo_execucao.py` refaz os números acima. Os sha256 de todos os
dados (CNF, LRAT aparado, `c.txt`, `h<m>.txt`, `meta.txt`) estão em `semquebra_M18.jsonl`; os
dados em si não vão para o git (1,9 GB, regenerados em ~2 min).

Notas honestas sobre o registro:

* No meio da corrida (19:38 e 21:10) passei 51 e depois mais 11 perfis da exg-1 para a exg-2 (a
  cota de T2D era 24 vCPUs, a 2ª VM é C2D). Na exg-1 isso foi feito tirando o diretório de dados
  desses perfis, de modo que os módulos B correspondentes falharam na hora de ler o arquivo
  (`rc = 1` em `modulos_exg1.jsonl`, 134 linhas, todas de perfis desviados) e foram compilados do
  zero na exg-2. Os `Data` desses perfis compilaram nas duas VMs.
* `lratk_final_seg` (e `LratKFinal.lean`) entrou depois que os `Data`/`B` da exg-1 já tinham
  começado; os `Final` da exg-1 foram gerados de novo antes de compilar (nenhum `Final` usou a
  versão sem segmentos). `LratK.lean`, `LratKData.lean` e `K742_Cnf.lean` são byte a byte os do
  repositório nas duas VMs.
* `Refut.lean` e `K742_Eq19.lean` foram compilados com `lean` direto (não `lake`): os `.olean` de
  `K742_Final`, `K742_Ponte` etc. vieram de um `lake build` no checkout completo, ligados por
  symlink no diretório dos `.olean` das refutações. Um `lake build CoveringK742Sat` do zero faz
  o mesmo em uma passada (ver "Reproduzir").

## Reproduzir

    lake build                         # alvo padrão: inclui K742Ponte.ponte18 (a ponte)
    python3 -m pytest -q tests/test_lean_k742.py

    # as 70 refutações e o teorema final (~38 h de CPU, ~3–9 GB por processo)
    export CADICAL=… LRAT_TRIM=…       # CaDiCaL c607304, lrat-trim b30f400
    for p in $(seq 0 69); do
      python3 tools/exatos/k742/lean/preparar_semquebra.py --perfil $p \
          --saida CoveringLean/K742Sat/dados > /tmp/prep_$p.json   # sha256 = semquebra_M18.jsonl
    done
    lake build CoveringK742Sat         # ou, com paralelismo controlado e registro por módulo:
    # python3 tools/exatos/k742/lean/vm/agendar.py --perfis 55,25,…,65 --jobs 7

Numa VM de lote (sem Mathlib, só para as refutações): copie `lean-toolchain`,
`tools/exatos/k742/lean/vm/lakefile.toml` (como `lakefile.toml`),
`CoveringLean/{LratK,LratKData,LratKFinal,K742_Cnf}.lean` e `tools/exatos/k742/`, e rode
`bash tools/exatos/k742/lean/vm/rodar.sh <perfis> <jobs>` (instala CaDiCaL e lrat-trim, prepara,
gera os módulos e chama o `agendar.py`).

O perfil 64 com a quebra (`K742Sat.P64`, também na lib) precisa dos dados de `gerar_dados.py`.

## Decisões tomadas sozinho (esta etapa)

* Ponte e refutações **sem** a quebra (d)–(f), como recomendado na etapa anterior: a forma normal
  do `canonizar.py` não precisou ser formalizada.
* Refutação dividida em `Data`/`B`/`Final` com dados pré-renumerados por Python (não precisa de
  confiança: o kernel confere cada passo, a CNF e o encadeamento), blocos de 100 passos e ~2 M
  dicas por módulo; cadeia final em segmentos de 200 blocos.
* Compilei com um agendador próprio (`agendar.py`, `lean` direto) em vez de `lake build`, para
  fixar o paralelismo pela memória e registrar tempo/RSS/rc de cada módulo.
* Usei duas VMs de tipos diferentes (T2D e C2D) e redistribuí perfis no meio da corrida, quando a
  2ª VM coube na cota; os dados dos perfis desviados foram tirados da 1ª VM (ver 4.2).
* O teorema final fica na lib `CoveringK742Sat` (fora do alvo padrão e do CI): o CI compila a
  ponte e o resto, não as 38 h de refutações.
* Os dados (1,9 GB) não foram para o bucket: o registro + sha256 ficam no repositório e os dados
  se regeneram em ~2 min, de forma determinística (conferido em duas CPUs).

## Falhas (esta etapa)

* O primeiro teste local da cadeia final com 12 001 blocos parou o kernel ("deep recursion
  detected"); daí `lratk_final_seg`. Achado antes de rodar na nuvem.
* O primeiro vigia de memória (`vigia.py`) só somava o RSS dos filhos da thread principal do
  `lake`, e por isso marcou 0,8 GB para builds que usavam 4 GB; corrigido para somar a sessão
  inteira.
* Na montagem final, o `lean` não acha módulos de um mesmo pacote (`CoveringLean.*`) espalhados
  em dois diretórios de `.olean`; resolvido com symlinks (ver 4.2).
* A primeira tentativa de criar a 2ª VM como T2D falhou por cota (`T2D_CPUS` = 24 na região).

## Decisões e falhas da etapa anterior (PR #34)


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

### Falhas da etapa anterior

* A primeira medição do `FromLRAT` no perfil 64 estourou a memória do container; o OOM killer
  matou também um processo de outro trabalho que rodava em paralelo
  (`tools/exatos/k742/redteam/indep.py 7 18 2 perfil`, a segunda opinião independente de M = 18).
  Ele precisa ser reiniciado por quem o lançou. Depois disso passei a rodar Lean com um vigia de
  memória que mata o processo antes do limite.
* Uma rodada do perfil 64 com `for G` foi morta pelo meu vigia a 10 GB; a causa era o
  `import Mathlib` (6,9 GB de base), não o verificador.
