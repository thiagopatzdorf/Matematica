# Red team: K_7(6,4) = 14 (e K_7(5,3) ≥ 16) (2026-10-05)

Revisão adversarial da afirmação de `docs/exatos/FIBRAS_GERAL.md` e de `tools/exatos/fibras/`
(PR #56, branch `feat/exatos-fibras`). **Commit auditado: `58d99938a95b701b50c736afad7054db9fce0a07`**
(o autor ainda pode empurrar; nada depois desse sha foi olhado). O objetivo era **quebrar** a
prova. Padrão de rigor: `REDTEAM_K742.md`. Scripts desta revisão: `tools/exatos/fibras_redteam/`
(os independentes não importam nada de `tools/exatos/fibras`; os que testam o codificador o
carregam de um diretório dado, para apontar para o commit auditado e para mutantes). Testes:
`tests/test_fibras_redteam.py`.

**Veredito: sobrevive com ressalva.** A afirmação K_7(6,4) = 14 se sustenta em tudo o que medi:
a cota superior é real, a lista de perfis está completa, os certificados correspondem ao
codificador auditado e reconferem com dois verificadores, a codificação independente concorda
em toda a amostra e nenhum código real ou aleatório foi perdido pela quebra de simetria. **Mas a
prova escrita do Lema 4 (quebra (h), uma das duas novas) está errada**, e o canonizador
`fib_canon.canonizar`, que o doc apresenta como a prova construtiva e que os testes do PR usam
como garantia, **produz formas normais que violam (h)**, inclusive na própria célula K_7(6,4),
M = 13. O enunciado de (h) continua verdadeiro: dou abaixo uma prova corrigida e um canonizador
corrigido, e a órbita por SAT (sem canonizador nenhum) nunca ficou UNSAT. Ou seja, os 8008
certificados valem, mas o argumento que liga "todos os perfis UNSAT" a "não existe código" tinha
um buraco que precisa ser fechado no doc e no código antes de chamar isto de teorema.

## 0. Cota superior K_7(6,4) ≤ 14

| conferência | resultado |
|---|---|
| `cota_superior.py` (numpy, lê o arquivo, nada do repo) em `data/codes/q7_n6_R4_M14.txt` do commit auditado | 14 palavras distintas, 117 649 pontos, **0 descobertos**; cada ponto é coberto por 1 a 6 palavras |
| `tools/verify/verify` compilado do `main` e do commit auditado (`-q 7 -n 6 -r 4 -m 14`) | `uncovered=0`, sha256 canônico `9f2c5351…6d62` nos dois |
| controle: uma palavra trocada por `000001` | o verificador próprio acusa pontos descobertos (teste) |
| literatura e ledger | `ledger/cells.json` K7(6,4): lb 13, ub 15 (Kéri 2011, chaves k/n); `literatura_pos_keri` 13–15 (Haas–Schlage-Puchta–Quistorff 2008/9, Kéri–Östergård 2005); `marosi_2026` e `gijswijt_polak_2025` sem entrada. O melhor publicado era **15**: o código de 14 melhora a cota superior |

## 1. A prova escrita, linha a linha (ataque 1)

| peça | conferido | resultado |
|---|---|---|
| Lema 1 (fibras, geral) | \|A_i\| ≤ s deixa q − s símbolos fora de A_i; palavra de F concorda com x ∈ B só na coordenada j, distância n − 1 > R; quem cobre x tem c_j ≠ a e d' ≤ R − 1; φ_i fixa S_i, então não perde concordância; a imagem é código de raio R − 1 em Z_{q−s}^{n−1} com ≤ M − s palavras. Também para s = 0 (B = hiperplano inteiro) e para multiconjuntos | **correto** |
| s_min = 1 em K_7(6,4), M = 13 | s = 0 exige K_7(5,3) ≤ 13; a cota inferior publicada é 15 (o próprio PR prova 16). s = 1 não é excluído (K_6(5,3) = 12 ≤ 12) | correto; só precisa de **K_7(5,3) ≥ 14** |
| s_min = 2 em K_7(5,3), M = 15 | s = 0 exige K_7(4,2) ≤ 15 (falso: K_7(4,2) = 19, no Lean desde v0.8.0; Rodemich 17 basta); s = 1 exige K_6(4,2) ≤ 14 (falso: K_6(4,2) = 15, Kéri 2011 e 8855 perfis LRAT do k742) | correto; 7 · 2 = 14 ≤ 15 deixa um tipo só, 3222222 |
| redução a M = 13 exatas | código com menos palavras completa-se com repetições; o Lema 1 e a CNF aceitam multiconjunto (nada proíbe palavras iguais) | correto |
| Lema 2 (R = n − 2 ⇔ concordar em ≥ 2 coordenadas; P_ij por equivalência) | releitura do `codificar`: P ↔ OU dos y, y ↔ x ∧ x; uma cláusula por ponto | correto |
| contador `exatamente` | o mesmo do k742 (conferido em `REDTEAM_K742.md`) | correto |
| (a)–(f) | o argumento do k742 vale palavra por palavra com "classe" no lugar de "classe de fibra" (k = n aqui, então não há coordenada livre) | correto |
| (g) colunas ≥ 2 de mesmo tipo em ordem lexicográfica | depois de (f) a ordem das palavras está fixa; trocar duas colunas ≥ 2 de mesmo tipo não muda as colunas 0 e 1, nem a ordem, nem as fibras, e leva coluna relabelada por primeira aparição em coluna relabelada; ordenar o grupo não desfaz (f) | **correto** |
| **(h) Lema 4** | ver 1.1 | **prova errada, enunciado verdadeiro** |

### 1.1 O defeito na prova do Lema 4

A prova escolhe, a cada passo, o bloco cujo "vetor ordenado dos rótulos que a coordenada 1 teria
se ele viesse agora" é o menor, e os rótulos hipotéticos dos símbolos novos são dados **na ordem
do índice do símbolo** (`rotulos_se_agora` em `fib_canon.py`). Depois afirma: "o vetor ordenado
de Y domina, componente a componente, o vetor u". Isso é falso quando os símbolos novos do bloco
têm multiplicidades diferentes.

Contraexemplo (`contraexemplo_h.py`, testado): Z_4^3, 10 palavras, coordenada 0 do tipo 3322,
coordenada 1 do tipo 3331 (os símbolos 0, 1, 2 formam uma classe). Os dois blocos de tamanho 3
são X = {1, 2, 2} e Y = {0, 1, 1} na coordenada 1. No passo 0 os dois têm vetor (0, 1, 1) (X: 1→0,
2→1; Y: 0→0, 1→1) e o desempate escolhe X. Aí o símbolo 1 fica com o rótulo 0, e Y passa a ter
vetor (0, 0, 2) < (0, 1, 1): **(h) violada**. A forma normal que `fib_canon.canonizar` devolve é

    000 010 010 101 101 121 212 222 322 333     (bloco 0 = 011, bloco 1 = 002)

e a CNF do perfil, lida com essa atribuição, tem uma cláusula (h) falsa. O passo errado: u deu o
menor rótulo ao símbolo de multiplicidade 1; depois o rótulo foi para o símbolo de
multiplicidade 2, e trocar rótulos entre símbolos de multiplicidades diferentes **não** preserva
dominância do vetor ordenado.

**Não é caso de laboratório.** Em códigos aleatórios com fibras de perfil (`massa_predicados.py`,
predicados (a)–(h) escritos à parte em `predicados.py`), a forma normal do repo viola (h) em:

| célula | códigos | forma do repo viola (h) | forma corrigida viola algo |
|---|---|---|---|
| K_4(3,1), M = 10 | 100 000 | 103 | 0 |
| K_4(4,2), M = 10 | 100 000 | 81 | 0 |
| K_5(4,2), M = 11 | 100 000 | 54 | 0 |
| K_7(4,2), M = 18 | 100 000 | 39 | 0 |
| K_7(5,3), M = 16 | 100 000 | 62 | 0 |
| **K_7(6,4), M = 13** (ordem min, a dos certificados) | 300 000 | **3** | 0 |
| K_7(6,4), M = 13, `--ordem max` | 300 000 | 285 | 0 |
| K_7(6,4), M = 14 | 100 000 | 27 | 0 |
| K_7(5,3), M = 15 (o perfil único 3222222^5) | 100 000 | 0 | 0 |

(mais 20 000 por célula numa primeira rodada, com os mesmos sinais; K_5(5,3), M = 9 e K_6(5,3),
M = 12 deram 0 nas duas formas.) Os testes do PR (`test_codigo_embaralhado_satisfaz_a_cnf_da_sua_instancia`,
21 códigos gulosos) não pegaram porque a taxa é de 10⁻⁵ a 10⁻³.

### 1.2 O enunciado continua verdadeiro: prova corrigida

Troque o guloso por: a cada passo, escolher o par (bloco, rotulação admissível por (e)) de **menor**
vetor. As rotulações admissíveis no passo t são exatamente as bijeções entre os símbolos novos
de cada classe c e os m_c primeiros rótulos livres F_t ∩ c; a menor é dar o menor rótulo ao
símbolo mais frequente no bloco (troca de dois rótulos l₁ < l₂ com mult(l₁) < mult(l₂) baixa o
vetor). Seja min_t(Y) o menor vetor de Y no passo t e v_t = min sobre os blocos restantes.

*Monotonia.* Seja Y escolhido no passo t + 1 com a rotulação L'. Os símbolos de Y que eram novos
no passo t receberam (no passo t, por X, ou no t + 1) rótulos distintos de F_t ∩ c. Ordene esses
símbolos por L' e dê a eles, nessa ordem, os m_c primeiros de F_t ∩ c: obtém-se uma rotulação L
admissível no passo t com L(s) ≤ L'(s) **símbolo a símbolo** (o i-ésimo menor de m elementos
distintos de F_t ∩ c é ≥ o i-ésimo elemento de F_t ∩ c). Desigualdade ponto a ponto passa para o
vetor ordenado com multiplicidades, componente a componente. Logo
v_{t+1} = vet(Y, L') ≥ vet(Y, L) ≥ min_t(Y) ≥ v_t. Os rótulos dados são os de (e) (cada passo
gasta os próximos livres da classe), (d) é ordenar dentro do bloco, e (f), (g) se refazem sem
mexer nas coordenadas 0 e 1. ∎

