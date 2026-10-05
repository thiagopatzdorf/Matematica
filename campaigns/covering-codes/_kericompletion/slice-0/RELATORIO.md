# Slice 0: Kéri K_q(n,R), relatório

Resultado: **nenhum código menor que a cota da tabela consultada foi encontrado nesta busca**; 0 células fechadas. Todas as 16 células tentadas ficam `SEM_MELHORA_NESTA_BUSCA`. Isto não prova que não exista código menor.

Método: SA genérico próprio (`work/sa.c`; M fixo = ub-1, minimiza pontos descobertos, 1 núcleo, `nice`, semente 1, T 0.5→0.12, 60 a 120 s CPU por célula). O kit base+remendo (`base_search`/`patch_opt`) não foi usado: não houve tempo. Extra: ILP exato (HiGHS, `work/ilp.py`) em K3(7,3) com M<=11: 240 s, sem solução e sem cota dual (nada provado). Sanidade: o SA nem reproduz as cotas das tabelas em células pequenas (K5(4,1) com M=51 ficou com 3 pontos descobertos), então o fracasso em ub-1 é fraco como evidência. Os verificadores (C oficial e verify.py) não rodaram: não houve código a verificar.

| célula | lb | ub tabela (fonte) | M tentado | melhor nº de pontos descobertos |
|---|---|---|---|---|
| K5(4,1) | 46 | 51 (keri_2011) | 50 | 6 |
| K3(7,3) | 11 | 12 (keri_2011) | 11 | 33 |
| K3(8,2) | 58 | 81 (keri_2011) | 80 | 315 |
| K2(14,3) | 44 | 64 (keri_2011) | 63 | 633 |
| K2(15,3) | 70 | 112 (keri_2011) | 111 | 1054 |
| K2(16,4) | 34 | 64 (keri_2011) | 63 | 759 |
| K7(6,4) | 13 | 15 (keri_2011) | 14 | 171 |
| K3(11,1) | 7832 | 9477 (keri_2011) | 9476 | 15327 |
| K5(8,2) | 861 | 1625 (keri_2011) | 1624 | 19496 |
| K3(12,4) | 65 | 175 (keri_2011) | 174 | 3089 |
| K2(20,6) | 24 | 64 (keri_2011) | 63 | 1819 |
| K3(13,6) | 14 | 36 (keri_2011) | 35 | 2814 |
| K2(21,3) | 1475 | 3072 (keri_2011) | 3071 | 74538 |
| K2(22,3) | 2544 | 4096 (keri_2011) | 4095 | 401928 |
| K3(14,1) | 166610 | 177147 (keri_2011) | 177146 | 850387 |
| K2(23,1) | 352827 | 393216 (keri_2011) | 393215 | 1302936 |
