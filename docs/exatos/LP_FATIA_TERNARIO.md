# Fatia mínima + LP nas células ternárias abertas (2026-10-05)

Pergunta: a via que fechou `K_3(6,2)` (redução por fatia mínima, `GAPS2_K362.md`, e certificados
de Farkas inteiros, `k362/K3_M16.md`) serve em outras células ternárias abertas? Células abertas
com `q = 3`, `n ≤ 8` no `ledger/cells.json`: `K_3(7,3)` 11–12, `K_3(6,1)` 71–73, `K_3(7,2)` 27–34,
`K_3(7,1)` 156–186, `K_3(8,3)` 16–27 (`K_3(8,4)` não está aberta). Para subir a cota inferior de
L para L+1 é preciso provar que **M = L** é inviável. Estados como no `AGENTS.md`.

## Resumo por célula

| célula | M testado | instâncias | o que o LP faz | estado | veredito |
|---|---|---|---|---|---|
| K_3(7,3) 11–12 | 11 | **143** (lista completa, 0,8 s) | **nenhuma** morre na raiz; valor mínimo do LP sem blocos fica em 9,0–11,0 (precisa passar de 11); a melhor (LP = 11,0) não fecha com ramificação até profundidade 8; RoundingSat sem simetria: 3 de 3 com tempo esgotado em 600 s | OBSERVED | via morta como está |
| K_3(6,1) 71–73 | 71, 72 | não enumerável: s* ∈ 18..24 e até ~10^27 órbitas antes do filtro | 44 de 44 amostras mortas na raiz (0,2–0,5 s cada), **mas** o LP também mata K aleatórios com M = 75 e 78, acima do valor 73 que existe; a amostra não mede nada | OBSERVED | gargalo é a lista, não o LP; amostra inválida |
| K_3(7,2) 27–34 | 27 | não enumerado: s* ∈ 7..9, até ~10^12,7 órbitas antes do filtro | 6 de 6 amostras na raiz (folga 0,43–0,46), e o mesmo com M = 30, 33, 36, 39, 42 (acima da cota superior 34) | OBSERVED | idem |
| K_3(7,1) 156–186 | — | s* ∈ 48..52, ~10^72 órbitas antes do filtro | não medido | — | fora de alcance da enumeração |
| K_3(8,3) 16–27 | 16 | s* ∈ 3..5, ~10^5,5 órbitas antes do filtro | um LP de 6 561 variáveis não terminou em 15 min no container disputado | — | não medido; por analogia com K_3(7,3) (R = 3, LP fraco) a aposta é ruim |

Validação em valores conhecidos:

| caso | instâncias | resultado | estado |
|---|---|---|---|
| K_3(5,2) = 8, M = 7 | 7 | 7 de 7 mortas na raiz; `verificar.py` aceita | COMPUTATIONALLY_VERIFIED |
| K_3(4,1) = 9, M = 8 | **0** | o filtro de contagem sozinho já elimina tudo | COMPUTATIONALLY_VERIFIED |
| K_3(5,1) = 27, M = 26 | **343** (lista nova por aumento canônico, ver abaixo; s* = 7: 3, s* = 8: 340) | 343 de 343 mortas na raiz, 17 s em 1 processo; `verificar.py`: `TODAS INVIÁVEIS` | COMPUTATIONALLY_VERIFIED |
| K_3(5,1), M = 27 (existe código) | lista não terminou (`aumento.py` passou de 60 min com s* = 9 e foi interrompido) | o código `H × Z_3` (Hamming [4,2] vezes um símbolo livre), normalizado por `canon_fatia`, cai numa instância que o LP **não** certifica, como deve | COMPUTATIONALLY_VERIFIED |
| K_3(6,3) = 6, M = 5 | 5 | **0 de 5** certificadas pelo LP (ramificação até 12). Fecha por outro caminho: as 3 com s* = 0 morrem pelo lema da fibra vazia (abaixo, com K_3(5,2) ≥ 8); as 2 com s* = 1, RoundingSat UNSAT em 17 s e 69 s (sem VeriPB aqui) | OBSERVED (a parte s* = 1 não tem prova conferida) |

Nenhuma cota do ledger muda. Nenhum código novo.

## 1. O que foi adaptado

O código da fatia (`fatia.py`, `fatia_pb.py`, `certificar_lp.py`, `verificar.py`) já recebe
`q, n, R, M` e não tem constante de `K_3(6,2)`: o filtro é `|U| ≤ (M − s*)·V(n−1, R−1)`, `s*` vai
de 0 a `⌊M/q⌋` e os blocos são as partições `t_1 ≥ … ≥ t_{q−1} ≥ s*` de `M − s*`. Conferi isso
lendo o código e rodando os valores conhecidos acima.