O ponto que faltava na prova original é comparar com o **mínimo** sobre rotulações, não com uma
rotulação fixa. `canon_corrigido.py` implementa esse guloso, escrito do zero.

### 1.3 Testes de completude (a)–(h) contra a CNF auditada

Três medidas por código, todas contra a CNF de `fib_encode.codificar` do commit auditado:
**repo** (a forma de `fib_canon` satisfaz?), **corr** (a forma de `canon_corrigido` satisfaz?),
**órbita** (SAT: CNF do perfil + variáveis de grupo — permutação de palavras, de coordenadas
compatíveis com o perfil e de símbolos por coordenada — sem canonizador; `orbita_fibras.py`).
Só a órbita decide se a CNF perde códigos.

| entrada | códigos | repo falha | corr falha | órbita UNSAT |
|---|---|---|---|---|
| K_7(6,4), M = 13, aleatórios com fibras ≥ 1 (cobertura fora), semente 101 | 1500 | 0 | 0 | **0 / 1500** |
| códigos em que a forma do repo viola (h) (seção 1.1): K_4(3,1) 103, K_4(4,2) 81, K_5(4,2) 54, K_7(4,2) M=18 39, K_7(5,3) M=16 62, K_7(6,4) M=13 3 (min) + 285 (max), M=14 27 + 2, cada um contra a CNF da sua ordem | 656 | — | 0 | **0 / 656** |
| K_4(4,2) = 7: 20 códigos que cobrem (achados por `gerar_codigos.py`), re-rotulados | 400 | 0 | 0 | 0 / 60 |
| K_5(4,2) = 11: 60 códigos que cobrem, re-rotulados | 600 | 0 | 0 | 0 / 60 |
| K_6(5,3) = 12: 10 códigos que cobrem (perfil 222222^5), re-rotulados | 200 | 0 | 0 | 0 / 60 |
| K_7(4,2) = 19: o código de partição 1 + 9 + 9, re-rotulado | 200 | 0 | 0 | 0 / 60 |
| K_7(6,4) = 14: o código do PR, re-rotulado (cobertura ligada) | 60 | 0 | 0 | 0 / 60 |
| K_7(5,3), M = 15, aleatórios (perfil único) | 200 | 0 | 0 | 0 / 20 |

