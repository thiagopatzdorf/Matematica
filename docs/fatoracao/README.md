# Fatoração de inteiros

Segundo domínio do hub, depois dos códigos de cobertura. O molde é o mesmo: **achar é caro, verificar é barato**.
Aqui o avaliador exato é a multiplicação: um divisor `d` de `N` com `1 < d < N` se confere em microssegundos, e só
ele decide.

## O que existe hoje

| peça | onde |
|---|---|
| registro dos números (RSA-100, RSA-260, RSA-270), com tamanho, `sha256` e como cada um foi conferido | `tools/fatoracao/numeros.json` |
| importador reproduzível: o número sai do texto da fonte por regra, nunca digitado à mão | `tools/fatoracao/importar_rsa.py` |
| avaliador exato (`1 < d < N` e `N % d == 0`; recusa registro corrompido) | `tools/fatoracao/verificar.py` |
| testes, com controle positivo (os fatores reais do RSA-260) e negativos | `tests/test_fatoracao.py` |
| executor da linha de base do CADO-NFS: uma linha por tentativa, repetição determinística do `nlucky=0` (sementes 1, 2, 3), falha contada na estatística | `tools/fatoracao/medir_cado.py`, `tests/test_fatoracao_medir.py` |

O problema em si (achar um fator do RSA-270, o menor número do desafio ainda aberto) entra pelo fluxo do repo: a
issue **Proposta de problema**, que um mantenedor aceita; só então vira cartão em `problems/cartoes/`.

Como cada número foi conferido: nos **fatorados**, `p * q == N` é uma identidade exata, então um dígito errado em
qualquer dos três faria o importador recusar. No **aberto** (RSA-270) não há identidade para conferir; por isso o
importador exige uma segunda cópia independente (a lista do desafio, com checksum) e compara dígito a dígito. As duas
coincidiram em 2026-10-04.

## Reproduzir

    curl -A "<seu-agente>" "https://en.wikipedia.org/w/index.php?title=RSA_numbers&action=raw" -o wiki.txt
    python3 tools/fatoracao/importar_rsa.py wiki.txt --segunda lista-do-desafio.txt
    python3 tools/fatoracao/verificar.py --lista
    python3 -m pytest -q -p no:cacheprovider tests/test_fatoracao.py

## O programa "bater o GNFS"

O GNFS (crivo de corpo de números, 1993) é o melhor método clássico conhecido para números gerais, com custo
`L[1/3]` e constante em torno de 1,92. Os recordes recentes vieram de engenharia (portar para GPU), não de um
algoritmo novo. **Bater o GNFS é pergunta de pesquisa em aberto**, e este programa existe para responder com
medida, não com esperança. Nada abaixo é alegação de novidade.

### Critério de vitória, escrito antes de qualquer experimento

*Proposto; vale quando o mantenedor aprovar este documento e não muda depois da primeira rodada.*

1. **O que é bater:** em semiprimos aleatórios e balanceados de 60 a cerca de 110 dígitos, um custo medido **sem
   depender de hardware** (relações necessárias, área peneirada, dimensão da matriz) que seja menor **e** cresça mais
   devagar que o do CADO-NFS padrão, com os intervalos de confiança de 95% da constante ajustada sem sobreposição.
2. **O que não conta:** vitória em um número só; tempo de relógio em uma máquina; ganho só de engenharia (GPU, código
   mais rápido) sem mudança algorítmica; tamanhos pequenos demais, em que o termo de ordem inferior domina. Alegações
   anteriores de fatoração por reticulados só fatoravam até ~70 a 80 bits e foram retiradas ou refutadas.
3. **Critério de parada:** se a linha de base medida não reproduzir o crescimento esperado do GNFS, ou se o ganho de
   rendimento (relações por unidade de área) ficar abaixo de 5% em três tamanhos seguidos, o programa para e registra
   o resultado negativo no mesmo lugar.

### Fases

| fase | o quê | avaliador |
|---|---|---|
| 0 | mapa da literatura: o que já foi tentado, para não repetir | busca com fonte citada |
| 1 | linha de base: CADO-NFS compilado e medido em tamanhos pequenos | tempo e contadores medidos, curva ajustada |
| 2 | avaliadores independentes de hardware: rendimento medido do peneiramento, Murphy-E e a função de ranqueamento de David e Zimmermann (2020), porque o Murphy-E pode ranquear polinômios errado | exato e barato |
| 3 | busca guiada por modelo sobre famílias de polinômios e regiões de peneiramento, sempre julgada pela fase 2 | o da fase 2 |
| 4 | só se o ganho **escalar** com o tamanho: discutir computação em escala | decisão do mantenedor |

### Limites honestos

* O mais provável é um ganho de fator constante da ordem de 10% (para o RSA-210 se achou um polinômio com Murphy-E
  cerca de 11% maior que o da fatoração histórica). Mudar o expoente seria descoberta de primeira grandeza.
* Mesmo um ganho assim não fatora o RSA-270: a estimativa grossa (fórmula do GNFS vezes custos auto-relatados dos
  recordes de 2026) é de dezenas de GPU-anos, ou cerca de US$ 1 milhão. É estimativa, não orçamento.
* Redes neurais que "adivinham" fatores não escalam; o modelo aqui entra como gerador de hipóteses, com avaliador
  exato, nunca como autoridade.
