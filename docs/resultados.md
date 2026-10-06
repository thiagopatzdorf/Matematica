# Resultados detalhados: cotas de cobertura verificadas pelo kernel

> Movido do `README.md` da raiz em 2026-10-04, sem perda de conteúdo. O que a raiz mostra é o resumo; os números por versão, as tabelas, os certificados e a reprodução moram aqui. Os links relativos e os caminhos entre crases partem da raiz do repositório.


The note is [paper/main.pdf](../paper/main.pdf), source [paper/main.tex](../paper/main.tex). Tag `v0.6.0`; DOI conceitual
[10.5281/zenodo.23085769](https://doi.org/10.5281/zenodo.23085769) (aponta sempre para a versão mais nova).

Estado (2026-10-03), Lean 4.34.1 + Mathlib v4.34.1, VM e2-highmem-8:

* `lake build` (alvo padrão, agora com `SynCheck`/`SynBridge`, clone limpo): **passa**, 8944 jobs, 4 min 16 s, pico 10,0 GB. Também roda no CI do GitHub a cada push.
* `lake build CoveringHeavy` (`K_2(6,1) = 12` e as oito cotas superiores): **passa**, 9181 jobs, 1 h 54 min de relógio (~9,3 h de CPU), pico 9,4 GB por processo.
* `lake build CoveringSyn` (os quatro certificados por síndromes da v0.4): **passa**, 8983 jobs, 10 min 35 s de relógio (~37 min de CPU para os quatro), pico 6,9 GB por processo.
* `lake build CoveringLean.Syn_K1137` (v0.5, `K_7(9,4) ≤ 1137`): **passa**, 2 min 41 s em 8 núcleos (331 s de CPU), pico 6,7 GB; `#print axioms` só `propext, Classical.choice, Quot.sound`.
* v0.6 (2026-10-03, contêiner de 4 núcleos, módulos próprios do zero): `Syn_K1134` 105 s, `Syn_K162` 101 s, `Syn_K2875` 364 s, `Syn_K5616` 654 s, todos exit 0, axiomas só `propext, Classical.choice, Quot.sound`; mutações rejeitadas pelo Lean em `docs/validacao/LEAN_RED_TEAM.md` (seção v0.6) e `docs/validacao/VALIDATION_v0.6.md`.

Nenhum `sorry`, nenhum `native_decide`, e todo `#print axioms` mostra no máximo `propext, Classical.choice, Quot.sound`.

## v0.6: `K_7(9,4) ≤ 1134` e mais dez cotas superiores, todas no kernel

Um teorema `∃ C : Finset (Fin n → ZMod q), C.card = M ∧ Covers R C` por célula. Em cada célula a lista em Lean
decodifica para o arquivo de `data/codes/` com o mesmo sha256 canônico.

| célula | nossa | anterior | declaração | certificado |
|---|---:|---:|---|---|
| `K_7(9,4)` | **1134** | 1475 (Marosi, arXiv:2608.19872v3) | `Syn.K7_9_4_le_1134_syn` (também `…_1137_syn`, `…_1141_syn`, `…_1285_syn`, `…_1351_syn`, `CoveringKernel.K7_9_4_le_1351_kernel`) | síndromes |
| `K_7(10,4)` | **5616** | 6517 (Kéri) | `Syn.K7_10_4_le_5616_syn` | síndromes |
| `K_5(11,4)` | **2875** | 3125 (Kéri) | `Syn.K5_11_4_le_2875_syn` | síndromes |
| `K_5(10,5)` | **162** | 175 (Kéri) | `Syn.K5_10_5_le_162_syn` | síndromes |
| `K_7(8,3)` | 1887 | 2337 (Kéri) | `Syn.K7_8_3_le_1887_syn` (também `CoveringKernel.K7_8_3_le_1893_kernel`) | síndromes |
| `K_5(10,4)` | 625 | 875 | `CoveringKernel.K5_10_4_le_625_kernel` | prefixos |
| `K_5(9,3)` | 1250 | 1275 | `CoveringKernel.K5_9_3_le_1250_kernel` | prefixos |
| `K_5(7,2)` | 500 | 525 | `CoveringKernel.K5_7_2_le_500_kernel` | prefixos |
| `K_5(9,4)` | 250 | 255 | `CoveringKernel.K5_9_4_le_250_kernel` | prefixos |
| `K_4(10,4)` | 192 | 208 | `CoveringKernel.K4_10_4_le_192_kernel` | prefixos |
| `K_5(9,5)` | 50 | 55 | `CoveringKernel.K5_9_5_le_50_kernel` | prefixos |

**Dois certificados.** Prefixos (`K2_*`, `K3_*`, lib `CoveringHeavy`): ~12 h de CPU para `(Z/7)^9`. Síndromes
(`SynCheck` só com o núcleo do Lean, `SynBridge` com Mathlib, lib `CoveringSyn`): o mesmo 1351 em ~8 min de CPU,
folhas ≤ 1,8 GB; o 1141 em ~9 min, o 1137 em 5,5 min. Gerador: `scripts/syndrome/gen_syn.py` (lê o formato `covering-code/v1`).

**Como os códigos foram achados:** todos são cosets de um código linear + remendo. O 1141 vem da enumeração das
6362 classes de `[9,3]_7`, com avaliação exata das síndromes órfãs (6, contra 27 da base original), e de um
otimizador de remendo (112 palavras); o 1137 usa a mesma base com 108 palavras, achadas por LNS com subproblema exato
(ILP no HiGHS). Nessa base o remendo precisa de pelo menos ⌈2058/24⌉ = 86 palavras (uma bola de raio 4 cobre no máximo 24
dos 2058 pontos órfãos); o intervalo 86–108 está em aberto. Ver `data/structured/` e `ledger/`.

**Varredura das bases (em auditoria, fora das afirmações):** a pasta `audit` da branch `feat/kit-de-busca`. A lista de
6362 classes é completa (fórmula de massa); o mínimo exato de órfãs por classe e as 1375 classes degeneradas estão sendo
fechados com teste diferencial e verificador independente.

## Resultados da v0.3

| Teorema | Enunciado | Como |
|---|---|---|
| `CoveringA6.K_2_6_1_ge_11` (`A6e_Excess`) | todo código binário de comprimento 6 que cobre com raio 1 tem ≥ 11 palavras | contagem dupla do excesso, sem busca: para `a ≠ c`, `|B(a) ∩ B(c)|` é par; daí `50K ≥ 512` |
| `SC.K_2_6_1_eq12` (`SearchK6ge12`) | `IsK 2 6 1 12`, isto é `K_2(6,1) = 12` | busca com poda verificada (`SearchCore.chkN`, correção em `SearchSound.chkN_sound`), translação "WLOG 63 ∈ C", exclusão de irmãos, 38 pedaços `G610_Chunk_*` com `decide +kernel` |
| `CoveringKernel.K7_9_4_le_1351_kernel` (`K3_K7_9_4_Final`) | existe `C : Finset (Fin 9 → ZMod 7)` com `C.card = 1351` e `Covers 4 C` | o código explícito (`C1_Data_K7_9_4`, sha256 canônico `54dbdade…1162`), checagem booleana `go` com prova de correção (`K2_Core`, `K2_Loop`, `K3_Bridge`), 2401 folhas em 95 pedaços `K3_K7_9_4_P*` |

`K_2(6,1) ≥ 11` deixa de ser condicional; `H2_counterexample_uncond` refuta H2 sem hipótese.

**Contexto na literatura, conferido em 2026-10-01** (comparação feita por nós, sem revisão externa):

* `K_2(6,1) = 12` é clássico (Stanton–Kalbfleisch, 1968). Novo aqui é a prova verificada pelo kernel. O banco Lean do
  Florath ([arXiv:2606.09600](https://arxiv.org/abs/2606.09600), `florath/covering-codes-lean`) tem `10 ≤ K_2(6,1) ≤ 12`.
* `K_7(9,4) ≤ 1351` fica abaixo da melhor cota superior publicada que encontramos, `1475` (Marosi,
  [arXiv:2608.19872](https://arxiv.org/abs/2608.19872) v3, 2026-09-02; Kéri 2011 tinha 1843). O código foi achado com o
  gerador `lincov` do repositório público do Marosi (`Mapika/coldcase`, commit `56a8cce`): 3 cosets de um núcleo
  `[9,3]_7` (1029 palavras) mais 322 de remendo guloso. A origem do remendo não ficou registrada; o código em si está
  em `data/codes/q7_n9_R4_M1351.txt` e o teorema não depende do gerador.
* A cota de esfera (`A1`–`A3`, `Chain`) já estava formalizada pelo Florath em junho de 2026; as 8 instâncias `SPH_*`
  estão abaixo das melhores cotas inferiores conhecidas (Kéri, Gijswijt–Polak 2025, Marosi 2026).

`data/codes/` traz também os outros 7 códigos (`K5(7,2) ≤ 500`, `K4(10,4) ≤ 192`, `K5(9,3) ≤ 1250`, `K5(10,4) ≤ 625`,
`K5(9,5) ≤ 50`, `K5(9,4) ≤ 250`, `K7(8,3) ≤ 1893`), todos abaixo das tabelas que conferimos e checados por três
verificadores independentes fora do Lean; **ainda não são teoremas Lean**. `K5(10,4) ≤ 625` é um código linear
`[10,4]_5`; falta conferir as tabelas de comprimento de Davydov–Marcugini–Pambianco.

## Formato estruturado e verificador oficial

Cada código de `data/codes/` tem uma descrição estruturada em `data/structured/` (cosets de um código linear,
cosets de subcódigos, palavras soltas, proveniência e sha256 canônico), e `tools/verify/verify.c` (C, sem
dependências) confere todos: `tools/verify/check_all.sh`, também no CI (`.github/workflows/verify-codes.yml`).
Especificação e números em [docs/code-format.md](code-format.md).

## O que está provado (biblioteca inteira)

Espaço `Fin n → ZMod q` (A1–A3, Chain, K3) ou `Fin n → Fin q` (A6*, Search*), com `hammingDist` do Mathlib.

| Arquivo | Conteúdo |
|---|---|
| `A1_Weight` | `weight_genfun`: `∑ X^peso = (1+(q-1)X)^n`; `count_weight`; `ball_zero_card` |
| `A2_Sphere` | `ball_card_indep`, `sphere_covering` (`q^n ≤ |C|·V`), `no_perfect`, `ceil_bound`, `equality_iff_perfect` |
| `A3_Numeric` | aritmética: `V` fechada, `⌈q^n/V⌉`, os 8 `cell_*` e `lb_*`, `tight_*` |
| `Chain` | `sphere_covering_formula` e os 8 `CoveringChain.SPH_K*_lb` |
| `A4_Closed` | `K_q(n,n-1)=q`, `K=1` para `R ≥ n`, monotonias |
| `A5_Frontier` | cota para cobertura parcial e limiar de viabilidade |
| `A6_Finite`, `A6b_Hamming` | contra-exemplos H5, H1, H3, Hamming `[7,4]` perfeito, `K_2(7,1)=16` |
| `A6c_Search` | verificador de busca antigo (`refuted_sound`), `code12` (`K_2(6,1) ≤ 12`) |
| `A6e_Excess` | `excess_bound` (abstrato), `K_2_6_1_ge_11`, `H2_counterexample_uncond` |
| `SearchCore`, `SearchSound`, `SearchBridgeA2` | busca `chkN` em bitmask (só núcleo), sua correção e a ponte para `W 2 6` e `ZMod 2` |
| `C1_CoverCheck`, `K2_Core`, `K2_Loop`, `K3_Bridge` | lista de palavras → `Covers R C` com cardinal exato, checagem `go` e `go_split` |
| `CoveringHeavy`: `SearchK6ge12`, `G610_*` | `K_2(6,1) = 12` |
| `CoveringHeavy`: `K3_K7_9_4_Final`, `K3_K7_9_4*`, `C1_Data_K7_9_4` | `K_7(9,4) ≤ 1351` |
| `CoveringHeavy`: `K3_<célula>_Final`, `K3_<célula>*`, `C1_Data_<célula>` (7 células) | as outras sete cotas da tabela da v0.4 |

## O que NÃO está provado (declarado)

* Os programas de busca não são verificados; só a saída deles é.
* Novidade na literatura é afirmação nossa, não do Lean; a busca bibliográfica está descrita acima.
* `A6d_SearchHeavy.lean` e `A5b_Stress.lean` continuam fora da biblioteca e não compilam (o primeiro ficou obsoleto
  com `A6e` e `SearchK6ge12`).
* Que os enunciados formais são os pretendidos é revisão humana: leia os enunciados de `K_2_6_1_ge_11`,
  `K_2_6_1_eq12`, os oito `K*_le_*_kernel` e as definições `ball`, `Covers`, `IsK` em `A2_Sphere` e `A6_Finite`.

## Reconstruir

`elan` + `lake exe cache get` + `lake build` (segundos). Os certificados: `lake build CoveringHeavy`, ~12,4 h de CPU;
cada módulo cabe em ~8,6 GB, e `lake build -j N` com `N ≈ RAM/9 GB` funciona. Os geradores dos pedaços estão em
`scripts/k261/` (`gen_demo.py`, espelho Python `sc_ref.py`, `scripts/k261/INTERFACE.md`) e `scripts/k794/` (`sim.c` mede os passos
por prefixo, `gen.py` escreve as folhas; `build1.sh`, `pool.sh` e `finish.sh` foram o agendador usado na VM e têm
caminhos dela). Evite `decide +kernel` sobre `Finset.univ` de tipos Pi grandes (17–24 GB).
