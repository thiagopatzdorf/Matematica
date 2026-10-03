# Fatos da campanha piloto `covering-codes` (Agente C)

Data da medição: 2026-10-02. Repositório: `/home/user/Matematica`, HEAD `bc3a3d727557e081fd0cabcc3580ede7e0da3e13`
(Merge #3), árvore com arquivos novos não versionados (os meus: `tools/campaign/`, `tests/test_campaign_verifier.py`,
`campaigns/`). Ambiente: container Linux x86_64, 4 vCPU, 15 GiB de RAM, Python 3.11.15, gcc 13.3.0, numpy 2.4.6.

Convenção: **MEDI** = rodei neste ambiente e a saída está citada; **DECLARADO** = só está escrito no README/paper/CI
(e não foi reproduzido aqui); **LI** = li o artefato (arquivo:linha), sem rodar nada. Nada abaixo foi inventado: o que
não achei em artefato está dito como "não achei".

---

## 1. Teoremas Lean finais do piloto (enunciados copiados dos `.lean`)

Definições (`CoveringLean/A2_Sphere.lean:25-30` e `A6_Finite.lean:24-43`):

```lean
-- A2_Sphere: Fin n → ZMod q
def ball (R : ℕ) (c : Fin n → ZMod q) : Finset (Fin n → ZMod q) := univ.filter fun x => hammingDist x c ≤ R
def Covers (R : ℕ) (C : Finset (Fin n → ZMod q)) : Prop := ∀ x : Fin n → ZMod q, ∃ c ∈ C, hammingDist x c ≤ R
-- A6_Finite: Fin n → Fin q
abbrev W (q n : ℕ) := Fin n → Fin q
def Covers {q n : ℕ} (R : ℕ) (C : Finset (W q n)) : Prop := ∀ x : W q n, ∃ c ∈ C, hammingDist x c ≤ R
def IsK (q n R k : ℕ) : Prop := (∃ C : Finset (W q n), C.card = k ∧ Covers R C) ∧ ∀ C : Finset (W q n), C.card < k → ¬ Covers R C
```

| teorema (nome qualificado) | arquivo:linha | enunciado EXATO | alvo | axiomas |
|---|---|---|---|---|
| `CoveringChain.SPH_K5_7_2_lb` | `Chain.lean:33` | `(C : Finset (Fin 7 → ZMod 5)) (hC : CoveringA2.Covers 2 C) : 215 ≤ C.card` | padrão | MEDI |
| `CoveringChain.SPH_K4_10_4_lb` | `Chain.lean:36` | `(C : Finset (Fin 10 → ZMod 4)) (hC : CoveringA2.Covers 4 C) : 51 ≤ C.card` | padrão | MEDI |
| `CoveringChain.SPH_K5_9_3_lb` | `Chain.lean:39` | `(C : Finset (Fin 9 → ZMod 5)) (hC : CoveringA2.Covers 3 C) : 327 ≤ C.card` | padrão | MEDI |
| `CoveringChain.SPH_K5_10_4_lb` | `Chain.lean:42` | `(C : Finset (Fin 10 → ZMod 5)) (hC : CoveringA2.Covers 4 C) : 158 ≤ C.card` | padrão | MEDI |
| `CoveringChain.SPH_K5_9_5_lb` | `Chain.lean:45` | `(C : Finset (Fin 9 → ZMod 5)) (hC : CoveringA2.Covers 5 C) : 12 ≤ C.card` | padrão | MEDI |
| `CoveringChain.SPH_K5_9_4_lb` | `Chain.lean:48` | `(C : Finset (Fin 9 → ZMod 5)) (hC : CoveringA2.Covers 4 C) : 52 ≤ C.card` | padrão | MEDI |
| `CoveringChain.SPH_K7_8_3_lb` | `Chain.lean:51` | `(C : Finset (Fin 8 → ZMod 7)) (hC : CoveringA2.Covers 3 C) : 439 ≤ C.card` | padrão | MEDI |
| `CoveringChain.SPH_K7_9_4_lb` | `Chain.lean:54` | `(C : Finset (Fin 9 → ZMod 7)) (hC : CoveringA2.Covers 4 C) : 221 ≤ C.card` | padrão | MEDI |
| `CoveringA6.K_2_6_1_ge_11` | `A6e_Excess.lean:144` | `(C : Finset (W 2 6)) (hC : Covers 1 C) : 11 ≤ C.card` | padrão | MEDI |
| `SC.K_2_6_1_eq12` | `SearchK6ge12.lean:17` | `IsK 2 6 1 12` (≥12 vem de `SC.K_2_6_1_ge12 : ∀ C : Finset (W 2 6), C.card < 12 → ¬ Covers 1 C`, linha 14) | **CoveringHeavy** | DECLARADO (README:11, paper:156) |
| `CoveringKernel.K7_9_4_le_1351_kernel` | `K3_K7_9_4_Final.lean:14` | `∃ C : Finset (Fin 9 → ZMod 7), C.card = 1351 ∧ CoveringA2.Covers 4 C` | **CoveringHeavy** | DECLARADO (README:11, paper:156) |

