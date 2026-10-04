# tools/exatos/k742 — inexistência em K_q(4,2) por perfis de fibras + SAT com prova LRAT

Alvo: **K_7(4,2)** (ledger: 17 ≤ K ≤ 19). Resultados e números em
`docs/exatos/FASE1_B_K742.md`. O método é o do Florath para `K_8(4,2) = 23`
(arXiv:2606.09600; repo `florath/covering-codes-lean`, commit `bbed9a6`,
`CoveringCodes/Database/Sources/OctonaryFourTwo.lean` e `data/K_8_4_2/README.md`):
lema das fibras, projeções de pares e classificadores finitos em CNF com refutação LRAT.
A divisão em perfis e a quebra de simetria abaixo são nossas.

| arquivo | o que faz |
|---|---|
| `encode.py` | lema das fibras, tipos, perfis e a CNF de cada perfil (`--listar`, `--perfil i --saida f.cnf`) |
| `canonizar.py` | o argumento de completude como algoritmo: leva qualquer código à forma normal da CNF do seu perfil |
| `rodar.py` | roda todos os perfis (CaDiCaL `--lrat` ou kissat), confere cada prova com `lrat-check` e grava uma linha JSON por perfil |
| `lrat.py` | verificador LRAT independente em Python (só RUP), para certificados pequenos e amostras |
| `lean/` | ponte para o Lean: `gerar_dados.py` (CNF + LRAT aparado de um perfil, sha256 em `manifesto.json`) e as medições do aparo; ver `docs/exatos/LEAN_K742.md` |
| `certificados/` | CNF + LRAT de `K_4(4,2) ≥ 7` (5 perfis, pequenos; conferidos nos testes) e os registros JSONL das rodadas com sha256 de cada CNF e prova |

## Enunciado

Para q, M dados, se a CNF de **todo** perfil é insatisfatível, não existe código de cobertura de
raio 2 em `Z_q^4` com M palavras, e portanto `K_q(4,2) ≥ M + 1` (um código menor completa-se até
M palavras distintas, pois M ≤ q^4).

## Lema 0 (comprimento 3, elementar)

Seja D um código de raio 1 em `Z_v^3` com M palavras e uma fibra `F(j,a)` com s palavras. Tome a
caixa B = {x : x_j = a, x_i ∉ A_i nas outras duas coordenadas}, A_i = {c_i : c ∈ F}, com
|B| ≥ (v − s)². Toda palavra de F difere de x ∈ B nas duas outras coordenadas (distância 2). Uma
palavra c ∉ F tem c_j ≠ a, logo cobre x só se coincide com x nas duas outras coordenadas: cobre
no máximo um ponto de B. Assim `(v − s)² ≤ M − s`. Como as v fibras de uma coordenada somam M,
`v · s* ≤ M`, com s* o menor s permitido. Junto com a cota de esferas isso dá
`K_6(3,1) ≥ 18` e `K_7(3,1) ≥ 21` (`encode.cota_elementar_31`; os valores verdadeiros são
`⌈v²/2⌉` = 18 e 25).

## Lema 1 (fibras de K_q(4,2))

Seja C de raio 2 em `Z_q^4`, |C| = M, e `F = F(j,a)` com |F| = s. Escolha, em cada uma das três
outras coordenadas, um conjunto S_i de q − s símbolos fora de A_i = {c_i : c ∈ F}. Para x com
x_j = a e x_i ∈ S_i, toda palavra de F está a distância 3. Quem cobre x é c ∉ F (c_j ≠ a), que
precisa coincidir com x em ≥ 2 das três outras coordenadas. Troque cada c_i ∉ S_i por um símbolo
fixo de S_i: a concordância com x não diminui, e as imagens formam um código de raio 1 em
`∏ S_i ≅ Z_{q−s}^3` com ≤ M − s palavras. Logo `K_{q−s}(3,1) ≤ M − s`.

Para q = 7 e M ≤ 18: s = 0 exigiria `K_7(3,1) ≤ 18` (falso, ≥ 21); s = 1 exigiria
`K_6(3,1) ≤ 17` (falso, ≥ 18). **Toda fibra tem ≥ 2 palavras**, só com o Lema 0. (Para a
validação em K_8(4,2), M = 22, usa-se `K_7(3,1) = 25`, como o Florath.)

## Perfis

Numa coordenada, os tamanhos das q fibras somam M e são ≥ s_min. O vetor ordenado
(decrescente) é um **tipo**. K_7(4,2), M = 17: excesso 17 − 14 = 3 sobre o mínimo 2, três tipos
(5222222, 4322222, 3332222); a menos de permutar coordenadas, **15 perfis** (multiconjuntos de 4
tipos). M = 18: excesso 4, cinco tipos, **70 perfis**.

## A CNF de um perfil (t_0, t_1, t_2, t_3)

