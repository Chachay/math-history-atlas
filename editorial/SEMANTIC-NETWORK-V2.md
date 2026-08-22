# Semantic Network V2

Status: migration architecture for post-R010 refactor.

This document defines the knowledge model before any new Network UI specification. The repository keeps one shared evidence base, but no longer assumes that every object and every relation belongs to one flat canonical graph.

## Product-level separation

- **Atlas** asks: what mathematical fields and bodies of work developed, and when?
- **Network** asks: what historical and mathematical objects are connected, and by what reviewed relation?
- **Story** asks: why did a mathematical question change into another question?

The three views share IDs, sources, claims, and mathematical objects. They do not share a single visual topology.

## Semantic layers

### Historical layer

Represents evidence-backed relations among historical actors, works, problems, results, and historically situated mathematical content.

Typical nodes:
- Person
- Work
- Event
- Problem
- Result
- ConceptState
- Concept identity when no reviewed state has yet been modeled

Typical claims:
- Person authored Work
- Work addressed Problem
- Work defined or used a ConceptState
- Work proved Result
- Work revised/responded-to/cited Work

A historical relation is not inferred from temporal proximity.

### Mathematical layer

Represents retrospective structural relations that are mathematically valid but are not automatically historical transmission or historical motivation.

Typical nodes:
- Concept
- ConceptState
- Result

Typical claims:
- one concept generalizes another
- a result depends on a concept
- a result strengthens another result

Current `modern_abstraction` claims project here.

### Inquiry layer

Represents editorial QuestionFrames used to organize reader-facing problem history.

A QuestionFrame is not assumed to be a verbatim historical question. It is an editorial formulation grounded by reviewed claims and sources.

Typical relations:
- continues
- branches
- converges
- retrospective handoff

QuestionFrame evolution belongs to Story/inquiry semantics, not to the default semantic Network topology.

## Claim mode is orthogonal to semantic layer

The existing `perspective` distinction remains valuable, but it answers a different question from semantic layer.

| Legacy perspective | V2 claim mode | Meaning |
| --- | --- | --- |
| historical | historical | claim about historical activity or meaning |
| later_interpretation | historiographic | later historical interpretation or reconstruction |
| modern_abstraction | mathematical_retrospective | modern mathematical structural relation |

A historiographic claim may still concern the Historical layer. For example, a later historian may connect two historical works without that connection becoming a modern mathematical relation.

## Core ontological distinction: Problem vs QuestionFrame

`Problem` is a historical/mathematical object: a task, obstacle, or problem situation that existed in the historical material.

`QuestionFrame` is an editorial reader-facing formulation used to organize inquiry.

They may be linked by evidence, but they are not interchangeable.

The existing files under `data/questions/` are treated as QuestionFrames during migration. Their IDs are preserved.

## Core ontological distinction: Concept vs ConceptState

`Concept` is a diachronic identity used to connect meanings across time.

`ConceptState` is a historically situated formulation/meaning of that concept.

Example pattern:

```text
Work (1872) --defines/uses--> ConceptState (1872) --state_of--> Concept
```

Historical assertions should increasingly target ConceptState when a reviewed historical state exists. V2 does **not** automatically rewrite legacy Work/Person -> Concept assertions, because that would strengthen historical interpretation without review.

## Claims are typed evidence-bearing relations

Every canonical relation is a Claim with:

- subject
- predicate
- object
- temporal scope
- claim mode / legacy perspective
- certainty
- evidence sources
- review status
- semantic layer
- relation family

The current assertion store is retained during migration, but V2 normalizes it into these dimensions at build time.

## Relation families

Initial migration families:

- `documentary`: authorship and document-level facts
- `problem_relation`: raised/motivated/spawned problem relations
- `development`: reframed/generalized/split/merged
- `transmission`: influenced
- `broad_association`: contributed_to
- `inquiry`: any claim whose endpoint is a QuestionFrame
- `identity`: structural ConceptState -> Concept relation

