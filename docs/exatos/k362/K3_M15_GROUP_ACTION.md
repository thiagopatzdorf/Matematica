# K₃(6,2), M = 15: o grupo que age no problema (2026-10-05)

Frente núcleo. Código: `tools/exatos/k362/grupo.py` (ação), `tools/exatos/k362/reducao.py` (lema da soma).
Testes: `tests/test_k362_nucleo.py`. Estados: OBSERVED, COMPUTATIONALLY_VERIFIED, PROVED. Nada aqui é
FORMALIZED (não há Lean).

## 1. O grupo G = S₃ ≀ S₆

Elemento `g = (π, σ₀, …, σ₅)`, com `π ∈ S₆` e `σᵢ ∈ S₃`. Ação em `Z₃⁶`: `(g·c)ᵢ = σᵢ(c_{π(i)})`.
`|G| = 3!⁶ · 6! = 46 656 · 720 = 33 592 320`. É o grupo de automorfismos do grafo de Hamming
H(6,3) (fato clássico; aqui só usamos que G age por isometrias, provado abaixo).

**Lema 1 (PROVED).** `d(g·x, g·y) = d(x, y)` para todo g, x, y.
*Prova.* `(g·x)ᵢ = (g·y)ᵢ ⇔ σᵢ(x_{π(i)}) = σᵢ(y_{π(i)}) ⇔ x_{π(i)} = y_{π(i)}` (σᵢ é bijeção). Como π é
bijeção, o número de i com igualdade é o mesmo. ∎

**Corolário 1 (PROVED).** Para todo código C: `|g·C| = |C|` (g é bijeção de Z₃⁶) e o raio de
cobertura de g·C é o de C (`d(g·x, g·C) = d(x, C)` pelo Lema 1, e x ↦ g·x é sobrejetiva). Logo
"existe código de raio 2 com 15 palavras" é invariante por G.

COMPUTATIONALLY_VERIFIED: `test_toda_transformacao_do_grupo_preserva_distancia_tamanho_e_raio`
(200 elementos aleatórios no código de 17 palavras) e
`test_composicao_e_inverso_do_grupo_agem_como_homomorfismo` (2 000 pares).

## 2. O que uma instância fixa e o subgrupo que a preserva

Instância `(s*, K, t)` de `tools/exatos/gaps2/fatia.py` (ver `docs/exatos/GAPS2_K362.md`):
`F(0,0)` é exatamente `{(0,k) : k ∈ K}`, `|F(0,b)| = t_b` para b = 1, 2, e toda fibra tem ≥ s*.

Seja `H = Stab_G({x : x₀ = 0})`. Um g preserva o hiperplano `{x₀ = 0}` sse π(0) = 0 e σ₀(0) = 0.
Então `H ≅ S₂ × (S₃ ≀ S₅)`, `|H| = 2 · 6⁵ · 120 = 1 866 240`: o S₂ troca os símbolos 1 e 2 da
coordenada 0, e S₃ ≀ S₅ age nas coordenadas 1..5.

**Lema 2 (PROVED).** Um g ∈ H com componente `h ∈ S₃ ≀ S₅` leva as soluções da instância
`(s*, K, t)` às soluções da instância `(s*, h·K, t')`, com `t' = t` se σ₀ = id e `t' = (t₂, t₁)` se
σ₀ = (1 2). Em particular, se `h ∈ Stab(K)` e (σ₀ = id ou t₁ = t₂), g é uma simetria da própria
instância.
*Prova.* Cobertura e tamanho: Corolário 1. Fatia 0: g fixa o hiperplano e age nele por h, então
`F(0,0)` vira `{(0, h·k)}`. Blocos: g leva `F(0,b)` em `F(0,σ₀(b))`. Fibras: g leva `F(j,a)` em
`F(π⁻¹(j), σ_{π⁻¹(j)}(a))` (bijeção entre fibras que preserva tamanhos), então "toda fibra tem ≥ s*"
é preservada. ∎

**Lema 3 (PROVED): as instâncias são órbitas.** Dentro de cada `(s*, t)`, as configurações K da lista
são duas a duas não equivalentes sob S₃ ≀ S₅, e toda classe que passa no filtro aparece. Isso é a
completude/unicidade de `fatia.configuracoes`, provada em `GAPS2_K362.md`. COMPUTATIONALLY_VERIFIED
de forma independente: as 11 000 configurações de s* = 5 têm 11 000 formas distintas no nauty (§4 de
`K3_M15_CANONICAL.md`). **Consequência: sob H, a lista de 12 049 já é exatamente uma por órbita;
N₁ = N₂ = N₃ = 12 049** (ver tabela em `K3_M15_DIAGNOSIS.md`).

