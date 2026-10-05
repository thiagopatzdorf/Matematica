# K₃(6,2) ≥ 16: red team da afirmação (2026-10-05)

Frente adversarial da operação K₃(6,2), M = 15. O trabalho aqui foi **tentar quebrar** a afirmação
"não existe código ternário de comprimento 6, raio de cobertura 2 e 15 palavras". Não é a
reprodução independente do zero; essa é de outra frente. Aqui eu audito o raciocínio e o código
que já existem:

* **(A) completude da redução.** PR #51 (`tools/exatos/gaps2/`, prova em `docs/exatos/GAPS2_K362.md`)
  e o lema do PR #55 (`tools/exatos/k362/reducao.py`, |U| ≤ 79);
* **(B) inviabilidade de cada instância.** PR #57, branch `feat/k362-contagem`, ainda em rascunho:
  `certificar_lp.py`, `verificar.py` e os 12 054 certificados em `dados/K3_6_2_M15_certificados.jsonl.gz`.

Código do red team: `tools/exatos/k362/redteam/`. Testes: `tests/test_k362_redteam.py`.

Estados usados: OBSERVED (medido, sem garantia), COMPUTATIONALLY_VERIFIED (conferido por programa) e
PROVED (prova escrita, aqui conferida linha a linha). **Nenhuma cota muda com este documento, e o
ledger não foi tocado.**

## Veredito

**A afirmação sobrevive, com ressalvas.** Nenhum dos ataques achou código que escape da redução,
restrição inválida no LP, nem certificado aceito sem merecer. As ressalvas abaixo são de
exposição e de independência. Nenhuma delas abre um buraco na prova.

1. A prova escrita em `GAPS2_K362.md` pula um passo: o de que `fatia.configuracoes` gera toda
   classe. Ela diz "um conjunto e a sua forma são isométricos, logo há um representante por
   classe", mas o que precisa ser dito é que todo conjunto aparece, antes da forma, como algum
   multiconjunto de colunas RGS. O passo é verdadeiro (argumento em A1), e aqui foi conferido por
   Burnside para todo s ≤ 5 (A2). Gravidade: **baixa**.
2. A normalização (`canon_fatia`) e a enumeração (`fatia`) só têm uma implementação. A conferência
   por Burnside cobre a enumeração. A normalização é conferida aqui só por amostragem: 26 códigos
   reais × isometrias aleatórias (só s* = 3 e 4) e 5 776 conjuntos de 15 pontos que passaram no
   filtro (1 877 com s* = 5). O argumento matemático (A1) não
   depende dela: `canon_fatia` é só um algoritmo que testa a prova. Gravidade: **baixa**.
3. O verificador do PR e o meu usam a mesma convenção de índices do certificado (linha k ↔
   restrição). Isso não ameaça a correção: cada verificador reconstrói a restrição de cada índice a
   partir de (s*, K, t), e toda restrição que ele monta é válida para todo código da instância (B1).
   Um índice "trocado" só poderia fazer um certificado bom falhar, nunca um ruim passar. Gravidade:
   **nenhuma** (registrada para quem formalizar).
4. Nada é formal. A cadeia depende de Python (enumeração, forma canônica) e de dois verificadores
   de Farkas em Python. Para virar teorema verificado por máquina, falta o Lean (ou ao menos uma
   enumeração em outra linguagem, por exemplo com nauty, que o PR #55 já usou para as formas de
   s* = 5). Gravidade: **média para publicação, nenhuma para a correção**.
5. O resumo do PR #57 diz que o perfil 5+5+5 "morre por um lema de fatia… mais 406 pelas colunas
   equilibradas… e 3 pelo LP do espaço inteiro". Isso é **diagnóstico, não prova**: os certificados
   usam só as cinco famílias do OPB (B1), e nenhum deles usa lema da fatia, colunas equilibradas,
   perfil equilibrado ou |U| ≤ 79. Não conferi os números 10 591/406/3. Convém dizer isso no texto
   do PR, para ninguém achar que esses lemas sustentam a prova. Gravidade: **baixa** (clareza).

O que corrigir: (i) acrescentar o passo do item 1 em `GAPS2_K362.md` e dizer que o filtro é
aplicado antes da forma por ser invariante por isometria; (ii) no PR #57, deixar explícito que os
lemas auxiliares não são usados pelos certificados; (iii) para afirmação pública, reprodução
independente (outra frente) e, idealmente, Lean.

