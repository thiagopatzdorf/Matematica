# Autópsia do único claim REFUTED: `h2-gap-nondecreasing`

Data: 2026-10-03. Agente P1. Convenção: **MEDI** = rodei e a saída está citada; **LI** = li arquivo:linha; **NÃO CONSTA** = procurei e não achei.
Restrições desta autópsia: sem git (então "git log/blame" **não foi consultado**, ver §9), sem rede (Zenodo v0.3 não foi aberto), US$0.

## 1. Respostas diretas

| pergunta | resposta |
|---|---|
| Qual era a afirmação? | **H2**: "o gap aditivo `K_q(n,R) − ⌈q^n/V⌉` é não decrescente em `n`", com `V` o tamanho da bola de raio `R` e `⌈·⌉` o teto da cota de esfera. É uma hipótese interna do autor, não um resultado da literatura. |
| Onde nasceu? | No comentário de `CoveringLean/A6c_Search.lean:8-12` ("so H2 ('the gap is nondecreasing in n') is false") e no cabeçalho de `A6_Finite.lean:4` ("refutations of H1, H2, H3, H5"). Não existe enunciado de H2 em nenhum outro arquivo versionado. |
| Por que foi refutada? | Gap em `(q,n,R)=(2,6,1)` é `≥ 1` e em `(2,7,1)` é `0`: `K_2(6,1) ≥ 11` e `⌈64/7⌉ = 10` dão gap `≥ 1`; `K_2(7,1) = 16 = 128/8` (Hamming `[7,4]` perfeito) dá gap `0`. Logo o gap **diminui** de `n=6` para `n=7`. |
| Tipo da refutação | **Formal, por contraexemplo finito decidido no kernel**, sem busca e sem oráculo externo. Detalhe em §3. Não é lógica pura, não é bibliográfica, e a parte computacional que existiu (busca exaustiva `refuted 64 7 …`) foi **abandonada**. |
| Quem depende do H2? | **Ninguém.** Nenhum claim, lema Lean, resíduo, tabela ou texto público usa H2 como premissa (§4). H2 é folha: depende de lemas PROVED e nada depende dele. |
| Frases públicas que ainda reproduzem H2? | **Nenhuma como afirmação.** O README (linha 23) só a cita para dizer que está refutada; paper, PDF e `nota.md` nunca a mencionam. Havia 3 imprecisões vizinhas, corrigidas (§5). Zenodo v0.3: não aberto (sem rede); o `paper/main.tex`/`main.pdf` do repositório não contêm H2. |
| Alguma tabela precisa ser regenerada? | **Não.** Nenhuma tabela do repositório tem coluna de gap nem usa monotonia do gap (§6). |
| Contaminação downstream? | **Nenhuma** (§4). O defeito real foi outro: H1, H3 e H5 eram refutadas no Lean e **não existiam na campanha** (§7). |

## 2. Origem e afirmação exata

LI `A6c_Search.lean:8-12`:
> `K_2(6,1) = 12` (C oracle); the sphere bound only gives `⌈64/7⌉ = 10`. We prove `≥ 11`, which is enough: the additive gap `K - ⌈S⌉` is `≥ 1` at `(2,6,1)` but `0` at `(2,7,1)` (`K_2(7,1) = 16 = 128/8`), so H2 ("the gap is nondecreasing in n") is false.

Leitura formal da hipótese (minha, a partir do comentário; o autor não a escreveu como fórmula): para `q` e `R` fixos, `g(n) := K_q(n,R) − ⌈q^n / V(q,n,R)⌉` satisfaz `g(n) ≤ g(n+1)`. Escopo do claim na campanha: `q=2, R=1`.

Contexto numérico: `A6_Finite.lean` numera as seções `(1) H5`, `(2) H1`, `(3) H3`, `A6b` `(4) Tightness` (não é refutação), `A6c` `(5) H2`. **H4 NÃO CONSTA** em nenhum arquivo (provavelmente é a seção (4), que prova que a cota de esfera é atingida por Hamming; isto é HIPÓTESE minha).

