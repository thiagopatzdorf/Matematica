# Cache compartilhado da Mathlib entre worktrees

Cada worktree deste repo precisa de `.lake/packages` com a Mathlib e as dependências (~7 GB com os
`.olean`). Com vários worktrees na mesma máquina, o disco acaba. Dois atalhos já deram errado:

* **symlink para o `.lake` de outro worktree**: quebrou quando o dono apagou a pasta;
* **usar a pasta de outro worktree direto**: o build escreveu 0,8 GB no `.lake` alheio.

O script [`tools/infra/lake_cache.sh`](../../tools/infra/lake_cache.sh) resolve com um cache por revisão da
Mathlib e uma cópia por **hardlink** (`cp -al`) em cada worktree.

## Por que hardlink

* não ocupa disco: os arquivos do worktree e do cache são os mesmos inodes;
* não depende de ninguém: apagar o cache não quebra o worktree, e apagar o worktree não toca no cache
  (só baixa a contagem de links);
* o build do projeto escreve em `.lake/build` do próprio worktree; os `.olean` dos pacotes, íntegros e na
  revisão do manifesto, não são reescritos. Medido em 2026-10-05: `lake build CoveringLean` completo
  (8956 jobs, sem rede) num worktree ligado ao cache deixou inode, mtime e sha256 de uma amostra do cache
  idênticos, nenhum arquivo do cache mais novo que o registro e os 8926 `.olean` conferidos por sha256.

## Uso

Num worktree novo, a partir de qualquer pasta dele:

    tools/infra/lake_cache.sh ligar        # cria .lake/packages a partir do cache
    lake build                             # não baixa nada; compila só o projeto

Se `.lake/packages` já existir como pasta, o script recusa; `ligar --forcar` apaga e liga. Um symlink
antigo é trocado pela cópia sem perguntar.

Outros comandos:

| comando | o que faz |
|---|---|
| `onde` | imprime a pasta do cache para a revisão da Mathlib do `lake-manifest.json` |
| `semear <pasta>` | cria o cache a partir de um `.lake/packages` completo (confere a revisão de cada pacote contra o manifesto) e grava o sha256 dos `.olean` |
| `verificar` | confere as revisões e o sha256 de todos os `.olean` do cache |
| `desligar` | apaga `.lake/packages` deste worktree; o cache fica |

A raiz do cache é `$LAKE_CACHE_DIR` ou, sem ela, a pasta `.mathlib-cache` ao lado do checkout principal
do repo (fora de qualquer worktree, para nenhum `rm -rf` de worktree alcançá-la). Dentro dela,
`<rev da mathlib>/packages`, `<rev>/lake-manifest.json` e `<rev>/oleans.sha256`.

## Criar o cache numa máquina nova

1. Num checkout com `.lake/packages` completo (`lake exe cache get` e `lake build --no-build Mathlib`
   dizendo "All targets up-to-date"), rode `tools/infra/lake_cache.sh semear .lake/packages`.
2. Confira com `tools/infra/lake_cache.sh verificar`.

Quando a Mathlib do manifesto mudar de revisão, `ligar` acusa que não há cache para ela: semeie de novo a
partir de um checkout atualizado. Caches de revisões antigas podem ser apagados com `rm -rf` quando nenhum
worktree usar mais aquela revisão.

## O que não fazer num worktree ligado

* **`lake update` ou mudar a revisão da Mathlib**: o Lake faria checkout nos pacotes. O `git checkout`
  troca arquivos por arquivos novos (não reescreve o inode), mas o worktree deixa de corresponder ao
  cache; nesse caso, `desligar` e trabalhe sem o cache.
* **editar arquivo dentro de `.lake/packages` à mão**: o editor pode gravar no mesmo inode e alterar o cache
  de todos. `verificar` acusa.

## Desfazer

* Um worktree: `tools/infra/lake_cache.sh desligar` e, se quiser a cópia própria de volta,
  `lake exe cache get`.
* O cache inteiro: `rm -rf "$(tools/infra/lake_cache.sh onde)/.."`. Worktrees já ligados continuam
  funcionando, porque os hardlinks seguram os dados.
