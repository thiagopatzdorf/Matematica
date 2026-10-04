# Lema das fibras em geral: K_q(n, R) com R ≤ n − 2 (2026-10-04)

Continuação de `FASE1_B_K742.md` (K_7(4,2) = 19). Aqui o lema das fibras e a redução por perfis
viram uma ferramenta para qualquer (q, n) com raio R = n − 2 (`tools/exatos/fibras/`), e
medimos, célula por célula da triagem, se ela cabe no orçamento.

## Resultado

<!-- RESUMO -->

| célula | antes | depois | afirmação provada | instâncias | verificação |
|---|---|---|---|---|---|
| **K_7(5,3)** | 15–17 | **16–17** | ∄ código com 15 palavras | 1 perfil | CaDiCaL UNSAT (221 s), `lrat-check` VERIFIED, `lrat.py` VERIFICADO (prova de 1,56 GB, sha256 `9cc887c5…`), kissat UNSAT (11 min) |
| **K_7(6,4)** | 13–15 | **14–15** | ∄ código com 13 palavras | 8008 perfis | 8008/8008 UNSAT, 8008/8008 `lrat-check` VERIFIED, amostra de 12 com `lrat.py` VERIFICADO |
<!-- LINHA_M16 -->

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
