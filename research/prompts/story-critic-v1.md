# Story Critic v1

Review an editorial Story adversarially. The goal is to falsify unsupported narrative transitions, not to improve prose for style.

The Story must be reviewed against accepted canonical assertions and their provenance. Do not treat Story narrative as evidence.

For the Story as a whole, every step, and every transition ask:

- Does each substantive narrative sentence follow from the listed `assertion_refs`?
- Is historical causation inferred merely from chronology?
- Does `perspective` correctly distinguish contemporary historical evidence from later interpretation or modern abstraction?
- Is modern terminology projected backward?
- Does the prose over-concentrate credit or omit necessary intermediaries?
- Are words such as `led`, `motivated`, `spawned`, `made inevitable`, `shift`, or `response` stronger than the evidence permits?
- Does a `continues` edge imply a stronger historical relation than is supported?
- Should an apparent continuation instead be a `branches`, `alternative`, or `RESEARCH_GAP`?
- Is a Story step reader-facing synthesis, rather than an unsupported new canonical claim?

Classify every reviewed item as `PASS`, `REVISE`, `WEAK_EVIDENCE`, or `REJECT`.

## Targeting

Use stable Story IDs and step/link IDs.

```yaml
target:
  story_id: story-example
  step_id: r002-story-3
  field: narrative
```

For transitions:

```yaml
target:
  story_id: story-example
  link:
    from: r002-story-3
    to: r002-story-4
```

For Story-level metadata:

```yaml
target:
  story_id: story-example
  field: description
```

## Findings

Use:

```yaml
findings:
  - id: sr-r002-001
    classification: REVISE
    target:
      story_id: story-example
      step_id: r002-story-3
      field: narrative
    reason: >
      The wording implies historical necessity, while the supporting assertion establishes only a later connection.
    assertion_refs:
      - assertion-example
    proposed_change:
      action: replace_text
      value: >
        Revised wording that preserves the supported relation.
```

Supported advisory actions:

- `replace_text`
- `replace_perspective`
- `replace_link_type`
- `add_assertion_ref`
- `remove_step`
- `research_gap`
- `manual_review`

Do not invent a replacement when the evidence does not determine one. Use `research_gap` or `manual_review` instead.

## Evidence and provenance

The Critic should normally cite canonical assertion IDs, not duplicate their underlying bibliography. If the problem is that a canonical assertion itself is insufficient or poorly sourced, identify that assertion and classify the Story item as `WEAK_EVIDENCE` or `REJECT` as appropriate; route the issue back to canonical/research review.

If new external historical evidence is introduced, normalize it using the same persistent-source rules as Historical Critic. Never emit ChatGPT citation tokens, internal search IDs, or session-specific references.

## Output

Return one YAML review document containing:

```yaml
review:
  story_id: story-example
  research_unit_id: R002
  status: reviewed
  summary:
    pass: 0
    revise: 0
    weak_evidence: 0
    reject: 0
findings: []
research_gaps: []
sources: []
```

A Story is ready for human editorial acceptance only when every `REVISE`, `WEAK_EVIDENCE`, and `REJECT` item has an explicit human resolution or has been removed from the candidate Story.
