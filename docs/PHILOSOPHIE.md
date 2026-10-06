<div align="center">

[Português](FILOSOFIA.md) · [English](PHILOSOPHY.md) · **Français**

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/filosofia-escuro.png">
  <source media="(prefers-color-scheme: light)" srcset="assets/filosofia-claro.png">
  <img alt="Ordo ex chao : des mots épars arrivent de la gauche et se posent, station après station, dans les quatre causes : matérielle, formelle, efficiente, finale" src="assets/filosofia-claro.png" width="100%">
</picture>

# Philosophie

**Du chaos à l’ordre : ce que nous faisons, pourquoi, et selon quelle règle nous décidons de ce qui est vrai.**

</div>

> *« INSUFFICIENT DATA FOR MEANINGFUL ANSWER. »*
>
> — Isaac Asimov, *La Dernière Question*[^asimov]

Ce texte suit l’ordre d’Aristote[^aristoteles].
Définitions, principes, propositions, méthode, causes.

Chaque affirmation factuelle renvoie au fichier qui la soutient.
Ce qui ne renvoie à rien est conviction, et écrit comme tel.

<p align="center">
<a href="#i-définitions">Définitions</a> ·
<a href="#ii-principes">Principes</a> ·
<a href="#iii-propositions">Propositions</a> ·
<a href="#iv-méthode">Méthode</a> ·
<a href="#v-les-quatre-causes">Quatre causes</a> ·
<a href="#vi-le-théorème-de-james">James</a> ·
<a href="#vii-ce-qui-nous-échappe-encore">Horizon</a> ·
<a href="#viii-lacunes-déclarées">Lacunes</a>
</p>

---

## I. Définitions

**1. Cellule.** Un nombre `K_q(n,R)` : le plus petit code de longueur `n`, sur `q` symboles, qui laisse
chaque mot à distance de Hamming au plus `R` d’un mot du code
([article, Introduction](../paper/main.tex)).

```math
K_q(n,R) \;=\; \min\bigl\lbrace\,|C| \;:\; C \subseteq \mathbb{Z}_q^n,\ \ \forall x \in \mathbb{Z}_q^n\ \ \exists c \in C,\ \ d_H(x,c) \le R \,\bigr\rbrace
```

Les tables de Kéri comptent 1145 cellules, avec `q` de 2 à 21 ([registre](../ledger/README.md)).

**2. Borne.** Un intervalle.

```math
\text{inférieure} \;\le\; K_q(n,R) \;\le\; \text{supérieure}
```

La borne supérieure se prouve en montrant un code.
L’inférieure, en prouvant qu’aucun code plus petit n’existe.

**3. Entropie locale.** Le doute qui reste sur une cellule.
L’écart entre ses deux bornes, et l’incertitude sur chacune.
Locale, parce qu’elle appartient à un problème, non à l’univers.

**4. Effondrement de l’état.** L’instant où l’intervalle devient un point.
Avant, beaucoup de réponses possibles. Après, une seule.

**5. État de certification.** Le degré de confiance dans chaque borne, sur une échelle qui ne fait que
monter : `CLAIMED`, `WITNESS_CHECKED`, `CERTIFICATE_VERIFIED` (bornes inférieures seulement),
`FORMALIZED`, `INDEPENDENTLY_REPRODUCED` ([registre, Certificação](../ledger/README.md)).

---

## II. Principes

> Celui qui propose peut se tromper à loisir. Celui qui tranche doit être bon marché et exact.

**1. Vérifier coûte moins que trouver.**
Trouver un code, c’est chercher dans un espace immense. Vérifier un code donné, c’est un calcul fini.
C’est l’asymétrie que formalise la question P vs NP.
Pour nous, c’est une boussole d’ingénieur, pas un théorème.

**2. La découverte coûteuse devient vérification bon marché.**
Une recherche qui aboutit laisse un certificat : un code explicite, une réfutation LRAT, des
multiplicateurs de Farkas entiers, un théorème du noyau ([article, Introduction](../paper/main.tex)).
Qui vient ensuite ne refait pas la recherche. Il vérifie.

**3. L’évaluateur tranche.**
Le cœur de ce dépôt n’est pas le solveur. C’est le vérificateur :
[`tools/verify/verify.c`](../tools/verify/verify.c) et le noyau de Lean.

**4. Le mesuré l’emporte sur le lu.**
Une borne de la littérature entre comme `CLAIMED`. Elle ne monte que si quelque chose ici la vérifie.
L’état est calculé par un script, jamais écrit à la main ([`ledger/build.py`](../ledger/build.py)).

