# Fatia mínima + LP no alfabeto binário (2026-10-05)

Missão S2: levar a via que matou `K_3(6,2)` com M = 15 e M = 16 (fatia mínima de
[`GAPS2_K362.md`](GAPS2_K362.md) + certificados de Farkas de
[`k362/K3_M16.md`](k362/K3_M16.md)) para as células binárias abertas `K_2(11,3)`, `K_2(12,4)`,
a família `K_2(2R+4,R)`, `K_2(10,1)`, `K_2(10,2)` e `K_2(11,2)`. Código em
`tools/exatos/lp_bin/`, testes em `tests/test_lp_bin.py`. Estados como no `AGENTS.md`.

**Resultado: nenhuma cota mudou, e nada vai para o ledger.** A via reproduz, com certificado
exato, quatro valores binários conhecidos e quase todo `K_2(10,3) = 12`. Nas células abertas ela
para em dois lugares diferentes, medidos abaixo: (1) a relaxação linear fica fraca quando M passa
de ~2 vezes a cota de esferas (`K_2(12,4)`), e (2) a lista de configurações não cabe quando s* é
grande (`R ≤ 2` e `K_2(11,3)`).

## Resumo por célula

Estados como no `AGENTS.md`: OBSERVED (medido, sem prova), COMPUTATIONALLY_VERIFIED (certificado
aceito por verificador exato, mais a completude da redução), PROVED (demonstração fechada).
"Morta" = instância com certificado de Farkas aceito; "viva" = sem certificado no orçamento.

| célula | lb–ub | M testado | lista (sha256 do JSON) | medido | resultado | estado |
|---|---|---|---|---|---|---|
| K2(6,1) | 12 | 11 | 4 instâncias (`00c38a61…`) | 4 de 4 mortas, aceitas por `verificar_bin.py` | reproduz lb 12 | COMPUTATIONALLY_VERIFIED |
| K2(7,2) | 7 | 6 | 16 (`d3da5719…`) | 16 de 16 aceitas | reproduz lb 7 | COMPUTATIONALLY_VERIFIED |
| K2(9,3) | 7 | 6 | 41 (`eba157ee…`) | 41 de 41 aceitas | reproduz lb 7 | COMPUTATIONALLY_VERIFIED |
| K2(8,2) | 12 | 11 | 1 723 (`d436983b…`) | 1 723 de 1 723 aceitas (também no `verificar.py` do K3) | reproduz lb 12 | COMPUTATIONALLY_VERIFIED |
| K2(10,3) | 12 | 11 | 13 022 (`4e1b26ee…`) | 13 020 aceitas (118 625 folhas); 425 e 701 sem certificado | lb 12 **não** reproduzida por inteiro | 13 020 instâncias: COMPUTATIONALLY_VERIFIED; a célula: OBSERVED |
| K2(9,1) | 62 | — | não gerada | — | não tentada (s* até 30, lista não cabe) | — |
| K2(12,4) | 11–12 | 11 | 73 029 (`15b70965…`) | raiz: 21 512 mortas (29,5 %), 51 517 vivas; ramos em 24 vivas: 15 fecham | lb não muda | OBSERVED |
| K2(14,5) | 10–12 | 10 | 341 547 (`1fef7e2b…`) | raiz em 1 000 sorteadas: 990 mortas, 10 vivas; raiz inteira e ramos em [`K2_14_5.md`](K2_14_5.md): 2 835 sem certificado | lb 11 **não** provada; elo mais barato da família | OBSERVED |
| K2(16,6) | 9–12 | 9 | 8 795 (`e09b5d7e…`) | raiz: 8 499 mortas (96,6 %), 296 vivas; ramos em 10 vivas: 5 fecham | lb 10 não provada | OBSERVED |
| K2(18,7)…K2(24,10) | 9–12 | — | não gerada | — | não tentadas (2^18 a 2^24 pontos) | — |
| K2(11,3) | 15–16 | 15 | não cabe (s* até 7) | sorteio: s* = 7 e s* = 5, 20 de 20 mortas na raiz cada | lb não muda | OBSERVED |
| K2(10,2) | 24–30 | 23 | não cabe (s* até 11) | sorteio s* = 11: 20 de 20 mortas; filtro cortou 1 018 963 sorteios | lb não muda | OBSERVED |
| K2(10,1), K2(11,2) | 107–120, 37–44 | — | não cabe | nenhuma medição concluída | não atacadas | — |

