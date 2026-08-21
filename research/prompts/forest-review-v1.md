# Forest Review v1

Review the current Math History Atlas as a portfolio of canonical Question paths and reader-facing Stories at a roadmap checkpoint.

This is **not** a Historical Critic, not a Story Critic, and not a Story Architecture Review of one or two Stories. Assume the current Research Units have completed their normal evidence and editorial gates. The task here is to inspect the forest as a whole and produce a prioritized work queue before allocating the next numbered Research Unit.

## Trigger

Run this review only at an explicit roadmap checkpoint, initially **after R010 is merged to `main`**.

Do not run against an in-progress R010 branch. Read current `main` only after the checkpoint unit is complete.

## Inputs

Read current `main` and inspect:

- `research/WORK-CYCLE.md`
- current roadmap files under `research/`
- all current files under `editorial/stories/`
- current Story Architecture reviews under `editorial/reviews/`
- canonical Questions under `data/questions/`
- canonical assertions, especially Question-to-Question assertions under `data/assertions/`
- persistent gaps under `research/gaps/`
- current Research Unit briefs and promotion maps where useful for provenance and scope

Use existing Story Architecture tooling for focused structural context where it helps:

```bash
python -m scripts.story_architecture_review context <story-id> [<story-id> ...]
```

Do not infer historical causation from visual Network proximity, Story order, or overlap. Preserve the `predicate`, `perspective`, `certainty`, and `status` of canonical Question-to-Question assertions.

## Purpose

Determine how the accumulated research graph should be edited and extended next.

The review should answer, at forest level:

1. Which canonical Question paths have become major Story spines?
2. Which Stories have abrupt or weak entry points relative to their titles and reader promise?
3. Which Questions appear to be locally answered, handed off, branched, or left open across the existing Stories?
4. Which Stories unnecessarily duplicate material, and which overlaps are useful orientation?
5. Which intersections are historically evidenced, which are later/editorial parallels, and which remain unresolved?
6. Which researched material is orphaned or underused editorially?
7. Which unresolved items are editorial problems, which need supplementary research, and which may justify a future numbered Research Unit?
8. What work should happen **before** allocating the next R-number?

## Review principles

### A. Do not reward exhaustive upstream coverage

A broad Story title does not require reconstructing the entire earlier history of the subject.

Prefer bounded editorial entry with natural context compression where appropriate. Do not create a research obligation merely because a subject has deeper historical roots.

### B. Use the smallest sufficient work type

For each identified problem, distinguish:

- `editorial_edit`
- `editorial_synthesis`
- `supplementary_research`
- `candidate_future_unit`

Do not create a future-unit candidate when an editorial change or bounded supplementary check is sufficient.

### C. Preserve research/editorial separation

Do not rewrite Stories during the Forest Review.

Do not promote new canonical historical claims during the Forest Review.

Do not allocate a new R-number during the Forest Review.

The Forest Review produces a queue and a human decision gate.

### D. Treat Story-local Question disposition as editorial

You may describe Questions within specific Stories as:

- `opens`
- `continues`
- `branches`
- `answered_for_story`
- `handoff`
- `remains_open`

These are Story-local editorial observations only. They do not close or mutate the canonical Question globally.

### E. Distinguish overlap from intersection

For cross-Story relations, distinguish:

- repeated orientation that helps the reader;
- unnecessary duplication;
- shared Question path;
- genuine historically evidenced intersection;
- later/editorial parallel;
- missing synthesis despite adequate research;
- unresolved historical transmission that still needs research.

Do not infer a reusable Episode object from a single overlap. Episode extraction remains a later schema decision if repeated duplication becomes substantial.

## Required output

Persist the Forest Review as YAML under:

```text
editorial/reviews/forest-review-post-r010.yaml
```

Use the following structure:

```yaml
review:
  type: forest
  checkpoint: post-R010
  review_date: YYYY-MM-DD
  status: awaiting_human_decision
  scope:
    through_unit: R010

forest:
  major_spines:
    - id: spine-example
      questions: [q-example-a, q-example-b]
      stories: [story-example]
      assessment: >
        ...

  entry_issues:
    - story: story-example
      assessment: >
        ...

  handoffs:
    - story: story-example
      from_question: q-example-a
      to_question: q-example-b
      disposition: handoff
      assessment: >
        ...

  overlaps:
    - stories: [story-a, story-b]
      relation: duplication | shared_path | historical_intersection | editorial_parallel | synthesis_candidate
      assessment: >
        ...

  underused_material:
    - refs: [q-example]
      assessment: >
        ...

work_queue:
  - id: fw-001
    priority: P0
    kind: editorial_edit | editorial_synthesis | supplementary_research | candidate_future_unit
    targets: [story-example]
    research_burden: none | light | medium | full_research
    reason: >
      ...
    depends_on: []

future_unit_candidates:
  - candidate_id: unnumbered-stable-id
    originating_gaps: [gap-id]
    rationale: >
      ...
    readiness: not_ready | plausible | strong_candidate
    blocked_by: []

human_gate:
  required: true
  questions:
    - Which editorial repairs should run before the next Research Unit?
    - Which supplementary research items are worth doing now?
    - Which candidate, if any, should receive the next roadmap-controlled R-number?
```

## Prioritization

Use priorities conservatively:

- `P0`: reader-facing structural defect or synthesis problem that should be addressed before the next numbered unit;
- `P1`: useful editorial/supplementary work that can be scheduled soon but need not block the next unit;
- `P2`: valid but deferrable cleanup or longer-range research candidate.

A large number of P0 items is itself a signal that the review is over-escalating. Prefer a small set of consequential repairs.

## Initial post-R010 regression targets

At minimum, explicitly reconsider these already-known structures in the forest context:

1. `story-function`
   - broad title / Fourier-era entry;
   - overlap with the Fourier heat/representation Story;
   - decide whether this remains a light editorial repair or exposes a larger synthesis need.

2. `story-fourier-heat-representation`
   - `q-heat-propagation` as a possible `answered_for_story` / handoff point;
   - later mathematical Questions exposed by the heat problem.

3. `story-cauchy-rigor-continuity` and `story-quantified-control`
   - parallel paths and the existing convergence/continuity intersection;
   - whether synthesis is needed before further research.

4. `story-r008-uniqueness`
   - Question evolution as a strong Story spine;
   - preserve the different strengths of historical and later-interpretation Question edges.

5. R009 and R010 Stories
   - evaluate them in the same forest-level terms after they are merged;
   - do not privilege older fixtures over newer material.

## Stop condition

Stop after persisting the Forest Review and presenting the prioritized queue and human gate.

Do **not**:

- edit production Stories;
- create or modify canonical entities/questions/assertions;
- perform substantial new historical research;
- allocate R011 or any later R-number;
- open an implementation PR for editorial repairs unless the human explicitly chooses the next action.

The next step is a human roadmap/editorial decision based on the persisted review.
