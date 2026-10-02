# Auditoria de completude: as 6362 classes de códigos [9,3]_7

Data: 2026-10-02. Só CPU local, sem VM e sem gasto. Tudo abaixo é reproduzível com os
scripts de `scripts/audit/`:

    cd scripts/audit
    python3 verify_list.py <classes_sorted.jsonl> ../../data/audit/enum_completeness_result.json   # ~1 min
    python3 degenerate.py ../../data/audit/degenerate_classes.jsonl ../../data/audit/degenerate_summary.json  # ~10 s

| arquivo | papel |
|---|---|
| `scripts/audit/audit_lib.py` | PG(2,7), retas, projetividades, códigos, contagens analíticas (Python puro) |
| `scripts/audit/pg2_orbits.c` | forma canônica, estabilizador, enumeração de órbitas, equivalência por força bruta, conjuntos sem referencial |
| `scripts/audit/verify_list.py` | tarefas 1 e 2 (lista não degenerada) |
| `scripts/audit/degenerate.py` | tarefa 3 (classes degeneradas) |
| `data/audit/enum_completeness_result.json` | saída medida da tarefa 1/2 |
| `data/audit/degenerate_summary.json`, `data/audit/degenerate_classes.jsonl` | saída medida da tarefa 3 |

**Independência.** Nada aqui reaproveita código do `base_search.c`. A numeração de pontos
da auditoria é outra (vetores normalizados em ordem lexicográfica; o `base_search` põe o
referencial padrão primeiro). A numeração dele só é reconstruída para conferir o campo
`pts`. A ideia matemática de "forma canônica = menor imagem sobre referenciais" é a
mesma — é o jeito natural de fazer isso —, mas aqui ela é reimplementada e, mais
importante, a completude é provada por um argumento que **não depende** de a forma canônica
estar certa: a fórmula de massa (seção 2).

## 0. Entrada

- arquivo: `classes_sorted.jsonl`, 6362 linhas, sha256 `4e2035d93538f808e679771be576c2046d59672bc70657d1e45e5b491ce7bad1` (confere com o prefixo esperado `4e2035d93538f808…`).
- caso: q = 7, n = 9, k = 3, r = 6.

## 1. Mapeamento `pts` ↔ `A` e checagens por linha

No `base_search`, `code_from_points` toma o multiconjunto ordenado `S` de 9 pontos, usa a
primeira ocorrência de e1, e2, e3 como conjunto de informação e as 6 colunas restantes
`rest[i]`, e escreve H = [I6 | A] com a linha i de A igual a −(ponto `rest[i]`). Logo

    G = [ −A^T | I3 ]   (3 × 9),   G·H^T = −A^T + A^T = 0 (mod 7),

e as colunas de G são exatamente os pontos de `S`: as 6 primeiras são os `rest[i]`, as 3
últimas são e1, e2, e3. O script refaz G de `A` e confere, nas 6362 linhas:

| checagem | falhas |
|---|---|
| G·H^T = 0 mod 7 | 0 |
| G sem coluna nula | 0 |
| colunas de G contêm 4 pontos em posição geral (força bruta em Python sobre 4-subconjuntos) | 0 |
| multiconjunto das colunas de G == `pts` (traduzido da numeração do `base_search`) | 0 |

**Duplicatas.** Invariante calculado em Python a partir do código: distribuição de pesos
(343 palavras) + tipos de reta (pontos do multiconjunto em cada uma das 57 retas, ordenado)
+ perfil por ponto (multiplicidade, contagens nas 8 retas pelo ponto). Ele é fraco nesta
família: só **688** valores distintos, com 585 grupos empatados e **70 745 pares** para
testar. Cada par foi testado por força bruta direta em C (`pg2_orbits equiv`: fixa um
referencial ordenado F0 de S1, percorre todas as 4-uplas ordenadas de pontos distintos de
S2 e testa g(S1) = S2 com g a única projetividade F0 → F). Resultado: **0 pares
equivalentes**. Conferências do próprio teste: 300 pares sorteados refeitos em Python
puro (0 divergências) e controle positivo (50 linhas levadas por projetividade aleatória
deram "equivalente" no C, 10 delas também no Python). Além disso, as 6362 formas
canônicas calculadas pela auditoria são **todas distintas**.

