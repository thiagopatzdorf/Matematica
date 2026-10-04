# Mapa da literatura: quem atacou o expoente do GNFS, e onde a matemática está

Fase 0 do programa "bater o GNFS" (ver [`README.md`](README.md)). Pergunta: **o que já foi tentado para baixar o
expoente do custo de fatorar, o que se sabe provado, e por que o 1/3 está parado desde 1990?**

Regra do documento: cada afirmação diz de onde veio e **o quanto eu verifiquei**. Estados:

* **lido**: abri o texto da fonte e conferi a frase.
* **resumo**: abri a página do artigo e li o resumo; não li o corpo.
* **busca**: só vi o trecho que um buscador devolveu. Vale como pista, **não como fato**, até alguém abrir a fonte.
* **não lido**: sei que existe e não abri.

Data da coleta: 2026-10-04. Nada aqui é alegação de novidade.

## 1. O que decide o expoente (mecanismo)

Pomerance (1996), **lido**: o custo de um crivo é da ordem de `exp( √(2 · log X · log log X) )`, em que **X é o
tamanho dos números auxiliares** que se espera achar suaves. No crivo quadrático X fica perto de `n^(1/2+ε)`. No
crivo de corpo de números (NFS) escolhe-se polinômio `f` e inteiro `m` de modo que `(a − mb)·N(a − αb)` fique abaixo
de um X da forma `exp(c'·(log n)^(2/3)·(log log n)^(1/3))`, o que dá o expoente 1/3. Em dígitos: os números testados
têm cerca da potência 2/3 do número de dígitos de `n`, contra mais da metade no crivo quadrático. O mesmo texto
diz que o tempo do NFS é uma **conjectura** apoiada em heurística, e não um teorema.

**Consequência para este programa:** atacar o expoente é, concretamente, **encolher X**, isto é, achar um jeito de
obter números auxiliares assintoticamente menores do que `exp((log n)^(2/3)…)` com o mesmo custo de busca. É essa
grandeza (o tamanho dos números a testar) que um avaliador exato consegue medir, sem hardware e sem crivo.

Pomerance sobre o salto 1/2 → 1/3, **lido**: *"If reducing the constant in the exponent had such a profound impact in
passing from the continued-fraction method to the quadratic sieve, think what reducing the exponent in the exponent
might accomplish."*

## 2. Linha do tempo das descidas que existiram

| ano | o quê | efeito | estado |
|---|---|---|---|
| anos 1920 | Kraitchik: congruências `u² ≡ v² (mod n)` com `x² − n` | método base | lido |
| década de 1970 | frações contínuas (Brillhart, Morrison) | fatorar números de ~50 dígitos virou rotina | lido |
| 1981 (ideia) a 1990 | crivo quadrático (Pomerance), expoente 1/2 | dobrou o tamanho fatorável: recorde de 116 dígitos em 1990; RSA-129 em 1994 | lido |
| 1988-1990 | crivo de corpo de números (Pollard; Lenstra, Lenstra, Manasse; Buhler, Lenstra, Pomerance; ideia dos caracteres quadráticos de Adleman); F9 em 1990 | **expoente 1/2 → 1/3**, `c = (64/9)^(1/3) ≈ 1,923` | lido |
| 1993 | NFS com vários polinômios (Coppersmith) | só a constante: 1,923 → ~1,902 | busca |
| 1993 | "fábrica de fatoração" (Coppersmith): pré-cálculo repartido por muitos números | constante por número ~1,639, com pré-cálculo ~2,007 | busca |
| 2014 | NFS em lote (Bernstein, Lange) | em custo de área×tempo: ~1,704 por chave contra ~1,976 de uma chave só | busca (ver aviso) |

**Aviso sobre o modelo de custo:** os números de 2014 são em **área × tempo** de circuito, não em operações. Não se
compara a coluna "efeito" de linhas com modelos de custo diferentes.

Leitura: desde 1990 todas as melhorias verificadas **mexem na constante**. Ninguém publicou, com prova ou com
fatoração reproduzível, um expoente abaixo de 1/3 para fatorar números gerais.

## 3. Ataques que tentaram mexer no expoente ou no que ele mede

| linha | o que prometia | o que se sabe | estado |
|---|---|---|---|
| Reticulados (Schnorr, 2021, "fast factoring by SVP") | dimensão do reticulado `O(n/log²n)`, "destrói o RSA" | reprodução independente (SchnorrGate, Ducas): 0 relações em 1000 tentativas nos parâmetros testados; implementação híbrida: só até ~70 bits, sem relações suficientes a partir de ~80 bits; nenhum artigo de fatoração polinomial do autor passou em revisão | busca |
| Cálculo de índice para fatorar (Stange, 2022, arXiv 2211.06821) | fatorar por relações multiplicativas módulo `n` | subexponencial `exp(O(√(log n log log n)))`, ou `exp(O((log n)^(1/3)(log log n)^(2/3)))` com NFS; a própria autora diz que é mais lento que os melhores métodos | resumo |
| Variantes de Fermat e determinísticas (por exemplo arXiv 1308.2891, 2503.07151) | reduzir iterações | custo ainda exponencial em `n`, ou exige bits conhecidos de um fator; não tocam o expoente subexponencial | resumo |
| Computação quântica (Shor e variantes) | tempo polinomial | **fora do escopo** deste programa (clássico) | não lido |

