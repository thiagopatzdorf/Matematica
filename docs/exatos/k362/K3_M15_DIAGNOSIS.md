# K₃(6,2), M = 15: diagnóstico das 12 049 instâncias (2026-10-05)

Frente núcleo (simetria). Companheiros: `K3_M15_GROUP_ACTION.md` (grupo e provas),
`K3_M15_CANONICAL.md` (forma canônica). A autópsia SAT das seis duras é de outra frente
(`K3_M15_HARD6.md`, em produção); a literatura está no PR #54 (`LITERATURE_K3_6_2.md`).
Estados: OBSERVED (medido, sem garantia), COMPUTATIONALLY_VERIFIED (conferido por programa),
INDEPENDENTLY_REPRODUCED (duas implementações sem código comum), PROVED (prova escrita aqui ou em
`GAPS2_K362.md`). Nada é FORMALIZED. **Nenhuma cota muda com este documento.**

## Primeiro relatório (respostas curtas)

1. **O que são as 12 049.** Uma instância `(s*, K, t)` fixa a fibra mínima `F(0,0)` de um código
   hipotético de 15 palavras: as 5 (ou 2, 3, 4) palavras com x₀ = 0 são exatamente `{(0,k) : k ∈ K}`,
   os outros 238 − s* pontos de `{x₀ = 0}` estão fora, e os blocos `x₀ = 1, 2` têm `t₁ ≥ t₂` palavras.
   12 049 = 5 (s* = 2) + 108 (s* = 3) + 936 (s* = 4) + **11 000 (s* = 5, t = (5,5))**.
   Reproduzido aqui: `rodar_pb.py --listar` devolveu 12 049 em 21 min (COMPUTATIONALLY_VERIFIED).
2. **Grupo.** G = S₃ ≀ S₆, |G| = 33 592 320. O estabilizador da normalização é
   H = S₂ × (S₃ ≀ S₅), |H| = 1 866 240. Provas de que cada ação preserva cobertura, tamanho e as
   restrições extras: `K3_M15_GROUP_ACTION.md` §1–2 (PROVED).
3. **Simetria ignorada.** Entre instâncias: **nenhuma** sob H — as 11 000 configurações de s* = 5
   têm 11 000 formas nauty distintas (INDEPENDENTLY_REPRODUCED: nauty × `fatia.forma`). O desperdício
   é a **escolha da fibra**: no caso equilibrado as 18 fibras têm 5 palavras e um código cai em até
   18 instâncias (OBSERVED: 18 classes distintas em 269 de 300 códigos equilibrados aleatórios).
   Dentro de cada instância sobra `Stab(K) × S₂`, de ordem 2 a 384 (distribuição na §3), que o
   RoundingSat não usa.
4. **As seis duras.** Seis órbitas **distintas** (6 formas nauty diferentes; já era forçado pelo
   Lema 3). O que têm em comum é uma invariante: `|U(K)|` entre 48 e 69 (a população vai de 42 a
   110) e estabilizador pequeno (1 a 6). Não estão relacionadas por simetria.
5. **Órbitas genuínas.** Sob H: 12 049 (a lista já é exata). Com a escolha canônica "fibra de menor
   |U|" (PROVED): **8 107** (7 058 equilibradas + 1 049). Em volume de busca, o teto ideal para as
   equilibradas é ~1/18 do atual; o número de classes de códigos de 15 palavras é, conjecturalmente, 0.
6. **Implementar primeiro:** o filtro da fibra de menor |U| — **só remover instâncias**, sem mexer no
   OPB. É provado, custa nada e é compatível com as provas VeriPB já feitas (o OPB das instâncias que
   ficam é idêntico). Logo depois (fase 2): **dividir** as instâncias de |U| baixo pela classe de uma
   segunda fibra (canonical augmentation), em vez de acrescentar restrições.
7. **Benchmark (§7).** Ganho do filtro: −33 % de instâncias, mas só ~−10 % de CPU estimado pela
   amostra (as removidas são as fáceis). Quebra de simetria **escrita como restrições PB** (regras
   "min"/"max" com variáveis auxiliares, e os cortes antipodais do Raval) **piorou** o RoundingSat:
   10 s → mais de 400 s e → 48 s na instância 10182. A redução promissora é a que divide, não a que
   acrescenta.

## 1. A codificação, matematicamente

Código C ⊂ Z₃⁶, |C| = 15, palavras distintas (sem perda: `GAPS2_K362.md`), raio de cobertura 2.

* **Fibra** `F(j,a) = {c ∈ C : c_j = a}`; são 18 (6 coordenadas × 3 símbolos). `s* = min |F(j,a)|`.
  Como as três fibras de uma coordenada somam 15, `s* ≤ 5`, e **s* = 5 ⇔ todas as 18 fibras têm 5
  palavras** ("configuração 5+5+5" vale em **todas** as coordenadas ao mesmo tempo, não numa só).
* **Normalização** (GAPS2): leva uma fibra mínima a (0,0), ordena os blocos da coordenada 0
  (`t₁ ≥ t₂`), e leva a projeção K de F(0,0) em Z₃⁵ ao representante canônico da sua classe sob
  S₃ ≀ S₅.