## Tabela dos ataques

| # | ataque | resultado | estado |
|---|---|---|---|
| A1 | prova de completude (GAPS2), linha a linha, contra `fatia.py` e `canon_fatia.py` | correta; 1 passo omitido (ressalva 1) | PROVED (com o passo acrescentado aqui) |
| A2 | a lista tem toda órbita que passa no filtro? (Burnside × `configuracoes` sem filtro × lista) | 1 / 5 / 35 / 490 / 11 075 órbitas para s* = 1..5; passam 0 / 1 / 27 / 468 / 11 000; nenhuma falta, nenhuma sobra, blocos completos | COMPUTATIONALLY_VERIFIED |
| A3 | a lista do verificador é a do `--listar`? | regenerada do zero aqui: sha256 `5a07459e…217e6`, idêntico ao do PR | COMPUTATIONALLY_VERIFIED |
| A4 | lema do PR #55 (soma de \|U\| ≤ 1 428, logo \|U\| ≤ 79) | prova conferida; vale também nos códigos de 17 com o M ajustado; **não é usado** pelos certificados | PROVED |
| B1 | cada família de restrição do LP vale para todo código da instância? | cinco famílias, cada uma com prova de uma linha (abaixo); nenhuma outra aparece nos certificados | PROVED |
| B2 | `verificar.py` confere Farkas do jeito certo, em inteiros, sobre o sistema regenerado? | sim (leitura linha a linha, abaixo) | PROVED (leitura) |
| B3 | verificador de Farkas mínimo, do zero, em `Fraction`, nos 12 054 certificados | 12 049 de 12 049 instâncias, 12 054 folhas, nenhuma recusada | COMPUTATIONALLY_VERIFIED |
| B4 | árvores das instâncias 16 e 2178 | 5 e 2 folhas; completude conferida semanticamente (toda atribuição das variáveis ramificadas cai numa folha) | COMPUTATIONALLY_VERIFIED |
| B5 | mutações (y negativo, sem linhas de fibra, outra instância, sem o maior y, M = 16, árvore sem folha) contra os dois verificadores | as obrigatórias (y < 0, sem fibras, árvore sem folha) foram 100 % recusadas pelos dois; nas informativas os dois concordam em 100 % | COMPUTATIONALLY_VERIFIED |
| C1 | códigos reais de 17 palavras × isometrias aleatórias: cadeia inteira (normalização → instância canônica → filtro → restrições → LP) | 26 códigos, 208 isometrias, 0 falhas; o gerador do PR não certifica nenhuma das 2 instâncias reais | COMPUTATIONALLY_VERIFIED |
| C2 | certificados de M = 15 transplantados para instâncias viáveis (as dos códigos de 17) | 31 224 folhas, nenhuma aceita (Farkas exige isso) | COMPUTATIONALLY_VERIFIED |
| C3 | conjuntos de 15 pontos (subconjuntos de códigos reais, aleatórios e equilibrados) que passam no filtro caem numa instância da lista | 5 776 de 5 776 na lista (s* = 2..5) | COMPUTATIONALLY_VERIFIED |
| C4 | lemas auxiliares com o M ajustado nos códigos reais | 0 falhas nos 26 | COMPUTATIONALLY_VERIFIED |

## A. Completude da redução

### A1. A prova do `GAPS2_K362.md`, linha a linha

* **Palavras distintas.** Um código com repetição e M ≤ 3⁶ troca a cópia por um ponto fora dele e
  continua cobrindo. Também vale para códigos com menos de 15 palavras: completa-se até 15. Logo
  basta excluir conjuntos de exatamente 15 pontos distintos. ✔
* **s\* e a fibra.** `s* = min |F(j,a)|`; como `Σ_a |F(j,a)| = 15`, vale `s* ≤ 5`. Qualquer fibra
  mínima serve, e empates não importam: a prova só usa que `|F(0,0)| = s*` e que toda fibra tem
  pelo menos s\* palavras. `canon_fatia` escolhe o menor (j,a) em ordem lexicográfica, o que é uma
  escolha válida entre as possíveis. ✔
