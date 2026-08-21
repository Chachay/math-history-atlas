# Work design — R005 / R006 and Story cleanup

## Goal

Finish the first analysis arc without duplicating Stories, then deliberately open a second major field branch in algebra.

## Sequence

### 0. Finish current integration PR

Complete mobile review of the Story-handoff / Person-navigation work. Confirm that reviewed cross-Story transitions make R001–R004 read as an integrated graph and that Person pages are reachable.

Do not layer R005 on top of an unreviewed Network integration state.

### 1. Retire the duplicate active rigor Story

`story-rigor` (**How can infinity be trusted?**) overlaps too heavily with `story-cauchy-rigor-continuity`.

Action:

- remove `story-rigor` from active Stories after confirming no unique reviewed historical path would be lost;
- preserve the title and concept as a future **Theme / guided route**, not as a second Story over the same Cauchy evidence;
- do not invent a Theme schema merely to keep the title visible if the product does not yet need it; a candidate/roadmap artifact is sufficient.

This cleanup should be a small editorial/UI PR, separate from R005 research.

### 2. Run R005 — quantified limit control / ε–δ

Approved brief: `research/units/R005-epsilon-delta-rigor.md`.

Purpose:

- extend R002's convergence/continuity line into explicit quantified control;
- test the Weierstrass-centered textbook narrative;
- distinguish lecture/manuscript/publication dates;
- create a new Story such as **How precisely must “arbitrarily close” be controlled?**;
- add only reviewed cross-Story handoffs to R002/R005.

R005 is the capstone of the current analysis cycle, not permission to absorb completeness, real-number construction, Cantor, or measure theory.

### 3. Analysis-arc integration checkpoint

After R005, review the analysis branch as a whole:

- R001 Fourier — representation;
- R002 Cauchy — convergence/continuity;
- R003 Dirichlet — function/admissibility;
- R004 Riemann — integration;
- R005 quantified limits/continuity.

Check for:

- duplicate Story blocks;
- missing or over-strong Story transitions;
- temporal occurrence splits that need reviewed handoffs rather than node merging;
- Person navigation;
- unresolved research gaps that should remain visible rather than silently closed.

Do not start another analysis Research Unit merely to make the line look more complete.

### 4. UI prerequisite for a genuine second field

Before R006 Phase B, make sure the Atlas can represent and enter an algebra branch from field data.

Current hard-coded Atlas paths may be adequate as a sketch but are not sufficient evidence that a second field can scale. Minimum prerequisite:

- Algebra is a selectable field context;
- the Network can frame/filter the algebra cluster;
- Person navigation works for algebra actors;
- field placement is data-driven enough that R006 does not require hand-positioning every new historical node.

Keep this bounded. Do not turn it into a full visual redesign.

### 5. Run R006 — solvability, permutations, Galois

Approved brief: `research/units/R006-solvability-permutations-galois.md`.

Purpose:

- open the first substantial algebra branch;
- begin from polynomial solvability, not modern group axioms;
- investigate Lagrange, Abel, and Galois with direct evidence for transmission and chronology;
- create a Question-driven Story around solvability by radicals;
- allow the algebra cluster to remain separate from analysis unless a genuine reviewed intersection exists.

## Why this order

The project currently risks two opposite failures:

1. staying in analysis long enough that the Atlas becomes a disguised analysis timeline;
2. jumping to algebra before the existing analysis Stories and cross-links are coherent.

R005 gives the existing branch a natural stopping point. R006 then stress-tests the core architecture: the Atlas must support multiple fields and multiple historical clusters without forcing one synthetic genealogy.

## Candidate later units

After R006, select based on graph gaps rather than a predetermined textbook syllabus. Strong candidates include:

- Cantor — uniqueness of trigonometric series and exceptional point sets;
- later group abstraction / Cayley;
- Lebesgue — measure and integration;
- completeness / construction of the real numbers;
- a historically responsible frequency/harmonic-analysis unit that can eventually mature **Seeing the world by frequency**.

## Operating rule

For every new Research Unit, ask both:

- **What new historical question/field does this add?**
- **Which existing Story, transition, Theme candidate, or graph gap does it mature?**

The repository should gain integration depth as well as research breadth.
