# problems/: registro de problemas

Cada problema é um **cartão** (`cartoes/<id>.json`, regras em [SPEC.md](SPEC.md), referências em
[PRIOR_ART.md](PRIOR_ART.md)). Hoje há 5, semeados do ledger e de `tools/exatos`:
K_7(9,4), K_7(10,4), K_7(8,3), K_5(10,4) (cotas superiores com Lean) e K_7(4,2) (valor exato, LRAT).

```
python3 tools/problems/validate.py --all        # confere todos os cartões
```

## Propor

Abra a issue **Proposta de problema** (os campos são os do cartão). Um mantenedor aceita ou
arquiva com motivo. Sem avaliador exato não vira `aberto`. Para propor por PR, parta de um cartão existente,
deixe só a entrada `proposto` no histórico e valide:

```
python3 - <<'PY'
import json, pathlib
c = json.loads(pathlib.Path("problems/cartoes/cobertura-k7-9-4-ub.json").read_text())
c.update(id="cobertura-k7-9-5-ub", titulo="K_7(9,5): cota superior", estado="proposto", celula_ledger=None,
         enunciado_formal=None, nosso={"valor": None, "estado": "nenhum", "prova": None})
c["historico"] = [{"quem": "seu-usuario", "papel": "qualquer", "quando": "2026-10-04",
                   "de": None, "para": "proposto", "evidencia": {}}]
pathlib.Path("problems/cartoes/cobertura-k7-9-5-ub.json").write_text(json.dumps(c, ensure_ascii=False, indent=2) + "\n")
PY
python3 tools/problems/validate.py problems/cartoes/cobertura-k7-9-5-ub.json   # ok, 1/1 válidos
rm problems/cartoes/cobertura-k7-9-5-ub.json                                    # é só o exemplo
```

## Reivindicar

Comente na issue do problema e abra o PR que passa o cartão a `reivindicado`, com `expira_em` de
até 30 dias. A reivindicação expira sozinha; só quem reivindicou submete o candidato nesse prazo.

## Submeter um candidato

Abra a issue **Submissão de candidato** com o artefato, o `sha256`, o comando do avaliador e a
saída inteira. Rode antes o avaliador do cartão (`avaliador.como_rodar`); sem a saída anexada, não
há `verificado`. O PR usa o template de `.github/pull_request_template.md`.

## Resolver

`candidato → verificado` (saída do avaliador exato) → `certificado` (kernel do Lean) → `publicado`
(só o dono). Resultado com prova LRAT mas sem Lean fica em `verificado`.

## Para quem mexe nas ferramentas

* `tools/problems/lifecycle.py`: estados, papéis, transições e evidência exigida.
* `tools/problems/validate.py`: o validador (`--all`, `--json`, saída ≠ 0 se algum cartão for inválido).
* `tools/problems/seed_from_ledger.py`: regera os cartões semeados (determinístico). `--reverificar`
  roda o verificador (~1 min) e refaz `evidencias/`.
* Testes: `python3 -m pytest -q -p no:cacheprovider tests/test_problems*.py`.
