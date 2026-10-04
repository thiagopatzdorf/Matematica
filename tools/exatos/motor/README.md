# tools/exatos/motor — busca exaustiva de K_q(n,R) com rejeição de isomorfos

Fase 0 da campanha de valores exatos (`docs/exatos/TRIAGEM_2026-10-04.md`). Resultados, números e
a decisão sobre a fase 1 estão em `docs/exatos/FASE1_A.md`.

Pergunta que o motor responde: **existe C ⊂ Z_q^n com |C| ≤ M e raio de cobertura ≤ R?**
Também classifica códigos ótimos (conta as classes de equivalência) e conta códigos rotulados
sem simetria, que é o que os testes usam para conferir o motor contra ele mesmo e contra a
literatura.

Como nos outros scripts de `tools/exatos`, um `NAO_EXISTE` daqui é **evidência computacional,
não prova**. Para virar teorema falta o certificado conferido de forma independente (ver
`FASE1_A.md`, seção "Caminho para o Lean").

## Compilar e rodar

    sudo apt-get install -y libnauty-dev          # nauty 2.8.8 (Ubuntu 24.04)
    make -C tools/exatos/motor                    # gera tools/exatos/motor/motor

    motor Q N R M --D d [--corte K] [--cert ARQ]  # existência: topo até o nível d, fundo DFS
    motor Q N R M --classificar                   # classes de códigos ótimos de tamanho M
    motor Q N R M --ingenuo                       # contagem rotulada (sem simetria)
    motor Q N R M --D d --estimar P               # estimador de Knuth do fundo (P sondas)
    motor Q N R M --D d --reps-out ARQ            # grava os representantes do nível d
    motor Q N R M --reps-in ARQ --parte i/P       # fundo só nos representantes j ≡ i (mod P)

Outras opções: `--ordem inv` (ponto de ramificação do topo = maior índice descoberto, para uma
segunda execução com outra árvore), `--sem-dual` (desliga a poda iv), `--metodo-ganho 0|1|2`
(força o método de cálculo dos ganhos; todos dão o mesmo número, os testes conferem),
`--semente S` (estimador).

Código de saída: 0 = `NAO_EXISTE` (ou modo de contagem), 10 = `EXISTE` (o código vai para a
saída padrão, uma palavra por linha, no formato de `tools/verify/verify`), 2 = erro de uso.

Limites: `q^n ≤ 65536` e `M + n·q + n ≤ 64` (o grafo do nauty cabe numa palavra de 64 bits).

## Algoritmo

Notação: `B(c)` é a bola de raio R em torno de c, `U(S)` os pontos descobertos por S,
`G = S_q ≀ S_n` (permutações de coordenadas e, em cada coordenada, de símbolos), `|G| = q!^n·n!`.
G é o grupo de isometrias do espaço de Hamming, então preserva "ser código de cobertura de
raio R com M palavras".

**Topo (níveis 1..D), busca em largura com formas canônicas.** O nível 1 é `{canon({0})}`. Para
cada representante S do nível k, escolhe um ponto descoberto `p = f(S)` (o de menor índice, ou o
de maior índice com `--ordem inv`) e gera os filhos `canon(S ∪ {w})` para todo `w ∈ B(p)`.
Filhos com a mesma forma canônica entram uma vez só (tabela de hash). Filho que cobre tudo
encerra a busca com `EXISTE`.

**Forma canônica.** Para um conjunto S de k palavras, monta o grafo colorido com três classes
de vértices: palavras (k), pares (coordenada j, símbolo a) (n·q) e coordenadas (n). A palavra i
liga-se a (j, s_i[j]) e cada (j, a) liga-se a j. O nauty devolve a rotulação canônica. A forma
canônica é o conjunto de palavras lido do grafo canônico: a coordenada nova de j é a posição do
vértice j na sua classe, e o símbolo novo de (j, a) é a ordem de (j, a) entre os pares da mesma
coordenada. Como isso é lido só do grafo canônico, duas entradas equivalentes dão a mesma
forma. Os automorfismos do grafo colorido são exatamente os elementos de G que preservam S:
um automorfismo permuta coordenadas e, dentro de cada coordenada, símbolos, e palavras
distintas têm vizinhanças distintas, então a ação nas palavras fica determinada.

**Fundo (níveis > D), busca em profundidade sem simetria**, a partir de cada representante do
nível D: escolhe o ponto descoberto com menos centros permitidos, tenta os centros permitidos
da bola dele em ordem de ganho decrescente e, depois de tentar c, proíbe c nos irmãos
seguintes.

### Por que é completo (prova)

Seja C um código de cobertura com |C| ≤ M.

1. *Topo.* Afirmação: para todo nível k alcançado, existe um representante S_k do nível k e
   g ∈ G com S_k ⊆ g(C). Para k = 1: G é transitivo, então algum g leva uma palavra de C em 0, e
   `canon({0})` é imagem de `{0}`. Passo: S_k ⊆ g(C) e S_k não cobre tudo; então
   `p = f(S_k)` é descoberto por S_k e coberto por g(C), logo existe `w ∈ g(C) ∩ B(p)`, com
   `w ∉ S_k`. O filho `S_k ∪ {w} ⊆ g(C)` é gerado, e sua forma canônica `h(S_k ∪ {w})` está
   no nível k+1 e é subconjunto de `hg(C)`. A escolha de p só depende de S_k, que é o
   representante armazenado; por isso não importa por qual caminho S_k foi alcançado.
