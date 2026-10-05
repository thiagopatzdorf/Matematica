# Linha de base de informação das relações do GNFS

> Campanha de compressão, experimento central. Pergunta: das relações que o crivo produz, quantas existem porque o problema
> contém informação nova e quantas porque o algoritmo ainda não sabe onde essa informação está? Nenhum dinheiro foi gasto; nada
> aqui é afirmação sobre P = NP nem sobre quebrar RSA. Pré-registro: [`predicoes-informacao.md`](predicoes-informacao.md), commitado
> antes de coletar o conjunto `teste`. Ontologia das afirmações: PROVADO, VERIFICADO, EVIDÊNCIA, HIPÓTESE
> (`tools/fatoracao/baseline/claims.jsonl`, C15 a C20).

## Resumo em 8 linhas

1. **R0** (nível de resultado da campanha): nada que melhore "informação útil por segundo de CPU" foi encontrado, e o escalonador de
   crivo ativo (a única coisa que mede essa razão) **não foi testado**. O que existe é um instrumento e medidas.
2. O instrumento reproduz o `purge` do CADO-NFS **exatamente** (linhas e colunas, início e depois dos singletons) nas 21 capturas
   (c30 do repositório mais as 20 analisadas: c60, c70, c80, c90). Isso é pré-requisito: antes só c30 e c60_0 batiam, e o resto tinha erro de 1 a 3 colunas.
3. Previsões registradas antes do `teste`: **P1, P2, P4 e P5 passaram; P3 falhou** (margem de parada acima de 15% em 2 de 11 instâncias).
4. A margem entre as relações coletadas e o mínimo observado **não é constante**: 8% a 19% em c60/c70, 0,1% a 4% em c80, 0,5% a 10% em c90.
   No c60_0 o CADO fechou com `rels_wanted = 46100` (47 087 brutas na pasta, contra 50 961 do lote original), **VERIFICADO**; com 43 000 faltou excesso.
5. A "redundância" por proxy **não cresce** com o tamanho: o expoente de Heaps das ideais novas **sobe** com N (0,43 a 0,51), o excesso final do núcleo real fica
   abaixo do modelo de configuração, a compressibilidade não passa a do modelo de configuração (1,5% pior, não melhor), a ordem das relações não carrega
   informação nesse código (bits iguais com a ordem embaralhada). Isso mata a versão "compressão assintótica por esses proxies".
6. Dois custos crescem com N e são desperdício **medido**, não inferido: relações duplicadas exatas (7% em c60, 17% em c80/c90) e a fração de únicas removidas nos singletons
   (31% em c60, 47% em c90). A segunda **não** é "inútil": ela só existe porque a colisão que a salvaria não veio (ver seção 6).
7. Rejeitar cedo funciona **para filtrar**, não para economizar crivo: um modelo logístico simples, com informação só do passado, tem AUC 0,77 a 0,85 e rejeita 5% a 13% das
   relações perdendo 1% das úteis, com treino em um tamanho e teste em outro. A relação já foi achada quando se decide; economiza filtragem, não busca.
8. Resposta provisória à pergunta final: nos tamanhos medidos (60 a 90 dígitos) o **trabalho extra além do mínimo é pequeno e já conhecido**
   (sobra de parâmetros e duplicatas); o resto parece **necessário por colisão**. Nada indica, ainda, que o algoritmo "não saiba onde a informação está".

## Resultados (gerado de `informacao_resultados.json`)

