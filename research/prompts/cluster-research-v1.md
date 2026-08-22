# Cluster Research v1
Investigate `[TOPIC]` during `[PERIOD]` for a structured interactive history of modern mathematics. Do not write a conventional biography. Extract the problems researchers were actually trying to solve, how reader-facing questions should be framed, important people/works/concepts/results/events, developments that answered or created problems, intersections of research lines, and concepts whose historical meaning differs from modern usage.

Distinguish `historical`, `later_interpretation`, and `modern_abstraction`. Never project later terminology backward as contemporary motivation. Require identifiable sources for significant claims; prefer primary works and scholarly history. Explicitly record uncertainty and disagreement.

## Semantic Network V2 discipline

The project uses one evidence-backed knowledge base with separate Historical, Mathematical, and Inquiry semantic layers. Read `editorial/SEMANTIC-NETWORK-V2.md` before producing canonical candidates.

Do not treat all extracted objects as peer nodes in one flat graph.

- A **Problem** is a historical/mathematical object: a task, obstacle, or problem situation evidenced in the historical material.
- A **QuestionFrame** is an editorial formulation used to organize reader understanding. For packet compatibility it is still emitted under the `questions` key.
- A **Concept** is a diachronic identity.
- A **ConceptState** is the historically situated meaning/formulation evidenced for a specific period.
- A **Work** is a historical object; a Source is the evidence record/edition used to support a claim.

When the historical material supports a problem but not the exact reader-facing wording, model the historical object as `Problem` and place the editorial formulation under `questions`. Do not pretend the QuestionFrame is a verbatim historical question.

QuestionFrame relations belong to the Inquiry layer. They may be historically grounded, historiographic, or retrospective, but they are not automatically documentary transmission or mathematical dependency edges.

For historically changing concepts, produce `concept_state_candidates` whenever the period-specific meaning matters. Prefer a future pattern such as:

```text
Work -> ConceptState -> Concept
```

over attaching every historical claim directly to a timeless Concept identity.

### Relation precision

A canonical semantic edge should say what the evidence supports. Prefer specific relations when justified (for example authorship, definition/use, proof/result, revision/response, or historically documented development).

`contributed_to` is a broad fallback, not a desirable default topology edge. Use it only when the evidence supports association but not a more precise relation. Never strengthen it mechanically to `influenced`, `motivated`, `spawned`, `defined`, or `proved`.

If a desired relation cannot be stated precisely from the current evidence, record the gap rather than creating an edge for graph completeness.

Return structured sections: `entities`, `questions`, `assertions`, `question_transitions`, `intersection_candidates`, `concept_state_candidates`, `story_candidates`, `sources`, `uncertainties`. Branching and recombination are expected.

For each proposed assertion, make clear enough in its wording/notes for later promotion to determine:

- subject and object type;
- historical vs mathematical vs inquiry role;
- historical / later-interpretive / modern-abstraction perspective;
- whether the relation is precise or deliberately broad;
- temporal scope;
- supporting source IDs.

## Persistent source requirements

Do not emit ChatGPT citation markup, internal web-search result IDs,
or session-specific citation tokens.

These identifiers are temporary and must never be stored in the Research Packet.

All evidence must be normalized into persistent source records.

Each source must have:

- a stable `source_id`;
- source type (`primary`, `secondary`, `reference`, etc.);
- author or responsible organization where known;
- title;
- publication or date information where known;
- a persistent URL when available;
- a locator such as page, section, chapter, theorem, or first page when useful.

Assertions and question transitions must reference only stable `source_id` values.

Web search is a discovery mechanism, not a persistent evidence format.
