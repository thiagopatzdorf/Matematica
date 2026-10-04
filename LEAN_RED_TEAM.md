# Red team adversarial: `Syn.K7_9_4_le_1137_syn` (K_7(9,4) ≤ 1137)

- Repositório: `thiagopatzdorf/Matematica`, branch `main`, commit `fcf0984`, num clone local separado (só leitura, nada alterado, nada commitado).
- Toolchain: Lean 4.34.1 (commit 5045d005), Mathlib `d13f23b7` (rev v4.34.1, do `lake-manifest.json`).
- Data: 2026-10-02. Todos os scripts e builds rodaram numa cópia no scratchpad (`.../scratchpad/core`, `regen`, `wrong`, `m1`, `m3`).

## Veredito

**Nenhum ataque invalidou a alegação.** O enunciado é o certo: `∃ C : Finset (Fin 9 → ZMod 7), C.card = 1137 ∧ CoveringA2.Covers 4 C`, com `Covers R C := ∀ x, ∃ c ∈ C, hammingDist x c ≤ R` (Mathlib `hammingDist`). Ele compila do zero na minha cópia e só depende de `[propext, Classical.choice, Quot.sound]`. Os quatro enunciados adulterados (raio 3, card 1136, n=8, q=6) e os três certificados adulterados são rejeitados. Uma checagem independente por força bruta em Python, sobre os 7^9 = 40.353.607 pontos, também confirma a cobertura.

Os achados abaixo são de **processo e de base de confiança**, não furos na prova.

## Tabela ataque → resultado → evidência

