# Fase 1, subagente B: K_7(4,2) (2026-10-04)

**Resultado: K_7(4,2) = 19.** Antes: 17 ≤ K ≤ 19 (Rodemich 1970 / Kéri–Östergård 2005).
A cota superior 19 é a construção por partição 1+3+3 (já conferida no verificador oficial na
triagem). A inferior sai de duas inexistências, cada uma reduzida a CNFs com refutação LRAT
conferida por **dois verificadores independentes**:

| afirmação | perfis (CNFs) | resultado | provas |
|---|---|---|---|
| ∄ código de raio 2 em Z_7^4 com 17 palavras ⇒ K ≥ 18 | 15 | 15 UNSAT | 15/15 `lrat-check` VERIFIED, 15/15 `lrat.py` VERIFICADO |
| ∄ código com 18 palavras ⇒ **K ≥ 19** | 70 | 70 UNSAT | 70/70 `lrat-check` VERIFIED, 70/70 `lrat.py` VERIFICADO |

Status honesto: é um resultado **computacional com certificado** (LRAT conferido), mais um
argumento de redução escrito à mão (README de `tools/exatos/k742/`) e testado por máquina. Ainda
**não** é um teorema no Lean. O caminho até lá está no fim deste documento. Não mexi no ledger:
a decisão de registrar `ours_computational` (ou esperar o Lean) fica para quem revisa.

## Método (resumo; prova completa em `tools/exatos/k742/README.md`)

Reaproveita a ideia do Florath para `K_8(4,2) = 23` (arXiv:2606.09600; repo
`florath/covering-codes-lean`, commit `bbed9a6`): lema das fibras + projeções de pares + SAT com
LRAT. A divisão em perfis e a quebra de simetria são nossas, e ficaram muito mais simples que a
cadeia de lemas de grafos do Florath: aqui não precisei de nenhum argumento de grafo à mão.

1. **Lema das fibras.** Uma fibra (coordenada j, símbolo a) com s palavras força
   `K_{7−s}(3,1) ≤ M − s`. Com cotas **elementares** (Lema 0 do README: `K_6(3,1) ≥ 18`,
   `K_7(3,1) ≥ 21`), para M ≤ 18 toda fibra tem ≥ 2 palavras.
2. **Perfis.** Por coordenada, os 7 tamanhos de fibra somam M e são ≥ 2: M = 17 tem 3 tipos e 15
   perfis; M = 18 tem 5 tipos e 70 perfis.
3. **CNF por perfil.** Coordenada 0 constante (blocos), fibras exatas por contador sequencial,
   projeções de pares exatas, uma cláusula de cobertura por ponto de Z_7^4 (2401), e quebra de
   simetria (ordem dentro de bloco + precedência de símbolos de mesma fibra). ~4,7 mil variáveis
   e ~20 mil cláusulas por perfil.
4. **Completude.** Todo código cai em algum perfil e satisfaz a CNF dele depois de uma isometria
   e de uma reordenação das palavras (prova no README, implementada em `canonizar.py`).

## Validações da fase 0 (todas antes de afirmar K_7)

| caso | o que se espera | o que saiu |
|---|---|---|
| K_4(4,2) = 7: ∄ 6 | todos UNSAT | 5/5 UNSAT, LRAT conferido (certificados no repo, conferidos de novo no pytest pelo `lrat.py`) |
| K_4(4,2) = 7: existe 7 | algum perfil SAT | 5 de 15 perfis SAT; os códigos cobrem |
| K_5(4,2) = 11: ∄ 10 | todos UNSAT | 210/210 UNSAT, LRAT conferido (10,6 s de solver) |
| K_6(4,2) = 15: ∄ 14 | todos UNSAT | 8855/8855 UNSAT, LRAT conferido (2080 s de solver, 7,5 GB de prova conferida e descartada; `certificados/K6_4_2_M14.jsonl.gz`) |
| K_8(4,2) = 23 (Florath): ∄ 22 | todos UNSAT | **1001/1001 UNSAT, LRAT conferido** na VM `exb-2` (5552 s de solver, maior perfil 14 s; 55,5 GB de prova conferida e descartada). JSONL no bucket (`exatos/k742/K8_4_2_M22.jsonl`, sha256 `219505950c95…`). Reproduz o resultado do Florath com o mesmo pipeline |
| SAT no perfil do código da partição, q = 4, 5, 6, 7 (M = 7, 11, 15, 19) | SAT, código que cobre | 4/4 SAT; o kissat devolve um código e ele cobre Z_q^4 inteiro |
| controle sem a quebra de simetria (d)–(f) | o mesmo UNSAT | M = 17: perfis 0, 5, 10, 14 UNSAT (6–92 s). **M = 18: 70/70 UNSAT** com kissat (3529 s de parede somados, maior 1011 s): o resultado não depende da parte mais delicada da quebra de simetria |

Testes (`tests/test_k742.py`, ~7 s, sem solver externo):

- códigos de cobertura conhecidos (partição, q = 4, 5, 7), embaralhados por elementos aleatórios
  de S_q ≀ S_4 e com as palavras em ordem aleatória, levados à forma normal: a atribuição
  satisfaz **todas** as cláusulas da CNF do seu perfil;
- listas aleatórias de 17 e 18 palavras com fibras ≥ 2 (que não cobrem): só falham cláusulas de
  cobertura, e **exatamente uma por ponto descoberto** (a cobertura está codificada de forma
  exata, nos dois sentidos);
- mutação: apertar a quebra de simetria (precedência entre símbolos de fibras diferentes) faz 8
  testes falharem — os testes enxergam uma quebra de simetria errada;
