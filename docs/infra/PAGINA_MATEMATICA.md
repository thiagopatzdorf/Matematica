# Página pública: genesisinnovation.io/matematica

Como a página `site/matematica/` chega a <https://genesisinnovation.io/matematica>, como publicar de novo
e como tirar do ar. Medido em 2026-10-06.

## Como a raiz é servida

`genesisinnovation.io` (e `www.`, que redireciona com 301) é domínio customizado do Worker Cloudflare
`mybagcenter-static-legado-proxy`. A fonte dele vive em outro repositório
(`thiagopatzdorf/fabrica-de-sites`, `infra/static-legado/worker.js`). O Worker lê do bucket GCS público
`mybagcenter-static-legado`, prefixo `genesis/`:

| URL | objeto no bucket |
|---|---|
| `/` | `genesis/index.html` |
| `/matematica` | `genesis/matematica` (objeto sem extensão = a página) |
| `/matematica/estilo.css` | `genesis/matematica/estilo.css` |
| `/matematica/` | 301 para `/matematica` |
| objeto ausente | 404 de verdade, com `x-robots-tag: noindex` |

O mesmo esquema já serve `/provas/cobertura`, `/mosca` e `/ferramentas`. Antes da primeira publicação,
`/matematica` dava 404.

**Por isso a publicação não mexe na Cloudflare.** Não cria Worker, rota nem DNS, e não muda nada na raiz
nem nos subdomínios. Cada visita passa pelo Worker que já existe, e esse Worker conta na cota grátis de
100 mil invocações por dia, que a conta inteira divide com a loja. São cerca de 3 invocações por visita
(página, CSS/JS e `dados.json`). Na semana de 29/09 a 05/10 o pico foi 37 mil por dia, 37% da cota,
medido com `cloudflare_uso` do Factory MCP. Uma rota nova de Worker em `genesisinnovation.io/matematica*`
foi descartada: disputaria precedência com o domínio customizado do proxy e não traria ganho.

## Gerar os dados

```bash
python3 tools/site/gerar_dados_site.py              # reescreve site/matematica/dados.json
python3 tools/site/gerar_dados_site.py --verificar  # CI: falha se o versionado estiver velho
```

Os números vêm de `ledger/cells.json`, conferidos contra `ledger/COBERTURA.md`. O script falha se os dois
divergirem. Também usa `data/codes/`, `.zenodo.json`, `CITATION.cff` e `git rev-parse HEAD`. Só
`gerado_em` e `commit` mudam entre execuções. O teste é `tests/test_gerar_dados_site.py`.

## Publicar, despublicar, restaurar

Script: `tools/site/publicar_matematica.py` (só stdlib). Sem `--confirmar` ele não grava nada, só mostra
o plano.

```bash
python3 tools/site/publicar_matematica.py publicar                 # plano (seco)
python3 tools/site/publicar_matematica.py publicar --confirmar     # sobe site/matematica/
python3 tools/site/publicar_matematica.py listar
python3 tools/site/publicar_matematica.py despublicar --confirmar  # inversa: tira do ar
python3 tools/site/publicar_matematica.py restaurar --carimbo AAAAMMDDTHHMMSSZ --confirmar
```

Ao publicar, o script:

1. sobe `index.html` como o objeto `genesis/matematica`, injetando `<base href="/matematica/">` (sem isso,
   `estilo.css` relativo resolveria na raiz do site);
2. reescreve âncoras `href="#x"` para `href="/matematica#x"` (com o `<base>`, `#x` recarregaria a
   página);
3. sobe o resto da pasta em `genesis/matematica/<arquivo>` com `cache-control: public, max-age=60`;
4. ignora `.md` e `.py`, e recusa extensão desconhecida ou arquivo acima de 5 MB.

**Templo:** antes de sobrescrever ou apagar, o script copia cada objeto atual para
`gs://factory-cauteloso-telemetria/matematica-site-backup/<carimbo>/`. `restaurar --carimbo` volta
exatamente àquele estado. Arquivo que saiu da pasta também sai do ar. No fim, o script baixa cada arquivo
pela URL pública e compara os bytes: se o arquivo no ar não for idêntico ao enviado, a saída é 1.

### Credencial

O script lê um token OAuth com escopo de escrita no bucket em `$GCS_TOKEN` e nunca o imprime. Sem essa
variável, tenta `gcloud auth print-access-token`. Na factory-01, a service account `agentes-cloud`
(`storage.admin`) cunha o token em memória a partir do cofre:

```bash
# na factory-01, num clone descartável deste repo (nunca no checkout vivo)
git clone -q --depth 1 https://github.com/thiagopatzdorf/Matematica.git "$TMPDIR/mat" && cd "$TMPDIR/mat"
export GCS_TOKEN="$(cd "$FACTORY_APPS"/factory && python3 -c 'import sys; sys.path.insert(0, "bin"); import gcp_credencial; print(gcp_credencial.token())')"
python3 tools/site/publicar_matematica.py publicar --confirmar
unset GCS_TOKEN
```

`$FACTORY_APPS` é a pasta `apps` do checkout das mãos da Factory na factory-01. Pelo Factory MCP, a tool
`executar` já começa em `apps/factory`.

## Histórico

| data | o quê | carimbo de volta |
|---|---|---|
| 2026-10-06 01:10Z | 1ª publicação: página provisória mínima, fora do repo, só para provar a rota, mais `dados.json`. O bucket estava vazio nesse prefixo. A conferência falhou por dois motivos medidos: 403 ao User-Agent `Python-urllib` e o beacon do Web Analytics injetado pela borda. Os dois foram corrigidos no script | `20261006T011017Z` (vazio) |
| 2026-10-06 01:11Z | republicação com conferência `ok` | `20261006T011143Z` |
| 2026-10-06 01:12Z | prova da inversa: `despublicar` deu 404, `restaurar` voltou a 200 com o mesmo conteúdo. Raiz e `/provas/cobertura` seguiram 200 | `20261006T011158Z` |

Próximo passo: depois do merge de `index.html`, `estilo.css`, `app.js` e `conteudo.json`, rodar `publicar --confirmar`
a partir da `main`. Isso substitui a página provisória.
