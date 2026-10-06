## O que mudou

<!-- Uma ou duas frases. Se mexeu num cartão (problems/cartoes/*.json): qual `id` e qual transição.
     Se mexeu numa célula do ledger: qual célula, valor antes → depois. -->

## Por quê

## Como validei

<!-- A prova. Cole o comando e o resultado (contagem de testes, saída do avaliador). "Rodou sem erro" não conta. -->

```
python3 -m pytest -q tests infinito/tests
ruff check <arquivos .py alterados>
python3 tools/problems/validate.py --all        # se mexeu em problems/
tools/verify/check_all.sh                        # se mexeu em data/codes/
lake build                                       # se mexeu em CoveringLean/
```

## Estado

<!-- Se o PR afirma uma cota ou resultado: em que degrau da escada ele fica, e qual evidência sustenta esse degrau.
     CLAIMED → WITNESS_CHECKED → CERTIFICATE_VERIFIED → INDEPENDENTLY_REPRODUCED → FORMALIZED.
     Nunca suba o estado acima da evidência. Novidade na literatura é afirmação nossa, não do Lean.
     Se o PR não afirma resultado, escreva "não se aplica". -->

## O que ficou de fora

Risco: baixo|médio|alto — motivo

<!-- baixo: só docs. médio: código com teste. alto: .github/workflows/, infinito/, CoveringLean/ (enunciado
     ou definição), dados já publicados (ledger/, data/, paper/), deploy. Detalhes em CONTRIBUTING.md. -->

Closes #N