* **Blocos.** Renomear os símbolos 1, 2 da coordenada 0 é isometria. Com `t₁ = t₂`, as duas ordens
  dão a mesma instância. `t_b ≥ s*` vale porque s\* é o mínimo. `blocos_restantes` enumera
  exatamente os `t₁ ≥ t₂ ≥ s*` de soma `15 − s*`. Conferi por força bruta em
  `lista_completa.blocos`. ✔
* **Passo 3 (K canônico).** Isometrias que fixam a coordenada 0 permutam as coordenadas 1..5 e os
  símbolos de cada uma. Elas levam K a qualquer conjunto da sua classe sob S₃ ≀ S₅, sem mexer na
  coordenada 0 nem nos blocos. ✔
* **Passo omitido (ressalva 1).** "A lista tem pelo menos um representante por classe" precisa de:
  todo conjunto de s pontos distintos, com os pontos numa ordem qualquer, tem colunas que, depois de
  renomear os símbolos de cada coluna (isometria), são cadeias de crescimento restrito. O
  multiconjunto dessas colunas é um dos `combinations_with_replacement(pats, m)` percorridos por
  `configuracoes`, e esse combo é isométrico ao conjunto. Como o filtro (|U|) é invariante por
  isometria, aplicá-lo ao combo antes da forma não perde nada. A forma é invariante (mínimo sobre
  as ordens dos pontos; RGS absorve símbolos; ordenar absorve coordenadas) e é um representante
  isométrico. Logo há exatamente um por classe. Isso é verdadeiro, mas não está escrito. ✔ com
  ressalva.
* **Lema da fatia (filtro de contagem).** `(0,y)` com `y ∈ U` não é coberto por F(0,0); quem o cobre
  difere na coordenada 0, logo está a distância ≤ 1 de y nas outras. São 15 − s\* palavras, e cada
  uma cobre no máximo `V(5,1) = 11` desses pontos. ✔ O código (`configuracoes` com `cap`,
  `instancias` com `descobertos`) aplica exatamente `|U| ≤ (M − s)·V(n−1, R−1)`. ✔
* **s\* = 0 e s\* = 1.** São excluídos pelo filtro, que o código aplica igual: `|U| = 243 > 165` e
  `192 > 154`. Burnside confirma 1 órbita em cada, e nenhuma passa. ✔
* **Prova × código.** As cinco famílias do OPB em `fatia_pb.opb` são as da tabela do documento, e
  são as mesmas que `certificar_lp.sistema` e `verificar.py` montam (B1). A normalização de
  `canon_fatia` segue os passos 1–3 na mesma ordem. ✔

### A2. A lista contém toda órbita (Burnside)

`burnside.py` conta as órbitas de s-subconjuntos de Z₃⁵ sob S₃ ≀ S₅ por classes de conjugação. O
tipo de ciclo de g só depende do tipo de σ ∈ S₅ e da classe da holonomia em cada ciclo de σ, e o
peso total é conferido contra |G| = 933 120. Ele bate com a contagem por força bruta em 7 casos
pequenos (teste). `lista_completa.py` gera `fatia.configuracoes(3, 5, s)` **sem filtro**, confere a
contagem contra Burnside, calcula |U| por força bruta sem `fatia.descobertos` e compara com a lista:

    python3 tools/exatos/k362/redteam/lista_completa.py --instancias i15.json     # ~35 min, 1 processo
    0 {'orbitas': 1, 'passam': 0, 'na_lista': 0, 'faltam': 0, 'sobram': 0, 'blocos_ruins': 0}
    1 {'orbitas': 1, 'passam': 0, 'na_lista': 0, 'faltam': 0, 'sobram': 0, 'blocos_ruins': 0}
    2 {'orbitas': 5, 'passam': 1, 'na_lista': 1, 'faltam': 0, 'sobram': 0, 'blocos_ruins': 0}
    3 {'orbitas': 35, 'passam': 27, 'na_lista': 27, 'faltam': 0, 'sobram': 0, 'blocos_ruins': 0}
    4 {'orbitas': 490, 'passam': 468, 'na_lista': 468, 'faltam': 0, 'sobram': 0, 'blocos_ruins': 0}
    5 {'orbitas': 11075, 'passam': 11000, 'na_lista': 11000, 'faltam': 0, 'sobram': 0, 'blocos_ruins': 0}
    12049 instâncias na lista, 12049 distintas -> COMPLETA

