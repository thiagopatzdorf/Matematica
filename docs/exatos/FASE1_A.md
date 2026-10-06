# Fase 0 e fase 1 (subagente A): motor sem isomorfos, K4(7,4) e K3(7,3)

Data: 2026-10-04. Código: `tools/exatos/motor/` (algoritmo, provas das podas e reprodução no
`README.md` de lá). Testes: `tests/test_motor_exatos.py`.

## Resposta curta

- **O motor está pronto e confere.** Busca em largura com formas canônicas do nauty nos primeiros
  níveis e DFS com proibição dos irmãos no fundo, com quatro podas provadas e um "corte por ordem"
  entre representantes. Ele reproduz o número de códigos ótimos inequivalentes das tabelas do
  Kéri em 20 células, inclusive K4(4,3) = 79 classes, K4(5,4) = 269, K4(6,5) = 839 e K5(4,3) = 471.
  A soma das órbitas `Σ |G|/|Aut(C)|` bate com a contagem rotulada sem simetria em 10 células
  (ex.: K4(4,3): 58 247 680 nos dois lados). Também reproduz **K2(8,2) ≥ 12**, **K5(4,2) ≥ 11** (ambas em duas execuções com
  árvores diferentes) e **K3(5,1) ≥ 27** (5,05·10^9 nós, 5,2 CPU-h na nuvem). Ver as seções "Validação" e "Reproduções".
- **Fase 1: parei, como a regra mandava.** A árvore real ficou muito mais de 100× acima da
  estimativa ideal da triagem nas duas células:
  - **K4(7,4), M = 9:** melhor configuração medida, 7,1·10^18 nós no fundo (Knuth), contra o
    ideal de 4·10^7, ou seja, cerca de 2·10^11×.
  - **K3(7,3), M = 11:** 8·10^12 a 5,5·10^13 nós, contra 4·10^8, ou seja, 2·10^4× a 10^5×.

  Projeção de custo para K3(7,3) M = 11: cerca de 10^13 nós × 75–100 µs ≈ 2–3·10^5 CPU-h, ou
  US$ 2,5 mil a 3,5 mil em spot. É duas ordens acima do orçamento de US$ 12, então **nenhuma
  computação da fase 1 foi feita na nuvem**. As duas células seguem abertas: não existe resultado
  de inexistência nem de existência.
- **Achado no ledger:** o campo `published.sources.keri_2011.n_optimal` está truncado quando o
  valor tem um dígito e o expoente tem vários. A tabela do Kéri diz K4(4,3) = 4^79, e o ledger
  guarda 7. O mesmo acontece com K4(3,2) (21 → 2), K4(5,4) (269 → 2), K4(6,5) (839 → 8), K5(3,2)
  (54 → 5) e K5(4,3) (471 → 4). O motor dá os valores da tabela. Não mexi no ledger, que é gerado:
  fica registrado aqui e no relatório.
