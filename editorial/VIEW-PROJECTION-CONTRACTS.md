# View Projection Contracts

The Atlas uses one canonical heterogeneous graph and multiple view-specific projections.

Canonical identity and relation semantics are shared across views. Coordinates, axis priority, node/edge prominence, and disclosure policy are view concerns, not canonical facts.

## Global rules

- Do not force shared coordinates across views.
- Preserve shared IDs and reviewed relation semantics across views.
- Story membership must not be interpreted as canonical topology.
- Historical, later-interpretive, and modern-abstraction relations must not collapse into one visual relation.
- Missing reviewed edges are meaningful and must not be replaced by proximity or layout continuity.
- A view must state what question it answers for the reader; node and edge prominence follow that contract.

## Atlas View — What developed?

Primary structure: field-scale mathematical development, branching, and recombination.

Temporal treatment: long chronology.

Axis priority: chronology first, discipline/field structure second.

Node/edge emphasis: field paths and major branch points are primary; individual historical objects are secondary.

Reader question: what mathematical areas, objects, and practices developed, where in the mathematical landscape, and when?

Story treatment: entry points into researched material, not layout lanes.

## Network View — What connects?

Primary structure: reviewed relation topology across the canonical heterogeneous graph.

Reader question: what is connected to what, and in what reviewed sense?

Temporal treatment: chronology remains available and visually important, but it must not suppress relation topology.

Axis priority: relation topology first; chronology constrains and orients the layout rather than defining a single narrative path.

Peer node classes: Question, Work, Concept, and Person. Their visual forms differ by role, but no one class is the universal backbone of Network.

Primary edges: reviewed canonical relations among those heterogeneous nodes. Predicate, perspective, certainty, and status carry meaning. A Work or Concept becoming a hub is a valid Network finding rather than layout noise.

Story treatment: optional overlay/path through a stable relation graph. Story selection must not move canonical nodes and must not manufacture canonical relations.

Editorial projection edges may be used only as explicitly secondary aids where a Story records a path not yet represented by a canonical assertion. They must never become the default topology or be visually confusable with reviewed relations.

Progressive disclosure should reduce density without changing ontology: filters may hide node or relation classes, but the default Network should communicate heterogeneous connectivity rather than a Question-only forest.

## Story View — Why did the question change?

Primary structure: editorial Question evolution and explanatory sequence.

Reader question: why did a mathematical question change, branch, become sharper, or hand off to another question?

Temporal treatment: chronology is metadata and an ordering constraint, but narrative order is primary.

Axis priority: narrative sequence first.

Node/edge emphasis: Story steps are primary; links explain editorial transitions. Work, Concept, and Person provide the historical mechanism and context for Question evolution.

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

Concept becomes the primary node because the projection asks a Concept-centered question, not because Concept is globally primary in the canonical graph.

## Implementation gate

A UI change conforms to these contracts only if its visual hierarchy preserves the distinction between canonical graph structure, editorial Story structure, and layout-only decisions.

For the current redesign, the acceptance shorthand is:

- Atlas = What developed?
- Network = What connects?
- Story = Why did the question change?

A Network implementation that defaults to Question-only topology fails this contract even if Story lanes have been removed.