- Variáveis `x[k][i][a]` (palavra k, coordenada i = 1..3, símbolo a), exatamente uma por (k, i).
- Coordenada 0 constante: as palavras vêm em blocos, o bloco a tem t_0[a] palavras com símbolo a.
- Fibra exata: `Σ_k x[k][i][a] = t_i[a]` (contador sequencial com equivalências).
- Projeções `P[i,j,a,b] ↔ ∨_k (palavra k tem a em i e b em j)`.
- Cobertura: para cada w ∈ Z_q^4, `∨_{i<j} P[i,j,w_i,w_j]` (distância ≤ 2 ⇔ concordar em 2
  coordenadas). São q^4 cláusulas, uma por ponto.
- Quebra de simetria: (d) dentro de cada bloco, a coordenada 1 é não decrescente; (e) na
  coordenada 1, entre símbolos a, a+1 de mesma fibra, o primeiro bloco em que a+1 aparece não é
  anterior ao primeiro em que a aparece; (f) nas coordenadas 2 e 3, entre símbolos a, a+1 de
  mesma fibra, a primeira palavra com a vem antes da primeira com a+1.

## Prova de completude (todo código cai numa instância satisfeita)

Seja C um código de cobertura com M palavras. As operações abaixo são isometrias de Hamming
(S_q em cada coordenada, S_4 nas coordenadas) ou uma reordenação da lista de palavras, e
preservam a cobertura e os tipos de fibra:

1. Pelo Lema 1, toda fibra tem ≥ s_min; cada coordenada tem um tipo; o multiconjunto é um
   perfil da lista. Permute as coordenadas para os tipos ficarem na ordem do perfil
   (a coordenada 0 recebe o tipo de menor simetria residual).
2. Em cada coordenada, renomeie os símbolos para que o símbolo a tenha fibra t_i[a]
   (ordem decrescente; empates em qualquer ordem por enquanto).
3. Ordene as palavras pelo símbolo da coordenada 0: os blocos ficam com os tamanhos t_0.
4. Coordenada 1: percorra os blocos em ordem; em cada bloco, os símbolos que aparecem pela
   primeira vez recebem, dentro da sua classe de fibra, os menores rótulos ainda livres, na ordem
   dos rótulos atuais. Dentro de cada bloco, ordene as palavras pela coordenada 1 (empates
   mantêm a ordem). Agora (d) vale por construção, e (e) vale porque os rótulos de cada classe
   foram dados em ordem de primeiro bloco, e símbolos novos de um mesmo bloco receberam rótulos
   crescentes.
5. A ordem das palavras está fixada. Coordenadas 2 e 3: percorra as palavras em ordem e dê a
   cada símbolo, na primeira aparição, o menor rótulo livre da sua classe de fibra. Isso não
   mexe nas coordenadas 0 e 1, nem nas fibras, nem na ordem; e (f) vale por construção.

As variáveis x lidas da forma normal satisfazem as cláusulas de fibra e de simetria, e as
auxiliares (contadores, P) ficam determinadas por suas definições; as cláusulas de cobertura
valem porque C cobre. Logo a CNF do perfil é satisfatível. Contrapositiva: todas UNSAT ⇒ não
existe C. `canonizar.py` implementa exatamente estes passos, e `tests/test_k742.py` confere, com
códigos embaralhados por elementos aleatórios do grupo, que a atribuição satisfaz todas as
cláusulas (e que, para códigos que não cobrem, falham só cláusulas de cobertura, exatamente uma
por ponto descoberto). Uma mutação que aperta a quebra de simetria (precedência sem respeitar a
classe de fibra) faz esses testes falharem.

## Como reproduzir

    # solvers (commits usados estão no doc da fase 1)
    git clone https://github.com/arminbiere/cadical && (cd cadical && ./configure && make)
    git clone https://github.com/marijnheule/drat-trim && (cd drat-trim && make)
    export CADICAL=$PWD/cadical/build/cadical LRAT_CHECK=$PWD/drat-trim/lrat-check
    # K_7(4,2) >= 18 (15 perfis) e >= 19 (70 perfis), com prova LRAT conferida
    python3 tools/exatos/k742/rodar.py --q 7 --M 17 --dir saida --prova -j 8
    python3 tools/exatos/k742/rodar.py --q 7 --M 18 --dir saida --prova -j 8
    # validações: K_4(4,2)=7, K_5(4,2)=11, K_8(4,2)=23 (inexistência de M-1)
    python3 tools/exatos/k742/rodar.py --q 5 --M 10 --dir v --prova
    python3 tools/exatos/k742/rodar.py --q 8 --M 22 --dir v --prova --descartar

A CNF é determinística (mesmo texto a cada geração): o sha256 de cada CNF nos JSONL de
`certificados/` confere com o que `encode.py` gera hoje.
