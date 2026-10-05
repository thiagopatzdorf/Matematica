# GAPS2: resultado por célula (2026-10-04)

Missão: células abertas com folga ≤ 2 que ninguém mais estava atacando. Eram `K_3(6,2)` (15–17),
a família binária `K_2(2R+4,R)` (cota superior 12) e `K_2(11,3)` (15–16), mais uma triagem de
`K_7(6,4)`, `K_15(5,3)`, `K_5(9,6)`, `K_8(7,5)`, `K_9(8,6)` e `K_10(9,7)`. A redução usada está
em `GAPS2_K362.md`. O executor é `tools/exatos/gaps2/rodar_pb.py`, que usa RoundingSat com
`--proof-log`, confere cada prova com o VeriPB e grava uma linha JSON por instância.

**Resultado: nenhuma cota mudou.** Nada vai para o ledger. O que fica é a ferramenta, a
reprodução certificada de `K_3(6,2) ≥ 15` e a medição do custo de `K_3(6,2) ≥ 16`.

## Resumo

| célula | lb–ub | o que foi feito | medido | resultado |
|---|---|---|---|---|
| K3(6,2) | 15–17 | M = 14: as 863 instâncias. M = 15: amostra de 240 das 12 049 | M = 14: 863 de 863 inviáveis, as 863 provas VeriPB conferidas. M = 15: 234 de 234 inviáveis e conferidas; 6 duras, de 3,5 min a mais de 30 min (sem prova) | lb 15 reproduzida com certificado. lb 16 **não** fechada: o custo extrapolado e o tamanho das provas passam do orçamento (ver abaixo) |
| K2(2R+4,R), R = 4…10 | 9–12 a 11–12 | só a triagem de viabilidade | o filtro de contagem da fatia não corta nada (`5·V(11,4) = 2810 > 2^11`); `K_2(24,10)` tem `2^24` variáveis de ponto | não atacada: esta redução não serve para ela |
| K2(11,3) | 15–16 | um perfil do controle sem quebra de simetria (`indep_pb`, tipo (8,7) nas 11 coordenadas), RoundingSat por 600 s | `UNKNOWN` após 600 s (142 mil conflitos); são 4 368 perfis | não atacada além disso. Configurações da fatia ~`C(73,10)`, inviável enumerar |
| K7(6,4), K15(5,3), K5(9,6), K8(7,5), K9(8,6), K10(9,7) | folga 2 | triagem de tamanho do PB por pontos | termos de cobertura `q^n·V(n,R)`: 2,9·10⁹, 2,2·10¹⁰, 1,0·10¹², 9,4·10¹¹, 4,1·10¹⁴ e 2,3·10¹⁷ | fora de alcance para esta família de método (o K3(6,2) tem 5,3·10⁴) |

`K_3(7,3)` e `K_4(7,4)` ficaram de fora, porque a missão só os admitia com método novo medido,
e o método daqui já não escala para `K_3(6,2)` com M = 15.

## K_3(6,2): os números

Máquina: `t2d-standard-8` spot, com 8 vCPU e 32 GB, e 8 processos em paralelo. Registros em
`tools/exatos/gaps2/registros/`, uma linha por instância, com resultado, tempos, sha256 do OPB e
sha256 da prova. As provas foram conferidas e descartadas (`--descartar`), porque somam dezenas
de GB; cada uma pode ser regerada pelo comando de reprodução.

**M = 14** (`K3_6_2_M14.jsonl.gz`): 863 instâncias (17 + 17 + 17 com `s* = 3`, 406 + 406 com
`s* = 4`), todas `UNSATISFIABLE` e as 863 com `s VERIFIED UNSATISFIABLE`. Tempo do solver: soma
de 2 469 s e máximo de 581 s. Conferência: soma de 446 s. Isso reproduz, com certificado, a cota
`K_3(6,2) ≥ 15` de Bertolo–Östergård–Weakley (2004), e é a validação do pipeline numa instância
de verdade.

**M = 15**: 12 049 instâncias. Por `(s*, blocos)`: s* = 2 tem 5; s* = 3 tem 108; s* = 4 tem
936; s* = 5, blocos (5,5), tem 11 000. A amostra são 240 índices
(`K3_6_2_M15_amostra.txt`, 2 %), escolhidos ao acaso pelo corpo anterior, sem semente registrada.
Todos rodaram:

- 234 terminaram `UNSATISFIABLE` com prova conferida (`K3_6_2_M15.jsonl.gz`). Tempo do solver:
  média de 12,6 s, mediana de 3,6 s, máximo de 215 s e soma de 2 944 s. Conferência: soma de
  494 s e máximo de 28 s. A prova chega a 2,2 GB, e as 234 somam 36,8 GB.
- 6 são duras, todas com `s* = 5` (índices 7955, 9118, 10603, 11739, 11804 e 11927). Com
  `--proof-log`, passaram de 7 a 13 min sem terminar e escreveram de 2,1 a 4,6 GB de prova cada,
  a ~7 MB/s por processo. O disco de 29 GB ia encher em minutos, então a rodada foi parada.
  Depois rodaram de novo **sem prova**, um processo por instância, com teto de 30 min. Aqui só
  há o veredito, que **não** vale como certificado. Cinco terminaram inviáveis: 11927 em 3 min
  30 s, 11739 em 7 min 41 s, 11804 em 9 min 48 s, 7955 em 26 min 10 s e 9118 em 29 min 8 s. A
  10603 foi parada aos 30 min sem veredito (1,35 milhão de conflitos).

**Extrapolação** (amostra de 240, então é ordem de grandeza):

- fáceis: ~11 750 × (12,6 s + 2,1 s) ≈ 48 CPU-h;
- duras: 6/240 ≈ 2,5 %, ou seja, ~300 instâncias de 3,5 min a mais de 30 min sem prova (média
  das cinco que terminaram: ~15 min). Com
  prova, a ~7 MB/s, uma instância de 30 min escreve ~13 GB. Só isso já passa de 150 CPU-h, e
  pede disco de dezenas de GB por processo, ou prova em fluxo direto para o VeriPB (não testado);
- a cauda não tem teto conhecido: uma das seis passou de 30 min sem veredito.

Além do custo, fechar `K_3(6,2) ≥ 16` como teorema pede uma **codificação independente**. O
controle sem quebra (`indep_pb`, por perfil de fibras) teria o perfil `(5,5,5)^6` inteiro como
uma instância só, e isso não termina. Então, mesmo com as 12 049 inviáveis, faltaria o segundo
caminho.

**Decisão (minha):** parar `K_3(6,2)` aqui. Com US$ 10 no total para a missão, o resto da
rodada de M = 15 custaria uma parte grande do orçamento sem teto na cauda e sem a codificação
independente. O que destrava é a simetria que sobra no caso equilibrado (`s* = 5`, as 18 fibras
com 5 palavras, o mesmo código em até 18 instâncias). Uma escolha canônica da fibra, e não
"uma fibra mínima qualquer", cortaria isso. Ela não foi implementada.

## Reprodução

    # lista (precisa de numpy)
    python3 tools/exatos/gaps2/rodar_pb.py --q 3 --n 6 --R 2 --M 15 --listar i15.json
    # roda com prova VeriPB (só stdlib + binários roundingsat e veripb)
    ROUNDINGSAT=... VERIPB=... python3 tools/exatos/gaps2/rodar_pb.py --q 3 --n 6 --R 2 --M 15 \
        --instancias i15.json --dir saida -j 8 --descartar --so "$(cat tools/exatos/gaps2/registros/K3_6_2_M15_amostra.txt)" --tempo 3600

Binários: RoundingSat compilado da fonte oficial (com `--proof-log`) e VeriPB 2 (Rust). Os testes
`tests/test_gaps2*.py` rodam com eles quando as variáveis `ROUNDINGSAT` e `VERIPB` apontam para
os executáveis, e pulam quando não apontam.

## Custo

Uma VM spot (`t2d-standard-8`, 30 GB pd-standard, sem IP externo) ligada de cerca de 22:00 às
23:22 UTC. Pelo preço de tabela do spot nessa região, isso dá bem menos de US$ 1. O container
local e a factory-01 não entram na conta. A VM foi parada ao fim (prova no relatório do PR).