**5. L’erreur est une mesure, non une dette.**
Là où une preuve casse, une règle manquait.
C’est pourquoi nous publions ce qui a échoué ([article, « Where the same methods stop »](../paper/main.tex)).
C’est pourquoi chaque nouvelle borne inférieure affronte une red team avant d’entrer
([K₇(5,3)](exatos/REDTEAM_K753.md), [K₇(6,4)](exatos/REDTEAM_K764.md),
[K₃(6,2)](exatos/k362/K3_M16_REDTEAM.md)).

**6. Ne jamais dire plus que ce qui est prouvé.**
La phrase du registre est fixe :

> *A machine-checked ledger of covering-code upper bounds, with formally certified exact entries.*

La table entière n’a pas été vérifiée formellement.
Les bornes inférieures sont, presque toutes, héritées de la littérature
([couverture](../ledger/COBERTURA.md)).

---

## III. Propositions

<p align="center">
  <img alt="Échelle des états : CLAIMED, WITNESS_CHECKED, CERTIFICATE_VERIFIED, FORMALIZED, INDEPENDENTLY_REPRODUCED" src="assets/escada-de-estados.svg" width="90%">
</p>

| proposition | preuve |
|---|---|
| **488 des 1145 bornes supérieures** sont `FORMALIZED` ou `INDEPENDENTLY_REPRODUCED`. Parmi les inférieures, 3 sont `CERTIFICATE_VERIFIED` et 2 `FORMALIZED`. | [`ledger/COBERTURA.md`](../ledger/COBERTURA.md) |
| **Deux cellules exactes avec les deux bornes dans le noyau :** `K₂(6,1) = 12` et `K₇(4,2) = 19`. | [article, « A certified ledger »](../paper/main.tex) · [LEAN_K742](exatos/LEAN_K742.md) |
| **Trois effondrements potentiellement nouveaux**, non trouvés dans la littérature consultée : `K₃(6,2) = 17`, `K₇(6,4) = 14`, `K₇(5,3) = 17`. Les trois bornes inférieures sont `CERTIFICATE_VERIFIED`, pas des théorèmes du noyau. | [NOVIDADE_V09](exatos/NOVIDADE_V09.md) · [registre](../ledger/README.md) |

---

## IV. Méthode

<p align="center">
  <img alt="Effondrement : du chaos de la recherche à la structure d’un certificat vérifié" src="assets/colapso.svg" width="90%">
</p>

> Le cycle ne se termine que lorsque quelque chose a changé d’état et a été vérifié.

1. **Choisir** une cellule selon le doute qu’elle garde.
2. **Chercher.** La partie coûteuse : constructions, SAT, programmation linéaire, red team.
3. **Certifier.** Réduire la découverte à un objet qu’un vérificateur exact contrôle.
4. **Enregistrer** dans le registre, avec source, sha256 et état calculé ([`ledger/cells.json`](../ledger/cells.json)).
5. **Exposer.** Article, DOI, lacunes déclarées. Pour qu’un autre refasse sans avoir à nous croire.

Le registre est la mémoire.<br>
Qui arrive demain ne refait pas la recherche.<br>
Il lit l’état, et vérifie le certificat.

---

## V. Les quatre causes

<p align="center">
  <img alt="Les quatre causes d’Aristote appliquées à ce dépôt : matérielle, formelle, efficiente, finale" src="assets/quatro-causas.svg" width="90%">
</p>

| cause | la question d’Aristote | ici |
|---|---|---|
| **Matérielle** | de quoi ? | Des mots sur un alphabet fini ; des codes ; des certificats ([un code](../data/codes/q7_n6_R4_M14.txt), réfutations LRAT, multiplicateurs de Farkas). |
| **Formelle** | qu’est-ce qui la fait être ce qu’elle est ? | L’échelle des états et le noyau de Lean, qui décident de ce qui compte comme su. |
| **Efficiente** | par l’œuvre de quoi ? | La boucle de recherche et de vérification. Des générateurs qui proposent, des vérificateurs qui tranchent. Des personnes et des agents. |
| **Finale** | en vue de quoi ? | Inverser l’entropie locale. Rendre su l’incertain. Et rendre le su bon marché à vérifier de nouveau, pour toujours. |

---

## VI. Le théorème de James