Os `#print axioms` de MEDI foram rodados um por um com `lake env lean <arquivo temporário com "import CoveringLean" + "#print axioms <nome>">`;
saídas literais em `campaigns/covering-codes/_fatos/axiomas/<teorema>.txt`. Todas as 9 saem:
`'<nome>' depends on axioms: [propext, Classical.choice, Quot.sound]`.

**Os dois teoremas pesados não foram reproduzidos aqui.** `#print axioms` exige o `.olean` do módulo; os de
`CoveringHeavy` (133 módulos: 38 `G610_Chunk_*` + 95 `K3_K7_9_4_P*`, contados com `ls | grep -c`) levam ~12,4 h de CPU
(README:9, paper:155) e não foram compilados. Medi, no lugar, os lemas do alvo padrão de que eles dependem
(`axiomas/_lemas_do_alvo_padrao.txt`): `CoveringA2.sphere_covering`, `sphere_covering_V`, `CoveringA6.excess_bound`,
`even_inter`, `code12_card`, `code12_covers`, `H2_counterexample_uncond`, `CoveringKernel.cert_of_go`, `covers_of_go`,
`SC.chkN_sound`, `SC.K_2_6_1_eq12_of`: todos `[propext, Classical.choice, Quot.sound]`. Atenção: `SC.K_2_6_1_eq12_of`
tem a hipótese `(h : Ref 6 (root 6 10))`; o fato de a hipótese ser descarregada pelos 38 pedaços é o que NÃO medi.

## 2. Dependências entre teoremas/lemas (imports, `grep "^import"`)

- Todos os arquivos do alvo padrão: `import Mathlib` + o anterior da cadeia. `CoveringLean.lean` importa 17 módulos (A1–A4, A5, A6, A6b, A6c, A6e, Chain, SearchCore, SearchSound, SearchBridgeA2, C1_CoverCheck, K2_Core, K2_Loop, K3_Bridge).
- `Chain` ← `A1_Weight` (`ball_zero_card`, `weight_genfun`), `A2_Sphere` (`sphere_covering_V`), `A3_Numeric` (`lb_*`) (`Chain.lean:2-4`, uso `Chain.lean:24-55`). As 8 `SPH_*_lb` são `lb_* _ (sphere_covering_formula hC)`.
- `K_2_6_1_ge_11` ← `no_cover_2_6_1_le10_uncond` ← `excess_bound` + `vol_2_6_1` + `even_inter` (`A6e_Excess.lean:129-146`); `A6e` importa `A6c_Search` ← `A6b_Hamming` ← `A6_Finite`.
- `K_2_6_1_eq12` (`SearchK6ge12`) ← `G610_Top` (+38 `G610_Chunk_i`) e `SearchBridgeA2`; `SC.K_2_6_1_eq12_of` (`SearchSound.lean:472`) ← `chkN_sound` (`:377`) ← `SearchCore`. O ramo "≤12" usa `code12` (`A6c_Search.lean:177-181`).
- `K7_9_4_le_1351_kernel` ← `K3_K7_9_4` (2401 folhas em 95 `K3_K7_9_4_P*`) + `K3_Bridge` (`cert_of_go`, `covers_of_go`, `K3_Bridge.lean:37,52`) ← `K2_Core` (`go`) ← `K2_Loop` (`go_split` `:45`, `go_sound` `:95`); dado em `C1_Data_K7_9_4.lean`.
- `A5b_Stress` (importa `A5_Frontier`) e `A6d_SearchHeavy` (importa `A6c_Search`) não estão em `CoveringLean.lean` nem em `CoveringHeavy`.

