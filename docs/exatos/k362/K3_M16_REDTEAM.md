# K₃(6,2) = 17: red team da afirmação de M = 16 (2026-10-05)

Este red team é continuação de `K3_M15_REDTEAM.md` (PR #59) e tem como alvo o PR #60 (branch
`feat/k362-m16`, documento `K3_M16.md`). O PR afirma que as **12 674 instâncias** da fatia mínima
com M = 16 são inviáveis já no LP. Elas se dividem em s\* = 2: 18, s\* = 3: 124, s\* = 4: 1 461 e
s\* = 5: 11 071, com 13 099 certificados de Farkas. Como existe código de 17 palavras, isso daria
`K₃(6,2) = 17`. Repeti os ataques de M = 15, adaptados, procurando quebrar a afirmação, não
confirmá-la. As ferramentas são as mesmas de `tools/exatos/k362/redteam/`, agora com `--M`/`--tamanho`.

Estados: OBSERVED, COMPUTATIONALLY_VERIFIED e PROVED, como no documento de M = 15. **Nenhuma cota
muda com este documento, e o ledger não foi tocado.**

## Veredito

**A afirmação "não existe código de 16 palavras" (logo K₃(6,2) = 17) sobrevive, com as mesmas
ressalvas de M = 15.** Nenhum dos seis ataques achou instância faltando, combinação de blocos
omitida, restrição inválida, árvore incompleta nem certificado aceito sem merecer. As lacunas
achadas são de redação e de ferramenta. Nenhuma tem gravidade alta.

* A frase do resumo "todas com blocos (6, 5)" vale só para s\* = 5. A lista tem **todas** as
  combinações válidas para s\* ≤ 4: s\* = 4 com (8,4), (7,5) e (6,6); s\* = 3 com 4 combinações;
  s\* = 2 com 6. Isso foi conferido por força bruta.
* O filtro `|U| ≤ (16 − s*)·11`, que dá 121 para s\* = 5, tem a constante certa e a mesma prova.
* O meu verificador mínimo precisou de conserto antes de rodar (seção 3). A versão do PR #59
  enumerava 2^v atribuições com v ≤ 20, e M = 16 tem árvore com 23 variáveis.
* O branch `feat/k362-m16` está empilhado sobre a versão **antiga** do #57 (`600d1c9`), não sobre a
  atual (`970d56c`). Contra a atual, o diff do #60 parece apagar o passo RGS do `GAPS2_K362.md` e a
  obrigatoriedade do `--sha256`. A fusão das duas é limpa (`git merge-tree` sem conflito) e não
  regride nada, mas o #60 precisa de rebase para o diff ficar legível.

Para afirmação pública continua faltando o mesmo que em M = 15: reprodução independente (outra
frente, outro canonicalizador, outro verificador) e, idealmente, Lean.

## Tabela dos ataques

| # | ataque | resultado | estado |
|---|---|---|---|
| 1a | prova de completude e constantes para M = 16 | válida para M qualquer ≤ 729; filtro (16 − s\*)·11 = 165/154/154/143/132/121 | PROVED |
| 1b | blocos por s\* | todas as combinações `t₁ ≥ t₂ ≥ s*` presentes; "(6,5)" é só s\* = 5 | COMPUTATIONALLY_VERIFIED |
| 1c | Burnside × `configuracoes` sem filtro × lista | 1/1/5/35/490/11 075 órbitas; passam 0/0/3/31/487/11 071; nada falta nem sobra | COMPUTATIONALLY_VERIFIED |
| 1d | lista regenerada | sha256 `3cb5b5cc…b4f9ae7`, idêntico | COMPUTATIONALLY_VERIFIED |
| 2 | `farkas_min` nos 13 099 certificados | 12 674 de 12 674, nenhuma recusada | COMPUTATIONALLY_VERIFIED |
| 3 | 81 árvores com ramificação | 81 de 81 completas (semântica e estrutural); até 23 variáveis, 33 folhas | COMPUTATIONALLY_VERIFIED |
| 4 | mutações | obrigatórias 100 % recusadas (inclusive 506 árvores mutiladas); concordância de 100 % | COMPUTATIONALLY_VERIFIED |
| 5 | 26 códigos de 17 × isometrias; 442 subcódigos de 16; 3 069 conjuntos de 16 | 0 falhas; 32 193 transplantes recusados; gerador não certifica as instâncias reais | COMPUTATIONALLY_VERIFIED |
| 6 | famílias de restrição | as mesmas cinco de M = 15; nenhuma nova | PROVED / COMPUTATIONALLY_VERIFIED |

