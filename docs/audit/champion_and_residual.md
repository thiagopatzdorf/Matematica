# Base campeã de K_7(9,4) e o remendo residual

Data: 2026-10-02. Alvo: o código de 1137 palavras (`data/codes/q7_n9_R4_M1137.txt` no repo
Matematica, provado no Lean) = 3 classes laterais de C0 = [9,3]_7 (1029 palavras) + remendo de 108.

Tudo abaixo é contagem exata (aritmética mod 7, enumeração exaustiva), sem amostragem.
Reprodução (≈ 15 s de CPU cada, exceto o ILP):

    python3 scripts/audit/champion_structure.py      # -> data/audit/champion/structure.json
    python3 scripts/audit/champion_residual.py       # -> data/audit/champion/residual.json
    python3 scripts/audit/champion_residual_ilp.py 24 1500   # -> data/audit/champion/ilp_thr24.json (+ .log)

Convenções: H = [I_6 | A], A = `666 065 652 643 621 615`, síndrome inteira = Σ s_j 7^j.
Trio da base S = {0, 4191, 7708}.

## A. Estrutura

### A.1 O código C0

| medida | valor |
|---|---|
| parâmetros | [9,3,6]_7 |
| distribuição de pesos | A0=1, A6=18, A7=162, A8=54, A9=108 |
| dual | [9,6,3]_7, A3=18, A4=648, A5=2538, … |
| MDS? | não; **MDS [9,3,7]_7 não existe** (arco em PG(2,7) tem no máximo q+1=8 pontos), então d=6 é o máximo para [9,3]_7 |
| quase-MDS | d = n−k (AMDS) e d⊥ = k (o dual também é AMDS): **C0 é NMDS** |
| raio de cobertura de C0 | 5; pesos de líderes de classe: 1, 54, 1296, 17964, 87804, **10530** (pesos 0..5) |
| |Bc| (síndromes de peso 5) | 10530 — **o menor das 6362 classes** (é a linha 1 de `classes_sorted.jsonl`, ordenado por nBc; a 2ª tem 10548) |

Configuração dos 9 pontos (colunas de G) em PG(2,7):

- 9 pontos distintos (nenhum repetido), não é arco: retas com 0/1/2/3 pontos = 18/9/27/3.
- As **3 trissecantes não são concorrentes e particionam os 9 pontos** (coordenadas {2,3,6}, {1,7,8},
  {0,4,5}): os pontos são **3 pontos em cada lado de um triângulo**, sem usar os vértices.
- A única cúbica que passa pelos 9 pontos é o próprio triângulo (21 pontos racionais, 3 pontos
  singulares): a cúbica é degenerada, então C0 **não** é código AG de curva elíptica.
- Cônicas: no máximo 6 dos 9 pontos numa cônica não degenerada (9 cônicas atingem 6). Logo C0
  **não** é RS estendido nem "cônica + 1 ponto". A base antiga (1285) e a 2ª classe por nBc **são**
  "8 pontos de uma cônica + 1 ponto" (ver A.3).
- **Forma normal** (coordenadas do triângulo, medida pelo script), com μ3 = {1,2,4} (raízes cúbicas
  da unidade em F_7):

      lado z=0: (1, ζ, 0)     lado x=0: (0, 1, 3ζ)     lado y=0: (1, 0, 3ζ),     ζ ∈ μ3.

  Três pontos (1,a,0), (0,1,b), (1,0,c) são colineares sse c = −ab (Menelau). Com a ∈ μ3 e
  b ∈ 3μ3, −ab ∈ μ3 e c ∈ 3μ3: **nenhuma transversal**. Se o 3º lado usasse c ∈ μ3 (sem a torção),
  sairia a configuração de Hesse AG(2,3) com 12 retas, estabilizador 216 e A6 = 72. Conferido
  numericamente (`reference_triangle_configurations` em structure.json): torcida = 3 retas,
  |Stab| = 54, pesos idênticos aos de C0; Hesse = 12 retas, |Stab| = 216, pesos (1,0,…,72,0,216,54).
  Em uma frase: **C0 é o "Hesse torcido"**: a torção de um lado por um não-cubo mata as 9
  transversais e deixa só as 3 palavras de peso 6 (a menos de escalar) dos lados.

Grupo de automorfismos (força bruta sobre todos os referenciais ordenados dos 9 pontos):

- Estabilizador em PGL(3,7): **54** (= toro μ3×μ3 de ordem 9 × grupo de ordem 6 nos lados);
  grupo monomial de C0: 6·54 = **324**; age **transitivamente nas 9 coordenadas**.
- Comparação: base antiga 16 (órbitas de coordenadas 8+1), 2ª classe por nBc 12 (órbitas 6+2+1).

### A.2 O trio, as órfãs e o centro comum