Com cobertura ligada (códigos que cobrem), as formas normais são conferidas contra a CNF inteira,
inclusive as 7^6 cláusulas de cobertura. A órbita roda sem as cláusulas de cobertura: para um
código que cobre, toda imagem cobre e as P são definidas por equivalência, então elas valem em
qualquer elemento da órbita (com elas o solver só fica mais lento; medido: > 50 min para 60
códigos de K_7(6,4), M = 14, contra 48 s sem). As formas normais do canonizador corrigido e os
predicados de `predicados.py` concordam com a CNF nos dois sentidos nos códigos da linha 2 (a CNF
reprova a forma do repo e aceita a corrigida).

Não achei código real da família com 17 palavras para K_7(5,3) (o melhor conhecido); os testes de
K_7(5,3) são com códigos aleatórios do perfil.

### 1.4 Poder dos testes: quebras erradas plantadas (`mutantes.py`)

Cada mutante troca um trecho do `fib_encode.py` auditado (`mutantes.py`); o controle é o texto
sem mudança. "Órbita UNSAT" = algum código da amostra cuja órbita inteira violaria a CNF mutante
(mutante pego por SAT, sem canonizador); "forma viola" = a forma normal corrigida deixa de satisfazer.

| mutante | K_4(4,2), M = 10 (100 códigos): órbita UNSAT / forma viola | K_7(6,4), M = 13 (30 códigos) |
|---|---|---|
| controle | 0 / 0 | 0 / 0 |
| (h) também entre blocos de tamanhos diferentes | 35 / 44 | 25 / 28 |
| (h) nos dois sentidos (força blocos iguais) | 46 / 48 | 29 / 30 |
| (g) entre colunas de tipos diferentes | 24 / 49 | 25 / 26 |
| (e) sem respeitar a classe | 12 / 16 | 16 / 19 |
| (f) sem respeitar a classe | 55 / 87 | 29 / 29 |
| (h) na coordenada 2 em vez da 1 | 0 / 24 | 0 / 27 |
| (g) incluindo a coluna 1 | 0 / 2 | 0 / 3 |