Arquivos que mencionam H2 (grep em tudo, exceto `.lake`, `.git`, `audit/`, `verifier_runs/`, `reports/lean-build-*`):

| arquivo | papel |
|---|---|
| `CoveringLean/A6c_Search.lean:8,12,183-194` | origem; `H2_counterexample` **condicional** a `refuted 64 7 bm6 nbr6 10 0 = true`, ainda na biblioteca |
| `CoveringLean/A6d_SearchHeavy.lean:10,20-28` | `H2_unconditional`: tentativa de remover a condição por busca no kernel; **nunca compilou** (>24 GB de RAM em ~2,5 min); fora de `CoveringLean.lean`; obsoleto |
| `CoveringLean/A6e_Excess.lean:148-161` | `H2_counterexample_uncond`: a refutação final, incondicional |
| `CoveringLean/A6_Finite.lean:4` | cabeçalho que lista H1, H2, H3, H5 |
| `README.md:23,80` | linha 23: "refuta H2 sem hipótese"; linha 80: tabela de arquivos |
| `tools/campaign/migrate_covering.py` | cria o claim, o contraexemplo e o registro formal |
| `campaigns/covering-codes/{claims,counterexamples,formal}/…h2…` | os três registros; `_fatos/PILOT_FACTS.md:49,154`; `_fatos/axiomas/_lemas_do_alvo_padrao.txt:7`; `reports/REPRODUCTION_REPORT.md` (linha do registro formal) |
| `docs/`, `scripts/`, `paper/main.tex`, `paper/main.pdf`, `nota.md`, `CITATION.cff` | **NÃO CONSTA** (grep de `H2`, `gap`, `nondecreas`, `monoton`; `pdftotext` do PDF) |

`migrate_covering.py` e A6d fazem parte do histórico, não foram alterados. `nota.md` é o texto de v0.2 (commit `54424602`, branch `research/preco-da-impossibilidade`, LI no próprio `nota.md`); já estava marcado como desatualizado em `_fatos/PILOT_FACTS.md:140`.

## 3. Por que foi refutada, e de que tipo

**Teorema** (`A6e_Excess.lean:149-154`, copiado):

```lean
theorem H2_counterexample_uncond :
    (∀ C : Finset (W 2 6), C.card < 11 → ¬ Covers 1 C) ∧
    (∃ C : Finset (W 2 6), C.card = 12 ∧ Covers 1 C) ∧
    IsK 2 7 1 16 ∧ HasVol 2 6 1 7 ∧ (2 ^ 6 + 7 - 1) / 7 = 10 ∧ (2 ^ 7 + 8 - 1) / 8 = 16
```

Cada conjunto é uma peça da refutação e vem de um mecanismo diferente:

1. **`K_2(6,1) ≥ 11`** = `no_cover_2_6_1_le10_uncond` (`A6e:129`): contagem dupla do excesso (`excess_bound`, abstrata) + `even_inter` (`|B(a) ∩ B(c)|` é par para `a ≠ c`, 64×64 casos por `decide +kernel`) + `vol_2_6_1` (`HasVol 2 6 1 7`, `decide +kernel`) + `omega`. **Sem busca.**
2. **`K_2(6,1) ≤ 12`** = `code12_card` e `code12_covers` (`A6c:180-181`, `decide +kernel` sobre 12 palavras). **Não é necessário para a refutação** (só `≥ 11` basta); está no enunciado porque `K_2(6,1) = 12` é o valor real.
3. **`K_2(7,1) = 16`** = `K_2_7_1` (`A6b:33`): `hamming_card`, `hamming_covers` (`decide +kernel`) mais `not_covers_of_count` (cota de esfera por contagem, `A6_Finite`). **Formal, sem busca.**
4. **Aritmética dos tetos**: `(2^6+7−1)/7 = 10`, `(2^7+8−1)/8 = 16` por `norm_num`.

