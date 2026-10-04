# Avaliadores: a verificação como contrato único

> Cabe uma engine onde verificar é mais barato que gerar; o que decide é o avaliador, barato e exato.

Antes, "isto está verificado?" tinha cinco respostas espalhadas (o `verify.c`, scripts, testes do
ledger, frases do README). Agora tem uma: um **avaliador** devolve um `Resultado` em JSON, igual para
pessoa, agente, CI e para o MCP Infinito.

```
python3 -m evaluators                                   # lista os avaliadores
python3 -m evaluators covering_code data/codes/q5_n9_R4_M250.txt [--json] [--opt pontos=20]
python3 -m evaluators lean_honesty [CoveringLean]       # alvo padrão: CoveringLean/
python3 -m evaluators ponte_ledger [ledger/cells.json]  # alvo padrão: o ledger do repo
```

Código de saída: **0** passou; **1** reprovou; **2** não deu para avaliar (sem compilador C, alvo
ausente, uso errado). Roda da raiz do repo, só com Python 3 (stdlib) e, no `covering_code`, um
compilador C (`cc`, `gcc` ou `clang`; ou `EVALUATORS_VERIFY_BIN` apontando para um `verify` pronto).

## O contrato (`evaluators/base.py`)

| campo | significado |
|---|---|
| `avaliador`, `versao` | quem avaliou e em qual versão da regra |
| `ok` | passou? |
| `veredito` | uma linha de texto, a que se mostra a um humano |
| `evidencia` | dict com os números e achados que sustentam o veredito |
| `sha256_arquivo` | sha256 dos **bytes do arquivo** como está no disco (`null` se não há um arquivo) |
| `sha256_canonico` | sha256 do **conteúdo como conjunto de palavras** (`null` se não se aplica) |
| `tempo_s` | tempo de parede da avaliação |
| `comando_reproducao` | o comando que refaz exatamente esta avaliação |

`evidencia["erro"]` só existe quando o avaliador não conseguiu avaliar (saída 2): não é reprovação.
Avaliador novo é uma subclasse de `Avaliador` com `@registrar`; o CLI e o registro o acham sozinhos.

## Os dois sha256 (e por que o ledger "diverge" do verificador sem divergir)

* **`sha256_arquivo`**: `sha256` dos bytes do `.txt`. É o que o ledger guarda (`ours_lean.sha256`) e
  o que `sha256sum arquivo` mostra. Muda se a **ordem** das linhas mudar.
* **`sha256_canonico`**: o `sha256` das palavras **ordenadas por byte, unidas por LF, com LF final**
  (definição em `docs/code-format.md`; é o que o `tools/verify/verify.c` imprime e o que está nos
  cabeçalhos `C1_Data_*.lean`). **Não** depende da ordem das linhas: identifica o código, não o arquivo.

Exemplo real, `data/codes/q5_n9_R4_M250.txt` (o `K_5(9,4) ≤ 250`). As palavras estão na ordem de
geração, não ordenadas (`000000000`, `440401100`, `330302200`, ...), então:

```
sha256_arquivo   c605e57c41117da0141fdd88dc3972598fb4dd6e02bedc3edd477330f3bf5922   <- o do ledger
sha256_canonico  b818a971c86488280ed74c524398dae5561dd1e231de6d734b7206cbfd9a478c   <- o do verify
```

Os dois descrevem o mesmo código; não há divergência. Só coincidem quando o arquivo já está ordenado
(caso do `q7_n9_R4_M1134.txt` e do `q7_n8_R3_M1887.txt`). Para saber se **dois arquivos são o mesmo
código**, compare o canônico; para saber se **o arquivo foi alterado**, compare o do arquivo com o
ledger. O avaliador `ponte_ledger` faz a segunda conferência.

## `covering_code`

Compila `tools/verify/verify.c` num diretório temporário e roda o verificador exato (dígitos < q,
comprimento n, sem repetição, total = M do nome do arquivo, todo ponto de Z_q^n a distância ≤ R de
alguma palavra). Se não cobre, `evidencia.pontos_descobertos` lista até `pontos` (padrão 10) pontos
concretos fora de toda bola, e `evidencia.uncovered` o total. O verificador ganhou a opção `-u K`
para isso; sem `-u` a saída é idêntica à de antes (`check_all.sh` segue igual). Parâmetros fora do
padrão de nome: `--opt q=5 --opt n=7 --opt r=2 --opt m=499`.

## `lean_honesty`

Reprova uso **real** de `sorry` (e `sorryAx`), `native_decide` (e `decide +native`, `ofReduceBool`) ou
declaração `axiom` em `CoveringLean/**/*.lean`. Um léxico mínimo apaga comentários (`--`, `/- -/`
aninhado, docstrings `/-- -/` e `/-! -/`), strings (com escape e cruas), caracteres e `«ident»` antes
de procurar, porque os arquivos dizem "sem `sorry`, sem `native_decide`" **em comentário** e a busca
ingênua daria falso alarme. `evidencia.mencoes_so_em_comentario_ou_string` conta o que foi ignorado,
para o filtro ser auditável. **Limite:** é análise de texto; o `#print axioms` de cada teorema (só
`propext`, `Classical.choice`, `Quot.sound`) exige rodar `lake build` e não é checado aqui.

## `ponte_ledger`

Para cada célula `ours_lean` de `ledger/cells.json`: `M` do ledger == `M` do nome do arquivo em
`data/codes` == número de palavras do arquivo; q, n, R do nome == os da célula; sha256 do ledger ==
`sha256_arquivo` do disco; a declaração citada existe nos `.lean` (nome completo, com `namespace`);
e os números do nome da declaração (`K7_9_4_le_1134_syn`) batem com a célula e com M. Célula sem
arquivo em `data/codes` (K2(6,1), cujo código vive nos `G610_Chunk_*`) é listada em `puladas`.
Divergência é um **achado** em `evidencia.achados`; o avaliador nunca corrige número. Opções:
`--opt raiz=<dir>` (onde ficam `data/codes` e `CoveringLean`) e `--opt lean=<dir>`.

## Testes

`python3 -m pytest -q -p no:cacheprovider tests/test_evaluators.py` (cada avaliador tem teste que
falha sem ele; `ponte_ledger` é testado por mutação numa cópia em tmp).