**Nenhuma cota inferior subiu.** Não há certificado novo para célula aberta; os certificados
aceitos acima são de valores já conhecidos. Nada vai para `ledger/`, `data/` ou `paper/`.


## 1. O que mudou em relação ao ternário

**A redução é a mesma**, com q = 2 (prova de completude em `GAPS2_K362.md`, válida para todo q,
n, R e M ≤ q^n). No binário a coordenada 0 tem só dois blocos, então a instância é `(s*, K, t)` com
`t = (M − s*,)`, e `s* ≤ ⌊M/2⌋`.

**Enumeração nova das configurações** (`fatia_bin.py`). A de `fatia.configuracoes` calcula a forma
canônica com `s!` permutações em Python por multiconjunto de colunas e já leva horas com `m = 11`.
No binário, uma configuração de `s` pontos de `Z_2^m` a menos de isometria é um vetor de contagem
`c` sobre os `2^(s−1)` padrões de coluna normalizados (ponto 0 com bit 0; complementar a coluna é
isometria), a menos da ação de `S_s` nos padrões. A lista guarda de cada órbita o vetor
lexicograficamente máximo (comparação exata em blocos de `int64`), vetorizada em numpy. Testes: a
lista tem as mesmas classes que `fatia.configuracoes` em sete casos `(m, s)` e as mesmas
instâncias que `fatia.instancias` em três células.

**LP reduzido por simetria** (`certificar_bin.py`). Seja `H` o grupo das permutações das
coordenadas 1..n−1 que trocam colunas idênticas de K. `H` fixa a coordenada 0 e K ponto a ponto,
então preserva o sistema da instância; a média de uma solução 0-1 sobre `H` é uma solução
fracionária constante nas órbitas de `H`. Basta então um peso por órbita da fatia 1. As
configurações estruturadas, que são as difíceis, têm poucas classes de coluna e um LP pequeno.

**O certificado gravado é do sistema completo.** O dual do LP reduzido se levanta exatamente
(`y_x = ỹ_A·L/|A|` nas linhas de cobertura da órbita A; a linha reduzida de fibra é a soma das
`m_v` linhas de coordenada), e a folga fica multiplicada por `L > 0`. A conferência é de
`verificar_bin.py`, escrito do zero, só biblioteca padrão, que reconstrói o sistema completo e não
sabe nada de órbitas. As folhas sem ramificação também passam no `verificar.py` do K3(6,2).

**Ramificação agregada.** Quando o LP reduzido é viável, a ramificação em uma variável (a do
`certificar_lp.py`) quebra a simetria e não termina: a solução fracionária é espalhada (valores de
~0,08 em centenas de pontos). Aqui se ramifica na soma inteira `N_B = Σ_{c∈B} z_c` da órbita mais
fracionária (`N_B ≤ k` ou `N_B ≥ k + 1`, invariantes por H) e, quando todos os `N_B` são inteiros,
em `z_c = 1 / 0` de um ponto de uma órbita parcialmente cheia, que passa a refinar o agrupamento
das colunas. Cada decisão vai na folha como linha `Σ_{c∈S} z_c ≥ r` ou `≤ r` com `S` explícito;
o verificador confere que os dois filhos de cada nó são `(S, ≤ k)` e `(S, ≥ k+1)` com o mesmo `S`
(exaustivo porque a soma é inteira).