Conclusão: `g(6) ≥ 11 − 10 = 1` e `g(7) = 16 − 16 = 0`, então `g(7) < g(6)` e H2 é falsa.

**Classificação precisa**: refutação **formal por contraexemplo finito (instância `(2,6,1)→(2,7,1)`)**, 100% decidida no kernel do Lean 4.34.1 + Mathlib v4.34.1, `#print axioms` = `propext, Classical.choice, Quot.sound`, sem `sorry`, sem `native_decide` (registro formal `f-h2-counterexample`, `axioms_status: OK`, `sorry_free: true`, `source_sha256 2b31e93a…d892e`).

Três ressalvas que a classificação "formal" não apaga:

* **A dedução final não está no kernel.** O Lean prova os seis fatos; ele **não define** `gap` nem enuncia `¬ (∀ n, gap n ≤ gap (n+1))`. O passo "esses fatos ⇒ ¬H2" é uma linha de aritmética feita à mão (e aqui). É a mesma pendência já declarada para todos os claims: "que os enunciados formais são os pretendidos é revisão humana" (README, "O que NÃO está provado").
* **O "gap = 2" do registro do contraexemplo usa `K_2(6,1) = 12`**, que não é teorema do alvo padrão (`SC.K_2_6_1_eq12` é do alvo pesado, não reproduzido; o claim `k2-6-1-eq-12` é `EXHAUSTIVE_BOUNDED`). O que o kernel do alvo padrão sustenta é o gap `≥ 1`, que já refuta. A descrição de `cx-h2-gap-nondecreasing` ("12−10 = 2") é verdadeira dado o valor clássico (Stanton–Kalbfleisch, citado no Kéri e no Florath, **não lido**), mas a refutação **não depende dele**.
* **História computacional**: a primeira versão (`A6c`, `H2_counterexample`) era *condicional* a uma busca exaustiva no kernel que nunca compilou (A6d, OOM); o valor `K_2(6,1) ≥ 11` valia então como `COMPUTATIONALLY_VERIFIED` por oráculo C (LI cabeçalho de A6d). A refutação só virou incondicional quando a contagem dupla (A6e) substituiu a busca. O condicional segue na biblioteca (`H2_counterexample`, `no_cover_2_6_1_le10`, `refuted_sound`) como legado; nada o usa além de A6d.

Quanto ao tipo "lógica/bibliográfica": **não** é bibliográfica (nenhum resultado externo foi usado como premissa) e **não** é puramente lógica (depende de fatos numéricos específicos).

## 4. Auditoria, derivados, grafo de dependências

### Eventos de auditoria (`audit/log.jsonl`)

A campanha é refeita do zero por `tools/campaign/migrate_covering.py`; cada refação reescreve a cadeia (os `seq` mudam). Por isso **a cadeia anterior foi copiada, não alterada**, para `_autopsia/audit-pre-regeneracao/` (`log.jsonl`, `anchors.jsonl`, `SHA256SUMS`, e os 3 registros de H2). `log.jsonl` anterior: sha256 `bd0f0516…b533`, 356 eventos, âncora seq 320.

