# Fatia 6: relatório (busca parcial, recozimento simulado)

Método: `work/sa.c` (recozimento simulado de M palavras, custo = pontos descobertos, delta exato por troca de um dígito), 1 núcleo, `nice -n 10`, alvo M = ub_publicada - 1. Cada célula: 2 execuções curtas (seeds 11 e 12, ciclos térmicos 3; T 0.35->0.15 e 0.25->0.10). Células K2(11,1), K2(12,2) e parte de K5(6,2): 110 s por execução; as demais: 50 s.

Nenhum código com M menor que a cota da tabela consultada foi encontrado nesta busca; nenhuma célula foi fechada. Não é afirmação de inexistência. Limitações: o SA não foi calibrado (sanidade: K2(11,1) com M=200 cobriu; com M=191 ficou em 6 pontos descobertos), e os limites inferiores não foram tocados. Sem verificadores rodados, pois nada a verificar.

| célula | lb | ub tabela (fonte) | M tentado | menor nº de pontos descobertos | estado |
|---|---|---|---|---|---|
| K2(11,1) | 180 | 192 (keri_2011) | 191 | 6 | SEM_MELHORA_NESTA_BUSCA |
| K2(12,2) | 62 | 78 (keri_2011) | 77 | 207 | SEM_MELHORA_NESTA_BUSCA |
| K5(6,2) | 71 | 125 (keri_2011) | 124 | 229 | SEM_MELHORA_NESTA_BUSCA |
| K3(9,3) | 31 | 54 (keri_2011) | 53 | 262 | SEM_MELHORA_NESTA_BUSCA |
| K3(10,2) | 323 | 555 (keri_2011) | 554 | 2169 | SEM_MELHORA_NESTA_BUSCA |
| K5(7,1) | 2765 | 3125 (keri_2011) | 3124 | - | NAO_TENTADA (sa.c limita M<=1024) |
| K2(17,1) | 7426 | 8192 (keri_2011) | 8191 | - | NAO_TENTADA (sa.c limita M<=1024) |
| K2(18,7) | 9 | 12 (keri_2011) | 11 | 1049 | SEM_MELHORA_NESTA_BUSCA |
| K2(19,5) | 40 | 64 (keri_2011) | 63 | 23016 | SEM_MELHORA_NESTA_BUSCA |
| K7(7,3) | 127 | 343 (keri_2011) | 342 | 2308 | SEM_MELHORA_NESTA_BUSCA |
| K2(20,8) | 9 | 12 (keri_2011) | 11 | 3112 | SEM_MELHORA_NESTA_BUSCA |
| K5(9,6) | 10 | 12 (keri_2011) | 11 | 2404 | SEM_MELHORA_NESTA_BUSCA |
| K2(22,7) | 21 | 64 (keri_2011) | 63 | 1421 | SEM_MELHORA_NESTA_BUSCA |
| K3(14,4) | 273 | 729 (keri_2011) | 728 | 67174 | SEM_MELHORA_NESTA_BUSCA |
| K2(23,8) | 14 | 32 (keri_2011) | 31 | 17604 | SEM_MELHORA_NESTA_BUSCA |

Comandos/logs: `work/log_*.txt`, driver `work/run.sh`/`work/run2.sh`.
