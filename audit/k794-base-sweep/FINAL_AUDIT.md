# Auditoria final: varredura de bases para K_7(9,4) (2026-10-02)

Dois resultados de natureza diferente, que não se misturam:

| | o que é | status |
|---|---|---|
| **Teorema** | `K_7(9,4) ≤ 1137` | provado em Lean 4 e checado pelo kernel (`Syn.K7_9_4_le_1137_syn`); não depende desta varredura |
| **Computação** | mínimo de síndromes órfãs = 6 nas 7737 classes de bases de 3 classes laterais de um `[9,3]_7`, atingido por uma única classe | computado e auditado; condicionado à exatidão do `exactT2` (argumentada e testada por amostra) |

## A. Qual é o melhor bound provado?

`K_7(9,4) ≤ 1137`. O intervalo conhecido é `264 ≤ K_7(9,4) ≤ 1137`, com a cota inferior de Kéri.
A cota publicada anterior era 1475 (Marosi, arXiv:2608.19872v3).

## B. O que o Lean certifica exatamente?

```
theorem Syn.K7_9_4_le_1137_syn :
  ∃ C : Finset (Fin 9 → ZMod 7), C.card = 1137 ∧ CoveringA2.Covers 4 C
```

Isto é: existe um código explícito de 1137 palavras em `(Z/7)^9` que cobre todo o espaço com raio de
Hamming 4 (`hammingDist` do Mathlib). O `#print axioms` mostra só `propext`, `Classical.choice` e
`Quot.sound`; não há `sorry` nem `native_decide`. O Lean **não** certifica nada sobre a varredura
nem sobre a otimalidade.

## C. Quantos casos foram examinados?

7737 classes monomiais de `[9,3]_7`:

- **6362 não degeneradas.** A lista é completa: a fórmula de massa fecha em 31 931 793 642, e duas
  enumerações independentes, com formas canônicas diferentes, chegam ao mesmo resultado.
- **1375 degeneradas:** 1297 com coluna nula e 78 sem referencial.

Para cada classe foram listados **todos** os trios com até 8 órfãs (T = 8). O registro por classe
está em `data/RESULTS.csv`.

## D. Houve ausentes ou duplicatas?

Não. Nas duas listas: missing = 0, duplicates = 0, divergent = 0, A trocado = 0, saída inexata = 0,
arquivo estranho = 0 (`ledger_sweep.py`). O red team reconferiu isso de forma independente
(`rt_coverage.py`, lendo o A de dentro de cada arquivo), e as 62 cópias locais são idênticas byte a
byte às do shard.

## E. Implementações independentes concordaram?

Sim, em todo o domínio comum testado:

- T = 8, amostra estratificada de **14 classes** (mínimo, Q25, mediana, Q75, máximo e sorteadas):
  exactT = exactT2 = verify_trios em 14/14;
- classe 1: T = 10, as três iguais (3 órbitas); T = 30, exactT = exactT2 (1992 órbitas);
- **FFT sem poda** (red team), classe 1: as mesmas 3 órbitas e o mesmo mínimo 6.

Limites: o `verify_trios` é independente na implementação, não no método de poda. A semente da
amostra é fixa. A recontagem completa sem o `exactT2` não foi feita (~200–550 h de CPU). Ainda em
andamento, e não bloqueantes: T = 30 nas classes 2, 3 e 5; classe 2 com T = 25, sementes e sym=0/1
(red team).

## F. T = 20 ou as degeneradas produziram melhoria?

Não.

- **Degeneradas:** nenhuma das 1375 tem trio com ≤ 8 órfãs.
- **T = 20:** nas 38 classes de menor |Bc| já rodadas (de 120), só a classe 1 tem trio com ≤ 20
  órfãs. A 2ª melhor classe tem mínimo ≥ 21 nessa faixa; nas demais, o certificado é "≥ 9".
- **Nenhuma construção com menos de 1137 palavras apareceu.**

**Residual da base campeã** (exato, `docs/audit/champion_and_residual.md`):

| | valor |
|---|---|
| pontos órfãos | 2058 |
| máximo de órfãos numa bola de raio 4 | 24 |
| cota inferior do remendo | 86 (LP = 85,75, com certificado dual) |
| remendo usado | 108 |
| gap | 22 |
| menor código possível com esta base | 1115 |

**Estrutura da campeã:** o código é `[9,3,6]_7`, quase-MDS, com o menor |Bc| de todas as classes. Os
9 pontos formam um "triângulo de Hesse torcido", com estabilizador de ordem 54. As 6 órfãs formam
uma única órbita. As outras bases comparadas são do tipo "cônica + 1 ponto", com estabilizadores 16 e
12; isso é uma correlação medida em 3 bases, não um teorema.

## G. Quanto foi gasto?

~US$1,25 estimados, contra um teto de US$25: e2 + t2d spot para as 6362 (US$1,02) e t2d spot para as
degeneradas (US$0,23). Todas as VMs foram destruídas depois de entregar.

## H. Qual afirmação pública é justificável agora?

Justificável:

- "K_7(9,4) ≤ 1137, provado em Lean 4 e checado pelo kernel" (já publicado na v0.5).
- "Entre as bases formadas por 3 classes laterais de um código linear [9,3]_7 (todas as 7737 classes
  monomiais), o menor número de síndromes órfãs é 6, atingido por uma única classe; resultado
  computacional, auditado, condicionado à exatidão do programa de busca."
- "Com essa base, o remendo precisa de pelo menos 86 palavras; usamos 108."

Não justificável:

- que 1137 seja ótimo;
- qualquer cota inferior para K_7(9,4) vinda desta busca;
- que a base campeã seja a melhor fora da família "3 classes laterais de um [9,3]_7".

**A versão pública (v0.5) não muda:** a varredura não trouxe bound novo. Não há Zenodo novo, DOI
novo nem post.

## Próximo experimento exato mais barato (não executado; seria campanha nova)

Refutar um remendo de 86 palavras na base campeã por SAT ou cobertura exata. Com 86 palavras a folga
é 24·86 − 2058 = 6, o que força um quase-ladrilhamento rígido de cada classe órfã. Se der UNSAT, a cota
inferior do remendo nessa base sobe para 87. Custo: CPU local, sem nuvem.
