# Red team da varredura de bases [9,3]_7 (raio 4, 3 classes laterais)

Data: 2026-10-02. Auditor adversarial, só leitura sobre os resultados existentes. Sem VM e sem gasto.
CPU: no máximo 1 núcleo local. Scripts do red team em `scripts/audit/redteam/`.

**Alegação atacada.** Sobre as 7737 classes monomiais de códigos [9,3]_7 (6362 não degeneradas e
1375 degeneradas), o mínimo de órfãs `|Bc ∩ (Bc+s1) ∩ (Bc+s2)|` é 6. Ele é atingido só por
A = "666 065 652 643 621 615". Toda outra classe tem mínimo ≥ 9 (varredura com T = 8).

**Veredito.** Nenhum ataque invalidou a alegação. Os problemas achados estão na documentação e na
proveniência, não no resultado. Dois ataques computacionais (5 e 7) ficaram **incompletos**, porque
a fila em núcleo único não terminou antes do prazo. Os detalhes estão na tabela.

## Tabela

| # | ataque | resultado | evidência |
|---|---|---|---|
| 1 | cobertura: L esperados × arquivos, A lido de dentro de cada arquivo, truncado, sem `exact`, L duplicado | FALHOU EM INVALIDAR | `rt_coverage.py` na factory-01. fz: N=6362, 6362 arquivos, **0 problemas**: nenhum faltando, nenhum extra, nenhum duplicado, A, nBc e parâmetros (q,n,R,t,T) = (7,9,4,3,8) batem em todos, `exact:true` em todos, nenhuma linha estranha. O mínimo do JSON é igual ao menor TRIO, e o trio relatado está entre as linhas TRIO. O sha256 de cada arquivo e as órfãs batem com o `ledger_final.jsonl`. fzdeg: N=1375, 1375 arquivos, **0 problemas**, ledger também bate. Classes com órfãs ≤ 8: só L=1 (6, A da alegação). As 1375 degeneradas: nenhuma. Os dois `classes_sorted.jsonl` remotos têm o mesmo sha256 das cópias locais (4e2035d9…, e 2a66e7fd… = `data/audit/degenerate_classes.jsonl`). |
| 2 | shards e migração: localimp, L errado nas cópias | FALHOU EM INVALIDAR | Os 62 arquivos de `localimp/` (L = 5363–5424) são idênticos byte a byte (`cmp`) às cópias em `fz-0((L-1)%3+1)/`. Os 7737 arquivos estão todos no shard esperado `(L-1)%3+1`. Um arquivo com o L errado seria pego pelo ataque 1, porque o A impresso pelo binário vem do argv da linha L. |
| 3 | canonização e enumeração (fórmula de massa) | FALHOU EM INVALIDAR (reprodução independente) | `rt_orbits.c` foi escrito do zero, sem kit.h, base_search, pg2_orbits nem audit_lib. Ele usa outra forma canônica: o mínimo sobre (tripla ordenada não colinear do suporte) × toro diagonal (36). Essa forma vale também sem referencial. Ele também calcula o |Stab| e confere a massa **por número de colunas nulas z**, contra C(m+56,m) − 57·C(m+7,m) + 399, o número de m-multiconjuntos de posto 3. Resultado sobre as 6362+1375 linhas: **7737 válidas, 0 inválidas, 0 pares na mesma órbita**. A massa bate em todo z=0..6: z=0: 31 966 098 199 (= C(65,9) − 651 681); z=1: 4 425 798 972; z=2: 553 075 446; z=3: 61 377 106; z=4: 5 904 402; z=5: 469 224; z=6: 26 068. A soma só das 6362 dá 31 931 793 642, igual ao lado esquerdo da auditoria. Isso prova, de forma independente, que as strings A da lista cobrem toda classe monomial de [9,3]_7 exatamente uma vez. A lista também está ordenada por (nBc, A), como diz o REPRODUCE.md. |
| 4 | poda: estouro de uint8/uint16, T ≥ 255, teto m ≤ 250 | FALHOU EM INVALIDAR | Leitura do código: `m = ceil(mu·N/|Bc|)` é capado em 250 (`if (m > 250) m = 250`) e tem piso 1. Cada y de Y contribui no máximo 1 a cada célula do bloco, porque b ↦ y−b é injetiva, então `blk ≤ my ≤ 250 < 256`. Com T ≥ 255, `blk[l] > T` nunca poda: fica mais lento, sem erro. A contagem completa `o` é `int`. No exactT, `cnt` é uint16 com m=200. Medido nas 7737 saídas: nBc mínimo 10 530 (m = 202) nas não degeneradas e 32 004 (m = 67) nas degeneradas. O teto nunca foi atingido com mu=18. |
| 5 | simetria do trio (sym=1 perde trio?) | FALHOU EM INVALIDAR (argumento); teste empírico INCOMPLETO | Argumento (§3 de exactT2_correctness.md) relido: P1 vale também para hi=0, porque pcH[0]=57 é invariante. P2 é a linearidade de hi, e o salto usa `pcH[addhi[H·HI+neghi[h1]]]` = pc(H − h1), como no texto. O s1 = λd com d de pc mínimo sempre está entre os s1 canônicos percorridos. Não achei furo. Teste: o **FFT exato sem poda** (`rt_fft_trios.py`, abaixo) na classe 1 com T=8 deu as mesmas 3 órbitas (orf 6) que o vt, e MIN_GLOBAL = 6. A comparação exactT × exactT2 sym=0 × sym=1 × FFT na classe 2 com T=25 estava na fila e **não terminou** (ver "Pendente"). |
| 6 | degeneradas: completude das 1375, forma sistemática | FALHOU EM INVALIDAR | Ver o ataque 3: a massa por z, calculada de forma independente, fecha com as 1375 linhas, e o z=0 fecha com 6362+78. Todo código [9,3] tem conjunto de informação (posto 3), então todo código tem forma H=[I6\|A] após permutação. Uma classe sem forma sistemática derrubaria a massa do seu z. Contagem por z (rt_orbits): 78 / 1049 / 189 / 44 / 11 / 3 / 1, que bate com `degenerate_summary.json` (com e sem referencial somados). |
| 7 | dependência de semente/ordem | INCOMPLETO | O binário oficial não aceita semente: `kit_rs` é fixo, então todas as VMs usaram a mesma amostra Y para a mesma classe, e a varredura nunca exercitou outra Y. `rt_build_seeded.sh` compila uma cópia com `RT_SEED`. As rodadas com semente 1 (mu=18) e semente 2 (mu=5, outro tamanho de Y) na classe 2 com T=25 estavam rodando no fim do prazo. Indireto: o exactT (Y de 200, outra sequência de sorteio) e o exactT2 (Y de 202) deram as mesmas saídas nas 14 classes do diferencial, e a FFT, que não tem Y, confere a classe 1. |
| 8 | escopo do texto público | ACHOU PROBLEMAS (documentação; o paper está correto) | Ver "Problemas" abaixo. O `paper/main.tex` v0.5 está bem delimitado: a linha 168 diz que o mínimo sobre as 6362 e as 1375 "is under audit and is not a claim of this note". |