- **Grupo da base** (pares (L,c), L induzido por Aut(C0) no espaço de síndromes, c translação, com
  L·S + c = S), a menos das translações por C0: ordem **54**. Ele induz no trio só as rotações
  cíclicas (Z3), não as transposições.
- Os 3 trios canônicos com 6 órfãs, {0,4191,7708}, {0,20875,59538}, {0,21613,64832}, são
  **equivalentes entre si** por Aut(C0) + translação (os três pares conferidos). A classe tem,
  portanto, **uma única base de 6 órfãs a menos de simetria** entre as três listadas (a varredura
  exactT2 com T=20 lista 6 trios com 6 órfãs nessa classe; não conferi a equivalência dos 6, só dos
  3 canônicos).
- As 6 órfãs: síndromes 19141, 37272, 63434, 75935, 89846, 111459. Todas têm peso de líder 5, e
  t − s também tem peso 5 para cada s do trio (cada órfã está a distância exatamente 5 das 3 classes).
- Formam **uma só órbita** do grupo da base (transitivo nas 6).
- Estão num **plano afim** (posto das diferenças = 2) de F_7^6, em duas retas com 3 órfãs cada
  (coordenadas no plano: (0,0),(1,0),(3,0) e (0,1),(3,4),(1,2)). O plano das órfãs não contém
  as direções do trio (posto conjunto 3).
- **Centro comum**: o baricentro do trio, das 6 órfãs e dos 9 tipos de síndrome que cobrem 24
  órfãs (B.1) é o mesmo ponto c = 246260 (vetor de síndrome). O trio é c + {τ, ρτ, ρ²τ} sob a rotação
  de ordem 3 do grupo; órfãs (6) e tipos-24 (9) são órbitas do mesmo grupo em volta de c.

### A.3 Comparação

| | campeã (1137) | base antiga (1285) | 2ª classe por nBc |
|---|---|---|---|
| A | 666 065 652 643 621 615 | 652 132 256 141 231 402 | 666 066 651 642 634 623 |
| pesos | 18/162/54/108 | 24/144/72/102 | 18/162/54/108 |
| trissecantes | 3, triângulo | 4, concorrentes | 3, concorrentes |
| máx. na cônica | 6 | 8 (cônica + 1) | 8 (cônica + 1) |
| |Stab PGL| | 54 (transitivo) | 16 | 12 |
| nBc | 10530 (mínimo global) | 11634 | 10548 |
| melhor trio | 6 órfãs, 1 órbita, plano afim | 24 órfãs (grupo da base 4, 6 órbitas de 4, posto 6) | nenhum trio com ≤ 20 órfãs (exactT2 T=20, `t20/c_2.out`) |

O que torna a base especial, de forma mensurável:

1. A 2ª classe tem **os mesmos pesos** de C0 e nBc só 18 maior, mas não chega a 20 órfãs: não é a
   distribuição de pesos nem o tamanho de Bc. A diferença está na geometria: triângulo torcido
   (estabilizador 54, transitivo) contra cônica + 1 ponto (12, não transitivo).
2. Com estabilizador grande, Bc é muito simétrico, e o trio pode ser escolhido como órbita Z3 em
   volta de um centro; as interseções Bc ∩ (Bc+s1) ∩ (Bc+s2) colapsam para uma só órbita de 6.
   Na base antiga o grupo da base tem ordem 4 e as órfãs se espalham em 6 órbitas, posto 6.
3. Isto é **correlação medida em 3 bases**, não teorema: não provei que estabilizador grande implica
   poucas órfãs. A varredura das 6362 classes (outro relatório) diz que só esta classe tem trio com
   ≤ 8 órfãs.

## B. O remendo residual

### B.1 Formulação exata

P = união das 6 classes órfãs, |P| = 2058. Problema: o menor W ⊂ F_7^9 com
P ⊂ ∪_{w∈W} Ball(w,4) (set cover com 7^9 colunas e 2058 linhas).

**Redução exata**: o número de pontos da classe órfã t numa bola de centro w só depende da síndrome
σ = Hw: |Ball(w,4) ∩ (classe t)| = Nb[t − σ], Nb[d] = #{e : wt(e) ≤ 4, He = d}. As 40 353 607 bolas
caem em 117 649 tipos (um por σ), cada um com 343 translações por C0. Dentro de uma classe
(identificada com F_7^3 pelas coordenadas 6,7,8) a palavra (σ, a) cobre a + D(t−σ).

Cobertura de P por uma bola (histograma por tipo; multiplique por 343 para palavras):

| pontos de P na bola | 24 | 19 | 18 | 17 | 16 | ≤ 15 |
|---|---|---|---|---|---|---|
| tipos σ | **9** | 54 | 435 | 702 | 864 | o resto |