Contagem igual a Burnside, com formas duas a duas distintas, quer dizer exatamente uma configuração
por órbita. Uma forma que não fosse invariante daria contagem maior; uma que não fosse completa
daria contagem menor. Só os dois defeitos juntos, cancelando-se exatamente em todos os s, passariam,
e o PR #55 já tinha conferido as 11 000 formas de s\* = 5 contra o nauty. Resíduo: a enumeração sem
filtro ainda é a do `fatia.py`; o que é independente aqui é a contagem e o |U|.

### A3. A lista do verificador é a do `--listar`

    python3 tools/exatos/gaps2/rodar_pb.py --q 3 --n 6 --R 2 --M 15 --listar i15_regen.json   # ~40 min com a máquina cheia
    12049 instâncias -> i15_regen.json
    sha256sum i15_regen.json
    5a07459ed8a82a18ad4169739f887c6ec77c90b24576680d40c3650a239217e6

É idêntico ao sha256 do PR #57 e ao do `dados/K3_6_2_M15_instancias.json.gz` descomprimido. O
`verificar.py` confere esse sha256 quando recebe `--sha256`, e o teste do PR fixa o valor.

### A4. O lema do PR #55

`Σ_{(j,a)} |U(j,a)| ≤ Σ_x d(x,C)`: tome a palavra c mais próxima de x, a distância d ≤ 2. Nas 6 − d
coordenadas j em que c concorda com x, c está em `F(j, x_j)` e cobre x, logo x não está em
`U(j, x_j)`. Então x aparece em no máximo d dos U. Soma: `≤ 2·(729 − 15) = 1 428`, e a menor das 18
fibras tem `|U| ≤ ⌊1 428/18⌋ = 79`. ✔ A prova não precisa de equilíbrio, e conferi a versão com M
ajustado nos códigos de 17 (C4). **Os certificados do PR #57 não usam esse lema**: certificam as
12 049 instâncias, inclusive as 3 942 que ele descartaria. A afirmação (A) não depende do PR #55.

## B. Inviabilidade de cada instância

### B1. As famílias de restrição do LP e a validade de cada uma

Variáveis `z_c ∈ [0,1]`, uma por ponto de Z₃⁶ (indicador de "c é palavra"). Num código normalizado
da instância (s\*, K, t):

| família | forma | por que vale para todo código da instância |
|---|---|---|
| cobertura | `Σ_{d(c,x)≤2} z_c ≥ 1`, para todo x | raio de cobertura 2 |
| fibras | `Σ_{c_j=a} z_c ≥ s*`, j = 1..5, todo a | s\* é o mínimo de todas as fibras |
| tamanho | `Σ z_c = 15` | palavras distintas (A1) |
| blocos | `Σ_{c_0=b} z_c = t_b`, b = 1, 2 | definição de t na normalização |
| fatia 0 (limites) | `z_c = 1` para c ∈ {0}×K, `z_c = 0` nos outros c com `c_0 = 0` | F(0,0) = {0}×K exatamente |
| ramo (só 16 e 2178) | `z_c = 0` ou `z_c = 1` em cada folha | z é 0-1; as folhas cobrem os dois valores |

**Nenhuma outra família aparece.** Os dois verificadores só aceitam índices de linha de cobertura
(`< 729`) e de fibra (`729 + (j−1)·3 + a`, j ≥ 1, só com s\* > 0), e `mu` de comprimento 3
(tamanho, bloco 1, bloco 2). Lema da fatia τ\*, colunas equilibradas, perfil `Σ i·A_i(x) = 60`,
|U| ≤ 79 e o lema de projeção não entram no sistema certificado (ressalva 5). No LP eles aparecem
só como consequência das cinco famílias: por exemplo, as linhas de cobertura da fatia somadas ao
tamanho já dão o LP τ\*.

### B2. Leitura do `verificar.py`

Para `G z ≥ h`, `E z = e`, `lb ≤ z ≤ ub`, y ≥ 0 e μ livre:
`y·h + μ·e ≤ (yᵀG + μᵀE)·z ≤ Σ_c max(g_c·lb_c, g_c·ub_c)`. Se o lado esquerdo for estritamente
maior, não existe nem solução fracionária. O `verificar.py`:

