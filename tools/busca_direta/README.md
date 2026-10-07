# busca_direta: busca tabu no espaço inteiro, para qualquer q ≤ 10

O kit de `scripts/search`/`scripts/attack` (classes laterais + remendo) supõe `q` primo e uma base
linear. Esta pasta cobre o que ele não alcança: células pequenas (`q^n < 2^32`, na prática até ~10^8)
com `q` qualquer, inclusive 4, 6, 8, 9 e 10, por busca local direta sem estrutura imposta.

    gcc -O3 -march=native -std=gnu99 -o tabu tools/busca_direta/tabu.c            # M < 255
    gcc -O3 -march=native -std=gnu99 -DCNT16 -o tabu16 tools/busca_direta/tabu.c  # M >= 255
    ./tabu q n R M segundos semente prefixo [tenure=1] [max_cand=0] [pesos=0] [inicial.txt]
    tools/verify/verify -q Q -n N -r R -m M prefixo_M<M>.txt                     # obrigatório

    gcc -O3 -march=native -std=gnu99 -o tabu_grupo tools/busca_direta/tabu_grupo.c
    ./tabu_grupo q n R nrep segundos semente prefixo "geradores" [tenure=1] [max_cand=0]

`tabu_grupo.c` prescreve um grupo G de isometrias (cada gerador é `y_i = x_{p_i} + a_i mod q`) e busca só
os representantes das órbitas: a órbita de pontos fica coberta sse a bola de algum representante a
intersecta, então o custo de um movimento é o mesmo da busca direta, contado por órbita. É o método de
Östergård–Weakley (1999) com que muitos recordes antigos foram achados.

O movimento e a conta incremental (duas cascas de raio exato `R` fora da coordenada trocada, em vez
da bola inteira) estão no cabeçalho de `tabu.c`. Em lote: `pesado/jobs/busca_tabu.sh` com os alvos de
`pesado/jobs/busca_tabu.alvos`.

## Calibração medida (2026-10-07, 1 núcleo por corrida)

| célula | ótimo / recorde | o que a busca achou | tempo |
|---|---:|---:|---|
| K_2(5,1), K_3(4,1), K_3(5,1) | 7, 9, 27 (exatos) | 7, 9, 27 | < 2 s |
| K_2(10,1) | 120 (exato) | 120 (tenure 1 ou 3); nada abaixo de 130 com tenure 8, 15 ou 30 | 10 s |
| K_3(6,1) | 71 | 73 (quatro combinações de tenure e pesos) | 40–60 s |
| K_4(10,5) | 54 | 62 (com M = 61 chegou a 1 descoberto) | 15 min |
| K_5(10,6) | 45 | 49 | 15 min |
| K_4(8,4) | 28 | com M = 27, 23 pontos descobertos no melhor momento | 60 s |
| K_5(7,3) | 100 | com M = 99, 72 descobertos | 60 s |
| 25 células médias (lista no corpo do PR), M = recorde − 1 | ub publicado | nenhuma zerou; menores descobertos: K_5(5,2) 17, K_5(6,3) 19, K_4(8,4) 23, K_3(8,3) 25 | 60 s cada |

Com grupo (`tabu_grupo`, 90–120 s por grupo; |G| entre parênteses): K_4(10,5) chegou a 70 com a troca
cíclica (10), e com 6 representantes (60) a 2 pontos descobertos; K_5(10,6) chegou a 60 (troca cíclica e
S2+translação, 10) e, com 4 representantes da troca cíclica (40 < 45), a 146 descobertos em ~10 min;
K_5(8,4) chegou a 80 (cíclica, 8), com 9 representantes (72) a 11 descobertos. Nada abaixo de recorde.

Varredura com grupo (2026-10-07, 90 s por grupo, grupos: troca cíclica C, translação por 1…1 T1,
negação N, meia-volta S2, ciclos paralelos P3/P4/P5 e produtos): **empates** com o recorde, conferidos no
verificador oficial, em K_3(8,3) = 27 (T1), K_3(11,5) = 27 (T1), K_7(6,3) = 77 (T1) e K_5(6,3) = 25 (N);
nenhum abaixo. Quase: K_4(8,4) com N e com translação por 2…2 ficou a 2 pontos de cobrir 30 palavras
(recorde 28); K_5(7,3) com C ficou a 1 ponto de 105 (recorde 100); K_7(6,3) com C a 1 ponto de 84.
Corridas focadas de 25 min: K_7(6,3) com N (76–77 palavras) parou em 38 descobertos e com P3 (78) em 27;
K_4(10,5) com S2+T1 (48) em 392 e com P5 (50) em 181; K_5(10,6) com C (40) em 140.

Leitura: a busca é correta (acha os ótimos pequenos e nunca menos; todo código gravado passa no
verificador) e fica longe dos recordes de 2011 nas células médias. Esses recordes não são de busca
local cega: quase sempre têm estrutura (somas diretas, classes laterais, grupo prescrito). Esta
ferramenta é o piso de comparação, não a arma.

O que não ajudou, medido: `pesos = 1` (peso por ponto descoberto, à moda do RWLS) deu 96 descobertos
contra 72 sem pesos em K_5(7,3) com M = 99 e 60 s; base aditiva de F_4 (classes laterais de um código
F_2-linear em F_4^10, órfãs por Walsh–Hadamard) + remendo pelo `tools/patch_setcover` deu 64 em
K_4(10,5) (48 da base + 16 de remendo).
