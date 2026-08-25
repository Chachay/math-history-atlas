# Story Semantic Map / Focus Interaction Contract

## Decision

Keep three reader views: **Atlas**, **Network**, and **Story**. `Focus` is not a fourth view. It is a shared interaction that selects and expands a local semantic region while preserving the current view's purpose.

- **Atlas — landscape:** where in mathematics to enter.
- **Network — structure:** what is connected to what, without a privileged editorial path.
- **Story — journey:** which local path matters for a question, and why.
- **Focus — interaction:** expand the selected semantic object without discarding surrounding context.

## Shared semantic substrate

All three views consume canonical semantic projections. They must not invent historical causation from chronology or UI geometry.

Concept identities bridge scales:

`Field -> Concept -> ConceptState -> Work / Problem / Result`

ConceptState chronology is descriptive. A state-to-state development arrow requires an explicit reviewed publishable development claim.

## Story formula

`Story map = local semantic projection + QuestionFrames + editorial spine`

The Story spine is not canonical Network topology. It privileges a researched question path over a local semantic map while leaving nearby branches visible as context.

### Story map behavior

- The editorial spine is visually primary.
- Canonical semantic relations near the spine remain visible but secondary.
- QuestionFrames annotate why the spine moves; they are not default semantic nodes.
- Selecting a nearby branch focuses/expands it without silently rewriting the Story spine.
- A reader can return to the Story spine after exploring a branch.
- Story nodes and edges must resolve to reader labels; internal research IDs never appear.

## Focus is type-sensitive

Do not implement Focus as a universal `one node + one hop` card.

### Concept focus

Show a **diachronic evolution window**:

- Concept identity as the anchor.
- Multiple attested ConceptStates together, ordered by time.
- Work / Problem / Result branches attached to relevant states.
- Explicit evidence-bearing development transitions when available.
- No inferred causal arrows from chronology alone.

### Work focus

Show a **semantic neighborhood** around the historically situated Work:

- problems addressed,
- results,
- concept states / mathematical content,
- documentary or development relations when reader-relevant.

### Problem focus

Show a **response structure**:

- works that address it,
- results that resolve or sharpen it,
- related concept states,
- later problems only where supported by canonical relations.

### Result focus

Show **origin and mathematical consequences/dependencies** supported by canonical relations.

### Person focus

Person is an access point to Works, not the mathematical center of the map.

## Junctions / intersections

A junction is not merely a high-degree node. It is a local region where distinct semantic or conceptual threads meet.

The UI should express junctions through a local semantic map rather than a long adjacency list. Story view additionally shows which route through the junction belongs to the editorial spine.

Example:

```
                  convergence
                       |
representation == Function -- integration
                       ||
                 function scope
```

`==` / `||` indicate the Story spine only in this schematic; they are not new predicates.

For Concept focus, time is the primary spine and semantic branches cross it. For Work focus, semantic relations are primary and time situates the Work. A single layout must not be forced onto all node kinds.

## Network

Network remains the unprivileged semantic structure view. A full overview may remain available as a secondary orientation map, but the reader's main interaction should be local semantic expansion with context preserved.

Network must not turn Story QuestionFrame transitions into semantic edges.

## Atlas

Atlas is a coarse-grained projection of the same substrate, not a hard-coded field illustration. It aggregates Field -> Concept -> ConceptState and exposes entry points into the semantic map. Cross-field Concepts should be visible as bridges rather than duplicated independent objects.

## Navigation history

Breadcrumb/history records the reader's actual exploration path. It is neither canonical graph truth nor Story editorial structure.

## Reader-facing relation vocabulary

Canonical predicates remain precise internally. Reader UI groups them into a small number of semantic categories such as Problems, Mathematical ideas, Results, Earlier/later developments, and Works/attribution. Raw predicates should appear only where they materially aid interpretation.

## Implementation sequence

1. Generate Concept evolution and semantic Atlas projections from canonical data.
2. Centralize graph queries and reader relation grouping.
3. Build a reusable **LocalSemanticMap** component with type-sensitive projections.
4. Integrate LocalSemanticMap into Story first: editorial spine + nearby semantic branches.
5. Reuse it in Network without the editorial spine.
6. Replace hard-coded Atlas branches with semantic aggregation and Concept entry points.
7. Keep full Network overview as optional orientation, not the primary reading surface.

## Acceptance criteria

- Story retains a readable question-driven spine while exposing nearby semantic branches.
- Selecting Function or another Concept shows multiple historical states together rather than one-hop replacement.
- A junction shows multiple threads simultaneously and makes the Story-selected route distinguishable.
- Network and Story reuse the same semantic local-map component; only the editorial overlay differs.
- Atlas Concept entry points resolve to the same Concept identities used by Network/Story.
- No internal IDs, editorial caveats, or unsupported causal arrows appear in reader UI.
