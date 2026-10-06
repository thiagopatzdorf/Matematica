# Códigos de cobertura de segunda ordem: tabela exata para n pequeno

Este diretório calcula K^(2)_q(n,r), o menor número de bilhetes que garante o prêmio no
**bolão de segunda ordem** de Elimelech e Schwartz, para q = 2 com n ≤ 6 e q = 3 com n ≤ 5,
em todo 1 ≤ r < n. É um problema irmão do bolão clássico K_q(n,R) do ledger, e **não entra nas
contagens do ledger** (nada aqui lê ou escreve em `ledger/`, a não ser a leitura de cotas
publicadas de K_q e K_{q²} em `ledger/cells.json`).

## O problema em palavras: partida e revanche

No bolão clássico há n jogos, cada um com q resultados possíveis; um bilhete é um palpite para os
n jogos, e ganha quem acerta pelo menos n − r. K_q(n,r) é o menor número de bilhetes que garante
um bilhete premiado.

Na versão de segunda ordem cada jogo tem **partida e revanche**, cada uma com q resultados. O
apostador compra bilhetes comuns (um palpite por jogo, como antes), mas pode usar **dois**
bilhetes, um para as partidas e outro para as revanches (pode ser o mesmo bilhete duas vezes).
Ele acerta o jogo i se o primeiro bilhete acerta a partida i **e** o segundo acerta a revanche i.
Ganha quem acerta pelo menos n − r jogos. K^(2)_q(n,r) é o menor número de bilhetes que garante a
vitória contra qualquer resultado.

## Definições

* C ⊆ Z_q^n é o conjunto de bilhetes (o código).
* O 2-peso de uma matriz 2×n é o número de colunas não nulas.
* C^2 é o conjunto das matrizes 2×n cujas duas linhas são palavras de C (a mesma palavra pode
  aparecer nas duas linhas).
* R_2(C) = max sobre (u1,u2) ∈ (Z_q^n)^2 de min sobre (c1,c2) ∈ C×C de
  |supp(u1−c1) ∪ supp(u2−c2)|.
* K^(2)_q(n,r) = min |C| com R_2(C) ≤ r.

Fonte: D. Elimelech e M. Schwartz, *The Second-Order Football-Pool Problem and the Optimal Rate
of Generalized-Covering Codes*, arXiv:2210.00531 (versão de conferência no ISIT 2023). O artigo
resolve a taxa assintótica, κ_2(ρ,q) = 1 − H_{q²}(ρ), e **não traz valores para n pequeno**.

## Cotas que saem de graça (com prova curta)

**Isometria das colunas.** Leia a matriz 2×n (u1;u2) como um vetor de comprimento n sobre o
alfabeto Z_q^2: a coluna i vira o símbolo (u1_i, u2_i). O 2-peso da matriz é o peso de Hamming
desse vetor, então o espaço das matrizes com a 2-métrica é isométrico a H(n, q²). Sob esse mapa,
C^2 vira o código C⊗C = {((c1_i, c2_i))_i : c1, c2 ∈ C}, com exatamente |C|^2 palavras, e
**R_2(C) é o raio de cobertura comum de C⊗C em H(n, q²)**. Isso dá:

* **(a) cota pela raiz.** Se R_2(C) ≤ r, C⊗C cobre H(n, q²) com raio r, logo
  |C|^2 = |C^2| ≥ K_{q²}(n,r) e K^(2)_q(n,r) ≥ ⌈√K_{q²}(n,r)⌉. Os valores (ou cotas inferiores)
  de K_4 e K_9 vêm do ledger, só leitura.
* **Esfera.** As |C|^2 bolas de raio r cobrem os q^{2n} pontos:
  |C|^2 · V ≥ q^{2n}, com V = Σ_{i≤r} C(n,i)(q²−1)^i.
* **(b) primeira ordem.** R(C) ≤ R_2(C) ≤ 2R(C). A primeira desigualdade: tome u1 = u2 = u a
  distância R(C) de C; para quaisquer c1, c2, a união dos suportes contém supp(u−c1), que tem
  pelo menos R(C) elementos. A segunda: escolha c1, c2 os mais próximos de u1, u2. Logo
  K^(2)_q(n,r) ≥ K_q(n,r) e K^(2)_q(n,2s) ≤ K_q(n,s).

**Teorema das q palavras (as células triviais).** Para 1 ≤ r ≤ n:

* K^(2)_q(n,r) = 1 se e só se r = n (uma palavra só deixa o par (u1,u2) que discorda dela em
  todas as coordenadas, nas duas linhas, a distância n).
