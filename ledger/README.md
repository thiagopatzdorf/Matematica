# Ledger de células de cobertura

Uma entrada por célula `K_q(n,R)` das tabelas do Kéri (1145 células, `q` de 2 a 21), com a melhor
cota inferior e superior **publicadas**, a fonte de cada uma e o **nosso** estado. É a memória que o
loop de recordes (`scripts/loop/record_loop.py`) lê e escreve, e a fonte da página pública
(`scripts/publish/genesis_page.py`).

| arquivo | o que é | quem escreve |
|---|---|---|
| `cells.json` | o ledger, uma célula por linha | `build.py` (não edite à mão) |
| `ours.json` | o nosso estado por célula: `ours_computational` e `ours_lean` | à mão ou `record_loop.py` |
| `provenance.json` | proveniência de cada código nosso (regra abaixo) | à mão ou `record_loop.py` |
| `sources.json` | fontes publicadas, fixadas por commit | à mão, ao reler a literatura |
| `runs.jsonl` | toda tentativa do loop, inclusive as que falharam | `record_loop.py` |
| `build.py` | gera `cells.json` | |
| `cobertura.py` | gera `COBERTURA.md`: quantas cotas em cada estado de certificação, por q | |
| `COBERTURA.md` | o relatório de cobertura | `cobertura.py` (não edite à mão) |
| `targets.py` | ranqueia células-alvo para busca | |

## Fontes (lidas em 2026-10-02)

