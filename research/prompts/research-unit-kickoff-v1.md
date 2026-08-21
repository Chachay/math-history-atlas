# Research Unit Kickoff v1

Use this prompt to start a new research unit in a fresh ChatGPT conversation with access to the repository.

## Inputs

- Repository: `Chachay/math-history-atlas`
- Unit ID: `R00X`
- Optional topic hint: `<topic hint or leave blank>`
- Optional approved unit brief: `research/units/R00X-*.md`

## Mission

Take one new bounded research unit from topic selection through **Phase A and Phase B**, using the repository's current workflow and schemas. Do not merge the final PR. The human reviews critic findings and the mobile preview before merge.

## First action: recover repository state

Before proposing a topic or editing files:

1. Read `README.md`.
2. Read `editorial/WORKFLOW.md`.
3. Read `research/EXTERNAL-CONTEXT-GUIDELINE.md` when it exists. Apply it whenever a unit involves physics, engineering, astronomy, computation, economics, or another domain outside mathematics.
4. Read the current schemas and validators in `scripts/models.py` and `scripts/validate.py`.
5. Inspect current canonical entities/questions/assertions, current Stories, and the most recent completed research units.
6. Read these prompts:
   - `research/prompts/cluster-research-v1.md`
   - `research/prompts/historical-critic-v1.md`
   - `research/prompts/story-editor-v2.md`
   - `research/prompts/story-critic-v1.md`
7. Inspect the latest Network/Story semantics before drafting. In particular, Story steps may carry Story-local temporal anchors; entity birth/start dates are not automatically the date at which an entity appears in a Story.
8. Check `research/units/` for a file whose name begins with the requested unit ID, e.g. `R003-*.md`. If exactly one approved brief exists, read it and treat its scope/integration target as the default topic unless current `main` makes the brief stale or contradictory. If several briefs exist, ask which one to use. If none exists, use the topic-selection procedure below.
9. When artifacts for the unit already exist, run or inspect `python -m scripts.research_unit_status R00X` before deciding what stage to resume.

Do not rely on remembered repository state when the current `main` branch can be read.

## Topic selection

If an approved unit brief exists, first test whether it is still bounded and compatible with current `main`. Do not re-open broad topic selection merely because another plausible topic exists. Raise a scope issue only if the brief has become stale, duplicates newly merged work, or conflicts with current canonical data.

If the user supplied a topic but no approved brief exists, test whether it is bounded and useful for the graph before proceeding.

If neither a topic nor an approved brief exists, propose 2–3 candidates based on the **current graph**, preferring a unit that:

- intersects at least one accepted/researched node from an existing Story;
- introduces a genuinely new mathematical question/problem/concept line rather than merely extending a biography;
- creates a useful branch, convergence, or cross-Story intersection;
- is narrow enough to research with primary and specialist secondary sources;
- helps expose weaknesses in the graph/editorial model without choosing a topic merely for UI convenience.

When an external scientific/engineering context is involved, keep the proposed Atlas Question mathematical. State the external context, mathematical response, Atlas Question, historical test, and retrospective-risk test separately. Do not make a physics or engineering problem the main Question merely because it motivated the historical work.

Do not infer causation merely because the new unit follows an existing one chronologically.

Wait for human approval of the topic if more than one materially different direction is plausible and no approved brief already fixes the scope.

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

For units involving an external domain, the packet must also distinguish the external historical problem from the mathematical method and from the mathematical Question that the Atlas follows. Treat the claimed outside → inside transition as a research claim, not as framing that is exempt from criticism.

Normalize persistent sources. Web search is discovery, not persistent evidence.

Before the packet enters criticism or human review, run the artifact gate:

```text
python -m scripts.check_research_artifact research/packets/R00X-....yaml
```

No malformed or structurally unresolved artifact should enter a semantic review gate.

### A2. Independent Historical Critic

Apply `historical-critic-v1.md` adversarially. Attempt to falsify claims and transitions rather than improve prose.

Every finding must have a stable unique `id` and classification:

- `PASS`
- `REVISE`
- `WEAK_EVIDENCE`
- `REJECT`

For actionable non-PASS findings, provide machine-actionable `target` / `proposed_change` only when safe.

After saving the review, run the artifact gate again:

```text
python -m scripts.check_research_artifact research/reviews/R00X-....yaml
```

This must verify review IDs, source references, and current packet targets before the human-resolution gate.

### A3. Human research resolution

Present only the material non-PASS findings to the user, with a concise recommendation for each. Do not silently accept critic findings on the user's behalf.

After the user decides, record the human resolution.

### A4. Integrity binding and verified promotion

Bind the resolution to the exact packet/review fingerprints using the repository tooling. `bind_resolution` performs semantic resolution validation before writing fingerprints and must refuse stale, incomplete, or unresolvable decisions.

Run package-aware integrity tooling as modules from the repository root:

```text
python -m scripts.bind_resolution R00X
python -m scripts.promote_verified R00X
python -m scripts.promote_verified R00X --apply
```

For smartphone/connector-centered operation, use the permanent **Research Unit Ops** GitHub Actions workflow rather than adding a unit-specific temporary workflow. It accepts a unit ID, target ref, and operation (`status`, `check`, `bind`, `promote-dry-run`, or `promote-apply`) and delegates semantics to repository Python modules.

Do not invoke `bind_resolution.py` or `promote_verified.py` by file path in CI runners; both import the `scripts` package and must retain the repository root on Python's module search path.

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

Use `python -m scripts.research_unit_status R00X` as a read-only audit of the current gate; it must not replace human judgment.

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

For externally motivated episodes, explain only enough of the outside domain to establish the historical stakes. Move the reader onto the mathematical Question rather than turning the Story into an application tutorial.

### B2. Story Critic

Apply `story-critic-v1.md` independently. Check:

- sentence-level assertion support;
- causation vs chronology;
- modern terminology projected backward;
- perspective;
- Story-link semantics;
- temporal ordering;
- missing intermediaries;
- whether a purported branch/convergence is actually evidenced;
- for external-context episodes, whether the Story overstates motivation or turns a later mathematical relation into historical influence.

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
- uncertain evidence remains an explicit research gap rather than being smoothed into narrative;
- external scientific or engineering problems may explain historical context, but the Atlas Question spine remains mathematical unless the project explicitly changes scope.

## Minimal fresh-chat command

If the unit has an approved brief in `research/units/`, the user should be able to start a new conversation with only:

```text
Open Chachay/math-history-atlas and follow research/prompts/research-unit-kickoff-v1.md for R003. Read current main and use the approved R003 brief in research/units/.
```

For the next unit, replace `R003` with `R004`.
