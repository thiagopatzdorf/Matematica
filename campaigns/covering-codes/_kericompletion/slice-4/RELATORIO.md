# Fatia 4 — relatório (parcial, busca de linha de base)

Método: recozimento simulado genérico (`work/sa.c`, 1 núcleo, `nice 10`, semente 1) minimizando pontos descobertos com M palavras fixas. Cada célula: calibração em M=ub publicada e tentativa em M=ub-1. Os ciclos de tempo foram curtos (30+190 s nas 3 primeiras, 15+85 s nas demais; o laço foi interrompido por reset de sessão e reiniciado). Comandos: `./sa q n R M secs 1 saida` (ver `work/run.sh`, `work/run2.sh`, `work/log.txt`).

**Resultado: nenhum código encontrado com M menor que a cota da tabela; nenhuma célula fechada.** Nem a calibração em M=ub publicada cobriu em nenhum caso (o SA genérico é mais fraco que as construções da tabela), portanto estes números são só limite do método, nunca evidência sobre K_q(n,R).

| célula | ub tabela (fonte) | lb | M tentado | melhor nº descobertos (calibração em ub / em ub-1) | estado |
|---|---|---|---|---|---|
| K2(10,1) | 120 (keri_2011) | 107 | 119 | 23 / 5 | SEM_MELHORA_NESTA_BUSCA |
| K5(5,1) | 184 (keri_2011) | 162 | 183 | 21 / 48 | SEM_MELHORA_NESTA_BUSCA |
| K2(13,2) | 128 (keri_2011) | 101 | 127 | 602 / 598 | SEM_MELHORA_NESTA_BUSCA |
| K7(5,1) | 769 (keri_2011) | 606 | 768 | 975 / 961 | SEM_MELHORA_NESTA_BUSCA |
| K3(10,4) | 36 (keri_2011) | 18 | 35 | 248 / 317 | SEM_MELHORA_NESTA_BUSCA |
| K5(7,3) | 100 (keri_2011) | 38 | 99 | 77 / 68 | SEM_MELHORA_NESTA_BUSCA |
| K2(17,5) | 32 (keri_2011) | 20 | 31 | 2343 / 2536 | SEM_MELHORA_NESTA_BUSCA |
| K2(18,2) | 2944 (keri_2011) | 1702 | 2943 | 9934 / 9306 | SEM_MELHORA_NESTA_BUSCA |
| K2(19,3) | 1024 (keri_2011) | 513 | 1023 | 16263 / 15703 | SEM_MELHORA_NESTA_BUSCA |
| K3(12,1) | 27702 (keri_2011) | 21531 | 27701 | 46305 / 41636 | SEM_MELHORA_NESTA_BUSCA |
| K2(20,5) | 128 (keri_2011) | 62 | 127 | 16573 / 15527 | SEM_MELHORA_NESTA_BUSCA |
| K5(9,2) | 6375 (keri_2011) | 3367 | 6374 | 114136 / 106599 | SEM_MELHORA_NESTA_BUSCA |
| K2(21,1) | 122880 (keri_2011) | 96477 | 122879 | 236762 / 184693 | SEM_MELHORA_NESTA_BUSCA |
| K3(14,5) | 243 (keri_2011) | 69 | 242 | 7818 / 4845 | SEM_MELHORA_NESTA_BUSCA |
| K2(23,6) | 224 (keri_2011) | 73 | 223 | 42803 / - | NAO_TENTADA |
| K5(10,2) | 23000 (keri_2011) | 13161 | 22999 | - / - | NAO_TENTADA |

Notas: K2(23,6) em M=223 foi interrompida antes de terminar (só a calibração em M=224 rodou; estado NAO_TENTADA); K5(10,2) não foi tentada (NAO_TENTADA). Dois verificadores (C oficial e verify.py) não foram usados pois não houve código a verificar. Nada foi alterado fora de slice-4/.
