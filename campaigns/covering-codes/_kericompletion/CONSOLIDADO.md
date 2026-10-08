# Rodada 1 da campanha "completar a tabela de Kéri": consolidado

Data: 2026-10-05. Fonte dos números: os `slice-N/resultados.json` (contados por script, não os resumos dos agentes).

## Resultado

| | células |
|---|---:|
| escopo (camada 0, q primo ≤ 13, q^n ≤ 1e7) | 156 |
| tentadas, SEM_MELHORA_NESTA_BUSCA | 113 |
| NAO_TENTADA | 43 |
| código menor que a cota da tabela consultada, verificado | **0** |
| intervalo fechado (lb = ub) por busca exata | **0** |

Nenhum código novo foi gerado (`slice-*/codes/` vazio nas 10 fatias), portanto os dois verificadores (C oficial e `scripts/search/verify.py`) não tiveram o que verificar.

## Leitura correta

O resultado é **negativo e fraco**. Todas as fatias usaram um recozimento simulado genérico (M = cota − 1, 1 núcleo, de 15 s a 300 s por célula). Esse método **nem reproduz a própria cota da tabela** na maioria das células onde foi calibrado (por exemplo K5(4,1) = 51, K3(7,1) = 186, K3(7,2) = 34). Logo "SEM_MELHORA_NESTA_BUSCA" mede o limite do método, não a tabela. "Não achei" não é "não existe".

Nenhuma fatia rodou o kit estruturado (`base_search` → `patch_opt`/`patch_lns`), que é o que produziu os 1285 e 1134, nem ILP/SAT exato para fechar intervalos pequenos.

## Erros de método (viram regra)

1. **Dez agentes em 4 núcleos**: ~39% de CPU por processo e buscas de 15 a 60 s. Pouca CPU espalhada por muitas células não alcança nenhuma.
2. **`pkill` por nome** (`run.sh`, `sa`) em container compartilhado: fatias 2 e 3 confessaram; as fatias 1 e 7 perderam o lote (13 e 11 `NAO_TENTADA`). Regra: cada agente usa nome de processo único e mata só por PID.
3. **Limite de sessão da API** parou os 10 agentes no meio; retomados, entregaram com prazos menores.
4. **Formato**: K13(6,1) não cabe no formato oficial de arquivo (q = 13 precisa de dígitos > 9).
5. Limite fixo de M = 1024 no SA da fatia 6 abortou K5(7,1) e K2(17,1).
6. Cada commit parcial empurrado cancelou o CI do commit anterior; o único CI que vale é o do último commit.

## Segunda fase proposta (não executada; precisa de infra)

- **Poucas células, CPU de verdade**: uma VM descartável (teto US$5/rodada), 1 processo por célula com nome único, sem `pkill` por nome.
- **Kit estruturado** (`base_search enum` → `patch_opt` → `patch_lns`) nas células pequenas sugeridas pelos agentes: K7(8,2), K5(8,1), K3(12,3), K7(4,1), K7(5,3), K5(7,4), K2(11,2), K2(12,3).
- **ILP exato com quebra de simetria** para tentar fechar K2(12,4) (lb 11, ub 12) e K3(7,3).
- **Calibração obrigatória**: toda célula primeiro tem de reproduzir a cota da tabela; sem isso, o negativo não conta.
- Qualquer código achado só entra após dois verificadores PASS e reverificação do maestro. Linguagem: "menor que a cota da tabela consultada", nunca "recorde" nem "novidade".