<!-- gen:resultados -->
| id | conj | brutas | duplicatas | na matriz | cortada pelos cliques | removida nos singletons | emergência | t_min | margem | I(W): excesso / ideais |
|---|---|---|---|---|---|---|---|---|---|---|
| c60_0_t1 | dev | 50961 | 0.074 | 0.464 | 0.220 | 0.316 | 0.675 | 0.903 | 0.097 | M5 / M3 |
| c60_1_t1 | dev | 53409 | 0.080 | 0.447 | 0.266 | 0.287 | 0.653 | 0.878 | 0.122 | M5 / M3 |
| c60_2_t1 | dev | 51369 | 0.083 | 0.488 | 0.201 | 0.311 | 0.677 | 0.913 | 0.087 | M5 / M3 |
| c70_0_t1 | dev | 182904 | 0.107 | 0.312 | 0.331 | 0.356 | 0.684 | 0.845 | 0.155 | M5 / M3 |
| c70_1_t1 | dev | 186383 | 0.116 | 0.306 | 0.343 | 0.352 | 0.679 | 0.837 | 0.163 | M5 / M3 |
| c70_2_t1 | dev | 178678 | 0.127 | 0.383 | 0.229 | 0.388 | 0.727 | 0.905 | 0.095 | M5 / M3 |
| c80_0_t1 | dev | 300752 | 0.174 | 0.595 | 0.007 | 0.398 | 0.796 | 0.999 | 0.001 | M5 / M3 |
| c80_1_t1 | dev | 296381 | 0.163 | 0.574 | 0.028 | 0.398 | 0.793 | 0.995 | 0.005 | M5 / M3 |
| c80_2_t1 | dev | 307488 | 0.177 | 0.560 | 0.058 | 0.381 | 0.780 | 0.986 | 0.014 | M5 / M3 |
| c60_0_t1 | teste | 52864 | 0.069 | 0.419 | 0.289 | 0.292 | 0.658 | 0.868 | 0.132 | M5 / M3 |
| c60_1_t1 | teste | 50169 | 0.070 | 0.488 | 0.188 | 0.324 | 0.692 | 0.922 | 0.078 | M5 / M3 |
| c60_2_t1 | teste | 50565 | 0.071 | 0.473 | 0.206 | 0.321 | 0.680 | 0.912 | 0.088 | M5 / M3 |
| c70_0_t1 | teste | 191545 | 0.114 | 0.281 | 0.388 | 0.331 | 0.658 | 0.808 | 0.192 | M5 / M3 |
| c70_1_t1 | teste | 190895 | 0.126 | 0.299 | 0.355 | 0.347 | 0.670 | 0.829 | 0.171 | M5 / M3 |
| c70_2_t1 | teste | 185565 | 0.130 | 0.346 | 0.293 | 0.362 | 0.696 | 0.866 | 0.134 | M5 / M3 |
| c80_0_t1 | teste | 305969 | 0.185 | 0.590 | 0.019 | 0.391 | 0.788 | 0.997 | 0.003 | M5 / M3 |
| c80_1_t1 | teste | 298248 | 0.156 | 0.538 | 0.074 | 0.389 | 0.786 | 0.982 | 0.018 | M5 / M3 |
| c80_2_t1 | teste | 306371 | 0.162 | 0.495 | 0.135 | 0.370 | 0.767 | 0.960 | 0.040 | M5 / M3 |
| c90_0_t1 | teste | 1104865 | 0.176 | 0.316 | 0.259 | 0.425 | 0.736 | 0.899 | 0.101 | M5 / M3 |
| c90_1_t1 | teste | 984000 | 0.158 | 0.454 | 0.030 | 0.516 | 0.819 | 0.995 | 0.005 | M5 / M3 |

| treino (dígitos) | teste (dígitos) | n | AUC logística | AUC só maior primo | fração rejeitada a 99% de recall | precisão da rejeição |
|---|---|---|---|---|---|---|
| 60 | 60 | 3 | 0.852 | 0.769 | 0.078 | 0.776 |
| 60 | 70 | 3 | 0.836 | 0.775 | 0.132 | 0.856 |
| 60 | 80 | 3 | 0.770 | 0.660 | 0.068 | 0.872 |
| 60 | 90 | 2 | 0.772 | 0.677 | 0.105 | 0.908 |
| 70 | 60 | 3 | 0.849 | 0.769 | 0.068 | 0.736 |
| 70 | 70 | 3 | 0.849 | 0.775 | 0.118 | 0.808 |
| 70 | 80 | 3 | 0.795 | 0.660 | 0.050 | 0.822 |
| 70 | 90 | 2 | 0.800 | 0.677 | 0.093 | 0.886 |
| 80 | 60 | 3 | 0.839 | 0.769 | 0.066 | 0.718 |
| 80 | 70 | 3 | 0.837 | 0.775 | 0.116 | 0.790 |
| 80 | 80 | 3 | 0.813 | 0.660 | 0.052 | 0.829 |
| 80 | 90 | 2 | 0.818 | 0.677 | 0.099 | 0.888 |

