# Lema das fibras em geral: K_q(n, R) com R ≤ n − 2 (2026-10-04)

Continuação de `FASE1_B_K742.md` (K_7(4,2) = 19). Aqui o lema das fibras e a redução por perfis
viram uma ferramenta para qualquer (q, n) com raio R = n − 2 (`tools/exatos/fibras/`), e
medimos, célula por célula da triagem, se ela cabe no orçamento.

## Resultado

**Resumo (2026-10-05):** K_7(6,4) = 14 (∄ 13 por 8008 perfis com LRAT, e um código de 14
achado pela própria varredura de M = 14). K_7(5,3) sobe para 16–17; a prova de ∄ 16 (201 376
perfis) está em andamento, ver a linha de M = 16. K_q(4,2), q = 16…20: o método não alcança
(seção "Medições"); sondas de existência também não acharam código.

| célula | antes | depois | afirmação provada | instâncias | verificação |
|---|---|---|---|---|---|
| **K_7(5,3)** | 15–17 | **16–17** | ∄ código com 15 palavras | 1 perfil | CaDiCaL UNSAT (221 s), `lrat-check` VERIFIED, `lrat.py` VERIFICADO (prova de 1,56 GB, sha256 `9cc887c5…`), kissat UNSAT (11 min) |
| **K_7(6,4)** | 13–15 | **= 14** | ∄ código com 13 palavras; código com 14 | 8008 perfis + 1 SAT | 8008/8008 UNSAT, 8008/8008 `lrat-check` VERIFIED, amostra de 12 com `lrat.py` VERIFICADO; o código de 14 (`data/codes/q7_n6_R4_M14.txt`) passa no `tools/verify/verify` (0 de 117 649 pontos descobertos) |
<!-- LINHA_M16 -->
| K_7(5,3), M = 16 | 16–17 | (em andamento) | ∄ código com 16 palavras | 201 376 perfis | 201 375 UNSAT com `lrat-check` VERIFIED; falta 1 perfil (3322222^5), em 4953 cubos |

Status honesto, igual ao do k742: resultado **computacional com certificado** (LRAT conferido por
dois verificadores, um deles em amostra), mais os lemas abaixo, escritos à mão e testados por
máquina. Não está no Lean e não mexi no ledger.

Dependências de literatura: o Lema 1 em K_7(5,3) usa K_6(4,2) = 15 (Kéri 2011; nós também
reprovamos ∄ 14 no k742) e só a cota de Rodemich K_7(4,2) ≥ 17; em K_7(6,4) usa K_6(5,3) ≥ 12
(que o próprio Lema 1 prova: s_min = 2 em K_6(5,3) com 11 palavras, 6 · 2 > 11) e
K_7(5,3) ≥ 15 (HSPQ).

## Lema 1 (fibras, geral)

**Enunciado.** Seja C ⊂ Z_q^n um código de raio R ≤ n − 2 com M palavras, e F = F(j,a) = {c ∈ C :
c_j = a} com s = |F| < q palavras. Então

    K_{q−s}(n − 1, R − 1) ≤ M − s.

**Prova.** Para cada coordenada i ≠ j seja A_i = {c_i : c ∈ F} (|A_i| ≤ s) e escolha S_i ⊂ Z_q ∖ A_i
com |S_i| = q − s. Seja B = {x : x_j = a, x_i ∈ S_i para i ≠ j}. Toda palavra de F difere de x ∈ B
nas n − 1 outras coordenadas, e n − 1 > R: F não cobre nada de B. Quem cobre x ∈ B é c ∉ F, com
c_j ≠ a, e então d(x, c) = 1 + d'(x, c) ≤ R, onde d' é a distância nas n − 1 outras coordenadas:
d'(x, c) ≤ R − 1. Fixe σ_i ∈ S_i e φ_i : Z_q → S_i, identidade em S_i e σ_i fora. Se c_i = x_i então
c_i ∈ S_i e φ_i(c_i) = x_i: φ não diminui a concordância com nenhum x ∈ B. Logo
{φ(c restrita às coordenadas ≠ j) : c ∉ F} é um código de raio R − 1 em ∏ S_i ≅ Z_{q−s}^{n−1} com
no máximo M − s palavras. ∎