## 3. A simetria que H não vê: a escolha da fibra

O normalizador do GAPS2 escolhe *uma* fibra de tamanho s* (a de menor (j,a)). Um elemento de G
fora de H leva a fibra (0,0) para outra fibra. No caso equilibrado (M = 3s*, ou seja s* = 5,
t = (5,5)), **todas as 18 fibras têm 5 palavras** (cada coordenada reparte 15 em três fibras ≥ 5),
então todo código equilibrado satisfaz até 18 instâncias, uma por fibra, a menos de classes repetidas.

OBSERVED: em 300 códigos equilibrados aleatórios (não cobridores), as 18 fibras caem em 18 classes
distintas em 269 casos, 17 em 26 e 16 em 5. O fator de redundância é ~18, não uma cota frouxa.

## 4. Escolha canônica da fibra e o lema da soma

Para uma fibra (j,a) seja `U(j,a) = {x : x_j = a, d(x,c) > 2 ∀ c ∈ F(j,a)}` (para x e c na mesma
fatia, a distância é a das projeções, então `|U(0,0)| = |U(K)|` é a quantidade que o filtro antigo
já calculava).

**Lema 4, lema da soma (PROVED).** Se C cobre Z₃⁶ com raio R e |C| = M (palavras distintas), então
`Σ_{(j,a)} |U(j,a)| ≤ Σ_x d(x,C) ≤ R(3⁶ − M)`.
*Prova.* `Σ_{(j,a)} |U(j,a)| = Σ_x #{j : x ∈ U(j, x_j)}`. Fixe x e uma palavra c mais próxima,
`d(c,x) = d(x,C) ≤ R`. Se `c_j = x_j`, então `c ∈ F(j, x_j)` e cobre x, logo `x ∉ U(j, x_j)`.
Portanto `#{j : x ∈ U(j,x_j)} ≤ #{j : c_j ≠ x_j} = d(x,C)`. Somando: a primeira desigualdade. A
segunda: `d(x,C) = 0` nas M palavras e `≤ R` nos outros 3⁶ − M pontos. ∎

**Corolário 2 (PROVED).** Num código equilibrado de raio 2 com 15 palavras, a fibra de menor |U| tem
`|U| ≤ ⌊2·714/18⌋ = ⌊79,33⌋ = 79`. Normalizando por essa fibra (em vez de "a de menor (j,a)"), as
instâncias equilibradas com `|U(K)| ≥ 80` podem ser descartadas: **todo código de 15 palavras
continua coberto por alguma instância restante** (as não equilibradas não mudam; as equilibradas
caem na instância da sua fibra de menor |U|, que passa no filtro novo, e no filtro antigo
`|U| ≤ 110` porque 79 < 110). COMPUTATIONALLY_VERIFIED: o lema em 9 códigos que cobrem
(`test_lema_da_soma_nao_falha_em_codigo_que_cobre`), a normalização + filtro + OPB em imagens
aleatórias do código de Hamming ternário [4,2,3] e de um código de K₂(6,1) com 12 palavras, e a
reprodução de K₃(4,1) = 9 e K₂(4,1) = 4 pelo pipeline reduzido com RoundingSat.

**Corolário 3 (PROVED), quebra de simetria dentro da instância.** Na mesma normalização, toda fibra
tem `|U(j,a)| ≥ |U(K)|`. `reducao.opb(..., regra="min")` escreve isso com variáveis `w_{x,j}`.
Com a regra oposta (fibra de **maior** |U|), toda fibra tem `|U(j,a)| ≤ |U(K)|` (`regra="max"`), mas
o Corolário 2 não vale. Os dois são válidos; o benchmark (`K3_M15_DIAGNOSIS.md` §7) mostra que, como
restrições extras no PB, **os dois pioram o RoundingSat**.

## 5. O que não é simetria

* Permutar fibras *de coordenadas diferentes* não é uma operação separada: é sempre induzida por um
  elemento de G (π e σ). Não há "N₄" independente além da escolha da fibra (§3).
* Complemento, translação por vetor de Z₃⁶ e multiplicação por escalar já estão em G (são σᵢ).
* Nenhuma simetria fora de G preserva a distância de Hamming em Z₃⁶ (Aut H(6,3) = S₃ ≀ S₆); não há
  simetria escondida a mais para explorar.
