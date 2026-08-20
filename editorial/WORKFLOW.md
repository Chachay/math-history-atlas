# Editorial Story workflow

Stories are a revisable editorial layer built on canonical historical data. They are not a second source of facts.

## End-to-end flow

```text
Research Packet
→ Historical Critic
→ Human research resolution
→ Bind resolution to packet/review fingerprints
→ Verified canonical fact promotion
→ Canonical assertions/questions/entities
→ Canonical provenance map
→ Story Editor draft
→ Story Critic
→ Human editorial resolution
→ editorial/stories/*.yaml
→ validate/build
→ PR Preview deep link
→ visual review
→ merge
```

## Responsibilities

### Research Packet
Collects candidate historical claims, chronology, questions, and sources. It may contain claims that never become canonical.

### Historical Critic
Challenges source support, causation, chronology, terminology, priority, and historical motivation before canonical promotion. Every finding must have a stable, unique `id`.

### Human research resolution
Records the human decision on critic findings. A resolution is not reusable indefinitely: before promotion it must be bound to the exact packet and review content by SHA-256 fingerprints.

Run package-aware integrity tooling as modules from the repository root:

```text
python -m scripts.bind_resolution R002
```

If either the Research Packet or Historical Critic review later changes, the stored fingerprints become stale. The unit must be reviewed/rebound before promotion.

### Verified canonical promotion
Promotion must pass the integrity gate before any accepted correction is applied:

```text
python -m scripts.promote_verified R002
python -m scripts.promote_verified R002 --apply
```

`promote_verified.py` refuses promotion when:

- the resolution has no integrity binding;
- the packet fingerprint changed;
- the review fingerprint changed;
- review finding IDs are missing or duplicated;
- the resolution names a different packet or review file.

This prevents an old human resolution from being applied to a newer research artifact.

### Canonical layer
Stores durable entities, questions, and source-backed assertions. Canonical assertions must carry perspective, certainty, sources, and status.

### Canonical provenance map
For each promoted research unit, retain a machine-readable map under `research/promotions/` connecting Research Packet objects to their canonical IDs and, where applicable, Story steps. The purpose is auditability, not runtime rendering.

The expected chain is:

```text
Research Packet object
→ critic finding / human resolution
→ canonical entity/question/assertion
→ Story step assertion_refs
```

### Story Editor
Uses canonical data only. It creates a candidate editorial DAG whose steps contain `narrative`, `assertion_refs`, and `perspective`. Unsupported transitions become research gaps.

### Story Critic
Reviews the Story as narrative: sentence support, transition strength, perspective, causation, modern terminology, and branch/continuation semantics. It does not promote new facts.

### Human editorial review
Accepts, revises, or rejects Story Critic findings. A Story should not be treated as editorially complete merely because its underlying canonical facts are accepted.

## Required Story-step traceability

Every substantive Story step must contain:

```yaml
- id: r002-story-1
  ref: q-example
  role: Question
  narrative: >
    Reader-facing synthesis.
  assertion_refs:
    - assertion-example
  perspective: historical
```

The traceability chain is:

```text
Story step
→ canonical assertion_refs
→ canonical source IDs
→ persistent sources
```

Where a canonical assertion was promoted from a Research Packet, a promotion/canonical map should additionally retain:

```text
canonical assertion ID
→ Research Packet assertion / chronology / question reference
```

This second link is provenance, not runtime UI data.

## R002 acceptance gate

Before starting Story drafting for a second research unit, the workflow must support these repeatable operations without R001-specific code:

1. Produce a bounded Research Packet and Historical Critic review.
2. Require stable, unique finding IDs in the critic output.
3. Complete human research resolution.
4. Bind that resolution to the exact packet/review SHA-256 fingerprints.
5. Refuse promotion if either upstream artifact changes after binding.
6. Promote only human-accepted claims to canonical data.
7. Retain a canonical-promotion provenance map.
8. Generate a Story draft from canonical data with stable step IDs.
9. Run Story Critic against the draft and canonical assertions.
10. Resolve Story findings independently from research findings.
11. Validate that Story assertion references are non-dangling.
12. Build the SPA and open a stable deep link to the changed Story for mobile review.

## Editorial constraints

- `historical` must not be used for retrospective synthesis unsupported as a contemporary relation.
- `later_interpretation` must not be presented as the historical actors' own motivation.
- `modern_abstraction` must be visibly explanatory rather than attributed backward.
- `continues` is not a neutral visual connector; it asserts a stronger editorial continuity than `branches`.
- A smooth Story is never a reason to hide a research gap.
- Story prose may be rewritten without changing canonical facts; changing the facts requires returning to the research/canonical workflow.