Os cinco mutantes sabidamente errados são pegos pela órbita nas duas células. Os dois últimos não
são pegos pela órbita: não são necessariamente errados (podem ser quebras válidas, só diferentes
da forma normal), e o teste não afirma nada sobre eles; servem para mostrar que a comparação com
a forma normal é mais sensível que a órbita e não deve ser usada sozinha como juiz.

Em K_7(5,3), M = 15 (perfil único 3222222^5, 50 códigos) a órbita pega (h) nos dois sentidos
(50/50) e (f) sem classe (47/50); os demais não são pegos ali (no perfil único todas as colunas têm
o mesmo tipo, então "(g) entre tipos diferentes" coincide com o original, e as variações de (e) e
de (h) entre tamanhos podem ser satisfeitas por alguma imagem). É uma célula pobre para medir
poder; o poder foi medido nas duas acima.

## 2. Completude da lista de perfis (ataque 2)

`perfis_indep.py` enumera os tipos por força bruta sobre `itertools.product` (sem a recursão do
repo) e compara conjunto a conjunto com o JSONL:

| JSONL | tipos | perfis esperados | no JSONL | faltam | sobram | duplicados | fora de ordem / não fechados |
|---|---|---|---|---|---|---|---|
| `K7_6_4_M13.jsonl` | 11 | 8008 = C(16,6) | 8008 | 0 | 0 | 0 | 0 / 0 (8008 UNSAT, 8008 `lrat_check` VERIFIED) |
| `K7_5_3_M15.jsonl` | 1 | 1 | 1 | 0 | 0 | 0 | 0 / 0 |

Todo registro de K_7(6,4) é `ordem` min (o campo não existe nos registros; `rodar.py` só grava
`ordem` em versões posteriores), e a ordem dos tipos de cada registro bate com (simetria
residual, lexicográfica).

## 3. Codificação independente (ataque 3)

`indep_perfil.py`, sem importar nada de `tools/exatos/fibras`: one-hot em **todas** as
coordenadas, fibras exatas por totalizador do pysat, cobertura só no sentido necessário
(T_ij(a,b) → ∨_w Y, Y → X ∧ X) e quebra de simetria **mínima e trivial**: tipo P[i] na coordenada
i, fibra P[i][a] no símbolo a e palavras em ordem lexicográfica. Nada de (d)–(h). O espaço
inteiro com uma variável por palavra de Z_7^6 não cabe (cada bola de raio 4 tem 24 337 pontos:
2,9·10⁹ literais); fiz por perfil, com kissat 4.0.4 (`8af8e56`), outro solver que o do PR.

