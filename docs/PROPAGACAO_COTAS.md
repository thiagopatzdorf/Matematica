# Propagação de cotas: o que muda por consequência

`tools/propagar/propagar.py` aplica as desigualdades provadas entre células `K_q(n,R)` até o ponto fixo, partindo
de (a) o ledger atual e (b) o ledger mais os resultados novos. Ele responde a três perguntas: o ledger se contradiz?
O que um resultado novo implica nas outras células? Que célula fica exata? Nada aqui escreve no ledger.

```bash
python3 tools/propagar/propagar.py                          # cenários (a) e (b), com as cadeias
python3 tools/propagar/propagar.py --json rel.json          # o mesmo em JSON
python3 tools/propagar/propagar.py --novo 7,5,3:lb=17,ub=17 # e se K7(5,3) = 17?
python3 -m pytest -q -p no:cacheprovider tests/test_propagar.py
```

Sai com código 1 se houver inconsistência (`lb > ub` em alguma célula), para servir de gate.

## Regras usadas, e de onde vem cada uma

Toda regra de cota superior é um teorema de [`CoveringLean/Regras.lean`](../CoveringLean/Regras.lean), e todas são
clássicas (Cohen, Honkala, Litsyn e Lobstein, *Covering Codes*, North-Holland 1997, cap. 3; as mesmas regras
aparecem nas tabelas de Kéri). A cota inferior sai da **mesma** desigualdade lida ao contrário: se
`K(A) ≤ f(K(B))` vale para os números verdadeiros, com `f` crescente, então `lb(A) ≤ K(A) ≤ f(K(B))` e daí
uma inferior para `K(B)`. Nenhuma regra nova entra, só contrapositiva.

| regra | teorema (Lean) | cota superior | cota inferior (contrapositiva) |
|---|---|---|---|
| monotonia do raio | `UB.radius_mono` | `K(n,R+1) ≤ K(n,R)` | `K(n,R) ≥ K(n,R+1)` |
| alongamento livre | `UB.lengthen_free` | `K(n+1,R+1) ≤ K(n,R)` | `K(n,R) ≥ K(n+1,R+1)` |
| coordenada muda | `UB.lengthen_dummy` | `K(n+1,R) ≤ q·K(n,R)` | `K(n,R) ≥ ⌈K(n+1,R)/q⌉` |
| punção | `UB.puncture` | `K(n,R) ≤ K(n+1,R)` | `K(n+1,R) ≥ K(n,R)` |
| projeção de alfabeto | `UB.project` | `K_a(n,R) ≤ K_q(n,R)`, `a ≤ q` | `K_q(n,R) ≥ K_a(n,R)` |
| soma direta | `UB.direct_sum` | `K(n₁+n₂,R₁+R₂) ≤ K(n₁,R₁)·K(n₂,R₂)` | `K(n₁,R₁) ≥ ⌈K(n₁+n₂,R₁+R₂)/K(n₂,R₂)⌉` |
| raio grande | `UB.large_radius` | `n ≤ R ⇒ K = 1` | — |
| palavras constantes | `UB.constant_symbol` | `q(n−R−1) < n ⇒ K ≤ q` | — |
| cota da esfera | (clássica, *Covering Codes* cap. 6) | — | `K ≥ ⌈qⁿ / V_q(n,R)⌉` |

Conferência das direções sugeridas na missão: `K_q(n,R) ≤ q·K_q(n−1,R)` é a coordenada muda;
`K_q(n+1,R+1) ≤ K_q(n,R)` é o alongamento livre; `K_q(n,R) ≥ K_q(n+1,R)/q` está **certa** (contrapositiva da
coordenada muda); `K_q(n,R) ≥ K_{q−1}(n,R)` está **certa** (contrapositiva da projeção). A direção errada é
pega: com a punção invertida o ledger real dá 1674 contradições, com a projeção invertida, 1034 (medido em
2026-10-05, mutando o script).

**Domínio.** Para cada `q`, todo `(n,R)` com `1 ≤ n ≤ N_q` (o maior `n` da tabela) e `0 ≤ R ≤ n`. As células fora
das 1145 (`R = 0`, `R` acima do teto da tabela) entram só como passo intermediário, com a esfera, `qⁿ`, raio
grande e palavras constantes como base, e não são reportadas. Os valores de partida da tabela são `best.ub`
(que já conta os nossos códigos de `data/codes/`) e `certification.lb.value`.