## 3. Axiomas, sorry, native_decide: o que o repositório declara

- LI: `README.md:11` "Nenhum `sorry`, nenhum `native_decide`, e todo `#print axioms` mostra no máximo `propext, Classical.choice, Quot.sound`"; `paper/main.tex:156` (só para os 3 teoremas do paper); `nota.md:28` (versão antiga, 8 SPH).
- LI: `#print axioms` existem nos `.lean` de A1, A2, A6_Finite, A6b, A6c, A6e, Chain, SearchSound, SearchBridgeA2, SearchK6ge12 (`:23-25`), K3_Bridge (`:70`), K3_K7_9_4_Final (`:20`).
- MEDI: o `lake build` imprimiu todos os `#print axioms` do alvo padrão (log completo guardado em `/tmp`, não no repo) e `grep -c sorry` do log = 0; `grep "declaration uses"` = nada.
- MEDI: `grep -rn "sorry\|native_decide\|^axiom" CoveringLean/*.lean`, fora A6d/A5b, só acha comentários/docstrings (A5_Frontier:28, A6_Finite:7, K2_Core:6, K3_Bridge:12).
- O CI (`.github/workflows/verify-codes.yml`) NÃO roda `#print axioms` nem escaneia `sorry`: o job `lean` só faz `lake build` do alvo padrão (`lean-action`, `build: true`). Declarar "nenhum sorry" depende, portanto, de leitura do log do build (que avisa `declaration uses 'sorry'`), não de um gate.

## 4. Toolchain Lean (MEDI)

- `lean-toolchain` = `leanprover/lean4:v4.34.1`; `lake-manifest.json`: mathlib rev `d13f23b723b8a846827a245b89c10fc7d3f11612` (inputRev `v4.34.1`), `lakefile.toml` `rev = "v4.34.1"`.
- elan: `curl --cacert /root/.ccr/ca-bundle.crt https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh` + `sh elan-init.sh -y --default-toolchain none` → `elan 4.2.4`; `elan toolchain install leanprover/lean4:v4.34.1` → "Lean (version 4.34.1, x86_64-unknown-linux-gnu, commit 5045d005…)". TLS verificado, nada desligado.
- `lake exe cache get`: 8908 arquivos baixados e descompactados, rc 0 (~2 min).
- `lake build` (alvo padrão): **"Build completed successfully (8942 jobs)"**, rc 0, **221 s** de relógio neste container de 4 vCPU (README declara 32 s numa e2-highmem-8; os `.olean` de `CoveringLean` não estavam em cache aqui, então compilei os ~40 módulos; a diferença não contradiz o README, mas o "32 s" não é reproduzível a frio). O número de jobs (8942) bate com o README (`README.md:8`).
- Espaço: `.lake/` ficou com 7,8 GB (está no `.gitignore`).
- `A5b_Stress.lean`: `timeout 110 lake env lean` terminou com rc 137 (morto por SIGKILL; não investiguei se foi OOM). `A6d_SearchHeavy.lean`: NÃO rodei (README:71 diz que estoura memória; o risco era derrubar a sessão). Os dois seguem como "não compilam" = DECLARADO, com evidência parcial só para A5b.

## 5. Códigos, witnesses e sha256

Comando: `python3` sobre `data/codes/*.txt` (calculei o sha256 canônico = sha256 das palavras ordenadas por byte, unidas por LF, com LF final) e comparei com `canonical_sha256` de `data/structured/*.json` (MEDI):