## 2. Fórmula de massa (o teste de completude)

Seja X o conjunto dos 9-multiconjuntos de pontos de PG(2,7) que contêm um referencial.
PGL(3,7) age em X; pela relação órbita–estabilizador,

    |X| = Σ_{órbitas O} |PGL(3,7)| / |Stab(S_O)|.

Se a lista tem exatamente um representante por órbita, a soma sobre a lista é |X|. Se
faltasse uma órbita, a soma ficaria menor (cada termo é ≥ 1); se houvesse duplicata, maior.
Como as duplicatas já foram excluídas na seção 1, a igualdade prova que não falta nenhuma.

**|PGL(3,7)|** = (7³−1)(7³−7)(7³−7²)/(7−1) = 342·336·294/6 = **5 630 688** (confere).

**|Stab(S)|.** Teorema fundamental: duas 4-uplas ordenadas em posição geral determinam
uma única projetividade. Fixado um referencial ordenado F0 ⊆ S, cada g ∈ Stab(S) leva F0
a uma 4-upla ordenada F de pontos distintos de S e g é determinado por F. O C conta as
4-uplas F de S cuja imagem normalizada N_F(S) é igual à de F0 (equivalente a g(S) = S,
com multiplicidades). Os 10 maiores estabilizadores e 20 sorteados foram refeitos em
Python por força bruta: 0 divergências. Distribuição medida:

| \|Stab\| | 1 | 2 | 3 | 4 | 6 | 8 | 9 | 12 | 16 | 18 | 24 | 42 | 54 | 84 | 216 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| classes | 5145 | 900 | 109 | 93 | 82 | 9 | 6 | 7 | 1 | 4 | 1 | 1 | 2 | 1 | 1 |

Todos dividem 5 630 688.

**Lado direito, |X|.** Total de 9-multiconjuntos de 57 pontos: C(65,9) = 31 966 749 880.
Um conjunto de pontos não contém referencial se e só se está contido numa reta L ou em
L ∪ {P}. Contagem por tamanho s do suporte (conjuntos), e cada suporte de tamanho s gera
C(8, s−1) multiconjuntos de tamanho 9:

| s | numa reta: 57·C(8,s) (s ≥ 2) | posto 3: triângulos (s=3) ou 57·C(8,s−1)·49 | × C(8,s−1) |
|---|---|---|---|
| 1 | 57 | 0 | 1 |
| 2 | 1 596 | 0 | 8 |
| 3 | 3 192 | 26 068 = C(57,3) − 57·C(8,3) | 28 |
| 4 | 3 990 | 156 408 | 56 |
| 5 | 3 192 | 195 510 | 70 |
| 6 | 1 596 | 156 408 | 56 |
| 7 | 456 | 78 204 | 28 |
| 8 | 57 | 22 344 | 8 |
| 9 | 0 | 2 793 | 1 |

Multiconjuntos sem referencial: 651 681 de posto ≤ 2 + 34 304 557 de posto 3 =
**34 956 238**. Três conferências independentes:

1. **busca em profundidade** (`pg2_orbits livres`): enumera todos os conjuntos sem 4 pontos
   em posição geral sem supor a classificação "reta + ponto" (a propriedade é hereditária,
   então a busca é exaustiva); bate com a tabela acima em todos os s;
2. posto ≤ 2 por inclusão–exclusão sobre retas: 57·C(16,9) − 7·57 = 651 681 (cada
   multiconjunto concentrado num ponto foi contado nas 8 retas pelo ponto);
3. posto 3 sem referencial pela soma de massa das 78 órbitas estruturais da seção 3:
   34 304 557.

Resultado:

| | valor |
|---|---|
| lado direito \|X\| = 31 966 749 880 − 34 956 238 | **31 931 793 642** |
| lado esquerdo Σ 5 630 688 / \|Stab(S)\| sobre as 6362 linhas | **31 931 793 642** |

