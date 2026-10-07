# Campanha de compressão: o RSA-270 como exame final, não como alvo

Protocolo **proposto e pré-registrado** do programa "bater o GNFS" (ver [`README.md`](README.md) e o mapa em
[`literatura.md`](literatura.md)). Nada foi gasto. Este documento só passa a valer quando o mantenedor o aprovar, e os
critérios abaixo **não mudam depois da primeira rodada**: mudar exige um PR que diga o que mudou e por quê.

A pergunta científica não é "fatoramos o RSA-270?". É: **uma parte grande do trabalho do GNFS é informação
computacionalmente redundante, e dá para medir onde, e se essa redundância cresce com o tamanho de N?**

## 0. Regras

* **Quatro estados para toda afirmação**, no livro [`claims.jsonl`](../../tools/fatoracao/baseline/claims.jsonl), com
  regras que um teste impõe (`tests/test_claims_fatoracao.py`):
  * **PROVADO**: teorema com fonte lida (ou resumo lido) e o limite do que ele diz;
  * **VERIFICADO**: reproduzível por um teste que existe no repositório, ou por comando e commit declarados;
  * **EVIDÊNCIA**: dado medido ou publicado, com o dado anexado e o **limite** do que ele não mostra;
  * **HIPÓTESE**: enunciado com o que o **derrubaria** e o experimento (E0 a E7) que o decide.
* **Nenhuma alegação sobre P = NP nem sobre quebra geral de RSA** sai de benchmark. O livro de afirmações é testado contra isso.
* **Nenhum gasto** (GPU, nuvem, créditos) sem decisão explícita do mantenedor. O RSA-270 só entra no degrau final (seção 2).
* Cada experimento grava **uma linha por tentativa**, com semente, `exit`, logs e `sha256`; falha conta na estatística
  (`tools/fatoracao/medir_cado.py`).

## 1. O que se mede: razão de compressão ponta a ponta

```
razão de compressão  ρ  =  compute do melhor baseline reproduzível  /  compute do método novo
```

* **Ponta a ponta** soma `polyselect + crivo + filtragem + álgebra linear + raiz` **mais o custo das tentativas que
  falharam e o da sintonia de parâmetros**. Fase omitida no método novo é erro, não zero
  (`tools/fatoracao/contabilidade.py`, com teste).
* **Unidade:** núcleo-segundo medido num binário fixo (CADO-NFS no commit `692ecb7e`), **mais** contadores
  independentes de hardware: relações necessárias, área peneirada, candidatos de polinômio avaliados, linhas × peso da
  matriz. GPU e CPU nunca se misturam numa razão sem contador comum.
* **Baseline reproduzível:** dois, e a razão oficial é contra o segundo.
  * **b0:** parâmetros padrão do CADO para o tamanho.
  * **b1:** o mesmo CADO com sintonia dos parâmetros dentro de um **orçamento igual** ao que o método novo gastou
    ajustando os seus. Comparar só com b0 infla a razão; reporta-se as duas e vale b1.
* **Incerteza:** pelo menos 10 réplicas por tamanho e pelo menos 3 tamanhos; intervalo de 95% por bootstrap
  (`ic_razao`). Os dados atuais mostram por que: o mesmo c90 levou 500, 477 e 398 s (spread de 25%).
* **O degrau é decidido pelo limite inferior do intervalo**, nunca pela estimativa pontual.

### Custo de informação: relações achadas por bit do fator

A razão ρ mede compute. O custo de informação mede **quanta busca** foi paga para entregar o resultado, com um contador
que não depende de hardware: `relações achadas pelo crivo / (rodadas que entregaram o fator x bits do menor fator)`
(`contabilidade.informacao`, com teste). A rodada que falhou soma no numerador e não no divisor.

Limite que precisa ficar escrito: dado `N`, o fator `p` é determinado, então a complexidade de Kolmogorov condicional
`K(p | N)` é `O(1)`. O custo não está em bits que faltam; está em **tempo de busca**. O que o modelo do James (custo =
D · busca + N · verificação) enxerga é a parte da busca que se repete: `repetida = 1 - distintas/achadas`.

Linha de base congelada (`tools/fatoracao/baseline/cado_legado.jsonl`, CADO-NFS, 4 threads, semiprimos balanceados):

