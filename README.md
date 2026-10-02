# Lean 4 + Mathlib: cotas de cobertura, verificadas pelo kernel

The note is [paper/main.pdf](paper/main.pdf), source [paper/main.tex](paper/main.tex). Tag `v0.3.0`; DOI conceitual
[10.5281/zenodo.23085769](https://doi.org/10.5281/zenodo.23085769) (aponta sempre para a versão mais nova).

Estado (2026-10-01), Lean 4.34.1 + Mathlib v4.34.1, VM e2-highmem-8:

* `lake build` (alvo padrão, biblioteca `CoveringLean`): **passa**, 8942 jobs, 32 s, pico 7,7 GB.
* `lake build CoveringHeavy` (os dois certificados de busca, 133 módulos): **passa**, 9073 jobs, 1 h 41 min de relógio com até 8 módulos em paralelo (~12,4 h de CPU somadas), pico 8,8 GB por processo.

Nenhum `sorry`, nenhum `native_decide`, e todo `#print axioms` mostra no máximo `propext, Classical.choice, Quot.sound`.

## Resultados novos desta versão

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

## O que NÃO está provado (declarado)

* Os outros 7 códigos de `data/codes/` não têm teorema Lean (só verificação computacional).
* Novidade na literatura é afirmação nossa, não do Lean; a busca bibliográfica está descrita acima.
* `A6d_SearchHeavy.lean` e `A5b_Stress.lean` continuam fora da biblioteca e não compilam (o primeiro ficou obsoleto
  com `A6e` e `SearchK6ge12`).
* Que os enunciados formais são os pretendidos é revisão humana: leia os enunciados de `K_2_6_1_ge_11`,
  `K_2_6_1_eq12`, `K7_9_4_le_1351_kernel` e as definições `ball`, `Covers`, `IsK` em `A2_Sphere` e `A6_Finite`.

## Reconstruir

`elan` + `lake exe cache get` + `lake build` (segundos). Os certificados: `lake build CoveringHeavy`, ~12,4 h de CPU;
cada módulo cabe em ~8,6 GB, e `lake build -j N` com `N ≈ RAM/9 GB` funciona. Os geradores dos pedaços estão em
`scripts/k261/` (`gen_demo.py`, espelho Python `sc_ref.py`, `INTERFACE.md`) e `scripts/k794/` (`sim.c` mede os passos
por prefixo, `gen.py` escreve as folhas; `build1.sh`, `pool.sh` e `finish.sh` foram o agendador usado na VM e têm
caminhos dela). Evite `decide +kernel` sobre `Finset.univ` de tipos Pi grandes (17–24 GB).