## 1. Completude da lista de M = 16

### 1a. A prova vale para M = 16, e as constantes estão certas

A prova de completude do `GAPS2_K362.md` é escrita para M qualquer ≤ qⁿ. Conferi cada passo
substituindo M = 16:

* **palavras distintas**: 16 ≤ 729, a troca da cópia continua valendo ✔;
* **s\* ≤ ⌊16/3⌋ = 5**, porque as três fibras de uma coordenada somam 16 ✔. Com s\* = 5, toda
  coordenada tem perfil 5+5+6, e há 12 fibras mínimas; qualquer uma serve ✔;
* **filtro**: a constante é `(M − s*)·V(5,1) = (16 − s*)·11`, o que dá 165 / 154 / 154 / 143 /
  132 / 121 para s\* = 0..5. A prova não muda: um ponto `(0,y)` com `y ∈ U` só é coberto por uma
  das `16 − s*` palavras de fora, cada uma a distância ≤ 1 de y, e cada bola de raio 1 em Z₃⁵ tem
  11 pontos. s\* = 0 e s\* = 1 ficam de fora (`|U| = 243 > 176` e `192 > 165`) ✔. Pelo código,
  `fatia.instancias` usa `cap = (M − s)·vol(n−1, R−1, q)`, a mesma conta ✔;
* **blocos**: `t₁ ≥ t₂ ≥ s*` com soma `16 − s*` ✔ (conferido na lista, abaixo);
* **as famílias de restrição** dependem de M só no tamanho (`Σz = 16`) e nos blocos ✔.

O lema do PR #55 para M = 16 (`Σ|U| ≤ 1 426`, logo a menor das 12 fibras mínimas tem |U| ≤ 118) está
certo (PROVED, mesma prova). Ele **não é usado** pela lista nem pelos certificados, e a variante
108, que usa um mínimo medido por MILP (OBSERVED), também não. A lista usa o filtro genérico 121,
que é o mais fraco: é a escolha segura.

### 1b. Blocos por s\*

O resumo do PR diz "todas com blocos (6, 5)", mas isso vale **só para s\* = 5**, onde (6, 5) é a
única opção (`t₁ ≥ t₂ ≥ 5`, soma 11). Contei os blocos na lista do PR. Para s\* ≤ 4 aparecem todas
as combinações válidas, cada configuração com todas elas:

| s\* | palavras fora de F(0,0) | blocos válidos `t₁ ≥ t₂ ≥ s*` | na lista (configurações × blocos) |
|---|---|---|---|
| 2 | 14 | (7,7) (8,6) (9,5) (10,4) (11,3) (12,2) | 3 × 6 = 18 |
| 3 | 13 | (7,6) (8,5) (9,4) (10,3) | 31 × 4 = 124 |
| 4 | 12 | (6,6) (7,5) (8,4) | 487 × 3 = 1 461 |
| 5 | 11 | (6,5) | 11 071 × 1 = 11 071 |

O `lista_completa.py` confere, para cada configuração, que o conjunto de blocos é exatamente o
gerado por força bruta (`blocos_ruins = 0` em todo s\*). **Nada é omitido**, e a frase do resumo
só está imprecisa (a tabela da seção 2 do próprio `K3_M16.md` está certa). COMPUTATIONALLY_VERIFIED.

### 1c. Burnside contra a lista