| dígitos | bits do fator | rodadas | falhas | relações por bit | repetida |
|---:|---:|---:|---:|---:|---:|
| 60 | 99,7 | 3 | 0 | 524 | 0,076 |
| 65 | 108,0 | 3 | 0 | 904 | 0,063 |
| 70 | 116,3 | 3 | 0 | 1567 | 0,140 |
| 75 | 124,6 | 3 | 0 | 2154 | 0,080 |
| 80 | 132,9 | 3 | 0 | 2322 | 0,180 |
| 85 | 141,2 | 3 | 0 | 3912 | 0,163 |
| 90 | 149,5 | 3 | 1 | 10253 | 0,155 |
| 95 | 157,8 | 1 | 0 | 16259 | 0,279 |

**Limite do dado:** 1 a 3 rodadas por tamanho e nenhum intervalo de confiança; o c95 tem uma só. Serve para fixar a
métrica e o ponto de partida, **não** para concluir tendência (isso é o E6). Parte da repetição o CADO já colhe na hora
(duplicatas, células pares); a coluna `repetida` é a que sobra no filtro.

### Lei de Amdahl com os números do recorde

Participação de cada fase no **relógio** do RSA-896 (post de Weis; relógio não é compute, porque o número de nós varia
por fase), em `contabilidade.RSA896_HORAS`:

| fase | % do relógio | teto se custasse 0 |
|---|---|---|
| seleção de polinômio | 6,2 | 1,07× |
| crivação | 38,0 | 1,61× |
| filtragem | 9,1 | 1,10× |
| álgebra linear (Krylov, lingen, mksol) | 44,4 | 1,80× |
| caracteres e raiz | 2,2 | 1,02× |

* Um speedup de 100× numa fase de 1% rende **1,0100×** ponta a ponta. Local não é global.
* **Mesmo que crivação e álgebra linear custassem zero, o teto é 5,7×**, porque seleção, filtragem e raiz somam 17,6%.
  Para **10×** essas três também precisam cair 1,8×; para **100×**, 17,6×; para **1000×**, 176×.
* Logo, **degraus de 10× para cima exigem mudar a estrutura do método** (quantas relações são necessárias, qual o
  tamanho da matriz), não afinar uma etapa. Esse é o critério de "não é otimização cosmética".

## 2. A escada de benchmarks que cabe de verdade

A escada pedida (RSA-200, 220, 240, 250, 260, 896, 270) **não pode ser executada de ponta a ponta** com réplicas.
Datas de fatoração na lista do desafio (texto cru da Wikipedia): RSA-200 em 2005-05-09, RSA-220 em 2016-05-13, RSA-240
em 2019-11, RSA-250 em 2020-02-28, RSA-260 em 2026-09-03, RSA-896 em 2026-09-19 (30 GPU-anos ao todo, 177.929 h de H100 só
na janela de crivação). Meu sandbox tem 4 núcleos. Extrapolando minha própria curva por `L[1/3]` (limite superior
grosseiro: a constante calibrada caiu 2,8× entre c80 e c95, então a fórmula superestima), c150 custaria cerca de 0,6
núcleo-ano e c200 centenas. Por isso a escada é esta:

| degrau | números | o que se mede | execução |
|---|---|---|---|
| **A** (dev e teste) | semiprimos gerados, balanceados, c60 a c120 | ponta a ponta, ≥10 réplicas | sandbox; c100 a c120 pedem núcleos alugados (decisão) |
| **B** (externo, pequeno) | números do desafio públicos de c100 a c155 | ponta a ponta, 1 execução com o método **congelado** | só depois do A; c155 passa de 1 núcleo-ano |
| **C** (por fase, sem ponta a ponta) | RSA-200, 220, 240, 250, 260 e 896 | polinômio, test sieve de poucos special-q, estatísticas publicadas | `ρ` é **projeção** com a mistura de fases do recorde: **HIPÓTESE**, não medida |
| **D** | RSA-270 | ponta a ponta | só se os critérios da seção 7 forem cumpridos **e** o mantenedor decidir o gasto |

O degrau C já tem o RSA-896: o polinômio publicado foi reproduzido (resultante `−8N`, `alpha −11,12`, Murphy-E
`5,293e-10`) e congelado em `tools/fatoracao/baseline/rsa896.json`.

**Armadilha de validade (EVIDÊNCIA, C08):** de c60 a c95 a crivação ocupa 72 a 86% da CPU e a álgebra linear 4 a 9%; no
RSA-896 são 38% e 44%. Um método que comprima a crivação em c90 tem teto de ganho de ponta a ponta muito maior ali do que
no recorde. Todo `ρ` medido em A ou B é reportado **por fase** e **reprojetado com a mistura do RSA-896**; essa
projeção é a que vale para decidir o degrau.

## 3. Cegamento: o que dá e o que não dá para esconder

