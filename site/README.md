# Mapa da fronteira (site estático)

Gera, a partir de `ledger/cells.json`, o site que mostra o estado do conhecimento sobre as células
`K_q(n,R)`: página inicial com os números do ledger, mapa q × n × R em SVG, tabela filtrável, ranking
de alvos (vem de `ledger/targets.py`, sem lógica duplicada) e uma página por célula com cotas, fontes,
nosso estado e os comandos para atacá-la.

## Gerar

```bash
python3 scripts/site/build.py                 # escreve site/out/ (descartável; está no .gitignore)
python3 -m pytest -q -p no:cacheprovider tests/test_site.py
```

Só stdlib. O build é determinístico: o rodapé usa o sha e a data do **commit** (`git log -1`), nunca o
relógio, então duas execuções no mesmo commit dão bytes idênticos. Para fixar à mão (por exemplo, sem
git): `--commit SHA --data AAAA-MM-DD`. `--saida DIR` muda o destino.

Conteúdo versionado: `scripts/site/build.py` e `site/templates/` (`style.css`, `app.js`). O HTML gerado
não é versionado. Nenhuma requisição de rede: sem CDN, fonte externa ou analytics; o único JS é
`assets/app.js` (filtro e ordenação; sem ele a tabela continua completa).

## Publicar (descrição; este diretório não publica nada)

`site/out/` é uma pasta de arquivos estáticos: qualquer hospedagem estática serve (`index.html` na raiz,
links relativos, funciona até aberto de `file://`). O publicador existente da casa,
`scripts/publish/genesis_page.py`, gera a página única `/provas/cobertura` da Genesis; o mapa é outro
produto e ainda não tem publicador. Antes de subir: rode o build num commit já na `main`, para o rodapé e
os links de código apontarem para algo que existe, e rode os testes.

## Escolhas de design

* Cinco estados exclusivos por célula (nossa cota no Lean, melhorada por outros, aberta sem ataque,
  aberta atacada sem melhora, fechada), cada um com cor **e** glifo; cores da paleta categórica validada
  com `validate_palette.js` nos dois modos.
* O mapa tem o equivalente textual (tabela por q) e cada quadrado é um link com `aria-label`.
* Links de código apontam para `main` no GitHub; só aparecem arquivos Lean que existem (`theorem` achado
  por busca em `CoveringLean/`).
