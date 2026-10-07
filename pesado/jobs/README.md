# Scripts do trabalho pesado (allowlist)

O tipo `script` do MCP Infinito (`pesado`) só roda arquivos desta pasta, pelo nome sem `.sh`, e só de um commit que
**já está na `main`** (a VM confere com `git merge-base --is-ancestor`). Script novo entra por PR revisado, como
qualquer código: é isso que faz a allowlist ser allowlist, e não um comando livre com outro nome.

Contrato de um script:

* roda na raiz do repo, no commit pedido, com `timeout` igual às horas pedidas;
* recebe `SHARD_INDEX` (0..N-1), `SHARD_TOTAL` (N), `JOB_ID` e `SAIDA` no ambiente: divida o trabalho por
  `SHARD_INDEX` (ex.: a órbita `k` vai para o shard `k % SHARD_TOTAL`) e grave o resultado em `$SAIDA/`;
* `$SAIDA/` sobe para o bucket de estado como `jobs/<job>/shard-<i>-saida.tar.gz` e o log como `shard-<i>.log`;
  o fim do log (3 KB) e o código de saída sempre voltam por `pesado_status`;
* nunca grava segredo, nunca chama API paga: a VM não tem credencial, e é bom que continue assim;
* resultado de busca é **hipótese** até passar pelo verificador exato e, se for teorema, pelo Lean.

| script | o que faz | horas típicas |
|---|---|---|
| `fumaca` | prova de vida do lote: imagem, commit, CPU e upload da saída | 0,2 |
| `fibras-k4-7-4-m9` | K₄(7,4), M = 9: os 792 perfis do lema das fibras com LRAT conferido (`tools/exatos/fibras`, R = n − 3); todos UNSAT ⇒ K₄(7,4) = 10 | 1–3 por shard (paralelo 6) |
| `fibras-k3-7-3-m11` | K₃(7,3), M = 11: os 11 440 perfis, cobertura por 4-uplas; todos UNSAT ⇒ K₃(7,3) = 12 | 1–3 por shard (paralelo 6) |