**O que não escala é a lista.** `fatia.configuracoes` percorre multiconjuntos de colunas RGS; o
número de padrões cresce como o número de Bell em `s*`, e com `s* ≥ 7` não termina. Por isso
escrevi `tools/exatos/gaps2/aumento.py`: representantes nível a nível (acrescenta um ponto, forma
canônica = menor conjunto de índices sobre o grupo inteiro `S_q ≀ S_m`, tabela em numpy), com a
poda hereditária `cobertos(T) + (s − k)·V(m,R) ≥ q^m − cap`, que nunca descarta um subconjunto de
um conjunto válido (prova no docstring). Só serve quando o grupo cabe em memória: `m ≤ 4` com
`q = 3` (31 104 elementos). `tests/test_aumento.py` confere contra `fatia.py`: as contagens de
órbitas de `s` pontos de `Z_3^4` (s = 1..4: 1, 4, 20, 144; s = 5 deu 1 245 nos dois, fora do
teste por tempo), as listas de instâncias de K_3(5,2) M = 7, 8 e K_3(4,1) M = 8, 9 (iguais a
menos de isometria) e a poda contra o filtro aplicado só no fim.

**Lema da fibra vazia** (vale para qualquer célula; é o caso `s* = 0` da prova do filtro). Se
`s* = 0`, a fatia `{x_0 = 0}` inteira é coberta pelas `M` palavras com raio `R − 1` nas outras
coordenadas, logo `M ≥ K_q(n−1, R−1)`. Para K_3(7,3) com M = 11 as 6 instâncias com `s* = 0`
pedem `K_3(6,2) ≤ 11`, falso pela cota da literatura (15) e pelos certificados de M = 15 do
`K3_M15_CONTAGEM.md`. Para K_3(6,3) com M = 5 pedem `K_3(5,2) ≤ 5`, falso (M = 7 certificado
acima). O LP não enxerga isso: o LP da fatia vazia é o LP de cobertura de `Z_q^{n−1}`, que vale
`q^{n−1}/V(n−1,R−1)` (9,99 em K_3(6,2)). **Não** pus o lema no código: ele só mataria 6 das 143
instâncias de K_3(7,3) e o resto também não fecha.

## 2. K_3(7,3), M = 11 (prioridade)

Lista completa: 143 instâncias (`rodar_pb.py --listar`, 0,8 s): `s* = 0`: 6, `s* = 1`: 5,
`s* = 2`: 18 (6 configurações × 3 blocos), `s* = 3`: 114 (57 × blocos (5,3) e (4,4)).

| medida | resultado |
|---|---|
| valor do LP `min Σz` com a fatia fixada, fibras ≥ s*, sem fixar blocos (63 configurações) | 9,99 (s* = 0), 10,14 (s* = 1), 9,86–10,42 (s* = 2), 9,0–11,0 (s* = 3). Nenhuma passa de 11: **0 de 63 mortas na raiz** |
| dual de Farkas na raiz com blocos fixos (instâncias 0, 35, 36) | 0 (LP viável) |
| melhor configuração (LP = 11,0; instâncias 35 e 36), `certificar` até profundidade 8 | sem certificado (234 s e 199 s) |
| instância 0 (s* = 0), profundidade 4 | sem certificado (81 s) |
| RoundingSat `d4edbf7` sem SoPlex, sem quebra de simetria, 600 s | instâncias 35 (s* = 3), 11 (s* = 2), 6 (s* = 1): **3 UNKNOWN** |

Leitura: a folga do LP é de uma palavra em 11 com 2 187 variáveis. Raio grande deixa a relaxação
fraca: a cota de esferas é 2187/379 = 5,8, contra 11 a provar. Em K_3(6,2) a cota de esferas é
9,99 contra 16. O mesmo aconteceu no caso conhecido K_3(6,3) (0 de 5). A via, como está, não
fecha K_3(7,3). O que poderia fechar, não testado: aplicar a fatia em duas coordenadas (fixar as
duas fibras mínimas, como LMT fazem em K_3(6,1)), ou cortes de cobertura de subcubos com
arredondamento inteiro (Chvátal–Gomory) a partir de `K_3(m, r)` pequenos.

## 3. K_3(6,1), M = 71 e 72 (o boss)

**Constantes.** `V(5,0) = 1`, então o filtro é `|U| ≤ M − s*`. Como 23 ou 24 bolas de raio 1
(11 pontos) precisam cobrir `243 − (M − s*)` pontos de `Z_3^5`, sobra `s* ≥ 18` nos dois casos
(`11s ≥ 243 − M + s`). Logo `s* ∈ 18..24` (M = 72) e `18..23` (M = 71).

**Lista.** Até ~10^27 órbitas de 24 pontos antes do filtro (`C(243,24)/|S_3 ≀ S_5|`). O filtro
pede conjuntos quase perfeitos (24 bolas com sobreposição total ≤ 69), mas nada indica que isso
traga a conta para menos de muitos milhões; `aumento.py` não roda em `m = 5` (o grupo tem 933 120
elementos e a tabela não cabe) e não medi a contagem.

**LP.** Amostras por busca local (`amostra_lp.py`), blocos sorteados:

| M | s* | amostras | mortas na raiz | |U| | folga do dual |
|---|---|---|---|---|---|
| 72 | 24 | 22 | 22 | 30–48 | 0,10–0,26 |
| 72 | 22 | 6 | 6 | 38–49 | 0,14–0,21 |
| 72 | 21 | 4 | 4 | 50–51 | 0,19–0,23 |
| 72 | 24 = `H × Z_3` menos 3 palavras | 4 | 4 | 24 | 0,107 |
| 71 | 23 | 10 + 4 (`H × Z_3` menos 4) | 14 | 32–46 | 0,14–0,35 |
| 72 | 18 | — | — | a busca não achou K com |U| ≤ 54 | — |

**Controle que derruba a amostra.** O LP também mata K aleatórios onde existe código: K_3(6,1)
com M = 75 (3 de 3), 78 (3 de 3), 81 (1 de 3); K_3(5,1) com M = 27 (5 de 6) e M = 30 (3 de 6),
quando `K_3(5,1) = 27`; K_3(7,2) com M = 36, 39, 42, acima da cota superior 34. Ele só para de
matar bem acima (K_3(6,1) M = 90, K_3(7,2) M = 45: 0 certificadas). Ou seja, um K aleatório que
passa no filtro quase nunca se estende a um código, de qualquer tamanho perto do ótimo, e o LP
vê isso. As instâncias que decidem são as raras, de K estruturado (fatias de códigos bons), e a
amostra uniforme por busca local não as encontra. **Extrapolar "x% morrem na raiz" de uma amostra
assim não é válido** (OBSERVED; é o motivo do aviso no docstring de `amostra_lp.py`).

Tentativa de pular a lista: MILP com só a fatia inteira (243 binárias, `Σ = s*`, ponto 0 fixo) e
o resto contínuo, M = 72, s* = 24, blocos (24, 24), HiGHS: **tempo esgotado em 600 s**.

Veredito: o LP da fatia é forte em K_3(6,1), mas sem uma lista de representantes para
`s* = 18..24` em `Z_3^5` (ou uma quebra de simetria que faça o papel dela num B&B) não há como
rodar tudo, e a amostra não permite estimar. A peça que falta é a enumeração (canonização por
nauty, que o container tem como `dreadnaut`, com a poda hereditária de `aumento.py`), e o
primeiro número a medir é a contagem de órbitas com `s* = 18, 19` (as mais restritas).

## 4. K_3(7,2), K_3(7,1), K_3(8,3)

* **K_3(7,2), M = 27**: `cap = 13(27 − s*)`, e 73-bolas cobrindo `729 − cap` dá `s* ∈ 7..9`. A
  busca local não achou K com `s* = 7` (folga de sobreposição 42). Amostras com s* = 8, 9: 6 de
  6 na raiz, folga 0,43–0,46, 4 s por LP. Mesmo problema de amostra que em K_3(6,1). Lista em
  `Z_3^6`: grupo de 33,6 milhões de elementos, só com nauty.
* **K_3(7,1), M = 156**: `s* ∈ 48..52`, ~10^72 órbitas antes do filtro. Fora de alcance.
* **K_3(8,3), M = 16**: `s* ∈ 3..5` (379-bolas cobrindo `603 + 99s*`). A lista seria pequena
  (~10^5,5 órbitas antes do filtro; `configuracoes` com s* = 5 percorre 63 milhões de
  multiconjuntos, horas em Python), mas um único LP com 6 561 variáveis não terminou em 15 min no
  container (carga 8 em 4 núcleos). Por analogia com K_3(7,3) (cota de esferas 11,4 contra 16),
  o LP deve ser fraco. Não gastei VM nisso.

## 5. Como reproduzir

    # listas
    python3 tools/exatos/gaps2/rodar_pb.py --q 3 --n 7 --R 3 --M 11 --listar k373.json   # 143
    python3 tools/exatos/gaps2/aumento.py  --q 3 --n 5 --R 1 --M 26 --listar k351.json   # 343, ~12 min
    # certificados e conferência exata
    python3 tools/exatos/k362/contagem/certificar_lp.py --q 3 --n 5 --R 1 --M 26 \
        --instancias k351.json --saida k351.jsonl.gz -j 1
    python3 tools/exatos/k362/contagem/verificar.py --q 3 --n 5 --R 1 --M 26 \
        --instancias k351.json --certificados k351.jsonl.gz --sha256 965d72ae…a691a5405f
    # amostra (controle negativo, não estimativa)
    python3 tools/exatos/gaps2/amostra_lp.py 3 6 1 72 24 12 21 6 0

sha256 completo da lista de K_3(5,1) M = 26:
`965d72aee97eb027fcf17eff0e079b1a70ac94c189c63c5c50c175a691a5405f`. A lista e os certificados
não foram versionados (regeneram em minutos).

## Decisões tomadas sozinho

* Não usei VM: nada do que mediria cabia em US$ 2 com chance de fechar (K_3(7,3) não fecha nem
  com ramificação; K_3(6,1)/K_3(7,2) não têm lista).
* RoundingSat compilado da fonte oficial sem SoPlex (o download do SoPlex no GitHub deu 403 no
  proxy). VeriPB não instalou (não está no PyPI), então nenhum UNSAT de RoundingSat aqui tem prova
  conferida.
* Parei a medição de RoundingSat em K_3(7,3) depois de 3 tempos esgotados de 3.
