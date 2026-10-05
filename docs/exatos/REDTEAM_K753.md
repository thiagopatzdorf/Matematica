# Red team: K_7(5,3) ≥ 17, ou seja, ∄ código com 16 palavras (2026-10-05)

Revisão adversarial da rodada M = 16 de K_7(5,3) feita com o codificador de fibras
(`tools/exatos/fibras/`, branch `feat/exatos-fibras`). O objetivo era **quebrar** a prova, não
confirmá-la. Scripts desta revisão: `tools/exatos/fibras_redteam/k753_*.py`. Resultados brutos:
`tools/exatos/fibras_redteam/resultados/k753_*.json[l]`.

**Veredito: não achei erro.** A lista de perfis está completa. Os três perfis caros têm todos os
cubos fechados, e os cubos cobrem o espaço inteiro de cada um. Em 51 registros, a CNF e a prova
LRAT regeneradas aqui saíram iguais às gravadas, bit a bit, e passaram em dois verificadores.
Uma codificação independente também deu UNSAT em 8 de 8 perfis. Junto com a cota superior 17
da literatura (Rivas Soriano), isso sustenta **K_7(5,3) = 17**.
Confiança: alta. Duas ressalvas, na seção 5: as 9 provas grandes que não reconferi e a
dependência de K_6(4,2) = 15, que vem da literatura.

Na data desta revisão, `docs/exatos/FIBRAS_GERAL.md` (branch `feat/exatos-fibras`) ainda dizia
"em andamento: falta 1 perfil (3322222^5), em 4953 cubos". Esse perfil fechou durante a revisão
(seção 2). Atualizar aquela tabela é decisão do dono.

## 1. A lista de perfis de M = 16 está completa

`k753_perfis.py` refaz a enumeração sem importar nada de `tools/exatos/fibras`: monta os tipos
por força bruta e forma os perfis como multiconjuntos de 5 tipos. Depois compara essa lista,
conjunto a conjunto, com os registros do autor. Também confere cada registro:
(q, n, M, k, s_min), UNSAT com `lrat_check` VERIFIED, nenhum controle ligado, tipos válidos,
ordem dos tipos coerente com a `ordem` gravada (min ou max) e `inst` igual à posição do perfil
nessa ordem. A string do tipo não tem separador ("10111111" = 10,1,1,1,1,1,1), então só é aceita
quando admite uma única decomposição.

| medida | valor |
|---|---|
| tipos (partições de 16 em 7 partes ≥ 1) | 28 |
| perfis esperados = C(28+4, 5) | 201 376 |
| registros inteiros, perfis distintos | 201 374 / 201 374 (0 duplicados) |
| perfis fechados só por cubos | 2: 3322222^5 (inst 58870) e 3322222^4·4222222 (inst 7714) |
| faltam / sobram | 0 / 0 |
| registros por ordem | max 180 864, min 22 404 |
| sha256 da CNF regenerada, amostra de 2000 registros | 2000 iguais, 0 divergentes |

Resultado: `resultados/k753_perfis.json`. Testes: `test_lista_de_perfis_de_k7_5_3_com_16_nao_perde_nem_inventa_perfil`
e `test_tipo_gravado_sem_separador_com_parte_de_dois_digitos_e_lido_sem_ambiguidade`.

## 2. Cubos dos perfis 55, 7714 e 58870

Um perfil fechado por cubos só está provado se valem duas coisas: (i) todo código do perfil cai
em algum cubo e (ii) todo cubo é UNSAT. `k753_cubos.py` ataca as duas.

**(i) Cobertura, por SAT, sem confiar em enumerador nenhum.** Da CNF auditada do perfil, pego só
as cláusulas que não tocam variáveis das coordenadas ≥ 2 nem as vizinhas delas. Um subconjunto
de cláusulas é uma relaxação: todo modelo da CNF inteira também satisfaz esse subconjunto. A ele
somo uma cláusula de bloqueio por cubo. Se o resultado for UNSAT, todo modelo da CNF inteira cai
em algum cubo. Deu UNSAT nos três perfis, com a prova conferida por `lrat-check` e `cake_lpr`. Como controle, retiro a negação de um cubo:
a CNF fica SAT e o modelo cai dentro do cubo liberado. Isso mostra que a CNF não é UNSAT por
acidente.

| inst | perfil | cubos | UNSAT (prova verificada) | controle |
|---|---|---|---|---|
| 55 | 4222222³·3322222² | 765 | `lrat-check` VERIFIED, `cake_lpr` VERIFIED | SAT no cubo 92 |
| 7714 | 4222222·3322222⁴ | 1812 | `lrat-check` VERIFIED, `cake_lpr` VERIFIED | SAT no cubo 1405 |
| 58870 | 3322222⁵ | 4953 | `lrat-check` VERIFIED, `cake_lpr` VERIFIED | SAT no cubo 3984 |

Resultado: `resultados/k753_cobertura_cubos.jsonl`, com o sha256 de cada CNF.

**(ii) Todo cubo fechado.** Para cada índice 0..N−1, exigi registro UNSAT com `lrat_check`
VERIFIED e o cubo gravado igual ao da enumeração. Também regenerei a CNF do cubo e comparei o
sha256 com o gravado.

| inst | índices fechados | sha256 da CNF | observação |
|---|---|---|---|
| 7714 | 1812 / 1812 | 1812 iguais | — |
| 55 | (perfil inteiro) | — | fechado como registro inteiro (UNSAT, 5200 s). Os 55 cubos gravados são extras e também batem |
| 58870 | **4953 / 4953** | 4953 iguais | fechou às 08:10Z de 2026-10-05; às 05:54Z eram 3649 |

