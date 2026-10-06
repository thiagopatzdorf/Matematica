# Fatia mínima com canonização por nauty (2026-10-05)

Pergunta (de `LP_FATIA_TERNARIO.md`, PR #68): em `K_3(6,1)` (71–73) e `K_3(7,2)` (27–34) o LP da
fatia mínima mata tudo o que se amostra, mas a lista de instâncias não sai, porque `aumento.py`
só canoniza até `m ≤ 4` (o grupo `S_3 ≀ S_m` vira tabela em memória). Dá para montar a lista com
nauty, e quanto ela custa? Estados como no `AGENTS.md`: OBSERVED (medido, sem prova),
COMPUTATIONALLY_VERIFIED (conferido por programa independente), PROVED (prova escrita).

## Resumo

| célula | M | s* | órbitas que passam no filtro | custo medido da lista | estado |
|---|---|---|---|---|---|
| K_3(6,1) | 72 | 18 | **30** | 32 s, 6,1 × 10^6 chamadas ao nauty | OBSERVED (método conferido em casos pequenos, seção 2) |
| K_3(6,1) | 71 | 18 | **18** | 30 s | OBSERVED |
| K_3(6,1) | 72 | 19 | **411 930** | 1 830 s de parede em 4 núcleos, 1,05 × 10^9 chamadas | OBSERVED |
| K_3(6,1) | 72 | 20 | **≥ 182 856 864** (piso: 175 de 4 096 partes contadas por inteiro em 1 h) | ≥ 10 774 s de CPU só nessas 175 partes | OBSERVED |
| K_3(7,2) | 27 | 7 | **0** | 0,07 s | OBSERVED |
| K_3(7,2) | 27 | 8 | **14 314 204** | 53 s de parede em 3 núcleos, 1,9 × 10^7 chamadas | OBSERVED |
| K_3(7,2) | 27 | 9 | **≈ 8,2 × 10^10 ± 0,6 × 10^10** (estimado por 8 partes sorteadas de 4 096) | ≈ 180 CPU-h só para enumerar | OBSERVED |

**Veredito: nenhuma das duas células cabe em US$ 10, então parei no número medido.** Nenhuma
cota muda, não usei VM e não rodei o LP na lista inteira de nenhuma célula (só na parte
`s* = 18` de K_3(6,1), seção 3).

* `K_3(7,2)`, M = 27: só o `s* = 8` já são 28,6 milhões de instâncias (14 314 204 órbitas × 2
  blocos, (11,8) e (10,9)). O LP leva 1,4 s por instância (20 de 20 certificadas na raiz numa
  amostra, medido no container com carga), ou seja ≈ 11 100 CPU-h. Mesmo a US$ 0,005 por vCPU-h
  (abaixo do preço spot, de propósito, para a conta errar a favor de caber) isso dá ≥ US$ 55. E o
  `s* = 9` tem ~10^11 órbitas: não cabe nem guardar a lista.
* `K_3(6,1)`, M = 72: o `s* = 19` sozinho são 3,3 milhões de instâncias (411 930 × 8 blocos). A
  ~0,3 s por LP (medido no PR #68) isso daria ~275 CPU-h, que talvez coubesse. Mas a lista
  precisa de todo `s*` de 18 a 24, e o `s* = 20` já tem **pelo menos 182 856 864 órbitas**
  (contadas, não estimadas), isto é ≥ 1,28 × 10^9 instâncias (7 blocos) e ≥ 10^5 CPU-h de LP,
  ≥ US$ 530 pela mesma conta. Não cabe.
* **E o LP não mata nem todo o `s* = 18`** (seção 3): numa das 30 configurações de M = 72 (e
  numa das 18 de M = 71), justamente a mais estruturada, os blocos equilibrados não têm
  certificado nem com ramificação até profundidade 12. A lista completa, mesmo que coubesse, não
  fecharia a célula só com o LP da raiz.

## 1. A canonização (o que foi feito)

`tools/exatos/gaps2/nauty_fatia.c` (núcleo em C, `libnauty`) e `nauty_fatia.py` (interface,
compila o C uma vez por versão da fonte). Prova completa no docstring de `nauty_fatia.py`; em
resumo:

**Grafo colorido.** Para um conjunto `X` de pontos de `Z_q^m`: `m` vértices de coordenada (cor
0), `q·m` vértices de símbolo `(i,a)` (cor 1), um vértice por ponto (cor 2); arestas `i — (i,a)` e
`x — (i, x_i)`. Um isomorfismo que preserva as cores leva coordenadas em coordenadas (`σ`) e os
símbolos de `i` nos de `σ(i)` (`π_i`), logo é um elemento `g` de `S_q ≀ S_m`; e o ponto `x`, que
só é vizinho de `(i, x_i)`, vai para o ponto vizinho de `(σ(i), π_i(x_i))`, isto é, para `g(x)`.
A volta é imediata. Então `Γ(X) ≅ Γ(Y)` (com cores) **⇔** `Y = g(X)` para algum `g`, e o rótulo
canônico do nauty dá forma canônica igual **⇔** mesma órbita (PROVED, docstring).

**Aumento canônico de McKay** (não guarda níveis, não precisa do grupo). Deleção canônica: entre
os pontos de maior sobreposição marginal `mo_Y(y) = |B(y) ∩ cob(Y − y)|`, o de maior rótulo
canônico. Filho `X+p` aceito se `p` está na órbita de `Aut(X+p)` da deleção canônica, sem repetir
classe entre filhos do mesmo pai. O filtro de contagem da fatia `|U| ≤ cap` equivale a
`ov(X) = |X|·V − |cob(X)| ≤ orc`, e `ov` só cresce com `X`, então todo subconjunto de um
conjunto válido é válido e o aumento é completo e sem repetição (indução no docstring, PROVED).

**Poda que decidiu a viabilidade.** Escolher a deleção pela maior sobreposição marginal faz `mo`
do ponto acrescentado nunca diminuir ao longo de um caminho. Daí
`ov(X_s) ≥ ov(X_k) + soma dos s−k menores max(mo_k, δ(p))`, com `δ(p) = |B(p) ∩ cob(X_k)|`, e o
nó que viola isso morre. Medido em K_3(6,1), M = 72, `s* = 18` (estimador de Knuth, 2 000–5 000
sondas; só ordem de grandeza, ver a seção 3 sobre estimadores): deleção pelo maior rótulo puro,
~2,2 × 10^11 chamadas ao nauty previstas; com a poda por `δ` só, 1,6 × 10^11; com a deleção por
`mo` + poda, **6,1 × 10^6 medidas** (contagem exata em 32 s). O filtro em si não muda: a poda só tira nós sem descendente válido.

## 2. Conferências (tests/test_fatia_nauty.py)

| conferência | resultado | estado |
|---|---|---|
| órbitas de `s`-subconjuntos sem filtro contra Burnside (`k362/redteam/burnside.py`) em `Z_3^4` (s = 1..5), `Z_3^5` (0..5), `Z_3^6` (1..4), `Z_2^5` (1..7), `Z_4^3` (1..5) | todas iguais (ex.: 1, 1, 5, 35, 490, 11 075 em `Z_3^5`) | COMPUTATIONALLY_VERIFIED |
| com filtro, mesmas órbitas que `aumento.py` em `Z_3^4` | iguais em (s, cap) = (4,50), (5,40), (6,30), (7,20) no teste; (8,15) e (9,10) também, fora do teste por tempo do `aumento.py` | COMPUTATIONALLY_VERIFIED |
| com filtro, mesmas órbitas que `fatia.configuracoes` em `Z_3^5` | iguais em (s, R, cap) = (3,1,150), (4,1,199), (4,2,40); (5,2,20) e (5,1,190) também, fora do teste por tempo | COMPUTATIONALLY_VERIFIED |
| lista de instâncias igual à de `fatia.instancias` | K_3(5,2) M = 7, 8; K_3(4,1) M = 8, 9 | COMPUTATIONALLY_VERIFIED |
| K_3(5,1) M = 26 | 343 instâncias (s* = 7: 3), como o `aumento.py` (que levou ~12 min; aqui segundos) | COMPUTATIONALLY_VERIFIED |
| forma canônica invariante por isometria aleatória, e distinta entre órbitas | 20 de 20; 20 formas para as 20 órbitas de 3 pontos de `Z_3^4` | COMPUTATIONALLY_VERIFIED |
| contagem em partes paralelas = sequencial | 11 075 nos dois | COMPUTATIONALLY_VERIFIED |

## 3. As medições

**K_3(6,1).** `V(5,1) = 11`, `cap = M − s*`, `orc = 11 s* − 243 + (M − s*)`: 9, 19, 29, …, 69
para `s* = 18..24` em M = 72 (8, 18, …, 58 para `s* = 18..23` em M = 71). Nós por nível em
`s* = 19`, M = 72 (exato):
`1, 1, 3, 14, 84, 742, 6 054, 33 324, 109 907, 203 737, 198 165, 3 503 563, 20 099 086,
47 251 538, 48 392 455, 21 915 741, 3 800 533, 584 772, 131 063, 411 930`. M = 71 com
`s* = 19` não foi contado (as órbitas de M = 71 são um subconjunto das de M = 72, porque o
orçamento é menor; o custo é o mesmo da ordem).

`s* = 20`, M = 72 (`orc` = 29): `--parcial 4096 7 3600 -j 4` contou 175 das 4 096 partes
(sorteadas em ordem fixa) em 1 h de parede: **182 856 864 órbitas** nessas partes, 10 774 s de CPU.
É um piso, não estimativa. Multiplicar pela fração de partes daria ~4 × 10^9, mas a cauda pesada
(abaixo) proíbe confiar nesse fator.

**O LP da fatia em `s* = 18` (lista completa, pequena).** M = 72: 30 configurações × 10 blocos =
300 instâncias; M = 71: 18 × 9 = 162. `certificar_lp.py -j 4` (21 s e 22 s) e `verificar.py`
com sha256:

| M | instâncias | aceitas pelo `verificar.py` | sem certificado | sha256 da lista |
|---|---|---|---|---|
| 72 | 300 | 294 | 264–269: a mesma configuração, blocos (32,22) a (27,27) | `17f5f800a7820f191008fd851ba918f53def5c742d899cd02b3f255fd1659f9a` |
| 71 | 162 | 157 | 139–143: a mesma configuração, blocos (31,22) a (27,26) | `b98ad20cbaa8184830d1b24ea5b311f4578800c2f8ca93bedf1982d669311d2d` |

A configuração que resiste é um conjunto de 18 pontos de `Z_3^5` com bolas de raio 1 disjuntas
(um código de distância mínima 3 com 18 palavras, o máximo possível, `A_3(5,3) = 18`):
`00000 00111 01022 01201 02120 02212 10021 10202 11112 11220 12010 12101 20122 20210 21011
21100 22002 22221`. Nos blocos desequilibrados (36,18) a (34,20) ela morre na raiz, e em (33,21)
morre com 18 folhas. Nos equilibrados o LP da raiz é viável (dual 0, 92 a 157 variáveis
fracionárias) e a ramificação até profundidade 12 não fecha. É o que o PR #68 previu: as
instâncias que decidem são as de K estruturado, que a amostra aleatória não acha.
As 11 instâncias sem certificado, passadas ao MILP do HiGHS (`scipy.optimize.milp`, sem
quebra de simetria, limite de 20 min): **todas inviáveis**, em 4 a 115 s cada. Isso é OBSERVED,
não prova: o HiGHS não emite certificado conferível. Ou seja, nenhum código com 71 ou 72 palavras
tem `s* = 18`, segundo o solver, mas 6 + 5 instâncias continuam sem prova conferida. Fechar isso
exigiria certificado de B&B (VeriPB/RoundingSat com prova, que não instalou no PR #68) ou
cortes melhores. Listas e certificados não versionados (regeneram em segundos com os comandos
da seção 4); sha256 dos certificados gerados: M = 72
`6dd6a97690229b96097b12b235fa30bc97d91121d64c0d591aab46d5ebdc28d8`, M = 71
`4448ec1a2bb9483286de58b181d7946cae3273631c77e207cb9ce607459d36b3` (gzip, não reprodutível
byte a byte).

**K_3(7,2).** `V(6,2) = 73`, `V(6,1) = 13`, `orc` = 42, 102, 162 para `s* = 7, 8, 9`. Nós por nível
em `s* = 8` (exato): `1, 1, 4, 19, 248, 2 710, 53 062, 559 169, 14 314 204`. `s* = 7` não tem
nenhuma configuração (acaba no nível 6), o que explica a busca local do PR #68 não ter achado
nenhuma.

**Estimadores: um serviu, outro não (OBSERVED, e é a lição que fica).**

| estimador | caso | previsto | medido |
|---|---|---|---|
| Knuth, 300 sondas | K_3(7,2) s* = 8, folhas | 2,7 × 10^8 | 14 314 204 |
| Knuth, 3 000 sondas (2 sementes) | idem | 6,9 × 10^6 e 1,4 × 10^6 | 14 314 204 |
| 16 partes sorteadas de 4 096 (nível 6) | idem | 1,19 × 10^7 ± 0,40 × 10^7 | 14 314 204 (ok) |
| 8 partes sorteadas de 1 024 (nível 6) | K_3(6,1) M = 72 s* = 19 | 4 096 ± 2 688 órbitas, 2 665 s de CPU | **411 930** órbitas, ~7 300 s de CPU |

A árvore de K_3(6,1) tem cauda pesada: quase todas as partes têm 0 folhas e poucas têm quase
todas. Por isso o `s* = 9` de K_3(7,2) (partes com 1,5–2,7 × 10^7 folhas cada, coeficiente de
variação 0,2) é uma estimativa razoável, e qualquer estimativa por amostra em K_3(6,1) não é. Para
K_3(6,1) com `s* ≥ 20` uso só **cotas inferiores medidas**: partes contadas por inteiro até um
prazo (`--parcial`), que dão um piso para as órbitas e para os segundos.

## 4. Como reproduzir

    G=tools/exatos/gaps2/nauty_fatia.py
    python3 $G --q 3 --n 6 --R 1 --M 72 --s 18 --contar -j 4            # 30 órbitas, ~30 s
    python3 $G --q 3 --n 6 --R 1 --M 72 --s 19 --contar -j 4            # 411 930, ~30 min
    python3 $G --q 3 --n 6 --R 1 --M 72 --s 20 --parcial 4096 7 3600 -j 4   # piso em 1 h
    python3 $G --q 3 --n 7 --R 2 --M 27 --s 8 --contar -j 3             # 14 314 204, ~1 min
    python3 $G --q 3 --n 7 --R 2 --M 27 --s 9 --amostrar 4096 6 8 -j 4  # ~8,2e10
    python3 $G --q 3 --n 5 --R 1 --M 26 --listar k351.json -j 4         # 343 instâncias
    python3 $G --q 3 --n 6 --R 1 --M 72 --s 18 --listar k361.json -j 4  # 300 instâncias
    C=tools/exatos/k362/contagem
    python3 $C/certificar_lp.py --q 3 --n 6 --R 1 --M 72 --instancias k361.json --saida k361.jsonl.gz -j 4
    python3 $C/verificar.py --q 3 --n 6 --R 1 --M 72 --instancias k361.json \
        --certificados k361.jsonl.gz --sha256 17f5f800…59f9a   # 294 de 300; recusa 264–269

`-j` distribui partes da árvore (nós de um nível repartidos por índice) por processos. Precisa
de `gcc` e `libnauty-dev` (Debian/Ubuntu); a lista sai no mesmo formato de `rodar_pb.py
--listar`, então `certificar_lp.py` e `verificar.py` a leem sem mudança.

## Decisões tomadas sozinho

* Núcleo em C contra a `libnauty` em vez de chamar `dreadnaut` por subprocesso: o `dreadnaut`
  por processo custa milissegundos, e as contagens acima pediram 10^6–10^9 rótulos.
* A deleção canônica pela maior sobreposição marginal (e não pelo maior rótulo) foi escolha
  minha; ela é o que tornou `s* = 18, 19` contáveis. A prova de que a lista não muda está no
  docstring e os testes conferem contra três fontes.
* Não usei VM: a projeção medida passa do teto nas duas células (seção Resumo). Não mexi em
  ledger, data ou paper.
* Rodei o LP só onde a lista inteira é pequena (`s* = 18` de K_3(6,1)), como conferência do
  caminho lista → `certificar_lp` → `verificar` com sha256, e o MILP do HiGHS só nas 11 que
  sobraram. Não são parte de nenhuma cota.
* O piso de `s* = 20` usa 1 h de parede em 4 núcleos; parei aí porque o piso já passa do teto.
* Não versionei listas grandes (a de K_3(7,2) s* = 8 tem 14 milhões de linhas).
