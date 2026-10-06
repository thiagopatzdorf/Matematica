<div align="center">

[English](README.md) · **Português** · [Français](README.fr.md)

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/assets/banner-escuro.png">
  <source media="(prefers-color-scheme: light)" srcset="docs/assets/banner-claro.png">
  <img alt="Matemática: do caos à estrutura, onde só conta o que a máquina confere" src="docs/assets/banner-claro.png" width="100%">
</picture>

# Matemática

**Descoberta cara, verificação barata: cotas de códigos de cobertura que um avaliador exato e o kernel do Lean conferem.**

[![ci](https://github.com/thiagopatzdorf/Matematica/actions/workflows/ci.yml/badge.svg)](https://github.com/thiagopatzdorf/Matematica/actions/workflows/ci.yml)
[![verify-codes](https://github.com/thiagopatzdorf/Matematica/actions/workflows/verify-codes.yml/badge.svg)](https://github.com/thiagopatzdorf/Matematica/actions/workflows/verify-codes.yml)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23085769.svg)](https://doi.org/10.5281/zenodo.23085769)
[![Lean 4](https://img.shields.io/badge/Lean-4-0f6db4?logo=lean&logoColor=white)](https://lean-lang.org)
[![Licença: CC BY 4.0](https://img.shields.io/badge/licen%C3%A7a-CC%20BY%204.0-lightgrey.svg)](LICENSE)

[Página](https://genesisinnovation.io/matematica) ·
[Resultados](docs/resultados.md) ·
[Filosofia](docs/FILOSOFIA.md) ·
[Documentação](docs/README.md) ·
[Nota](paper/main.pdf)

</div>

---

## O problema em uma imagem

Imagine uma cidade onde cada casa tem um endereço de `n` letras, e a distância entre duas casas é quantas letras
é preciso trocar para ir de um endereço ao outro. Uma torre alcança todas as casas a até `R` trocas. **Qual é o
menor número de torres que cobre a cidade inteira?** Esse número é `K_q(n,R)`.

No menor exemplo interessante, os endereços são as 8 palavras de 3 bits e cada torre alcança uma troca. Duas
torres, em `000` e `111`, bastam: toda outra palavra está a um bit de uma delas. Uma torre só cobre 4 casas, então
`K_2(3,1) = 2`.

```mermaid
graph LR
  T0(("000")):::torre === A["001"] & B["010"] & C["100"]
  T1(("111")):::torre === F["011"] & E["101"] & D["110"]
  A -.- F & E
  B -.- F & D
  C -.- E & D
  classDef torre fill:#0f6db4,color:#fff,stroke:#0f6db4
```

Toda resposta tem dois lados. A **cota superior** é mostrar torres que bastam: achar é difícil, mas conferir é só
contar. A **cota inferior** é provar que menos torres é impossível, e esse é o lado difícil, porque é preciso
descartar todas as alternativas. Explicado em quatro camadas (30 segundos, ensino médio, graduação, pesquisa) em
[docs/EXPLICANDO.md](docs/EXPLICANDO.md); o porquê do método, em [docs/FILOSOFIA.md](docs/FILOSOFIA.md).

## I. Definição

Um **código de cobertura** é um conjunto de palavras de comprimento `n` sobre `q` símbolos tal que toda palavra do
espaço fica a distância de Hamming no máximo `R` de alguma delas. `K_q(n,R)` é o tamanho do menor código assim:

$$K_q(n,R) \;=\; \min\bigl\{\,|C| \;:\; C \subseteq \mathbb{Z}_q^n,\ \ \forall x \in \mathbb{Z}_q^n\ \ \exists c \in C,\ \ d_H(x,c) \le R \,\bigr\}$$

Uma cota superior é um código explícito: achar é difícil, conferir é contar. A referência são as
[tabelas do Kéri](https://old.sztaki.hu/~keri/codes/); o vocabulário inteiro está no [glossário](docs/GLOSSARIO.md).

## II. Princípios

1. **Só conta o que a máquina confere.** Prova é um avaliador determinístico ou o kernel do Lean. Opinião de modelo, ou de gente, não é prova.
2. **Verificação barata vale mais que descoberta cara.** A busca pode ser cara e falível; o que fica no repositório é o certificado que se confere em segundos.
3. **Todo erro vira regra.** Um defeito achado vira teste que falha, não lembrete.
4. **Tudo é reversível.** Cada estado é reconstruível a partir do repositório: códigos, certificados, ledger e provas.

O porquê de cada um está em [docs/FILOSOFIA.md](docs/FILOSOFIA.md).

## III. Proposições

A machine-checked ledger of covering-code upper bounds, with formally certified exact entries.
O bloco abaixo é gerado a partir de `ledger/cells.json` e não se edita à mão.

<!-- RESULTADOS:INICIO -->
<!-- Gerado por tools/site/gerar_resultados.py a partir de ledger/cells.json; não edite à mão. -->

> A machine-checked ledger of covering-code upper bounds, with formally certified exact entries.

| o quê | valor |
|---|---:|
| células `K_q(n,R)` no ledger (q de 2 a 21) | **1145** |
| exatas (cota inferior = superior) | **523** |
| abertas | **622** |
| cotas superiores que são teorema do kernel do Lean (FORMALIZED + INDEPENDENTLY_REPRODUCED) | **542** de 1145 (478 + 64) |
| cotas inferiores por estado (quase todas herdadas da literatura) | CLAIMED 1140 · CERTIFICATE_VERIFIED 3 · FORMALIZED 2 |
| exatas fechadas aqui (o intervalo publicado estava aberto) | **4** (1 com as duas cotas no kernel; 3 com a inferior por certificado verificado fora do Lean) |
| células com teorema Lean próprio | **15** (12 abaixo da melhor cota superior publicada que achamos) |
| códigos explícitos em `data/codes/` | **19** (todos passam no verificador C oficial, `tools/verify/check_all.sh`, no CI); 13 são a testemunha atual de uma cota do ledger, sha256 conferido |

Versão 0.9.1 · DOI [10.5281/zenodo.23085769](https://doi.org/10.5281/zenodo.23085769) · ledger atualizado em 2026-10-06. As cotas inferiores **não** estão, em geral, no Lean: só 2 delas são teorema do kernel.

### Destaques

Células com resultado próprio: teorema Lean nosso ou cota inferior por certificado verificado. Exatas novas primeiro; depois, maior ganho relativo na cota superior.

| célula | antes (publicado) | agora | estado inferior | estado superior | prova |
|---|---:|---:|---|---|---|
| `K_7(6,4)` | 13–15 | **= 14** | CERTIFICATE_VERIFIED | INDEPENDENTLY_REPRODUCED | [FIBRAS_GERAL](docs/exatos/FIBRAS_GERAL.md) · `CoveringK764.K_7_6_4_le_14` · [código](data/codes/q7_n6_R4_M14.txt) |
| `K_3(6,2)` | 15–17 | **= 17** | CERTIFICATE_VERIFIED | INDEPENDENTLY_REPRODUCED | [K3_M16](docs/exatos/k362/K3_M16.md) · `CoveringLedger.K3_6_2_le_17` |
| `K_7(5,3)` | 15–17 | **= 17** | CERTIFICATE_VERIFIED | INDEPENDENTLY_REPRODUCED | [FIBRAS_GERAL](docs/exatos/FIBRAS_GERAL.md) · `CoveringK753.K_7_5_3_le_17` · [código](data/codes/q7_n5_R3_M17.txt) |
| `K_7(4,2)` | 17–19 | **= 19** | FORMALIZED | FORMALIZED | [FASE1_B_K742](docs/exatos/FASE1_B_K742.md) · `K742.K_7_4_2_le_19` · `K742.K_7_4_2_eq_19` |
| `K_5(10,4)` | 177–875 | 177–**625** (−28,6 %) | CLAIMED | INDEPENDENTLY_REPRODUCED | `CoveringKernel.K5_10_4_le_625_kernel` · [código](data/codes/q5_n10_R4_M625.txt) |
| `K_7(9,4)` | 264–1475 | 264–**1134** (−23,1 %) | CLAIMED | INDEPENDENTLY_REPRODUCED | `Syn.K7_9_4_le_1134_syn` · [código](data/codes/q7_n9_R4_M1134.txt) |
| `K_7(8,3)` | 471–2337 | 471–**1887** (−19,3 %) | CLAIMED | INDEPENDENTLY_REPRODUCED | `Syn.K7_8_3_le_1887_syn` · [código](data/codes/q7_n8_R3_M1887.txt) |
| `K_7(10,4)` | 1007–6517 | 1007–**5607** (−14,0 %) | CLAIMED | INDEPENDENTLY_REPRODUCED | `Syn.K7_10_4_le_5607_syn` · [código](data/codes/q7_n10_R4_M5607.txt) |
| `K_5(9,5)` | 19–55 | 19–**50** (−9,1 %) | CLAIMED | INDEPENDENTLY_REPRODUCED | `CoveringKernel.K5_9_5_le_50_kernel` · [código](data/codes/q5_n9_R5_M50.txt) |
| `K_5(11,4)` | 546–3125 | 546–**2875** (−8,0 %) | CLAIMED | INDEPENDENTLY_REPRODUCED | `Syn.K5_11_4_le_2875_syn` · [código](data/codes/q5_n11_R4_M2875.txt) |
| `K_4(10,4)` | 62–208 | 62–**192** (−7,7 %) | CLAIMED | INDEPENDENTLY_REPRODUCED | `CoveringKernel.K4_10_4_le_192_kernel` · [código](data/codes/q4_n10_R4_M192.txt) |
| `K_5(10,5)` | 41–175 | 41–**162** (−7,4 %) | CLAIMED | INDEPENDENTLY_REPRODUCED | `Syn.K5_10_5_le_162_syn` · [código](data/codes/q5_n10_R5_M162.txt) |
| `K_5(7,2)` | 236–525 | 236–**500** (−4,8 %) | CLAIMED | INDEPENDENTLY_REPRODUCED | `CoveringKernel.K5_7_2_le_500_kernel` · [código](data/codes/q5_n7_R2_M500.txt) |
| `K_5(9,3)` | 354–1275 | 354–**1250** (−2,0 %) | CLAIMED | INDEPENDENTLY_REPRODUCED | `CoveringKernel.K5_9_3_le_1250_kernel` · [código](data/codes/q5_n9_R3_M1250.txt) |
| `K_5(9,4)` | 64–255 | 64–**250** (−2,0 %) | CLAIMED | INDEPENDENTLY_REPRODUCED | `CoveringKernel.K5_9_4_le_250_kernel` · [código](data/codes/q5_n9_R4_M250.txt) |
| `K_2(6,1)` | = 12 | **= 12** | FORMALIZED | FORMALIZED | `SC.K_2_6_1_eq12` |

Potencialmente novas (não encontradas na literatura que pesquisamos, ver [NOVIDADE_V09](docs/exatos/NOVIDADE_V09.md)): `K_7(6,4)`, `K_3(6,2)`, `K_7(5,3)`.

Lacunas declaradas: a cota inferior de `K_7(6,4)`, `K_3(6,2)`, `K_7(5,3)` é certificado computacional verificado, não teorema do Lean.
<!-- RESULTADOS:FIM -->

## IV. Demonstração

Toda cota sobe uma escada de estados, e cada degrau exige uma conferência mais forte que o anterior:

<p align="center">
  <img alt="Escada de estados: CLAIMED, WITNESS_CHECKED, CERTIFICATE_VERIFIED, FORMALIZED, INDEPENDENTLY_REPRODUCED" src="docs/assets/escada-de-estados.svg" width="90%">
</p>

| estado | o que foi conferido |
|---|---|
| `CLAIMED` | está numa fonte publicada; nada foi conferido aqui |
| `WITNESS_CHECKED` | um verificador exato, fora do Lean, aceitou o certificado |
| `CERTIFICATE_VERIFIED` | só cota inferior: certificados LRAT, VeriPB ou Farkas fixados por sha256, conferidos por verificador independente do gerador e com red team |
| `FORMALIZED` | há teorema do Lean, checado pelo kernel, sem hipótese pendente |
| `INDEPENDENTLY_REPRODUCED` | formalizado **e** conferido por um segundo verificador, executado |

A definição completa de cada degrau está em [ledger/README.md](ledger/README.md); a contagem por estado, em
[ledger/COBERTURA.md](ledger/COBERTURA.md). Para reproduzir, bastam três comandos (precisa de `cc`, Python 3 e
[elan](https://lean-lang.org/install/)):

```bash
git clone https://github.com/thiagopatzdorf/Matematica && cd Matematica
tools/verify/check_all.sh          # todo código de data/codes/ no verificador oficial em C
lake exe cache get && lake build   # as provas no kernel do Lean
```

## V. Método

<p align="center">
  <img alt="Colapso: do caos da busca à estrutura do certificado verificado" src="docs/assets/colapso.svg" width="90%">
</p>

O método é um colapso: muitos candidatos (busca, SAT, construções algébricas, agentes) entram, um avaliador exato
decide, e o que sobra é estrutura conferível. O fluxo real, arquivo por arquivo, está em
[docs/ARQUITETURA.md](docs/ARQUITETURA.md); a versão visual, em
[genesisinnovation.io/matematica](https://genesisinnovation.io/matematica).

## VI. Horizonte

O mesmo princípio sustenta o [teorema do James](https://github.com/thiagopatzdorf/james-theorems), em que descobrir
é caro e verificar é barato. Os [Problemas do Milênio](https://www.claymath.org/millennium-problems/) são a inspiração
de longo prazo do método, não algo que este repositório resolva ou ataque.

## VII. Contribua · Cite · Licença

**Contribua.** Escolha uma célula com `python3 ledger/targets.py --top 10`, abra uma issue dizendo qual você ataca e
siga o [CONTRIBUTING.md](CONTRIBUTING.md). Agentes começam pelo [AGENTS.md](AGENTS.md) e pelo
[MCP Infinito](infinito/README.md).

**Cite.** DOI conceitual [10.5281/zenodo.23085769](https://doi.org/10.5281/zenodo.23085769), que aponta sempre para
a versão mais nova. Os metadados estão em `CITATION.cff`, e o GitHub oferece o botão "Cite this repository".

**Licença.** [CC BY 4.0](LICENSE). Conduta: [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md). Segurança: [SECURITY.md](SECURITY.md).
