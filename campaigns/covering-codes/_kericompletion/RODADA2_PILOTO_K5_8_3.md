# Rodada 2, piloto em K5(8,3): calibração do kit estruturado (2026-10-05)

Objetivo: antes de atacar células abertas, ver se `base_search enum` reproduz a cota da tabela (Kéri 2011: K5(8,3) <= 325 = 13 classes laterais de um [8,2]_5).

Comando (VM kr-teste-a, binário estático, 1 processo por t, `timeout 1500`):
`base_search enum 5 8 2 3 <t> 40` com t = 13 (M = 325) e t = 12 (M = 300).

Resultado (18 classes de [8,2]_5, enumeração completa, 2 processos terminaram sozinhos):

| t | M | menor nº de classes laterais órfãs (melhores 3) |
|---|---|---|
| 13 | 325 | 19, 22, 27 |
| 12 | 300 | 48, 49, 61 |

**Calibração falhou:** com t = 13 (a própria cota da tabela) nenhuma classe chegou a zero órfãs. A escolha das classes extras para t > 3 é gulosa (README do kit), e o `enum` não rodou remendo. Portanto este resultado não diz nada sobre K5(8,3) < 325; diz que o `enum` sozinho não reproduz a construção da tabela e que falta o passo de remendo (`patch_opt`) e/ou busca exata das síndromes.

Nenhum código foi gerado; nenhum verificador rodou. Custo: VM e2-highmem-4 ligada ~25 min (~US$0,15), desligada ao fim. Não foi afirmado nenhum resultado sobre a tabela.
