# Auditoria de leitura do verificador do Marosi (`verify_cov.py`)

Agente MA, 2026-10-03. Somente leitura: nenhum código de terceiros foi executado (nem `verify_cov.py`, nem `verify_independent.py`, nem `lincov`). Custo: US$0.

## 0. O que foi lido

| item | origem | identificação |
|---|---|---|
| repositório | `https://github.com/Mapika/coldcase`, clone local preexistente no scratchpad do agente anterior (`.../scratchpad/w/cc`) | `HEAD` = `56a8cce` ("Journal version: 26 UB + 58 LB ...") = o commit citado no README |
| verificador | `cov/verify_cov.py` (352 linhas) | sha256 `57907fb7f33397a42e4617b8634d27d0d3e884836226ae045ebd305bdfea28ed` |
| cópia do anexo | `paper/covering/anc/verify_cov.py` | `cmp` = idêntica a `cov/verify_cov.py` |
| anexo K7(9,4) | `paper/covering/anc/K7_9_4_M1475.txt` | 1475 linhas, 1475 distintas, todas `^[0-6]{9}$`; sha256 `b3e6054913d7c0407546c82e0bf9755ad10a4fe9e0c2f68ab10a2cc707ac6ace` (bate com o registrado em `literature/lit-marosi-2608-19872-v2.json`) |
| segundo verificador (só lido) | `cov/verify_independent.py` | importa só `argparse, json, sys, numpy` |

## 1. Ficha técnica

* **Linguagem:** Python 3 puro, um arquivo, sem pacote.
* **Dependências:** stdlib (`argparse, json, os, sys, math.comb, time`) + `numpy` (importado só dentro de `verify_numpy`/`choose_method`, linhas 171 e 262). O método `pure` não precisa de numpy.
* **Rede, subprocess, eval/exec, pickle, ctypes, socket:** nenhum. Varredura por texto: zero ocorrências.
* **Escrita em disco:** nenhuma. Há dois `open` só de leitura (linha 63, o arquivo de código; linha 291, `json.load(open(a.json))`, só com `--json`). Saída só em stdout. Exit code 0 = verificado; 1 = há descoberto; 2 = nenhum método rodou; 3 = métodos discordam.
* **Formato de entrada:** uma palavra por linha; `#` comenta; linha vazia ignorada; palavra = n caracteres base-36 (um por coordenada) ou inteiros separados por espaço/vírgula. Cada dígito deve estar em [0,q); comprimento deve ser n; duplicatas são removidas e só **avisadas** (linhas 308 e 91-92).
* **Compatibilidade com `data/codes/*.txt`:** total. Nosso formato é uma palavra de n dígitos por linha, s[0]..s[n-1], dígitos 0..6 para q=7 (conferido em `q7_n9_R4_M1285.txt`: `000000000`, `551665001`...). A convenção de ordem do dígito não importa para cobertura (a distância de Hamming é simétrica nas coordenadas), então não há risco de leitura invertida. Diferenças de contrato: (a) o dele **não** verifica M (só avisa se o sidecar `--json` traz `M` diferente) e **aceita duplicata** (dedup silencioso com aviso); o nosso `verify-c` exige M e rejeita duplicata (exit 2). (b) Ele aceita q,n,R pela linha de comando sem cruzar com o nome do arquivo.
* **Discrepância de documentação (achado):** o `README.txt` do anexo manda rodar `python3 verify_cov.py K6_8_4_M166.txt 6 8 4` (posicional). O script exige `-q 6 -n 8 -R 4`; a forma posicional falha no `argparse` ("unrecognized arguments"). Não afeta correção; afeta quem copiar o comando. O comando exato abaixo usa as flags.

## 2. Algoritmo

Dois métodos exaustivos, escolhidos por `choose_method` (linha 255): `pure` se `q^n ≤ 3e8` **e** `M·V ≤ 5e7`; senão `numpy`.

