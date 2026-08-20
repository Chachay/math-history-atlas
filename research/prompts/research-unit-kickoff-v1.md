# Research Unit Kickoff v1

Use this prompt to start a new research unit in a fresh ChatGPT conversation with access to the repository.

## Inputs

- Repository: `Chachay/math-history-atlas`
- Unit ID: `R00X`
- Optional topic hint: `<topic hint or leave blank>`

## Mission

Take one new bounded research unit from topic selection through **Phase A and Phase B**, using the repository's current workflow and schemas. Do not merge the final PR. The human reviews critic findings and the mobile preview before merge.

## First action: recover repository state

Before proposing a topic or editing files:

1. Read `README.md`.
2. Read `editorial/WORKFLOW.md`.
3. Read the current schemas and validators in `scripts/models.py` and `scripts/validate.py`.
4. Inspect current canonical entities/questions/assertions, current Stories, and the most recent completed research units.
5. Read these prompts:
   - `research/prompts/cluster-research-v1.md`
   - `research/prompts/historical-critic-v1.md`
   - `research/prompts/story-editor-v2.md`
   - `research/prompts/story-critic-v1.md`
6. Inspect the latest Network/Story semantics before drafting. In particular, Story steps may carry Story-local temporal anchors; entity birth/start dates are not automatically the date at which an entity appears in a Story.

Do not rely on remembered repository state when the current `main` branch can be read.

## Topic selection

If the user supplied a topic, test whether it is bounded and useful for the graph before proceeding.

If no topic was supplied, propose 2–3 candidates based on the **current graph**, preferring a unit that:

- intersects at least one accepted/researched node from an existing Story;
- introduces a genuinely new question/problem/concept line rather than merely extending a biography;
- creates a useful branch, convergence, or cross-Story intersection;
- is narrow enough to research with primary and specialist secondary sources;
- helps expose weaknesses in the graph/editorial model without choosing a topic merely for UI convenience.

Do not infer causation merely because the new unit follows an existing one chronologically.

Wait for human approval of the topic if more than one materially different direction is plausible.

## Phase A — Research to canonical promotion

### A1. Branch and packet

Create a dedicated branch from current `main`, normally:

```text
research/r00x-<short-topic-slug>
```

Run the research process defined by `cluster-research-v1.md` and save a bounded packet under `research/packets/`.

The packet must distinguish:

- contemporary historical claims;
- later historical interpretation;
- modern mathematical abstraction;
- chronology/date type where relevant;
- uncertainty and source gaps.

Normalize persistent sources. Web search is discovery, not persistent evidence.

### A2. Independent Historical Critic

Apply `historical-critic-v1.md` adversarially. Attempt to falsify claims and transitions rather than improve prose.

Every finding must have a stable unique `id` and classification:

- `PASS`
- `REVISE`
- `WEAK_EVIDENCE`
- `REJECT`

For actionable non-PASS findings, provide machine-actionable `target` / `proposed_change` only when safe.

### A3. Human research resolution

Present only the material non-PASS findings to the user, with a concise recommendation for each. Do not silently accept critic findings on the user's behalf.

After the user decides, record the human resolution.

### A4. Integrity binding and verified promotion

Bind the resolution to the exact packet/review fingerprints using the repository tooling. Refuse stale or incomplete promotion.

Promote only human-accepted material to canonical data. Reuse existing canonical IDs when the historical object/question is genuinely the same; do not create duplicates simply because the research unit is new.

Retain a machine-readable canonical provenance map under `research/promotions/`.

Before Story drafting, verify:

```text
Research Packet
→ Historical Critic
→ Human resolution
→ integrity binding
→ canonical object/assertion
```

## Phase B — Story drafting and editorial criticism

### B1. Story draft

Use `story-editor-v2.md` against canonical data only.

Each substantive Story step must carry:

- stable step ID;
- canonical `ref`;
- role;
- reader-facing narrative;
- `assertion_refs`;
- `perspective`;
- Story-local temporal anchor when required by the current schema/workflow.

The Story is a DAG. Use `continues`, `branches`, `converges`, `alternative`, or other currently allowed link types according to their semantic meaning. A smooth line is not evidence of historical continuity.

Do not make a Story line move backward in historical time merely because a referenced Concept or Person originated earlier. If the Story intentionally looks backward, use the repository's explicit retrospective semantics rather than hiding the reversal.

### B2. Story Critic

Apply `story-critic-v1.md` independently. Check:

- sentence-level assertion support;
- causation vs chronology;
- modern terminology projected backward;
- perspective;
- Story-link semantics;
- temporal ordering;
- missing intermediaries;
- whether a purported branch/convergence is actually evidenced.

Present material non-PASS findings to the human. Apply only explicitly resolved editorial revisions.

If Story links or temporal anchors change after Story Critic, invalidate or re-run the affected transition review rather than pretending the earlier review still covers the new DAG.

## Validation and preview

Before declaring Phase B complete:

1. Run repository validation/tests/build through CI or available tooling.
2. Confirm the changed Story's canonical provenance is non-dangling.
3. Confirm chronological Story-link validation passes.
4. Confirm SPA build passes.
5. Open a PR to `main` and obtain the mobile PR Preview.
6. Give the user direct links to the changed Story and its Network context.

Do not say CI is green unless the latest head checks were actually read.

## Stop condition

Stop with the PR open for human/mobile review. Do **not** merge unless the user explicitly asks.

Report:

- research unit title and period;
- critic summary;
- unresolved research gaps;
- canonical additions/reused nodes;
- Story title and important intersections;
- Story Critic summary;
- latest CI status;
- PR and direct preview links.

## Hard historical constraints

Across all units:

- chronology alone does not establish influence or motivation;
- `motivated`, `spawned`, `influenced`, and priority claims require stronger evidence than mathematical relatedness;
- do not silently translate historical definitions into modern set-theoretic, epsilon-delta, spectral, topological, or other later abstractions;
- distributed developments should not be collapsed into single-person invention stories;
- intermediary people/works/results should be added when historically necessary;
- modern mathematical relation and historical motivation are separate claims;
- uncertain evidence remains an explicit research gap rather than being smoothed into narrative.

## Minimal fresh-chat command

After this prompt exists on `main`, a user should be able to start a new conversation with only:

```text
Open Chachay/math-history-atlas and follow research/prompts/research-unit-kickoff-v1.md for R003. Read current main first, then propose the research theme.
```

For the next unit, replace `R003` with `R004`.