Validação antes de usar: K_4(4,2): M = 6, 5/5 perfis UNSAT; M = 7, 5 de 15 SAT com códigos que
cobrem (os mesmos números do red team do k742); K_5(5,3) ∄ 8: 21/21 UNSAT (igual ao PR).

| perfil (inst) | tipos | indep + kissat | tempo (s) | repo (CaDiCaL, s) |
|---|---|---|---|---|
| 0 | 3322111 3322111 3322111 3322111 3322111 3322111 | UNSAT | 294 | 7.9 |
| 8005 | 2222221 2222221 7111111 7111111 7111111 7111111 | UNSAT | 88 | 1.1 |
| 6918 | 3222211 5311111 6211111 4411111 7111111 7111111 | UNSAT | 75 | 1.3 |
| 212 | 3322111 3322111 3322111 5221111 5311111 4411111 | UNSAT | 82 | 3.5 |
| 7955 | 3331111 3331111 2222221 2222221 2222221 7111111 | UNSAT | 177 | 8.0 |
| 6269 | 4222111 3331111 2222221 7111111 7111111 7111111 | UNSAT | 92 | 1.6 |
| 4264 | 4321111 3222211 3222211 5221111 6211111 4411111 | UNSAT | 98 | 3.3 |
| 7988 | 4411111 4411111 4411111 2222221 7111111 7111111 | UNSAT | 84 | 1.1 |
| 7272 | 5221111 5221111 3331111 4411111 2222221 2222221 | UNSAT | 70 | 5.4 |
| 7634 | 5311111 5311111 6211111 2222221 2222221 7111111 | UNSAT | 75 | 5.6 |
| 7900 | 6211111 3331111 2222221 2222221 7111111 7111111 | UNSAT | 82 | 2.5 |
| 8007 | 7111111 7111111 7111111 7111111 7111111 7111111 | UNSAT | 137 | 0.3 |
| 2997 | 3322111 2222221 2222221 2222221 2222221 2222221 | INDEFINIDO | 1200 | 249.0 |
| 8001 | 2222221 2222221 2222221 2222221 2222221 2222221 | INDEFINIDO | 1200 | 177.6 |
| 7078 | 3222211 2222221 2222221 2222221 2222221 2222221 | INDEFINIDO | 1200 | 134.1 |
| 4999 | 4321111 2222221 2222221 2222221 2222221 2222221 | INDEFINIDO | 1200 | 121.0 |
| 3112 | 4321111 4321111 4321111 3222211 5221111 5311111 | UNSAT | 90 | 3.6 |
| 7958 | 3331111 3331111 7111111 7111111 7111111 7111111 | UNSAT | 170 | 0.4 |
| 2722 | 3322111 5221111 3331111 3331111 4411111 7111111 | UNSAT | 83 | 2.8 |
| 5117 | 4222111 4222111 4222111 5311111 5311111 4411111 | UNSAT | 87 | 3.1 |

Amostra estratificada (semente 4764): o perfil 0, um perfil aleatório por tipo da coordenada 0
(11 estratos), os quatro de maior tempo de solver no JSONL e quatro aleatórios; 20 perfis no
total. **16/20 UNSAT, 0 SAT**, 1786 s de kissat somados nos UNSAT (70 a 295 s cada, 13 a 450
vezes o tempo do repo, como esperado sem (d)–(h)). **4 INDEFINIDOS em 1200 s**
(2997, 8001, 7078, 4999): justamente os de maior simetria (cinco ou seis coordenadas do tipo
2222221), que também são os mais caros no repo. INDEP_LONGO

**Cobertura exata do que reproduzi de forma independente: 16 dos 8008 perfis (0.20 %)**.
Nenhum desacordo: em nenhum perfil a codificação independente deu SAT onde o repo deu UNSAT. Não é
reprodução da prova inteira (no ritmo medido, ~90 s por perfil fácil, seriam ≥ 200 h de CPU, e a
cota de 32 vCPU estava ocupada: 28 em uso por exe-1, exe-2, exe-3 e factory-01, então não subi VM).
O valor da amostra é outro: mostra que, nos perfis medidos, o UNSAT não depende de (d)–(h), de
contador, de cobertura por equivalência nem do CaDiCaL.

## 4. Certificados LRAT (ataque 4)