| momento | seq | ação | hash (64 hex) |
|---|---|---|---|
| anterior | 83 | `formal.create f-h2-counterexample` | `f337f04685eb06b9…` |
| anterior | 205 | `counterexamples.create cx-h2-gap-nondecreasing` (agente-c) | `484bf484738148e24e0361316f9cd4651dc656df0b75780490d78b5007ca9c65` |
| anterior | 206 | `claim.create` IDEA | `077878af4808231d81ac59539e73ab5b175e3f71fc484e67651df91f011c7600` |
| anterior | 207 | `claim.evidence` formal | `d5e4cc0f027aaa11601d50b01228681de311aaeac502ec69009e80104f547879` |
| anterior | 208 | `claim.status.CONJECTURE` | `3043ddb9257981c2688f63eb9675dc88af3ccc5f462222114e2ede64447f9296` |
| anterior | 209 | `claim.evidence` counterexamples (migrate_covering.py) | `eda15c52ba1d747a497962d0d4f9e85850d486bdb1e81c178f90914027acfd57` |
| anterior | 210 | `claim.status.REFUTED` | `6d01a4ed392269e0b477a1a813824faa9f6acdb49df7c7b8a73ac42e2e6db133` |
| **atual** | 83 | `formal.create f-h2-counterexample` | `0ded24deca05c959…` |
| **atual** | 208 | `counterexamples.create cx-h2-gap-nondecreasing` | `cfa756f215aac1004798a4e7fe74ea2449e6c54ec05e6a48e855b3cb56bcc49a` |
| **atual** | 209 | `claim.create` | `a1935e836f30a45d9fed5a4281048fafb5bf1f00ed20060ea6f3f7a1953eb5ce` |
| **atual** | 210 | `claim.evidence` formal | `c4c450bbf85d8de22014dce001afa8b02f885e8c5b25b59c6d3b3d3e1e78901e` |
| **atual** | 211 | `claim.status.CONJECTURE` | `082f969d008ea3d10f76fc404f5119cd656f7e7a98d8f62e3c2d9aa350385ae9` |
| **atual** | 212 | `claim.evidence` counterexamples | `10ff5456fa7c3ebf69a8b37ada7dba94599b7544bcb4c3eb4caa2c44d1a985c8` |
| **atual** | 213 | `claim.status.REFUTED` | `b4e999cba2001990a9a714559de5a291aa72f152eef246caf0cf02e08c3b42db` |

Estados do claim: IDEA → CONJECTURE → REFUTED (guarda de REFUTED: contraexemplo registrado; o claim nunca passou de CONJECTURE, então não exigiu witness). Atores: `agente-c` (PROPOSER, cria) e `migrate_covering.py` (COUNTEREXAMPLE_HUNTER, refuta); o registro formal foi medido por `migrate_covering.py` (FORMALIZER) com `lake build` real.

### Derivados do claim

`claims/h2-gap-nondecreasing.json`, `counterexamples/cx-h2-gap-nondecreasing.json`, `formal/f-h2-counterexample.json`; linha em `reports/REPRODUCTION_REPORT.md`. Nenhum witness, experimento, verificador, literatura ou resíduo.

### Grafo de dependências

```
h2-gap-nondecreasing (REFUTED, depends_on = [])
  └─ evidência: cx-h2-gap-nondecreasing, f-h2-counterexample
       └─ CoveringA6.H2_counterexample_uncond  (A6e:149)   <-- folha: ninguém a usa
            ├─ no_cover_2_6_1_le10_uncond (A6e:129)
            │    ├─ excess_bound   (A6e)         = claim excess-bound-lemma      (PROVED)
            │    ├─ even_inter     (A6e:123)     = claim even-inter-ball1-binary (PROVED)
            │    └─ vol_2_6_1      (A6e:121)
            ├─ code12, code12_card, code12_covers (A6c:177-181)
            ├─ K_2_7_1 (A6b:33) ← hamming_card, hamming_covers, vol_2_7_1, not_covers_of_count (A6_Finite)
            ├─ vol_2_6_1
            └─ norm_num (os dois tetos)
```

Quem usa cada lema da refutação (a seta é "usado por"; nenhuma chega ao H2):

| lema | usado por |
|---|---|
| `excess_bound`, `even_inter` | `no_cover_2_6_1_le10_uncond` → `K_2_6_1_ge_11` → claim `k2-6-1-lb-11` (PROVED); claims `excess-bound-lemma`, `even-inter-ball1-binary` (PROVED) |
| `vol_2_6_1` | `no_cover_2_6_1_le10_uncond`, `H2_counterexample_uncond` |
| `no_cover_2_6_1_le10_uncond` | `K_2_6_1_ge_11`, `H2_counterexample_uncond` |
| `K_2_6_1_ge_11` | claim `k2-6-1-lb-11`; **nenhum teorema Lean** |
| `code12`, `code12_card`, `code12_covers` | `SearchSound.lean:471-473` (`K_2_6_1_eq12`), claims `k2-6-1-ub-12` (PROVED) e `k2-6-1-eq-12`, witness `w-q2-n6-r1-m12` (derivado de `def code12`) |
| `K_2_7_1` | **só** `H2_counterexample` (A6c:188) e `H2_counterexample_uncond`; nenhum claim |