* **Kéri 2011**: `cov/bounds.json` do repositório público do Marosi
  ([Mapika/coldcase](https://github.com/Mapika/coldcase), commit `56a8cce`), transcrição das tabelas do
  Kéri congeladas em 2011. Traz também, no campo `lb_updated`, as cotas inferiores de
  **Gijswijt–Polak** ([arXiv:2504.01932](https://arxiv.org/abs/2504.01932), só `q ≤ 5`).
* **Marosi 2026** ([arXiv:2608.19872](https://arxiv.org/abs/2608.19872)): as 26 cotas superiores de
  `cov/results/final_records.json` e as 58 inferiores SDP de `cov/lb/results/lb_master.json` com
  `improves_best_known`. O `bounds.json` sozinho **não** traz as melhorias do Marosi; por isso o build
  lê os três arquivos.
* **Florath** ([arXiv:2606.09600](https://arxiv.org/abs/2606.09600),
  [florath/covering-codes-lean](https://github.com/florath/covering-codes-lean), commit `bbed9a6`):
  a tabela gerada do banco Lean (`florath_lean`, cotas provadas em Lean) e a compilação de literatura
  pós-Kéri (`literatura_pos_keri`, que hoje só acrescenta 4 inferiores binárias de Wu–Chen 2024).
* **Quem o Marosi atacou**: `attack_records*.json`, `attack_sieges.json`, `sweep_targets.json`,
  `results/cov_sweep_state.json` (superiores) e `lb_master.json` (inferiores).

Desempate: com valores iguais, o crédito vai para a fonte mais antiga (Kéri, depois GP, Marosi,
Florath); a compilação pós-Kéri só leva o crédito quando é estritamente melhor.

**Limite declarado**: literatura pós-2011 fora dessas fontes (em especial binária e ternária) não foi
auditada. Uma célula "que ninguém atacou desde 2011" quer dizer: ninguém nessas fontes.

## Esquema de uma célula

```json
{"id": "K7(9,4)", "q": 7, "n": 9, "R": 4, "space": 40353607, "sphere_bound": 221,
 "published": {"lb": {"value": 264, "source": "keri_2011", "ref": "..."},
               "ub": {"value": 1475, "source": "marosi_2026", "ref": "..."},
               "exact": false,
               "sources": {"keri_2011": {...}, "gijswijt_polak_2025": null, "marosi_2026": {...},
                           "florath_lean": {...}, "literatura_pos_keri": {...}}},
 "marosi_attacked": {"ub": true, "lb": false, "evidence": ["record:final_records.json", "..."]},
 "ub_improved_since_2011": true,
 "ours_computational": {"M": 1285, "file": "data/codes/q7_n9_R4_M1285.txt", "sha256": "...", "provenance": "P-1285"},
 "ours_lean": {"M": 1351, "declaration": "CoveringKernel.K7_9_4_le_1351_kernel", "tag": "v0.3.0", "...": "..."},
 "best": {"ub": 1285, "holder": "ours_computational", "beats_published": true},
 "status": "ours_lean"}
```

`status` é o nosso estado mais forte: `ours_lean` > `ours_computational` > `published`. `best` é a
melhor cota superior conhecida contando a nossa. `ours_lean.tag` é a tag git em que o teorema saiu;
`tag: null` com `tag_pendente` quer dizer provado mas ainda não etiquetado.

## Certificação: estado e proveniência de cada cota

A machine-checked ledger of covering-code upper bounds, with formally certified exact entries.
(Não diga que a tabela inteira foi verificada formalmente: as cotas inferiores são, quase todas,
herdadas da literatura.)

Cada célula ganha `certification = {"ub": {...}, "lb": {...}, "exact": bool}`, calculado pelo
`build.py` (nunca à mão). Cada lado tem `value`, `state` e `provenance`. A escada é cumulativa:

| estado | o que exige |
|---|---|
| `CLAIMED` | a cota está numa fonte publicada de versão congelada; nada foi conferido aqui |
| `WITNESS_CHECKED` | o certificado foi conferido por um verificador exato fora do Lean: código explícito no `tools/verify`, ou refutação LRAT de inexistência |
| `FORMALIZED` | há teorema do Lean, checado pelo kernel, com exatamente esta cota e sem hipótese pendente |
| `INDEPENDENTLY_REPRODUCED` | formalizada **e** conferida por um segundo verificador independente, executado (hoje: o código de `data/codes/` passa no `tools/verify` em C, além do kernel) |

`provenance` traz sempre os seis campos `fonte` (fonte original: chave do Kéri, arquivo do Marosi,
regra do Florath, ou `nosso`), `versao` (chave de `meta.versoes`, que guarda repo, commit, arquivo,
data de leitura e sha256 da tabela; ou tag/data, para resultado nosso), `witness`, `sha256`,
`verificador_independente` e `lean` (declaração e tag). Campo vazio leva `lacuna`. Uma prova Lean de
terceiros com o mesmo valor (Florath) vai em `formalizacao_externa`, mas **não sobe o estado**: não
foi reconstruída aqui.

Cota inferior nossa entra em `ours.json` como `"lb": {value, estado, witness, sha256,
verificador_independente, lean, ...}`. O build aborta se o registro chamar de `FORMALIZED` um
teorema com `lean.condicional`, se a inferior ficar abaixo da publicada ou acima da superior.

**K_7(4,2) = 19**: superior `FORMALIZED` (`K742.K_7_4_2_le_19`, código da partição no Lean, v0.7);
inferior `FORMALIZED` desde a v0.8 (`K742.K_7_4_2_eq_19`, incondicional, lib `CoveringK742Sat`; ver
`docs/exatos/LEAN_K742.md`). Fica em `FORMALIZED`, não em `INDEPENDENTLY_REPRODUCED`: a escada hoje
só reconhece como segundo verificador o `tools/verify` em C (ou o avaliador Python) sobre um código
explícito; as 70 refutações LRAT conferidas por `lrat-check` e `lrat.py` ficam registradas em
`verificador_independente`, e a codificação independente não tem LRAT (segunda opinião, não
certificado). Subir de estado por esse caminho é decisão do mantenedor.

## Certificação em lote das cotas superiores (`tools/certificar/`)

Nenhuma célula ganha prova artesanal: `tools/certificar/gerar.py` escolhe, para cada célula, o
certificado mais barato que atinge `best.ub` e gera o Lean.

* **Base sem witness**: espaço inteiro, raio ≥ n (uma palavra), palavras constantes (pombal).
* **Witness explícito pequeno** (`tools/certificar/witnesses/`, conferido pelo kernel com
  `UB.of_go`): achado por recozimento (`buscar.py`), importado do banco do Florath
  (`importar_florath.py`, BSD-3, aviso em `witnesses/LICENSE-florath`) ou da construção por
  partição (`tools/exatos/particao_q42.py --gravar DIR` e `buscar.py --importar DIR`).
* **Regra** a partir de outras células (`CoveringLean/Regras.lean`): soma direta, alongamento
  livre, coordenada muda, punção, monotonia do raio, projeção de alfabeto.

Saídas geradas: `CoveringLean/Ledger/W*.lean` (witnesses), `CoveringLean/Ledger/Cotas.lean` (um
`CoveringLedger.K<q>_<n>_<R>_le_<M> : K q n R ≤ M` por célula) e `ledger/formal_ub.json`, que o
`build.py` lê: cota com teorema gerado sobe para `FORMALIZED`; se vier de witness explícito, o
avaliador Python de `buscar.py` reconfere o código em todo pytest e a cota fica
`INDEPENDENTLY_REPRODUCED`.

```bash
python3 tools/certificar/buscar.py --limite 2000000 --segundos 10   # witnesses novos (opcional)
python3 tools/certificar/gerar.py && lake build CoveringLedger
python3 ledger/build.py && python3 ledger/cobertura.py
```

## Nosso estado em 2026-10-03

| célula | publicado (superior) | Lean | computacional |
|---|---|---|---|
| K7(9,4) | 1475 (Marosi) | ≤ 1134, `Syn.K7_9_4_le_1134_syn`, v0.6.0 (pendente) | |
| K7(10,4) | 6517 (Kéri) | ≤ 5616, `Syn.K7_10_4_le_5616_syn`, v0.6.0 (pendente) | |
| K5(11,4) | 3125 (Kéri) | ≤ 2875, `Syn.K5_11_4_le_2875_syn`, v0.6.0 (pendente) | |
| K5(10,5) | 175 (Kéri) | ≤ 162, `Syn.K5_10_5_le_162_syn`, v0.6.0 (pendente) | |
| K7(8,3) | 2337 (Kéri) | ≤ 1893, `CoveringKernel.K7_8_3_le_1893_kernel` | ≤ 1887 |
| K5(10,4) | 875 (Kéri) | ≤ 625, `CoveringKernel.K5_10_4_le_625_kernel` | |
| K5(9,3) | 1275 (Kéri) | ≤ 1250, `CoveringKernel.K5_9_3_le_1250_kernel` | |
| K5(7,2) | 525 (Kéri) | ≤ 500, `CoveringKernel.K5_7_2_le_500_kernel` | |
| K5(9,4) | 255 (Kéri) | ≤ 250, `CoveringKernel.K5_9_4_le_250_kernel` | |
| K4(10,4) | 208 (Kéri) | ≤ 192, `CoveringKernel.K4_10_4_le_192_kernel` | |
| K5(9,5) | 55 (Kéri) | ≤ 50, `CoveringKernel.K5_9_5_le_50_kernel` | |
| K2(6,1) | 12 (Kéri, exata) | = 12, `SC.K_2_6_1_eq12`, v0.3.0 | |
| K7(4,2) | 19 (Kéri, 17–19) | ≤ 19, `K742.K_7_4_2_le_19`, v0.7.0; = 19, `K742.K_7_4_2_eq_19`, v0.8.0 | ≥ 19 por LRAT |

Os sete teoremas sem tag entram na v0.4.0. Os 10 arquivos de `data/codes/` passam no verificador
padrão (`scripts/loop/verify_cover.py`; K7(9,4) leva ~15 s, o resto < 3 s).

## Regra de proveniência

**Todo código novo que entra em `data/codes/` leva um registro em `provenance.json` com os seis
campos `{gerador, commit, seed, comando, data, agente}`.** Campo desconhecido fica `null` com uma
`lacuna` explicando por quê; nunca se inventa valor. O `record_loop.py` preenche os seis sozinho, e
o teste `test_todo_codigo_nosso_tem_registro_de_proveniencia_com_os_seis_campos` reprova código
nosso sem registro (ou com campo nulo sem lacuna declarada).

**A lacuna que originou a regra**: o código de `K7(9,4) ≤ 1351` é 3 cosets de um núcleo `[9,3]_7`
(1029 palavras, gerador `lincov` do coldcase, commit `56a8cce`) mais **322 palavras de remendo
guloso cuja origem se perdeu**: não há script, seed, comando nem registro de quem rodou. O teorema
Lean não depende disso (o código explícito é o certificado), mas a busca não é reproduzível. Os
códigos de 1285 e 1887 foram resgatados da factory-01 na mesma situação, e os 6 anteriores a
2026-10-01 também não têm registro de geração. Está tudo declarado em `provenance.json`.

## Comandos

```bash
python3 ledger/build.py                 # baixa as fontes nos commits fixos (cache em ledger/.cache/)
python3 ledger/build.py --fonte DIR     # sem rede: DIR/coldcase/... e DIR/florath/...
python3 ledger/cobertura.py             # depois do build: reescreve COBERTURA.md
python3 ledger/targets.py --top 15      # células-alvo
python3 scripts/loop/record_loop.py --celula "K2(4,1)"             # seco (padrão)
python3 scripts/loop/record_loop.py --celula "K2(4,1)" --executar  # gera, verifica, registra, prepara certs/
python3 -m pytest -q tests              # sem rede (tests/fixtures/fontes/ é um recorte das fontes)
```

O loop aceita `--gerador` e `--verificador` com os placeholders `{q} {n} {R} {saida} {arquivo}
{seed}`; o verificador padrão é `scripts/loop/verify_cover.py` até o `tools/verify` existir. Quando
um código verificado melhora o nosso estado, o loop copia o código para `data/codes/`, atualiza
`ours.json`, `cells.json` e `provenance.json`, e prepara `certs/K<q>_<n>_<R>_M<M>/` (código,
`CERT.json` com a declaração Lean prevista, README) para quem fizer o teorema.

Trocar o commit fixado em `sources.json`: rode `build.py`, depois
`python3 tests/fixtures/recortar_fontes.py DIR` para refazer a fixture; o teste
`test_ledger_commitado_bate_com_o_recortado_nas_celulas_do_recorte` falha se as duas divergirem.

## Publicação (`scripts/publish/`)

* `zenodo_newversion.py --record ID --pdf PDF --zenodo-json .zenodo.json`: nova versão no Zenodo.
  Seco por padrão (sem rede); `--publicar` publica. Token só de `ZENODO_TOKEN`, nunca impresso.
* `genesis_page.py --doi DOI --tag TAG`: gera `build/provas/cobertura.html` a partir do ledger, no
  molde da página da v0.3. Só gera o arquivo; não sobe nada.
