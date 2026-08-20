# R003 brief — Dirichlet and the changing concept of function after Fourier

## Purpose

Use R003 to turn the existing `What is a function?` PoC stub into a source-backed researched Story and to connect R001's arbitrary-function problem with the nineteenth-century clarification of admissible functions.

## Proposed title

**Dirichlet — trigonometric series, arbitrary functions, and the changing concept of function**

## Working period

Core: **1829–1837**. Earlier background may reach back to Fourier and the vibrating-string/function debates only as needed to establish the problem; later material should be excluded unless needed to interpret Dirichlet's legacy.

## Existing graph intersections to inspect first

- `concept-fourier-series`
- `concept-function`
- `concept-continuity`
- `concept-arbitrary-function`
- `q-what-is-function`
- `q-fourier-series-convergence`
- Dirichlet's existing 1829 work/entity and R001 assertions

Reuse existing canonical IDs when the object is genuinely the same.

## Core research questions

1. What problem was Dirichlet actually addressing in his work on trigonometric series, and what restrictions did he impose compared with Fourier's broader representational claims?
2. What language did Dirichlet use for arbitrary/discontinuous functions, and what did he treat as admissible input to a trigonometric expansion?
3. Which text/date supports the historical claim often paraphrased as a more general or "modern" definition of function? Distinguish the date of writing, reading, and publication where needed.
4. How did Dirichlet's convergence work relate historically to Fourier and Cauchy? Do not infer motivation from chronology or mathematical similarity alone.
5. Which parts of the later textbook story "Euler/Fourier → Dirichlet → modern function" are supported by primary texts and which are later historiography?
6. What role did discontinuity play? Avoid treating `discontinuous function` as a timeless modern category if the historical language is different.
7. What intermediaries or earlier disputes are necessary to avoid over-concentrating credit on Dirichlet?

## Historical claims that must be tested rather than assumed

- "Dirichlet gave the first modern definition of function."
- "Fourier caused the modern concept of function."
- "Dirichlet solved Fourier's convergence problem in full generality."
- "The concept of discontinuous function was already identical to the modern concept."

Any of these may survive in qualified form, but none should enter canonical data merely as textbook lore.

## Primary-source targets

The research should locate stable primary editions/scans for the relevant Dirichlet papers and identify page-level passages for:

- convergence conditions for trigonometric series;
- treatment of arbitrary/discontinuous functions;
- any explicit definition-like formulation of function;
- explicit references to Fourier, Cauchy, or mathematical-physics motivation when claimed.

Use specialist historiography to interpret reception and conceptual change, not as a substitute for available primary passages.

## Phase-B integration target

R003 should **upgrade, not duplicate**, the existing Story stub:

`story-function` — **What is a function?**

Expected Story architecture is provisional and must be evidence-driven, but likely needs to distinguish:

- earlier analytic/formula-oriented conceptions;
- Fourier's broad representational practice;
- the problem posed by arbitrary/discontinuous data;
- Dirichlet's formulation/restrictions;
- a remaining gap leading toward Riemann and integrability.

Every researched Story step must have `narrative`, `assertion_refs`, `perspective`, and a Story-local `temporal_anchor` under the current schema.

Do not preserve the PoC step order merely because it already exists. Replace the stub with the reviewed Story if the evidence requires a different DAG.

## Network effect expected

R003 should deepen the existing Fourier/function intersection rather than simply append a new biography. A successful unit should make `concept-function`, `concept-fourier-series`, and the Dirichlet work/person visible as historically distinct but connected occurrences.

## Handoff to R004

The final R003 Story should leave an explicit downstream question around **what conditions on a function make representation/integration legitimate**, but it must not presuppose Riemann's answer. That question becomes the natural entry point for R004.

## Fresh-chat command

```text
Open Chachay/math-history-atlas and follow research/prompts/research-unit-kickoff-v1.md for R003. Use research/units/R003-dirichlet-function-concept.md as the approved unit brief. Read current main first and proceed through Phase A and Phase B, stopping with an open PR for review.
```
