# Semantic migration review — R008 / R010 fixtures

Status: implementation review for Semantic Network V2.

## Purpose

R008 and R010 are the first canonical-data fixtures migrated after the Semantic Network V2 refactor. The goal is not to rewrite Story prose or strengthen historical claims. The goal is to decompose already reviewed material into typed historical/mathematical relations that can support a reader-facing Network without using Story adjacency or vague `contributed_to` edges as topology.

## Global migration rule

A publishable assertion is not automatically a primary Network edge.

Only predicates with an explicit domain/range contract are `typed` and eligible for `default_network_visible`. Legacy predicates such as `raised_question`, `generalized`, `reframed`, and `influenced` remain evidence-bearing claims but are now classified as `legacy`. `contributed_to` remains `broad`.

This deliberately prefers a sparse but semantically interpretable Network over a dense graph whose lines have ambiguous meaning.

## R008 — Cantor uniqueness / exceptional sets / derived sets

### New historical objects

- a scoped historical `Problem` for uniqueness under the 1870 hypotheses;
- `Result` nodes for Cantor's 1870 theorem, 1871 finite-exception extension, and 1872 derived-set extension;
- a 1872 `ConceptState` for the enlarged class of exceptional point sets.

### Typed relation structure

The reviewed 1870–1872 sequence is decomposed as:

```text
Heine 1870 Work --addresses--> 1870 uniqueness Problem
Cantor 1870 Work --proves--> 1870 Result --resolves--> scoped Problem
Cantor 1871 Work --proves--> 1871 Result --strengthens--> 1870 Result
Cantor 1872 Work --defines--> 1872 derived-set ConceptState
Cantor 1872 Work --uses--> 1872 exceptional-set ConceptState
Cantor 1872 Work --proves--> 1872 Result --strengthens--> 1871 Result
1872 Result --depends_on--> derived-set / exceptional-set ConceptStates
```

Authorship relations connect Heine/Cantor to the relevant Works.

### Historical restraint preserved

- The detailed Heine↔Cantor direction of suggestion remains broad/uncertain; no new `influenced` edge is created.
- The Riemann/Schwarz proof-chain gap remains unresolved.
- No 1872→1874/transfinite-set-theory edge is created.
- QuestionFrame evolution remains in the Inquiry layer.

## R010 — Jordan / Borel / Lebesgue measure and integration

### New historical objects/states

- a historical `Problem` for Lebesgue's explicitly stated primitive-function limitation of Riemann integration;
- `ConceptState` records for Jordan content (1892), Borel measure (1898), measurable-set language (1898–1901), Lebesgue measure (1901), and the Lebesgue integral in 1901 and 1902.

### Typed relation structure

The historical graph deliberately keeps the predecessor lines asymmetric:

```text
Jordan --authored--> Jordan 1892 Work --uses--> Jordan-content state

Borel --authored--> Borel 1898 Work
Borel 1898 Work --defines--> Borel-measure / measurable-set states

Lebesgue --authored--> 1901 Work --addresses--> Riemann primitive-function Problem
Problem --concerns--> Riemann-integral ConceptState (R004)
1901 Work --cites--> Borel 1898 Work
1901 Work --uses--> Borel measurable-set state
1901 Work --defines--> Lebesgue-measure / Lebesgue-integral states
1902 Thesis --develops--> 1901 Work
```

The modern containment relation is represented separately as:

```text
Lebesgue integral --generalizes--> Riemann integral
mode: mathematical_retrospective
```

### Historical restraint preserved

- No Cantor→Borel or Cantor→Lebesgue causal edge is introduced.
- No direct Jordan→Lebesgue causal edge is introduced. Jordan remains a reviewed predecessor cluster; convergence of the integration and set-size lines remains Inquiry/Story semantics.
- The only direct Borel→Lebesgue historical handoff promoted to primary topology is Lebesgue's explicit citation/use of Borel's measurable-set work.
- Later named convergence theorems remain outside this migration.

## Compatibility policy

Legacy assertion IDs are retained because existing Stories cite them as provenance. The migration adds precise V2 claims alongside those legacy claims rather than silently changing the meaning of Story evidence references.

A later cleanup may retire redundant legacy claims only after Story/evidence references are migrated deliberately.

## UI implication

This fixture migration does not implement Network UI. It establishes the graph that a future Network projection may consume:

- QuestionFrames are absent from the semantic Network;
- Story selection must highlight grounded canonical objects/claims rather than drawing Story-only edges;
- topology may be driven by Person/Work/Problem/Result/ConceptState relations;
- chronology remains metadata with node-type-specific semantics rather than a universal axis.

## Review gate

Before merge:

- validation/tests/build must pass;
- R008 typed graph must preserve the documented 1870→1871→1872 strengthening sequence without inventing later handoffs;
- R010 must expose the explicit Borel citation while keeping Jordan and Cantor causal gaps absent;
- generated semantic audit must show legacy/broad claims as migration queues rather than default topology.