| arquivo | M | sha256 canônico (12 primeiros) | = JSON declarado | arquivo já está na forma canônica |
|---|---|---|---|---|
| `q4_n10_R4_M192` | 192 | `907b0f19b29b` | sim | não |
| `q5_n10_R4_M625` | 625 | `9e6866710516` | sim | não |
| `q5_n7_R2_M500` | 500 | `5bebf8d23b34` | sim | não |
| `q5_n9_R3_M1250` | 1250 | `ee6235466bb1` | sim | não |
| `q5_n9_R4_M250` | 250 | `b818a971c864` | sim | não |
| `q5_n9_R5_M50` | 50 | `6125e06ca894` | sim | não |
| `q7_n8_R3_M1887` | 1887 | `98531afbd8af` | sim | sim |
| `q7_n8_R3_M1893` | 1893 | `7c276cf1fffe` | sim | não |
| `q7_n9_R4_M1285` | 1285 | `aa388cc9642b` | sim | não |
| `q7_n9_R4_M1351` | 1351 | `54dbdade1337` | sim | não |

(Os sha256 do arquivo em bytes, que é o que os registros da campanha usam, estão em `campaigns/covering-codes/witnesses/`.)

- MEDI (elo Lean ↔ witness): extraí a lista de 1351 inteiros de `CoveringLean/C1_Data_K7_9_4.lean` (`def K7_9_4`), decodifiquei em base 7 little-endian e conferi: estritamente crescente, todos < 7^9, e o sha256 canônico é `54dbdade1337432303847d2fd0d1c13b506de08ba518e1694c5fb37ed0e81162`, **idêntico** ao de `data/codes/q7_n9_R4_M1351.txt`. Ou seja, o teorema pesado fala do mesmo código que os verificadores conferem.
- ACHADO: o cabeçalho de `C1_Data_K7_9_4.lean` diz "GENERATED by scripts/gen_lean_cover.py ... (tests/test_lean_cover.py regenerates and diffs)" e cita `data/certificates/K7_9_4.json`. **Nenhum dos três existe neste repositório** (`ls` → "No such file"). O gerador do arquivo Lean não está versionado; o elo é só a conferência acima.
- ACHADO: `data/codes/` tem **10** códigos, não os "7 + 1351" do README. Além dos sete da tabela do paper (`M192, M625, M500, M1250, M250, M50, M1893`) e do `M1351`, há `q7_n9_R4_M1285` (melhor que o 1351 para a mesma célula) e `q7_n8_R3_M1887` (melhor que o 1893). Eles estão documentados em `docs/code-format.md:84-85` mas **não** em `README.md`, `nota.md`, `paper/main.tex` (grep de "1285|1887" fora de `data/`, `scripts/`, `tests/`, `docs/`: nada). O paper afirma `K_7(9,4) ≤ 1351` e `K_7(8,3) ≤ 1893` enquanto o próprio repositório tem códigos verificados menores.
- Proveniência (`data/structured/*.json`, campo `provenance`): `1351` → `lincov (Mapika/coldcase)` commit `56a8cce`, "remendo de 322 palavras sem registro", `repo_commit 562fa42`, data 2026-10-01; `1285` → `scripts/search/gen.py` com `data/search/p1285.json`, comando registrado, data 2026-10-02, origem "VM lean-build2 (~/h/s2/b)"; `1887` → "maestro (VM lean-build2)", data 2026-10-02; os outros 7: gerador, comando, seed e data = `null`, "busca anterior à v0.3; o gerador não foi registrado" (`scripts/codes/build_structured.py:23-31`).
- Estrutura (`docs/code-format.md:80-95`, conferida por `tests/test_code_format.py` e `build_structured.py --check`): 1351 = 3 cosets de `[9,3]_7` + 46 cosets de uma reta; 1285 = 3 cosets de `[9,3]_7` + 36 retas + 4 palavras; 1887/1893 = 5 cosets de `[8,3]_7` + 172/178 palavras; 625 é o próprio `[10,4]_5`; 1250, 500, 250, 50 são uniões de cosets; 192 usa `group: xor`.

## 6. Geradores, buscas

