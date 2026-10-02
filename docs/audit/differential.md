# Teste diferencial: exactT × exactT2 × verify_trios (× FFT)

Implementações comparadas:

- `exactT`: referência, em `scripts/search/base_search.c`.
- `exactT2`: o binário da varredura (`sym=1`, SWAR).
- `verify_trios`: `scripts/audit/verify_trios.c`. É uma implementação independente (bola, aritmética,
  canonização), mas usa a mesma ideia de poda por amostra e o mesmo xorshift.
- FFT: `scripts/audit/redteam/rt_fft_trios.py`, do red team. Faz a contagem exata **sem poda**, por
  correlação cíclica em `Z_7^6`.

A comparação é entre os conjuntos de órbitas canônicas (translação × escalar), com o valor de órfãs de
cada uma, e é feita por `scripts/audit/compare_diff.py`.

## Amostra estratificada com T = 8 (a configuração da varredura)

A amostra tem 14 classes (posição L na lista ordenada por |Bc|): 1 (|Bc| mínimo), 2, 3, 5, 10, 50,
1591 (Q25), 3181 (mediana), 4772 (Q75), 6362 (máximo) e 1170, 1329, 4445, 5560 (sorteadas com a
semente 20261002).

| L | exactT | exactT2 | verify_trios | resultado |
|---|---|---|---|---|
| 1 | 3 órbitas, mín. 6 | 3 órbitas, mín. 6 | 3 órbitas, mín. 6 | IGUAIS |
| 2, 3, 5, 10, 50, 1170, 1329, 1591, 3181, 4445, 4772, 5560, 6362 | nenhum trio ≤ 8 | nenhum trio ≤ 8 | nenhum trio ≤ 8 | IGUAIS (13/13) |

**14/14 iguais.** A FFT sem poda, na classe 1 com T = 8, dá as mesmas 3 órbitas e o mesmo mínimo
global de 6 (erro de arredondamento 1,4e-12).

## T > 8 (conjuntos não vazios)

| classe | T | comparação | resultado |
|---|---|---|---|
| 1 | 10 | exactT × exactT2 × verify_trios | 3 = 3 = 3 órbitas, IGUAIS |
| 1 | 30 | exactT × exactT2 | 1992 = 1992 órbitas (órfãs de 6 a 30), IGUAIS |
| 1, 2, 3, 5 | 30 | três implementações | **em andamento** (lento: a poda quase não age com T = 30) |
| 2 | 25 | exactT2 sym=1, semente 1 (mu=18, m≈201) × semente 2 (mu=5, m≈56) | **78 = 78 órbitas, IGUAIS** (18 com 21 órfãs, 36 com 24, 24 com 25; mínimo 21): a poda não depende da amostra Y |
| 2 | 25 | FFT sem poda × exactT2 sym=1 (sementes 1 e 2) | **78 = 78 = 78 órbitas, IGUAIS**; mínimo global da FFT (sem limiar) = 21 |
| 2 | 25 | exactT × exactT2 sym=0 × exactT2 sym=1 × FFT | **78 órbitas nas quatro, IGUAIS** (mínimo 21) |
| 3, 4 e degeneradas 319, 40 | 8 | FFT sem poda × varredura | nenhum trio ≤ 8 em nenhuma; mínimos globais exatos 24, 27, 1556 e 1756 |

## Limites deste teste

- O `verify_trios` não é independente no método, só na implementação. A única contagem sem poda é a
  FFT, feita nas classes 1, 2, 3, 4 e nas degeneradas 319 e 40: bateu em todas.
- A semente da amostra Y é fixa no binário oficial. A independência em relação a Y é garantida pelo
  argumento (a poda vale para qualquer Y ⊂ X); o teste empírico com duas sementes e dois tamanhos de amostra na classe 2 (T=25) deu conjuntos
  idênticos.
- Recontar as 7737 classes sem o `exactT2` custaria ~550 h de CPU com a FFT ou ~200–400 h com o
  `verify_trios`. Não foi feito.
