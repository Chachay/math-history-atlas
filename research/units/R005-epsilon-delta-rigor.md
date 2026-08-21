# R005 brief — quantified control of limits, continuity, and ε–δ language

## Purpose

Use R005 to complete the first major analysis arc by investigating how nineteenth-century analysis moved from limit/infinitesimal language toward explicit quantified control of approximation. The unit should test, rather than assume, the textbook narrative that “Weierstrass invented epsilon-delta rigor.”

## Proposed title

**Weierstrass and the quantified control of limits — continuity, convergence, and ε–δ language**

## Working period

Core: approximately **1840–1880**.

Earlier Cauchy/Bolzano material may enter as necessary antecedent evidence. Later twentieth-century formalism is out of scope except as clearly marked retrospective interpretation.

## Dependency

R005 should start from current `main` after the Story-integration/person-navigation work is merged or otherwise reconciled. Reuse the existing Cauchy, continuity, convergence, uniform-convergence, function, and limit-related canonical IDs where historically identical.

## Existing graph intersections to inspect first

- `story-cauchy-rigor-continuity`
- `q-uniform-convergence-emergence`
- `concept-continuity`
- `concept-convergence`
- `concept-function`
- Cauchy canonical works/person
- Weierstrass canonical entity if already present
- any existing limit/infinitesimal entities and questions

## Core research questions

1. What problem was Weierstrass actually trying to solve when using explicit inequalities and variable bounds in analysis?
2. What evidence exists for the chronology and wording of ε–δ formulations in Weierstrass's lectures, notes, students' records, and publications?
3. How should Cauchy's limit/infinitesimal language be compared with later ε–δ formulations without treating the difference as a simple “incorrect → correct” replacement?
4. What role did Bolzano, Heine, Dini, and other intermediaries play in the emergence and circulation of quantified definitions?
5. When and in what settings did ε and δ become stable notation for definitions of limits and continuity?
6. How does the development connect historically to the stronger control of convergence already represented in R002, and where is the connection only a modern mathematical relation?
7. Which claims about “arithmetization of analysis” are supported by primary sources, and which are later historiographical syntheses?
8. What unresolved question should remain after R005 — e.g. completeness of the real numbers, pathological functions, set-theoretic foundations, or another rigor problem — without absorbing those later developments into this unit?

## Historical claims that must be tested rather than assumed

- “Weierstrass invented the epsilon-delta definition.”
- “Cauchy did not understand limits because he used infinitesimals.”
- “The modern textbook definition first appeared in one identifiable published paper.”
- “Uniform convergence directly caused epsilon-delta analysis.”
- “Arithmetization of analysis was a single-person program with one start date.”

## Primary-source targets

Locate stable primary editions/scans or reliable scholarly editions for:

- Weierstrass lecture material or publications containing explicit quantified formulations;
- Cauchy's formulations used for comparison;
- Bolzano/Heine or other intermediaries where priority/transmission claims are made;
- chronology distinguishing lecture date, manuscript date, publication date, and later edited publication.

Specialist historiography is required for transmission, priority, and the phrase “arithmetization of analysis.”

## Phase-B integration target

R005 should create a new researched Story rather than expanding `story-rigor` back into a duplicate of R002.

Working Story question:

**How precisely must “arbitrarily close” be controlled?**

Likely roles:

- inherited limit/continuity problem from Cauchy;
- need for explicit control of allowed error and corresponding input variation;
- quantified response(s);
- notation and formulation becoming standardized;
- remaining gap concerning the number system or other foundations.

The Story should intersect R002 where evidence supports a historical or retrospective handoff, but should not assert a single linear Cauchy → Weierstrass transmission without evidence.

## Theme consequence

`story-rigor` / **How can infinity be trusted?** should not remain an active duplicate Story. Treat that title as a future cross-Story theme or guided route spanning R002 and R005 (and possibly later completeness material), not as another evidence path over the same six nodes.

## Network effect expected

R005 should give the analysis branch a clean stopping point for the current cycle:

Fourier / representation → Cauchy / convergence and continuity → Dirichlet / admissibility → Riemann / integration → quantified limit-control.

This is one major branch, not the universal history of analysis.

## Fresh-chat command

```text
Open Chachay/math-history-atlas and follow research/prompts/research-unit-kickoff-v1.md for R005. Use research/units/R005-epsilon-delta-rigor.md as the approved unit brief. Read current main first, preserve the distinction among publication, lecture, manuscript, and later-edition dates, and test rather than assume the claim that Weierstrass invented epsilon-delta rigor. Proceed through Phase A and Phase B and stop at PR/mobile review.
```
