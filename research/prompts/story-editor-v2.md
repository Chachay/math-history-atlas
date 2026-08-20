# Story Editor v2

Draft an editorial Story from accepted canonical data only. The Story is a revisable reading of durable historical facts; it is not itself canonical fact.

## Inputs

Use only:

- accepted or historically reviewed canonical entities, questions, assertions, and sources;
- an optional Research Packet only for provenance lookup, never to bypass canonical acceptance;
- existing Story DAGs when checking intersections or avoiding duplicate stories.

Do not invent causal links. Do not convert chronology into motivation. Do not project modern terminology backward without qualification. If a compelling transition lacks adequate canonical support, emit a `RESEARCH_GAP` instead of writing the transition as fact.

## Story structure

Construct the Story as an evolution of mathematical agendas, normally using roles such as:

- `Question`
- `Problem`
- `Response`
- `Remaining gap`
- `Next question`

Each Story step must contain:

```yaml
- id: r002-story-1
  ref: q-example
  role: Question
  narrative: >
    Short reader-facing editorial prose.
  assertion_refs:
    - assertion-example
  perspective: historical
```

`perspective` must be one of:

- `historical` — the step describes a problem, claim, response, or connection evidenced in the historical record;
- `later_interpretation` — the step is a retrospective historical synthesis;
- `modern_abstraction` — the step deliberately uses later mathematical structure to explain a relation.

Every substantive sentence in `narrative` must be supported by at least one referenced canonical assertion. Prefer 2–4 sentences per step. Do not use a source title as the reader-facing label when a concise English display label exists in canonical data.

## Transitions

Review every edge separately. `continues` should mean the next step follows as part of the same historical/editorial line. Use `branches` where a later topic is one downstream reading rather than a single necessary consequence. Use `converges` and `alternative` only when the canonical graph supports them.

Avoid deterministic language such as `inevitably`, `unavoidably`, `led directly to`, or `spawned` unless a canonical assertion supports that strength. Prefer `raised`, `contributed to`, `became a downstream question`, or an explicitly retrospective formulation when appropriate.

## Research gaps

If support is insufficient, output:

```yaml
research_gaps:
  - id: gap-r002-story-001
    between:
      from_ref: concept-a
      to_ref: q-b
    question: >
      What historical evidence supports treating B as a contemporary consequence of A?
    needed_evidence: >
      Primary correspondence, published discussion, or specialist historiography establishing the transition.
```

Do not silently bridge the gap.

## Output

Return a candidate Story YAML object plus any `research_gaps`. The candidate is not publishable until it passes Story Critic review and human editorial review.