Para n = 4, R = 2 é o Lema 1 do k742 (`K_{q−s}(3,1) ≤ M − s`). Com R = 1 o lado esquerdo é
(q − s)^{n−1}. O lema só usa **cotas inferiores** da subcélula: `fib_encode.fibra_minima` pega a
melhor lb do ledger (`tools/exatos/folgas.py`, todas as fontes), e `K_v(3,1) = ⌈v²/2⌉`
(Kalbfleisch–Stanton) quando o ledger não tem.

**s_min.** É o menor s que o lema não exclui. Como as q fibras de uma coordenada somam M, se
q · s_min > M não existe código: o lema sozinho prova K ≥ M + 1.

**Lema 0 (k742).** Para K_7(4,2) o k742 deu uma prova elementar de K_6(3,1) ≥ 18 e K_7(3,1) ≥ 21.
Aqui não há análogo elementar geral: as subcélulas usadas em cada alvo estão listadas na tabela
de alvos, todas com valor da literatura (Kéri 2011) ou nosso (K_7(4,2) = 19, que **não** é
necessário em nenhum alvo abaixo: a lb 17 de Rodemich basta).

## Lema 2 (cobertura por projeções de pares, R = n − 2)

d(x, c) ≤ n − 2 ⇔ x e c concordam em ≥ 2 coordenadas. Logo C cobre x sse, para algum par i < j,
(x_i, x_j) ∈ P_ij(C) = {(c_i, c_j) : c ∈ C}. A CNF tem uma variável por (i, j, a, b), definida de
forma exata a partir das palavras, e uma cláusula de largura C(n,2) por ponto de Z_q^n.

Para R < n − 2 (ex.: K_5(9,6), R = n − 3) seria preciso projetar triplas: C(9,3) · 5³ = 10 500
variáveis e 5⁹ ≈ 2·10⁶ cláusulas de largura 84 (1,6·10⁸ literais por instância). Fora do escopo.

## Lema 3 (completude da redução por prefixo de tipos)

O **tipo** de uma coordenada é o vetor decrescente dos tamanhos das q fibras (partição de M em q
partes ≥ s_min). Ordem total dos tipos: `chave_tipo` (menor simetria residual, depois
lexicográfica). Uma **instância** fixa os tipos das k primeiras coordenadas, t_0 ≤ … ≤ t_{k−1}, e
deixa as outras livres (cada símbolo com ≥ s_min palavras). k = n é o perfil do k742;
k < n reduz o número de instâncias (C(T + k − 1, k), T = número de tipos) à custa de instâncias
mais frouxas — continua correto, porque só relaxa.

Quebra de simetria, todas isometrias de Hamming ou reordenação das palavras:

- (a) coordenadas ordenadas por `chave_tipo` (estável); (b) nas coordenadas de tipo fixo, o
  símbolo a tem fibra t_i[a];
- (c) palavras em blocos pelo símbolo da coordenada 0; (d) dentro do bloco, coordenada 1 não
  decrescente;
- (e) coordenada 1: entre símbolos a, a + 1 da mesma **classe** (mesmo tamanho de fibra; numa
  coordenada livre, todos), o primeiro bloco em que a + 1 aparece não é anterior ao de a;
- (f) coordenadas ≥ 2: entre símbolos da mesma classe, a primeira palavra com a vem antes da
  primeira com a + 1;
- (g) **novo**: colunas consecutivas ≥ 2 de mesmo tipo (ou ambas livres) em ordem
  lexicográfica (coluna i ≤_lex coluna i + 1, lida na ordem das palavras).

**Prova.** Os passos (a)–(f) são os do k742 (README de `tools/exatos/k742/`), trocando "classe de
fibra" por "classe" para cobrir as coordenadas livres, em que todos os símbolos são
intercambiáveis porque a restrição (≥ s_min) é simétrica. Para (g): depois de (f), a ordem das
palavras está fixada e cada coluna ≥ 2 foi relabelada por primeira aparição, uma operação que só
depende do conteúdo da própria coluna e da sua classe. Permutar colunas de mesmo tipo não muda a
ordem das palavras, nem as colunas 0 e 1, nem as fibras, e leva colunas relabeladas em colunas
relabeladas; então ordenar cada grupo lexicograficamente preserva (a)–(f) e dá (g). ∎