| # | Ataque | Resultado | Evidência |
|---|---|---|---|
| 1 | Procurar `sorry`/`admit`/`axiom`/`unsafe`/`implemented_by`/`extern`/`@[csimp]`/`native_decide`/`ofReduceBool`/`trustCompiler`/`opaque`/`macro`/`elab`/`syntax`/`#eval`/`run_cmd`/`initialize`/`IO`/`include_str`/`set_option debug.*` no fecho de imports do teorema (19 arquivos: A2_Sphere, K2_Loop, K2_Core, C1_CoverCheck, K3_Bridge, SynCheck, SynBridge, SynData_K1137, SynLeaf_K1137_0..9, Syn_K1137) | FALHOU EM INVALIDAR | Nenhuma ocorrência em código. Só aparecem em comentários ("sem `native_decide`") e em `#print axioms`. O único `set_option` é `maxRecDepth 100000` (Syn_K1137.lean:23), um limite do elaborador que não afrouxa o kernel. O único atributo é `@[simp]` (C1_CoverCheck.lean:47). As `leanOptions` do `lakefile.toml` (linhas 6–10) são inócuas. |
| 2 | Axiomas reais do teorema | FALHOU EM INVALIDAR | Saída do meu build: `'Syn.K7_9_4_le_1137_syn' depends on axioms: [propext, Classical.choice, Quot.sound]`. Não aparece `Lean.ofReduceBool`, ou seja, `decide +kernel` não usa o compilador. |
| 3 | Dado externo lido em tempo de compilação (arquivo, FFI) | FALHOU EM INVALIDAR | Não há `IO`, `include_str` nem elaborador customizado. Todo o dado é literal Lean em `SynData_K1137.lean` (Spec `PK1137` e `LK1137`). |
| 4 | Definição de `Covers`: `<` vs `≤`, raio, alfabeto, dimensão, quantificadores | FALHOU EM INVALIDAR | A2_Sphere.lean:29–30. Saída do `#print CoveringA2.Covers`: `fun {q n} R C => ∀ (x : Fin n → ZMod q), ∃ c ∈ C, hammingDist x c ≤ R`. `#check` do teorema: `∃ C, C.card = 1137 ∧ CoveringA2.Covers 4 C`, com `C : Finset (Fin 9 → ZMod 7)` (Syn_K1137.lean:84–85). O tipo é `ZMod 7`, não `Fin 7`, e mesmo que fosse daria no mesmo. A cardinalidade é igualdade exata (`= 1137`), que é mais forte que `≤`. |
| 5 | Enunciados adulterados contra o mesmo certificado (meu `Adv.lean`) | FALHOU EM INVALIDAR (todos rejeitados) | Raio 3: `rfl : PK1137.R = 3` falha. Card 1136: o kernel rejeita `decide (LK1137.length = 1136)`. `Fin 8`: `PK1137.n = 8` falha e `m < 7^8` dá falso. `ZMod 6`: `PK1137.q = 6` falha. O controle com o enunciado exato passa. |
| 6 | Duplicatas na lista ⇒ card menor que 1137 | FALHOU EM INVALIDAR | `syn_cert` exige `L.all (· < q^n) && strictlyInc L` (checado por `decide +kernel`) e usa `card_codeOf`, provado por injetividade de `word` em `[0, q^n)` (C1_CoverCheck.lean:243–257). Logo `card = L.length = 1137`, sem `≤`. Em Python independente: 1137 inteiros estritamente crescentes, todos < 7^9, e 1137 strings distintas. |
| 7 | Decodificação Nat → dígitos → `Fin 9 → ZMod 7` / ponte vale para todo x? | FALHOU EM INVALIDAR | `syn_cert` (SynBridge.lean:339ss) faz `intro x` (linha 362) para `x : Fin n → ZMod q` arbitrário. Ele monta `a` (dígitos do bloco), `c = a·G`, `y = x − c` e `t` (índice de y no transversal, `t < q^(n−k)`). Cada passo está provado: `D_enc`, `enc_lt`, `hyt`, `chkPiv_sound`. Não há restrição a um subconjunto. A convenção de dígitos `D q w i = w / q^i % q` (SynCheck.lean:21) é a mesma de `word`/`dig` (`word_eq_wdf`, K3_Bridge). |
| 8 | "Síndrome coberta ⇒ ponto coberto" é geral? Soma nas classes laterais | FALHOU EM INVALIDAR | Coberto pelo lema genérico `S_dsum` (soma dígito a dígito mod q é linear em ZMod q). O ramo da testemunha usa `rₛ + (m ⊕ a)·G ∈ L` (via `chkB`, que checa os q^k membros de cada coset) e `hammingDist_sub_right`. O ramo órfão checa os q^k pontos `y_t + a·G` um a um (`chkO`). Tudo é teorema Lean sem hipótese extra: as hipóteses de `syn_cert` são todas descarregadas no Syn_K1137.lean:86–87. |
| 9 | Alinhamento folhas ↔ montagem (offset, tamanho de bloco, 7^6 = 117649, índices de órfãos) | FALHOU EM INVALIDAR | O tipo de `chkT_sound PK1137 _ _ _ _ TK1137_c i` precisa casar com `okT PK1137 (4096*c+i)`. Os órfãos casam por `PK1137.orphs.getD i 0`. Os comprimentos estão fixados por `rfl` (`orphs.length = 6`, `reps.length = 3`). Um offset ou número errado não tipa. O build passou. |
| 10 | O código do teorema é o de `data/codes/q7_n9_R4_M1137.txt` (sha256 df3e8d52…)? | FALHOU EM INVALIDAR | Script independente meu: desempacotei `PN` (26 bits × 1137, resto 0), obtive `unpack == LK1137`, decodifiquei em base 7 little-endian e ordenei as strings. O resultado é byte a byte igual ao arquivo, com sha256 `df3e8d527bc393a9680fe4b2b39e7bde088ab6a02f2f94ee26019a5efc05a102`, igual ao `sha256sum` do arquivo. Ressalva: esse vínculo é externo ao Lean, que prova só sobre `LK1137`. O sha no comentário do .lean não é checado pelo Lean, mas também não é necessário: o teorema vale para `LK1137`, seja qual for o arquivo. |
| 11 | Arquivos gerados sem verificação / reprodutibilidade do gerador | FALHOU EM INVALIDAR | Rodei `gen_syn.py data/structured/q7_n9_R4_M1137.json K1137` numa pasta à parte. Os 12 arquivos `Syn*_K1137*.lean` saíram **byte a byte idênticos** aos do repositório. Além disso, o Lean não confia no gerador: um certificado errado não compila (itens 12–14). |
| 12 | Teste negativo `--wrong` (palavra de remendo removida) | FALHOU EM INVALIDAR (rejeitado) | O gerador acusa 3 órfãos descobertos (t=72989, 85727, 114214). O kernel rejeita os 3 `chkO` (`decide` proved … is false) em `SynLeaf_K1137W_8`. |
| 13 | Negativo mais forte que `--wrong` (M1): mesma remoção, mas com testemunhas *argmin* em vez de zeros, falhando só nos 1–3 pontos realmente descobertos | FALHOU EM INVALIDAR (rejeitado) | Os 3 `chkO` de `SynLeaf_K1137M1_8` são rejeitados. A folha `BK…_0` do mesmo arquivo passa. |
| 14 | Negativo M3: certificado mentiroso que tira o órfão t=20133 da lista e dá testemunha de coset a distância 5 | FALHOU EM INVALIDAR (rejeitado) | `SynLeaf_K1137M3_1`: `(kernel) application type mismatch … chkT PK1137M3 2048 4096 16384`, isto é, o bloco que contém t=20133. |
| 15 | Checagem positiva do kernel nas 39 folhas reais, com Lean puro sem Mathlib | FALHOU EM INVALIDAR | As 10 `SynLeaf_K1137_*.lean` compilaram com `exit 0` (139+145+128+125+133+137+91+26+6+3 s, 2 em paralelo, `nice`). Depois SynBridge e Syn_K1137 compilaram com Mathlib. |
| 16 | Não-vacuidade do verificador | FALHOU EM INVALIDAR | `example : okT PK1137 0 59 = false := by decide +kernel` (Syn_K1137.lean:81) compila. Itens 12–14 acima. |
| 17 | Verdade matemática independente do Lean | FALHOU EM INVALIDAR | Em Python/numpy, marquei as bolas de raio 4 (182.791 pontos cada) das 1137 palavras sobre os 7^9 pontos: **0 descobertos**. Controle negativo: tirando uma palavra, sobram 366 pontos descobertos. |
| 18 | Base de confiança de `decide +kernel` | Observação (não é furo) | As folhas dependem da aceleração GMP de `Nat` no kernel (`Nat.pow/div/mod/shiftRight/beq/ble`). Isso é parte padrão do kernel de Lean 4 e não aparece em `#print axioms`. É a base de confiança usual de qualquer prova `decide` com números grandes. |
| 19 | O CI garante o resultado? | **ACHOU PROBLEMA (processo, baixo)** | `lakefile.toml:4` define `defaultTargets = ["CoveringLean"]`, e `CoveringSyn` (linhas 26–31) fica fora. O job `lean` do `.github/workflows/verify-codes.yml:61–74` roda só `lake build` do alvo padrão. Logo **o CI nunca compila `Syn_K1137`**. A alegação depende de build manual (README.md:11). Um commit que quebre o certificado passaria verde. |
| 20 | Qualidade do `--wrong` do gerador | **ACHOU PROBLEMA (teste, informativo)** | `gen_syn.py:206`: para um órfão que falha, o gerador emite testemunhas `[0]*q**k`. A rejeição fica trivial (a palavra 0 está longe da maioria dos pontos) e não exercita o caso "quase certo". Meu M1 (item 13) fecha essa lacuna e também é rejeitado. |