* **`pure` (linhas 109-152):** `bytearray(q^n)`; para cada palavra, marca todos os pontos da bola de raio R por enumeração BFS por camadas (posição inicial `p0` crescente para não repetir subconjunto de posições). Custo M·V, V = Σ_{i≤R} C(n,i)(q−1)^i. Recusa se `q^n > 3e8` (MemoryError tratado).
* **`numpy` (linhas 169-230), meet-in-the-middle:** divide n = n1+n2 (n1 = n//2), indexa w = (x,y). d(c,w) = d1(c1,x)+d2(c2,y). Pré-calcula `D1[i,x]` (int16, M×q^n1) e, para cada palavra i e raio r≤R, o bitset sobre y de {y : d2(c2_i,y) ≤ r}. Para cada x, faz OR dos bitsets `bits[i, R−D1[i,x]]` das palavras com D1≤R e conta bits; o ponto x é coberto sse a contagem = q^n2. Máscara de bits de preenchimento no último byte (linha 203-206). Não materializa q^n.
* **Raciocínio de correção (lido, não testado):** a decomposição de distância é correta; `pure` e `numpy` compartilham só `parse_code`. O auto-teste dele (`test_verify.py`) diz comparar "três implementações"; não foi executado.

## 3. Complexidade e memória para q=7, n=9, R=4 (q^n = 40 353 607)

V(9,4) = 1 + 54 + 1296 + 18 144 + 163 296 = 182 791. Para M=1475: M·V = 2,70e8 > 5e7, então o `auto` escolhe **numpy**.

| método | tempo estimado | memória estimada |
|---|---|---|
| numpy (n1=4, n2=5: X=2401, Y=16 807, W8=2101 B) | ~10-40 s. Pré-cálculo: 1475 × (5 comparações sobre 16 807 + 5 `packbits`); laço principal: 2401 iterações, cada uma copia por fancy-index e faz OR de até 1475 linhas de 2101 B (≈3 MB) | `D1` 7,1 MB + `bits` 15,5 MB + tabelas pequenas + numpy: pico < 150 MB |
| pure | 2,7e8 marcações em Python puro, ~5-15 min (estimativa grosseira; não medida) | `bytearray` de 40,4 MB + frontier por palavra (até 163 296 tuplas ≈ dezenas de MB) + `sum(covered)` itera 40 M; pico < 300 MB |

Todas são estimativas por contagem de operações; **nada foi medido** (proibido executar). `--radius` repete a verificação ~4 vezes (busca binária) e não deve ser usado.

## 4. Linhas preocupantes (segurança), com número de linha

Nenhuma linha executa código externo. Lista completa do que merece nota:

| linha | o que | risco | mitigação |
|---|---|---|---|
| 47-51 | `import argparse, json, os, sys, math` | nenhum | stdlib |
| 63 | `open(path)` no argumento posicional | lê qualquer arquivo que o chamador aponte (só leitura) | sandbox read-only; passar caminho fixo |
| 70-73, 78-79, 82-87 | erros via `raise SystemExit(msg)` | a mensagem ecoa a linha do arquivo (`%r`) | saída vai para stdout capturado; só texto |
| 113 | `raise MemoryError` se `q^n > 3e8` | nenhum | trata em 322-324 |
| 171 | `import numpy` dentro da função | executa o código do numpy instalado e **qualquer `numpy.py` que apareça antes no `sys.path`** (o diretório do script é o primeiro) | rodar com `python3 -I` num diretório vazio onde só o script e o código foram copiados |
| 262 | `import numpy` em `choose_method` | idem | idem |
| 291 | `json.load(open(a.json))` | só com `--json`; JSON não executa código | não passar `--json`; usar `-q -n -R` |
| 317 | `import time` | nenhum | stdlib |
| 340-341 | `--radius` | só custo de CPU (4× mais lento) | não usar |

Nenhum `eval`, `exec`, `compile`, `__import__`, `pickle`, `marshal`, `subprocess`, `os.system`, `socket`, `urllib`, `ctypes`, escrita (`'w'`, `'a'`), nem `os.remove`/`shutil`. Risco residual real: (i) cadeia de suprimento do `numpy` instalado; (ii) o diretório do script no `sys.path` (resolvido com `-I` e diretório limpo: no clone original o diretório `cov/` contém muitos outros `.py` que **não** devem ficar ao lado); (iii) negação de serviço por CPU/RAM (resolvida com limites).

## 5. Comparabilidade com os nossos três verificadores

| verificador | algoritmo | linguagem | relação com o dele |
|---|---|---|---|
| `verify-c` (`tools/verify/verify.c`) | marca bolas de raio R num bitset | C | **mesma lógica** que o `pure` dele (marcação da bola), mais M/duplicata/formato estritos |
| `verify-rust` | dilatação por camadas, 1 byte por ponto, O(R·n·q^n) | Rust | mesma ideia do `dilate` do `verify_independent.py` dele (que não é o `verify_cov.py`) |
| `verify-py-dilation` | dilatação do indicador do código | Python+numpy | idem; não compartilha lógica com o `numpy` dele |
| **`verify_cov.py --numpy`** | **meet-in-the-middle com bitsets por raio** | Python+numpy | **algoritmo diferente de todos os nossos três**: seria o quarto método independente em lógica |

Conclusão: o `pure` é redundante com o `verify-c`; o `numpy` (MITM) é o que acrescenta independência algorítmica. O que acrescenta independência **de autoria** é que o código é do Marosi (autor da literatura), não do agente-c nem do Thiago. Ressalva honesta: o manuscrito declara ter sido escrito pelo sistema Claude (nota em `lit-marosi-2608-19872-v3.json`); autoria "independente" é de pessoa/linhagem de código, não de modelo.

## 6. Sandbox mínimo e comando exato (NÃO EXECUTADO)

Alvo da futura execução: o anexo dele, `K7_9_4_M1475.txt`, para checar a afirmação K_7(9,4) ≤ 1475 da literatura, **e** o nosso `data/codes/q7_n9_R4_M1285.txt` (mesmo formato). A execução em dois arquivos é a que serve de quarto verificador para os nossos witnesses.

Preparação (leitura/cópia, sem executar o script):

    # 1) diretório limpo, só 2 arquivos, somente leitura
    WORK=$(mktemp -d)                      # fora do repo
    mkdir "$WORK/in" "$WORK/out"
    cp .../cov/verify_cov.py "$WORK/in/"
    cp .../anc/K7_9_4_M1475.txt "$WORK/in/"
    cp data/codes/q7_n9_R4_M1285.txt "$WORK/in/"
    sha256sum "$WORK"/in/*                 # tem de bater com a tabela da secao 0 (script e anexo)
    chmod 0444 "$WORK"/in/*; chmod 0555 "$WORK/in"

Execução sem rede, sem privilégio, com limites (Linux; `unshare` e `prlimit` do util-linux; usuário comum, sem sudo; `/work` = `$WORK`):

    unshare --net --pid --fork --mount-proc -- \
      prlimit --cpu=300 --as=4294967296 --fsize=0 --nofile=64 --nproc=32 -- \
      env -i PATH=/usr/bin:/bin LANG=C.UTF-8 \
      python3 -I -B /work/in/verify_cov.py /work/in/K7_9_4_M1475.txt -q 7 -n 9 -R 4 --method both

repetido com `/work/in/q7_n9_R4_M1285.txt`. Se `unshare --net` exigir privilégio no host, usar a variante de container abaixo (a rede fica desligada por `--network=none`). `-I` (modo isolado) ignora `PYTHON*` e o site do usuário e **não** põe o diretório do script nem o cwd em `sys.path`; ainda assim `in/` tem só os 3 arquivos, sem nada que sombreie `numpy`/`json`. `--as=4 GiB` é teto de espaço de endereço (numpy reserva mais virtual que RSS); o pico real esperado é < 300 MB.

Variante em container (mais forte; imagem sem rede, arquivos montados `:ro`):

    docker run --rm --network=none --read-only --cap-drop=ALL --security-opt=no-new-privileges \
      --user 65534:65534 --pids-limit 64 --memory 2g --memory-swap 2g --cpus 2 \
      -v "$WORK/in":/in:ro --tmpfs /tmp:size=16m \
      python:3.12-slim python3 -I -B /in/verify_cov.py /in/K7_9_4_M1475.txt -q 7 -n 9 -R 4 --method both

(a imagem precisa ter `numpy`; sem rede dentro do container, a imagem tem de ser construída/trazida antes, e o sha da imagem registrado. Sem numpy o script cai no `pure` automaticamente: mais lento, mas ainda correto.)

Limites recomendados: 2 GiB de RAM (estimativa de pico < 300 MB), 2 vCPU, `--cpu=300` s de CPU (o `pure` pode exigir mais: use 1200 s só se o `numpy` falhar), `--fsize=0` (nenhuma escrita), sem rede.

### O que seria executado e por que é (in)seguro

Seria executado: `verify_cov.py` (352 linhas, lidas inteiras acima), `numpy` já instalado, e os 9 caracteres × 1475 linhas do anexo como dado. Seguro porque: não há rede, escrita, subprocesso, `eval` ou desserialização no script; o dado só é interpretado como dígitos (parse linha 60-92, que rejeita qualquer caractere fora de base-36 e dígito ≥ q). Inseguro apenas pelo que não depende do script: a cadeia de suprimento do `numpy`/Python do host (mitigada por imagem fixada por sha e `-I`) e consumo de recursos (mitigado por `prlimit`/cgroup). O nosso `data/codes/q7_n9_R4_M1285.txt` é gerado por nós.

## 7. Veredito

**Executar sob autorização: SIM, risco baixo**, desde que (1) no sandbox acima, (2) após conferir os sha256 da seção 0, (3) com `--method both` (cruza `pure` × `numpy` dentro do próprio script, exit 3 se discordarem) e (4) registrando a saída como um quarto verificador **independente em algoritmo e autoria**, não como substituto dos três já registrados. Resultado esperado: `RESULT : VERIFIED -- K_7(9,4) <= 1475` para o anexo dele, e `<= 1285` para o nosso.

Riscos residuais: numpy do host; autoria declarada como gerada por modelo; contrato mais frouxo que o nosso (aceita duplicata, não impõe M); README do anexo com sintaxe de CLI errada (não afeta a verificação, só reprodução); a estimativa de tempo/memória é por contagem, não medida. Não executado nada nesta auditoria.
