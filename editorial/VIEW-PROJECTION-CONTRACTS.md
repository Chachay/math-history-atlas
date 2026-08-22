# View Projection Contracts

The Atlas uses one shared evidence-backed knowledge base with multiple semantic layers and multiple view-specific projections.

Shared IDs, sources, claims, and mathematical objects persist across views. Coordinates, axis priority, node/edge prominence, disclosure policy, and even which semantic layer is primary are view concerns, not canonical facts.

See `editorial/SEMANTIC-NETWORK-V2.md` for the underlying ontology.

## Global rules

- Do not force shared coordinates across views.
- Preserve shared IDs and reviewed claim semantics across views.
- Do not flatten Historical, Mathematical, and Inquiry layers into one undifferentiated graph.
- Story membership and Story adjacency must not be interpreted as canonical Network topology.
- Historical, historiographic, and mathematical-retrospective claim modes must not collapse into one visual relation.
- Missing reviewed edges are meaningful and must not be replaced by proximity or layout continuity.
- Candidate and source-checked claims are research state, not reader-facing graph state.

## Atlas View

Primary question: **What developed?**

Primary structure: field-scale branching, recombination, and long-run development.

Temporal treatment: long chronology is strong.

Axis priority: chronology first, discipline/field structure second.

Node/edge emphasis: field paths and major branch points are primary; individual historical objects are secondary.

Story treatment: entry points into researched material, not layout lanes.

## Network View

Primary question: **What connects?**

Primary structure: evidence-backed Historical + Mathematical relation topology.

Default nodes:
- Person
- Work
- Problem
- Result
- ConceptState
- Concept identities where useful

QuestionFrames are not default Network nodes; they belong to the Inquiry layer.

Temporal treatment: time is node/claim metadata and a possible soft layout constraint. There is no universal strict chronological axis because Person birth years, Work publication dates, ConceptState periods, and Concept identities do not have equivalent temporal semantics.

Axis priority: relation topology first. Time and field are secondary constraints/filters.

Primary edges: publishable, sufficiently typed claims. Broad `contributed_to` associations remain inspectable but do not define default topology.

Story treatment: selecting a Story may highlight canonical nodes and reviewed claims used by that Story. It must not add a Story-only edge, move canonical nodes, or imply transmission/causation from narrative adjacency.

Progressive disclosure:

1. default typed Historical + Mathematical relations;
2. reveal broader/interpretive relations;
3. select Story to highlight grounded material already present in the graph;
4. inspect predicate / claim mode / certainty / status / source grounding when needed.

## Story View

Primary question: **Why did the question change?**

Primary structure: editorial QuestionFrame sequence grounded in reviewed historical/mathematical claims.

Temporal treatment: chronology is evidence and an ordering constraint, but narrative/inquiry order is primary.

Axis priority: narrative sequence first.

Node/edge emphasis: QuestionFrames and Story steps are primary; Story links express editorial transitions.

Story treatment: first-class narrative object.

A Story may locally treat a QuestionFrame as opening, continuing, branching, answered-for-story, handed off, or remaining open without manufacturing a canonical historical relation.

## Person View

Primary structure: attribution and participation around a focal Person within the Historical layer.

Temporal treatment: chronology is useful but subordinate to relevance around the Person.

Node/edge emphasis: Person is focal; authored Works and their reviewed Problems, Results, ConceptStates, and claims provide context.

Story treatment: navigation to curated readings that use claims connected to the Person.

Person proximity must never substitute for documentary transmission.

## Future Evidence View

Primary structure: Claim as a first-class inspection object.

A relation rendered as an edge in Network may be reified as a node here:

```text
subject -> Claim <- Source
           |
           v
         object
```

Primary metadata: predicate, semantic layer, claim mode, certainty, status, period, and source support.

Coordinates are optimized for inspection rather than historical narrative.

## Future Concept View

Primary structure: a focal Concept identity and its historically situated ConceptStates, Works, Results, and retrospective mathematical relations.

Concept may become the focal node in this projection even though Concept identity is not necessarily a strong positional object in Network.

## Implementation gate

A UI change conforms to these contracts only if its visual hierarchy preserves the distinctions between:

- shared knowledge base vs view projection;
- Historical / Mathematical / Inquiry semantic layers;
- evidence-backed Claim vs Story transition;
- Concept identity vs ConceptState;
- historical time vs editorial temporal anchoring;
- reader-facing reviewed claims vs research-state claims.