**O filtro de contagem no binário.** O GAPS2 notou que ele não corta nada para `K_2(2R+4,R)`, e
isso se confirma (`K_2(12,4)` e `K_2(16,6)` ficam com todas as classes de `s* = 5` e `s* = 4`).
Para R pequeno é o contrário: o filtro é fortíssimo (em `K_2(10,2)`, M = 23, s* = 11, só 20 de
~1 milhão de conjuntos sorteados passam), mas a lista inteira das classes não cabe na enumeração
por vetor de contagem.

## 2. Por célula

Máquina: VM spot `t2d-standard-8` (8 vCPU AMD, 32 GB), 2026-10-05 08:14–11:46 UTC, mais o
container local para os casos pequenos. Código na versão `8d2ee14` desta branch, salvo onde dito.
Os arquivos de certificado grandes (até 55 MB) **não** estão versionados; os sha256 abaixo
identificam a lista de instâncias, que é a parte da prova que qualquer um regenera com
`fatia_bin.py --listar` e confere.

### Valores conhecidos (validação)

`K2(6,1) ≥ 12`, `K2(7,2) ≥ 7`, `K2(9,3) ≥ 7` e `K2(8,2) ≥ 12`: todas as instâncias da lista em
M = lb − 1 ganharam certificado, e `verificar_bin.py` (rodado de novo em 2026-10-05 sobre os
certificados gerados) respondeu `recusadas 0 -> TODAS INVIÁVEIS` nas quatro. Com a completude
da redução (`GAPS2_K362.md`) isso é COMPUTATIONALLY_VERIFIED, reprodução independente da
literatura. Controle no sentido oposto: em M = K (onde existe código), `K2(6,1)` M = 12 deixa 5
das 111 instâncias e `K2(7,2)` M = 7 deixa 14 das 23 sem certificado na raiz, como deve ser, e o
teste `test_codigo_otimo_conhecido_nunca_ganha_certificado` impede o contrário.

### K2(10,3) = 12, M = 11 (validação maior)

* Lista: 13 022 instâncias, s* = 1: 1, 2: 9, 3: 43, 4: 649, 5: 12 320; 116 s.
* Primeira rodada (código `5acba3e`, orçamento 20 000 nós): 22 min 56 s de parede, 5 181 s de CPU,
  800 MB; 12 345 fecham no LP reduzido da raiz, 671 com ramificação agregada, 6 sem certificado.
* Refeitas com o código `7274af9`/`8d2ee14` e orçamento 100 000: 420, 421, 423 e 697 fecham (de 369
  a 712 s cada). O arquivo resultante (sha256 `926986b7…`) passa no `verificar_bin.py`: **13 020 de
  13 022 aceitas, 118 625 folhas, recusadas 2 [425, 701]**.
* 425 e 701 com orçamento 400 000: a 701 parou sem certificado em 1 199 s, praticamente o mesmo
  tempo da rodada de 100 000 nós (1 205 s), então o limite que ela bate **não** é o orçamento de
  nós (causa não diagnosticada). A 425 terminou com `agregado` em 5 292 s, mas **o certificado se
  perdeu**: o processo principal foi encerrado por mim (`pkill`) segundos depois, durante a escrita
  do arquivo, e o gzip truncado só contém as instâncias 0–420. Fica OBSERVED, não verificada.
* Conclusão: falta certificado para 2 de 13 022; `K2(10,3) ≥ 12` **não** está reproduzida por esta
  via. Próximo passo barato: refazer só a 425 (~1,5 h em um núcleo) e investigar por que a 701
  para em ~1 200 s.

### K2(12,4), 11–12, M = 11

* Lista: 73 029 instâncias (s* = 0: 1, 1: 1, 2: 11, 3: 71, 4: 1 727, 5: 71 218); 3 min 11 s, 825 MB.
* LP reduzido só na raiz, todas: 1 529 s com 6 processos; **21 512 mortas (29,5 %), 51 517
  vivas** (todas as de s* ≤ 3 e quase todas as de s* = 4 ficam vivas).
* Ramificação agregada em 24 vivas sorteadas (orçamento 2 000 nós, código `5acba3e`, antes da
  correção de arredondamento): 15 fecham (1 a 75 s), 9 não (55 a 431 s).