- `scripts/search/gen.py` (21 linhas) + `data/search/p1285.json`: regenera `q7_n9_R4_M1285.txt` byte a byte (MEDI: `tests/test_code_format.py::test_gen_py_regenerates_1285_byte_for_byte` passou; o sha256 do arquivo é `89cbd6b2…`, igual ao registrado em `build_structured.py:53`).
- **Gerador do 1351**: `lincov` do Marosi (`Mapika/coldcase`, commit `56a8cce`) está declarado em `README.md:28-29`, `paper/main.tex:73-74`, `data/structured/q7_n9_R4_M1351.json`. **Não está neste repositório e eu não o executei** (sem acesso/sem registro de comando); o remendo guloso de 322 palavras "não ficou registrado" (README:30-31). Reprodução do 1351 = não é possível; só a verificação do código final.
- Busca de `K_2(6,1)`: `scripts/k261/sc_ref.py` é um espelho Python do `SearchCore.chkN` (`INTERFACE.md`: "o Python tem de espelhar bit a bit"). MEDI: `python3 scripts/k261/sc_ref.py 6 10` → `{"ok": true, "nodes": 436727}` em 0,64 s (nenhuma cobertura com 11 palavras contendo a 63; é o argumento WLOG do README); `... 6 10 2` → 46 nós, **38** estados na fronteira (bate com os 38 pedaços `G610_Chunk_*`); controle positivo `... 6 11` → `{"ok": false, "nodes": 46542}` (acha cobertura com 12). Este espelho **compartilha a lógica** com o `chkN` do Lean: não é verificação independente do teorema, só confere que o algoritmo faz o que o Lean diz.
- Geradores de pedaços Lean: `scripts/k261/gen_demo.py` (para `G610_*`), `scripts/k794/gen.py`, `sim.c` (medidor de passos), `build1.sh/pool.sh/finish.sh` (agendador da VM, com caminhos dela: README:79-80).
- `scripts/codes/{codefmt,expand,structure,build_structured}.py`: formato `covering-code/v1` (`docs/code-format.md`).

## 7. Verificadores: quais são, de fato

O README (`:36-37`) e o paper (`main.tex:129`) dizem "três verificadores independentes fora do Lean". **No repositório identifico menos:**

1. `tools/verify/verify.c` (C99, 260 linhas, `sha256 48c3f872…89cf98`): marca bolas de raio R num bitset, conta descobertos, confere dígitos/comprimento/duplicata/M, imprime o sha256 canônico. Roda sobre os 10 códigos (`check_all.sh`). É o único verificador de cobertura completo versionado.
2. `scripts/codes/expand.py` + `codefmt.py` (Python): **não verifica cobertura**; expande o JSON estruturado e confere o `canonical_sha256`. `check_all.sh` encadeia `expand.py | verify` (então a cobertura do JSON expandido ainda é conferida pelo `verify.c`, não por lógica independente). Compartilha o `verify.c` no passo de cobertura.
3. `tests/test_verify.py::test_uncovered_count_matches_an_independent_python_check`: força bruta em Python (distância ponto a ponto), **só no `q5_n7_R2_M500` com a primeira palavra removida**, para comparar a contagem de descobertos com a do C. É um controle negativo de um código perturbado, não uma verificação positiva dos 10 códigos.
4. O Lean (`cert_of_go`, só para o 1351, pesado).

Resposta honesta: **2 verificações independentes de cobertura em linguagens distintas existem só para o 1351 (C + kernel Lean, este último pesado e não reproduzido aqui); para os outros 9 códigos há exatamente 1 (o `verify.c`)**; o "três" do README/paper não é identificável nos artefatos. Para a campanha eu **escrevi um segundo verificador**, `tools/campaign/verify_cover_dilation.py` (numpy; método diferente: dilatação do indicador do código no grid R vezes por "mudar uma coordenada", sem enumerar bolas nem tabela de deslocamentos), com `tests/test_campaign_verifier.py` (3 testes: concorda com o C em sha256 e em contagem de descobertos num negativo; entrada inválida → saída 2). Ele é independente em implementação e algoritmo; **não** é independente em autoria (mesmo agente, mesma especificação do formato). Isso fica registrado no verificador.

MEDI com os dois (todos os 10 códigos, ambos `uncovered=0`, mesmo sha256 canônico; tempos: C 1,1 s no 1351 por `docs/code-format.md:129` (DECLARADO) / numpy 1,8-2,0 s para 40 353 607 pontos (MEDI)). Negativo (q5_n9_R5_M50 sem a primeira palavra): ambos `uncovered=621`.

## 8. Testes e CI