| dígitos | n | bits/relação real | configuração | ordem embaralhada | gzip real | emergência real | emergência configuração | excesso final real | configuração | β de Heaps | ideais novos por relação no fim |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 60 | 3 | 187.1 | 184.2 | 187.2 | 0.430 | 0.676 | 0.717 | 3092 | 3885 | 0.435 | 0.258 |
| 70 | 3 | 206.7 | 203.5 | 206.7 | 0.444 | 0.675 | 0.725 | 15176 | 18668 | 0.463 | 0.297 |
| 80 | 3 | 225.6 | 222.3 | 225.7 | 0.450 | 0.780 | 0.850 | 2970 | 7394 | 0.464 | 0.277 |
| 90 | 2 | 241.6 | 238.8 | 241.6 | 0.465 | 0.777 | 0.775 | 22268 | 43684 | 0.508 | 0.338 |

| métrica | inclinação por dígito | IC 95% | n |
|---|---|---|---|
| beta_de_heaps | +0.0021 | [+0.0014, +0.0028] | 11 |
| emergencia_fracao | +0.0042 | [+0.0019, +0.0065] | 11 |
| excesso_final_sobre_linhas | -0.0028 | [-0.0058, +0.0002] | 11 |
| excesso_real_menos_configuracao | -0.0006 | [-0.0011, -0.0001] | 11 |
| fracao_cortada_pelos_cliques | -0.0055 | [-0.0130, +0.0020] | 11 |
| fracao_duplicatas | +0.0035 | [+0.0024, +0.0047] | 11 |
| fracao_na_matriz | +0.0006 | [-0.0063, +0.0075] | 11 |
| fracao_removida_nos_singletons | +0.0049 | [+0.0030, +0.0068] | 11 |
| margem_de_parada | -0.0030 | [-0.0068, +0.0008] | 11 |
| t_min_fracao | +0.0030 | [-0.0008, +0.0068] | 11 |
| w_sq_por_coluna_final | -0.0004 | [-0.0017, +0.0009] | 11 |

Veredictos (conjunto `teste`, 11 instâncias):

- **P1: passou** — {"fora_de_0.5_0.85": []}
- **P2: passou** — {"frac_M5_no_excesso": 1.0, "ideais_vistos_M2_ou_M3_em_todas": true}
- **P3: FALHOU** — {"margem_acima_de_15pct": ["c70_0_t1", "c70_1_t1"], "inclinacao_da_margem": {"ic95": [-0.006795273434935932, 0.0008393525239665037], "inclinacao_por_digito": -0.002977960455484714, "n": 11}}
- **P4: passou** — {"pares_reprovados": [], "n_pares": 6}
- **P5: passou** — {"excesso_real_nao_menor_que_o_nulo": [], "maior_diferenca_de_compressibilidade": 0.016932934142128486}
<!-- /gen -->

Leitura das tabelas: `emergência` é a fração das relações brutas em que o núcleo do purge deixa de ser vazio; `t_min` é a menor fração com excesso
do núcleo de pelo menos 160 (o `keep` do CADO); `margem = 1 - t_min`. `na matriz` é a fração das relações únicas (sem as livres) que chegam
à matriz final. Os índices do ajuste `I(W)` são M5 (limiar) para o excesso e M3 (log) para ideais vistos, escolhidos por BIC entre M1 linear, M2 potência, M3 log, M4 saturação e M5 limiar, **declarados antes**.

## 1. Formato dos dados

Uma captura por execução do CADO-NFS (`tools/fatoracao/captura_relacoes.py`, formato `relacoes-cado/v1`), em arquivos compactos e reproduzíveis
(gzip sem data, `sha256` por arquivo no `manifest.json`; nada depende do relógio):

