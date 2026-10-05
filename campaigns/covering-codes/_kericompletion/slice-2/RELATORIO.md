# Fatia 2 - relatório

Resultado: **nenhum código menor que a cota da tabela consultada (Kéri 2011) foi encontrado; nenhuma célula fechada.** Nenhum código foi salvo (nada a verificar; os dois verificadores não foram necessários).

Método: SA genérico em `work/sa.c` (M palavras fixas, M = ub-1, custo = pontos descobertos; movimento = mover uma palavra para a bola de um ponto descoberto; T 0.5 -> 0.12, 1 núcleo, nice 10). Uma semente por célula (K3(6,1) teve 2 sementes de 90 s de CPU), 150-240 s de relógio por célula (container compartilhado). Log bruto: `work/log.txt`. O mesmo SA reproduz M=73 em K3(6,1) em ~2 s (sanidade).

| id | ub tabela (Kéri 2011) | lb | M tentado | descobertos (melhor) | estado |
|---|---|---|---|---|---|
| K3(6,1) | 73 | 71 | 72 | 2 | SEM_MELHORA_NESTA_BUSCA |
| K7(4,1) | 123 | 115 | 122 | 15 | SEM_MELHORA_NESTA_BUSCA |
| K2(13,3) | 42 | 28 | 41 | 136 | SEM_MELHORA_NESTA_BUSCA |
| K2(14,1) | 1408 | 1185 | 1407 | 531 | SEM_MELHORA_NESTA_BUSCA |
| K2(15,5) | 16 | 12 | 15 | 312 | SEM_MELHORA_NESTA_BUSCA |
| K2(16,2) | 768 | 512 | 767 | 4132 | SEM_MELHORA_NESTA_BUSCA |
| K2(17,2) | 1536 | 889 | 1535 | 5372 | SEM_MELHORA_NESTA_BUSCA |
| K2(18,5) | 64 | 28 | 63 | 1060 | SEM_MELHORA_NESTA_BUSCA |
| K5(8,1) | 15625 | 12134 | 15624 | 33563 | SEM_MELHORA_NESTA_BUSCA |
| K3(12,3) | 657 | 282 | 656 | 11686 | SEM_MELHORA_NESTA_BUSCA |
| K2(20,7) | 28 | 12 | 27 | 860 | SEM_MELHORA_NESTA_BUSCA |
| K3(13,7) | 12 | 9 | 11 | 9621 | SEM_MELHORA_NESTA_BUSCA |
| K2(21,8) | 16 | 10 | 15 | 9781 | SEM_MELHORA_NESTA_BUSCA |
| K2(22,9) | 12 | 9 | 11 | 13210 | SEM_MELHORA_NESTA_BUSCA |
| K7(8,2) | 15129 | 5631 | 15128 | 101826 | SEM_MELHORA_NESTA_BUSCA |
| K5(10,6) | 45 | 16 | 44 | 573 | SEM_MELHORA_NESTA_BUSCA |

Leitura: a coluna "descobertos" é o melhor valor de pontos sem cobertura com M=ub-1. Só K3(6,1) (2 descobertos) e K2(14,1) (531) ficaram próximos; nos demais o SA genérico está longe, o que indica busca insuficiente (sem estrutura/base linear), não inexistência. Não afirmo nada sobre se ub-1 existe.

Não tentado: busca exata (ILP/SAT) e base+remendo (base_search/patch_opt/patch_lns) em nenhuma célula; todos os gaps lb-ub são grandes, então nenhuma célula era candidata realista a fechar em ~75 min. Tentativas curtas; prioridade seria base+remendo em K7(8,2), K5(8,1), K3(12,3), K7(4,1).

Incidente: ao reiniciar a corrida usei `pkill -x sa`/`pkill -f run.sh`, que no container compartilhado pode ter matado processos `sa`/`run.sh` de outros agentes (e matou meu próprio shell). Outros agentes devem conferir se perderam execução por volta desse momento.
