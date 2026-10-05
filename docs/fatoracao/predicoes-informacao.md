# Previsões registradas antes de coletar o conjunto `teste`

Escritas em 2026-10-05, com o pipeline `tools/fatoracao/baseline_informacao.py` congelado neste mesmo commit. O conjunto `dev`
(c60, c70, c80 com três instâncias cada) serviu para desenvolver o pipeline; os números dele **não** foram usados para escolher
estas previsões depois de vistos. O conjunto `teste` (sementes de prefixo `teste`) só é coletado depois deste commit.
Cada previsão pode falhar, e a falha vai para o relatório sem ajuste.

| id | previsão | falha se |
|---|---|---|
| P1 | O núcleo do purge é vazio até ~50% das relações e a transição fica entre 50% e 85% das brutas. | transição fora de [0,5; 0,85] em mais de 1 instância |
| P2 | Para `excesso`, o modelo de saturação (M5) vence por BIC em ≥90% das instâncias; para `ideais_vistos`, vencem M2/M3 (potência ou log). | M5 vence menos de 90% ou M1 (linear) vence `ideais_vistos` |
| P3 | A margem de parada (1 − t_min/brutas) é ≤15% e o intervalo da inclinação final contém 0. | margem >15% em mais de 1 instância |
| P4 | A previsão de relações descartadas por prefixo, treinada num tamanho e testada no seguinte, tem AUC ≥0,75 e rejeita ≤15% das relações úteis no ponto de 99% de recall. | AUC <0,75 ou fração rejeitada >15% |
| P5 | O excesso real fica abaixo do modelo de configuração; a compressibilidade do real e do nulo difere menos de 10%. | excesso real ≥ nulo, ou diferença ≥10% |

Nível de resultado (campanha): R0 se P4 falha e nenhum preditor de descarte dá ≥1,1× em informação útil por CPU; só sobe com
transferência entre tamanhos medida no `teste`. RSA-896 não entra como dado cego.
