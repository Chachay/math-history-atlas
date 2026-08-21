# Research and Editorial Work Cycle

This document describes the repository-level operating cycle for expanding and editing the Math History Atlas.

The Atlas is no longer treated as a simple sequence of Research Units (`R001`, `R002`, ...). Research Units remain the main mechanism for adding historically checked material, but they are now complemented by editorial checkpoints that review how the accumulated Question network becomes reader-facing Stories.

## 1. Three work cycles

### A. Research Unit cycle

Use a numbered Research Unit when the Atlas needs new historical evidence, new canonical objects, or a bounded investigation of a mathematical Question.

Typical cycle:

```text
Approved Research Unit brief
→ Research Packet
→ Historical Critic
→ Human resolution
→ integrity binding
→ verified promotion
→ canonical promotion
→ Story draft
→ Story evidence gate
→ Story Critic
→ persistent unresolved gaps
→ validation / preview / merge
```

Research Units are the high-frequency cycle. They grow the canonical research graph.

Do not allocate a new R-number merely because some supporting context is missing. R-number allocation is roadmap-controlled.

### B. Story Architecture Review cycle

Use this cycle when the problem is not primarily missing historical evidence, but the way researched material is organized into Stories.

Typical triggers:

- a broad Story title begins abruptly at a narrow research-unit starting point;
- the reader may incorrectly infer that a subject's history begins with the first detailed Story block;
- a Story needs a natural compressed prehistory rather than exhaustive upstream reconstruction;
- a Question appears to be answered, handed off, branched, or left open within a particular Story;
- Network Question-to-Question relations have developed into a plausible narrative path;
- two Stories repeat, intersect, or partially overlap the same researched material;
- existing canonical material may be sufficient, but editorial synthesis is needed.

The first implementation of this cycle is tracked in GitHub issue #33.

The review should remain lighter than a new Research Unit. It should distinguish editorial problems from evidence problems and should prefer synthesis or bounded context over unnecessary new research.

### C. Forest Review cycle

Use this lower-frequency cycle after several Research Units or at roadmap checkpoints.

Its purpose is to review the Story forest as a whole:

- Which Question paths are becoming major spines?
- Which Stories overlap or diverge?
- Where are meaningful historical intersections?
- Which open gaps are merely editorial, which need supplementary research, and which justify a future Research Unit?
- What should the next roadmap-controlled Research Unit be?

A Forest Review is a portfolio-level decision point, not a substitute for Historical Critic or Story Critic.

## 2. Default operating rhythm

The default loop remains research-first:

```text
Research Unit
→ Research Unit
→ Research Unit
→ editorial checkpoint when useful
→ more Research Units
→ Forest Review at a roadmap checkpoint
```

Do not run Story Architecture Review after every Research Unit by default. Insert it when the accumulated graph or Story set gives a concrete editorial reason.

A practical pattern is:

```text
R00X
R00Y
R00Z
→ Story Architecture Review if signals exist
→ continue research
→ Forest Review after the planned cluster / roadmap milestone
```

The human semantic gate is therefore no longer only "accept or reject critic findings." The human may also decide whether the next action should be:

- continue with the next approved Research Unit;
- run a Story Architecture Review;
- perform light supplementary research;
- perform editorial synthesis;
- run a Forest Review before allocating another R-number.

## 3. Research versus editorial work

Use the smallest work type that can resolve the problem.

### Prefer editorial work when

- the needed historical material is already canonical or adequately researched;
- the problem is Story entry, pacing, ordering, overlap, or handoff;
- a broad subject needs a short contextual lead rather than an exhaustive upstream history;
- two Stories need to be aligned around an existing intersection.

### Prefer supplementary research when

- a narrow supporting fact or context sentence needs checking;
- the missing evidence does not justify a standalone Question spine;
- the work can be completed without consuming a new roadmap slot.

### Prefer a new Research Unit when

- the missing material is itself a bounded mathematical-historical problem;
- it introduces or materially extends a canonical Question path;
- it needs primary/specialist source work and Historical Critic at full depth;
- the roadmap explicitly allocates the next R-number to it.

## 4. Bounded Story entry

A Story is not required to reconstruct the entire upstream history implied by its title.

For example, a future Story such as `What is a real number?` must not automatically expand backward to antiquity. A Story may choose a later detailed entry point if the reader is oriented naturally.

The editorial requirement is:

> The reader should understand why the detailed Story begins where it does, without being misled into thinking that the subject itself began there.

Use natural context compression when needed. Avoid workflow-like disclaimer prose such as:

```text
This Story does not attempt to reconstruct the entire earlier history.
```

Prefer flowing reader-facing prose that briefly acknowledges the longer background and then moves into the detailed historical episode.

Context compression may carry a lighter research burden than core historical claims, but it must not introduce strong claims of priority, direct influence, causation, or "first" status without appropriate evidence.

## 5. Question paths and Story-local disposition

Canonical Questions remain global objects. A Story may, however, give a Question a local editorial role.

Story Architecture Review may describe a Question as:

- `opens`
- `continues`
- `branches`
- `answered_for_story`
- `handoff`
- `remains_open`

These are Story-local editorial dispositions, not canonical truth states.

For example, `How does heat propagate?` can be treated as `answered_for_story` within the Fourier Story once the narrative has moved from the physical heat problem into the mathematical problems exposed by Fourier's method. The canonical Question itself remains historically and globally available.

Likewise, Network Question-to-Question edges are potential narrative spines. They do not automatically imply historical causation. Story editing must preserve the distinction among historical transition, later interpretation, and editorial relation.

## 6. Editorial gaps versus research gaps

Do not collapse every discovered problem into a future Research Unit.

Story Architecture Review should eventually distinguish at least:

Gap kind:

```text
evidence
entry_context
coverage
synthesis
intersection
```

Research burden:

```text
none
light
medium
full_research
```

Resolution mode:

```text
editorial_edit
editorial_synthesis
supplementary_research
candidate_future_unit
```

These axes are intentionally separate. For example, an `entry_context` problem may require only a `light` burden and an `editorial_edit`, while an `evidence` problem may require `full_research` without necessarily becoming a new numbered unit.

## 7. Current implementation boundary

PR #32 / issue #28 owns mechanical Story evidence and research-gap completion:

- Story assertion/source traceability;
- perspective checks;
- stronger scrutiny of `continues` links;
- persistent unresolved research gaps;
- distinction between supplementary work and future-unit candidates;
- no automatic R-number allocation.

Issue #33 owns the next Story Architecture layer:

- bounded entry and contextual leads;
- selected Question paths;
- Story-local closure / handoff;
- overlap, synthesis, and intersections across Stories;
- richer editorial gap classification.

Do not introduce reusable Episode objects, production Story-local lifecycle schema, or automatic Story generation until repeated review evidence justifies those abstractions.

## 8. Suggested human commands

A normal Research Unit remains explicit:

```text
Open Chachay/math-history-atlas and follow research/prompts/research-unit-kickoff-v1.md for R009. Read current main and use the approved R009 brief in research/units/.
```

A Story Architecture Review should eventually have its own prompt, for example:

```text
Open Chachay/math-history-atlas and run the Story Architecture Review for story-function and its neighboring Question paths.
```

A Forest Review should similarly be explicit at a roadmap checkpoint, for example:

```text
Review the current Story forest after R010. Identify duplicated paths, weak Story entries, unresolved handoffs, intersections, and candidate future research directions before allocating R011.
```

The long-term operational goal is that the repository can report the current frontier and suggest the next semantic gate, while the human retains control over roadmap allocation and historical/editorial judgment.