* Com menos de q palavras, em cada coordenada falta um símbolo; o par u1 = u2 = "símbolo que
  falta em cada coordenada" fica a distância n. Logo K^(2)_q(n,r) ≥ q para todo r < n.
* Com exatamente q palavras, **min R_2(C) = n − ⌈n/q²⌉**, atingido pelas q palavras constantes.
  Prova: chame de cheia uma coordenada onde as q palavras usam os q símbolos. Numa coordenada
  não cheia o adversário põe, nas duas linhas, um símbolo que falta: ela nunca é acertada. Numa
  coordenada cheia i, cada coluna (u1_i,u2_i) é acertada por exatamente um par ordenado de
  palavras (c1,c2); o adversário distribui as colunas das coordenadas cheias o mais
  uniformemente possível entre os q² pares, e nenhum par acerta mais que ⌈n/q²⌉ colunas. Para
  as palavras constantes o par (a…a, b…b) acerta todas as colunas iguais a (a,b), e alguma coluna
  se repete pelo menos ⌈n/q²⌉ vezes (casa dos pombos).
* Portanto **K^(2)_q(n,r) = q exatamente quando n − ⌈n/q²⌉ ≤ r ≤ n − 1**, e K^(2)_q(n,r) > q
  abaixo disso. Na faixa da tabela: q = 2 dá r ≥ n − ⌈n/4⌉ (r = n−1 sempre, e também r = n−2 para
  n ≥ 5); q = 3 dá só r = n − 1 (para n ≤ 9).

Esse teorema é conferido por força bruta em `tests/test_segunda_ordem.py`.

**Construções e monotonia.**

* C = Z_q^{n−r} × {0}^r tem R_2 ≤ r: K^(2)_q(n,r) ≤ q^{n−r}.
* Para r = 1, o código de paridade {c : Σc_i ≡ 0 (mod q)} também tem q^{n−1} palavras e R_2 = 1:
  toda palavra está a uma troca do código **em qualquer coordenada escolhida**, então as duas
  linhas usam a mesma coordenada.
* Furar uma coordenada não aumenta R_2: K^(2)_q(n−1,r) ≤ K^(2)_q(n,r). Acrescentar uma coordenada
  fixa aumenta R_2 em no máximo 1: K^(2)_q(n+1,r+1) ≤ K^(2)_q(n,r).

## Tabela

TABELA_AQUI

Leitura: um número só é valor **exato** (as duas cotas conferidas); `a–b` é intervalo. Estado de
cada célula, com a origem de cada cota, em `segunda_ordem/dados/tabela.json`.

ESTADO_AQUI

## Como as cotas foram obtidas

**Verificadores** (`raio2.py`). `r2_bruto` é a definição ao pé da letra em Python puro (para cada
par (u1,u2), mínimo sobre todos os pares de palavras do tamanho da união dos suportes).
`r2_rapido` usa a isometria das colunas e faz busca em largura com várias fontes em H(n, q²).
Os dois são comparados em códigos aleatórios nos testes, e toda testemunha pequena o bastante
é reconferida pelos dois. Uma terceira formulação, por projeções, é usada na busca e na
codificação booleana: R_2(C) ≤ r se e só se, para todo par (u1,u2), existe um conjunto S de n−r
coordenadas em que u1|_S e u2|_S são projeções de palavras de C. Ela também é comparada com o
verificador exato nos testes.

**Cotas superiores** (`busca.py`). Recozimento simulado com troca de uma palavra, custo = número
de pares (u1,u2) descobertos. Toda testemunha está em `dados/testemunhas.json` (palavras com a
coordenada 1 à esquerda) e é reconferida por `python3 -m segunda_ordem.tabela conferir`.

**Cotas inferiores** (`codificacao.py`). A pergunta "existe C com |C| ≤ M e R_2(C) ≤ r?" vira uma
fórmula booleana pela formulação por projeções (variáveis x_c, y_{S,a}, z_{S,{a,b}}, só
implicações "para baixo"; ver o docstring). Sempre se fixa 0 ∈ C, sem perda (translação é
isometria). Dois caminhos com certificado:

* **VeriPB**: RoundingSat minimiza Σ x_c com log de prova, e VeriPB 3.0.2 confere
  `VERIFIED BOUNDS M <= obj <= M`. Sem outra quebra de simetria.