* exige `y` inteiro ≥ 0 (`isinstance(v, int) and v >= 0`) e `mu` inteiro de comprimento q ✔;
* recusa índice fora de `[0, 729 + 15)` e linha de fibra com s\* = 0 ✔;
* reconstrói g a partir de (s\*, K, t) e das bolas que ele mesmo calcula; não lê nenhuma matriz
  guardada ✔. Lado esquerdo: `mu₀·M + Σ mu_b·t_b + Σ y_cob·1 + Σ y_fib·s*` ✔. Lado direito:
  `g_c·fixo_c` nas fixadas e `max(g_c, 0)` nas livres, que é a forma certa para [0,1] ✔;
* usa desigualdade estrita (`lhs > rhs`) ✔ e trata folha cujas fixações contradizem a fatia como
  vazia, o que está certo ✔;
* confere a árvore (mesma variável nos dois lados, recursivo, folha = caminho vazio) ✔, e que os
  registros são exatamente as instâncias da lista, na ordem, com (s\*, K, t) iguais ✔;
* a conferência do sha256 é opcional na linha de comando; o teste do PR e o documento a fixam.
  Sem `--sha256`, uma lista adulterada passaria, mas aí a falha seria do insumo, não do Farkas. ⚠
  menor.

### B3. Verificador mínimo, escrito do zero

`farkas_min.py` não importa nada do gerador, do `verificar.py` nem do `gaps2`. Monta cada restrição
como dicionário explícito, soma em `Fraction` e confere a completude da árvore **semanticamente**:
enumera todas as atribuições 0/1 das variáveis ramificadas e exige que cada uma caia em alguma folha.

    python3 tools/exatos/k362/redteam/farkas_min.py --instancias i15_regen.json \
        --certificados K3_6_2_M15_certificados.jsonl.gz --sha256 5a07459e…217e6
    sha256 da lista: 5a07459ed8a82a18ad4169739f887c6ec77c90b24576680d40c3650a239217e6
    12049 de 12049 instâncias, 12054 folhas, recusadas [], faltam [] -> TODAS INVIÁVEIS
    real 6m28s

O `verificar.py` do PR, na mesma máquina: `12049 de 12049 instâncias, 12054 folhas, recusadas []
-> TODAS INVIÁVEIS` (13 s).

### B4. As ramificações

* 16 (s\* = 3, t = (6,6)): folhas `{640=1}`, `{640=0, 389=1}`, `{640=0, 389=0, 709=1}`,
  `{640=0, 389=0, 709=0, 628=1}` e `{640=0, 389=0, 709=0, 628=0}`, uma "escada" que cobre as 16
  atribuições;
* 2178 (s\* = 5): `{642=1}` e `{642=0}`.

As variáveis ramificadas têm índice ≥ 243, então são pontos com `c_0 ≠ 0` e nenhuma contradiz a
fatia. As duas árvores passam na conferência estrutural do PR e na semântica do `farkas_min`.

### B5. Mutações

`mutacoes.py`, amostra de 400 instâncias (semente 7), cada folha mutada de seis jeitos e conferida
pelos dois verificadores. O `verificar.py` do PR é carregado do próprio branch:

    python3 tools/exatos/k362/redteam/mutacoes.py --instancias i15.json --certificados cert.jsonl.gz \
        --verificar-pr verificar_pr.py --amostra 400
    mutação: [testadas, aceitas por farkas_min, aceitas pelo verificar.py do PR]
      neg      [400, 0, 0]
      sem_fib  [359, 0, 0]
      troca    [400, 7, 7]
      maior_y  [400, 368, 368]
      M16      [400, 375, 375]
      folha    [7, 0, 0]
    RESULTADO: OK

* **Têm de ser recusadas, e foram:** y = −1 (400 de 400), sistema sem as linhas de fibra nas 359
  folhas que as usam, e as duas árvores sem uma das 7 folhas.
* **Informativas** (aceitar não é defeito; o que importa é que os dois verificadores concordem, e
  concordaram em 100 %):
  * `troca`: 7 de 400 certificados também provam outra instância do mesmo s\*. É possível quando o
    certificado não depende da forma exata de K;
  * `maior_y`: 368 de 400 continuam válidos sem a entrada de y de maior peso, o que mostra que há
    folga. O gerador arredonda escalando, e a folga é grande;
  * `M16`: o mesmo certificado, conferido na instância de M = 16 com o mesmo (s\*, K) e `t₁ + 1`,
    ainda vale em 375 de 400. Isso **não** é prova falsa: essas instâncias de M = 16 são, até onde se
    sabe, inviáveis também (o PR mediu 198 de 201 inviáveis na raiz para s\* ≤ 4). O teste que
    importa para "prova falsa" é o C2, em instâncias sabidamente viáveis.
