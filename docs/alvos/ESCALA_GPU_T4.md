# GPU (T4) nas cotas superiores K_q(n,R): o que foi medido e como escalar (2026-10-07)

Pergunta do dono: a T4 corta o custo da busca de cotas superiores, ou derruba o método? Resposta curta, com número:
**para a busca (cota superior), sim, de 2× a ~4× por dólar quando o trabalho por iteração é pesado, e nada quando é
minúsculo; para a prova (cota inferior, SAT/LRAT e kernel do Lean), não: é CPU.** Tudo abaixo foi medido na VM spot
`gcp-t4-teste` (n1-standard-8 = 8 vCPU, que são 4 núcleos com SMT, + 1 T4, Ubuntu 24.04, driver 610.57, CUDA 12.0),
com `tools/busca_gpu/tabu_gpu.cu` (PR #119). Gasto da fase: ver "Custo".

## 1. O que foi construído e conferido

`tabu_gpu.cu`: uma cadeia por bloco de 128 threads, cobertura por contagem de bolas no espaço inteiro. Três modos:
0 = tabu de `tools/busca_direta/tabu.c` (movimento de uma coordenada, candidatos em paralelo);
1 = SA guiado de uma coordenada; 2 = SA que realoca uma palavra para a bola de um descoberto (o movimento do `sa_cover.c`).

* Correção: o modo `-DEMU` roda o **mesmo** código em CPU e, a cada lançamento, recompara as contagens
  incrementais com uma recontagem do zero (teste `tests/test_busca_gpu_emu.py`); nos três modos, 0 divergências.
* Todo código achado na GPU passou no verificador oficial (`tools/verify/verify`, `uncovered=0`).
* Limites do PoC: M ≤ 128, q^n ≤ 4 M pontos, contagem em `uint8` (M < 255). Em células com casca grande
  (por exemplo K_4(10,5): 129 mil pontos por candidato) o tabu desta versão varre demais; lá o tabu da CPU, que usa a
  lista curta de descobertos, ainda é melhor.

## 2. Medidas (mesma VM, mesmo alvo)

### 2.1 Vazão, K_5(6,3) com M = 24 (alvo que ninguém fecha; recorde 25), iterações do tabu por segundo

| onde | iterações/s |
|---|---|
| CPU, 8 processos `tabu.c` (a VM inteira) | 18 900 (2 360 por processo) |
| CPU, 4 processos (um por núcleo físico) | 17 200 (4 300 por processo) |
| T4, 40 cadeias | 113 600 |
| T4, 160 cadeias | 175 500 |
| T4, 240 cadeias, `-DMAXC=640` (uma "onda" de blocos) | **342 700** |
| T4, 640–1920 cadeias | 232 000–273 000 (efeito de cauda dos lançamentos) |

Ou seja, **~18× a VM inteira em CPU**. O gargalo era memória compartilhada: reduzir `MAXC` de 1536 para 640 subiu de
245 mil para 343 mil it/s, e a T4 ficou em ~45 W de 70 W, então ainda há folga.

### 2.2 Tempo até um alvo fácil, K_5(6,3) M = 25 (empata o recorde)

CPU, 8 sementes: 0,3 a 39,8 s (mediana ~6 s). T4, 40 cadeias: **todas as 40 fecharam em 0,84 s**.

### 2.3 K_3(6,1) com M = 73 (ub conhecida; `sa_cover` em CPU), mesmo recozimento

| onde | resultado |
|---|---|
| CPU, 6 processos `sa_cover` | 5 de 6 em 13 s (4,6 M iterações cada); o 6º em 72 s |
| T4, SA de uma coordenada (modo 1), ciclo 2 M, 240 cadeias | 1º sucesso em 3,1 s; **83 de 240 em 60 s** (25,6 M it/s) |
| T4, SA que realoca (modo 2), ciclo 2 M, 240 cadeias | 1º sucesso em 3,3 s; **121 de 240 em 60 s** (23,0 M it/s) |
| T4, modo 1 com ciclo 200 mil | 10 de 240 em 120 s: o cronograma de resfriamento decide mais que a vazão |

Achado: a GPU **não encurta** o tempo de uma cadeia (cada cadeia roda a ~100 mil it/s, menos que os 360 mil do
`sa_cover` em um núcleo); ela multiplica o número de cadeias independentes. Serve para caça de evento raro, não
para latência de um resultado único.

## 3. Custo por resultado: onde a GPU compensa

Preços de lista (spot, sa-east1, por hora): VM com T4 ≈ US$ 0,40; CPU `c2d-highcpu-8` ≈ US$ 0,09 (a CPU da c2d é mais
rápida que a da n1, então a comparação abaixo favorece a GPU). Cálculo, não medida na c2d:

| problema | vazão GPU / CPU (mesma VM) | US$ por unidade, GPU vs CPU c2d | veredito |
|---|---|---|---|
| tabu em K_5(6,3) (casca de 640 pontos) | 18× | ~4× mais barato na GPU | GPU compensa |
| SA em K_3(6,1) (bola de 13 pontos) | ~4–5× em sucessos/s | ≈ igual (US$ 5,6 e 5,4 por 100 mil sucessos) | empate |
| prova SAT/LRAT (cota inferior) | não roda em GPU | — | CPU |
| kernel do Lean (1 700–4 800 CPU-h) | não roda em GPU | — | CPU |

## 4. Cotas reais do projeto (lidas em 2026-10-07, `southamerica-east1`)

* **GPUs: 1 no total** (`GPUS_ALL_REGIONS` 1/1; T4 spot 1/1 em uso; L4 spot 0/1; V100/P100/P4/K80: 1 cada). Escalar GPU
  para mais de uma exige pedido de aumento de cota (decisão do dono).
* **CPU**: `CPUS_ALL_REGIONS` 44/96 (52 livres), `C2D_CPUS` 0/100, `E2_CPUS` 0/24, `T2A_CPUS` (ARM) 0/96, `T2D_CPUS` 24/24
  (cheio), `N2_CPUS` 0/200, `IN_USE_ADDRESSES` 3/8.
* Disco da T4: 100 GB e **99% cheio** (44 GB de modelos do Ollama, 24 GB de outro usuário, 12 GB do `worker`); instalar o CUDA
  exigiu excluir as bibliotecas estáticas. Sem folga para nada maior.

## 5. Como escalar

1. **Vazão por GPU** (sem custo novo): ocupação (`MAXC`), memória compartilhada para a contagem em células pequenas
   (q^n ≤ ~48 KB cabe no bloco), vários blocos por cadeia nas células de casca grande, lista curta de descobertos como
   no `tabu.c` para q^n grande. Esperado: mais 2–3× (não medido).
2. **Mais cadeias, mais variedade**: o SA converge por cronograma; vale varrer `ciclo` (2 M foi bem melhor que 200 mil)
   e `T0/Tmin` por célula antes de escalar horas.
3. **CPU em paralelo na mesma VM**: os 7 vCPU livres rodam `sa_cover`/`tabu` enquanto a GPU trabalha (feito em K_3(6,1) M = 72).
4. **Mais CPU, barato**: `c2d-highcpu-16` spot sem IP externo, até ~52 vCPU livres hoje, para o que é CPU
   (lote K_3(7,3) do lema das fibras, SAT/LRAT); a ordem dos preços está em `docs/exatos/LEAN_K474_PLANO.md`.
5. **Mais GPU**: só com cota maior (`GPUS_ALL_REGIONS`), ou GPU de outro provedor (preços por hora em outra conversa; 4090
   de US$ 0,34/h seria ~10× a FP32 da T4), decisão do dono.

## 5b. Limpeza do disco da T4 e pedido de cota (por ordem do dono, 2026-10-07)

**Disco** (100 GB, estava 99% cheio, 1,6 GB livres; agora 89%, 11 GB livres). Apaguei só o que é descartável ou se refaz:

| o que | tamanho | por que pode |
|---|---|---|
| `~/imgfactory/jobs/*` com mais de 14 dias (2743 pastas, todas de 10 a 12/09) | 7,1 GB | pasta de trabalho do `bin/imagem.py`: a foto entra por scp, o resultado volta para quem chamou; refaz-se a partir das fotos originais; nenhum job rodando |
| `~/.cache/pip` | 0,8 GB | cache |
| journal do systemd (vacuum para 100 MB) | 0,8 GB | log antigo |
| `apt-get clean` | ~0,8 GB | cache de pacotes |

**Não toquei** (e por quê): `/home/arthurjww` (24 GB, outro usuário, sem permissão de leitura); os modelos `synex-ai` e
`synex-security` do Ollama (~13 GB cada, **não aparecem em nenhum arquivo do repo**, então não são do James, provavelmente de
outro usuário); `gpt-oss:20b` (dois blobs de 13,8 GB, um deles criado pela corrida de FunSearch de hoje cedo) e o Ornith
(o cérebro do James); `~/.cache/huggingface` (modelos de voz do `voz-james.service`, em uso). Se o dono confirmar que os
`synex-*` e um dos `gpt-oss:20b` podem sair, são ~27 GB (`ollama rm`, e `ollama pull` volta).

**Cota de GPU** (Cloud Quotas API; só pedido, não gasta nada). Estado antes: `GPUS_ALL_REGIONS` 1 (pedido de 07/09, aprovado em 1),
T4 e L4 spot por região 1 cada; as cotas **por zona são fixas** (`is_fixed`) e não aceitam pedido. Pedi **4** para
`GPUS-ALL-REGIONS-per-project` (atualizando o pedido existente), `PREEMPTIBLE-NVIDIA-T4-GPUS-per-project-region` e
`PREEMPTIBLE-NVIDIA-L4-GPUS-per-project-region` em `southamerica-east1`, com o e-mail do dono como contato (a API exige).
Os três ficaram `reconciling` (em análise). Histórico do projeto: pedidos de CPU grandes foram negados ou concedidos pela
metade (T2D 48 → 24, E2 48 → 0), então 4 pode virar 2 ou 1; se negarem, o plano é reaproveitar a única GPU.

## 6. Decisões tomadas sozinho

* Adicionei a chave pública da factory-01 ao metadata `ssh-keys` da instância `gcp-t4-teste`, com validade de 12 h
  (expira em 2026-10-08T10:05Z; o agente do GCE a remove sozinho). Foi por pedido do dono ("pega acesso").
* Removi o cache do `apt` e excluí as bibliotecas estáticas do CUDA para caber; **não apaguei nada do James**.
* Armei `shutdown -h +240` no início como teto de segurança.

## 7. O que NÃO foi feito

* Nenhum recorde até aqui. K_3(6,1), M = 72 (aberto desde 1989): 3 variantes de SA na T4 (modo 1 com ciclos de 2 M e 20 M, modo 2 com
  ciclo de 2 M; 240 cadeias, 8 min cada, ~43 bilhões de iterações) e 6 processos `sa_cover` em CPU (~3,2 bilhões, 25 min):
  **todos ficam em 2 pontos descobertos**, o mesmo platô já medido pela sondagem de 04/10 e pelo `k361-lider`.
  Mais iterações (13× a CPU) não tiraram a busca do platô, o que reforça que o obstáculo é estrutural, não de vazão.
* Resultados das células de recorde (K_4(7,3), K_3(8,3), K_5(6,3)): seção a ser preenchida no fim da fase 7.
* Não comparei com a c2d na prática (o preço por resultado da seção 3 é cálculo).
* Não otimizei o kernel além de `MAXC`.
