# Problemas de matemática resolvidos por IA em 2026, e o que serve para K_q(n,R)

Levantamento de 2026-10-07 (campanha da madrugada). A pergunta: o que a OpenAI, a DeepMind e
outros publicaram em 2026 sobre problemas abertos resolvidos por IA, que técnica cada um usou, o
que foi verificado formalmente e o que é só afirmação, e o que disso dá para usar nas cotas
K_q(n,R) do ledger.

**Resposta curta.** Nenhum resultado de IA de 2026 toca códigos de cobertura, raio de cobertura ou
o problema da loteria esportiva (*football pool*). O item "binary codes" da OpenAI é uma cota
**superior assintótica de empacotamento** (A(n,d), melhora a MRRW) e não dá número para nenhuma
célula K_q(n,R) finita. O que serve para nós é **método**, não resultado: (1) o LLM evolui o
programa de busca e um avaliador exato decide (AlphaEvolve), (2) enunciado confiável separado da
prova e checado por uma ferramenta independente (OpenAI, Comparator), (3) lemas de teste contra
enunciado errado (DeepMind), (4) cota inferior por SDP com dual racional, e Lean por cima.

## Como foi feito

- **Fontes primárias lidas**: o PDF da OpenAI (249 páginas, versão de 06/08/2026) e o
  repositório `openai/ten-proofs` clonado e inspecionado; os PDFs do arXiv 2511.02864 (AlphaEvolve,
  81 páginas) e 2605.22763 (AlphaProof Nexus, 60 páginas), com busca nas palavras-chave
  `covering`, `Hamming`, `Lean`, `verif*`, `cost`; as páginas do arXiv de 2608.19872, 2608.27494,
  2604.03789 e 2608.24961.
- **Só por fonte secundária** (o site da OpenAI devolve 403 para leitura automática): o anúncio do
  unit-distance (TechCrunch, Understanding AI) e o nome "Astra" (SiliconANGLE, Quanta). O PDF da
  OpenAI diz apenas "an internal OpenAI model".
- **Buscas** (WebSearch estendida, `papers_buscar` do Infinito no arXiv): "covering codes covering
  radius new bounds 2026", "LLM evolutionary search covering design / covering code / covering
  array 2026", "covering codes covering radius upper bounds". Nenhum resultado com IA em
  códigos de cobertura.
- **Não feito**: não rodei `lake build` do `ten-proofs` (21 MB de Lean, mathlib inteira); a
  contagem de `sorry` abaixo é por texto. Não li o PDF separado de *reasoning walkthroughs* da
  OpenAI. Gasto: US$ 0 (nenhuma chamada paga).

## O que saiu em 2026 (e o que está verificado)