Le dépôt [thiagopatzdorf/james-theorems](https://github.com/thiagopatzdorf/james-theorems) démontre en
Lean 4, sans Mathlib et sans `sorry`, trois propriétés de **modèles** simples de la philosophie qui
guide ce travail
([README](https://github.com/thiagopatzdorf/james-theorems/blob/12616cf56ed737a2cdfb9034753d5679c8091b49/README.md)).

**Connaissance** (`amortizacao`).
Dans une file de $N$ tâches, dont $D$ distinctes, en partant d’une base vide : exactement $D$
recherches et $N$ vérifications.

```math
\text{coût} \;=\; D \cdot \text{recherche} \;+\; N \cdot \text{vérification}
```

([Conhecimento.lean](https://github.com/thiagopatzdorf/james-theorems/blob/12616cf56ed737a2cdfb9034753d5679c8091b49/JamesTheorems/Conhecimento.lean)).
Que le coût par tâche tende vers celui de vérifier lorsque $D$ croît moins vite que $N$ est une
lecture de l’auteur, non une partie de l’énoncé.

**Sécurité** (`gate`).
Pour tout journal, même adversarial, aucune action critique n’apparaît exécutée sans approbation
enregistrée
([Seguranca.lean](https://github.com/thiagopatzdorf/james-theorems/blob/12616cf56ed737a2cdfb9034753d5679c8091b49/JamesTheorems/Seguranca.lean)).

**Âme** (`replay`, `retomada`, `revezamento`).
L’état est le repli d’une transition pure sur le journal.
Deux corps ayant la même transition atteignent le même état.
Un corps peut s’arrêter à n’importe quel événement, et un autre reprend depuis l’instantané.
Le journal peut être partagé entre plusieurs corps
([Alma.lean](https://github.com/thiagopatzdorf/james-theorems/blob/12616cf56ed737a2cdfb9034753d5679c8091b49/JamesTheorems/Alma.lean)).

> La frontière, dans les mots du dépôt lui-même : les théorèmes valent pour les modèles, non pour le code de production.

Ce sont des preuves courtes sur des structures simples.
Elles ne résolvent pas un problème difficile. Elles rendent exacte la forme d’un argument.

Ici, cette forme rencontre un problème réel : le registre est le journal, le certificat est la
vérification bon marché, et la recherche coûteuse n’a lieu qu’une fois par cellule.

---

## VII. Ce qui nous échappe encore

Les sept Problèmes du prix du millénaire du Clay Mathematics Institute sont un horizon, non une cible.
Nous n’en attaquons aucun.

L’un d’eux, **P vs NP**, demande si tout ce qui se vérifie vite se trouve aussi vite.
C’est l’asymétrie sur laquelle repose tout ce travail, et personne ne sait si elle est réelle.

La conjecture de Poincaré a été résolue par Perelman, dans des prépublications de 2002 et 2003.
Le prix lui a été décerné en 2010, et il l’a refusé. Les six autres restent ouverts[^clay].

---

## VIII. Lacunes déclarées

- Les bornes inférieures de `K₃(6,2)`, `K₇(6,4)` et `K₇(5,3)` ne sont pas des théorèmes du noyau. Elles
  reposent sur une réduction démontrée sur papier et sur des certificats vérifiés hors de Lean
  ([article](../paper/main.tex)).
- La borne supérieure `K₇(5,3) ≤ 17` a désormais notre propre code de 17 mots et un théorème Lean (`CoveringK753.K_7_5_3_le_17`) ; la lacune restante est la borne inférieure, hors de Lean.
- « Potentiellement nouveau » signifie non trouvé dans les sources listées. Des textes en accès fermé
  de 2004 à 2009 n’ont pas été lus ([NOVIDADE_V09](exatos/NOVIDADE_V09.md)).
- La littérature postérieure à 2011 hors des sources du registre n’a pas été auditée
  ([registre](../ledger/README.md)).

Pour le problème expliqué depuis le début : [Expliqué](EXPLIQUE.md).

---

<p align="center"><em>Que la lumière soit. Mais seulement là où il y a un certificat.</em></p>

[^asimov]: Isaac Asimov, « The Last Question » (*La Dernière Question*), *Science Fiction Quarterly*, novembre 1956.
[^aristoteles]: Aristote, *Physique* II 3 et *Métaphysique* Δ 2 : les quatre causes, ou les quatre manières de répondre à « pourquoi ? ».
[^clay]: [claymath.org/millennium-problems](https://www.claymath.org/millennium-problems/) ; [conjecture de Poincaré](https://www.claymath.org/millennium/poincare-conjecture/) ; [le refus](https://www.claymath.org/news/poincare-chair-2/).
