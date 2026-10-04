# patch_setcover: o remendo como SET COVER UNICUSTO, sem simetria imposta

Nossos melhores códigos são **base + remendo**: uma união de classes laterais de um código
linear (a base) deixa um resíduo `U` de pontos a distância `> R`, e o remendo é um conjunto de
palavras soltas cujas bolas cobrem `U`. Achar o menor remendo é exatamente o **problema de
cobertura de conjuntos unicusto** (USCP): linhas = pontos de `U`, colunas = bolas
`B_R(w) ∩ U` de todas as palavras `w` do espaço.

Até aqui o remendo vinha de recozimento simulado (`scripts/search/patch_opt.c`) ou de ILP com
simetria imposta (`candidates/k7_9_4_1134/ilp_sym.py`, invariância por uma reta de C0). Esta
pasta traz o estado da arte de busca local para USCP, sem simetria nenhuma.

## Arquivos

| arquivo | o que faz |
|---|---|
| `patch_inst.c` | gera a instância: resíduo da base, cobertura de cada palavra, conjuntos com `>= T` pontos (formato binário PSC1) |
| `rwls.c` | a busca (RWLS; CC por hiperaresta opcional) |
| `psc_io.py` | lê/escreve PSC1, converte OR-Library (`scp*.txt`) para unicusto, ILP exato de referência (HiGHS, só para instância pequena) |
| `make_base.py` | separa base e remendo de um código do repo (`data/structured/*.json`) |
| `register.py` | grava `data/codes` + `data/attack` de um remendo novo (o JSON estruturado sai do `scripts/codes/build_structured.py`) |
| `quotient.py` | instância quociente por uma translação (remendo invariante por uma reta, a família do `ilp_sym.py`) |
| `../../tests/test_patch_setcover.py` | testes rápidos (ótimos conhecidos K_2(5,1)=7, K_3(3,1)=5; resíduo e conjuntos contra força bruta) |

    gcc -O3 -march=native -o patch_inst patch_inst.c
    gcc -O3 -march=native -o rwls rwls.c
    ./patch_inst 7 9 4 base.txt 16 k794_T16.bin [remendo_conhecido.txt]
    ./rwls k794_T16.bin -t 3600 -s 1 -k 104 -i remendo_105.txt -o melhor.txt

`base.txt` = as palavras da base (convenção do repo: dígito `k` da linha é a coordenada `k`).
O código final é `base.txt` + a saída `-o`; **nada vira afirmação sem `tools/verify/verify` e
`scripts/attack/verify_bfs`** (dois algoritmos independentes destes programas).

## O algoritmo (RWLS) e a referência

**Gao, Yao, Weise & Li (2015)**, *An efficient local search heuristic with row weighting for
the unicost set covering problem*, EJOR 246(3):750–761, doi:10.1016/j.ejor.2015.05.038.
O PDF é fechado e não está no acervo (o bucket `gs://factory-literatura-matematica/txt/` não tem
texto de USCP); a implementação segue a descrição do algoritmo, e a correção foi conferida pelo
número: nas instâncias unicusto da OR-Library ela bate os melhores valores conhecidos da
literatura (tabela em `docs/attack/SETCOVER_2026-10-04.md`).

```
w(e) = 1 para todo ponto; S = guloso; tira redundantes; S* = S
repita até o tempo/alvo:
    enquanto S cobre tudo: S* = S; tira de S o conjunto de maior score
    tira de S o de maior score (empate: mais antigo), exceto o último posto (tabu)
    e = ponto descoberto sorteado
    põe, entre os conjuntos que cobrem e e têm canAdd, o de maior score (empate: mais antigo)
    w(e) += 1 para todo ponto descoberto
score(s) = +soma w dos descobertos de s (s fora) | -soma w dos que só s cobre (s dentro)
```

* `-c 1` (padrão, RWLS): configuration checking por vizinhança — conjunto tirado não volta
  até que um conjunto que compartilha ponto com ele mude de estado.
* `-c 2`: CC por hiperaresta de **Wang, Ouyang, Zhang & Yin (2017)**, *A novel local search for
  unicost set covering problem using hyperedge configuration checking and weight diversity*,
  Sci. China Inf. Sci. 60:062103, doi:10.1007/s11432-015-5377-8 (NuSC): libera os conjuntos de
  um ponto que mudou entre coberto e descoberto. A "diversidade de pesos" do NuSC não está
  implementada.
* `-b 1` (nosso): desempate pelo tamanho do conjunto antes da idade. Medido em K_7(9,4): pior
  que o desempate por idade (ver relatório); fica como opção, não como padrão.
* `-G N` (nosso): N gulosos aleatorizados antes da busca (fila de baldes, desempate sorteado,
  redundantes tirados em ordem aleatória). **Foi o que deu K_7(10,4) ≤ 5607.**
* `-I d [-S s]` (nosso): guloso iterado no lugar do RWLS (tira d conjuntos, refaz guloso, aceita platô).
* `-g γ -r ρ` e `-u cap` (nossos): suavização de pesos e recomeço por deriva. Medidos em
  K_7(9,4): não ajudaram (relatório, seção 3).
* `-T c`: sobe o corte de cobertura na leitura, sem regerar a instância.
* Detalhe de implementação: o xor dos ids dos cobridores de cada ponto dá o cobridor único em
  O(1), que é o que o score precisa quando a contagem passa de 2 para 1.

## O corte T (limite honesto)

Com `T = 1` a instância de K_7(9,4) teria ~376 M incidências. O gerador guarda só palavras
com `>= T` pontos do resíduo; a busca é completa **dentro dessa família**. O relatório diz o T
de cada rodada. Um remendo ótimo pode, em princípio, usar palavras abaixo do corte.

## Memória

`patch_inst`: `q^n` bytes + `4 q^n` (índice de candidato) — 7^10 ≈ 1,4 GB. `rwls`: ~8 bytes por
incidência nos dois sentidos (instância de 100 M incidências ≈ 1 GB).