`lrat_amostra.py` regenera a CNF com o codificador auditado, compara sha256, roda o CaDiCaL 3.0.1
(`c607304`, o mesmo do PR) com `--lrat --binary=false`, compara o sha256 da prova e confere com
**dois** verificadores: `lrat-check` (drat-trim `2e3b2dc`) e **cake_lpr** (verificador extraído do
CakeML, `cake_lpr.S` com o sha256 publicado no repositório dele). Amostra estratificada: perfis 0
e 8007, dois por tipo da coordenada 0 e os cinco de maior tempo de solver no JSONL.

| conferência | resultado (27 perfis: 0, 2074, 2610, 2997, 3547, 4578, 4999, 5289, 5512, 6366, 6617, 6718, 7078, 7330, 7480, 7636, 7759, 7851, 7922, 7949, 7956, 7981, 7984, 8001, 8002, 8006, 8007) |
|---|---|
| sha256 da CNF regenerada = `sha256.cnf` do JSONL | **27/27** |
| CaDiCaL UNSAT | 27/27 (964 s somados; maior 258 s, perfil 2997) |
| prova LRAT bit a bit igual à do JSONL (`sha256.lrat`) | **27/27** |
| `lrat-check` VERIFIED | 27/27 (112 s) |
| **cake_lpr** `s VERIFIED UNSAT` | **27/27** (400 s) |

Além disso, `sha_amostra.py` regenerou a CNF de **400 perfis aleatórios** (semente 2026) de
`K7_6_4_M13.jsonl` e do perfil único de `K7_5_3_M15.jsonl`: **400/400 e 1/1 com o mesmo sha256**.
Os certificados são do codificador do commit auditado, não de uma versão anterior.

**K_7(5,3) ∄ 15 (de carona).** O perfil único regenerado: sha256 da CNF igual; CaDiCaL UNSAT em
250 s; prova de 1,56 GB **bit a bit igual** à do JSONL (`9cc887c5…`); `lrat-check` VERIFIED (28 s)
e **cake_lpr** `s VERIFIED UNSAT` (91 s).


## 5. Literatura (ataque 5)

OpenAlex (busca semântica "q-ary covering codes covering radius new bounds", 2011+), o ledger
(`literatura_pos_keri`, `florath_lean` 7–19, `marosi_2026`, `gijswijt_polak_2025`) e o texto de
Marosi 2026 (arXiv 2608.19872, tabelas para 5 ≤ q ≤ 21): nada dá 14 nem melhora 13–15 para
K_7(6,4) desde Kéri 2011; Marosi não lista K_7(6,4). Busca curta, como pedido: não é revisão
exaustiva.

## 6. Lacunas, com gravidade

| # | lacuna | gravidade | efeito no resultado | o que fecha |
|---|---|---|---|---|
| 1 | **A prova escrita do Lema 4 (quebra (h)) está errada** e `fib_canon.canonizar`, a prova construtiva citada no doc, gera formas normais que violam (h) (10⁻⁵ a 10⁻³ dos códigos; 3 em 300 000 em K_7(6,4), M = 13, ordem min; contraexemplo explícito na seção 1.1). `tests/test_fibras.py` passa (28 passed, 1 skipped, conferido aqui) porque a amostra é pequena demais para a taxa | **alta para a prova**, nenhuma para os certificados | a CNF não muda e o enunciado de (h) é verdadeiro (prova corrigida na seção 1.2; órbita SAT em 0 de 656 códigos que derrubam o guloso, 0 de 1500 aleatórios). Vale também para K_7(5,3) ∄ 15 e para a rodada M = 16, que usam (h) | trocar o guloso pelo de `canon_corrigido.py` (mínimo sobre rotulações admissíveis), reescrever a prova do Lema 4 com o argumento da seção 1.2 e pôr no PR um teste de massa (predicados + órbita por SAT), não só os 21 códigos gulosos |
| 2 | A reprodução independente cobre **16 dos 8008 perfis**; os 4 de maior simetria ficaram INDEFINIDOS em 1200 s de kissat | média | o UNSAT da célula inteira continua apoiado em uma codificação (a do PR), conferida aqui por sha256, prova bit a bit e dois verificadores numa amostra, e pelos testes de completude | rodar `indep_amostra.py` nos 8008 (≥ 200 h de CPU) quando houver cota, ou uma codificação independente com quebra de simetria mais forte e provada à parte |
| 3 | Segundo verificador (cake_lpr) só em 27 de 8008 provas (+ a de K_7(5,3)) | baixa | o PR conferiu as 8008 com `lrat-check`; as 27 reproduzidas saíram bit a bit iguais | regenerar as 8008 provas e passar cake_lpr (~11 h de CaDiCaL + ~10 h de cake_lpr, pelos tempos medidos) |
| 4 | Dependências de literatura: K_7(6,4) usa K_7(5,3) ≥ 14 (publicado 15, Kéri/HSPQ); K_7(5,3) ≥ 16 usa K_6(4,2) = 15 (Kéri 2011 e 8855 perfis LRAT do k742, sem red team independente para q = 6) e K_7(4,2) ≥ 17 (no Lean). Se em vez da literatura se usar o K_7(5,3) ≥ 16 do próprio PR, a cadeia passa a depender de (h) duas vezes | baixa | nenhuma com a literatura | citar as fontes no doc e não encadear o resultado novo de K_7(5,3) no de K_7(6,4) |
| 5 | Os registros do JSONL de K_7(6,4) não têm os campos `ordem` e `sem` que o `rodar.py` auditado grava (foram gerados por uma versão anterior) | baixa | nenhuma: 400/400 CNFs regeneradas pelo codificador auditado têm o mesmo sha256 | registrar no doc a versão do `rodar.py` usada, ou regravar os campos |
| 6 | Nenhum código real de K_7(5,3) com 17 palavras nos testes de completude (só aleatórios do perfil) | baixa | — | achar/importar o código de Kéri e passar em `completude.py --cobre` |
| 7 | Nada disto está no Lean (Lemas 1–4, ponte código → CNF, LRAT no kernel) | informativa | — | como no k742 |


