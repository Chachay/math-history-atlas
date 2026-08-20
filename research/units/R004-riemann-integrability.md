# R004 brief — Riemann, trigonometric series, discontinuous functions, and integrability

## Purpose

Use R004 to open a genuinely new line from the Fourier/Dirichlet function problem into **integration theory** and to create a researched bridge toward later analysis without collapsing the development into “Fourier invented the Riemann integral.”

## Proposed title

**Riemann — trigonometric series, discontinuous functions, and integrability**

## Working period

Core: **1854–1867**. Earlier Dirichlet/Fourier context may be included as inherited problem structure. Later measure-theoretic developments should remain out of scope except as clearly marked retrospective interpretation.

A key chronology question is the distinction among Riemann's writing/presentation dates and later publication of the trigonometric-series memoir. The packet and critic must identify the date type explicitly rather than flattening them into one year.

## Dependency

R004 should start from the **current `main` after R003 is merged** if R003 changes canonical function/Dirichlet nodes or replaces `story-function`. Do not run R004 against a stale pre-R003 graph and then manually reconcile duplicates.

## Existing graph intersections to inspect first

- `concept-fourier-series`
- `concept-function`
- `concept-continuity`
- Dirichlet canonical work/person/questions from R001/R003
- Riemann's existing person entity if present
- convergence questions from R001/R002

Reuse canonical IDs when historically identical.

## Core research questions

1. What problem was Riemann actually addressing in his work on representing functions by trigonometric series?
2. Why did questions of integrability arise in that setting? Distinguish historical motivation from the modern theorem-level relation between Fourier analysis and integration.
3. How did Riemann characterize or work with discontinuous functions, and what limitations did he impose?
4. What exactly is historically new in Riemann's treatment of integration compared with preceding practice? Avoid treating the modern textbook Riemann integral as if its current axiomatic presentation were already present unchanged.
5. How did Riemann engage with Dirichlet's convergence conditions and function concept?
6. Which chronology is relevant for the trigonometric-series memoir: composition, academic presentation/submission, or publication?
7. Which later claims about “Riemann integration arising from Fourier series” are supported as historical motivation and which are retrospective mathematical reconstruction?
8. What new remaining gap naturally leads beyond Riemann — e.g. pathological/discontinuous functions, exceptional sets, or later measure/integration theory — without prematurely importing Lebesgue?

## Historical claims that must be tested rather than assumed

- "Riemann invented integration because Fourier series failed."
- "The Riemann integral was created specifically to solve Fourier's problem."
- "Dirichlet's definition of function directly caused Riemann's integration theory."
- "Riemann's 1854 work was published in 1854."
- "Riemann's discontinuous functions are exactly the modern category with no terminological or conceptual gap."

## Primary-source targets

Locate stable primary editions/scans and page-level passages for:

- Riemann's trigonometric-series memoir;
- his discussion of integrability/discontinuity;
- explicit references to Fourier and Dirichlet where historically claimed;
- academic chronology establishing composition/presentation/publication dates.

Use specialist historiography to adjudicate the motivation question and the relation between the memoir and the later textbook “Riemann integral.”

## Phase-B integration target

R004 should create or upgrade a researched Story centered on a question such as:

**When is a function integrable enough for trigonometric representation?**

This should intersect the researched `story-function` produced by R003, but should not merely extend it linearly. Likely Story roles include:

- inherited representation/function problem;
- limits of existing convergence conditions;
- integrability as a new control question;
- Riemann's response;
- remaining gaps/pathologies.

The Story DAG should branch from existing function/Fourier nodes where historically justified. All temporal anchors are Story-local occurrences, not entity birth dates.

## Network effect expected

R004 should add the first strong bridge from the existing Fourier/Cauchy/Dirichlet cluster into **integration**. If successful, the Network should show an intersection among Fourier representation, function admissibility, convergence, and integrability without presenting them as one inevitable chain.

## Deferred downstream possibilities

Do not absorb these into R004 unless the evidence forces them into the bounded story:

- Cantor and uniqueness/exceptional point sets;
- Lebesgue and measure/integration;
- Hilbert-space/Fourier-analysis reinterpretations.

Those are later units.

## Fresh-chat command

```text
Open Chachay/math-history-atlas and follow research/prompts/research-unit-kickoff-v1.md for R004. Use research/units/R004-riemann-integrability.md as the approved unit brief. Confirm that R003 is already merged into current main, then proceed through Phase A and Phase B, stopping with an open PR for review.
```