As órbitas por Burnside são as mesmas de M = 15, porque só dependem de Z₃⁵: 1, 1, 5, 35, 490 e
11 075 para s\* = 0..5. `configuracoes` sem filtro bate com elas. Com |U| recalculado por força
bruta e o filtro de M = 16:

    python3 tools/exatos/k362/redteam/lista_completa.py --M 16 --instancias i16.json
    0 {'orbitas': 1, 'passam': 0, 'na_lista': 0, 'faltam': 0, 'sobram': 0, 'blocos_ruins': 0}
    1 {'orbitas': 1, 'passam': 0, 'na_lista': 0, 'faltam': 0, 'sobram': 0, 'blocos_ruins': 0}
    2 {'orbitas': 5, 'passam': 3, 'na_lista': 3, 'faltam': 0, 'sobram': 0, 'blocos_ruins': 0}
    3 {'orbitas': 35, 'passam': 31, 'na_lista': 31, 'faltam': 0, 'sobram': 0, 'blocos_ruins': 0}
    4 {'orbitas': 490, 'passam': 487, 'na_lista': 487, 'faltam': 0, 'sobram': 0, 'blocos_ruins': 0}
    5 {'orbitas': 11075, 'passam': 11071, 'na_lista': 11071, 'faltam': 0, 'sobram': 0, 'blocos_ruins': 0}
    12674 instâncias na lista, 12674 distintas -> COMPLETA

Toda órbita com |U| ≤ (16 − s\*)·11 está na lista, e só elas. COMPUTATIONALLY_VERIFIED.

### 1d. Lista regenerada

    python3 tools/exatos/gaps2/rodar_pb.py --q 3 --n 6 --R 2 --M 16 --listar i16_regen.json   # ~45 min com a máquina cheia
    12674 instâncias -> i16_regen.json
    sha256sum i16_regen.json
    3cb5b5cc47cd2b418daeaf6643ee9dd0f03c87f221f57d2f4e9cc5bb0b4f9ae7

Idêntico ao sha256 do PR e ao `dados/K3_6_2_M16_instancias.json.gz` descomprimido.
COMPUTATIONALLY_VERIFIED.

## 2. Inviabilidade: verificador mínimo nos 13 099 certificados

O `farkas_min.py` (do PR #59, escrito do zero, em `Fraction`, sem importar gerador, verificador do
PR nem `gaps2`) usa a mesma conferência de M = 15, com `--M 16`:

    python3 tools/exatos/k362/redteam/farkas_min.py --M 16 --instancias i16.json \
        --certificados K3_6_2_M16_certificados.jsonl.gz --sha256 3cb5b5cc…b4f9ae7
    sha256 da lista: 3cb5b5cc47cd2b418daeaf6643ee9dd0f03c87f221f57d2f4e9cc5bb0b4f9ae7
    12674 de 12674 instâncias, 13099 folhas, recusadas [], faltam [] -> TODAS INVIÁVEIS
    real 2m38s

O `verificar.py` do PR, sobre a lista regenerada: `12674 de 12674 instâncias, 13099 folhas,
recusadas [] -> TODAS INVIÁVEIS`. COMPUTATIONALLY_VERIFIED.

## 3. As 81 árvores com ramificação

**Erro encontrado no meu próprio verificador, e corrigido antes da rodada.** O `arvore_cobre` do
PR #59 conferia a completude enumerando as 2^v atribuições das variáveis ramificadas, com teto
v ≤ 20. Em M = 15 o máximo era 4. Em M = 16 há árvore com **23 variáveis distintas**: o verificador
teria parado com exceção. Isso não daria falso positivo, mas deixaria a ferramenta inútil
justamente onde mais importa. Troquei por uma conferência semântica exata que não explode. As
folhas são cubos (atribuições parciais); divide-se por uma variável de algum cubo e se recursa com
os cubos compatíveis, e um cubo vazio cobre tudo. Ela continua sem supor estrutura de árvore. Os
testes novos a comparam com a enumeração em 2 000 casos aleatórios e numa escada de 30
variáveis (`test_arvore_cobre_diverge_da_enumeracao_de_atribuicoes`,
`test_arvore_escada_de_30_variaveis_estoura_ou_falha`). A versão do PR #59 deve receber a mesma
troca.

Resultado nas 81 instâncias com ramificação (2 com s\* = 3, 9 com s\* = 4, 70 com s\* = 5):

* **81 de 81 cobrem** {0,1}^vars, pela conferência semântica e pela estrutural do `verificar.py`;
* no máximo 23 variáveis distintas, profundidade máxima 8 e até 33 folhas (instância 41);
* nenhuma variável ramificada está na fatia (todas com índice ≥ 243, ou seja `c₀ ≠ 0`), e nenhuma
  folha tem fixações contraditórias;
* toda instância que fecha na raiz tem uma folha só, sem fixações.

COMPUTATIONALLY_VERIFIED.