2. *Fundo.* Invariante: no nó (X, F) da DFS do representante S, se existe código C' ⊇ X com
   |C'| ≤ M e C' ∩ F ⊆ X, ele (ou outro código) é achado no subárvore. Prova: p é descoberto por
   X, então C' tem algum centro em B(p) que não está em F; seja c o primeiro deles na ordem dos
   candidatos. Os irmãos anteriores proíbem só centros fora de C', então no filho c a invariante
   vale de novo para C'. Nada de C' é perdido.
3. As podas abaixo só descartam nós sem completação; o corte por ordem descarta nós cujas
   completações já foram exploradas em outro representante.

Juntando: se existe código, algum representante do nível D é subconjunto de uma imagem dele e
a DFS desse representante acha um código. Logo `NAO_EXISTE` só sai se não existe código.

### As podas e por que cada uma é correta

Em todo nó com l palavras ainda livres e u = |U| pontos descobertos:

- **(i) contagem:** se `l·|B| < u`, corta. Cada palavra nova cobre no máximo |B| pontos.
- **(ii) soma dos l maiores ganhos:** ganho(c) = |B(c) ∩ U|. Se a soma dos l maiores ganhos entre
  os centros permitidos é menor que u, corta. As l palavras novas são centros permitidos
  distintos, e juntas cobrem no máximo a soma dos seus ganhos, que é no máximo a soma dos l
  maiores.
- **(iii) ponto sem centro:** se algum ponto descoberto não tem centro permitido na bola, corta.
  Nenhuma completação o cobre.
- **(iv) cota dual:** para cada ponto descoberto x, seja `mg(x)` o maior ganho de um centro
  permitido que cobre x, e `y_x = 1/mg(x)`. Para todo centro permitido c,
  `Σ_{x ∈ B(c) ∩ U} y_x ≤ |B(c) ∩ U| · (1/ganho(c)) = 1`, porque `mg(x) ≥ ganho(c)` para todo
  x ∈ B(c). Se C' cobre U com centros permitidos, então
  `Σ_x y_x ≤ Σ_{c ∈ C'} Σ_{x ∈ B(c) ∩ U} y_x ≤ |C'|` (dualidade fraca da cobertura fracionária).
  Se `Σ_x y_x > l` (com folga de 1e-6 contra arredondamento), corta.
- **No topo** valem (i), e (ii) quando l ≤ 3, sem proibições (todo centro é permitido). Desligar a
  poda (ii) no topo só aumenta o número de representantes, nunca muda a resposta.

**Corte por ordem (`--corte K`).** Os representantes do nível D são numerados (ordem
lexicográfica das formas canônicas). Na DFS do representante j, quando um filho X (com |X| ≤ K)
contém um subconjunto de D palavras cuja forma canônica é o representante i < j, o filho é
descartado e o centro novo fica proibido nos irmãos seguintes. Correção: seja C um código e j*
o menor índice tal que C tem um D-subconjunto equivalente a S_{j*} (existe, pelo item 1). Na
DFS de S_{j*}, a imagem g(C) ⊇ S_{j*} não tem D-subconjunto equivalente a S_i com i < j*, então
nenhum nó X ⊆ g(C) é cortado, e todo centro cortado está fora de g(C), o que preserva a
invariante do item 2. Só se testam os D-subconjuntos que contêm o centro novo: os outros já
foram testados no pai.

## Ganhos: três métodos, mesmo número

`ganho(c) = |B(c) ∩ U|` para toda palavra c:

- **q = 2, 4 ou 8:** o índice `Σ s_k q^k` é a concatenação dos bits dos dígitos, então a soma
  dígito a dígito no grupo `(Z_2)^{log q}` é o XOR dos índices e `B(c) = c ⊕ B(0)`. O vetor de
  ganhos é a convolução-XOR de `1_U` com `1_{B(0)}`, calculada com a transformada de
  Walsh–Hadamard em inteiros (exata).
- **poucos descobertos:** soma 1 em todo centro da bola de cada ponto descoberto.
- **caso geral:** popcount de `B(c) AND U`.

O teste `test_metodos_de_ganho_dao_a_mesma_arvore` confere que os três geram a mesma árvore
(mesmo número de nós).

## Certificado reexecutável

`--cert ARQ` grava uma linha por representante do nível D: índice, as D palavras (índices em
base q, little-endian, como no `verify`) e o número de nós do fundo, mais o total. Com
`--reps-out` / `--reps-in --parte i/P` os representantes viram unidades de trabalho
independentes: os testes conferem que a soma das partes dá o mesmo total de nós que a
execução única.

## Testes

`python3 -m pytest -q tests/test_motor_exatos.py` (alguns segundos): compila o motor e confere

- classificação contra o número de códigos ótimos inequivalentes das tabelas do Kéri
  (`n_optimal` do ledger);
- soma das órbitas `Σ |G|/|Aut(C)|` igual à contagem rotulada sem simetria;
- existência em M = K e inexistência em M = K − 1 em várias células, com D, corte, ordem e poda
  dual variando, e contra o `dfs_cover.c` (implementação independente, sem simetria);
- equivalência dos três métodos de ganho e da execução em partes.
