# Códigos explícitos transcritos de artigos

Cada `<chave>.json` traz a citação completa (autores, título, veículo, volume, ano, páginas, DOI) e,
item a item, o lugar exato no artigo e os dados explícitos: listas de palavras, matrizes do método
matricial (`A = [I_k M]`, código `{x : Ax ∈ S}`), matrizes de verificação, grupos de automorfismos
com representantes de órbita, ou uma construção explícita sobre itens anteriores (soma direta
amalgamada, soma direta em blocos, Corolário 3 de Kéri–Östergård). **Os PDFs não são versionados**:
só os fatos matemáticos. Cada transcrição foi conferida contra a imagem da página.

| arquivo | o quê |
|---|---|
| `ostergard_kaikkonen_1998.json` | Östergård e Kaikkonen, *New upper bounds for binary covering codes*, Discrete Math. 178 (1998) 165–179, DOI 10.1016/S0012-365X(97)81825-0 |
| `ostergard_weakley_1999.json` | Östergård e Weakley, *Constructing covering codes with given automorphisms*, Des. Codes Cryptogr. 16 (1999) 65–73, DOI 10.1023/A:1008326409439 |
| `hamalainen_honkala_kaikkonen_litsyn_1993.json` | Hämäläinen, Honkala, Kaikkonen e Litsyn, *Bounds for binary multiple covering codes*, Des. Codes Cryptogr. 3 (1993) 251–275, DOI 10.1007/BF01388486 (só as linhas μ = 1) |
| `keri_ostergard_2005.json` | Kéri e Östergård, *Bounds for covering codes over large alphabets*, Des. Codes Cryptogr. 37 (2005) 45–60, DOI 10.1007/s10623-004-3804-8 |
| `surjetivos/` | ingredientes r-sobrejetivos (covering arrays) do Corolário 3 que não saem de fórmula: o código do Exemplo 3 de KO05 e os achados aqui por recozimento simulado, com os tamanhos das Tabelas 2 e 3 de KO05 |

`tools/literatura/codigos_papers.py` reconstrói tudo e confere com avaliador exato, independente do
Lean e do `tools/verify/verify.c` (bitset de `2^n` bits para binários; exaustão de cada ingrediente
e força bruta até `q^n ≤ 3·10^6` para o Corolário 3); `--escrever --registrar` grava em
`data/codes/` os que cabem no verificador oficial (`q ≤ 10`, `n ≤ 20`) e registra no ledger.
`tests/test_literatura_codigos.py` refaz as conferências.

## Achado: o (19,320)4 da Tabela 1 de Östergård–Kaikkonen não cobre com raio 4

Transcrito da página 167 (`672, 1952, 15AE, 164E, 894, 1BAB; 0, 5A2, 1DE0, 1BF4, E57`, `k = 13`),
o código tem 320 palavras mas raio 5 (12 032 pontos a distância 5), e o `[19,6]` cuja verificação é
a mesma matriz (Exemplo 5, anunciado `[19,6]5`) tem raio 6. Os outros três códigos da Tabela 1, na
mesma convenção, batem; nenhuma troca de um dígito hexadecimal (em `M` ou em `S`) nem de um ou dois
bits de `M` conserta. É provável erro de impressão. Esse código é ingrediente do Exemplo 7
(`K(23,5) ≤ 640`) e da chave a9 da Tabela 3 (`K(27,6)`, `K(29,7)`, `K(30,8)`, `K(31,8)`, `K(33,9)`,
e `K(32,9)` por a1); essas células continuam só anunciadas aqui.

## No Lean

`tools/literatura/gerar_lean.py` gera os certificados das células cuja cota publicada é igual à do
código (e `--registrar` grava `ours_lean` em `ledger/ours.json`, depois do build verde):

* Corolário 3 (79 células de chave `n`): o teorema genérico `CoveringSurj.cobre`
  (`CoveringLean/Surjetivo.lean`, no alvo padrão) e, por célula, `CoveringLit.K<q>_<n>_<R>_le_<M>`
  (`CoveringLean/Literatura/KO05.lean`); a sobrejetividade de cada ingrediente é conferida pelo
  kernel com um mapa de bits (`checkSurj`), em `CoveringLean/Literatura/Surj_*.lean`;
* binários pequenos por witness (`CoveringLean/Literatura/Binarios.lean`, `UB.of_go`) e K₂(14,1) ≤
  1408 pela regra `K(n+1,R) ≤ 2K(n,R)` sobre o (13,704)1;
* binários uniões de cosets pelo certificado por síndromes (`Syn.K2_<n>_<R>_le_<M>_syn`, specs em
  `syn/`, lib `CoveringSyn`).

`lake build CoveringLiteratura` (~1 h de CPU; o ingrediente de 11⁴ palavras leva ~35 min) e
`lake build CoveringSyn`. Ficam de fora do Lean os binários cujo transversal passa de 2¹⁷ pontos
(K₂(21,7), K₂(23,8), K₂(25,9), K₂(26,9), K₂(27,10), K₂(28,6), K₂(28,10)): conferidos só pelo
avaliador exato, continuam CLAIMED no ledger.