**Bate exatamente.** Com 0 duplicatas, a lista de 6362 classes é completa: toda órbita de
PGL(3,7) em 9-multiconjuntos com referencial tem exatamente um representante na lista.

**Contraprova adicional.** Uma enumeração própria de órbitas (`pg2_orbits enum 7 9`, 4
fatias, ~1 min) — multiconjuntos que contêm o referencial padrão e são mínimos entre
suas imagens — achou 6362 órbitas, com **o mesmo conjunto** de formas canônicas da lista
e a mesma soma de massa.

## 3. Classes degeneradas (fora da varredura)

Código [9,3]_7 a menos de equivalência monomial ↔ (z colunas nulas, multiconjunto de
m = 9 − z pontos de posto 3) a menos de PGL(3,7). (q = 7 é primo, então não há automorfismo
de corpo; equivalência monomial = permutação + escala por coordenada.) A varredura cobre
só z = 0 com referencial. Fica de fora:

- (i) z ≥ 1: a parte não nula tem m = 9 − z ∈ {3, …, 8} pontos de posto 3, com referencial
  (m ≥ 4, órbitas pela enumeração própria `enum m`) ou sem referencial;
- (ii) z = 0 sem referencial, posto 3.

Sem referencial e posto 3 só há dois formatos: **triângulo** (3 pontos não colineares com
multiplicidades a+b+c = m; órbita ↔ partição, pois as permutações dos vértices são
projetividades; |Stab| = 36·#permutações que preservam as multiplicidades) e **reta + ponto**
(≥ 3 pontos numa reta L, P fora; L e P são únicos; o estabilizador de (L,P) é GL(2,7) e age
em L como PGL(2,7) com núcleo de ordem 6; órbita ↔ (multiplicidade j de P, órbita de
PGL(2,7) do multiconjunto em L), |Stab| = 6·|Stab_PGL(2,7)|).

Cada linha da tabela foi conferida por fórmula de massa (soma de |PGL(3,7)|/|Stab| ==
número de multiconjuntos daquele tipo, contado por fórmula/busca); as órbitas de PGL(2,7)
também (u = 3…8). **Todas batem** (`degenerate_summary.json`, campo `massa_ok: true`).

| tipo | z | m | com referencial | sem referencial (posto 3) |
|---|---|---|---|---|
| (ii) | 0 | 9 | — (é a lista: 6362) | **78** (7 triângulos + 71 reta+ponto) |
| (i) | 1 | 8 | 1006 | 43 |
| (i) | 2 | 7 | 165 | 24 |
| (i) | 3 | 6 | 32 | 12 |
| (i) | 4 | 5 | 5 | 6 |
| (i) | 5 | 4 | 1 | 2 |
| (i) | 6 | 3 | — | 1 |

Totais: tipo (i) **1297** (1209 com referencial + 88 sem), tipo (ii) **78**,
degeneradas **N = 1375**. Total de classes monomiais de códigos [9,3]_7: 6362 + 1375 = 7737.

`data/audit/degenerate_classes.jsonl` tem 1375 linhas `{"A": …, "tipo": …}` (todas as
strings A distintas). Para cada classe, as coordenadas foram permutadas para que as 3
últimas formem um conjunto de informação (3 colunas não colineares de G); com
G' = B⁻¹G = [P | I3], H = [I6 | A] com A = −P^T, e G'·H^T = 0 conferido. Ida e volta
conferida: G refeito de A tem z colunas nulas e parte não nula na mesma órbita (forma
canônica igual, para as com referencial; posto 3, sem referencial e mesmo perfil de
multiplicidades, para as outras). A permutação de coordenadas não muda as órfãs (seção 4).

**Custo estimado** da avaliação de órfãs (NÃO executada): 1375 × ~20 s ≈ 27 500 s ≈
7,6 h num núcleo físico, ≈ 1,9 h nos 4 núcleos locais (sem gasto de nuvem). Ressalva: o
tempo de 20 s foi medido em códigos não degenerados; com colunas repetidas ou nulas a bola
B = {He : wt(e) ≤ R} fica menor e o tempo pode mudar.

## 4. Invariância do mínimo de órfãs por equivalência monomial

Seja C ⊆ F_q^n linear com matriz de checagem H (r × n, posto r), B = {He : wt(e) ≤ R} ⊆ F_q^r
a bola de síndromes e, para um trio T = {0, s1, s2} ⊆ F_q^r, órf(T) = #{s ∈ F_q^r :
s ∉ T + B} (as síndromes não cobertas pela união das classes laterais C, C+e1, C+e2 dilatadas
pelo raio R). Seja C' = C·M com M = P·D monomial (P permutação, D diagonal invertível).

