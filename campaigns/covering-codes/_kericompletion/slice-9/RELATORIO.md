# Fatia 9: relatório (K_q(n,R), cotas superiores)

Resultado: **nenhum código menor que a cota da tabela consultada foi achado**; nenhuma célula fechada. 0 códigos para verificar (portanto nenhum passou pelos dois verificadores; `/tmp/verify` compilado, não usado).

Método: SA direto em C (`work/sa.c`, 1 núcleo, `nice -n 10`): M palavras livres, custo = pontos descobertos, movimento = mover uma palavra para perto de um ponto descoberto ou vizinho a distância 1. Alvo único M = ub-1, T0=0.5, T1=0.25, semente 1, via `work/batch.sh` (log em `work/batch.log`). Sem calibração em M=ub, exceto K3(7,1) (M=186 e 190: não chegou a 0, melhor 61 e 9 descobertos), o que mostra que o SA simples não reproduz sequer as cotas da tabela. Não foram usados base+remendo nem ILP/SAT exato (tempo).

| célula | ub tabela (fonte) | M tentado | tempo | melhor nº de pontos descobertos | estado |
|---|---|---|---|---|---|
| K3(7,1) | 186 (keri_2011) | 185 | 150s | 23 | SEM_MELHORA_NESTA_BUSCA |
| K3(8,3) | 27 (keri_2011) | 26 | 200s | 36 | SEM_MELHORA_NESTA_BUSCA |
| K2(14,2) | 248 (keri_2011) | 247 | 240s | 747 | SEM_MELHORA_NESTA_BUSCA |
| K3(9,1) | 1269 (keri_2011) | 1268 | 240s | 1241 | SEM_MELHORA_NESTA_BUSCA |
| K2(16,5) | 28 (keri_2011) | 27 | 240s | 144 | SEM_MELHORA_NESTA_BUSCA |
| K7(6,1) | 4435 (keri_2011) | 4434 | 240s | 7980 | SEM_MELHORA_NESTA_BUSCA |
| K3(11,3) | 243 (keri_2011) | 242 | 240s | 5875 | SEM_MELHORA_NESTA_BUSCA |
| K5(8,4) | 65 (keri_2011) | 64 | 240s | 282 | SEM_MELHORA_NESTA_BUSCA |
| K2(19,1) | 31744 (keri_2011) | 31743 | 200s | 43293 | SEM_MELHORA_NESTA_BUSCA |
| K7(7,1) | 31045 (keri_2011) | 31044 | 200s | 30091 | SEM_MELHORA_NESTA_BUSCA |
| K3(13,4) | 335 (keri_2011) | 334 | 200s | 16250 | SEM_MELHORA_NESTA_BUSCA |
| K2(21,7) | 32 (keri_2011) | - | - | - | NAO_TENTADA |
| K2(22,8) | 28 (keri_2011) | - | - | - | NAO_TENTADA |
| K3(14,3) | 2187 (keri_2011) | 2186 | 200s | 659895 | SEM_MELHORA_NESTA_BUSCA |
| K2(23,9) | 16 (keri_2011) | - | - | - | NAO_TENTADA |

NAO_TENTADA: K2(21,7), K2(22,8), K2(23,9) (bolas de ~2e5 a 1e6 pontos tornam o SA direto inviável no orçamento; as cotas da tabela vêm de construções estruturadas) .

"Não achei" não significa "não existe": é só esta busca curta. Lower bounds não foram tocados. Nada fora de slice-9/ foi alterado. `codes/` está vazio.