Sentido da dependência: a **refutação depende** de lemas que sustentam claims PROVED; **nenhum claim depende do H2**. Se um desses lemas fosse falso, a refutação cairia, não o contrário. A refutação **não** é circular com `k2-6-1-lb-11` (a mesma peça `K_2_6_1_ge_11` é usada em ambos, e está medida).

A "monotonia" que existe na biblioteca (`A4_Closed`: `Kle_mono_R`, `K_q(n+1,R+1) ≤ K_q(n,R)`; `A5_Frontier`: `achievesEps_mono`) é sobre `K` em `R`/`n`/`ε`, **não** sobre o gap; não é H2 nem depende dela.

## 5. Frases públicas

| lugar | situação | ação |
|---|---|---|
| `README.md:23` | cita "H2" sem dizer o que é (crítico para quem lê; não afirma H2) | **corrigido**: agora diz o que H2 afirmava e que foi refutada |
| `README.md:78` | "contra-exemplos H5, H1, H3" sem dizer que são refutações nem que a campanha as registra | **corrigido** (mesma linha, sem mudar a numeração do README, que `migrate_covering.py` cita por linha) |
| `README.md:80` | `H2_counterexample_uncond` na tabela de arquivos: correto | nada |
| `nota.md:41` | "`K_2(6,1) ≥ 11` continua condicional … não compila": **falso** no repositório atual (`K_2_6_1_ge_11` é incondicional desde A6e); era verdade só no tar do commit `54424602` | **corrigido**, preservando a ressalva do snapshot |
| `nota.md:38` | "`K_7(9,4) ≤ 1351` não é teorema": também falso hoje (`K7_9_4_le_1351_kernel`, alvo pesado, não reproduzido pela campanha) | **corrigido** no mesmo espírito (não é H2, é a mesma classe: texto vivo desatualizado) |
| `paper/main.tex`, `paper/main.pdf` | não mencionam H2. A linha 106 ("replaces a hypothesis that the previous version … left open") fala da condição `refuted … = true` da busca, **não** do H2; está correta | **não editado** (publicação; decisão do dono) |
| Zenodo v0.3 | não aberto (sem rede). O tag é o mesmo `v0.3.0` do `paper/main.pdf` do repositório, que não tem H2 | nada a fazer |

## 6. Tabelas e contaminação

* **Tabelas**: nenhuma tabela do README/paper/nota/`docs/` tem coluna de gap ou usa a monotonia do gap (grep de `gap`, `ceil`, `nondecreas`). As tabelas de cotas (`SPH_*`) são cotas de esfera e não dependem de H2. `campaign.json` `universe` (9 células `(q,n,R)`) também não: não houve mudança de universo. **Nada a regenerar.** O `REPRODUCTION_REPORT.md` foi regenerado só porque a migração apaga `reports/`.
* **Downstream**: `depends_on` de H2 é `[]` e nenhum claim o cita; resíduos (`res-a6d-searchheavy`) falam de `K_2(6,1) ≥ 11`, não de H2; o teste (c) abaixo prova que nenhum claim ≥ EMPIRICAL depende, nem transitivamente, de REFUTED.

## 7. Achado maior: três refutações órfãs (H1, H3, H5)

`A6_Finite.lean` refuta mais três hipóteses, todas com `#print axioms` limpo, e **a campanha só registrava o H2**: evidência negativa no Lean e ausente do sistema. Agora registradas (REFUTED, `kind: conjecture`, com contraexemplo e registro formal medido; os enunciados Lean abaixo foram copiados por regex do `.lean` na migração e estão em `refuting_lean_statement` de cada claim).

