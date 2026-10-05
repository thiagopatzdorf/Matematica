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

## Remendo sobre bases menores (2026-10-05, mesma VM)

Como a base de t = 13 já tem 325 palavras (= a cota), o caminho certo é base menor + palavras/retas soltas. `base_search enum 5 8 2 3 t 40` com t = 9, 10, 11 (18 classes de [8,2]_5 cada, completas) e depois `patch_opt base_t.json --secs 300 --seed 1` na melhor classe de cada t (todas com A = "40 04 44 44 43 43"):

| t | palavras da base | órfãs (melhor classe) | menor M com cobertura completa pelo `patch_opt` |
|---|---:|---:|---:|
| 9 | 225 | 317 | 380 |
| 10 | 250 | 165 | 380 |
| 11 | 275 | 92 | 380 |

O `patch_opt` fechou coberturas completas (por exemplo M = 383 = 275 + 21 retas x 5 + 3 palavras em t = 11, encolhido depois para 380), mas estagnou em 380, **55 acima da cota da tabela (325)**. As três buscas ainda corriam quando a VM foi desligada (limite de 300 s por seed, uma seed só).

Conclusão da calibração: o pipeline `enum` + `patch_opt`, com uma seed e 300 s, **não reproduz** a cota da tabela em K5(8,3). Os 325 de Kéri vêm de outra estrutura (ou de uma busca muito mais longa e com mais sementes). Nada foi afirmado sobre K5(8,3) < 325. Os códigos de M = 380 gerados não são resultado (estão acima da tabela) e não foram salvos no repo.

Próximo passo possível (não executado): mais sementes e tempo no `patch_opt`, bases com k = 3, ou buscar na literatura a construção que dá 325 (K5(8,3) = 5^3 + ... via linear [8,3]_5 mais classes) antes de qualquer outra célula.