## Problemas, por gravidade

1. **Crítico / alto:** nenhum.
2. **Médio:** nenhum.
3. **Baixo (processo):** o CI não compila `CoveringSyn`, então `Syn.K7_9_4_le_1137_syn` não é rechecado a cada commit (`lakefile.toml:4,26–31`; `verify-codes.yml:61–74`). Sugestão: um job separado com `lake build CoveringLean.Syn_K1137`, que leva ~3 min em 8 núcleos com o cache do Mathlib.
4. **Informativo:**
   - O `--wrong` emite testemunhas zeradas (`gen_syn.py:206`), um teste negativo fraco. Um negativo com testemunhas argmin também é rejeitado.
   - O vínculo "LK1137 = arquivo com sha df3e8d52…" é externo ao Lean. Conferi de forma independente: bate.
   - A base de confiança inclui a aceleração GMP de `Nat` no kernel, o que é padrão.

## Como reproduzir (resumo)

- Folhas só com o núcleo: `LEAN_PATH=build lean src/CoveringLean/SynLeaf_K1137_i.lean -o build/CoveringLean/SynLeaf_K1137_i.olean`, depois de compilar `SynCheck` e `SynData_K1137`.
- Montagem: `A2_Sphere → K2_Loop → K2_Core → C1_CoverCheck → K3_Bridge → SynBridge → Syn_K1137 → Adv`, com `LEAN_PATH` incluindo os `.lake/build/lib/lean` dos pacotes do Mathlib (cópia por hardlink do cache).
- Scripts Python: `indep.py` (sha, unpack e cobertura por força bruta) e `indep_neg.py` (controle negativo), no scratchpad da sessão.
- `leanchecker` (replay do kernel) **não** foi rodado por mim. O outro agente já estava rodando sobre as mesmas folhas, então matei o meu para não duplicar CPU.