1. A aplicação e ↦ eM é uma bijeção linear de F_q^n que preserva o peso de Hamming
   (permuta coordenadas e as multiplica por escalares não nulos).
2. H' = H·(M^{-1})^T é matriz de checagem de C': para c ∈ C, H'(cM)^T = H(M^{-1})^T M^T c^T =
   Hc^T = 0, e o posto é r. Logo a síndrome de eM em C' é H'(eM)^T = He^T: **o espaço de
   síndromes é o mesmo e a identificação é a identidade**. Se se usar outra matriz de
   checagem H'' = UH' (U ∈ GL(r,q)), as síndromes mudam pelo isomorfismo linear s ↦ Us.
3. Portanto B' = {H'(e')^T : wt(e') ≤ R} = {He^T : wt(eM) ≤ R} = {He^T : wt(e) ≤ R} = B
   (ou B' = U·B com outra H). Um isomorfismo linear φ leva B em B', trios {0,s1,s2} em
   trios {0,φs1,φs2} (fixa 0), somas de conjuntos em somas (φ(T+B) = φT + φB) e
   complementares em complementares. Logo órf_{C'}(φT) = órf_C(T) para todo T, e como φ é
   bijeção entre os trios, **min_T órf(T) é o mesmo para C e C'**.
4. Duas matrizes H = [I6 | A] da mesma classe monomial (inclusive as obtidas por permutar
   coordenadas para chegar à forma sistemática, seção 3) dão o mesmo mínimo. Por isso basta
   avaliar um representante por classe.

## 5. A cadeia de redução

    PROBLEMA: bases = união de 3 classes laterais de um código linear [9,3]_7
              (C ∪ (C+e1) ∪ (C+e2)); minimizar as órfãs (síndromes não cobertas no raio R).
       │  o mínimo depende só da classe monomial de C (seção 4)
       ▼
    classes monomiais de códigos [9,3]_7  =  7737
       ├── não degeneradas (sem coluna nula, colunas com referencial): 6362
       │      lista conferida: sem duplicatas (70 745 pares, força bruta) e completa
       │      (fórmula de massa 31 931 793 642 = 31 931 793 642; enumeração própria igual)
       └── degeneradas: N = 1375  — AINDA NÃO AVALIADAS
              (i)  com coluna nula: 1297     (ii) sem coluna nula e sem referencial: 78

**O que a varredura das 6362 prova** (supondo que a avaliação de órfãs de cada classe, o
`exactT2`, esteja certa — isso não é auditado aqui): o mínimo de órfãs entre as bases
"3 classes laterais de um [9,3]_7 **não degenerado**" é o menor valor achado nessas 6362.

**O que NÃO prova:**

- nada sobre os 1375 códigos degenerados: um deles poderia, em princípio, dar menos órfãs.
  Só depois de avaliá-los o mínimo vale para todos os [9,3]_7;
- não verifica a correção do `exactT2`/contagem de órfãs (é outra auditoria);
- nada sobre bases com outro número de classes laterais, com códigos de outra dimensão,
  ou não lineares;
- **nada sobre o valor de K_7(9,4) em geral.** Isto só delimita a família "união de 3
  classes laterais de um [9,3]_7" como base para a receita base + remendo. Uma cota
  superior vem de um código de cobertura explícito e verificado; uma cota inferior exige
  argumento próprio. Nenhuma das duas sai daqui.