`fib_canon.py` implementa a forma normal. `tests/test_fibras.py` confere com códigos de cobertura
(gerados por guloso) embaralhados por elementos aleatórios de S_q ≀ S_n, em (q, n, k) variados: a
atribuição satisfaz todas as cláusulas; com uma palavra trocada (código que não cobre) falham só
cláusulas de cobertura, exatamente uma por ponto descoberto; e dois mutantes errados da quebra
de simetria (precedência entre classes diferentes; lexicográfica nos dois sentidos) são pegos.

## Lema 4 (ordem dos blocos de mesmo tamanho, a quebra (h))

**Enunciado.** Na forma normal pode-se exigir, além de (a)–(g): (h) para blocos consecutivos
b, b + 1 da coordenada 0 **de mesmo tamanho**, a sequência da coordenada 1 do bloco b (já não
decrescente por (d)) é ≤_lex a do bloco b + 1.

**Prova.** Símbolos da coordenada 0 com a mesma fibra podem ser permutados (isometria), o que
permuta os blocos de um mesmo grupo de tamanho e muda a relabelagem (e) da coordenada 1.
Construa a ordem por um guloso dentro de cada grupo: a cada passo, para cada bloco restante,
calcule o vetor ordenado dos rótulos que a coordenada 1 teria se ele viesse agora (rótulos já
dados ficam; símbolos novos recebem os próximos rótulos livres da sua classe) e escolha o menor
lexicograficamente. Seja v_t o vetor escolhido no passo t e Y o bloco escolhido no passo t + 1.
No passo t, o vetor de Y era u ≥_lex v_t (escolha gulosa). Depois do passo t, cada rótulo de Y só
pode crescer: rótulos já dados não mudam, e um símbolo novo de Y numa classe c recebe, no passo t
ou depois, um rótulo ≥ ao próximo livre de c no passo t; como os rótulos de uma classe são
distintos, o vetor ordenado de Y domina, componente a componente, o vetor u. Logo
v_{t+1} ≥_lex u ≥_lex v_t. Os rótulos que o guloso atribui são exatamente os de (e) na ordem
final; depois disso (d), (f), (g) se refazem sem mexer nas coordenadas 0 e 1. ∎

Em K_7(5,3) com M = 15 (coordenada 0 do tipo 3222222, um grupo de seis blocos de tamanho 2) os
padrões válidos da coordenada 1 caem de 118 710 para 380 com (h), e a instância, que o kissat não
resolvia em 20 min de CPU sem (h), sai em 221 s de CaDiCaL com prova.

`fib_canon.canonizar` implementa o guloso; `test_ordem_dos_blocos_h_precisa_do_guloso` mostra
que, sem o guloso, a forma normal viola (h) em algum código (as cláusulas restringem de verdade),
e os testes de completude passam com ele.

**Ordem da coordenada 0.** Com (h), vale pôr na coordenada 0 o tipo de **maior** simetria
residual (mais blocos iguais): `--ordem max`. Cada perfil é completo sozinho nas duas ordens
(a canonização com qualquer `chave_tipo` leva todo código daquele multiconjunto de tipos à CNF
do perfil), então uma rodada pode misturar perfis provados em ordens diferentes; o `rodar.py
--pular` usa isso, casando perfis pelo multiconjunto de tipos.

## Cubos

`fib_cubos.py` divide uma instância pela coordenada 1 das L primeiras palavras: a lista é a de
todos os prefixos de atribuições que satisfazem as cláusulas que só falam da coordenada 1
(one-hot, fibra, (d), (e), (h)); o teste confere contra força bruta. Medido em K_7(5,3), M = 15:
cubos são mais caros no total do que a instância inteira (L = 9: 3355 cubos de ~1–2 min; a
instância inteira com (h) leva 221 s), então não foram usados nos resultados. Ficam para provas
que não cabem no disco (cada cubo tem sua prova pequena).

## s_min e contagem de perfis, alvo por alvo

`python3 tools/exatos/fibras/fib_encode.py --q Q --n N --M M [--k K]` (cotas das subcélulas: melhor
lb do ledger). T = número de tipos; perfis = C(T + n − 1, n).