- MEDI `bash tools/verify/check_all.sh`: rc 0, "check_all: 10 códigos, todos cobrem (0 pontos descobertos)", e para cada um "expand -> mesmo sha256 canônico".
- MEDI `python3 -m unittest discover -s tests -v`: **19 testes, OK, 22,2 s** (antes de eu acrescentar `tests/test_campaign_verifier.py`, +3 testes, que também passam: `python3 -m unittest tests.test_campaign_verifier` → "Ran 3 tests ... OK"). `tests/test_code_format.py` (12) + `tests/test_verify.py` (7).
- LI `.github/workflows/verify-codes.yml`: job `verify` (compila com `-Werror`, `check_all.sh`, `unittest`) e job `lean` (`lean-action` v1.6.0, `use-mathlib-cache: true`, `build: true`, alvo padrão; 90 min). `runs-on: ubuntu-latest` (**hospedado**: o `AGENTS.md` do monorepo da Fábrica proíbe runner hospedado, mas este é outro repo, público). Segundo `docs/code-format.md:141-142`, o job `lean` não tinha sido rodado no GitHub (nem havia Lean no container que escreveu o doc); eu rodei o equivalente local (`lake exe cache get` + `lake build` do alvo padrão: passou), mas não o workflow em si.
- O CI não cobre: `CoveringHeavy`, `#print axioms`, `sc_ref.py`, regeneração do 1351.

## 9. Literatura registrada (como está escrito; NÃO reconferi nas fontes)

- Marosi, "New upper and lower bounds on covering codes K_q(n,R) for alphabets of size 5≤q≤21", arXiv:2608.19872 **v3, 2026-09-02**: `K_7(9,4) ≤ 1475` (`README.md:27-28`; `paper/main.tex:80` diz "version 3, September 2026"; bib `:176`). Repositório `Mapika/coldcase`, commit `56a8cce` (gerador `lincov`).
- Kéri 2011, tabelas (`https://old.sztaki.hu/~keri/codes/`): `K_7(9,4) ≤ 1843` (README:28, paper:80) e a coluna "previous" da Tabela do paper (`main.tex:139-145`): K5(7,2) 525, K4(10,4) 208, K5(9,3) 1275, K5(10,4) 875, K5(9,5) 55, K5(9,4) 255, K7(8,3) 2337.
- Florath, arXiv:2606.09600 (`florath/covering-codes-lean`): `10 ≤ K_2(6,1) ≤ 12` no banco Lean dele (README:25-26; paper:121); formalizou a cota de esfera em junho/2026 (README:32).
- Stanton & Kalbfleisch 1968, *Aequationes Math.* 1, 94-103: `K_2(6,1) = 12` "clássico" (README:25; paper bib `:180`). Gijswijt & Polak, arXiv:2504.01932 (2025): lower bounds; `K_7(9,4) ≥ 264` é "a melhor cota inferior que conhecemos" (`main.tex:81`), sem fonte nominal da cota 264 no texto.
- "conferido em 2026-10-01 (comparação feita por nós, sem revisão externa)" (README:23). Para `q=4` a busca "foi mais fraca" e `K_5(10,4) ≤ 625` é linear `[10,4]_5`: "falta conferir as tabelas de Davydov–Marcugini–Pambianco" (README:37-38; paper:129-130).
- Não achei no repositório as cotas inferiores "melhores conhecidas" das 7 células (só a de `K_7(9,4)`: 264).
- `nota.md` está **desatualizado** (versão 0.2 do paper): diz que `K_7(9,4) ≤ 1351` e `K_2(6,1) ≥ 11` não são teoremas e que A6d "não compila" como pendência; contradiz `README.md`. Não usei `nota.md` como fonte de estado; usei README/paper v0.3.

## 10. O que NÃO está provado (README:67-74)

1. Os outros 7 códigos de `data/codes/` não têm teorema Lean (só verificação computacional). (+ os dois extras 1285 e 1887, que também não têm.)
2. Novidade na literatura é afirmação do autor, não do Lean.
3. `A6d_SearchHeavy.lean` e `A5b_Stress.lean` fora da biblioteca e não compilam.
4. Que os enunciados formais dizem o pretendido é revisão humana (`K_2_6_1_ge_11`, `K_2_6_1_eq12`, `K7_9_4_le_1351_kernel`, `ball`, `Covers`, `IsK`): **sem `statement_review` registrado**, a guarda `FORMALLY_VERIFIED` da campanha nega.
5. (MEDI/LI) A cota de esfera não é resultado (`main.tex:124-127`): as 8 instâncias estão abaixo das melhores cotas inferiores da literatura; `K_7(9,4) ≥ 221` contra 264 conhecida.
6. (LI) Para `K_7(9,4)` a faixa é `221 ≤ K ≤ 1351` no que o Lean prova (e `≤ 1285` no que há verificado em `data/`): longe de resolvida.

