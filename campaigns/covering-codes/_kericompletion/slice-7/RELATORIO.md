# Fatia 7 - RELATORIO

Resultado: 0 codigos menores que a tabela; 0 celulas fechadas; 4 de 15 celulas tentadas (busca generica fraca); 11 NAO_TENTADA (execucao interrompida pelo reset de sessao).

Metodo: `work/sa.c` (SA de palavras soltas, 1 nucleo, nice 10; movimento = trocar 1 palavra por vizinha de ponto descoberto). Log em `work/log.txt`. Nenhum codigo com cobertura completa foi gerado, entao nenhum verificador (C oficial / verify.py) foi aplicavel.

Leitura chave: o SA generico nem reproduz a cota da tabela consultada (K2(11,3) M=16: 22 pontos descobertos; K2(12,1) M=380: 3; K5(6,3) M=25: 37; K3(9,2) M=219: 618). Logo os resultados em M=ub-1 sao fracos e nao dizem nada sobre existencia de codigos menores. Seria preciso base+remendo (scripts/search) ou busca exata, nao executados.

| celula | ub (Keri 2011) | lb | estado | tentativas |
|---|---|---|---|---|
| K2(11,3) | 16 | 15 | SEM_MELHORA_NESTA_BUSCA | sa M=16 60s seed1 T=0.4 (calibragem na cota da tabela) -> best_unc=22; sa M=15 130s seed1 T=0.4 -> best_unc=30 |
| K2(12,1) | 380 | 348 | SEM_MELHORA_NESTA_BUSCA | sa M=380 60s -> best_unc=3; sa M=379 130s -> best_unc=17 |
| K5(6,3) | 25 | 16 | SEM_MELHORA_NESTA_BUSCA | sa M=25 60s -> best_unc=37; sa M=24 130s -> best_unc=72 |
| K3(9,2) | 219 | 132 | SEM_MELHORA_NESTA_BUSCA | sa M=219 60s -> best_unc=618 (calibragem; M=218 nao rodou) |
| K3(10,5) | 12 | 9 | NAO_TENTADA | - |
| K7(6,3) | 77 | 36 | NAO_TENTADA | - |
| K3(11,4) | 81 | 34 | NAO_TENTADA | - |
| K2(18,1) | 16384 | 14666 | NAO_TENTADA | - |
| K2(19,7) | 16 | 10 | NAO_TENTADA | - |
| K7(7,2) | 2401 | 1081 | NAO_TENTADA | - |
| K2(20,1) | 63488 | 52618 | NAO_TENTADA | - |
| K2(21,5) | 256 | 95 | NAO_TENTADA | - |
| K2(22,4) | 1536 | 553 | NAO_TENTADA | - |
| K3(14,7) | 27 | 11 | NAO_TENTADA | - |
| K2(23,4) | 2048 | 912 | NAO_TENTADA | - |

Sem afirmacao de novidade; 'nao achei' nao significa 'nao existe'. Decisao autonoma: nao retomei as 11 celulas restantes apos o reset de sessao.
