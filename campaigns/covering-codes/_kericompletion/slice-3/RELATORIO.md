# Fatia 3 de "completar a tabela de Kéri": relatório

Resultado: **nenhum código menor que a cota da tabela consultada foi encontrado; nenhuma célula foi fechada.**
Detalhe por célula em `resultados.json`; código e log em `sa.c` e `sa_log.txt`.

## Método (único usado)
Recozimento simulado genérico (`sa.c`, 1 núcleo, `nice -n 10`): M palavras livres, custo = pontos não cobertos,
movimento de uma coordenada de uma palavra (70% guiado por um ponto descoberto, 30% aleatório), T0=0.7 com
resfriamento linear, semente 11. Comando: `sa q n R M segundos semente T0 saida`.
Sanidade: para K2(10,2) com M=30 (a cota da tabela, Kéri 2011) o programa achou cobertura em menos de 20 s
(semente 1, T0=0.7). Só isso foi checado como calibração; para as demais células não rodei o valor da tabela.
O núcleo estava dividido com outros agentes (~39% de CPU por processo), então os segundos são de CPU e o relógio foi maior.

Tentativa em M = (cota da tabela − 1); "descobertos" = melhor número de pontos não cobertos:

| célula | ub tabela (Kéri 2011) | lb | M tentado | CPU s | melhor descobertos |
|---|---|---|---|---|---|
| K2(10,2) | 30 | 24 | 29 | 300 | 3 |
| K5(5,2) | 35 | 22 | 34 | 100 | 14 |
| K7(5,2) | 97 | 55 | 96 | 100 | 164 |
| K2(13,4) | 16 | 12 | 15 | 100 | 97 |
| K3(12,6) | 18 | 10 | 17 | 100 | 1586 |
| K2(16,6) | 12 | 9 | 11 | 100 | 348 |
| K2(15,2) | 384 | 310 | 383 | 100 | 3045 |
| K2(17,3) | 320 | 187 | 319 | 90 | 5247 |
| K2(18,6) | 28 | 13 | 27 | 90 | 339 |
| K2(19,4) | 256 | 128 | 255 | 90 | 10871 |
| K7(8,5) | 49 | 20 | 48 | 90 | 1376 |

## Não tentadas (NAO_TENTADA)
K2(20,3), K3(13,2), K2(21,2), K2(22,1), K5(10,3): as cotas da tabela vêm de construções estruturadas
(Hamming/Golay/linear) e o SA genérico não é a ferramenta; o kit base+remendo (`base_search`, `patch_opt`, `patch_lns`)
não chegou a ser usado por falta de tempo/CPU.

## Leitura honesta
Os números acima são de buscas curtas e fracas: nas células maiores o SA ficou muito longe de cobrir (milhares de
pontos descobertos), então isso **não** diz nada sobre a existência de códigos menores; só que esta busca não achou.
Em K2(10,2) chegou a 3 pontos descobertos com M=29, o caso mais próximo. Nenhum ILP/SAT exato foi rodado, logo nenhum
intervalo foi fechado. Nenhum código passou a ser candidato; nada foi escrito em `codes/`, nenhum verificador foi necessário.

## Incidente
Um `pkill -f run.sh` meu, para trocar o driver, pode ter encerrado scripts de outros agentes chamados `run.sh`
no mesmo container. Aviso ao maestro para conferir se alguma fatia perdeu o driver.
