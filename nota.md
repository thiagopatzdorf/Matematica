# A cota de esfera, verificada pelo kernel

O paper, em inglês: [PDF](paper/main.pdf). A página pública é https://genesisinnovation.io/provas/paper.

## O que o Lean aceitou, e o que ainda não é teorema.

Uma cota de cobertura só vale como teorema quando o kernel confere a conta. Esta página publica o que passou e o arquivo que produz esse passe. O que não passou não entra na lista.

## O que está provado

O espaço é `Fin n → ZMod q`, com a distância de Hamming do Mathlib. A bola de raio `R` tem tamanho `V`. Qualquer código `C` que cobre o espaço satisfaz `q^n ≤ |C| · V`. Se `V` não divide `q^n`, a desigualdade é estrita. Desses dois fatos saem oito cotas, cada uma um teorema de ponta a ponta: todo código que cobre com aquele raio tem pelo menos aquele tamanho.

| Teorema | Cota |
|---|---|
| `SPH_K5_7_2_lb` | `K_5(7,2) ≥ 215` |
| `SPH_K4_10_4_lb` | `K_4(10,4) ≥ 51` |
| `SPH_K5_9_3_lb` | `K_5(9,3) ≥ 327` |
| `SPH_K5_10_4_lb` | `K_5(10,4) ≥ 158` |
| `SPH_K5_9_5_lb` | `K_5(9,5) ≥ 12` |
| `SPH_K5_9_4_lb` | `K_5(9,4) ≥ 52` |
| `SPH_K7_8_3_lb` | `K_7(8,3) ≥ 439` |
| `SPH_K7_9_4_lb` | `K_7(9,4) ≥ 221` |

`K_7(9,4) ≥ 221` é a cota de Hamming deste comprimento. Não é um teto. Não diz que existe um código com 221 palavras.

## Como foi conferido

Lean 4.34.1 e Mathlib `v4.34.1`. `lake build` completo: 8934 jobs, 34 segundos, pico de 7,6 GB, numa máquina e2-standard-8. Nenhum `sorry` e nenhum `native_decide` na biblioteca. `#print axioms` de cada teorema final mostra no máximo `propext`, `Classical.choice` e `Quot.sound`.

O fonte é o commit `54424602` da branch `research/preco-da-impossibilidade`. O arquivo que esta página serve é esse fonte, não um resumo:

[covering-lean.tar](https://genesisinnovation.io/provas/covering-lean.tar)

Arquivos soltos, o mesmo conteúdo: [provas/lean/](https://genesisinnovation.io/provas/lean/CoveringLean.lean).

Reconstruir: `elan`, `lake exe cache get`, `lake build` dentro do tar. Evite `decide +kernel` sobre `Finset.univ` de tipos `Pi` grandes: isso pediu 17–24 GB e não faz parte do build que passou.

## O que não está provado

- Nenhum teto. Em particular, `K_7(9,4) ≤ 1351` não é teorema: o código que sustentaria esse número não está neste arquivo e não foi reconstruído.
- `K_2(6,1) ≥ 11` continua condicional. `A6d_SearchHeavy.lean` está no tar e **não compila**: a busca exaustiva no kernel estourou a memória. Enquanto `refuted 64 7 bm6 nbr6 10 0 = true` não for um teorema, a cota vale como verificação computacional, não como prova formal.
- O Lean não confere os códigos grandes palavra por palavra, nem decide se a cota é nova na literatura.
