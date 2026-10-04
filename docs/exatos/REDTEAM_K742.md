# Red team: K_7(4,2) = 19 (2026-10-04)

Revisão adversarial da afirmação de `docs/exatos/FASE1_B_K742.md` e de `tools/exatos/k742/`
(PR #18). O objetivo era **quebrar** a prova, não confirmá-la. Scripts desta revisão:
`tools/exatos/k742/redteam/` (nenhum deles muda o codificador; os independentes não importam
nada de `tools/exatos/k742`).

**Veredito: não achei erro.** Nenhum contraexemplo, nenhum perfil faltando, nenhuma cota errada,
nenhuma solução perdida pela quebra de simetria. A cota inferior K_7(4,2) ≥ 18 foi confirmada por
uma codificação inteiramente independente; K_7(4,2) ≥ 19 foi confirmada pela codificação do repo
com e sem a parte delicada da quebra de simetria, com provas LRAT regeneradas e conferidas aqui.
Confiança: alta para "a afirmação é verdadeira"; o que falta para ser teorema está no fim.

## 1. A prova escrita, linha a linha

| peça | conferido | resultado |
|---|---|---|
| Lema 0 (comprimento 3) | caixa B com \|B\| ≥ (v−s)²; palavra fora de F cobre ≤ 1 ponto de B; (v−s)² − (M−s) é decrescente em s < v, então o mínimo s* é bem definido; v·s* ≤ M | correto. v = 6, M = 17: s ≤ 2 dá 16 > 15, logo s ≥ 3 e 6·3 = 18 > 17 ⇒ **K_6(3,1) ≥ 18**. v = 7, M = 20: s ≥ 3 e 21 > 20 ⇒ **K_7(3,1) ≥ 21** |
| Lema 1 (fibras) | \|A_i\| ≤ s garante q − s símbolos livres; palavras de F ficam a distância 3; trocar c_i ∉ S_i por um símbolo de S_i não reduz a concordância (c_i ≠ x_i antes); imagem é código de raio 1 em Z_{q−s}^3 com ≤ M − s palavras | correto, vale também para multiconjuntos |
| s_min = 2 para q = 7, M ≤ 18 | s = 0 exige K_7(3,1) ≤ M ≤ 18: falso **só pela cota de esferas** (343/19 > 18). s = 1 exige K_6(3,1) ≤ 17: falso pelo Lema 0 | correto e elementar. `fibra_minima` usa ⌈v²/2⌉ (valor da literatura), mas dá o mesmo s_min; o teste `test_lema_das_fibras_de_k7_m18_so_precisa_de_cotas_elementares` cobre isso |
| enunciado (M ≤ q^4, completar até M distintas) | um código de cobertura com < 18 palavras completa-se com palavras distintas até 18, e o Lema 1 vale para ele | correto. A rodada M = 17 é logicamente redundante (M = 18 basta), mas serve de controle |
| perfis | enumerei as partições por força bruta (`perfis_indep.py`) | M = 17: 3 tipos, **15** perfis; M = 18: 5 tipos, **70**; q = 5, M = 10: 7 tipos, 210. Iguais, conjunto a conjunto, ao `encode.py --listar`, sem duplicata |
| distância ≤ 2 ⇔ concordar em ≥ 2 | d = 4 − (nº de concordâncias); concordar em ≥ 2 ⇔ algum par (i, j) com (w_i, w_j) ∈ P_ij(C) | correto. A cobertura é exata nos dois sentidos (teste do repo + o teste de órbita abaixo com cláusulas de cobertura) |
| contador sequencial `exatamente` | r[i][j] ↔ r[i−1][j] ∨ (r[i−1][j−1] ∧ x_i); unidades finais ≥ k e ¬ ≥ k+1 | correto (equivalências completas) |
| projeções P | i = 0: P ↔ ∨_{k no bloco a} x[k][j][b]; i ≥ 1: y ↔ x ∧ x, P ↔ ∨ y | correto |
| palavras repetidas | a CNF permite repetição: é relaxação, não perde nada | correto |
| quebra de simetria (d)–(f) | ver abaixo | correta |

**Quebra de simetria, argumento independente.** O grupo usado é S_7 em cada coordenada × S_4 nas
coordenadas × reordenação das palavras. (a)–(c) só fixam a ordem das coordenadas, a ordem dos
símbolos por fibra e a ordem das palavras por bloco: óbvio. Para (d)–(f) basta exibir, para todo
código, um elemento da órbita que satisfaz as três:

- coordenada 1: percorrendo os blocos em ordem, rotular os símbolos novos de cada bloco com os
  menores rótulos livres **da sua classe de fibra**, em ordem crescente. Como toda fibra tem ≥ 2,
  todo símbolo aparece, então isso é uma bijeção dentro de cada classe (preserva as fibras).
  O primeiro bloco de aparição fica monótono no rótulo dentro da classe ⇒ (e). Ordenar as
  palavras dentro do bloco pela coordenada 1 ⇒ (d), sem mexer em (e) (que só olha blocos);
- coordenadas 2 e 3: com a ordem das palavras já fixa, rotular por primeira aparição dentro da
  classe. Cada palavra introduz no máximo um símbolo novo por coordenada, então a primeira
  aparição de a vem **estritamente** antes da de a+1 ⇒ (f). Não mexe em coordenadas 0 e 1, nem
  em fibras, nem na ordem.

As três restrições usam variáveis disjuntas no que importa ((e) depende só de blocos, não da
ordem dentro do bloco; (f) só da ordem final), então não há conflito entre elas. É exatamente o
README e o `canonizar.py`. Não achei caso de borda: o único seria fibra 0 (símbolo que nunca
aparece), que não ocorre com s_min ≥ 1.

## 2. Testes empíricos independentes

| teste | o que mede | resultado |
|---|---|---|
| **Reprodução dos 85 certificados** (CaDiCaL 3.0.1 `c6073042`, drat-trim `2e3b2dc`, compilados aqui) | as CNFs e provas do repo | 85/85 CNF com o mesmo sha256 do JSONL; **85/85 LRAT bit a bit iguais**; 85/85 `lrat-check` VERIFIED. 117 s (M = 17) + 576 s (M = 18) de solver |
| **Órbita por SAT** (`orbita.py`; não usa `canonizar.py`) | para um código C, a CNF do perfil + variáveis de grupo (permutação de palavras, permutação de símbolos por coordenada, coordenadas compatíveis com o perfil) tem de ser SAT | códigos aleatórios com fibras ≥ s_min: q = 7, M = 17: **600/600**; M = 18: **600/600**; q = 6, M = 14: 200/200; q = 5, M = 10: 300/300; q = 4, M = 6: 200/200 |
| poder do teste de órbita (`mutantes.py`) | quatro apertos errados da quebra de simetria, 100 códigos de M = 18 | (f) sem classe de fibra: 84 falhas; (e) sem classe: 44; (e) estrita: 87; (d) estrita: 81. Controle: (f) também na coordenada 1 (que é implicada por (d)+(e)) dá 0 falhas, como o argumento prevê |
| órbita com cobertura | códigos que cobrem, achados pela codificação independente, com as cláusulas de cobertura ligadas | q = 4, M = 7: 13/13; q = 5, M = 11: **68/68** (12 perfis); q = 7, M = 19 (partição 1+3+3): 3/3 |
| **perfil a perfil, repo × independente** (`compara.py`) | se a quebra de simetria perdesse códigos, haveria perfil SAT no independente e UNSAT no repo | q = 4, M = 6: 5/5 UNSAT nos dois; M = 7: 15 perfis, os mesmos 5 SAT; q = 5, M = 10: 210/210 UNSAT nos dois (⇒ **K_5(4,2) ≥ 11** confirmado de forma independente); **q = 5, M = 11: 715 perfis, os mesmos 12 SAT e 703 UNSAT, 0 desacordos** |
| controle sem (d)–(f) (`semquebra.py`, CaDiCaL 1.9.5 do pysat, outro solver/versão) | o resultado não depende da parte delicada | M = 17: 15/15 UNSAT (94 s); **M = 18: 70/70 UNSAT** (763 s, maior 175 s) |
| **K_7(4,2) ≥ 18 independente** (`indep.py`) | variável x_w por palavra de Z_7^4 (2401), cobertura pela bola de raio 2 (distância direta, sem projeções), fibras exatas com totalizador do pysat, só renomeação por fibra + lex-leader x ≤_lex g(x) para transposições de símbolos vizinhos de mesma fibra e trocas de coordenadas de mesmo tipo (válido: as restrições são invariantes por esses g e o lex-mínimo da órbita satisfaz todas) | **15/15 perfis UNSAT** ⇒ **K_7(4,2) ≥ 18 confirmado de forma independente**. CaDiCaL 1.9.5 (pysat), 30 724 s de CPU somados (maior perfil 4 043 s, menor 337 s), sem prova LRAT (é segunda opinião, não certificado). `resultados/indep_q7_M17.jsonl` |
| cota superior | construção por partição refeita aqui (`cod19.py`): {0000} ∪ MDS[4,2,3]_3 em {1,2,3} ∪ o mesmo em {4,5,6} | 19 palavras distintas, 0 pontos descobertos em Z_7^4 |

A codificação independente foi validada antes de ser usada para afirmar inexistência: reproduz
K_4(4,2) = 7 e K_5(4,2) = 11 nos dois sentidos (UNSAT em M − 1, os mesmos perfis SAT em M), e o
lex-leader não muda o conjunto de perfis SAT de q = 4, M = 7 (com e sem: os mesmos 5).

## 3. O que não consegui fazer

- **(b) para q = 6**: a codificação independente por perfil leva ~8 s por perfil em q = 6 e
  K_6(4,2) ≥ 15 tem 8855 perfis (~20 h de CPU); o modo global (sem perfis, lex-leader nos
  geradores de S_6 ≀ S_4) não terminou em 10 min nem para q = 5. Ficou só a reprodução do repo.
- **K_6(3,1) ≥ 18 por SAT**: a busca ingênua não terminou nem K_5(3,1) ≥ 13 em 25 min. Não é
  necessário: o Lema 0 dá a cota à mão, e eu a conferi.
- **K_7(4,2) ≥ 19 independente**: M = 18 tem 70 perfis; no ritmo de M = 17 (~34 min por perfil), seriam
  ~1 dia de CPU. Para M = 18 a evidência é a codificação do repo (com prova LRAT reproduzida e,
  sem (d)–(f), com outro solver), mais os testes de completude acima.

## 4. Observações menores (não invalidam)

1. `fibra_minima` chama `k_v31` (= ⌈v²/2⌉, valor da literatura) e não `cota_elementar_31`. Para
   K_7 com M ≤ 18 o resultado é o mesmo, e há teste; mas seria mais limpo passar a cota como
   parâmetro, para que a afirmação "só cotas elementares" esteja no caminho do código.
2. A rodada M = 17 não é necessária para K ≥ 19 (completar até 18 palavras); vale como controle.
3. `lrat.py` aceita dica já satisfeita (pula) e não suporta RAT: é mais leniente que o necessário
   mas correto (cada passo aceito é RUP). A garantia principal é o `lrat-check`.

## 5. Grau de confiança e o que falta

- **K_7(4,2) ≥ 18**: duas codificações independentes (variáveis, cobertura, cardinalidade e quebra
  de simetria diferentes), dois solvers, prova LRAT conferida. Confiança muito alta.
- **K_7(4,2) ≥ 19**: uma codificação, verificada à mão e por testes de completude que pegam
  quatro apertos errados; prova LRAT reproduzida bit a bit e conferida; controle sem (d)–(f) com
  outro solver. Confiança alta. O passo humano que resta confiar é o Lema 1 + a ponte
  código → CNF, ambos curtos e conferidos acima.
- **Falta para virar teorema**: Lean (Lema 0, Lema 1, ponte para a CNF do perfil, e checagem das
  LRAT no kernel; 3,6 GB de prova precisam ser aparados ou divididos antes), e, se quiser uma
  segunda fonte para M = 18, rodar `indep.py 7 18 2 perfil` (~1 dia de CPU, sem nuvem paga).

Saídas brutas em `tools/exatos/k742/redteam/resultados/` (JSONL). Reproduzir (da raiz do repo; precisa de `python-sat`; `indep.py 7 17` leva ~8 h de CPU):

    python3 tools/exatos/k742/redteam/perfis_indep.py
    python3 tools/exatos/k742/redteam/orbita.py 7 18 1 300
    python3 tools/exatos/k742/redteam/mutantes.py 7 18 100
    python3 tools/exatos/k742/redteam/compara.py 5 11 0 1
    python3 tools/exatos/k742/redteam/semquebra.py 7 18
    python3 tools/exatos/k742/redteam/indep.py 7 17 2 perfil
    python3 tools/exatos/k742/redteam/cod19.py