* O método recebe **só `N` e um orçamento**. Quem conhece `p`, `q` e o melhor polinômio é o avaliador. Um teste
  (`test_metodo_novo_que_le_o_gabarito...`) reprova código em `tools/fatoracao/metodos/` que aponte para `baseline/`,
  `rsa896`, `numeros.json` ou o livro de afirmações.
* **Três conjuntos:** *dev* (sementes `dev-*`, onde se desenvolve e se treina), *teste* (sementes `teste-*`, números
  gerados só na avaliação, depois de o commit do método ser registrado) e *externo* (números do desafio).
* **Limite honesto:** o RSA-896 **não é cego para o pesquisador**. Eu li os fatores e o polinômio. Por isso a evidência
  primária é a dos semiprimos de *teste* gerados; os números do desafio só validam depois de o método estar congelado.
  Qualquer ajuste feito depois de ver o resultado externo invalida o externo **para aquela versão** do método.
* Modelos aprendidos treinam só em *dev*, nunca em dados públicos do `N` avaliado (relações, polinômios, matriz).

## 4. Onde procurar a redundância mensurável

Primeiro o que já se vê nos números (C14, EVIDÊNCIA): o crivo do RSA-896 visitou cerca de 1,5e19 células e achou 3,8e10
relações, **cerca de 4e8 células por relação**. O espaço de candidatos é exponencial; o que sai dele é muito pouco. A
pergunta é se existe estrutura que dê as regiões produtivas **sem visitar** a maior parte. O que o CADO e o recorde
**já colheram** (então não conta como descoberta): duplicatas removidas na hora (23,2%), células com `i` e `j` pares
puladas (25% das células, relações idênticas), produtividade por intervalo de special-q.

| o que o pedido lista | como se mede | experimento |
|---|---|---|
| candidatos descartados | relações por célula e por special-q, por região | E3 |
| relações duplicadas | taxa de duplicata por região e por special-q | E3 |
| correlações entre propriedades baratas e rendimento futuro | correlação de postos de preditores baratos contra rendimento medido | E1 |
| equivalências e simetrias entre candidatos | colisões de classes canônicas de polinômios e de special-q | E5 |
| informação recalculada | perfil de tempo do `las` (redução de reticulado, ECM, buckets) | E4 |
| regiões previsíveis | rendimento por special-q previsto por características do reticulado | E3 |
| enumeração trocada por classificação | os mesmos preditores como classificadores, custo por acerto | E1, E3, E4 |
| menos relações e matriz menor ao mesmo tempo | curva relações × tamanho da matriz × custo total | E2 |

## 5. Registro de experimentos (pré-registro)

Cada experimento declara a hipótese nula e o critério de morte **antes** de rodar.

* **E0 — contabilidade do desperdício.** *Feito.* Pergunta: de onde vem o custo e quanto sobrevive até a matriz?
  Resultado (EVIDÊNCIA, C07, C08, C09): no RSA-896 só 15,6% das relações achadas sobrevivem ao purge e 3,9% viram linhas de
  matriz, mas isso **não** prova redundância de informação (depende da política de relações e do limite de primos
  grandes, e a fusão combina linhas). No sandbox a fração que sobrevive ao purge fica entre 22% e 46% sem tendência clara
  (c95 tem 1 réplica). Custo: zero.
* **E1 — preditores baratos do rendimento do polinômio.** Para cada `N` gerado (dev: c80, c90, c100), pelo menos 200
  candidatos do `polyselect`; características baratas (Murphy-E, alpha, lognorm, skew, raízes, coeficientes);
  rendimento real por test sieve de poucos special-q. Métrica: correlação de postos (Spearman) e arrependimento do
  top-k. Treino em *dev*, avaliação em *teste*. **Morte:** o melhor preditor aprendido não supera o Murphy-E por mais de
  0,05 em Spearman nos números de teste (hipótese C11). Custo: núcleos, horas.
* **E2 — relações necessárias e a curva do compromisso.** Guardar os arquivos de relações, rodar a filtragem sobre
  prefixos e achar o **mínimo** que dá matriz resolvível; medir relações × linhas × peso × custo total. Isto define o
  baseline b1 e a "sobra" de crivo. **Morte:** a sobra é menor que 5% (sem redundância de relações a recuperar).
  Pré-requisito: o executor passar a guardar as relações (hoje apaga a pasta no sucesso).
* **E3 — mapa de produtividade por special-q e região.** Rendimento único por special-q e taxa de duplicata, previstos
  por características do reticulado reduzido (norma da base, raízes, tamanho de q). Se previsível, pular o pior quantil
  e medir o efeito **no custo ponta a ponta** a número fixo de relações. **Morte (C12):** ganho evitável menor que 5% do
  custo de crivo, ou o total de relações necessárias sobe e anula o ganho.
