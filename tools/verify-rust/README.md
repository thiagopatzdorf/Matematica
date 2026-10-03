# verify-rust: verificador de cobertura independente (Rust, só biblioteca padrão)

Segundo verificador, escrito sem consultar `tools/verify/verify.c`,
`tools/campaign/verify_cover_dilation.py` nem `scripts/codes/*.py`. Serve para
que um erro de autoria ou de lógica de um dos dois não passe sozinho.

## Uso

    cd tools/verify-rust && cargo build --release --offline
    target/release/verify-rust --q Q --n N --R R --M M <arquivo>

Os quatro parâmetros são obrigatórios; o nome do arquivo nunca é fonte de
parâmetro. Formato: uma palavra por linha, `n` dígitos `0..9`, `w = Σ s[k]·q^k`
(`docs/code-format.md`). CRLF final é tolerado.

## Contrato de exit codes

| exit | significado |
|---|---|
| 0 | exatamente M palavras distintas, todas válidas, e o código cobre Z_q^n com raio R |
| 1 | há palavra do espaço descoberta (imprime `first_uncovered=` e a contagem) |
| 2 | conteúdo contradiz os parâmetros: comprimento ≠ n, dígito ≥ q ou não decimal, duplicata, #palavras ≠ M |
| 3 | uso/operacional: arquivo ilegível, parâmetro ausente/inválido (q∉2..10, R>n, q^n > 2^33…) |

A checagem de conteúdo (2) vem antes da de cobertura (1).

## Algoritmo: dilatação por camadas

`S0` = código (um byte por ponto de Z_q^n). `S_{k+1} = D(S_k)`, com
`D(S) = ⋃_p L_p(S)` e `L_p(S) = {x : a reta de x na posição p encontra S}`.
Depois de R passos, `S_R` é a bola de raio R do código; conta-se os zeros.
`L_p` é feito por blocos contíguos (stride `q^p`): OR de q segmentos e réplica.
Não há laço espaço × código nem enumeração de bola por ponto.

Complexidade: tempo `O(R · n · q^n)` operações de byte (vetorizáveis), memória
`3 · q^n` bytes (atual, próximo, temporário), independente de M.

## Medidas reais (container de 4 vCPU, release, 1 thread)

q=7,n=9 (40 353 607 pontos): 1,6 a 2,1 s, ~121 MB. q=5,n=10 (9 765 625): 0,5 s,
~29 MB. O suite de 10 witnesses inteiro leva ~6 s. (A bola de raio 4 em q=7,n=9
tem 182 791 pontos; enumerá-la por ponto custaria ~7·10^12 operações, por isso
a dilatação.)

## Comando exato sobre os witnesses

    sh tools/verify-rust/run_all.sh

(lê q,n,R,M do nome de cada `data/codes/*.txt` NO SCRIPT e os passa
explicitamente; imprime exit e tempo; retorna 0 só se todos passam). Hoje há
10 witnesses em `data/codes`, todos exit 0. Testes:
`python3 -m unittest tests.test_verify_rust` (~10 s) e
`cd tools/verify-rust && cargo test --offline`.

## Declaração de independência

Li: `docs/code-format.md` e a especificação do pedido. Não li
`tools/verify/verify.c`, `tools/campaign/verify_cover_dilation.py` nem
`scripts/codes/*.py`. (Listei os nomes em `tools/` e `data/codes/`.)
O código K_2(6,1)=12 usado nos testes foi achado por busca local própria.
