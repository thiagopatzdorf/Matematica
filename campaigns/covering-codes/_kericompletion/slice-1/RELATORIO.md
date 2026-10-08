# Fatia 1: relatorio

Resultado: nenhum codigo menor que a cota da tabela consultada foi encontrado. 3 de 16 celulas tentadas; 13 NAO_TENTADA (busca sequencial interrompida por reset de sessao; nada alem disso foi gravado).

Ferramenta: `sa_generico.c` (SA generico, `sa q n R M secs seed T0 T1 saida`). Sanidade: com M igual a cota publicada achou cobertura de K7(4,2) com 19 e K3(6,2) com 17 em 20 s (nao verificadas por dois verificadores, so teste da ferramenta, nao e resultado).

| celula | ub publicada (fonte) | tentativa | resultado |
|---|---|---|---|
| K3(6,2) | 17 (Kéri 2011 (tabelas, http://old.sztaki.hu/~keri/codes/)) | slice-1/sa_generico.c (SA em C, mover 1 palavra p/ bola de ponto descoberto), M=16, semente 1, 240s, 1 nucleo nice, best_uncovered=9; nao achou cobertura com M=16 | SEM_MELHORA_NESTA_BUSCA |
| K7(4,2) | 19 (Kéri 2011 (tabelas, http://old.sztaki.hu/~keri/codes/)) | slice-1/sa_generico.c (SA em C, mover 1 palavra p/ bola de ponto descoberto), M=18, semente 1, 240s, 1 nucleo nice, best_uncovered=24; nao achou cobertura com M=18 | SEM_MELHORA_NESTA_BUSCA |
| K3(8,1) | 486 (Kéri 2011 (tabelas, http://old.sztaki.hu/~keri/codes/)) | processo de busca interrompido (reset de sessao) antes de chegar aqui | NAO_TENTADA |
| K2(14,5) | 12 (Kéri 2011 (tabelas, http://old.sztaki.hu/~keri/codes/)) | processo de busca interrompido (reset de sessao) antes de chegar aqui | NAO_TENTADA |
| K2(15,4) | 32 (Kéri 2011 (tabelas, http://old.sztaki.hu/~keri/codes/)) | processo de busca interrompido (reset de sessao) antes de chegar aqui | NAO_TENTADA |
| K2(16,3) | 192 (Kéri 2011 (tabelas, http://old.sztaki.hu/~keri/codes/)) | processo de busca interrompido (reset de sessao) antes de chegar aqui | NAO_TENTADA |
| K2(17,4) | 112 (Kéri 2011 (tabelas, http://old.sztaki.hu/~keri/codes/)) | processo de busca interrompido (reset de sessao) antes de chegar aqui | NAO_TENTADA |
| K2(18,4) | 192 (Kéri 2011 (tabelas, http://old.sztaki.hu/~keri/codes/)) | processo de busca interrompido (reset de sessao) antes de chegar aqui | NAO_TENTADA |
| K5(8,5) | 15 (Kéri 2011 (tabelas, http://old.sztaki.hu/~keri/codes/)) | slice-1/sa_generico.c (SA em C, mover 1 palavra p/ bola de ponto descoberto), M=14, semente 1, 180s, 1 nucleo nice, best_uncovered=1688 (so 18688 movimentos; bola enorme, SA lento); nao achou cobertura com M=14 | SEM_MELHORA_NESTA_BUSCA |
| K3(12,5) | 54 (Kéri 2011 (tabelas, http://old.sztaki.hu/~keri/codes/)) | processo de busca interrompido (reset de sessao) antes de chegar aqui | NAO_TENTADA |
| K2(20,4) | 512 (Kéri 2011 (tabelas, http://old.sztaki.hu/~keri/codes/)) | processo de busca interrompido (reset de sessao) antes de chegar aqui | NAO_TENTADA |
| K3(13,3) | 1215 (Kéri 2011 (tabelas, http://old.sztaki.hu/~keri/codes/)) | processo de busca interrompido (reset de sessao) antes de chegar aqui | NAO_TENTADA |
| K2(21,6) | 64 (Kéri 2011 (tabelas, http://old.sztaki.hu/~keri/codes/)) | processo de busca interrompido (reset de sessao) antes de chegar aqui | NAO_TENTADA |
| K2(22,2) | 24576 (Kéri 2011 (tabelas, http://old.sztaki.hu/~keri/codes/)) | processo de busca interrompido (reset de sessao) antes de chegar aqui | NAO_TENTADA |
| K13(6,1) | 92535 (Kéri 2011 (tabelas, http://old.sztaki.hu/~keri/codes/)) | processo de busca interrompido (reset de sessao) antes de chegar aqui | NAO_TENTADA |
| K2(23,2) | 32768 (Kéri 2011 (tabelas, http://old.sztaki.hu/~keri/codes/)) | processo de busca interrompido (reset de sessao) antes de chegar aqui | NAO_TENTADA |

Nenhum limite inferior foi alterado; nenhuma fechada por busca exata (ILP/SAT nao rodou). K13(6,1) nao e representavel no formato oficial (digitos > 9). "Nao achei" nao significa "nao existe".