---

# v0.6: red team de `Syn.K7_9_4_le_1134_syn`, `Syn.K5_10_5_le_162_syn`, `Syn.K5_11_4_le_2875_syn` e `Syn.K7_10_4_le_5616_syn`

- Branch `feat/v0.6` (worktree próprio), 2026-10-03. Lean 4.34.1, Mathlib `v4.34.1`.
- Números completos (build, verificadores, sha256, mutações) em `VALIDATION_v0.6.md` e `verification/outputs/v0.6/`.

## Veredito

**Nenhum ataque invalidou as quatro alegações.** As quatro compilam e só dependem de `[propext,
Classical.choice, Quot.sound]`. Os enunciados são os pedidos: n, q, R e M conferidos por `example …
:= teorema`, com o tipo escrito por extenso. Toda mutação de dado foi rejeitada pelo kernel, e cinco
verificadores independentes dão 0 pontos descobertos em todo o espaço. Os achados são de processo.

## Tabela ataque → resultado → evidência

| # | Ataque | Resultado | Evidência |
|---|---|---|---|
| 1 | Construções proibidas nos arquivos dos quatro certificados + `SynCheck`/`SynBridge` | FALHOU EM INVALIDAR | `grep` de `sorry`, `admit`, `native_decide`, `axiom`, `implemented_by`, `extern`, `unsafe`, `ofReduceBool`, `#eval`, `run_cmd`, `include_str`: só um comentário em `SynBridge.lean:22`. `set_option` só `maxRecDepth 100000`. |
| 2 | Axiomas | FALHOU EM INVALIDAR | `#print axioms` dos quatro: `[propext, Classical.choice, Quot.sound]` (`verification/outputs/v0.6/lean_statements.txt`). |
| 3 | Enunciado certo (n, q, R, M) | FALHOU EM INVALIDAR | `example : ∃ C : Finset (Fin 10 → ZMod 7), C.card = 5616 ∧ CoveringA2.Covers 4 C := Syn.K7_10_4_le_5616_syn` e os análogos (9/7/4/1134, 10/5/5/162, 11/5/4/2875) compilam (`Stmt.lean.txt`). |
| 4 | `Covers` é a definição usual | FALHOU EM INVALIDAR | `#print CoveringA2.Covers` = `fun {q n} R C => ∀ (x : Fin n → ZMod q), ∃ c ∈ C, hammingDist x c ≤ R`; `Iff.rfl` com a forma desdobrada compila. |
| 5 | Gerador assume q = 7 / n = 9 | FALHOU EM INVALIDAR | Os certificados q = 5 (n = 10, 11) e q = 7, n = 10 compilam. `tests/test_gen_syn.py` regenera o K162 byte a byte. A ponte `syn_cert` é genérica em `q n R M` (`[NeZero q]`). |
| 6 | Lista do `.lean` = código publicado | FALHOU EM INVALIDAR | `decode_synData.py --tag T`: `unpack(PN) == L`, L estritamente crescente e < q^n, e forma canônica = `.txt` ordenado, com o mesmo sha256 canônico nas quatro células. |
| 7 | M1: trocar 1 palavra por outra que descobre pontos | FALHOU EM INVALIDAR (rejeitada ×4) | O kernel recusa a folha `B…_s` da classe lateral atingida. Pontos descobertos pela troca: 378, 160, 55, 111. |
| 8 | M2: remover 1 palavra | FALHOU EM INVALIDAR (rejeitada ×4, duas formas) | M2a, card: `decide (L.length = M)` dá kernel type mismatch. M2b, enunciado com M−1: folhas `O…`/`B…` recusadas (índices deslocados). Pontos descobertos: 460, 171, 59, 125. |
| 9 | M3: alterar 1 entrada da tabela de cobertura | FALHOU EM INVALIDAR (rejeitada ×4) | A testemunha de t = 0 em `T…_0` trocada pela palavra a distância > R do exemplo de não-vacuidade: `decide` prova que a folha é falsa. |
| 10 | O arranjo de mutação mente? | **ACHOU PROBLEMA (no meu harness, corrigido)** | Na 1ª versão, `lake: command not found` contava como "rejeitada". Na 2ª, o `LEAN_PATH` resolvia `CoveringLean.*` só na pasta à parte. Os dois casos foram pegos e corrigidos: só conta erro do Lean com posição no arquivo, e um controle positivo (folha original renomeada) tem de compilar antes. Os 4 controles compilam. |
| 11 | Certificado do K2875 sem órfãs (`orphs = []`) é vácuo? | FALHOU EM INVALIDAR | Com 0 órfãs, `hO` é `absurd` sobre `orphs.length = 0` (por `rfl`). A cobertura fica toda nas 120 folhas `T`/`B`, e a M3 (testemunha falsa em `T`) é rejeitada. Os 23 × 125 pontos-base são checados por `chkB`. |
| 12 | Verdade fora do Lean | FALHOU EM INVALIDAR | `tools/verify/verify`, `verify_cover.py`, `scripts/search/verify.py`, `scripts/attack/verify_bfs.c`, `verify_bfs/main.rs` (constantes trocadas em cópia) e a força bruta por bolas do `decode_synData.py`: 0 descobertos. Distribuições de distância idênticas nos dois BFS. |
| 13 | CI recompila os certificados? | **ACHOU PROBLEMA (processo, baixo; herdado da v0.5)** | `CoveringSyn` continua fora do alvo padrão e do job `lean`. Os quatro teoremas novos dependem de build manual, que somam ~20 min em 4 núcleos (ver `VALIDATION_v0.6.md`). |
| 14 | `build_structured.py --check` no 1134 | **ACHOU PROBLEMA (dado, corrigido)** | O JSON do 1134 (branch `feat/k794-1134`) não era regenerável: remendo fora de ordem e sem registro. Corrigido sem mudar palavras nem sha. O certificado regenerado é idêntico. |

## Como reproduzir

```bash
export PATH=$HOME/.elan/bin:$PATH
lake build CoveringLean.Syn_K1134 CoveringLean.Syn_K162 CoveringLean.Syn_K2875 CoveringLean.Syn_K5616
verification/lean/run_mutations_syn.sh K162 /tmp/mut/K162 --full      # e K1134, K2875, K5616 (sem --full)
python3 verification/lean/decode_synData.py --tag K5616 --cover
tools/verify/check_all.sh
```
