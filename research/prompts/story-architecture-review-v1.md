# Story Architecture Review v1

Review one or more existing reader-facing Stories as editorial paths through the canonical Question network.

This is **not** a Historical Critic and not a Story Critic. Assume the Story has already passed its evidence gate and historical review. The task here is to test whether researched material is organized into a coherent, bounded, non-misleading reader path.

## Inputs

Read current `main` and the relevant files under:

- `editorial/stories/`
- `editorial/reviews/`
- `data/questions/`
- `data/assertions/`
- `research/gaps/`

First generate structural context with:

```bash
python -m scripts.story_architecture_review context <story-id> [<story-id> ...]
```

The context is descriptive only. Shared Questions, refs, or assertions do not by themselves establish historical influence or causation.

The context also exposes canonical Question-to-Question Network assertions. Inspect their `predicate`, `perspective`, `certainty`, and `status` before treating them as part of a Story spine. A `candidate` edge remains a hypothesis; its presence in the Network must not silently upgrade it into a reviewed Story transition.

## Review dimensions

### 1. Entry

Ask whether the detailed Story begins at an editorially defensible point.

A broad title does **not** require exhaustive upstream reconstruction. Earlier history may be compressed into a short, natural lead when the detailed Story needs a bounded entry point.

Prefer reader-facing prose that flows into the selected period. Avoid workflow/disclaimer prose such as:

> This Story does not attempt to reconstruct the entire earlier history.

Context compression may use lighter research burden than a core historical claim, but it must not smuggle in strong priority, causation, direct influence, or `first` claims without appropriate evidence.

### 2. Question path

Identify the canonical Question path the Story curates.

Network Question-to-Question relations are potential narrative spines, not automatically historical causal chains. Preserve distinctions among:

- historical transition;
- later historical interpretation;
- modern abstraction/editorial relation.

Use the canonical Question-edge metadata surfaced by the context tool rather than inferring transition strength from visual proximity or Story order. Candidate or low-certainty edges may be useful editorial signals but are not reviewed historical transitions.

Do not strengthen a retrospective or thematic relation merely because it makes a cleaner Story.

### 3. Story-local Question disposition

For important Questions, record editorial disposition as appropriate:

- `opens`
- `continues`
- `branches`
- `answered_for_story`
- `handoff`
- `remains_open`

These are **Story-local editorial states**. They do not mutate or close the canonical Question globally.

`answered_for_story` means only that the Story has obtained enough of an answer to move its reader-facing focus elsewhere.

### 4. Overlap / synthesis / intersection

Compare neighboring Stories.

Distinguish:

- useful repeated orientation;
- unnecessary duplication;
- shared Question path;
- genuine historically evidenced intersection;
- later/editorial parallel;
- material already researched but not yet synthesized.

Prefer editorial synthesis over a new numbered Research Unit when the needed evidence is already canonical and reviewed.

Do not introduce a reusable Episode object merely because two Stories overlap once. Treat Episode extraction as a later schema decision if repeated material duplication accumulates across several Stories.

## Classifications

Each finding is one of:

- `PASS`
- `REVISE`
- `WEAK_EVIDENCE`
- `REJECT`

For every non-PASS finding, classify three independent properties:

### Gap kind

- `evidence`
- `entry_context`
- `coverage`
- `synthesis`
- `intersection`

### Research burden

- `none`
- `light`
- `medium`
- `full_research`

### Resolution mode

- `editorial_edit`
- `editorial_synthesis`
- `supplementary_research`
- `candidate_future_unit`

A detected gap must **not** automatically consume an R-number.

An `entry_context` problem alone must never be escalated directly to `candidate_future_unit`. First ask whether a bounded natural lead or light editorial research resolves it.

## Persistent output

Save the review as YAML under `editorial/reviews/`.

Use this structure:

```yaml
review:
  type: story_architecture
  review_date: YYYY-MM-DD
  status: reviewed
  stories:
    - story-example
  summary:
    pass: 0
    revise: 0
    weak_evidence: 0
    reject: 0

findings:
  - id: sar-001
    classification: REVISE
    dimension: entry
    stories: [story-example]
    reason: >
      ...
    question_dispositions:
      - question: q-example
        disposition: opens
    gap:
      kind: entry_context
      research_burden: light
      resolution_mode: editorial_edit
      needed_work: >
        ...
```

PASS findings may omit `gap`.

Validate the artifact with:

```bash
python -m scripts.story_architecture_review validate editorial/reviews/<file>.yaml
```

## Current regression cases

The first implementation should remain sensible for these distinct structures:

1. `story-function`
   - broad title with abrupt Fourier-era entry;
   - bounded natural context should be preferred over exhaustive pre-Fourier research;
   - overlap with the Fourier Story should be visible.

2. `story-fourier-heat-representation`
   - `q-heat-propagation` can be treated as `answered_for_story` / handoff while remaining globally open;
   - the Story then moves into prescribed-data and representation Questions;
   - nearby candidate Network edges must remain visibly candidate rather than being promoted by the review.

3. `story-cauchy-rigor-continuity` + `story-quantified-control`
   - parallel convergence/continuity lines and their existing intersection should be distinguishable from a demand for a new Research Unit.

4. `story-r008-uniqueness`
   - convergence → uniqueness → exceptional sets → derived-set structure should read as a strong Question-path spine;
   - transitions must retain their different historical/later-interpretation strengths as recorded in canonical Question-edge assertions.

## Non-goals

Do not in this review cycle:

- rewrite the canonical Question schema;
- make Story-local dispositions canonical states;
- automatically generate or rewrite Stories;
- create reusable Episode objects;
- require exhaustive upstream chronology;
- convert editorial gaps into numbered Research Units without roadmap/human review.
