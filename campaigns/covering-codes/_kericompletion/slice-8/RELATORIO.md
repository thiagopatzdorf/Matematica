# Fatia 8 — relatório parcial

Resultado: **nenhum código menor que a cota da tabela consultada (Kéri 2011 (tabelas, http://old.sztaki.hu/~keri/codes/)) foi achado; nenhuma célula fechada.** Nenhum arquivo em `codes/` (nada para verificar; /tmp/verify e verify.py não foram necessários).

Células tentadas: 8 de 15 (busca fraca, ver abaixo). O resto: NAO_TENTADA (limite de tempo/sessão).

| célula | ub publicada | estado |
|---|---|---|
| K3(7,2) | 34 | SEM_MELHORA_NESTA_BUSCA |
| K2(12,4) | 12 | SEM_MELHORA_NESTA_BUSCA |
| K2(14,4) | 28 | SEM_MELHORA_NESTA_BUSCA |
| K3(9,4) | 18 | SEM_MELHORA_NESTA_BUSCA |
| K3(10,1) | 3645 | NAO_TENTADA |
| K7(6,2) | 343 | SEM_MELHORA_NESTA_BUSCA |
| K3(11,5) | 27 | SEM_MELHORA_NESTA_BUSCA |
| K5(8,3) | 325 | NAO_TENTADA |
| K2(19,2) | 4096 | NAO_TENTADA |
| K7(7,4) | 49 | SEM_MELHORA_NESTA_BUSCA |
| K3(13,5) | 108 | SEM_MELHORA_NESTA_BUSCA |
| K2(21,4) | 896 | NAO_TENTADA |
| K2(22,6) | 128 | NAO_TENTADA |
| K3(14,2) | 19683 | NAO_TENTADA |
| K2(23,7) | 64 | NAO_TENTADA |

## O que foi feito
- `sa_generico.c`: recozimento simulado próprio (q,n,R,M), 1 núcleo, nice 10. Compilação: `gcc -O3 -march=native -o sa sa_generico.c -lm`; uso `sa q n R M secs seed [out]` (T0/T1 por variável de ambiente).
- Rodadas com M = ub-1 (120-150 s cada): melhores descobertos em resultados.json. Nenhuma chegou a 0.
- Calibragem: em K3(7,2) a busca não atingiu nem M=36 (cota da tabela: 34), então o resultado negativo diz pouco sobre a existência de códigos menores; "não achei" não é "não existe".
- Kit base+remendo: só `base_search enum` em K7(7,4) e K7(6,2) (órfãs acima); `patch_opt`/`patch_lns` não rodaram. Busca exata (ILP/SAT) não tentada.
- Limites inferiores só lidos de ledger/cells.json (não alterados). Nada fora de slice-8/ foi escrito.

## Ficou de fora / próximos passos
Todas as células NAO_TENTADA; para as demais, remendo com patch_opt sobre bases boas, e SA com simetria; fechamento exato de K2(12,4) (lb 11, ub 12) exige ILP com quebra de simetria.