- **Achado de método:** a estimativa ideal da triagem ("nós de Knuth da DFS ingênua / |G|") fica
  10^4 a 10^10 vezes abaixo do que este motor consegue, **inclusive nos casos já resolvidos da
  literatura**. Então ela não serve como previsão de custo (seção "Por que a árvore real é tão
  maior").

## Validação (fase 0)

Tudo roda no `pytest` (`python3 -m pytest -q tests/test_motor_exatos.py`: 66 testes, cerca de
1 min neste container de 4 núcleos dividido com outro subagente).

| verificação | o que confere | resultado |
|---|---|---|
| classificação × Kéri | nº de códigos ótimos inequivalentes = expoente da tabela (17 células no teste, mais K4(5,4), K4(6,5) e K5(4,3) rodadas à mão) | 20/20 batem (ex.: K2(8,3) 6, K3(6,4) 7, K4(4,3) 79, K5(3,2) 54, K4(5,4) 269, K4(6,5) 839, K5(4,3) 471) |
| órbitas × contagem rotulada | `Σ_C \|G\|/\|Aut(C)\|` (formas canônicas + estabilizador do nauty) = nº de códigos rotulados achados pela DFS sem simetria | 10/10 (K2(4,1) 40, K2(5,1) 320, K2(6,1) 2 240, K2(6,2) 1 456, K2(7,1) 240, K2(7,2) 71 680, K3(3,1) 54, K3(4,1) 72, K4(3,1) 432, K4(4,3) 58 247 680) |
| existência/inexistência | M = K existe e M = K − 1 não, em 8 células, com 4 variantes (D = 2; D = 3 com corte; ordem invertida no topo; sem a poda dual) | 64/64 |
| diferencial | mesma resposta do `dfs_cover.c` (implementação independente, sem nauty) | 5/5 |
| métodos de ganho | Walsh–Hadamard, acumulação e popcount geram a mesma árvore (mesmo nº de nós) | 2/2 |
| execução em partes | `--parte i/3` soma os mesmos nós e representantes da execução inteira | ok |
| código achado | sai no formato do `tools/verify/verify` e passa nele (`uncovered=0`) | ok |

O teste da classificação foi o que achou o defeito do ledger: a primeira versão comparava com o
campo do ledger e falhou em K4(4,3) (79 contra 7). A contagem rotulada (58 247 680 > 7·|G| =
55 738 368) mostra que 7 classes é impossível, e a tabela do Kéri diz 79.

## Reproduções de valores conhecidos

"D" é o último nível com formas canônicas; "corte" é o tamanho máximo de conjunto em que o corte
por ordem é testado. Tempos medidos neste container (4 núcleos divididos com o subagente B).
"Ideal" é a coluna "nós / |Aut|" da triagem.

| instância (∄ M) | configuração | resultado | nós do fundo | formas canônicas | tempo | ideal (triagem) |
|---|---|---|---|---|---|---|
| K2(6,1), 11 | D 3, corte 6 | NAO_EXISTE | 933 | 3 596 | 0,08 s | — |
| K2(7,2), 6 | D 3, corte 6 | NAO_EXISTE | 164 | 973 | 0,02 s | — |
| K3(5,2), 7 | D 3, corte 6 | NAO_EXISTE | 14 953 | 68 011 | 0,97 s | — |
| K4(4,2), 6 | D 3, corte 6 | NAO_EXISTE | 72 262 | 757 686 | 10,5 s | — |
| K3(6,3), 5 | D 3, corte 6 | NAO_EXISTE | 243 934 | 1 768 775 | 31 s | — |
| **K2(8,2), 11** | D 5, corte 7 | **NAO_EXISTE** | 18 524 245 | 3 299 981 | 121 s | 2·10^3 |
| **K2(8,2), 11** (2ª execução) | D 4, corte 7, ordem invertida | **NAO_EXISTE** | 24 042 821 | 7 987 126 | 177 s | |
| **K5(4,2), 10** | D 6, corte 8 (nuvem, 8 partes) | **NAO_EXISTE** | 95 616 817 | ≈ 2,2·10^8 | 146 s por parte (0,3 CPU-h) | 7·10^2 |
| **K5(4,2), 10** (2ª execução) | D 6, corte 8, ordem invertida (82 910 representantes) | **NAO_EXISTE** | 119 329 552 | ≈ 4,3·10^8 | 288 s por parte | |
| **K3(5,1), 26** | D 8 (102 202 representantes), sem corte (nuvem, 8 partes) | **NAO_EXISTE** | 5 054 727 440 | 132 276 | 2 310–2 480 s por parte (5,2 CPU-h) | — |

Estimadas (Knuth, sem rodar até o fim):

| instância (∄ M) | configuração | nós do fundo (Knuth) | ideal (triagem) | razão |
|---|---|---|---|---|
| K2(10,3), 11 | D 5, corte 7 | 4,8·10^12 | 2·10^6 | 2·10^6 |
| K3(7,3), 10 | D 5, corte 8 | 4,4·10^10 | 1·10^6 | 4·10^4 |
| K4(7,4), 8 | D 4, corte 6 | 2,7·10^14 | 3·10^4 | 9·10^9 |
| K6(4,2), 14 | D 4, corte 7 | 6,2·10^13 | — | — |

Ou seja: o motor reproduz K2(8,2) ≥ 12, K5(4,2) = 11 (∄ 10) e K3(5,1) = 27 (∄ 26, o football
pool de Kamps–van Lint) e as células pequenas. K2(8,2) e K5(4,2) foram conferidas por uma
segunda execução com outra árvore (ordem invertida no topo, outro nível D); K3(5,1) rodou uma vez
só. Mas o motor **não** reproduz localmente
K3(7,3) ≥ 11 (≈ 900 CPU-h), K4(7,4) ≥ 9, K2(10,3) ≥ 12 nem K6(4,2) = 15. Os autores dessas
cotas usaram argumentos estruturais (fibras, códigos encurtados, matrizes de partição) além da
busca.

Os certificados das duas execuções de K2(8,2) estão em `docs/exatos/certificados/`: uma linha
por representante do nível D (índice, palavras, nós do fundo), mais a linha `FIM`. Das execuções
na nuvem ficou o resumo (`NUVEM_exa-1_resumo.txt`: sha256 e linha `FIM` de cada parte, mais o
comando para refazer). Os certificados completos por representante (102 202 linhas para
K3(5,1)) não foram copiados antes de a VM ser destruída. Foi um erro meu; eles são
reexecutáveis com o comando do resumo.

## Fase 1: as medições que decidiram parar

**K3(7,3), M = 11** (|G| = 6^7·7! = 1,41·10^9; |B| = 379):

| configuração | representantes do nível D | nós do fundo (Knuth) |
|---|---|---|
| D 4, sem corte | 1 413 | 2,3·10^16 |
| D 5, sem corte | 127 113 | 1,1·10^16 |
| D 5, corte 7 / 8 / 9 (sem poda dual) | 127 113 | 3,0·10^13 / 1,3·10^13 / 8,5·10^12 (200–300 sondas) |
| D 5, corte 9, com poda dual | 127 113 | 5,5·10^13 (1 500 sondas) |
| D 6, corte 9 | 17 793 735 (topo: 48,7 M formas canônicas, 490 s) | 7,9·10^12 (300 sondas) |

Custo por nó medido: cerca de 75 µs (sem corte) e 100 µs (corte 8). O estimador de Knuth tem
cauda pesada: com mais sondas a estimativa sobe (8,5·10^12 com 200, 5,5·10^13 com 1 500), então
os números acima são piso, não teto.

**K4(7,4), M = 9** (|G| = 24^7·7! = 2,31·10^13; |B| = 3 991):

| configuração | representantes do nível D | nós do fundo (Knuth) |
|---|---|---|
| D 3, sem corte | 75 | 4,1·10^21 |
| D 5, sem corte | 1 458 753 (topo: 19,2 M formas canônicas, 218 s) | 3,7·10^19 |
| D 4, corte 6, com poda dual | 4 731 | 7,1·10^18 |

**Tentativa de fundo por SAT** (o caminho usado pelo Florath no K8(4,2)): CaDiCaL 1.9.5 via
PySAT, com a cobertura dos pontos descobertos e "no máximo M − D palavras" (contador
sequencial), num representante aleatório do nível 6 de K3(7,3) M = 11. Não resolveu em 100 s.
A DFS gasta cerca de 45 s por representante desse nível (8·10^12 nós / 1,78·10^7
representantes × 100 µs). Sem a redução estrutural, o SAT direto não ganha da DFS.

## Por que a árvore real é tão maior que a "ideal"

1. A estimativa da triagem divide os nós da DFS **com proibição dos irmãos** por |G|. Mas a
   proibição já elimina boa parte da mesma redundância que a simetria eliminaria: cada conjunto
   rotulado aparece uma vez na DFS. As duas reduções se sobrepõem em vez de se multiplicar. Nos
   casos pequenos a "ideal" dá menos de 1 nó (K4(4,2), M = 6: 0,07), o que já mostra que ela não
   é uma cota alcançável.
2. A simetria se esgota cedo. O estabilizador fica trivial depois de 4 a 5 palavras. Daí para
   baixo, cada representante é um problema sem simetria, com 5 ou 6 palavras livres e poda fraca:
   em K3(7,3), 11·379 = 4 169 pontos de bola para 2 187 pontos, quase 2× de folga. Passar o topo
   de D = 5 para D = 6 multiplicou os representantes por 140 e quase não mudou o fundo.
3. O corte por ordem recupera parte do que a busca em largura perde ao zerar as proibições:
   ×10 a ×1 000 nas medições. Mas ele custa formas canônicas por nó, e acima do conjunto de
   tamanho 9 o custo passa o ganho.

Regra para a próxima triagem: **estimar com o motor real (Knuth sobre o fundo a partir dos
representantes), nunca com nós/|G|**. O motor faz isso em segundos (`--estimar`).

## O que faltaria para fechar K3(7,3) e K4(7,4)

Em ordem de chance, todos com trabalho de teoria antes de CPU:

- **Restrição por fibras** (o passo do Florath em K8(4,2) e o lema das fibras da triagem): as
  palavras com `x_j = a` cobrem o subespaço `x_j = a` com raio R, e as outras com raio R − 1.
  Para K3(7,3) M = 11, `K_3(6,2) ≥ 15 > 11` dá direto que **toda fibra tem ≥ 1 palavra**. Provar
  ≥ 2 (cobertura mista de F_3^6 com 1 bola de raio 3 e 10 de raio 2) restringiria cada coordenada a
  distribuições com todo símbolo ≥ 2, uma poda forte nos níveis profundos.
- **Classificação por metades** (Kéri–Östergård): classificar primeiro os subcódigos encurtados
  possíveis (tamanho ≤ ⌊M/q⌋ numa coordenada) e só depois colar.
- **Cota de LP verdadeira nos nós profundos** (a poda iv é só uma solução dual viável barata).

## Caminho para o Lean (quando houver uma inexistência nova)

O motor não emite prova. Para certificar um `NAO_EXISTE`, há dois caminhos com base no que este
repo já tem:

1. **Folhas `decide +kernel` sobre os ramos.** O certificado lista os representantes do nível D.
   Seria preciso (a) provar em Lean que a lista é completa a menos de isometria (a cadeia de
   formas canônicas: cada filho gerado é levado a um representante por uma isometria explícita,
   que o motor teria de gravar), e (b) para cada representante, refutar a completação com um
   `chkN` generalizado para (q, R), que hoje só cobre q = 2 e R = 1.
2. **LRAT.** Cada representante vira uma CNF (cobertura + cardinalidade, como em
   `sat_rep.py` da medição acima) refutada por CaDiCaL com prova LRAT, conferida por
   `cake_lpr` ou pelo verificador LRAT do Lean, como o Florath fez no K8(4,2). A completude da
   lista de representantes continua precisando do item (a).

Nas reproduções acima isso não foi feito: elas são evidência computacional e validação do
motor, não teoremas novos.

## Custo e máquinas

- Fase 0: CPU local, cerca de 5 CPU-h neste container (dividido com o subagente B).
- Nuvem: uma VM spot `exa-1` (t2d-standard-8, US$ 0,177/h, teto de 3 h), só para as
  reproduções da fase 0 (K3(5,1) e as duas execuções de K5(4,2)). Ficou ligada cerca de 0,95 h,
  ou cerca de 7,6 CPU-h, a **≈ US$ 0,17** (o disco pd-standard de 20 GB custa menos de US$ 0,01). Foi
  destruída com `lote-gcp.py --destruir exa-1 --confirmar` e conferida com `gcp_vm listar`.
- Fase 1 nas células-alvo: US$ 0 (parada pela regra dos 100×).

## Decisões tomadas sozinho

- Interpretei a regra "> 100× o ideal ⇒ pare" por célula. As duas estouraram, então a fase 1
  parou inteira, sem gasto.
- Usei a nuvem (≈ US$ 0,17; o teto da VM era US$ 0,53) para **reproduções** da fase 0 (K3(5,1) ≥ 27 e
  K5(4,2) ≥ 11), não para as células-alvo, porque localmente levariam de 6 a 10 h divididas com o
  subagente B.
- Mudei o workflow `verify-codes.yml` para instalar `libnauty-dev`. No CI, a falta de nauty faz
  os testes do motor falharem em vez de pularem.
- Não corrigi o `n_optimal` do ledger (é gerado; a correção é no parser das tabelas do Kéri).
  Os testes usam os valores lidos da tabela, com comentário.
- A poda (ii) no topo só roda quando faltam ≤ 3 palavras: mais cedo ela custa mais do que corta, e
  desligá-la nunca muda a resposta.
