# Fibras com raio R < n − 2: K₄(7,4) e K₃(7,3) (campanha de 2026-10-07)

Continuação de `FIBRAS_GERAL.md` (K₇(5,3) = 17, K₇(6,4) = 14), que só alcançava R = n − 2. Aqui o
codificador de fibras passa a valer para qualquer R ≤ n − 2 e é usado nas duas células da fase 1
da `TRIAGEM_2026-10-04.md` em que o motor sem isomorfos parou (`FASE1_A.md`: árvore 10⁴–10¹¹×
acima do previsto).

## Resultado

| célula | antes | depois | afirmação provada | instâncias | verificação |
|---|---|---|---|---|---|
| **K₄(7,4)** | 9–10 | **10** (ub 10 de Rivas Soriano, publicado) | ∄ código com 9 palavras | 792 perfis: 786 inteiros + 6 em 168 cubos | 792/792 perfis fechados, todo registro UNSAT com `lrat-check` VERIFIED; `fecha_perfis.py --R 4` 792/792; 10/10 CNFs regeneradas batem o sha256; registro em `tools/exatos/fibras/certificados/K4_7_4_M9.jsonl.xz` (manifesto `K4_7_4_M9.sha256`) |
| K₃(7,3) | 11–12 | 11–12 (sem mudança) | parcial: ver "K₃(7,3)" | <!-- K373 --> | idem, por perfil |

Status honesto, igual ao de `FIBRAS_GERAL.md`: resultado **computacional com certificado** (LRAT
conferido por perfil ou por cubo), mais os lemas escritos à mão e testados por máquina. Não está no
Lean e o ledger não foi tocado. A cota superior 10 é da literatura (Rivas Soriano, chave q do
Kéri): este repositório ainda não tem o código de 10 palavras (ver "Cota superior").

Custo de K₄(7,4): 6,8 h de solver e 0,8 h de `lrat-check` somadas nos registros que fecham a célula
(151 GB de LRAT conferidos e descartados), em VMs spot `c2d-highcpu-16` e `t2d-standard-16`.

### Como a rodada saiu (o que não funcionou primeiro)

* **Ordem dos tipos.** Na ordem `min` (coordenada 0 = tipo de menor simetria residual), 772 dos
  792 perfis saíram em segundos, mas 20 passaram de 900 s, e em cubos (`--cubos 9`) o mais duro
  pedia 112 cubos de ~160 s. Na ordem `max` (coordenada 0 = tipo de maior simetria residual, o
  que dá à quebra (h) blocos iguais para ordenar) o mesmo perfil, (3321)²(3222)⁵, saiu inteiro em
  162 s, e 14 dos 20 saíram inteiros em 85–230 s. Os 6 restantes, (3222)⁶·x, foram em 28 cubos cada
  (42–550 s por cubo). Regra: perfil difícil vai primeiro para a ordem `max`, só depois para cubos.
* **Disco.** Em `pd-standard` de 40 GB (~5 MB/s de escrita) as provas LRAT de 16 solvers em
  paralelo encheram o disco e deixaram a CPU em 67 % de espera de E/S. A prova cresce ~5 MB/s por
  processo. O job aceita `TRAB=/dev/shm/...`, e o número de solvers simultâneos tem de caber em
  RAM ÷ (5 MB/s × tempo-limite).
* **K₃(7,3) com prefixo k = 4** (715 instâncias em vez de 11 440): 22 das 25 primeiras passaram de
  200 s. Abandonado; a rodada voltou aos perfis inteiros.


## Lema 2' (cobertura por t-uplas)

**Enunciado.** Seja t = n − R ≥ 2. Para x, c ∈ Z_q^n, d(x, c) ≤ R se e só se existe T ⊂ {0, …, n−1}
com |T| = t e x_T = c_T. Logo C cobre Z_q^n com raio R se e só se, para todo x, existe T com
x_T ∈ P_T(C) = {c_T : c ∈ C}.

**Prova.** d(x, c) ≤ R ⇔ x e c concordam em ≥ n − R = t coordenadas ⇔ algum t-subconjunto das
coordenadas de concordância existe. ∎

A CNF (`fib_encode.codificar(..., R=R)`, função `_cobertura_tuplas`) tem uma variável P[T, v]
para cada t-subconjunto T e cada v ∈ Z_q^t, definida de forma exata: P[T, v] ↔ OR sobre as
palavras w de (AND das t igualdades x_w,i = v_i); com 0 ∈ T as candidatas são só as palavras do
bloco v₀, porque a coordenada 0 já está fixada pelos blocos (quebra (c)). Uma cláusula de largura
C(n, t) por ponto de Z_q^n. Para t = 2 o caminho antigo, por pares, é gerado sem mudança (mesma
numeração; os sha256 das CNFs certificadas de K₇(5,3) e K₇(6,4) continuam iguais).

O Lema 1 (fibras) já valia para R ≤ n − 2, e os Lemas 3 e 4 (quebras (a)–(h)) só usam isometrias
e reordenação das palavras: não dependem de R. Então a redução por perfis vale igual.

| célula | M | subcélulas do Lema 1 (lb) | s_min | tipos | perfis |
|---|---|---|---|---|---|
| K₄(7,4) 9–10 | 9 | K₄(6,3) ≥ 11 > 9; K₃(6,3) = 6 ≤ 8 | 1 | 6 | 792 |
| K₃(7,3) 11–12 | 11 | K₃(6,2) ≥ 15 > 11; K₂(6,2) = 4 ≤ 10 | 1 | 10 | 11 440 |

## Validação em valores conhecidos (R < n − 2)

| caso | esperado | saiu |
|---|---|---|
| K₃(6,3) = 6: ∄ 5 (t = 3) | todos UNSAT | 7/7 UNSAT, 7/7 `lrat-check` VERIFIED |
| K₃(6,3): existe 6 | algum SAT | 8 SAT, os 8 códigos cobrem Z₃⁶ |
| K₃(5,2) = 8: ∄ 7 (t = 3) | todos UNSAT | 56/56 UNSAT, 56/56 VERIFIED |
| K₃(5,2): existe 8 | algum SAT | 1 SAT que cobre |
| codificação independente (`fibras_redteam/indep_raio.py`), K₃(5,2) | ∄ 7, existe 8 | 56/56 UNSAT (kissat), o perfil SAT do caminho principal é SAT aqui também |

Testes (`tests/test_fibras_raio_geral.py`): completude da forma normal com R < n − 2 em 8 casos
(q, n, R, k), uma cláusula violada por ponto descoberto, R = n − 2 explícito igual ao padrão,
s_min e número de perfis dos alvos, e `fecha_perfis` não conta registro de outro raio.