Os registros de 58870 estavam espalhados em 8 arquivos JSONL: as rodadas a–g e a de teste, com
4968 linhas no total. Esse conjunto fica identificado pelo sha256 da saída de `sha256sum *.jsonl`
com os arquivos ordenados por nome:
`65f5ca1f235a5c7f60e9d1959af2a42cc3a42b22929b3adad116c09c7e42ed28`.
Resultado: `resultados/k753_cubos_conferidos.jsonl`.

Erro meu, registrado: na primeira comparação dos 1812 cubos de 7714, todos os sha256 divergiram.
A causa estava no meu script, que gravava o rótulo do cubo como lista, enquanto o `rodar.py`
grava como tupla. Depois da correção, 1812 de 1812 bateram. Não era defeito dos registros.

## 3. Amostra de LRAT regenerado

A amostra é estratificada, com semente fixa (`k753_amostra.py`): um perfil por tipo da
coordenada 0 em cada ordem, os de maior tempo de solver, os de maior prova, 12 aleatórios e 6
cubos de cada perfil fechado por cubos, num total de 60 registros. Para cada um, `k753_lrat.py`
regenera a CNF com o codificador auditado e compara o sha256. Depois roda `cadical --lrat`,
compara o sha256 da prova e confere a prova com `lrat-check` e `cake_lpr`.

| resultado | registros |
|---|---|
| sha256 da CNF igual, sha256 da prova igual bit a bit, `lrat-check` VERIFIED, `cake_lpr` VERIFIED | **51** |
| pulados (prova > 600 MB; ver seção 5) | 9 |
| qualquer divergência | 0 |

Os 51 cobrem os 28 tipos da coordenada 0 na ordem max, 2 tipos na ordem min, 12 perfis
aleatórios e 9 cubos (6 de 7714 e 3 de 58870). Resultado: `resultados/k753_lrat_amostra.jsonl`.

Na primeira passada, o perfil 198542 deu NOT VERIFIED porque o disco encheu e a prova saiu
truncada (o sha256 da prova também divergiu). Refiz com espaço livre e passou. Não era defeito
do registro.

## 4. Codificação independente (amostra pequena)

`indep_perfil.py` não compartilha código com o codificador do repo. Usa one-hot em todas as
coordenadas, o totalizador do pysat, cobertura só no sentido necessário e apenas a quebra de
simetria trivial. Rodei o kissat (teto de 600 s) nos 8 primeiros perfis da amostra que não são
cubos e que o repo resolveu em menos de 100 s (`k753_indep.py`):

| resultado | perfis |
|---|---|
| UNSAT | 8 / 8 (1,4 s a 7,7 s cada) |
| SAT ou indefinido | 0 |

Resultado: `resultados/k753_indep.jsonl`. A amostra é pequena de propósito: o container é
compartilhado. A mesma codificação reproduz K_4(4,2) = 7 em
`test_codificacao_independente_reproduz_k4_4_2_igual_a_7`. Os mutantes da quebra de simetria
de K_7(5,3) (`resultados/mutantes_k753.jsonl`) foram rodados antes, no commit da80f2c: todo
mutante que mexe em (f) ou em (h) nos dois sentidos é pego.

## 5. Lacunas explícitas

1. **9 provas grandes não reconferidas aqui.** O registro do autor diz `lrat_check` VERIFIED
   para todas. Não as regenerei porque a prova passa de 600 MB e o disco local tinha 4 GB
   livres:

   | inst | cubo | estrato | prova |
   |---|---|---|---|
   | 784 | — | maior tempo de solver | 27,8 GB |
   | 55 | — | maior tempo de solver | 20,7 GB |
   | 2 | — | maior tempo de solver | 11,7 GB |
   | 35119 | — | maior tempo de solver | 1,45 GB |
   | 7716 | — | maior tempo de solver | 1,23 GB |
   | 0 | — | maior prova | 3,16 GB |
   | 58872 | — | maior prova | 2,67 GB |
   | 58870 | 3500 | cubo de 58870 | 878 MB |
   | 58870 | 4952 | cubo de 58870 | 726 MB |

   Para fechar: `k753_lrat.py` com a amostra filtrada nesses 9, numa máquina com disco.
2. **Literatura.** O Lema 1 (fibras) em K_7(5,3) usa K_6(4,2) = 15 (Kéri 2011). A cota superior
   K_7(5,3) ≤ 17 é de Rivas Soriano. Nenhuma das duas foi refeita aqui.
3. A codificação independente cobriu só 8 perfis baratos. Nenhum perfil caro e nenhum cubo foi
   reproduzido por ela.

## Como reproduzir

    # binários: CADICAL, LRAT_CHECK, CAKE_LPR, KISSAT no ambiente; DIR_FIBRAS = tools/exatos/fibras
    python3 tools/exatos/fibras_redteam/k753_perfis.py 7 5 16 1 K7_5_3_M16.jsonl CUBOS.jsonl
    python3 tools/exatos/fibras_redteam/k753_cubos.py $DIR_FIBRAS cobertura 7 5 16 1 max 58870 $TMP
    SEM_REPO=1 python3 tools/exatos/fibras_redteam/k753_cubos.py $DIR_FIBRAS conferir 7 5 16 1 max 58870 CUBOS_58870/*.jsonl
    python3 tools/exatos/fibras_redteam/k753_lrat.py $DIR_FIBRAS resultados/k753_amostra.jsonl $TMP --max-bytes 600000000
    python3 tools/exatos/fibras_redteam/k753_indep.py resultados/k753_amostra.jsonl $TMP 600 8