* **DRAT**: com a quebra de simetria lex-leader (x ≥_lex g(x) para as transposições de
  coordenadas e as transposições de dois símbolos numa coordenada), CaDiCaL refuta |C| ≤ M−1 e
  drat-trim confere a prova (`s VERIFIED`). A quebra é correta pelo argumento padrão de
  Crawford–Ginsberg–Luks–Roy (1996): em cada órbita, o vetor lexicograficamente máximo satisfaz
  todas essas restrições ao mesmo tempo. Ela não é derivada dentro da prova DRAT: o certificado
  vale para a fórmula com a quebra, e a passagem para a fórmula original é esse lema. Os testes
  conferem, em células pequenas, que a quebra não muda o mínimo.

Os registros (sha256 da fórmula e da prova, tamanho, método) estão em `dados/certificados.json`.
Provas pequenas vão comprimidas em `dados/provas/`; as grandes não cabem no repositório e são
refeitas pelo comando abaixo (o sha256 registrado é o da nossa execução; RoundingSat e CaDiCaL
não prometem prova byte a byte igual entre versões).

## Como reproduzir

    python3 -m segunda_ordem.tabela conferir        # reconfere testemunhas e cotas (segundos)
    python3 -m segunda_ordem.tabela gerar           # regrava dados/tabela.json
    python3 -m pytest -q -p no:cacheprovider tests/test_segunda_ordem.py

Certificados de cota inferior (precisam dos binários; caminhos por variável de ambiente):

    ROUNDINGSAT=... VERIPB=... python3 -m segunda_ordem.tabela veripb 2 5 1
    CADICAL=... DRAT_TRIM=... python3 -m segunda_ordem.tabela drat 3 4 2

RoundingSat (commit d4edbf7), VeriPB 3.0.2, CaDiCaL (master de 2026-10) e drat-trim (master) foram
os usados aqui. `SEGUNDA_ORDEM_TRABALHO` escolhe a pasta das fórmulas e provas (padrão
`segunda_ordem_trabalho/`, fora do git).

## Literatura (revisão de 2026-10-06)

Busca em OpenAlex, Consensus e arXiv por "generalized covering radius", "second-order covering
codes" e "football pool second order", mais as obras que citam o artigo-fonte.

* Elimelech–Firer–Schwartz, *The generalized covering radii of linear codes*, IEEE TIT 67(12),
  2021 (arXiv:2012.06467): definem R_t para códigos **lineares** e dão cotas assintóticas; o único
  valor concreto de comprimento pequeno é o Exemplo 3 (Hamming: R_t = t). Conferimos: o
  [7,4] de Hamming tem R_2 = 2 pelos nossos verificadores (teste no repositório).
* Elimelech–Schwartz, arXiv:2210.00531 (ISIT 2023): taxa ótima assintótica para t = 2, sem
  tabela.
* Li–Shangguan–Wei, arXiv:2608.24856 (2026): estende a taxa ótima a todo t e a códigos lineares;
  assintótico, sem tabela.
* Yu–Schwartz, arXiv:2609.14477 (2026): raios de empacotamento × cobertura generalizados; sem
  tabela de K^(2).
* A linha de BCH, Reed–Muller, Melas e Zetterberg (Yohananov–Schwartz, Özbudak–Öztürk,
  Xiong–Yip, Li–Xiong, e outros, 2022–2026) calcula R_2 de **famílias lineares** específicas de
  comprimento 2^m − 1 ou parecido, não o mínimo sobre todos os códigos.

**Não achei nenhuma tabela de K^(2)_q(n,r) para n pequeno, nem para códigos lineares.** Pelo que
foi revisado, os valores daqui são plausivelmente os primeiros publicados. Isso não prova que
não existam em outro lugar (teses, anais sem indexação, bases pagas não foram consultadas).

## O que NÃO se afirma aqui

* Nada sobre K_q(n,R) do ledger: os números deste diretório são de outro problema.
* Nenhuma célula em intervalo é afirmada exata, por mais forte que pareça a evidência da busca
  (o recozimento falhar abaixo de um tamanho não prova nada).
* As cotas inferiores da raiz e de K_q herdam o estado das cotas do ledger, que para essas
  células pequenas são valores da literatura (Kéri e anteriores), não certificados nossos.
* Os certificados DRAT valem para a fórmula com quebra de simetria; a ponte para a fórmula
  original é o lema lex-leader, não uma prova verificada por máquina.
* A codificação booleana e o contador sequencial do PySAT são confiados como corretos por
  teste (o mínimo SAT bate com a força bruta em células pequenas), não por prova formal.
