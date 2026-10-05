# Regras para agentes neste repositório

Fonte curta e acionável para qualquer agente (Claude Code, Codex, Gemini, o que for). Pessoas leem o
[CONTRIBUTING.md](CONTRIBUTING.md); termos em [docs/GLOSSARIO.md](docs/GLOSSARIO.md); desenho em
[docs/ARQUITETURA.md](docs/ARQUITETURA.md). Se um comando daqui divergir do código ou do CI, quem vale é o código:
corrija este arquivo no mesmo PR.

## Setup (conferido em 2026-10-04)

    python3 -m pip install pytest==8.4.2 numpy==2.4.6    # versões do CI
    tools/verify/check_all.sh                            # compila o verificador em C e confere os 16 códigos
    python3 -m pytest -q -p no:cacheprovider tests       # suíte Python (sem rede)

* `libnauty-dev` (apt) é necessário para `tests/test_motor_exatos.py`; sem ele esse teste **pula**, e o CI não pode pular.
* Os testes do MCP (`infinito/tests`) pedem também as dependências de `infinito/requirements.txt`.
* Lean: `elan` (a versão vem de `lean-toolchain`), depois `lake exe cache get` e `lake build`. Não existe `lake`
  em todo ambiente; se faltar, **diga que não rodou** em vez de supor que passa.
* Vários worktrees na mesma máquina: não copie nem aponte symlink para o `.lake` de outro; use o cache por hardlink
  (`tools/infra/lake_cache.sh ligar`, ver [docs/infra/LAKE_CACHE.md](docs/infra/LAKE_CACHE.md)).
* Trabalhe em um worktree ou branch seu. Não reescreva histórico enviado, não faça `git stash` em checkout compartilhado.

## Como validar

| mexeu em | rode |
|---|---|
| código, ledger, geradores, docs com links | `python3 -m pytest -q -p no:cacheprovider tests` |
| um código em `data/codes/` | `tools/verify/check_all.sh` (ou `python3 scripts/loop/verify_cover.py <arquivo> <q> <n> <R>`) |
| `CoveringLean/` ou `lakefile.toml` | `lake build` (e, para certificados por síndromes, `lake build CoveringSyn`) |
| `infinito/` | `python3 -m pytest -q -p no:cacheprovider infinito/tests` |
| ledger (fontes) | `python3 ledger/build.py` e depois os testes; nunca edite `ledger/cells.json` à mão |

Cole no corpo do PR o comando e a contagem de testes. "Rodou sem erro" não é prova.

## Nunca

* **Alterar número do ledger à mão** (`ledger/cells.json`, `ledger/ours.json`): ele sai de `ledger/build.py` e do
  loop de recordes. Todo código novo leva registro de proveniência com os seis campos (ver `ledger/README.md`).
* **Afirmar recorde, "melhor conhecido" ou "novo" sem avaliador exato.** Primeiro `tools/verify/verify`; depois, se for
  teorema, o Lean. Um `INFEASIBLE` de busca não prova inexistência.
* **Mexer em `CoveringLean/` sem `lake build` verde.** Não introduza `sorry`, `native_decide` nem axioma novo.
* Alterar `data/`, `ledger/*.json` publicados, `paper/` ou a tag de versão sem ordem explícita do mantenedor.
* Pôr segredo, token, URL do Infinito, `/home/...` ou IP interno em arquivo versionado. Para provar que um segredo
  existe, imprima o tamanho.
* Desligar, pular ou afrouxar teste e gate para passar o CI. Nunca publicar (Zenodo, site) nem fazer merge: isso é do dono.
* Escrever o nome do modelo ou do motor em commit, arquivo ou texto.

## Commit e PR

* Commit: `tipo(escopo): descrição` em português, `tipo` entre `feat|fix|docs|refactor|test|chore|ci`, com o rodapé
  `Co-Authored-By: James.V1 <noreply@factory.mybagcenter.com>`.
* PR: uma coisa só, até ~400 linhas alteradas; o corpo traz o que mudou, por que, o comando e o resultado, o que ficou
  de fora e `Risco: baixo|médio|alto — motivo`. Risco alto (workflows, `infinito/`, `CoveringLean/` com mudança de
  enunciado, dado publicado) só o mantenedor aprova.
* Português do Brasil com acento em docs, commits e textos visíveis.

## O MCP Infinito

Ferramentas de pesquisa com orçamento por pessoa (US$ 20, teto em código). Comece por `meus_creditos`. Leia
[infinito/README.md](infinito/README.md) antes de gastar. Tudo que custa é seco por padrão (mostra preço e saldo) e só
roda com `confirmar=true`.

| ferramenta | para quê | custa? |
|---|---|---|
| `celula` | uma célula do ledger (`"K7(9,4)"` ou `"7,9,4"`): cotas, fontes e o nosso estado | não |
| `alvos` | células ranqueadas por chance de melhorar (`limite`, `max_espaco`) | não |
| `verificar_codigo` | verificador exato em C num arquivo de `data/codes/` (`q<Q>_n<N>_R<R>_M<M>.txt`) | não |
| `papers_buscar` | arXiv, OpenAlex, Semantic Scholar ou Zenodo (`fonte`); repetida volta do cache | não |
| `pesado` | trabalho pesado na VM (`lake_build`, `verificar_grande`); veja `pesado_tipos` e acompanhe com `pesado_status` | sim |
| `gemini` | modelo de linguagem; reserva o pior caso e cobra os tokens medidos | sim |

Antes de gastar: rode `pesado` ou `gemini` sem `confirmar` para ver custo e saldo. Resposta de `gemini` é hipótese,
nunca prova. A URL pessoal é a senha: nunca em issue, PR ou log.

## Onde reportar atrito

Algo confuso, um comando que não roda, regra que contradiz o código ou um erro seu: abra uma issue com `atrito:` no título
dizendo o comando, a saída e o que você esperava. Erro é medida do que
falta de regra: descreva o defeito, não a pessoa, e se possível proponha o teste ou a linha de documento que o evita.
Segurança vai por e-mail, não por issue: ver [SECURITY.md](SECURITY.md).
