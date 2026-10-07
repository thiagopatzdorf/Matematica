<div align="center">

[English](README.md) · [Português](README.pt-BR.md) · **Français**

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/assets/banner-escuro.png">
  <source media="(prefers-color-scheme: light)" srcset="docs/assets/banner-claro.png">
  <img alt="Matemática : du chaos à la structure, où seul compte ce que la machine vérifie" src="docs/assets/banner-claro.png" width="100%">
</picture>

# Matemática

**Découverte coûteuse, vérification bon marché : des bornes de codes de recouvrement vérifiées par un évaluateur exact et par le noyau de Lean.**

[![ci](https://github.com/thiagopatzdorf/Matematica/actions/workflows/ci.yml/badge.svg)](https://github.com/thiagopatzdorf/Matematica/actions/workflows/ci.yml)
[![verify-codes](https://github.com/thiagopatzdorf/Matematica/actions/workflows/verify-codes.yml/badge.svg)](https://github.com/thiagopatzdorf/Matematica/actions/workflows/verify-codes.yml)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23085769.svg)](https://doi.org/10.5281/zenodo.23085769)
[![Lean 4](https://img.shields.io/badge/Lean-4-0f6db4?logo=lean&logoColor=white)](https://lean-lang.org)
[![Licence : CC BY 4.0](https://img.shields.io/badge/licence-CC%20BY%204.0-lightgrey.svg)](LICENSE)

[Site](https://genesisinnovation.io/matematica) ·
[Résultats](docs/resultados.md) ·
[Philosophie](docs/PHILOSOPHIE.md) ·
[Documentation](docs/README.md) ·
[Note](paper/main.pdf)

</div>

---

## Le problème en une image

Imaginez une ville où chaque maison a une adresse de `n` lettres, et où la distance entre deux maisons est le nombre
de lettres à changer pour passer d'une adresse à l'autre. Une tour atteint toutes les maisons à au plus `R`
changements. **Quel est le plus petit nombre de tours qui couvre toute la ville ?** Ce nombre est `K_q(n,R)`.

Dans le plus petit cas intéressant, les adresses sont les 8 mots de 3 bits et chaque tour atteint un changement.
Deux tours, en `000` et `111`, suffisent : tout autre mot est à un bit de l'une d'elles. Une seule tour ne couvre que
4 maisons, donc `K_2(3,1) = 2`.

```mermaid
graph LR
  T0(("000")):::tour === A["001"] & B["010"] & C["100"]
  T1(("111")):::tour === F["011"] & E["101"] & D["110"]
  A -.- F & E
  B -.- F & D
  C -.- E & D
  classDef tour fill:#0f6db4,color:#fff,stroke:#0f6db4
```

Toute réponse a deux côtés. Une **borne supérieure** montre des tours qui suffisent : les trouver est difficile, mais
vérifier, c'est compter. Une **borne inférieure** prouve qu'un nombre plus petit est impossible, et c'est le côté
difficile, car il faut écarter toutes les alternatives. Expliqué en quatre niveaux (30 secondes, lycée, licence,
recherche) dans [docs/EXPLIQUE.md](docs/EXPLIQUE.md) ; le pourquoi de la méthode, dans
[docs/PHILOSOPHIE.md](docs/PHILOSOPHIE.md).

## I. Définition

Un **code de recouvrement** est un ensemble de mots de longueur `n` sur `q` symboles tel que tout mot de l'espace se
trouve à distance de Hamming au plus `R` de l'un d'eux. `K_q(n,R)` est la taille du plus petit code de ce type :

```math
K_q(n,R) \;=\; \min\bigl\lbrace\,|C| \;:\; C \subseteq \mathbb{Z}_q^n,\ \ \forall x \in \mathbb{Z}_q^n\ \ \exists c \in C,\ \ d_H(x,c) \le R \,\bigr\rbrace
```

Une borne supérieure est un code explicite : le trouver est difficile, le vérifier, c'est compter. La référence est
constituée par les [tables de Kéri](https://old.sztaki.hu/~keri/codes/) ; tout le vocabulaire est dans le
[glossaire](docs/GLOSSARIO.md) (en portugais).

## II. Principes

1. **Seul compte ce que la machine vérifie.** Une preuve est un évaluateur déterministe ou le noyau de Lean. L'avis d'un modèle, ou d'une personne, n'est pas une preuve.
2. **Une vérification bon marché vaut mieux qu'une découverte coûteuse.** La recherche peut être chère et faillible ; ce qui reste dans le dépôt est le certificat qui se vérifie en quelques secondes.
3. **Toute erreur devient une règle.** Un défaut trouvé devient un test qui échoue, pas un pense-bête.
4. **Tout est réversible.** Chaque état se reconstruit à partir du dépôt : codes, certificats, registre et preuves.

Le pourquoi de chacun est dans [docs/PHILOSOPHIE.md](docs/PHILOSOPHIE.md).

## III. Propositions

A machine-checked ledger of covering-code upper bounds, with formally certified exact entries.
Le bloc ci-dessous est généré à partir de `ledger/cells.json` et ne se modifie pas à la main.

<!-- RESULTADOS:INICIO -->
<!-- Généré par tools/site/gerar_resultados.py à partir de ledger/cells.json ; ne pas modifier à la main. -->

> A machine-checked ledger of covering-code upper bounds, with formally certified exact entries.

| quoi | valeur |
|---|---:|
| cellules `K_q(n,R)` dans le registre (q de 2 à 21) | **1145** |
| exactes (borne inférieure = borne supérieure) | **523** |
| ouvertes | **622** |
| bornes supérieures qui sont des théorèmes du noyau de Lean (FORMALIZED + INDEPENDENTLY_REPRODUCED) | **670** sur 1145 (579 + 91) |
| bornes inférieures par état (presque toutes héritées de la littérature) | CLAIMED 1140 · CERTIFICATE_VERIFIED 3 · FORMALIZED 2 |
| valeurs exactes établies ici (l'intervalle publié était ouvert) | **4** (1 avec les deux bornes dans le noyau ; 3 avec la borne inférieure par certificat vérifié hors de Lean) |
| cellules avec un théorème Lean à nous | **110** (12 sous la meilleure borne supérieure publiée que nous avons trouvée) |
| codes explicites dans `data/codes/` | **44** (tous passent le vérificateur C officiel, `tools/verify/check_all.sh`, en CI) ; 38 sont le témoin actuel d'une borne du registre, sha256 vérifié |

Version 0.9.1 · DOI [10.5281/zenodo.23085769](https://doi.org/10.5281/zenodo.23085769) · registre mis à jour le 2026-10-06. Les bornes inférieures ne sont **pas**, en général, dans Lean : seules 2 d'entre elles sont des théorèmes du noyau.

### Faits marquants

Cellules avec un résultat à nous : théorème Lean ou borne inférieure par certificat vérifié. Nouvelles valeurs exactes d'abord ; ensuite, plus grand gain relatif sur la borne supérieure.

| cellule | avant (publié) | maintenant | état inférieur | état supérieur | preuve |
|---|---:|---:|---|---|---|
| `K_7(6,4)` | 13–15 | **= 14** | CERTIFICATE_VERIFIED | INDEPENDENTLY_REPRODUCED | [FIBRAS_GERAL](docs/exatos/FIBRAS_GERAL.md) · `CoveringK764.K_7_6_4_le_14` · [code](data/codes/q7_n6_R4_M14.txt) |
| `K_3(6,2)` | 15–17 | **= 17** | CERTIFICATE_VERIFIED | INDEPENDENTLY_REPRODUCED | [K3_M16](docs/exatos/k362/K3_M16.md) · `CoveringLedger.K3_6_2_le_17` |
| `K_7(5,3)` | 15–17 | **= 17** | CERTIFICATE_VERIFIED | INDEPENDENTLY_REPRODUCED | [FIBRAS_GERAL](docs/exatos/FIBRAS_GERAL.md) · `CoveringK753.K_7_5_3_le_17` · [code](data/codes/q7_n5_R3_M17.txt) |
| `K_7(4,2)` | 17–19 | **= 19** | FORMALIZED | FORMALIZED | [FASE1_B_K742](docs/exatos/FASE1_B_K742.md) · `K742.K_7_4_2_le_19` · `K742.K_7_4_2_eq_19` |
| `K_5(10,4)` | 177–875 | 177–**625** (−28,6 %) | CLAIMED | INDEPENDENTLY_REPRODUCED | `CoveringKernel.K5_10_4_le_625_kernel` · [code](data/codes/q5_n10_R4_M625.txt) |
| `K_7(9,4)` | 264–1475 | 264–**1134** (−23,1 %) | CLAIMED | INDEPENDENTLY_REPRODUCED | `Syn.K7_9_4_le_1134_syn` · [code](data/codes/q7_n9_R4_M1134.txt) |
| `K_7(8,3)` | 471–2337 | 471–**1887** (−19,3 %) | CLAIMED | INDEPENDENTLY_REPRODUCED | `Syn.K7_8_3_le_1887_syn` · [code](data/codes/q7_n8_R3_M1887.txt) |
| `K_7(10,4)` | 1007–6517 | 1007–**5607** (−14,0 %) | CLAIMED | INDEPENDENTLY_REPRODUCED | `Syn.K7_10_4_le_5607_syn` · [code](data/codes/q7_n10_R4_M5607.txt) |
| `K_5(9,5)` | 19–55 | 19–**50** (−9,1 %) | CLAIMED | INDEPENDENTLY_REPRODUCED | `CoveringKernel.K5_9_5_le_50_kernel` · [code](data/codes/q5_n9_R5_M50.txt) |
| `K_5(11,4)` | 546–3125 | 546–**2875** (−8,0 %) | CLAIMED | INDEPENDENTLY_REPRODUCED | `Syn.K5_11_4_le_2875_syn` · [code](data/codes/q5_n11_R4_M2875.txt) |
| `K_4(10,4)` | 62–208 | 62–**192** (−7,7 %) | CLAIMED | INDEPENDENTLY_REPRODUCED | `CoveringKernel.K4_10_4_le_192_kernel` · [code](data/codes/q4_n10_R4_M192.txt) |
| `K_5(10,5)` | 41–175 | 41–**162** (−7,4 %) | CLAIMED | INDEPENDENTLY_REPRODUCED | `Syn.K5_10_5_le_162_syn` · [code](data/codes/q5_n10_R5_M162.txt) |
| `K_5(7,2)` | 236–525 | 236–**500** (−4,8 %) | CLAIMED | INDEPENDENTLY_REPRODUCED | `CoveringKernel.K5_7_2_le_500_kernel` · [code](data/codes/q5_n7_R2_M500.txt) |
| `K_5(9,3)` | 354–1275 | 354–**1250** (−2,0 %) | CLAIMED | INDEPENDENTLY_REPRODUCED | `CoveringKernel.K5_9_3_le_1250_kernel` · [code](data/codes/q5_n9_R3_M1250.txt) |
| `K_5(9,4)` | 64–255 | 64–**250** (−2,0 %) | CLAIMED | INDEPENDENTLY_REPRODUCED | `CoveringKernel.K5_9_4_le_250_kernel` · [code](data/codes/q5_n9_R4_M250.txt) |
| `K_2(6,1)` | = 12 | **= 12** | FORMALIZED | FORMALIZED | `SC.K_2_6_1_eq12` |
| `K_2(12,3)` | 19–28 | 19–28 | CLAIMED | INDEPENDENTLY_REPRODUCED | `CoveringLit.K2_12_3_le_28` · [code](data/codes/q2_n12_R3_M28.txt) |
| `K_2(13,1)` | 607–704 | 607–704 | CLAIMED | INDEPENDENTLY_REPRODUCED | `Syn.K2_13_1_le_704_syn` · [code](data/codes/q2_n13_R1_M704.txt) |
| `K_2(13,3)` | 28–42 | 28–42 | CLAIMED | INDEPENDENTLY_REPRODUCED | `CoveringLit.K2_13_3_le_42` · [code](data/codes/q2_n13_R3_M42.txt) |
| `K_2(14,1)` | 1185–1408 | 1185–1408 | CLAIMED | FORMALIZED | `CoveringLit.K2_14_1_le_1408` |
| `K_2(14,4)` | 16–28 | 16–28 | CLAIMED | INDEPENDENTLY_REPRODUCED | `CoveringLit.K2_14_4_le_28` · [code](data/codes/q2_n14_R4_M28.txt) |
| `K_2(15,2)` | 310–384 | 310–384 | CLAIMED | INDEPENDENTLY_REPRODUCED | `Syn.K2_15_2_le_384_syn` · [code](data/codes/q2_n15_R2_M384.txt) |
| `K_2(15,4)` | 23–32 | 23–32 | CLAIMED | INDEPENDENTLY_REPRODUCED | `CoveringLit.K2_15_4_le_32` · [code](data/codes/q2_n15_R4_M32.txt) |
| `K_2(17,3)` | 187–320 | 187–320 | CLAIMED | INDEPENDENTLY_REPRODUCED | `Syn.K2_17_3_le_320_syn` · [code](data/codes/q2_n17_R3_M320.txt) |
| `K_2(17,5)` | 20–32 | 20–32 | CLAIMED | INDEPENDENTLY_REPRODUCED | `Syn.K2_17_5_le_32_syn` · [code](data/codes/q2_n17_R5_M32.txt) |
| `K_2(18,2)` | 1702–2944 | 1702–2944 | CLAIMED | INDEPENDENTLY_REPRODUCED | `Syn.K2_18_2_le_2944_syn` · [code](data/codes/q2_n18_R2_M2944.txt) |
| `K_2(18,3)` | 316–512 | 316–512 | CLAIMED | INDEPENDENTLY_REPRODUCED | `Syn.K2_18_3_le_512_syn` · [code](data/codes/q2_n18_R3_M512.txt) |
| `K_2(19,4)` | 128–256 | 128–256 | CLAIMED | INDEPENDENTLY_REPRODUCED | `Syn.K2_19_4_le_256_syn` · [code](data/codes/q2_n19_R4_M256.txt) |
| `K_2(19,6)` | 17–32 | 17–32 | CLAIMED | INDEPENDENTLY_REPRODUCED | `Syn.K2_19_6_le_32_syn` · [code](data/codes/q2_n19_R6_M32.txt) |
| `K_2(21,3)` | 1475–3072 | 1475–3072 | CLAIMED | FORMALIZED | `Syn.K2_21_3_le_3072_syn` |
| `K_2(23,4)` | 912–2048 | 912–2048 | CLAIMED | FORMALIZED | `Syn.K2_23_4_le_2048_syn` |
| `K_2(24,5)` | 376–1024 | 376–1024 | CLAIMED | FORMALIZED | `Syn.K2_24_5_le_1024_syn` |
| `K_6(5,2)` | 36–66 | 36–66 | CLAIMED | INDEPENDENTLY_REPRODUCED | `CoveringLit.K6_5_2_le_66` · [code](data/codes/q6_n5_R2_M66.txt) |
| `K_6(6,4)` | = 10 | **= 10** | CLAIMED | INDEPENDENTLY_REPRODUCED | `CoveringLit.K6_6_4_le_10` · [code](data/codes/q6_n6_R4_M10.txt) |
| `K_6(7,4)` | 18–36 | 18–36 | CLAIMED | INDEPENDENTLY_REPRODUCED | `CoveringLit.K6_7_4_le_36` · [code](data/codes/q6_n7_R4_M36.txt) |
| `K_6(10,6)` | 25–72 | 25–72 | CLAIMED | FORMALIZED | `CoveringLit.K6_10_6_le_72` |
| `K_7(5,2)` | 55–97 | 55–97 | CLAIMED | INDEPENDENTLY_REPRODUCED | `CoveringLit.K7_5_2_le_97` · [code](data/codes/q7_n5_R2_M97.txt) |
| `K_7(7,5)` | = 11 | **= 11** | CLAIMED | INDEPENDENTLY_REPRODUCED | `CoveringLit.K7_7_5_le_11` · [code](data/codes/q7_n7_R5_M11.txt) |
| `K_7(9,6)` | 17–37 | 17–37 | CLAIMED | FORMALIZED | `CoveringLit.K7_9_6_le_37` |
| `K_8(5,2)` | 83–128 | 83–128 | CLAIMED | INDEPENDENTLY_REPRODUCED | `CoveringLit.K8_5_2_le_128` · [code](data/codes/q8_n5_R2_M128.txt) |
| `K_8(7,4)` | 37–92 | 37–92 | CLAIMED | INDEPENDENTLY_REPRODUCED | `CoveringLit.K8_7_4_le_92` · [code](data/codes/q8_n7_R4_M92.txt) |
| `K_8(7,5)` | 14–16 | 14–16 | CLAIMED | INDEPENDENTLY_REPRODUCED | `CoveringLit.K8_7_5_le_16` · [code](data/codes/q8_n7_R5_M16.txt) |
| `K_8(8,6)` | = 12 | **= 12** | CLAIMED | FORMALIZED | `CoveringLit.K8_8_6_le_12` |
| `K_8(9,6)` | 22–48 | 22–48 | CLAIMED | FORMALIZED | `CoveringLit.K8_9_6_le_48` |
| `K_9(5,2)` | 113–189 | 113–189 | CLAIMED | INDEPENDENTLY_REPRODUCED | `CoveringLit.K9_5_2_le_189` · [code](data/codes/q9_n5_R2_M189.txt) |
| `K_9(7,4)` | 51–120 | 51–120 | CLAIMED | INDEPENDENTLY_REPRODUCED | `CoveringLit.K9_7_4_le_120` · [code](data/codes/q9_n7_R4_M120.txt) |
| `K_9(7,5)` | 16–21 | 16–21 | CLAIMED | INDEPENDENTLY_REPRODUCED | `CoveringLit.K9_7_5_le_21` · [code](data/codes/q9_n7_R5_M21.txt) |
| `K_9(8,6)` | 15–17 | 15–17 | CLAIMED | FORMALIZED | `CoveringLit.K9_8_6_le_17` |
| `K_9(9,7)` | = 13 | **= 13** | CLAIMED | FORMALIZED | `CoveringLit.K9_9_7_le_13` |
| `K_10(5,2)` | 149–250 | 149–250 | CLAIMED | INDEPENDENTLY_REPRODUCED | `CoveringLit.K10_5_2_le_250` · [code](data/codes/q10_n5_R2_M250.txt) |
| `K_10(7,5)` | 19–26 | 19–26 | CLAIMED | INDEPENDENTLY_REPRODUCED | `CoveringLit.K10_7_5_le_26` · [code](data/codes/q10_n7_R5_M26.txt) |
| `K_10(8,6)` | 17–22 | 17–22 | CLAIMED | FORMALIZED | `CoveringLit.K10_8_6_le_22` |
| `K_10(9,7)` | 16–18 | 16–18 | CLAIMED | FORMALIZED | `CoveringLit.K10_9_7_le_18` |
| `K_10(10,8)` | = 14 | **= 14** | CLAIMED | FORMALIZED | `CoveringLit.K10_10_8_le_14` |
| `K_11(7,5)` | 22–31 | 22–31 | CLAIMED | FORMALIZED | `CoveringLit.K11_7_5_le_31` |
| `K_11(8,6)` | 20–27 | 20–27 | CLAIMED | FORMALIZED | `CoveringLit.K11_8_6_le_27` |
| `K_12(5,2)` | 256–468 | 256–468 | CLAIMED | FORMALIZED | `CoveringLit.K12_5_2_le_468` |
| `K_12(7,5)` | 25–36 | 25–36 | CLAIMED | FORMALIZED | `CoveringLit.K12_7_5_le_36` |
| `K_12(8,6)` | 23–32 | 23–32 | CLAIMED | FORMALIZED | `CoveringLit.K12_8_6_le_32` |
| `K_13(4,2)` | = 57 | **= 57** | CLAIMED | FORMALIZED | `CoveringLit.K13_4_2_le_57` |
| `K_13(7,5)` | 29–42 | 29–42 | CLAIMED | FORMALIZED | `CoveringLit.K13_7_5_le_42` |
| `K_13(8,6)` | 25–37 | 25–37 | CLAIMED | FORMALIZED | `CoveringLit.K13_8_6_le_37` |
| `K_14(4,2)` | = 66 | **= 66** | CLAIMED | FORMALIZED | `CoveringLit.K14_4_2_le_66` |
| `K_14(5,2)` | 381–686 | 381–686 | CLAIMED | FORMALIZED | `CoveringLit.K14_5_2_le_686` |
| `K_14(5,3)` | 50–54 | 50–54 | CLAIMED | FORMALIZED | `CoveringLit.K14_5_3_le_54` |
| `K_14(7,3)` | 1570–4802 | 1570–4802 | CLAIMED | FORMALIZED | `CoveringLit.K14_7_3_le_4802` |
| `K_14(7,5)` | 34–48 | 34–48 | CLAIMED | FORMALIZED | `CoveringLit.K14_7_5_le_48` |
| `K_14(8,6)` | 29–42 | 29–42 | CLAIMED | FORMALIZED | `CoveringLit.K14_8_6_le_42` |
| `K_15(4,2)` | = 75 | **= 75** | CLAIMED | FORMALIZED | `CoveringLit.K15_4_2_le_75` |
| `K_15(5,2)` | 465–855 | 465–855 | CLAIMED | FORMALIZED | `CoveringLit.K15_5_2_le_855` |
| `K_15(5,3)` | 57–59 | 57–59 | CLAIMED | FORMALIZED | `CoveringLit.K15_5_3_le_59` |
| `K_15(7,3)` | 1745–6497 | 1745–6497 | CLAIMED | FORMALIZED | `CoveringLit.K15_7_3_le_6497` |
| `K_15(7,5)` | 39–54 | 39–54 | CLAIMED | FORMALIZED | `CoveringLit.K15_7_5_le_54` |
| `K_15(8,6)` | 33–49 | 33–49 | CLAIMED | FORMALIZED | `CoveringLit.K15_8_6_le_49` |
| `K_16(4,2)` | 86–87 | 86–87 | CLAIMED | FORMALIZED | `CoveringLit.K16_4_2_le_87` |
| `K_16(5,2)` | 576–1024 | 576–1024 | CLAIMED | FORMALIZED | `CoveringLit.K16_5_2_le_1024` |
| `K_16(5,3)` | = 64 | **= 64** | CLAIMED | FORMALIZED | `CoveringLit.K16_5_3_le_64` |
| `K_16(7,3)` | 2226–8192 | 2226–8192 | CLAIMED | FORMALIZED | `CoveringLit.K16_7_3_le_8192` |
| `K_16(7,5)` | 44–60 | 44–60 | CLAIMED | FORMALIZED | `CoveringLit.K16_7_5_le_60` |
| `K_16(8,6)` | 38–56 | 38–56 | CLAIMED | FORMALIZED | `CoveringLit.K16_8_6_le_56` |
| `K_17(4,2)` | 97–99 | 97–99 | CLAIMED | FORMALIZED | `CoveringLit.K17_4_2_le_99` |
| `K_17(5,2)` | 671–1241 | 671–1241 | CLAIMED | FORMALIZED | `CoveringLit.K17_5_2_le_1241` |
| `K_17(5,3)` | = 73 | **= 73** | CLAIMED | FORMALIZED | `CoveringLit.K17_5_3_le_73` |
| `K_17(7,3)` | 2806–10657 | 2806–10657 | CLAIMED | FORMALIZED | `CoveringLit.K17_7_3_le_10657` |
| `K_17(7,5)` | 49–66 | 49–66 | CLAIMED | FORMALIZED | `CoveringLit.K17_7_5_le_66` |
| `K_17(8,6)` | 43–63 | 43–63 | CLAIMED | FORMALIZED | `CoveringLit.K17_8_6_le_63` |
| `K_18(4,2)` | 109–111 | 109–111 | CLAIMED | FORMALIZED | `CoveringLit.K18_4_2_le_111` |
| `K_18(5,2)` | 807–1458 | 807–1458 | CLAIMED | FORMALIZED | `CoveringLit.K18_5_2_le_1458` |
| `K_18(5,3)` | = 82 | **= 82** | CLAIMED | FORMALIZED | `CoveringLit.K18_5_3_le_82` |
| `K_18(6,4)` | 66–80 | 66–80 | CLAIMED | FORMALIZED | `CoveringLit.K18_6_4_le_80` |
| `K_18(7,3)` | 3492–13122 | 3492–13122 | CLAIMED | FORMALIZED | `CoveringLit.K18_7_3_le_13122` |
| `K_18(7,5)` | 55–72 | 55–72 | CLAIMED | FORMALIZED | `CoveringLit.K18_7_5_le_72` |
| `K_18(8,6)` | 48–70 | 48–70 | CLAIMED | FORMALIZED | `CoveringLit.K18_8_6_le_70` |
| `K_19(4,2)` | 121–123 | 121–123 | CLAIMED | FORMALIZED | `CoveringLit.K19_4_2_le_123` |
| `K_19(5,3)` | = 91 | **= 91** | CLAIMED | FORMALIZED | `CoveringLit.K19_5_3_le_91` |
| `K_19(6,4)` | 73–86 | 73–86 | CLAIMED | FORMALIZED | `CoveringLit.K19_6_4_le_86` |
| `K_19(7,3)` | 4282–18737 | 4282–18737 | CLAIMED | FORMALIZED | `CoveringLit.K19_7_3_le_18737` |
| `K_19(7,5)` | 61–81 | 61–81 | CLAIMED | FORMALIZED | `CoveringLit.K19_7_5_le_81` |
| `K_19(8,6)` | 53–77 | 53–77 | CLAIMED | FORMALIZED | `CoveringLit.K19_8_6_le_77` |
| `K_20(4,2)` | 134–135 | 134–135 | CLAIMED | FORMALIZED | `CoveringLit.K20_4_2_le_135` |
| `K_20(5,3)` | = 100 | **= 100** | CLAIMED | FORMALIZED | `CoveringLit.K20_5_3_le_100` |
| `K_20(6,4)` | 81–93 | 81–93 | CLAIMED | FORMALIZED | `CoveringLit.K20_6_4_le_93` |
| `K_20(7,3)` | 5215–21202 | 5215–21202 | CLAIMED | FORMALIZED | `CoveringLit.K20_7_3_le_21202` |
| `K_20(7,5)` | 68–89 | 68–89 | CLAIMED | FORMALIZED | `CoveringLit.K20_7_5_le_89` |
| `K_20(8,6)` | 58–84 | 58–84 | CLAIMED | FORMALIZED | `CoveringLit.K20_8_6_le_84` |
| `K_21(4,2)` | = 147 | **= 147** | CLAIMED | FORMALIZED | `CoveringLit.K21_4_2_le_147` |
| `K_21(5,3)` | 111–114 | 111–114 | CLAIMED | FORMALIZED | `CoveringLit.K21_5_3_le_114` |
| `K_21(6,4)` | 89–99 | 89–99 | CLAIMED | FORMALIZED | `CoveringLit.K21_6_4_le_99` |
| `K_21(7,4)` | 497–1029 | 497–1029 | CLAIMED | FORMALIZED | `CoveringLit.K21_7_4_le_1029` |
| `K_21(7,5)` | 75–98 | 75–98 | CLAIMED | FORMALIZED | `CoveringLit.K21_7_5_le_98` |
| `K_21(8,6)` | 64–91 | 64–91 | CLAIMED | FORMALIZED | `CoveringLit.K21_8_6_le_91` |

Potentiellement nouvelles (introuvables dans la littérature consultée, voir [NOVIDADE_V09](docs/exatos/NOVIDADE_V09.md)) : `K_7(6,4)`, `K_3(6,2)`, `K_7(5,3)`.

Lacunes déclarées : la borne inférieure de `K_7(6,4)`, `K_3(6,2)`, `K_7(5,3)` est un certificat calculatoire vérifié, pas un théorème Lean.
<!-- RESULTADOS:FIM -->

## IV. Démonstration

Chaque borne gravit une échelle d'états, et chaque échelon exige une vérification plus forte que le précédent :

<p align="center">
  <img alt="Échelle d'états : CLAIMED, WITNESS_CHECKED, CERTIFICATE_VERIFIED, FORMALIZED, INDEPENDENTLY_REPRODUCED" src="docs/assets/escada-de-estados.svg" width="90%">
</p>

| état | ce qui a été vérifié |
|---|---|
| `CLAIMED` | figure dans une source publiée ; rien n'a été vérifié ici |
| `WITNESS_CHECKED` | un vérificateur exact, hors de Lean, a accepté le certificat |
| `CERTIFICATE_VERIFIED` | bornes inférieures seulement : certificats LRAT, VeriPB ou Farkas fixés par sha256, vérifiés par un vérificateur indépendant du générateur, avec red team |
| `FORMALIZED` | il existe un théorème Lean, vérifié par le noyau, sans hypothèse en suspens |
| `INDEPENDENTLY_REPRODUCED` | formalisé **et** vérifié par un second vérificateur, effectivement exécuté |

La définition complète de chaque échelon est dans [ledger/README.md](ledger/README.md) ; le décompte par état, dans
[ledger/COBERTURA.md](ledger/COBERTURA.md). Reproduire demande trois commandes (il faut `cc`, Python 3 et
[elan](https://lean-lang.org/install/)) :

```bash
git clone https://github.com/thiagopatzdorf/Matematica && cd Matematica
tools/verify/check_all.sh          # chaque code de data/codes/ dans le vérificateur officiel en C
lake exe cache get && lake build   # les preuves dans le noyau de Lean
```

## V. Méthode

<p align="center">
  <img alt="Effondrement : du chaos de la recherche à la structure du certificat vérifié" src="docs/assets/colapso.svg" width="90%">
</p>

La méthode est un effondrement : de nombreux candidats (recherche, SAT, constructions algébriques, agents) entrent,
un évaluateur exact tranche, et ce qui reste est une structure vérifiable. Le pipeline réel, fichier par fichier, est
dans [docs/ARQUITETURA.md](docs/ARQUITETURA.md) (en portugais) ; la version visuelle, sur
[genesisinnovation.io/matematica](https://genesisinnovation.io/matematica).

## VI. Horizon

Le même principe sous-tend le [théorème de James](https://github.com/thiagopatzdorf/james-theorems), où découvrir
coûte cher et vérifier coûte peu. Les [problèmes du prix du millénaire](https://www.claymath.org/millennium-problems/)
sont l'inspiration à long terme de la méthode, non quelque chose que ce dépôt résout ou attaque.

## VII. Contribuer · Citer · Licence

**Contribuer.** Choisissez une cellule avec `python3 ledger/targets.py --top 10`, ouvrez une issue indiquant celle
que vous attaquez et suivez [CONTRIBUTING.md](CONTRIBUTING.md). Les agents commencent par [AGENTS.md](AGENTS.md) et
le [MCP Infinito](infinito/README.md).

**Citer.** DOI de concept [10.5281/zenodo.23085769](https://doi.org/10.5281/zenodo.23085769), qui pointe toujours
vers la version la plus récente. Les métadonnées sont dans `CITATION.cff`, et GitHub propose le bouton
« Cite this repository ».

**Licence.** [CC BY 4.0](LICENSE). Conduite : [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md). Sécurité : [SECURITY.md](SECURITY.md).
