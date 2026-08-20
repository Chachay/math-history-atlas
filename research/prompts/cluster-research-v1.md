# Cluster Research v1
Investigate `[TOPIC]` during `[PERIOD]` for a structured interactive history of modern mathematics. Do not write a conventional biography. Extract the problems researchers were actually trying to solve, how questions changed, important people/works/concepts/results/events, developments that answered or created questions, intersections of research lines, and concepts whose historical meaning differs from modern usage.

Distinguish `historical`, `later_interpretation`, and `modern_abstraction`. Never project later terminology backward as contemporary motivation. Require identifiable sources for significant claims; prefer primary works and scholarly history. Explicitly record uncertainty and disagreement.

Return structured sections: `entities`, `questions`, `assertions`, `question_transitions`, `intersection_candidates`, `concept_state_candidates`, `story_candidates`, `sources`, `uncertainties`. Branching and recombination are expected.

## Persistent source requirements

Do not emit ChatGPT citation markup, internal web-search result IDs,
or session-specific citation tokens such as:

``

These identifiers are temporary and must never be stored in the
Research Packet.

All evidence must be normalized into persistent source records.

Each source must have:

- a stable `source_id`;
- source type (`primary`, `secondary`, `reference`, etc.);
- author or responsible organization where known;
- title;
- publication or date information where known;
- a persistent URL when available;
- a locator such as page, section, chapter, theorem, or first page
  when useful.

Assertions and question transitions must reference only stable
`source_id` values.

Web search is a discovery mechanism, not a persistent evidence format.