| célula | M | subcélula do Lema 1 (lb) | s_min | T | perfis (k = n) | k = 2 |
|---|---|---|---|---|---|---|
| K_16(4,2) 86–87 | 86 | K_12(3,1) = 72 | 4 | 983 | 3,9·10^10 | 483 636 |
| K_17(4,2) 97–99 | 97 / 98 | K_13(3,1) = 85 | 4 | 4370 / 5332 | 1,5·10^13 / 3,4·10^13 | — |
| K_18(4,2) 109–111 | 109 / 110 | K_14(3,1) = 98 | 4 | 20 040 / 23 928 | 6,7·10^15 / 1,4·10^16 | — |
| K_19(4,2) 121–123 | 121 / 122 | K_15(3,1) = 113 | 4 | 79 855 / 93 854 | 1,7·10^18 / 3,2·10^18 | — |
| K_20(4,2) 134–135 | 134 | K_16(3,1) = 128 | 4 | 332 557 | 5,1·10^20 | — |
| **K_7(5,3) 15–17** | **15** | K_6(4,2) = 15, K_7(4,2) ≥ 17 | **2** | **1** | **1** | — |
| **K_7(5,3)** | **16** | K_6(4,2) = 15 ≤ 15 | 1 | 28 | 201 376 | 406 |
| **K_7(6,4) 13–15** | **13** | K_6(5,3) = 12 ≤ 12, K_7(5,3) ≥ 15 | 1 | 11 | **8008** | 66 |
| K_7(6,4) | 14 | idem | 1 | 15 | 38 760 | 120 |
| K_8(7,5) 14–16 | 14 | K_7(6,4) ≥ 13 ≤ 13 | 1 | 11 | 19 448 | 66 |
| K_8(7,5) | 15 | K_8(6,4) ≥ 15 ≤ 15 | 0 | 146 | 3,2·10^11 | — |
| K_15(5,3) 57–59 | 57 / 58 | K_12(4,2) = 48 | 3 | 77 / 101 | 2,6·10^7 / 9,7·10^7 | — |
| K_5(9,6) 10–12 | 10 / 11 | K_4(8,5) = 8 / K_5(8,5) = 11 | 1 / 0 | 7 / 37 | 5005 / 8,9·10^8 | — |

Validação na mesma família (valores conhecidos):

| caso | esperado | saiu |
|---|---|---|
| K_5(5,3) = 9: ∄ 8 (s_min = 1, 21 perfis) | todos UNSAT | 21/21 UNSAT, `lrat-check` e `lrat.py` 21/21 (também com `--ordem max` e com cubos L = 3: 164 cubos) |
| K_5(5,3) = 9: existe 9 (126 perfis) | algum SAT | 30 SAT, os 30 códigos cobrem Z_5^5 |
| K_6(5,3) = 12: ∄ 11 | — | o Lema 1 sozinho: s_min = 2, 6 · 2 > 11 |
| K_6(5,3) = 12: existe 12 (3003 perfis, kissat) | algum SAT | 1 SAT (o perfil 222222^5), o código cobre Z_6^5; 3002 UNSAT |
| controles sem (g) e (h) em K_5(5,3), M = 8 | o mesmo UNSAT | 21/21 UNSAT com prova |
| K_q(4,2) do k742 (q = 7, M = 17, 18; q = 8, M = 22; q = 5, M = 10) | mesmo s_min e mesmos perfis | `test_lema_geral_reproduz_o_k742_em_k_q_4_2` |

## K_7(6,4) = 14: o código

Achado pela varredura de M = 14 (`rodar.py --q 7 --n 6 --M 14 --ordem max`, instância 0, perfil
2222222^6, CaDiCaL 18,6 s) e conferido três vezes: `cobre` do `rodar.py`, força bruta à parte em
Python e o verificador oficial (`tools/verify/verify -q 7 -n 6 -r 4 -m 14`, sha256 canônico
`9f2c5351…`). Fica em `data/codes/q7_n6_R4_M14.txt`; o teste
`test_codigo_k7_6_4_com_14_palavras_nao_deixa_ponto_descoberto` confere a cobertura.

    000000 011111 100011 122200 212222 221122 333333
    343444 434455 444366 555534 565643 656665 666556