## 7. Veredito

**Sobrevive com ressalva.** Confiança alta de que K_7(6,4) = 14 é verdadeiro: cota superior
conferida por dois verificadores; lista de perfis completa; certificados do codificador auditado
(401 CNFs regeneradas com o mesmo sha256, 28 provas regeneradas bit a bit e conferidas por
lrat-check e cake_lpr); 16 perfis reproduzidos por codificação e solver independentes, sem
desacordo; nenhuma solução perdida pela quebra de simetria em 2 476 testes de órbita por SAT
(inclusive os 656 códigos que derrubam o guloso do repo) e 0 falhas da forma normal corrigida em
1,72 milhão de códigos aleatórios. A ressalva é a lacuna 1: **a prova do Lema 4 precisa ser substituída** (a
da seção 1.2 serve) e o canonizador do repo corrigido antes de o resultado ser apresentado como
teorema; a lacuna 2 é o que falta para uma segunda prova independente da célula inteira.
K_7(5,3) ≥ 16 (de carona): mesmo veredito, com a mesma ressalva (usa (h) no seu único perfil).

## 8. Reproduzir

Da raiz do repo, com o commit auditado em `$FIB` (o diretório `tools/exatos/fibras` dele),
`python-sat`, e os binários em `CADICAL`, `KISSAT`, `LRAT_CHECK`, `CAKE_LPR`:

    python3 tools/exatos/fibras_redteam/cota_superior.py data/codes/q7_n6_R4_M14.txt
    python3 tools/exatos/fibras_redteam/perfis_indep.py $FIB/certificados/K7_6_4_M13.jsonl 7 6 13 1
    python3 tools/exatos/fibras_redteam/contraexemplo_h.py
    python3 tools/exatos/fibras_redteam/massa_predicados.py 7 6 13 1 300000 29 --repo $FIB
    python3 tools/exatos/fibras_redteam/completude.py $FIB 7 6 13 1 1500 101 --orbita 1500
    python3 tools/exatos/fibras_redteam/mutantes.py $FIB 4 4 10 1 100 3
    python3 tools/exatos/fibras_redteam/indep_amostra.py $FIB/certificados/K7_6_4_M13.jsonl "$TMPDIR" 1200 0 8005 …
    python3 tools/exatos/fibras_redteam/lrat_amostra.py $FIB $FIB/certificados/K7_6_4_M13.jsonl "$TMPDIR" 0 2074 …
    python3 tools/exatos/fibras_redteam/sha_amostra.py $FIB $FIB/certificados/K7_6_4_M13.jsonl 400 2026
    python3 -m pytest -q -p no:cacheprovider tests/test_fibras_redteam.py