`contributed_to` remains queryable, but is deliberately excluded from the **default Network topology**. It is too semantically broad to carry the visual meaning of a primary graph edge.

The migration must prefer an absent edge over inventing a stronger relation.

## Domain/range rules

V2 begins enforcing relation typing incrementally.

Currently enforced:

- `authored`: Person -> Work
- `ConceptState.state_of`: ConceptState -> Concept

Future predicates should declare domain/range before being admitted to the canonical Network vocabulary.

Legacy predicates that cannot yet meet a precise contract remain available to evidence/research tools but need not be reader-facing edges.

## Publishability boundary

Research state and reader state are different.

Reader-facing projections accept only:

- `historically_reviewed`
- `accepted`
- `published`

They exclude:

- `candidate`
- `source_checked`

This fixes the legacy behavior in which `graph.json` could expose candidate claims to the UI merely because they existed in canonical assertion files.

## Generated projections

During migration the build produces four graph artifacts.

### `graph.json`

Legacy compatibility aggregate. Kept temporarily so existing UI/research tooling does not silently change behavior.

### `semantic-network.json`

Reader-facing Historical + Mathematical semantic graph.

Contains:
- Entity nodes
- ConceptState nodes
- publishable non-inquiry claims
- structural ConceptState -> Concept edges
- `default_edge_ids` for sufficiently typed primary relations

QuestionFrames are absent.

### `inquiry-graph.json`

Reader-facing editorial inquiry graph.

Contains:
- QuestionFrames
- publishable claims touching QuestionFrames

Story remains responsible for narrative sequence.

### `research-claims.json`

All normalized claims, including non-publishable research claims. This is for review/debugging, not default reader presentation.

### `semantic-audit.json`

Migration queues derived from current canonical data:

- broad publishable relations
- inquiry-layer claims currently stored as assertions
- unpublished research claims
- unclassified relation types
- historical claims targeting Concepts that already have ConceptState records

## Temporal semantics

There is no universal node `start_year` semantics.

- Person: birth/death
- Work: composition/presentation/publication depending on record
- Event: event interval
- Problem: period of active formulation/attention
- Result: proof/presentation/publication depending on record
- ConceptState: attested historical interval
- Concept: diachronic identity; a single birth year should not determine Network coordinates
- QuestionFrame: editorial temporal anchoring, not necessarily a historical event date

Therefore the V2 Network must not use one strict chronological axis across all node types.

## Story boundary

Story links are editorial narrative transitions. They must never be rendered as if they were canonical historical edges merely because two Story steps are adjacent.

Selecting a Story in Network may highlight canonical nodes/claims used by that Story. It must not create new causal/transmission edges in the semantic graph.

## Source vs Work

A `Work` is a historical object. A `Source` is an evidence record/edition/bibliographic witness used to support a claim.

These should remain distinct. A future migration should add an explicit witness/edition relation between Source records and Work objects where useful.

## Migration policy

1. Preserve existing IDs.
2. Do not strengthen historical claims mechanically.
3. Introduce semantic projections before destructive canonical rewrites.
4. Use `semantic-audit.json` to prioritize human-reviewed migration.
5. Move QuestionFrame evolution out of default Network topology.
6. Prefer ConceptState endpoints for historical content only after evidence review.
7. Replace or retire `contributed_to` incrementally when a more specific relation is justified.
8. Only after semantic migration stabilizes should Network UI layout be redesigned.

## Acceptance gate for V2 model

Before Network UI work resumes:

- candidate/source_checked claims are absent from reader projections;
- QuestionFrames are absent from default semantic Network;
- ConceptStates are first-class semantic nodes;
- broad relations are not primary default edges;
- relation family and claim mode are independently inspectable;
- Story adjacency cannot manufacture Network edges;
- R008 and R010 remain representable without inventing undocumented causal bridges;
- the migration audit identifies remaining legacy ambiguities rather than hiding them.