As palavras vêm aos pares, e cada símbolo aparece duas vezes em cada coordenada (o perfil
2222222). Mesmo padrão de K_6(5,3) = 12 (o código SAT do perfil 222222^5 da validação), o que
sugere K_q(q−1, q−3) ≤ 2q em geral; não investiguei além disso. **Não mexi no ledger**: a
cota superior publicada era 15 (Kéri 2011) e o dono decide como registrar.

## Sonda de existência (`sonda.py`)

`rodar.py` só alcança perfis por índice. Para procurar código num perfil escolhido (o equilibrado,
que fica no meio da lista quando T é grande) há `tools/exatos/fibras/sonda.py`: mesma CNF,
prefixo dado à mão, código decodificado e conferido em Z_q^n. UNSAT de sonda não prova nada.

Rodadas desta missão (tempo-limite 1500 s cada, um núcleo, t2d/e2 spot; prefixo = k cópias
do tipo equilibrado). Nenhuma achou código; nenhuma conclusão sobre inexistência:

| célula (cota) | M | k | kissat | CaDiCaL |
|---|---|---|---|---|
| K_8(6,4) 15–19 | 16 / 17 / 18 | 6 | INDEFINIDO ×3 | INDEFINIDO ×3 |
| K_8(6,4) | 16 | 1 | INDEFINIDO | — |
| K_8(7,5) 14–16 | 14 / 15 | 7 | INDEFINIDO ×2 | INDEFINIDO ×2 |
| K_14(5,3) 50–54 | 52 / 53 | 5 | INDEFINIDO ×2 | — |
| K_15(5,3) 57–59 | 58 | 5 | INDEFINIDO | — |
| K_16(4,2) 86–87 | 86 | 2 / 4 | INDEFINIDO ×2 | INDEFINIDO (k = 4) |
| K_17(4,2) 97–99 | 97 / 98 | 4 | INDEFINIDO ×2 | — |
| K_18(4,2) 109–111 | 110 | 4 | INDEFINIDO | — |
| K_19(4,2) 121–123 | 122 | 4 | INDEFINIDO | — |
| K_20(4,2) 134–135 | 134 | 4 | INDEFINIDO | — |

Nos K_q(4,2) o equilibrado é provavelmente o perfil errado: os melhores códigos conhecidos
vêm de partição do alfabeto em 3 blocos (`tools/exatos/particao_q42.py`), com fibras desiguais.

## Medições e o que não coube

Custos medidos numa t2d-standard-8 spot (CaDiCaL 3.0.1 `c607304` com `--lrat`, `lrat-check` do
drat-trim `2e3b2dc`, kissat 4.0.4 `8af8e56`).

- **K_q(4,2), q = 16…20.** O lema dá só s_min = 4 (K_{q−4}(3,1) é muito menor que M − 4: folga
  de 10 a 16 palavras), e os perfis vão de 3,9·10^10 a 5·10^20. Mesmo a relaxação mais grossa (k
  = 1, 983 instâncias para q = 16) não serve: a instância 0 de K_16(4,2), M = 86, k = 1, ficou
  INDEFINIDA após 1200 s de kissat. Não há caminho com este método; precisaria de um lema que
  force fibras perto de q²/3/q ≈ q/3, ou de uma redução estrutural nova (partição em blocos).
- **K_8(7,5), M = 14.** 19 448 perfis, mas a CNF tem 2,2 milhões de cláusulas (8^7 pontos) e o
  kissat levou 653 s e 469 s nos dois perfis medidos: ~3000 CPU-h. Fora do orçamento.
- **K_7(6,4), M = 14.** Com `--ordem max` e CaDiCaL o primeiro perfil (2222222^6, o de maior
  simetria) saiu **SAT** em 18,6 s: o código abaixo. A amostra de 32 perfis aleatórios da ordem
  max, rodada antes, tinha dado 32 UNSAT em 1–11 s cada; a varredura parou no SAT.
- **K_15(5,3).** s_min = 3 e 2,6·10^7 perfis com CNFs de 15^5 = 759 375 cláusulas de cobertura.
  Fora.
- **K_5(9,6).** R = n − 3: a cobertura não se escreve com pares (seção do Lema 2). Fora do escopo
  desta ferramenta.