* Este é o gargalo (1) do topo: M = 11 é ~2 vezes a cota de esferas (6) e a relaxação linear fica
  fraca. Fechar exigiria ramificar ~51 mil instâncias com ~40 % de falha no orçamento atual.

### Família K2(2R+4,R): K2(14,5) é o elo mais barato

`K(n+2,R+1) ≤ K(n,R)` dá `K2(16,6) ≤ K2(14,5) ≤ K2(12,4)`; uma lb nova em uma célula só sobe as
de n menor, que já estão acima. Medido:

* **K2(14,5), M = 10** (ganharia lb 11): lista com **341 547 instâncias** (s* = 0: 1, 1: 1, 2: 13,
  3: 109, 4: 4 048, 5: 337 375), 17 min 05 s, 2,9 GB. LP reduzido na raiz em 1 000 sorteadas
  (semente 20261005): **990 mortas, 10 vivas**, 126,5 s com 6 processos. Extrapolação (OBSERVED,
  não prova): a raiz de todas custa ~43 000 s de parede nessa VM (~12 h, ~US$ 2,1 a
  US$ 0,1771/h) e deixa ~3 400 vivas para ramificar. É a melhor razão morta/custo da família.
* **K2(16,6), M = 9** (ganharia lb 10): lista com 8 795 instâncias (s* ≤ 4); raiz em todas: **8 499
  mortas (96,6 %), 296 vivas** (as 296 continuam vivas com o arredondamento corrigido). Ramificação
  em 10 vivas sorteadas, orçamento 3 000 nós: 5 fecham (2 a 238 s), 5 não (215 a 850 s).
* K2(18,7) em diante: não gerado; com 2^18 pontos a lista e o LP passam do que coube aqui.

### K2(11,3), K2(10,2), K2(11,2), K2(10,1)

Gargalo (2): s* chega a ⌊M/2⌋ (7, 11, 18, 53) e a enumeração por vetor de contagem não termina.
Só houve sorteio (`amostra_bin.py`, não é prova): `K2(11,3)` M = 15 com s* = 7 e s* = 5, 20 de 20
mortas na raiz em cada; `K2(10,2)` M = 23 com s* = 11, 20 de 20 mortas, e o filtro de contagem
recusou 1 018 963 sorteios antes de achar as 20. As LPs morrem fácil; o que falta é uma lista
completa que caiba (por exemplo, fatia em duas coordenadas). `K2(11,2)` e `K2(10,1)` não chegaram
a ser medidas.

### Custo

VM `lote-s2-binario`: ~3 h 32 min a US$ 0,1771/h ≈ **US$ 0,63** (+ disco de 20 GB pd-standard,
centavos). Destruída em 2026-10-05 11:46 UTC por `bin/lote-gcp.py --destruir`.


## Reprodução

    # lista (numpy); o sha256 é parte da prova
    python3 tools/exatos/lp_bin/fatia_bin.py --n 10 --R 3 --M 11 --listar i.json
    # certificados (numpy + scipy/HiGHS), com orçamento de nós por instância
    python3 tools/exatos/lp_bin/certificar_bin.py --n 10 --R 3 --M 11 --instancias i.json \
        --saida c.jsonl.gz -j 4 --orcamento 20000
    # refaz só as que ficaram sem certificado
    python3 tools/exatos/lp_bin/certificar_bin.py ... --refazer c.jsonl.gz --orcamento 100000 --saida c2.jsonl.gz
    # conferência exata (só biblioteca padrão)
    python3 tools/exatos/lp_bin/verificar_bin.py --n 10 --R 3 --M 11 --instancias i.json \
        --certificados c.jsonl.gz --sha256 "$(sha256sum i.json | cut -c1-64)"
    # medição por sorteio (não é prova)
    python3 tools/exatos/lp_bin/amostra_bin.py --n 11 --R 3 --M 15 --s 7 --k 20 --semente 1
