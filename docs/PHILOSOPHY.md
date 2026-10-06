[Português](FILOSOFIA.md) · **English** · [Français](PHILOSOPHIE.md)

# Philosophy: from chaos to order

> *"INSUFFICIENT DATA FOR MEANINGFUL ANSWER."* — Isaac Asimov, *The Last Question*

This text says what we do, why we do it, and by what rule we decide what is true.
It follows Aristotle's order: definitions, principles, propositions, method, causes.
Every factual claim points to the file that supports it.
What does not point anywhere is conviction, and is written as such.

## I. Definitions

1. **Cell.** A number `K_q(n,R)`: the smallest code of length `n` over `q` symbols that leaves every
   word within Hamming distance `R` of some codeword ([paper, Introduction](../paper/main.tex)). Kéri's
   tables hold 1145 cells, with `q` from 2 to 21 ([ledger](../ledger/README.md)).
2. **Bound.** An interval: `lower ≤ K_q(n,R) ≤ upper`. The upper bound is proved by showing a code.
   The lower bound, by proving that no smaller code exists.
3. **Local entropy.** The doubt that remains about a cell. The gap between its two bounds, and the
   uncertainty about each. Local, because it belongs to one problem, not to the universe.
4. **State collapse.** The moment the interval becomes a point. Before, many possible answers. After,
   only one.
5. **Certification state.** The degree of trust in each bound, on a ladder that only climbs:
   `CLAIMED`, `WITNESS_CHECKED`, `CERTIFICATE_VERIFIED` (lower bounds only), `FORMALIZED`,
   `INDEPENDENTLY_REPRODUCED` ([ledger, Certificação](../ledger/README.md)).

## II. Principles

1. **Checking is cheaper than finding.** Finding a code is a search in an immense space. Checking a
   given code is a finite computation. This is the asymmetry that the P vs NP question formalizes. For
   us it is an engineering compass, not a theorem.
2. **Expensive discovery becomes cheap verification.** A search that succeeds leaves a certificate: an
   explicit code, an LRAT refutation, integer Farkas multipliers, a kernel theorem
   ([paper, Introduction](../paper/main.tex)). Whoever comes next does not repeat the search. They check.
3. **The evaluator decides.** Whoever proposes may be wrong at will. Whoever decides must be cheap and
   exact. The heart of this repository is not the solver. It is the checker:
   [`tools/verify/verify.c`](../tools/verify/verify.c) and the Lean kernel.
4. **What is measured beats what is read.** A bound from the literature enters as `CLAIMED`. It climbs
   only when something here checks it. The state is computed by a script, never written by hand
   ([`ledger/build.py`](../ledger/build.py)).
5. **Error is a measurement, not a debt.** Where a proof breaks, a rule was missing. That is why we
   publish what failed ([paper, "Where the same methods stop"](../paper/main.tex)). That is why every
   new lower bound faces a red team before it enters ([K₇(5,3)](exatos/REDTEAM_K753.md),
   [K₇(6,4)](exatos/REDTEAM_K764.md), [K₃(6,2)](exatos/k362/K3_M16_REDTEAM.md)).
6. **Never claim more than was proved.** The ledger's sentence is fixed: *"A machine-checked ledger of
   covering-code upper bounds, with formally certified exact entries."* The whole table has not been
   formally verified. The lower bounds are, almost all of them, inherited from the literature
   ([coverage](../ledger/COBERTURA.md)).

## III. Propositions

- **488 of the 1145 upper bounds** are `FORMALIZED` or `INDEPENDENTLY_REPRODUCED`. Among the lower
  bounds, 3 are `CERTIFICATE_VERIFIED` and 2 are `FORMALIZED`
  ([`ledger/COBERTURA.md`](../ledger/COBERTURA.md)).
- **Two exact cells with both bounds in the kernel:** `K₂(6,1) = 12` and `K₇(4,2) = 19`
  ([paper, "A certified ledger"](../paper/main.tex); [LEAN_K742](exatos/LEAN_K742.md)).
- **Three collapses that are potentially new**, not found in the literature we searched:
  `K₃(6,2) = 17`, `K₇(6,4) = 14`, `K₇(5,3) = 17`. All three lower bounds are `CERTIFICATE_VERIFIED`,
  not kernel theorems ([NOVIDADE_V09](exatos/NOVIDADE_V09.md); [ledger](../ledger/README.md)).

## IV. Method

The cycle ends only when something has changed state and has been checked.

