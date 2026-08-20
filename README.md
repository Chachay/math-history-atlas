# Math History Atlas

A mobile-first SPA and research pipeline for representing modern mathematical history as a **historical graph + curated stories + derived story intersections**, rather than as a single timeline.

## Architecture

- `research/`: candidate packets, critic reviews, research gaps, promotion provenance, and reusable LLM prompts.
- `data/`: canonical historical entities, assertions, questions, concept states, and field polyhierarchy.
- `editorial/`: revisable Story DAGs, Story reviews, collections, and editorial workflow documentation.
- `generated/`: compiler output consumed by the SPA.
- `scripts/`: validation and build/compiler steps.
- `app/`: React/TypeScript/Vite prototype with Atlas, Network, Story, and Person views.

Core separation: **historical facts != historical interpretation != story narrative**. UI projections are also separate from the full graph.

## Data flow

```text
Research
→ Candidate Packet
→ Historical Critic
→ Human research review
→ Accepted canonical data
→ Story Editor
→ Story Critic
→ Human editorial review
→ Build
→ Generated JSON
→ SPA / PR Preview
```

## Local setup (PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python scripts/validate.py
pytest
python scripts/build.py
cd app
npm install
npm run dev
```

Use Python 3.12+ and Node.js 22+.

## Validation and build

```powershell
python scripts/validate.py
pytest
python scripts/build.py
```

The validator checks duplicate IDs, dangling references, source coverage, predicates, field parents, periods, Story references, Story assertion references, narrative traceability, and DAG cycles. Invalid data returns a non-zero exit code.

## Research and editorial workflow

1. Run `research/prompts/cluster-research-v1.md` for a bounded cluster.
2. Save output under `research/packets/`; it is not canonical yet.
3. Review it with `research/prompts/historical-critic-v1.md` and resolve material findings.
4. Promote only accepted entities/questions/assertions into `data/`, retaining provenance under `research/promotions/`.
5. Draft reader-facing Stories with `research/prompts/story-editor-v2.md` using canonical data only.
6. Review each Story independently with `research/prompts/story-critic-v1.md`.
7. Apply explicit human editorial resolutions; unresolved transitions become research gaps rather than smooth prose.
8. Run validation/build and use the Story's stable hash route in the PR Preview for mobile review.

See `editorial/WORKFLOW.md` for the R002-ready acceptance gate and responsibility split.

## GitHub PR review workflow

Keep review units small enough to inspect on mobile. PRs should summarize the proposed question transition, evidence, perspective, expected Story/network effect, and provide a direct Preview route for changed Stories. CI runs tests, validation, generated-data build, and SPA build before merge.

## Sample data

The PoC sample is in `data/**/core.yaml`, `editorial/stories/core.yaml`, and `sources/core.yaml`. It covers Euler, Fourier, Cauchy, Riemann, early analysis concepts, and three intersecting stories. Interpretive claims are deliberately marked as candidates where specialist verification is still required.

## Next steps

1. Use R002 as the first fresh research unit to exercise the full Research → Story Critic workflow without R001-specific intervention.
2. Add a PR-summary generator optimized for direct Story deep links and mobile review.
3. Expand through Cantor, Lebesgue, Hilbert, topology/cohomology, Serre, and Grothendieck.
4. Improve Atlas projection and interactive graph rendering without changing canonical graph semantics.

## V5 mobile UI

The React SPA follows the V5 interaction model:

- **Atlas** — chronological field evolution with branching and recombination.
- **Network** — historical nodes with multiple Story paths overlaid; shared nodes become intersections.
- **Story** — vertical editorial reading with a parallel-Story rail; Story content comes from editorial YAML rather than UI hardcoding.
- **Person** — contribution/profile index generated from canonical data.

`scripts/build.py` mirrors generated JSON into `app/public/data/`, so the SPA consumes build products rather than hard-coded mock objects. Hash routes provide stable deep links on GitHub Pages and nested PR Preview deployments.
