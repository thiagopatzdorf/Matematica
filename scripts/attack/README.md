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