* Primeira versão do ataque `M16` (registro do erro): conferi com M = 16 sem ajustar t. O
  `farkas_min` recusou por assertiva (`sum(t) ≠ M − s`), e o `verificar.py` aceitou 383. Os dois
  estão certos: esse sistema é trivialmente inviável (5 + 10 ≠ 16), e o `verificar.py` não exige
  coerência de (s\*, t, M) porque ela vem da lista. Corrigi a mutação para um sistema coerente.

## C. Códigos reais e conjuntos de 15 pontos

**Códigos.** São 26 códigos de 17 palavras, todos conferidos por força bruta como de raio 2: o C17
de `tests/test_gaps2.py` e 25 achados pelo `sa_cover.c` (60 sementes de 6 s; 25 chegaram a 0
pontos descobertos). Nenhum código de 16 palavras é conhecido; uma busca de 20 s parou em 7 pontos
descobertos. Os 26 têm só **2 distribuições de distância** e caem em só 2 instâncias depois da
normalização: 24 em s\* = 4, `t = (7,6)`, e 2 em s\* = 3, `t = (7,7)`. **Nenhum código real tem
s\* = 5.** Por isso o ramo das 11 000 instâncias equilibradas só é exercitado pelos conjuntos
sintéticos abaixo (ressalva registrada em "Lacunas").

    python3 tools/exatos/k362/redteam/codigos_reais.py c17_*.txt --isometrias 8 --transplantes 150 \
        --aleatorios 3000 --instancias i15.json --certificados cert.jsonl.gz --certificar-lp certificar_lp.py
    26 códigos de 17 palavras, 2 distribuições de distância distintas
    208 isometrias normalizadas, 31224 certificados transplantados recusados, 2 instâncias distintas
    passadas ao gerador LP (nenhuma deve ser certificada)
    15 palavras: 1791 passaram no filtro, 1791 achadas na lista
    falhas: []
    RESULTADO: OK            (14 min, 1 processo)