* **E4 — informação recalculada na cofatoração e na redução de reticulado.** Perfil do tempo do `las`; política
  aprendida de orçamento de ECM por cofator. Mede relações perdidas por segundo economizado. Prior: os parâmetros de ECM
  do CADO já são ajustados por simulação; o ganho esperado é de fator constante pequeno.
* **E5 — equivalências entre candidatos.** Canonizar polinômios (translação, rotação) e special-q; contar colisões nas
  saídas reais do `polyselect`. **Morte:** colisões abaixo de 1%.
* **E6 — a razão cresce com `N`?** Qualquer `ρ` positivo é medido em ≥3 tamanhos de A; ajusta-se `log ρ` contra dígitos.
  **Morte (C13):** o intervalo de 95% da inclinação contém 0 ou é negativo. É a pergunta central da campanha.
* **E7 — red team e validação externa** (seção 6), obrigatório antes de qualquer aumento de compute.

## 6. Red team

Antes de aumentar compute com qualquer resultado positivo, um relatório de ataque (PR próprio) tenta destruí-lo. O
resultado precisa sobreviver a **todos**:

1. **Baseline fraco:** refazer b1 com orçamento de sintonia 3× maior; a razão cai quanto?
2. **Ruído de relógio:** réplicas em outro horário e com a máquina ociosa; contadores independentes de hardware concordam?
3. **Vazamento:** o método usa algo que depende de `p`, `q` ou do polinômio publicado? (teste de guarda e revisão manual)
4. **Overfit a um `N`:** vale em números de *teste* novos, em pelo menos 3 tamanhos?
5. **Contabilidade:** alguma fase ficou de fora, ou uma tentativa falha foi descartada? (`razao_fim_a_fim` e o registro por tentativa)
6. **Mistura de fases:** a razão sobrevive à reprojeção com as participações do RSA-896?
7. **Extrapolação da álgebra linear:** em c60 a c120 ela pesa pouco e no recorde pesa 44%; o método piora a matriz?
8. **Parâmetros que o CADO já ajusta:** o "ganho" é só uma sintonia que um desenvolvedor do CADO faria numa tarde?
9. **Comparações múltiplas:** quantas hipóteses foram testadas? Correção e conjunto de teste selado.
10. **Segunda implementação:** outra pessoa (ou outro agente) reproduz a razão sem ver o código original?

## 7. Escada de resultados e o que mais precisa valer

O degrau é lido no **limite inferior** do intervalo de 95% de `ρ` ponta a ponta (já reprojetado com a mistura do RSA-896).

| degrau | significado | além do limite inferior, exige |
|---|---|---|
| 1× | baseline reproduzido | executor e baseline congelados (feito: RSA-896 por fase, lote de 60 a 95) |
| 2× | melhoria confirmada | ≥3 tamanhos, números de teste, ≥10 réplicas |
| 5× | engenharia significativa | álgebra linear **medida**, não só crivo; razão por fase |
| 10× | resultado forte | passa no red team (1 a 10); projeção com a mistura do RSA-896 ≥ 5× |
| 100× | possível nova abordagem algorítmica | segunda implementação independente e **explicação mecanística** da redundância |
| 1000× | investigar mudança de regime | ajuste do tipo `L[a, c]` aos custos medidos; nenhuma alegação antes disso |

**Antes de cada degrau acima do 2×, o mantenedor decide o gasto.** O RSA-270 vira exame final **só** se, em A e B, o `ρ`
sobreviver ao red team **e** crescer com `N` (E6). Até lá, nada é gasto tentando fatorá-lo.

## 8. Estado hoje e próximos passos

* **Feito:** lote do CADO-NFS (21 de 22 execuções corretas; 1 falha `nlucky=0`), executor com repetição determinística,
  polinômio do RSA-896 reproduzido e congelado, contabilidade ponta a ponta, livro de afirmações (14 entradas).
* **Prior honesto:** o GNFS é engenhado há mais de 30 anos e as redundâncias óbvias (duplicatas, células pares, ajuste de
  primos grandes) já foram colhidas. A chance de achar `ρ ≥ 2×` em fontes novas é baixa, mas a campanha foi desenhada
  para **responder barato e matar cedo**.
* **Próximos, em ordem e sem gasto:** (1) o executor passar a guardar as relações (pré-requisito de E2);
  (2) E1 em c80 e c90 no sandbox; (3) E5 sobre as saídas do `polyselect`; (4) só então pedir ao mantenedor uma decisão de
  gasto para A em c100 a c120.
