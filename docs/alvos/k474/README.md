# K₄(7,4) ≤ 10: testemunha explícita

A cota superior 10 é da literatura (Rivas Soriano, chave do Kéri), mas o código não estava no repo.
Com a cota inferior K₄(7,4) ≥ 10 provada por LRAT na campanha de 2026-10-07 (fibras, 792 perfis de
M = 9 todos UNSAT), este arquivo fecha o par: **K₄(7,4) = 10**, com as duas metades conferíveis aqui.

| arquivo | o que é |
|---|---|
| `q4_n7_R4_M10.txt` | 10 palavras de F₄⁷ (dígito `k` da linha = coordenada `k`), raio de cobertura 4 |

Conferido com os dois verificadores do repo:

    tools/verify/verify docs/alvos/k474/q4_n7_R4_M10.txt
    q=4 n=7 R=4 M=10 points=16384 uncovered=0 sha256=f2abfa603967023157efdd98786f7bdce44efcc103006ed525b661728475aac7

    python3 scripts/loop/verify_cover.py docs/alvos/k474/q4_n7_R4_M10.txt 4 7 4
    {"ok": true, "q": 4, "n": 7, "R": 4, "M": 10, "distintas": 10, "descobertas": 0}

Proveniência: `tools/busca_direta/tabu.c` (busca tabu direta), `./tabu 4 7 4 14 120 1 prefixo`,
semente 1, na primeira dezena de segundos (as sementes 2 e 3 também acharam 10; com 9 palavras, nenhuma
das 4 sementes zerou em 120 s, melhor = 108 pontos descobertos, o que é esperado dado o LRAT).
Ledger e `data/codes/` não foram mexidos: registrar a célula como exata é do fluxo do ledger.
