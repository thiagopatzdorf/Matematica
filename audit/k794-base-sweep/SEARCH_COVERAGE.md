# Cobertura da varredura de bases para K_7(9,4)

## Qual é o espaço

A família varrida é a das **bases com 3 classes laterais**. Uma base é a união
`(r_0 + C_0) ∪ (r_1 + C_0) ∪ (r_2 + C_0)` de três classes laterais de um código linear
`C_0 = [9,3]_7`, com `C_0 = ker H` e `H` uma matriz 6×9.

Para cada código `C_0`, interessa o número mínimo de **síndromes órfãs** sobre todos os trios de
síndromes `{s_0, s_1, s_2}`. Uma síndrome é órfã quando nenhuma palavra das três classes cobre,
com raio 4, as 343 palavras dela.

```
órfãs(C_0) = min_{trios {0, s1, s2}} | Bc ∩ (Bc + s1) ∩ (Bc + s2) |,   B = { H e : wt(e) <= 4 }
```

## Cadeia de redução

| passo | afirmação | status | onde |
|---|---|---|---|
| 1 | `órfãs` é invariante por equivalência monomial de `C_0` (permutação e escala de coordenadas) | provado no papel | `docs/audit/enum_completeness.md` §4 (kit) |
| 2 | `órfãs` só depende do trio a menos de translação e de escalar | provado no papel | `docs/audit/exactT2_correctness.md`, Lema 0 (kit) |
| 3 | as classes monomiais de `[9,3]_7` **não degeneradas** (sem coluna nula e com 4 pontos em posição geral) são exatamente as 6362 de `classes_sorted.jsonl` | verificado por computador: fórmula de massa `Σ |PGL(3,7)|/|Stab| = 31 931 793 642` = número de 9-multiconjuntos de PG(2,7) com referencial; enumeração independente reproduz as 6362 formas canônicas; 0 duplicatas | `docs/audit/enum_completeness.md` §2 |
| 4 | as classes **degeneradas** são 1375: 1297 com coluna nula e 78 sem referencial | verificado por computador (fórmula de massa por tipo) | `data/audit/degenerate_summary.json` (kit) |
| 5 | o mínimo exato de `órfãs` em cada uma das 6362 + 1375 classes, com limiar T = 8 | **computado** por um único binário otimizado (`exactT2`), cuja exatidão é **argumentada** (`exactT2_correctness.md`) e **testada** por amostra: diferencial em 14 classes estratificadas, mais FFT sem poda na classe 1. A recontagem independente das 7737 classes **não** foi feita | `data/RESULTS.csv`, `COMPUTE_CERTIFICATE.json` |

Juntos, os passos 1–5 dão o **mínimo de órfãs na família inteira** das bases com 3 classes
laterais de um `[9,3]_7` (7737 classes monomiais), **condicionado** à exatidão do `exactT2`.
Essa exatidão está argumentada e testada por amostra, mas o programa não está verificado formalmente
e a varredura não foi refeita de forma independente. Os passos 1–4 não dependem dele.

## O que esta varredura NÃO cobre

- Bases com outro número de classes laterais (t ≠ 3), ou de outra dimensão (`[9,k]_7` com k ≠ 3).
- Códigos que não são união de classes laterais mais um remendo. Ou seja: **nada aqui é cota
  inferior para K_7(9,4)**. A cota inferior conhecida segue 264 (Kéri).
- O tamanho do remendo. A varredura mede órfãs, não palavras. Que a base com menos órfãs leve ao
  menor código é heurística, não teorema.

## O que significa o limiar T = 8

Para cada classe, a computação lista **todos** os trios com órfãs ≤ 8 e relata o mínimo, ou "nenhum"
(`orphans = -1`). Logo:

- o valor exato do mínimo só é conhecido nas classes com mínimo ≤ 8;
- nas demais, o resultado certificado é "mínimo ≥ 9". Uma rodada à parte com T = 20,
  nas 120 primeiras classes (ainda parcial), aparece em `FINAL_AUDIT.md`.