* **C1 (cadeia inteira em M = 17).** Em 208 isometrias aleatórias (8 por código), a normalização
  é isometria (mesma distribuição de distâncias, continua cobrindo), K sai na forma canônica, passa
  no filtro de M = 17, e o código transformado satisfaz **todas** as restrições da instância no
  sistema escrito do zero (`farkas_min.Sistema`), não no OPB do `fatia_pb`. O gerador do PR
  (`certificar_lp.certificar`), rodado nas 2 instâncias distintas com M = 17, **não** devolveu
  certificado. Como K canônico + filtro equivale a estar na lista (A2: a lista é exatamente "as
  formas canônicas que passam no filtro"), não foi preciso enumerar a lista inteira de M = 17.
* **C2 (soundness do Farkas).** 31 224 folhas de certificados de M = 15, transplantadas para as
  instâncias viáveis dos códigos de 17, foram todas recusadas pelo `farkas_min`. É o que o lema de
  Farkas exige: se um certificado passasse numa instância com solução, o verificador estaria
  errado. O teste `test_multiplicador_aleatorio_prova_instancia_viavel` faz o mesmo com (y, μ)
  aleatórios.
* **C3 (a lista não tem buraco onde há conjuntos de verdade).** Conjuntos de 15 pontos: 15 palavras
  de um código real, 15 pontos aleatórios e, na segunda rodada, conjuntos equilibrados (cada coluna
  é uma permutação de `0⁵1⁵2⁵`, todas as 18 fibras com 5). Toda vez que a instância normalizada
  passa no filtro de M = 15, ela está na lista de 12 049, com os mesmos blocos, e satisfaz todas as
  restrições que não são de cobertura:

      python3 tools/exatos/k362/redteam/codigos_reais.py c17_repo.txt c17_2.txt --isometrias 2 \
          --transplantes 5 --aleatorios 6000 --semente 2 --instancias i15.json --certificados cert.jsonl.gz
      15 palavras: 3985 passaram no filtro, 3985 achadas na lista; por s*: [(2, 133), (3, 1561), (4, 414), (5, 1877)]
      RESULTADO: OK

  No total são 5 776 de 5 776, com 1 877 em s\* = 5.
* **C4 (lemas com o M do código).** Nos 26 códigos (`codigos_reais.lemas`) valem: a identidade
  `Σ_c (n − d(x,c)) = Σ_j |F(j,x_j)|` em todo x (o perfil equilibrado é o caso M = 15 dela); o lema
  da soma `Σ|U(j,a)| ≤ Σ_x d(x,C) ≤ 2(729 − M)` e a cota do mínimo; o lema da fatia
  `τ*₁(U(j,a)) ≤ M − |F(j,a)|` em **todas as 18 fibras** de cada código (LP); e o lema de projeção
  `r_a + c_b + 2n_ab ≥ ⌈(81 − M)/8⌉` em todos os pares de coordenadas. Nenhuma falha. Esses lemas
  não sustentam os certificados (B1); o teste é só para que nenhum texto do PR afirme algo falso.

## Lacunas encontradas

| # | lacuna | gravidade | correção sugerida |
|---|---|---|---|
| L1 | `GAPS2_K362.md` omite o passo "todo conjunto aparece como multiconjunto de colunas RGS antes da forma" e não diz que o filtro é aplicado antes da forma por ser invariante | baixa (o passo é verdadeiro e foi conferido por Burnside) | acrescentar dois parágrafos ao documento |
| L2 | enumeração (`fatia.configuracoes`, `fatia.forma`) e normalização (`canon_fatia`) têm uma implementação só | baixa | a reprodução independente (outra frente) deve gerar a lista com outro canonicalizador (nauty) e comparar o sha256 ou o conjunto de formas |
| L3 | nenhum código real tem s\* = 5; o ramo equilibrado só foi exercitado por conjuntos sintéticos (1 877) e pela prova | baixa | nada a corrigir na prova; registrar |
| L4 | o resumo do PR #57 cita lema da fatia, colunas equilibradas e LP do espaço como o que "mata" o 5+5+5, mas os certificados usam só as 5 famílias do OPB; os números 10 591/406/3 não foram conferidos aqui | baixa (clareza) | dizer no PR que são diagnóstico, não parte da prova |
| L5 | `verificar.py` só confere o sha256 da lista se receber `--sha256`, e não confere coerência de (s\*, t, M), que herda da lista | muito baixa | tornar o sha256 obrigatório para M = 15 (ou embutido) |
| L6 | nada é formal (Python de ponta a ponta) | média para publicação, nenhuma para a correção | Lean, ou ao menos a reprodução independente com outro verificador e outra enumeração |

Nenhuma lacuna de gravidade alta ou crítica foi encontrada.

## Reprodução

    git show origin/feat/k362-contagem:tools/exatos/k362/contagem/dados/K3_6_2_M15_certificados.jsonl.gz > cert.jsonl.gz
    git show origin/feat/k362-contagem:tools/exatos/k362/contagem/verificar.py > verificar_pr.py
    git show origin/feat/k362-contagem:tools/exatos/k362/contagem/certificar_lp.py > certificar_lp.py
    python3 tools/exatos/gaps2/rodar_pb.py --q 3 --n 6 --R 2 --M 15 --listar i15.json
    python3 tools/exatos/k362/redteam/burnside.py
    python3 tools/exatos/k362/redteam/lista_completa.py --instancias i15.json
    python3 tools/exatos/k362/redteam/farkas_min.py --instancias i15.json --certificados cert.jsonl.gz
    python3 tools/exatos/k362/redteam/mutacoes.py --instancias i15.json --certificados cert.jsonl.gz \
        --verificar-pr verificar_pr.py --amostra 400
    gcc -O2 -o sa tools/exatos/sa_cover.c -lm
    for s in $(seq 1 60); do ./sa 3 6 2 17 6 $s c17_$s.txt; done      # 25 sementes chegaram a 0
    python3 tools/exatos/k362/redteam/codigos_reais.py c17_*.txt --isometrias 8 --transplantes 150 \
        --aleatorios 3000 --instancias i15.json --certificados cert.jsonl.gz --certificar-lp certificar_lp.py
    python3 -m pytest -q -p no:cacheprovider tests/test_k362_redteam.py

Tudo em CPU local, no máximo 2 processos meus, sem VM e sem gasto.
