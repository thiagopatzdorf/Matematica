# K_3(6,1): viabilidade medida (2026-10-04)

**Pergunta:** quanto custa fechar o football pool `K_3(6,1)` (hoje 71 ≤ K ≤ 73) com certificado,
pela decomposição de Linderoth–Margot–Thain (LMT) resolvida por SAT/PB com prova?

**Resposta curta:** com os métodos medidos aqui, **inviável** dentro de qualquer orçamento
razoável. O melhor motor (RoundingSat, planos de corte) resolve os subproblemas mais fáceis de
v = 6 (M = 59, 60) em 0,5–10 min cada, mas o tempo cresce ~1,8–3,1× por palavra (cota inferior) a mais e 4 de 6 subproblemas de M = 62 e
6 de 6 de M = 72 sorteados estouraram 30 min. A cota inferior **medida** para
M = 72 é 30 300 CPU-h (US$ 548) mesmo supondo que nenhum subproblema passe de 30 min; a extrapolação pela escada medida dá
de 9 × 10^6 a 2 × 10^9 CPU-h (US$ 1,6 × 10^5 a 4 × 10^7), ordens acima do teto. Não gastei além de US$ 0,40 (VM de 2 h 40 min).

## 1. A decomposição de LMT (relatório técnico de 2007, PDF lido)

Fonte: J. Linderoth, F. Margot, G. Thain, *Improving Bounds on the Football Pool Problem via
Symmetry Reduction and High-Throughput Computing*, INFORMS J. Computing 21 (2009) 445–457;
relatório técnico em `jlinderoth.github.io/papers/Linderoth-Margot-Thain-07-TR-2.pdf`.

1. **Sistema de cobertura (Östergård–Blass 2001)** com m = 2: `y_jk` = palavras com prefixo
   (j,k); `9 y_jk + Σ_vizinhos ≥ 81`, `Σ y = M` (eq. 2.2). As soluções não isomorfas são as
   "sequências".
2. **Exclusão de sequências** (seção 3.3): provam por PLI que toda fibra tem ≥ 20 palavras
   (p = 19: 15 min com "squashing") e depois ≥ 22 (p = 21: 385 967 PLIs, 49 023 CPU-h só de
   enumeração + 83 CPU-dias + 139 h de MINTO). Isso **não tem certificado**; os próprios autores
   escrevem que o trabalho "is not a proof in the mathematical sense".
3. **y-SIP** (2.3): o PLI original com as contagens por bloco fixas, resolvido por
   branch-and-bound com poda de isomorfos (FATCOP + Condor/MW, até 4 500 processadores), com
   reordenação e **agregação** das quatro últimas entradas de y (3.1).
4. Números publicados (tabela 2 e 4): M = 66..72 têm 797, 1 723, 3 640, 7 527, 13 600, 24 023 e
   40 431 sequências (264 e 393 agregadas em M = 71 e 72). M = 69 custou **110 anos-CPU** e
   M = 70 **30 anos-CPU** (grade de 2007). M = 71 e 72 nunca terminaram: a cota está em 71 desde
   2009.

**Depois de 2009** (consultas da triagem, `TRIAGEM_2026-10-04.md`, seção "Literatura"): as 18
obras que citam LMT no OpenAlex são simetria em PLI (orbital branching, Ostrowski et al.) e
Marenco–Rey 2026 (estudo poliédrico, sem cota nova); Gijswijt–Polak (SDP) dá 60,86; Marosi 2026
tentou a inferior por SDP sem melhorar. Ninguém retomou M = 71/72.

## 2. Reprodução da decomposição

`tools/exatos/k361/sistema.c` (README ao lado tem o argumento completo). Contagens de órbitas
pelo grupo de ordem 72, conferidas no `tests/test_k361.py`:

| M | p (fibras ≥) | nossas sequências | publicado |
|---|---|---|---|
| 64, 65, 66 | — | 423, 839, 1 674 | 423, 839, 1 674 (Margot et al. 2003, citado por LMT) |
| 66, 67, 68 | 20 | 797, 1 723, 3 640 | 797, 1 723, 3 640 (LMT tabela 2) |
| 69 | 20 | **7 257** | 7 527 (LMT; provável troca de dígitos, os outros seis batem) |
| 70, 71, 72 | 20 | 13 600, 24 023, 40 431 | 13 600, 24 023, 40 431 |
| 71, 72 | 22 | 4 739, 9 942 | (LMT usaria p = 22 depois da exclusão de p = 21) |
| 71, 72 | 18 (elementar) | 36 666, 59 707 | — |

Descoberta: a tabela 2 de LMT foi feita com **p = 20**, não 22.

**Uma melhoria sem computação.** Em vez da exclusão de LMT, escolho as coordenadas 0 e 1 como
as de menor fibra; então as fibras das coordenadas 2..5 têm pelo menos `max(menor linha, menor
coluna)` palavras. Isso dispensa os 49 mil CPU-h não certificados de LMT e entra na CNF/OPB de
cada sequência (teste dedicado). O preço: M = 72 vira 59 707 sequências (cota elementar 18) em
vez de 9 942.

