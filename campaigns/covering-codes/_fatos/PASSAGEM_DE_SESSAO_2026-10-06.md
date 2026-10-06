# Passagem de sessão (2026-10-06): tudo o que o próximo corpo precisa

Escrito antes de a sessão ser limpa. Só vale o que está aqui, nos commits e nos arquivos citados.

## 1. O que o Thiago quer (em uma frase)
Descoberta matemática **rigorosa e reprodutível** sobre códigos de cobertura K_q(n,R) (repo `thiagopatzdorf/Matematica`), com evidência auditável. Regras dele: nunca virar "não encontrei" em "não existe"; nunca virar "verificado por programa" em "provado formalmente"; nunca virar "menor que a tabela consultada" em "novo recorde"; palavras proibidas: "novo recorde", "primeiro", "inédito", "estado da arte" (como afirmação). Sem Zenodo/DOI/anúncio/dinheiro sem autorização. Não executar código de terceiros não auditado.

## 2. Onde as coisas estão
| o quê | onde |
|---|---|
| PR da campanha (rascunho, sem merge) | `thiagopatzdorf/Matematica#47`, branch `claude/problem-archaeology-catalog-x6n3ps` |
| PR da camada de evidência (rascunho, CI verde em `126ce91`) | `thiagopatzdorf/fabrica-de-sites#1050`, mesma branch |
| Campanha | `campaigns/covering-codes/` (gerada por `tools/campaign/migrate_covering.py`, do zero a cada vez) |
| Camada de evidência do kernel | fabrica-de-sites `apps/factory/src/factory_cauteloso/matematica/kernel.py` + `docs/matematica/ESCADA_DE_EVIDENCIA.md` |
| Auditoria dos 5 claims do v0.7 | `campaigns/covering-codes/_auditoria/AUDITORIA_5_NOVOS_CLAIMS.md` |
| Rodada 1 de Kéri | `campaigns/covering-codes/_kericompletion/CONSOLIDADO.md` (+ `slice-0..9/`) |
| Piloto da rodada 2 | `campaigns/covering-codes/_kericompletion/RODADA2_PILOTO_K5_8_3.md` |

Branch na hora desta nota: `main` já está na **v0.9** do paper (K7(6,4) <= 14 virou teorema Lean `CoveringK764.K_7_6_4_le_14`); a branch estava 19 commits atrás.

## 3. O que está de fato estabelecido (e o que não está)
- **Estados de claim** (`IDEA < CONJECTURE < EMPIRICAL < EXHAUSTIVE_BOUNDED < INDEPENDENTLY_REPRODUCED < PROVED < FORMALLY_VERIFIED < EXTERNALLY_REPRODUCED`, `REFUTED`). `PROVED` aqui = teorema Lean construído no kernel (sem `sorry`, axiomas só `propext`/`Classical.choice`/`Quot.sound`) + >= 2 verificadores de grupos de independência distintos em PASS. **Não** é: enunciado revisado por humano (isso é `FORMALLY_VERIFIED`; `statement_review` falta em todos), reprodução externa, nem novidade.
- **Eixo ortogonal "kernel evidence"** (`NONE < EXTERNAL_RUN_REPORTED < KERNEL_VERIFIED < KERNEL_INDEPENDENTLY_REPRODUCED`), calculado, nunca guardado, não lido pelas guardas do claim. Independência exige **duas execuções reais** com `instance_id` capturado distinto, logs distintos, mesmo commit/toolchain. Teste ponta a ponta com duas VMs: claim `k7-8-3-ub-1887` chegou a `KERNEL_INDEPENDENTLY_REPRODUCED`, estado do claim continuou `PROVED`.
- **CoveringHeavy** passou inteiro numa VM (9181 jobs, axiomas padrão). Os 9–10 claims pesados continuam em `KERNEL_VERIFIED` (uma execução); segunda execução independente NÃO foi feita (gasto novo, não autorizado em separado).
- **Os 5 claims do v0.7** (1134, 5607, 5616, 162, 2875): Lean do zero OK, 4 a 7 verificadores PASS, `statement_review` ausente, novelty **não** checada (`MELHORA_APARENTE_A_CONFIRMAR` contra Kéri 2009/2011 e Marosi v2/v3). Ressalva aberta: 4 deles apontam para o mesmo `log_sha256` de build Lean (`7da8f951…`): confirmar se é log único de várias construções ou cópia.
- **Literatura**: Marosi arXiv:2608.19872 v1=1743 (2026-08-20), v2/v3=1475 (2026-08-23/09-02). Kéri: PDFs de 2009-10-15, índice até 2011-11-25. Risco aberto: soma direta amalgamada (ADS) 931/1225 para K_7(9,4), a busca SAT foi inconclusiva. K_5(10,4)=625 é linear [10,4]_5, AMBÍGUO. Código do Marosi (`verify_cov.py`) **NÃO foi executado** (plano de sandbox pronto em `_planos/AUDITORIA_CODIGO_MAROSI.md`).
- **Kéri, rodada 1**: 156 células (camada 0, q primo <= 13, q^n <= 1e7), 10 agentes, SA genérico de 15–300 s: **0 códigos menores que a tabela, 0 intervalos fechados**, 43 `NAO_TENTADA`. Negativo **fraco**: o SA nem reproduz as cotas da própria tabela (K5(4,1)=51, K3(7,1)=186, K3(7,2)=34).
- **Kéri, rodada 2 (piloto K5(8,3), tabela 325)**: `base_search enum` (18 classes de [8,2]_5) com t=13 deixa >=19 órfãs (não reproduz); t=9/10/11 + `patch_opt` (1 seed, 300 s) estagna em M=380 (+55 sobre a tabela). **Nenhuma afirmação sobre a tabela.** Próximo passo sensato: ler a construção da Kéri para 325 antes de gastar mais CPU. Regra de calibração: célula nenhuma é atacada antes de o pipeline reproduzir uma cota conhecida.

