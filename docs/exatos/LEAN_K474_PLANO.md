# K₄(7,4) ≥ 10 e K₄(6,3) ≥ 12 no Lean: o que falta e quanto custa (medido em 2026-10-07)

Estado: as duas cotas estão no ledger como `CERTIFICATE_VERIFIED` (LRAT conferido fora do Lean,
`FIBRAS_RAIO_GERAL.md`). Este documento mede o que falta para o Lean as aceitar, sem formalizar
nada ainda. Nenhuma VM foi usada; tudo rodou em 4 núcleos locais (US$ 0).

## Veredito curto

* **Não é "só rodar".** O precedente (K₇(4,2) = 19, `LEAN_K742.md`) mostra o custo do kernel,
  mas só valia porque a ponte código → CNF foi feita **sem** as quebras de simetria (d)–(h).
  Aqui isso **não transfere**: medido abaixo, sem (d)–(h) a prova de K₄(7,4) cresce de 10× a 34× ou mais.
  Então a ponte do Lean precisa formalizar a forma normal (d)–(h), ou o custo sai da faixa.
* **A dependência CLAIMED some barato.** O Lema 1 de K₄(6,3) com M = 11 exige K₄(5,2) > 11, e não
  o 16 da literatura. K₄(5,2) ≥ 12 está agora fechado por computador: 3003 perfis, todos UNSAT com
  `lrat-check` VERIFIED, 0,8 GB de LRAT, 2,5 min em 2 núcleos
  (`tools/exatos/fibras/certificados/K4_5_2_M11.jsonl.xz`). Sem isso a cadeia do Lean
  K₄(5,2) → K₄(6,3) → K₄(7,4) tinha um elo que o ledger só marca `CLAIMED`.
* **Custo do kernel (extrapolado, não medido).** Acima de US$ 50 com certeza para o par: faixa
  ≈ US$ 45–50 para K₄(7,4) e ≈ US$ 115–130 para K₄(6,3), mais ~20 h e ~55 h de parede com ≤ 90 vCPU.
  **Não gasto nada disso sem o "pode" do dono.** O piloto de K₄(5,2) ≥ 12 custa ≈ US$ 0,25.

## 1. A cadeia que o Lean teria de provar

1. K₄(5,2) ≥ 12 (3003 perfis; `K4_5_2_M11`) — e os lemas abaixo para q = 4, R = 2.
2. K₄(6,3) ≥ 12: Lema 1 (fibra vazia exige K₄(5,2) ≤ 11, falso por 1; fibra com s palavras exige
   K₄₋ₛ(5,2) ≤ 11 − s, só limites superiores de K₃, K₂, K₁) + Lema 2′ (cobertura por triplas) +
   quebras + 8008 perfis (402 GB de LRAT).
3. K₄(7,4) ≥ 10: o mesmo com K₄(6,3) > 9 (agora vem do passo 2) + 792 perfis (151 GB de LRAT).
4. Cota superior de K₄(7,4) = 10: testemunha `data/codes/q4_n7_R4_M10.txt` (cobertura por
   `decide +kernel` em 4⁷ = 16 384 pontos: cabe, como o código de 19 palavras de K₇(4,2)).

Do que o `K742` já deixou pronto e é genérico: o verificador `LratK`, `lratk_refute`/`lratk_final_seg`
e o esquema Data/B/Final. O que é específico de q = 7, n = 4 e **precisa ser refeito**: Lema 0/1 para
q = 4 e R < n − 2, a CNF (`cnfSemQuebra` ↔ `fib_encode.codificar`), a ponte código → CNF.

## 2. Medidas

### 2.1 Tamanho da prova no kernel (por dica)

`lrat-trim` b30f400 numa prova de K₄(7,4) M = 9 (perfil 64, com quebras): 27,5 MB de LRAT → 7,5 MB aparados,
**2 064 304 dicas** → **0,075 dica por byte de LRAT original**. No K₇(4,2): 205 M dicas para 3,00 GB →
0,068. Usei a faixa 0,068–0,075. Custo do kernel no K₇(4,2): 0,58 ms de CPU por dica, ≈ US$ 0,026 por
CPU-h de VM spot (US$ 1,0 por 37,8 CPU-h, disco incluído).