- Máximo = **24**, atingido só por 9 tipos (3087 palavras), todos com perfil (4,4,4,4,4,4); os 9
  tipos formam uma órbita do grupo da base e estão num plano afim com o mesmo centro c. Entre 24 e
  19 não há nada.
- Máximo por classe órfã = 4 (cada uma das 6).

### B.2 Cotas

| cota | valor | certificado |
|---|---|---|
| inferior trivial | ⌈2058/24⌉ = **86** | toda bola tem ≤ 24 pontos de P (enumeração dos 117 649 tipos) |
| LP (relaxação do set cover, todas as 7^9 colunas) | **2058/24 = 85,75** | dual u_p = 1/24 para todo p ∈ P: viável porque toda bola tem ≤ 24 pontos de P; primal: uma palavra de cobertura 24 simetrizada pelas translações e pelo grupo da base (transitivo nas 6 órfãs) cobre cada ponto com peso 24/2058 por unidade. O LP agregado de 6 linhas e o LP explícito com as 3087 colunas de cobertura 24 dão 85,75 no HiGHS |
| superior | **108** (remendo do 1137) | conferido ponto a ponto: cobre as 2058 órfãs; 84 palavras de cobertura 24 + 24 de cobertura 18; soma das coberturas 2448, excesso 390 |
| relaxação inteira (B.4) | 86 (não melhora) | HiGHS, 25 min: dual bound 86, raiz 85,773 após 162 cortes, 0 nós |

**Gap: 108 − 86 = 22. Com esta base, o 1137 está a 22 palavras da cota inferior; o melhor
concebível com estas 3 classes é 1029 + 86 = 1115.** O LP não melhora a cota trivial: o LP é
exatamente a cota de contagem, porque o grupo da base é transitivo nas órfãs.

### B.3 Grafo órfã → remendo

- Nenhuma palavra cobre pontos de **exatamente uma** classe órfã (0 palavras). Cada classe órfã é
  tocada por 36 741 817 palavras, todas tocando também outra.
- Palavras por número de classes órfãs tocadas: 0 → 1029 (as próprias classes da base),
  2 → 21 609, 3 → 372 498, 4 → 3 895 794, 5 → 12 669 048, **6 → 23 393 629** (58% de 7^9).
- Cobertura máxima conjunta por número de classes tocadas: 2 → 6, 3 → 7, 4 → 10, 5 → 13, 6 → 24.
- Por classe: máximo 4 pontos; tipos σ por cobertura da classe 0: 0/1/2/3/4 → 10530/48187/43380/14364/1188.

### B.4 O que a integralidade exige (relaxação agregada)

Relaxação **válida** (não é ILP restrito; é cota): as 3087 palavras de cobertura 24 entram como
binárias; todas as outras (cobertura ≤ 19) viram um inteiro y e folgas z_p ∈ [0,1] com
Σ z_p ≤ 19·y. Todo remendo verdadeiro é solução dela, então o dual bound do B&B é cota inferior do
remendo. Quebra de simetria válida: sem nenhuma palavra-24, |W| ≥ ⌈2058/19⌉ = 109 > 108; com
alguma, uma translação por C0 a leva para a = 000.

Resultado (`data/audit/champion/ilp_thr24.json`, `.log`): LP da raiz 85,75; com 162 cortes,
85,773; dual bound **86** no limite de 25 min (1506 s, 0 nós explorados). A solução primal de 178
é a trivial do HiGHS e não significa nada. **A relaxação não passou de 86** no tempo dado.

O que fica claro na conta: com W = 86, a folga é 24·86 − 2058 = 6. Isso só deixa duas formas:
(a) 86 palavras-24 com sobreposição total ≤ 6 (em cada classe órfã, 344 incidências para 343 pontos:
exatamente um ponto duplo por classe); (b) 85 palavras-24 + 1 palavra de cobertura 18 ou 19
(qualquer palavra ≤ 17 deixa 2040 + 17 < 2058). Nos dois casos, cada classe F_7^3 precisa de um
quase-ladrilhamento por translações das formas D(t−σ_k) de 4 pontos, **com as mesmas translações
nas 6 classes**. É um problema de cobertura exata pequeno e muito rígido.

### O que NÃO foi provado

- Não há cota inferior acima de 86 provada (salvo o que B.4 disser); o gap 22 está aberto.
- Não provei que nenhuma outra base de 3 classes dá remendo menor; só que esta é a única classe com
  trio de ≤ 8 órfãs (outro relatório) e que a 2ª classe por nBc não tem trio com ≤ 20.
- A explicação "estabilizador grande ⇒ poucas órfãs" é observação em 3 bases, não teorema.
- A equivalência por simetria foi conferida só entre os 3 trios canônicos, não entre os 6 trios que
  o exactT2 lista.
- Nenhuma busca heurística nova foi rodada nesta auditoria (restrição de escopo do coordenador).
