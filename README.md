# Lean 4 + Mathlib: cota de esfera, verificada pelo kernel

Estado (2026-10-01): `lake build` completo **passa** (8934 jobs, 34 s, pico 7,6 GB, Lean 4.34.1 + Mathlib v4.34.1,
medido numa VM e2-standard-8). Nenhum `sorry`, nenhum `native_decide`, e todo `#print axioms` mostra no máximo
`propext, Classical.choice, Quot.sound`.

## O que está provado

Espaço `Fin n → ZMod q` com `hammingDist`/`hammingNorm` do Mathlib.

| Arquivo | Conteúdo |
|---|---|
| `A1_Weight` | `weight_genfun`: `∑ X^peso = (1+(q-1)X)^n`; `count_weight`; `ball_zero_card` |
| `A2_Sphere` | `ball_card_indep` (toda bola tem o mesmo tamanho), `sphere_covering` (`q^n ≤ |C|·V`), `no_perfect` (`V ∤ q^n ⇒ q^n < |C|·V`), `ceil_bound`, `equality_iff_perfect` |
| `A3_Numeric` | aritmética: `V` fechada, `⌈q^n/V⌉`, os 8 `cell_*` e `lb_*`, `tight_*` |
| `Chain` | liga A1+A2+A3: `sphere_covering_formula` e os 8 teoremas finais `CoveringChain.SPH_K*_lb` |
| `A4_Closed` | `K_q(n,n-1)=q`, `K=1` para `R ≥ n`, monotonias |
| `A5_Frontier` | cota para cobertura parcial (fração `1-ε`) e limiar de viabilidade |
| `A6_Finite`, `A6b_Hamming` | contra-exemplos finitos (H5, H1, H3), Hamming `[7,4]` perfeito, `K_2(7,1)=16` |
| `A6c_Search` | verificador de busca (`refuted_sound`) e `K_2(6,1) ≥ 11` **condicional** à busca |

Os 8 teoremas ponta a ponta (todo código `C` que cobre com raio `R` tem `|C| ≥ cota`):
`SPH_K5_7_2_lb` (215), `SPH_K4_10_4_lb` (51), `SPH_K5_9_3_lb` (327), `SPH_K5_10_4_lb` (158),
`SPH_K5_9_5_lb` (12), `SPH_K5_9_4_lb` (52), `SPH_K7_8_3_lb` (439), `SPH_K7_9_4_lb` (221).

## O que NÃO está provado (declarado)

* **Busca exaustiva `K_2(6,1) ≥ 11`**: `A6d_SearchHeavy.lean` (fora da biblioteca, não compilado) tenta fechá-la com
  `decide +kernel`, e isso estourou 24 GB de RAM em 2,5 min (195 112 nós, contados em Python). Por isso
  `no_cover_2_6_1_le10` e `H2_counterexample` valem só sob a hipótese `refuted … = true`; a claim continua
  COMPUTATIONALLY_VERIFIED. Caminhos: dividir a árvore em declarações separadas, popcount barato, simetria.
* `A5b_Stress.lean` (fora da biblioteca): estresses exaustivos, não compilado.
* Lean **não** verifica os 8 códigos de até 5^10 palavras (só moveria a confiança para o compilador), nem novidade,
  nem acha códigos.
* Que os enunciados formais são **os pretendidos** (A1 usa `hammingNorm`, A2 usa `hammingDist`, A3 a fórmula fechada;
  `Chain.ball_zero_eq_V` os une) é revisão humana.

Reconstruir: `elan` + `lake exe cache get` + `lake build` nesta pasta. Evite `decide +kernel` sobre `Finset.univ` de
tipos Pi grandes (17–24 GB).