**Qual M primeiro.** ∄72 sozinho dá `K = 73` (um código menor completa-se até 72 palavras), sem
precisar refazer 66..71. ∄71 é mais barato (36 666 contra 59 707 sequências, e cada uma com uma
palavra a menos) mas só leva a cota a 72. Medi os dois extremos da escada (M = 59..66) e o alvo
M = 72; a escada mostra que o custo por palavra cresce rápido demais para que 71 seja "barato".

## 3. Validação do pipeline em casos conhecidos

| caso | resultado | prova |
|---|---|---|
| K_3(5,1) = 27: ∄26 (8 sequências) | 8/8 UNSAT, CaDiCaL 17 s no total | 8/8 `lrat-check` VERIFIED (container e VM) e 8/8 `lrat.py` (verificador independente de `k742`) |
| idem, RoundingSat | 8/8 UNSAT, 8,7 s no total | 8/8 **VeriPB 3.0.2** `s VERIFIED UNSATISFIABLE` |
| K_3(5,1) = 27: existe 27 (40 sequências) | 1 SAT, 39 UNSAT; o código achado cobre Z_3^5 | — |
| contagens de sequências | 6 de 7 linhas publicadas reproduzidas exatamente | `tests/test_k361.py` |

Defeito pego no caminho: o primeiro `amostra.py` tomava `"c NOT VERIFIED"` como sucesso (contém
"VERIFIED"), e o CaDiCaL 3 grava LRAT binário por padrão. Os dois estão corrigidos e o teste de
resumo cobre a marcação de tempo esgotado.

## 4. Medições em v = 6

VM `k361-a`, c2d-highmem-8 spot (AMD EPYC 7B13, 8 vCPU = 4 núcleos com SMT, 62 GB), um processo
por vCPU; tempos de parede por subproblema. Tarifa: **US$ 0,1448/h por 8 vCPU = US$ 0,0181 por
vCPU-h** (tabela do `lote-gcp.py`, preço spot medido em 2026-10-02, southamerica-east1).
Tempo-limite 30 min por subproblema (CaDiCaL em M = 59: 4 h, interrompido aos 1 h 58 min).
Dados brutos em `tools/exatos/k361/medicoes/*.jsonl`; `resumo.py` gera as colunas. As
sequências de M = 72 são as do modo `auto` (cota 18, 59 707); o `p` gravado em cada linha é a
cota de fibra do sufixo calculada para aquela sequência. M = 64 e 66 com RoundingSat ficaram de
fora: M = 62 já estourava, e o tempo foi para o alvo.

| motor | M | amostra | resultado | mediana | p90 | máx |
|---|---|---|---|---|---|---|
| CaDiCaL + lex-leader | 59 | 2 de 2 | 2 TEMPO (interrompido) | > 7 113 s | | |
| CaDiCaL + lex-leader | 66 (p = 20) | 8 de 797 | 8 TEMPO | > 1 800 s | | |
| SCIP 10 (PLI, simetria padrão) | 66 (p = 20) | 2 | 2 TEMPO (container) | > 600 s | | |
| CP-SAT 9.15 | v = 5, M = 26 | 1 | TEMPO | > 120 s | | |
| RoundingSat + SoPlex | 59 | 2 de 2 | 2 UNSAT | 328 s | 621 s | 621 s |
| RoundingSat + SoPlex | 60 | 6 de 11 | 6 UNSAT | 192 s | 376 s | 376 s |
| RoundingSat + SoPlex | 62 | 6 de 88 | 2 UNSAT, 4 TEMPO | > 1 815 s | > 1 830 s | > 1 835 s |
| RoundingSat + SoPlex | **72** | 6 de 59 707 | **6 TEMPO** | > 1 826 s | > 1 834 s | > 1 835 s |

Leituras:

- **SAT puro (o método do K_7(4,2)) não transfere.** O y-SIP é um problema de contagem
  (cobertura com somas fixas); CDCL não faz o raciocínio de PL que LMT e Margot usam. O CaDiCaL não
  refuta nem M = 59, doze palavras abaixo da cota conhecida.
- **Planos de corte ajudam muito** (RoundingSat refuta as duas sequências de M = 59 em 35 s e
  621 s; o CaDiCaL não refutou nenhuma em 7 113 s), mas não o bastante: o salto de M = 60 para
  M = 62 já leva a mediana de 192 s para além do limite de 30 min.

## 5. Extrapolação

Só existem medições com tempo finito até M = 62, e em M = 62 a mediana já é censurada. Por
isso tudo abaixo é **cota inferior** do custo com este pipeline (`resumo.escada`, testado):

