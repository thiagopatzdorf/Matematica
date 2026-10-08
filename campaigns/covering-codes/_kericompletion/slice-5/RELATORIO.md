# Fatia 5 — relatório (covering codes K_q(n,R))

Método: SA genérico em C (`work/sa.c`, move uma coordenada de uma palavra, metade guiada por ponto descoberto, T 1.0→0.2), alvo M = ub_publicada−1, 1 núcleo, 1 semente. Calibração: K2(11,2) com M=50 achou cobertura em 3 s (SA funciona), mas em M=ub−1 nenhuma célula chegou a 0 descobertos.

Nenhum código menor que a cota da tabela consultada foi encontrado; nenhuma célula foi fechada (não houve busca exata ILP/SAT: espaços de 16 mil a 8 milhões de pontos tornam o ILP direto inviável no orçamento). Resultado negativo desta busca curta, não prova de inexistência.

| célula | ub tabela (fonte) | lb | M tentado | melhor nº de pontos descobertos | s | estado |
|---|---|---|---|---|---|---|
| K2(11,2) | 44 (keri_2011) | 37 | 43 | 24 | 191 | SEM_MELHORA_NESTA_BUSCA |
| K2(12,3) | 28 (keri_2011) | 19 | 27 | 15 | 191 | SEM_MELHORA_NESTA_BUSCA |
| K2(13,1) | 704 (keri_2011) | 607 | 703 | 456 | 46 | SEM_MELHORA_NESTA_BUSCA |
| K7(5,3) | 17 (keri_2011) | 15 | 16 | 62 | 191 | SEM_MELHORA_NESTA_BUSCA |
| K3(10,3) | 105 (keri_2011) | 61 | 104 | 1807 | 46 | SEM_MELHORA_NESTA_BUSCA |
| K5(7,4) | 21 (keri_2011) | 12 | 20 | 234 | 61 | SEM_MELHORA_NESTA_BUSCA |
| K2(17,6) | 16 (keri_2011) | 11 | 15 | 1110 | 46 | SEM_MELHORA_NESTA_BUSCA |
| K2(18,3) | 512 (keri_2011) | 316 | 511 | 13434 | 46 | SEM_MELHORA_NESTA_BUSCA |
| K2(19,6) | 32 (keri_2011) | 17 | 31 | 3871 | 46 | SEM_MELHORA_NESTA_BUSCA |
| K3(12,2) | 2187 (keri_2011) | 1919 | 2186 | 102158 | 46 | SEM_MELHORA_NESTA_BUSCA |
| K2(20,2) | 8192 (keri_2011) | 5330 | 8191 | 86446 | 46 | SEM_MELHORA_NESTA_BUSCA |
| K5(9,1) | 78125 (keri_2011) | 53896 | 78124 | 132922 | 46 | SEM_MELHORA_NESTA_BUSCA |
| K2(22,5) | 512 (keri_2011) | 150 | 511 | 5470 | 46 | SEM_MELHORA_NESTA_BUSCA |
| K3(14,6) | 81 (keri_2011) | 24 | 80 | 1242 | 48 | SEM_MELHORA_NESTA_BUSCA |
| K2(23,5) | 640 (keri_2011) | 235 | 639 | 74075 | 46 | SEM_MELHORA_NESTA_BUSCA |
| K5(10,1) | 390625 (keri_2011) | 241122 | 390624 | 622064 | 46 | SEM_MELHORA_NESTA_BUSCA |

Tempo: 190 s por célula nas três primeiras (K7(5,3), K2(11,2), K2(12,3)), 45 a 61 s nas demais (sessão interrompida no meio; tempos curtos, 1 semente). Verificadores (C oficial e verify.py) não foram usados porque nenhum código foi achado. Nada fora de slice-5/ foi alterado.
