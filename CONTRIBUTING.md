# Como contribuir

Vale para pessoas e para agentes. Agentes leem também o [AGENTS.md](AGENTS.md), que é a versão curta e acionável.
Termos técnicos estão em [docs/GLOSSARIO.md](docs/GLOSSARIO.md); o desenho do sistema, em
[docs/ARQUITETURA.md](docs/ARQUITETURA.md).

## O ciclo: proposta, reivindicação, candidato, verificação, certificado, publicação

| etapa | o que acontece | onde fica hoje |
|---|---|---|
| 1. proposta | alguém aponta um problema ou uma célula `K_q(n,R)` que vale atacar | uma issue; `python3 ledger/targets.py --top 10` ranqueia células |
| 2. reivindicação | você avisa que está nela, para ninguém duplicar a busca | um comentário na issue, com prazo e método |
| 3. candidato | um código (ou argumento) achado por busca, heurística ou construção | arquivo `data/codes/q<q>_n<n>_R<R>_M<M>.txt`, uma palavra por linha |
| 4. verificação | um avaliador exato confere; só ele decide | `tools/verify/check_all.sh` (ou `scripts/loop/verify_cover.py`) |
| 5. certificado | a prova que o kernel do Lean aceita | `scripts/syndrome/gen_syn.py` gera os módulos; `lake build` confere |
| 6. publicação | cota entra no ledger, na nota e no site; versão no Zenodo | **é do dono do repositório** (mantenedor), nunca de um agente |

O atalho das etapas 3 e 4 é o loop de recordes: `python3 scripts/loop/record_loop.py --celula "K2(4,1)"` mostra o
plano (seco por padrão); com `--executar` gera, verifica, registra no ledger e prepara a pasta do certificado.

## O que conta como prova

* **Cota superior** (existe um código com `M` palavras): o verificador exato em C, `tools/verify/verify`, que confere
  que as palavras são distintas, que `|C| = M` e que **todo** ponto do espaço está a distância ≤ `R` de alguma delas.
  Vira teorema só com o certificado no Lean (kernel, sem `sorry`, sem `native_decide`).
* **Cota inferior ou inexistência** ("não há código menor"): prova no Lean ou prova SAT/LRAT verificada de forma
  independente. Um `INFEASIBLE` ou `NAO_EXISTE` de script de busca **não** é prova (ver `tools/exatos/README.md`).
* **Novidade** ("melhor que a literatura"): é afirmação nossa, nunca do Lean. Cite a fonte comparada e a data da
  conferência, como em `docs/literatura/STATE_OF_ART.md`. Não chame de "recorde mundial" o que foi só "o menor valor que achamos".
* **Nunca** conta: opinião de modelo, "rodou sem erro", número sem comando que o reproduza. Cole o comando e a saída.

## Pull requests

* **Um PR, um assunto, pequeno**: mire em até ~400 linhas alteradas, sem contar dado gerado. Passou disso, quebre em
  partes (`parte 1 de 3`) e diga no corpo o que fica para o próximo.
* **Teste que falha sem a mudança**, com nome que descreve a falha (por exemplo
  `test_link_do_readme_aponta_para_arquivo_que_nao_existe`). Não desligue nem afrouxe teste para passar.
* **Corpo do PR**: o que mudou, por que, o comando que você rodou e o resultado (contagem de testes), o que ficou de
  fora e a linha `Risco: baixo|médio|alto — motivo`.
* **Commit**: Conventional Commits em português, `tipo(escopo): descrição`, com `tipo` entre `feat`, `fix`, `docs`,
  `refactor`, `test`, `chore` e `ci`. Commits feitos por agentes do mantenedor levam o rodapé
  `Co-Authored-By: James.V1 <noreply@factory.mybagcenter.com>`; nunca o nome do modelo ou do motor. Pessoas assinam
  como são.
* **Idioma**: português do Brasil, com acento, em docs, issues, commits e textos visíveis. Identificadores de código
  seguem o arquivo vizinho. Inglês vale onde faz a ideia chegar.
* **Nunca** no Git: segredo, token, URL pessoal do Infinito, caminho de máquina (`/home/...`) ou IP interno.

### Classes de risco e revisão

| risco | o que é | quem aprova |
|---|---|---|
| baixo | só documentação, comentário, texto | uma revisão |
| médio | código com teste (geradores, avaliadores, scripts, dados novos que passam no verificador) | uma revisão, com o teste verde no CI |
| alto | `.github/workflows/`, `infinito/` (infra, segredos, créditos), `CoveringLean/` (mudança de enunciado ou de definição), dados já publicados (`ledger/`, `data/`, `paper/`), qualquer deploy | só o mantenedor |

A classe é a do arquivo mais arriscado do diff; na dúvida, suba a classe. Mudança em `CoveringLean/` exige `lake build`
verde no corpo do PR. Número do ledger não se edita à mão: ele sai de `ledger/build.py` e do loop de recordes.

## Crédito de infra pelo Infinito

O MCP Infinito dá a cada colaborador convidado um teto de **US$ 20 de infra**, aplicado em código (até 10 pessoas).
Consultar o ledger e verificar códigos é grátis; computação pesada e Gemini custam crédito e só rodam com
`confirmar=true`. Quem convida e aumenta crédito é o administrador. Detalhes e a lista de ferramentas em
[infinito/README.md](infinito/README.md). A URL pessoal é a senha: nunca em issue, PR ou chat.

## Revisão

A revisão confere três coisas, nesta ordem: (1) o avaliador exato aprova o candidato, reproduzido por quem revisa;
(2) o enunciado formal diz o que a nota diz (revisão humana dos enunciados, como em `docs/validacao/LEAN_REVIEW.md`); (3) nada que
não foi medido virou afirmação. Quem revisa pergunta o que tornou o erro provável, não quem errou.

## Além dos códigos de cobertura

O hub já tem as três peças para receber problemas de outros domínios:

* **registro de problemas** em [problems/](problems/README.md): um Cartão por problema (enunciado, avaliador, estado,
  quem reivindicou), com as regras em [problems/SPEC.md](problems/SPEC.md) e os formulários de issue
  "Proposta de problema" e "Submissão de candidato";
* **avaliadores** em [evaluators/](evaluators/README.md): um avaliador exato por tipo de problema, todos com o mesmo
  contrato (entrada candidata; saída aprovado, reprovado ou não avaliável, com motivo);
* **mapa público** em [site/](site/README.md), gerado do ledger.

Se você quer propor um domínio novo, abra uma issue descrevendo qual seria o avaliador barato e exato: sem ele o
problema ainda é subjetivo. Achou algo que o repositório afirma e não se sustenta? Use o formulário
"Erro em certificado ou no ledger"; um erro achado vale mais que um acerto, porque vira regra.
