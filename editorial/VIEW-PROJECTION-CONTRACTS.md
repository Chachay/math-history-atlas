# View Projection Contracts

The Atlas uses one canonical heterogeneous graph and multiple view-specific projections.

Canonical identity and relation semantics are shared across views. Coordinates, axis priority, node/edge prominence, and disclosure policy are view concerns, not canonical facts.

## Global rules

- Do not force shared coordinates across views.
- Preserve shared IDs and reviewed relation semantics across views.
- Story membership must not be interpreted as canonical topology.
- Historical, later-interpretive, and modern-abstraction relations must not collapse into one visual relation.
- Missing reviewed edges are meaningful and must not be replaced by proximity or layout continuity.

## Atlas View

Primary structure: field-scale branching and recombination.

Temporal treatment: long chronology.

Axis priority: chronology first, discipline/field structure second.

Node/edge emphasis: field paths and major branch points are primary; individual historical objects are secondary.

Story treatment: entry points into researched material, not layout lanes.

## Network View

Primary structure: reviewed relation topology, with Question-to-Question evolution as the default reader-facing spine.

Temporal treatment: chronology remains the strong axis.

Axis priority: time first; branch/continuation/convergence topology second.

Primary nodes: Question.

Contextual nodes: Work and Concept.

Navigational nodes: Person.

Primary edges: reviewed canonical relations needed to understand Question evolution.

Story treatment: overlay/path through a stable graph. Story selection must not move canonical nodes.

Progressive disclosure:

1. default Question spine + strongest reviewed relations;
2. expand Work / Concept / Person context;
3. select Story to highlight an editorial route;
4. inspect predicate / perspective / certainty / source grounding when needed.

## Story View

Primary structure: editorial sequence.

Temporal treatment: chronology is metadata and an ordering constraint, but narrative order is primary.

Axis priority: narrative sequence first.

Node/edge emphasis: Story steps are primary; links explain editorial transitions.

Story treatment: first-class narrative object.

A Story may locally treat a canonical Question as opening, continuing, branching, answered-for-story, handed off, or remaining open without changing the global canonical Question.

## Person View

Primary structure: attribution and participation around a focal Person.

Temporal treatment: chronology is useful but subordinate to relevance around the Person.

Node/edge emphasis: Person is primary; related Works, Concepts, Questions, and accepted assertions provide context.

Story treatment: navigation to curated readings that include the Person.

Person proximity must never substitute for documentary transmission.

## Future Evidence View

Primary structure: assertion semantics and evidence grounding.

Primary edges: predicate, perspective, certainty, status, period, and source support.

Coordinates are optimized for inspection rather than historical narrative.

## Future Concept View

Primary structure: a focal mathematical Concept and its historical uses, reformulations, generalizations, and Question relations.

Concept may become the primary node in this projection even though Question is primary in the default Network.

## Implementation gate

A UI change conforms to these contracts only if its visual hierarchy preserves the distinction between canonical graph structure, editorial Story structure, and layout-only decisions.