| alvo | LRAT conferido e descartado | dicas (faixa) | CPU-h do kernel (0,58 ms/dica) | US$ (≈ 0,026/CPU-h) |
|---|---|---|---|---|
| K₄(5,2) ≥ 12 (piloto) | 0,8 GB | 54–60 M | 8,7–9,7 | ≈ 0,25 |
| K₄(7,4) ≥ 10 | 151 GB | 10,3–11,3 G | 1 660–1 820 | ≈ 43–47 |
| K₄(6,3) ≥ 12 | 402 GB | 27–30 G | 4 400–4 850 | ≈ 115–126 |

Ressalvas honestas: (a) o LRAT de 151/402 GB é o que o `lrat-check` leu (sem aparo); a razão
dicas/byte vem de **uma** prova de K₄ e de K₇(4,2), não das 8800 provas; (b) o custo por dica foi medido
em perfis de 5–40 M dicas, e as maiores provas daqui chegam a ~3 GB (≈ 200 M dicas num perfil só): o
esquema Data/B/Final divide, mas a memória do `Data` (9 GB no pior perfil do K₇(4,2)) precisa ser
medida; (c) com a cota global de 96 vCPU do projeto, K₄(7,4) leva ~21 h e K₄(6,3) ~55 h de parede.

### 2.2 Sem as quebras (d)–(h) a prova não cabe

Mesma CNF de K₄(7,4) M = 9, ordem `max`, CaDiCaL 3.0.1 `c607304`, `--lrat`, com `quebra=True` e com
`quebra=False` (só (a)–(c), o que o K₇(4,2) usou):

| perfil | com (d)–(h) | sem (d)–(h) | razão do LRAT |
|---|---|---|---|
| 331 | 1,9 s, 11 MB | 28,1 s, 152 MB | 14× |
| 154 | 2,2 s, 9 MB | 28,6 s, 152 MB | 17× |
| 404 | 3,8 s, 18 MB | 22,7 s, 128 MB | 7× |
| 64 (um dos mais simétricos) | UNSAT, 27 MB | **não fechou**: > 940 MB em ~3 min quando o processo foi cortado | > 34× |

n = 4 perfis. No K₇(4,2) a mesma troca custou +11 % de dicas depois do aparo; aqui a quebra pesa uma
ordem de grandeza ou mais. Extrapolando sem mais medida: 1,5–5 TB de LRAT só em K₄(7,4), ou seja, de
centenas a milhares de US$ no kernel. **Decisão que não é minha** (afeta custo e esforço): formalizar
(d)–(h) no Lean (o `K742` evitou isso de propósito; `canonizar.py`/`fib_canon.py` são o ponto de
partida e `REDTEAM_K764.md` corrige a prova de (h)), ou desistir do Lean para estas duas células.

### 2.3 Erro → regra

Compilei o CaDiCaL com `./configure -q` ("quiet"), que **remove** a opção `-q` do binário. O
`rodar.py` chama `cadical -q …`, o solver sai com código 1 em 3 ms e o `rodar.py` grava
`INDEFINIDO` para **todos** os perfis sem dizer por quê. Quem reproduzir os certificados deve compilar com
`./configure && make` (como em `pesado/jobs/_fibras_comum.sh`). Pendente (issue, não neste PR): fazer o
`rodar.py` falhar alto quando `rc` ∉ {10, 20} nos primeiros perfis.

## 3. Plano proposto (nada disto foi feito além do 2)

1. **Piloto barato (≈ US$ 0,25).** K₄(5,2) ≥ 12 no Lean: Lema 0/1 para q = 4, R = 2, forma normal com
   (d)–(h) formalizada, 3003 perfis pelo esquema Data/B/Final. Prova se a ponte com quebras funciona antes
   de gastar nos grandes.
2. **K₄(7,4) ≥ 10** (≈ US$ 45–50) só depois de 1 passar e com o "pode" do dono.
3. **K₄(6,3) ≥ 12** (≈ US$ 115–130) idem, e só se 2 passou.
4. Zenodo: só quando o Lean aceitar 2 (e 3 para o ≥ 12); o dono dá o "publica".

## 4. O que NÃO foi feito

* Nenhuma linha de Lean escrita neste PR; nenhuma VM; nada publicado.
* O ledger não muda: K₄(5,2) já tem lb 16 `CLAIMED` (Kéri); o ≥ 12 computacional entra só como
  registro de certificados.