* **Fatia**: o hiperplano `{x₀ = 0}`. **U(K)**: pontos da fatia a distância > 2 de K. Filtro de
  contagem do GAPS2: `|U(K)| ≤ (15 − s*)·V(5,1) = (15 − s*)·11` (110 para s* = 5).
* **O que a instância fixa no OPB**: os 243 indicadores da fatia (5 a 1, 238 a 0), as somas dos
  blocos, a cobertura dos 729 pontos e `|F(j,a)| ≥ s*` para j ≥ 1. Restam 486 variáveis livres.

## 2. Grupo óbvio e o que já é usado

| simetria | usada? | onde |
|---|---|---|
| levar a fibra mínima à coordenada 0, símbolo 0 | sim | normalização passo 1 |
| ordenar os blocos `t₁ ≥ t₂` | sim | passo 2 |
| S₃ ≀ S₅ na projeção da fibra | sim, exatamente (uma instância por órbita) | passo 3 + `fatia.forma`; conferido por nauty |
| qual das fibras mínimas foi escolhida | **não** | fator ~18 no caso equilibrado |
| `Stab(K)` × S₂ (troca 1↔2 em x₀ quando t₁ = t₂) dentro da instância | **não** | o solver vê a instância sem simetria |

## 3. Simetria desperdiçada, em números (COMPUTATIONALLY_VERIFIED, `orbitas.py`)

`|Stab(K)|` em S₃ ≀ S₅ nas 11 000 instâncias equilibradas:

| \|Stab\| | 1 | 2 | 3 | 4 | 6 | 8 | 10 | 12 | 16 | 20 | 24 | 32 | 48 | 64 | 96 | 192 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| instâncias | 4 717 | 4 241 | 2 | 1 323 | 164 | 297 | 3 | 115 | 63 | 1 | 32 | 15 | 18 | 6 | 2 | 1 |

O grupo de simetria da instância é `Stab(K) × S₂` (t₁ = t₂ = 5), de ordem `2·|Stab(K)|`. Para
s* = 4 (468 configurações): |Stab| de 1 a 192; para s* = 3 (27): de 4 a 720; para s* = 2: 240.

`|U(K)|` nas 11 000 equilibradas, por faixa de 10: 40–49: 105; 50–59: 1 067; 60–69: 2 632; 70–79:
3 254; 80–89: 2 429; 90–99: 1 159; 100–109: 347; 110: 7. O filtro `|U| ≤ 79` deixa 7 058.

## 4. A redução que é teorema

Lema da soma (`K3_M15_GROUP_ACTION.md` §4, PROVED): `Σ_{(j,a)} |U(j,a)| ≤ Σ_x d(x,C) ≤ 2·714 = 1 428`;
logo a fibra de menor |U| tem |U| ≤ 79. Escolhendo essa fibra na normalização, **12 049 → 8 107**
instâncias, sem perder código (prova de completude no mesmo lugar; testes de completude com o código
de Hamming ternário e um código de K₂(6,1) sob isometrias aleatórias, e reprodução de K₃(4,1) = 9 e
K₂(4,1) = 4 pelo pipeline reduzido com RoundingSat — os quatro testes de solver passam).

| etapa | instâncias | estado |
|---|---|---|
| lista do GAPS2 | 12 049 | COMPUTATIONALLY_VERIFIED (reproduzida) |
| N₁: normalização trivial (fibra, blocos) | 12 049 | já embutida |
| N₂: coordenadas (S₅) | 12 049 | já embutida (RGS + colunas ordenadas) |
| N₃: símbolos (S₃⁵) | 12 049 | já embutida; nauty confirma 1 por órbita |
| N₄: escolha da fibra, regra "menor \|U\|" | **8 107** | PROVED (lema da soma) |
| N₅: órbitas genuínas (classes de códigos) | desconhecido; conjectura 0 | — |

N₄ não divide por 18 porque as instâncias são classes de **fatias**, não de códigos: cada classe K
continua podendo ser a fibra mínima de algum código. O 1/18 aparece no volume de busca dentro das
instâncias, e só é capturado se a instância souber que "a fibra 0 é a canônica" (§7: escrever isso
como restrição PB não funcionou).

## 5. As seis duras (parte de órbitas; a autópsia SAT é da outra frente)

| índice | \|U\| | \|Stab\| | K | veredito sem prova (GAPS2) |
|---|---|---|---|---|
| 7955 | 57 | 2 | 00000 00011 00122 11101 12222 | UNSAT 26 min |
| 9118 | 69 | 4 | 00000 00011 01101 10022 12201 | UNSAT 29 min |
| 10603 | 54 | 4 | 00000 00111 01022 11211 12122 | UNKNOWN aos 30 min |
| 11739 | 48 | 1 | 00000 00111 01022 11101 22210 | UNSAT 7,7 min |
| 11804 | 49 | 1 | 00000 00111 01022 11201 22220 | UNSAT 9,8 min |
| 11927 | 54 | 6 | 00000 00001 11110 11121 22212 | UNSAT 3,5 min |