- os dois verificadores LRAT recusam prova adulterada (dica trocada numa linha);
- a CNF guardada (K_4) e o sha256 das CNFs de K_7 são exatamente o que o codificador gera hoje.

## Números de K_7(4,2)

Medidos com CaDiCaL 3.0.1 (`c607304`) `--lrat`, `lrat-check` do drat-trim (`2e3b2dc`) e o
verificador Python `tools/exatos/k742/lrat.py`. kissat 4.0.4 (`8af8e56`) só como segunda
opinião, sem prova.

| M | perfis | CaDiCaL (soma, 1 núcleo) | maior perfil | `lrat-check` (soma) | LRAT (texto) | kissat (soma) |
|---|---|---|---|---|---|---|
| 17 | 15 | 107 s (container) | 18 s | 17 s | 0,57 GB | — |
| 18 | 70 | 1011 s (container, 6 processos em 4 núcleos) | 33 s (VM) | 148 s | 3,0 GB | 961 s, 70/70 UNSAT |

**Reprodutibilidade:** M = 17 e M = 18 rodaram no container e na VM `exb-1`; as CNFs **e as
provas LRAT saíram bit a bit iguais** (mesmo sha256; conferido nos 15 perfis de M = 17 e numa
amostra de 4 perfis de M = 18, inclusive os dois maiores): o codificador e o CaDiCaL são
determinísticos.

**Certificados:** CNF e LRAT comprimidos (gzip) dos 85 perfis, mais os JSONL, no bucket privado
`gs://factory-literatura-matematica/exatos/k742/` (175 objetos, 758 MB; tamanhos conferidos
contra a cópia local depois do upload). O sha256 de cada CNF e de cada LRAT descomprimidos está
em `tools/exatos/k742/certificados/K7_4_2_M17.jsonl` e `K7_4_2_M18.jsonl` (o `.gz` carrega nome e data no cabeçalho, então o hash que vale é o
do arquivo descomprimido).

## Custo

| VM | tipo | uso | tempo | custo |
|---|---|---|---|---|
| exb-1 | t2d-standard-8 spot | K_7 M = 17 e 18 com prova + `lrat.py` nos 85 | ~13 min | ~US$ 0,04 |
| exb-2 | t2d-standard-8 spot | validação K_8(4,2) M = 22 (1001 perfis) | ~17 min | ~US$ 0,05 |

A tabela de preço do `lote-gcp.py` diz US$ 0,177/h para a t2d-standard-8 spot (a triagem
estimava 0,10). Discos pd-standard de 30 e 20 GB por minutos: centavos. Total ≈ US$ 0,10 do orçamento de US$ 8. O container local fez a fase 0 inteira.

## Caminho para o Lean

> **Atualização:** o estado atual (o que já é teorema, o verificador LRAT no kernel, números e
> custo do que falta) está em `docs/exatos/LEAN_K742.md`. O texto abaixo é o plano original.

O Florath já mostrou o caminho: `OctonaryFourTwoBlockLRAT.lean` lê CNF + LRAT com
`include_str`, monta a fórmula reflexiva e checa a refutação no kernel
(`Mathlib.Tactic.Sat.FromLRAT`). Para K_7(4,2) ≥ 19 falta:

1. **Lema das fibras e Lema 0 no Lean** — análogos diretos de
   `octonaryFourRadiusTwo_symbol_fiber_card_ge_two_of_card_le_twenty_two` e do `SparseSlicer`.
2. **Ponte código → CNF**: formalizar a forma normal (o `canonizar.py`) e que ela satisfaz a CNF
   do perfil. É a parte mais trabalhosa; a alternativa é imitar o Florath e provar no Lean só a
   ponte para um "grafo de perfil" mais fraco.
3. **Tamanho das provas.** 3,6 GB de LRAT em texto é demais para `include_str` + kernel. Antes
   de levar ao Lean: aparar (`drat-trim -L`), procurar uma quebra de simetria mais forte, e
   dividir os perfis grandes (55 com 296 MB, 25 com 221 MB) em cubos. O Florath levou ao Lean 4
   arquivos LRAT pequenos, não 85 grandes.

## Decisões tomadas sozinho

- Fui além de M = 17: como as 15 instâncias de M = 17 fecharam em 2 minutos de CPU, rodei as 70
  de M = 18 (16 min de kissat, 6 min de CaDiCaL), dentro do orçamento e do pedido ("se sobrar
  orçamento, tentar 18").
- O lema das fibras para K_7 usa só cotas elementares (Lema 0), para a prova não depender de
  `K_6(3,1) = 18` e `K_7(3,1) = 25` da literatura; a validação em K_8 usa `K_7(3,1) = 25`, como
  o Florath.
- Provas da validação K_8 (1001 perfis) e K_6 (8855 perfis) foram conferidas e **descartadas**
  (`--descartar`): guardar ~19 GB de prova de um resultado já provado por outro não compensa. O
  JSONL guarda tamanho e sha256 de cada uma.
- Os certificados de K_7 foram gerados na VM e subidos a partir da factory-01 (cópia por scp na
  rede interna); o token ficou em memória no `subir.py` e nunca foi impresso.
- Não atualizei `ledger/ours.json`: o resultado é computacional e o ledger tem campo para isso,
  mas o registro deve passar por revisão.

## Falhas e limites

- O primeiro script das VMs falhou em silêncio (`apt-get install` sem `apt-get update`; sem
  `set -e` o script seguiu e o `rodar.py` quebrou por falta do binário). Consertado com
  `set -e` + `apt-get update`; custou ~5 min de VM.
- Uma rodada local de M = 19 sem perceber que o lema das fibras cai para ≥ 1 em M = 19
  (814 385 perfis) foi interrompida; para validar o lado SAT rodei só o perfil do código da
  partição.