## 4. Mutações

    python3 tools/exatos/k362/redteam/mutacoes.py --M 16 --instancias i16.json --certificados cert16.jsonl.gz \
        --verificar-pr verificar_pr.py --amostra 400
    mutação: [testadas, aceitas por farkas_min, aceitas pelo verificar.py do PR]
      neg      [413, 0, 0]
      sem_fib  [259, 0, 0]
      troca    [413, 0, 0]
      maior_y  [413, 318, 318]
      M+1      [413, 206, 206]
      folha    [506, 0, 0]
    RESULTADO: OK

* **Obrigatórias, todas recusadas pelos dois verificadores:** y = −1, sistema sem linhas de fibra
  (nas 259 folhas que as usam) e cada uma das **506 árvores mutiladas**. Essas são as 81 árvores,
  cada uma sem uma das suas folhas.
* **Informativas, com 100 % de concordância entre os dois:** `troca` 0 de 413 (mais específico que
  em M = 15, onde foram 7); `maior_y` 318; `M+1` 206. Este último é o certificado conferido na
  instância de M = 17 com o mesmo (s\*, K) e `t₁ + 1`. Aceitar não é defeito: muitas instâncias de
  M = 17 são inviáveis, e o código de 17 só vive em algumas. O teste decisivo para prova falsa é a
  seção 5, nas instâncias de M = 17 que **têm** solução.

COMPUTATIONALLY_VERIFIED.

## 5. Códigos reais e subcódigos de 16 palavras

Os mesmos 26 códigos de 17 palavras do red team de M = 15 (o C17 do repositório e 25 do
`sa_cover.c`, todos conferidos por força bruta). Em M = 15 e M = 16 eles caem nas mesmas 2
instâncias de M = 17: s\* = 4, t = (7,6) e s\* = 3, t = (7,7).

    python3 tools/exatos/k362/redteam/codigos_reais.py c17_*.txt --tamanho 16 --isometrias 8 --transplantes 150 \
        --aleatorios 3000 --instancias i16.json --certificados cert16.jsonl.gz --certificar-lp certificar_lp.py
    26 códigos de 17 palavras, 2 distribuições de distância distintas
    208 isometrias normalizadas, 32193 certificados transplantados recusados, 2 instâncias distintas
    passadas ao gerador LP (nenhuma deve ser certificada)
    16 palavras: 3069 passaram no filtro, 3069 achadas na lista; por s*: [(2, 376), (3, 735), (4, 1027), (5, 931)]
    subcódigos de 16 palavras: {'total': 442, 'na_lista': 442, 'fora_do_filtro': 0}
    falhas: []
    RESULTADO: OK            (7 min, 1 processo)

* **Cadeia inteira em M = 17.** 208 isometrias: a normalização é isometria, K sai canônico, passa
  no filtro, e o código satisfaz todas as restrições da sua instância no sistema escrito do zero.
  O gerador do PR não certifica nenhuma das 2 instâncias reais.
* **Soundness.** 32 193 folhas dos certificados de **M = 16**, transplantadas para as instâncias
  viáveis de M = 17, foram todas recusadas, como o lema de Farkas exige.
* **Subcódigos de 16 palavras, todos.** Os 26 × 17 = **442** subcódigos (um por palavra tirada),
  cada um sob uma isometria aleatória, passam no filtro de M = 16 e caem numa instância **da lista
  de 12 674**. Lá violam só linhas de cobertura, o que tem de acontecer, porque nenhum cobre. O PR
  conferiu os 17 subcódigos de um código; aqui são os de todos os 26.
* **Conjuntos de 16 pontos.** 16 palavras de códigos reais, 16 pontos aleatórios e conjuntos com
  as fibras no perfil de s\* = 5 de M = 16: cada coluna é uma permutação de `0⁶1⁵2⁵`, o perfil
  5+5+6 em toda coordenada. Os 3 069 que passaram no filtro (931 com s\* = 5, incluindo os
  subcódigos) estão na lista e só violam cobertura.
* **Lemas com o M do código** nos 26 códigos: a mesma conferência de M = 15, que não depende da
  lista. Valem.

COMPUTATIONALLY_VERIFIED. Como em M = 15, nenhum código real tem s\* = 5; o ramo das 11 071
instâncias s\* = 5 é exercitado pelos 931 conjuntos sintéticos e pela prova.

