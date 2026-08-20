# R003–R004 integration roadmap

## Sequence

1. **Editorial maintenance before/alongside R003**: upgrade `story-rigor` (`How can infinity be trusted?`) from PoC stub using already accepted R002 canonical material where possible. This is not a new research unit unless new factual gaps emerge.
2. **R003**: Dirichlet / changing function concept. Replace or substantially rewrite the `story-function` PoC stub after research + Story Critic.
3. **R004**: Riemann / integrability. Start only after R003 is merged so it can reuse the current canonical Dirichlet/function graph and researched `story-function`.
4. Keep `story-frequency` (`Seeing the world by frequency`) explicitly deferred. It needs a later bounded unit on modes/harmonic or Fourier analysis rather than being filled with retrospective modern language now.

## Existing stubs

### `story-rigor` — How can infinity be trusted?

Status: PoC stub.

Preferred action: editorially reconstruct from R002 canonical assertions, with Story Editor + Story Critic. If a sentence or transition cannot be supported from R002, create a research gap rather than opening R003 scope.

### `story-function` — What is a function?

Status: PoC stub.

Preferred action: R003 owns this Story. Do not create a second near-duplicate Story under a new ID unless the research demonstrates two genuinely different editorial questions.

### `story-frequency` — Seeing the world by frequency

Status: PoC stub, deferred.

Preferred action: preserve as a placeholder or mark for later replacement. Do not treat modern frequency-domain language as Fourier's own conceptual framing without evidence.

## Integration rules for R003/R004

- Read current `main` first; repo state is authoritative.
- Reuse canonical IDs for the same historical object.
- Research Packet facts are candidates until Historical Critic + human resolution + verified promotion.
- Story prose is editorial and must reference canonical assertions.
- Story-local `temporal_anchor` controls Network occurrence time; entity start/birth dates do not.
- A Story DAG is not a timeline of entity births and must not move backward unless an explicit retrospective edge is intended.
- If Story links or temporal anchors change after Story Critic, the affected transition review becomes stale and must be re-run.
- Do not merge R004 before R003 if R004 depends on R003 canonical IDs or Story structure.

## Desired graph after R004

Conceptually, not as a predetermined causal chain:

```text
R001 Fourier
heat / representation / arbitrary functions
          │
          ├──────────────┐
          │              │
R002 Cauchy         R003 Dirichlet
convergence         function admissibility
continuity          convergence restrictions
          │              │
          └──────┬───────┘
                 │
             R004 Riemann
        trigonometric series / integrability
                 │
            later branches
       Cantor / Lebesgue / others
```

Every arrow in the rendered Story/Network must ultimately be justified by the actual reviewed DAG and assertions, not by this planning sketch.

## Fresh-chat commands

R003:

```text
Open Chachay/math-history-atlas and follow research/prompts/research-unit-kickoff-v1.md for R003. Use research/units/R003-dirichlet-function-concept.md as the approved unit brief. Read current main first and proceed through Phase A and Phase B, stopping with an open PR for review.
```

R004, after R003 merge:

```text
Open Chachay/math-history-atlas and follow research/prompts/research-unit-kickoff-v1.md for R004. Use research/units/R004-riemann-integrability.md as the approved unit brief. Confirm that R003 is merged into current main, then proceed through Phase A and Phase B, stopping with an open PR for review.
```