| arquivo | conteúdo |
|---|---|
| `relacoes.tsv.gz` | TODAS as relações brutas que o filtro consumiu, na ordem canônica (bloco do `filelist`, depois a ordem do arquivo), com `q`, `rho`, `a`, `b` e os primos de cada lado (hex). Soma de **todas as rodadas** de filtragem |
| `arquivos.json` | por bloco: relações, special-q processados e CPU (`W`, a unidade de trabalho independente de hardware) |
| `livres.tsv.gz`, `poly.txt`, `purgadas.tsv.gz`, `index.gz`, `purge.json` | o que o filtro fez com elas; `purge.json` traz todas as rodadas (`rodadas`) e a última em `inicio`/`apos_singletons`/`final` |
| `badideais.txt`, `inercias.txt` | ideais ruins (`numbertheory_tool`) e inércia excepcional (`tools/fatoracao/cado/inercia.cpp`), necessários para a coluna certa |
| `manifest.json` | contagens por estágio, parâmetros, sementes, commit do CADO, `sha256` de cada arquivo |

Conjuntos: `dev` (c60, c70, c80, três cada) e `teste` selado (c60, c70, c80 três cada; c90 duas), semente por prefixo (`medir_cado.py gerar ... --prefixo dev|teste`).
O RSA-896 **não** entra como dado cego. Conjunto pequeno reproduzível no repositório: `tests/fixtures/fatoracao/captura_c30` e `captura_c60_0`
(esta com ideais ruins e inércia, 2,5 MB). Os `sha256` das 20 capturas analisadas estão em `informacao_resultados.json` (`sha256_manifesto`).

## 2. Relação → purge → matriz

`relacoes.py` reconstrói a matriz como o CADO: coluna = **ideal** `(lado, p, raiz)` com `raiz = a·b⁻¹ mod p` (`p` para o ponto no infinito); ideal ruim vira
`nbad` colunas, escolhidas pelo ramo de `(a, b)` módulo `p^k`; o expoente é dividido pela inércia e só o ímpar fica (`dup2`: `e &= 1`); relação livre lista todas as colunas
de `p` (e o infinito se `p | lc(f)`). O descasque de singletons e a lista de linhas até a matriz saem daí. **VERIFICADO** (C15): o início e o fim do descasque batem com o `purge`
do CADO, em linhas e colunas, nas 21 capturas, incluindo as que precisaram de 2 a 4 rodadas (c80, c90).

Três erros que custaram um ciclo cada, todos agora com teste: (a) só c30 e c60_0 batiam porque faltavam ideais ruins e inércia; (b) a captura lia só a primeira rodada de filtragem
(o c80 filtra 3 ou 4 vezes, com excesso -19 557, -7 564, +160 no c80_0 do lote legado) e invalidou as primeiras capturas c80, refeitas; (c) o `inercia` chamava uma rotina cara para todo resíduo
até `p` (p até 1e7) e travou uma coleta.

## 3. Curva de rank marginal

A forma que cabe medir a esse custo é o **núcleo do purge** (linhas e colunas depois dos singletons, 40 pontos por instância): para cada prefixo de relações, o excesso
(linhas do núcleo menos colunas) é um limite inferior do espaço nulo. Ele é **vazio até cerca de dois terços das relações** (emergência 0,65 a 0,82) e cresce depois como uma **rampa**:
o modelo de limiar (M5) vence por BIC em 11 de 11 instâncias teste. Ou seja, a informação marginal medida por esse proxy é **zero até um limiar** e depois linear: não satura cedo (hipótese "o rank satura muito antes" não se sustenta).
O rank exato em GF(2) do c60 **não foi calculado** (ficou como pendência), então "relações por novo grau de liberdade" não tem número aqui.

## 4. Novidade estrutural