## 4. O único lugar vizinho onde o expoente caiu: logaritmo discreto em característica pequena

Em 2013 Joux obteve `L(1/4+ε)` para logaritmo discreto em corpos finitos de característica pequena, e Barbulescu,
Gaudry, Joux e Thomé (ePrint 2013/400) obtiveram um algoritmo **quase-polinomial** nesse caso (**busca**). Provado
depois, há versão **com prova** do quase-polinomial (arXiv 2206.10327, **busca**: só vi o título).

Por que isso **não transfere** para fatoração, segundo o que a busca devolveu: o ganho vem da **descida** e da
estrutura do corpo finito (o grupo multiplicativo de `F_{q^k}`), que não tem análogo em `Z/NZ`. **Esta explicação é da
literatura como o buscador a resumiu; eu não verifiquei o argumento.** Fica como a primeira leitura a fazer na
fase 0b, porque é o único caso onde um expoente abaixo de 1/3 existiu num problema irmão.

Boudot et al. (CRYPTO 2020, ePrint 2020/697), **resumo**: RSA-240 (795 bits) e logaritmo discreto de 795 bits no mesmo
hardware; conclusão deles: o logaritmo discreto não é muito mais difícil que a fatoração do mesmo tamanho **para
corpos primos**. Ou seja, nos casos relevantes para RSA, os dois problemas continuam no mesmo regime 1/3.

## 5. Onde a matemática está (estado provado)

* **NFS heurístico → provado só numa variante.** Lee e Venkatesan (J. Number Theory 187, 2018; arXiv 1805.08873),
  **resumo**: variantes **randomizadas** do NFS e do método de Coppersmith de vários polinômios encontram congruências
  de quadrados em tempo esperado que **coincide com as melhores estimativas heurísticas**. A constante provada que
  vi citada (L(1/3; 2,88)) veio de **busca** e não conferi. O NFS usado na prática continua sem prova.
* **Limites inferiores:** nenhum incondicional conhecido (frase de uma busca; **busca**, não conferi). Sabe-se que a
  versão de decisão está em NP ∩ coNP, então não é NP-completa a menos que NP = coNP (**busca**, resultado padrão).
* **Estado da arte prático:** NFS. Recorde recente de RSA-896 em 2026-09 (sessão anterior; fonte a anexar).

## 6. Por que "não está congelada, mas em algum ponto está"

O que dá para afirmar com o que li:

1. O expoente é função de **um** número, X, o tamanho dos auxiliares (seção 1). Baixar o expoente é o mesmo que
   encolher X de forma assintótica, não é "otimizar o crivo".
2. O X do NFS vem de **estrutura algébrica** (escolha de `f` e `m`). O caso de números de forma especial (SNFS) tem
   constante menor (~1,526, de memória; **não verificado**), o que mostra que estrutura muda a constante. Não mostra
   que se consiga **fabricar** estrutura para um `n` qualquer.
3. Não há prova de que o 1/3 seja o fim. O que existe é ausência de ideia: 36 anos sem nada que passasse da constante.

O que **não** dá para afirmar: que haja barreira provada. Ninguém tem; esta é a parte do "em algum ponto está" que
continua em aberto.

## 7. Lacunas deste mapa (o que falta pesquisar antes de dizer "mapeado")

* Polinômio: Kleinjung, Joux-Lercier, e David-Zimmermann (2020, o Murphy-E ranquear errado). **não lido**.
* NFS em torre (TNFS, exTNFS) e variantes de campo de funções: onde as constantes caíram em corpos de extensão.
* ECM e o método do grupo de classes (expoente 1/2); a razão de não competirem.
* O artigo de 2025 *On the complexity formulae of the number field sieve and its variants* (Designs, Codes and
  Cryptography). A página redirecionou para login; **não li**.
* A explicação rigorosa de por que a descida de Joux não se adapta a `Z/NZ` (seção 4).
* Provas de limites em modelos restritos (algoritmos tipo crivo, genéricos). Existe literatura; **não pesquisei**.

## 8. O que isto permite testar (liga com o programa)

Se atacar o expoente é encolher X, o avaliador natural é **o tamanho dos números auxiliares que o polinômio escolhido
produz para um `n` dado**, medido em bits, versus o esforço de busca gasto para achá-lo. É aritmética inteira, independe
de hardware e é barato em tamanhos de 60 a 200 dígitos. A curva "esforço de busca × tamanho obtido" pode ser ajustada
e comparada com a prevista. Resultado esperado pela teoria: ganho só de ordem inferior. Mas é a medida que **ficaria
diferente** se existisse estrutura nova, e a literatura acima não mostra que alguém a tenha feito dessa forma.
(Isto é uma hipótese de pesquisa, não um resultado, e entra como eixo novo do critério de vitória em PR à parte.)
