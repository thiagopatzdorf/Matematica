# Novidade antes de publicar: os candidatos da v0.9 (S10, 2026-10-05)

Pergunta: os resultados que estão em PR para a v0.9 já foram obtidos ou publicados por outra pessoa?
Para cada um, a classificação vem com as consultas feitas e com a frase de crédito que o artigo deve usar.

Este documento **não** avalia se as provas estão certas. Isso é dos red teams (#59, #61, #62). Ele só
responde se o resultado já existia na literatura. Nada foi gasto (US$ 0,00), nenhum número do ledger
foi tocado e nenhuma VM foi usada.

Legenda (a mesma de `k362/LITERATURE_K3_6_2.md`): **CONHECIDO** = está numa fonte que li;
**PROVÁVEL CONHECIDO** = fonte secundária, ou texto que não consegui ler e que pode conter o
resultado; **NÃO ENCONTRADO** = procurei e não achei, com as consultas listadas;
**POTENCIALMENTE NOVO** = não encontrado em nenhuma das fontes primárias que cobririam o caso.

## Veredito em uma tabela

| resultado (PR) | antes | o que o PR afirma | veredito | quem tinha o quê |
|---|---|---|---|---|
| K₃(6,2) ≥ 16 (#57, #59) | 15–17 | ∄ código de 15 palavras | **POTENCIALMENTE NOVO** | lb 15: Bertolo–Östergård–Weakley 2004; ub 17: Hämäläinen–Rankinen 1991 |
| K₃(6,2) = 17 (#60, #61) | 15–17 | ∄ código de 16 palavras | **POTENCIALMENTE NOVO** (a cota inferior; o 17 da cota superior é de 1991) | idem; Raval 2026 e Florath 2026 atacaram M = 16 sem fechar |
| K₇(6,4) ≤ 14 (#56, #62) | 13–15 | código explícito de 14 palavras | **POTENCIALMENTE NOVO** | ub 15: Kéri–Östergård 2005 |
| K₇(6,4) ≥ 14, logo = 14 (#56, #62) | 13–15 | ∄ código de 13 palavras | **POTENCIALMENTE NOVO** | lb 13: Haas–Schlage-Puchta–Quistorff 2009 |
| K₇(5,3) ≥ 16 (#56, #62) | 15–17 | ∄ código de 15 palavras | **POTENCIALMENTE NOVO** | lb 15: Haas–Quistorff–Schlage-Puchta (anúncio de 2009); ub 17: Rivas Soriano 2006 |
| K₇(5,3) = 17 (em andamento no #56) | 15–17 | ∄ 16 ainda não fechou | não se aplica ainda; se fechar, mesmo veredito | idem |

Nenhum dos cinco aparece em nenhuma fonte de 2011 a 2026 que consultei, inclusive as que listam as
três células explicitamente com os valores antigos: a compilação pós-Kéri do Florath (2026-09-16), a
tabela do `coldcase` do Marosi (2026-08) e as próprias tabelas do Kéri (vivas, sem atualização desde
2011-11-25).

## As células, uma por uma

### K₃(6,2)

**Histórico conferido.** 12 → 14 (Blass–Litsyn 1998) → 15 (Bertolo–Östergård–Weakley 2004) na cota
inferior; 17 (Hämäläinen–Rankinen 1991) na superior. Esfera: 10. SDP de Gijswijt–Polak: 13,1228.

| fonte | o que diz | como conferi |
|---|---|---|
| Kéri, `3_tables.pdf` (2011-11-24, ainda o arquivo vivo) | `6  i 15–17 u`; chave i = BOW 2004, u = HR 1991 | listagem viva de `old.sztaki.hu/~keri/codes/` lida hoje: mesmas datas de 2011 |
| Florath, `covering-codes-lean`, HEAD `bbed9a6` (2026-09-16, sem commit depois) | `post-keri`: `3,6,2,15,17,…bertolo…,…hamalainen_rankinen…`; Lean: 10–17 | `git clone` hoje; `git log` |
| Raval, Zenodo 10.5281/zenodo.22510341 (v0.1.1, 2026-09-07) e GitHub `d0a7b4c` | 6 de 38 ramos de M ≤ 16 excluídos; "No new global bound is claimed" | `git ls-remote`: HEAD e tags (v0.1.0, v0.1.1) iguais aos lidos em `LITERATURE_K3_6_2.md`; lista de repositórios do autor (API do GitHub, da factory-01): nada novo sobre K₃(6,2) depois de 2026-09-07 |
| Gijswijt–Polak, arXiv:2504.01932v2 | 13,1228 (Tab. 7), sem melhoria | já lido na revisão anterior |
| Marosi, arXiv:2608.19872 v3 (atual; v4 não existe) | só 5 ≤ q ≤ 21; SDP de K₃(6,2) no `coldcase` dá lb 14 | página `abs` lida hoje: histórico v1–v3; `coldcase` clonado hoje (master `56a8cce` e `research/symbolic-q82`) |
| OEIS A060439 (triângulo de K₃(n,R), rev. 22, 2026-05-30) | dados só até n = 5 | busca JSON no OEIS |

### K₇(6,4)

**Histórico conferido.** Na cota inferior: 10 (Rodemich 1970: ⌈49/5⌉) → 11 (preprint do HSPQ, tabelas
do Kéri de 16/12/2007) → 13 (Kéri, chave k = HSPQ 2008–2009) → **14 (nosso)**. Na superior: 15
(Kéri–Östergård 2005, chave n) → **14 (nosso)**.

- O preprint de Haas–Schlage-Puchta–Quistorff, *Lower Bounds on Covering Codes via Partition
  Matrices* (cópia em uni-rostock.de, sha256 `840b9783…`, lido inteiro), Tabela 1: `K7(6,4)
  Theorem 6  10  11  15`. O Teorema 6 é a recursão `K_{q+1}(n+1,R+1) ≥ min{2(q+1), K_q(n,R)+1}`.
  Com `K₆(5,3) = 12` (exato no Kéri, anunciado pelos mesmos autores em 2008-01-22) ela dá
  `min{14, 13} = 13`, que é o 13 da tabela. **Observação para o paper:** essa recursão nunca passa
  de `2(q+1) = 14` aqui, e o valor que provamos é exatamente esse teto. A versão publicada (JCTA
  116 (2009) 478–484) não pôde ser lida (ScienceDirect: 403); a resenha do zbMATH confirma "36
  explicit new lower bounds", o mesmo número de linhas do preprint.
- Colbourn–Kéri–Rivas Soriano–Schlage-Puchta, *Covering and radius-covering arrays* (DAM 2010; texto
  no acervo): K_q(n,R) = CAN_R(n, n, q), mas a tabela de q = 7 vai só até r = 3. **K₇(6,4) não
  aparece.**
- Haas–Halupczok–Schlage-Puchta, EJC 16 (2009) R133 (texto no acervo): trata `K_q(n, n−k)` para
  k ≥ 3. A Tabela 5 (q = 7) não tem nem K₇(6,4) nem K₇(5,3).
- Quistorff–Schlage-Puchta, *On generalized surjective codes* (Studia 2011; acervo): a Tabela 6 de
  σ₇ vai só até n = 4.
- Kéri, `6-21_tables.pdf` (2009-10-15, vivo): `6  k 13–15 n`. `coldcase/cov/data/keri_third_party.csv`
  e o `post-keri` do Florath: 13–15. Lean do Florath: 7–19.
- Marosi v3: K₇ só em (8,4), (9,4), (9,5), (10,5) na Tabela 1 e (7,2)…(10,2) na Tabela 2. O
  `coldcase` não tem arquivo, certificado nem registro de ataque para (7,6,4)
  (`git grep` em todos os ramos; `attack_records*.json` só tem n ≥ 8 para q = 7). No nosso ledger,
  `marosi_attacked` = `{lb: false, ub: false}`.

### K₇(5,3)

**Histórico conferido.** Na cota inferior: 13 (Rodemich: ⌈49/4⌉) → 14 (HSPQ, preprint, Teorema 6:
`min{14, K₆(4,2)+1}`) → 15 (Haas–Quistorff–Schlage-Puchta, anúncio no Kéri em **2009-10-06**:
"K7(5,3)>=15; K7(10,7)>=15") → **16 (nosso)**. Superior: 17 (Rivas Soriano, anúncio no Kéri em
2006-01-25: "K7(5,3)<=17").

- O 15 não está no preprint do HSPQ (que dá 14). O CKRS 2010 tabela a célula como `x 15−17 g`, com
  a chave `x` = [20] "W. Haas, J. Quistorff and J.-C. Schlage-Puchta, *New lower bounds for covering
  codes*, manuscript". Não achei esse manuscrito publicado (OpenAlex por autores e título: 0
  resultados). **A fonte citável do 15 é a tabela do Kéri** (chave k, "Haas–Schlage-Puchta–Quistorff,
  2008–2009") e o anúncio datado na página de atualizações.
- Mesmas fontes de 2011–2026 da seção anterior: Kéri `5  k 15–17 q`; Florath 15–17 (Lean 7–23);
  `coldcase` 15–17, sem ataque; Marosi sem a célula.

## Frases de crédito para o paper (texto pronto, em inglês)

- **K₃(6,2).** "The previous bounds were 15 ≤ K₃(6,2) ≤ 17: the lower bound 15 is due to Bertolo,
  Östergård and Weakley [BOW04], improving 14 of Blass and Litsyn [BL98], and the upper bound 17 is due
  to Hämäläinen and Rankinen [HR91]. We show that no ternary code of length 6, covering radius 2 and 16
  codewords exists; hence K₃(6,2) = 17, attained by the code of [HR91]. Partial exclusions for M ≤ 16
  were obtained independently by Raval [Rav26] (6 of 38 normalized branches) and attempted by Florath
  [Flo26], without a global bound."
- **K₇(6,4).** "Previously 13 ≤ K₇(6,4) ≤ 15, with the lower bound from the recursive partition-matrix
  bound of Haas, Schlage-Puchta and Quistorff [HSQ09] (Kéri's key k) and the upper bound 15 from the
  alphabet-partition construction of Kéri and Östergård [KÖ05]. We give a code with 14 codewords and
  prove that no code with 13 codewords exists, so K₇(6,4) = 14. Note that the recursion of [HSQ09,
  Thm. 6] is capped at 2(q+1) = 14 here."
- **K₇(5,3).** "Previously 15 ≤ K₇(5,3) ≤ 17, with the lower bound 15 announced by Haas, Quistorff and
  Schlage-Puchta (Kéri's tables, update of 2009-10-06; key k) and the upper bound 17 by Rivas Soriano
  (Kéri's tables, update of 2006-01-25; key q). We prove K₇(5,3) ≥ 16."
- Para as tabelas: "Kéri, G., *Tables for bounds on covering codes*, http://old.sztaki.hu/~keri/codes/
  (last update 2011-11-25; accessed 2026-10-05)". Para o 15 de K₇(5,3), citar a tabela e não o
  manuscrito, que não encontrei publicado.

Referências (título, volume, páginas e DOI conferidos no OpenAlex em 2026-10-05):

- [BOW04] R. Bertolo, P. R. J. Östergård, W. D. Weakley, *An updated table of binary/ternary mixed
  covering codes*, J. Combin. Des. 12(3) (2004) 157–176, doi:10.1002/jcd.20008 (OpenAlex W1963788317).
- [HR91] H. O. Hämäläinen, S. Rankinen, *Upper bounds for football pool problems and mixed covering
  codes*, J. Combin. Theory Ser. A 56(1) (1991) 84–95, doi:10.1016/0097-3165(91)90024-B (OpenAlex
  W2044451186).

Demais: [BL98] Blass–Litsyn, *Several new lower bounds for football pool systems*, Ars Combin. 50
(1998) 297–302 (só resenha zbMATH Zbl 0962.94041); [HSQ09] J. Combin. Theory Ser. A 116 (2009) 478–484,
doi:10.1016/j.jcta.2008.06.008; [KÖ05] Des. Codes Cryptogr. 37 (2005) 45–60,
doi:10.1007/s10623-004-3804-8; [Rav26] Zenodo doi:10.5281/zenodo.22510341 (v0.1.1); [Flo26]
arXiv:2606.09600 e `github.com/florath/covering-codes-lean`, `docs/failures/K_3_6_2.md`.

### Conferência da bibliografia do rascunho (PR #63)

| chave | o que o #63 escreve | o que o OpenAlex diz | ação |
|---|---|---|---|
| `bow2004` | "D.~Bertolo", *An updated table of binary/ternary mixed covering codes*, J. Combin. Des. 12 (2004) 157–176 | primeiro autor **Riccardo Giuseppe Bertolo** (ORCID 0000-0003-0260-4601); título, volume e páginas iguais; número 3; doi:10.1002/jcd.20008 | trocar "D." por "R."; acrescentar o número 3 e o DOI; o título está certo |
| `hr1991` | "H.~Hämäläinen and S.~Rankinen", *Upper bounds for football pool problems and mixed covering codes*, J. Combin. Theory Ser. A 56 (1991) 84–95 | **Heikki O. Hämäläinen** e Seppo Rankinen; título, volume e páginas iguais; número 1; doi:10.1016/0097-3165(91)90024-B | pode virar "H.~O. Hämäläinen"; acrescentar o DOI; o título está certo |
| `bl1998` | Blass–Litsyn, *Several new lower bounds for football pool systems*, Ars Combin. 50 (1998) 297–302 | não está no OpenAlex; a resenha do zbMATH (Zbl 0962.94041) confirma título e páginas | manter |

Os dois `\todo{conferir o título exato}` do #63 podem sair: os títulos estão certos. O erro real é a
inicial do primeiro autor de `bow2004`.

Atenção a duas armadilhas de citação:

1. A chave k do Kéri diz "Haas–Schlage-Puchta–Quistorff, 2008–2009", mas o JCTA (como o preprint)
   dá 14 para K₇(5,3) e 11 para K₇(6,4) **pela recursão aplicada às tabelas de 2007**. O 13 de K₇(6,4)
   sai do mesmo Teorema 6 com `K₆(5,3) = 12`; o 15 de K₇(5,3) é do anúncio de 2009. Não escrever "HSQ09
   proved K₇(5,3) ≥ 15" sem ressalva.
2. A ordem dos autores muda entre as fontes (Haas–Schlage-Puchta–Quistorff no JCTA; Haas–Quistorff–
   Schlage-Puchta no anúncio de 2009 e no manuscrito). Usar a do documento citado.

## Consultas feitas (todas em 2026-10-05)

| onde | consulta | resultado |
|---|---|---|
| tabelas do Kéri, vivas | listagem do diretório e `index.htm` | arquivos de 2009-10-15 e 2011-11-24; última atualização 2011.11.21; nada sobre as três células depois de 2009 |
| acervo da factory-01 (`dados/txt`, 1 274 arquivos; `dados/tabelas`) | regex `K_?7 ?\((6, ?4\|5, ?3)\)` e variantes com espaços; `Marosi`; `19872` | nenhum texto cita K₇(6,4); K₇(5,3) só no CKRS 2010 (15–17); versão nova do Marosi no acervo (W7203953290) sem as células |
| arXiv, PDF | Marosi 2608.19872v3 (sha256 `42cc6b49…`), `pdftotext`, `grep` | sem K₃(6,2), K₇(6,4), K₇(5,3); anc só com K₇(8,4), (9,4), (9,5), (10,5) |
| API do arXiv, por data | `abs:"covering code" OR abs:"covering codes"`, `ti:"covering radius"`, `abs:"football pool"`, `abs:"covering radius" AND abs:ternary`, `abs:"covering codes" AND abs:"lower bound"`, `abs:"covering codes" AND abs:Lean`; autores Florath, Marosi, Östergård, Kéri, Raval, Gijswijt | mais recente relevante: 2609.16078 (binário R = 2) e 2609.35027 (reticulados); nada sobre as células |
| GitHub | `Mapika/coldcase` (todos os ramos), `florath/covering-codes-lean` (HEAD `bbed9a6`), `ruturajr-raval/*` | as três células com os valores antigos; nenhum código ou certificado novo |
| Zenodo (API) | `"covering code"`, `"covering codes"`, `"covering radius"`, `"K_7(6,4)" OR "K7(6,4)" OR "K_7(5,3)"`, versões do 22510341 | só Raval (2026-09-07) e o nosso v0.8.0 (23147167) |
| OpenAlex | citantes de HSPQ JCTA (6), de Kéri–Östergård 2005 (8), de BOW 2004 (14), de Rodemich 1970 desde 2010 (5); `covering codes large alphabets covering radius n-2`; título do manuscrito HQS | nenhum citante traz cota nova nas células; Mendes–Monte Carmelo–Poggi 2010 só q = 3, 4 |
| Semantic Scholar (API) | resumos de Monte Carmelo 2012 e Mendes et al. 2010 | coberturas "curtas" para q potência de primo; tabelas só para q = 3, 4 |
| OEIS | `covering code ternary radius 2`, `rook domains covering`, A060439 | K₃(6,·) não tabelado |
| web | `"K_7(6,4)" OR "K7(6,4)"`, `"K_q(n,n-2)" … Rodemich`, `"K_3(6,2)" OR "K3(6,2)" … 2026`, `… "17 codewords" OR "K_3(6,2)=17"`, `Raval "K_3(6,2)"`, `"K_7(5,3)" … 16`, `"length q-1" … "q-3"` | só as fontes já listadas; o preprint do HSPQ veio daqui |
| Infinito `papers_buscar` | `semanticscholar` | `HTTPError` (a ferramenta segue instável, como na revisão anterior); `arxiv`: ruído |

## O que NÃO foi possível checar

- **Textos completos fechados**: BOW 2004 (Wiley), HSPQ JCTA publicado, Kéri–Östergård 2005
  (Springer), Monte Carmelo 2012 e dos Santos–Monte Carmelo 2013 (ScienceDirect, 403; o CORE devolveu
  HTML). A versão publicada do HSPQ pode ter tabela diferente do preprint. Nada indica que tenha 14
  para K₇(6,4) ou 16 para K₇(5,3), porque as tabelas do Kéri de 2009 (que incorporam esse trabalho)
  dão 13 e 15.
- **O manuscrito HQS "New lower bounds for covering codes"**: não achei. Se ele existir publicado,
  é o lugar onde o 15 de K₇(5,3) foi provado, e é preciso conferir se ele não traz também algo sobre
  K₇(6,4).
- **Google Scholar, MathSciNet, Scopus**: sem acesso. **Teses** (Haas e Quistorff, Freiburg/Berlim;
  livro de Kaski–Östergård 2006): não lidas.
- **Codetables/LinCode**: não se aplicam, porque tabelam códigos lineares por distância mínima e não
  códigos de cobertura não lineares. A tabela de Litsyn (`eng.tau.ac.il/~litsyn/tablecr`) é binária e
  antiga.
- Submissões ainda não listadas no arXiv, e versões novas de repositórios depois de hoje.

## Decisões tomadas sozinho

- Classifiquei como POTENCIALMENTE NOVO (e não como NOVO) porque a busca tem as lacunas acima,
  sobretudo os textos fechados de 2004–2009.
- Para K₃(6,2) = 17 o veredito vale só para a cota inferior. O 17 da cota superior é de 1991 e o
  crédito do código vai para Hämäläinen–Rankinen.
- Tratei a correção dos resultados como fora do escopo. O veredito de novidade não muda se um red
  team derrubar uma prova; nesse caso o resultado simplesmente sai da lista.
- Não citei o manuscrito HQS como fonte do 15: cito a tabela do Kéri e a data do anúncio.