## 6. Famílias de restrição usadas em M = 16

Os dois verificadores só aceitam índices de cobertura (`< 729`), de fibra (`729 + (j−1)·3 + a`,
j ≥ 1) e `mu` de comprimento 3. Contei nos 13 099 certificados: 5 417 folhas usam só cobertura
(mais tamanho e blocos) e 7 682 usam cobertura e fibra. **Nenhum índice fora disso. Não há família
nova.** As famílias são as cinco de M = 15 (cobertura, fibras ≥ s\*, tamanho = 16, blocos e
fatia 0), mais as fixações de ramo. A validade de cada uma para M = 16 tem a mesma prova de
`K3_M15_REDTEAM.md` (B1), trocando 15 por 16: as fibras valem porque s\* é o mínimo, o tamanho
porque as palavras são distintas, e os blocos e a fatia pela normalização. O lema da projeção
(`≥ 9`), o lema da fatia τ\* ≤ 11 e o lema do #55 (118 ou 108) aparecem no `K3_M16.md` só como
contexto. **Nenhum entra nos certificados.** PROVED (famílias) e COMPUTATIONALLY_VERIFIED
(contagem dos índices).

## Lacunas encontradas

| # | lacuna | gravidade | correção sugerida |
|---|---|---|---|
| M1 | resumo do `K3_M16.md`: "12 674 instâncias … (todas com blocos (6, 5))" sugere que só há (6,5), mas isso vale só para s\* = 5 | baixa (redação; a lista está completa) | escrever "as de s\* = 5 com blocos (6, 5)" |
| M2 | `farkas_min.arvore_cobre` do PR #59 enumerava 2^v (v ≤ 20) e pararia nas árvores de M = 16 (até 23 variáveis) | baixa (ferramenta do red team; erro de recusa, não de aceitação) | consertado aqui; levar a mesma troca ao PR #59 |
| M3 | o #60 está sobre `600d1c9` (o #57 antigo); contra o #57 atual, o diff parece remover o passo RGS e o `--sha256` obrigatório | baixa (a fusão é limpa) | rebase do #60 sobre o #57 atual |
| M4 | o `K3_M16.md` diz que o red team de M = 15 "se aplica aqui sem mudança", mas o verificador de árvore precisou mudar (M2) | muito baixa | ajustar a frase |
| M5 | herdadas de M = 15: enumeração e normalização com uma implementação só; nenhum código real com s\* = 5; nada formal | baixa / baixa / média para publicação | reprodução independente com nauty e outro verificador; Lean |

Nenhuma lacuna de gravidade alta ou crítica foi encontrada.

## Reprodução

    git show origin/feat/k362-m16:tools/exatos/k362/contagem/dados/K3_6_2_M16_certificados.jsonl.gz > cert16.jsonl.gz
    git show origin/feat/k362-m16:tools/exatos/k362/contagem/verificar.py > verificar_pr.py
    git show origin/feat/k362-m16:tools/exatos/k362/contagem/certificar_lp.py > certificar_lp.py
    python3 tools/exatos/gaps2/rodar_pb.py --q 3 --n 6 --R 2 --M 16 --listar i16.json
    python3 tools/exatos/k362/redteam/lista_completa.py --M 16 --instancias i16.json
    python3 tools/exatos/k362/redteam/farkas_min.py --M 16 --instancias i16.json --certificados cert16.jsonl.gz \
        --sha256 3cb5b5cc47cd2b418daeaf6643ee9dd0f03c87f221f57d2f4e9cc5bb0b4f9ae7
    python3 tools/exatos/k362/redteam/mutacoes.py --M 16 --instancias i16.json --certificados cert16.jsonl.gz \
        --verificar-pr verificar_pr.py --amostra 400
    python3 tools/exatos/k362/redteam/codigos_reais.py c17_*.txt --tamanho 16 --isometrias 8 --transplantes 150 \
        --aleatorios 3000 --instancias i16.json --certificados cert16.jsonl.gz --certificar-lp certificar_lp.py

Os códigos `c17_*.txt` vêm de `sa_cover.c`, como em `K3_M15_REDTEAM.md`. Tudo rodou em CPU local,
com no máximo 2 processos meus, sem VM e sem gasto.
