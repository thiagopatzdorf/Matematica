# K_3(6,2), M = 15 e 16: uma escada de lemas legíveis no lugar dos certificados de Farkas (2026-10-05)

Os certificados de Farkas de `K3_M15_CONTAGEM.md` e `K3_M16.md` matam todas as instâncias, mas cada um
é um vetor de pesos sobre 729 pontos mais as fibras, sem leitura humana. Aqui, cada instância
(s*, K, t) é levada pelo **degrau mais legível que a mata**, e cada degrau tem um certificado pequeno
conferido em inteiros (`confere_*`, só a biblioteca padrão). Código em `tools/exatos/k362/estrutura/`.

## Os degraus

Fatia 0 = palavras com c_0 = 0; K = as s* projeções delas em Z_3^5; U(K) = pontos a distância >= 3 de K.
Uma palavra fora da fatia 0 só cobre (0, u) se sua projeção está a distância <= 1 de u.

| degrau | enunciado (mata se) | depende de |
|---|---|---|
| P1 | P ⊂ U, pontos a distância >= 3 entre si, \|P\| > M − s* (casa dos pombos) | K |
| T  | pesos inteiros w >= 0 em U, w(B_1(y)) <= W para todo y, Σw > W(M − s*) | K |
| F  | T somado às fibras (coordenada i, símbolo b) com a falta s* − \|K_{i,b}\| | K |
| X  | complemento de B_2(F) em Z_3^6: Σw > (M − s*)·max_c w(B_2(c)) | K |
| XB | X com os blocos: Σw > t_1·λ_1 + t_2·λ_2 | K, t |
| XBF | XB com as fibras | K, t |

P1, T e F só dependem de K, e as K de M = 15 estão quase todas na lista de M = 16: o censo
roda uma vez por K (11 592 K únicas) e decide os dois M.

## Resultado (instâncias; a coluna é o primeiro degrau que mata)

| M | instâncias | P1 | T | F | X | XB | XBF | só o LP inteiro, inviável | só ramificando |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 15 | 12 049 | 5 668 | 5 952 | 416 | 6 | 5 | 0 | 0 | 2 |
| 16 | 12 674 | 1 271 | 8 988 | 1 891 | 350 | 60 | 22 | 11 | 81 |

Por s* (M = 16): s* = 2, todas por P1 (18); s* = 3, 40 P1, 80 T e 4 de resíduo; s* = 4,
222 P1, 1 134 T, 42 F e 63 de resíduo; s* = 5, 991 P1, 7 774 T, 1 849 F e 457 de resíduo.
Tabela completa: `python3 tools/exatos/k362/estrutura/censo.py --saida <(zcat .../dados/censo_K.jsonl.gz) --resumo`.

Leitura:

* **M = 15**: 99,9 % das instâncias morrem só com a fatia 0, e 47 % por casa dos pombos pura (P1).
  Sobram 13; 11 morrem pelo complemento da fibra (X/XB) e 2 precisam ramificar.
* **M = 16**: 95,9 % morrem só com a fatia 0; P1 cai para 10 % (a folga M − s* cresce) e T vira o
  lema dominante (71 %). Dos 524 restantes, 432 morrem por X/XB/XBF, 11 só pelo LP da instância
  inteira e **81 só ramificando**.
* **Conferência cruzada**: as instâncias em que o LP da instância inteira (0 <= z <= 1) é *viável*
  são exatamente as que têm certificado de Farkas com mais de uma folha em `contagem/dados`: 2 de 2
  em M = 15, 81 de 81 em M = 16 (igualdade de conjuntos, conferida). Nenhum lema de LP pode matá-las;
  o próximo passo legível para elas é um lema de integralidade (corte), não mais um degrau de LP.

## Sanidade

Cada degrau marcado como "mata" teve o certificado conferido em inteiros na hora (`lemas.confere_*`,
`todas_fatias.confere_complemento`). O conjunto P do P1 vai gravado no censo. Teste negativo feito
num P1 válido de M = 16: duplicar um ponto, retirar um ponto ou trocar um ponto por um de K faz
`confere_empacotamento` devolver falso.

## O que isto não é

Não é prova nova: a prova continua sendo a conferência exata dos certificados de Farkas. Os degraus
são a mesma desigualdade escrita em forma que se lê, e o censo diz quanto da prova cabe em cada forma.
X/XB/XBF e T/F não têm certificado gravado no repositório (só P1); para regravá-los, rode os scripts.

## Reprodução

    # censo da fatia 0 (≈ 4 h em 1 processo com a máquina disputada; retoma de onde parou)
    python3 tools/exatos/k362/estrutura/censo.py --saida censo_K.jsonl
    python3 tools/exatos/k362/estrutura/censo.py --saida censo_K.jsonl --resumo
    # resíduo nas fatias 1 e 2 (≈ 2 min)
    python3 tools/exatos/k362/estrutura/residuo.py --censo censo_K.jsonl --saida residuo.jsonl

Saídas desta rodada: `tools/exatos/k362/estrutura/dados/censo_K.jsonl.gz` e `residuo.jsonl.gz`.
