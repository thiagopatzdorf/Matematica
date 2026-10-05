# K_3(6,2) com M = 15: contagem, LP agregado e certificados de Farkas (2026-10-05)

Frente matemática da operação K₃(6,2). Pergunta: existe `C ⊂ Z_3^6` com 15 palavras e raio de
cobertura 2? Sabido: `15 ≤ K_3(6,2) ≤ 17`. Código em `tools/exatos/k362/contagem/`, testes em
`tests/test_k362_contagem.py`. Estados como no `AGENTS.md`: OBSERVED, COMPUTATIONALLY_VERIFIED,
INDEPENDENTLY_REPRODUCED, PROVED, FORMALIZED.

## Resumo

### O que o certificado verificado usa (a prova)

| resultado | estado |
|---|---|
| **As 12 049 instâncias da fatia mínima com M = 15 são inviáveis já na relaxação linear.** 12 047 caem na raiz e 2 ramificam, com 5 e 2 folhas. São 12 054 certificados de Farkas inteiros, conferidos por um verificador exato que usa só a biblioteca padrão. Com a completude da redução (`GAPS2_K362.md`), isso dá **K_3(6,2) ≥ 16** | COMPUTATIONALLY_VERIFIED. Sobreviveu ao red team (PR #59, `K3_M15_REDTEAM.md`, com verificador de Farkas escrito do zero). Falta reprodução independente da enumeração. **Não vai para o ledger** |

Cada certificado usa **só** as cinco famílias de restrições do OPB do GAPS2 (cobertura, fibras ≥ s*, tamanho, blocos e fatia 0 fixada), sobre o sistema 0-1 **inteiro** de cada instância (729 variáveis). A cadeia da prova tem dois elos: a completude da lista (`GAPS2_K362.md`, com o passo das colunas RGS e a conferência por Burnside) e os 12 054 certificados. **Nenhum lema desta página entra nela.** Nem o lema da fatia na forma LP, nem as colunas equilibradas, nem o lema do perfil equilibrado, nem os LPs agregados, nem os ramos de Raval.

### Diagnóstico, fora da prova

| resultado | estado |
|---|---|
| Por que o 5+5+5 fica fácil para o LP: das 11 000 configurações com s* = 5, 10 591 já morrem pelo LP de cobertura **só da fatia** (lema da fatia), mais 406 pelo mesmo LP com as colunas equilibradas, e as 3 restantes (1129, 6339, 10111) só pelo LP do espaço inteiro. Os certificados versionados **não** são desses LPs da fatia; o red team não conferiu esses números | OBSERVED (HiGHS em ponto flutuante, sem certificado guardado) |
| Lema do perfil equilibrado: todas as fibras com 5 palavras ⇔ `Σ_c d(x,c) = 60` para todo x ⇔ `B_1 = 0` no dual de MacWilliams | PROVED (abaixo); não usado na prova |
| Lema da fatia: `τ*(U(K)) ≤ M − s` para toda fibra de tamanho s | PROVED (abaixo); não usado na prova |
| LPs agregados (vetor local + Delsarte + pares): o melhor dá **12**. O 5+5+5 com ILP agregado continua viável | OBSERVED (solver em ponto flutuante) |
| Ramos de Raval com a barra de M = 15: **9 de 38 morrem, 29 ficam abertos**. Com qualquer ordem das órbitas, o primeiro ramo tem LP ≤ 9,51 < 12, e fixar um 4º centro não passa de 9,36 < 11 | OBSERVED (LP em ponto flutuante; os 9 duais foram conferidos em inteiros só pelo gerador, sem verificador independente) |

As 6 instâncias que custaram de 3,5 a mais de 30 minutos ao RoundingSat no GAPS2 (7955, 9118,
10603, 11739, 11804 e 11927, todas com s* = 5) estão entre as que o LP da fatia já mata
(diagnóstico). O certificado delas, como o de todas as outras, é do sistema inteiro.

## 1. Contagem dupla

`|Z_3^6| = 729`, `V(6,2) = 73`, `15·73 − 729 = 366` (excesso).

**Interseção de bolas** `|B_2(c) ∩ B_2(c')|` por `d = d(c,c')`, contagem exata (`esferas.intersecoes`):

| d | 0 | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|---|
| \|B∩B'\| | 73 | 33 | 25 | 12 | 6 | 0 | 0 |

Com `m(x)` = multiplicidade de cobertura e `A_d` = pares não ordenados de palavras a distância d:
`Σ_x (m(x) − 1) = 366` e `Σ_x C(m(x),2) = 33A_1 + 25A_2 + 12A_3 + 6A_4`.

**Capacidade radial** `a_r(d) = |S_r(z) ∩ B_2(c)|` com `d(z,c) = d` (`esferas.capacidades`; a mesma
tabela do Raval). Linhas r = 1..6, colunas d = 0..6:

    r=1: 12 12  4  3  0  0  0   (|S_1| =  12)
    r=2: 60 20 20  9  6  0  0   (|S_2| =  60)
    r=3:  0 40 24 25 16 10  0   (|S_3| = 160)
    r=4:  0  0 24 24 27 25 15   (|S_4| = 240)
    r=5:  0  0  0 12 20 26 36   (|S_5| = 192)
    r=6:  0  0  0  0  4 12 22   (|S_6| =  64)

Todo ponto z satisfaz `Σ_d a_r(d) A_d(z) ≥ |S_r|` ("cascas"). Com M = 15: a linha 6 dá
`14·4 = 56 < 64` (todo centro tem outro a distância ≥ 5), e a linha 3 dá `14·10 = 140 < 160` (todo
centro tem outro a distância ≤ 4).

**Projeção em duas coordenadas** (lema do Raval, refeito para M = 15). Para as coordenadas j, k e os
símbolos a, b, os 81 pontos com `(x_j, x_k) = (a,b)` recebem capacidade de no máximo
`15 + 8(r_a + c_b + 2n_ab)`. Logo `r_a + c_b + 2n_ab ≥ ⌈66/8⌉ = 9`, e somando em b, `r_a ≥ 3`.
Toda fibra tem de 3 a 9 palavras. PROVED (contagem direta). No LP de 3 centros, esses cortes
arredondados não mudaram nenhum valor.

**Lema do perfil equilibrado.** PROVED. Para todo x vale `Σ_{c∈C} (n − d(x,c)) = Σ_j |F(j, x_j)|`,
porque cada coordenada em que c concorda com x conta uma vez dos dois lados. Se toda fibra tem
`M/q` palavras, o lado direito é `nM/q = 30`, então `Σ_i i·A_i(x) = 60` em todo x. Somando
`Σ_a |F(j,a)|² ≥ M²/q` (Cauchy–Schwarz, com igualdade só no equilibrado) sobre j, obtém-se
`Σ_k k·a_k ≤ nM(q−1)/q = 60`, com igualdade só no equilibrado. Isso é `B_1 = 0`, porque
`K_1(k) = 12 − 3k`. Teste: `test_perfil_equilibrado_fixa_a_soma_das_distancias_em_todo_ponto`.

**Lema da fatia.** PROVED. Seja F uma fibra `{c : c_j = a}` com s palavras e K as suas projeções
em `Z_3^5`, que são s pontos distintos. Seja `U(K)` o conjunto dos pontos a distância > 2 de K. O
ponto `(a, y)` com `y ∈ U(K)` não é coberto por F. Então é coberto por uma palavra c fora de F, que
já difere em j, logo `d(y, c') ≤ 1`. Assim, as `M − s` palavras de fora cobrem U(K) com raio 1, e
o número de cobertura fracionário `τ*_1(U(K))` é no máximo `M − s`. A versão de contagem pura,
`|U| ≤ (M − s)·11`, é o filtro do GAPS2. A versão LP é muito mais forte: para s = 5, das 11 000
configurações que passam no filtro, 10 591 têm `τ* > 10` (OBSERVED, diagnóstico; os certificados
versionados não usam este lema).

Validação do lema: `K_3(4,1)`, M = 8, fica sem configuração viável em todo s*. `K_3(5,2)`, M = 7,
deixa 1 configuração. É o esperado, porque o lema sozinho não precisa matar tudo.

## 2. LP e ILP agregados

`esferas.lp_local`: as variáveis são `N(v)`, o número de pontos com vetor local
`v = (A_0(x), …, A_6(x))`, mais o enumerador `a_k`. As restrições são `Σ N = 729`, cobertura
(`v_0 + v_1 + v_2 ≥ 1`), cascas, as identidades de pares `Σ_x A_i A_j = M Σ_k a_k p^k_ij`, a
média nas palavras e Delsarte. Menor M viável:

| LP | K_3(6,2) | K_3(5,2) (= 8) | K_3(4,1) (= 9) |
|---|---|---|---|
| esfera | 10 | 6 | 9 |
| vetor local + cascas | 11 | 6 | 9 |
| + Delsarte | 11 | 6 | 9 |
| + identidades de pares | **12** | 6 | 9 |
| SDP de Gijswijt–Polak (literatura) | 13,12 | — | — |

Com o perfil 5+5+5 (`Σ i v_i = 60` em todo vetor, `B_1 = 0`), M = 15 continua viável, e
**também como ILP em N(v)** (584 vetores locais admissíveis). Resultado negativo: nenhuma
desigualdade agregada desta família mata o 5+5+5. O que fecha é o LP do sistema inteiro de cada
instância da fatia, depois de a redução quebrar a simetria (seção 4).
SDP/Terwilliger (tarefa 3): não foi feito. O LP já fica abaixo do SDP conhecido, e a seção 4 tornou
o SDP desnecessário para M = 15.

## 3. Os 38 ramos de Raval com a barra de M = 15

Reproduzi a partição de Raval (Zenodo 10.5281/zenodo.22510341): centro em `000000`, âncora de peso
máximo `1^d 0^{6−d}` com d ∈ {5, 6}, e 3º centro de peso ≤ 4 na menor órbita do estabilizador do
par. Os dois lemas valem para M = 15 com folga maior. Os |H| e |U| dos 38 ramos batem com a
tabela dele. O LP de cobertura residual (12 centros livres, `esferas.ramos_raval`) dá:

- **morrem (LP > 12): 9**. São 5/17 `002220` (12,31), 5/18 `002221` (12,31), 5/19–5/23
  (14,67 a 14,83), 6/12 `001222` (12,17) e 6/13 `002222` (13,77). Os 6 de Raval mais 3 novos.
  Os duais inteiros foram conferidos com `W > 12Q` pelo próprio gerador; não estão versionados;
- **abertos: 29**. Os LPs ficam entre 9,29 e 10,86.

**Limite estrutural (OBSERVED):** o primeiro ramo de qualquer ordem de órbitas não exclui nada. Sem
exclusão, o LP de 3 centros fica em no máximo 9,44 (d = 5) ou 9,51 (d = 6), abaixo de 12. Num ramo
aberto (5/0), fixar qualquer um dos 662 quartos centros deixa o LP entre 9,13 e 9,36, abaixo de 11.
**O LP residual por centros não fecha M = 15 em profundidade 3 ou 4.** A redução por fatia, sim.

## 4. Certificados por instância (o resultado)

`certificar_lp.py`: para cada instância `(s*, K, t)` da lista do GAPS2, monta o sistema 0-1 do OPB
(cobertura, fibras ≥ s*, tamanho, blocos e fatia 0 fixada) e resolve o dual do LP: `y ≥ 0` nas
linhas "≥" e `μ` livre nas "=". Arredonda para inteiros e confere

    Σ y·rhs + Σ μ·rhs  >  Σ_c max(g_c lb_c, g_c ub_c),   g = yᵀG + μᵀE,

o que exclui até soluções fracionárias. Se a raiz não basta, ramifica em `z_c ∈ {0,1}` e
certifica cada folha. `verificar.py` (biblioteca padrão, inteiros) reconstrói cada sistema a
partir de `(s*, K, t)`. Confere cada folha, confere que as folhas formam uma árvore completa e
confere que os registros são exatamente as instâncias da lista, na ordem.

**Medido:** 12 049 instâncias, 12 054 folhas. As instâncias 16 (s* = 3, blocos (6,6)) e 2178
(s* = 5) ramificam, com 5 e 2 folhas; todas as outras fecham na raiz. Suporte médio de y: 78
linhas (máximo 164). 10 842 folhas usam linhas de fibra. Geração: ~20 min em 2 processos.
Conferência: **7 s**. Dados: `dados/K3_6_2_M15_instancias.json.gz` (lista; o sha256 do JSON é
`5a07459e…217e6`) e `dados/K3_6_2_M15_certificados.jsonl.gz` (2,2 MB).

**Por que vale como prova, com a ressalva do estado:** (1) todo código de 15 palavras cai numa
instância da lista, e todas as restrições dela valem para ele. Isso é a completude da redução, com
prova escrita em `GAPS2_K362.md` (inclusive o passo das colunas RGS) e conferida por Burnside no
red team. (2) Cada instância não tem nem solução fracionária, o que o certificado mostra em
aritmética inteira, usando só as cinco famílias de restrições do OPB. Logo não existe código
de 15 palavras, e `K_3(6,2) ≥ 16`.

**Red team já feito:**

- **Erro real pego pelo verificador:** a primeira rodada tinha 5 certificados com `y = −1` (piso de
  um `−1e-12` do solver). A conferência do gerador não exigia `y ≥ 0`, e o verificador independente
  recusou as 5. O gerador agora corta em 0 e recusa y negativo, e as 5 foram regeradas. Há um teste
  de mutação com exatamente esse defeito.
- A lista de instâncias bate, índice a índice, com os 234 registros da rodada RoundingSat/VeriPB do
  GAPS2 (`K3_6_2_M15.jsonl.gz`: s*, blocos e configuração).
- O pipeline reproduz `K_3(5,2) ≥ 8` e `K_2(6,1) ≥ 12`: abaixo do ótimo fica tudo certificado, e
  no ótimo há instâncias sem certificado. Também reproduz `K_3(4,1) ≥ 9`.
- Sanidade contra prova falsa: o código conhecido de 17 palavras, normalizado, satisfaz o sistema
  da sua instância com M = 17, e o LP dessa instância é viável.
- Amostra de M = 16 (201 das 1 603 instâncias com s* ≤ 4): 198 com LP inviável e 3 viáveis na
  raiz. O LP não mata tudo indiscriminadamente.
- Mutações recusadas: y negativo, linhas de cobertura removidas, certificado aplicado a outra
  instância e árvore sem um ramo.

**Red team externo (PR #59, `K3_M15_REDTEAM.md`):** sobrevive com ressalvas de exposição e de
independência; nenhuma é de gravidade alta. Um verificador de Farkas em `Fraction`, escrito do zero,
aceitou as 12 054 folhas. As ressalvas L1, L4 e L5 foram tratadas neste PR: o passo das colunas RGS
está em `GAPS2_K362.md`, este resumo separa prova de diagnóstico, e o `--sha256` é obrigatório.

**O que falta antes de qualquer afirmação pública:** uma enumeração independente da lista (outro
canonicalizador, por exemplo nauty, com comparação de sha256 ou do conjunto de formas) e,
idealmente, conferência dos certificados no Lean. Por regra, nada disso entra no ledger
por este PR.

## Reprodução

    # lista (≈ 22 min, numpy): deve dar o sha256 5a07459e…217e6
    python3 tools/exatos/gaps2/rodar_pb.py --q 3 --n 6 --R 2 --M 15 --listar i15.json
    # certificados (≈ 20 min, 2 processos; numpy + scipy/HiGHS)
    python3 tools/exatos/k362/contagem/certificar_lp.py --q 3 --n 6 --R 2 --M 15 \
        --instancias i15.json --saida c15.jsonl.gz -j 2
    # conferência exata (só biblioteca padrão, ≈ 7 s)
    zcat tools/exatos/k362/contagem/dados/K3_6_2_M15_instancias.json.gz > i15.json
    python3 tools/exatos/k362/contagem/verificar.py --q 3 --n 6 --R 2 --M 15 --instancias i15.json \
        --certificados tools/exatos/k362/contagem/dados/K3_6_2_M15_certificados.jsonl.gz \
        --sha256 5a07459ed8a82a18ad4169739f887c6ec77c90b24576680d40c3650a239217e6
    # tabelas e LPs agregados (+ os 38 ramos)
    python3 tools/exatos/k362/contagem/esferas.py --ramos

## Próximo passo natural (não feito)

M = 16 pela mesma via (vale `K_3(6,2) = 17` se tudo morrer). A amostra acima mostra 3 instâncias
s* ≤ 4 com LP viável na raiz, que pedem ramificação. A lista de s* = 5 para M = 16 tem filtro
`|U| ≤ 121` e ainda não foi gerada.
