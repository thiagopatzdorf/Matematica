# Kit de busca: códigos de cobertura q-ários (base + remendo)

Ferramentas genéricas para atacar cotas superiores de `K_q(n,R)` com a receita que
funcionou em `K_7(9,4)`:

1. **base**: união de `t` classes laterais de um código linear `C = [n,k]_q`
   (síndromes `0, s_1, …, s_{t-1}`);
2. **remendo**: palavras soltas e/ou retas (classes laterais de subcódigos de dimensão 1)
   que cobrem o resíduo, ou seja, as classes laterais **órfãs** que a base não cobre;
3. **verificação independente** antes de declarar qualquer coisa.

A alavanca é a base: cada síndrome órfã custa uma classe lateral inteira (`q^k` pontos)
de resíduo. Em `K_7(9,4)`: 24 órfãs levavam a 1285; a base de 6 órfãs que o
`base_search` achou levou a 1168 já na primeira rodada.

Todos os programas supõem `q` primo. Palavras e síndromes viram inteiros em base `q`,
com o dígito `i` igual à coordenada `i` (o caractere `i` da linha no arquivo `.txt`).

## Arquivos

| arquivo | o que faz |
|---|---|
| `kit.h` | núcleo comum: tabelas de soma em `F_q^r`, bola de síndromes `B`, RNG |
| `base_search.c` | classes de equivalência de `[n,k]_q` e órfãs exatas da base |
| `patch_opt.c` | otimizador de remendo (SA com listas invertidas, palavras + retas) |
| `expand.py` | JSON de estrutura → lista de palavras (Python puro, para conferência cruzada) |
| `verify.py` | verificador independente (numpy, dilatação de Hamming); imprime o sha256 canônico |
| `xs.sh` | varre `base_search exactT` por um intervalo da lista de classes |

Compilar:

    gcc -O3 -march=native -o base_search base_search.c -lm
    gcc -O3 -march=native -o patch_opt   patch_opt.c   -lm

## base_search

    base_search enum  q n k R t nS1 [shard nshard] [count]
    base_search eval  q n R t nS1 "A"
    base_search exact q n R "A"
    base_search exactT q n R T "A" [m=200] [maxprint=1000]
    base_search canon q n R "A"

- **enum** percorre **todas** as classes de equivalência (monomial) de códigos `[n,k]_q`
  não degenerados: órbitas de `PGL(k,q)` sobre multiconjuntos de `n` pontos de
  `PG(k-1,q)` que contêm `k+1` pontos em posição geral. O representante canônico é a menor
  imagem ordenada entre todos os referenciais ordenados. A geração é ordenada (todo
  canônico contém o referencial padrão), então nada se repete e nada falta. Com `t=1`
  só mede `|Bc|` (barato: 6362 classes de `[9,3]_7` em ~25 s por núcleo); com `t>=3`
  avalia cada classe com a heurística de `eval`. Para paralelizar, use `shard`/`nshard`
  (por resto da contagem).
  Ficam de fora: códigos com coluna nula e multiconjuntos sem `k+1` pontos em posição
  geral (suporte numa reta mais um ponto). São classes ruins para cobertura.
- **eval** (rápido, **não exato**): `c(s) = |Bc ∩ (Bc+s)|` sai da autocorrelação via DFT em
  `Z_q^r`, testa os `nS1` candidatos a `s1` de menor `c` e escolhe o `s2` ótimo exato.
  *Cuidado medido:* em `[9,3]_7` essa heurística devolve 24 na classe cujo ótimo exato é 6.
  Use só como peneira.
- **exact / exactT** (exato para `t=3`): varre todo `s1` (um por classe escalar, já que a
  contagem é invariante por escalar e por translação do trio) e, para cada um, o `s2`
  ótimo. O `exactT` lista todos os trios com órfãs `<= T` e poda de forma exata: as órfãs
  contadas numa amostra `Y ⊂ X` já são cota inferior, então só os `s2` com `cnt_Y <= T`
  são conferidos em `X` inteiro. Custo em `[9,3]_7`: ~70–90 s por classe com `T=6`.
- **canon** dá a forma canônica de um `A` qualquer, para saber se duas bases são a mesma classe.

Saída: uma linha JSON por classe, `{"A": …, "nBc": …, "orphans": …, "coset_syndromes": [0,s1,s2]}`
(no `exactT`, `orphans = -1` significa "nenhum trio com <= T").

## patch_opt

    patch_opt base.json [--dirs g1,g2|auto] [--ndirs D] [--L retas] [--W palavras]
              [--tauw x] [--taul y] [--init sol.json] [--secs s] [--seed s]
              [--T0 t] [--T1 t] [--cyc n] [--out prefixo]

Entrada (JSON simples):

    {"q":7,"n":9,"R":4,"A":"666 065 652 643 621 615","coset_syndromes":[0,7708,4191]}

O `s1`/`s2` dos `p*.json` da frente 2b também serve, e `"frozen":"lista.txt"` congela uma
lista arbitrária de palavras como base. O programa:

1. marca a bola da base e extrai o resíduo;
2. conta, para cada palavra, quantos pontos do resíduo ela cobre (`cnt`);
3. candidatos: palavras com `cnt >= tauw` e retas `p+<g>` (com `g` nas direções dadas, que
   devem ser palavras de `C`) cuja cota `Σ cnt >= taul`. Por padrão ficam as ~400 mil
   melhores palavras e as ~300 mil melhores retas. No modo auto, as direções são as `D`
   melhores pela soma das 64 maiores cotas;
4. monta as **listas invertidas** (candidato → pontos do resíduo na sua bola, e ponto →
   candidatos). Um movimento custa `|lista|`, não `q^n`;
5. SA com reaquecimento, de composição fixa: entra um candidato que cobre um ponto
   descoberto e sai o de menor perda entre 3 sorteados do mesmo tipo. Ao zerar o resíduo,
   grava `prefixo_M<M>.txt` + `.json` e encolhe (tira uma palavra, ou troca uma reta por
   `q-1` palavras gulosas) e continua.

O JSON de saída traz `A`, `coset_syndromes`, `lines` (`[[g,rep],…]`), `gens`/`reps` (quando
há uma só direção, no formato do `gen.py` da frente 2b) e `words`. Para refazer a lista:
`expand.py sol.json out.txt`.

## Verificação (obrigatória)

    python3 verify.py q n R arquivo.txt     # sai 0 só se VALID; imprime sha256_canon

O `verify.py` não reaproveita código do kit: marca as palavras num tensor `(q,)^n` e faz
`R` dilatações de Hamming com `np.roll`. Para `K_7(9,4)` leva ~30 s e ~100 MB. Na VM também
existe `~/h/s2/b/ver` (C, frente 2b). Uma solução só é declarada depois de passar pelos dois.

## Receita K_7(9,4) (2026-10-02)

    base_search enum 7 9 3 4 1 0 > classes.jsonl         # |Bc| de todas as 6362 classes
    # ordenar por nBc e rodar exactT nas primeiras:
    base_search exactT 7 9 4 6 "666 065 652 643 621 615"  # -> 6 órfãs, trio [0,7708,4191]
    patch_opt base6.json --dirs 101111100 --L 0 --W 150 --T0 0.6 --T1 0.1 --secs 3600 --out b6
    python3 verify.py 7 9 4 b6_M<melhor>.txt