**Limite declarado.** Ficam de fora regras que exigem hipótese não registrada no ledger (soma direta amalgamada,
que pede código normal), regras de alfabeto produto e as cotas inferiores fortes (excesso, van Wee, SDP): elas
já estão nos valores do ledger quando alguém as aplicou, mas o propagador não as reaplica em célula nova.

## Resultado em 2026-10-05

### (1) Inconsistências no ledger atual: nenhuma

Nenhuma célula fica com `lb > ub` depois do ponto fixo, nem em (a) nem em (b).

### O ledger atual não é fechado pelas regras: duas melhorias implicadas

Não são contradições, são cotas que o próprio ledger já implica e não registra.

* **K17(7,2) ≤ 245208** (ledger: 252735, Kéri). Cadeia: `K17(6,2) ≤ 14424` (ledger, Kéri) e coordenada muda,
  `K17(7,2) ≤ 17·14424 = 245208`. Vale tanto quanto o 14424 do Kéri, que não está formalizado aqui (o banco Lean do
  Florath só chega a 41905 nessa célula). Ou a tabela do Kéri deixou de aplicar a regra, ou o 14424 está mal
  transcrito; nos dois casos vale conferir na fonte antes de usar.
* **K17(8,4) ≥ 1507** (ledger: 1464, Marosi 2026, SDP). Cadeia: `K16(8,4) ≥ 1507` (ledger, Kéri) e projeção de
  alfabeto, `K17(8,4) ≥ K16(8,4)`. A série de `q = 12` a `16` (513, 684, 917, 1181, 1507) fica bem acima da esfera,
  e a de `q = 17` em diante, colada nela: o método que deu a inferior até `q = 16` não foi estendido. A melhoria
  passa a inferior SDP do Marosi; depende só do 1507 do Kéri.

Esses dois valores ficam presos num teste de regressão (`tests/test_propagar.py`): quando o ledger absorver ou
corrigir algum deles, o teste avisa.

### (2) Melhorias por consequência dos resultados novos: nenhuma

Cenário (b): K3(6,2) = 17, K7(6,4) = 14, K7(5,3) ≥ 16 e K7(4,2) = 19. O ponto fixo de (b) difere do de (a) só nas
próprias células novas. O motivo é a folga: cada vizinho já tem cota melhor que a implicada (`b_implicacoes` no
JSON lista tudo; os casos mais apertados):

| resultado | regra | implica | o vizinho já tem |
|---|---|---|---|
| K7(6,4) ≥ 14 | projeção | K8(6,4) ≥ 14 | ≥ 15 |
| K7(6,4) ≥ 14 | alongamento (contrapositiva) | K7(5,3) ≥ 14 | ≥ 16 (novo) |
| K7(6,4) ≤ 14 | alongamento | K7(7,5) ≤ 14 | ≤ 11 |
| K7(5,3) ≥ 16 | projeção | K8(5,3) ≥ 16 | ≥ 17 |
| K7(5,3) ≥ 16 | alongamento (contrapositiva) | K7(4,2) ≥ 16 | = 19 |
| K3(6,2) ≥ 17 | alongamento (contrapositiva) | K3(5,1) ≥ 17 | = 27 |
| K3(6,2) ≥ 17 | punção | K3(7,2) ≥ 17 | ≥ 27 |
| K3(6,2) ≤ 17 | alongamento | K3(7,3) ≤ 17 | ≤ 12 |

A soma direta também não fecha nada: o propagador testa todos os pares e nenhum melhora.

### (3) Células que ficam exatas

Só as próprias: **K3(6,2) = 17** e **K7(6,4) = 14**. Se K7(5,3) ≥ 17 sair, **K7(5,3) = 17** fica exata
(`--novo 7,5,3:lb=17` confirma, e de novo sem consequência fora dela). Nenhuma célula fica exata por consequência.

## Como usar quando sair resultado novo

Rode com `--novo q,n,R:lb=…,ub=…` (repetível). Se `b_melhorias_por_consequencia` vier vazio, a seção
`b_implicacoes` diz por quanto cada vizinho escapou. Uma melhoria implicada não é recorde até virar ledger pelo
caminho normal (`ledger/build.py` e, se for teorema, o Lean com a regra correspondente de `Regras.lean`).
