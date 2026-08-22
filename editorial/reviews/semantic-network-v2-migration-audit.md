# Semantic Network V2 — R001–R010 Migration Audit

Status: post-schema audit, before claim-by-claim semantic migration.

Source of truth for the exhaustive queues is generated `semantic-audit.json`. This review records the editorial conclusions that should survive regeneration.

## Snapshot

Current canonical assertion store contains **123 claims**.

- publishable (`historically_reviewed` / `accepted` / `published`): **121**
- research-only (`candidate` / `source_checked`): **2**
- Historical layer: **78**
- Mathematical layer: **4**
- Inquiry layer: **41**
- broad `contributed_to` publishable relations: **64**
- sufficiently typed default Network edges under the initial V2 projection: **18**
- unclassified predicates: **0**
- historical claims targeting a Concept that already has ConceptState records: **37**

The old Network's sparsity after Story lanes were removed was therefore not only a layout problem. Most reviewed connectivity was encoded either as editorial Inquiry relations or as intentionally broad `contributed_to` claims that are too weak to carry primary Network topology.

## Broad-relation concentration by research unit

| Unit | Broad publishable claims |
| --- | ---: |
| R001 | 1 |
| R002 | 8 |
| R003 | 3 |
| R004 | 5 |
| R005 | 8 |
| R006 | 6 |
| R007 | 11 |
| R008 | 7 |
| R009 | 9 |
| R010 | 6 |
| **Total** | **64** |

R007, R009, R002, and R005 are the highest-yield migration areas. This does **not** mean those packets are weak; it means the conservative canonical promotion vocabulary collapsed several distinct historical relations into `contributed_to`.

## Inquiry layer

**41 claims** touch a QuestionFrame and are now projected into the Inquiry layer rather than default Network topology.

This is an architectural correction, not a rejection of those claims. QuestionFrame transitions remain evidence-grounded and are central to Story, but they must not be mistaken for documentary transmission or mathematical dependency edges.

The two legacy core claims `assertion-heat-to-convergence` and `assertion-fourier-series-function` are also research-only candidates, so V2 reader projections exclude them entirely.

## ConceptState migration queue

There are **37 historical claims** whose object is a Concept that already has one or more ConceptState records.

Do not retarget these mechanically. A historical claim may concern:

- the specific historical state recorded for that period;
- the broader diachronic Concept identity;
- a relation that is too imprecise and should disappear from default topology;
- a Result or Problem that should be modeled instead.

R008 is especially valuable as a migration fixture because its 1870–1872 ConceptStates are already comparatively explicit.

## Migration classes

### A — Structural / low-risk

Changes that do not strengthen historical interpretation:

- preserve Person -> Work `authored` as documentary typed claims;
- expose ConceptState -> Concept `state_of` as structural identity edges;
- separate Inquiry claims from Network claims;
- enforce reader publishability boundary;
- preserve claim mode independently from semantic layer;
- annotate heterogeneous node temporal semantics.

These are implemented in PR #47.

### B — Predicate refinement with existing evidence

Broad claims whose source grounding likely supports a more precise relation, but which still require reopening the assertion/evidence pair before migration.

Typical candidates:

- Work -> ConceptState: `defines`, `uses`, `reformulates`, `develops`;
- Work -> Result: `proves` / `establishes`;
- Work -> Problem: `addresses`;
- Work -> Work: `revises`, `responds_to`, `cites`.

The migration should be claim-by-claim. Assertion IDs and source records should be preserved where possible.

### C — Attribution mediation

Person -> Concept `contributed_to` edges are usually poor default Network edges.

Preferred model when evidence exists:

```text
Person --authored/presented--> Work --typed relation--> ConceptState / Result / Problem
```

Do not fabricate a Work mediator when the source base does not support one. In that case the broad claim remains inspectable but secondary.

### D — Historical concept development

Concept -> Concept relations require special care. They may represent:

- historically documented development;
- historiographic reconstruction;
- modern mathematical generalization.

Claim mode and semantic layer must be checked independently before assigning a precise predicate.

### E — Research gap, not migration

If a desired Network edge cannot be stated more precisely from existing evidence, leave the edge broad/secondary or absent and register a research gap. Do not solve graph aesthetics by strengthening causation or transmission.

## Priority migration fixtures

1. **R008** — tests Work/ConceptState/Result semantics in a tightly documented 1870–1872 sequence while preserving the later-interpretive convergence entry.
2. **R010** — tests the distinction between historical Lebesgue relations, retrospective mathematical containment, and the absence of a fabricated Cantor -> Borel transmission chain.
3. **R009** — high concentration of broad relations; useful for Work revision and Concept development semantics.
4. **R007** — highest broad-relation count and a known missing Gauss -> Riemann transmission gap; useful for proving that an absent edge remains acceptable.
5. **R002/R005** — tests historiography, teaching/circulation, continuity/uniform convergence, and Person/Work mediation.

## UI consequence

Do not resume Network layout implementation merely because V2 now emits a graph.

The next Network UI must consume `semantic-network.json` and must treat:

- relation topology as primary;
- time as type-specific metadata/soft constraint;
- broad relations as progressively disclosed;
- Story selection as highlighting already-grounded nodes/claims rather than drawing Story-only lines.

## Human gate after refactor

PR #47 can merge once the V2 architecture and reader/research boundary are accepted. Claim-by-claim predicate refinement can then proceed in separate migration PRs, beginning with R008/R010 fixtures, without blocking the schema refactor itself.