Ideais vistos nas relações do crivo crescem como `W^β` (lei de Heaps) com `β` entre 0,43 (c60) e 0,51 (c90), e o modelo logarítmico (M3) é o melhor por BIC para `ideais_vistos` em 11 de 11. No fim da coleta
ainda aparece cerca de 0,26 a 0,34 ideal novo por relação. **O expoente cresce com N** (inclinação +0,0021 por dígito, IC95 [+0,0014, +0,0028]): quanto maior o número, **menos** a novidade
estrutural satura. O hipergrafo (vértices = ideais grandes, hiperarestas = relações) tem componente gigante no fim (50% a 78% dos ideais grandes vistos) Isso é o contrário do que
a hipótese de compressão assintótica precisaria para esse proxy.

## 5. Compressibilidade (evidência auxiliar, não prova)

Código adaptativo por relação, mais gzip, bzip2 e lzma, no real, no modelo de configuração (mesmos graus, embaralhando os ideais) e na ordem embaralhada. Resultado: **o real é cerca de 1,5% menos compressível que o
modelo de configuração** e **idêntico à ordem embaralhada**. Compressibilidade de representação mostra regularidade de grau, não estrutura nova, e não prova compressibilidade algorítmica do GNFS.

## 6. O que morre no purge, e por quê isso não é "redundante"

Destino de cada relação única: **na matriz** (28% a 59%), **cortada pelos cliques** (1% a 39%, depende de quanto o CADO passou do mínimo), **removida nos singletons** (29% a 52%), mais as duplicatas exatas
(7% a 19% das brutas). Termos precisos: "removida no estágio X" **não** significa "inútil". Uma relação singleton é removida porque nenhuma outra relação colidiu com um dos seus ideais; se a colisão viesse
(mais relações), ela seria necessária. Por isso não escrevemos "x% eram redundantes". Fração duplicada exata é desperdício medido: a mesma `(a, b)` achada por special-q diferentes.

**Previsibilidade com informação só do passado** (modelo logístico com ridge, características online, treino em um tamanho `dev`, teste em outro tamanho `teste`): AUC 0,77 a 0,85
(a regra "maior primo do lado 1" sozinha dá 0,66 a 0,78), e a 99% de recall das úteis rejeita 5% a 13% das relações com precisão de 72% a 91%. Cai pouco entre tamanhos
(0,85 no mesmo tamanho; 0,77 do c60 para o c90), o que indica regularidade e não memorização, mas a regularidade é conhecida: ideal grande colide menos. **Projeção de aceleração: nenhuma comprovada.**
A relação já foi achada quando a característica existe; evitar o crivo exigiria prever **antes** de crivar (isso é o crivo ativo, seção 12).

## 7. Curva de informação I(W)

Modelos fixados antes: M1 `I = aW`, M2 `I = aW^α`, M3 `I = a log W`, M4 saturação, M5 limiar. Vencedores por BIC no `teste`: excesso do núcleo → M5 em 11 de 11; ideais vistos → M3 em 11 de 11.
Em outras palavras: o que o filtro precisa (excesso) é limiar + rampa, e a novidade estrutural é logarítmica. O **trabalho por coluna final** (`W` em special-q por coluna) não tem inclinação significativa com N
(IC contém 0).

## 8. Escala: c60, c70, c80, c90 (E6)

Inclinações por dígito (tabela acima, `teste`, n = 11): duplicatas **sobem** (+0,0035, IC [+0,0024, +0,0047]); removida nos singletons **sobe** (+0,0049, IC [+0,0030, +0,0068]); `na matriz`,
`cortada pelos cliques`, `t_min`, margem de parada e excesso final sobre linhas **não têm inclinação distinguível de 0**. O `c100` não foi coletado (não era barato: o c90 já leva ~10 min por tentativa e falhou 3 vezes com `nlucky=0`
no c90_0; as relações e o purge dele existem e valem, a álgebra linear é outro fato).

## 9. Transferência entre tamanhos

Ver a segunda tabela. Treino em c60, c70 ou c80 e teste em c60 a c90: AUC 0,77 a 0,85. O par c80 → c90 (AUC 0,82) e c60 → c90 (0,77) mostram que a regularidade transfere. Como acima, é a regularidade conhecida do tamanho do maior primo.

