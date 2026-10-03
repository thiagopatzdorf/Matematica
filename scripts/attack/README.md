# Ataque às células de 2011: classes laterais + remendo, genérico em (q, n, R)

Receita que deu `K_7(9,4) <= 1137`, transformada em linha de montagem para qualquer `q` primo.
Tudo aqui é busca; **nada vira afirmação sem `verify_bfs` e `tools/verify/verify`** (dois
algoritmos independentes dos buscadores) e sem conferir `ledger/cells.json`.

## A ideia em uma frase

Uma união de `t` classes laterais de um `[n,k]_q` cobre exatamente as síndromes de `S + B`,
`B = {H e : wt(e) <= R}`. O que sobra (síndromes órfãs, `q^k` pontos cada) é coberto por
palavras soltas (remendo). O tamanho final é `t*q^k + |remendo|`.

## Linha de montagem (comandos usados de verdade)

    gcc -O3 -march=native -o scripts/attack/hsearch   scripts/attack/hsearch.c   -lm
    gcc -O3 -march=native -o scripts/attack/coset_wsa scripts/attack/coset_wsa.c -lm
    gcc -O3 -march=native -o scripts/attack/verify_bfs scripts/attack/verify_bfs.c
    gcc -O3 -march=native -o scripts/search/coset_sa  scripts/search/coset_sa.c  -lm
    gcc -O3 -march=native -o scripts/search/patch_opt scripts/search/patch_opt.c -lm
    gcc -O3 -march=native -o scripts/search/base_search scripts/search/base_search.c -lm

1. **H** — `hsearch q n k R reinicios passos seed [ntop] [t]`: subida de encosta em `A` de
   `H=[I|A]`. `t=1` maximiza `|B|`; `t=2,3` minimiza as órfãs da melhor base de t classes.
   Imprime `H="..."`, que é o argumento dos programas seguintes.
2. **base grossa** — `base_search eval q n R t nS1 "A"` (t <= 3, exato/quase) ou
   `coset_sa q n R "H" t secs seed T0 T1 out` (t qualquer, SA no espaço de síndromes).
3. **refinar** — `expand_cosets.py lift q n "H" sindromes.txt j`: a mesma base vista como
   `t*q` classes do subcódigo `x_j = 0`. Agora o SA troca classes de custo `q^(k-1)`.
4. **base fina** — `coset_sa` (t fixo, encolhe quando zera) ou `coset_wsa` (t livre,
   minimiza `t*q^k + w*órfãs`; `w` = custo medido de remendo por órfã).
5. **remendo** — `expand_cosets.py expand ... > base.txt`, depois
   `patch_opt base.json --L 0 --W 200 --secs 600` com `{"q":..,"n":..,"R":..,"frozen":"base.txt"}`.
6. **verificar** — `verify_bfs q n R codigo.txt M` e `tools/verify/verify -q -n -r -m`.
7. **guardar** — `data/codes/q<Q>_n<N>_R<R>_M<M>.txt` + proveniência em
   `data/attack/<mesmo nome>.json` (H, síndromes, remendo, origem, verificação).

## Lições medidas (2026-10-03)

* Cobrir `F_q^r` com translações de `B` é ineficiente: em `K_7(10,3)` (k=4) 14 translações
  (densidade 3,2) ainda deixam 1,2% de órfãs. Bases lineares grandes (k alto, t <= 3) dão
  densidade melhor; por isso o caminho é grosso (k, t pequeno) -> lift -> fino (k-1).
* Uma órfã custa ~q^k / (cobertura máx por palavra) de remendo, muito menos que uma classe.
  `K_7(10,4)`: 3 órfãs de 343 pontos = 179 palavras (cobertura máx 7). `K_5(11,4)`: 7 órfãs
  de 125 = 147 palavras. Daí o `coset_wsa`.
* `coset_wsa`: a temperatura é em palavras. Com T0=120 o t sobe sem parar (entra aceito
  demais); T0 ~ w, T1 ~ w/8 funcionou.
* A posição das órfãs pesa tanto quanto o número: a mesma base grossa de `K_7(10,4)`,
  refinada por `x_9 = 0` ou por `x_6 = 0`, deu 3 órfãs nos dois casos e remendos de 179 e
  128 palavras. Próximo passo natural: o SA da base fina medir o custo do remendo (ou a
  cobertura máx por palavra sobre as órfãs), não só a contagem.
* Refinar mais um nível (k=2) não ajudou: `K_5(11,4)` 115 -> 114 classes deixa 7 órfãs
  que custam 25 palavras (= a classe tirada); `K_7(10,4)` em k=2 não saiu de 21 órfãs.

## Resultado por célula (2026-10-03; nenhuma vira afirmação: ledger intocado)

| célula | ub publicado | nosso verificado | construção | arquivo |
|---|---:|---:|---|---|
| K5(10,5) | 175 | **162** | [10,3]_5, t=1 (8 órfãs) + 37 palavras (cota do LP p/ esta base: 147) | `data/codes/q5_n10_R5_M162.txt` |
| K5(11,4) | 3125 | **2875** | 23 classes de [11,3]_5, sem remendo | `data/codes/q5_n11_R4_M2875.txt` |
| K7(10,4) | 6517 | **5616** | 16 classes de [10,3]_7 (3 órfãs) + 128 palavras | `data/codes/q7_n10_R4_M5616.txt` |
| K5(11,6) | 125 | 125 (= ub) | [11,3]_5 com raio 6; em k=2 com t=4 sobram 7746 órfãs | — |
| K7(9,3) | 8575 | sem melhora | k=4 t=3: 44 órfãs de 2401 pontos; k=3 t=24: 139 órfãs | — |
| K7(10,3) | 42189 | sem melhora | k=5 t=3 cobre (50421); lift k=4 t=20 deixa 63 órfãs | — |
| K7(10,6) | 175 | não atacada a fundo | k=2: B tem 5,41M de 5,76M síndromes (t=1); remendo de R=6 é caro de enumerar | — |