### Verificação extra: contagem exata por FFT (algoritmo diferente, sem poda)

`rt_fft_trios.py` monta a bola enumerando os e de peso ≤ 4. Para cada s1 canônico, ele calcula
cnt[s2] = |X ∩ (Bc+s2)| para **todo** s2 por correlação cíclica em Z_7^6 (FFT 6-D do numpy). Não
há amostra, bloco, simetria nem saída antecipada. O erro de arredondamento é medido e impresso.

| classe | nBc | órbitas ≤ 8 | mínimo global | erro de arred. | tempo | bate com a varredura |
|---|---|---|---|---|---|---|
| L=1 (campeã) | 10 530 | 3 (todas com 6), iguais ao vt byte a byte | **6** | 1,4e-12 | 255 s | sim |
| L=2, L=3, L=4, D319, D40 | — | — | — | — | — | **pendente** (fila) |

Custo: ~255 s por classe num núcleo, ou seja, ~550 h de CPU para as 7737. É um certificado
independente viável em nuvem, não aqui.

## Problemas encontrados (por gravidade)

1. **Médio, documentação: referências a arquivos que não existem.** `Matematica/audit/k794-base-sweep/SEARCH_COVERAGE.md`
   cita `RESULTS.csv`, `COMPUTE_CERTIFICATE.json` e `FINAL_AUDIT.md`, e diz que "o mínimo exato acima de 8 sai
   de uma rodada à parte com T = 20, nas 120 primeiras classes". Nada disso está no repositório. O
   REPRODUCE.md manda fazer checkout de `<kit_commit>` "fixado em COMPUTE_CERTIFICATE.json", que não existe.
   `docs/audit/exactT2_correctness.md` cita `docs/audit/differential.md`, que também não existe. Diz ainda que
   foram rodados "conjuntos completos com T=30: classes 1, 2, 3 e 5", mas no scratchpad só há T=30 para a classe 1.