## 10. Controles aleatórios

Modelo de configuração (mesma distribuição de graus por lado, ideais embaralhados) e ordem embaralhada (mesma matriz). Resultado: o **excesso final real é menor que o do modelo de configuração em 11 de 11** (3 092 contra 3 885 no c60; 22 268 contra 43 684 no c90);
o núcleo do real emerge **antes** do que o do modelo de configuração em 3 de 4 tamanhos (c60, c70, c80); no c90 há empate (0,777 contra 0,775); a ordem embaralhada não muda o excesso final nem os bits. Logo a matriz observada **não é só** a distribuição de graus.
Interpretação (HIPÓTESE, não testada): ideais pequenos muito reutilizados, que é estrutura do GNFS e não de uma matriz esparsa qualquer.

## 11. Ponto de parada

Simulação (prefixo de relações brutas, `t_min` por tamanho, margens na tabela). **VERIFICADO** em uma instância (C16): no c60_0, com o mesmo polinômio e `tasks.sieve.rels_wanted = 46 100` (previsto `t_min` = 46 015), o CADO fechou na primeira rodada com excesso 160
e imprimiu os fatores gerados; com 43 000 e com 40 769 o excesso da primeira rodada foi -1 176 e o CADO pediu mais 10 000. Arquivo: `tools/fatoracao/baseline/parada_c60_0.json`. **Não é lei geral**: é uma instância, a margem varia de 0,1% a 19%, e nos tamanhos
maiores o laço de rodadas do CADO já pára perto do mínimo.

## 12. O que não foi feito

- **Crivo ativo** (escalonador que escolhe special-q/região por informação marginal esperada): não implementado, por ordem do plano só depois destas medidas. É a única peça que mede `Q_I = informação útil nova / s de CPU` contra o crivo comum.
- **E1** (seleção de polinômio) e os US$ 300: não executados.
- **c100**, rank exato em GF(2), 3-core e fases de transição além do componente gigante: pendentes.
- Só 11 instâncias `teste` (2 em c90); um semiprimo por semente; hardware único. O intervalo de inclinação é t de Student com ruído suposto normal.
- Dois ajustes de infraestrutura apareceram **depois** de congelar o pipeline (retomada por instância e captura de todas as rodadas) e não mudam nenhuma métrica; estão nos commits.

## Hipóteses que morreram, e as que não

| hipótese | resultado |
|---|---|
| "o rank satura cedo" | **morreu**: limiar + rampa (M5), sem saturação |
| "a novidade estrutural satura mais rápido em números maiores" | **morreu**: β de Heaps sobe com N |
| "a redundância de representação cresce com N" | **morreu**: o real não é mais compressível que o nulo de configuração, e a ordem não importa |
| "dá para parar em 80% das relações e fechar a mesma matriz" | **morreu** como regra geral: precisa de 81% a 99,9% (`t_min`) |
| "a regularidade é só memorização local" | **morreu** (transfere entre tamanhos), mas ela é de segunda ordem: tamanho do maior primo |
| "rejeição cedo economiza crivo" | **não testada** (só filtragem); depende do crivo ativo |
| "o trabalho cresce muito mais rápido que a informação marginal" | **sem evidência** nos tamanhos medidos (R0) |

## Reproduzir

    python3 tools/fatoracao/medir_cado.py gerar 60,70,80,90 3 conj.json --prefixo teste
    CADO_INERCIA=<bin> CADO_NUMBERTHEORY_TOOL=<numbertheory_tool> python3 tools/fatoracao/medir_cado.py medir conj.json res.jsonl \
        --cado <árvore do cado-nfs> --trabalho <pasta> --guardar-relacoes <pasta de capturas>
    python3 tools/fatoracao/baseline_informacao.py analisar saida.json --cache <pasta> --dev <capturas dev> --teste <capturas teste>
    python3 tools/fatoracao/baseline_informacao.py relatorio saida.json
    python3 -m pytest -q tests/test_relation_information_baseline.py