## 4. Decisões que tomei sozinho (para não virarem folclore)
1. Tirei o passo redundante de `numpy` do `verify-codes.yml`; o diff de risco alto ficou só nos gatilhos `campaigns/**`. **Aprovação continua sendo do Thiago.**
2. Excluí `campaigns/.../_literatura/*/scripts` e `_kericompletion/*/work` do `ruff` (artefatos de pesquisa, não importáveis).
3. Para o código `q7_n6_R4_M14` (entrou na main em #56 sem teorema Lean) criei a exceção explícita `SEM_TEOREMA_LEAN_DECLARADO` em `tests/test_campaign_coherence.py`; o teste falha sozinho quando o código ganha teorema. **Hoje ela está obsoleta** (a main já tem o teorema): tirar na próxima regeneração.
4. Reaproveitei a VM `kr-teste-a` (parada) em vez de criar máquina nova; gasto da fase 2 ~US$0,3 de US$5. Não toquei nas VMs `lote-*` (não são minhas).
5. Mantive o claim novo de K7(6,4)=14 abaixo de `PROVED` (só `INDEPENDENTLY_REPRODUCED`) enquanto não havia Lean.

## 5. Pendências que são do Thiago (nada disso foi autorizado)
- Aprovar o diff de `.github/workflows/verify-codes.yml` (risco alto).
- Decidir se executo o `verify_cov.py` do Marosi numa VM descartável sem credenciais.
- Apagar as VMs `kr-teste-a` e `kr-teste-b` (as ferramentas daqui recusam DELETE).
- Segunda execução do CoveringHeavy em duas VMs (gasto novo) para `KERNEL_INDEPENDENTLY_REPRODUCED` nos pesados.
- `statement_review` humano (leva a `FORMALLY_VERIFIED`) e revisão externa de novidade.
- Se quer que código sem Lean seja barrado da campanha em vez de entrar abaixo de `PROVED`.

## 6. Como operar (aprendido por erro)
- **Regenerar a campanha**: `FACTORY_SRC=<checkout fabrica-de-sites>/apps/factory/src python3 tools/campaign/migrate_covering.py` (~35 min; roda verificadores em cada witness). Rodar em background, não com `sleep`.
- **O CI testa o PR mesclado com a main.** Código novo na main sem witness na campanha quebra `test_campaign_coherence` (já aconteceu 2x). Sempre `git fetch origin main`, mesclar e regenerar antes de culpar o teste.
- **Cada push cancela o CI do commit anterior**: `gate` vermelho com `success cancelled` é cancelamento, não falha. Só o CI do último commit vale. O hook de fim de turno pede commit a cada alteração: evite deixar agentes escrevendo no repo durante a espera.
- **`/tmp` das VMs é limpo no reboot**; binários ficam em `~/kbin`. VM sem internet nem `gcc`: compilar estático na factory-01 e `scp`.
- **Agentes**: 10 agentes em 4 núcleos dão negativos fracos; `pkill` por nome em container compartilhado derruba o lote dos outros (nome de processo único, matar por PID); limite de sessão da API para tudo. `executar` do Factory MCP estoura em 60 s no cliente.
- Commit sempre com `Co-Authored-By: James.V1 <noreply@factory.mybagcenter.com>`. Idioma: português.