## 11. Fase 2: migração (MEDI, `python3 tools/campaign/migrate_covering.py --factory-src <src>`)

- Campanha `covering-codes` criada por `tools/campaign/migrate_covering.py` (idempotente; preserva `_fatos/`). `data_root` = `"../.."` (relativo à pasta da campanha, que é como `verify.raiz_dados` interpreta; `"."` apontaria para a própria pasta da campanha).
- Estados finais (guardas reais de `claims.mudar_estado`): 15 PROVED (8 SPH, `k2-6-1-lb-11`, `k2-6-1-ub-12`, 5 lemas, `sphere-covering-general`), 10 INDEPENDENTLY_REPRODUCED (os 10 códigos de `data/codes`, incluindo 1351, 1285, 1887), 2 EXHAUSTIVE_BOUNDED (`k2-6-1-lb-12`, `k2-6-1-eq-12`), 1 REFUTED (H2). Nenhum FORMALLY_VERIFIED (falta `statement_review`).
- Corridas: 22 + 2 = verify-c e verify-py-dilation PASS em 11 witnesses (10 de `data/codes` + `code12` gerado do Lean). `reproduce` (com `--lean`): PASS 10, FAIL 1; o FAIL é o passo de axiomas dos 2 registros pesados (módulo `CoveringHeavy` não compilado: `lake env lean` rc=1), exatamente a limitação declarada.
- Cobertura do universo (9 células): 1 resolvida (K_2(6,1)), 8 residuais.
- `lint`: 14 `same_code_verifier` (falso positivo: claims PROVED por Lean não têm corrida de verificador e a regra os trata como "reproduzidos"), 3 `unexpected_axiom` (os 2 registros pesados sem axiomas medidos: correto), 2 `shared_hidden_assumption` (literatura Kéri/Marosi não reproduzida: correto).
- Achado da infra: `model._g_proved` só exige que EXISTA um registro formal; só `FORMALLY_VERIFIED` chama `validar_registro_formal`. O script exige validade antes de PROVED (`promover`), então o estado final não depende dessa folga.

## 12. Autópsia do REFUTED (2026-10-03, Agente P1; detalhes em `_autopsia/AUTOPSIA_REFUTED.md`)

- MEDI: `A6_Finite.lean` refuta H1, H3 e H5 (`H1_counterexample`, `H3_counterexample`, `H5_counterexample`) e a campanha só tinha o H2. Registrados em `tools/campaign/migrate_covering.py` como claims REFUTED (`h1-alpha-nonincreasing`, `h3-alpha-le-2`, `h5-ceil-bound-needs-perfect`) com contraexemplo e registro formal medido (`#print axioms`: `propext, Classical.choice, Quot.sound`). Estados finais: 15 PROVED, 10 INDEPENDENTLY_REPRODUCED, 2 EXHAUSTIVE_BOUNDED, **4 REFUTED** (31 claims).
- LIMITAÇÃO: o texto original de H1, H3 e H5 não está em nenhum arquivo versionado além do nome e de um comentário de uma linha em `A6_Finite.lean`; os enunciados dos claims são leitura desses comentários, e o que o Lean refuta literalmente está em `refuting_lean_statement` de cada claim.
- MEDI: `tests/test_refuted_hypotheses.py` (6 testes) falha se a biblioteca refutar `H<n>` sem claim REFUTED, se README/nota/docs/paper afirmarem uma hipótese refutada sem dizê-lo, ou se claim ≥ EMPIRICAL depender (mesmo transitivamente) de REFUTED.
- A cadeia anterior à regeneração (356 eventos, âncora seq 320) está copiada em `_autopsia/audit-pre-regeneracao/` com sha256.
