# K₃(6,2), M = 15: forma canônica independente do SAT (2026-10-05)

Código: `tools/exatos/k362/canon.py`. Testes: `tests/test_k362_nucleo.py`. Precisa do `dreadnaut`
(pacote `nauty`); sem ele os testes de nauty pulam.

## 1. Duas implementações

1. **nauty (`canon_nauty`).** Grafo colorido com três classes de vértice: um vértice por ponto, um
   por coordenada, um por par (coordenada, símbolo) ligado à sua coordenada; o ponto p liga-se a
   (i, pᵢ). Um isomorfismo que respeita as cores leva cada bloco {(i,0),(i,1),(i,2)} ao bloco de
   outra coordenada (cada par tem um único vizinho de cor "coordenada"), logo é um elemento de
   S₃ ≀ S_m mais a permutação induzida nos pontos. Os pontos são distintos, então os automorfismos
   do grafo correspondem bijetivamente a `Stab(K)`, e o `grpsize` do nauty é `|Stab(K)|`
   (PROVED pelo argumento acima; COMPUTATIONALLY_VERIFIED contra a força bruta). A forma canônica é
   a lista de adjacências do grafo canônico. Roda um processo `dreadnaut` por lote.
2. **força bruta (`canon_forca_bruta`)**: mínimo lexicográfico da imagem ordenada sobre os
   `6^m · m!` elementos. Árbitro dos testes para m = 3.

A terceira, já existente e usada pela enumeração, é `fatia.forma` (mínimo sobre ordens dos pontos
das colunas em RGS ordenadas). O nauty não compartilha código com ela.

Meta: equivalentes ⇒ mesma forma; não equivalentes ⇒ formas diferentes. A primeira metade vale para
qualquer forma canônica de verdade; a segunda é o que separa canonicalização de heurística.

## 2. O que os testes conferem (COMPUTATIONALLY_VERIFIED)

| teste | o que mede |
|---|---|
| `test_forma_do_nauty_separa_exatamente_as_classes_da_forca_bruta` | para s = 2, 3, 4 pontos em Z₃³: em 60 conjuntos sorteados, "mesma forma no nauty" ⇔ "mesma forma na força bruta" (1 770 pares por s), `|Stab|` do nauty = força bruta em 15, e o número de formas distintas entre **todos** os conjuntos = número de representantes de `fatia.configuracoes` |
| `test_forma_do_nauty_nao_muda_sob_milhares_de_transformacoes_aleatorias` | 3 000 imagens (20 conjuntos de 5 pontos em Z₃⁵ × 150 elementos aleatórios de S₃ ≀ S₅): forma e `|Stab|` idênticos |
| `test_representantes_nao_equivalentes_tem_formas_diferentes_no_nauty` | os representantes de `fatia.configuracoes(3,4,4)` (dois a dois não equivalentes) têm formas duas a duas distintas |

Erro meu registrado: a primeira versão do teste de invariância sorteava **um elemento por ponto**
em vez de um por conjunto. O teste falhou e o nauty estava certo: as "imagens" não eram isométricas
(`fatia.forma` também discordava). Corrigido; o comentário no teste diz por quê.

## 3. Banco de validação: classificar códigos inteiros

`canon.classificar(q, n, R, M)` gera códigos nível a nível (cada conjunto ramifica nas palavras que
cobrem o menor ponto descoberto do seu representante) e deduplica pela forma do nauty. A completude
está na docstring (se C cobre e S ⊂ g(C) é o representante guardado, g(C) tem uma palavra fora de S
que cobre esse ponto). Contagens publicadas (frente de literatura, PR #54) e o `motor` em C de
`tools/exatos/motor/` (canonicalização própria, outro código):

| célula | literatura | `motor --classificar` | `canon.classificar` (nauty) |
|---|---|---|---|
| K₃(4,1) = 9 | 1 classe | 1 | 1 |
| K₃(6,3) = 6 | 28 classes | 28 | ver `K3_M15_DIAGNOSIS.md` §8 |

`python3 tools/exatos/k362/canon.py 3 6 3 6` reproduz a linha de baixo.

## 4. Aplicação à lista de M = 15 (COMPUTATIONALLY_VERIFIED)

`python3 tools/exatos/k362/orbitas.py --instancias i15.json` (lista de `rodar_pb.py --listar`, 12 049
instâncias, 21 min neste container): em cada `(s*, blocos)`, o número de formas nauty distintas é
igual ao de configurações — 1, 27, 468 e **11 000 de 11 000** para s* = 2, 3, 4, 5. Logo a lista do
GAPS2 é uma por órbita sob `Stab_G({x₀ = 0})`, confirmado por implementação independente
(INDEPENDENTLY_REPRODUCED no sentido "duas implementações sem código comum concordam"; não é prova).

## 5. Limites

* A forma canônica é de **conjuntos de pontos** sob S_q ≀ S_m. Para as instâncias isso basta, porque o
  S₂ da coordenada 0 age trivialmente em K. Não é forma canônica de "instância + código parcial".
* Canonicalizar não prova nada sobre K₃(6,2); só garante que contagens de órbitas estão certas.