* Seis órbitas distintas sob H (COMPUTATIONALLY_VERIFIED). Todas sobrevivem ao filtro novo.
* 11739, 11804 e 10603 compartilham o prefixo `00000 00111 01022` (três pontos idênticos na forma
  canônica). OBSERVED, sem interpretação ainda.
* "Estão na mesma órbita sob troca de fibra?" só faz sentido se existir um código que contenha as duas
  fibras; como nenhum código de 15 palavras é conhecido, a pergunta não tem resposta sem busca.

## 6. Hipótese sobre a origem da dificuldade (OBSERVED, não teorema)

**A dificuldade é |U(K)| baixo: a fatia fixa "cobre demais" e propaga pouco.** Na amostra de 234
instâncias com veredito (218 equilibradas), o tempo mediano do solver por faixa de |U| é 10,1 s
(50–59), 8,3 s (60–69), 3,1 s (70–79), 1,5 s (80–89), 0,4 s (90–99) e 0,8 s (100+); as seis duras
estão em 48–69, e nove das dez mais lentas entre as que terminaram têm |U| ≤ 77 (a exceção, 3222,
tem |U| = 84 e levou 86 s, e por isso o filtro não é só "tirar as fáceis"). Combinada com o fator ~18:
cada código equilibrado aparece nas instâncias de **todas** as suas fibras, inclusive as de |U| alto
(fáceis) — mas o trabalho pago é nas de |U| baixo, que são justamente as que a regra "menor |U|"
mantém. Previsão testável: dividir as instâncias de |U| ≤ 60 pela classe de uma segunda fibra
transforma cada dura em muitas com |U| efetivo maior. Há 846 instâncias com |U| ≤ 57.

## 7. Benchmark mínimo (OBSERVED; container local, 2 processos, RoundingSat sem prova)

| instância (\|U\|) | OPB original | + regra "min" (w, \|U\| ≥ u) | + regra "max" (w, \|U\| ≤ u) | + cortes antipodal/esfera-3 do Raval |
|---|---|---|---|---|
| 10182 (62) | UNSAT, 10,0 s, 23 875 conflitos | sem veredito em 400 s (479 153 conflitos) | sem veredito em 400 s (197 101) | UNSAT, 48,1 s, 89 362 conflitos |
| 9139 (60) | UNSAT, 85,1 s, 57 404 conflitos | interrompido | interrompido | — |

Filtro, estimado da amostra: tira 60 das 218 equilibradas, que custaram 266 dos 2 771 s de solver
(9,6 %) e 49 dos 494 s de conferência. Extrapolado: ~1/3 das instâncias e ~1/10 do CPU. As seis
duras e a cauda ficam.

**Conclusão do benchmark.** Acrescentar restrições válidas (simétricas ou de quebra de simetria) à
instância deixa o RoundingSat mais lento aqui — a prova por planos de corte fica mais cara, não mais
curta. A redução promissora é estrutural: menos instâncias (filtro) e instâncias menores (divisão).

## 8. Validação do canonicalizador em códigos inteiros

Bancos de contagem publicada sugeridos pela frente de literatura. `motor --classificar` (C, outra
canonicalização) dá K₃(6,3): 28 classes, K₃(5,2): 1, K₃(4,1): 1 — batendo com a literatura.
`canon.classificar` (nauty, Python): K₃(4,1) = 9 → 1 classe; K₃(6,3) = 6 → ver o corpo do PR (rodada
local). K₂(9,2) = 16 (4 classes) e K₃(5,2) = 8 ficaram de fora por custo em Python.

## 9. Âncora do Raval como redução do caso equilibrado

A normalização por distância (centro em 000000, antípoda a distância 5 ou 6, terceiro centro de peso
≤ 4 por órbita) dá 38 ramos completos para M ≤ 16, sem o defeito "o mesmo código em 18 instâncias".
Avaliação: cada ramo fixa 3 palavras e nada mais; a fatia fixa 243 variáveis. Como restrição extra
na fatia, os dois lemas do Raval pioraram a 10182 (§7). Como **partição**, a âncora e a fatia usam
elementos de G diferentes e não se compõem sem refazer a normalização; a combinação natural é
"fibra canônica (menor |U|) e, dentro dela, a órbita do par antipodal sob `Stab(K)`" — fase 2, não
implementada. O LP residual dos 38 ramos com barra M = 15 é da frente de contagem.

## Reprodução

    python3 tools/exatos/gaps2/rodar_pb.py --q 3 --n 6 --R 2 --M 15 --listar i15.json   # 21 min
    python3 tools/exatos/k362/orbitas.py --instancias i15.json --duras 7955,9118,10603,11739,11804,11927
    python3 tools/exatos/k362/reducao.py --instancias i15.json --q 3 --n 6 --R 2 --M 15 --saida i15_red.json
    ROUNDINGSAT=... python3 -m pytest -q -p no:cacheprovider tests/test_k362_nucleo.py
