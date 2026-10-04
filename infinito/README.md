# ∞ Infinito

<!-- resumo: MCP universal com orçamento por pessoa (até 10, US$ 20 cada, ajustável pela MCP interna); a matemática é o primeiro módulo. -->

MCP para colaboradores do repo `Matematica`. Cada pessoa recebe **uma URL pessoal** (`https://<host>/mcp/<token>/`,
o mesmo padrão do MCP da Factory), cola em Configurações > Conectores > Adicionar conector personalizado e usa as
ferramentas com um **teto de infra em dólares aplicado em código**. Alternativa: `INF_AUTH=access` (Cloudflare Access).
Desenhado para virar universal: a matemática é só o primeiro módulo (`infinito_mcp/modulos/`).

## O que existe

| módulo | tools | custa crédito? |
|---|---|---|
| núcleo | `meus_creditos`, `admin_usuarios`, `admin_creditos` | não |
| `matematica` | `celula`, `alvos`, `nossos_resultados`, `codigos`, `verificar_codigo`, `documento` | não (leitura e verificador exato) |
| `papers` | `papers_buscar` (arXiv, OpenAlex, Semantic Scholar, Zenodo), `paper_guardar`, `biblioteca_buscar` | não (APIs abertas; busca repetida vem do cache do bucket) |
| `pesado` | `pesado_tipos`, `pesado` | **sim** (computação) — reserva antes, confirma depois |
| `gemini` | `gemini` | **sim** — reserva o pior caso, cobra os tokens medidos pela API |
| acesso (admin) | `admin_convidar`, `admin_revogar`, `admin_acessos` | não |

Publicar (Zenodo, site) e fazer merge **não existem aqui**: continuam com o dono.

## Dinheiro

* Até `INF_MAX_USUARIOS` pessoas (padrão **10**); a 11ª recebe "lotado". O administrador não ocupa vaga.
* Teto de cada pessoa: `INF_TETO_PADRAO_USD` (padrão **20**), guardado no ledger do bucket, não no código.
* **Aumentar crédito**: `admin_creditos(email, somar_usd=10, motivo="...")`. Só administrador (e-mail em
  `INF_ADMINS`) ou token de serviço do Access (`INF_TOKENS_SERVICO`) — é o caminho da MCP interna da Factory,
  que chama o Infinito como serviço. Motivo obrigatório; cada mudança vira um evento.
* **O crédito cobre computação e Gemini.** Preços do Gemini em `INF_GEMINI_PRECOS` (US$/milhão de tokens); os padrões
  (gemini-3.8-flash, 3.5-flash, 3.1-pro-preview) vêm da página oficial lida em 2026-10-03; reconfira antes de aumentar crédito.
  **A chave do cofre está sem créditos pré-pagos (HTTP 402 em 2026-10-03):** até recarregar no AI Studio, `gemini` falha
  e desfaz a reserva.
* Reserva aberta já conta como gasto (duas chamadas paralelas não furam o teto). Sem ledger, nada que custa roda.

## Acesso por URL com token

* `admin_convidar(nome, email)` abre uma vaga, gera o token e devolve a URL **uma única vez**; no ledger fica só o
  sha256. `admin_revogar(email)` corta a pessoa sem afetar as outras. Token errado ou revogado dá 404 genérico.
* Quem convida é o administrador: o token da MCP interna da Factory (`INF_TOKEN_ADMIN`, vem do cofre).
* A URL é a senha: por canal privado, nunca em chat, issue ou PR. **Cuidado no Cloud Run:** o log de requisição
  registra o caminho, ou seja, o token. Exclua `run.googleapis.com/requests` do Logging (ou use `INF_AUTH=access`).

## Quem está usando (consulta fácil)

`admin_usuarios` (só admin) devolve, ordenado por quem usou há menos tempo: nome, e-mail, chamadas, primeira e última
atividade, as 3 tools mais usadas, teto, gasto e disponível. As chamadas do próprio administrador não entram na conta.
O resumo mora em `atividade/resumo.json` no bucket de estado; gravar atividade nunca derruba uma tool.

## Computação pesada (a VM `lean-build2`)

`pesado(tipo, horas, parametros, confirmar=true)` reserva `horas × tarifa`, liga a VM com **um** job de allowlist
(`lake_build` ou `verificar_grande`), e `pesado_status` cobra o **tempo real** ao terminar. A VM se desliga sozinha
(`timeout` + `shutdown` no script) e tem um limite permanente de 6 h ligada (`maxRunDuration`, que o Compute não deixa
remover). Um job por vez; a VM não tem credencial, então só volta o código de saída e o fim do log (3 KB).
Provado em produção em 2026-10-03: `verificar_grande` em `K_4(10,4) ≤ 192` → `uncovered=0`, 69 s, US$ 0,0115.
`busca` não é um tipo: devolver um código achado exigiria uma credencial de armazenamento para a VM (decisão do dono).

## Estado honesto (2026-10-03)

* **Pronto, testado (47 testes) e no ar**: porta por token, ledger, matemática, papers, Gemini (Vertex), `pesado` com VM
  real, consulta de uso, rota própria `https://infinito.genesisinnovation.io/mcp/<token>/` (as URLs `run.app` antigas
  continuam valendo).
* **Cloudflare barra o User-Agent padrão do Python** (erro 1010). Clientes normais passam; scripts devem se identificar.
* **Preços do Gemini no Vertex** não foram conferidos (a tabela é a do AI Studio): reconfira antes de aumentar crédito.

## Para levantar (risco alto: infra, só o Thiago)

Molde igual ao `apps/propostas` da fabrica-de-sites (`infra/propostas-mcp/levantar.py`).

1. Bucket privado de estado (`INF_BUCKET_ESTADO`) e service account própria só com `objectAdmin` nele e
   leitura/escrita em `factory-literatura-matematica`.
2. `docker build -f infinito/Dockerfile .` e deploy no Cloud Run (min 0, **max 1 instância**: o trinco do ledger
   é por processo).
3. Segredos no serviço: `INF_TOKEN_ADMIN`, `GEMINI_API_KEY` (Secret Manager, nunca em arquivo) e `INF_URL_BASE`.
   Depois: `admin_convidar` para cada pessoa.
4. Para escalar: `INF_MAX_USUARIOS` e `INF_MODULOS` são variáveis, não código.

Inversa (templo): apagar serviço, aplicação do Access e SA. O bucket de estado fica (é o histórico de gasto).
