# Candidato K_4(6,2) ≤ 48 (código de terceiros, conferido aqui; NÃO está no ledger)

- Origem: Tamal Maharaj, *Quaternary Preparata codes are quasi-perfect covering codes in the Hamming metric*,
  arXiv:2610.03760v1 (2026-09-27), Proposição 12 e Tabela 2. As 48 palavras foram copiadas da Tabela 2 do PDF.
  O crédito é dele; nós só conferimos. Antes: K₄(6,2) ≤ 52 (ref. [14] do artigo; também 52 no ledger).
- Conferido em 2026-10-07 pelo verificador oficial (`tools/verify/verify.c`):
  `q=4 n=6 R=2 M=48 points=4096 uncovered=0 sha256=b2451b37e7d516f6e00b848001894b2d6153bf1a3eda3333c55340310b526fd9`
  e, de forma independente, por força bruta em Python sobre os 4096 pontos (todos a distância ≤ 2 de alguma palavra).
- Não feito: entrada em `data/codes/`, `ledger/ours.json` e Lean; isso muda contagens e o texto da próxima versão e
  é decisão do dono (a origem é externa, então a proveniência precisa dizer "publicado por Maharaj 2026").
- Não feito: o octacode (K₄(8,2) ≤ 256, código de Preparata P₃) do mesmo artigo.
