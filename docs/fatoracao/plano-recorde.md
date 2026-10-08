# Plano do recorde: o RSA-270 com o menor custo de informação

Registro de 2026-10-07. O dono decidiu **ir atrás do recorde** (fatorar um número do desafio RSA) aplicando a filosofia e o
teorema do James: o ponto não é só fatorar, é fatorar **com o menor custo de informação possível**. Este plano diz o que
isso exige, o que já está de pé e o que só o mantenedor pode decidir. **Nada foi gasto.**

## O alvo

* **RSA-270** (270 dígitos, 895 bits): o menor número do desafio que segue aberto (lista da Wikipédia, texto cru, conferida
  em 2026-10-07; `tools/fatoracao/numeros.json` tem o número conferido dígito a dígito em duas fontes).
* O RSA-896 foi fatorado em 2026-09-19 (Weis) e o RSA-260 em 2026-09-03 (Lu), os dois com GNFS em GPU. O RSA-270 tem **um bit a
  menos** que o RSA-896, então custa da mesma ordem.
* Referência de custo: Weis relata cerca de 30 GPU-anos, até 2048 GPUs, 10 dias, e escreve que o trabalho "não melhorou de forma
  significativa o tempo do GNFS". Lu: cerca de 4.900 GPU-dias (e ~US$ 400 mil, **fonte secundária**).
* O alvo é **perecível**: quem já tem o pipeline em GPU pode fatorá-lo a qualquer momento. Se cair antes, o degrau D vira só
  exame do método, sem o título de primeiro. O resultado científico não muda.

## O que conta como vitória (duas medidas, as duas reportadas)

1. **Fatorar:** `p · q = N` com `1 < p < N` (avaliador exato, `tools/fatoracao/verificar.py`).
2. **Custo de informação e razão de compressão:** relações por bit do fator ([campanha](campanha-compressao.md), seção 1) e
   ρ ponta a ponta contra o baseline b1, com intervalo de 95%.

Fatorar com o custo do baseline é **recorde de engenharia**, não resultado do método (critério 2 do [README](README.md)). Só vale
como resultado do James se ρ sobreviver ao red team e crescer com `N` (E6).

## O caminho, sem pular degrau

| passo | o quê | custo | quem decide |
|---|---|---|---|
| 1 | contador de custo de informação e linha de base (este PR) | zero | feito |
| 2 | executor guarda as relações (pré-requisito do E2) | zero | segue o protocolo |
| 3 | E1, E3, E5 em c80 e c90 no sandbox | zero | segue o protocolo |
| 4 | degrau A em c100 a c120 (≥ 10 réplicas, ≥ 3 tamanhos) | núcleos alugados | **mantenedor** |
| 5 | E6: ρ cresce com `N`? red team (E7) | zero a baixo | segue o protocolo |
| 6 | RSA-270 ponta a ponta | da ordem de dezenas de GPU-anos | **mantenedor**, só se 5 passar |

Pela Lei de Amdahl do protocolo, mesmo com crivo e álgebra linear a custo zero o teto ponta a ponta é 5,7×. O mais provável é
ganho de fator constante pequeno; o plano existe para responder isso com medida e matar cedo.

## O que só o mantenedor decide (pedido numa mensagem só)

* **Teto de gasto** para o degrau 4 e para o degrau 6, e a fonte da conta (o orçamento do Infinito é US$ 20 por pessoa; o degrau 6
  não cabe nele).
* **De onde vem o compute do degrau 6:** nuvem paga, créditos, parceiros. GPU comercial em escala é o que os dois recordes usaram.
* **Se vale ir ao degrau 6 sem ρ > 1** (recorde de engenharia puro). A recomendação é que não, pelo critério acima.

## Em aberto, a pesquisar antes de qualquer gasto

* Os portes de CADO-NFS para GPU de Weis e de Lu são públicos? Sem eles, o degrau 6 inclui reescrever o porte, que é a maior parte
  do custo de engenharia. **Não verificado.**
* Fase 0b do [mapa da literatura](literatura.md): por que a descida de Joux não vale em `Z/NZ`.
* Custo real por GPU-hora no fornecedor que o mantenedor escolher; as estimativas acima são de terceiros.