| cenário | fator por palavra | s por subproblema (M = 72) | CPU-h, M = 72 (59 707) | US$ | CPU-h, M = 71 (36 666) | US$ |
|---|---|---|---|---|---|---|
| piso medido: nada passa de 30 min | 1 | 1 826 | 30 300 | 548 | 18 600 | 337 |
| escada M = 59 → 62 (medianas 328 s → > 1 815 s) | ≥ 1,77 | ≥ 5,4 × 10^5 | ≥ 9,0 × 10^6 | ≥ 1,6 × 10^5 | ≥ 3,1 × 10^6 | ≥ 5,7 × 10^4 |
| escada M = 60 → 62 (medianas 192 s → > 1 815 s) | ≥ 3,08 | ≥ 1,4 × 10^8 | ≥ 2,3 × 10^9 | ≥ 4,1 × 10^7 | ≥ 4,6 × 10^8 | ≥ 8,3 × 10^6 |

- O **piso** é a única linha sem modelo: 6 de 6 subproblemas sorteados de M = 72 passaram de
  30 min, então a média é pelo menos isso (bootstrap 90 % da média censurada: 30 232–30 363
  CPU-h; com 6 de 6 censurados, a chance de um subproblema típico caber em 30 min é pequena:
  se metade coubesse, 6 de 6 estourarem teria probabilidade 1/64).
- O **intervalo** da extrapolação é o espaço entre as duas escadas: 9 × 10^6 a 2 × 10^9 CPU-h
  para ∄72, e ambas são cotas inferiores porque a mediana de M = 62 é censurada. A amostra é
  pequena (2, 6, 6, 6) e M = 59 tem só duas sequências, por isso dou cenário, não ponto.
- Comparação externa: LMT gastaram ~110 anos-CPU (~9,6 × 10^5 CPU-h) em M = 69 com
  branch-and-bound de PLI e poda de isomorfos sobre 7 527 sequências. Nosso pipeline, a 1,77×
  por palavra, já está acima disso em M = 69 com cota de prova; ele é mais fraco que o B&B de
  LMT, não mais forte.

## 6. Recomendação

**Não financiar a campanha.** Mesmo o piso medido (US$ 548 para ∄72, sem crescimento
nenhum) passa cem vezes o teto desta fase, e a extrapolação mais otimista é US$ 1,6 × 10^5.
Fechar `K_3(6,1)` com certificado não é questão de computação com estes motores; é de método.

O que mudaria a conta, em ordem de custo (nenhum foi tentado aqui):

1. **PLI com prova** no lugar de SAT/PB: um branch-and-bound com relaxação de PL, simetria
   orbital e a agregação das quatro últimas entradas de y (LMT 3.1), emitindo certificado VIPR
   (SCIP exato). É o que fez M = 69, 70 terminarem; o desafio é o certificado num B&B desse
   tamanho. Medir primeiro em M = 62, onde o RoundingSat já estoura.
2. **Agregar subproblemas**: LMT reduzem 40 431 sequências de M = 72 a 393 grupos agregados.
   Nosso modo `auto` dispensa a exclusão não certificada mas multiplica as sequências (59 707
   contra 9 942 com p = 22); certificar a exclusão p = 21 de LMT (49 mil CPU-h na grade de 2007)
   pode ser mais barato que pagar por 6× mais subproblemas.
3. Só depois disso, uma nova amostra (30 subproblemas de M = 72, ~US$ 2) para reabrir esta
   conta. Qualquer gasto acima de US$ 5 é decisão do mantenedor.

## Custo desta fase e limpeza

- VM `k361-a` (c2d-highmem-8 spot): criada 20:14:48 UTC, desligada e destruída às ~22:53 UTC
  de 2026-10-04, ~2 h 40 min a US$ 0,1448/h = **US$ 0,39**, mais disco (centavos). O container
  local (SCIP, CP-SAT, validações v = 5) não tem custo de nuvem. Total da fase: **≈ US$ 0,40**,
  dentro do teto de US$ 5.
- A VM foi apagada com `lote-gcp.py --destruir` depois de os resultados estarem neste branch
  (`medicoes/`); `vm.sh` a reconstrói do zero (solvers por commit, ver abaixo).
- Versões: repo `d3cfed5` na VM; CaDiCaL `c607304`, kissat `2e3b2dc`, drat-trim `8af8e56`,
  RoundingSat `d4edbf7` (com SoPlex).

## Decisões tomadas sozinho

- RoundingSat como motor principal depois de o CaDiCaL não refutar M = 59 (decisão de método).
- Cortei M = 64 e 66 da escada do RoundingSat quando M = 62 estourou, para gastar o tempo de VM
  no alvo M = 72 (semente 7, 6 sequências).
- Interrompi o CaDiCaL de M = 59 aos 7 113 s (limite era 14 400 s): o RoundingSat já resolvera
  as mesmas duas sequências em 35 s e 621 s, e o número só cresceria a cota inferior.
- A extrapolação usa duas escadas (base M = 59 e M = 60) em vez de um ajuste, porque com uma
  mediana censurada no topo qualquer ajuste é cota inferior; o intervalo é entre elas.
- Destruí a VM (não só desliguei): os dados estão no branch e `vm.sh` a reconstrói.
- Removi o caminho CP-SAT de `ysip.py`/`amostra.py` (só medição, sem prova, e já superado pelo
  RoundingSat); o resultado medido continua na tabela.