| data | quem | resultado | técnica declarada | verificação formal | fonte primária |
|---|---|---|---|---|---|
| 2026-05-20 | OpenAI | contraexemplo à conjectura da distância unitária de Erdős (1946): ≥ n^(1+c) pares, Sawin explicitou n^1.014 | "modelo de raciocínio de uso geral"; a construção usa anéis de inteiros de corpos de números, torres de corpos de classes (Golod–Shafarevich) e projeção para o plano | **nenhuma em Lean** conhecida; verificação **humana** por Alon, Bloom, Gowers, Litt, Sawin, Shankar, Tsimerman, Wang e Wood | [arXiv 2605.20695](https://arxiv.org/abs/2605.20695) ("Remarks on the disproof…"); anúncio em [openai.com](https://openai.com/index/model-disproves-discrete-geometry-conjecture/) |
| 2026-05-21 (v2 06-08) | Google DeepMind | AlphaProof Nexus: 9 de 353 problemas de Erdős formalizados, 44 de 492 conjecturas do OEIS, um problema da lista de Ben Green | subagentes LLM (Gemini) ↔ compilador do Lean; a versão completa tem população evolutiva de esboços e o AlphaProof como ferramenta; "algumas centenas de dólares" por problema | **sim, Lean** de ponta a ponta; especialistas conferiram que o enunciado em Lean diz o que o problema diz | [arXiv 2605.22763](https://arxiv.org/abs/2605.22763) |
| 2026-08-01 (rev. 08-06) | OpenAI | "Ten advances": empacotamento de esferas (limiar de Cohn–Elkies), códigos binários e esféricos, grupo não-sófico, rigidez de Connes, permanente, repetição paralela quântica, CVP, volume de Ehrhart, Erdős 183, 146 e 180 | não descrita no manuscrito (só os resultados); fontes secundárias falam do modelo interno "Astra" | **sim, Lean 4.32 + mathlib**: `formalization.yaml` declara `sorry_count: 0` e só os axiomas `propext`, `Quot.sound`, `Classical.choice`; `grep -c sorry` deu 0 nos 11 arquivos. Cada resultado tem um **desafio do Comparator** (enunciado curto com `sorry` + módulo solução + axiomas permitidos + checador independente `nanoda`) | [PDF](https://cdn.openai.com/pdf/ten-proofs-oai.pdf), [github.com/openai/ten-proofs](https://github.com/openai/ten-proofs) |
| 2026-04-04 (v2 05-30) | Ju et al. (Pequim) | conjectura de Anderson (álgebra comutativa) | dois agentes: raciocínio informal com busca de teoremas (Rethlas/Matlas) e formalização (Archon/LeanSearch) | **sim, Lean 4**, "essencialmente sem humano" | [arXiv 2604.03789](https://arxiv.org/abs/2604.03789) |
| 2025-11-03 (base) | DeepMind + Tao, Gómez-Serrano, Georgiev, Wagner | AlphaEvolve em 67 problemas; melhoras em vários, inclusive Kakeya em corpo finito (d = 3, 4, 5) | LLM evolui **programas** que buscam construções; avaliador automático | só **um** caso (Kakeya, d = 3) foi formalizado em Lean, pelo AlphaProof, "porque os passos já estavam na mathlib"; o resto é construção conferida por avaliador ou prova à mão | [arXiv 2511.02864](https://arxiv.org/abs/2511.02864) |

**Release `openai/math` (criado em 2026-10-06, [github.com/openai/math](https://github.com/openai/math)).**
Não li este repositório; registro a leitura do dono, que o varreu inteiro (~722 problemas) em
2026-10-07: **nada direto** de códigos de cobertura, K_q(n,R), Kéri, Hadamard, Schur, Euler ou
*decks*. Conexões estruturais que ele viu: a família 133 (k-WL) com a nossa escada J em isomorfismo
de grafos, a família 102 com NP/compressão, e o tema de formalização e proveniência. O cruzamento
automático dos 722 problemas com este repositório é tarefa de outro agente da campanha
(m6-cruzamento), não deste documento.

Contexto que pesa na leitura:

- Em outubro de 2025 a OpenAI anunciou "10 problemas de Erdős resolvidos" pelo GPT-5; o mantenedor
  do erdosproblems.com chamou de "deturpação dramática": o modelo tinha **achado na literatura**
  soluções que ele não conhecia ([TechCrunch](https://techcrunch.com/2026/05/20/openai-claims-it-solved-an-80-year-old-math-problem-for-real-this-time/),
  [Quanta](https://www.quantamagazine.org/why-the-legendary-erdos-problems-are-falling-to-ai-20260803/)).
  Busca na literatura é o primeiro uso real dessas ferramentas, e também a primeira fonte de alarme
  falso.
- O levantamento de [arXiv 2608.24961](https://arxiv.org/abs/2608.24961) (Jin, Ke, Sui, 25/08/2026)
  conta artigos de matemática com IA: 71% se dizem "totalmente resolvidos" **pela descrição dos
  próprios autores**, sem separar o que tem verificação formal. Combinatória é a área com mais
  artigos.
- O AlphaProof Nexus relata lemas "da literatura" que o modelo citou e que eram **alucinação**; o
  Lean os pegou. É o argumento deles para verificação de ponta a ponta.

## Códigos de cobertura em 2026: o que existe

Nenhum destes declara uso de IA. Os três primeiros já estão no ledger e nos levantamentos
anteriores (ver `docs/literatura/VARREDURA_2026-10-03.md` e `docs/literatura/STATE_OF_ART.md`).

- **Marosi**, arXiv [2608.19872](https://arxiv.org/abs/2608.19872) (v1 20/08, v3 02/09/2026):
  25 superiores para 5 ≤ q ≤ 15 (busca local com sementes estruturais + LNS com "transformadas de
  cobertura do espaço inteiro" que avaliam todas as posições candidatas de uma vez) e 58 inferiores
  para 6 ≤ q ≤ 21 pela hierarquia SDP de Gijswijt–Polak, cada uma com **dual racional** conferido
  por checador em aritmética exata. Não toca q ≤ 4.
- **Gijswijt–Polak**, arXiv [2504.01932](https://arxiv.org/abs/2504.01932) (v2 19/06/2026): SDP
  para q ≤ 5.
- **Florath 2026**: K_8(4,2) = 23 certificado em Lean (arXiv 2606.16688) e o certificado Lean da
  prova SDP de K_2(13,1) ≥ 607 (Zenodo 10.5281/zenodo.21024792). É o único precedente de cota
  **inferior** por SDP checada em Lean.
- **Wu**, arXiv [2608.27494](https://arxiv.org/abs/2608.27494) (26/08/2026): código linear
  [50,40]_2 de raio 2, ℓ_2(10,2) ≤ 50. Comprimento 50 está fora do ledger (q = 2 vai até n = 33).
- **Boyvalenkov–Özbudak–Stoyanova**, arXiv [2605.03589](https://arxiv.org/abs/2605.03589): raio de
  cobertura de arranjos ortogonais (LP). Outro problema: o raio de um objeto dado, não K_q(n,R).

## O que se aplica ao ledger, e o que não

Estado medido no `main` (commit 82b7ac0) com `ledger/cells.json`: 1145 células; cota superior
FORMALIZED em 551, INDEPENDENTLY_REPRODUCED em 91, CLAIMED em 503; cota inferior **CLAIMED em
1140**, CERTIFICATE_VERIFIED em 3, FORMALIZED em 2. O buraco formal está nas inferiores.

**Não se aplica:**

- Os resultados em si. Empacotamento assintótico (OpenAI, capítulo 2), Erdős, OEIS: nada vira
  número em célula nossa. O método espectral da OpenAI (harmônicos booleanos sobre camadas de peso,
  generalizando o argumento da MRRW) é parente das cotas LP/SDP, mas foi feito para empacotamento e
  para n → ∞; transportar para cobertura com n ≤ 33 é pesquisa, não tarefa de uma madrugada.
- "Modelo de raciocínio resolve sozinho": nem a OpenAI descreve o processo, e o custo por problema
  no AlphaProof Nexus (centenas de dólares, até 3000 episódios) não cabe em US$ 30.
- Prova formal de recorde de busca: o AlphaEvolve só formalizou quando a mathlib já tinha os
  passos. Os nossos certificados de cota superior já são `decide` no kernel, que é o caso fácil.

**Aplica-se:**

1. A divisão de trabalho do AlphaEvolve: o LLM é caro e criativo, então ele escreve a **estratégia
   de busca**, que roda barata e em escala; o avaliador decide. Os autores registram três
   lições que valem direto para nós: o avaliador é o componente crítico; o sistema **trapaceia**
   quando o avaliador vaza (ponto flutuante, aproximação de restrição global); função de perda
   contínua guia melhor do que discreta.
2. O formato do Comparator: um arquivo de desafio de ~150 linhas que só **define** e **enuncia**
   (ex.: `B_BinaryCodes.lean` define distância de Hamming, código e a taxa como `limsup`), a
   solução em outro módulo, a lista de axiomas permitidos num JSON, e um segundo verificador de
   kernel (`nanoda`). Quem revisa lê só o enunciado. Hoje o nosso `evaluators/lean_honesty.py` é
   análise de texto (o próprio arquivo declara o limite: "macros que gerem `sorry` só um
   `lake build` mostra"), e o predicado de cobertura está definido mais de uma vez em
   `CoveringLean/` (`def Covers` aparece em `A2_Sphere.lean`, `A4_Closed.lean` e `A6_Finite.lean`,
   e `Kle` também em `A4_Closed.lean`).
3. Lemas de teste contra enunciado errado (AlphaProof Nexus, OEIS): antes de atacar a conjectura,
   o agente prova que a definição formal reproduz os primeiros termos conhecidos. Para nós:
   antes de aceitar uma definição de K_q(n,R) num arquivo novo, ela tem de provar valores triviais
   conhecidos (por exemplo K_2(3,1) = 2 e K_q(n,n) = 1).
4. O caminho AlphaEvolve → prova → Lean para inferiores: dual racional do SDP conferido em
   aritmética exata (Marosi), depois em Lean (Florath). É o que tira inferiores de CLAIMED.

## Técnicas para os agentes testarem nesta campanha (prioridade)

Cada uma com o avaliador barato e exato que decide, porque sem avaliador o LLM está adivinhando.

1. **Evoluir a heurística, não o código (AlphaEvolve aplicado às superiores).**
   O Gemini do Infinito gera variantes de um gerador de busca (semente estrutural + movimentos de
   busca local), cada variante roda alguns minutos em CPU spot sobre um conjunto fixo de células
   abertas, e a nota é o tamanho do melhor código **conferido pelo verificador oficial**
   (binário de `tools/verify/verify.c`, compilado por `tools/verify/check_all.sh`). Perda contínua: número de palavras descobertas ponderado, não só
   "cobre/não cobre". Rodar o mesmo programa em várias (q,n,R) ao mesmo tempo, como o artigo
   recomenda. Custo: poucos centavos de LLM por geração; o grosso é CPU. Sucesso: um tamanho abaixo
   do ledger, verificado. Risco conhecido: trapaça do avaliador — o avaliador nunca pode ser o
   próprio programa evoluído.
2. **Enunciado único + Comparator nos certificados do kernel.**
   Um módulo só de definições e enunciados (o predicado de cobertura e `K ≤ M`, `K ≥ M`), todos os
   certificados importando dele, e um JSON por cota com o nome do teorema e os axiomas permitidos,
   checado com `leanprover/comparator` (+ `nanoda`). Avaliador: o próprio Comparator, binário.
   Custo: zero em API; um `lake build` (pode ir para o `pesado`). Sucesso: N certificados existentes
   passando no Comparator sem mudança de enunciado. Mexe em `CoveringLean/` com enunciado: risco
   alto, aprovação do mantenedor.
3. **Lemas de teste na definição.** Barato e imediato: provar no mesmo módulo de enunciados, por
   `decide`, meia dúzia de valores conhecidos (triviais e alguns exatos pequenos já
   FORMALIZED). Se a definição estiver errada, os lemas falham antes de qualquer cota "nova".
4. **Inferior por SDP com dual racional, depois Lean.** Escolher 1–3 células cuja inferior vem de
   Gijswijt–Polak ou Marosi (q ≤ 21), reconstruir o dual racional, conferir com checador exato
   (CERTIFICATE_VERIFIED) e só então tentar o Lean no formato do certificado de Florath para
   K_2(13,1) ≥ 607. Avaliador: checagem exata de positividade semidefinida do dual (racional, sem
   ponto flutuante). Ganho: atacar o 1140 de 1145 inferiores CLAIMED.
5. **Loop LLM ↔ Lean só para lemas pequenos.** Agente A do AlphaProof Nexus: o erro do compilador
   volta para o prompt, com teto de tentativas e de custo por lema (ex.: US$ 0,50). Alvos: regras de
   propagação que o ledger usa e ainda não estão no kernel (monotonicidade em n e em R, soma
   direta), não recordes. Avaliador: `lake build` do arquivo. O próprio artigo diz que o agente
   básico custa mais nos problemas difíceis: não usar em problema difícil.

Fica de fora de propósito: pedir ao modelo uma "prova" de exato em linguagem natural. Resposta de
LLM é hipótese; sem o Lean ou o verificador ela não entra no ledger (regra do `AGENTS.md`).
