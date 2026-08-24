# Projection V3 — exploration contract

## Purpose

Keep canonical historical/evidence data unchanged while giving readers three scales of navigation:

1. **Atlas** — field-scale landscape aggregated from researched semantic material.
2. **Network Overview** — time-positioned Work / Problem / Result / ConceptState topology.
3. **Network Focus** — one selected node and a small, semantically grouped set of routes outward.

Stories remain curated inquiry paths over the historical graph; user breadcrumbs are navigation history and are not canonical graph edges.

## Concept identity and evolution

`Concept` is a diachronic identity. `ConceptState` is a historically attested state.

`concept-evolution.json` groups states by Concept and orders them chronologically. Chronological adjacency MUST NOT be interpreted as historical causation. A transition such as `develops`, `generalizes`, or `revises` is shown as such only when supported by a reviewed canonical claim.

Reader-facing Concept exploration should therefore distinguish:

- **attested states over time** — safe grouping;
- **reviewed historical development** — evidence-bearing relation;
- **later mathematical comparison** — retrospective relation, explicitly marked when surfaced.

## Network Focus

Focus mode does not replace the overview projection. It is a second interaction mode.

Selecting a node should show:

- the focus node;
- reader-facing summary/detail;
- adjacent routes grouped into a small number of semantic sections;
- concept evolution as a dedicated route when the focus is a Concept or ConceptState;
- breadcrumb history recording the user's actual path.

Canonical predicates remain precise (`addresses`, `defines`, `uses`, `proves`, `strengthens`, `revises`, etc.). The UI may compress them into reader groups such as **Problems**, **Mathematical content**, **Results**, and **Earlier / later work**. UI grouping never rewrites canonical predicates.

Aim for no more than about seven immediately actionable choices. High-degree neighborhoods should fold behind group-level navigation rather than silently dropping edges.

## Atlas aggregation

Atlas must cease being a hard-coded illustration. Its future projection should aggregate researched semantic material through:

`Field -> Concept identity -> ConceptState -> Work / Problem / Result`

Field membership is a coarse-grained view, not a replacement for semantic relations. Cross-field connections should be derived from shared Concepts, semantic claims, and researched Stories rather than manually drawn decorative paths.

## Non-goals

- No force-directed graph.
- No new causal edges inferred from chronology.
- No collapse of Result into Work or ConceptState into Concept.
- No return to `graph.json` as source of truth.
- No removal of Story or Atlas in favor of a single graph explorer.
