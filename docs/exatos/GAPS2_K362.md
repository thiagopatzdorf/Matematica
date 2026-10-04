# Fatia mínima: redução de `K_q(n,R) ≤ M` a instâncias pseudo-booleanas (2026-10-04)

Ferramenta: `tools/exatos/gaps2/` (`fatia.py`, `fatia_pb.py`, `canon_fatia.py`). Testes:
`tests/test_gaps2.py`. O alvo foi `K_3(6,2)`, aberta em 15–17: provar que não existe código com
15 palavras subiria a cota inferior para 16. Este documento traz só a redução e a prova de que
ela é completa. As medições e o resultado por célula ficam em `GAPS2_RESULTADOS.md`.

## A redução

Seja `C ⊂ Z_q^n` um código de raio de cobertura `R` com `M ≤ q^n` palavras. Pode-se supor as
palavras distintas: se houver repetição, troca-se a cópia por uma palavra que não está em `C`, e
o código continua cobrindo.

**Fibra.** `F(j,a) = {c ∈ C : c_j = a}`. Seja `s*` o menor `|F(j,a)|` sobre todo `j` e todo `a`.

**Normalização** (só isometrias de Hamming, que preservam o raio de cobertura):

1. escolha `(j,a)` com `|F(j,a)| = s*` e leve a coordenada `j` para a 0 e o símbolo `a` para o 0;
2. renomeie os outros símbolos da coordenada 0 para que os blocos `t_b = |F(0,b)|`, com
   `b = 1..q−1`, fiquem em ordem decrescente: `t_1 ≥ … ≥ t_{q−1} ≥ s*`;
3. as projeções das palavras de `F(0,0)` nas coordenadas 1..n−1 formam um conjunto `K` de `s*`
   pontos distintos de `Z_q^{n−1}`. Permutando as coordenadas 1..n−1 e os símbolos de cada uma
   (isometrias que fixam a coordenada 0), leve `K` ao representante canônico da sua classe.

**Representantes.** `fatia.configuracoes(q, m, s)` enumera um conjunto de `s` pontos por classe
de isometria de `Z_q^m`. As colunas são escritas como cadeias de crescimento restrito, que
absorvem as permutações de símbolos. O multiconjunto ordenado de colunas absorve a permutação
das coordenadas. Por fim, o mínimo sobre as ordens dos pontos é a forma canônica (`fatia.forma`).
Um conjunto e a sua forma canônica são isométricos por construção. Logo a lista tem pelo menos um
representante por classe, e a deduplicação pela forma deixa exatamente um.

**Filtro de contagem (lema da fatia).** Seja `U` o conjunto dos pontos `y ∈ Z_q^{n−1}` a
distância `> R` de todo ponto de `K`. Um ponto `x = (0, y)` com `y ∈ U` não é coberto por
nenhuma palavra de `F(0,0)`. Então é coberto por uma palavra `c` com `c_0 ≠ 0`, que já gasta uma
diferença na coordenada 0 e por isso fica a distância `≤ R − 1` de `y` nas outras coordenadas.
Cada uma das `M − s*` palavras fora de `F(0,0)` cobre no máximo `V(n−1, R−1)` pontos da fatia.
Daí

    |U| ≤ (M − s*) · V(n−1, R−1).

Configurações que violam isso são descartadas antes da forma canônica, que é a parte cara.

**Instância** `(s*, K, t)`. Para cada `s*` de 0 a `⌊M/q⌋`, cada `K` que passa no filtro e cada
`t = (t_1 ≥ … ≥ t_{q−1} ≥ s*)` com soma `M − s*`, `fatia_pb.opb` escreve um problema PB sobre
os indicadores `z_c`, um por ponto `c ∈ Z_q^n`:

| restrição | forma |
|---|---|
| cobertura | `Σ_{d(c,x) ≤ R} z_c ≥ 1` para todo `x` |
| tamanho | `Σ z_c = M` |
| fatia 0 | `z_c = 1` para `c = (0, k)` com `k ∈ K`; `z_c = 0` para os outros `c` com `c_0 = 0` |
| blocos | `Σ_{c_0 = b} z_c = t_b` para `b = 1..q−1` |
| fibras | `Σ_{c_j = a} z_c ≥ s*` para `j ≥ 1` e todo `a` (vale porque `s*` é o mínimo) |

**Completude.** Todo código normalizado como acima satisfaz todas as restrições da instância
`(s*, K, t)` que lhe corresponde, e essa instância está na lista: `K` é o representante canônico
e passa no filtro (pelo lema), e `t` está entre os blocos enumerados. Portanto, se todas as
instâncias são inviáveis, não existe código com `M` palavras.

## O que os testes conferem (`tests/test_gaps2.py`)

- A lista de representantes tem exatamente uma configuração por órbita. A conferência é contra a
  contagem de órbitas por força bruta sobre `S_q ≀ S_m`, em seis casos `(q, m, s)`.
- O filtro só descarta o que a contagem exclui: comparado com a lista sem filtro.
- `canon_fatia.normalizar` aplica a normalização acima a um código qualquer. O código transformado
  satisfaz todas as restrições do OPB da sua instância. Isso foi conferido num código de 17
  palavras de `K_3(6,2)` e no código de Hamming ternário `[4,2,3]`, cada um sob isometrias
  aleatórias. Um código que não cobre viola só restrições de cobertura. E uma normalização errada
  de propósito (blocos trocados) é recusada pelo OPB.
- Com `roundingsat` e `veripb` presentes, o pipeline PB reproduz valores conhecidos, com cada
  inviabilidade conferida pelo VeriPB: `K_3(4,1) = 9` (M = 8 inviável, M = 9 viável),
  `K_3(5,2) ≥ 8` e `K_2(6,1) ≥ 12`. Sem os binários, esses quatro testes pulam.

## Limites

- A redução escolhe **uma** fibra mínima. Quando todas as fibras têm o mesmo tamanho, sobra simetria.
  Em `K_3(6,2)` com M = 15, as instâncias com `s* = 5` são 11 000 das 12 049, e nelas as 18
  fibras têm exatamente 5 palavras:
  o mesmo código aparece em até 18 instâncias. É por isso que essas instâncias são as caras
  (ver `GAPS2_RESULTADOS.md`).
- Para alfabeto binário com n grande o filtro de contagem não corta nada (por exemplo,
  `5 · V(11,4) > 2^11`), e o número de configurações explode. Esta redução não serve para a
  família `K_2(2R+4, R)`.
