# Red team: K_4(7,4) ≥ 10 e K_4(6,3) ≥ 12 (2026-10-07)

Revisão adversarial independente das provas LRAT de `docs/exatos/FIBRAS_RAIO_GERAL.md` (PR #111) e de
`tools/exatos/fibras/`. **Commit auditado: `1964d8b` (main).** O objetivo era **quebrar** a prova: achar
um passo falso, um perfil faltando, uma CNF que não diz o que a prova diz, uma quebra de simetria que
perde código. Padrão de rigor: `REDTEAM_K764.md`. Scripts desta revisão (os independentes não importam o
canonizador nem o codificador do repo; os que precisam do codificador dele só o usam para regenerar CNFs):
`tools/exatos/fibras_redteam_k474/`. Testes: `tests/test_fibras_redteam_k474.py`.

## Veredito

**Sobrevive. Nenhuma falha que invalide K_4(7,4) ≥ 10 (logo = 10) ou K_4(6,3) ≥ 12.** Tudo o que tentei
falhou em derrubar a prova, e três coisas que o texto original só afirmava passaram a ser medidas:
(i) a dependência de literatura de K_4(6,3) ≥ 12 era K_4(5,2) ≥ 16 só CLAIMED no ledger, mas o que o Lema 1
usa é **K_4(5,2) ≥ 12**, e isto foi recalculado aqui (3003 perfis, todos UNSAT com LRAT) — junto com
K_4(6,3) ≥ 10 (462 perfis), de modo que a cadeia inteira fecha **só com a cota de esferas + a mesma
máquina**; (ii) a CNF de tamanho real aponta exatamente os pontos descobertos (propagação, 50 códigos);
(iii) **todas** as CNFs dos dois registros (954 + 10 090) regeneram o sha256 gravado e as 63 provas reproduzidas saem
**bit a bit iguais** às do registro. As ressalvas são de rigor e de cobertura (seções 6 e 7), não de verdade.

## 0. Resumo por ataque

| # | ataque | resultado |
|---|---|---|
| 1 | Lema 1 à mão, por construção explícita em códigos reais, por SAT exato, e direção (só lb de s excluído importa) | correto; 0 falhas em 314 fibras construídas, mutante pego (23 falhas); todos os códigos reais do repo respeitam `s_min` |
| 2 | Quebras (a)–(h): órbita por SAT (grupo completo), sem canonizador | **0 UNSAT em 4000 testes** (2000 por célula, 1000 códigos × 2 ordens) + 1000 adversariais (colunas iguais/palavras repetidas) + controle real de 10 palavras; 4 mutantes pegos nas duas células |
| 3 | Codificação da cobertura por t-uplas: codificador do zero | concorda em 5 células pequenas (SAT e UNSAT, t = 2, 3, 4); CNF real aponta exatamente os pontos descobertos (K_4(6,3) e K_4(7,4)); CNF completa aceita o código real de K_4(7,4), M = 10 |
| 4 | Contagem de perfis e cubos | 792 e 8008 recalculados; cada perfil uma vez, nenhum faltando/sobrando/duplicado; 168 + 2100 cubos = projeção exata dos modelos da CNF na coordenada 1 (18 + 6 perfis) |
| 5 | Reprova do zero + segundo solver + segundo verificador | ver seção 5 |
| 6 | Consistência do ledger | 0 contradições em 4702 comparações entre 1145 células |

## 1. Lema 1 (fibras)

### 1.1 Prova à mão, refeita

C ⊂ Z_q^n (multiconjunto, M palavras) cobre com raio R ≤ n − 2; F = {c : c_j = a}, s = |F| < q.
A_i = {c_i : c ∈ F} tem ≤ s elementos, logo existe S_i ⊂ Z_q ∖ A_i com |S_i| = q − s. Para x com x_j = a e
x_i ∈ S_i, toda c ∈ F discorda de x em todas as n − 1 outras coordenadas: d = n − 1 > R, então quem cobre x
é c ∉ F, com c_j ≠ a e d(x,c) = 1 + d'(x,c) ≤ R. A φ_i (identidade em S_i, um σ_i ∈ S_i fora) nunca
diminui a concordância com x ∈ ∏S_i, então a imagem de C ∖ F (sem a coordenada j) é código de raio R − 1
em Z_{q−s}^{n−1} com ≤ M − s palavras. **Correto**, inclusive s = 0 e multiconjuntos (completar com
repetições leva "∄ M" a "∄ ≤ M"). Falha por construção se S_i puder cruzar A_i (mutante abaixo).

### 1.2 O que de fato sustenta s_min = 1

Só a exclusão de **s = 0** importa para a correção: `s_min` é o primeiro s não excluído, e as instâncias são
"todas as fibras ≥ s_min". Que s = 1 seja permitido (K_3(6,3) = 6 ≤ 8; K_3(5,2) = 8 ≤ 10) só poderia *aumentar*
o número de perfis, nunca perder código. Logo as dependências reais são:

| célula | exclusão de s = 0 | cota usada | de onde vem |
|---|---|---|---|
| K_4(7,4), M = 9 | K_4(6,3) > 9 | ≥ 10 basta (ledger: 12 deste certificado; 11 HSPQ) | **recalculado aqui**: ∄ 9 em K_4(6,3), 462 perfis (esfera K_4(5,2) ≥ 10 > 9 exclui s = 0) |
| K_4(6,3), M = 11 | K_4(5,2) > 11 | ≥ 12 basta (ledger: 16, CLAIMED) | **recalculado aqui**: ∄ 11 em K_4(5,2), 3003 perfis (esfera K_4(4,1) ≥ 20 > 11 exclui s = 0) |

A cota de esferas sozinha **não** basta para a segunda (K_4(5,2) ≥ 10 < 12): sem o cálculo de 3003 perfis a
cadeia depende de literatura. Medido: `K4_5_2_M11.jsonl.xz`, 3003/3003 UNSAT com `lrat-check` VERIFIED
(149 s de solver, 104 s de check), 40/40 CNFs regeneradas batem o sha256; `K4_6_3_M9.jsonl.xz`, 462/462
(190 s + 39 s). Pela codificação independente (seção 3): 300/300 perfis de K_4(5,2) sorteados UNSAT em kissat.
Ressalva: os dois cálculos usam o **mesmo** codificador/quebras que a prova principal (cobertos pelas
seções 2–4), não são uma prova independente do Lema 1.

### 1.3 Construção explícita em códigos reais (`lema1_construcao.py`)

Códigos que cobrem (guloso podado, mais os códigos reais de `data/codes/`), toda fibra (j, a) com s < q, S_i e
σ_i sorteados: a imagem tem ≤ M − s palavras e cobre Z_{q−s}^{n−1} com raio R − 1 **em 314 de 314 fibras**
(K_4(4,2), K_3(6,3), K_5(5,3), K_4(7,4), …). Mutante "S_i sorteado em todo Z_q": 23 falhas em 127 fibras.

### 1.4 Contra um solver exato (`lema1_sat.py`, `cobertura_indep.py`)

"Existe código de M palavras que cobre e tem exatamente s palavras com símbolo 0 na coordenada 0?" Onde o
lema exclui, a resposta tem de ser UNSAT. K_3(4,1) = 9 e K_4(3,1) = 8 calculados por SAT aqui. Resultados:
K_3(4,1), M = 9, 10, s = 0, 1, 2: UNSAT (lema exclui s = 0; s = 1, 2 permitidos mas UNSAT, sem
contradição); K_3(5,2), M = 8, s = 0 (K_3(4,1) = 9 > 8): UNSAT (70 s); K_4(4,2), M = 7, s = 0
(K_4(3,1) = 8 > 7): UNSAT (22 s). Nenhum contraexemplo.

### 1.5 Direção e ledger

Todo código real do repo com R ≤ n − 2 e q^n ≤ 3·10^5 tem toda fibra ≥ `fibra_minima(q,n,R,M)`
(`test_nenhuma_fibra_de_codigo_real...`); o código de 10 palavras de K_4(7,4) tem colunas de tipo 3331 (todas
as fibras ≥ 1, s_min = 1). Cota superior 10: o arquivo cobre Z_4^7 com raio 4 (0 de 16 384 descobertos,
numpy, pela definição de distância). `consistencia_ledger.py`: 1145 células, 4702 comparações pelas
desigualdades K(n,R) ≤ K(n+1,R), K(n+1,R+1) ≤ K(n,R), K(n+1,R) ≤ qK(n,R), K(n,R+1) ≤ K(n,R), K_q ≤ K_{q+1}:
**0 contradições** com os valores novos (e o teste pega K_4(6,3) ≥ 17 plantado).

## 2. Quebras de simetria (a)–(h)

Prova de (h) (Lema 4) relida: o guloso "menor vetor sobre rotulações admissíveis" é monótono (a rotulação
L ≤ L' símbolo a símbolo, construída com os m_c primeiros rótulos livres, existe no passo anterior), a
versão corrigida em `REDTEAM_K764.md` está certa; (e) em nível de bloco e a precedência por palavra do
`fib_cubos` coincidem sob (d). Não achei buraco na escrita; o teste de verdade é o da órbita.

`orbita_indep.py` (escrito do zero): para um código C qualquer (cubra ou não), a CNF da instância do perfil de
C (quebra = True) mais variáveis de grupo (permutação de palavras M × M, de coordenadas n × n, de símbolos
q × q por coordenada de destino) tem de ser SAT. Códigos com as colunas do perfil sorteado.

| entrada | testes | UNSAT |
|---|---|---|
| K_4(7,4) M = 9, 1000 códigos × ordens min/max, semente 2026 (sem cobertura) | 2000 | **0** |
| K_4(6,3) M = 11, 1000 códigos × 2 ordens, semente 2027 | 2000 | **0** |
| adversariais (colunas copiadas a menos de rotulação, palavras repetidas, pares que diferem em 1 coordenada), K_4(7,4) / K_4(6,3), 250 × 2 | 500 + 500 | **0** |
| código real de 10 palavras de K_4(7,4), CNF **completa com cobertura**, ordem max e min | 2 | SAT, SAT |

Poder (mutantes de `fib_encode.py`, 60 testes cada; UNSAT = mutante pego):

| mutante | K_4(7,4) M = 9 | K_4(6,3) M = 11 | K_4(4,2) M = 10 |
|---|---|---|---|
| controle | 0 | 0 | 0 |
| (h) nos dois sentidos | 51 | 39 | 21 |
| (e) sem classe | 12 | 4 | 8 |
| (f) sem classe | 58 | 55 | 26 |
| (g) entre tipos diferentes | 47 | 33 | 14 |

## 3. Codificação da cobertura (Lema 2')

* `cobertura_indep.py`: um `m[x][u]` por ponto e palavra com contador sequencial próprio ("concorda em ≥ t
  coordenadas"), one-hot em todas as colunas, sem projeção. `diferencial.py` compara com
  `fib_encode.codificar(quebra=False)` em instâncias de perfil com células fixadas (de códigos reais re-rotulados,
  de aleatórios e com uma célula estragada): K_4(4,2) M = 7 (t = 2), K_3(4,1) M = 9 (t = 3), K_3(5,2) M = 8 (t = 3),
  K_3(6,3) M = 6 (t = 3), K_2(7,3) M = 4 (t = 4): 60 casos cada, 17+18+15+21+28 = **99 SAT, 201 UNSAT, 0 desacordos**,
  e todo modelo de ambos cobre pela definição.
* Tamanho real (`cobertura_pontual.py`): CNF de uma instância sorteada com as variáveis x de um código do
  perfil (melhorado por colina para cobrir mais), propagação unitária, cláusula de cada ponto falsa **sse** o
  ponto é descoberto pela definição d ≤ R: 25 + 25 códigos (K_4(6,3) M = 11; K_4(7,4) M = 9), 335–795 pontos
  descobertos por código, **conjuntos idênticos em 50/50**.
* SAT em tamanho real: CNF completa (cobertura por triplas + (a)–(h)) da instância do código de 10 palavras de
  K_4(7,4) é SAT nas duas ordens (35 s).
* sha256: **954/954** CNFs de K_4(7,4) e ****10 090/10 090**** de K_4(6,3) regeneram o sha256 do registro (o repo conferia
  uma amostra); em **todos** os registros o campo `tipos` é a instância `inst` na ordem gravada (0 incoerentes).
* Contraprova por solver: pela codificação independente de perfil (`indep_instancia.py`, só estrutura de perfil +
  palavras de um bloco em ordem lex, nada de (d)–(h)) com kissat: K_4(5,2) M = 11, **300/300 UNSAT**; K_4(6,3) M = 11:
  3 de 5 perfis sorteados UNSAT (2433, 5150, 5039), os 2 mais lentos (305, 1386) **sem decisão em 900 s**, 0 SAT. K_4(7,4) M = 9: o perfil mais fácil (239) **não terminou em 1200 s** sem (d)–(h) — não
  consegui contraprova independente por solver para essa célula (seção 7).

## 4. Perfis e cubos (`perfis_cubos.py`, `cubos_cnf.py`)

| célula | s_min | tipos | perfis | no registro | faltando / sobrando / duplicados | inteiros + em cubos |
|---|---|---|---|---|---|---|
| K_4(7,4), M = 9 | 1 | 6 | 792 = C(12,7) | 792 | 0 / 0 / 0 | 786 + 6 (168 cubos) |
| K_4(6,3), M = 11 | 1 | 11 | 8008 = C(16,6) | 8008 | 0 / 0 / 0 | 7990 + 18 (2100 cubos) |

(enumeração por estrelas e barras e multiconjuntos por índices, sem a recursão do repo; um perfil inteiro e em
cubos ao mesmo tempo: 0.) Misturar ordens min e max no mesmo registro (772 + 14 em K_4(7,4)) é válido: cada
perfil é completo sozinho (teste de órbita nas duas ordens).

Cubos: o conjunto de prefixos da coordenada 1 que satisfazem as regras do doc (uma palavra por símbolo, fibras
exatas, (d), (e), (h)), por força bruta com poda, é **igual** ao dos `cubo` gravados em todos os 24 perfis
(faltam 0, sobram 0, duplicados 0, `cubo_idx` bijetivo; 28 em cada perfil de K_4(7,4), 39–267 em K_4(6,3)). Pela
CNF: o conjunto de projeções de todos os modelos (SAT com bloqueio, sem as cláusulas de cobertura, que só tiram
modelos) na coordenada 1 é igual aos cubos gravados — **24/24 perfis** (inclusive os 28 e 136 modelos). L = 9 em
K_4(6,3), M = 11: o prefixo de 9 palavras já separa tudo.

Poder do `fecha_perfis.py` (mutação do registro): sem um perfil inteiro, sem um cubo, `lrat_check` ≠ VERIFIED ou
um SAT → código de saída 1 (testado). Fragilidade achada: ele confia no campo `tipos` (ver achado 2).

## 5. Reprova do zero (CaDiCaL c607304 `--lrat`, `lrat-check` 2e3b2dc, `lrat-trim` b30f400, kissat 8af8e56)

Sorteio com semente 20261007: 3 perfis inteiros com tempo ≤ 60 s + os 2 mais lentos de cada célula + 1 perfil
inteiro em cubos. Para cada registro: CNF regenerada (sha256 igual), CaDiCaL → UNSAT, **sha256 da prova igual ao do
registro (bit a bit)**, `lrat-check` VERIFIED, `lrat-trim` com checagem (saída 20 = `s VERIFIED`; controle:
prova corrompida → saída 1, prova truncada → sem VERIFIED), kissat (sem prova) UNSAT.
Controle do verificador: prova com hint trocado e prova truncada dão `c NOT VERIFIED` no `lrat-check`.

| célula | perfis reprovados | resultado |
|---|---|---|
| K_4(7,4), M = 9 | 5 inteiros (239, 378, 79 [fáceis]; 121, 191 [os mais lentos, 230 e 258 s no registro]) + **14 dos 28 cubos** do perfil (3222)^7 (cubos 0–13, interrompido por tempo) | 19/19: CNF sha256 igual, UNSAT, **prova bit a bit igual**, `lrat-check` VERIFIED, `lrat-trim` saída 20; kissat UNSAT em 18, o 19º (perfil 121) cortado por mim em 240 s |
| K_4(6,3), M = 11 | 5 inteiros (2433, 5039, 5150 [fáceis]; 1386, 305 [lentos, 179 e 238 s]) + **os 39 cubos** do perfil inteiro 3103 (4322 4322 4322 5222 5222 5222…) | 44/44 nos mesmos itens; kissat UNSAT em 42, 2 cortados por mim (perfis 1386 e 305) |

Em números: 63 provas LRAT regeneradas (13,9 GB conferidos e descartados; CaDiCaL somou 3386 s contra 2135 s dos
registros originais, a máquina estava dividida com outras corridas). Nenhuma divergência: **63/63 provas idênticas às
do registro** (portanto o registro descreve provas que o CaDiCaL fixado de fato produz). Perfis completamente
reprovados: K_4(6,3) 6 de 8008 (5 inteiros + 1 em cubos); K_4(7,4) 5 inteiros de 792 + metade de um perfil em cubos.
Logs: `fibras_redteam_k474/resultados/reprova_k47{4,3}.jsonl.xz`.

## 6. Achados

| # | achado | gravidade | efeito | o que fecha |
|---|---|---|---|---|
| 1 | A dependência declarada ("K_4(5,2) = 16, Kéri 2011", CLAIMED) é maior que a usada (K_4(5,2) ≥ 12); a esfera dá 10, então sem cálculo a prova de K_4(6,3) ≥ 12 dependia de literatura não conferida | baixa (resolvida) | nenhum | `K4_5_2_M11` (3003 perfis, LRAT) e `K4_6_3_M9` (462) em `fibras_redteam_k474/resultados/`, teste `test_registro_do_red_team_fecha_todos...`; sugiro o dono registrar K_4(5,2) ≥ 12 e K_4(6,3) ≥ 10 como resultado nosso e atualizar `dependencias` no ledger (não toquei no ledger) |
| 2 | `fecha_perfis.py` conta um perfil como fechado pelo campo `tipos` do registro, sem conferir contra `inst` nem o sha256 (só amostra opcional): um registro com `tipos` trocado ou fabricado fecharia o perfil errado | baixa | nenhum nos certificados (0 incoerentes em 11 044; 954 + 10 090 shas regeneram) | `pc.registros_incoerentes` + teste; sugiro `fecha_perfis` rodar a coerência por padrão |
| 3 | O certificado é um **log** (sha256 de CNF e prova + "VERIFIED"); as provas (553 GB) não estão versionadas e a conferência exige re-rodar | informativa | a regenerabilidade foi medida: provas reproduzidas saem idênticas bit a bit | manter o registro de CaDiCaL/`lrat-check` exatos (feito no doc) |
| 4 | A "codificação independente" do PR cobre 26/40 (K_4(7,4)) e 58/60 (K_4(6,3)) com tempos esgotados nos perfis simétricos; nenhuma contraprova por solver existia para a célula inteira | média (rigor) | a evidência independente de K_4(7,4) é a de estrutura (seções 2–4), não a de solver | a minha, sem (d)–(h), também não termina em K_4(7,4) (perfil 239: 1200 s). Fecha com quebra de simetria própria e forte, ou segundo verificador formal nas 954 provas |
| 5 | Os testes `test_kissat_confirma_*` leem logs; não reexecutam o kissat | informativa | — | minhas reprovas rodam o kissat de fato (amostra) |

## 7. O que NÃO foi coberto

* Só 12 perfis foram reprovados (6 por célula; dois perfis inteiros lentos por célula e um perfil em cubos
 ); as outras ~8800 provas só têm o registro e a regeneração de CNF.
* Segundo verificador formal (cake_lpr) não foi usado; usei `lrat-check` e `lrat-trim`.
* Os testes de órbita são amostrais (4000 + 1000 + controle), não exaustivos; a garantia de completude vem da
  prova escrita do Lema 3/4 relida, e da prova corrigida de `REDTEAM_K764.md`.
* Nenhuma contraprova por solver independente para K_4(7,4); em K_4(6,3) só 5 perfis.
* O controle de SAT em tamanho real de K_4(6,3) (código de ≤ 16 palavras) não foi feito (busca sem sucesso no
  tempo); o caminho t = 3, n = 6 foi coberto por propagação pontual e por K_3(6,3)/K_3(5,2).
* Literatura: não refiz a busca de novidade; K_4(7,4) = 10 usa a cota superior publicada (Rivas Soriano, o
  código está em `data/codes/` e foi conferido). Lean: nada disto está no kernel.

## 8. Reproduzir

Da raiz do repo, com `python-sat`, numpy e os binários em `CADICAL`, `LRAT_CHECK`, `LRAT_TRIM`, `KISSAT`:

    python3 tools/exatos/fibras_redteam_k474/lema1_construcao.py 2026 6
    python3 tools/exatos/fibras_redteam_k474/lema1_sat.py 4 4 2 7
    python3 tools/exatos/fibras_redteam_k474/orbita_massa.py 4 7 4 9 1000 2026 0 [mutante]
    python3 tools/exatos/fibras_redteam_k474/orbita_alvo.py 4 6 3 11 250 78
    python3 tools/exatos/fibras_redteam_k474/diferencial.py 3 5 2 8 60 1
    python3 tools/exatos/fibras_redteam_k474/cobertura_pontual.py 4 6 3 11 25 20261007
    python3 tools/exatos/fibras_redteam_k474/controle_sat_k474_m10.py
    python3 tools/exatos/fibras_redteam_k474/perfis_cubos.py tools/exatos/fibras/certificados/K4_6_3_M11.jsonl.xz 4 6 3 11
    python3 tools/exatos/fibras_redteam_k474/cubos_cnf.py tools/exatos/fibras/certificados/K4_7_4_M9.jsonl.xz 4 7 4 9
    python3 tools/exatos/fibras_redteam_k474/reprovar.py CERT.jsonl.xz Q N R M SAIDA.jsonl inteiro:INST:ORDEM cubos:INST:ORDEM
    python3 tools/exatos/fibras_redteam_k474/consistencia_ledger.py
    python3 -m pytest -q -p no:cacheprovider tests/test_fibras_redteam_k474.py