1. **Choose** a cell by the doubt it holds.
2. **Search.** The expensive part: constructions, SAT, linear programming, red team.
3. **Certify.** Reduce the discovery to an object an exact checker can verify.
4. **Record** it in the ledger, with source, sha256 and computed state ([`ledger/cells.json`](../ledger/cells.json)).
5. **Expose.** Paper, DOI, declared gaps. So that someone else can redo it without trusting us.

The ledger is memory.
Whoever arrives tomorrow does not repeat the search.
They read the state, and check the certificate.

## V. The four causes

- **Material:** words over a finite alphabet; codes; certificates
  ([a code](../data/codes/q7_n6_R4_M14.txt), LRAT refutations, Farkas multipliers).
- **Formal:** the ladder of states and the Lean kernel, which decide what counts as known.
- **Efficient:** the loop of search and verification. Generators that propose, checkers that decide.
  People and agents.
- **Final:** to reverse local entropy. To make the uncertain known. And to make the known cheap to
  check again, forever.

## VI. The James theorem

The repository [thiagopatzdorf/james-theorems](https://github.com/thiagopatzdorf/james-theorems)
proves in Lean 4, without Mathlib and without `sorry`, three properties of simple **models** of the
philosophy behind this work
([README](https://github.com/thiagopatzdorf/james-theorems/blob/12616cf56ed737a2cdfb9034753d5679c8091b49/README.md)).

- **Knowledge** (`amortizacao`). In a queue of `N` tasks, `D` of them distinct, starting from an empty
  base: exactly `D` searches and `N` verifications. The cost is `D·search + N·verification`
  ([Conhecimento.lean](https://github.com/thiagopatzdorf/james-theorems/blob/12616cf56ed737a2cdfb9034753d5679c8091b49/JamesTheorems/Conhecimento.lean)).
  That the cost per task tends to the cost of checking when `D` grows more slowly than `N` is the
  author's reading, not part of the statement.
- **Safety** (`gate`). For any log, even an adversarial one, no critical action appears as executed
  without a recorded approval
  ([Seguranca.lean](https://github.com/thiagopatzdorf/james-theorems/blob/12616cf56ed737a2cdfb9034753d5679c8091b49/JamesTheorems/Seguranca.lean)).
- **Soul** (`replay`, `retomada`, `revezamento`). The state is the fold of a pure transition over the
  log. Two bodies with the same transition reach the same state. A body may stop at any event, and
  another resumes from the snapshot. The log may be split among bodies
  ([Alma.lean](https://github.com/thiagopatzdorf/james-theorems/blob/12616cf56ed737a2cdfb9034753d5679c8091b49/JamesTheorems/Alma.lean)).

The boundary, in the repository's own words: the theorems hold for the models, not for production code.
They are short proofs about simple structures.
They do not solve a hard problem. They make the shape of an argument exact.
Here, that shape meets a real problem: the ledger is the log, the certificate is the cheap
verification, and the expensive search happens once per cell.

## VII. What still escapes us

The seven Millennium Prize Problems of the Clay Mathematics Institute are a horizon, not a target.
We attack none of them.
One of them, **P vs NP**, asks whether everything that can be checked quickly can also be found quickly.
It is the asymmetry this whole work leans on, and no one knows whether it is real.
The Poincaré conjecture was solved by Perelman, in preprints of 2002 and 2003. The prize was awarded
in 2010, and he declined it. The other six remain open
([claymath.org](https://www.claymath.org/millennium-problems/);
[Poincaré](https://www.claymath.org/millennium/poincare-conjecture/);
[the refusal](https://www.claymath.org/news/poincare-chair-2/)).

## VIII. Declared gaps

- The lower bounds of `K₃(6,2)`, `K₇(6,4)` and `K₇(5,3)` are not kernel theorems. They rest on a
  reduction proved on paper and on certificates checked outside Lean ([paper](../paper/main.tex)).
- The upper bound `K₇(5,3) ≤ 17` now has our own 17-word code and a Lean theorem (`CoveringK753.K_7_5_3_le_17`); the remaining gap is the lower bound, outside Lean.
- "Potentially new" means not found in the sources listed. Closed-access texts from 2004 to 2009 were
  not read ([NOVIDADE_V09](exatos/NOVIDADE_V09.md)).
- Literature after 2011 outside the ledger's sources has not been audited ([ledger](../ledger/README.md)).

For the problem explained from scratch: [Explained](EXPLAINED.md).

*Let there be light. But only where there is a certificate.*