| claim | hipótese (leitura do comentário) | contraexemplo |
|---|---|---|
| `h1-alpha-nonincreasing` | `α(q,n,R) = K·V/q^n` é não crescente em `n` (`A6_Finite:95`) | `α(2,3,1)=1 → α(2,4,1)=5/4` |
| `h3-alpha-le-2` | `α(q,n,R) ≤ 2` para todo `(q,n,R)` (`A6_Finite:102`) | `α(3,3,2)=19/9 > 2` (`K_3(3,2)=3`, `V=19`) |
| `h5-ceil-bound-needs-perfect` | se `V ∤ q^n` então `K > ⌈q^n/V⌉` (a cota com teto só é atingida por perfeitos) | `K_2(2,1)=2=⌈4/3⌉`, `V=3 ∤ 4` |

**Limitação declarada**: o texto original de H1, H3 e H5 **NÃO CONSTA** em arquivo versionado além do nome e do comentário de uma linha em `A6_Finite.lean`. O de H5 é **inferido** (do enunciado que o Lean refuta e de `no_perfect` em `A2_Sphere`); o de H3 só tem o "2" e a desigualdade lidos do cabeçalho. O que está **certo** é o que o Lean refuta literalmente (`refuting_lean_statement`); a ligação com a hipótese do autor é interpretação. Quem tiver o texto original deve conferir os três enunciados.

## 8. Defeito que tornou o erro provável, e as regras que ficaram

* **O que faltava** (entropia local): nada ligava "a biblioteca refuta `H<n>`" a "a campanha tem esse claim". O H2 só foi registrado porque o autor o usou como exemplo do fluxo REFUTED; as outras três ficaram só no Lean.
* **Regras determinísticas** (`tests/test_refuted_hypotheses.py`, 6 testes, verificados por mutação: injetei um parágrafo "o gap é não decrescente" no README e um `H4_counterexample` num `.lean` temporário, ambos falharam e foram revertidos):
  * (a) falha se existir `theorem H<n>_counterexample*`/`H<n>_unconditional*` em `CoveringLean/*.lean` sem claim REFUTED `H<n>:` com contraexemplo e registro formal medido (axiomas ⊆ {propext, Classical.choice, Quot.sound}, `sorry_free`);
  * (b) falha se README, nota.md, `docs/*.md` ou `paper/main.tex` citarem `H<n>` ou reescreverem a hipótese (paráfrases em `PARAFRASES`) num parágrafo sem palavra de refutação; inclui controle positivo; falha também se uma hipótese refutada não tiver paráfrase cadastrada;
  * (c) falha se claim ≥ EMPIRICAL depender, direta ou transitivamente, de claim REFUTED.
  * Limite do (b): é heurístico (regex por parágrafo); pega o H2 reintroduzido em PT/EN, não toda reformulação.
* `python3 -m unittest discover -s tests`: **72 testes, OK** (66 antigos + 6 novos).

## 9. O que NÃO foi feito, e por quê

* **git log/blame** (autoria e data da introdução de H2, commit em que A6c/A6e mudaram): **não consultado**, por restrição da tarefa. Para fechar: `git log -S'nondecreasing' --follow -- CoveringLean/A6c_Search.lean` e `git log --follow -- CoveringLean/A6e_Excess.lean CoveringLean/A6d_SearchHeavy.lean`.
* Zenodo v0.3 (arquivo publicado) não foi aberto (sem rede).
* `paper/main.tex` não foi editado (nada a corrigir sobre H2).
* O texto original de H1/H3/H5 não foi encontrado (§7).
* A revisão humana dos enunciados formais (`statement_review`) segue pendente: nenhum claim é `FORMALLY_VERIFIED`, e isto inclui o passo "fatos ⇒ ¬H2" (§3).