2. **Médio, escopo: a tabela do SEARCH_COVERAGE.md marca o passo 5 como "computado, auditado"**, e a frase
   "Juntos, os passos 1–5 dão o mínimo de órfãs na família inteira" afirma o resultado sem a ressalva da
   própria doc: a varredura de produção usou um único binário otimizado, a recontagem independente das
   7737 classes não foi feita (o próprio REPRODUCE §5 admite) e o diferencial cobre 14 classes. O README
   (linhas 41–43) está correto ("em auditoria, fora das afirmações").
3. **Baixo, proveniência inferida, não registrada.** Os arquivos `c_L.out` não trazem o commit nem o modo.
   O campo `versao` do ledger é deduzido pelo horário (mtime). O `fazenda.sh` faz `git pull` do branch vivo
   `feat/kit-de-busca` a cada (re)lançamento. Uma VM religada depois de preempção compila o que estiver
   no topo do branch naquele momento. Medido: o base_search.c só mudou nos commits a44bed6 (12:40),
   75a844b (12:55) e 3c4ed99 (13:32), e a cópia atual na factory-01 tem o sha256 b3b6cd92…, igual ao 3c4ed99.
   Então os arquivos de 12:40–12:55 podem ter vindo do a44bed6 (exactT2 sem sym), o que a tabela de
   proveniência não lista. Como todas as variantes têm a mesma saída pelos argumentos, isso não muda o
   resultado. Mas a tabela de proveniência é reconstrução, não registro. Correção barata: o binário
   imprimir o commit (`-DKIT_COMMIT`) e os parâmetros (mu, sym, m) no JSON.
4. **Baixo, a semente é fixa.** O kit_rnd não tem semente no exactT/exactT2, então a varredura não
   testou a independência em relação a Y. Ela é garantida pelo argumento da poda, mas não foi exercitada.
5. **Informativo, o "verificador independente" não é algoritmicamente independente.** O verify_trios usa a
   mesma poda por amostra (com a mesma constante de xorshift do kit). A independência é só de
   implementação. A FFT deste red team é a primeira contagem sem poda, e foi feita em 1 classe.

## Pendente (fila em andamento quando o prazo acabou)

Em `scratchpad/rt/` (queue.sh, queue2.sh, queue3.sh), em sequência, num núcleo:
classe 2 com T=25: exactT2 com semente 1, com semente 2 e mu=5, FFT exata; depois exactT, exactT2 sym=0 e
sym=1. Depois a FFT com T=8 nas classes L=3, L=4 e nas degeneradas de menor nBc (ledger L=319 e L=40).
Para comparar: `python3 scripts/audit/redteam/rt_compare.py fft_25_2.out t1_25_2.out t2s0_25_2.out t2s1_25_2.out t2seed1_25_2.out t2seed2mu5_25_2.out`.
O primeiro queue.sh perdeu as três rodadas exactT por falta de `/usr/bin/time`. O queue2.sh as refaz.

## Scripts

| script | ataque |
|---|---|
| `scripts/audit/redteam/rt_coverage.py` | 1, 2 (rodado na factory-01, `~/state/maestro/redteam/`) |
| `scripts/audit/redteam/rt_orbits.c` | 3, 6 (37 s num núcleo) |
| `scripts/audit/redteam/rt_fft_trios.py` | 5 e contagem exata sem poda |
| `scripts/audit/redteam/rt_build_seeded.sh` | 7 |
| `scripts/audit/redteam/rt_compare.py` | 5, 7 (compara conjuntos de órbitas) |
