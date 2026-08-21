# R006 brief — polynomial solvability, permutations, and the road to Galois

## Purpose

Use R006 to open the first substantial **algebra** branch of the Atlas. Start from the concrete problem of solving polynomial equations by radicals and investigate how work on transformations and permutations of roots changed the mathematical object of study from formulas for solutions toward structural conditions for solvability.

Do not begin with the modern abstract definition of a group and project it backward.

## Proposed title

**Why can some equations be solved by radicals and others cannot? — permutations, solvability, and Galois**

## Working period

Core: approximately **1770–1846**.

Earlier equation-solving background may be summarized only as needed. Later abstract group theory, field theory, and twentieth-century Galois theory belong to later units unless required as explicitly retrospective interpretation.

## Dependency

R006 should begin after R005 has either merged or reached a stable stopping point, so the Atlas can deliberately branch away from the now-developed analysis line. It should not be forced to connect historically to R005 merely because it follows it editorially.

Before Phase B, check that the Atlas/field UI can display a genuinely separate algebra path rather than routing every research unit into the analysis lane.

## Existing graph intersections to inspect first

- `algebra` field and its parents/children
- Euler/Lagrange/Abel/Galois person entities if present
- any existing polynomial/equation entities
- existing `group`, `permutation`, `field`, or solvability concepts if present
- any prototype data touching algebra: treat it as editorial hypothesis unless source-checked

Reuse canonical IDs only when the historical object is genuinely the same.

## Core research questions

1. What was the concrete problem surrounding solutions of polynomial equations by radicals in the late eighteenth and early nineteenth centuries?
2. What did Lagrange actually learn from comparing formulas for roots and the behavior of expressions under permutations of roots?
3. What exactly did Abel prove about the general quintic, and what did he not prove?
4. What problem was Galois addressing, and how did permutations/substitutions enter his criterion for solvability?
5. To what extent did Galois possess something recognizably related to a modern group concept, and where would that terminology be anachronistic?
6. Which developments are historically connected by direct reading, correspondence, citation, or shared problem structure, and which are later reconstructions of a clean Lagrange → Abel → Galois genealogy?
7. What dates should be used for Galois material: composition, submission, rejection/revision, death, posthumous publication, or later editorial recovery?
8. What remaining question naturally opens toward abstract algebra: when did permutations, substitutions, groups, fields, or algebraic structures become objects studied in their own right?

## Historical claims that must be tested rather than assumed

- “Lagrange invented group theory.”
- “Abel proved the quintic has no solution.”
- “Galois invented the modern group.”
- “Galois theory was immediately understood after 1832.”
- “Modern normal subgroups, fields, and group actions can be read directly into Galois's terminology.”
- “There is a single uninterrupted transmission Lagrange → Abel → Galois.”

## Primary-source targets

Locate stable primary editions/scans and page-level passages for:

- Lagrange's work on algebraic equations and permutations/substitutions of roots;
- Abel's impossibility result for the general quintic and its exact scope;
- Galois manuscripts/memoirs relevant to solvability by radicals and groups of substitutions;
- chronology of submissions and posthumous publication;
- direct references among these authors where a historical connection is claimed.

Use specialist historiography for the emergence of the modern group concept and for interpreting Galois's terminology.

## Phase-B integration target

Create a new algebra Story centered on the question:

**Why can some equations be solved by radicals and others cannot?**

Likely roles:

- Problem: general solution formulas for polynomial equations;
- Structural clue: permutations/substitutions of roots;
- Negative result: limits on radical formulas;
- Response: solvability conditions expressed through substitution structure;
- Remaining gap: the later abstraction of groups/fields as independent mathematical objects.

The Story should branch from the Atlas's algebra field, not from the R001–R005 analysis chain unless evidence identifies a genuine intersection.

## Network effect expected

R006 should be the first test that the Atlas is not merely a history of nineteenth-century analysis. The Network should show a second major historical cluster with its own internal Story path, while the Atlas makes the field-level branch visible.

A lack of cross-link to the analysis Stories is acceptable. Connectivity should come from real shared entities or reviewed historical transitions, not editorial pressure to make one connected graph.

## UI prerequisite

Before accepting Phase B, verify that:

- the Atlas derives or can represent the algebra branch from field data rather than only a hard-coded decorative path;
- entering Algebra can filter or frame the relevant Network cluster;
- algebra Person pages are reachable through assertion-backed navigation.

If the current Atlas cannot do this, create a bounded UI prerequisite PR rather than weakening the historical data to fit the UI.

## Deferred downstream possibilities

- formal emergence of abstract groups after Galois;
- Cayley and permutation groups;
- Dedekind/Noether and structural algebra;
- field theory as a mature framework;
- algebra/geometry recombination.

## Fresh-chat command

```text
Open Chachay/math-history-atlas and follow research/prompts/research-unit-kickoff-v1.md for R006. Use research/units/R006-solvability-permutations-galois.md as the approved unit brief. Read current main first. Treat modern group/field terminology as retrospective unless supported, distinguish Galois manuscript/submission/publication dates, and do not force an artificial link back to the analysis Stories. Proceed through Phase A and Phase B and stop at PR/mobile review.
```
