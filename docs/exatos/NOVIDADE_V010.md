# Novidade antes de publicar: os candidatos da v0.10 (campanha de 2026-10-07)

Pergunta: os resultados de cota inferior que entram na v0.10 (#111, ledger em #114) já foram obtidos ou
publicados por outra pessoa? Para cada um, a classificação vem com as consultas feitas e com a frase de
crédito que o artigo deve usar.

Este documento **não** avalia se as provas estão certas. Isso é do red team, que **ainda não foi feito**
para estas duas cotas (só houve a dupla checagem do próprio #111: kissat em todos os perfis e codificação
independente em amostra). Ele só responde se o resultado já existia na literatura. A checagem é a do
m2-literatura, registrada como comentário no PR #111 em 2026-10-07; aqui ela é transcrita no formato do
[`NOVIDADE_V09.md`](NOVIDADE_V09.md). Gasto: US$ 0,00. Nenhum número do ledger foi tocado.

Legenda (a mesma de `NOVIDADE_V09.md`): **CONHECIDO** = está numa fonte que li; **PROVÁVEL CONHECIDO** =
fonte secundária, ou texto que não consegui ler e que pode conter o resultado; **NÃO ENCONTRADO** =
procurei e não achei, com as consultas listadas; **POTENCIALMENTE NOVO** = não encontrado em nenhuma das
fontes primárias que cobririam o caso.

## Veredito em uma tabela

| resultado (PR) | antes | o que o PR afirma | veredito | quem tinha o quê |
|---|---|---|---|---|
| K₄(7,4) ≥ 10, logo = 10 (#111, #112, #114) | 9–10 | ∄ código de 9 palavras | **NÃO ENCONTRADO**, com uma lacuna: Haas 2011 não lido | lb 9: Haas–Schlage-Puchta–Quistorff (chave k do Kéri); ub 10: Rivas Soriano (chave q, site QuiniWin, não arbitrado) |
| K₄(6,3) ≥ 12 (#111, #114) | 11–14 | ∄ código de 11 palavras | **NÃO ENCONTRADO**, com a mesma lacuna | lb 11: Haas–Quistorff–Schlage-Puchta (chave k; ≥ 10 sem computador em HHS 2009); ub 14: Bertolo–Di Pasquale–Santisi (chave x, toto1x2.it) |

**Por que não é POTENCIALMENTE NOVO.** Há uma fonte primária que cobriria exatamente estas células e que
ninguém leu: W. Haas, *Lower bounds for quaternary covering codes*, Ars Combin. 99 (2011) 19–23 (fechado).
Pela legenda, texto não lido que pode conter o resultado impede o veredito. A inferência abaixo diz que
provavelmente ele não contém ≥ 10 nem ≥ 12, mas **é inferência, não leitura**. Por isso:

* **as duas células não entram em `NOVIDADE_CONFERIDA`** (`tools/site/gerar_resultados.py`), e o badge de
  exatas potencialmente novas continua em 3;
* a frase da v0.10 é: *valor exato novo no ledger (K₄(7,4) = 10) e cota inferior nova no ledger
  (K₄(6,3) ≥ 12); não encontrados nas fontes lidas; novidade não conferida (falta Haas 2011)*.

Quem tiver acesso ao Ars Combin. 99 fecha a dúvida: lendo o artigo, se ele não tiver ≥ 10 nem ≥ 12, o
veredito vira POTENCIALMENTE NOVO e as duas células entram em `NOVIDADE_CONFERIDA` no mesmo PR.

## As fontes, uma por uma

| fonte | o que diz | como conferi |
|---|---|---|
| Kéri, `4-5_tables.pdf` (índice do servidor: 2009-10-15), `old.sztaki.hu/~keri/codes/` | K₄(6,3) **11–14** (chaves k e x); K₄(7,4) **9–10** (chaves k e q) | arquivo vivo lido em 2026-10-07 |
| Kéri, `biblio.pdf`, ref. [137] | chave q = *P. P. Rivas Soriano, QuiniWin*, site de um programa de reduções de quiniela: não é artigo arbitrado | lido |
| Kéri, `biblio.pdf`, ref. [49] (dez/2008) | Haas 2011 já listado como "submitted"; as tabelas de 2009, posteriores, continuam com 11 e 9 | lido; é a base da inferência |
| Chen–Honkala 1990; tabela do Kéri de 2008 | K₄(6,3) ≥ 8; depois ≥ 10 | histórico, via Kéri e HHS 2009 |
| Haas–Halupczok–Schlage-Puchta, *Lower bounds for q-ary codes with large covering radius*, EJC 16 (2009) #R133 | prova K₄(6,3) ≥ 10 sem computador; anuncia ≥ 11 (e K₄(5,2) = 16) para trabalho futuro de Haas–Quistorff–Schlage-Puchta | texto aberto, lido |
| Gijswijt–Polak, arXiv:2504.01932v2 (2026-06-19) | Tabela 3 (novas inferiores para q = 4, 5) não traz (4,6,3) nem (4,7,4); Tabela 8: SDP 8,76 e 6,40 | PDF lido |
| Marosi, arXiv:2608.19872v3 (2026-09-02) | só q ≥ 5 (inferiores de q = 6 a 21) | lido |
| Florath, arXiv:2606.09600 e Zenodo | base formal em Lean, não tabela de recordes; para estas células só a cota da esfera (6 e 5) | ledger + leitura |
| W. Haas, Ars Combin. 99 (2011) 19–23 | **não lido** (fechado) | lacuna |

Consultas feitas (todas sem resultado para estas células): OpenAlex OQL `"covering code*" AND ("covering
radius" OR "football pool" OR "q-ary" OR quaternary OR nonbinary)` a partir de 2011 (70 obras); Consensus
"exact values of quaternary covering codes K_4(n,R)"; Zenodo "covering code K_4(7,4)"; busca na web com
Haas, Rivas Soriano e "quaternary covering codes". A busca no arXiv pelo Infinito falhou nesse horário
(HTTPError); os artigos do arXiv acima vieram do OpenAlex e de leitura direta.

## A cota superior de K₄(7,4)

O "= 10" depende da cota superior, que na literatura vem só do site QuiniWin (não arbitrado, sem código
achado no Wayback Machine). O código de 10 palavras deste repositório (`data/codes/q4_n7_R4_M10.txt`,
achado por `tools/busca_direta/tabu.c`, sha256 canônico `f2abfa60…`) passa no verificador oficial, então
a cota superior aqui é testemunha conferida, não o anúncio.

## Frase de crédito para o artigo

*The previous bounds were 9 ≤ K₄(7,4) ≤ 10 and 11 ≤ K₄(6,3) ≤ 14, the lower bounds by Haas,
Schlage-Puchta and Quistorff as recorded in Kéri's tables, the upper bound 10 announced by Rivas Soriano and
14 by Bertolo, Di Pasquale and Santisi. We did not find K₄(7,4) ≥ 10 or K₄(6,3) ≥ 12 in the sources we read;
one paper that would cover these cells (Haas 2011) was not read, so novelty is not established.*

## Tentativas de ler Haas 2011 (2026-10-07, sem sucesso)

Nenhuma fonte aberta devolveu o texto: busca web (só a ficha no dblp), zbMATH (HTTP 403), Semantic
Scholar (HTTP 429), dblp pelo fetch (bloqueado por Anubis), OpenAlex e arXiv pelo Infinito (nenhuma
obra com esse título; não há preprint). O veredito **não muda**: lacuna aberta, as duas células
continuam fora de `NOVIDADE_CONFERIDA`. Precisa de acesso ao Ars Combin. 99 (19–23) por biblioteca ou
do próprio autor (Wolfgang Haas, Freiburg).

Achado de passagem, fora desta checagem: arXiv:2610.03760 (2026-09-27, Maharaj) afirma K₄(8,2) ≤ 256
(octacode, código de Preparata P₃) e K₄(6,2) ≤ 48 (antes 352 e 52). As 48 palavras de K₄(6,2) estão na
Tabela 2 do artigo; passam no verificador oficial deste repositório (`q=4 n=6 R=2 M=48 points=4096
uncovered=0`, sha256 canônico `b2451b37…`), o que confirma o ≤ 48. O crédito é do autor do artigo, não
nosso; a entrada no ledger fica para decisão do dono (PR separado, só com o candidato). O octacode
(K₄(8,2) ≤ 256) ainda não foi construído aqui.
